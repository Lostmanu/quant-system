"""GUARDIA DE COMPLETITUD — «cerré una ruta de tres» deja de ser posible en silencio.

POR QUÉ EXISTE. Es mi modo de fallo más reincidente, medido sobre el propio registro del método:

    E-44  «el defecto vive en el carril Binance» — con 4 contraejemplos en mi propia tabla
    E-49  la regla del guardia escrita DOS veces; quitar una no abría el agujero
    E-53  compuerta del carril en 1 productor de 3 (`eco_runner_lit`, el prospectivo oficial, abierto)
    E-55  compuerta de consumo en 3 lectores de 16

Cuatro veces el mismo patrón: arreglo el caso que estoy mirando y declaro arreglada la clase. No es
un fallo de juicio — es una **búsqueda que no hice**. Y una búsqueda se mecaniza.

═══ SEGUNDA VERSIÓN (mesa, 2026-08-28, 4ª reauditoría) ═══

La v1 «tampoco era load-bearing todavía», y las seis objeciones eran ciertas. Verificadas
ejecutando, una a una:

  · **no corría en el CI ni tenía pruebas.** Es la única que importa de verdad y las otras cinco son
    de segundo orden: un guardia que no corre en ningún sitio no tiene poder de veto, así que sus
    puntos ciegos no «dejaban pasar» nada — no había compuerta.
  · **sólo miraba `analysis/`.** Hay **6 llamadas reales bajo `tools/`** que no veía.
  · **buscaba TEXTO, no llamadas.** `if op not in fuente` acierta en un comentario y falla con
    `from numpy import load`, `numpy.load` o cualquier alias. Prueba de que el defecto era real:
    `cryptohft_adapter.py` estaba EXIMIDO y no tiene una sola llamada — la exención era fantasma,
    inventada por una coincidencia de texto.
  · **las exenciones abarcaban ficheros enteros.** Eximir `eco_gate_b.py` eximía sus 5 llamadas y
    las que se añadieran después, para siempre y en silencio.
  · **comprobaba presencia por módulo**, no que la compuerta domine al productor: bastaba que el
    fichero NOMBRARA `exigir_produccion` en cualquier sitio.
  · **no veía a los escritores.** Sólo vigilaba `np.load`, así que los **6 `np.savez`** que escriben
    artefactos sin pasar por la primitiva eran invisibles — y ahí vive el agujero del eco.

QUÉ COMPRUEBA AHORA:

  **A · EXCLUSIVIDAD, por callsite.** Una operación peligrosa sólo puede aparecer donde se la
  encapsula. Se detecta por AST resolviendo alias (`import numpy as np`, `import numpy`,
  `from numpy import load`, `from numpy import load as L`). Cada excepción se declara por
  `fichero::función::operación` **con el número esperado de llamadas**: añadir una segunda en una
  función ya eximida rompe el build.

  **B · DOMINANCIA.** No basta que el módulo nombre su guardia: en la MISMA función que publica, la
  compuerta tiene que estar en el nivel superior del cuerpo —no escondida en una rama— y ANTES.
  Sigue sin ser un análisis de flujo completo; es una cota inferior mecanizable, y cubre el caso que
  falló: nombrar el guardia sin que gobierne nada. Lo que NO ve: que el bucle de la compuerta y el de
  la producción recorran el MISMO conjunto. Eso lo fijan los tests del productor.

LO QUE NO COMPRUEBA, y conviene decirlo: que el guardia haga lo que dice. Eso lo fijan sus tests, y
que sus tests muerdan lo fija el arnés de mutación.

    python tools/guardia_completitud.py            # rc=0 si no falta ninguno
    python tools/guardia_completitud.py --verboso  # además, lo que sí está cubierto
    python tools/guardia_completitud.py --censo    # las llamadas encontradas, para auditar la tabla
"""
from __future__ import annotations

import argparse
import ast
import glob
import hashlib
import os
import sys

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAQUETES = ("analysis", "tools")
NUMPY_VIGILADAS = ("load", "savez", "savez_compressed", "save")

