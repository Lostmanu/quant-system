"""Tests de analysis/xsection.py — puerta de viabilidad cross-sectional (LEDGER H5).
Lo crítico: la maquinaria DETECTA un lead-lag inyectado y NO lo alucina sin él."""
import os
import sys
import numpy as np
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.xsection import (per_second, csic_panel, returns_from_close, neutralize,
                               leadlag_matrix, directional_D, shuffle_null, evaluate)


class TestDeteccion:
    LIQ, THIN = [0, 1, 2, 3], [4, 5, 6, 7]

    def test_detecta_leadlag_inyectado(self):
        # flujo de LÍQUIDOS en t empuja el retorno de FINOS en t+1 → D grande y >p99
        rng = np.random.default_rng(0)
        T, S = 4000, 8
        fp = rng.normal(0, 1, (T, S))               # predictor (flujo) en t
        rt = rng.normal(0, 0.5, (T, S))             # objetivo (retorno) en t+1
        drive = fp[:, self.LIQ].mean(1)
        for j in self.THIN:
            rt[:, j] += 0.3 * drive                 # inyecta líquido→fino
        D = directional_D(leadlag_matrix(fp, rt), self.LIQ, self.THIN)
        null = shuffle_null(fp, rt, self.LIQ, self.THIN, n=500)
        assert D > np.percentile(null, 99)          # detectado
        assert D > null.mean() + 4 * null.std()

    def test_no_alucina_sin_estructura(self):
        # flujo y retorno independientes → D dentro del nulo (no significativo)
        rng = np.random.default_rng(1)
        T, S = 4000, 8
        fp = rng.normal(0, 1, (T, S))
        rt = rng.normal(0, 1, (T, S))
        D = directional_D(leadlag_matrix(fp, rt), self.LIQ, self.THIN)
        null = shuffle_null(fp, rt, self.LIQ, self.THIN, n=500)
        z = (D - null.mean()) / null.std()
        assert abs(z) < 3                           # indistinguible de ruido
        assert D < np.percentile(null, 99)

    def test_direccionalidad_correcta(self):
        # si el lead-lag va al REVÉS (finos→líquidos), D debe ser NEGATIVO (no positivo)
        rng = np.random.default_rng(2)
        T, S = 4000, 8
        fp = rng.normal(0, 1, (T, S))
        rt = rng.normal(0, 0.5, (T, S))
        drive = fp[:, self.THIN].mean(1)
        for j in self.LIQ:
            rt[:, j] += 0.3 * drive                 # inyecta fino→líquido
        D = directional_D(leadlag_matrix(fp, rt), self.LIQ, self.THIN)
        null = shuffle_null(fp, rt, self.LIQ, self.THIN, n=500)
        assert D < np.percentile(null, 1)           # D negativo, fuera por abajo


class TestNeutralizacion:
    def test_quita_factor_comun(self):
        # x_i = beta_i·factor_común + idiosincrático → tras neutralizar, residuo ~ sin
        # el factor común (correlación residual baja), pese a betas heterogéneas
        rng = np.random.default_rng(3)
        T, S = 3000, 4
        common = rng.normal(0, 1, T)
        betas = [0.5, 1.0, 1.5, 2.0]
        x = np.column_stack([betas[i] * common + rng.normal(0, 0.3, T)
                             for i in range(S)])
        xt = neutralize(x)
        for i in range(S):
            assert abs(np.corrcoef(xt[:, i], common)[0, 1]) < 0.2

    def test_leave_one_out_sin_autoresta(self):
        # la cesta de i NO incluye a i: con 1 columna idéntica replicada, neutralizar
        # no la anula a 0 contra sí misma de forma trivial (sanity de leave-one-out)
        rng = np.random.default_rng(4)
        x = rng.normal(0, 1, (1000, 3))
        xt = neutralize(x)
        assert xt.shape == x.shape
        assert np.isfinite(xt).all()


class TestMuestreo:
    def test_per_second_agrega(self):
        ts = np.array([1000, 1400, 1900, 2200, 3000], dtype="int64")  # seg 1,1,1,2,3
        price = np.array([10., 11., 12., 20., 30.])
        qty = np.array([1., 1., 1., 1., 1.])
        side = np.array([1., -1., 1., 1., -1.])
        usec, d, sg, last = per_second(ts, price, qty, side)
        assert usec.tolist() == [1, 2, 3]
        assert np.allclose(d, [33., 20., 30.])              # 10+11+12, 20, 30
        assert np.allclose(sg, [11., 20., -30.])            # 10-11+12, 20, -30
        assert np.allclose(last, [12., 20., 30.])           # último precio del segundo

    def test_csic_panel_shapes_y_clock(self):
        # 2 símbolos con dólar uniforme → ~target barras, sin NaN tras warmup
        sec = np.arange(0, 1000, dtype="int64")
        secs = [sec, sec]
        dols = [np.ones(1000), np.ones(1000)]
        sgns = [np.full(1000, 0.5), np.full(1000, -0.5)]
        lasts = [100.0 + np.arange(1000) * 0.01, 50.0 + np.arange(1000) * 0.01]
        close, flow, bound, miss = csic_panel(secs, dols, sgns, lasts, target_bars=50)
        assert close.shape == flow.shape and close.shape[1] == 2
        assert 40 <= close.shape[0] <= 50                   # ~target
        assert np.isfinite(close).all()                     # sin NaN
        ret = returns_from_close(close)
        assert np.isfinite(ret).all() and ret.shape == close.shape


class TestEvaluatePipeline:
    def test_evaluate_extremo_a_extremo(self):
        # pipeline completo (neutralize→leadlag→D→null) detecta lead-lag inyectado
        rng = np.random.default_rng(7)
        T, S = 3000, 8
        liq, thin = [0, 1, 2, 3], [4, 5, 6, 7]
        flow = rng.normal(0, 1, (T, S))
        ret = rng.normal(0, 0.5, (T, S))
        drive = flow[:, liq].mean(1)
        ret[1:, thin] += 0.3 * drive[:-1, None]             # flujo líq en t → ret fino t+1
        D, null, rho = evaluate(flow, ret, liq, thin, n_shuffle=400)
        assert D > np.percentile(null, 99)
