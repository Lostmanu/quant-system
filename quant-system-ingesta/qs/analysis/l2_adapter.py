"""analysis/l2_adapter.py — reconstrucción de libro L2 desde diffs → forma normalizada.

Convierte un flujo de DIFFs incrementales en una serie de snapshots de libro top-L en la
representación normalizada de `book.py` (bid_px/bid_sz/ask_px/ask_sz [T,L]). Soporta el
formato de Tardis (`incremental_book_L2`: filas largas timestamp,is_snapshot,side,price,
amount) y sirve de plantilla para el de nuestra captura propia (writer.py, arrays por
update con update-ids) — ambos colapsan al MISMO libro reconstruido.

Algoritmo (estándar de libro incremental): mantener {precio: cantidad} por lado; cada fila
fija el nivel (amount>0) o lo borra (amount==0); un `is_snapshot` nuevo tras diffs reinicia
el libro. En puntos de muestreo se extraen los top-L niveles ordenados (bid desc, ask asc).

NOTA: la reconstrucción de NUESTRO formato (con first/final/prev_final_update_id) debe
validar la continuidad de update-ids (detectar gaps) — eso va en su adaptador propio,
contra L2 real; aquí queda el de Tardis, validado contra su muestra gratuita.
"""
from __future__ import annotations
import gzip
import numpy as np


def iter_tardis_l2(path: str):
    """Itera (ts_us, is_snapshot, side, price, amount) de un .csv.gz de Tardis."""
    with gzip.open(path, "rt") as f:
        f.readline()                                         # cabecera
        for line in f:
            p = line.rstrip("\n").split(",")
            # exchange,symbol,timestamp,local_timestamp,is_snapshot,side,price,amount
            yield int(p[2]), p[4] == "true", p[5], float(p[6]), float(p[7])


def reconstruct(rows, top_l: int = 10, sample_every: int = 2000, max_rows=None):
    """Reconstruye el libro y muestrea cada `sample_every` updates. Devuelve
    (ts[T], bid_px[T,L], bid_sz[T,L], ask_px[T,L], ask_sz[T,L]) con bid_px DESC, ask_px ASC.
    Solo emite snapshots con ≥ top_l niveles por lado (libro maduro)."""
    bids: dict[float, float] = {}
    asks: dict[float, float] = {}
    prev_snap = False
    ts_l, bpx, bsz, apx, asz = [], [], [], [], []
    for i, (ts, is_snap, side, price, amount) in enumerate(rows):
        if max_rows is not None and i >= max_rows:
            break
        if is_snap and not prev_snap:                        # snapshot nuevo → reinicia libro
            bids.clear(); asks.clear()
        prev_snap = is_snap
        book = bids if side == "bid" else asks
        if amount == 0.0:
            book.pop(price, None)
        else:
            book[price] = amount
        if (i + 1) % sample_every == 0 and len(bids) >= top_l and len(asks) >= top_l:
            bb = sorted(bids.items(), key=lambda kv: -kv[0])[:top_l]   # mejores bids (desc)
            aa = sorted(asks.items(), key=lambda kv: kv[0])[:top_l]    # mejores asks (asc)
            if bb[0][0] >= aa[0][0]:
                continue            # libro bloqueado/cruzado (nivel stale transitorio): se salta
            ts_l.append(ts)
            bpx.append([p for p, _ in bb]); bsz.append([s for _, s in bb])
            apx.append([p for p, _ in aa]); asz.append([s for _, s in aa])
    arr = lambda x: np.array(x, "float64")
    return (np.array(ts_l, "int64"), arr(bpx), arr(bsz), arr(apx), arr(asz))


def reconstruct_tardis_file(path: str, **kw):
    """Atajo: reconstruye directamente desde un .csv.gz de Tardis."""
    return reconstruct(iter_tardis_l2(path), **kw)


def qs_depth_to_book(bid_prices, bid_volumes, ask_prices, ask_volumes):
    """Captura PROPIA (`@depth10@100ms`, writer.py): cada fila ya es un snapshot top-L
    consistente (bid desc, ask asc) → NO necesita reconstrucción (a diferencia de los diffs
    de Tardis); solo se apila a arrays [T,L] para `book.py`. Validado contra muestra real de
    la VPS: libro no cruzado, features sanas, top-10 = D_10 del Plan/H3."""
    arr = lambda col: np.array([list(r) for r in col], dtype="float64")
    return arr(bid_prices), arr(bid_volumes), arr(ask_prices), arr(ask_volumes)


def update_id_gaps(prev_final_update_id, final_update_id) -> int:
    """Control de CALIDAD de la captura: nº de rupturas de continuidad
    (prev_final[i+1] != final[i]) en el stream de Binance. gaps=0 ⇒ no se perdió ningún
    mensaje (verificado en la muestra real: 0 gaps)."""
    pf = np.asarray(prev_final_update_id)
    fn = np.asarray(final_update_id)
    return int((pf[1:] != fn[:-1]).sum())
