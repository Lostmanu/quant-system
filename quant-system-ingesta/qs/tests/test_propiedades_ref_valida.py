"""Propiedades conservadas del clasificador, fórmula y detector de referencia.

La consecuencia se contrasta con la fórmula de producción y el límite independiente
de la prueba. Se retiran propiedades de los productores y recibos que ya no existen.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import propiedades as P                                                # noqa: E402
from analysis import ref_valida as RV                                  # noqa: E402

D = (5_000,)
LIMITE_ABSURDO = 9_000.0        # |markout| >= esto no es un markout, es un dato roto




# =============================================================== LA propiedad central (E-43)
def test_PROPIEDAD_ninguna_referencia_aceptada_produce_un_markout_absurdo():
    """∀ (ref, px): si `clasificar` dice «ok», el markout resultante es finito y |mo| < 9.000 bps.

    Es la propiedad que E-43 violaba. Y está enunciada sobre la CONSECUENCIA, no sobre el tipo del
    dato: da igual que `ref` sea finito y positivo si el número que produce no es un markout."""
    def prop(caso):
        ref, px = caso
        if RV.clasificar(ref, px) != "ok":
            return True
        v = RV.markout_bps(ref, px)
        return math.isfinite(v) and abs(v) < LIMITE_ABSURDO

    P.exigir(prop, P.casos_ref_px(), "ok => markout finito y no absurdo")




def test_PROPIEDAD_clasificar_es_TOTAL_y_solo_devuelve_clases_declaradas():
    """Nunca explota y nunca inventa una clase. Un `KeyError` aguas abajo por una clase no declarada
    convertiría un descarte en una caída del runner a mitad de una corrida de horas."""
    def prop(caso):
        ref, px = caso
        return RV.clasificar(ref, px) in RV.CLASES

    P.exigir(prop, P.casos_ref_px(), "clasificar total")




# =============================================================== paridad entre implementaciones




# =============================================================== cuadre R3 (metamórfica)


# =============================================================== el recibo (E-48)




# =============================================================== deteccion de contaminacion
def test_PROPIEDAD_solo_lo_BIT_EXACTO_cuenta_como_cero_acreditado():
    """∀ valor: se cuenta como EXACTA sólo si es bit a bit `-lado·1e4`. Lo demás, como mucho, casi-cero.

    Es la sobreafirmación que la mesa señaló —15.540 presentados como «ceros» cuando el detector sólo
    acreditaba «compatibles»— convertida en propiedad."""
    rng = P._rng()

    def prop(k):
        lado = 1.0 if k % 2 else -1.0
        objetivo = -lado * 1e4
        delta = rng.choice((0.0, 1e-9, 0.005, 0.02, 1.0, -0.005))
        v = objetivo + delta
        c = RV.contaminacion(np.array([[v]]), np.array([lado]))
        return c["exacta"] == (1 if v == objetivo else 0)

    P.exigir(prop, list(range(P.N_CASOS)), "exacta <=> bit-exacto")