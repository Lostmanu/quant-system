"""analysis/xsection.py — Puerta de viabilidad cross-sectional (LEDGER H5, sub-test
de feasibility, pre-registro v2 congelado 2026-06-19, hash 8024f8c).

NO evalúa H5 (que necesita L2 + meses). Es el filtro §4.1 sobre los 12 meses de
aggTrades que YA tenemos: ¿queda estructura cross-sectional residual entre los 8
nombres TRAS neutralizar el factor común de mercado? Condición ~necesaria, no
suficiente. PASA → luz verde al programa L2. FALLA → la estructura es sobre todo
beta de BTC; pivotar a liquidez single-name (H1/H3).

Diseño CONGELADO (ver LEDGER):
  • Muestreo CSIC: una barra del panel cierra cuando el dólar AGREGADO de los 8
    alcanza V* (≈100 barras/día). Los 8 se muestrean en los MISMOS límites.
  • Por nombre/barra: flujo firmado normalizado f = Σ(b·v)/Σv (OFI) y retorno log.
  • Neutralización: residualizar contra la cesta equiponderada de los OTROS 7
    (leave-one-out, β-ajustada por OLS). Probe ESTRUCTURAL in-sample, no backtest.
  • Estadístico PRIMARIO direccional: D = Σ_{líq→fino} ρ_{i→j} − Σ_{fino→líq} ρ_{i→j},
    ρ_{i→j}=corr(f̃_i,t , r̃_j,t+1). Líq/fino = top-4/bottom-4 por dólar (determinista).
  • Nulo: 1000 desplazamientos circulares COMUNES a todo el panel de predictores.
  • Veredicto: PASA si D>p99 del nulo y >p95 en ambas mitades; FALLA si D<p95; gris si no.

Causalidad/IO aislados de las funciones puras. Trades-only (bid-ask bounce presente:
sesga hacia FALLA, conservador; el mid limpio es para el H5 real con L2/bookTicker).
"""
from __future__ import annotations
import numpy as np

SYMBOLS = ("AVAXUSDT", "LINKUSDT", "DOTUSDT", "NEARUSDT",
           "ATOMUSDT", "LTCUSDT", "FILUSDT", "UNIUSDT")


