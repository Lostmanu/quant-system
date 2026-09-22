"""EL REGISTRO DE LA SONDA: un identificador, una función que se importa y se puede llamar.

La declaración por AST del prerregistro acredita que existe un símbolo con ese nombre. Eso no es lo
mismo que una implementación: un AST no distingue una función de un nombre suelto —de hecho hasta
2026-08-28 una variable LOCAL dentro de otra función satisfacía la declaración (E-71)— y, aunque lo
distinguiera, seguiría sin decir que el módulo IMPORTA ni que alguien la LLAMA.

Aquí se fija lo otro: que resuelva de verdad, que el registro y el prerregistro digan lo mismo, y
que nadie gaste un crédito antes de comprobarlo.
"""
import os
import sys

import pytest

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(QS, "tools"))
import registro_sonda as RS                                           # noqa: E402


# ═══════════════════════════════════ RESOLVER de verdad, no leer
def test_un_id_que_no_esta_en_el_registro_no_resuelve():
    with pytest.raises(RS.ReglaNoEjecutable, match="no está en el registro"):
        RS.resolver("C0")


def test_una_regla_bien_registrada_devuelve_la_FUNCION(monkeypatch):
    """Control de no-trivialidad: sin esto, todo lo demás lo cumpliría un registro que rechaza todo."""
    monkeypatch.setattr(RS, "REGLAS", {"C1": "analysis.ref_valida:clasificar"})
    fn = RS.resolver("C1")
    assert callable(fn) and fn("100.0", "100.0") == "ok"


def test_una_CONSTANTE_no_es_una_implementacion_ejecutable(monkeypatch):
    """`LIMITE_ABSURDO_BPS` existe y es legítima como umbral, pero no se puede INVOCAR. El AST no
    distingue las dos cosas; el import sí, y por eso esto se resuelve importando."""
    monkeypatch.setattr(RS, "REGLAS", {"C1": "analysis.ref_valida:LIMITE_ABSURDO_BPS"})
    with pytest.raises(RS.ReglaNoEjecutable, match="NO es invocable"):
        RS.resolver("C1")


def test_un_modulo_que_no_importa_se_dice_con_su_motivo(monkeypatch):
    monkeypatch.setattr(RS, "REGLAS", {"C1": "analysis.modulo_que_no_existe:f"})
    with pytest.raises(RS.ReglaNoEjecutable, match="no importa"):
        RS.resolver("C1")


def test_un_atributo_que_no_existe_en_un_modulo_que_SI_importa(monkeypatch):
    monkeypatch.setattr(RS, "REGLAS", {"C1": "analysis.ref_valida:funcion_inventada"})
    with pytest.raises(RS.ReglaNoEjecutable, match="no define"):
        RS.resolver("C1")


def test_un_destino_sin_los_dos_puntos_no_resuelve(monkeypatch):
    monkeypatch.setattr(RS, "REGLAS", {"C1": "analysis.ref_valida"})
    with pytest.raises(RS.ReglaNoEjecutable, match="modulo:funcion"):
        RS.resolver("C1")


# ═══════════════════════════════════ ANTES del primer crédito, y TODAS de golpe
def test_exigir_listo_reporta_TODAS_las_que_fallan_no_la_primera(monkeypatch):
    """Descubrir a mitad de campaña que la quinta regla no importa deja media campaña gastada y
    ningún resultado utilizable."""
    monkeypatch.setattr(RS, "REGLAS", {"C1": "analysis.no_existe:f", "C2": "analysis.tampoco:g"})
    with pytest.raises(RS.ReglaNoEjecutable) as e:
        RS.exigir_listo(["C1", "C2", "C3"])
    texto = str(e.value)
    assert "C1" in texto and "C2" in texto and "C3" in texto, "las tres, no la primera"


def test_exigir_listo_devuelve_las_funciones_cuando_todo_resuelve(monkeypatch):
    monkeypatch.setattr(RS, "REGLAS", {"C1": "analysis.ref_valida:clasificar",
                                       "C2": "analysis.ref_valida:markout_bps"})
    resueltas = RS.exigir_listo(["C1", "C2"])
    assert set(resueltas) == {"C1", "C2"} and all(callable(f) for f in resueltas.values())


# ═══════════════════════════════════ UNA sola fuente
def test_norma_SIN_codigo_se_denuncia(monkeypatch):
    monkeypatch.setattr(RS, "REGLAS", {})
    problemas = RS.cuadra_con_el_prerregistro(["C1"])
    assert len(problemas) == 1 and "norma sin" in problemas[0]


def test_codigo_SIN_norma_tambien(monkeypatch):
    """Los dos sentidos. Una regla registrada que el documento no declara es código que nadie
    pre-registró, y eso es la misma clase de mentira que la contraria."""
    monkeypatch.setattr(RS, "REGLAS", {"C9": "analysis.ref_valida:clasificar"})
    problemas = RS.cuadra_con_el_prerregistro([])
    assert len(problemas) == 1 and "código sin" in problemas[0]


def test_cuando_coinciden_no_hay_problema(monkeypatch):
    monkeypatch.setattr(RS, "REGLAS", {"C1": "analysis.ref_valida:clasificar"})
    assert RS.cuadra_con_el_prerregistro(["C1"]) == []


# ═══════════════════════════════════ el ESTADO de hoy, fijado a propósito
def test_HOY_el_registro_esta_VACIO_y_la_sonda_NO_puede_correr():
    """No es un test de relleno: fija que el estado declarado y el real coinciden. El día que alguien
    registre la primera regla, este test le obliga a mirar aquí y a decir por qué."""
    assert RS.REGLAS == {}, "si ya hay reglas, actualiza este test y el prerregistro"
    sys.path.insert(0, os.path.join(QS, "tools"))
    import guardia_documental as G
    assert len(G.exigir_cobertura(RS.DOC_SONDA)) > 0, "con el registro vacío no se ejecuta"
