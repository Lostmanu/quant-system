"""LA GUARDIA DOCUMENTAL, ACREDITADA. Hasta hoy no tenía un solo test (mesa, 2026-08-27, P0-5).

Una guardia sin tests es exactamente el objeto que este proyecto ya catalogó dos veces: algo que se
cree activo, que nadie vuelve a mirar, y que lleva meses sin morder. Peor aún en este caso, porque su
veredicto es binario y silencioso — cuando dice OK, nadie mira por qué.

Los casos se montan sobre REPOSITORIOS GIT DE VERDAD en un temporal. No hay dobles: la comprobación
que aquí importa es de ANCESTRÍA, y el caso que destapó el fallo-abierto —dos commits HERMANOS en
ramas divergentes— no se puede simular con un mock sin dar por supuesto justo lo que se mide.
"""
import io
import json
import os
import subprocess
import sys

import pytest

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(QS, "tools"))
import guardia_documental as G                                        # noqa: E402


# ===================================================== andamio: un repo git minúsculo
def _git(repo, *args, **kw):
    entorno = dict(os.environ)
    if kw.get("fecha"):                      # para construir un DAG con FECHAS SESGADAS (P0-7)
        entorno["GIT_AUTHOR_DATE"] = entorno["GIT_COMMITTER_DATE"] = kw["fecha"]
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=repo,
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=entorno)
    if kw.get("exigir", True) and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr}")
    return r.stdout.strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """Un repo con `docs/` y `quant-system-ingesta/qs/`, y la guardia apuntando a él."""
    raiz = tmp_path / "repo"
    (raiz / "docs").mkdir(parents=True)
    qs = raiz / "quant-system-ingesta" / "qs" / "analysis"
    qs.mkdir(parents=True)
    _git(str(raiz), "init", "-q", "-b", "main")
    (raiz / "semilla.txt").write_text("1\n", encoding="utf-8")
    _git(str(raiz), "add", "semilla.txt")
    _git(str(raiz), "commit", "-q", "-m", "semilla")
    monkeypatch.setattr(G, "RAIZ", str(raiz))
    monkeypatch.setattr(G, "DOCS", str(raiz / "docs"))
    monkeypatch.setattr(G, "QS", str(raiz / "quant-system-ingesta" / "qs"))
    monkeypatch.setattr(G, "EXIMIDOS", frozenset())
    return raiz


def _escribe(repo, rel, texto):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    io.open(str(p), "w", encoding="utf-8", newline="\n").write(texto)


def _commit(repo, rel, texto, mensaje, fecha=None):
    _escribe(repo, rel, texto)
    _git(str(repo), "add", "--", rel)
    _git(str(repo), "commit", "-q", "-m", mensaje, fecha=fecha)
    return _git(str(repo), "rev-parse", "HEAD")


PREREG = ("# Prerregistro\n\n<!-- PRECEDE: quant-system-ingesta/qs/tools/sonda.py -->\n\n"
          "**C1** la primera regla.\n")


# ===================================================== A · CRONOLOGÍA
def test_el_prereg_ANTES_y_el_artefacto_DESPUES_es_correcto(repo):
    """Control de no-trivialidad: sin esto, todo lo demás lo cumpliría una guardia que grita siempre."""
    _commit(repo, "docs/PREREG_X.md", PREREG, "prereg")
    _commit(repo, "quant-system-ingesta/qs/tools/sonda.py", "x = 1\n", "artefacto")
    problemas, _ = G.comprobar_cronologia()
    assert problemas == []


def test_el_artefacto_ANTES_que_el_prereg_es_E42(repo):
    _commit(repo, "quant-system-ingesta/qs/tools/sonda.py", "x = 1\n", "artefacto")
    _commit(repo, "docs/PREREG_X.md", PREREG, "prereg")
    problemas, _ = G.comprobar_cronologia()
    assert len(problemas) == 1 and "E-42" in problemas[0]
    assert "ANCESTRO" in problemas[0], "debe decir POR QUÉ, no sólo que falla"


