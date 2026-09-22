"""GUARDIA DOCUMENTAL — dos comprobaciones mecánicas contra dos fallos que ningún agente cazó.

Los cuatro instrumentos del proyecto (leer, revisarse, refutar, ejecutar) fallaron los mismos dos días
con dos defectos que son puramente mecánicos y por tanto no necesitaban un lector:

  · **E-42 — un documento titulado `PREREG` escrito DESPUÉS de ver el resultado.** La cronología real
    fue censo → forense (que dio la vuelta al veredicto a favor de la casa) → y luego el «pre-registro».
    Un pre-registro lo es respecto del RESULTADO, no del teclado.
  · **E-45 — una especificación prometiendo lo que el código descartaba.** R2 decía que los indicadores
    «se emiten en el npz»; el código los tiraba.

SEGUNDA VERSIÓN (mesa, 2026-08-27). La primera tenía **un falso verde estructural** y **una
comprobación que no comprobaba**:

  · La cronología miraba el **árbol de trabajo**: pasaba hoy *precisamente porque* la herramienta y el
    recibo que el prerregistro debe preceder **aún no existen**, y habría fallado para siempre el día
    que existieran legítimamente. Un guardia que se vuelve rojo al cumplirse lo que vigila se
    desactiva a la semana. Ahora compara **commits introductores y ancestría**: el artefacto puede —y
    debe— aparecer DESPUÉS; lo prohibido es que fuera ANTES.
  · La spec-vs-código buscaba el identificador **como texto**, así que un comentario o un test la
    satisfacían sin implementación. Ahora el documento declara **dónde vive cada regla**
    (`R1=analysis/ref_valida.py:clasificar`) y el guardia comprueba por AST que ese **símbolo existe**
    en ese fichero. Sigue sin ser prueba de que la regla sea correcta —eso no lo puede comprobar una
    máquina— pero ya no la satisface una frase.

DISEÑO, y la restricción que lo manda: **esto no puede retrasar ni ensuciar el proyecto.** Corre en
milisegundos, no abre un solo `.npz`, no toca la red y no escribe nada. Los prerregistros anteriores a
la regla quedan EXIMIDOS uno a uno, enumerados: exigirles retroactivamente una declaración que no
existía sería inventar una falta.

    python tools/guardia_documental.py            # rc=0 si todo cuadra
    python tools/guardia_documental.py --verboso  # además, lo que está pendiente (no falla)
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import glob
import json
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registro_sonda as RS   # noqa: E402

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ = os.path.dirname(os.path.dirname(QS))
DOCS = os.path.join(RAIZ, "docs")

# Prerregistros ANTERIORES a esta regla (2026-08-27). Se enumeran UNO A UNO —no con un comodín— para
# que añadir uno a la lista sea un acto visible en el diff y no un descuido.
EXIMIDOS = frozenset({
    "PREREG_B.md", "PREREG_B_GATE.md", "PREREG_CONFIRMACION_LIT.md", "PREREG_CONTRARIAN.md",
    "PREREG_ECO_LIT_INSUMOS.md", "PREREG_MAKER_LIGHTER.md",
})

_PRECEDE = re.compile(r"<!--\s*PRECEDE:\s*(.*?)\s*-->", re.S)
_IDS_IMPL = re.compile(r"<!--\s*IDS-IMPLEMENTADOS:\s*(.*?)\s*-->", re.S)
_ID_REGLA = re.compile(r"\*\*([RMCST]\d+(?:-[a-z]+)?)\b")
_FORMA_ID = re.compile(r"[RMCST]\d+(?:-[a-z]+)?")     # lo que NO tiene esta forma es prosa, no declaración
_DECL = re.compile(r"^([RMCST]\d+(?:-[a-z]+)?)\s*=\s*([^:]+):(\w+)(!constante)?$")


def _git(*args) -> str:
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else ""


def commits_introductores(pathspec: str) -> list:
    """TODOS los commits que añadieron algún path que casa `pathspec`, del más viejo al más nuevo.

    DOS DEFECTOS QUE ARREGLA (mesa, P0-7), y el segundo es el que producía el falso verde:

      · **una sola adición.** Un `PRECEDE` con comodín casa VARIOS ficheros; quedarse con una
        adición e ignorar las demás deja pasar al hermano que llegó antes del prerregistro.
      · **«la última línea es la más antigua» es FALSO en un DAG.** `git log` ordena por fecha de
        commit en reverso, no topológicamente: con fechas sesgadas —o con relojes distintos, que es
        lo normal entre máquinas— la última línea puede no ser un ancestro de nada. Se pide
        `--topo-order --reverse`, que sí respeta la ancestría, y `--full-history`, sin el cual git
        poda adiciones en ramas laterales de un merge.

    Se devuelven TODAS y se comprueban TODAS: la única forma de que un conjunto entero preceda es
    que preceda cada uno."""
    salida = _git("log", "--diff-filter=A", "--format=%H", "--full-history", "--topo-order",
                  "--reverse", "--", pathspec)
    return [c.strip() for c in salida.split("\n") if c.strip()]


def introducciones_por_renombre(pathspec: str) -> list:
    """Commits que hicieron aparecer un path por RENOMBRE, no por creación.

    P0-7, segunda mitad. Un artefacto puede añadirse ANTES del prerregistro con un nombre cualquiera
    y renombrarse DESPUÉS a uno que casa el `PRECEDE`: para `--diff-filter=A` eso es una adición
    posterior al prerregistro, y la cronología da verde sobre un resultado que ya existía.

    NO se finge seguir el renombre. La receta que propuso la mesa —`--find-renames`— se comprobó
    EJECUTÁNDOLA y no arregla nada: la detección de renombres cambia cómo se REPORTA el cambio, no
    hace visible que el contenido existía antes bajo otro nombre. Así que se hace lo honesto:
    **detectarlo y rechazarlo**. Si un artefacto vigilado llegó por renombre, la guardia no puede
    establecer cuándo existió su contenido por primera vez, y lo dice en vez de certificarlo."""
    # SIN pathspec, y no es un detalle: comprobado ejecutando, `--diff-filter=R` CON pathspec
    # devuelve VACÍO, porque un renombre necesita los dos lados en el diff y el pathspec sólo
    # deja pasar el destino. Mi primera versión hacía justo eso y no detectaba nada — habría
    # sido un detector decorativo, que es la clase de control que este proyecto cataloga.
    # Se recorre la historia con `--raw` y se casa el DESTINO del renombre contra el pathspec.
    salida = _git("log", "--diff-filter=R", "--find-renames", "--full-history",
                  "--topo-order", "--reverse", "--format=%H", "--raw")
    commit, encontrados = "", []
    for linea in salida.split("\n"):
        s = linea.strip()
        if not s:
            continue
        if not s.startswith(":"):
            commit = s
            continue
        partes = s.split("\t")
        if len(partes) >= 3 and partes[0].split()[-1].startswith("R"):
            destino = partes[2]
            if destino == pathspec or fnmatch.fnmatch(destino, pathspec):
                encontrados.append(commit)
    return encontrados


def _commit_introductor(pathspec: str) -> str:
    """La adición MÁS ANTIGUA, o '' si no está en la historia. Se conserva para los usos que sólo
    necesitan saber SI algo está ya en la historia."""
    cs = commits_introductores(pathspec)
    return cs[0] if cs else ""


def _blob_del_arbol(rel: str) -> str:
    """SHA-1 del contenido ACTUAL del fichero. Es la identidad del TEXTO, no la del nombre."""
    return _git("hash-object", "--", os.path.join(RAIZ, rel))


def _blob_en_head(rel: str) -> str:
    """SHA-1 de la versión de `rel` en HEAD. '' si no está en HEAD."""
    return _git("rev-parse", f"HEAD:{rel}")


def ruta_limpia(rel: str) -> bool:
    """¿El árbol de trabajo coincide con HEAD para ese path?

    P0-5. `commit_del_texto_vigente` hasheaba el ÁRBOL DE TRABAJO y buscaba en la historia un commit
    que coincidiera. Si alguien revierte el documento a una versión pasada SIN commitear, esos bytes
    SÍ existen en la historia y el sello salía `commiteado: True` — apuntando a la v1 mientras HEAD
    tiene la v2. Un worktree sucio se presentaba como normativa congelada."""
    return bool(_blob_en_head(rel)) and _blob_del_arbol(rel) == _blob_en_head(rel)


def commit_del_texto_vigente(rel: str) -> tuple:
    """(commit, blob) donde el texto normativo ACTUAL entró en la historia. ('', blob) si aún no.

    EL DEFECTO QUE ARREGLA (mesa, P0-5): atarse al commit introductor ata el recibo a la **v1** del
    documento. `PREREG_SONDA_COBERTURA.md` nació en 546148e, pero sus reglas vigentes se escribieron
    en 807d0fe: un recibo que citara 546148e estaría certificando un texto que ya no rige. Lo que hay
    que fijar es el BLOB — el contenido exacto—, y el commit relevante es aquel en que ese contenido
    apareció, no aquel en que apareció el nombre del fichero."""
    blob = _blob_en_head(rel)                          # LA DE HEAD, no la del arbol de trabajo
    if not blob or not ruta_limpia(rel):
        # Sin ruta limpia no hay texto vigente que sellar: lo que se lee en disco no es lo que la
        # historia contiene, y sellar el segundo mientras se ejecuta con el primero es la mentira
        # exacta que P0-5 describe.
        return "", _blob_del_arbol(rel)
    # LA TRANSICIÓN MÁS RECIENTE QUE ACTIVÓ ESTE TEXTO, no su primera aparición histórica
    # (mesa 2026-08-29, P0-7). El defecto y su reproducción:
    #
    #     prereg v1  ->  resultado  ->  v2  ->  revert EXACTO a los bytes de v1
    #
    # Devolviendo la PRIMERA aparición, el sello apuntaba al commit de v1 —anterior al
    # resultado— y la cronología daba verde, aunque v1 se hubiera reactivado DESPUÉS de ver el
    # resultado. Un prerregistro que se puede reactivar a posteriori no pre-registra nada.
    #
    # Se recorre de HEAD hacia atrás mientras el blob siga siendo el mismo: el último commit
    # antes del primer desacuerdo ES la transición que lo puso en vigor.
    historia = [c for c in _git("log", "--format=%H", "--topo-order", "--", rel).split("\n")
                if c.strip()]
    activador = ""
    for c in historia:                                 # de la MÁS NUEVA a la más vieja
        if _git("rev-parse", f"{c}:{rel}") != blob:
            break                                      # aquí cambió: el anterior lo activó
        activador = c
    return activador, blob


def _es_ancestro(a: str, b: str) -> bool:
    """¿`a` es ancestro ESTRICTO de `b`? Falso si son el mismo commit, o si alguno no resuelve.

    EL MISMO COMMIT NO ES ANTERIOR (mesa, P0-6). La versión anterior devolvía `True` para `a == b`
    con el razonamiento «el mismo commit no es posterior, luego vale», y es al revés: escribir el
    prerregistro y el resultado **a la vez** no demuestra ninguna precedencia — es exactamente lo
    que haría quien redacta el prerregistro con el resultado ya delante, que es E-42."""
    if not a or not b or a == b:
        return False
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b],
                          cwd=RAIZ, capture_output=True).returncode == 0


def comprobar_cronologia(verboso=False):
    """A · Un PREREG declara QUÉ precede, y eso no puede ser ANTERIOR a él.

    La comparación es de ANCESTRÍA entre commits introductores, no de existencia. Que el artefacto
    exista hoy es lo NORMAL y lo esperado: un pre-registro se escribe para que algo venga después.
    Lo que lo invalida es que ya estuviera antes — eso es E-42."""
    problemas, notas = [], []
    for ruta in sorted(glob.glob(os.path.join(DOCS, "PREREG_*.md"))):
        nombre = os.path.basename(ruta)
        if nombre in EXIMIDOS:
            notas.append(f"{nombre}: EXIMIDO (anterior a la regla)")
            continue
        texto = io.open(ruta, encoding="utf-8").read()
        m = _PRECEDE.search(texto)
        if not m:
            problemas.append(f"{nombre}: no declara `PRECEDE`. Un prerregistro que no dice QUÉ precede "
                             f"no es verificable, y por tanto no es un prerregistro.")
            continue
        rutas = [x.strip() for x in m.group(1).replace("\n", " ").split(",") if x.strip()]
        if not rutas:
            problemas.append(f"{nombre}: `PRECEDE` está vacío.")
            continue
        # EL COMMIT DEL TEXTO VIGENTE, no el introductor (mesa, P0-5). Si el documento nació en A y
        # sus reglas se reescribieron en B, un artefacto aparecido entre A y B desciende de A y la
        # versión anterior lo aceptaba — pero ese artefacto es ANTERIOR a las reglas que dicen
        # pre-registrarlo. Es E-42 otra vez, colándose por la diferencia entre el nombre y el texto.
        c_doc, _blob = commit_del_texto_vigente(f"docs/{nombre}")
        if not c_doc and _commit_introductor(f"docs/{nombre}"):
            # NOTA, no problema — y la distinción es de diseño, no una concesión. Editar un
            # prerregistro deja su texto sin commitear durante un rato: si eso pusiera rojo el
            # chequeo general, la guardia estaría roja justo mientras se hace trabajo legítimo, que
            # es el antipatrón que su propia cabecera describe. Donde SÍ es un impedimento absoluto
            # es antes de gastar, y ahí lo bloquea `exigir_cobertura` (§7 bis del prerregistro).
            notas.append(f"{nombre}: su texto actual aún no está commiteado — la cronología se "
                         f"comprueba contra la última versión commiteada. Para EJECUTAR bajo él hay "
                         f"que commitearlo: `--exigir` lo bloquea.")
            c_doc = _commit_introductor(f"docs/{nombre}")
        for r in rutas:
            # TODAS las introducciones, no una (P0-7). Un comodín casa varios ficheros y basta con
            # que UNO llegara antes para que el prerregistro no lo pre-registre.
            renombres = introducciones_por_renombre(r)
            if renombres:
                problemas.append(
                    f"{nombre}: `{r}` apareció por RENOMBRE en {renombres[0][:8]}. La guardia "
                    f"no puede establecer cuándo existió ese contenido por primera vez —un "
                    f"artefacto puede añadirse antes del prerregistro y renombrarse después—, "
                    f"así que no lo certifica. Fail-closed (E-42).")
                continue
            introducciones = commits_introductores(r)
            if introducciones:
                for c_art in introducciones:
                    if _es_ancestro(c_doc, c_art):
                        if verboso:
                            notas.append(f"{nombre}: `{r}` en {c_art[:8]}, DESCENDIENTE ESTRICTO del "
                                         f"prereg {c_doc[:8]} — correcto.")
                        continue
                    if not c_doc:
                        motivo = ("y el prerregistro no se ha commiteado todavía: llega tarde")
                    elif c_art == c_doc:
                        motivo = (f"en EL MISMO commit que el prerregistro ({c_doc[:8]}): escribir "
                                  f"los dos a la vez no establece ninguna precedencia")
                    elif _es_ancestro(c_art, c_doc):
                        motivo = (f"y es ANCESTRO del prerregistro ({c_doc[:8]}): el documento no lo "
                                  f"pre-registra, lo describe")
                    else:
                        motivo = (f"y no desciende del prerregistro ({c_doc[:8]}): son ramas "
                                  f"HERMANAS, la precedencia no está establecida — y sin establecerla "
                                  f"no se puede afirmar")
                    problemas.append(f"{nombre}: `{r}` se introdujo en {c_art[:8]} {motivo} (E-42).")
                continue

            # AÚN NO está en la historia: correcto, es lo que un prerregistro espera.
            if os.path.exists(os.path.join(RAIZ, r)) or glob.glob(os.path.join(RAIZ, r)):
                if not c_doc:
                    problemas.append(
                        f"{nombre}: `{r}` ya está en el árbol de trabajo y el prerregistro AÚN NO "
                        f"se ha commiteado. Se estaría escribiendo el prerregistro con el artefacto "
                        f"ya delante (E-42).")
                elif verboso:
                    notas.append(f"{nombre}: `{r}` existe sin commitear, y el prereg ya está en "
                                 f"{c_doc[:8]} — correcto.")
            elif verboso:
                notas.append(f"{nombre}: `{r}` aún no existe. Correcto.")
    return problemas, notas


def _define_simbolo(ruta_py: str, simbolo: str, constante: bool = False) -> bool:
    """¿`ruta_py` define `simbolo` en el NIVEL DE MÓDULO? Por AST, no por texto.

    Por defecto exige algo INVOCABLE. `constante=True` —que el documento pide explícitamente con el
    sufijo `!constante`— acepta además una asignación de módulo, para las reglas que son umbrales.

    Un `grep` lo satisface un comentario; un `ast.walk` lo satisfacía una variable local. Esto exige
    algo invocable e importable — que sigue sin probar que la regla sea CORRECTA, pero ya no la
    cumple ni una frase ni un nombre suelto."""
    try:
        arbol = ast.parse(io.open(ruta_py, encoding="utf-8").read())
    except Exception:
        return False
    # SOLO el NIVEL SUPERIOR, y sólo cosas INVOCABLES (mesa, P0-4). `ast.walk` recorría también los
    # cuerpos de función, así que una VARIABLE LOCAL con el nombre de la regla —`regla_uno = 1`
    # dentro de cualquier otra función— satisfacía la declaración. Una regla que dice vivir en
    # `mod.py:regla_uno` tiene que ser algo que se pueda LLAMAR, y tiene que poder importarse.
    #
    # (Al reproducir el dictamen se comprobó que el parámetro y el import NO pasaban ya —son
    # `ast.arg` y `ast.alias`, no `ast.Name`—: de los tres ejemplos que la mesa citó sólo la variable
    # local era real. El arreglo cierra los tres de todos modos.)
    for n in arbol.body:                                   # SOLO el nivel superior
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == simbolo:
            return True
        if not constante:
            continue
        # Una CONSTANTE es implementación legítima de una regla que es un umbral (`R2` es el límite
        # de 9.000 bps), pero hay que DECLARARLO: `R2=fichero.py:NOMBRE!constante`. El valor por
        # defecto sigue siendo lo estricto —invocable—, y aceptar una constante es un acto visible
        # en el diff, no un descuido. Exigir función SIEMPRE no cerraba P0-4: sólo rompía un caso
        # bueno, y la guardia me lo dijo al primer intento.
        if isinstance(n, ast.AnnAssign) and getattr(n.target, "id", None) == simbolo:
            return True
        if isinstance(n, ast.Assign) and any(getattr(d, "id", None) == simbolo for d in n.targets):
            return True
    return False


def comprobar_spec_vs_codigo(verboso=False):
    """B · Toda regla declarada implementada dice DÓNDE vive, y ese símbolo tiene que existir.

    Formato: `IDS-IMPLEMENTADOS: R1=analysis/ref_valida.py:clasificar, R3=...`. Los ids que el
    documento enumera y NO declara implementados se reportan como pendientes y **no fallan**: un
    pre-registro habla de cosas que aún no existen, y tratarlas como deuda pondría rojo el build por
    diseñar con antelación."""
    problemas, notas = [], []
    for ruta in sorted(glob.glob(os.path.join(DOCS, "*.md"))):
        texto = io.open(ruta, encoding="utf-8").read()
        m = _IDS_IMPL.search(texto)
        if not m:
            continue
        nombre = os.path.basename(ruta)
        crudos = [x.strip() for x in m.group(1).replace("\n", " ").split(",") if x.strip()]
        # Un token sin FORMA de declaración es prosa que MENCIONA el marcador — p. ej. el documento
        # que explica esta herramienta. Tratarlo como declaración ponía rojo el build por documentar
        # el guardia (E-52), que es la clase de falso positivo que hace que un guardia se desactive.
        decls = [d for d in (_DECL.match(x) for x in crudos) if d]
        if crudos and not decls:
            if verboso:
                notas.append(f"{nombre}: menciona el marcador sin declarar reglas — se ignora.")
            continue
        todos = set(_ID_REGLA.findall(texto))
        declarados = set()
        for d in decls:
            ident, rel, simbolo = d.group(1), d.group(2).strip(), d.group(3)
            es_cte = bool(d.group(4))
            declarados.add(ident)
            if ident not in todos:
                problemas.append(f"{nombre}: declara `{ident}` implementado pero ese id NO aparece "
                                 f"como regla en el propio documento.")
                continue
            destino = os.path.join(QS, rel)
            if not os.path.isfile(destino):
                problemas.append(f"{nombre}: `{ident}` apunta a `{rel}`, que no existe.")
            elif not _define_simbolo(destino, simbolo, es_cte):
                problemas.append(f"{nombre}: `{ident}` dice vivir en `{rel}:{simbolo}` y ese símbolo "
                                 f"NO está definido ahí. Una especificación que promete lo que el "
                                 f"código no tiene es E-45.")
            elif verboso:
                notas.append(f"{nombre}: `{ident}` → `{rel}:{simbolo}` existe.")
        for i in sorted(todos - declarados):
            notas.append(f"{nombre}: `{i}` declarado y PENDIENTE (no exigido).")
    return problemas, notas


def sello_normativo(rel: str) -> dict:
    """EL SELLO QUE DEBE VIAJAR EN EL RECIBO: el blob del texto vigente y el commit en que entró.

    Un recibo que cite el commit introductor certifica la v1 del documento, no el texto que rige
    (mesa, P0-5). Lo que identifica un prerregistro congelado es el CONTENIDO."""
    commit, blob = commit_del_texto_vigente(rel)
    return {"documento": rel, "blob_sha1": blob, "commit_del_texto": commit,
            "commiteado": bool(commit)}


def exigir_cobertura(nombre_doc: str) -> list:
    """BLOQUEA mientras alguna regla del documento no tenga implementación LIGADA.

    Es lo contrario de `comprobar_spec_vs_codigo`, y a propósito: allí una regla pendiente es normal
    —un prerregistro habla de lo que aún no existe— y no puede poner rojo el build. Aquí, en cambio,
    se pregunta si el documento está listo para EJECUTARSE, y entonces una regla sin código es un
    impedimento absoluto: gastar créditos bajo un prerregistro a medio implementar es ejecutar un
    protocolo que nadie puede verificar después.

    La mesa (P0-5): «bloquear la ejecución mientras cualquier regla C/S/T siga sin implementación
    ligada». Se llama ANTES de gastar, no al terminar."""
    ruta = os.path.join(DOCS, nombre_doc)
    if not os.path.isfile(ruta):
        return [f"{nombre_doc}: no existe. No se ejecuta un protocolo sin su prerregistro."]
    texto = io.open(ruta, encoding="utf-8").read()
    if not commit_del_texto_vigente(nombre_doc if nombre_doc.startswith("docs/")
                                    else f"docs/{nombre_doc}")[0]:
        return [f"{nombre_doc}: el texto vigente NO está commiteado. Un prerregistro que puede "
                f"cambiar mientras corre el protocolo no congela nada."]
    m = _IDS_IMPL.search(texto)
    crudos = [x.strip() for x in m.group(1).replace("\n", " ").split(",") if x.strip()] if m else []
    declaradas = {}
    for d in (_DECL.match(x) for x in crudos):
        if d:
            declaradas[d.group(1)] = (d.group(2).strip(), d.group(3), bool(d.group(4)))
    problemas = []
    # EL REGISTRO Y EL DOCUMENTO TIENEN QUE DECIR LO MISMO (mesa, cierre minimo). El AST acredita que
    # existe un simbolo; el registro acredita que ese simbolo se IMPORTA y es INVOCABLE, y que alguien
    # lo llamara antes de gastar. Son cosas distintas y hacen falta las dos.
    if nombre_doc == RS.DOC_SONDA:
        problemas += RS.cuadra_con_el_prerregistro(declaradas)
    for ident in sorted(set(_ID_REGLA.findall(texto))):
        if ident not in declaradas:
            problemas.append(f"{nombre_doc}: `{ident}` no declara DÓNDE está implementada. "
                             f"Sin implementación ligada no se ejecuta.")
            continue
        rel, simbolo, es_cte = declaradas[ident]
        destino = os.path.join(QS, rel)
        if not os.path.isfile(destino) or not _define_simbolo(destino, simbolo, es_cte):
            problemas.append(f"{nombre_doc}: `{ident}` dice vivir en `{rel}:{simbolo}` y ahí no está.")
    return problemas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verboso", action="store_true", help="además, lo que está pendiente (no falla)")
    ap.add_argument("--exigir", metavar="PREREG_X.md",
                    help="BLOQUEA (rc=2) si alguna regla de ese documento no tiene implementación "
                         "ligada. Se invoca ANTES de gastar créditos, no al terminar.")
    ap.add_argument("--sello", metavar="docs/PREREG_X.md",
                    help="imprime el sello normativo (blob del texto vigente + su commit) para el recibo")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    if args.sello:
        s = sello_normativo(args.sello)
        print(json.dumps(s, ensure_ascii=False, sort_keys=True))
        return 0 if s["commiteado"] else 2

    if args.exigir:
        problemas = exigir_cobertura(args.exigir)
        print(f"COBERTURA EXIGIDA — {args.exigir}\n")
        for p in problemas:
            print(f"      *** {p}")
        if problemas:
            print(f"\n{len(problemas)} regla(s) sin implementación ligada. NO SE EJECUTA: gastar bajo "
                  f"un prerregistro a medio implementar produce un protocolo que nadie puede\n"
                  f"verificar después. Impleméntalas y declara dónde viven.")
            return 2
        s = sello_normativo(f"docs/{args.exigir}")
        print(f"      todas las reglas ligadas.\n"
              f"      sello normativo: blob {s['blob_sha1'][:12]} en {s['commit_del_texto'][:8]}\n"
              f"      ESTE es el sello que el recibo debe citar — no el commit introductor.")
        return 0

    print("GUARDIA DOCUMENTAL — cronología por ANCESTRÍA y spec-vs-código por SÍMBOLO\n")
    todos_problemas = []
    for etiqueta, fn in (("A · cronología de prerregistros (E-42)", comprobar_cronologia),
                         ("B · spec declarada vs código (E-45)", comprobar_spec_vs_codigo)):
        problemas, notas = fn(args.verboso)
        print(f"  {etiqueta}")
        for n in notas:
            print(f"      · {n}")
        for p in problemas:
            print(f"      *** {p}")
        if not problemas:
            print("      OK")
        print()
        todos_problemas += problemas

    if todos_problemas:
        print(f"*** {len(todos_problemas)} problema(s). El build se para: son defectos MECÁNICOS,")
        print("*** de los que no necesitan un lector para verse.")
        return 1
    print("Sin problemas. LO QUE ESTO NO COMPRUEBA, y conviene tenerlo presente: que la regla escrita")
    print("sea BUENA, ni que el símbolo al que apunta haga lo que dice. Sólo que exista donde dice")
    print("existir y que el prerregistro no llegue tarde.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
