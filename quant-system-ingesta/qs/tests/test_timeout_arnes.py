# -*- coding: utf-8 -*-
"""EL LÍMITE DE TIEMPO SE TRATA, NO SE PROPAGA (M-15).

Medido el 2026-09-05: `subprocess.TimeoutExpired` subía sin capturar desde `_correr` y mataba la
corrida ENTERA del arnés. La de referencia murió en la fila 152 de 199 tras 6 h 30 de reloj; el test
que agotó el límite tarda **1,86 s** aislado. Por qué se agotó no está demostrado y no se
afirma aquí. Los veredictos ya emitidos quedaron en el log —no se perdió evidencia—, pero la ejecución no se pudo
completar y hubo que repetir el trabajo: dos horas.

El contrato que se prueba aquí, y es el que fijó Manuel:

  · límite en la LÍNEA BASE  → abortar, sin ejecutar ni una mutación;
  · límite en una MUTACIÓN   → registrar «TIMEOUT — NO ACREDITA»; continuar sólo tras limpieza
    local comprobada y sin deriva observada. Conservar temporales o fallar la limpieza detiene;
  · resultado GLOBAL         → rc distinto de cero. Nunca mordida, éxito ni salto de plataforma;
  · se conservan la salida parcial, la identidad de la fila y el límite aplicado;
  · se captura SOLO `TimeoutExpired`: una cancelación o un fallo del arnés siguen subiendo.

Los focales **simulan** el agotamiento en vez de esperar quince minutos: `_correr_o_timeout` está
separada justo para eso.
"""
import os
from pathlib import Path
import subprocess
import sys

import pytest

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(QS, "tools"))
import arnes_comun as G                                             # noqa: E402
import mutacion_ref_valida as R                                         # noqa: E402

ARNESES = pytest.mark.parametrize("arnes", [R], ids=["referencia"])


@pytest.fixture(autouse=True)
def _copia_minima_del_ejecutor(tmp_path, monkeypatch):
    """Focal del ORQUESTADOR, no una ejecución semántica de los mutantes.

    Se mantienen las anclas de las primeras filas reales, la validación real de baseline y el
    clasificador real. La colección auxiliar ve tests mínimos con los nombres declarados. No se
    copian 175 ficheros ni se ejecutan tests de mercado para probar un timeout simulado.
    """
    fuente = tmp_path / "fuente"
    for rel in (R.REL_PROD,):
        destino = fuente / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes((Path(G.QS_REAL) / rel).read_bytes())
    tests = fuente / "tests"
    tests.mkdir()
    nombres = sorted(set(R.MUTACIONES[0][2]))
    (tests / "test_minimo.py").write_text(
        "\n".join(f"def {nombre}():\n    pass\n" for nombre in nombres), encoding="utf-8")
    (tests / "test_vacio.py").write_text("# colección vacía deliberada\n", encoding="utf-8")
    monkeypatch.setattr(G, "QS_REAL", str(fuente))
    monkeypatch.setattr(G, "COPIABLES", ("analysis", "tests"))
    monkeypatch.setattr(R, "FICHEROS_TEST", ("tests/test_minimo.py",))
    monkeypatch.setattr(G.tempfile, "tempdir", str(tmp_path))


def _expira(limite):
    def _falso(*a, **kw):
        raise subprocess.TimeoutExpired(cmd=["pytest"], timeout=limite,
                                        output="PARCIAL-ANTES-DE-EXPIRAR", stderr="")
    return _falso


# ═══════════════════ la primitiva compartida: los DOS arneses la usan
def test_el_limite_agotado_NO_sube_como_excepcion_y_devuelve_su_identidad(monkeypatch):
    """Antes esto tiraba la corrida entera. Ahora vuelve con el límite y la salida parcial."""
    monkeypatch.setattr(G, "_correr_o_timeout", _expira(900))
    razones, recuento, invalida, rc, n_passed, timeout = G._correr("x", ["t"], "bt")
    assert timeout["limite"] == 900
    assert timeout["parcial"] == {"stdout": "PARCIAL-ANTES-DE-EXPIRAR", "stderr": ""}
    assert razones == {} and n_passed == 0 and rc is None
    assert "TIMEOUT" in recuento and "900" in recuento
    assert invalida is False, "un límite agotado NO es «módulo roto»: son cosas distintas"


