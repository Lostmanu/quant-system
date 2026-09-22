"""analysis/haircut.py — haircut del Sharpe por comparaciones múltiples (Harvey-Liu 2015).

Tercera parte del MOTOR DE VALIDACIÓN. DSR/PBO corrigen el sobreajuste DENTRO de un estudio;
el haircut corrige la inferencia ACUMULADA: cuántos tests (propios y de la literatura)
buscaron algo parecido sobre datos parecidos. Con N tests, el máximo de N normales bajo la
nula ya supera t=2 con holgura → un t-stat "significativo" puede no valer nada.

Framework (Harvey-Liu, ec. 1 + def. de HSR):
  t = SR·√T  ⟺  SR = t/√T   (T = nº de observaciones, NO anualizado)
  pS = Pr(|r| > t)           (p-value de un test único, dos colas)
  pM = ajuste de pS por N tests (Bonferroni / Holm / BHY)
  HSR = t*/√T  con  t* = Φ⁻¹(1 − pM/2)   (Sharpe deshinchado)
  haircut = (SR − HSR) / SR

HALLAZGO de Harvey-Liu: el haircut es NO LINEAL — los Sharpe altos se penalizan poco (ya
superan la nula con holgura) y los marginales a casi cero (probablemente ruido). La regla
del 50 % de la industria es arbitraria y económicamente incorrecta.

Tres métodos (de más a menos conservador): Bonferroni (FWER, sin supuestos de dependencia) >
Holm (FWER, secuencial) > BHY (Benjamini-Yekutieli, FDR bajo dependencia ARBITRARIA — el
recomendado para backtesting, porque las estrategias están correlacionadas). Fiel a las
defs. del paper; BY = `fdr_by` estándar (factor de dependencia c(M)=Σ1/i ≈ ln M + γ).
"""
from __future__ import annotations
import math
import numpy as np
from analysis.overfit import _norm_cdf, _norm_ppf


def sharpe_to_t(sharpe: float, n: int) -> float:
    """t-ratio = SR·√T (Harvey-Liu ec. 1). n = nº de observaciones, SR no anualizado."""
    return sharpe * math.sqrt(n)


def t_to_pvalue(t: float) -> float:
    """p-value de un test único, dos colas: pS = Pr(|r| > t) = 2·(1 − Φ(|t|))."""
    return 2.0 * (1.0 - _norm_cdf(abs(t)))


def harmonic_c(m: int) -> float:
    """Factor de dependencia de BHY: c(M) = Σ_{j=1}^{M} 1/j ≈ ln(M) + γ_EM."""
    return float(np.sum(1.0 / np.arange(1, m + 1)))


def bonferroni(pvals: np.ndarray) -> np.ndarray:
    """p-values ajustados por Bonferroni (FWER): min(M·p, 1). El más conservador."""
    p = np.asarray(pvals, dtype="float64")
    return np.minimum(len(p) * p, 1.0)


def holm(pvals: np.ndarray) -> np.ndarray:
    """p-values ajustados por Holm (FWER, secuencial step-down): ordena ascendente y aplica
    (M−i+1)·p_(i) con monotonía no decreciente (cumulative max). Menos conservador que Bonf."""
    p = np.asarray(pvals, dtype="float64")
    m = len(p)
    order = np.argsort(p)
    raw = (m - np.arange(m)) * p[order]                 # (M−i+1)·p_(i), i=1..M
    adj = np.clip(np.maximum.accumulate(raw), 0.0, 1.0)
    out = np.empty(m)
    out[order] = adj
    return out


def bhy(pvals: np.ndarray) -> np.ndarray:
    """p-values ajustados por Benjamini-Yekutieli (FDR bajo dependencia ARBITRARIA), el
    recomendado por Harvey-Liu para backtesting. Ordena ascendente, factor M·c(M)/i con
    monotonía (cumulative min desde el mayor rango). Menos conservador → haircuts razonables
    para Sharpes altos."""
    p = np.asarray(pvals, dtype="float64")
    m = len(p)
    c = harmonic_c(m)
    order = np.argsort(p)
    raw = p[order] * m * c / np.arange(1, m + 1)         # p_(i)·M·c(M)/i
    adj = np.clip(np.minimum.accumulate(raw[::-1])[::-1], 0.0, 1.0)
    out = np.empty(m)
    out[order] = adj
    return out


def haircut_sharpe(sharpe: float, n: int, p_adjusted: float):
    """Dado el p-value AJUSTADO por multiple testing, devuelve (HSR, haircut): el Sharpe
    deshinchado HSR = t*/√n con t* = Φ⁻¹(1 − p_adj/2), y el haircut (SR−HSR)/SR ∈ [0,1]."""
    t_star = max(_norm_ppf(1.0 - p_adjusted / 2.0), 0.0)
    hsr = t_star / math.sqrt(n)
    haircut = (sharpe - hsr) / sharpe if sharpe > 0 else 1.0
    return hsr, max(min(haircut, 1.0), 0.0)


def haircut_bonferroni(sharpe: float, n: int, n_tests: int):
    """Atajo para una sola estrategia con `n_tests` ensayos (incluida la literatura): aplica
    Bonferroni a su p-value y devuelve (HSR, haircut). Conservador, pero solo necesita N."""
    p_adj = min(n_tests * t_to_pvalue(sharpe_to_t(sharpe, n)), 1.0)
    return haircut_sharpe(sharpe, n, p_adj)
