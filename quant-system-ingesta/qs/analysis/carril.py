"""analysis/carril.py — CONFORMIDAD DEL CARRIL DE REFERENCIA. Una sola regla, productores y consumidores.

EL DEFECTO QUE CIERRA. El pre-registro congelado manda, para un símbolo con identidad CERTIFICADA,
el **mid de Binance** como `precio_ref` en todos los horizontes. El código usa el **trade más cercano**.
Es un incumplimiento de ESTIMANDO, no una errata.

POR QUÉ ESTE MÓDULO Y NO UN `if` EN `confirm_runner`. Porque eso fue exactamente el primer intento, y
la mesa lo tumbó el 2026-08-27:

  · la compuerta cubría **un** productor de tres. `pilot_runner` y —peor— `eco_runner_lit`, que es el
    **productor prospectivo oficial**, seguían pudiendo escribir npz no conformes;
  · el escape forense permitía producir el npz y la no-conformidad quedaba **sólo** en un JSON lateral
    que ningún consumidor exigía;
  · y el npz se escribía **antes** que el lateral, así que un crash entre medias dejaba un artefacto
    sin marca — y `main` omite los npz que ya existen, de modo que la marca no volvía a intentarse.
    Un artefacto calculado contra trades podía pasar por decisivo.

LAS TRES PIEZAS, y el orden importa:

ESTE MÓDULO SÓLO DICE QUÉ CARRIL TOCA Y SI EL USADO LO CUMPLE. La acreditación del artefacto —hash de
los bytes, procedencia, publicación atómica y rechazo en consumo— vive en `analysis/artefacto.py`, que
llama aquí para RECALCULAR la conformidad. Tener las dos cosas en dos sitios fue la primera versión, y
mantener dos mecanismos de acreditación en paralelo es exactamente la duplicación de E-49.

La compuerta de producción se ata al **directorio canónico** y no a la función: lo que hace peligroso
a un artefacto es *dónde acaba*, no quién lo generó — y así los tests que producen en un temporal
(identidad-byte M-10) siguen corriendo sin tocarlos.

LO QUE ESTE MÓDULO NO DECIDE. Qué carril es el correcto para cada capa: eso lo dice el pre-registro de
cada una. Capa 2 marca contra prints de Lighter **por diseño** (§5 de `PREREG_MAKER_LIGHTER`) y es
conforme a su propio prereg; el piloto y la confirmación exigen mid de Binance para certificados. Aquí
sólo se registra qué se usó, qué se exigía, y si coinciden.
"""
from __future__ import annotations

import io
import json
import os

# ---------------------------------------------------------------------------------------------
# CARRILES. Nombres estables: acaban escritos en la marca y una marca vieja tiene que seguir siendo
# legible dentro de un año.
MID_BINANCE = "mid_binance"
TRADE_BINANCE = "trade_mas_cercano_binance"
PRINTS_LIGHTER = "prints_lighter"

# Símbolos con identidad CERTIFICADA (ρ retornos-5m ≥ 0,95): el prereg les exige mid.
CERTIFICADOS = ("LIT", "DOGE")

VAR_ESCAPE = "QS_CARRIL_NO_CONFORME"      # escape EXPLÍCITO, sólo para reproducción forense


class CarrilNoConforme(RuntimeError):
    """Excepción PROPIA, y no un `RuntimeError` cualquiera, por un motivo concreto.

    `confirm_runner.main` envolvía cada día en `except Exception` y convertía el fallo en una línea
    impresa: una corrida bloqueada por incumplimiento normativo seguía adelante día tras día,
    gastando créditos, e imprimía «PRIMARIA COMPLETA» terminando en 0. Con una clase propia, el
    llamador puede —y debe— dejarla pasar. Lo señaló la mesa (2026-08-27, P0-2)."""


