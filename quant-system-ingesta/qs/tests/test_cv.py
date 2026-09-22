"""Tests de analysis/cv.py — purga, embargo, Purged K-Fold y CPCV (AFML cap. 7 y 12)."""
import os
import sys
import numpy as np
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.cv import (purged_train_mask, purged_kfold, cpcv_splits, n_backtest_paths,
                         _test_blocks)


class TestPurgaYEmbargo:
    def test_purga_quita_solapados(self):
        # CLAVE (anti-fuga): obs en t=0..9, etiqueta que dura 2 (t1=t0+2). Test={5},
        # ventana [5,7]. Deben PURGARSE las obs cuya etiqueta solapa [5,7] = idx 3,4,6,7;
        # sobreviven 0,1,2 (terminan antes de 5) y 8,9 (empiezan después de 7).
        t0 = np.arange(10.0); t1 = t0 + 2
        train = purged_train_mask(t0, t1, [5], embargo_pct=0.0)
        assert np.where(train)[0].tolist() == [0, 1, 2, 8, 9]

    def test_embargo_quita_posteriores(self):
        # sin solape (t1=t0) para aislar el EMBARGO: test={5}, step=2 → quita 6 y 7
        t0 = np.arange(10.0); t1 = t0.copy()
        train = purged_train_mask(t0, t1, [5], embargo_pct=0.2)   # step=int(10*0.2)=2
        assert np.where(train)[0].tolist() == [0, 1, 2, 3, 4, 8, 9]

    def test_embargo_absoluto_por_lookback(self):
        # embargo en barras ABSOLUTAS (≥ lookback del feature): test={10}, steps=5 →
        # quita 11..15 del train (un rolling de 5 barras no verá el test a través del feature)
        t0 = np.arange(20.0); t1 = t0.copy()
        train = purged_train_mask(t0, t1, [10], embargo_steps=5)
        assert np.where(train)[0].tolist() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 16, 17, 18, 19]

    def test_sin_solape_ni_embargo_no_purga(self):
        t0 = np.arange(10.0); t1 = t0.copy()
        train = purged_train_mask(t0, t1, [5], embargo_pct=0.0)
        assert np.where(train)[0].tolist() == [0, 1, 2, 3, 4, 6, 7, 8, 9]

    def test_bloques_contiguos(self):
        assert _test_blocks(np.array([2, 3, 4, 7, 8])) == [(2, 4), (7, 8)]
        assert _test_blocks(np.array([5])) == [(5, 5)]


class TestPurgedKFold:
    def test_particiona_y_no_se_pisan(self):
        n = 100
        t0 = np.arange(float(n)); t1 = t0.copy()              # sin solape
        folds = list(purged_kfold(t0, t1, n_splits=5, embargo_pct=0.0))
        assert len(folds) == 5
        all_test = []
        for tr, te in folds:
            assert set(tr).isdisjoint(set(te))               # train ∩ test = ∅
            all_test += te.tolist()
        assert sorted(all_test) == list(range(n))            # los test particionan todo

    def test_solape_reduce_el_train(self):
        # con etiquetas que solapan, el train purgado es MENOR que el ingenuo
        n = 100
        t0 = np.arange(float(n)); t1 = t0 + 5                 # etiquetas de 5 barras
        tr_purg, te = next(purged_kfold(t0, t1, n_splits=5, embargo_pct=0.01))
        assert len(tr_purg) < n - len(te)                    # se purgó algo en la frontera


class TestCPCV:
    def test_numero_de_splits_y_caminos(self):
        n = 120
        t0 = np.arange(float(n)); t1 = t0.copy()
        splits = list(cpcv_splits(t0, t1, n_groups=6, k_test=2, embargo_pct=0.0))
        from math import comb
        assert len(splits) == comb(6, 2) == 15               # C(N,k) splits
        assert n_backtest_paths(6, 2) == comb(5, 1) == 5     # C(N-1,k-1) caminos

    def test_cada_grupo_en_C_N1_k1_tests(self):
        # cada grupo participa en exactamente C(N-1,k-1) conjuntos de test (AFML 12.4.2)
        n, N, k = 120, 6, 2
        t0 = np.arange(float(n)); t1 = t0.copy()
        cnt = {g: 0 for g in range(N)}
        for _, _, combo in cpcv_splits(t0, t1, n_groups=N, k_test=k):
            for g in combo:
                cnt[g] += 1
        assert all(c == n_backtest_paths(N, k) for c in cnt.values())   # == 5 cada uno

    def test_train_test_disjuntos_y_purgados(self):
        n = 120
        t0 = np.arange(float(n)); t1 = t0 + 3
        for tr, te, _ in cpcv_splits(t0, t1, n_groups=6, k_test=2, embargo_pct=0.01):
            assert set(tr).isdisjoint(set(te))


class TestGuardas:
    def test_kfold_n_splits_invalido(self):
        t0 = np.arange(10.0)
        with pytest.raises(ValueError):
            list(purged_kfold(t0, t0, n_splits=1))

    def test_cpcv_k_invalido(self):
        t0 = np.arange(10.0)
        with pytest.raises(ValueError):
            list(cpcv_splits(t0, t0, n_groups=4, k_test=4))
