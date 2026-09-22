"""Tests de analysis/bars.py — barras information-driven AFML §2.3 (Plan 1.6)."""
import os
import sys
import numpy as np
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.bars import standard_bars, imbalance_bars, runs_bars, auto_threshold


def _series(prices, qtys, sides, t0=1000, dt=10):
    n = len(prices)
    ts = np.array([t0 + i * dt for i in range(n)], dtype="int64")
    return (ts, np.array(prices, "float64"), np.array(qtys, "float64"),
            np.array(sides, "float64"))


def _rand_flow(n, seed, p_buy=0.58):
    """Flujo sintético con desequilibrio VARIABLE (qty y signos), para tests donde
    el umbral EWMA debe moverse dentro de las barras."""
    rng = np.random.default_rng(seed)
    qtys = rng.uniform(1.0, 10.0, n)
    sides = rng.choice([1.0, -1.0], n, p=[p_buy, 1 - p_buy])
    prices = 100.0 + np.cumsum(rng.normal(0, 0.05, n))
    ts = (np.arange(n) * 10).astype("int64")
    return ts, prices, qtys, sides


def _imb_reference(ts, price, qty, side, kind, warmup_T, ewma_T_span, ewma_imb_span,
                   max_ticks=None, min_imbalance=1e-12):
    """Referencia INDEPENDIENTE con el umbral congelado EXPLÍCITAMENTE al inicio de
    cada barra. Si producción recalculara el umbral intra-barra, divergiría de
    esto. Siembra idéntica a producción. Devuelve [(start_idx, close_idx), ...]."""
    n = len(price)
    m = (side if kind == "tick" else side * qty if kind == "volume"
         else side * price * qty).astype("float64").tolist()
    aT, ai = 2.0 / (ewma_T_span + 1.0), 2.0 / (ewma_imb_span + 1.0)
    ewmaT = float(warmup_T)
    k = min(max(int(warmup_T), 1), n)
    seed = float(np.mean(m[:k]))
    ewma_imb = seed if abs(seed) > min_imbalance else (
        min_imbalance if seed >= 0 else -min_imbalance)
    closes, i = [], 0
    while i < n:
        thr = max(ewmaT * abs(ewma_imb), min_imbalance)      # CONGELADO
        theta, start, done = 0.0, i, False
        while i < n:
            theta += m[i]
            ewma_imb = ai * m[i] + (1.0 - ai) * ewma_imb
            nt = i - start + 1
            if abs(theta) >= thr or (max_ticks is not None and nt >= max_ticks):
                closes.append((start, i))
                ewmaT = aT * nt + (1.0 - aT) * ewmaT
                i += 1
                done = True
                break
            i += 1
        if not done:
            break
    return closes


def _runs_reference(ts, price, qty, side, kind, warmup_T, ewma_T_span, ewma_run_span,
                    max_ticks=None, min_theta=1e-12):
    """Referencia INDEPENDIENTE de runs: umbral congelado al inicio de barra y EWMA
    actualizadas SOLO al cerrar. Si producción contaminara el umbral intra-barra o
    actualizara las EWMA por tick, divergiría. Devuelve [(start_idx, close_idx), ...]."""
    n = len(price)
    v = (np.ones(n) if kind == "tick" else qty if kind == "volume"
         else price * qty).astype("float64")
    aT = 0.0 if ewma_T_span is None else 2.0 / (ewma_T_span + 1.0)
    aR = 2.0 / (ewma_run_span + 1.0)
    ewmaT = float(warmup_T)
    k = min(max(int(warmup_T), 1), n)
    sseed, vseed = side[:k] > 0, v[:k]
    vmean = float(vseed.mean())
    if vmean <= 0.0:
        vmean = min_theta
    ewmaP = float(sseed.mean())
    ewma_vbuy = float(vseed[sseed].mean()) if sseed.any() else vmean
    ewma_vsell = float(vseed[~sseed].mean()) if (~sseed).any() else vmean
    s_l, v_l = side.tolist(), v.tolist()
    closes, i = [], 0
    while i < n:
        thr = max(ewmaT * max(ewmaP * ewma_vbuy, (1.0 - ewmaP) * ewma_vsell), min_theta)
        buy_acc = sell_acc = 0.0
        n_buy, sum_vbuy, sum_vsell, start, done = 0, 0.0, 0.0, i, False
        while i < n:
            vt = v_l[i]
            if s_l[i] > 0:
                buy_acc += vt; n_buy += 1; sum_vbuy += vt
            else:
                sell_acc += vt; sum_vsell += vt
            nt = i - start + 1
            if max(buy_acc, sell_acc) >= thr or (max_ticks is not None and nt >= max_ticks):
                closes.append((start, i))
                ewmaT = aT * nt + (1.0 - aT) * ewmaT
                ewmaP = aR * (n_buy / nt) + (1.0 - aR) * ewmaP
                if n_buy > 0:
                    ewma_vbuy = aR * (sum_vbuy / n_buy) + (1.0 - aR) * ewma_vbuy
                if nt - n_buy > 0:
                    ewma_vsell = aR * (sum_vsell / (nt - n_buy)) + (1.0 - aR) * ewma_vsell
                i += 1; done = True; break
            i += 1
        if not done:
            break
    return closes