def test_EL_FALLO_ABIERTO_dos_commits_HERMANOS_no_establecen_precedencia(repo):
    """EL defecto que la mesa señaló. La versión anterior sólo descartaba la relación MALA
    (`artefacto es ancestro del prereg`); con dos ramas divergentes ninguno es ancestro del otro, así
    que caía en el `else` y la guardia daba el caso por BUENO sin que nadie hubiera establecido nada.

    Una guardia tiene que exigir la relación buena, no descartar la mala."""
    base = _git(str(repo), "rev-parse", "HEAD")
    _commit(repo, "docs/PREREG_X.md", PREREG, "prereg en main")
    _git(str(repo), "checkout", "-q", "-b", "otra", base)
    _commit(repo, "quant-system-ingesta/qs/tools/sonda.py", "x = 1\n", "artefacto en otra")
    _git(str(repo), "checkout", "-q", "main")
    _git(str(repo), "merge", "-q", "--no-ff", "otra", "-m", "merge")   # los dos visibles desde HEAD…
    problemas, _ = G.comprobar_cronologia()                            # …pero HERMANOS entre sí
    assert len(problemas) == 1, "la precedencia NO está establecida y no puede darse por buena"
    assert "HERMANAS" in problemas[0] and "E-42" in problemas[0]


def test_un_prereg_sin_PRECEDE_no_es_verificable(repo):
    _commit(repo, "docs/PREREG_X.md", "# sin declaración\n\n**C1** algo.\n", "prereg mudo")
    problemas, _ = G.comprobar_cronologia()
    assert len(problemas) == 1 and "PRECEDE" in problemas[0]


def test_el_artefacto_YA_en_el_arbol_con_el_prereg_sin_commitear(repo):
    _escribe(repo, "quant-system-ingesta/qs/tools/sonda.py", "x = 1\n")
    _escribe(repo, "docs/PREREG_X.md", PREREG)
    problemas, _ = G.comprobar_cronologia()
    assert len(problemas) == 1 and "AÚN NO" in problemas[0]


# ===================================================== el TEXTO, no el NOMBRE
def test_el_commit_del_TEXTO_VIGENTE_no_es_el_introductor(repo):
    """El caso real: `PREREG_SONDA_COBERTURA.md` nació en 546148e y sus reglas se reescribieron en
    807d0fe. Atarse al introductor certifica un texto que ya no rige."""
    a = _commit(repo, "docs/PREREG_X.md", "# v1\n\n**C1** vieja.\n", "v1")
    b = _commit(repo, "docs/PREREG_X.md", "# v2\n\n**C1** NUEVA.\n", "v2")
    commit, blob = G.commit_del_texto_vigente("docs/PREREG_X.md")
    assert commit == b and commit != a, "el sello debe apuntar al texto que RIGE"
    assert blob and len(blob) == 40


def test_un_artefacto_ENTRE_la_v1_y_las_reglas_vigentes_NO_pasa(repo):
    """E-42 por la puerta de atrás: el artefacto desciende del documento, pero es ANTERIOR a las
    reglas que dicen pre-registrarlo."""
    _commit(repo, "docs/PREREG_X.md", "# v1\n\n<!-- PRECEDE: quant-system-ingesta/qs/tools/sonda.py -->\n\n**C1** vieja.\n", "v1")
    _commit(repo, "quant-system-ingesta/qs/tools/sonda.py", "x = 1\n", "artefacto")
    _commit(repo, "docs/PREREG_X.md", PREREG, "reglas reescritas")
    problemas, _ = G.comprobar_cronologia()
    assert len(problemas) == 1 and "E-42" in problemas[0]


def test_editar_un_prereg_NO_pone_roja_la_guardia_pero_SI_bloquea_la_ejecucion(repo):
    """La separacion importa. Si tener el texto sin commitear pusiera rojo el chequeo general, la
    guardia estaria roja justo mientras se hace trabajo legitimo — el antipatron que su propia
    cabecera describe y que la desactivaria en una semana. Donde SI es un impedimento absoluto es
    antes de gastar creditos: ahi lo bloquea `exigir_cobertura`."""
    _commit(repo, "docs/PREREG_X.md", PREREG, "v1")
    _escribe(repo, "docs/PREREG_X.md", PREREG + "\n**C2** añadida sin commitear.\n")
    problemas, notas = G.comprobar_cronologia()
    assert problemas == [], "editar no puede poner rojo el build"
    assert any("no esta commiteado" in n.replace("á", "a") for n in notas), "pero SI se avisa"
    assert G.sello_normativo("docs/PREREG_X.md")["commiteado"] is False
    assert any("NO" in p for p in G.exigir_cobertura("PREREG_X.md")), "y ejecutar queda bloqueado"


