"""Tests de analysis/cryptohft_adapter.py — reconstrucción de diffs CHD a libro @grid + guardia de día-corrupto."""
import os
import sys
import numpy as np
import pyarrow as pa
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analysis.cryptohft_adapter import (reconstruct_timegrid, cryptohft_to_book,
                                        is_corrupt_day, cryptohft_to_book_guarded, CorruptDayError)


class TestReconstruccion:
    def test_topL_ordenado_en_rejilla(self):
        # construye libro en t=0, dispara emisión en t=150 (rejilla 100). top-2 ordenado.
        ev = [0, 0, 0, 0, 0, 0, 150]
        sd = ["bid", "bid", "bid", "ask", "ask", "ask", "bid"]
        px = ["100", "99", "98", "101", "102", "103", "100"]
        qt = ["5", "4", "3", "5", "4", "3", "5"]
        ts, bpx, bsz, apx, asz = reconstruct_timegrid(ev, sd, px, qt, top_l=2, sample_ms=100)
        assert len(ts) == 1 and ts[0] == 100
        assert list(bpx[0]) == [100.0, 99.0] and list(apx[0]) == [101.0, 102.0]   # bid desc, ask asc
        assert list(bsz[0]) == [5.0, 4.0]

    def test_cantidad_cero_borra_nivel(self):
        # mejor ask 101 se borra (qty 0) antes de la rejilla → top ask pasa a 102.
        ev = [0, 0, 0, 0, 0, 50, 150]
        sd = ["bid", "bid", "ask", "ask", "ask", "ask", "bid"]
        px = ["100", "99", "101", "102", "103", "101", "100"]
        qt = ["5", "4", "5", "4", "3", "0", "5"]               # qty 0 en 101 = borrar
        ts, bpx, bsz, apx, asz = reconstruct_timegrid(ev, sd, px, qt, top_l=2, sample_ms=100)
        assert list(apx[0]) == [102.0, 103.0]                  # 101 desapareció

    def test_libro_cruzado_se_salta(self):
        # best bid 102 >= best ask 101 → snapshot cruzado, NO se emite.
        ev = [0, 0, 0, 0, 150]
        sd = ["bid", "bid", "ask", "ask", "bid"]
        px = ["102", "101", "101", "100", "102"]               # asks por debajo de bids = cruzado
        qt = ["5", "4", "5", "4", "5"]
        ts, *_ = reconstruct_timegrid(ev, sd, px, qt, top_l=2, sample_ms=100)
        assert len(ts) == 0

    def test_loader_tabla(self):
        ev = [0, 0, 0, 0, 0, 0, 150]
        t = pa.table({"event_time": ev,
                      "side": ["bid", "bid", "bid", "ask", "ask", "ask", "bid"],
                      "price": ["100", "99", "98", "101", "102", "103", "100"],
                      "quantity": ["5", "4", "3", "5", "4", "3", "5"]})
        ts, bpx, bsz, apx, asz = cryptohft_to_book(t, top_l=2, sample_ms=100)
        assert len(ts) == 1 and list(bpx[0]) == [100.0, 99.0]


# --------- helpers para construir libros sintéticos [T, L] ----------
def _frozen_book(T=200, L=5):
    """Libro totalmente CONGELADO: precios y tamaños constantes → ofi==0 siempre, best-bid-size sin cambio."""
    bpx = np.tile(np.array([100, 99, 98, 97, 96], "float64")[:L], (T, 1))
    apx = np.tile(np.array([101, 102, 103, 104, 105], "float64")[:L], (T, 1))
    bsz = np.tile(np.array([5, 4, 3, 2, 1], "float64")[:L], (T, 1))
    asz = np.tile(np.array([5, 4, 3, 2, 1], "float64")[:L], (T, 1))
    return bpx, bsz, apx, asz


def _active_book(T=200, L=5):
    """Libro VIVO: precio y tamaño del top varían cada paso → ofi!=0 frecuente y best-bid-size cambia."""
    bpx, bsz, apx, asz = _frozen_book(T, L)
    t = np.arange(T)
    bpx[:, 0] = 100.0 + (t % 5) * 0.1          # el mejor bid se mueve → ofi vivo
    bsz[:, 0] = 5.0 + (t % 4)                   # el tamaño del mejor bid cambia
    return bpx, bsz, apx, asz


