"""EL CENSO DE COMPLETITUD, ACREDITADO. Hasta hoy no tenía una sola prueba (mesa, 2026-08-28).

Y esa era, de sus seis objeciones, la única que importaba de verdad: un guardia que no corre en
ningún sitio no tiene poder de veto, así que sus puntos ciegos no «dejaban pasar» nada — no había
compuerta. Las otras cinco son puntos ciegos de algo que no vigilaba.

Los casos se montan sobre ÁRBOLES SINTÉTICOS en un temporal, con las tablas del censo sustituidas:
así cada test fija UNA propiedad del censo en vez de depender de cómo esté el repo hoy — que es lo
que haría que el test cambiase de significado cada vez que alguien añade un fichero.
"""
import hashlib
import io
import os
import sys

import pytest

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(QS, "tools"))
import guardia_completitud as G                                       # noqa: E402


@pytest.fixture
def arbol(tmp_path, monkeypatch):
    """Un `analysis/` y un `tools/` sintéticos, y el censo apuntando a ellos."""
    for paq in ("analysis", "tools"):
        (tmp_path / paq).mkdir()
    monkeypatch.setattr(G, "QS", str(tmp_path))
    monkeypatch.setattr(G, "EXCLUSIVAS", (
        ("np.load", ("analysis/cargador.py",), "motivo de carga"),
        ("np.savez", ("analysis/cargador.py",), "motivo de escritura"),
    ))
    monkeypatch.setattr(G, "EXENTAS", {})
    monkeypatch.setattr(G, "EXCLUSIVIDAD_SELLADAS", {})
    monkeypatch.setattr(G, "DOMINANCIA_SELLADAS", {})
    monkeypatch.setattr(G, "DOMINANCIA", (("publicar", "exigir_produccion", "motivo"),))
    return tmp_path


def escribe(arbol, rel, fuente):
    io.open(str(arbol / rel), "w", encoding="utf-8", newline="\n").write(fuente)


# ═══════════════════════════════════ (c) AST, NO TEXTO — en las DOS direcciones
def test_un_np_load_en_un_COMENTARIO_no_es_una_llamada(arbol):
    """Falso POSITIVO de la v1. Y no es hipotético: `cryptohft_adapter.py` estaba EXIMIDO del censo
    sin tener una sola llamada — la exención era fantasma, inventada por una coincidencia de texto."""
    escribe(arbol, "analysis/x.py", "# aqui NO usamos np.load\nTEXTO = 'np.load'\n")
    assert G.comprobar_exclusividad()[0] == []


@pytest.mark.parametrize("fuente,como", [
    ("import numpy as np\ndef f():\n    return np.load('a')\n", "alias np"),
    ("import numpy\ndef f():\n    return numpy.load('a')\n", "sin alias"),
    ("import numpy as onp\ndef f():\n    return onp.load('a')\n", "otro alias"),
    ("from numpy import load\ndef f():\n    return load('a')\n", "import directo"),
    ("from numpy import load as L\ndef f():\n    return L('a')\n", "import renombrado"),
], ids=["alias_np", "sin_alias", "otro_alias", "import_directo", "import_renombrado"])
def test_una_llamada_REAL_se_ve_escrita_como_se_escriba(arbol, fuente, como):
    """Falso NEGATIVO de la v1. `if 'np.load' not in fuente` sólo ve una de estas cinco formas."""
    escribe(arbol, "analysis/x.py", fuente)
    problemas, _ = G.comprobar_exclusividad()
    assert len(problemas) == 1, f"la forma «{como}» tiene que verse"


def test_el_cargador_puede_usar_la_operacion_que_encapsula(arbol):
    """Control de no-trivialidad: sin esto, todo lo anterior lo cumpliría un censo que grita siempre."""
    escribe(arbol, "analysis/cargador.py", "import numpy as np\ndef cargar(p):\n    return np.load(p)\n")
    assert G.comprobar_exclusividad()[0] == []


# ═══════════════════════════════════ (b) tools/ TAMBIÉN
def test_una_carga_bajo_tools_ya_no_es_invisible(arbol):
    """La v1 sólo miraba `analysis/*.py`. En el repo real había SEIS llamadas bajo `tools/`."""
    escribe(arbol, "tools/h.py", "import numpy as np\ndef f():\n    return np.load('a')\n")
    problemas, _ = G.comprobar_exclusividad()
    assert len(problemas) == 1 and problemas[0].startswith("tools/h.py::f::np.load")


def test_el_glob_ve_LOS_DOS_NIVELES(arbol):
    """Mi primera versión de este test sólo ponía un fichero ANIDADO, y con `recursive=False` el
    patrón `**` degenera en `*`: encuentra el anidado y pierde el de nivel superior — justo al revés
    de lo que yo asumí. Es decir, el test pasaba con la comprobación rota, que es exactamente el modo
    de fallo que este censo persigue. Lo destapó el arnés de mutación declarándolo VACUO."""
    (arbol / "analysis" / "sub").mkdir()
    escribe(arbol, "analysis/arriba.py", "import numpy as np\ndef f():\n    return np.load('a')\n")
    escribe(arbol, "analysis/sub/z.py", "import numpy as np\ndef g():\n    return np.load('a')\n")
    problemas, _ = G.comprobar_exclusividad()
    assert len(problemas) == 2, f"los DOS niveles: {problemas}"


