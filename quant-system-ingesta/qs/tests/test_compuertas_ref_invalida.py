"""Las COMPUERTAS del incidente de referencia inválida — que BLOQUEEN, no que lo digan.

POR QUÉ EXISTEN. La mesa (2026-08-27) rechazó la primera reparación en parte porque varias «reglas»
eran declarativas: el careo IMPRIMÍA «con brecha ≤0,2 es interpretable» y seguía pasara lo que pasara;
el STOP sobre el carril no conforme era documental y nada impedía ejecutar el runner; y los artefactos
contaminados seguían siendo consumibles aguas abajo.

Una compuerta que no bloquea es una glosa. Estos tests la acreditan **haciéndola disparar**.
"""
import io
import os
import subprocess
import sys

import numpy as np
import pytest

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QS)
sys.path.insert(0, os.path.join(QS, "tools"))

from analysis import ref_valida as RV                                  # noqa: E402
from analysis import carril as CA                                      # noqa: E402


# ============================================================ compuerta de CONSUMO
def test_exigir_limpio_RECHAZA_un_artefacto_contaminado():
    """No basta con avisar: tiene que impedir el consumo. Se prueba con la firma real del defecto."""
    lado = np.array([1.0, -1.0, 1.0])
    mo = np.array([[-1e4], [+1e4], [12.0]])          # dos con firma de ref=0, una sana
    with pytest.raises(RuntimeError, match="ARTEFACTO CONTAMINADO"):
        RV.exigir_limpio(mo, lado, "bloque_de_prueba.npz")


def test_exigir_limpio_DEJA_PASAR_lo_limpio():
    """Control de no-trivialidad: si rechazara todo, el test de arriba no acreditaría nada."""
    lado = np.array([1.0, -1.0])
    mo = np.array([[12.0], [-3.0]])
    c = RV.exigir_limpio(mo, lado, "limpio.npz")
    assert c["total"] == 0 and c["exacta"] == 0


def test_exigir_limpio_distingue_EXACTA_de_CASI_CERO():
    """`ref = 0` da un valor bit-exacto; una referencia positiva diminuta cae cerca pero NO es un cero.
    Contarlas juntas fue la sobreafirmación que la mesa señaló: 15.540 «ceros» eran «compatibles»."""
    lado = np.array([1.0, 1.0])
    mo = np.array([[-1e4], [-1e4 + 0.005]])
    c = RV.contaminacion(mo, lado)
    assert c["exacta"] == 1 and c["casi"] == 1 and c["total"] == 2


def test_el_escape_forense_es_EXPLICITO_y_no_silencioso():
    lado = np.array([1.0])
    mo = np.array([[-1e4]])
    c = RV.exigir_limpio(mo, lado, "x.npz", permitir=True)
    assert c["exacta"] == 1, "con el escape se PASA, pero devolviendo el recuento a la vista"




# ============================================================ compuerta del CARRIL (fail-closed)
CANON = "data_hist/lighter_confirm/blocks"


def test_el_carril_no_conforme_IMPIDE_producir_para_un_simbolo_certificado():
    """El pre-registro manda MID para LIT y DOGE; los runners usan el trade más cercano."""
    assert CA.conforme("LIT", "confirmacion", CA.TRADE_BINANCE) is False
    assert CA.conforme("DOGE", "piloto", CA.TRADE_BINANCE) is False
    with pytest.raises(RuntimeError, match="CARRIL NO CONFORME"):
        CA.exigir_produccion("LIT", "confirmacion", CA.TRADE_BINANCE, CANON, CANON)




def test_capa2_es_CONFORME_con_prints_de_lighter_y_no_queda_bloqueada_de_rebote():
    """Capa 2 marca contra prints del propio Lighter POR DISEÑO (§5 del prereg de capa 2). Tratarla
    como no conforme sería inventar un incumplimiento donde no lo hay, y la mesa fue explícita en que
    no afirma que capa 2 esté invalidada."""
    assert CA.exigido_para("LIT", "capa2") == CA.PRINTS_LIGHTER
    assert CA.conforme("LIT", "capa2", CA.PRINTS_LIGHTER) is True
    CA.exigir_produccion("LIT", "capa2", CA.PRINTS_LIGHTER, CANON, CANON)      # no lanza


def test_fuera_del_directorio_CANONICO_no_bloquea_pero_SI_marca():
    """Se ata al DESTINO y no a la función: lo que hace peligroso a un artefacto es dónde acaba. Así
    `test_m10_differ_core`, que produce en un temporal para comparar identidad-byte, sigue corriendo
    —si esto bloqueara, el CI se pondría rojo por proteger algo que no estaba en peligro."""
    CA.exigir_produccion("LIT", "confirmacion", CA.TRADE_BINANCE, "/tmp/otro_sitio", CANON)


