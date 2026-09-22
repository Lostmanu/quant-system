"""analysis/ref_valida.py — LA validación de precio de referencia. Una sola, compartida por TODOS.

POR QUÉ EXISTE ESTE MÓDULO Y NO UN `if` EN CADA SITIO. El 2026-08-26 se encontró que
`pilot_observer.realized_markouts` aceptaba referencias inválidas: con `ref = 0` devuelve exactamente
`−lado·10.000,00 bps`, que es **finito** y por tanto atraviesa el `isfinite` de toda la cadena y se
promedia como observación legítima. La primera reparación puso el guardia **sólo ahí** y el informe
afirmó que el defecto «vivía en el carril de referencia Binance», porque capa 2 sólo tenía 4 celdas.

La mesa lo rechazó (2026-08-27): **cuatro no es cero**. `maker_sim.markouts` — otra función, otro
carril, otra referencia — tenía el mismo agujero. Una regla implementada dos veces es una regla que
se arregla una vez y se olvida la otra. Aquí hay UNA definición y cinco puntos de llamada la usan:

    analysis/pilot_observer.py:realized_markouts   <- confirm_runner, eco_fase2_wti,
                                                      eco_runner_wti, pilot_runner
    analysis/maker_sim.py:markouts                 <- maker_capa2_runner

LAS CLASES, y por qué son tres y no dos:

  · `no_finita`    NaN, +inf, -inf. No es un precio.
  · `no_positiva`  <= 0, el cero incluido. No es un precio.
  · `degenerada`   finita y positiva, pero con `|markout| >= 9.000 bps` — es decir, la referencia dice
                   que el activo perdió o ganó más del 90 % respecto del precio del fill entre el
                   fill y el instante de referencia. Eso no es un markout, es un dato roto. La decisión
                   se toma sobre el MARKOUT, no sobre un ratio: ver `LIMITE_ABSURDO_BPS` y por qué.

**LA TERCERA CLASE ES POSTERIOR AL CENSO, Y SE DECLARA ASÍ.** La regla original (`docs/`, especificación
post-incidente) sólo rechazaba lo no finito y lo no positivo, y contaba —sin filtrar— lo que cayera
fuera de la banda. Estaba mal, y lo señaló la mesa por implicación: **un `ref` positivo diminuto
(`1e-9`) es finito y positivo, produce la misma firma de −10.000 bps y habría pasado el guardia.**

Se endurece tras comprobar que el cambio es un **no-op demostrable** sobre los datos existentes:

    celdas con firma exacta `-lado*1e4` .......... 15.540
    celdas |mo| >= 9.000 que NO son esa firma .....      0
    celdas 3.000 <= |mo| < 9.000 .................      0
    celdas 1.000 <= |mo| < 3.000 .................     79   (movimientos reales del 10-30 %)

es decir, rechazar lo degenerado echa exactamente las mismas 15.540 que ya echaba R1 y ni una más. Se
endurece porque cierra un agujero futuro sin mover ningún resultado presente — no porque mejore
ninguna cifra. **Decidido DESPUÉS de mirar el censo; se dice, no se disfraza de anterior.**

LO QUE ESTE MÓDULO NO HACE. No filtra por plausibilidad económica. El límite de 9.000 bps no es una
opinión sobre qué movimiento es razonable para LIT: es la frontera donde el markout deja de ser un
markout —±90 % en el horizonte de medida—. Una banda estrecha (5 %, 20 %) SÍ sería un filtro
post-dato capaz de mover resultados, y está prohibida sin su propio pre-registro con umbral
justificado antes del dato. El de aquí es un no-op demostrable: 0 celdas con `|mo| >= 9.000` que no
sean la firma exacta, y 0 entre 3.000 y 9.000.
"""
from __future__ import annotations

import numpy as np

