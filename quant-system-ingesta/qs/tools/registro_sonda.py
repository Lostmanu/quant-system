"""REGISTRO DE LA SONDA — un identificador, una función ejecutable, y nadie gasta antes de resolverla.

POR QUÉ (mesa, 2026-08-28, cierre mínimo): *«La sonda necesita un registro único ID → función
ejecutable, utilizado realmente antes del primer crédito.»*

Lo que había era una declaración en un comentario del prerregistro (`C1=analysis/mod.py:regla_uno`)
comprobada por AST. Eso acredita que **existe un símbolo con ese nombre** — y ni siquiera eso hacía
bien: hasta hoy una variable LOCAL dentro de otra función la satisfacía (E-71). Pero aunque el AST
fuese perfecto, seguiría sin acreditar lo que importa: que esa función se pueda **importar** y que
alguien la **llame**. Un identificador que nadie invoca es documentación, no implementación.

LAS TRES PROPIEDADES, y son distintas:

  1. **UNA fuente.** El registro y el `IDS-IMPLEMENTADOS` del prerregistro tienen que coincidir en
     los dos sentidos. Dos listas que se parecen es E-49, y ya ha pasado dos veces esta semana: el
     productor del eco sellaba unos campos y su gate comprobaba otros.
  2. **RESOLUBLE de verdad.** `resolver()` importa el módulo y comprueba que el atributo existe y es
     invocable. Un AST no distingue una función de un nombre; un import sí.
  3. **ANTES del primer crédito.** `exigir_listo()` se llama al arrancar la sonda, antes de tocar la
     red. Si algo no resuelve, no se gasta.

ESTADO HOY: el registro está **VACÍO**, y es el estado correcto. La sonda no está implementada, así
que `guardia_documental.py --exigir PREREG_SONDA_COBERTURA.md` devuelve `rc=2` con sus 13 reglas sin
ligar y la sonda **no puede correr**. Que lo impida una máquina y no un acuerdo es justamente el
punto: los controles que hay que acordarse de respetar mueren por desuso.

    python tools/registro_sonda.py            # qué hay registrado y qué resuelve
"""
from __future__ import annotations

import importlib
import os
import sys

QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ReglaNoEjecutable(RuntimeError):
    """Clase propia: un `except Exception` de más arriba no puede confundirla con un fallo de E/S."""


# ═══ EL REGISTRO. id -> "modulo.python:funcion". Se añade una entrada CUANDO la función existe, no
# cuando se planea. Vacío hoy, y esa es la verdad del estado del proyecto.
REGLAS: dict = {}

DOC_SONDA = "PREREG_SONDA_COBERTURA.md"


def resolver(ident: str):
    """La función ejecutable de `ident`. Levanta `ReglaNoEjecutable` con el motivo exacto."""
    if ident not in REGLAS:
        raise ReglaNoEjecutable(
            f"`{ident}` no está en el registro. Una regla que nadie puede invocar es documentación, "
            f"no implementación — y con ella la sonda no arranca.")
    destino = REGLAS[ident]
    if ":" not in destino:
        raise ReglaNoEjecutable(f"`{ident}` -> `{destino}`: falta `modulo:funcion`")
    mod_nombre, fn_nombre = destino.rsplit(":", 1)
    if QS not in sys.path:
        sys.path.insert(0, QS)
    try:
        mod = importlib.import_module(mod_nombre)
    except Exception as e:                                  # noqa: BLE001 — el motivo viaja al mensaje
        raise ReglaNoEjecutable(f"`{ident}` -> `{destino}`: el módulo no importa ({e!r})")
    fn = getattr(mod, fn_nombre, None)
    if fn is None:
        raise ReglaNoEjecutable(f"`{ident}` -> `{destino}`: el módulo no define `{fn_nombre}`")
    if not callable(fn):
        raise ReglaNoEjecutable(
            f"`{ident}` -> `{destino}`: `{fn_nombre}` existe pero NO es invocable. Un AST no "
            f"distingue una función de un nombre suelto; un import sí, y por eso esto se resuelve "
            f"importando y no leyendo.")
    return fn


def exigir_listo(ids) -> dict:
    """Resuelve TODAS las reglas o levanta. Se llama ANTES de gastar el primer crédito.

    Devuelve {id: función}. Se resuelven todas de golpe y no una a una bajo demanda: descubrir a
    mitad de la campaña que la quinta regla no importa deja media campaña gastada y ningún
    resultado utilizable."""
    fallos, resueltas = [], {}
    for ident in sorted(ids):
        try:
            resueltas[ident] = resolver(ident)
        except ReglaNoEjecutable as e:
            fallos.append(str(e))
    if fallos:
        raise ReglaNoEjecutable(
            "LA SONDA NO ARRANCA — reglas sin implementación ejecutable:\n  · " +
            "\n  · ".join(fallos) +
            "\n\nEsto se comprueba ANTES de tocar la red: gastar bajo un protocolo a medio "
            "implementar produce un resultado que nadie puede verificar después.")
    return resueltas


def cuadra_con_el_prerregistro(declaradas) -> list:
    """El registro y el `IDS-IMPLEMENTADOS` del prerregistro tienen que decir LO MISMO.

    En los dos sentidos: una regla registrada que el documento no declara es código sin norma, y una
    declarada que no está registrada es norma sin código. Las dos son la misma clase de mentira."""
    problemas = []
    for ident in sorted(set(declaradas) - set(REGLAS)):
        problemas.append(f"`{ident}` lo declara el prerregistro y NO está en el registro: norma sin "
                         f"código.")
    for ident in sorted(set(REGLAS) - set(declaradas)):
        problemas.append(f"`{ident}` está en el registro y el prerregistro NO lo declara: código sin "
                         f"norma.")
    return problemas


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    print("REGISTRO DE LA SONDA — id -> función ejecutable\n")
    if not REGLAS:
        print("  VACÍO. La sonda no está implementada, así que no puede correr — y lo impide una")
        print("  máquina, no un acuerdo. `guardia_documental.py --exigir` devuelve rc=2.")
        return 0
    malas = 0
    for ident in sorted(REGLAS):
        try:
            resolver(ident)
            print(f"  {ident:6} -> {REGLAS[ident]}  OK")
        except ReglaNoEjecutable as e:
            print(f"  {ident:6} *** {e}")
            malas += 1
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
