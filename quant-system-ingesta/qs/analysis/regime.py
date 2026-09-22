"""analysis/regime.py — Clasificación exógena de régimen (Plan Maestro §2.1).

Segmenta el mercado en 4 estados con dos métricas sobre una ventana retrospectiva
móvil de N observaciones (aquí, barras information-driven de bars.py):

  • Volatilidad — Z-score CAUSAL de la desviación estándar:
        Z_σ(t) = (σ_local(t) − μ_σ(<t)) / σ_σ(<t)
    σ_local(t) = std de los retornos a 1 paso en la ventana actual; μ_σ(<t) y
    σ_σ(<t) = media y std de σ_local con ventana EXPANSIVA usando EXCLUSIVAMENTE
    datos anteriores a t. Esta causalidad estricta es la corrección central del
    Plan (la v2.0 normalizaba con todo el dataset → sesgo de anticipación que
    invalida silenciosamente cualquier backtest). Burn-in: las primeras `burn_in`
    observaciones acumulan normalización pero NO emiten régimen (-1).

  • Estructura direccional — Variance Ratio INSESGADO de Lo-MacKinlay (1988):
    sobre la ventana N (ver variance_ratio). VR>1 persistencia (tendencia); VR<1
    reversión (rango); 1.0 es el punto neutro intrínseco (NO es un z-score). Se usa
    el estimador insesgado, no el simple Var(r^k)/(k·Var(r¹)) que el Plan escribe en
    su forma de libro: el simple está sesgado a la baja en muestra finita y
    descentraría la banda de histéresis (adenda Plan v2.2, 2026-06-17).

Anti flip-flop: histéresis (entrar/salir con umbrales distintos) + permanencia
mínima (un cambio de régimen solo se acepta si la condición se sostiene N_dwell
observaciones consecutivas). Defaults del Plan (k=50, N=2000, dwell=100,
umbrales 1.1/0.9 y 1.05/0.95); TODOS calibrables en Fase 5 — aquí son
placeholders, no optimizados.

4 regímenes:  1=alta vol+tendencia  2=alta vol+rango  3=baja vol+tendencia
              4=baja vol+rango   (-1 = burn-in / no evaluable)

Toda la clasificación es estrictamente CAUSAL: regime[t] depende solo de
close[0..t] (verificado por test de invarianza ante truncamiento).

Uso:  python analysis/regime.py --symbol AVAXUSDT [--bars dollar_standard]
"""
from __future__ import annotations
import numpy as np

REGIME = {("high", "trend"): 1, ("high", "range"): 2,
          ("low", "trend"): 3, ("low", "range"): 4}
BURN = -1
# Suelo de volatilidad REAL: por debajo de esto (retornos esencialmente idénticos),
# σ_local es roundoff de log/exp y el z-score amplificaría ruido numérico a valores
# espurios. Muy por debajo de cualquier vol real (~1e-4 a 1e-2), muy por encima del
# roundoff (~1e-16). Sirve para no clasificar ruido como régimen.
MIN_SIGMA = 1e-10


def volatility_zscore(close: np.ndarray, N: int) -> tuple[np.ndarray, np.ndarray]:
    """(σ_local, Z_σ). Z_σ(t) usa σ_local de índices ESTRICTAMENTE anteriores a t."""
    M = len(close)
    logp = np.log(close)
    r1 = np.diff(logp)                       # retornos a 1 paso, longitud M-1
    sigma = np.full(M, np.nan)
    z = np.full(M, np.nan)
    for t in range(N, M):
        sigma[t] = r1[t - N:t].std()         # std de los N retornos que terminan en t
    s = ss = 0.0
    cnt = 0                                   # acumuladores expansivos (solo < t)
    for t in range(N, M):
        if cnt >= 2:
            mu = s / cnt
            var = ss / cnt - mu * mu
            sd = np.sqrt(var) if var > 0 else 0.0
            # σ_σ y σ_local deben ser volatilidad REAL, no roundoff (precio casi
            # constante → todo ~1e-17 y el cociente amplificaría ruido a régimen falso)
            if sd > MIN_SIGMA and sigma[t] > MIN_SIGMA:
                z[t] = (sigma[t] - mu) / sd
        s += sigma[t]                         # añade σ_local(t) DESPUÉS de usar Z(t)
        ss += sigma[t] * sigma[t]
        cnt += 1
    return sigma, z


