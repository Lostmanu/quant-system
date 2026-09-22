"""analysis/labeling.py — etiquetado triple-barrera, meta-labeling y bet sizing (AFML §3 y §10.3).

Cuarta parte del MOTOR. Separa dos problemas que un modelo único mezcla y por eso sobreajusta:
el LADO (dirección) y el TAMAÑO (cuánto fiarse). Tres piezas encadenadas (López de Prado):
  • M1 (modelo primario, p. ej. una regla económica o un clasificador) decide el side.
  • M2 (meta-labeler) decide si ese side ACERTARÁ → filtra falsos positivos (target 0/1).
  • M3 (bet sizing) traduce la probabilidad del M2 a tamaño de posición.

Aquí va el NÚCLEO determinista y testeable (fiel a los snippets 3.x de AFML y a §10.3):
  • `triple_barrier` — etiqueta cada evento por la primera barrera tocada (TP/SL/vertical).
  • `meta_label` — el target 0/1 del meta-labeler (¿acertó el side de M1?).
  • `bet_size` — tamaño de apuesta sigmoid-CDF (§10.3): bet=0 sin edge, curva en S.

Los clasificadores M1/M2 son envoltorios estándar (sklearn) que se conectan cuando haya
features reales; la VALIDACIÓN del pipeline reusa `cv.py` (CPCV), `overfit.py` (DSR/PBO real)
y `haircut.py` (BHY real) — NO se reimplementan aquí.
"""
from __future__ import annotations
import numpy as np
from analysis.overfit import _norm_cdf


def triple_barrier(prices: np.ndarray, event_idx, vert_idx, target,
                   pt_mult: float = 1.0, sl_mult: float = 1.0):
    """Método de triple barrera (AFML §3). Para cada evento (índice en `event_idx`, con su
    barrera vertical en `vert_idx`) busca cuál barrera se toca PRIMERO: take-profit a
    +pt_mult·target, stop-loss a −sl_mult·target, o la vertical (tiempo). Devuelve
    (barrier[n], ret[n]) con barrier ∈ {+1 TP, −1 SL, 0 vertical} y `ret` el retorno (long)
    en el toque. pt_mult/sl_mult=0 desactiva esa barrera horizontal."""
    prices = np.asarray(prices, dtype="float64")
    ev = np.asarray(event_idx, dtype="int64")
    vt = np.asarray(vert_idx, dtype="int64")
    tg = np.asarray(target, dtype="float64")
    n = len(ev)
    barrier = np.zeros(n, dtype="int64")
    ret = np.zeros(n)
    for i in range(n):
        e, v = int(ev[i]), int(vt[i])
        r = prices[e:v + 1] / prices[e] - 1.0
        pt, sl = pt_mult * tg[i], -sl_mult * tg[i]
        hit_pt = pt_mult > 0 and bool((r >= pt).any())
        hit_sl = sl_mult > 0 and bool((r <= sl).any())
        j_pt = int(np.argmax(r >= pt)) if hit_pt else len(r)
        j_sl = int(np.argmax(r <= sl)) if hit_sl else len(r)
        if not hit_pt and not hit_sl:
            barrier[i], ret[i] = 0, r[-1]                  # vertical (tiempo)
        elif j_pt <= j_sl:
            barrier[i], ret[i] = 1, r[j_pt]                # take-profit primero
        else:
            barrier[i], ret[i] = -1, r[j_sl]               # stop-loss primero
    return barrier, ret


def meta_label(side, ret) -> np.ndarray:
    """Target del meta-labeler (AFML meta-labeling): 1 si el side predicho ACERTÓ
    (side·ret > 0), 0 si fue un falso positivo de M1. El M2 aprende a filtrar los 0."""
    return (np.asarray(side, dtype="float64") * np.asarray(ret, dtype="float64") > 0).astype(int)


def bet_size(p) -> np.ndarray:
    """Tamaño de apuesta desde la probabilidad del M2 (AFML §10.3, sigmoid CDF):
    z = (p−0.5)/√(p(1−p)),  bet = 2·Φ(z) − 1 ∈ [0,1]. Propiedad clave: bet=0 cuando p=0.5
    (sin convicción, sin apuesta); curva en S que acelera hacia los extremos."""
    p = np.clip(np.asarray(p, dtype="float64"), 1e-9, 1 - 1e-9)
    z = (p - 0.5) / np.sqrt(p * (1 - p))
    cdf = (_norm_cdf(float(z)) if z.ndim == 0
           else np.array([_norm_cdf(float(v)) for v in z]))
    return np.clip(2.0 * cdf - 1.0, 0.0, 1.0)
