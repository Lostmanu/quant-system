"""Tests de analysis/toxicity.py — VPIN (Easley-López de Prado-O'Hara 2012)."""
import os
import sys
import numpy as np
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.toxicity import vpin, bucket_volume_for


def _ser(qtys, sides, price=None):
    n = len(qtys)
    ts = (np.arange(n) * 10).astype("int64")
    p = np.asarray(price if price is not None else [100.0] * n, "float64")
    return ts, p, np.asarray(qtys, "float64"), np.asarray(sides, "float64")


class TestVPINComportamiento:
    def test_todo_compras_vpin_1(self):
        # flujo 100% comprador → cada bucket V^B=V, V^S=0 → |V^B−V^S|/V = 1 → VPIN=1
        ts, p, q, s = _ser([1.0] * 20, [1] * 20)
        _, _, vp, oi = vpin(ts, p, q, s, bucket_volume=2.0, n=1)
        assert np.allclose(oi, 1.0)
        assert np.allclose(vp[np.isfinite(vp)], 1.0)

    def test_balanceado_vpin_0(self):
        # alternancia compra/venta de igual qty → cada bucket de V=2 lleva 1 compra +
        # 1 venta → V^B=V^S → imbalance 0 → VPIN=0
        ts, p, q, s = _ser([1.0] * 20, [1, -1] * 10)
        _, _, vp, oi = vpin(ts, p, q, s, bucket_volume=2.0, n=1)
        assert np.allclose(oi, 0.0, atol=1e-12)
        assert np.allclose(vp[np.isfinite(vp)], 0.0, atol=1e-12)

    def test_division_de_trade_entre_buckets(self):
        # un trade gigante (venta de 30) se DIVIDE entre buckets conservando su lado.
        # compra5 / venta30 / compra5, V=10 → buckets: [b5+s5], [s10], [s10], [s5+b5]
        # → imbalance normalizado [0, 1, 1, 0]
        ts, p, q, s = _ser([5.0, 30.0, 5.0], [1, -1, 1])
        _, _, vp, oi = vpin(ts, p, q, s, bucket_volume=10.0, n=1)
        assert oi.tolist() == [0.0, 1.0, 1.0, 0.0]

    def test_vpin_en_rango_0_1(self):
        rng = np.random.default_rng(0)
        q = rng.uniform(0.5, 5.0, 5000)
        s = rng.choice([1.0, -1.0], 5000, p=[0.55, 0.45])
        ts, p, q, s = _ser(q, s)
        _, _, vp, oi = vpin(ts, p, q, s, bucket_volume=float(q.sum()) / 100, n=50)
        f = vp[np.isfinite(vp)]
        assert (f >= 0).all() and (f <= 1).all()
        assert (oi >= 0).all() and (oi <= 1 + 1e-12).all()

    def test_desbalance_persistente_sube_vpin(self):
        # flujo muy comprador (90%) → VPIN alto; flujo balanceado → VPIN bajo
        rng = np.random.default_rng(1)
        s_hi = rng.choice([1.0, -1.0], 4000, p=[0.9, 0.1])
        s_lo = rng.choice([1.0, -1.0], 4000, p=[0.5, 0.5])
        ts, p, q, s = _ser([1.0] * 4000, s_hi)
        _, _, vp_hi, _ = vpin(ts, p, q, s, bucket_volume=20.0, n=50)
        ts, p, q, s = _ser([1.0] * 4000, s_lo)
        _, _, vp_lo, _ = vpin(ts, p, q, s, bucket_volume=20.0, n=50)
        assert np.nanmean(vp_hi) > np.nanmean(vp_lo) + 0.3

    def test_causal_primeros_n_menos_1_nan(self):
        ts, p, q, s = _ser([1.0] * 100, [1, -1] * 50)
        _, _, vp, _ = vpin(ts, p, q, s, bucket_volume=2.0, n=10)
        assert np.isnan(vp[:9]).all() and np.isfinite(vp[9:]).all()


class TestVPINBordes:
    def test_bucket_volume_no_positivo_lanza(self):
        ts, p, q, s = _ser([1.0] * 5, [1] * 5)
        with pytest.raises(ValueError):
            vpin(ts, p, q, s, bucket_volume=0.0, n=1)

    def test_side_no_unitario_lanza(self):
        ts, p, q, s = _ser([1.0, 1.0, 1.0], [1, 0, 1])
        with pytest.raises(ValueError):
            vpin(ts, p, q, s, bucket_volume=1.0, n=1)

    def test_n_invalido_lanza(self):
        ts, p, q, s = _ser([1.0] * 5, [1] * 5)
        with pytest.raises(ValueError):
            vpin(ts, p, q, s, bucket_volume=1.0, n=0)

    def test_volumen_insuficiente_devuelve_vacio(self):
        ts, p, q, s = _ser([1.0, 1.0], [1, -1])
        out = vpin(ts, p, q, s, bucket_volume=1000.0, n=1)
        assert all(len(x) == 0 for x in out)

    def test_bucket_volume_for_escala(self):
        # 2 días, volumen total 200 → 100/día; 50 buckets/día → V=2
        ts = np.array([0, 2 * 86_400_000], "int64")
        q = np.array([100.0, 100.0])
        assert abs(bucket_volume_for(q, ts, buckets_per_day=50) - 2.0) < 1e-9
