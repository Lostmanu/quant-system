"""Tests de analysis/hl_adapter.py (loader de snapshots de Hyperliquid)."""
import numpy as np
import pytest

pd = pytest.importorskip("pandas")  # dep de infra/vendor, no del core → skip si no está instalada

from analysis.hl_adapter import hl_snapshot_to_book, to_uniform_grid, snapshot_cadence


def _df(rows):
    return pd.DataFrame(rows, columns=["event_time", "side", "price", "quantity"])


def test_agrupa_por_event_time_y_ordena_lados():
    rows = [(1000, "bid", "10.0", "1"), (1000, "bid", "9.0", "2"),
            (1000, "ask", "12.0", "4"), (1000, "ask", "11.0", "3"),
            (2000, "bid", "10.5", "1"), (2000, "ask", "10.6", "2")]
    ts, bpx, bsz, apx, asz = hl_snapshot_to_book(_df(rows), top_l=3)
    assert list(ts) == [1000, 2000]
    assert bpx[0, 0] == 10.0 and bpx[0, 1] == 9.0          # bid DESC
    assert apx[0, 0] == 11.0 and apx[0, 1] == 12.0          # ask ASC (aunque llegaran desordenados)
    assert np.isnan(bpx[0, 2]) and np.isnan(apx[0, 2])      # niveles faltantes = NaN
    assert bpx[1, 0] == 10.5 and apx[1, 0] == 10.6


def test_top_l_recorta_y_asocia_sizes():
    rows = [(1000, "bid", f"{10 - i}", f"{i + 1}") for i in range(5)] + [(1000, "ask", "20", "9")]
    ts, bpx, bsz, apx, asz = hl_snapshot_to_book(_df(rows), top_l=2)
    assert bpx.shape == (1, 2)
    assert bpx[0, 0] == 10.0 and bsz[0, 0] == 1.0           # el mejor bid conserva SU size
    assert bpx[0, 1] == 9.0 and bsz[0, 1] == 2.0


def test_uniform_grid_locf():
    ts = np.array([1000, 2000])
    a = np.array([[1.0], [2.0]])
    grid, (g,) = to_uniform_grid(ts, [a], 500)
    assert list(grid) == [1000, 1500, 2000]
    assert list(g[:, 0]) == [1.0, 1.0, 2.0]                 # LOCF: 1500 usa el snapshot de 1000


def test_snapshot_cadence_basico():
    rows = [(t, "bid", "10", "1") for t in (0, 500, 1040, 1580)]
    rep = snapshot_cadence(_df(rows))
    assert rep["n_snapshots"] == 4
    assert rep["mediana_ms"] == 540.0
