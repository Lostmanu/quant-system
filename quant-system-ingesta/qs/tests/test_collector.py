"""Tests del colector de tick de Lighter (infra/lighter_collector/collector.py) — ruta CRÍTICA desde que
el eco necesita su 2º símbolo no-token a 50 ms. Cubre los bordes que la revisión externa marcó sin cubrir:
zstd concatenado decodificable, flush por umbral, y — el bug cazado — que el watchdog NO mate con el
buffer sin flushear. Se salta si falta zstandard (dep de infra, no del core)."""
import importlib.util
import os
import sys

import pytest

zstd = pytest.importorskip("zstandard")

# collector.py vive en infra/lighter_collector (fuera de qs/); se carga por ruta.
_COLLECTOR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "infra", "lighter_collector", "collector.py"))


def _load_collector(tmp_path):
    spec = importlib.util.spec_from_file_location("qs_collector_under_test", _COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                    # importa sin websockets (movido dentro de run())
    mod.DATA = str(tmp_path)                        # redirige la salida al tmp del test
    return mod


def test_zstd_concatenado_decodable(tmp_path):
    """Varios flush → frames concatenados → todas las líneas se recuperan íntegras y en orden."""
    m = _load_collector(tmp_path)
    w = m.HourlyZstWriter()
    lines = [f'{{"recv_ns":{i},"frame":"m{i}"}}\n'.encode() for i in range(7)]
    w.add(lines[0]); w.add(lines[1]); w.flush()      # frame 1
    w.add(lines[2]); w.add(lines[3]); w.flush()      # frame 2
    w.add(lines[4]); w.flush()                       # frame 3
    files = [f for f in os.listdir(tmp_path) if f.endswith(".zst")]
    assert len(files) == 1                            # todo a la MISMA hora → un fichero
    with open(os.path.join(tmp_path, files[0]), "rb") as fh:
        recovered = zstd.ZstdDecompressor().stream_reader(fh).read()
    assert recovered == b"".join(lines[:5])           # 5 líneas, orden preservado, sin corrupción


def test_flush_por_umbral_de_5000(tmp_path):
    """add() dispara flush solo, sin perder líneas, al llegar a 5000 en el buffer."""
    m = _load_collector(tmp_path)
    w = m.HourlyZstWriter()
    for i in range(5000):
        w.add(f'{{"i":{i}}}\n'.encode())
    assert w.buf == []                                # se vació al cruzar el umbral
    assert w.n_lines == 5000
    files = [f for f in os.listdir(tmp_path) if f.endswith(".zst")]
    recovered = zstd.ZstdDecompressor().stream_reader(
        open(os.path.join(tmp_path, files[0]), "rb")).read()
    assert recovered.count(b"\n") == 5000


def test_watchdog_no_mata_con_buffer_sin_flushear(tmp_path, monkeypatch):
    """EL BUG CAZADO: con el disco crítico, el buffer se escribe ANTES de que el watchdog salga.
    Antes del fix, sys.exit() ocurría antes de escribir → pérdida silenciosa del buffer."""
    m = _load_collector(tmp_path)
    w = m.HourlyZstWriter()
    for i in range(10):
        w.buf.append(f'{{"i":{i}}}\n'.encode())       # 10 líneas en buffer, sin flushear

    class _FullDisk:
        total, free = 100, 1                          # 99 % usado > DISK_CRIT (0.85)
    monkeypatch.setattr(m.shutil, "disk_usage", lambda _p: _FullDisk())

    with pytest.raises(SystemExit) as exc:            # el watchdog SÍ sale (protege el disco)...
        w.flush()
    assert exc.value.code == 3
    files = [f for f in os.listdir(tmp_path) if f.endswith(".zst")]
    assert len(files) == 1                            # ...PERO el buffer se escribió primero
    recovered = zstd.ZstdDecompressor().stream_reader(
        open(os.path.join(tmp_path, files[0]), "rb")).read()
    assert recovered.count(b"\n") == 10               # las 10 líneas a salvo, cero pérdida


def test_flush_vacio_es_noop(tmp_path):
    m = _load_collector(tmp_path)
    w = m.HourlyZstWriter()
    w.flush()                                         # sin buffer → no crea fichero
    assert [f for f in os.listdir(tmp_path) if f.endswith(".zst")] == []
