"""Tests de analysis/haircut.py — haircut del Sharpe por multiple testing (Harvey-Liu)."""
import os
import sys
import math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.haircut import (sharpe_to_t, t_to_pvalue, harmonic_c, bonferroni, holm,
                              bhy, haircut_sharpe, haircut_bonferroni)


class TestConversiones:
    def test_sharpe_t_pvalue(self):
        assert abs(sharpe_to_t(0.1, 100) - 1.0) < 1e-12
        assert abs(t_to_pvalue(1.959964) - 0.05) < 1e-4      # t crítico bilateral 5%
        assert abs(t_to_pvalue(0.0) - 1.0) < 1e-12


class TestAjustes:
    def test_bonferroni_exacto(self):
        assert np.allclose(bonferroni(np.array([0.01, 0.04, 0.5])), [0.03, 0.12, 1.0])

    def test_ajuste_nunca_baja_el_p(self):
        rng = np.random.default_rng(0)
        p = rng.uniform(0, 1, 50)
        for adj in (bonferroni(p), holm(p), bhy(p)):
            assert (adj >= p - 1e-12).all() and (adj <= 1.0 + 1e-9).all()

    def test_monotonia_por_rango(self):
        rng = np.random.default_rng(1)
        p = rng.uniform(0, 1, 40)
        for fn in (holm, bhy):
            s = fn(p)[np.argsort(p)]
            assert (np.diff(s) >= -1e-12).all()              # no decreciente en el rango

    def test_harmonic_c(self):
        assert abs(harmonic_c(100) - (math.log(100) + 0.5772156649)) < 0.01


class TestHaircutNoLineal:
    def test_marginal_casi_total_alto_poco(self):
        # CLAVE (resultado central de Harvey-Liu): el haircut es NO LINEAL — el Sharpe
        # marginal se penaliza casi al 100 %, el excepcional muy poco. La regla del 50 %
        # es económicamente incorrecta.
        n, N = 240, 100
        _, hc_marginal = haircut_bonferroni(2.0 / math.sqrt(n), n, N)   # t≈2 marginal
        _, hc_fuerte = haircut_bonferroni(5.0 / math.sqrt(n), n, N)     # t≈5 excepcional
        assert hc_marginal > 0.9
        assert hc_fuerte < 0.4
        assert hc_fuerte < hc_marginal

    def test_mas_tests_mas_haircut(self):
        n = 240
        sr = 4.0 / math.sqrt(n)
        _, hc_pocos = haircut_bonferroni(sr, n, 10)
        _, hc_muchos = haircut_bonferroni(sr, n, 1000)
        assert hc_muchos > hc_pocos

    def test_hsr_no_negativo(self):
        hsr, hc = haircut_sharpe(0.13, 240, p_adjusted=1.0)   # p_adj=1 → t*=0 → HSR=0
        assert hsr == 0.0 and hc == 1.0