class TestGuardiaDiaCorrupto:
    def test_libro_congelado_es_corrupto(self):
        # ambas condiciones disparan: best-bid-size sin cambio Y ofi==0 siempre.
        rep = is_corrupt_day(*_frozen_book())
        assert rep["corrupt"] is True
        assert rep["frozen_book"] is True and rep["dead_ofi"] is True
        assert rep["bsz_change_frac"] == 0.0 and rep["ofi_zero_frac"] == 1.0

    def test_libro_activo_no_es_corrupto(self):
        # ninguna condición dispara: size cambia y ofi vive.
        rep = is_corrupt_day(*_active_book())
        assert rep["corrupt"] is False
        assert rep["frozen_book"] is False and rep["dead_ofi"] is False

    def test_AND_no_OR_dia_quieto_pero_vivo_no_es_corrupto(self):
        # EL test clave de la precisión del usuario: best-bid-size CONGELADO (frozen_book True) pero el
        # OFI sigue VIVO (precios se mueven) → dead_ofi False → con AND NO es corrupto. Con OR (el diseño
        # rechazado) este día válido se marcaría corrupto por error.
        bpx, bsz, apx, asz = _frozen_book()
        t = np.arange(len(bpx))
        apx[:, 0] = 101.0 + (t % 2) * 0.5         # el mejor ask oscila → ofi!=0 casi siempre
        # bsz[:,0] queda constante (congelado) a propósito
        rep = is_corrupt_day(bpx, bsz, apx, asz)
        assert rep["frozen_book"] is True          # (1) size congelado, dispara
        assert rep["dead_ofi"] is False            # (2) ofi vivo, NO dispara
        assert rep["corrupt"] is False             # AND → no corrupto (OR lo habría marcado mal)

    def test_libro_degenerado_pocos_snapshots_es_corrupto(self):
        rep = is_corrupt_day(*_frozen_book(T=50))   # T<min_snapshots
        assert rep["corrupt"] is True and "degenerado" in rep["nota"]

    def test_loader_guardado_falla_fuerte_en_corrupto(self):
        # construye una tabla CHD cuyo libro reconstruido queda congelado → cryptohft_to_book_guarded lanza.
        # nivel top siempre el mismo precio/tamaño en cada snapshot → ofi==0 y size sin cambio.
        n_grid = 150
        ev, sd, px, qt = [], [], [], []
        for g in range(n_grid + 2):
            tt = g * 100
            for p, q in [("100", "5"), ("99", "4"), ("98", "3"), ("97", "2"), ("96", "1")]:
                ev.append(tt); sd.append("bid"); px.append(p); qt.append(q)
            for p, q in [("101", "5"), ("102", "4"), ("103", "3"), ("104", "2"), ("105", "1")]:
                ev.append(tt); sd.append("ask"); px.append(p); qt.append(q)
        t = pa.table({"event_time": ev, "side": sd, "price": px, "quantity": qt})
        with pytest.raises(CorruptDayError) as ei:
            cryptohft_to_book_guarded(t, top_l=5, sample_ms=100)
        assert ei.value.report["corrupt"] is True

    def test_loader_guardado_pasa_libro_limpio(self):
        # libro VIVO → no corrupto → devuelve el libro normalizado. Precios FIJOS (la reconstrucción
        # acumula niveles, así no se congela en un máximo histórico) y el tamaño del mejor bid cambia
        # cada grid → best-bid-size se mueve Y ofi!=0 por la rama "mismo precio" (Qb[t]−Qb[t-1]).
        n_grid = 150
        ev, sd, px, qt = [], [], [], []
        for g in range(n_grid + 2):
            tt = g * 100
            for lvl, q in zip([100, 99, 98, 97, 96], [5 + (g % 4), 4, 3, 2, 1]):
                ev.append(tt); sd.append("bid"); px.append(str(lvl)); qt.append(str(q))
            for lvl, q in zip([101, 102, 103, 104, 105], [5, 4, 3, 2, 1]):
                ev.append(tt); sd.append("ask"); px.append(str(lvl)); qt.append(str(q))
        t = pa.table({"event_time": ev, "side": sd, "price": px, "quantity": qt})
        ts, bpx, bsz, apx, asz = cryptohft_to_book_guarded(t, top_l=5, sample_ms=100)
        assert len(ts) > 0