# ---------------------------------------------------------------------------------------------
# A · EXCLUSIVIDAD. (operación, dónde PUEDE vivir, por qué)
EXCLUSIVAS = (
    ("np.load", ("analysis/artefacto.py",),
     "cargar un artefacto sin pasar por `artefacto.cargar` salta la acreditación (E-55): sin "
     "manifiesto, sin hash de los bytes, sin esquema de contenido y sin recomputar la conformidad "
     "del carril contra la capa que el consumidor espera"),
    ("np.savez", ("analysis/artefacto.py",),
     "escribir un artefacto sin pasar por `artefacto.publicar` lo deja SIN manifiesto — y un npz "
     "sin manifiesto es indistinguible de uno acreditado para quien lo lea después"),
    ("np.savez_compressed", ("analysis/artefacto.py",),
     "mismo caso que `np.savez`, y además rompería la identidad-byte de M-10"),
)

# V2 lote 3: se retiran todos los sitios históricos exentos con sus consumidores.
# El mecanismo y sus pruebas sintéticas permanecen.
EXENTAS = {}

# ---------------------------------------------------------------------------------------------
# B · DOMINANCIA. (función que marca, guardia que tiene que dominarla, por qué)
DOMINANCIA = (
    ("publicar", "exigir_produccion",
     "quien publica un artefacto tiene que haber pasado la compuerta del carril ANTES, y en el "
     "nivel superior de la función — no dentro de una rama que puede no tomarse"),
)


# V2 lote 2: se retiran los tres sitios sellados de I5 junto con sus instrumentos.
# El mecanismo conserva sus pruebas sintéticas; no quedan excepciones activas aquí.
# clave -> (llamadas, SHA-256 del módulo completo, fundamento de la excepción).
EXCLUSIVIDAD_SELLADAS = {}
DOMINANCIA_SELLADAS = {}


def modulos():
    """Todos los `.py` de los paquetes vigilados, recursivamente. (rel, fuente)."""
    for paq in PAQUETES:
        for f in sorted(glob.glob(os.path.join(QS, paq, "**", "*.py"), recursive=True)):
            # AST y hash se derivan de una sola lectura, sin normalizar CRLF a LF.
            with open(f, "rb") as source:
                fuente = source.read().decode("utf-8")
            yield os.path.relpath(f, QS).replace(os.sep, "/"), fuente


def _comprobar_selladas(tabla, vistas, fuentes, verboso):
    problemas, notas = [], []
    for clave, (esperadas, sha, motivo) in sorted(tabla.items()):
        n_selladas = vistas.get(clave, 0)
        if not n_selladas:
            problemas.append(f"{clave}: EXENCIÓN SELLADA FANTASMA — no hay ninguna llamada así.")
            continue
        rel = clave.split("::")[0]
        if n_selladas != esperadas:
            problemas.append(f"{clave}: la exención sellada declara {esperadas} llamada(s) y hay {n_selladas}.")
        if hashlib.sha256(fuentes[rel].encode("utf-8")).hexdigest() != sha:
            problemas.append(f"{clave}: SHA-256 distinto del módulo auditado; exención sellada inválida.")
        elif n_selladas == esperadas and verboso:
            notas.append(f"{clave}: {n_selladas} — EXENTA SELLADA ({motivo})")
    return problemas, notas


def _alias_numpy(arbol):
    """(módulos que son numpy, nombres importados directamente de numpy).

    Sin esto, `from numpy import load` o `import numpy` se escapan — y una búsqueda por el texto
    `np.load` los da por inexistentes."""
    mods, directas = {}, {}
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "numpy":
                    mods[a.asname or a.name] = "numpy"
        elif isinstance(n, ast.ImportFrom) and n.module == "numpy":
            for a in n.names:
                directas[a.asname or a.name] = a.name
    return mods, directas


