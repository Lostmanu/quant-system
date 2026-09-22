"""Tests de analysis/overfit.py — PSR, DSR y PBO (Bailey-López de Prado)."""
import os
import sys
import math
import numpy as np
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.overfit import (psr, expected_max_sharpe, deflated_sharpe, pbo,
                              effective_n_trials, min_track_record_length,
                              _norm_cdf, _norm_ppf)


class TestNormal:
    def test_cdf_ppf_inversas(self):
        assert abs(_norm_cdf(0.0) - 0.5) < 1e-12
        for p in (0.05, 0.25, 0.5, 0.84, 0.975):
            assert abs(_norm_cdf(_norm_ppf(p)) - p) < 1e-6


class TestPSR:
    def test_sharpe_cero_da_medio(self):
        assert abs(psr(0.0, 100) - 0.5) < 1e-9          # Φ(0)=0.5

    def test_sharpe_positivo_supera_medio(self):
        assert psr(0.1, 250) > 0.5

    def test_mas_muestra_mas_confianza(self):
        assert psr(0.1, 1000) > psr(0.1, 100)           # mismo SR, más n → más confianza

    def test_cola_pesada_baja_la_confianza(self):
        # curtosis alta (colas) reduce el PSR para el mismo Sharpe
        assert psr(0.1, 500, skew=0.0, kurt=8.0) < psr(0.1, 500, skew=0.0, kurt=3.0)


class TestDSR:
    def test_max_sharpe_crece_con_ensayos(self):
        assert expected_max_sharpe(100) > expected_max_sharpe(10) > expected_max_sharpe(2)

    def test_pocos_ensayos_invalido(self):
        with pytest.raises(ValueError):
            expected_max_sharpe(1)

    def test_mas_ensayos_deshincha_mas(self):
        # mismo Sharpe; más ensayos → benchmark mayor → DSR menor (más deshinchado)
        d_pocos = deflated_sharpe(0.15, 1000, n_trials=5, sr_std=0.1)
        d_muchos = deflated_sharpe(0.15, 1000, n_trials=5000, sr_std=0.1)
        assert d_pocos > d_muchos


class TestNeffYMinTRL:
    def test_n_eff_interpola_entre_1_y_N(self):
        assert effective_n_trials(100, 0.0) == 100        # sin correlación → N
        assert effective_n_trials(100, 1.0) == 1.0        # todos iguales → 1
        assert 1 < effective_n_trials(100, 0.5) < 100     # intermedio
        assert effective_n_trials(100, 0.9) < effective_n_trials(100, 0.1)  # monótono

    def test_mintrl_ejemplo_tres_anos(self):
        # SR 0.95 anualizado diario → SR per-día = 0.95/√252; al 95% ≈ 756 días (~3 años)
        sr_d = 0.95 / np.sqrt(252)
        trl = min_track_record_length(sr_d, target_prob=0.95)
        assert 700 < trl < 820

    def test_mintrl_objetivo_mas_exigente_pide_mas_datos(self):
        sr_d = 0.95 / np.sqrt(252)
        assert min_track_record_length(sr_d, 0.99) > min_track_record_length(sr_d, 0.95)

    def test_mintrl_infinito_si_sr_no_supera_benchmark(self):
        assert min_track_record_length(0.05, sr_benchmark=0.05) == math.inf


class TestPBO:
    def test_ruido_da_pbo_medio_en_promedio(self):
        # RUIDO puro: la mejor IS es azar OOS → E[PBO]≈0.5. Una sola matriz NO basta (las
        # C(S,S/2) combinaciones comparten datos → correlacionadas); se promedia sobre
        # realizaciones independientes.
        rng = np.random.default_rng(0)
        ps = [pbo(rng.normal(0, 1, (160, 8)), n_splits=8)[0] for _ in range(30)]
        assert 0.40 < float(np.mean(ps)) < 0.60
        assert len(pbo(rng.normal(0, 1, (160, 8)), 8)[1]) == math.comb(8, 4)

    def test_senal_real_da_pbo_bajo(self):
        # una columna con drift REAL y consistente → mejor IS = mejor OOS → PBO≈0
        rng = np.random.default_rng(1)
        M = rng.normal(0, 1, (200, 10))
        M[:, 0] += 0.5                                   # señal verdadera en la estrategia 0
        p, _ = pbo(M, n_splits=10)
        assert p < 0.15

    def test_guardas(self):
        with pytest.raises(ValueError):
            pbo(np.zeros((100, 1)))                      # < 2 estrategias
        with pytest.raises(ValueError):
            pbo(np.zeros((100, 5)), n_splits=7)          # S impar
