"""analysis/cv.py — validación cruzada financiera (AFML cap. 7 y 12): purga, embargo,
Purged K-Fold y Combinatorial Purged Cross-Validation (CPCV).

EL PROBLEMA (AFML §7.3): la CV estándar FILTRA en finanzas porque las etiquetas se solapan
en el tiempo. Una etiqueta Y_i se decide sobre el intervalo [t0_i, t1_i] (p. ej. triple
barrera: desde la barra hasta que se toca una barrera). Si una observación de TRAIN tiene su
ventana de etiqueta solapada con la del TEST, el modelo "ve el futuro" → backtest inflado
que no existe fuera de muestra. Subir k mejora el resultado SOLO por la fuga (AFML §7.4.1).

LA SOLUCIÓN (AFML §7.4):
  • PURGA: quitar del train toda obs cuya ventana [t0,t1] solape la del test.
  • EMBARGO: quitar además las obs inmediatamente POSTERIORES al test (correlación serial);
    h ≈ 0.01·T suele bastar.
CPCV (AFML §12.4): en vez de UN camino de backtest, prueba combinaciones de k grupos de N
→ C(N,k) splits y **C(N-1,k-1) CAMINOS** de backtest. Esa distribución de caminos es la
materia prima de PBO y del Deflated Sharpe (los siguientes módulos del motor).

Fiel a los snippets 7.1 (getTrainTimes), 7.2 (getEmbargoTimes), 7.4.3 (PurgedKFold) y §12.4,
en numpy/índices (sin pandas). La condición de purga `t0<=j & t1>=i` es EXACTAMENTE la unión
de los tres casos df0/df1/df2 del snippet 7.1 (el train empieza dentro / termina dentro /
envuelve al test) — el solape de intervalos.
"""
from __future__ import annotations
from itertools import combinations
from math import comb
import numpy as np


def _test_blocks(test_idx: np.ndarray):
    """Bloques contiguos de índices de test (runs de índices consecutivos). El test de CPCV
    es unión de k grupos → puede ser no contiguo; cada bloque se purga por su intervalo."""
    ti = np.sort(np.asarray(test_idx))
    if len(ti) == 0:
        return []
    brk = np.where(np.diff(ti) > 1)[0]
    starts = np.concatenate([[0], brk + 1])
    ends = np.concatenate([brk, [len(ti) - 1]])
    return [(int(ti[s]), int(ti[e])) for s, e in zip(starts, ends)]


def purged_train_mask(t0: np.ndarray, t1: np.ndarray, test_idx, embargo_pct: float = 0.0,
                      embargo_steps: int | None = None):
    """Máscara booleana de TRAIN tras PURGA + EMBARGO (AFML §7.4), dado el conjunto de test.
    t0[i] = tiempo de la observación; t1[i] = tiempo en que se RESUELVE su etiqueta (t1>=t0).

    PURGA corta la fuga de ETIQUETAS (el modelo no ve el futuro vía el target). EMBARGO corta
    la fuga de FEATURES (vía rolling windows / autocorrelación). REGLA (refinamiento sobre el
    embargo básico de AFML): el embargo debe ser ≥ max(lookback del feature más largo,
    horizonte de decaimiento de la autocorrelación) — si usas un rolling de 60 barras, un
    embargo menor deja que el train vea el test A TRAVÉS del feature. Por eso se puede fijar
    en barras ABSOLUTAS (`embargo_steps`), no solo como fracción `embargo_pct` (AFML usa
    fracción; aquí se permite lo más correcto)."""
    t0 = np.asarray(t0, dtype="float64")
    t1 = np.asarray(t1, dtype="float64")
    n = len(t0)
    train = np.ones(n, dtype=bool)
    train[np.asarray(test_idx)] = False
    step = int(embargo_steps) if embargo_steps is not None else int(n * embargo_pct)
    for a, b in _test_blocks(np.asarray(test_idx)):
        i, j = t0[a], t1[b]                               # intervalo temporal del bloque de test
        train &= ~((t0 <= j) & (t1 >= i))                # PURGA: solape de etiquetas
        if step > 0:
            train[b + 1: min(b + 1 + step, n)] = False    # EMBARGO: obs tras el test
    return train


def purged_kfold(t0: np.ndarray, t1: np.ndarray, n_splits: int = 5,
                 embargo_pct: float = 0.0, embargo_steps: int | None = None):
    """K-Fold PURGADO (AFML §7.4.3): cada fold contiguo es el test; el train es el resto,
    purgado + embargado. Genera (train_idx, test_idx)."""
    if n_splits < 2:
        raise ValueError("n_splits debe ser ≥ 2")
    n = len(t0)
    bd = np.linspace(0, n, n_splits + 1).astype(int)
    for s in range(n_splits):
        test_idx = np.arange(bd[s], bd[s + 1])
        train = purged_train_mask(t0, t1, test_idx, embargo_pct, embargo_steps)
        yield np.where(train)[0], test_idx


def cpcv_splits(t0: np.ndarray, t1: np.ndarray, n_groups: int = 6, k_test: int = 2,
                embargo_pct: float = 0.0, embargo_steps: int | None = None):
    """Combinatorial Purged CV (AFML §12.4): test sobre cada combinación de `k_test` grupos
    de `n_groups` (C(N,k) splits), train purgado + embargado. Genera
    (train_idx, test_idx, grupos_test)."""
    if not 1 <= k_test < n_groups:
        raise ValueError("se requiere 1 ≤ k_test < n_groups")
    n = len(t0)
    bd = np.linspace(0, n, n_groups + 1).astype(int)
    groups = [np.arange(bd[g], bd[g + 1]) for g in range(n_groups)]
    for combo in combinations(range(n_groups), k_test):
        test_idx = np.sort(np.concatenate([groups[g] for g in combo]))
        train = purged_train_mask(t0, t1, test_idx, embargo_pct, embargo_steps)
        yield np.where(train)[0], test_idx, combo


def n_backtest_paths(n_groups: int, k_test: int) -> int:
    """Nº de CAMINOS de backtest de CPCV = C(N-1, k-1) (AFML §12.4.2). Cada grupo participa
    en exactamente este nº de splits de test → se recombinan en esos caminos."""
    return comb(n_groups - 1, k_test - 1)
