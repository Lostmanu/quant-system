"""Tests de analysis/book.py — features de libro L2 (cimiento H1/H3)."""
import os
import sys
import numpy as np
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.book import (mid, relative_spread, microprice, book_imbalance,
                           depth_within, depth_imbalance, book_resilience)


def _book(bid_px, bid_sz, ask_px, ask_sz):
    f = lambda x: np.asarray(x, "float64")
    return f(bid_px), f(bid_sz), f(ask_px), f(ask_sz)


class TestFeaturesSnapshot:
    def test_mid_y_spread(self):
        bp, bs, ap, as_ = _book([[99.5]], [[1]], [[100.5]], [[1]])
        assert mid(bp, ap)[0] == 100.0
        assert abs(relative_spread(bp, ap)[0] - 0.01) < 1e-12     # (100.5-99.5)/100

    def test_microprice_se_desplaza_con_la_presion(self):
        # más tamaño en el BID (presión compradora) → microprice POR ENCIMA del mid
        bp, bs, ap, as_ = _book([[99.0]], [[9.0]], [[101.0]], [[1.0]])
        mp = microprice(bp, bs, ap, as_)[0]
        assert mp > mid(bp, ap)[0]
        assert abs(mp - (99.0 * 1.0 + 101.0 * 9.0) / 10.0) < 1e-12   # =100.8
        # simétrico: más tamaño en el ASK → microprice por DEBAJO del mid
        bp, bs, ap, as_ = _book([[99.0]], [[1.0]], [[101.0]], [[9.0]])
        assert microprice(bp, bs, ap, as_)[0] < mid(bp, ap)[0]

    def test_microprice_cae_al_mid_si_vacio(self):
        bp, bs, ap, as_ = _book([[99.0]], [[0.0]], [[101.0]], [[0.0]])
        assert microprice(bp, bs, ap, as_)[0] == 100.0

    def test_book_imbalance(self):
        bp, bs, ap, as_ = _book([[100, 99]], [[3, 1]], [[101, 102]], [[1, 1]])
        assert abs(book_imbalance(bs, as_, k=1)[0] - 0.5) < 1e-12     # (3-1)/(3+1)
        assert abs(book_imbalance(bs, as_, k=2)[0] - (4 - 2) / 6) < 1e-12

    def test_depth_within_banda(self):
        # mid=100, δ=0.01 → banda [99,101]. bids 99.5(sz2 dentro),98(sz5 fuera);
        # asks 100.5(sz3 dentro),102(sz7 fuera)
        bp, bs, ap, as_ = _book([[99.5, 98.0]], [[2, 5]], [[100.5, 102.0]], [[3, 7]])
        d_bid, d_ask = depth_within(bp, bs, ap, as_, delta=0.01)
        assert d_bid[0] == 2.0 and d_ask[0] == 3.0
        assert abs(depth_imbalance(bp, bs, ap, as_, 0.01)[0] - (2 - 3) / 5) < 1e-12

    def test_guardas(self):
        bp, bs, ap, as_ = _book([[100.0]], [[1.0]], [[101.0]], [[1.0]])
        with pytest.raises(ValueError):
            book_imbalance(bs, as_, k=0)
        with pytest.raises(ValueError):
            depth_within(bp, bs, ap, as_, delta=0.0)
        bad = np.array([[100.0, float("inf")]])
        with pytest.raises(ValueError):
            mid_in = np.array([[100.0]])
            depth_within(bad, np.array([[1.0, 1.0]]), np.array([[101.0, 102.0]]),
                         np.array([[1.0, 1.0]]), 0.01)


class TestResiliencia:
    def test_detecta_recuperacion(self):
        # profundidad estable en 100, cae a 40 durante 5 snapshots, vuelve a 100.
        # ref≈100 → caída ≥50%. target = 40 + 0.5·100·0.5 = 65 → recupera en snapshot 5.
        depth = np.full(300, 100.0)
        depth[150:155] = 40.0
        med, times = book_resilience(depth, drop=0.5, horizon=50)
        assert len(times) == 1 and med == 5.0

    def test_sin_eventos_devuelve_nan(self):
        depth = np.full(300, 100.0)                       # libro plano: sin caídas
        med, times = book_resilience(depth, drop=0.5, horizon=50)
        assert np.isnan(med) and len(times) == 0

    def test_serie_corta_nan(self):
        med, times = book_resilience(np.full(10, 100.0), horizon=50)
        assert np.isnan(med)
