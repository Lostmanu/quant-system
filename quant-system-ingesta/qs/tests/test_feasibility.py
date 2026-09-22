"""Tests de analysis/feasibility.py — viabilidad (§4.1) y latencia ×10 (§5.2)."""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.feasibility import (clears_costs, supports_detection, latency_degradation,
                                  feasibility_gate)


class TestCostesYViabilidad:
    def test_clears_costs(self):
        net, ok = clears_costs(0.0010, 0.0004)             # edge 10 bps vs coste 4 bps
        assert ok and abs(net - 0.0006) < 1e-12
        net, ok = clears_costs(0.0002, 0.0004)             # edge < coste
        assert not ok

    def test_supports_detection(self):
        # SR per-día ~0.06 (≈0.95 anual) → MinTRL ~756; con 2000 obs sí, con 300 no
        sr = 0.95 / np.sqrt(252)
        trl, ok = supports_detection(sr, 2000)
        assert ok and 700 < trl < 820
        _, ok2 = supports_detection(sr, 300)
        assert not ok2


class TestLatencia:
    def test_senal_rapida_se_evapora(self):
        # señal con lookahead de 1 barra: gana a lag 1, pero a lag 10 es ruido → degrada
        rng = np.random.default_rng(0)
        ret = rng.normal(0, 0.01, 2000)
        signal = np.r_[np.sign(ret[1:]), 0.0]              # signal[t] = sign(ret[t+1])
        sr_b, sr_s, deg = latency_degradation(signal, ret, base_lag=1, factor=10)
        assert sr_b > 1.0 and deg > 0.5                    # fuerte a lag1, se evapora a ×10

    def test_drift_persistente_sobrevive(self):
        # drift positivo persistente: capturable igual con o sin latencia → degradación baja
        rng = np.random.default_rng(1)
        ret = 0.002 + rng.normal(0, 0.01, 2000)
        signal = np.ones(2000)
        _, _, deg = latency_degradation(signal, ret, base_lag=1, factor=10)
        assert deg < 0.30                                  # sobrevive el test de latencia

    def test_gate_combinado(self):
        rng = np.random.default_rng(2)
        ret = 0.002 + rng.normal(0, 0.01, 2000)
        signal = np.ones(2000)
        g = feasibility_gate(sharpe=0.95 / np.sqrt(252), n_available=2000,
                             edge_per_trade=0.0010, cost_roundtrip=0.0004,
                             signal=signal, fwd_ret=ret)
        assert g["cubre_costes"] and g["sobrevive_latencia"] and g["soporta_deteccion"]
        assert g["pass"] is True
