"""EL ARTEFACTO ACREDITADO — los ataques de la mesa, convertidos en tests.

2ª reauditoría (2026-08-27). La mesa tumbó la acreditación de entonces REPRODUCIENDO dos ataques:

    marca {"conforme": true} + bytes arbitrarios                 → ACEPTADO
    marca trade_mas_cercano_binance + extra {"conforme": true}   → ACEPTADO

4ª reauditoría (2026-08-28) — P0-1. La versión que arreglaba aquello **seguía autenticándose a sí
misma**, un nivel más arriba: la conformidad se recalculaba, sí, pero contra la capa que el propio
manifiesto se atribuía. Un bloque legítimo de capa 2 trasplantado a confirmación entraba sin una
queja. Y peor —variante reproducida al verificar el dictamen—: bastaba **editar la palabra `capa`**
en el JSON, porque el SHA cubría el npz pero no el manifiesto.

Las dos veces el fallo fue el mismo: **el objeto auditado aportaba el criterio con el que se le
auditaba**. Aquí están los tres ataques y todo lo que hay que validar para que esto acredite algo.
"""
import io
import json
import os
import shutil
import sys

import numpy as np
import pytest

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QS)
from analysis import artefacto as AR                                   # noqa: E402
from analysis import carril as CA                                      # noqa: E402


# ===================================================== andamio
def cuerpo(capa, n=3, k=2):
    """Un contenido MÍNIMO pero VÁLIDO para la familia `capa`. Que exista este andamio es parte del
    punto: si construir un artefacto bien formado fuera difícil, el esquema estaría mal puesto."""
    mo = np.zeros((n, k), "float64")
    comun = {"mo": mo, "descartes": np.zeros((n, k), "int64")}
    if capa == "capa2":
        return dict(comun, lado=np.ones(n, "int8"), cota=np.zeros(n, "int8"),
                    through=np.zeros(n, "bool"), label=np.zeros(n, "int8"),
                    ts=np.arange(n, dtype="int64"), n_intervalos=np.int64(1),
                    n_invalidos=np.int64(0))
    if capa == "piloto":
        return dict(comun, tipo=np.zeros(n, "int8"), slow=np.zeros(n, "bool"),
                    is_bid=np.ones(n, "bool"), label=np.zeros(n, "int8"),
                    estrato=np.int8(0))
    if capa == "confirmacion":
        return dict(comun, tipo=np.zeros(n, "int8"), slow=np.zeros(n, "bool"),
                    is_bid=np.ones(n, "bool"), owner=np.zeros(n, "int64"),
                    vol20=np.zeros(n, "float64"), t_fill=np.arange(n, dtype="int64"),
                    thr_con_at=np.zeros(n, "bool"), amb=np.int64(0))
    raise AssertionError(capa)


def _publica_limpio(tmp_path, sym="LIT", day="2026-03-06", capa="capa2",
                    carril=CA.PRINTS_LIGHTER, arrays=None):
    destino = str(tmp_path / f"{sym}_{day}.npz")
    AR.publicar(destino, arrays if arrays is not None else cuerpo(capa), simbolo=sym, fecha=day,
                capa=capa, carril_usado=carril)
    return destino


def _reescribe_manifiesto(destino, **cambios):
    ruta = AR.ruta_manifiesto(destino)
    m = json.load(io.open(ruta, encoding="utf-8"))
    m.update(cambios)
    io.open(ruta, "w", encoding="utf-8", newline="\n").write(json.dumps(m, sort_keys=True))
    return m


