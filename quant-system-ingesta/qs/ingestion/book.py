"""book.py — Libro L2 local con protocolo de sincronización de Binance Futures.

Implementa ESPEC-INGESTA §3-4. La cadena de secuencia (pu == u_anterior) es la
garantía de integridad: si se rompe, el libro local ya no refleja el real y es
obligatorio re-snapshot (BOOK_REBUILD).
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import IntEnum

DEPTH_LEVELS = 10


class EventType(IntEnum):
    DEPTH_UPDATE = 0
    BOOK_REBUILD = 1


class GapError(Exception):
    """Cadena de secuencia rota: pu != u_anterior. Requiere re-snapshot."""


@dataclass
class BookRecord:
    recv_ts_ns: int        # pared (epoch ns): partición por día, correlación
    recv_mono_ns: int      # monotónico (v2): orden y gaps, inmune a NTP
    event_ts_ms: int
    first_update_id: int
    final_update_id: int
    prev_final_update_id: int
    event_type: int
    bid_prices: list[float]
    bid_volumes: list[float]
    ask_prices: list[float]
    ask_volumes: list[float]


@dataclass
class LocalBook:
    """Mantiene el libro completo en dicts precio→volumen y emite top-10."""
    symbol: str
    bids: dict[float, float] = field(default_factory=dict)
    asks: dict[float, float] = field(default_factory=dict)
    last_update_id: int = -1   # u del último diff aplicado (o lastUpdateId del snapshot)
    synced: bool = False

    # ---- Inicialización desde snapshot REST ----
    def load_snapshot(self, snapshot: dict) -> None:
        """snapshot: respuesta de GET /fapi/v1/depth (lastUpdateId, bids, asks)."""
        self.bids = {float(p): float(q) for p, q in snapshot["bids"] if float(q) > 0}
        self.asks = {float(p): float(q) for p, q in snapshot["asks"] if float(q) > 0}
        self.last_update_id = snapshot["lastUpdateId"]
        self.synced = False  # synced solo tras aplicar el primer diff válido

    # ---- Aplicación de diffs del stream @depth@100ms ----
    def apply_diff(self, ev: dict) -> BookRecord | None:
        """Aplica un evento depthUpdate. Devuelve BookRecord, o None si el
        evento es anterior al snapshot (se descarta). Lanza GapError si la
        cadena de secuencia se rompe."""
        U, u, pu = ev["U"], ev["u"], ev["pu"]

        if not self.synced:
            # ═══ EMPALME CON EL SNAPSHOT ═══ (mesa 2026-08-29, dictamen 6º)
            #
            # LA REGLA OFICIAL DE USDⓈ-M FUTURES, literal: descartar los eventos con `u < L`, y el
            # primero que se aplica debe cumplir `U <= L <= u`.
            #
            # HISTORIA, porque explica por qué el código dice hoy menos de lo que decía ayer:
            #
            #  · el comentario original afirmaba que `U <= L+1 <= u` (SPOT) era «equivalente» a la
            #    regla de futuros. ES FALSO: difieren exactamente en `U == L+1`.
            #  · al corregirlo añadí una extensión —aceptar `U == L+1` cuando `pu == L`— apoyada en un
            #    barrido propio. La mesa la RECHAZÓ, y con razón: ese barrido no tenía script ni recibo
            #    versionado, sólo vivía en comentarios y en tests que fijaban la regla que yo había
            #    elegido. Un número sin procedencia no acredita nada, y menos si altera la población
            #    aceptada. Fuera. Si vuelve, será con instrumento y recibo propios, como cambio
            #    normativo previo y no como «invariante equivalente».
            #
            # AFIRMACIÓN RETIRADA (mesa, 2026-08-29). Aquí decía que «el `pu` del primer evento se
            # comprueba igual que el de los siguientes». **Era falsa**: la comparación de `pu` vive
            # sólo en el `else`, a partir del segundo evento, y los propios tests aceptan `pu=97` con
            # `L=100`. Escribí la glosa y además se la repetí al firmante.
            #
            # Y NO se añade esa guardia, que era la tentación obvia: la regla oficial NO exige
            # `pu == L` en el primer empalme, así que exigirlo rechazaría eventos válidos. Un
            # comentario falso se arregla borrándolo, no endureciendo el código para que encaje.
            if u < self.last_update_id:
                return None
            L = self.last_update_id
            if not (U <= L <= u):
                raise GapError(f"{self.symbol}: empalme inválido (U={U}, u={u}, last={L}): el "
                               f"snapshot no cae dentro del evento (USDⓈ-M exige U <= L <= u)")
            self.synced = True
        else:
            if pu != self.last_update_id:
                raise GapError(f"{self.symbol}: pu={pu} != u_anterior={self.last_update_id}")

        for p, q in ev["b"]:
            p, q = float(p), float(q)
            if q == 0:
                self.bids.pop(p, None)
            else:
                self.bids[p] = q
        for p, q in ev["a"]:
            p, q = float(p), float(q)
            if q == 0:
                self.asks.pop(p, None)
            else:
                self.asks[p] = q

        self.last_update_id = u
        return self._record(ev, EventType.DEPTH_UPDATE)

    def rebuild_record(self, ev_ts_ms: int | None = None) -> BookRecord:
        """Registro marcador tras re-snapshot (estado actual, tipo BOOK_REBUILD)."""
        fake = {"E": ev_ts_ms or int(time.time() * 1000),
                "U": self.last_update_id, "u": self.last_update_id, "pu": -1}
        return self._record(fake, EventType.BOOK_REBUILD)

    # ---- helpers ----
    def top(self, n: int = DEPTH_LEVELS):
        bp = sorted(self.bids, reverse=True)[:n]
        ap = sorted(self.asks)[:n]
        return ([float(p) for p in bp], [self.bids[p] for p in bp],
                [float(p) for p in ap], [self.asks[p] for p in ap])

    def _record(self, ev: dict, etype: EventType) -> BookRecord:
        bp, bv, ap, av = self.top()
        return BookRecord(
            recv_ts_ns=time.time_ns(),
            recv_mono_ns=time.monotonic_ns(),
            event_ts_ms=ev["E"],
            first_update_id=ev["U"],
            final_update_id=ev["u"],
            prev_final_update_id=ev["pu"],
            event_type=int(etype),
            bid_prices=bp, bid_volumes=bv,
            ask_prices=ap, ask_volumes=av,
        )
