"""analysis/hl_adapter.py — loader de Hyperliquid (CHD `hyperliquid_futures`). CAPÍTULO 2.

El orderbook de HL en CHD es 100% `event_type='snapshot'` (libro COMPLETO ~30 niveles/lado por push;
NO diffs como Binance) → NO se reconstruye: se agrupa por `event_time` y cada grupo ES el libro.
`cryptohft_to_book` (Binance) NO sirve aquí: acumula niveles stale → libro cruzado → ~0 snapshots
emitidos (así se detectó el formato). Validado 2026-07-01 (BTC + AIXBT, 2026-01-15): 0% libros
cruzados, 10/10 niveles, spreads sensatos (BTC 0,10 bps; AIXBT 4,95 bps).

CADENCIA (corrección de premisa 2026-07-02, auditoría externa + histograma propio, ver
`snapshot_cadence`): los pushes van a ~0,5s (mediana 542 ms) con distribución IDÉNTICA entre símbolos
(BTC y AIXBT coinciden a 2 decimales) ⇒ calendario GLOBAL del feed, NO eventos por símbolo, y NO la
cadencia del matching: los bloques de HL son ~0,1-0,2s y existe carrera residual de priority fees en el
tier taker (~45 ms/bp, cap 8 bp). La protección estructural del maker es otra (docs verificados):
CANCELS y POST-ONLY se ordenan ANTES que GTC/IOC dentro del bloque, enforced onchain por el L1, y la
priority fee NO puede comprar por delante de un cancel. Implicación de simulación: lo intra-push es
invisible → horizontes ≥1s y cota de cola PESIMISTA como primaria. Ver LEDGER §CAPÍTULO 2."""
from __future__ import annotations
import numpy as np


def hl_snapshot_to_book(df, top_l: int = 10):
    """df de orderbook HL (CHD, event_type='snapshot') → (ts[T], bpx, bsz, apx, asz) [T, top_l].
    Cada `event_time` distinto = un snapshot completo del libro. bid desc, ask asc; NaN donde falten
    niveles. Sin reconstrucción de diffs (el push YA es el libro)."""
    et = df["event_time"].to_numpy().astype("int64")
    is_bid = df["side"].to_numpy().astype(str) == "bid"
    price = df["price"].to_numpy().astype("float64")
    qty = df["quantity"].to_numpy().astype("float64")
    o = np.argsort(et, kind="stable")
    et, is_bid, price, qty = et[o], is_bid[o], price[o], qty[o]
    uet, start = np.unique(et, return_index=True)
    T = len(uet)
    bpx = np.full((T, top_l), np.nan); bsz = np.zeros((T, top_l))
    apx = np.full((T, top_l), np.nan); asz = np.zeros((T, top_l))
    ends = np.append(start[1:], len(et))
    for i in range(T):
        s, e = start[i], ends[i]
        gb = is_bid[s:e]
        bp, bq = price[s:e][gb], qty[s:e][gb]
        ap, aq = price[s:e][~gb], qty[s:e][~gb]
        if len(bp):
            k = np.argsort(-bp)[:top_l]
            bpx[i, :len(k)] = bp[k]; bsz[i, :len(k)] = bq[k]
        if len(ap):
            k = np.argsort(ap)[:top_l]
            apx[i, :len(k)] = ap[k]; asz[i, :len(k)] = aq[k]
    return uet, bpx, bsz, apx, asz


def to_uniform_grid(ts, arrs, grid_ms: int):
    """LOCF a rejilla uniforme de `grid_ms` (ofi_signal/forward_return asumen paso constante).
    Devuelve (grid, [arr[grid] ...])."""
    ts = np.asarray(ts, dtype="int64")
    grid = np.arange(ts[0], ts[-1] + 1, grid_ms, dtype="int64")
    idx = np.clip(np.searchsorted(ts, grid, side="right") - 1, 0, len(ts) - 1)
    return grid, [np.asarray(a)[idx] for a in arrs]


def snapshot_cadence(df) -> dict:
    """Diagnóstico de cadencia del feed: distribución de deltas entre snapshots. Evidencia de la
    corrección de premisa (2026-07-02): mediana ~542 ms, idéntica entre símbolos = calendario global."""
    et = np.unique(df["event_time"].to_numpy().astype("int64"))
    d = np.diff(et).astype("float64")
    pct = lambda lo, hi: float(np.mean((d >= lo) & (d < hi)) * 100)
    return {"n_snapshots": int(len(et)), "min_ms": float(d.min()), "p1_ms": float(np.percentile(d, 1)),
            "mediana_ms": float(np.median(d)), "p99_ms": float(np.percentile(d, 99)),
            "max_ms": float(d.max()), "pct_lt_480": pct(0, 480), "pct_480_600": pct(480, 600),
            "pct_ge_1000": pct(1000, 1e18)}