def test_una_corrida_normal_NO_declara_timeout(monkeypatch):
    """CONTROL POSITIVO de la primitiva: sin agotar el límite, `timeout` es None y todo lo demás
    llega intacto. Sin esto, «devolver siempre timeout» pasaría los otros focales."""
    esperado = ({"test_x": "assert"}, "1 failed", False, 1, 0, None)
    monkeypatch.setattr(G, "_correr_o_timeout", lambda *a, **kw: esperado)
    assert G._correr("x", ["t"], "bt") == esperado


def test_SOLO_se_captura_TimeoutExpired_y_no_una_cancelacion(monkeypatch):
    """Tragarse un `KeyboardInterrupt` sería peor que el defecto que esto arregla: el operador pulsa
    Ctrl-C y el arnés seguiría como si nada."""
    def _cancelado(*a, **kw):
        raise KeyboardInterrupt()
    monkeypatch.setattr(G, "_correr_o_timeout", _cancelado)
    with pytest.raises(KeyboardInterrupt):
        G._correr("x", ["t"], "bt")


def test_una_excepcion_AJENA_tampoco_se_convierte_en_timeout(monkeypatch):
    def _roto(*a, **kw):
        raise OSError("el disco dice que no")
    monkeypatch.setattr(G, "_correr_o_timeout", _roto)
    with pytest.raises(OSError, match="el disco dice que no"):
        G._correr("x", ["t"], "bt")


def test_el_limite_por_defecto_sigue_siendo_900_y_se_pasa_al_subproceso(monkeypatch):
    """No se sube en esta tanda, y se comprueba que el valor llega de verdad a `subprocess.run`:
    un límite que el lanzamiento ignorase dejaría el contrato sin efecto."""
    assert G.TIMEOUT_S == 900
    visto = {}

    class _R:
        stdout, stderr, returncode = "1 passed", "", 0

    def _espia(*a, **kw):
        visto["timeout"] = kw.get("timeout")
        return _R()
    monkeypatch.setattr(subprocess, "run", _espia)
    G._correr_o_timeout("x", ["t"], "bt", ("tests/test_x.py",), G.TIMEOUT_S)
    assert visto["timeout"] == 900


# ═══════════════════ los DOS consumidores reales (el libro tiene ejecutor propio y no entra)
@ARNESES
def test_la_LINEA_BASE_que_agota_el_limite_ABORTA_sin_ejecutar_mutaciones(arnes, monkeypatch, capsys):
    """Sin base limpia, un rojo tras mutar no sería atribuible a la mutación. Se exige además que no
    se haya copiado ni ejecutado NADA después."""
    corridas = {"n": 0}

    def _base_expira(*a, **kw):
        corridas["n"] += 1
        return ({}, "TIMEOUT tras 900s", False, None, 0,
                {"limite": 900, "parcial": {"stdout": "PARC", "stderr": ""},
                 "muestra": "PARC"})
    monkeypatch.setattr(G, "_correr", _base_expira)
    monkeypatch.setattr(arnes, "_correr", _base_expira, raising=False)
    monkeypatch.setattr(sys, "argv", [arnes.__name__])
    rc = arnes.main()
    assert rc == 6, "la base agotada tiene que abortar con su propio código"
    assert corridas["n"] == 1, "se ejecutó algo MÁS que la línea base"
    salida = capsys.readouterr().out
    assert "LINEA BASE AGOTO" in salida or "LÍNEA BASE AGOTÓ" in salida
    assert "900" in salida and "PARC" in salida, "no conserva el límite ni la salida parcial"