def test_un_fichero_BORRADO_y_vuelto_a_anadir_no_esconde_su_adicion_original(repo):
    """`git log -1 --diff-filter=A` devuelve la adición MÁS RECIENTE. Con ella, un artefacto que
    estuvo delante desde el principio se presentaba como recién llegado."""
    primero = _commit(repo, "quant-system-ingesta/qs/tools/sonda.py", "x = 1\n", "artefacto v1")
    _git(str(repo), "rm", "-q", "--", "quant-system-ingesta/qs/tools/sonda.py")
    _git(str(repo), "commit", "-q", "-m", "borrado")
    _commit(repo, "quant-system-ingesta/qs/tools/sonda.py", "x = 2\n", "artefacto v2")
    assert G._commit_introductor("quant-system-ingesta/qs/tools/sonda.py") == primero


# ===================================================== B · SPEC vs CÓDIGO
IMPL_OK = ("# Prerregistro\n\n<!-- PRECEDE: quant-system-ingesta/qs/tools/sonda.py -->\n"
           "<!-- IDS-IMPLEMENTADOS: C1=analysis/mod.py:regla_uno -->\n\n**C1** la primera regla.\n")


def test_una_regla_que_dice_vivir_donde_NO_esta_es_E45(repo):
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py", "def otra_cosa():\n    pass\n")
    _escribe(repo, "docs/PREREG_X.md", IMPL_OK)
    problemas, _ = G.comprobar_spec_vs_codigo()
    assert len(problemas) == 1 and "E-45" in problemas[0]


def test_una_regla_bien_ligada_pasa(repo):
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py", "def regla_uno():\n    pass\n")
    _escribe(repo, "docs/PREREG_X.md", IMPL_OK)
    assert G.comprobar_spec_vs_codigo()[0] == []


def test_un_COMENTARIO_no_satisface_la_declaracion(repo):
    """La v1 buscaba el símbolo como TEXTO. Por AST, una mención no basta."""
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py", "# regla_uno vive aquí, de verdad\n")
    _escribe(repo, "docs/PREREG_X.md", IMPL_OK)
    assert len(G.comprobar_spec_vs_codigo()[0]) == 1


def test_declarar_implementado_un_id_que_no_es_regla_del_documento(repo):
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py", "def regla_uno():\n    pass\n")
    _escribe(repo, "docs/PREREG_X.md", IMPL_OK.replace("**C1** la primera regla.", "**C9** otra."))
    problemas, _ = G.comprobar_spec_vs_codigo()
    assert any("NO aparece" in p for p in problemas)


def test_la_prosa_que_MENCIONA_el_marcador_no_es_una_declaracion(repo):
    """E-52: la guardia se ponía roja con el documento que la explicaba."""
    _escribe(repo, "docs/PREREG_X.md", "<!-- IDS-IMPLEMENTADOS: …ver el formato arriba… -->\n"
                                       "**C1** algo.\n")
    assert G.comprobar_spec_vs_codigo()[0] == []


@pytest.mark.parametrize("ident", ["R1", "M2", "C3", "S4", "T5"])
def test_las_reglas_S_y_T_TAMBIEN_se_reconocen(repo, ident):
    """La sonda numera C0–C4, S1–S5 y T1–T3, y la expresión sólo aceptaba `[RMC]`: sus ocho reglas
    S/T eran invisibles para la guardia, que devolvía rc=0 sin haberlas mirado."""
    assert G._ID_REGLA.findall(f"**{ident}** una regla.") == [ident]


