"""Pruebas conservadas de ref_valida: clases, banda y R4. Solo datos sintéticos.

Las pruebas exclusivas de los productores retirados permanecen en e1c2757.
"""
import os
import sys
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis import ref_valida as RV

@pytest.mark.parametrize("ref,clase", [
    (float("nan"), "no_finita"), (float("inf"), "no_finita"), (float("-inf"), "no_finita"),
    (0.0, "no_positiva"), (-0.0, "no_positiva"), (-1.0, "no_positiva"), (-100.0, "no_positiva"),
    (1e-9, "degenerada"), (1e-300, "degenerada"), (1e6, "degenerada"),
    (101.0, "ok"), (100.0, "ok"), (99.0, "ok"),
])
def test_clasificar_asigna_la_clase_correcta(ref, clase):
    """El ORDEN de comprobación importa: un NaN tiene que salir `no_finita`, no `degenerada`, o el
    diagnóstico del incidente diría lo que no es."""
    assert RV.clasificar(ref, 100.0) == clase


@pytest.mark.parametrize("ratio,ok", [
    (0.1, False), (1.9, False),                      # los bordes EXACTOS ya valen ±9.000 bps: fuera
    (0.1000001, True), (1.8999999, True),            # justo dentro, sí
    (0.5, True), (1.5, True),
    (2.0, False), (10.0, False),                     # +10.000 y +90.000 bps: no son markouts
])
def test_los_bordes_de_la_banda_son_los_declarados(ratio, ok):
    """La banda se DERIVA del límite de 9.000 bps y es ABIERTA: en el borde exacto el markout ya vale
    ±9.000, que es el límite de lo absurdo, no un valor aceptable.

    La primera versión fijó la banda a mano en [0,1 ; 10] afirmando que fuera de ella
    `|markout| ≥ 9.000`. **Era falso por arriba**: ratio 10 da +90.000 bps. La regla toleraba
    markouts diez veces más absurdos en un sentido que en el otro. Lo cazó el falsificador por
    propiedades con `ref = 45,68 · px = 6,13` (E-51); ningún ejemplo escrito a mano lo miraba."""
    assert (RV.clasificar(100.0 * ratio, 100.0) == "ok") is ok


@pytest.mark.parametrize("bps", [1.0, 100.0, 5_000.0, 8_999.0, 9_001.0, 9_999.0])
def test_la_banda_es_SIMETRICA_en_consecuencia(bps):
    """El mismo |markout| a cada lado recibe la MISMA clase. Es lo que garantiza decidir sobre el
    markout en vez de sobre un ratio: `1.0 - 0.9` no vale `0.1` en float64, y con dos constantes
    derivadas el borde de abajo quedaba dentro y el de arriba fuera.

    El rango llega hasta 9.999 y no más: **por encima de 10.000 bps el precio de abajo se vuelve
    NEGATIVO**, y ahí la clase correcta ya no es `degenerada` sino `no_positiva` — no es asimetría,
    es que un precio negativo no es un precio. Ese caso lo cubre el test de abajo."""
    arriba = RV.clasificar(100.0 * (1.0 + bps / 1e4), 100.0)
    abajo = RV.clasificar(100.0 * (1.0 - bps / 1e4), 100.0)
    assert arriba == abajo, f"a {bps} bps: arriba «{arriba}» y abajo «{abajo}»"


def test_por_debajo_de_menos_10000_bps_el_precio_es_NEGATIVO_y_esa_es_la_clase():
    """Frontera del dominio, fijada a propósito: un markout de −10.000 bps significa `ref = 0` y por
    debajo significa `ref < 0`. La clase deja de ser `degenerada` y pasa a `no_positiva`, que es más
    informativa. Se fija para que nadie lo «arregle» pensando que es una asimetría."""
    assert RV.clasificar(100.0 * (1.0 - 1.2), 100.0) == "no_positiva"
    assert RV.clasificar(100.0 * (1.0 + 1.2), 100.0) == "degenerada"
    assert RV.clasificar(0.0, 100.0) == "no_positiva"


def test_la_banda_NO_es_un_filtro_de_plausibilidad_economica():
    """Un movimiento del 30 % es enorme para un perp y DEBE pasar: la banda no opina de mercados.
    Si alguien la estrechara a 5 % o 20 % tendría un filtro post-dato capaz de mover resultados."""
    assert RV.clasificar(130.0, 100.0) == "ok"
    assert RV.clasificar(70.0, 100.0) == "ok"


def test_R4_no_dice_nada_cuando_no_hay_rechazos():
    cnt = RV.contadores_vacios(1)
    assert RV.linea_r4(cnt, 100, 0, 5_000) is None


def test_R4_avisa_por_debajo_del_umbral_y_GRITA_por_encima():
    cnt = RV.contadores_vacios(1)
    cnt["ref_no_positiva"][0] = 1
    assert "[R1]" in RV.linea_r4(cnt, 1000, 0, 5_000)          # 0,1 % -> aviso normal
    cnt["ref_no_positiva"][0] = 60
    assert "[R4] ANOMALÍA" in RV.linea_r4(cnt, 1000, 0, 5_000)  # 6 % -> anomalía


def test_R4_cuenta_LAS_TRES_clases_no_solo_una():
    """La v1 contaba sólo `ref_invalida`. Con tres clases, sumar una sola subestimaría el incidente."""
    cnt = RV.contadores_vacios(1)
    cnt["ref_no_finita"][0] = 20
    cnt["ref_no_positiva"][0] = 20
    cnt["ref_degenerada"][0] = 20
    assert RV.total_rechazos_ref(cnt, 0) == 60
    assert "[R4] ANOMALÍA" in RV.linea_r4(cnt, 1000, 0, 5_000)


@pytest.mark.parametrize("n_ref,n,esperado", [(50, 1000, "[R1]"), (51, 1000, "[R4]"),
                                              (5, 100, "[R1]"), (6, 100, "[R4]")])
def test_R4_la_frontera_del_umbral_es_ESTRICTA_al_5_por_ciento(n_ref, n, esperado):
    cnt = RV.contadores_vacios(1)
    cnt["ref_degenerada"][0] = n_ref
    assert esperado in RV.linea_r4(cnt, n, 0, 5_000)