# ═══════════════════════════════════ (f) los ESCRITORES, que no se miraban
def test_un_np_savez_fuera_del_publicador_se_ve(arbol):
    """Sólo se vigilaba `np.load`, así que los seis escritores que dejan un npz SIN manifiesto eran
    invisibles — y ahí vivía el agujero del eco."""
    escribe(arbol, "analysis/w.py", "import numpy as np\ndef f():\n    np.savez('a', x=1)\n")
    problemas, _ = G.comprobar_exclusividad()
    assert len(problemas) == 1 and "np.savez" in problemas[0]


# ═══════════════════════════════════ (d) exenciones POR CALLSITE, no por fichero
def test_la_exencion_es_por_FUNCION_no_por_fichero(arbol, monkeypatch):
    """Eximir el fichero eximía sus llamadas de hoy Y las que se añadieran mañana, en silencio."""
    escribe(arbol, "analysis/x.py",
            "import numpy as np\n"
            "def eximida():\n    return np.load('a')\n"
            "def NO_eximida():\n    return np.load('b')\n")
    monkeypatch.setattr(G, "EXENTAS", {"analysis/x.py::eximida::np.load": (1, "declarada")})
    problemas, _ = G.comprobar_exclusividad()
    assert len(problemas) == 1 and "NO_eximida" in problemas[0]


def test_una_SEGUNDA_llamada_en_una_funcion_eximida_rompe_el_build(arbol, monkeypatch):
    """El número esperado está a propósito: una exención no se hereda."""
    escribe(arbol, "analysis/x.py",
            "import numpy as np\ndef f():\n    np.load('a')\n    return np.load('b')\n")
    monkeypatch.setattr(G, "EXENTAS", {"analysis/x.py::f::np.load": (1, "declarada")})
    problemas, _ = G.comprobar_exclusividad()
    assert len(problemas) == 1 and "declara 1 llamada(s) y hay 2" in problemas[0]


def test_una_exencion_FANTASMA_se_denuncia(arbol, monkeypatch):
    """La v1 tenía una. Una exención que no cubre nada hoy cubriría en silencio lo que aparezca."""
    monkeypatch.setattr(G, "EXENTAS", {"analysis/no_existe.py::f::np.load": (1, "fantasma")})
    problemas, _ = G.comprobar_exclusividad()
    assert len(problemas) == 1 and "FANTASMA" in problemas[0]


def test_una_exencion_con_el_numero_correcto_pasa(arbol, monkeypatch):
    escribe(arbol, "analysis/x.py", "import numpy as np\ndef f():\n    return np.load('a')\n")
    monkeypatch.setattr(G, "EXENTAS", {"analysis/x.py::f::np.load": (1, "declarada")})
    assert G.comprobar_exclusividad()[0] == []


# ═══════════════════════════════════ (e) DOMINANCIA, no mera presencia
DOMINA = """
def produce():
    exigir_produccion('LIT')
    publicar('x')
"""
DOMINA_EN_BUCLE = """
def produce():
    for s in SYMS:
        exigir_produccion(s)
    for s in SYMS:
        publicar(s)
"""
NO_DOMINA_OTRA_FUNCION = """
def compuerta():
    exigir_produccion('LIT')

def produce():
    publicar('x')
"""
NO_DOMINA_EN_RAMA = """
def produce():
    if cond:
        exigir_produccion('LIT')
    publicar('x')
"""
NO_DOMINA_DESPUES = """
def produce():
    publicar('x')
    exigir_produccion('LIT')
"""
NO_DOMINA_EN_TRY = """
def produce():
    try:
        exigir_produccion('LIT')
    except Exception:
        pass
    publicar('x')
"""


@pytest.mark.parametrize("fuente", [DOMINA, DOMINA_EN_BUCLE],
                         ids=["antes_en_la_misma_funcion", "en_bucle_sobre_los_simbolos"])
def test_la_compuerta_que_SI_domina(arbol, fuente):
    """`for` no es una rama: compuertar en bucle sobre todos los símbolos ANTES del bucle de
    producción es el patrón CORRECTO. Mi primera regla lo marcaba, y era la regla la que estaba mal."""
    escribe(arbol, "analysis/p.py", fuente)
    assert G.comprobar_dominancia()[0] == []


@pytest.mark.parametrize("fuente,por_que", [
    (NO_DOMINA_OTRA_FUNCION, "el modulo la NOMBRA pero no gobierna nada"),
    (NO_DOMINA_EN_RAMA, "una rama puede no tomarse"),
    (NO_DOMINA_DESPUES, "despues de publicar ya se ha gastado"),
    (NO_DOMINA_EN_TRY, "un except se la traga — que es como P0-2 dejo pasar el rechazo"),
], ids=["en_otra_funcion", "en_una_rama", "despues_de_publicar", "dentro_de_un_try"])
def test_la_compuerta_que_NO_domina(arbol, fuente, por_que):
    escribe(arbol, "analysis/p.py", fuente)
    problemas, _ = G.comprobar_dominancia()
    assert len(problemas) == 1, por_que


