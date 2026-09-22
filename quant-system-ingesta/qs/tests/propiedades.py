"""FALSIFICADOR POR PROPIEDADES — genera entradas adversariales y busca el contraejemplo.

POR QUÉ EXISTE, y es la clase de instrumento que faltaba. El registro del método mide qué encuentra
cada instrumento: leer (revisor externo, 19), revisarse (autor, 15), refutar (revisión adversarial,
12), ejecutar (arnés de mutación, 3). Ninguno de los cuatro genera **entradas**. Y dos defectos del
2026-08-27 son exactamente eso — «quien escribió el test no pensó en ese valor»:

  · E-43 — el guardia exigía `finito and > 0`, así que un `ref = 1e-9` seguía produciendo −10.000 bps.
    El caso central sobrevivió a su propia reparación porque nadie escribió ese ejemplo.
  · E-48 — el recibo del censo hacía hash de la lista ORDENADA de SHA, así que **permutar dos hashes
    entre rutas lo dejaba idéntico**. Nadie escribió el ejemplo «permuta y compara».

Un test por EJEMPLO comprueba los casos que a su autor se le ocurrieron. Una propiedad comprueba una
afirmación sobre TODO un dominio, y el generador se encarga de traer lo que a nadie se le ocurrió.

POR QUÉ NO `hypothesis`. Añadirla obliga a tocar `requirements-lock.txt`, que fija las versiones
exactas del CI verde; arriesgar ese verde para ganar comodidad sería justo lo contrario del encargo.
Esto es más pobre a propósito —no encoge contraejemplos ni aprende— pero hace lo único que hacía
falta: **traer los valores que nadie escribe a mano**, de forma DETERMINISTA y reproducible.

LA SEMILLA ES PARTE DEL CONTRATO. `SEMILLA` está fija: dos corridas dan exactamente los mismos casos,
así que un fallo en CI se reproduce en local con el índice del caso. Cambiarla es cambiar el
experimento, y por la disciplina de la casa eso se declara, no se hace en silencio.
"""
from __future__ import annotations

import random

SEMILLA = 20260827          # CONGELADA. Cambiarla = cambiar el experimento; se declara.
N_CASOS = 400               # por propiedad; barato (milisegundos) y suficiente para estos dominios


# ---------------------------------------------------------------------------------------------
# DOMINIOS. Los valores «raros» NO son aleatorios: son la lista de lo que rompe código numérico,
# escrita a mano y SIEMPRE incluida. Lo aleatorio se añade encima para cubrir lo que no está aquí.
# ---------------------------------------------------------------------------------------------
PATOLOGICOS = (
    0.0, -0.0, float("nan"), float("inf"), float("-inf"),
    1e-323, 5e-324, 1e-300, 1e-9, 1e-6,          # positivos que NO son cero pero se le parecen
    -1e-9, -1.0, -100.0,
    1e300, 1e18, 1e9,                             # absurdamente grandes
    0.1, 10.0,                                    # los BORDES exactos de la banda con px=1
)


def _rng():
    return random.Random(SEMILLA)


def precios(rng, n):
    """Precios de fill plausibles + los patológicos. Un `px` roto también tiene que estar cubierto."""
    out = list(PATOLOGICOS)
    while len(out) < n:
        e = rng.choice((-6, -3, -1, 0, 1, 3, 6))
        out.append(rng.uniform(1.0, 10.0) * (10.0 ** e))
    return out[:n]


def referencias(rng, n, px_ref=100.0):
    """Referencias: patológicos SIEMPRE, más ratios alrededor de los bordes de la banda [0,1 ; 10].

    Los ratios se concentran a propósito cerca de 0,1 y 10 — un `off-by-epsilon` en la frontera es el
    fallo que un generador uniforme casi nunca visita y que un revisor humano nunca escribe."""
    out = list(PATOLOGICOS)
    bordes = (0.1, 10.0)
    while len(out) < n:
        t = rng.random()
        if t < 0.35:
            b = rng.choice(bordes)
            out.append(px_ref * b * (1.0 + rng.choice((-1, 1)) * 10 ** rng.uniform(-12, -1)))
        elif t < 0.6:
            out.append(px_ref * 10 ** rng.uniform(-12, 12))
        else:
            out.append(px_ref * rng.uniform(0.5, 2.0))
    return out[:n]


def lados(rng, n):
    return [rng.choice((True, False)) for _ in range(n)]


# ---------------------------------------------------------------------------------------------
def para_todo(propiedad, casos, etiqueta=""):
    """Ejecuta `propiedad(caso)` sobre cada caso. Devuelve el PRIMER contraejemplo, o None.

    Devuelve el caso entero, no un booleano: un contraejemplo que no dice CUÁL entrada lo produjo
    obliga a adivinar, y adivinar es lo que este instrumento existe para evitar. Una propiedad que
    revienta con una excepción también cuenta como contraejemplo — «no debería explotar» es parte de
    lo que se afirma."""
    for i, caso in enumerate(casos):
        try:
            ok = propiedad(caso)
        except Exception as e:                      # noqa: BLE001 — explotar ES un contraejemplo
            return dict(indice=i, caso=caso, motivo=f"{type(e).__name__}: {e}", etiqueta=etiqueta)
        if not ok:
            return dict(indice=i, caso=caso, motivo="la propiedad NO se cumple", etiqueta=etiqueta)
    return None


def exigir(propiedad, casos, etiqueta):
    """`para_todo` + aserción con el contraejemplo dentro del mensaje. Para usar desde un test."""
    ce = para_todo(propiedad, casos, etiqueta)
    assert ce is None, (
        f"CONTRAEJEMPLO en «{etiqueta}» (semilla {SEMILLA}, caso #{ce['indice']}):\n"
        f"  entrada: {ce['caso']!r}\n"
        f"  motivo : {ce['motivo']}\n"
        f"  reproducir: mismo SEMILLA y mismo indice — este falsificador es determinista.")


def casos_ref_px(n=N_CASOS, px_base=100.0):
    """Pares (ref, px) cruzando referencias patológicas con precios de fill patológicos."""
    rng = _rng()
    refs, pxs = referencias(rng, n, px_base), precios(rng, n)
    return [(refs[i], pxs[i % len(pxs)]) for i in range(n)]


def casos_ref_px_lado(n=N_CASOS, px_base=100.0):
    rng = _rng()
    refs, pxs, lds = referencias(rng, n, px_base), precios(rng, n), lados(rng, n)
    return [(refs[i], pxs[i % len(pxs)], lds[i]) for i in range(n)]

