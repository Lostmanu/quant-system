"""analysis/overfit.py — deflación del Sharpe y probabilidad de sobreajuste del backtest.

Segunda parte del MOTOR DE VALIDACIÓN. Tres herramientas para separar hallazgos reales de
flukes estadísticos, fieles a Bailey-López de Prado:

  • PSR — Probabilistic Sharpe Ratio (Bailey-LdP): P[SR_real > benchmark], corrigiendo por
    nº de retornos, asimetría y curtosis (no-normalidad).
  • DSR — Deflated Sharpe Ratio (Bailey-LdP 2014): PSR con el benchmark = E[máx SR] tras N
    ensayos → corrige la SELECCIÓN por multiple testing. Un Sharpe alto encontrado tras
    miles de pruebas no es significativo; el DSR lo deshincha.
  • PBO — Probability of Backtest Overfitting vía CSCV (Bailey-Borwein-LdP-Zhu 2015):
    sobre una matriz T×N (periodos × estrategias), fracción de particiones IS/OOS donde la
    mejor estrategia in-sample cae por debajo de la mediana out-of-sample. >0.5 ⇒ sobreajuste
    probable; <0.1 ⇒ robusto.

Fórmulas verbatim de los papers (docs/papers/): PSR y E[máx SR] (BaileyLopezDePrado-2014,
ec. de §«expected maximum» + snippet getExpectedMaxSR), CSCV (Algoritmo 2.3). Sin scipy:
normal propia (erf + Acklam) para no añadir dependencias.
"""
from __future__ import annotations
from itertools import combinations
import math
import numpy as np

EULER_MASCHERONI = 0.5772156649015329


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    """Inversa de la normal estándar (aprox. de Acklam, error < 1e-9)."""
    if p <= 0.0:
        return -math.inf
    if p >= 1.0:
        return math.inf
    a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00)
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def psr(sharpe: float, n: int, skew: float = 0.0, kurt: float = 3.0,
        sr_benchmark: float = 0.0) -> float:
    """Probabilistic Sharpe Ratio: P[SR_real > sr_benchmark]. `sharpe` y `sr_benchmark` en
    la MISMA frecuencia (NO anualizados); n = nº de retornos; skew/kurt de los retornos
    (curtosis normal = 3). PSR>0.95 ⇒ el SR supera el benchmark con 95 % de confianza."""
    denom = math.sqrt(1.0 - skew * sharpe + (kurt - 1.0) / 4.0 * sharpe ** 2)
    return _norm_cdf((sharpe - sr_benchmark) * math.sqrt(n - 1.0) / denom)


def expected_max_sharpe(n_trials: int, sr_std: float = 1.0, sr_mean: float = 0.0) -> float:
    """E[máx SR] tras `n_trials` ensayos independientes (Bailey-LdP 2014, apéndice 1) — el
    benchmark de deflación. = sr_mean + sr_std·[(1−γ)·Z⁻¹(1−1/N) + γ·Z⁻¹(1−1/(N·e))]."""
    if n_trials < 2:
        raise ValueError("n_trials debe ser ≥ 2")
    g = EULER_MASCHERONI
    maxz = ((1 - g) * _norm_ppf(1 - 1.0 / n_trials)
            + g * _norm_ppf(1 - 1.0 / (n_trials * math.e)))
    return sr_mean + sr_std * maxz


def deflated_sharpe(sharpe: float, n: int, n_trials: int, sr_std: float,
                    skew: float = 0.0, kurt: float = 3.0) -> float:
    """Deflated Sharpe Ratio (Bailey-LdP 2014): PSR con benchmark = E[máx SR] de `n_trials`
    ensayos cuya dispersión de Sharpes es `sr_std`. Corrige selección (multiple testing) +
    no-normalidad. DSR>0.95 ⇒ el Sharpe NO es un fluke esperable tras tantos ensayos."""
    return psr(sharpe, n, skew, kurt, expected_max_sharpe(n_trials, sr_std))


