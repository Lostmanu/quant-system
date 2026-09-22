"""Tests de analysis/l2_adapter.py — reconstrucción de libro L2 desde diffs."""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.l2_adapter import reconstruct, qs_depth_to_book, update_id_gaps


class TestReconstruccion:
    def test_snapshot_y_diffs(self):
        # snapshot inicial + un borrado (mejor bid) + un nivel nuevo (mejor ask)
        rows = [
            (1, True, "bid", 100.0, 5.0), (1, True, "bid", 99.0, 3.0),
            (1, True, "ask", 101.0, 4.0), (1, True, "ask", 102.0, 2.0),
            (2, False, "bid", 100.0, 0.0),     # borra el mejor bid → pasa a 99
            (3, False, "ask", 100.5, 6.0),     # nuevo mejor ask en 100.5
        ]
        ts, bpx, bsz, apx, asz = reconstruct(rows, top_l=1, sample_every=1)
        assert bpx[-1, 0] == 99.0 and apx[-1, 0] == 100.5   # estado final correcto
        assert bsz[-1, 0] == 3.0 and asz[-1, 0] == 6.0

    def test_orden_de_niveles(self):
        rows = [(1, True, "bid", 100.0, 1.0), (1, True, "bid", 98.0, 1.0),
                (1, True, "bid", 99.0, 1.0), (1, True, "ask", 103.0, 1.0),
                (1, True, "ask", 101.0, 1.0), (1, True, "ask", 102.0, 1.0)]
        ts, bpx, bsz, apx, asz = reconstruct(rows, top_l=3, sample_every=1)
        assert bpx[-1].tolist() == [100.0, 99.0, 98.0]      # bids DESC
        assert apx[-1].tolist() == [101.0, 102.0, 103.0]    # asks ASC
        assert (bpx[-1, 0] < apx[-1, 0])                    # libro no cruzado

    def test_resnapshot_reinicia(self):
        # un is_snapshot nuevo tras diffs debe REINICIAR el libro (no mezclar)
        rows = [(1, True, "bid", 100.0, 5.0), (1, True, "ask", 101.0, 5.0),
                (2, False, "bid", 50.0, 9.0),                # nivel viejo
                (3, True, "bid", 200.0, 1.0), (3, True, "ask", 201.0, 1.0)]  # resnapshot
        ts, bpx, bsz, apx, asz = reconstruct(rows, top_l=1, sample_every=1)
        assert bpx[-1, 0] == 200.0 and apx[-1, 0] == 201.0  # libro nuevo, sin el 50.0/100.0

    def test_solo_emite_libro_maduro(self):
        # con menos de top_l niveles por lado no se emite snapshot
        rows = [(1, True, "bid", 100.0, 1.0), (1, True, "ask", 101.0, 1.0)]
        ts, bpx, bsz, apx, asz = reconstruct(rows, top_l=5, sample_every=1)
        assert len(ts) == 0

    def test_captura_propia_directa(self):
        # nuestra captura ya son snapshots top-L → apilar a [T,L] sin reconstruir
        bp = [[100.0, 99.0], [101.0, 100.0]]; bv = [[5.0, 3.0], [4.0, 2.0]]
        ap = [[101.0, 102.0], [102.0, 103.0]]; av = [[6.0, 1.0], [5.0, 2.0]]
        bpx, bsz, apx, asz = qs_depth_to_book(bp, bv, ap, av)
        assert bpx.shape == (2, 2) and bpx[1, 0] == 101.0 and asz[0, 0] == 6.0

    def test_update_id_gaps(self):
        # cadena continua → 0 gaps; cadena rota → lo detecta
        assert update_id_gaps([0, 10, 20], [10, 20, 30]) == 0
        assert update_id_gaps([0, 10, 99], [10, 20, 30]) == 1     # 99 != 20

    def test_salta_libro_bloqueado(self):
        # nivel stale: bid a 101 con el ask también en 101 → bloqueado → NO se emite,
        # pero el snapshot consistente posterior (tras borrar el stale) SÍ
        rows = [(1, True, "bid", 100.0, 5.0), (1, True, "ask", 101.0, 5.0),
                (2, False, "bid", 101.0, 1.0),     # stale: bid bloqueado con el ask
                (3, False, "bid", 101.0, 0.0)]     # se borra el stale → libro sano (100/101)
        ts, bpx, bsz, apx, asz = reconstruct(rows, top_l=1, sample_every=1)
        assert (bpx[:, 0] < apx[:, 0]).all()        # ningún snapshot emitido está bloqueado
        assert bpx[-1, 0] == 100.0 and apx[-1, 0] == 101.0