# ═══════════════════ TABLA MÍNIMA: base válida + una fila que agota + otra que muerde
#
# La primera versión de estos dos focales no aislaba nada, y los defectos eran los que esta casa
# persigue en el código ajeno:
#   · desactivaba `_problemas_baseline` y dejaba que NINGUNA fila acreditara, así que su `rc != 0`
#     no demostraba que lo impusiera el timeout: lo imponía el resto;
#   · el segundo comparaba dos cadenas CONSTANTES y pasaba con cualquier objeto, incluso sin arnés.
#
# Con dos copias de una fila real —una con timeout simulado y otra con fallo esperado simulado—
# el clasificador real distingue continuación, recuento y retorno. No acredita mutantes reales.
# Base simulada VÁLIDA: sin razones, rc=0 y exactamente los tests declarados pasando. La primera versión
# constante traía razones y rc=1 —o sea, una base ROTA— y por eso `_problemas_baseline` abortaba
# con 3 antes de llegar a ninguna fila. El focal no medía lo que decía.
_AGOTA = ({}, "TIMEOUT tras 900s", False, None, 0,
          {"limite": 900, "parcial": {"stdout": "PARC-OUT", "stderr": ""}, "muestra": "PARC-OUT"})


def _tabla_de_dos(arnes, monkeypatch, con_timeout):
    """Duplica la primera fila real y simula los resultados del ejecutor.

    Las filas se toman de su propia tabla —misma ancla, mismo test declarado— para que todas sus
    defensas sigan vivas: el pre-vuelo interno, la comprobación de ancla única y la de tests
    huérfanos. Una tabla inventada las hacía saltar, y desactivarlas para que el focal pasara sería
    exactamente lo que esta casa no admite. Se simulan base, timeout y fallo esperado; la fixture
    reduce la copia y la colección, sin desactivar el validador de base ni el clasificador.
    """
    real = arnes.MUTACIONES[0]
    filas = [("fila-que-agota",) + tuple(real[1:]), ("fila-que-muerde",) + tuple(real[1:])]
    monkeypatch.setattr(arnes, "MUTACIONES", filas)
    declarados = len(set(real[2]))
    base_ok = ({}, f"{declarados} passed", False, 0, declarados, None)
    muerde = (dict(real[2]), "1 failed", False, 1, 0, None)
    llamadas = {"n": 0}

    def _ejecutor(*a, **kw):
        llamadas["n"] += 1
        Path(a[2]).mkdir(parents=True, exist_ok=True)
        residuo = Path(a[2]) / "residuo-de-pytest"
        residuo.write_text("sintético", encoding="utf-8")
        residuo.chmod(0o444)  # propiedad de los objetos git que bloqueaba Windows
        if llamadas["n"] == 1:
            return base_ok                                   # línea base LIMPIA
        if llamadas["n"] == 2 and con_timeout:
            return _AGOTA
        return muerde
    for mod in {G, arnes}:
        monkeypatch.setattr(mod, "_correr", _ejecutor, raising=False)
    monkeypatch.setattr(sys, "argv", [arnes.__name__])
    return llamadas


@ARNESES
def test_una_FILA_que_agota_el_limite_se_registra_y_la_corrida_CONTINUA(arnes, monkeypatch, capsys):
    """El caso que costó dos horas: la corrida tiene que llegar a la SEGUNDA fila."""
    llamadas = _tabla_de_dos(arnes, monkeypatch, con_timeout=True)
    try:
        rc = arnes.main()
    except SystemExit as e:                                            # algunos `main` salen así
        rc = e.code
    salida = capsys.readouterr().out
    assert llamadas["n"] == 3, "se debe ejecutar base y exactamente dos filas"
    assert "TIMEOUT" in salida and "NO ACREDITA" in salida
    assert "SIN MEDIR" in salida, "el recuento no separa lo no medido de lo que no muerde"
    assert "900" in salida and "PARC-OUT" in salida, "no conserva el límite ni la muestra"
    assert rc == 1, "el único fallo de este escenario debe ser el timeout de una fila"
    assert "1/2" in salida and "1 fila(s) SIN MEDIR" in salida


