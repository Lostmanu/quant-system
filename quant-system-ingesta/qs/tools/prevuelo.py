# -*- coding: utf-8 -*-
"""PRE-VUELO — lo que se comprueba en SEGUNDOS antes de lanzar algo que tarda HORAS.

MOTIVACION, medida y no supuesta (2026-09-03). En una sola sesion se perdieron ~3,5 h de reloj en
repeticiones que un chequeo de segundos habria evitado:

 · el arnes integro relanzado porque unas inserciones en produccion partieron las anclas de dos
   filas antiguas. El arnes lo dice, si — a los ONCE MINUTOS de empezar a correr, y despues de
   haber copiado el arbol 52 veces;
 · una suite de 45 min repetida porque se edito el arbol MIENTRAS media (E-80, tercera vez);
 · un barrido de 75 min y su censo de 50 min sobre un commit que quedo obsoleto una hora despues.

Ninguna de esas tres es un fallo de calidad: son fallos de ORDEN. Este fichero pone el orden
delante, y falla CERRADO — si algo no cuadra, no se lanza nada.

LO QUE COMPRUEBA (todo sin ejecutar ni un test):

 1. ARBOL LIMPIO. Ningun fichero RASTREADO modificado. Medir sobre un arbol que cambia produce un
    numero que no corresponde a ningun commit, y este proyecto ya retracto uno por eso.
 2. ANCLAS UNICAS. Para cada arnes, cada texto que va a sustituir aparece EXACTAMENTE UNA VEZ en su
    fichero objetivo. Cero ocurrencias = ancla muerta (el arnes dira ANCLA NO UNICA dentro de una
    hora); dos o mas = la mutacion tocaria un sitio que no es el suyo.
 3. TESTS DECLARADOS EXISTENTES. Cada test nombrado por una fila existe en los ficheros de test de
    ese arnes. Un test que no existe no puede fallar con su marcador, asi que su fila no acredita
    nada — y este proyecto ya se comio una fila asi durante una tanda entera.
 4. HUELLA DE `.git/qs-*` y de `data_hist/eco_b`, impresa para poder compararla despues. Tres veces
    han escrito ahi los tests del propio proyecto.
 5. HEAD y rama, impresos, para que encabecen el log de lo que se vaya a lanzar.

LO QUE **NO** ES: no ejecuta tests, no acredita nada y no sustituye a ninguna verificacion. Es una
puerta previa. Todo lo que hoy se corre se sigue corriendo entero.

    python tools/prevuelo.py                 # antes de lanzar suite/arnes/barrido
    python tools/prevuelo.py --arnes ref     # solo un arnes
    python tools/prevuelo.py --permitir-sucio  # cuando se mide A PROPOSITO sobre el arbol de trabajo
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import os
import re
import subprocess
import sys

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(QS))
_AQUI = os.path.join(QS, "tools")

# ARNÉS CONSERVADO (V2 lote 3), con la forma EXACTA de su tabla. Se declaran aqui y no se adivinan: si alguien
# anade un arnes y no lo mete en esta lista, el pre-vuelo NO lo cubre — y eso es preferible a un
# descubrimiento automatico que falle en silencio sobre una forma que no conoce.
#
#   modulo        : fichero bajo tools/
#   tabla         : nombre del atributo con las filas
#   objetivo      : ruta relativa a qs/ del fichero que se muta por defecto
#   objetivo_en   : indice de la fila que lleva un objetivo propio (None si no lo admite)
#   tests_en      : indice de la fila que nombra sus tests
#   ficheros_test : rutas relativas a qs/ donde tienen que existir esos tests
ARNESES = {"ref": {"modulo": "mutacion_ref_valida.py", "tabla": "MUTACIONES",
            "objetivo": os.path.join("analysis", "ref_valida.py"),
            "objetivo_en": 3, "tests_en": 2, "ficheros_test": None}}


def _git(*args) -> tuple:
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip()


def _cargar(nombre_fichero: str):
    """Importa el arnés sin ejecutar su main."""
    ruta = os.path.join(_AQUI, nombre_fichero)
    for p in (_AQUI, QS):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location("_prevuelo_" + nombre_fichero[:-3], ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tests_de(fila, idx):
    """Los tests que la fila declara. Dos formas vivas: un dict {test: marcador} y un str suelto."""
    if idx is None or len(fila) <= idx:
        return []
    v = fila[idx]
    if isinstance(v, dict):
        return list(v)
    if isinstance(v, str):
        return [v]
    return list(v or [])


def _base_nodo(nombre: str) -> str:
    """`test_x[param]` -> `test_x`. Los tests parametrizados se declaran por su base."""
    return nombre.split("[", 1)[0]


_DEF_TEST = re.compile(r"^\s*def\s+(test_\w+)\s*\(", re.M)


def _nombres_de_test(cuerpos) -> list:
    """Los nombres de test REALES de unos ficheros, como los ve pytest."""
    nombres = []
    for c in cuerpos:
        nombres.extend(_DEF_TEST.findall(c))
    return nombres


def _casan(declarado: str, nombres) -> list:
    """Los tests que casarian con lo declarado, con la semantica de `-k`: SUBCADENA.

    Los tres arneses declaran su test de dos formas distintas y las dos son legitimas:
    `ref`/`gate` ponen el nombre COMPLETO como clave de un dict, y `libro` pone una SUBCADENA que
    va a `-k` (p. ej. `M1212_abort_ajeno_no_equivalente` casa con
    `test_M1212_abort_ajeno_no_equivalente_STOP_y_sello_sobrevive`). Comprobar `def <nombre>(`
    marcaba 27 filas VIVAS del arnes del libro como inexistentes: el pre-vuelo habria mentido en su
    primera corrida, que es exactamente la clase de fallo que existe para cazar.
    """
    d = _base_nodo(declarado)
    return [n for n in nombres if d == n or d in n]


def revisar_arnes(clave: str) -> list:
    """Devuelve la lista de PROBLEMAS del arnes (vacia = limpio)."""
    cfg = ARNESES[clave]
    problemas = []
    try:
        mod = _cargar(cfg["modulo"])
    except Exception as e:                                     # noqa: BLE001
        return [f"[{clave}] el arnes NO IMPORTA: {type(e).__name__}: {e}"]
    filas = getattr(mod, cfg["tabla"], None)
    if not filas:
        return [f"[{clave}] no tiene tabla `{cfg['tabla']}` o esta vacia"]

    # ── (2) anclas unicas en su objetivo
    cache = {}
    for fila in filas:
        rel = cfg["objetivo"]
        if cfg["objetivo_en"] is not None and len(fila) > cfg["objetivo_en"]:
            rel = fila[cfg["objetivo_en"]]
        ruta = os.path.join(QS, rel)
        if ruta not in cache:
            try:
                cache[ruta] = io.open(ruta, encoding="utf-8").read()
            except OSError as e:
                cache[ruta] = None
                problemas.append(f"[{clave}] objetivo ILEGIBLE {rel}: {e}")
        texto = cache[ruta]
        if texto is None:
            continue
        for viejo, _nuevo in fila[1]:
            n = texto.count(viejo)
            if n != 1:
                que = "ANCLA MUERTA (0 ocurrencias)" if n == 0 else f"ANCLA AMBIGUA ({n} ocurrencias)"
                problemas.append(f"[{clave}] {que} en {rel} · fila: {fila[0][:88]}")

    # ── (3) tests declarados que existen
    rels = cfg["ficheros_test"] or getattr(mod, "FICHEROS_TEST", ())
    cuerpo = []
    for rt in rels:
        try:
            cuerpo.append(io.open(os.path.join(QS, rt), encoding="utf-8").read())
        except OSError as e:
            problemas.append(f"[{clave}] fichero de test ILEGIBLE {rt}: {e}")
    nombres = _nombres_de_test(cuerpo)
    if nombres:
        for fila in filas:
            for t in _tests_de(fila, cfg["tests_en"]):
                if not _casan(t, nombres):
                    problemas.append(f"[{clave}] TEST DECLARADO QUE NO EXISTE: {t} · fila: {fila[0][:70]}")
    return problemas


def _huella_dir(ruta) -> str:
    """Listado ordenado -> sha256. Detecta altas, bajas y renombrados; no lee contenidos."""
    if not os.path.isdir(ruta):
        return "(no existe)"
    nombres = sorted(os.listdir(ruta))
    h = hashlib.sha256("\n".join(nombres).encode("utf-8")).hexdigest()[:12]
    return f"{len(nombres)} entrada(s) · {h}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arnes", choices=sorted(ARNESES) + ["todos"], default="todos")
    ap.add_argument("--permitir-sucio", action="store_true",
                    help="no exigir arbol limpio (para medir A PROPOSITO sobre el arbol de trabajo)")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    rc_head, head = _git("rev-parse", "HEAD")
    _, rama = _git("rev-parse", "--abbrev-ref", "HEAD")
    _, sucio = _git("status", "--porcelain")
    rastreados = [l for l in sucio.splitlines() if l and not l.startswith("??")]
    _, comun = _git("rev-parse", "--git-common-dir")
    comun_abs = os.path.abspath(os.path.join(REPO, comun)) if comun else None

    print("PRE-VUELO — segundos antes de horas\n")
    print(f"  HEAD        {head or '(sin repositorio)'}")
    print(f"  rama        {rama}")
    print(f"  arbol       {'LIMPIO' if not rastreados else str(len(rastreados)) + ' rastreado(s) MODIFICADO(S)'}")
    for l in rastreados[:10]:
        print(f"                {l}")
    if comun_abs:
        for sub in ("qs-consumo-candidato", "qs-gate-b"):
            print(f"  .git/{sub:<22} {_huella_dir(os.path.join(comun_abs, sub))}")
    print(f"  data_hist/eco_b            {_huella_dir(os.path.join(QS, 'data_hist', 'eco_b'))}")
    print()

    problemas = []
    if rc_head != 0 or not head:
        problemas.append("no se resuelve HEAD: sin repositorio no hay nada que encabece un log")
    if rastreados and not args.permitir_sucio:
        problemas.append(f"{len(rastreados)} fichero(s) RASTREADO(S) modificado(s): medir sobre un arbol "
                         f"que cambia da un numero que no corresponde a ningun commit (E-80). "
                         f"Commitea, guarda o pasa --permitir-sucio a proposito.")

    claves = sorted(ARNESES) if args.arnes == "todos" else [args.arnes]
    for k in claves:
        p = revisar_arnes(k)
        n_filas = "?"
        try:
            n_filas = len(getattr(_cargar(ARNESES[k]["modulo"]), ARNESES[k]["tabla"], []))
        except Exception:                                      # noqa: BLE001
            pass
        print(f"  arnes {k:<6} {n_filas} fila(s) · {'OK' if not p else str(len(p)) + ' PROBLEMA(S)'}")
        problemas.extend(p)

    if problemas:
        print(f"\n*** NO SE LANZA NADA — {len(problemas)} problema(s):")
        for m in problemas:
            print(f"      {m}")
        print("\n*** Cada uno de estos se habria descubierto DENTRO de una corrida larga, con el")
        print("*** tiempo ya gastado. Por eso este chequeo va delante y falla cerrado.")
        return 3
    print("\n  LISTO PARA LANZAR. Encabeza el log con el HEAD de arriba.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