# EL LÍMITE SE DECLARA EN LAS UNIDADES QUE IMPORTAN — bps de markout — y la banda de ratio se DERIVA.
#
# La primera versión hizo lo contrario: fijó la banda a mano en [0,1 ; 10] y afirmó que fuera de ella
# «|markout| >= 9.000 bps». **Era falso en la mitad superior.** Como `mo = (ref/px - 1)·1e4`, el borde
# inferior 0,1 da −9.000 bps, pero el superior 10 da **+90.000**: la regla toleraba markouts diez
# veces más absurdos por arriba que por abajo, con una justificación escrita que no se sostenía.
#
# Lo encontró el falsificador por propiedades (`tests/propiedades.py`) en su PRIMERA corrida, con
# `ref = 45,68 · px = 6,13` (ratio 7,45 → +64.500 bps, clasificado «ok»). Ningún test por ejemplo lo
# miraba, porque nadie escribe ese par a mano. Queda registrado como E-51.
#
# Y EL PRIMER ARREGLO TAMPOCO VALIA. Derivar `BANDA_MIN = 1.0 - 0.9` y `BANDA_MAX = 1.0 +
# 0.9` parece simetrico y NO lo es en float64: `1.0 - 0.9 = 0.09999999999999998` pero `1.0 + 0.9 =
# 1.9` exacto. El ratio 0,1 quedaba DENTRO y el 1,9 FUERA — la misma asimetria de E-51, ahora por
# representacion en vez de por aritmetica mental. Lo cazo el test de simetria escrito para el primer
# arreglo, antes de que saliera del banco.
#
# La forma correcta no compara ratios: compara EL MARKOUT, que es la unidad en la que esta enunciada
# la regla. `abs()` hace la simetria imposible de romper por construccion, y no hay dos constantes
# que puedan divergir.
LIMITE_ABSURDO_BPS = 9_000.0            # |markout| >= esto no es un markout: es un dato roto


def markout_bps(ref: float, px: float) -> float:
    """El markout SIN signo de lado, en bps. Una sola definicion de la formula, aqui."""
    return (float(ref) / float(px) - 1.0) * 1e4


def banda():
    """Los bordes de ratio EQUIVALENTES al limite, solo para informar y documentar. La decision NO
    los usa — se toma sobre el markout — para que no puedan divergir de `LIMITE_ABSURDO_BPS`."""
    return (1.0 - LIMITE_ABSURDO_BPS / 1e4, 1.0 + LIMITE_ABSURDO_BPS / 1e4)


CLASES = ("ok", "no_finita", "no_positiva", "degenerada")
CLASES_RECHAZO = ("no_finita", "no_positiva", "degenerada")


def clasificar(ref, px) -> str:
    """Clasifica UNA referencia contra el precio del fill. Devuelve una de `CLASES`.

    El orden importa y es el que hace el diagnóstico legible: primero lo que no es un número, luego
    lo que no es un precio, y sólo al final la relación con `px`. Invertirlo etiquetaría un `NaN`
    como «degenerada», que no dice nada de lo que pasó."""
    r = float(ref)
    if not np.isfinite(r):
        return "no_finita"
    if r <= 0.0:
        return "no_positiva"
    p = float(px)
    if not np.isfinite(p) or p <= 0.0:
        return "no_finita" if not np.isfinite(p) else "no_positiva"
    # Sobre el MARKOUT, no sobre el ratio: `abs()` hace la simetria imposible de romper. ESTRICTO en
    # el borde — ahi el markout YA vale +-9.000 bps, que es el limite de lo absurdo, no un valor bueno.
    return "ok" if abs(markout_bps(r, p)) < LIMITE_ABSURDO_BPS else "degenerada"




def contadores_vacios(n_horizontes: int) -> dict:
    """Contadores POR CAUSA. Nunca un total agregado: «no había referencia cerca en el tiempo» y «la
    referencia que había estaba rota» son diagnósticos distintos, y mezclarlos volvería a esconder
    exactamente el defecto que este módulo existe para impedir."""
    return {c: np.zeros(n_horizontes, dtype="int64")
            for c in ("sin_tfill", "px_invalido", "tiempo",
                      "ref_no_finita", "ref_no_positiva", "ref_degenerada")}


def total_rechazos_ref(cnt: dict, k: int) -> int:
    """Los rechazos por REFERENCIA en el horizonte k. R4 cuenta esto, no sólo una de las tres clases."""
    return int(cnt["ref_no_finita"][k] + cnt["ref_no_positiva"][k] + cnt["ref_degenerada"][k])


