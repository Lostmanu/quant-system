"""analysis/bars.py — Barras information-driven (Plan 1.6; AFML cap. 2 §2.3.1).

Construye barras ESTÁNDAR tick/volume/dollar a partir de los aggTrades históricos
de `data_hist/`, fiel a López de Prado, *Advances in Financial Machine Learning*,
§2.3.1 (`docs/papers/LopezDePrado-2018-AFML.pdf`, págs. 26-29).

Por qué estas barras y no velas de tiempo: el muestreo por actividad (ticks/
volumen/dólar) produce retornos más cercanos a IID Normal (Mandelbrot-Taylor 1967;
Ané-Geman 2000), requisito de casi toda la inferencia posterior. AFML prefiere las
**dollar bars** (robustas a apreciación de precio y a cambios de supply). El Plan
1.6 prohíbe las velas de tiempo fijo precisamente por esto.

Signo del tick (mejora sobre AFML): en vez de la *tick-rule* (que INFIERE el signo
del cambio de precio), usamos el lado agresor REAL de Binance: `is_buyer_maker`.
is_buyer_maker=True → el comprador es el maker → agresor vendedor → b = -1.
is_buyer_maker=False → agresor comprador → b = +1. Es exacto, no inferido.
(Aviso §2.5 del Plan: las features de lado agresor pueden medir flujo retail
desinformado; eso afecta a su uso como SEÑAL, no a la construcción de barras.)

Las barras de DESEQUILIBRIO (TIB/VIB/DIB, §2.3.2.1-2) y de RUNS (TRB/VRB/DRB,
§2.3.2.3-4) están abajo en este mismo módulo (`imbalance_bars`, `runs_bars`), ambas
con su umbral EWMA causal congelado al inicio de barra. El PDF fuente está en
`docs/papers/` (gitignored por copyright).

Uso:  python analysis/bars.py --symbol AVAXUSDT --kind dollar [--bars-per-day 100]
                              [--method standard|imbalance|runs] [--months 2026-05]
                              [--demo]
"""
from __future__ import annotations
import numpy as np

BAR_COLUMNS = ("t_open_ms", "t_close_ms", "n_ticks", "open", "high", "low",
               "close", "vwap", "volume", "dollar", "buy_volume", "sell_volume")


def _validate_inputs(price: np.ndarray, qty: np.ndarray, side: np.ndarray) -> None:
    """Garantías de entrada (un tick corrupto en 66M reventaría el run sin
    mensaje útil): precio/qty finitos y `side` exactamente +1/-1. Con side ±1 el
    invariante buy+sell==volume se cumple siempre y no hay el caso ambiguo 0."""
    if len(price) == 0:
        return
    if not (np.isfinite(price).all() and np.isfinite(qty).all()):
        raise ValueError("precio/qty contienen NaN o inf")
    if not np.all(np.abs(side) == 1):
        raise ValueError("side debe ser +1/-1 (lado agresor real); recibido otro valor")


def standard_bars(ts_ms: np.ndarray, price: np.ndarray, qty: np.ndarray,
                  side: np.ndarray, kind: str, threshold: float) -> dict:
    """Barras estándar (AFML §2.3.1). `kind` ∈ {tick, volume, dollar}; `side` es
    +1/-1 (agresor comprador/vendedor). Una barra cierra cuando el acumulado de la
    métrica desde el último cierre alcanza `threshold`; la barra final incompleta
    se descarta (estándar). Construcción CAUSAL por definición: una barra solo
    depende de los ticks que contiene. Devuelve dict columna→lista."""
    n = len(price)
    _validate_inputs(price, qty, side)
    if kind == "tick":
        metric = np.ones(n, dtype="float64")
    elif kind == "volume":
        metric = qty.astype("float64")
    elif kind == "dollar":
        metric = (price * qty).astype("float64")
    else:
        raise ValueError(f"kind desconocido: {kind!r}")
    if n == 0 or threshold <= 0:
        return {c: [] for c in BAR_COLUMNS}

    cum = np.cumsum(metric)                       # métrica acumulada (creciente)
    cum_pv = np.cumsum(price * qty)               # Σ precio·qty → dólar y vwap
    cum_q = np.cumsum(qty.astype("float64"))      # Σ qty → volumen
    cum_buy = np.cumsum(np.where(side > 0, qty, 0.0))
    cum_sell = np.cumsum(np.where(side < 0, qty, 0.0))

    def seg(c, s, e):                             # suma en [s..e] desde acumulado
        return c[e] - (c[s - 1] if s > 0 else 0.0)

    out = {c: [] for c in BAR_COLUMNS}
    base, start = 0.0, 0
    while True:
        j = int(np.searchsorted(cum, base + threshold, side="left"))
        if j >= n:
            break                                # barra incompleta final: se descarta
        vol = seg(cum_q, start, j)
        out["t_open_ms"].append(int(ts_ms[start]))
        out["t_close_ms"].append(int(ts_ms[j]))
        out["n_ticks"].append(int(j - start + 1))
        out["open"].append(float(price[start]))
        out["high"].append(float(price[start:j + 1].max()))
        out["low"].append(float(price[start:j + 1].min()))
        out["close"].append(float(price[j]))
        out["vwap"].append(float(seg(cum_pv, start, j) / vol) if vol > 0
                           else float(price[j]))
        out["volume"].append(float(vol))
        out["dollar"].append(float(seg(cum_pv, start, j)))
        out["buy_volume"].append(float(seg(cum_buy, start, j)))
        out["sell_volume"].append(float(seg(cum_sell, start, j)))
        base, start = cum[j], j + 1
    return out