def _contenedores(arbol) -> dict:
    """id(nodo) -> nombre de la función que lo contiene ('<modulo>' si ninguna)."""
    m = {}
    for n in ast.walk(arbol):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for h in ast.walk(n):
                m[id(h)] = n.name                 # el más interno gana: ast.walk va de fuera adentro
    return m


def censo(rel: str, fuente: str) -> list:
    """Las llamadas VIGILADAS de un módulo, por AST. [(clave, op, funcion, lineno)]."""
    try:
        arbol = ast.parse(fuente)
    except SyntaxError:
        return []
    mods, directas = _alias_numpy(arbol)
    cont = _contenedores(arbol)
    out = []
    for n in ast.walk(arbol):
        if not isinstance(n, ast.Call):
            continue
        f, op = n.func, None
        if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                and f.value.id in mods and f.attr in NUMPY_VIGILADAS):
            op = f"np.{f.attr}"
        elif isinstance(f, ast.Name) and directas.get(f.id) in NUMPY_VIGILADAS:
            op = f"np.{directas[f.id]}"
        if op:
            fn = cont.get(id(n), "<modulo>")
            out.append((f"{rel}::{fn}::{op}", op, fn, n.lineno))
    return out


def comprobar_exclusividad(verboso=False):
    permitidos = {op: set(p) for op, p, _ in EXCLUSIVAS}
    motivos = {op: m for op, _, m in EXCLUSIVAS}
    problemas, notas = [], []
    vistas, fuentes = {}, {}
    for rel, fuente in modulos():
        fuentes[rel] = fuente
        for clave, op, fn, linea in censo(rel, fuente):
            if op not in permitidos:
                continue
            if rel in permitidos[op]:
                if verboso:
                    notas.append(f"{clave} (L{linea}) — es su sitio")
                continue
            vistas[clave] = vistas.get(clave, 0) + 1
    for clave, n in sorted(vistas.items()):
        rel, fn, op = clave.split("::")
        if clave in EXCLUSIVIDAD_SELLADAS:
            continue  # Recuento y bytes comprobados juntos, debajo; nunca aprobación por nombre.
        if clave not in EXENTAS:
            problemas.append(f"{clave}: {n} llamada(s) a `{op}` fuera de "
                             f"{', '.join(sorted(permitidos[op]))}. {motivos[op]}")
            continue
        esperadas, motivo = EXENTAS[clave]
        if n != esperadas:
            problemas.append(f"{clave}: la exención declara {esperadas} llamada(s) y hay {n}. Una "
                             f"exención no se hereda: si aparece otra, se declara o se cierra.")
        elif verboso:
            notas.append(f"{clave}: {n} — EXENTA ({motivo})")
    # una exención que ya no corresponde a ninguna llamada es una exención FANTASMA: cubre algo que
    # no existe y, si mañana existe, lo cubriría sin que nadie lo decidiera. La v1 tenía una.
    for clave in sorted(set(EXENTAS) - set(vistas)):
        problemas.append(f"{clave}: EXENCIÓN FANTASMA — no hay ninguna llamada así. Sobra, y "
                         f"mañana eximiría en silencio a la que aparezca.")
    fallos, selladas = _comprobar_selladas(EXCLUSIVIDAD_SELLADAS, vistas, fuentes, verboso)
    problemas.extend(fallos)
    notas.extend(selladas)
    return problemas, notas