# ============================================ P0-1 · EL ARTEFACTO NO PUEDE ELEGIR SU PROPIO EXAMEN
def test_P0_1_un_artefacto_de_CAPA2_no_se_acredita_como_CONFIRMACION(tmp_path):
    """EL ataque de la mesa, reproducido ejecutando: producción LEGÍTIMA de capa 2, trasplantada al
    directorio decisivo de confirmación. Antes entraba porque se le preguntaba si su carril era
    conforme *para capa 2*, que era la capa que él mismo declaraba."""
    origen, decisivo = tmp_path / "capa2", tmp_path / "confirm"
    origen.mkdir(); decisivo.mkdir()
    p = _publica_limpio(origen, capa="capa2", carril=CA.PRINTS_LIGHTER)
    q = str(decisivo / "LIT_2026-03-06.npz")
    shutil.move(p, q); shutil.move(AR.ruta_manifiesto(p), AR.ruta_manifiesto(q))

    z, man = AR.cargar(q, capa_esperada="capa2")           # como capa2 sigue siendo válido…
    assert man["no_acreditado"] is None
    with pytest.raises(AR.ArtefactoNoAcreditado, match="otra familia"):
        AR.cargar(q, capa_esperada="confirmacion")        # …pero el consumidor decisivo lo rechaza


def test_P0_1_editar_la_palabra_capa_en_el_JSON_ya_no_convierte_un_rechazo_en_aceptacion(tmp_path):
    """LA VARIANTE PEOR, que la mesa no llegó a nombrar: no hacía falta trasplantar nada. El SHA-256
    cubría los bytes del npz pero no el JSON que los acredita, así que UNA palabra cambiada volvía
    aceptable lo inaceptable."""
    p = _publica_limpio(tmp_path, sym="DOGE", day="2026-03-07", capa="confirmacion",
                        carril=CA.PRINTS_LIGHTER, arrays=cuerpo("confirmacion"))
    with pytest.raises(AR.ArtefactoNoAcreditado, match="carril"):
        AR.cargar(p, capa_esperada="confirmacion")        # correcto: DOGE en confirmación exige el mid
    _reescribe_manifiesto(p, capa="capa2")
    with pytest.raises(AR.ArtefactoNoAcreditado, match="otra familia"):
        AR.cargar(p, capa_esperada="confirmacion")        # sigue rechazado: lo esperado NO vive ahí


def test_P0_1_TODOS_los_campos_normativos_se_validan_por_separado(tmp_path):
    """POR QUE NO HAY un hash del propio manifiesto. Lo escribi, y el arnes de mutacion demostro
    que no acreditaba nada: su mutacion no mataba ningun test porque cada campo que cubria ya se
    valida aqui uno a uno. Un segundo mecanismo que no puede fallar solo es la duplicacion E-49.
    Este test fija esa propiedad: cambiar CUALQUIER campo normativo tiene su propio rechazo."""
    for campo, valor in (("esquema", 999), ("simbolo", "DOGE"), ("fecha", "2026-04-01"),
                         ("capa", "piloto"), ("carril_usado", CA.MID_BINANCE),
                         ("bytes", 1), ("sha256", "0" * 64)):
        d = tmp_path / campo
        d.mkdir()
        p = _publica_limpio(d, capa="capa2")
        _reescribe_manifiesto(p, **{campo: valor})
        with pytest.raises(AR.ArtefactoNoAcreditado):
            AR.cargar(p, capa_esperada="capa2")


def test_P0_1_cargar_EXIGE_la_capa_esperada_no_tiene_valor_por_defecto(tmp_path):
    """Si tuviera valor por defecto, los cinco consumidores habrían seguido igual y el arreglo sería
    decorativo. Sin él, cada llamante está OBLIGADO a declarar qué esperaba."""
    p = _publica_limpio(tmp_path)
    with pytest.raises(TypeError):
        AR.cargar(p)                                                       # noqa: intencionado


def test_P0_1_el_simbolo_esperado_tambien_se_puede_fijar(tmp_path):
    p = _publica_limpio(tmp_path, sym="LIT")
    with pytest.raises(AR.ArtefactoNoAcreditado, match="que espera"):
        AR.cargar(p, capa_esperada="capa2", simbolo_esperado="DOGE")


# ============================================ P0-1 · EL CONTENIDO, que antes no se miraba
def test_P0_1_un_npz_con_claves_inservibles_no_pasa(tmp_path):
    """La v1 aceptaba esto y el consumidor reventaba después con un KeyError — o, peor, no reventaba."""
    p = str(tmp_path / "LIT_2026-03-08.npz")
    with pytest.raises(AR.ArtefactoNoAcreditado, match="falta la clave"):
        AR.publicar(p, {"cualquier_cosa": np.array(["texto"]), "mo": np.zeros((0,), "int8")},
                    simbolo="LIT", fecha="2026-03-08", capa="capa2", carril_usado=CA.PRINTS_LIGHTER)


