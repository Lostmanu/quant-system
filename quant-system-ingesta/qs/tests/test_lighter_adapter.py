"""Tests de analysis/lighter_adapter.py v2 (diffs SET + anclas como ORÁCULO estructural + unidades)."""
import numpy as np
import pytest

pd = pytest.importorskip("pandas")  # dep de infra/vendor, no del core → skip si no está instalada

from analysis.lighter_adapter import (lighter_to_book, lighter_trades_ms,
                                      LighterUnitsError, LighterSeamError)

NS = 1_000_000
T0 = 1_768_000_000_000 * NS                      # epoch ns plausible (2026)


def _row(t_ms, etype, side, px, q):
    return dict(event_time=T0 + t_ms * NS, event_type=etype, side=side,
                price=str(px), quantity=str(q))


def _df(rows):
    return pd.DataFrame(rows)


def _updates_2niv(t_ms, bid0=100.0):
    return [_row(t_ms, "update", "bid", bid0, 1.0), _row(t_ms, "update", "bid", bid0 - 1, 2.0),
            _row(t_ms, "update", "ask", bid0 + 1, 2.0), _row(t_ms, "update", "ask", bid0 + 2, 3.0)]


def _ancla_2niv(t_ms, bid0=100.0, dq=0.0):
    return [_row(t_ms, "snapshot", "bid", bid0, 1.0 + dq), _row(t_ms, "snapshot", "bid", bid0 - 1, 2.0 + dq),
            _row(t_ms, "snapshot", "ask", bid0 + 1, 2.0 + dq), _row(t_ms, "snapshot", "ask", bid0 + 2, 3.0 + dq)]


def test_diffs_set_y_emision_causal():
    rows = _updates_2niv(0)
    rows += [_row(500, "update", "bid", 100.0, 5.0)]                   # SET: cambia size del mejor bid
    rows += [_row(1500, "update", "ask", 102.0, 9.0)]                  # flush causal
    ts, bpx, bsz, apx, asz, rep = lighter_to_book(_df(rows), top_l=2, sample_ms=100)
    assert rep["n_updates"] == 6 and rep["n_anchors"] == 0
    assert bsz[np.searchsorted(ts, T0 // NS + 600)][0] == 5.0


def test_qty0_borra_nivel():
    rows = _updates_2niv(0)
    rows += [_row(300, "update", "bid", 100.0, 0.0)]                   # borra el mejor bid
    rows += [_row(1500, "update", "ask", 103.0, 1.0)]
    ts, bpx, *_r, rep = lighter_to_book(_df(rows), top_l=2, sample_ms=100)
    after = ts[ts >= T0 // NS + 400]
    if len(after):
        assert bpx[np.searchsorted(ts, after[0])][0] == 99.0


def test_ancla_no_toca_el_libro():
    rows = _updates_2niv(0)                                            # siembra por diffs
    rows += _ancla_2niv(1000, bid0=200.0)                              # ancla DISTINTA: solo oráculo
    rows += [_row(2000, "update", "ask", 102.5, 1.0)]                  # flush
    ts, bpx, *_r, rep = lighter_to_book(_df(rows), top_l=2, sample_ms=100,
                                        max_structural_mismatch=1.0)
    assert rep["n_anchors"] == 1 and rep["oracle_checks"] == 1
    assert bpx[-1][0] == 100.0                                         # el libro sigue siendo el de los diffs


def test_oraculo_estructural_mide_y_pasa_cuando_cuadra():
    rows = _updates_2niv(0)
    rows += _ancla_2niv(1000, bid0=100.0, dq=0.0)                      # ancla IGUAL → estructural 0
    ts, *_r, rep = lighter_to_book(_df(rows), top_l=2, sample_ms=100)
    assert rep["structural_mismatch_mean"] == 0.0
    assert rep["qty_exact_frac_mean"] == 1.0


def test_oraculo_tolera_redondeo_de_feed():
    rows = _updates_2niv(0)
    rows += _ancla_2niv(1000, bid0=100.0, dq=1.0)                      # qty ±1 = redondeo tolerado
    ts, *_r, rep = lighter_to_book(_df(rows), top_l=2, sample_ms=100)
    assert rep["structural_mismatch_mean"] == 0.0 and rep["qty_exact_frac_mean"] == 1.0


def test_oraculo_falla_fuerte_con_hueco_real():
    rows = _updates_2niv(0)
    rows += _ancla_2niv(1000, bid0=250.0)                              # estructura totalmente distinta
    with pytest.raises(LighterSeamError):
        lighter_to_book(_df(rows), top_l=2, sample_ms=100, max_structural_mismatch=0.20)


def test_unidades_gritan():
    df = _df(_updates_2niv(0))
    df["event_time"] = df["event_time"] // 1_000_000                   # ms donde se espera ns
    with pytest.raises(LighterUnitsError):
        lighter_to_book(df, top_l=2)
    tdf = pd.DataFrame([dict(event_time=T0, price="1.0", quantity="2.0", is_buyer_maker=False)])
    with pytest.raises(LighterUnitsError):                             # ns donde se espera ms
        lighter_trades_ms(tdf)


def test_trades_ms_ok():
    tdf = pd.DataFrame([dict(event_time=1_768_000_000_000, price="1.5", quantity="2.0", is_buyer_maker=True)])
    ts, px, q, ibm = lighter_trades_ms(tdf)
    assert ts[0] == 1_768_000_000_000 and px[0] == 1.5 and q[0] == 2.0 and bool(ibm[0]) is True
