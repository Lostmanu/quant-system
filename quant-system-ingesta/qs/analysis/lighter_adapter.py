"""analysis/lighter_adapter.py — loader de Lighter (CHD `lighter`). CAPÍTULO 2. v2.

FORMATO (verificado 2026-07-02 + diagnóstico de semántica contra anclas): orderbook = diffs con cantidad
ABSOLUTA por nivel (SET, estilo Binance; qty=0 borra) + ANCLAS periódicas (`'snapshot'`, pocas/día).
`prev_final_update_id` viene NaN; el día ARRANCA en `update` (sin seed) → maduración desde vacío estilo
Binance (emite solo libros ≥top_l no cruzados).

EVIDENCIA del diagnóstico (1000PEPE 2026-04-15, ancla→ancla con 238k updates entre medias):
  • H-DELTA descartada (0/20). H-SET confirmada: precios top-10 exactos 9-10/10 ambos lados, y el lado
    QUIETO clava cantidades a la unidad (407055=407055) → el stream near-touch está COMPLETO.
  • Los únicos desajustes de cantidad viven en los 2-3 niveles HIPERACTIVOS en el instante del ancla →
    **skew de generación-vs-publicación del ANCLA** (la clase de seam predicha en el checklist), no huecos
    del stream: SET se AUTO-REPARA (cada update de un nivel lo resincroniza), así que un nivel activo no
    puede quedarse stale más que instantes; los quietos cuadran exactos.
DECISIÓN v2: las anclas NO reemplazan el libro (inyectarían su skew temporal) — son SOLO ORÁCULO.

CHECKLIST CONGELADO (LEDGER 2026-07-02) como código:
 1. UNIDADES con apellido: orderbook.event_time en NS, trades.event_time en MS (¡mixtas por canal!);
    assert de rango en la frontera (`LighterUnitsError` grita en ambos sentidos).
 2. SEAM declarado: el skew del ancla ES la clase de seam observada; se mide (oráculo), no se asume.
 3. RE-ANCLAJE como ORÁCULO: en cada ancla, métrica ESTRUCTURAL = fracción de precios top-`oracle_k` del
    ancla AUSENTES del libro reconstruido (membresía, robusta al skew), con la concordancia de cantidades
    en niveles coincidentes reportada como diagnóstico. Media estructural > `max_structural_mismatch` →
    `LighterSeamError` (fallar fuerte, jamás silencio).
"""
from __future__ import annotations
import heapq
import numpy as np

_NS_MIN, _NS_MAX = int(1e17), int(1e20)      # ~2001..~5138 en ns epoch
_MS_MIN, _MS_MAX = int(1e12), int(1e14)      # ~2001..~5138 en ms epoch


class LighterUnitsError(Exception):
    """Timestamps fuera del rango esperado para su canal (ns↔ms confundidos). Fallar fuerte."""


class LighterSeamError(Exception):
    """La ESTRUCTURA top-K del libro-por-diffs no contiene la del ancla: stream con huecos reales."""

    def __init__(self, report: dict):
        self.report = report
        super().__init__(f"oráculo estructural de re-anclaje falló: {report}")


def _assert_range(arr, lo: int, hi: int, name: str) -> None:
    v = int(arr[0])
    if not (lo <= v < hi):
        raise LighterUnitsError(f"{name}: primer valor {v} fuera de rango [{lo},{hi}) — ¿unidades confundidas?")


