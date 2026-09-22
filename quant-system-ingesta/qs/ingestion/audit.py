"""audit.py — Auditoría de integridad diaria (ESPEC-INGESTA §6, Plan Maestro 1.4).

Lee los datos depth de un día — parts `{kind}-NNNNN.parquet` del writer v1.2 y/o
el `{kind}.parquet` único (legacy o ya compactado) — y emite audit.json. El job
de cierre además compacta los parts del día en un único fichero por tipo
(escritura atómica e idempotente). FAIL en checks 1-5 → día corrupto.
"""
from __future__ import annotations
import glob
import json
import os
import pyarrow as pa
import pyarrow.parquet as pq
from .writer import COMPACT_META_KEY, QS_SCHEMA_KEY, QS_SCHEMA_VER, fsync_dir

REBUILD_WARN, REBUILD_FAIL = 5, 20
MAX_SILENCE_NS = 60_000_000_000  # 60 s


def _schema_ok(files: list[str]) -> bool:
    """c0 (v2.0): todo fichero del día debe declarar qs_schema=2 en su metadata."""
    for p in files:
        meta = pq.read_metadata(p).metadata or {}
        if meta.get(QS_SCHEMA_KEY) != QS_SCHEMA_VER:
            return False
    return True


def day_files(day_dir: str, kind: str) -> list[str]:
    """Parquets de un día en orden cronológico: el `{kind}.parquet` único
    (legacy/compactado, datos más antiguos) primero, luego los parts."""
    files = []
    single = os.path.join(day_dir, f"{kind}.parquet")
    if os.path.exists(single):
        files.append(single)
    files += sorted(glob.glob(os.path.join(day_dir, f"{kind}-*.parquet")))
    return files


def read_day(path: str, kind: str = "depth") -> pa.Table:
    """Tabla completa del día. `path` puede ser un parquet concreto o el
    directorio del día (concatena único + parts en orden)."""
    if os.path.isfile(path):
        return pq.read_table(path)
    files = day_files(path, kind)
    if not files:
        return pa.table({})        # num_rows == 0 → la auditoría marca FAIL
    return pa.concat_tables(
        [pq.read_table(p).replace_schema_metadata(None) for p in files])


def compact_day(day_dir: str, kind: str) -> dict:
    """Compacta los parts del día en `{kind}.parquet` (tmp + fsync + rename).

    Idempotente ante interrupciones: el compactado registra en su metadata
    parquet los parts absorbidos; si una pasada anterior murió entre el rename
    y el borrado, la siguiente solo limpia los parts restantes, sin duplicar.
    Los parts solo se borran con el compactado publicado y verificado."""
    final = os.path.join(day_dir, f"{kind}.parquet")
    parts = sorted(glob.glob(os.path.join(day_dir, f"{kind}-*.parquet")))
    if not parts:
        return {"compactado": False, "n_parts": 0}
    tables, absorbidos = [], set()
    if os.path.exists(final):      # legacy pre-v1.2 o compactación interrumpida
        prev = pq.read_table(final)
        meta = (prev.schema.metadata or {}).get(COMPACT_META_KEY)
        absorbidos = set(json.loads(meta)) if meta else set()
        tables.append(prev.replace_schema_metadata(None))
    nuevos = [p for p in parts if os.path.basename(p) not in absorbidos]
    if nuevos:
        tables += [pq.read_table(p).replace_schema_metadata(None) for p in nuevos]
        combined = pa.concat_tables(tables)
        registro = sorted(absorbidos | {os.path.basename(p) for p in nuevos})
        combined = combined.replace_schema_metadata(
            {COMPACT_META_KEY: json.dumps(registro).encode(),
             QS_SCHEMA_KEY: QS_SCHEMA_VER})
        tmp = final + ".tmp"
        with open(tmp, "wb") as f:
            pq.write_table(combined, f, compression="snappy")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, final)
        fsync_dir(day_dir)
        if pq.read_metadata(final).num_rows != combined.num_rows:
            raise RuntimeError(f"compactación inconsistente en {final}")
    for p in parts:
        os.remove(p)
    fsync_dir(day_dir)
    return {"compactado": True, "n_parts": len(nuevos),
            "n_rows": pq.read_metadata(final).num_rows}


def _count_rows(day_dir: str, kind: str) -> int:
    return sum(pq.read_metadata(p).num_rows for p in day_files(day_dir, kind))