def imbalance_bars(ts_ms: np.ndarray, price: np.ndarray, qty: np.ndarray,
                   side: np.ndarray, kind: str, *, warmup_T: float,
                   ewma_T_span: float = 100.0, ewma_imb_span: float = 100.0,
                   max_ticks: int | None = None, min_imbalance: float = 1e-12) -> dict:
    """Barras de DESEQUILIBRIO (AFML §2.3.2): TIB (kind='tick'), VIB ('volume'),
    DIB ('dollar'). Muestrean cuando el desequilibrio de flujo firmado supera lo
    esperado → más frecuentes bajo trading informado.

    θ_T = Σ m_t  con m_t = b_t (tick) | b_t·qty (volume) | b_t·dólar (dollar),
    b_t = +1/-1 (agresor). Cierra cuando |θ_T| ≥ E_0[T]·|E[m_t]|, donde E_0[T] es
    la EWMA de la longitud de barras previas y E[m_t] la EWMA del flujo firmado
    por tick. **Causalidad:** el umbral se CONGELA al inicio de cada barra con las
    EWMA disponibles ANTES de ella; las EWMA siguen actualizándose por tick para la
    barra SIGUIENTE (AFML: "E_0 al comienzo de la barra"). Así una barra nunca usa
    su propio desequilibrio tardío para fijar su umbral.

    Salvaguardas de estabilidad (NO son de AFML; el método es famoso por explotar/
    colapsar): `min_imbalance` evita umbral 0 (flujo equilibrado → cierres
    instantáneos) y `max_ticks` evita barras infinitas (θ que nunca alcanza un
    umbral grande). Ambas se declaran; si se disparan mucho, las barras dejan de
    ser puramente information-driven y hay que recalibrar.

    HALLAZGO EMPÍRICO (2026-06-16, AVAXUSDT mayo): con parámetros ingenuos estas
    barras se DEGENERAN — 65 % tocaron el cap, mediana = máx = cap → en la práctica
    son barras de tick fijo, no information-driven. Causa de fondo: en un mercado
    mayormente eficiente el desequilibrio neto θ crece como √T (aleatorio), no como
    T (persistente), así que rara vez alcanza el umbral E_0[T]·|E[m]| y manda el
    cap. Solo muestrean rápido bajo desequilibrio PERSISTENTE real (trading
    informado), que es escaso. Conclusión: requieren calibración cuidadosa (Fase 5)
    antes de ser útiles; NO tunear hasta que "se vean bien" (sería autoengaño). El
    sustrato fiable hoy son las dollar bars estándar.
    """
    n = len(price)
    if warmup_T <= 0:
        raise ValueError(f"warmup_T debe ser > 0 (recibido {warmup_T})")
    _validate_inputs(price, qty, side)
    if kind == "tick":
        m = side.astype("float64")
    elif kind == "volume":
        m = (side * qty).astype("float64")
    elif kind == "dollar":
        m = (side * price * qty).astype("float64")
    else:
        raise ValueError(f"kind desconocido: {kind!r}")
    out = {c: [] for c in BAR_COLUMNS}
    if n == 0:
        return out

    # listas Python: el bucle secuencial es más rápido que indexar numpy escalar
    m_l, p_l, q_l, s_l, t_l = (m.tolist(), price.tolist(), qty.tolist(),
                              side.tolist(), ts_ms.tolist())
    aT = 2.0 / (ewma_T_span + 1.0)
    ai = 2.0 / (ewma_imb_span + 1.0)
    ewmaT = float(warmup_T)
    # semilla del flujo firmado: media de calentamiento de los primeros ticks (NO
    # un solo trade — un whale inicial fijaría un umbral patológico no reproducible)
    k = min(max(int(warmup_T), 1), n)
    seed = float(np.mean(m[:k]))
    ewma_imb = seed if abs(seed) > min_imbalance else (
        min_imbalance if seed >= 0 else -min_imbalance)

    i = 0
    while i < n:
        start = i
        thr = max(ewmaT * abs(ewma_imb), min_imbalance)     # CONGELADO al inicio
        theta = 0.0
        o = hi = lo = p_l[i]
        vol = doll = buy = sell = 0.0
        closed = False
        while i < n:
            p, q, mv = p_l[i], q_l[i], m_l[i]
            theta += mv
            ewma_imb = ai * mv + (1.0 - ai) * ewma_imb      # update por tick (próxima barra)
            if p > hi:
                hi = p
            if p < lo:
                lo = p
            vol += q
            doll += p * q
            if s_l[i] > 0:
                buy += q
            else:
                sell += q
            nt = i - start + 1
            if abs(theta) >= thr or (max_ticks is not None and nt >= max_ticks):
                out["t_open_ms"].append(int(t_l[start]))
                out["t_close_ms"].append(int(t_l[i]))
                out["n_ticks"].append(nt)
                out["open"].append(float(o)); out["high"].append(float(hi))
                out["low"].append(float(lo)); out["close"].append(float(p))
                out["vwap"].append(float(doll / vol) if vol > 0 else float(p))
                out["volume"].append(float(vol)); out["dollar"].append(float(doll))
                out["buy_volume"].append(float(buy)); out["sell_volume"].append(float(sell))
                ewmaT = aT * nt + (1.0 - aT) * ewmaT        # update por barra
                i += 1
                closed = True
                break
            i += 1
        if not closed:
            break                                            # cola incompleta: descartada
    return out


