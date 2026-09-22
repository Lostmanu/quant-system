"""Tests de analysis/regime.py — clasificación de régimen (Plan §2.1)."""
import os
import sys
import numpy as np
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.regime import (classify_regime, volatility_zscore, variance_ratio,
                             label_from_signals, BURN, MIN_SIGMA)


def _close_from_returns(r):
    return np.exp(np.concatenate([[0.0], np.cumsum(r)]))   # precio>0 desde retornos


class TestVolatilidad:
    def test_zscore_nan_hasta_calentar(self):
        # antes de la ventana N no hay σ_local; y Z necesita ≥2 σ_local previos
        rng = np.random.default_rng(0)
        r = rng.normal(0, 0.001, 600)
        sigma, z = volatility_zscore(_close_from_returns(r), N=50)
        assert np.isnan(z[:50]).all()                      # sin ventana, sin σ_local
        assert np.isfinite(sigma[50:]).all()               # σ_local definido desde N

    def test_zscore_oracle_estrictamente_anterior(self):
        # ORACLE independiente: z[t] = (σ_local[t] − media(σ_local[N..t-1])) /
        # std(σ_local[N..t-1]), normalización ESTRICTAMENTE anterior. Si producción
        # incluyera σ_local[t] en su propia normalización (fuga CONTEMPORÁNEA,
        # invisible al test de truncamiento), divergiría de esto.
        rng = np.random.default_rng(5)
        r = np.concatenate([rng.normal(0, 0.001, 300), rng.normal(0, 0.005, 300)])
        close = _close_from_returns(r)
        N = 40
        sigma, z = volatility_zscore(close, N)
        checked = 0
        for t in range(N + 3, len(close)):
            prior = sigma[N:t]                              # σ_local de N..t-1 (anterior)
            mu, sd = prior.mean(), prior.std()
            if sd > MIN_SIGMA and sigma[t] > MIN_SIGMA:
                assert abs(z[t] - (sigma[t] - mu) / sd) < 1e-6
                checked += 1
            else:
                assert np.isnan(z[t])
        assert checked > 100                               # cubre la mayoría de la serie

    def test_salto_de_volatilidad_detectado(self):
        # primera mitad vol baja, segunda mitad vol alta → Z_σ grande → régimen alta-vol
        rng = np.random.default_rng(1)
        r = np.concatenate([rng.normal(0, 0.0005, 3000),
                            rng.normal(0, 0.01, 3000)])
        out = classify_regime(_close_from_returns(r), N=300, k=20, dwell=20,
                              burn_in=600)
        reg = out["regime"]
        # en la zona de alta vol (bien dentro), el régimen debe ser alta-vol (1 o 2)
        cola = reg[5000:5900]
        cola = cola[cola != BURN]
        assert len(cola) > 100
        assert (np.isin(cola, [1, 2])).mean() > 0.8        # mayoría alta volatilidad


class TestVarianceRatio:
    def test_tendencia_vr_mayor_que_1(self):
        # retornos con autocorrelación POSITIVA (AR(1) phi>0) → persistencia → VR>1
        rng = np.random.default_rng(2)
        n = 6000
        r = np.zeros(n)
        for i in range(1, n):
            r[i] = 0.45 * r[i - 1] + rng.normal(0, 0.001)
        vr = variance_ratio(_close_from_returns(r), N=500, k=20)
        v = vr[np.isfinite(vr)]
        assert np.median(v) > 1.05                          # tendencia

    def test_reversion_vr_menor_que_1(self):
        # autocorrelación NEGATIVA (phi<0) → reversión → VR<1
        rng = np.random.default_rng(3)
        n = 6000
        r = np.zeros(n)
        for i in range(1, n):
            r[i] = -0.45 * r[i - 1] + rng.normal(0, 0.001)
        vr = variance_ratio(_close_from_returns(r), N=500, k=20)
        v = vr[np.isfinite(vr)]
        assert np.median(v) < 0.95                          # rango/reversión

    def test_paseo_aleatorio_insesgado_en_media(self):
        # CLAVE (insesgadez Lo-MacKinlay): el VR verdadero de un paseo aleatorio = 1.
        # El estimador SIMPLE Var(r^k)/(k·Var(r¹)) está sesgado a la baja: la MEDIA
        # sobre paseos INDEPENDIENTES cae a ~0.98 (sesgo −2%) y descentra la histéresis
        # hacia 'rango'. El INSESGADO se queda en ~1.005. Una sola serie no sirve (sus
        # ventanas solapadas son una única trayectoria, no muestras independientes):
        # promediamos una estimación por paseo. FALLA con el simple (|−0.0196|>0.012).
        rng = np.random.default_rng(20260617)
        N, k, paths = 2000, 50, 1000
        est = np.empty(paths)
        for i in range(paths):
            close = _close_from_returns(rng.normal(0, 0.001, N))  # N+1 precios → 1 VR
            est[i] = variance_ratio(close, N=N, k=k)[N]            # única estim. causal
        assert np.isfinite(est).all()
        assert abs(est.mean() - 1.0) < 0.012                      # insesgado en media