# ----------------------------- funciones puras -------------------------------
def per_second(ts_ms: np.ndarray, price: np.ndarray, qty: np.ndarray,
               side: np.ndarray):
    """Agrega trades (ordenados por ts) a segundos activos. Devuelve por segundo:
    (sec, dollar, signed_dollar, last_price). last_price = precio del último trade del
    segundo (close). Asume ts_ms NO decreciente (load_trades ordena por (ts,id))."""
    dollar = price * qty
    sec = (ts_ms // 1000).astype("int64")
    usec, first = np.unique(sec, return_index=True)          # sec ya ordenado
    d = np.add.reduceat(dollar, first)
    sg = np.add.reduceat(side * dollar, first)
    lastpos = np.empty(len(usec), dtype="int64")             # último idx de cada segundo
    lastpos[:-1] = first[1:] - 1
    lastpos[-1] = len(price) - 1
    return usec, d, sg, price[lastpos]


def csic_panel(secs, dols, sgns, lasts, target_bars: int):
    """Reloj de Información Cross-Sectional. `secs/dols/sgns/lasts` son listas (una por
    símbolo) de arrays por-segundo. Una barra cierra cuando el dólar AGREGADO alcanza
    k·V*, V*=total/target_bars. Devuelve (close[T,S], flow[T,S], bound_sec[T], miss[S])
    donde T=nº de barras, S=nº de símbolos. Las barras sin trades de un símbolo heredan
    el close anterior (retorno 0) y flujo 0 (sin información)."""
    S = len(secs)
    # clock agregado a resolución de segundo activo (unión de segundos)
    all_sec = np.concatenate(secs)
    all_dol = np.concatenate(dols)
    g_sec, inv = np.unique(all_sec, return_inverse=True)
    g_dol = np.bincount(inv, weights=all_dol)
    cum = np.cumsum(g_dol)
    V = cum[-1] / target_bars
    pos = np.searchsorted(cum, V * np.arange(1, target_bars + 1), side="left")
    pos = np.unique(pos[pos < len(g_sec)])
    bound_sec = g_sec[pos]                                    # segundo-fin de cada barra
    T = len(bound_sec)
    close = np.full((T, S), np.nan)
    flow = np.zeros((T, S))
    miss = np.zeros(S, dtype="int64")
    for s in range(S):
        sec, d, sg, last = secs[s], dols[s], sgns[s], lasts[s]
        b = np.searchsorted(bound_sec, sec, side="left")     # barra de cada segundo
        keep = b < T                                         # cola tras la última barra
        b, d, sg, last, sec = b[keep], d[keep], sg[keep], last[keep], sec[keep]
        bd = np.bincount(b, weights=d, minlength=T)
        bsg = np.bincount(b, weights=sg, minlength=T)
        nz = bd > 0
        flow[nz, s] = bsg[nz] / bd[nz]                        # OFI por barra
        # close: último precio de la última barra-fila ocupada (segundos ordenados)
        lastrow = np.searchsorted(b, np.arange(T), side="right") - 1
        has = lastrow >= 0
        cl = np.full(T, np.nan)
        cl[has] = last[lastrow[has]]
        # carry-forward de barras sin trade
        idx = np.where(~np.isnan(cl))[0]
        if len(idx):
            cl[:idx[0]] = cl[idx[0]]                          # warmup hasta el 1er trade
            fill = np.maximum.accumulate(np.where(np.isnan(cl), -1, np.arange(T)))
            cl = cl[np.where(fill >= 0, fill, 0)]
        miss[s] = int((~nz).sum())
        close[:, s] = cl
    return close, flow, bound_sec, miss


def returns_from_close(close: np.ndarray) -> np.ndarray:
    """Retornos log close-to-close por columna (símbolo). Fila 0 = 0."""
    r = np.zeros_like(close)
    r[1:] = np.diff(np.log(close), axis=0)
    return r


def neutralize(x: np.ndarray) -> np.ndarray:
    """Residualiza cada columna i contra la cesta equiponderada de las OTRAS (leave-
    one-out, β-ajustada por OLS): x̃_i = x_i − β_i·b_i, b_i = media de las demás. Quita
    el factor común (≈ beta de BTC) sin sesgo mecánico de auto-resta."""
    T, S = x.shape
    tot = x.sum(axis=1, keepdims=True)
    basket = (tot - x) / (S - 1)                             # leave-one-out
    res = np.empty_like(x)
    for i in range(S):
        b = basket[:, i]
        bc = b - b.mean()
        xi = x[:, i] - x[:, i].mean()
        var = bc @ bc
        beta = (bc @ xi) / var if var > 0 else 0.0
        res[:, i] = x[:, i] - beta * b
    return res


def leadlag_matrix(fp: np.ndarray, rt: np.ndarray) -> np.ndarray:
    """ρ[i,j] = corr(fp_i, rt_j) entre columnas (predictor i, objetivo j)."""
    fz = (fp - fp.mean(0)) / (fp.std(0) + 1e-300)
    rz = (rt - rt.mean(0)) / (rt.std(0) + 1e-300)
    return (fz.T @ rz) / fp.shape[0]


def directional_D(rho: np.ndarray, liq, thin) -> float:
    """D = Σ_{i∈líq, j∈fino} ρ_{i→j} − Σ_{i∈fino, j∈líq} ρ_{i→j}."""
    return float(rho[np.ix_(liq, thin)].sum() - rho[np.ix_(thin, liq)].sum())


def shuffle_null(fp: np.ndarray, rt: np.ndarray, liq, thin, n: int = 1000,
                 seed: int = 0) -> np.ndarray:
    """Nulo de D: n desplazamientos circulares COMUNES a todo el panel de predictores
    (preservan la correlación cross-sectional contemporánea, rompen el timing del
    lead-lag)."""
    rng = np.random.default_rng(seed)
    Ta = fp.shape[0]
    out = np.empty(n)
    for k in range(n):
        sh = int(rng.integers(1, Ta))
        out[k] = directional_D(leadlag_matrix(np.roll(fp, sh, axis=0), rt), liq, thin)
    return out


def evaluate(flow: np.ndarray, ret: np.ndarray, liq, thin, n_shuffle=1000, seed=0):
    """D observado + nulo, alineando predictor f en t con objetivo r en t+1."""
    f_t, r_t = neutralize(flow), neutralize(ret)
    fp, rt = f_t[:-1], r_t[1:]                                # f en t → r en t+1
    rho = leadlag_matrix(fp, rt)
    D = directional_D(rho, liq, thin)
    null = shuffle_null(fp, rt, liq, thin, n_shuffle, seed)
    return D, null, rho


# ------------------------------ carga y CLI ----------------------------------
def main() -> None:
    import os
    import sys
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))      # → qs/
    sys.path.insert(0, os.getcwd())
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from analysis.bars import load_trades
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bars-per-day", type=float, default=100)
    ap.add_argument("--shuffles", type=int, default=1000)
    a = ap.parse_args()

    secs, dols, sgns, lasts, dollar_total, spans = [], [], [], [], [], []
    for s in SYMBOLS:
        ts, price, qty, side = load_trades("data_hist", s)
        us, d, sg, last = per_second(ts, price, qty, side)
        secs.append(us); dols.append(d); sgns.append(sg); lasts.append(last)
        dollar_total.append(float(d.sum()))
        spans.append((int(ts[0]), int(ts[-1])))
        print(f"  {s:10s} {len(ts):>12,} trades  {d.sum()/1e9:8.1f} G$  "
              f"segundos activos={len(us):,}", flush=True)
    days = (max(e for _, e in spans) - min(s for s, _ in spans)) / 86_400_000
    target_bars = int(a.bars_per_day * days)
    close, flow, bound, miss = csic_panel(secs, dols, sgns, lasts, target_bars)
    ret = returns_from_close(close)
    T = close.shape[0]
    print(f"\nCSIC: {T:,} barras del panel ({T/days:.0f}/día, objetivo {a.bars_per_day:.0f}); "
          f"{days:.0f} días")
    print("  ausencias por símbolo (barras sin trade, carry-forward): "
          + ", ".join(f"{s.split('USDT')[0]} {100*m/T:.1f}%" for s, m in zip(SYMBOLS, miss)))

    # split de liquidez DETERMINISTA: top-4 / bottom-4 por dólar total
    order = np.argsort(dollar_total)[::-1]
    liq, thin = sorted(order[:4].tolist()), sorted(order[4:].tolist())
    name = lambda I: ", ".join(SYMBOLS[i].split("USDT")[0] for i in I)
    print(f"  LÍQUIDOS (top-4 $): {name(liq)}   |   FINOS (bottom-4 $): {name(thin)}")

    def verdict(D, null, etiqueta):
        p95, p99 = np.percentile(null, 95), np.percentile(null, 99)
        z = (D - null.mean()) / (null.std() + 1e-300)
        pct = float((null < D).mean() * 100)
        print(f"  [{etiqueta}] D={D:+.3f}  nulo μ={null.mean():+.3f} σ={null.std():.3f}  "
              f"p95={p95:+.3f} p99={p99:+.3f}  → D supera al {pct:.1f}% del nulo (z={z:+.1f})")
        return D, p95, p99

    print("\n=== ESTADÍSTICO PRIMARIO (direccional líquidos→finos) ===")
    D, null, rho = evaluate(flow, ret, liq, thin, a.shuffles)
    D, p95, p99 = verdict(D, null, "ventana completa")

    half = T // 2
    Dh1, n1, _ = evaluate(flow[:half], ret[:half], liq, thin, a.shuffles, seed=1)
    Dh2, n2, _ = evaluate(flow[half:], ret[half:], liq, thin, a.shuffles, seed=2)
    print("  estabilidad (debe mantener signo y >p95 en AMBAS mitades):")
    _, p95_1, _ = verdict(Dh1, n1, "1ª mitad")
    _, p95_2, _ = verdict(Dh2, n2, "2ª mitad")

    passa = (D > p99) and (Dh1 > p95_1) and (Dh2 > p95_2) and (Dh1 > 0) and (Dh2 > 0)
    falla = D < p95
    estado = "PASA (luz verde al programa L2)" if passa else (
             "FALLA (despriorizar cross-sectional; pivotar a H1/H3)" if falla else
             "ZONA GRIS (no concluyente)")
    print(f"\n>>> VEREDICTO: {estado}")

    # secundarios DESCRIPTIVOS (no deciden)
    off = rho.copy(); np.fill_diagonal(off, 0.0)
    i, j = np.unravel_index(np.argmax(np.abs(off)), off.shape)
    print(f"\n--- descriptivos (no deciden el veredicto) ---")
    print(f"  par dirigido más fuerte: {SYMBOLS[i].split('USDT')[0]}→"
          f"{SYMBOLS[j].split('USDT')[0]}  ρ={off[i,j]:+.3f}")
    print(f"  |ρ| medio fuera de diagonal: {np.abs(off).mean():.4f}  "
          f"(autocorr propia media diag: {np.diag(rho).mean():+.4f})")


if __name__ == "__main__":
    main()