def runs_bars(ts_ms: np.ndarray, price: np.ndarray, qty: np.ndarray,
              side: np.ndarray, kind: str, *, warmup_T: float,
              ewma_T_span: float | None = None, ewma_run_span: float = 100.0,
              max_ticks: int | None = None, min_theta: float = 1e-12) -> dict:
    """Barras de RUNS (AFML §2.3.2.3-4): TRB (kind='tick'), VRB ('volume'), DRB
    ('dollar'). A diferencia de las de imbalance —que miran el flujo NETO firmado—,
    las de runs acumulan el flujo de CADA LADO POR SEPARADO y muestrean cuando el
    lado dominante supera lo esperado. AFML es explícito (§2.3.2.3): NO mide la
    longitud de la racha más larga, sino el conteo de cada lado SIN compensarlos.

        θ_T = max( Σ_{t|b_t=1} v_t , Σ_{t|b_t=-1} v_t ),
        con v_t = 1 (tick) | qty (volume) | precio·qty (dollar).
    Cierra cuando θ_T ≥ E_0[T]·max( P[b=1]·E[v|compra] , (1-P[b=1])·E[v|venta] ),
    donde E_0[T] es la longitud esperada de barra (ver modos abajo), P[b=1] la EWMA de
    la proporción de compras por barra, y E[v|·] la EWMA del volumen medio por lado
    ("de barras previas", textual en AFML).

    **Causalidad:** el umbral se CONGELA al inicio de cada barra con EWMA de barras
    ANTERIORES, que se actualizan SOLO al cerrar la barra. Esto es aún más limpio que
    imbalance (sin actualización intra-barra): una barra no puede usar su propia
    estadística para fijar su umbral.

    **E_0[T] — dos modos.** `ewma_T_span=None` (POR DEFECTO, recomendado para el
    laboratorio) FIJA E_0[T]=warmup_T: el objetivo de tamaño de barra es estable.
    `ewma_T_span=número` reproduce AFML literal (EWMA de longitudes de barras previas).
    En AMBOS, P[b=1] y E[v|·] siguen siendo EWMA por barra: las barras se adaptan a la
    actividad real del mercado (que es lo que aporta información); lo único que el modo
    fijo NO realimenta es la propia longitud de barra (ver HALLAZGO).

    Por qué importan frente a imbalance: el flujo de UN lado crece ~lineal con T, así
    que θ alcanza el umbral de forma regular y NO degenera como el desequilibrio neto
    (que crece como √T y por eso colapsaba al cap, ver `imbalance_bars`). Salvaguardas
    `min_theta` (umbral 0) y `max_ticks` (barra infinita) declaradas, igual que allí;
    no son de AFML.

    HALLAZGO + MEJORA (AVAXUSDT mayo, 2,78M trades, dollar): runs NO degeneran como
    imbalance — 0 % al cap (vs 65 %, cuya mediana=máx=cap), distribución de tamaños
    REAL. PERO con el E_0[T] REALIMENTADO de AFML la longitud de barra DERIVA al alza
    (mediana 1115→6876 en el mes, corr(índice,n_ticks)=+0.62): el punto fijo T*=E_0[T]
    es neutralmente estable y la cola pesada del dólar lo empuja arriba → la resolución
    de muestreo cambia DENTRO del dataset (veneno para el laboratorio: rompe la
    estacionariedad del proceso generador de barras). Por eso el modo por defecto FIJA
    E_0[T]: medido sobre el mismo mayo, la deriva DESAPARECE (corr +0.62→+0.09; mediana
    primeras/últimas 1115→6876 ⇒ 1049→1409) y la tasa se ancla al objetivo (25→84/día,
    objetivo 100). Esto DIVERGE del E_0[T] de AFML §2.3.2.3, por diseño y con evidencia
    (el modo AFML queda disponible con `ewma_T_span=número`). El sustrato más probado
    sigue siendo dollar bars estándar; runs con E_0[T] fijo es la mejor barra
    information-driven disponible.
    """
    n = len(price)
    if warmup_T <= 0:
        raise ValueError(f"warmup_T debe ser > 0 (recibido {warmup_T})")
    _validate_inputs(price, qty, side)
    if kind == "tick":
        v = np.ones(n, dtype="float64")
    elif kind == "volume":
        v = qty.astype("float64")
    elif kind == "dollar":
        v = (price * qty).astype("float64")
    else:
        raise ValueError(f"kind desconocido: {kind!r}")
    out = {c: [] for c in BAR_COLUMNS}
    if n == 0:
        return out

    p_l, q_l, s_l, v_l, t_l = (price.tolist(), qty.tolist(), side.tolist(),
                              v.tolist(), ts_ms.tolist())
    aT = 0.0 if ewma_T_span is None else 2.0 / (ewma_T_span + 1.0)  # None → E_0[T] fijo
    aR = 2.0 / (ewma_run_span + 1.0)
    ewmaT = float(warmup_T)
    # semilla de P[compra] y E[v|lado] desde los primeros ticks (NO un solo trade:
    # un whale inicial fijaría un umbral patológico no reproducible)
    k = min(max(int(warmup_T), 1), n)
    sseed = side[:k] > 0
    vseed = v[:k]
    vmean = float(vseed.mean())
    if vmean <= 0.0:                                  # qty degeneradas: evita umbral 0
        vmean = min_theta
    ewmaP = float(sseed.mean())
    ewma_vbuy = float(vseed[sseed].mean()) if sseed.any() else vmean
    ewma_vsell = float(vseed[~sseed].mean()) if (~sseed).any() else vmean

    i = 0
    while i < n:
        start = i
        thr = max(ewmaT * max(ewmaP * ewma_vbuy,
                              (1.0 - ewmaP) * ewma_vsell), min_theta)  # CONGELADO
        buy_acc = sell_acc = 0.0                       # Σ v_t de cada lado (θ = max)
        o = hi = lo = p_l[i]
        vol = doll = buy = sell = 0.0
        n_buy = 0
        sum_vbuy = sum_vsell = 0.0
        closed = False
        while i < n:
            p, q, vt = p_l[i], q_l[i], v_l[i]
            if s_l[i] > 0:
                buy_acc += vt; n_buy += 1; sum_vbuy += vt; buy += q
            else:
                sell_acc += vt; sum_vsell += vt; sell += q
            if p > hi:
                hi = p
            if p < lo:
                lo = p
            vol += q
            doll += p * q
            theta = buy_acc if buy_acc > sell_acc else sell_acc        # max de lados
            nt = i - start + 1
            if theta >= thr or (max_ticks is not None and nt >= max_ticks):
                out["t_open_ms"].append(int(t_l[start]))
                out["t_close_ms"].append(int(t_l[i]))
                out["n_ticks"].append(nt)
                out["open"].append(float(o)); out["high"].append(float(hi))
                out["low"].append(float(lo)); out["close"].append(float(p))
                out["vwap"].append(float(doll / vol) if vol > 0 else float(p))
                out["volume"].append(float(vol)); out["dollar"].append(float(doll))
                out["buy_volume"].append(float(buy)); out["sell_volume"].append(float(sell))
                # EWMA POR BARRA (semántica "de barras previas" para la SIGUIENTE)
                ewmaT = aT * nt + (1.0 - aT) * ewmaT
                ewmaP = aR * (n_buy / nt) + (1.0 - aR) * ewmaP
                if n_buy > 0:
                    ewma_vbuy = aR * (sum_vbuy / n_buy) + (1.0 - aR) * ewma_vbuy
                n_sell = nt - n_buy
                if n_sell > 0:
                    ewma_vsell = aR * (sum_vsell / n_sell) + (1.0 - aR) * ewma_vsell
                i += 1
                closed = True
                break
            i += 1
        if not closed:
            break                                       # cola incompleta: descartada
    return out