@ARNESES
def test_CONTROL_la_misma_tabla_SIN_timeout_acredita_y_devuelve_cero(arnes, monkeypatch, capsys):
    """El control que faltaba. Sin él, un arnés que devolviera siempre distinto de cero pasaría el
    focal de arriba, y la prueba no distinguiría el timeout de un fallo cualquiera."""
    _tabla_de_dos(arnes, monkeypatch, con_timeout=False)
    try:
        rc = arnes.main()
    except SystemExit as e:
        rc = e.code
    salida = capsys.readouterr().out
    assert "TIMEOUT" not in salida and "SIN MEDIR" not in salida
    assert rc == 0, "sin timeout y con las dos filas mordiendo, el resultado tiene que ser cero"
    assert "2/2" in salida


@pytest.mark.parametrize("stdout,stderr,esperado", [
    (b"OUT", b"ERR", {"stdout": "OUT", "stderr": "ERR"}),
    (None, b"ERR", {"stdout": "", "stderr": "ERR"}),
    (None, "ERR", {"stdout": "", "stderr": "ERR"}),
    ("OUT", b"ERR", {"stdout": "OUT", "stderr": "ERR"}),
    (b"\xff", None, {"stdout": "\ufffd", "stderr": ""}),
])
def test_cada_canal_del_timeout_se_normaliza_independientemente(monkeypatch, stdout, stderr, esperado):
    def expira(*a, **kw):
        raise subprocess.TimeoutExpired("pytest", 900, output=stdout, stderr=stderr)
    monkeypatch.setattr(G, "_correr_o_timeout", expira)
    timeout = G._correr("x", ["t"], "bt")[-1]
    assert timeout["parcial"] == esperado, "[M15-CANALES] se perdió un canal capturado"


@ARNESES
@pytest.mark.parametrize("en_base", [True, False], ids=["base", "fila"])
def test_los_canales_completos_llegan_al_LOG_no_solo_la_muestra(arnes, en_base, monkeypatch, capsys):
    original = "INICIO-OUT-" + "x" * 600 + "-FIN-OUT"
    parcial = {"stdout": original, "stderr": "INICIO-ERR-" + "y" * 600 + "-FIN-ERR"}
    _tabla_de_dos(arnes, monkeypatch, con_timeout=True)
    ejecutar = G._correr
    def salida_completa(*a, **kw):
        resultado = ejecutar(*a, **kw)
        if en_base or resultado[-1] is not None:
            return ({}, "TIMEOUT", False, None, 0,
                    {"limite": 900, "parcial": parcial, "muestra": "RESUMEN"})
        return resultado
    monkeypatch.setattr(G, "_correr", salida_completa)
    monkeypatch.setattr(sys, "argv", [arnes.__name__])
    assert arnes.main() == (6 if en_base else 1)
    log = capsys.readouterr().out
    assert original in log and parcial["stderr"] in log, "[M15-LOG] sólo se imprimió un recorte"


@ARNESES
@pytest.mark.parametrize("base", ["timeout", "roja"])
def test_la_deriva_tiene_prioridad_sobre_TODAS_las_salidas_de_base(arnes, base, monkeypatch, capsys):
    respuesta = _AGOTA if base == "timeout" else ({"t": "assert"}, "1 failed", False, 1, 0, None)
    monkeypatch.setattr(G, "_correr", lambda *a, **kw: respuesta)
    monkeypatch.setattr(G, "_huella", iter([{"control": "antes"}, {"control": "despues"}]).__next__)
    monkeypatch.setattr(sys, "argv", [arnes.__name__])
    assert arnes.main() == 4, "[M15-HUELLA] el aborto ocultó la deriva"
    assert "CAMBI" in capsys.readouterr().out


def test_los_huerfanos_NO_ocultan_un_fallo_de_limpieza(monkeypatch, capsys):
    llamadas = _tabla_de_dos(R, monkeypatch, con_timeout=False)
    monkeypatch.setattr(R, "FICHEROS_TEST", ("tests/test_vacio.py",))
    def falla(*a):
        raise OSError("LIMPIEZA-BLOQUEADA")
    monkeypatch.setattr(G, "_borrar_temporales", falla)
    assert R.main() == 7, "[M15-HUERFANOS] un return temprano ocultó el fallo de limpieza"
    assert llamadas["n"] == 1
    assert "LIMPIEZA-BLOQUEADA" in capsys.readouterr().out


