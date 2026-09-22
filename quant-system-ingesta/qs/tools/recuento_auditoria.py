"""Regenera el §2 de `docs/AUDITORIA_DEL_METODO.md` DESDE SUS TABLAS. Nadie teclea el recuento.

**Por qué existe.** El §2 de ese documento llegó a decir tres cifras distintas a la vez: 33 en la
cabecera, 26 en la conclusión y 22 en la tabla de descubridores. El propio documento avisaba de que
el recuento iba a mano — y esa nota no lo arreglaba, solo lo declaraba. Es exactamente el defecto que
`tools/medida.py` existe para impedir («el número deja de escribirlo quien informa»), vivo dentro del
documento que lo diagnostica. Lo señaló un revisor externo, contando las filas él mismo.

**Qué hace.** Parsea **todas** las tablas del registro (§1.1, §1.2 y las que se añadan después,
como §1.5), cuenta filas y descubridores,
y reescribe el bloque entre los marcadores. El resto del fichero no se toca.

    python tools/recuento_auditoria.py            # reescribe el bloque
    python tools/recuento_auditoria.py --check    # solo dice si esta al dia (para CI)
"""
import argparse
import io
import os
import re
import sys

_AQUI = os.path.abspath(__file__)                       # …/quant-system-ingesta/qs/tools/<este>
_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_AQUI))))
DOC = os.path.join(_RAIZ, "docs", "AUDITORIA_DEL_METODO.md")
INI = "<!-- RECUENTO:INICIO — generado por tools/recuento_auditoria.py, NO editar a mano -->"
FIN = "<!-- RECUENTO:FIN -->"

# la 4ª columna de §1.1 y de §1.2 es el descubridor; se normaliza quitando negritas y notas
_LIMPIA = re.compile(r"\*\*|`|\(|\)")


_ESCAPADO = "\x00"          # marcador interno para `\|`, que NO separa columnas


def _filas(texto, prefijo):
    """Filas de tabla cuyo primer campo es el id (E-01, X-03...). Devuelve [(id, descubridor)].

    Un `\\|` dentro de una celda es un pipe ESCAPADO de Markdown y no separa columnas. Partir por
    `|` a secas descoloca la fila entera y atribuye el descubridor equivocado — pasó en la primera
    ejecución de este generador, con la celda que contiene `systemctl list-timers \\| head -8`. Un
    contador con un bug de parseo es exactamente lo que este fichero no puede ser.
    """
    out = []
    for linea in texto.split("\n"):
        if not linea.startswith("| " + prefijo):
            continue
        campos = [c.strip().replace(_ESCAPADO, "|")
                  for c in linea.replace("\\|", _ESCAPADO).strip().strip("|").split("|")]
        if len(campos) < 4:
            continue
        out.append((campos[0], _LIMPIA.sub("", campos[3]).strip()))
    return out


def _exigir_ids_unicos(e, x):
    """Un id DUPLICADO corrompe en silencio cualquier recuento y cualquier referencia cruzada: dos
    filas distintas responden al mismo nombre y quien cite «E-25» no sabe a cuál se refiere.

    Pasó: al añadir el bloque de 2026-08-25 se reusó `E-25`, que ya existía desde el 2026-08-23. El
    documento publicó **34** cuando tenía **44** filas, y el generador —que existe justamente para
    que ese número no se teclee a mano— no lo cazó porque **nadie lo volvió a invocar**. Lo cazó la
    mesa, a mano. Este control convierte ese fallo en imposible de publicar: aquí se para.
    """
    ids = [i for i, _ in e + x]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit(
            f"IDS DUPLICADOS EN EL REGISTRO: {', '.join(dup)}\n"
            "Dos filas con el mismo id hacen ambigua toda referencia cruzada y falsean el recuento.\n"
            "Renumera la entrada MÁS NUEVA (las entradas no se borran: regla 4 del §0) y reejecuta.")


def recuento(texto):
    e, x = _filas(texto, "E-"), _filas(texto, "X-")
    _exigir_ids_unicos(e, x)
    tally = {}
    for _, d in e + x:
        clave = d.split(",")[0].split("+")[0].strip() or "(sin descubridor)"
        tally[clave] = tally.get(clave, 0) + 1
    return e, x, tally


def bloque(e, x, tally):
    L = [INI, "",
         f"De **{len(e) + len(x)} afirmaciones falsas** registradas "
         f"(**{len(e)}** del autor, **{len(x)}** del revisor externo):", "",
         "| descubridor | nº |", "|---|---|"]
    for k, v in sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| {k} | {v} |")
    L += [f"| **TOTAL** | **{sum(tally.values())}** |", "",
          "> *Este bloque lo genera `tools/recuento_auditoria.py` desde **todas** las tablas del*",
          "> *registro (§1.1, §1.2, §1.5 y las que se añadan). Rechaza publicar si hay un id duplicado.*",
          "> *Llegó a decir tres cifras distintas a la vez cuando se mantenía a mano; lo cazó un*",
          "> *revisor externo contando las filas. Si el total de la tabla no cuadra con la suma de*",
          "> *las filas, el fallo está en el generador o en el formato de una fila — no en el número.*",
          "", FIN]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="no escribe; rc=1 si esta desactualizado")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    t = io.open(DOC, encoding="utf-8").read()
    e, x, tally = recuento(t)
    nuevo = bloque(e, x, tally)
    print(f"  filas E-* (autor) ........ {len(e)}")
    print(f"  filas X-* (revisor) ...... {len(x)}")
    print(f"  TOTAL .................... {len(e) + len(x)}")
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"     {k:34} {v}")

    if INI not in t or FIN not in t:
        print(f"\n  los marcadores no estan en el documento; insertalos donde deba ir el recuento:\n"
              f"  {INI}\n  {FIN}")
        return 2
    ini, fin = t.index(INI), t.index(FIN) + len(FIN)
    if t[ini:fin] == nuevo:
        print("\n  RECUENTO AL DIA")
        return 0
    if args.check:
        print("\n  RECUENTO DESACTUALIZADO — corre sin --check para regenerarlo")
        return 1
    io.open(DOC + ".tmp", "w", encoding="utf-8", newline="\n").write(t[:ini] + nuevo + t[fin:])
    os.replace(DOC + ".tmp", DOC)
    print("\n  recuento REGENERADO desde las tablas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