# ---------------------------------------------------------------------------------------------
# DETECCIÓN EN ARTEFACTOS YA ESCRITOS
#
# Arreglar el productor no sanea lo ya producido. Los npz históricos siguen conteniendo celdas de
# ±10.000 bps y cualquier consumidor las promedia tan contento. La mesa lo señaló (2026-08-27) como
# ruta abierta: «los artefactos históricos contaminados siguen siendo consumibles aguas abajo».
#
# LA FIRMA, y por qué ésta y no `abs(mo) >= 9999.99`. La primera versión usó el valor absoluto, que
# también captura `ref ≈ 2·px` y cualquier movimiento superior al 100 %: no era una prueba. La firma
# correcta es de SIGNO, y es una equivalencia exacta dada la fórmula del markout:
#
#     mo == -lado*1e4   <=>   (ref - px)/px == -1   <=>   ref == 0
#
# Se distinguen DOS clases, porque no acreditan lo mismo:
#   · EXACTA    `mo` es bit a bit `-lado*1e4`  => la referencia era CERO. Acreditado.
#   · CASI-CERO dentro de tolerancia pero no bit-exacta => la referencia era positiva y diminuta
#                (`ref/px <~ 1e-6`). Es igual de inservible, pero NO es un cero y no se dice que lo sea.
# En los bloques del programa a 2026-08-27: 15.540 exactas y CERO casi-cero. Eso es un hecho de esos
# datos, no una propiedad del detector.

def contaminacion(mo, lado, *, tol: float = 0.01) -> dict:
    """Cuenta celdas con firma de referencia nula en un `mo` ya escrito. Devuelve exacta/casi/total."""
    mo = np.asarray(mo, dtype="float64")
    lado = np.asarray(lado, dtype="float64")
    if mo.ndim == 1:
        mo = mo[:, None]
    objetivo = -lado[:, None] * 1e4
    fin = np.isfinite(mo)
    exacta = fin & (mo == objetivo)
    cerca = fin & np.isclose(mo, objetivo, atol=tol, rtol=0.0)
    return dict(exacta=int(exacta.sum()), casi=int((cerca & ~exacta).sum()),
                total=int(cerca.sum()), finitos=int(fin.sum()))


def exigir_limpio(mo, lado, etiqueta: str, *, permitir: bool = False) -> dict:
    """Rechaza consumir un artefacto contaminado. `permitir=True` es el escape FORENSE explícito."""
    c = contaminacion(mo, lado)
    if c["total"] and not permitir:
        raise RuntimeError(
            f"ARTEFACTO CONTAMINADO: {etiqueta} tiene {c['total']} celdas con firma de referencia nula "
            f"({c['exacta']} exactas, {c['casi']} casi-cero) de {c['finitos']} finitas.\n"
            f"Se produjeron ANTES del guardia de `analysis/ref_valida.py` y promediarlas mueve el "
            f"resultado varios bps. Arreglar el productor no sanea lo ya escrito: hay que RE-DERIVAR.\n"
            f"Para un análisis FORENSE consciente, pasa `permitir=True` — y entonces lo que salga es "
            f"exploratorio, no confirmatorio.")
    return c


UMBRAL_R4 = 0.05        # fracción de eventos rechazados por REFERENCIA que dispara la anomalía


def linea_r4(cnt: dict, n_eventos: int, k: int, delta_ms: int, umbral: float = UMBRAL_R4):
    """R4 como FUNCIÓN PURA, no como un `print` enterrado en un runner.

    La primera versión (2026-08-26) metía este aviso directamente en `confirm_runner`, contaba sólo
    UNA de las tres clases de rechazo y no cubría a los otros tres llamadores. La mesa lo señaló como
    no load-bearing: un aviso que no se puede invocar desde un test no se puede acreditar, y uno que
    vive en un solo llamador no protege a los demás.

    Devuelve `None` si no hay nada que decir, o la línea a imprimir. Quien la llame decide dónde
    escribirla; lo que NO puede es reimplementar el criterio."""
    n_ref = total_rechazos_ref(cnt, k)
    if not n_ref:
        return None
    frac = n_ref / max(int(n_eventos), 1)
    marca = "[R4] ANOMALÍA" if frac > umbral else "[R1]"
    detalle = " · ".join(f"{c.replace('ref_', '')}={int(cnt[c][k])}"
                         for c in ("ref_no_finita", "ref_no_positiva", "ref_degenerada")
                         if int(cnt[c][k]))
    return (f"{marca}: Δ={delta_ms}ms · {n_ref} de {n_eventos} eventos descartados por REFERENCIA "
            f"({100.0 * frac:.3f}%) · {detalle}")