@ARNESES
def test_timeout_limpia_copia_y_basetemp_ANTES_de_la_siguiente_fila(arnes, monkeypatch):
    _tabla_de_dos(arnes, monkeypatch, con_timeout=True)
    copiar = G._copia_limpia
    observadas = []
    def copia(raiz, numero):
        if numero == 2:
            assert not (Path(raiz) / "qs_01").exists(), "[M15-LIMPIEZA] copia aún presente"
            assert not (Path(raiz) / "bt_01").exists(), "[M15-LIMPIEZA] basetemp aún presente"
            observadas.append(numero)
        return copiar(raiz, numero)
    monkeypatch.setattr(G, "_copia_limpia", copia)
    assert arnes.main() == 1
    assert observadas == [2]


@ARNESES
def test_fallo_de_limpieza_del_timeout_IMPIDE_la_fila_siguiente(arnes, monkeypatch):
    llamadas = _tabla_de_dos(arnes, monkeypatch, con_timeout=True)
    borrar = G._borrar_temporales
    def falla(raiz, *hijos):
        if hijos:
            raise OSError("LIMPIEZA-DE-FILA-BLOQUEADA")
        return borrar(raiz)
    monkeypatch.setattr(G, "_borrar_temporales", falla)
    with pytest.raises(OSError, match="LIMPIEZA-DE-FILA-BLOQUEADA"):
        arnes.main()
    assert llamadas["n"] == 2, "[M15-LIMPIEZA] se continuó pese a la limpieza fallida"


@ARNESES
def test_la_deriva_tras_timeout_IMPIDE_la_fila_siguiente(arnes, monkeypatch, capsys):
    llamadas = _tabla_de_dos(arnes, monkeypatch, con_timeout=True)
    lecturas = iter([{"control": "antes"}, {"control": "despues"}, {"control": "despues"}])
    monkeypatch.setattr(G, "_huella", lecturas.__next__)
    with pytest.raises(RuntimeError, match="árbol vigilado cambió"):
        arnes.main()
    assert llamadas["n"] == 2
    assert "CAMBI" in capsys.readouterr().out


@ARNESES
def test_la_deriva_DURANTE_limpieza_del_timeout_tambien_detiene(arnes, monkeypatch):
    llamadas = _tabla_de_dos(arnes, monkeypatch, con_timeout=True)
    lecturas = iter([{"control": "antes"}, {"control": "antes"},
                     {"control": "despues"}, {"control": "despues"}])
    monkeypatch.setattr(G, "_huella", lecturas.__next__)
    with pytest.raises(RuntimeError, match="durante la limpieza"):
        arnes.main()
    assert llamadas["n"] == 2, "[M15-HUELLA-POST] se continuó tras la deriva en limpieza"


def test_conservar_y_timeout_NO_finge_limpieza_ni_continua(monkeypatch, tmp_path):
    # Sale el CLI del gate; permanece este contrato de la primitiva compartida.
    raiz = tmp_path / "mutacion_refvalida_conservar"
    copia, basetemp = raiz / "qs_01", raiz / "bt_01"
    copia.mkdir(parents=True)
    basetemp.mkdir()
    monkeypatch.setattr(G, "_huella", lambda: {})

    def borrar_prohibido(*args):
        pytest.fail("conservar no permite fingir una limpieza")

    monkeypatch.setattr(G, "_borrar_temporales", borrar_prohibido)
    with pytest.raises(RuntimeError, match="timeout con --conservar"):
        G._cerrar_fila_timeout(str(raiz), str(copia), str(basetemp), {}, conservar=True)
    assert copia.is_dir() and basetemp.is_dir()


@ARNESES
def test_limpieza_final_fallida_NO_puede_devolver_verde(arnes, monkeypatch, capsys):
    _tabla_de_dos(arnes, monkeypatch, con_timeout=False)
    def falla(*a):
        raise OSError("LIMPIEZA-FINAL-BLOQUEADA")
    monkeypatch.setattr(G, "_borrar_temporales", falla)
    assert arnes.main() == 7, "[M15-LIMPIEZA-FINAL] un fallo de limpieza dio verde"
    assert "LIMPIEZA-FINAL-BLOQUEADA" in capsys.readouterr().out