# ===================================================== BLOQUEO por cobertura (P0-5)
def test_exigir_cobertura_BLOQUEA_mientras_una_regla_no_tenga_codigo(repo):
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py", "def regla_uno():\n    pass\n")
    _commit(repo, "docs/PREREG_X.md", IMPL_OK + "\n**C2** la segunda, sin implementar.\n", "prereg")
    problemas = G.exigir_cobertura("PREREG_X.md")
    assert len(problemas) == 1 and "C2" in problemas[0]


def test_exigir_cobertura_pasa_cuando_TODAS_estan_ligadas(repo):
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py",
             "def regla_uno():\n    pass\n\n\ndef regla_dos():\n    pass\n")
    _commit(repo, "docs/PREREG_X.md",
            IMPL_OK.replace(" -->", ", C2=analysis/mod.py:regla_dos -->") + "\n**C2** la segunda.\n",
            "prereg")
    assert G.exigir_cobertura("PREREG_X.md") == []


def test_exigir_cobertura_BLOQUEA_si_el_texto_vigente_no_esta_commiteado(repo):
    """Un prerregistro que puede cambiar mientras corre el protocolo no congela nada."""
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py", "def regla_uno():\n    pass\n")
    _escribe(repo, "docs/PREREG_X.md", IMPL_OK)
    problemas = G.exigir_cobertura("PREREG_X.md")
    assert len(problemas) == 1 and "NO está commiteado" in problemas[0]


def test_exigir_cobertura_BLOQUEA_si_el_documento_no_existe(repo):
    assert len(G.exigir_cobertura("PREREG_QUE_NO_ESTA.md")) == 1


def test_el_sello_lleva_blob_y_commit_del_texto(repo):
    _commit(repo, "docs/PREREG_X.md", PREREG, "prereg")
    s = G.sello_normativo("docs/PREREG_X.md")
    assert s["commiteado"] and len(s["blob_sha1"]) == 40 and len(s["commit_del_texto"]) == 40
    assert json.dumps(s), "el sello viaja en el recibo: tiene que ser serializable"


# ═══════════════════════════════════════ 4º DICTAMEN · los cuatro falsos verdes de la guardia
def test_P0_6_el_prereg_y_el_artefacto_EN_EL_MISMO_COMMIT_no_establecen_precedencia(repo):
    """`_es_ancestro` devolvia True para `a == b`. Lo escribi razonando «el mismo commit no es
    posterior, luego vale», y es al reves: escribir el prerregistro y el resultado A LA VEZ es
    exactamente lo que haria quien redacta el prerregistro con el resultado ya delante."""
    _escribe(repo, "docs/PREREG_X.md", PREREG)
    _escribe(repo, "quant-system-ingesta/qs/tools/sonda.py", "x = 1\n")
    _git(str(repo), "add", "--", "docs/PREREG_X.md", "quant-system-ingesta/qs/tools/sonda.py")
    _git(str(repo), "commit", "-q", "-m", "los dos a la vez")
    problemas, _ = G.comprobar_cronologia()
    assert len(problemas) == 1 and "MISMO commit" in problemas[0] and "E-42" in problemas[0]


def test_P0_6_la_ancestria_es_ESTRICTA(repo):
    c = _commit(repo, "docs/PREREG_X.md", PREREG, "prereg")
    assert G._es_ancestro(c, c) is False, "un commit no se precede a si mismo"


def test_P0_5_un_worktree_revertido_a_una_version_PASADA_no_pasa_por_commiteado(repo):
    """EL falso verde de P0-5. La guardia hasheaba el ARBOL DE TRABAJO y buscaba en la historia un
    commit que coincidiera: revertir el documento a la v1 sin commitear daba `commiteado: True`
    apuntando a la v1, mientras HEAD tiene la v2. Un worktree sucio se presentaba como congelado."""
    v1 = "# v1\n\n<!-- PRECEDE: quant-system-ingesta/qs/tools/sonda.py -->\n\n**C1** vieja.\n"
    a = _commit(repo, "docs/PREREG_X.md", v1, "v1")
    b = _commit(repo, "docs/PREREG_X.md", PREREG, "v2")
    assert G.sello_normativo("docs/PREREG_X.md")["commit_del_texto"] == b
    _escribe(repo, "docs/PREREG_X.md", v1)                    # REVERTIDO sin commitear
    s = G.sello_normativo("docs/PREREG_X.md")
    assert s["commiteado"] is False, f"la v1 esta en la historia ({a[:8]}) pero HEAD tiene la v2"
    assert G.ruta_limpia("docs/PREREG_X.md") is False
    assert any("NO esta commiteado" in p.replace("\u00e1", "a")
               for p in G.exigir_cobertura("PREREG_X.md"))


