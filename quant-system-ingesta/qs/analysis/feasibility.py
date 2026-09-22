"""analysis/feasibility.py — filtro de viabilidad (Plan §4.1) y test de latencia ×10 (§5.2).

Quinta y última parte del MOTOR. Antes (y después) de buscar un edge, comprobaciones que
matan candidatos barato:

  • VIABILIDAD PREVIA (§4.1): ¿nuestra longitud de datos SOPORTA detectar el Sharpe objetivo?
    (MinTRL, en `overfit.py`). ¿El edge por trade SUPERA el coste round-trip real? (a VIP 0-2
    pagamos ~1.4-2 bps maker; ~3-4 bps round-trip — research del propietario). Si el bruto no
    cubre el coste, no hay nada que validar.

  • TEST DE LATENCIA ×10 (§5.2): ¿sobrevive el edge si la ejecución se retrasa ×10? Un edge
    que se evapora al añadir latencia era una CARRERA DE VELOCIDAD disfrazada — que un
    escritorio pierde por diseño. Umbral del Plan: degradación > 30 % → archivar.

Reutiliza `min_track_record_length` de `overfit.py` (no se duplica).
"""
from __future__ import annotations
import numpy as np
from analysis.overfit import min_track_record_length

LATENCY_FAIL = 0.30          # degradación máxima tolerada a ×10 latencia (Plan §5.2)


def clears_costs(edge_per_trade: float, cost_roundtrip: float):
    """¿El edge BRUTO por trade supera el coste round-trip? (§4.1). Devuelve (neto, pasa)."""
    net = edge_per_trade - cost_roundtrip
    return net, net > 0


def supports_detection(sharpe: float, n_available: int, target_prob: float = 0.95,
                       skew: float = 0.0, kurt: float = 3.0):
    """¿La longitud de datos disponible SOPORTA detectar este Sharpe con significancia? (§4.1).
    Compara MinTRL con n_available. Devuelve (min_trl, pasa)."""
    trl = min_track_record_length(sharpe, target_prob, skew, kurt)
    return trl, n_available >= trl


def _sharpe(pnl: np.ndarray) -> float:
    sd = pnl.std()
    return float(pnl.mean() / sd) if sd > 0 else 0.0


def latency_degradation(signal: np.ndarray, fwd_ret: np.ndarray, base_lag: int = 1,
                        factor: int = 10):
    """Test de latencia ×`factor` (Plan §5.2). pnl(lag)[t] = signal[t]·fwd_ret[t+lag]: actúas
    sobre la señal en t pero la ejecución/captura ocurre `lag` barras después. Devuelve
    (sr_base, sr_slow, degradación) con degradación = 1 − SR(×factor)/SR(base). >0.30 ⇒ era
    velocidad disfrazada → archivar."""
    s = np.asarray(signal, dtype="float64")
    r = np.asarray(fwd_ret, dtype="float64")

    def sr_at(lag: int) -> float:
        m = len(s) - lag
        if m <= 1:
            return 0.0
        return _sharpe(s[:m] * r[lag:lag + m])

    sr_base = sr_at(base_lag)
    sr_slow = sr_at(base_lag * factor)
    deg = 1.0 - sr_slow / sr_base if sr_base > 0 else 1.0
    return sr_base, sr_slow, deg


def feasibility_gate(sharpe: float, n_available: int, edge_per_trade: float,
                     cost_roundtrip: float, signal: np.ndarray, fwd_ret: np.ndarray,
                     target_prob: float = 0.95):
    """Compuerta de viabilidad combinada (§4.1 + §5.2): MinTRL soportado, edge cubre costes, y
    el edge sobrevive a ×10 latencia. Devuelve un dict con cada chequeo y `pass` global."""
    trl, ok_trl = supports_detection(sharpe, n_available, target_prob)
    net, ok_cost = clears_costs(edge_per_trade, cost_roundtrip)
    sr_b, sr_s, deg = latency_degradation(signal, fwd_ret)
    ok_lat = deg <= LATENCY_FAIL
    return {
        "min_trl": trl, "n_available": n_available, "soporta_deteccion": ok_trl,
        "neto_tras_costes": net, "cubre_costes": ok_cost,
        "sr_base": sr_b, "sr_x10": sr_s, "degradacion_latencia": deg,
        "sobrevive_latencia": ok_lat,
        "pass": bool(ok_trl and ok_cost and ok_lat),
    }
