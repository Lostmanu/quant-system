"""analysis/artefacto.py — EL ARTEFACTO ACREDITADO. Bytes + hash + procedencia + CONTEXTO ESPERADO,
publicados y consumidos como UNA unidad.

═══ POR QUÉ ESTA VERSIÓN (mesa, 2026-08-28, 4ª reauditoría — P0-1) ═══

La v1 recalculaba la conformidad en vez de leerla, que era el arreglo correcto para el agujero
anterior… y aun así **el artefacto seguía autenticándose a sí mismo**, un nivel más arriba:

    CA.conforme(m["simbolo"], m["capa"], m["carril_usado"])
                             ↑↑↑↑↑↑↑↑↑
                 la CAPA contra la que se juzga sale del PROPIO manifiesto que se juzga

Un artefacto de capa 2 declara «soy capa2, carril prints_lighter»; se le pregunta si prints_lighter es
conforme **para capa2**; la respuesta es que sí. Nadie dijo nunca qué se ESPERABA. Reproducido
ejecutando: un bloque legítimo de capa 2 trasplantado al directorio decisivo de confirmación entró sin
una queja, y `confirm_screen._cells()` ingirió markouts calculados contra prints_lighter cuando el
prerregistro exige el mid de Binance.

Y una variante peor que la de la mesa, también reproducida: **no hace falta trasplantar nada**. El
SHA-256 cubría los bytes del npz pero no el JSON que los acredita, así que cambiar la palabra `capa`
en el manifiesto —una edición, hash del npz intacto— convertía un rechazo correcto en una aceptación.

Es el MISMO error que el `extra` que se sobrescribía `conforme`, un nivel más arriba: **en los dos
casos el objeto auditado aportaba el criterio con el que se le auditaba**. Una verificación en la que
el acusado pone la premisa no es una verificación, es una tautología.

═══ LAS CUATRO REGLAS ═══

  1. **El contexto esperado lo pone QUIEN LLAMA, y es obligatorio.** `cargar()` exige `capa_esperada`
     sin valor por defecto: no se puede leer un artefacto «a ver qué es». La conformidad se recalcula
     contra ESA capa, y el manifiesto tiene además que coincidir con ella. El manifiesto ya no elige
     el examen que se le aplica.
  2. **La conformidad se RECALCULA, nunca se lee.** Si el manifiesto trae `conforme`, se ignora.
  3. **El manifiesto lleva el SHA-256 y el tamaño del npz**; el consumidor lee los bytes UNA vez,
     hashea ESOS bytes y carga desde ESOS MISMOS bytes.
  4. **El contenido se valida contra el esquema de su familia**: claves exigidas, `mo` bidimensional
     de float64, y todos los vectores por-evento con la misma longitud. La v1 aceptaba un `mo` de
     shape (0,) e int8 y el consumidor reventaba después con un `KeyError` —o, peor, no reventaba—.

EL ORDEN DE PUBLICACIÓN, que es una defensa y no un detalle:

    npz.tmp  ->  sha de sus bytes  ->  manifiesto (atómico)  ->  rename del npz (atómico)

Así el artefacto canónico no existe nunca sin su manifiesto.

ESQUEMA 2. No hay compatibilidad con el 1 y es deliberado: bajo el STOP de producción no se publicó
ni un solo artefacto con el esquema 1, así que no existe ninguno en el mundo. Aceptar un formato que
nadie tiene sólo abriría una vía sin dueño.
"""
from __future__ import annotations

import hashlib
import io
import json
import os

import numpy as np

from analysis import carril as CA

ESQUEMA = 2
SUFIJO = ".manifiesto.json"

# Campos que definen la procedencia. `extra` NO puede pisarlos: van fuera de su alcance por
# construcción, no por convenio.
CAMPOS_NORMATIVOS = ("esquema", "simbolo", "fecha", "capa", "carril_usado", "bytes", "sha256")