def test_P0_5_la_ruta_limpia_es_lo_que_distingue_congelado_de_editable(repo):
    _commit(repo, "docs/PREREG_X.md", PREREG, "v1")
    assert G.ruta_limpia("docs/PREREG_X.md") is True
    _escribe(repo, "docs/PREREG_X.md", PREREG + "\ncualquier cambio\n")
    assert G.ruta_limpia("docs/PREREG_X.md") is False


def test_P0_7_un_COMODIN_con_fechas_sesgadas_ya_no_deja_pasar_al_hermano_anterior(repo):
    """LOS DOS defectos de P0-7 a la vez, que es como se producia el falso verde:

      · el comodin casa VARIOS ficheros y solo se inspeccionaba UNA adicion;
      · «la ultima linea de git log es la mas antigua» es FALSO — git log ordena por FECHA, no
        topologicamente, asi que basta con fechas sesgadas (o dos maquinas con relojes distintos)
        para que la linea leida sea la equivocada.

    Aqui `sonda_a.py` entra ANTES del prerregistro pero con fecha POSTERIOR, y `sonda_b.py` entra
    despues con fecha anterior: la version vieja leia solo `sonda_b` y daba verde."""
    _commit(repo, "quant-system-ingesta/qs/tools/sonda_a.py", "a = 1\n", "a (antes)",
            fecha="2026-01-20T00:00:00 +0000")
    _commit(repo, "docs/PREREG_X.md",
            "# p\n\n<!-- PRECEDE: quant-system-ingesta/qs/tools/sonda_*.py -->\n\n**C1** r.\n",
            "prereg", fecha="2026-01-15T00:00:00 +0000")
    _commit(repo, "quant-system-ingesta/qs/tools/sonda_b.py", "b = 1\n", "b (despues)",
            fecha="2026-01-10T00:00:00 +0000")

    orden = G._git("log", "--diff-filter=A", "--format=%H", "--",
                   "quant-system-ingesta/qs/tools/sonda_*.py").split("\n")
    assert len(orden) == 2, "el comodin casa las dos adiciones"
    problemas, _ = G.comprobar_cronologia()
    assert len(problemas) == 1 and "ANCESTRO" in problemas[0], \
        "sonda_a entro ANTES del prerregistro y tiene que verse"


def test_P0_7_se_comprueban_TODAS_las_introducciones_no_una(repo):
    _commit(repo, "quant-system-ingesta/qs/tools/sonda_a.py", "a = 1\n", "a")
    _commit(repo, "quant-system-ingesta/qs/tools/sonda_b.py", "b = 1\n", "b")
    assert len(G.commits_introductores("quant-system-ingesta/qs/tools/sonda_*.py")) == 2


def test_P0_7_las_introducciones_salen_en_orden_TOPOLOGICO_no_por_fecha(repo):
    a = _commit(repo, "quant-system-ingesta/qs/tools/sonda_a.py", "a = 1\n", "a",
                fecha="2026-01-20T00:00:00 +0000")
    b = _commit(repo, "quant-system-ingesta/qs/tools/sonda_b.py", "b = 1\n", "b",
                fecha="2026-01-10T00:00:00 +0000")
    assert G.commits_introductores("quant-system-ingesta/qs/tools/sonda_*.py") == [a, b], \
        "primero el ancestro, aunque su fecha sea posterior"