def test_el_escape_del_carril_YA_NO_abre_el_directorio_CANONICO(monkeypatch, tmp_path):
    """ESTE TEST FIJABA EL COMPORTAMIENTO CONTRARIO hasta hoy, y estaba mal.

    Acreditaba que con `QS_CARRIL_NO_CONFORME=1` la producción NO CONFORME pasaba en el canónico,
    «marcada» — y esa marca no existía para quien no publica por la primitiva: `eco_runner_lit`
    escribía con `np.savez`, ningún campo llevaba el carril y el gate no recalculaba nada (mesa
    2026-08-28, P0-2). Peor: para ese productor `conforme` era SIEMPRE False, así que el escape no
    era una excepción sino su única vía de escritura, encendida de forma permanente.

    Un escape que hay que dejar puesto no es un escape: es la puerta principal."""
    monkeypatch.setenv(CA.VAR_ESCAPE, "1")
    with pytest.raises(CA.CarrilNoConforme, match="NO sirve aquí"):
        CA.exigir_produccion("LIT", "confirmacion", CA.TRADE_BINANCE, CANON, CANON)
    # FUERA del canónico la reproducción forense sigue siendo posible: no se cierra la puerta a
    # reproducir, se cierra a reproducir DENTRO del sitio bueno.
    CA.exigir_produccion("LIT", "confirmacion", CA.TRADE_BINANCE, str(tmp_path / "forense"), CANON)


@pytest.mark.parametrize("valor", ["0", "true", "yes", ""])
def test_el_escape_del_carril_NO_se_activa_con_cualquier_valor(monkeypatch, valor):
    """Un escape que se enciende por accidente no es un escape."""
    monkeypatch.setenv(CA.VAR_ESCAPE, valor)
    with pytest.raises(RuntimeError, match="CARRIL NO CONFORME"):
        CA.exigir_produccion("LIT", "confirmacion", CA.TRADE_BINANCE, CANON, CANON)


# ============================================================ la ACREDITACION vive en `artefacto`
def test_la_maquinaria_de_marca_YA_NO_esta_duplicada_en_carril():
    """`carril` decide QUE carril toca; `artefacto` acredita el fichero. Tener las dos cosas en dos
    sitios fue la primera version, y dos mecanismos de acreditacion en paralelo es la duplicacion de
    E-49 — la misma que hizo que quitar un guardia no abriera ningun agujero."""
    for retirada in ("escribir_marca", "leer_marca", "ruta_marca", "exigir_consumo"):
        assert not hasattr(CA, retirada), f"`carril.{retirada}` deberia vivir solo en `artefacto`"
    for propia in ("exigido_para", "conforme", "exigir_produccion", "CarrilNoConforme"):
        assert hasattr(CA, propia)


def _cuerpo_capa2():
    """Se REUTILIZA el andamio de `test_artefacto`: dos constructores que se parecen pero no
    son iguales es la duplicacion que este proyecto cataloga como E-49."""
    from tests.test_artefacto import cuerpo
    return cuerpo("capa2", n=2)


def test_EL_ORDEN_SE_COMPRUEBA_EJECUTANDO_no_leyendo_fuentes(tmp_path, monkeypatch):
    """El npz canonico NUNCA existe sin su manifiesto — y se acredita provocandolo, no leyendo codigo.

    La version anterior comprobaba por `str.find` que una llamada aparecia antes que otra en el
    fichero. Eso fija el ORDEN DEL TEXTO, no el del flujo: un `return` entre medias, un `try` o un
    refactor lo dejaban verde sin que la garantia existiera."""
    import analysis.artefacto as A
    destino = str(tmp_path / "LIT_2026-03-06.npz")

    real = os.replace                     # ANTES de parchear: `A.os` ES el modulo os, y sin
                                          # capturar el original el doble se llama a si mismo
                                          # (lo destapo el arnes de mutacion: la fila moria con
                                          # RecursionError, no con la asercion que importa).
    def replace_que_falla_en_el_manifiesto(src, dst):
        if dst.endswith(A.SUFIJO):
            raise OSError("crash simulado justo al publicar el manifiesto")
        return real(src, dst)

    monkeypatch.setattr(A.os, "replace", replace_que_falla_en_el_manifiesto)
    with pytest.raises(OSError):
        A.publicar(destino, _cuerpo_capa2(), simbolo="LIT", fecha="2026-03-06",
                   capa="capa2", carril_usado=CA.PRINTS_LIGHTER)
    assert not os.path.exists(destino), "el npz canonico NO puede existir si el manifiesto no se publico"