def auto_threshold(ts_ms: np.ndarray, price: np.ndarray, qty: np.ndarray,
                   kind: str, bars_per_day: float) -> float:
    """Umbral que apunta a ~`bars_per_day` barras/día (granularidad, NO optimizado
    a ningún resultado; la calibración fina de V*/D*/N es de Fase 5, Plan 1.6)."""
    if len(ts_ms) == 0:
        raise ValueError("sin trades para calcular el umbral")
    if bars_per_day <= 0:
        raise ValueError(f"bars_per_day debe ser > 0 (recibido {bars_per_day})")
    span_days = max((int(ts_ms[-1]) - int(ts_ms[0])) / 86_400_000, 1e-9)
    if kind == "tick":
        total = len(price)
    elif kind == "volume":
        total = float(qty.sum())
    else:
        total = float((price * qty).sum())
    return total / span_days / bars_per_day


# ---- carga de datos y CLI (efectos de E/S aislados de las funciones puras) ----
def load_trades(data_hist: str, symbol: str, months: list[str] | None = None):
    import glob
    import os
    import pyarrow as pa
    import pyarrow.parquet as pq
    files = sorted(glob.glob(os.path.join(data_hist, symbol, "aggTrades-*.parquet")))
    if months:
        files = [f for f in files if any(m in os.path.basename(f) for m in months)]
    if not files:
        raise FileNotFoundError(f"sin aggTrades para {symbol} en {data_hist}")
    t = pa.concat_tables([pq.read_table(
        f, columns=["trade_ts_ms", "agg_trade_id", "price", "qty",
                    "is_buyer_maker"]) for f in files])
    ts = t.column("trade_ts_ms").to_numpy()
    ids = t.column("agg_trade_id").to_numpy()
    price = t.column("price").to_numpy()
    qty = t.column("qty").to_numpy()
    bm = t.column("is_buyer_maker").to_numpy()
    order = np.lexsort((ids, ts))                # determinismo: (ts, id)
    ts, price, qty, bm = ts[order], price[order], qty[order], bm[order]
    side = np.where(bm, -1.0, 1.0)               # is_buyer_maker → agresor vendedor
    return ts, price.astype("float64"), qty.astype("float64"), side


