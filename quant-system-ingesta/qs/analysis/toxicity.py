"""analysis/toxicity.py — VPIN (toxicidad de flujo, Easley-López de Prado-O'Hara 2012).

Mide cuándo el flujo es TÓXICO: selecciona adversamente a los proveedores de liquidez,
que pueden estar cotizando a pérdida sin saberlo. Cimiento del pivote a "predecir
liquidez/toxicidad" (LEDGER H1/H3, tras fallar el cross-sectional H5): VPIN alto debería
preceder a retiradas de liquidez y a mayor volatilidad — el mecanismo de H1.

VPIN (ec. 9 del paper, `docs/papers/EasleyLopezDePradoOHara-2012-FlowToxicity-VPIN.pdf`):

    VPIN = ( Σ_{τ=1}^{n} |V^B_τ − V^S_τ| ) / (n · V)

donde los trades se agrupan en *buckets* de VOLUMEN igual V (no de tiempo: "volume-time",
robusto al clustering de volatilidad), V^B_τ/V^S_τ son el volumen comprador/vendedor del
bucket τ (V^B_τ + V^S_τ = V), y n es la ventana móvil de buckets. VPIN ∈ [0,1].

Mejora sobre el paper (declarada): el paper estima V^B con su "bulk volume classification"
(CDF de cambios de precio estandarizados) PORQUE la mayoría de datasets no traen lado
fiable. Nosotros SÍ (lado agresor real `is_buyer_maker`) → usamos el buy/sell exacto, sin
la aproximación BVC. Misma mejora que en bars.py (tick-rule → lado real).

Fiel al paper: buckets de volumen con DIVISIÓN de trade (si un trade desborda el bucket,
el exceso pasa al siguiente; el lado del trade se conserva en ambas porciones). Params de
referencia del paper: V = 1/50 del volumen diario medio, n=50 ("VPIN diario") o n=250
("una semana", la combinación (50,250) que maximiza la correlación con |retorno|).

Causalidad: VPIN en el bucket τ usa SOLO los n buckets que terminan en τ (media móvil
hacia atrás); los primeros n−1 son NaN.

HALLAZGO EMPÍRICO (2026-06-19, data_hist, (50,50)): el feature es numéricamente sano
(VPIN∈[0,1], AVAX media 0.125, rango p5/p95 0.08/0.17) pero el HALLAZGO ESTRELLA del
paper NO TRANSFIERE a estos perpetuos finos: corr(VPIN_τ, |ret_τ+1|) ≈ 0 en los 3
símbolos probados (LINK −0.00, AVAX −0.02, ATOM +0.06; |ret| siguiente del quintil
VPIN-alto vs bajo difiere <5 bps y sin signo consistente). En el E-mini S&P VPIN sí
presagia volatilidad; aquí no. Probable: el flujo a escala de bucket (~29 min) está
poco desequilibrado en estos nombres (VPIN nunca pasa de ~0.22, lejos de los picos
~0.8 de eventos tóxicos en índices). MATIZ IMPORTANTE: esto es un test DESCRIPTIVO de
VPIN→volatilidad (un proxy crudo: predictor suave vs objetivo ruidoso); NO es H1, que
es VPIN→LIQUIDEZ (spread/profundidad) y necesita el L2 propio. No mata el reframe de
toxicidad — pero baja el prior sobre VPIN de catálogo y sugiere que en cripto fino la
señal tendrá que venir de medidas ADAPTADAS sobre el L2, no de métricas publicadas
sobre trades. VPIN se conserva como feature de referencia (reutilizable en H1/H3).
"""
from __future__ import annotations
import numpy as np