def variance_ratio(close: np.ndarray, N: int, k: int) -> np.ndarray:
    """VR_k(t) — estimador INSESGADO de Lo-MacKinlay (1988) sobre la ventana de N
    retornos que termina en t. Corrige el sesgo a la baja del estimador simple
    Var(r^k)/(k·Var(r¹)): con retornos solapados y muestra finita, el simple da
    ~0.97 para un paseo aleatorio (cuyo VR verdadero es 1), descentrando la banda
    de histéresis y sobre-clasificando "rango" (verificado: 48% de los paseos
    aleatorios → 'rango'). El insesgado centra en ~1. Adenda Plan v2.2 (2026-06-17).

        μ = (x_t − x_{t−N}) / N                  (retorno medio a 1 paso)
        σ²_a = Σ(Δx − μ)² / (N−1)                (var 1-paso, Bessel)
        σ²_c = Σ(x_j − x_{j−k} − kμ)² / m,  m = k(N−k+1)(1 − k/N)   (var k-paso)
        VR_k = σ²_c / σ²_a

    Estrictamente causal (la ventana [t−N, t] no toca precios futuros)."""
    M = len(close)
    vr = np.full(M, np.nan)
    if N < k + 1:
        return vr
    logp = np.log(close)
    for t in range(N, M):
        x = logp[t - N:t + 1]                  # N+1 precios → N retornos a 1 paso
        mu = (x[-1] - x[0]) / N
        d1 = np.diff(x) - mu
        sa = (d1 @ d1) / (N - 1)               # var 1-paso insesgada
        if sa <= MIN_SIGMA * MIN_SIGMA:        # vol real, no roundoff
            continue
        rk = x[k:] - x[:-k] - k * mu           # retornos k-paso solapados (N−k+1)
        m = k * (N - k + 1) * (1 - k / N)
        vr[t] = (rk @ rk) / m / sa
    return vr


def label_from_signals(z: np.ndarray, vr: np.ndarray, *, z_enter: float,
                       z_exit: float, vr_enter: float, vr_exit: float,
                       dwell: int, burn_in: int) -> np.ndarray:
    """Histéresis (por dimensión) + permanencia mínima (debounce del régimen
    combinado). Secuencial y causal. La histéresis CALIENTA durante el burn-in
    pero el régimen emitido es -1 hasta t≥burn_in."""
    M = len(z)
    regime = np.full(M, BURN, dtype="int64")
    vol, dirn = "low", "range"                # estados iniciales
    committed, cand, cand_n = BURN, BURN, 0
    for t in range(M):
        if not (np.isfinite(z[t]) and np.isfinite(vr[t])):
            regime[t] = BURN
            continue
        if committed == BURN:                 # primer estado válido: se SIEMBRA con
            # el primer signal vs el punto neutro de cada banda (1.0), no con un
            # default low/range sin evidencia
            vol = "high" if z[t] > 1.0 else "low"
            dirn = "trend" if vr[t] > 1.0 else "range"
            committed = cand = REGIME[(vol, dirn)]
            cand_n = 0
            regime[t] = committed if t >= burn_in else BURN
            continue
        if z[t] > z_enter:                    # histéresis volatilidad
            vol = "high"
        elif z[t] < z_exit:
            vol = "low"
        if vr[t] > vr_enter:                  # histéresis dirección
            dirn = "trend"
        elif vr[t] < vr_exit:
            dirn = "range"
        raw = REGIME[(vol, dirn)]
        if raw == committed:
            cand_n = 0                         # vuelve al actual → reinicia candidato
        else:
            if raw == cand:
                cand_n += 1
            else:
                cand, cand_n = raw, 1
            if cand_n >= dwell:                # sostenido N_dwell → se acepta el cambio
                committed = raw
                cand_n = 0
        regime[t] = committed if t >= burn_in else BURN
    return regime