class TestStandardBars:
    def test_tick_bars_cierran_cada_N_y_descartan_cola(self):
        ts, p, q, s = _series([1.0] * 10, [1.0] * 10, [1] * 10)
        b = standard_bars(ts, p, q, s, "tick", threshold=4)
        assert b["n_ticks"] == [4, 4]              # [0..3],[4..7]; [8,9] descartado
        assert b["t_open_ms"] == [1000, 1040] and b["t_close_ms"] == [1030, 1070]

    def test_volume_bars_acumulan_qty(self):
        ts, p, q, s = _series([1.0] * 9, [1.0] * 9, [1] * 9)
        b = standard_bars(ts, p, q, s, "volume", threshold=3)
        assert b["volume"] == [3.0, 3.0, 3.0] and b["n_ticks"] == [3, 3, 3]

    def test_volume_bars_qty_irregular(self):
        # qty 2,2,2 → primer cierre en el tick 1 (cum 4>=3); luego 2,1 (cum 3)
        ts, p, q, s = _series([1.0] * 5, [2, 2, 2, 2, 1], [1] * 5)
        b = standard_bars(ts, p, q, s, "volume", threshold=3)
        assert b["n_ticks"] == [2, 2] and b["volume"] == [4.0, 4.0]

    def test_dollar_bars_y_ohlcv_vwap(self):
        # precios 10,12,11,13 ; qty 1,1,1,1 ; dollar acumulado 10,22,33,46
        ts, p, q, s = _series([10, 12, 11, 13], [1, 1, 1, 1], [1, -1, 1, -1])
        b = standard_bars(ts, p, q, s, "dollar", threshold=30)
        # cierra en el tick 2 (cum 33>=30); barra [10,12,11]
        assert b["open"] == [10.0] and b["close"] == [11.0]
        assert b["high"] == [12.0] and b["low"] == [10.0]
        assert b["n_ticks"] == [3] and b["dollar"][0] == 33.0
        assert abs(b["vwap"][0] - 33.0 / 3) < 1e-9   # Σpq/Σq

    def test_buy_sell_volume_desde_side(self):
        ts, p, q, s = _series([1.0] * 4, [2, 3, 1, 4], [1, -1, 1, -1])
        b = standard_bars(ts, p, q, s, "volume", threshold=6)  # cierra en tick 2
        assert b["buy_volume"] == [3.0] and b["sell_volume"] == [3.0]  # 2+1 / 3

    def test_causalidad_truncar_no_altera_barras_previas(self):
        # añadir trades al final NO puede cambiar las barras ya cerradas (sin look-ahead)
        ts, p, q, s = _series([1, 2, 3, 4, 5, 6, 7, 8], [1] * 8, [1] * 8)
        full = standard_bars(ts, p, q, s, "tick", threshold=3)
        pref = standard_bars(ts[:5], p[:5], q[:5], s[:5], "tick", threshold=3)
        # la 1ª barra (ticks 0..2) debe ser idéntica en ambos
        for c in ("t_open_ms", "t_close_ms", "open", "close", "high", "low"):
            assert pref[c][0] == full[c][0]

    def test_threshold_grande_sin_barras(self):
        ts, p, q, s = _series([1.0] * 3, [1.0] * 3, [1] * 3)
        assert standard_bars(ts, p, q, s, "volume", threshold=1000)["close"] == []

    def test_auto_threshold_escala(self):
        # 2 días, volumen total 200 → ~100/día; 10 barras/día → umbral 10
        ts = np.array([0, 2 * 86_400_000], dtype="int64")
        p = np.array([1.0, 1.0]); q = np.array([100.0, 100.0])
        thr = auto_threshold(ts, p, q, "volume", bars_per_day=10)
        assert abs(thr - 10.0) < 1e-6


