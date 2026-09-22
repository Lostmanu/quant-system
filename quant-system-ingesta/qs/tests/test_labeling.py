"""Tests de analysis/labeling.py — triple-barrera, meta-label y bet sizing (AFML §3, §10.3)."""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.labeling import triple_barrier, meta_label, bet_size


class TestTripleBarrera:
    def test_take_profit_primero(self):
        p = np.array([100, 101, 102, 103.])
        b, r = triple_barrier(p, [0], [3], [0.02], pt_mult=1, sl_mult=1)
        assert b[0] == 1 and abs(r[0] - 0.02) < 1e-9       # toca TP (+2%) en idx 2

    def test_stop_loss_primero(self):
        p = np.array([100, 99.5, 99, 98.])
        b, r = triple_barrier(p, [0], [3], [0.01], pt_mult=2, sl_mult=1)
        assert b[0] == -1 and abs(r[0] - (-0.01)) < 1e-9   # toca SL (−1%) en idx 2

    def test_barrera_vertical(self):
        p = np.array([100, 100.2, 100.1])
        b, r = triple_barrier(p, [0], [2], [0.05], pt_mult=1, sl_mult=1)
        assert b[0] == 0 and abs(r[0] - 0.001) < 1e-9      # nadie toca → retorno final

    def test_take_profit_gana_si_empata_en_indice(self):
        # si TP y SL se tocan en la misma barra, gana TP (j_pt <= j_sl)
        p = np.array([100, 102.])
        b, _ = triple_barrier(p, [0], [1], [0.02], pt_mult=1, sl_mult=0.1)
        assert b[0] == 1


class TestMetaLabel:
    def test_acierto_y_fallo(self):
        side = np.array([1, 1, -1])
        ret = np.array([0.02, -0.01, -0.02])              # side·ret = [+, −, +]
        assert meta_label(side, ret).tolist() == [1, 0, 1]


class TestBetSize:
    def test_cero_sin_edge(self):
        assert abs(float(bet_size(0.5))) < 1e-9            # p=0.5 → sin apuesta

    def test_valores_de_la_tabla_afml(self):
        assert abs(float(bet_size(0.9)) - 0.8176) < 1e-3   # tabla §10.3
        assert abs(float(bet_size(0.6)) - 0.1617) < 1e-3

    def test_monotono_y_acotado(self):
        b = bet_size(np.array([0.5, 0.6, 0.7, 0.8, 0.9, 0.99]))
        assert (np.diff(b) > 0).all()                      # crece con la convicción
        assert (b >= 0).all() and (b <= 1).all()
