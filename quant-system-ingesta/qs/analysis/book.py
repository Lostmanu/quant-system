"""analysis/book.py — Features de libro L2 (cimiento de H1/H3, pivote a liquidez).

Las features que los datos de TRADE no podían dar (y por las que VPIN/cross-sectional
fallaron): el **mid limpio** y el **microprice** sin bid-ask bounce, la **profundidad**
por banda, el **imbalance** del libro y —lo realmente adaptado a cripto fino— la
**resiliencia** (velocidad de recuperación del libro tras un golpe; en book_resilience,
sobre series temporales de snapshots).

Representación NORMALIZADA de un snapshot de libro (fuente-agnóstica: vale igual para
nuestra captura propia y para Tardis, que entran por un adaptador distinto):
    bid_px, bid_sz : [T, L]  — L niveles bid, columna 0 = mejor bid, precio DESCENDENTE
    ask_px, ask_sz : [T, L]  — L niveles ask, columna 0 = mejor ask, precio ASCENDENTE
T snapshots × L niveles. Todas las features son CAUSALES por snapshot (solo usan el
estado del libro en ese instante); las de serie temporal lo dicen explícitamente.

NOTA DE ALCANCE: nuestro L2 se captura como DIFFs incrementales (writer.py:
first/final/prev_final_update_id). La reconstrucción diff→libro (aplicar diffs en orden
desde un snapshot) NO está aquí: es un adaptador aparte que debe validarse contra L2
REAL (reutiliza la lógica de `ingestion/audit.py`, ya probada en producción). Este
módulo asume el libro YA reconstruido en la forma normalizada de arriba.
"""
from __future__ import annotations
import numpy as np


def _check(bid_px, bid_sz, ask_px, ask_sz) -> None:
    arrs = (bid_px, bid_sz, ask_px, ask_sz)
    if len({a.shape for a in arrs}) != 1:
        raise ValueError("bid/ask precios y volúmenes deben tener la misma forma [T,L]")
    if bid_px.ndim != 2:
        raise ValueError("se esperan matrices [T, L] (T snapshots × L niveles)")
    if not all(np.isfinite(a).all() for a in arrs):
        raise ValueError("libro con NaN o inf")


def mid(bid_px: np.ndarray, ask_px: np.ndarray) -> np.ndarray:
    """Mid limpio (best_bid + best_ask)/2. Sin bid-ask bounce (a diferencia del precio
    de trade): es el ancla de precio que faltaba en el análisis de solo-trades."""
    return (bid_px[:, 0] + ask_px[:, 0]) / 2.0


def relative_spread(bid_px: np.ndarray, ask_px: np.ndarray) -> np.ndarray:
    """Spread relativo (ask−bid)/mid. Medida directa del coste de cruzar y proxy de
    iliquidez instantánea."""
    return (ask_px[:, 0] - bid_px[:, 0]) / mid(bid_px, ask_px)


def microprice(bid_px, bid_sz, ask_px, ask_sz) -> np.ndarray:
    """Microprice de Stoikov: (P_b·Q_a + P_a·Q_b)/(Q_a+Q_b). Pondera hacia el lado con
    MENOS tamaño → se desplaza en la dirección de la presión. Mejor predictor del
    próximo mid que el mid mismo. Con ambos tamaños 0, cae al mid."""
    b, a = bid_px[:, 0], ask_px[:, 0]
    qb, qa = bid_sz[:, 0], ask_sz[:, 0]
    w = qb + qa
    ws = np.where(w > 0, w, 1.0)                              # evita 0/0 en la rama no usada
    return np.where(w > 0, (b * qa + a * qb) / ws, (b + a) / 2.0)


def book_imbalance(bid_sz: np.ndarray, ask_sz: np.ndarray, k: int = 1) -> np.ndarray:
    """Imbalance de volumen de los k mejores niveles: (ΣQ_b − ΣQ_a)/(ΣQ_b + ΣQ_a) ∈
    [−1, 1]. >0 = presión compradora. Con ambos lados vacíos, 0."""
    if k < 1:
        raise ValueError("k debe ser ≥ 1")
    b = bid_sz[:, :k].sum(axis=1)
    a = ask_sz[:, :k].sum(axis=1)
    t = b + a
    return np.where(t > 0, (b - a) / t, 0.0)


def depth_within(bid_px, bid_sz, ask_px, ask_sz, delta: float):
    """Profundidad dentro de una banda ±`delta` (relativa) alrededor del mid (la D_δ del
    Plan/H3). Devuelve (D_bid, D_ask): suma de volumen con precio dentro de la banda en
    cada lado. Mide cuánto capital absorbe el libro antes de mover el precio `delta`."""
    if delta <= 0:
        raise ValueError("delta debe ser > 0")
    _check(bid_px, bid_sz, ask_px, ask_sz)
    m = mid(bid_px, ask_px)[:, None]
    lo, hi = m * (1.0 - delta), m * (1.0 + delta)
    d_bid = np.where(bid_px >= lo, bid_sz, 0.0).sum(axis=1)   # bids dentro de la banda
    d_ask = np.where(ask_px <= hi, ask_sz, 0.0).sum(axis=1)   # asks dentro de la banda
    return d_bid, d_ask