def test_P0_1_un_mo_que_no_es_de_coma_flotante_no_pasa(tmp_path):
    a = dict(cuerpo("capa2"), mo=np.zeros((3, 2), "int8"))
    with pytest.raises(AR.ArtefactoNoAcreditado, match="coma flotante"):
        AR.publicar(str(tmp_path / "LIT_2026-03-06.npz"), a, simbolo="LIT", fecha="2026-03-06",
                    capa="capa2", carril_usado=CA.PRINTS_LIGHTER)


def test_P0_1_UN_VECTOR_DESALINEADO_no_pasa(tmp_path):
    """El fallo más peligroso de todos porque es SILENCIOSO: si `lado` mide uno menos que `mo`, los
    estratos siguen calculándose y dejan de significar lo que dicen."""
    a = dict(cuerpo("capa2", n=5), lado=np.ones(4, "int8"))
    with pytest.raises(AR.ArtefactoNoAcreditado, match="desalineado"):
        AR.publicar(str(tmp_path / "LIT_2026-03-06.npz"), a, simbolo="LIT", fecha="2026-03-06",
                    capa="capa2", carril_usado=CA.PRINTS_LIGHTER)


def test_P0_1_el_contenido_se_valida_TAMBIEN_al_CARGAR(tmp_path):
    """Publicar y cargar son dos puertas distintas y las dos tienen que mirar. Un npz escrito
    por fuera de la primitiva —un runner viejo, una copia a mano— nunca pasa por la puerta de
    publicacion, asi que si solo mirara esa, el agujero seguiria abierto por el otro lado."""
    destino = str(tmp_path / "LIT_2026-03-06.npz")
    np.savez(destino, **dict(cuerpo("capa2", n=5), lado=np.ones(4, "int8")))
    _, man = AR.cargar(destino, capa_esperada="capa2", permitir_no_acreditado=True)
    assert any("desalineado" in x for x in man["no_acreditado"]), man["no_acreditado"]


def test_P0_1_el_esquema_se_comprueba_TAMBIEN_al_publicar(tmp_path):
    """Comprobarlo sólo al consumir deja llegar a disco un artefacto que ya costó su producción, y
    quien lo lea meses después no sabrá por qué está mal."""
    with pytest.raises(AR.ArtefactoNoAcreditado, match="NO SE PUBLICA"):
        AR.publicar(str(tmp_path / "LIT_2026-03-06.npz"), {"mo": np.zeros((2, 2))},
                    simbolo="LIT", fecha="2026-03-06", capa="capa2", carril_usado=CA.PRINTS_LIGHTER)
    assert not os.path.exists(str(tmp_path / "LIT_2026-03-06.npz")), "y no deja rastro"


def test_P0_1_una_capa_sin_esquema_declarado_no_se_publica(tmp_path):
    with pytest.raises(AR.ArtefactoNoAcreditado, match="sin esquema"):
        AR.publicar(str(tmp_path / "LIT_2026-03-06.npz"), cuerpo("capa2"), simbolo="LIT",
                    fecha="2026-03-06", capa="familia_inventada", carril_usado=CA.PRINTS_LIGHTER)


@pytest.mark.parametrize("capa", sorted(AR.FAMILIAS))
def test_P0_1_las_TRES_familias_publican_y_cargan_su_cuerpo_valido(tmp_path, capa):
    """Control de no-trivialidad del esquema: sin esto, todo lo de arriba lo cumpliría un validador
    que rechazara siempre — y habría roto producción en silencio."""
    carril = CA.exigido_para("LIT", capa)
    d = tmp_path / capa
    d.mkdir()
    p = _publica_limpio(d, capa=capa, carril=carril, arrays=cuerpo(capa))
    z, man = AR.cargar(p, capa_esperada=capa, simbolo_esperado="LIT")
    assert man["no_acreditado"] is None and z["mo"].shape == (3, 2)