# ───────────────────────────────────────────────────────────────── ESQUEMAS DE CONTENIDO POR FAMILIA
# Tomados de lo que los productores escriben y los consumidores leen HOY (verificado fichero a
# fichero), no de lo que la documentación promete. `por_evento` son los vectores que tienen que
# medir lo mismo que `mo`: si uno se desalinea, los estratos dejan de significar lo que dicen y el
# error es SILENCIOSO.
#
# `descartes` sólo se exige PRESENTE: su forma depende del número de horizontes y constreñirla aquí
# sería inventar una restricción que no he verificado contra producción.
FAMILIAS = {
    "confirmacion": {
        "exigidas": ("mo", "descartes", "tipo", "slow", "is_bid", "owner", "vol20", "t_fill",
                     "thr_con_at", "amb"),
        "por_evento": ("tipo", "slow", "is_bid", "owner", "vol20", "t_fill", "thr_con_at"),
    },
    "piloto": {
        "exigidas": ("mo", "descartes", "tipo", "slow", "is_bid", "label", "estrato"),
        "por_evento": ("tipo", "slow", "is_bid", "label"),
    },
    "capa2": {
        "exigidas": ("mo", "descartes", "lado", "cota", "through", "label", "ts",
                     "n_intervalos", "n_invalidos"),
        "por_evento": ("lado", "cota", "through", "label", "ts"),
    },
}


class ArtefactoNoAcreditado(RuntimeError):
    """Se distingue de un error cualquiera para que un consumidor no pueda confundirla con un fallo
    de E/S y seguir adelante."""