def depth_imbalance(bid_px, bid_sz, ask_px, ask_sz, delta: float) -> np.ndarray:
    """Imbalance de profundidad dentro de la banda ±delta: (D_bid−D_ask)/(D_bid+D_ask)."""
    d_bid, d_ask = depth_within(bid_px, bid_sz, ask_px, ask_sz, delta)
    t = d_bid + d_ask
    return np.where(t > 0, (d_bid - d_ask) / t, 0.0)


def book_resilience(depth: np.ndarray, drop: float = 0.5, horizon: int = 50):
    """Resiliencia (ADAPTADO a cripto fino, no es del manual): tras una CAÍDA de la
    profundidad ≥ `drop` (fracción) respecto a su media móvil previa, ¿cuántos snapshots
    tarda en recuperar la mitad del nivel perdido (vida media de recuperación)?
    `depth` es una serie temporal de profundidad total (p. ej. D_bid+D_ask). Devuelve la
    mediana del tiempo de recuperación sobre los eventos de caída (NaN si no hay eventos).
    Estrictamente causal: cada evento mira hacia ADELANTE solo `horizon` snapshots, y el
    nivel de referencia se toma de ANTES de la caída.

    Mecanismo (H1): los makers se retiran ante toxicidad → el libro pierde capacidad de
    absorción → resiliencia decreciente PRESAGIA la ruptura. Velocidad de recuperación
    como termómetro de salud del libro, en un mercado donde la finura es la regla."""
    T = len(depth)
    if T < horizon + 2:
        return float("nan"), np.array([], dtype="int64")
    ref = np.empty(T)                                        # media móvil causal previa
    win = max(horizon, 10)
    csum = np.concatenate([[0.0], np.cumsum(depth)])
    for t in range(T):
        s = max(0, t - win)
        ref[t] = (csum[t] - csum[s]) / max(t - s, 1)
    times = []
    t = 1
    while t < T - horizon:
        if ref[t] > 0 and depth[t] <= (1.0 - drop) * ref[t]:  # caída detectada
            target = depth[t] + drop * ref[t] * 0.5           # recupera la mitad
            rec = np.where(depth[t + 1:t + 1 + horizon] >= target)[0]
            if len(rec):
                times.append(int(rec[0] + 1))
            t += horizon                                      # no solapar eventos
        else:
            t += 1
    times = np.array(times, dtype="int64")
    return (float(np.median(times)) if len(times) else float("nan")), times


def ofi(bid_px, bid_sz, ask_px, ask_sz, levels: int = 1) -> np.ndarray:
    """Order Flow Imbalance (Cont–Kukanov–Stoikov 2014), CRUDO por snapshot. Maneja los
    MOVIMIENTOS del mejor precio con las tres ramas canónicas — NO el ΔQ ingenuo, que en cripto
    fino (la cotización salta a menudo) compararía volúmenes en niveles de precio distintos =
    basura. `levels`=k suma el OFI de los k primeros niveles (MLOFI). out[0]=0 (sin par previo).

      bid:  +Q_b[n]            si P_b[n] > P_b[n-1]  (precio sube → demanda añadida)
            Q_b[n]−Q_b[n-1]    si P_b[n] = P_b[n-1]
            −Q_b[n-1]          si P_b[n] < P_b[n-1]  (precio baja → demanda retirada)
      ask:  +Q_a[n]            si P_a[n] < P_a[n-1]  (precio baja → oferta añadida)
            Q_a[n]−Q_a[n-1]    si P_a[n] = P_a[n-1]
            −Q_a[n-1]          si P_a[n] > P_a[n-1]
      OFI_l = bid − ask ; >0 = presión compradora neta. (La normalización por profundidad se hace
      en h1_io, no aquí: este es el primitivo crudo, testeable con números limpios.)"""
    bid_px = np.asarray(bid_px, "float64"); bid_sz = np.asarray(bid_sz, "float64")
    ask_px = np.asarray(ask_px, "float64"); ask_sz = np.asarray(ask_sz, "float64")
    T = bid_px.shape[0]
    out = np.zeros(T)
    for l in range(min(levels, bid_px.shape[1])):
        Pb, Qb, Pa, Qa = bid_px[:, l], bid_sz[:, l], ask_px[:, l], ask_sz[:, l]
        eb = np.zeros(T); ea = np.zeros(T)
        eb[1:] = np.where(Pb[1:] > Pb[:-1], Qb[1:],
                          np.where(Pb[1:] == Pb[:-1], Qb[1:] - Qb[:-1], -Qb[:-1]))
        ea[1:] = np.where(Pa[1:] < Pa[:-1], Qa[1:],
                          np.where(Pa[1:] == Pa[:-1], Qa[1:] - Qa[:-1], -Qa[:-1]))
        out += eb - ea
    return out