class TestImbalanceBars:
    # spans enormes → EWMA congeladas en su init → umbral constante = warmup_T·|m0|
    BIG = 10 ** 9

    def test_tib_flujo_de_compra_cierra_por_umbral(self):
        # todo compras (m=+1), warmup_T=10, umbral≈10 → cierra cada 10 ticks
        n = 35
        ts, p, q, s = _series([1.0] * n, [1.0] * n, [1] * n)
        b = imbalance_bars(ts, p, q, s, "tick", warmup_T=10,
                           ewma_T_span=self.BIG, ewma_imb_span=self.BIG)
        assert b["n_ticks"][0] == 10 and b["n_ticks"][1] == 10  # 3 barras, cola descartada
        assert len(b["close"]) == 3

    def test_coincide_con_referencia_umbral_congelado(self):
        # CRÍTICO (hallazgo code-reviewer): el test antiguo usaba spans infinitos
        # que CONGELAN las EWMA → la causalidad se cumplía trivialmente y NO podía
        # detectar contaminación intra-barra del umbral. Aquí, spans FINITOS + flujo
        # de desequilibrio VARIABLE: producción debe coincidir bit a bit con una
        # referencia de umbral congelado. Si alguien recalcula el umbral dentro de
        # la barra, esto falla.
        ts, p, q, s = _rand_flow(400, seed=7)
        kw = dict(ewma_T_span=15, ewma_imb_span=15, max_ticks=120)
        b = imbalance_bars(ts, p, q, s, "volume", warmup_T=8, **kw)
        ref = _imb_reference(ts, p, q, s, "volume", 8, 15, 15, 120)
        got = [(int(t0 // 10), int(tc // 10))
               for t0, tc in zip(b["t_open_ms"], b["t_close_ms"])]
        assert got == ref and len(got) > 5

    def test_causalidad_prefijo_invariante(self):
        # spans FINITOS (EWMA con memoria entre barras): truncar la serie no altera
        # las barras ya cerradas del prefijo
        ts, p, q, s = _rand_flow(400, seed=3, p_buy=0.6)
        kw = dict(ewma_T_span=15, ewma_imb_span=15, max_ticks=120)
        full = imbalance_bars(ts, p, q, s, "volume", warmup_T=8, **kw)
        cut = int(full["t_close_ms"][4] // 10) + 1
        pref = imbalance_bars(ts[:cut], p[:cut], q[:cut], s[:cut], "volume",
                              warmup_T=8, **kw)
        npref = len(pref["close"])
        assert npref >= 5
        for c in ("t_open_ms", "t_close_ms", "n_ticks", "close", "vwap", "volume"):
            assert pref[c] == full[c][:npref]

    def test_volume_imbalance_pondera_por_qty(self):
        # m = side·qty; compras de qty 5 → θ crece de 5 en 5; warmup_T=2 → umbral 10
        n = 9
        ts, p, q, s = _series([1.0] * n, [5.0] * n, [1] * n)
        b = imbalance_bars(ts, p, q, s, "volume", warmup_T=2,
                           ewma_T_span=self.BIG, ewma_imb_span=self.BIG)
        assert b["n_ticks"][0] == 2 and b["volume"][0] == 10.0  # θ=10≥10 en 2 ticks

    def test_max_ticks_corta_runaway(self):
        # semilla de 10 compras → umbral 10; cap=20 (> umbral, para que la 1ª barra
        # cierre por umbral). 1ª barra: 10 compras → θ=10≥10, nt=10. Luego flujo
        # balanceado: θ oscila ~0, nunca llega a 10 → el cap (20) fuerza el cierre.
        sides = [1.0] * 10 + [1.0, -1.0] * 20
        n = len(sides)
        ts, p, q, s = _series([1.0] * n, [1.0] * n, sides)
        b = imbalance_bars(ts, p, q, s, "tick", warmup_T=10,
                           ewma_T_span=self.BIG, ewma_imb_span=self.BIG, max_ticks=20)
        assert b["n_ticks"][0] == 10                       # cierra por umbral
        assert all(nt == 20 for nt in b["n_ticks"][1:]) and len(b["n_ticks"]) >= 3

    def test_flujo_equilibrado_degenera_a_1tick(self):
        # flujo perfectamente equilibrado → desequilibrio esperado ~0 → umbral al
        # mínimo (clamp) → barras de 1 tick. Patología DOCUMENTADA (ROADMAP), no un
        # fallo: el clamp solo evita umbral 0.
        n = 12
        sides = [1.0, -1.0] * (n // 2)
        ts, p, q, s = _series([1.0] * n, [1.0] * n, sides)
        b = imbalance_bars(ts, p, q, s, "tick", warmup_T=4, max_ticks=6)
        assert all(nt == 1 for nt in b["n_ticks"])


class TestRunsBars:
    BIG = 10 ** 9                                     # spans enormes → EWMA congeladas

    def test_trb_compras_puras_cierra_por_umbral(self):
        # todo compras (v=1, P=1) → umbral=warmup_T·max(1·1,0·1)=warmup_T → cada 10 ticks
        n = 35
        ts, p, q, s = _series([1.0] * n, [1.0] * n, [1] * n)
        b = runs_bars(ts, p, q, s, "tick", warmup_T=10,
                      ewma_T_span=self.BIG, ewma_run_span=self.BIG)
        assert b["n_ticks"][:2] == [10, 10]
        assert len(b["close"]) == 3                    # 30 ticks; cola de 5 descartada

    def test_vrb_pondera_por_qty(self):
        # v=qty=5, todo compras, warmup_T=2 → umbral=2·max(1·5,0·5)=10 → cierra en 2 ticks
        n = 9
        ts, p, q, s = _series([1.0] * n, [5.0] * n, [1] * n)
        b = runs_bars(ts, p, q, s, "volume", warmup_T=2,
                      ewma_T_span=self.BIG, ewma_run_span=self.BIG)
        assert b["n_ticks"][0] == 2 and b["volume"][0] == 10.0

    def test_coincide_con_referencia_umbral_congelado(self):
        # spans FINITOS + flujo de desequilibrio VARIABLE: producción debe coincidir
        # bit a bit con la referencia de umbral congelado. Si alguien recalcula el
        # umbral dentro de la barra o actualiza las EWMA por tick (no por barra), falla.
        ts, p, q, s = _rand_flow(400, seed=7)
        kw = dict(ewma_T_span=15, ewma_run_span=15, max_ticks=120)
        b = runs_bars(ts, p, q, s, "volume", warmup_T=8, **kw)
        ref = _runs_reference(ts, p, q, s, "volume", 8, 15, 15, 120)
        got = [(int(t0 // 10), int(tc // 10))
               for t0, tc in zip(b["t_open_ms"], b["t_close_ms"])]
        assert got == ref and len(got) > 5

    def test_causalidad_prefijo_invariante(self):
        # truncar la serie no altera las barras ya cerradas del prefijo (sin look-ahead)
        ts, p, q, s = _rand_flow(400, seed=3, p_buy=0.6)
        kw = dict(ewma_T_span=15, ewma_run_span=15, max_ticks=120)
        full = runs_bars(ts, p, q, s, "volume", warmup_T=8, **kw)
        cut = int(full["t_close_ms"][4] // 10) + 1
        pref = runs_bars(ts[:cut], p[:cut], q[:cut], s[:cut], "volume",
                         warmup_T=8, **kw)
        npref = len(pref["close"])
        assert npref >= 5
        for c in ("t_open_ms", "t_close_ms", "n_ticks", "close", "vwap", "volume"):
            assert pref[c] == full[c][:npref]

    def test_no_degenera_donde_imbalance_si(self):
        # CLAVE: el MISMO flujo perfectamente alternado que degenera las imbalance a
        # 1 tick (test_flujo_equilibrado_degenera_a_1tick) NO colapsa las de runs:
        # acumulan cada lado por separado, θ≈0.5·T crece LINEAL → cierran a T≈3-5.
        # Afirmamos la propiedad robusta (ni 1-tick ni al cap), no el recuento exacto:
        # con flujo balanceado el cierre cae en el empate θ=umbral, sensible al ε de
        # las EWMA (no perfectamente congeladas con span finito); lo de fondo —que NO
        # degenera— es estable.
        n = 12
        sides = [1.0, -1.0] * (n // 2)
        ts, p, q, s = _series([1.0] * n, [1.0] * n, sides)
        br = runs_bars(ts, p, q, s, "tick", warmup_T=4,
                       ewma_T_span=self.BIG, ewma_run_span=self.BIG, max_ticks=6)
        assert len(br["n_ticks"]) >= 2
        assert min(br["n_ticks"]) >= 3 and max(br["n_ticks"]) < 6   # ni 1-tick ni cap
        bi = imbalance_bars(ts, p, q, s, "tick", warmup_T=4, max_ticks=6)
        assert all(nt == 1 for nt in bi["n_ticks"])    # contraste: imbalance SÍ degenera

    def test_modo_fijo_longitud_anclada(self):
        # modo POR DEFECTO (ewma_T_span=None): E_0[T] fijo en warmup_T. Con todo
        # compras (P=1) → umbral=warmup_T·1·1=warmup_T constante → TODAS las barras =
        # warmup_T ticks, sin deriva por muchas barras que pasen (vs el realimentado).
        n = 55
        ts, p, q, s = _series([1.0] * n, [1.0] * n, [1] * n)
        b = runs_bars(ts, p, q, s, "tick", warmup_T=10)   # ewma_T_span=None por defecto
        assert b["n_ticks"] == [10, 10, 10, 10, 10]        # ancladas; cola de 5 descartada

    def test_modo_fijo_coincide_con_referencia(self):
        # modo fijo con flujo variable: producción == oracle de umbral congelado bit a
        # bit (la rama aT=0 no debe romper la coincidencia con la referencia).
        ts, p, q, s = _rand_flow(400, seed=11)
        b = runs_bars(ts, p, q, s, "volume", warmup_T=8, ewma_T_span=None,
                      ewma_run_span=15, max_ticks=120)
        ref = _runs_reference(ts, p, q, s, "volume", 8, None, 15, 120)
        got = [(int(t0 // 10), int(tc // 10))
               for t0, tc in zip(b["t_open_ms"], b["t_close_ms"])]
        assert got == ref and len(got) > 5

    def test_invariantes_de_barra(self):
        ts, p, q, s = _rand_flow(500, seed=2, p_buy=0.55)
        b = runs_bars(ts, p, q, s, "dollar", warmup_T=10, ewma_T_span=20,
                      ewma_run_span=20, max_ticks=200)
        nb = len(b["close"])
        assert nb > 5
        for i in range(nb):
            assert abs(b["buy_volume"][i] + b["sell_volume"][i]
                       - b["volume"][i]) < 1e-9
            assert b["low"][i] <= b["open"][i] <= b["high"][i]
            assert b["low"][i] <= b["close"][i] <= b["high"][i]
            assert b["t_open_ms"][i] <= b["t_close_ms"][i]
        assert b["t_close_ms"] == sorted(b["t_close_ms"])


class TestInvariantesYBordes:
    def test_invariantes_de_barra(self):
        ts, p, q, s = _rand_flow(500, seed=1, p_buy=0.5)
        b = standard_bars(ts, p, q, s, "dollar", float((p * q).sum()) / 20)
        nb = len(b["close"])
        assert nb > 0
        for i in range(nb):
            assert abs(b["vwap"][i] - b["dollar"][i] / b["volume"][i]) < 1e-9
            assert abs(b["buy_volume"][i] + b["sell_volume"][i]
                       - b["volume"][i]) < 1e-9
            assert b["t_open_ms"][i] <= b["t_close_ms"][i]
            assert b["low"][i] <= b["open"][i] <= b["high"][i]
            assert b["low"][i] <= b["close"][i] <= b["high"][i]
        assert b["t_close_ms"] == sorted(b["t_close_ms"])      # no decreciente

    def test_nan_inf_lanza(self):
        ts, p, q, s = _series([1.0, float("inf"), 1.0], [1, 1, 1], [1, 1, 1])
        with pytest.raises(ValueError):
            standard_bars(ts, p, q, s, "tick", threshold=2)

    def test_side_no_unitario_lanza(self):
        ts, p, q, s = _series([1.0, 1.0, 1.0], [1, 1, 1], [1, 0, 1])
        with pytest.raises(ValueError):
            standard_bars(ts, p, q, s, "volume", threshold=2)
        with pytest.raises(ValueError):
            imbalance_bars(ts, p, q, s, "tick", warmup_T=2)
        with pytest.raises(ValueError):
            runs_bars(ts, p, q, s, "tick", warmup_T=2)

    def test_warmup_T_no_positivo_lanza(self):
        ts, p, q, s = _series([1.0] * 4, [1.0] * 4, [1] * 4)
        with pytest.raises(ValueError):
            imbalance_bars(ts, p, q, s, "tick", warmup_T=0)
        with pytest.raises(ValueError):
            runs_bars(ts, p, q, s, "tick", warmup_T=0)

    def test_un_solo_trade(self):
        ts, p, q, s = _series([5.0], [2.0], [1])
        b = standard_bars(ts, p, q, s, "volume", threshold=1)
        assert b["n_ticks"] == [1] and b["close"] == [5.0] and b["volume"] == [2.0]

    def test_auto_threshold_guardas(self):
        with pytest.raises(ValueError):
            auto_threshold(np.array([], "int64"), np.array([]), np.array([]), "tick", 10)
        ts = np.array([0, 86_400_000], "int64")
        with pytest.raises(ValueError):
            auto_threshold(ts, np.array([1.0, 1.0]), np.array([1.0, 1.0]), "tick", 0)