# ═══════════════════════════════════════ P0-4 · implementacion DECORATIVA
DECORATIVAS = {
    "variable_local": "def otra():\n    regla_uno = 1\n    return regla_uno\n",
    "variable_de_modulo": "regla_uno = 1\n",
    "funcion_ANIDADA": "def otra():\n    def regla_uno():\n        pass\n    return regla_uno\n",
    "clase": "class regla_uno:\n    pass\n",
    "parametro": "def otra(regla_uno):\n    return regla_uno\n",
    "import_renombrado": "import os as regla_uno\n",
    "solo_un_comentario": "# regla_uno vive aqui, de verdad\n",
    "asignacion_condicional_muerta": "if False:\n    regla_uno = 1\n",
}


@pytest.mark.parametrize("forma", sorted(DECORATIVAS))
def test_P0_4_ninguna_forma_DECORATIVA_acredita_una_regla(repo, forma):
    """`ast.walk` recorria tambien los cuerpos de funcion, asi que una variable local con el nombre
    de la regla satisfacia la declaracion. Al reproducir el dictamen se vio que de los tres ejemplos
    que la mesa citaba solo la variable local pasaba —el parametro es `ast.arg` y el import es
    `ast.alias`—, pero se cierran los ocho igual: una regla que dice vivir en `mod.py:regla_uno`
    tiene que ser algo INVOCABLE e IMPORTABLE."""
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py", DECORATIVAS[forma])
    _commit(repo, "docs/PREREG_X.md", IMPL_OK, "prereg")
    assert len(G.comprobar_spec_vs_codigo()[0]) == 1, f"`{forma}` no puede acreditar una regla"
    assert len(G.exigir_cobertura("PREREG_X.md")) == 1


def test_P0_4_una_FUNCION_de_nivel_de_modulo_SI_acredita(repo):
    """Control de no-trivialidad: sin esto, lo de arriba lo cumpliria un validador que rechace todo."""
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py", "def regla_uno():\n    pass\n")
    _commit(repo, "docs/PREREG_X.md", IMPL_OK, "prereg")
    assert G.comprobar_spec_vs_codigo()[0] == []
    assert G.exigir_cobertura("PREREG_X.md") == []


def test_P0_4_una_funcion_ASINCRONA_tambien(repo):
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py", "async def regla_uno():\n    pass\n")
    _commit(repo, "docs/PREREG_X.md", IMPL_OK, "prereg")
    assert G.comprobar_spec_vs_codigo()[0] == []


def test_P0_4_una_CONSTANTE_de_modulo_solo_acredita_si_se_DECLARA_como_tal(repo):
    """Mi primer arreglo de P0-4 exigia funcion SIEMPRE, y la guardia se puso roja sobre el repo real
    al primer intento: `R2` es un UMBRAL (`LIMITE_ABSURDO_BPS`), y una constante de modulo es su
    implementacion legitima. Exigir funcion no cerraba el agujero —el agujero eran las variables
    LOCALES—: solo rompia un caso bueno. Ahora el documento lo declara con `!constante`, que es un
    acto visible en el diff."""
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py", "regla_uno = 9000.0\n")
    _commit(repo, "docs/PREREG_X.md", IMPL_OK, "sin declarar")
    assert len(G.comprobar_spec_vs_codigo()[0]) == 1, "por defecto se exige algo invocable"
    _commit(repo, "docs/PREREG_X.md",
            IMPL_OK.replace(":regla_uno -->", ":regla_uno!constante -->"), "declarada")
    assert G.comprobar_spec_vs_codigo()[0] == []


def test_P0_4_una_variable_LOCAL_no_acredita_ni_declarandola_constante(repo):
    """El agujero real de P0-4 sigue cerrado: `!constante` acepta el NIVEL DE MODULO, no un nombre
    escondido dentro de otra funcion."""
    _escribe(repo, "quant-system-ingesta/qs/analysis/mod.py",
             "def otra():\n    regla_uno = 9000.0\n    return regla_uno\n")
    _commit(repo, "docs/PREREG_X.md",
            IMPL_OK.replace(":regla_uno -->", ":regla_uno!constante -->"), "prereg")
    assert len(G.comprobar_spec_vs_codigo()[0]) == 1


