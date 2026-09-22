"""Pruebas del pre-vuelo conservado. Las pruebas de cifras_paquete salen con él."""
import io
import json
import os
import sys

import pytest

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(QS, "tools"))
import prevuelo as P                                                    # noqa: E402


# ═══════════════════════════════════════════════════════ PRE-VUELO
def _arnes_falso(tmp_path, filas_src, objetivo_src="x = 1\ny = 2\n",
                 tests_src="def test_uno():\n    pass\n"):
    """Un arnés sintético completo bajo `tmp_path`, con la MISMA forma que los tres reales."""
    (tmp_path / "tools").mkdir(exist_ok=True)
    (tmp_path / "analysis").mkdir(exist_ok=True)
    (tmp_path / "tests").mkdir(exist_ok=True)
    io.open(tmp_path / "analysis" / "objetivo.py", "w", encoding="utf-8", newline="\n").write(objetivo_src)
    io.open(tmp_path / "tests" / "test_falso.py", "w", encoding="utf-8", newline="\n").write(tests_src)
    io.open(tmp_path / "tools" / "mut_falso.py", "w", encoding="utf-8", newline="\n").write(
        "MUTACIONES = [\n" + filas_src + "\n]\n")
    return {"modulo": "mut_falso.py", "tabla": "MUTACIONES",
            "objetivo": os.path.join("analysis", "objetivo.py"),
            "objetivo_en": None, "tests_en": 2,
            "ficheros_test": (os.path.join("tests", "test_falso.py"),)}


@pytest.fixture
def falso(tmp_path, monkeypatch):
    """Redirige el pre-vuelo al árbol sintético. NO toca el árbol real (tres contaminaciones)."""
    def _crear(filas_src, **kw):
        cfg = _arnes_falso(tmp_path, filas_src, **kw)
        monkeypatch.setattr(P, "QS", str(tmp_path))
        monkeypatch.setattr(P, "_AQUI", str(tmp_path / "tools"))
        monkeypatch.setattr(P, "ARNESES", {"falso": cfg})
        return P.revisar_arnes("falso")
    return _crear


def test_un_ancla_MUERTA_es_un_problema(falso):
    """Cero ocurrencias: la fila no acredita nada. Es LA clase que costó tres relanzamientos del
    arnés íntegro, once minutos cada uno, en una sola sesión."""
    p = falso('    ("fila", [("NO ESTA EN EL FICHERO", "z")], {"test_uno": "assert"}),')
    assert p, "un ancla a cero tiene que salir como problema"
    assert any("0" in m or "no unica" in m.lower() or "única" in m.lower() for m in p), p


def test_un_ancla_DUPLICADA_es_un_problema(falso):
    """Dos ocurrencias: la mutación tocaría un sitio que no es el suyo."""
    p = falso('    ("fila", [("x = 1", "z")], {"test_uno": "assert"}),',
              objetivo_src="x = 1\nx = 1\n")
    assert p, "un ancla a dos tiene que salir como problema"


def test_un_ancla_UNICA_no_da_problema(falso):
    assert falso('    ("fila", [("x = 1", "z")], {"test_uno": "assert"}),') == []


def test_un_TEST_DECLARADO_INEXISTENTE_es_un_problema(falso):
    """Un test que no existe no puede fallar con su marcador: su fila no acredita nada, y este
    proyecto ya se comió una fila así durante una tanda entera."""
    p = falso('    ("fila", [("x = 1", "z")], {"test_que_no_existe": "assert"}),')
    assert p and any("test" in m.lower() for m in p), p


def test_la_semantica_de_los_tests_es_SUBCADENA_como_en_pytest_k(falso):
    """LA COMPROBACIÓN QUE SE CAZÓ A SÍ MISMA. `mutacion_libro_tx` declara SUBCADENAS que van a `-k`
    (`M1212_abort_ajeno` casa con `test_M1212_abort_ajeno_no_equivalente_STOP`). Exigir
    `def <nombre>(` marcaba 27 filas VIVAS del arnés del libro como inexistentes: el pre-vuelo
    habría mentido en su primera corrida, que es justo la clase de fallo que existe para cazar."""
    p = falso('    ("fila", [("x = 1", "z")], {"M99_trozo": "assert"}),',
              tests_src="def test_M99_trozo_del_medio_y_mas_cosas():\n    pass\n")
    assert p == [], f"una subcadena de un test real tiene que casar; salió {p}"


def test_un_arnes_que_NO_IMPORTA_se_declara_en_vez_de_reventar(falso):
    """Un módulo roto tiene que salir como problema TIPADO, no como excepción cruda que aborte el
    pre-vuelo entero y deje los otros dos arneses sin revisar.

    LA PROPIEDAD SE AFIRMA, no se deja al azar del modo de fallo. Si `revisar_arnes` propaga, este
    test moría con la traza del `SyntaxError` y el arnés lo cazaba como CAUSA AJENA: el fallo no era
    de la aserción sino colateral. Envolviéndolo, el mutante muere por lo que este test dice."""
    try:
        p = falso('    ("fila", [("x = 1", "z")], {"test_uno": "assert"}),\n)))SINTAXIS ROTA(((')
    except Exception as e:                                     # noqa: BLE001
        pytest.fail(f"revisar_arnes PROPAGO {type(e).__name__} en vez de declararlo como problema")
    assert p and any("IMPORT" in m.upper() for m in p), p


def test_un_OBJETIVO_ILEGIBLE_se_declara(tmp_path, monkeypatch):
    cfg = _arnes_falso(tmp_path, '    ("fila", [("x = 1", "z")], {"test_uno": "assert"}),')
    cfg["objetivo"] = os.path.join("analysis", "no_existe.py")
    monkeypatch.setattr(P, "QS", str(tmp_path))
    monkeypatch.setattr(P, "_AQUI", str(tmp_path / "tools"))
    monkeypatch.setattr(P, "ARNESES", {"falso": cfg})
    p = P.revisar_arnes("falso")
    assert p and any("ILEGIBLE" in m.upper() for m in p), p


def test_TODOS_LOS_ARNESES_REALES_ESTAN_DECLARADOS():
    """LA GUARDIA CONTRA EL MODO DE FALLO QUE EL PROPIO PRE-VUELO NOMBRA: «si alguien añade un arnés
    y no lo mete en esta lista, el pre-vuelo NO lo cubre». Sin este test esa frase es una esperanza.
    Si aparece un `tools/mutacion_*.py` nuevo y nadie lo declara, esto se pone rojo."""
    en_disco = {f for f in os.listdir(os.path.join(QS, "tools"))
                if f.startswith("mutacion_") and f.endswith(".py")}
    declarados = {cfg["modulo"] for cfg in P.ARNESES.values()}
    assert en_disco == declarados, (f"arneses sin declarar en `prevuelo.ARNESES`: "
                                    f"{sorted(en_disco - declarados)}; declarados que no existen: "
                                    f"{sorted(declarados - en_disco)}")


def test_los_arneses_reales_pasan_el_prevuelo_hoy():
    """El árbol vigente está limpio para los tres. Si esto se pone rojo, hay una fila muerta AHORA."""
    for clave in sorted(P.ARNESES):
        assert P.revisar_arnes(clave) == [], f"el arnés {clave!r} tiene problemas de pre-vuelo"
