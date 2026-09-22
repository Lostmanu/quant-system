"""analysis/cryptohft_adapter.py — reconstrucción CryptoHFTData (diffs @tick) → libro normalizado @grid.

CHD orderbook: cada fila = (lado, precio, **cantidad ABSOLUTA**; cantidad 0 = borrar nivel). Columnas:
received_time(ns), event_time(ms), transaction_time(ms), side('bid'/'ask'), price/quantity (strings),
*_update_id.

CORRECCIÓN (2026-08-30). Esta cabecera decía «stream de DIFFs de Binance (`event_type='update'`, SIN
snapshot seed)». Era una afirmación sobre EL FEED y es FALSA: el canal SÍ entrega filas
`event_type='snapshot'` — 169 anclas en el caché local, en 112 de 112 ficheros de junio. La creencia
venía de la única colección medida entonces (`probe1`, diez ficheros de AVAX de mar-abr 2026), que no
tiene ninguna. Lo que SÍ sigue siendo cierto es la afirmación sobre ESTE ADAPTADOR: no lee las anclas,
no lee los `*_update_id`, y reconstruye desde vacío. Es decir, **descarta un ancla que el feed sí da**;
queda declarado como defecto vivo y su reparación no está autorizada aquí.

Sin usar el ancla, el libro se reconstruye desde vacío y MADURA en segundos (los niveles top cambian sub-segundo) → se exige ≥top_l por
lado (warmup) y libro no cruzado. Muestreo en REJILLA TEMPORAL (event_time, `sample_ms`) para casar con
la cadencia de la sonda (@100ms). Top-L solo: los niveles profundos sin diff quedan desconocidos, pero
son irrelevantes para OFI/mid. Devuelve la forma normalizada de book.py (bid desc, ask asc).
"""
from __future__ import annotations
import heapq
import os
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from analysis.book import ofi as book_ofi


class CorruptDayError(Exception):
    """Día CHD CORRUPTO (libro reconstruido CONGELADO). Se lanza para FALLAR FUERTE; el runner puede
    capturarla para SALTAR el día con log. Un día corrupto NUNCA se usa en silencio. Lleva el report."""

    def __init__(self, report: dict):
        self.report = report
        super().__init__(f"día CHD corrupto (libro congelado): {report}")