class TestHysteresisYDwell:
    P = dict(z_enter=1.1, z_exit=0.9, vr_enter=1.05, vr_exit=0.95)

    def test_histeresis_mantiene_estado_en_banda(self):
        # vr en banda (dir='range' inicial); z entra alta, se mantiene en la banda
        # [0.9,1.1], y sale baja
        z = np.array([1.2, 1.0, 1.0, 0.95, 0.8])
        vr = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        reg = label_from_signals(z, vr, dwell=1, burn_in=0, **self.P)
        # 2=alta+rango mientras vol=high; 4=baja+rango tras z<0.9
        assert reg.tolist() == [2, 2, 2, 2, 4]

    def test_dwell_suprime_flip_breve(self):
        # un flip de 1 tick a baja vol NO debe cambiar el régimen si dwell=3
        z = np.array([1.2, 0.8, 1.2, 1.2, 1.2])
        vr = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        reg = label_from_signals(z, vr, dwell=3, burn_in=0, **self.P)
        assert reg.tolist() == [2, 2, 2, 2, 2]              # el flip breve se ignora

    def test_dwell_acepta_cambio_sostenido(self):
        # baja vol sostenida 3 ticks → se acepta el cambio
        z = np.array([1.2, 0.8, 0.8, 0.8, 0.8])
        vr = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        reg = label_from_signals(z, vr, dwell=3, burn_in=0, **self.P)
        assert reg.tolist() == [2, 2, 2, 4, 4]              # commit en el 3er tick bajo


class TestCausalidadYBordes:
    def test_invarianza_ante_truncamiento(self):
        # CRÍTICO: regime[t] depende SOLO de close[0..t]; truncar la serie no altera
        # las clasificaciones previas (sin look-ahead / sesgo de anticipación)
        rng = np.random.default_rng(7)
        r = rng.normal(0, 0.002, 800) + 0.0003 * np.sin(np.arange(800) / 20)
        close = _close_from_returns(r)
        kw = dict(N=50, k=10, dwell=5, burn_in=100)
        full = classify_regime(close, **kw)
        cut = 500
        pref = classify_regime(close[:cut], **kw)
        assert np.array_equal(full["regime"][:cut], pref["regime"])
        for key in ("sigma_local", "z_sigma", "vr"):
            assert np.allclose(full[key][:cut], pref[key], equal_nan=True)

    def test_reconstruccion_punto_a_punto(self):
        # complemento al truncamiento: clasificar [0..t] da el MISMO regime en t que
        # clasificar la serie completa (sin dependencia de futuro)
        rng = np.random.default_rng(11)
        close = _close_from_returns(rng.normal(0, 0.003, 400))
        kw = dict(N=40, k=8, dwell=4, burn_in=80)
        full = classify_regime(close, **kw)
        for t in (120, 200, 333, 399):
            pt = classify_regime(close[:t + 1], **kw)
            assert pt["regime"][t] == full["regime"][t]

    def test_burn_in_emite_menos_uno(self):
        rng = np.random.default_rng(8)
        close = _close_from_returns(rng.normal(0, 0.002, 500))
        out = classify_regime(close, N=50, k=10, dwell=5, burn_in=200)
        assert (out["regime"][:200] == BURN).all()

    def test_vol_constante_no_clasifica_ruido(self):
        # retornos constantes (vol real ~0) → σ_local es roundoff → la guarda
        # MIN_SIGMA deja z/vr en NaN → ningún régimen real (todo -1)
        close = _close_from_returns(np.full(600, 0.001))
        out = classify_regime(close, N=50, k=10, dwell=5, burn_in=100)
        assert (out["regime"] == BURN).all()

    def test_senales_nan_antes_de_la_ventana(self):
        rng = np.random.default_rng(9)
        close = _close_from_returns(rng.normal(0, 0.002, 300))
        N = 50
        sigma, z = volatility_zscore(close, N)
        vr = variance_ratio(close, N, k=10)
        assert np.isnan(sigma[:N]).all() and np.isnan(z[:N]).all()
        assert np.isnan(vr[:N]).all()
        assert np.isfinite(sigma[N:]).all()

    def test_validaciones(self):
        ok = _close_from_returns(np.zeros(100))
        with pytest.raises(ValueError):
            classify_regime(np.array([1.0, -1.0, 2.0]), N=2, k=1)      # precio ≤ 0
        with pytest.raises(ValueError):
            classify_regime(ok, N=10, k=10)                            # N no > k
        with pytest.raises(ValueError):
            classify_regime(ok, N=20, k=5, z_enter=0.9, z_exit=1.1)    # enter<exit
        with pytest.raises(ValueError):
            classify_regime(ok, N=20, k=5, dwell=0)                    # dwell<1