def ruta_manifiesto(npz_path: str) -> str:
    base = npz_path[:-4] if npz_path.endswith(".npz") else npz_path
    return base + SUFIJO


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def publicar(destino: str, arrays: dict, *, simbolo: str, fecha: str, capa: str, carril_usado: str,
             extra=None) -> dict:
    """Publica npz + manifiesto como una unidad. Devuelve el manifiesto escrito.

    NO decide si el carril es conforme —eso lo hace `carril.exigir_produccion`, que debe llamarse
    ANTES y antes de gastar—; aquí sólo se registra qué se usó, y el consumidor recalculará contra
    la capa que ÉL espera."""
    if capa not in FAMILIAS:
        raise ArtefactoNoAcreditado(
            f"capa `{capa}` sin esquema de contenido declarado en FAMILIAS. Publicar una familia que "
            f"nadie ha descrito deja al consumidor sin nada contra lo que validar.")
    malos = _validar_contenido(arrays, capa, lambda k: arrays[k])
    if malos:
        raise ArtefactoNoAcreditado(
            f"NO SE PUBLICA {os.path.basename(destino)}: el contenido no cumple el esquema de "
            f"`{capa}`.\n  · " + "\n  · ".join(malos) +
            "\n\nSe comprueba al PUBLICAR y no sólo al consumir: un artefacto mal formado que llega "
            "a disco ya ha costado su producción, y quien lo lea meses después no sabrá por qué.")

    os.makedirs(os.path.dirname(destino) or ".", exist_ok=True)
    tmp_npz = destino + ".enpublicacion"
    with io.open(tmp_npz, "wb") as fh:
        np.savez(fh, **arrays)                    # los BYTES son los mismos que `np.savez(destino,…)`
    crudo = io.open(tmp_npz, "rb").read()

    man = {"esquema": ESQUEMA, "simbolo": simbolo, "fecha": fecha, "capa": capa,
           "carril_usado": carril_usado, "bytes": len(crudo), "sha256": _sha_bytes(crudo)}
    if extra:
        man["extra"] = extra                      # bajo SU clave: no puede pisar lo normativo

    ruta_man = ruta_manifiesto(destino)
    tmp_man = ruta_man + ".tmp"
    with io.open(tmp_man, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(man, fh, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp_man, ruta_man)                 # 1º el manifiesto…
    os.replace(tmp_npz, destino)                  # …2º el npz toma su nombre canónico
    return man


def _leer_manifiesto(npz_path: str):
    ruta = ruta_manifiesto(npz_path)
    if not os.path.exists(ruta):
        return None
    try:
        m = json.load(io.open(ruta, encoding="utf-8"))
    except Exception:
        return None                               # ilegible acredita tan poco como ausente
    return m if isinstance(m, dict) else None


def _validar_contenido(claves, capa: str, dame) -> list:
    """El npz cumple el esquema de su familia. `dame(k)` devuelve el array de la clave `k`.

    Se pasa un accessor en vez del NpzFile para poder validar TAMBIÉN al publicar, cuando lo que hay
    es un dict — y así el productor y el consumidor comparten literalmente la misma comprobación en
    vez de dos que se parecen (que es como nació E-49)."""
    esq = FAMILIAS.get(capa)
    if esq is None:
        return [f"capa `{capa}` sin esquema declarado"]
    presentes = set(claves)
    fallos = [f"falta la clave `{k}`" for k in esq["exigidas"] if k not in presentes]
    if "mo" not in presentes:
        return fallos
    mo = np.asarray(dame("mo"))
    if mo.dtype.kind != "f":
        fallos.append(f"`mo` es {mo.dtype} y tiene que ser de coma flotante: un markout entero es "
                      f"un markout truncado")
    if mo.ndim != 2:
        fallos.append(f"`mo` tiene ndim={mo.ndim} y tiene que ser (n_eventos, n_horizontes)")
        return fallos
    n = mo.shape[0]
    for k in esq["por_evento"]:
        if k not in presentes:
            continue
        v = np.asarray(dame(k))
        if v.ndim != 1:
            fallos.append(f"`{k}` tiene ndim={v.ndim} y tiene que ser un vector por evento")
        elif len(v) != n:
            fallos.append(f"`{k}` mide {len(v)} y `mo` tiene {n} eventos: un vector desalineado "
                          f"corrompe los estratos SIN dar error")
    return fallos


def _validar(m: dict, npz_path: str, crudo: bytes, capa_esperada: str, simbolo_esperado) -> list:
    """Todas las razones por las que este artefacto NO está acreditado. Lista vacía = acreditado.

    Se devuelven TODAS y no la primera: un consumidor que sólo ve el primer motivo arregla ese y
    vuelve a chocar, y quien audita no sabe cuántos problemas hay."""
    fallos = []
    nombre = os.path.basename(npz_path)
    if m.get("esquema") != ESQUEMA:
        fallos.append(f"esquema {m.get('esquema')!r} != {ESQUEMA}")
    for campo in ("simbolo", "fecha", "capa", "carril_usado", "sha256"):
        if not isinstance(m.get(campo), str) or not m.get(campo):
            fallos.append(f"campo `{campo}` ausente o no es texto")
    if m.get("bytes") != len(crudo):
        fallos.append(f"tamaño declarado {m.get('bytes')!r} != {len(crudo)} reales")
    sha = _sha_bytes(crudo)
    if m.get("sha256") != sha:
        fallos.append(f"SHA-256 declarado {str(m.get('sha256'))[:12]}… != {sha[:12]}… de los bytes")

    # POR QUÉ NO HAY UN HASH DEL PROPIO MANIFIESTO, aunque lo escribí primero y lo quité. Cubriría
    # los siete campos normativos… que ya se validan UNO A UNO justo aquí arriba, así que su mutación
    # en el arnés no mataba a ningún test: moría por otra defensa. Un segundo mecanismo que no puede
    # fallar solo no es defensa en profundidad, es la duplicación E-49 — y este proyecto tiene
    # catalogado que los controles que no son load-bearing acaban dando una seguridad que no dan.

    # EL NOMBRE tiene que casar con la procedencia: un manifiesto correcto junto al npz equivocado
    # acreditaría el fichero de otro día.
    base = nombre[:-4] if nombre.endswith(".npz") else nombre
    if "_" in base:
        sym_f, dia_f = base.rsplit("_", 1)
        if m.get("simbolo") != sym_f:
            fallos.append(f"símbolo del manifiesto {m.get('simbolo')!r} != {sym_f!r} del nombre")
        if m.get("fecha") != dia_f:
            fallos.append(f"fecha del manifiesto {m.get('fecha')!r} != {dia_f!r} del nombre")

    # ═══ EL CONTEXTO ESPERADO, que es lo que impide que el artefacto elija su propio examen ═══
    if m.get("capa") != capa_esperada:
        fallos.append(f"capa declarada {m.get('capa')!r} != {capa_esperada!r} que ESPERA el "
                      f"consumidor: este artefacto es de otra familia")
    if simbolo_esperado is not None and m.get("simbolo") != simbolo_esperado:
        fallos.append(f"símbolo declarado {m.get('simbolo')!r} != {simbolo_esperado!r} que espera "
                      f"el consumidor")

    # LA CONFORMIDAD SE RECALCULA, y contra la capa que espera QUIEN LLAMA — no contra la que el
    # manifiesto se atribuye. Si el manifiesto trae un campo `conforme`, se IGNORA.
    sym = simbolo_esperado if simbolo_esperado is not None else m.get("simbolo", "")
    if not CA.conforme(sym, capa_esperada, m.get("carril_usado", "")):
        fallos.append(f"carril `{m.get('carril_usado')}` != `"
                      f"{CA.exigido_para(sym, capa_esperada)}` que exige el prereg para "
                      f"`{sym}` en `{capa_esperada}`")
    return fallos


def cargar(npz_path: str, *, capa_esperada: str, simbolo_esperado=None,
           permitir_no_acreditado: bool = False):
    """EL ÚNICO camino para leer un artefacto del programa. Devuelve (datos, manifiesto).

    `capa_esperada` NO tiene valor por defecto, y es la corrección de fondo de P0-1: quien lee tiene
    que declarar qué esperaba encontrar. Un consumidor que no sabe qué familia está leyendo no está
    en condiciones de validar nada, y hasta hoy los cinco consumidores del programa cargaban sin
    decirlo — no por descuido suyo, sino porque la firma no se lo permitía.

    Lee los bytes UNA vez y carga desde esos MISMOS bytes: si el fichero cambiara entre el hash y la
    carga, el hash acreditaría unos bytes y el análisis hablaría de otros.

    `permitir_no_acreditado=True` es el escape FORENSE: devuelve los datos con el motivo a la vista.
    Lo que salga con él es exploratorio, jamás confirmatorio."""
    crudo = io.open(npz_path, "rb").read()
    m = _leer_manifiesto(npz_path)
    nombre = os.path.basename(npz_path)
    if m is None:
        fallos = [f"no hay manifiesto `{SUFIJO}`: el artefacto NO está acreditado"]
    else:
        fallos = _validar(m, npz_path, crudo, capa_esperada, simbolo_esperado)

    z = np.load(io.BytesIO(crudo))
    # El CONTENIDO se valida contra la familia que el consumidor espera, no contra la que el fichero
    # dice ser: si no, un artefacto mentiroso elegiría también qué esquema se le aplica.
    fallos = fallos + _validar_contenido(z.files, capa_esperada, lambda k: z[k])

    if fallos and not permitir_no_acreditado:
        raise ArtefactoNoAcreditado(
            f"ARTEFACTO NO ACREDITADO: {nombre}\n  · " + "\n  · ".join(fallos) +
            "\n\nLos bloques anteriores al 2026-08-27 no traen manifiesto: hay que RE-DERIVAR. Para un"
            " análisis FORENSE consciente, `permitir_no_acreditado=True` — y lo que salga es"
            " exploratorio, nunca confirmatorio.")
    return z, dict(m or {}, no_acreditado=fallos or None)