def vpin(ts_ms: np.ndarray, price: np.ndarray, qty: np.ndarray, side: np.ndarray,
         bucket_volume: float, n: int = 50):
    """VPIN sobre buckets de volumen `bucket_volume`, ventana móvil `n`. `side` es +1/-1
    (agresor comprador/vendedor). Devuelve (bucket_ts, bucket_px, vpin, oi_norm), uno por
    bucket completo (el bucket final incompleto se descarta). vpin[:n-1] = NaN (causal)."""
    if bucket_volume <= 0:
        raise ValueError(f"bucket_volume debe ser > 0 (recibido {bucket_volume})")
    if n < 1:
        raise ValueError(f"n debe ser ≥ 1 (recibido {n})")
    qty = qty.astype("float64")
    if not (np.isfinite(price).all() and np.isfinite(qty).all()):
        raise ValueError("precio/qty con NaN o inf")
    if not np.all(np.abs(side) == 1):
        raise ValueError("side debe ser +1/-1 (lado agresor real)")
    cumv = np.cumsum(qty)
    is_buy = (side > 0).astype("float64")
    cumv_buy = np.cumsum(qty * is_buy)
    total = float(cumv[-1])
    nb = int(total // bucket_volume)                      # buckets COMPLETOS
    empty = (np.array([], "int64"), np.array([]), np.array([]), np.array([]))
    if nb < 1:
        return empty

    edges = bucket_volume * np.arange(0, nb + 1)          # nb+1 fronteras de volumen
    k = np.clip(np.searchsorted(cumv, edges, side="left"), 0, len(cumv) - 1)
    prev_cum = np.where(k > 0, cumv[k - 1], 0.0)
    prev_buy = np.where(k > 0, cumv_buy[k - 1], 0.0)
    # volumen comprador acumulado hasta cada frontera (con división del trade que la cruza)
    B = prev_buy + (edges - prev_cum) * is_buy[k]
    Vb = np.diff(B)                                       # V^B por bucket
    Vs = bucket_volume - Vb                               # V^S por bucket (V^B+V^S=V)
    oi_norm = np.abs(Vb - Vs) / bucket_volume             # |V^B−V^S|/V ∈ [0,1]

    csum = np.concatenate([[0.0], np.cumsum(oi_norm)])
    vp = np.full(nb, np.nan)
    vp[n - 1:] = (csum[n:] - csum[:nb - n + 1]) / n       # media móvil causal de n buckets

    kb = np.clip(np.searchsorted(cumv, edges[1:], side="left"), 0, len(ts_ms) - 1)
    return ts_ms[kb].astype("int64"), price[kb].astype("float64"), vp, oi_norm


def bucket_volume_for(qty: np.ndarray, ts_ms: np.ndarray, buckets_per_day: float = 50):
    """V de referencia del paper: 1/buckets_per_day del volumen diario medio."""
    if buckets_per_day <= 0:
        raise ValueError("buckets_per_day debe ser > 0")
    days = max((int(ts_ms[-1]) - int(ts_ms[0])) / 86_400_000, 1e-9)
    return float(qty.astype("float64").sum()) / days / buckets_per_day


def main() -> None:
    import os
    import sys
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, os.getcwd())
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from analysis.bars import load_trades
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--buckets-per-day", type=float, default=50)
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--months", default=None, help="lista por comas, ej 2026-04,2026-05")
    a = ap.parse_args()
    months = a.months.split(",") if a.months else None
    print(f"cargando {a.symbol} ...", flush=True)
    ts, price, qty, side = load_trades("data_hist", a.symbol, months)
    days = (int(ts[-1]) - int(ts[0])) / 86_400_000
    V = bucket_volume_for(qty, ts, a.buckets_per_day)
    bts, bpx, vp, oi = vpin(ts, price, qty, side, V, a.n)
    fin = vp[np.isfinite(vp)]
    print(f"  {len(price):,} trades ({days:.0f} días)  V={V:,.1f}  buckets={len(vp):,}  "
          f"({a.buckets_per_day:.0f}/día objetivo, {len(vp)/days:.0f} real)")
    print(f"  VPIN  media={fin.mean():.3f}  mediana={np.median(fin):.3f}  "
          f"p5/p95={np.percentile(fin,5):.3f}/{np.percentile(fin,95):.3f}  "
          f"max={fin.max():.3f}  (rango teórico [0,1])")
    # REPLICACIÓN DESCRIPTIVA (NO un edge; valida que el feature mide algo real, como en
    # el paper Tabla 4): ¿VPIN alto precede a |retorno| alto en el bucket siguiente?
    r = np.diff(np.log(bpx))                              # r[b] = retorno del bucket b+1
    v0, ar1 = vp[:-1], np.abs(r)                          # VPIN en τ  vs  |ret| en τ+1
    m = np.isfinite(v0) & np.isfinite(ar1)
    rho = float(np.corrcoef(v0[m], ar1[m])[0, 1])
    hi = ar1[m][v0[m] >= np.percentile(v0[m], 80)].mean()
    lo = ar1[m][v0[m] <= np.percentile(v0[m], 20)].mean()
    print(f"  [descriptivo, replicación Easley-LdP-OHara] corr(VPIN_τ, |ret_τ+1|)={rho:+.3f}"
          f"  |ret| siguiente: VPIN-alto(q80+)={hi*1e4:.1f}bps vs VPIN-bajo(q20-)={lo*1e4:.1f}bps")


if __name__ == "__main__":
    main()