def classify_regime(close, *, N: int = 2000, k: int = 50, z_enter: float = 1.1,
                    z_exit: float = 0.9, vr_enter: float = 1.05,
                    vr_exit: float = 0.95, dwell: int = 100,
                    burn_in: int | None = None) -> dict:
    """Orquesta: σ_local, Z_σ, VR_k y el régimen por observación. `close` = serie
    de cierres (de barras). Devuelve dict de arrays. Estrictamente causal."""
    close = np.asarray(close, dtype="float64")
    if len(close) and not (np.isfinite(close).all() and (close > 0).all()):
        raise ValueError("close debe ser finito y > 0")
    if N <= k:
        raise ValueError(f"N ({N}) debe ser > k ({k})")
    if not (z_enter > z_exit and vr_enter > vr_exit):
        raise ValueError("umbrales de histéresis: enter debe ser > exit")
    if dwell < 1:
        raise ValueError("dwell debe ser ≥ 1")
    if burn_in is None:
        burn_in = 2 * N                        # calentamiento de la normalización
    if burn_in < 0:
        raise ValueError("burn_in debe ser ≥ 0")
    sigma, z = volatility_zscore(close, N)
    vr = variance_ratio(close, N, k)
    regime = label_from_signals(z, vr, z_enter=z_enter, z_exit=z_exit,
                                vr_enter=vr_enter, vr_exit=vr_exit,
                                dwell=dwell, burn_in=burn_in)
    return {"sigma_local": sigma, "z_sigma": z, "vr": vr, "regime": regime}


def main() -> None:
    import argparse
    import datetime
    import os
    import sys
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # → qs/
    sys.path.insert(0, os.getcwd())
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import pyarrow as pa
    import pyarrow.parquet as pq
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--bars", default="dollar_standard",
                    help="fichero de barras en data_hist/<symbol>/bars/ (sin .parquet)")
    ap.add_argument("--N", type=int, default=2000)
    ap.add_argument("--k", type=int, default=50)
    ap.add_argument("--dwell", type=int, default=100)
    ap.add_argument("--burn-in", type=int, default=None)
    a = ap.parse_args()
    src = os.path.join("data_hist", a.symbol, "bars", f"{a.bars}.parquet")
    t = pq.read_table(src)
    close = t.column("close").to_numpy()
    tclose = t.column("t_close_ms").to_numpy()
    print(f"{a.symbol}: {len(close):,} barras de {a.bars}")
    out = classify_regime(close, N=a.N, k=a.k, dwell=a.dwell, burn_in=a.burn_in)
    reg = out["regime"]
    names = {1: "alta-vol+tend", 2: "alta-vol+rango", 3: "baja-vol+tend",
             4: "baja-vol+rango", BURN: "burn-in"}
    print(f"  N={a.N} k={a.k} dwell={a.dwell} burn_in={a.burn_in or 2*a.N}")
    vals, cnts = np.unique(reg, return_counts=True)
    print("  distribución de regímenes:")
    for v, c in zip(vals.tolist(), cnts.tolist()):
        print(f"    {names.get(v, v):16s} {c:8,d}  ({100*c/len(reg):.1f}%)")
    n_eval = int((reg != BURN).sum())
    if n_eval:
        cambios = int((np.diff(reg[reg != BURN]) != 0).sum())
        print(f"  evaluables: {n_eval:,}  | cambios de régimen: {cambios:,}")
    prov = {b"qs_artifact": b"regime_classification", b"plan_ref": b"Plan 2.1",
            b"symbol": a.symbol.encode(), b"bars": a.bars.encode(),
            b"N": str(a.N).encode(), b"k": str(a.k).encode(),
            b"dwell": str(a.dwell).encode(),
            b"burn_in": str(a.burn_in or 2 * a.N).encode(),
            b"built_utc": datetime.datetime.now(datetime.timezone.utc)
                          .isoformat().encode()}
    tbl = pa.table({"t_close_ms": tclose, "close": close,
                    "sigma_local": out["sigma_local"], "z_sigma": out["z_sigma"],
                    "vr": out["vr"], "regime": reg}).replace_schema_metadata(prov)
    out_path = os.path.join("data_hist", a.symbol, "regime.parquet")
    pq.write_table(tbl, out_path, compression="snappy")
    print(f"  escrito: {out_path}  (con metadatos de procedencia)")


if __name__ == "__main__":
    main()