# ═══════════════════════════════ 5º DICTAMEN · P0-7 · lavar una elección posterior
def test_P0_7_REACTIVAR_la_v1_despues_de_ver_el_resultado_ya_no_da_verde(repo):
    """EL lavado. Secuencia: prereg v1 -> resultado -> v2 -> revert EXACTO a los bytes de v1.

    Devolviendo la PRIMERA aparición del blob, el sello apuntaba al commit de v1 —anterior al
    resultado— y la cronología daba verde. Pero v1 se reactivó DESPUÉS de ver el resultado: un
    prerregistro que se puede reactivar a posteriori no pre-registra nada."""
    v1 = "# v1\n\n<!-- PRECEDE: quant-system-ingesta/qs/tools/sonda.py -->\n\n**C1** la vieja.\n"
    v2 = "# v2\n\n<!-- PRECEDE: quant-system-ingesta/qs/tools/sonda.py -->\n\n**C1** la NUEVA.\n"
    c_v1 = _commit(repo, "docs/PREREG_X.md", v1, "v1")
    _commit(repo, "quant-system-ingesta/qs/tools/sonda.py", "x = 1\n", "EL RESULTADO")
    _commit(repo, "docs/PREREG_X.md", v2, "v2")
    c_rev = _commit(repo, "docs/PREREG_X.md", v1, "revert exacto a la v1")

    commit, _blob = G.commit_del_texto_vigente("docs/PREREG_X.md")
    assert commit == c_rev, "el sello tiene que apuntar a la TRANSICIÓN que reactivó el texto"
    assert commit != c_v1, "no a su primera aparición histórica"
    problemas, _ = G.comprobar_cronologia()
    assert len(problemas) == 1 and "E-42" in problemas[0]


def test_P0_7_un_cambio_NORMAL_sigue_sellando_a_su_commit(repo):
    """Control de no-trivialidad: sin esto, lo de arriba lo cumpliría un sello que devuelve siempre
    el último commit del fichero, y entonces el arreglo de P0-5 (atarse al TEXTO, no al nombre)
    habría quedado deshecho sin que nadie lo notara."""
    _commit(repo, "docs/PREREG_X.md", "# v1\n\n<!-- PRECEDE: quant-system-ingesta/qs/tools/sonda.py -->\n\n**C1** la vieja.\n", "v1")
    c2 = _commit(repo, "docs/PREREG_X.md", "# v2\n\n<!-- PRECEDE: quant-system-ingesta/qs/tools/sonda.py -->\n\n**C1** la NUEVA.\n", "v2")
    _commit(repo, "otro.txt", "ruido\n", "un commit que NO toca el prereg")
    commit, _ = G.commit_del_texto_vigente("docs/PREREG_X.md")
    assert commit == c2, "el texto vigente entró en v2 y ahí se queda"


def test_P0_7_un_artefacto_que_llega_por_RENOMBRE_no_se_certifica(repo):
    """La otra mitad. El artefacto se añade ANTES del prerregistro con otro nombre y se renombra
    DESPUÉS a uno que casa el `PRECEDE`: para `--diff-filter=A` eso es una adición posterior.

    NO se finge seguir el renombre —`--find-renames` se probó ejecutándolo y no lo arregla—: se
    detecta y se rechaza, que es lo que la guardia sí puede sostener."""
    _commit(repo, "quant-system-ingesta/qs/tools/otra_cosa.py", "x = 1\n", "el resultado, con otro nombre")
    _commit(repo, "docs/PREREG_X.md", PREREG, "prereg")
    _git(str(repo), "mv", "quant-system-ingesta/qs/tools/otra_cosa.py",
         "quant-system-ingesta/qs/tools/sonda.py")
    _git(str(repo), "commit", "-q", "-m", "renombrado a lo que casa el PRECEDE")
    problemas, _ = G.comprobar_cronologia()
    assert len(problemas) == 1 and "RENOMBRE" in problemas[0]


def test_P0_7_un_artefacto_creado_de_cero_despues_SI_pasa(repo):
    """Control de no-trivialidad del detector de renombres: no puede volverse un «no» universal."""
    _commit(repo, "docs/PREREG_X.md", PREREG, "prereg")
    _commit(repo, "quant-system-ingesta/qs/tools/sonda.py", "x = 1\n", "artefacto, creado de cero")
    assert G.comprobar_cronologia()[0] == []