def audit_depth(path: str) -> dict:
    """`path`: directorio del día o un parquet concreto."""
    if os.path.isdir(path):
        c0 = _schema_ok(day_files(path, "depth") + day_files(path, "trades"))
    else:
        c0 = _schema_ok([path])
    if not c0:
        # esquema desconocido/ausente (p. ej. día legacy v1): FAIL limpio SIN leer
        # los datos — leerlos podría reventar (columnas distintas, concat imposible)
        return {"n_events": 0, "n_rebuilds": 0, "max_silence_s": 0.0,
                "wall_regressions": 0, "status": "FAIL",
                "motivo": "qs_schema != 2: día no auditable con este contrato",
                "checks": {"c0_esquema": False, "c1_monotonia": False,
                           "c2_secuencia": False, "c3_no_cruzado": False,
                           "c4_niveles": False, "c5_volumenes": False,
                           "c6_sin_silencios": False}}
    t = read_day(path, "depth")
    n = t.num_rows
    res = {"n_events": n, "checks": {}, "n_rebuilds": 0, "max_silence_s": 0.0,
           "wall_regressions": 0}
    if n == 0:
        res["checks"] = {f"c{i}": False for i in range(0, 7)}
        res["status"] = "FAIL"
        return res

    recv = t.column("recv_ts_ns").to_pylist()
    mono = t.column("recv_mono_ns").to_pylist()
    fuid = t.column("final_update_id").to_pylist()
    puid = t.column("prev_final_update_id").to_pylist()
    etype = t.column("event_type").to_pylist()
    bp = t.column("bid_prices").to_pylist()
    ap = t.column("ask_prices").to_pylist()
    bv = t.column("bid_volumes").to_pylist()
    av = t.column("ask_volumes").to_pylist()

    # C1 (v2.0): monotonía sobre el reloj MONOTÓNICO, salvo en frontera de
    # rebuild (un reinicio de proceso resetea el monotónico y todo arranque
    # emite su marcador); empates ordenados por final_update_id.
    c1 = True
    for i in range(n - 1):
        if etype[i] == 1 or etype[i + 1] == 1:
            continue
        if mono[i] > mono[i + 1] or (mono[i] == mono[i + 1]
                                     and fuid[i] >= fuid[i + 1]):
            c1 = False
            break
    # informativo (salud NTP): retrocesos del reloj de pared, sin efecto en status
    res["wall_regressions"] = sum(1 for i in range(n - 1) if recv[i + 1] < recv[i])

    # C2: cadena de secuencia íntegra salvo rebuilds
    rebuilds = sum(1 for e in etype if e == 1)
    breaks = 0
    for i in range(1, n):
        if etype[i] == 1 or etype[i - 1] == 1:
            continue  # frontera de rebuild: cadena se reinicia
        if puid[i] != fuid[i - 1]:
            breaks += 1
    res["n_rebuilds"] = rebuilds
    c2 = breaks == 0 and rebuilds <= REBUILD_FAIL
    res["rebuild_level"] = ("FAIL" if rebuilds > REBUILD_FAIL
                            else "WARN" if rebuilds > REBUILD_WARN else "OK")

    # C3: libro no cruzado | C4: monotonía entre niveles | C5: volúmenes > 0
    c3 = c4 = c5 = True
    for i in range(n):
        b, a = bp[i], ap[i]
        if b and a and b[0] >= a[0]:
            c3 = False
        if any(b[j] < b[j + 1] for j in range(len(b) - 1)) or \
           any(a[j] > a[j + 1] for j in range(len(a) - 1)):
            c4 = False
        if any(v <= 0 for v in bv[i]) or any(v <= 0 for v in av[i]):
            c5 = False
        if not (c3 and c4 and c5):
            break

    # C6: sin silencios > 60 s
    max_gap = max((recv[i + 1] - recv[i] for i in range(n - 1)), default=0)
    res["max_silence_s"] = round(max_gap / 1e9, 1)
    c6 = max_gap <= MAX_SILENCE_NS

    res["checks"] = {"c0_esquema": c0, "c1_monotonia": c1, "c2_secuencia": c2,
                     "c3_no_cruzado": c3, "c4_niveles": c4, "c5_volumenes": c5,
                     "c6_sin_silencios": c6}
    res["status"] = "PASS" if all([c0, c1, c2, c3, c4, c5]) else "FAIL"
    if res["status"] == "PASS" and (not c6 or rebuilds > REBUILD_WARN):
        res["status"] = "WARN"   # silencios >60s o >5 rebuilds degradan el día
    return res


def write_audit(path: str, out_path: str, compact: bool = True) -> dict:
    """Job de cierre de día (§6): compacta depth y trades, audita y emite
    audit.json. `path`: directorio del día (con un parquet suelto no compacta)."""
    extra = {}
    if os.path.isdir(path):
        if compact:
            extra["compactacion"] = {"depth": compact_day(path, "depth"),
                                     "trades": compact_day(path, "trades")}
        extra["n_trades"] = _count_rows(path, "trades")
        # un .tmp huérfano delata un crash en mitad de un flush (≤60s perdidos)
        extra["n_tmp_huerfanos"] = len(glob.glob(os.path.join(path, "*.tmp")))
    r = audit_depth(path) | extra
    with open(out_path, "w") as f:
        json.dump(r, f, indent=2)
    return r