def _domina(arbol, fn_nombre: str, guardia: str, linea_marcada: int):
    """¿`guardia` se llama en el NIVEL SUPERIOR del cuerpo de `fn_nombre` y antes de `linea_marcada`?

    Cota inferior deliberada. No es un análisis de flujo: es la condición mecanizable que descarta el
    caso que de verdad falló —el módulo NOMBRA el guardia pero no gobierna nada— sin pretender más.
    Una llamada dentro de un `if` no cuenta: puede no tomarse."""
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) or nodo.name != fn_nombre:
            continue
        for stmt in nodo.body:                                  # SOLO el nivel superior del cuerpo
            for h in ast.walk(stmt):
                if (isinstance(h, ast.Call) and h.lineno < linea_marcada
                        and (getattr(h.func, "attr", None) == guardia
                             or getattr(h.func, "id", None) == guardia)):
                    # `If` y `Try` SÍ pueden saltarse la compuerta (una rama no tomada, un `except`
                    # que se la traga — que es como P0-2 dejó pasar el rechazo). `For`/`While`/`With`
                    # NO son ramas: su cuerpo se ejecuta, y compuertar en bucle sobre todos los
                    # símbolos antes del bucle de producción es el patrón CORRECTO, no un defecto.
                    # (Lo aprendí aquí: mi primera regla marcó `pilot_runner`, donde la compuerta
                    # está exactamente donde debe.)
                    if isinstance(stmt, (ast.If, ast.Try)):
                        continue
                    return True
    return False


def comprobar_dominancia(verboso=False):
    problemas, notas = [], []
    vistas, fuentes = {}, {}
    for marcada, guardia, motivo in DOMINANCIA:
        for rel, fuente in modulos():
            fuentes[rel] = fuente
            try:
                arbol = ast.parse(fuente)
            except SyntaxError:
                continue
            cont = _contenedores(arbol)
            for n in ast.walk(arbol):
                if not isinstance(n, ast.Call):
                    continue
                nombre = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
                if nombre != marcada:
                    continue
                fn = cont.get(id(n), "<modulo>")
                clave = f"{rel}::{fn}::{marcada}"
                vistas[clave] = vistas.get(clave, 0) + 1
                if clave in DOMINANCIA_SELLADAS:
                    continue  # También se valida si una edición añade dominancia aparente.
                if _domina(arbol, fn, guardia, n.lineno):
                    if verboso:
                        notas.append(f"{rel}::{fn}: `{guardia}` domina a `{marcada}` (L{n.lineno})")
                    continue
                problemas.append(f"{rel}::{fn} (L{n.lineno}): llama a `{marcada}` y `{guardia}` NO "
                                 f"la domina. {motivo}")
    fallos, selladas = _comprobar_selladas(DOMINANCIA_SELLADAS, vistas, fuentes, verboso)
    problemas.extend(fallos)
    notas.extend(selladas)
    return problemas, notas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verboso", action="store_true", help="además, lo que sí está cubierto")
    ap.add_argument("--censo", action="store_true", help="las llamadas encontradas, para auditar")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    if args.censo:
        total = 0
        for rel, fuente in modulos():
            for clave, op, fn, linea in censo(rel, fuente):
                marca = "SELLADA (pendiente de verificar)" if clave in EXCLUSIVIDAD_SELLADAS else (
                    "EXENTA" if clave in EXENTAS else "")
                print(f"  {clave}  L{linea}  {marca}")
                total += 1
        print(f"\n{total} llamadas vigiladas en {', '.join(PAQUETES)}/ (por AST, con alias resueltos)")
        return 0

    print("GUARDIA DE COMPLETITUD — exclusividad por callsite y dominancia de la compuerta\n")
    todos = []
    for etiqueta, fn in (("A · exclusividad (una operación peligrosa, un solo sitio)",
                          comprobar_exclusividad),
                         ("B · dominancia (la compuerta gobierna al productor, no lo acompaña)",
                          comprobar_dominancia)):
        problemas, notas = fn(args.verboso)
        print(f"  {etiqueta}")
        for n in notas:
            print(f"      · {n}")
        for p in problemas:
            print(f"      *** {p}")
        if not problemas:
            print("      OK")
        print()
        todos += problemas

    if todos:
        print(f"*** {len(todos)} ruta(s) sin cerrar. Esto es el patrón «cerré una de tres», y el")
        print("*** build se para porque enumerar a mano ya falló cuatro veces.")
        return 1
    print("Sin rutas abiertas. NO comprueba que el guardia haga lo que dice — eso lo fijan sus tests,")
    print("y que sus tests muerdan lo fija el arnés de mutación.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
