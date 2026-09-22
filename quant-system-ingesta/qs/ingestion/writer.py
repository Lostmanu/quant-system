"""writer.py — Buffer → Parquet con escritura atómica (ESPEC §5/§7, v2.0).

Cada flush publica parts inmutables `{kind}-NNNNN.parquet` vía tmp + fsync +
os.replace: nunca se reabre ni sobrescribe un fichero publicado. El directorio
de día se deriva del recv_ts_ns (pared) de cada registro. Esquema v2: doble
timestamp (recv_ts_ns pared + recv_mono_ns monotónico) y `qs_schema=2` en la
metadata de cada fichero. El flush es separable (due/take/write_rows) para
ejecutarse en un thread executor sin parar el event loop; si la escritura
falla, el llamante devuelve las filas al buffer (cero pérdida silenciosa).
El job de cierre de día compacta los parts (audit.compact_day).
"""
from __future__ import annotations
import json
import os
import re
import time
from dataclasses import asdict
import pyarrow as pa
import pyarrow.parquet as pq

QS_SCHEMA_KEY = b"qs_schema"               # versión de esquema en metadata parquet
QS_SCHEMA_VER = b"2"
COMPACT_META_KEY = b"qs_parts_compactados"  # metadata parquet: parts ya absorbidos
_SCHEMA_META = {QS_SCHEMA_KEY: QS_SCHEMA_VER}

DEPTH_SCHEMA = pa.schema([
    ("recv_ts_ns", pa.int64()), ("recv_mono_ns", pa.int64()),
    ("event_ts_ms", pa.int64()),
    ("first_update_id", pa.int64()), ("final_update_id", pa.int64()),
    ("prev_final_update_id", pa.int64()), ("event_type", pa.int8()),
    ("bid_prices", pa.list_(pa.float64())), ("bid_volumes", pa.list_(pa.float64())),
    ("ask_prices", pa.list_(pa.float64())), ("ask_volumes", pa.list_(pa.float64())),
], metadata=_SCHEMA_META)

TRADE_SCHEMA = pa.schema([
    ("recv_ts_ns", pa.int64()), ("recv_mono_ns", pa.int64()),
    ("event_ts_ms", pa.int64()), ("trade_ts_ms", pa.int64()),
    ("agg_trade_id", pa.int64()), ("price", pa.float64()), ("qty", pa.float64()),
    ("is_buyer_maker", pa.bool_()),
], metadata=_SCHEMA_META)

FLUSH_SECS, FLUSH_ROWS = 60, 50_000
DAY_NS = 86_400 * 10 ** 9


class PartialWriteError(Exception):
    """write_rows falló a mitad de un batch multi-día: `pending` contiene SOLO
    las filas aún no publicadas. Reintentar el batch completo duplicaría los
    días ya escritos (silencioso en trades, donde no hay check de cadena)."""

    def __init__(self, pending: list[dict], cause: Exception):
        super().__init__(str(cause))
        self.pending = pending


def fsync_dir(path: str) -> None:
    """Persiste el rename en el directorio (POSIX; en Windows no es posible)."""
    if os.name != "posix":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


class ParquetBuffer:
    """Acumula registros y publica un part parquet atómico por flush.

    Con auto_flush=True (tools, tests) add()/tick() disparan el flush síncrono.
    Con auto_flush=False (producción) el llamante usa due()/take()/write_rows()
    para hacer la escritura en un executor fuera del event loop.
    """

    def __init__(self, base_dir: str, symbol: str, kind: str, schema: pa.Schema,
                 auto_flush: bool = True):
        self.base, self.symbol, self.kind, self.schema = base_dir, symbol, kind, schema
        self.auto_flush = auto_flush
        self.rows: list[dict] = []
        self._last_flush = time.monotonic()   # gatillo de tiempo inmune a NTP (v2)
        self._day: str | None = None
        self._dir: str | None = None
        self._next = 0

    def add(self, rec) -> None:
        self.rows.append(asdict(rec) if hasattr(rec, "__dataclass_fields__") else rec)
        if self.auto_flush and self.due():
            self.flush()

    def due(self) -> bool:
        """¿Toca flush? Por volumen o por tiempo (reloj monotónico)."""
        return bool(self.rows) and (
            len(self.rows) >= FLUSH_ROWS
            or time.monotonic() - self._last_flush >= FLUSH_SECS)

    def tick(self) -> None:
        """Flush por tiempo aunque no lleguen registros nuevos (ESPEC §7)."""
        if self.auto_flush and self.due():
            self.flush()

    def take(self) -> list[dict]:
        """Extrae el buffer (atómico: sin awaits entre leer y vaciar) para que el
        llamante lo escriba en un executor. Si la escritura falla, debe devolver
        las filas al frente de self.rows."""
        rows, self.rows = self.rows, []
        self._last_flush = time.monotonic()
        return rows

    def write_rows(self, rows: list[dict]) -> None:
        """Publica `rows` como parts. Bloqueante (parquet + fsync): pensado para
        ejecutarse en un thread executor en producción. Si falla a mitad de un
        batch multi-día, lanza PartialWriteError con SOLO lo no publicado."""
        if not rows:
            return
        days: dict[int, list[dict]] = {}   # día UTC del recv_ts_ns (pared)
        for r in rows:
            days.setdefault(r["recv_ts_ns"] // DAY_NS, []).append(r)
        batches = [(d, days[d]) for d in sorted(days)]
        for i, (epoch_day, batch) in enumerate(batches):
            day = time.strftime("%Y-%m-%d", time.gmtime(epoch_day * 86_400))
            try:
                self._write_part(day, batch)
            except Exception as e:
                pendientes = [r for _, b in batches[i:] for r in b]
                raise PartialWriteError(pendientes, e) from e

    def flush(self) -> None:
        self.write_rows(self.take())

    def _next_index(self, d: str) -> int:
        """Continúa la numeración tras los parts ya publicados — incluidos los ya
        absorbidos por una compactación intradía (registrados en la metadata del
        compactado): reutilizar un índice haría que la siguiente compactación
        excluyera el part nuevo por nombre y lo borrara → pérdida de datos."""
        pat = re.compile(rf"{re.escape(self.kind)}-(\d+)\.parquet$")
        idxs = [int(m.group(1)) for n in os.listdir(d) if (m := pat.fullmatch(n))]
        final = os.path.join(d, f"{self.kind}.parquet")
        if os.path.exists(final):
            try:
                kv = pq.read_metadata(final).metadata or {}
                absorbidos = json.loads(kv.get(COMPACT_META_KEY, b"[]"))
                idxs += [int(m.group(1)) for n in absorbidos if (m := pat.fullmatch(n))]
            except Exception:
                pass   # compactado ilegible: numerar tras lo visible es lo mejor posible
        return max(idxs, default=-1) + 1

    def _write_part(self, day: str, rows: list[dict]) -> None:
        if day != self._day:           # rotación diaria (o primer part del proceso)
            self._dir = os.path.join(self.base, self.symbol, day)
            os.makedirs(self._dir, exist_ok=True)
            self._next = self._next_index(self._dir)
            self._day = day
        cols = {f.name: [r[f.name] for r in rows] for f in self.schema}
        path = os.path.join(self._dir, f"{self.kind}-{self._next:05d}.parquet")
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            pq.write_table(pa.table(cols, schema=self.schema), f, compression="snappy")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        fsync_dir(self._dir)
        self._next += 1

    def close(self) -> None:
        self.flush()