# ═══════════════════════════════════ el censo sobre el REPO REAL
@pytest.fixture(params=["np.load", "np.savez", "publicar"])
def sellada(arbol, monkeypatch, request):
    op = request.param
    source = ("import numpy as np\nraise AssertionError('NO_IMPORTAR_INSTRUMENTO')\n"
              f"def f():\n    {op}('a')\n")
    rel = "tools/cerrado.py"
    key = f"{rel}::f::{op}"
    table = {key: (1, hashlib.sha256(source.encode()).hexdigest(), "auditoría sintética")}
    name = "DOMINANCIA_SELLADAS" if op == "publicar" else "EXCLUSIVIDAD_SELLADAS"
    monkeypatch.setattr(G, name, table)
    escribe(arbol, rel, source)
    check = G.comprobar_dominancia if op == "publicar" else G.comprobar_exclusividad
    return rel, key, op, source, table, check


def test_sellada_cubre_solo_bytes_auditados_sin_importar(sellada):
    *_, check = sellada
    problems, notes = check(verboso=True)
    assert problems == []
    assert any("EXENTA SELLADA" in note for note in notes)


def _comprobar_cambio_sellado(arbol, sellada, change):
    rel, key, op, source, table, check = sellada
    if change == "body":
        escribe(arbol, rel, source + "# edición posterior\n")
        expected = "SHA-256 distinto"
    elif change == "newlines":
        (arbol / rel).write_bytes(source.replace("\n", "\r\n").encode())
        expected = "SHA-256 distinto"
    elif change == "second_call":
        source += f"    {op}('b')\n"
        escribe(arbol, rel, source)
        # Mantener válido el hash aísla la protección independiente del recuento.
        table[key] = (1, hashlib.sha256(source.encode()).hexdigest(), "sintética")
        expected = "declara 1 llamada(s) y hay 2"
    elif change == "missing":
        (arbol / rel).unlink()
        expected = "FANTASMA"
    elif change == "another_function":
        source += f"def otra():\n    {op}('b')\n"
        escribe(arbol, rel, source)
        table[key] = (1, hashlib.sha256(source.encode()).hexdigest(), "sintética")
        expected = "otra"
    else:
        escribe(arbol, "tools/futuro.py", source)
        expected = "tools/futuro.py"
    problems, _ = check()
    assert any(expected in p for p in problems), f"[SELLADA-{change}] {problems}"


# Nombres separados: el arnés exige que caiga CADA causa declarada. Agruparlas en
# parámetros de una sola función solo le permitiría exigir la primera que fallara.
def test_sellada_rechaza_edicion_del_cuerpo(arbol, sellada):
    _comprobar_cambio_sellado(arbol, sellada, "body")


def test_sellada_rechaza_cambio_de_saltos_de_linea(arbol, sellada):
    _comprobar_cambio_sellado(arbol, sellada, "newlines")


def test_sellada_rechaza_segunda_llamada_con_hash_valido(arbol, sellada):
    _comprobar_cambio_sellado(arbol, sellada, "second_call")


def test_sellada_denuncia_excepcion_fantasma(arbol, sellada):
    _comprobar_cambio_sellado(arbol, sellada, "missing")


def test_sellada_no_exime_otra_funcion(arbol, sellada):
    _comprobar_cambio_sellado(arbol, sellada, "another_function")


def test_sellada_no_exime_otro_archivo(arbol, sellada):
    _comprobar_cambio_sellado(arbol, sellada, "another_file")


def test_sobre_el_repo_real_el_censo_esta_VERDE():
    """No es redundante con el CI: si alguien abre una ruta, este test lo dice en la suite —donde se
    mira— y no sólo en el job del guardia."""
    assert G.comprobar_exclusividad()[0] == []
    assert G.comprobar_dominancia()[0] == []


def test_sobre_el_repo_real_hay_llamadas_vigiladas_de_verdad():
    """Sin esto, el test de arriba lo cumpliría un censo que no encuentra NADA — que es exactamente
    el modo de fallo de la v1 bajo `tools/`."""
    # V2 lote 3: quedan los dos sitios de artefacto; las excepciones históricas salen.
    # Inventario independiente de EXENTAS y del censo:
    # si desaparece un sitio conservado debe fallar aunque aparezcan otros que lo compensen.
    esperados = {
        "analysis/artefacto.py::cargar::np.load",
        "analysis/artefacto.py::publicar::np.savez",
    }
    vistos = {sitio for rel, src in G.modulos() for sitio, *_ in G.censo(rel, src)}
    faltan = esperados - vistos
    assert not faltan, f"llamadas vigiladas que el censo no ve: {sorted(faltan)}"