def effective_n_trials(n_trials: int, mean_corr: float) -> float:
    """Nº EFECTIVO de ensayos cuando las estrategias están correlacionadas (variantes del
    mismo modelo): N_eff = N·(1−ρ̄) + ρ̄ (aprox. de López de Prado-Lewis 2019; la versión
    rigurosa usa clustering). ρ̄ = correlación media de los retornos entre estrategias.
    ρ̄→1 ⇒ N_eff→1 (todos el mismo ensayo); ρ̄→0 ⇒ N_eff→N. Usar N en vez de N_eff
    SOBREPENALIZA el DSR (conservador). Se pasa el resultado como `n_trials` al DSR."""
    return max(n_trials * (1.0 - mean_corr) + mean_corr, 1.0)


def min_track_record_length(sharpe: float, target_prob: float = 0.95, skew: float = 0.0,
                            kurt: float = 3.0, sr_benchmark: float = 0.0) -> float:
    """Minimum Track Record Length (Bailey-LdP): nº mínimo de observaciones para que el
    Sharpe supere `sr_benchmark` con probabilidad `target_prob` (la INVERSA del PSR). Clave
    para el filtro de viabilidad (§4.1): ¿nuestra longitud de datos SOPORTA detectar el edge
    antes de buscarlo? Ej.: SR≈0.95 anualizado diario → ~756 días (~3 años). sharpe per-
    periodo; requiere sharpe > sr_benchmark."""
    if sharpe <= sr_benchmark:
        return math.inf
    moment = 1.0 - skew * sharpe + (kurt - 1.0) / 4.0 * sharpe ** 2
    return 1.0 + moment * (_norm_ppf(target_prob) / (sharpe - sr_benchmark)) ** 2


def _sharpe_cols(block: np.ndarray) -> np.ndarray:
    mu = block.mean(axis=0)
    sd = block.std(axis=0)
    return np.where(sd > 0, mu / np.where(sd > 0, sd, 1.0), 0.0)


def pbo(perf: np.ndarray, n_splits: int = 16):
    """Probability of Backtest Overfitting vía CSCV (Bailey-Borwein-LdP-Zhu 2015, Alg. 2.3).
    `perf`: matriz T×N de performance POR PERIODO de N estrategias/configuraciones. Parte las
    T filas en S=`n_splits` submatrices (S par), prueba las C(S,S/2) combinaciones IS/OOS, y
    para cada una mide el rango OOS de la MEJOR estrategia in-sample. Devuelve (pbo, logits):
    PBO = fracción con la mejor-IS por DEBAJO de la mediana OOS (logit ≤ 0). >0.5 sobreajuste,
    <0.1 robusto."""
    M = np.asarray(perf, dtype="float64")
    if M.ndim != 2 or M.shape[1] < 2:
        raise ValueError("perf debe ser T×N con N ≥ 2 estrategias")
    if n_splits % 2 != 0 or n_splits < 2:
        raise ValueError("n_splits (S) debe ser par y ≥ 2")
    T, N = M.shape
    parts = np.array_split(np.arange(T - T % n_splits), n_splits)
    logits = []
    for combo in combinations(range(n_splits), n_splits // 2):
        cs = set(combo)
        is_rows = np.concatenate([parts[s] for s in combo])
        oos_rows = np.concatenate([parts[s] for s in range(n_splits) if s not in cs])
        n_star = int(np.argmax(_sharpe_cols(M[is_rows])))     # mejor estrategia IS
        sr_oos = _sharpe_cols(M[oos_rows])
        rank = int((sr_oos < sr_oos[n_star]).sum()) + 1       # rango OOS (1=peor … N=mejor)
        omega = min(max(rank / (N + 1.0), 1e-9), 1 - 1e-9)
        logits.append(math.log(omega / (1 - omega)))
    logits = np.array(logits)
    return float((logits <= 0).mean()), logits