# ===================================================== LOS DOS ATAQUES DE LA 2ª REAUDITORÍA
def test_ATAQUE_1_manifiesto_fabricado_con_bytes_arbitrarios(tmp_path):
    destino = str(tmp_path / "LIT_2026-03-06.npz")
    np.savez(destino, **cuerpo("capa2"))
    io.open(AR.ruta_manifiesto(destino), "w", encoding="utf-8").write('{"conforme": true}')
    with pytest.raises(AR.ArtefactoNoAcreditado):
        AR.cargar(destino, capa_esperada="capa2")


def test_ATAQUE_2_extra_NO_puede_sobrescribir_la_conformidad(tmp_path):
    """EL agujero de la v1. `extra` vive bajo su propia clave y no puede tocar nada normativo — no por
    convenio, por construcción."""
    destino = str(tmp_path / "LIT_2026-03-06.npz")
    AR.publicar(destino, cuerpo("confirmacion"), simbolo="LIT", fecha="2026-03-06",
                capa="confirmacion", carril_usado=CA.TRADE_BINANCE,
                extra={"conforme": True, "carril_usado": CA.MID_BINANCE, "sha256": "0" * 64})
    m = json.load(io.open(AR.ruta_manifiesto(destino), encoding="utf-8"))
    assert m["carril_usado"] == CA.TRADE_BINANCE, "`extra` no puede pisar el carril declarado"
    assert m["sha256"] != "0" * 64, "`extra` no puede pisar el hash"
    assert m["extra"]["conforme"] is True, "lo que trae `extra` se guarda, pero BAJO SU CLAVE"
    with pytest.raises(AR.ArtefactoNoAcreditado, match="carril"):
        AR.cargar(destino, capa_esperada="confirmacion")


def test_la_conformidad_se_RECALCULA_y_el_campo_del_json_se_IGNORA(tmp_path):
    destino = _publica_limpio(tmp_path, capa="confirmacion", carril=CA.TRADE_BINANCE,
                              arrays=cuerpo("confirmacion"))
    _reescribe_manifiesto(destino, conforme=True)
    with pytest.raises(AR.ArtefactoNoAcreditado, match="carril"):
        AR.cargar(destino, capa_esperada="confirmacion")


# ===================================================== la ligadura con LOS BYTES
def test_un_npz_SUSTITUIDO_tras_publicarse_no_se_consume(tmp_path):
    destino = _publica_limpio(tmp_path)
    np.savez(destino, **cuerpo("capa2", n=9))                 # mismas claves, OTROS bytes
    with pytest.raises(AR.ArtefactoNoAcreditado, match="SHA-256"):
        AR.cargar(destino, capa_esperada="capa2")


def test_una_sustitucion_del_MISMO_TAMANO_solo_la_atrapa_el_SHA(tmp_path):
    """El test de arriba lo atrapa TAMBIÉN el tamaño, así que no acredita el hash por sí solo. Con
    idénticas claves, formas y dtypes los bytes miden lo mismo: aquí la única defensa en pie es el
    SHA-256. Lo destapó el arnés de mutación (E-62)."""
    destino = _publica_limpio(tmp_path)
    n = os.path.getsize(destino)
    with io.open(destino, "wb") as fh:
        np.savez(fh, **dict(cuerpo("capa2"), mo=np.ones((3, 2), "float64")))
    assert os.path.getsize(destino) == n, "el control exige MISMO tamaño"
    with pytest.raises(AR.ArtefactoNoAcreditado, match="SHA-256"):
        AR.cargar(destino, capa_esperada="capa2")


def test_un_manifiesto_con_TAMANO_mentido_no_se_consume(tmp_path):
    destino = _publica_limpio(tmp_path)
    _reescribe_manifiesto(destino, bytes=1)
    with pytest.raises(AR.ArtefactoNoAcreditado, match="tamaño"):
        AR.cargar(destino, capa_esperada="capa2")


def test_el_manifiesto_de_OTRO_dia_no_acredita_este(tmp_path):
    destino = _publica_limpio(tmp_path, day="2026-03-06")
    _reescribe_manifiesto(destino, fecha="2026-04-01")
    with pytest.raises(AR.ArtefactoNoAcreditado, match="fecha"):
        AR.cargar(destino, capa_esperada="capa2")