def reconstruct_timegrid(event_ms, side, price, qty, top_l: int = 10, sample_ms: int = 100, cap: int = 128):
    """Reconstruye el libro aplicando diffs en orden y lo MUESTREA en rejilla temporal (cada `sample_ms`
    sobre event_time). Snapshot causal: refleja todos los updates con tiempo < el punto de rejilla. Solo
    emite libros maduros (≥top_l por lado) y NO cruzados. PODA cada lado a los mejores `cap` precios
    (los profundos no afectan al top-L y, si vuelven al top, el diff los re-añade) → coste acotado.
    Devuelve (ts[T], bpx, bsz, apx, asz).

    OPTIMIZADO (jul-2026): `heapq.nlargest/nsmallest` en vez de `sorted(...)[:k]`+lambda (mismo top-L por
    precio, sin las 87M llamadas a lambda del profiler), y `side` acepta un array BOOL (`is_bid`, camino
    rápido desde cryptohft_to_book, que ya castea columnas a numpy) o strings 'bid'/'ask' (tests). La
    salida es BYTE-IDÉNTICA a la versión validada — verificado sobre días reales del solape."""
    _side = np.asarray(side)
    is_bid = _side if _side.dtype == bool else (_side == "bid")   # bool: camino rápido; strings: tests
    bids: dict[float, float] = {}
    asks: dict[float, float] = {}
    ts_l, bpx, bsz, apx, asz = [], [], [], [], []
    n = len(event_ms)
    next_grid = None
    for i in range(n):
        t = int(event_ms[i])
        if next_grid is None:
            next_grid = t + sample_ms
        while t >= next_grid:                                  # emite snapshots de toda rejilla cruzada
            if len(bids) >= top_l and len(asks) >= top_l:
                bb = heapq.nlargest(top_l, bids.items())       # top_l por precio desc (precios únicos → == sorted(-precio)[:top_l])
                aa = heapq.nsmallest(top_l, asks.items())      # top_l por precio asc
                if bb[0][0] < aa[0][0]:                        # no cruzado
                    ts_l.append(next_grid)
                    bpx.append([p for p, _ in bb]); bsz.append([s for _, s in bb])
                    apx.append([p for p, _ in aa]); asz.append([s for _, s in aa])
            next_grid += sample_ms
        p = float(price[i]); q = float(qty[i])
        if is_bid[i]:
            if q == 0.0:
                bids.pop(p, None)
            else:
                bids[p] = q
                if len(bids) > cap:                            # poda: quedarse los `cap//2` mejores (más altos)
                    bids = dict(heapq.nlargest(cap // 2, bids.items()))
        else:
            if q == 0.0:
                asks.pop(p, None)
            else:
                asks[p] = q
                if len(asks) > cap:                            # poda: quedarse los `cap//2` mejores (más bajos)
                    asks = dict(heapq.nsmallest(cap // 2, asks.items()))
    arr = lambda x: np.array(x, "float64")
    return np.array(ts_l, "int64"), arr(bpx), arr(bsz), arr(apx), arr(asz)


def cryptohft_to_book(path_or_table, top_l: int = 10, sample_ms: int = 100):
    """Carga un parquet de orderbook CHD (o una pa.Table) y lo reconstruye a libro normalizado @grid.
    Devuelve (ts_ms[T], bpx, bsz, apx, asz) listo para book.py / el análisis contrarian."""
    t = path_or_table if hasattr(path_or_table, "column_names") else pq.read_table(path_or_table)
    # cast en C++ (pyarrow) → numpy, en vez de to_pydict() que materializa listas Python de millones de
    # strings (42% del tiempo en el profiler). price/quantity vienen como strings → float64; side → bool.
    event_ms = t.column("event_time").cast(pa.int64()).to_numpy(zero_copy_only=False)
    price = t.column("price").cast(pa.float64()).to_numpy(zero_copy_only=False)
    qty = t.column("quantity").cast(pa.float64()).to_numpy(zero_copy_only=False)
    is_bid = pc.equal(t.column("side"), pa.scalar("bid")).to_numpy(zero_copy_only=False)
    return reconstruct_timegrid(event_ms, is_bid, price, qty, top_l=top_l, sample_ms=sample_ms)


# ===================== GUARDIA DE DÍA-CORRUPTO (libro reconstruido CONGELADO) =====================
# jul-01-2025 fue un día CORRUPTO aislado: el stream arrancaba con borrados qty=0 → el libro nunca se
# pobló → quedó CONGELADO → OFI muerto → señal degenerada. El adapter lo reconstruyó en SILENCIO sin
# error (824k snapshots, pero best-bid-size 0.0000 de cambio y ofi==0 al 99.92%). Esto lo caza.

def is_corrupt_day(bid_px, bid_sz, ask_px, ask_sz, *, k: int = 5,
                   max_bsz_change_frac: float = 0.01, min_ofi_zero_frac: float = 0.90,
                   min_snapshots: int = 100) -> dict:
    """Detecta un día CHD CORRUPTO = libro reconstruido CONGELADO. Regla **AND, no OR**: el día es
    corrupto si AMBAS:
      (1) best-bid-size cambia en <`max_bsz_change_frac` (1%) de los snapshots → libro inmóvil, Y
      (2) ofi==0 en >`min_ofi_zero_frac` (90%) de los snapshots → sin flujo.
    El AND es deliberado: un día VÁLIDO con spread/size muy estable puede disparar (1) pero NO (2) — el
    OFI sigue vivo (hay precio y trades). Solo el congelamiento genuino dispara ambas. Con OR, esos días
    quietos-pero-vivos se marcarían corruptos por error.

    Caso degenerado: <`min_snapshots` snapshots reconstruidos = libro que ni maduró → corrupto.
    Validado en dato real (ATOM): jul-01-2025 (cambio 0.0000 / ofi==0 0.9992) → corrupto; ago-01-2025
    (0.4524 / 0.2251) y oct-01-2025 (0.2563 / 0.3924) → activos, no corruptos. Separación enorme: los
    umbrales 1%/90% caen en huecos amplios. Devuelve dict con las 2 métricas, los 2 flags y `corrupt`."""
    bsz = np.asarray(bid_sz, "float64")
    T = bsz.shape[0]
    if T < min_snapshots:
        return {"corrupt": True, "frozen_book": True, "dead_ofi": True,
                "bsz_change_frac": 0.0, "ofi_zero_frac": 1.0, "n_snapshots": int(T),
                "nota": f"libro degenerado (<{min_snapshots} snapshots)"}
    bb0 = bsz[:, 0]
    bsz_change_frac = float(np.mean(bb0[1:] != bb0[:-1]))
    o = book_ofi(bid_px, bid_sz, ask_px, ask_sz, levels=k)
    ofi_zero_frac = float(np.mean(o == 0.0))
    frozen_book = bool(bsz_change_frac < max_bsz_change_frac)
    dead_ofi = bool(ofi_zero_frac > min_ofi_zero_frac)
    return {"corrupt": bool(frozen_book and dead_ofi), "frozen_book": frozen_book, "dead_ofi": dead_ofi,
            "bsz_change_frac": bsz_change_frac, "ofi_zero_frac": ofi_zero_frac, "n_snapshots": int(T)}


def cryptohft_to_book_guarded(path_or_table, *, top_l: int = 10, sample_ms: int = 100, k: int = 5):
    """Como `cryptohft_to_book` pero con el guardia: reconstruye y, si el día está CORRUPTO (libro
    congelado), **FALLA FUERTE** lanzando `CorruptDayError` (con el report). El runner la captura para
    SALTAR el día con log — nunca devuelve un libro corrupto en silencio. Día limpio → (ts,bpx,bsz,apx,asz)."""
    ts, bpx, bsz, apx, asz = cryptohft_to_book(path_or_table, top_l=top_l, sample_ms=sample_ms)
    rep = is_corrupt_day(bpx, bsz, apx, asz, k=k)
    if rep["corrupt"]:
        raise CorruptDayError(rep)
    return ts, bpx, bsz, apx, asz