@ARNESES
def test_cancelacion_no_queda_oculta_por_otro_fallo_de_limpieza(arnes, monkeypatch):
    def cancelada(*a, **kw):
        raise KeyboardInterrupt("CANCELACION-PRIMARIA")
    def falla(*a):
        raise OSError("LIMPIEZA-SECUNDARIA")
    monkeypatch.setattr(G, "_correr", cancelada)
    monkeypatch.setattr(G, "_borrar_temporales", falla)
    monkeypatch.setattr(sys, "argv", [arnes.__name__])
    with pytest.raises(KeyboardInterrupt, match="CANCELACION-PRIMARIA") as error:
        arnes.main()
    assert any("LIMPIEZA-SECUNDARIA" in n for n in error.value.__notes__)


def test_limpieza_retira_un_temporal_con_fichero_solo_lectura(tmp_path):
    raiz = tmp_path / "mutacion_gate_solo_lectura"
    objetos = raiz / "bt_00" / "repo" / ".git" / "objects" / "ab"
    objetos.mkdir(parents=True)
    objeto = objetos / "objeto"
    objeto.write_bytes(b"residuo con permisos de objeto git")
    objeto.chmod(0o444)
    G._borrar_temporales(str(raiz))
    assert not raiz.exists(), "[M15-0444] quedaron temporales de solo lectura"


def test_manejador_solo_lectura_propaga_errores_ajenos(monkeypatch):
    error = OSError("FALLO-AJENO")
    def prohibido(*a):
        pytest.fail("[M15-0444] se trató un error ajeno a permisos")
    monkeypatch.setattr(G.os, "chmod", prohibido)
    with pytest.raises(OSError) as visto:
        G._quitar_solo_lectura(prohibido, "no-se-toca", error)
    assert visto.value is error


def test_manejador_solo_lectura_no_oculta_un_reintento_fallido(tmp_path):
    objeto = tmp_path / "objeto"
    objeto.write_bytes(b"residuo")
    objeto.chmod(0o444)
    error = PermissionError("SIGUE-BLOQUEADO")
    llamadas = []
    def falla(ruta):
        llamadas.append(ruta)
        raise error
    with pytest.raises(PermissionError) as visto:
        G._quitar_solo_lectura(falla, str(objeto), PermissionError("SOLO-LECTURA"))
    assert visto.value is error
    assert llamadas == [str(objeto)]


def test_limpieza_prevalida_todos_los_destinos_sin_borrar_el_primero(tmp_path):
    raiz = tmp_path / "mutacion_gate_focal"
    copia = raiz / "qs_01"
    copia.mkdir(parents=True)
    ajeno = tmp_path / "ajeno"
    ajeno.mkdir()
    with pytest.raises(OSError, match="fuera del temporal"):
        G._borrar_temporales(str(raiz), str(copia), str(ajeno))
    assert copia.is_dir() and ajeno.is_dir()


def test_limpieza_NO_acepta_un_rmtree_que_no_borra(tmp_path, monkeypatch):
    raiz = tmp_path / "mutacion_gate_focal"
    raiz.mkdir()
    monkeypatch.setattr(G.shutil, "rmtree", lambda *a, **kw: None)
    with pytest.raises(OSError, match="no eliminó"):
        G._borrar_temporales(str(raiz))


@ARNESES
def test_temporal_en_repo_se_rechaza_sin_borrado_recursivo(arnes, tmp_path, monkeypatch):
    monkeypatch.setattr(G, "REPO_REAL", str(tmp_path))
    monkeypatch.setattr(sys, "argv", [arnes.__name__])
    def recursivo_prohibido(*a, **kw):
        pytest.fail("[M15-RAIZ] se intentó rmtree sobre una ubicación rechazada")
    monkeypatch.setattr(G.shutil, "rmtree", recursivo_prohibido)
    with pytest.raises(SystemExit, match="DENTRO del repo"):
        arnes.main()
    assert not list(tmp_path.glob("mutacion_*"))