def test_el_manifiesto_de_OTRO_simbolo_tampoco(tmp_path):
    destino = _publica_limpio(tmp_path, sym="LIT")
    _reescribe_manifiesto(destino, simbolo="DOGE")
    with pytest.raises(AR.ArtefactoNoAcreditado, match="símbolo|carril"):
        AR.cargar(destino, capa_esperada="capa2")


@pytest.mark.parametrize("campo", ["simbolo", "fecha", "capa", "carril_usado", "sha256"])
def test_un_campo_normativo_AUSENTE_invalida(tmp_path, campo):
    destino = _publica_limpio(tmp_path)
    ruta = AR.ruta_manifiesto(destino)
    m = json.load(io.open(ruta, encoding="utf-8"))
    del m[campo]
    io.open(ruta, "w", encoding="utf-8", newline="\n").write(json.dumps(m, sort_keys=True))
    with pytest.raises(AR.ArtefactoNoAcreditado):
        AR.cargar(destino, capa_esperada="capa2")


def test_un_ESQUEMA_desconocido_invalida(tmp_path):
    destino = _publica_limpio(tmp_path)
    _reescribe_manifiesto(destino, esquema=999)
    with pytest.raises(AR.ArtefactoNoAcreditado, match="esquema"):
        AR.cargar(destino, capa_esperada="capa2")


def test_manifiesto_ILEGIBLE_cuenta_como_ausente(tmp_path):
    destino = _publica_limpio(tmp_path)
    io.open(AR.ruta_manifiesto(destino), "w", encoding="utf-8").write("{no es json")
    with pytest.raises(AR.ArtefactoNoAcreditado, match="no hay manifiesto"):
        AR.cargar(destino, capa_esperada="capa2")


# ===================================================== controles de NO trivialidad
def test_un_artefacto_BIEN_publicado_SI_se_carga(tmp_path):
    """Sin esto, todo lo de arriba lo cumpliría un cargador que rechazara siempre."""
    a = dict(cuerpo("capa2"), mo=np.arange(6.0).reshape(3, 2))
    destino = _publica_limpio(tmp_path, arrays=a)
    z, man = AR.cargar(destino, capa_esperada="capa2", simbolo_esperado="LIT")
    assert np.array_equal(z["mo"], np.arange(6.0).reshape(3, 2))
    assert man["simbolo"] == "LIT" and man["capa"] == "capa2" and man["no_acreditado"] is None


def test_los_bytes_del_npz_son_los_de_np_savez(tmp_path):
    """La identidad-byte de M-10 depende de esto: publicar por la primitiva no puede cambiar el
    contenido del npz respecto de `np.savez(destino, **arrays)`."""
    arrays = cuerpo("capa2")
    a = str(tmp_path / "LIT_2026-03-06.npz")
    AR.publicar(a, arrays, simbolo="LIT", fecha="2026-03-06", capa="capa2",
                carril_usado=CA.PRINTS_LIGHTER)
    b = str(tmp_path / "directo.npz")
    with io.open(b, "wb") as fh:
        np.savez(fh, **arrays)
    assert io.open(a, "rb").read() == io.open(b, "rb").read()


def test_el_escape_forense_devuelve_los_MOTIVOS_a_la_vista(tmp_path):
    destino = _publica_limpio(tmp_path, capa="confirmacion", carril=CA.TRADE_BINANCE,
                              arrays=cuerpo("confirmacion"))
    z, man = AR.cargar(destino, capa_esperada="confirmacion", permitir_no_acreditado=True)
    assert z is not None
    assert man["no_acreditado"] and any("carril" in m for m in man["no_acreditado"])


def test_se_reportan_TODOS_los_motivos_no_solo_el_primero(tmp_path):
    destino = _publica_limpio(tmp_path)
    _reescribe_manifiesto(destino, bytes=1, fecha="2026-04-01")
    _, man = AR.cargar(destino, capa_esperada="capa2", permitir_no_acreditado=True)
    assert len(man["no_acreditado"]) >= 2