def lighter_to_book(df, top_l: int = 10, sample_ms: int = 100, cap: int = 512, oracle_k: int = 10,
                    max_structural_mismatch: float = 0.20):
    """Libro de Lighter a rejilla temporal. Devuelve (ts_ms[T], bpx, bsz, apx, asz, report).
    report: n_updates, n_anchors, oracle_checks, structural_mismatch_mean/max, qty_exact_frac_mean."""
    event_ns = df["event_time"].to_numpy().astype("int64")
    _assert_range(event_ns, _NS_MIN, _NS_MAX, "lighter.orderbook.event_time (esperado ns)")
    is_snap = df["event_type"].to_numpy().astype(str) == "snapshot"
    is_bid = df["side"].to_numpy().astype(str) == "bid"
    price = df["price"].to_numpy().astype("float64")
    qty = df["quantity"].to_numpy().astype("float64")

    o = np.argsort(event_ns, kind="stable")
    event_ms = event_ns[o] // 1_000_000
    is_snap, is_bid, price, qty = is_snap[o], is_bid[o], price[o], qty[o]
    n = len(event_ms)

    bids: dict[float, float] = {}
    asks: dict[float, float] = {}
    ts_l, bpx, bsz, apx, asz = [], [], [], [], []
    next_grid = None
    n_updates = n_anchors = 0
    struct_fracs: list[float] = []
    qty_exact: list[float] = []

    def _emit_until(t: int) -> None:
        nonlocal next_grid
        if next_grid is None:
            next_grid = t + sample_ms
            return
        while t >= next_grid:
            if len(bids) >= top_l and len(asks) >= top_l:
                bb = heapq.nlargest(top_l, bids.items())
                aa = heapq.nsmallest(top_l, asks.items())
                if bb[0][0] < aa[0][0]:
                    ts_l.append(next_grid)
                    bpx.append([p for p, _ in bb]); bsz.append([s for _, s in bb])
                    apx.append([p for p, _ in aa]); asz.append([s for _, s in aa])
            next_grid += sample_ms

    def _oracle(a_bids: dict, a_asks: dict) -> None:
        miss = tot = q_ok = q_tot = 0
        for anch, book, fn in ((a_bids, bids, heapq.nlargest), (a_asks, asks, heapq.nsmallest)):
            k = min(oracle_k, len(anch))
            if k == 0:
                continue
            for p, qa in fn(k, anch.items()):
                tot += 1
                qb = book.get(p)
                if qb is None:
                    miss += 1
                else:
                    q_tot += 1
                    if abs(qb - qa) <= 1e-6 * max(1.0, abs(qa)) + 1.5:   # feed redondea ±1
                        q_ok += 1
        if tot:
            struct_fracs.append(miss / tot)
        if q_tot:
            qty_exact.append(q_ok / q_tot)

    i = 0
    seeded = False
    while i < n:
        t = int(event_ms[i])
        _emit_until(t)
        if is_snap[i]:                                          # ancla = filas snap del MISMO instante
            j = i
            a_bids: dict[float, float] = {}
            a_asks: dict[float, float] = {}
            while j < n and is_snap[j] and int(event_ms[j]) == t:
                (a_bids if is_bid[j] else a_asks)[float(price[j])] = float(qty[j])
                j += 1
            n_anchors += 1
            if seeded:                                          # solo audita con libro ya maduro
                _oracle(a_bids, a_asks)
            i = j
            continue
        p = float(price[i]); q = float(qty[i])
        side = bids if is_bid[i] else asks
        if q == 0.0:
            side.pop(p, None)
        else:
            side[p] = q
            if len(side) > cap:
                keep = heapq.nlargest(cap // 2, side.items()) if side is bids else heapq.nsmallest(cap // 2, side.items())
                if side is bids:
                    bids = dict(keep)
                else:
                    asks = dict(keep)
        if not seeded and len(bids) >= top_l and len(asks) >= top_l:
            seeded = True
        n_updates += 1
        i += 1

    report = {"n_updates": n_updates, "n_anchors": n_anchors, "oracle_checks": len(struct_fracs),
              "structural_mismatch_mean": float(np.mean(struct_fracs)) if struct_fracs else 0.0,
              "structural_mismatch_max": float(np.max(struct_fracs)) if struct_fracs else 0.0,
              "qty_exact_frac_mean": float(np.mean(qty_exact)) if qty_exact else float("nan")}
    if struct_fracs and report["structural_mismatch_mean"] > max_structural_mismatch:
        raise LighterSeamError(report)
    arr = lambda x: np.array(x, "float64")
    return (np.array(ts_l, "int64"), arr(bpx), arr(bsz), arr(apx), arr(asz), report)


def lighter_trades_ms(df):
    """Trades de Lighter → (ts_ms, price, qty, is_buyer_maker). `event_time` de trades en MS
    (¡canal distinto, unidad distinta!) — assert de rango, sin conversión."""
    ts_ms = df["event_time"].to_numpy().astype("int64")
    _assert_range(ts_ms, _MS_MIN, _MS_MAX, "lighter.trades.event_time (esperado ms)")
    qcol = "quantity" if "quantity" in df.columns else "qty"
    return (ts_ms, df["price"].to_numpy().astype("float64"),
            df[qcol].to_numpy().astype("float64"), df["is_buyer_maker"].to_numpy().astype(bool))