def test_el_npz_canonico_aparece_SOLO_con_su_manifiesto(tmp_path):
    """Control de no-trivialidad del test de arriba: sin crash, publican los dos."""
    import analysis.artefacto as A
    destino = str(tmp_path / "LIT_2026-03-06.npz")
    A.publicar(destino, _cuerpo_capa2(), simbolo="LIT", fecha="2026-03-06",
               capa="capa2", carril_usado=CA.PRINTS_LIGHTER)
    assert os.path.exists(destino) and os.path.exists(A.ruta_manifiesto(destino))
    assert not os.path.exists(destino + ".enpublicacion")


# ============================================================ la herramienta conservada: rc y bloqueo

# Pruebas de carril conservadas literalmente desde test_eco_procedencia.

def test_el_escape_NO_deja_escribir_en_el_directorio_CANONICO(tmp_path, monkeypatch):
    """La v1 dejaba pasar aquí prometiendo una marca que, para quien no publica por la primitiva, no
    se escribía en ninguna parte. Un escape que hay que dejar puesto no es un escape: es la puerta
    principal."""
    canon = str(tmp_path / "blocks_lit")
    monkeypatch.setenv(CA.VAR_ESCAPE, "1")
    with pytest.raises(CA.CarrilNoConforme, match="NO sirve aquí"):
        CA.exigir_produccion("LIT", "eco", CA.TRADE_BINANCE, canon, canon)

def test_FUERA_del_canonico_una_reproduccion_forense_sigue_siendo_posible(tmp_path, monkeypatch):
    """No se cierra la puerta a reproducir: se cierra a reproducir DENTRO del sitio bueno."""
    monkeypatch.setenv(CA.VAR_ESCAPE, "1")
    CA.exigir_produccion("LIT", "eco", CA.TRADE_BINANCE,
                         str(tmp_path / "forense"), str(tmp_path / "blocks_lit"))

def test_sin_escape_tampoco_se_escribe_en_el_canonico(tmp_path, monkeypatch):
    canon = str(tmp_path / "blocks_lit")
    monkeypatch.delenv(CA.VAR_ESCAPE, raising=False)
    with pytest.raises(CA.CarrilNoConforme):
        CA.exigir_produccion("LIT", "eco", CA.TRADE_BINANCE, canon, canon)

def test_un_carril_CONFORME_entra_en_el_canonico_sin_ruido(tmp_path):
    """Control de no-trivialidad de la compuerta."""
    canon = str(tmp_path / "blocks_wti")
    CA.exigir_produccion("WTI", "eco", CA.PRINTS_LIGHTER, canon, canon)

def test_P0_2_la_compuerta_NO_depende_del_directorio_desde_el_que_se_lance(tmp_path, monkeypatch):
    """EL defecto. Todos los OUT_DIR_CANONICO del programa son RELATIVOS y `realpath` resuelve lo
    relativo contra el cwd: ejecutando desde otro sitio, el canonico apuntaba a la nada, el destino
    absoluto no caia dentro, y la compuerta AUTORIZABA un carril no conforme sobre el directorio
    oficial. Una defensa que depende de desde donde se lanza el proceso falla ABIERTA y en silencio."""
    canon_rel = os.path.join("data_hist", "eco_b", "blocks_lit")
    destino_abs = os.path.join(CA._QS, canon_rel)
    for cwd in (CA._QS, str(tmp_path), os.path.dirname(CA._QS)):
        monkeypatch.chdir(cwd)
        with pytest.raises(CA.CarrilNoConforme, match="mid_binance"):
            CA.exigir_produccion("LIT", "eco", CA.TRADE_BINANCE, destino_abs, canon_rel)

def test_P0_2_una_ruta_FUERA_del_canonico_sigue_permitida_desde_cualquier_cwd(tmp_path, monkeypatch):
    """Control de no-trivialidad: el anclaje no puede convertir la compuerta en un «no» universal —
    reproducir en un temporal forense tiene que seguir siendo posible."""
    for cwd in (CA._QS, str(tmp_path)):
        monkeypatch.chdir(cwd)
        CA.exigir_produccion("LIT", "eco", CA.TRADE_BINANCE, str(tmp_path / "forense"),
                             os.path.join("data_hist", "eco_b", "blocks_lit"))

def test_P0_2_mayusculas_y_separadores_mixtos_no_abren_la_compuerta(monkeypatch):
    """En Windows el mismo directorio se escribe de varias formas. Sin normalizar, la comparacion
    falla ABIERTA. En POSIX `normcase` no hace nada, asi que esto no cambia lo que corre el CI."""
    monkeypatch.chdir(CA._QS)
    canon = os.path.join("data_hist", "eco_b", "blocks_lit")
    for variante in (canon.replace(os.sep, "/"), canon.upper() if os.name == "nt" else canon):
        with pytest.raises(CA.CarrilNoConforme):
            CA.exigir_produccion("LIT", "eco", CA.TRADE_BINANCE,
                                 os.path.join(CA._QS, variante), canon)