def _excess_kurtosis(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    if len(x) < 4:
        return float("nan")
    m = x.mean()
    s2 = ((x - m) ** 2).mean()
    return float(((x - m) ** 4).mean() / s2 ** 2 - 3) if s2 > 0 else float("nan")


def demo_normality(ts_ms, price, qty, side, bars_per_day: float = 100) -> None:
    """Comprueba la afirmación de AFML: los retornos de dollar bars están MÁS
    cerca de la normal (menor curtosis) que los de time bars del mismo recuento."""
    thr = auto_threshold(ts_ms, price, qty, "dollar", bars_per_day)
    db = standard_bars(ts_ms, price, qty, side, "dollar", thr)
    dret = np.diff(np.log(np.array(db["close"])))
    # time bars de igual recuento: divide el horizonte en len(db) tramos iguales
    nb = len(db["close"])
    edges = np.linspace(int(ts_ms[0]), int(ts_ms[-1]) + 1, nb + 1)
    idx = np.searchsorted(ts_ms, edges[1:-1])
    closes_t = price[np.clip(np.append(idx, len(price)) - 1, 0, len(price) - 1)]
    tret = np.diff(np.log(closes_t))
    print(f"  barras: dollar={nb}  time={len(closes_t)}")
    print(f"  curtosis EXCESO de retornos  dollar={_excess_kurtosis(dret):+.2f}"
          f"   time={_excess_kurtosis(tret):+.2f}   "
          f"(AFML: dollar debe ser MENOR = más normal)")


def main() -> None:
    import argparse
    import os
    import sys
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # → qs/
    sys.path.insert(0, os.getcwd())
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import pyarrow as pa
    import pyarrow.parquet as pq
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--kind", default="dollar", choices=["tick", "volume", "dollar"])
    ap.add_argument("--method", default="standard",
                    choices=["standard", "imbalance", "runs"])
    ap.add_argument("--bars-per-day", type=float, default=100)
    ap.add_argument("--months", default=None, help="lista por comas, ej 2026-04,2026-05")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    months = a.months.split(",") if a.months else None
    print(f"cargando {a.symbol} ...", flush=True)
    ts, price, qty, side = load_trades("data_hist", a.symbol, months)
    days = (int(ts[-1]) - int(ts[0])) / 86_400_000
    print(f"  {len(price):,} trades  ({days:.1f} días)", flush=True)
    # procedencia: el parquet de barras debe ser AUTODESCRIPTIVO (con qué se hizo)
    import datetime
    prov = {b"qs_artifact": b"information_driven_bars",
            b"afml_ref": b"AFML cap.2 (2.3.1 estandar / 2.3.2 imbalance+runs)",
            b"method": a.method.encode(), b"kind": a.kind.encode(),
            b"symbol": a.symbol.encode(), b"months": (a.months or "all").encode(),
            b"bars_per_day_target": str(a.bars_per_day).encode(),
            b"n_trades": str(len(price)).encode(),
            b"built_utc": datetime.datetime.now(datetime.timezone.utc)
                          .isoformat().encode()}
    if a.method == "standard":
        thr = auto_threshold(ts, price, qty, a.kind, a.bars_per_day)
        bars = standard_bars(ts, price, qty, side, a.kind, thr)
        prov[b"threshold"] = repr(thr).encode()
        print(f"  {a.kind} bars (estándar): {len(bars['close']):,}  "
              f"(umbral={thr:,.2f}, ~{a.bars_per_day:.0f}/día)")
    else:
        warmup_T = max(len(price) / max(days, 1e-9) / a.bars_per_day, 2.0)
        cap = int(50 * warmup_T)
        builder = imbalance_bars if a.method == "imbalance" else runs_bars
        bars = builder(ts, price, qty, side, a.kind, warmup_T=warmup_T, max_ticks=cap)
        prov[b"warmup_T"] = repr(warmup_T).encode()
        prov[b"max_ticks"] = str(cap).encode()
        nb = len(bars["close"])
        nt = np.array(bars["n_ticks"]) if nb else np.array([0])
        hit_cap = int((nt >= cap).sum())
        print(f"  {a.kind} {a.method} bars: {nb:,}  (warmup_T={warmup_T:.0f}, "
              f"esperado~{a.bars_per_day:.0f}/día → {nb/max(days,1e-9):.0f}/día real)")
        print(f"  estabilidad: n_ticks min/mediana/máx = {nt.min()}/"
              f"{int(np.median(nt))}/{nt.max()}  | tocaron el cap (max_ticks={cap}): "
              f"{hit_cap} ({100*hit_cap/max(nb,1):.1f}%)")
    nb = len(bars["close"])
    out_dir = os.path.join("data_hist", a.symbol, "bars")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{a.kind}_{a.method}.parquet")
    table = pa.table({c: bars[c] for c in BAR_COLUMNS}).replace_schema_metadata(prov)
    pq.write_table(table, out, compression="snappy")
    print(f"  escrito: {out}  (con metadatos de procedencia)")
    if a.demo:
        print("--- demo normalidad (AFML §2.3.1.3) ---")
        demo_normality(ts, price, qty, side, a.bars_per_day)


if __name__ == "__main__":
    main()