def exigido_para(sym: str, capa: str) -> str:
    """Qué carril exige el pre-registro para `sym` en `capa`. Una sola tabla, aquí.

    `capa` es 'piloto' | 'confirmacion' | 'eco' | 'capa2'. Las tres primeras comparten el carril
    certificado (mid de Binance); capa 2 marca contra prints del propio Lighter por diseño."""
    if capa == "capa2":
        return PRINTS_LIGHTER
    return MID_BINANCE if sym in CERTIFICADOS else PRINTS_LIGHTER


def conforme(sym: str, capa: str, usado: str) -> bool:
    return usado == exigido_para(sym, capa)





# La raiz del paquete. Se ancla AQUI y no al cwd: ver `_absoluta`.
_QS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _absoluta(ruta: str) -> str:
    """Ancla una ruta relativa a la RAIZ DEL PAQUETE, nunca al directorio de trabajo.

    EL DEFECTO QUE ARREGLA (mesa 2026-08-29, P0-2). Todos los `OUT_DIR_CANONICO` del programa son
    rutas RELATIVAS, y `os.path.realpath` resuelve lo relativo contra el **cwd**. Ejecutando desde
    cualquier otro directorio, el canonico apuntaba a un sitio inexistente, el destino absoluto no
    caia dentro, y la compuerta AUTORIZABA un carril no conforme sobre el directorio oficial. La
    compuerta dependia de desde donde se lanzara el proceso, que es la peor clase de dependencia:
    invisible y ambiental."""
    return ruta if os.path.isabs(ruta) else os.path.join(_QS, ruta)


def _es_canonico(destino: str, canonico: str) -> bool:
    # `normcase` ademas de `realpath`: en Windows el mismo directorio se escribe con mayusculas
    # distintas y con separadores mixtos, y sin normalizar la comparacion falla ABIERTA. En POSIX
    # `normcase` no hace nada, asi que no cambia el comportamiento donde corre el CI.
    n = lambda x: os.path.normcase(os.path.realpath(_absoluta(x)))
    a, b = n(destino), n(canonico)
    return a == b or a.startswith(b + os.sep)


def exigir_produccion(sym: str, capa: str, usado: str, destino: str, canonico: str) -> None:
    """PRODUCTOR: se niega a escribir un artefacto no conforme en el directorio CANÓNICO.

    Fuera del canónico no bloquea —producir en un temporal es lo que hacen los tests de
    identidad-byte, y romperlos no protegería nada— pero la marca se escribe igual, así que el
    consumidor sigue pudiendo rechazarlo si alguien lo mueve luego al sitio bueno."""
    if conforme(sym, capa, usado) or not _es_canonico(destino, canonico):
        return
    # EL ESCAPE NO ABRE EL NAMESPACE OFICIAL (mesa 2026-08-28, P0-2). La versión anterior dejaba
    # pasar aquí prometiendo que «queda marcado como NO conforme y los consumidores lo rechazarán»,
    # y esa promesa era FALSA para todo productor que no publicase por `artefacto.publicar`:
    # `eco_runner_lit` escribía con `np.savez`, ningún campo registraba el carril y el gate no
    # recalculaba nada. Peor: para ese productor `conforme` era SIEMPRE False —la regla exige el mid
    # y él pasa el trade—, así que el escape no era una excepción sino su ÚNICA vía, encendida de
    # forma permanente. Un escape que hay que dejar puesto no es un escape: es la puerta principal.
    #
    # A partir de aquí el escape sirve para reproducir fuera del canónico, que es donde una
    # reproducción forense tiene que vivir. Dentro del canónico no hay escape que valga.
    raise CarrilNoConforme(
        f"CARRIL NO CONFORME: {sym} en capa «{capa}» exige `{exigido_para(sym, capa)}` y se iba a "
        f"producir con `{usado}` dentro del directorio canónico {canonico}.\n"
        f"Escribir aquí crearía un artefacto que viola el estimando pre-registrado. Arreglarlo es "
        f"implementar el carril exigido.\n"
        f"El escape {VAR_ESCAPE}=1 NO sirve aquí: una reproducción forense se escribe FUERA del "
        f"directorio canónico. Lo que entra en el canónico entra acreditado o no entra.")

