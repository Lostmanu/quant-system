"""Tests conservados de la maquinaria común de mutación — el verificador también se verifica.

Por qué existen (mesa, 2026-08-25): el arnés acumuló **tres** defectos propios en un solo día —
mutaba producción in situ, contaba una excepción colateral como mordida, y calculaba una guardia
(`base_rota`) que `main` no comprobaba. Un instrumento sin tests es una afirmación.

Se prueban las piezas PURAS (`_juzgar`, `_diferencias`): son donde vive la lógica de acreditación y
donde estaban los fallos. Correr el arnés entero desde aquí duplicaría minutos de pytest sin añadir
poder de detección.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.arnes_comun import (_diferencias, _interpretar,   # noqa: E402
                                   _juzgar, _problemas_baseline)

CAUSA = {"test_a": "DID NOT RAISE RuntimeError", "test_b": "[MUERDE-X]"}


def _estado(razones):
    return _juzgar(CAUSA, razones, n_passed=0)[0]


def test_acredita_solo_si_TODOS_muerden_por_su_causa():
    """El caso bueno. Sin este control positivo, un `_juzgar` que no acreditara nunca pasaría
    todos los tests negativos de abajo."""
    assert _estado({"test_a": "Failed: DID NOT RAISE RuntimeError",
                    "test_b": "AssertionError: [MUERDE-X] la propiedad"}) == "ROJO ✓"


def test_ninguno_muerde_es_TEST_VACUO():
    assert "VACUO" in _estado({})


def test_mordida_PARCIAL_no_acredita():
    """Declarar dos tests y conformarse con que caiga uno deja al otro libre de volverse vacuo sin
    que nadie se entere. Era el agujero: bastaba con que fallara cualquiera de los declarados."""
    e = _estado({"test_a": "Failed: DID NOT RAISE RuntimeError"})
    assert "PARCIAL" in e, e


def test_causa_AJENA_no_acredita():
    """Fallar el test esperado NO demuestra la causa esperada: un `TypeError` dentro del mismo test
    también sale como FAILED. Antes entraba como ROJO."""
    e = _estado({"test_a": "TypeError: 'NoneType' object is not subscriptable",
                 "test_b": "AssertionError: [MUERDE-X] la propiedad"})
    assert "AJENA" in e, e


def test_un_AssertionError_cualquiera_NO_vale_por_el_marcador():
    """El marcador `[MUERDE-X]` identifica la PROPIEDAD, no el tipo de excepción. Un regex laxo
    como /assert/ aceptaba cualquier aserción del test."""
    e = _estado({"test_a": "Failed: DID NOT RAISE RuntimeError",
                 "test_b": "AssertionError: assert 3 == 4"})
    assert "AJENA" in e, e


def test_un_fallo_COLATERAL_invalida_aunque_muerdan_todos_los_esperados():
    """Si además cae un test no declarado, la mutación tocó algo más y el resultado ya no es
    atribuible a la guardia — aunque los esperados hayan mordido correctamente."""
    e = _estado({"test_a": "Failed: DID NOT RAISE RuntimeError",
                 "test_b": "AssertionError: [MUERDE-X] la propiedad",
                 "test_vecino": "AssertionError: algo sin relación"})
    assert "COLATERAL" in e, e


def test_la_causa_se_compara_sin_distinguir_mayusculas():
    assert _estado({"test_a": "Failed: did not raise runtimeerror",
                    "test_b": "AssertionError: [muerde-x]"}) == "ROJO ✓"


def test_la_causa_normaliza_la_grafia_de_clase_de_pytest_sin_aceptar_otra_excepcion():
    assert _estado({"test_a": "Failed: DID NOT RAISE <class 'RuntimeError'>",
                    "test_b": "AssertionError: [MUERDE-X]"}) == "ROJO ✓"
    assert "AJENA" in _estado({"test_a": "Failed: DID NOT RAISE <class 'ValueError'>",
                               "test_b": "AssertionError: [MUERDE-X]"})


@pytest.mark.parametrize("antes,ahora,esperado", [
    ({"a": "1"}, {"a": "1", "b": "2"}, ([("b")], [], [])),          # alta
    ({"a": "1", "b": "2"}, {"a": "1"}, ([], ["b"], [])),            # BAJA
    ({"a": "1"}, {"a": "9"}, ([], [], ["a"])),                      # modificado
    ({"a": "1"}, {"a": "1"}, ([], [], [])),                         # intacto
])
def test_diferencias_detecta_altas_BAJAS_y_modificados(antes, ahora, esperado):
    """Una lista de sha no ve las BAJAS: un fichero borrado del árbol real pasaría inadvertido.
    Por eso la huella es un dict."""
    assert _diferencias(antes, ahora) == esperado


# ============ los focales que la mesa echaba en falta (P1-1, 2026-08-25) ============
# «Los 11 focales solo prueban `_juzgar` y `_diferencias`. No prueban `_correr`, las cuatro
# condiciones de baseline ni excepción/retorno→huella.» Correcto. `_correr` mezclaba el subproceso
# con la interpretación, así que la lógica que decide «inválida» no tenía forma de probarse — y ahí
# vivían DOS defectos ya cazados: `base_rota` calculada y no comprobada, y la detección por texto
# que `--tb=no` volvía inservible. Se extrajo `_interpretar`, que es pura.

_SALIDA_OK = "...\n1 passed, 99 deselected in 0.42s\n"
_SALIDA_FALLO = ("FAILED tests/t.py::test_a - Failed: DID NOT RAISE RuntimeError\n"
                 "1 failed, 99 deselected in 0.51s\n")


def test_interpretar_una_corrida_verde():
    razones, linea, invalida, n = _interpretar(_SALIDA_OK, 0)
    assert razones == {} and not invalida and n == 1 and "1 passed" in linea


def test_interpretar_recoge_el_motivo_COMPLETO_del_fallo():
    """El motivo es lo que permite verificar la CAUSA. Cuando pytest lo truncaba a «- Fa...» el
    arnés no podía acreditar nada — y se negó a hacerlo, que fue el comportamiento correcto."""
    razones, _, invalida, _ = _interpretar(_SALIDA_FALLO, 1)
    assert razones == {"test_a": "Failed: DID NOT RAISE RuntimeError"}
    assert not invalida


@pytest.mark.parametrize("rc", [2, 3, 4, 5, -1, 137])
def test_interpretar_marca_INVALIDA_cualquier_rc_ajeno_a_0_y_1(rc):
    """rc de pytest: 0 ok · 1 fallos · 2 interrumpido · 3 interno · 4 uso · 5 sin tests. Todo lo que
    no sea 0 o 1 significa que pytest no llegó a juzgar nada."""
    assert _interpretar(_SALIDA_OK, rc)[2] is True


def test_interpretar_marca_INVALIDA_un_recuento_con_ERRORES():
    """«error» = el test no llegó a correr (colección/import/fixture); «failed» = corrió y falló.
    Con `--tb=no` el SyntaxError NO se imprime, así que la detección va por el RECUENTO."""
    assert _interpretar("1 error in 0.37s\n", 1)[2] is True


def test_interpretar_marca_INVALIDA_una_salida_sin_recuento():
    assert _interpretar("", 0)[2] is True
    assert _interpretar("ruido sin recuento\n", 0)[2] is True


# ---------------------------------------------------------------- las cuatro de la baseline
def test_baseline_limpia_no_tiene_problemas():
    """Control POSITIVO: sin él, una función que siempre devolviera problemas pasaría los cuatro
    tests de abajo."""
    assert _problemas_baseline(0, False, {}, 14, 14) == []


@pytest.mark.parametrize("kw,fragmento", [
    (dict(rc=1), "returncode=1"),
    (dict(invalida=True), "recuento con errores"),
    (dict(razones={"test_x": "boom"}), "test_x"),
    (dict(n_passed=13), "13 de 14"),
])
def test_baseline_exige_las_CUATRO_por_separado(kw, fragmento):
    """EL P0-1 DE LA MESA. `razones == {}` sin mirar `rc` deja pasar un pytest que falló con un
    formato de nodo que `_FALLO` no reconoce: `razones={}`, `invalida=False`, y la base se declara
    VERDE. Cada condición se comprueba sola Y se NOMBRA en el mensaje."""
    base = dict(rc=0, invalida=False, razones={}, n_passed=14, n_esperados=14)
    p = _problemas_baseline(**{**base, **kw})
    assert p and any(fragmento in x for x in p), p


def test_baseline_acumula_TODOS_los_problemas_no_solo_el_primero():
    """Si algo va mal por cuatro motivos, el operador tiene que ver los cuatro: parar en el primero
    convierte una reparación en cuatro viajes."""
    assert len(_problemas_baseline(1, True, {"t": "x"}, 0, 14)) == 4


# ---------------------------------------------------------------- excepción → huella → relanzar
def test_una_EXCEPCION_no_se_traga_y_la_huella_se_juzga_igual(monkeypatch, capsys):
    """El P1 de la mesa. El `finally` calcula la deriva; si además hiciera `return`, se TRAGARÍA la
    excepción que lo trajo. Aquí se revienta la copia del árbol y se exige que (a) la excepción
    ORIGINAL salga, y (b) la huella se haya juzgado antes — visible en la salida."""
    import tools.mutacion_ref_valida as R
    M = R.M

    def _revienta(*a, **k):
        raise RuntimeError("fallo inyectado en la copia")

    monkeypatch.setattr(M, "_copia_limpia", _revienta)
    finalizaciones = []
    finalizar_real = M._finalizar_copia

    def finalizar(*args, **kwargs):
        resultado = finalizar_real(*args, **kwargs)
        finalizaciones.append(resultado)
        return resultado

    monkeypatch.setattr(M, "_finalizar_copia", finalizar)
    monkeypatch.setattr(sys, "argv", ["mutacion_ref_valida.py"])
    with pytest.raises(RuntimeError, match="fallo inyectado en la copia"):
        R.main()
    assert len(finalizaciones) == 1, "la huella no se juzgó antes de relanzar"
    diferencias, fallo_limpieza = finalizaciones[0]
    assert not any(diferencias) and fallo_limpieza is None
