"""Maquinaria conservada del arnés: copia, baseline, causas, timeout y limpieza.

Traslado desde mutacion_gate_b en e1c2757. La tabla y la entrada del gate se retiran;
ref_valida conserva este ejecutor y sus pruebas. No implementa protección científica.
"""
import argparse

import hashlib

import io

import os

import re

import shutil

import stat

import subprocess

import sys

import tempfile

QS_REAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REPO_REAL = os.path.abspath(os.path.join(QS_REAL, "..", ".."))

COPIABLES = ("analysis", "tests", "tools", "ingestion")

VIGILADAS = COPIABLES + (
    os.path.join("data_hist", "eco_b"),
    # M-13 escribió aquí al mezclar raíz del repo con una constante relativa a `qs/`; estaba fuera
    # del corral anterior, así que un mutante podía contaminarla sin que el arnés lo viera.
    os.path.join("..", "..", "data_hist", "eco_b"),
)

_FALLO = re.compile(r"^(?:FAILED|ERROR)\s+\S+::(\S+?)(?:\s+-\s+(.*))?$", re.M)

_PASADOS = re.compile(r"(\d+)\s+passed")

def _sha(path):
    with open(path, "rb") as f:
        h = hashlib.sha256()
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()

def _huella():
    """TODOS los ficheros de las rutas vigiladas, no solo los `.py` de tres directorios. Devuelve
    un dict para que la comparación detecte también las BAJAS, que una lista de sha no ve."""
    h = {}
    for sub in VIGILADAS:
        base = os.path.join(QS_REAL, sub)
        if not os.path.isdir(base):
            continue
        for raiz, dirs, ficheros in os.walk(base):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache")]
            for f in ficheros:
                if f.endswith(".pyc"):
                    continue
                p = os.path.join(raiz, f)
                try:
                    h[os.path.relpath(p, QS_REAL)] = _sha(p)
                except OSError:
                    h[os.path.relpath(p, QS_REAL)] = "ILEGIBLE"
    return h

def _diferencias(antes, ahora):
    return (sorted(f for f in ahora if f not in antes),                       # altas
            sorted(f for f in antes if f not in ahora),                       # BAJAS
            sorted(f for f in antes if f in ahora and antes[f] != ahora[f]))

def _copia_limpia(raiz_tmp, n):
    """Copia NUEVA por mutación: con una sola copia, los artefactos que un mutante deje en el
    filesystem los hereda el siguiente y el resultado deja de ser atribuible."""
    destino = os.path.join(raiz_tmp, f"qs_{n:02d}")
    for sub in COPIABLES:
        shutil.copytree(os.path.join(QS_REAL, sub), os.path.join(destino, sub),
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    return destino

def _interpretar(salida, returncode):
    """PURA: de la salida de pytest a (razones, línea de recuento, invalida, n_passed).

    Extraída de `_correr` para que se pueda probar SIN subproceso. La versión anterior mezclaba la
    llamada y la interpretación, así que la lógica que decide «inválida» no tenía test — y ahí
    vivían dos defectos: `base_rota` calculada y no comprobada, y la deteción por texto que
    `--tb=no` volvía inservible."""
    linea = next((x for x in reversed(salida.strip().split("\n"))
                  if "passed" in x or "failed" in x or "error" in x), "")
    razones = {t: (m or "").strip() for t, m in _FALLO.findall(salida)}
    m = _PASADOS.search(linea)
    n_passed = int(m.group(1)) if m else 0
    # INVÁLIDA: la mutación rompió el módulo (colección/import) o pytest ni siquiera corrió. Se
    # detecta por el RECUENTO y por el `returncode`, no por el texto: con `--tb=no` un SyntaxError
    # no llega a imprimirse. rc: 0 ok · 1 fallos · 2 interrumpido · 3 interno · 4 uso · 5 sin tests.
    invalida = bool(re.search(r"\d+\s+errors?\b", linea)) or returncode not in (0, 1) or not linea
    return razones, (linea[:58] or f"(sin recuento; rc={returncode})"), invalida, n_passed

def _problemas_baseline(rc, invalida, razones, n_passed, n_esperados, conteo_exacto=True):
    """PURA: las CUATRO condiciones de la línea base, cada una por separado y con su nombre.

    Se exigen las cuatro porque cualquiera sola deja un hueco: `razones == {}` sin mirar `rc` deja
    pasar un pytest que fallo con un formato de nodo que `_FALLO` no reconoce, y ése era el P0-1
    que la mesa cazó. Devuelve la lista de problemas; vacía = base utilizable.

    `conteo_exacto=False` (añadido 2026-08-27 para `tools/mutacion_ref_valida.py`): cuando los tests
    declarados están PARAMETRIZADOS, un nombre expande a varios nodos y exigir igualdad exacta
    rechazaría una base perfectamente limpia. Entonces se exige `n_passed >= n_esperados`, que sigue
    detectando lo que esta condición existe para detectar: que la selección `-k` no haya corrido lo
    declarado. El valor por defecto deja este arnés EXACTAMENTE como estaba."""
    p = []
    if rc != 0:
        p.append(f"returncode={rc} (se exige 0)")
    if invalida:
        p.append("recuento con errores o ilegible")
    if razones:
        p.append(f"fallos={sorted(razones)}")
    if (n_passed != n_esperados) if conteo_exacto else (n_passed < n_esperados):
        p.append(f"pasaron {n_passed} de {n_esperados} declarados")
    return p

def _texto(v) -> str:
    """Un canal de la excepción, como texto, venga como venga. `TimeoutExpired` puede traer `bytes`,
    `str` o `None` en cada canal con independencia de lo que pidiera el `run`."""
    if v is None:
        return ""
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="replace")
    return str(v)

def _mostrar_timeout(nombre, timeout):
    """Los canales completos van al log; `muestra` sólo sirve para el resumen de la fila."""
    print(f"TIMEOUT {nombre}: limite={timeout['limite']}s", flush=True)
    for canal in ("stdout", "stderr"):
        print(f"--- {nombre} / {canal} (texto completo capturado) ---", flush=True)
        print(timeout["parcial"][canal], flush=True)

def _quitar_solo_lectura(func, ruta, exc):
    """Reintenta una retirada denegada sobre un temporal ya validado.

    Git deja objetos 0444 que Windows no permite borrar. Otros errores, incluido
    un segundo fallo al retirar, se propagan; no se oculta una limpieza incompleta.
    """
    if not isinstance(exc, PermissionError):
        raise exc
    os.chmod(ruta, stat.S_IWRITE)
    func(ruta)

def _borrar_temporales(raiz, *hijos):
    """Baja estricta del directorio creado por el arnés o de sus hijos directos.

    Valida TODOS los destinos antes de borrar. Rechaza destinos enlazados/reparse y raíces dentro
    del proyecto. No elimina la carrera por pathname. Un error de inspección o retirada se propaga.
    """
    base = os.path.normcase(os.path.abspath(raiz))
    repo = os.path.normcase(os.path.realpath(REPO_REAL))
    if (base != os.path.normcase(os.path.realpath(raiz))
            or not os.path.basename(base).startswith(("mutacion_gate_", "mutacion_refvalida_"))
            or base == repo or base.startswith(repo + os.sep)):
        raise OSError(f"raíz temporal no autorizada para limpieza: {raiz}")
    destinos = []
    for ruta in hijos or (raiz,):
        p = os.path.normcase(os.path.abspath(ruta))
        if ((hijos and os.path.dirname(p) != base)
                or p != os.path.normcase(os.path.realpath(ruta))):
            raise OSError(f"destino fuera del temporal propio: {ruta}")
        try:
            st = os.lstat(ruta)
        except FileNotFoundError:
            continue
        if (not stat.S_ISDIR(st.st_mode) or stat.S_ISLNK(st.st_mode)
                or getattr(st, "st_file_attributes", 0) & 0x400):
            raise OSError(f"destino de limpieza no es directorio regular: {ruta}")
        destinos.append(ruta)
    for ruta in destinos:
        shutil.rmtree(ruta, onexc=_quitar_solo_lectura)
        if os.path.lexists(ruta):
            raise OSError(f"la retirada no eliminó el temporal: {ruta}")

def _cerrar_fila_timeout(raiz, copia, basetemp, huella_antes, conservar=False):
    """Sólo permite continuar tras retirada local comprobada y sin deriva observada.

    No demuestra ausencia global de descendientes del pytest terminado. Esa contención de procesos
    no forma parte de este ejecutor. Con `--conservar` se para: no se finge haber limpiado.
    """
    if any(_diferencias(huella_antes, _huella())):
        raise RuntimeError("árbol vigilado cambió: no se continúa tras el timeout")
    if conservar:
        raise RuntimeError("timeout con --conservar: se retienen los temporales y no se continúa")
    _borrar_temporales(raiz, copia, basetemp)
    if any(_diferencias(huella_antes, _huella())):
        raise RuntimeError("árbol vigilado cambió durante la limpieza del timeout")

def _finalizar_copia(raiz, huella_antes, conservar=False):
    """Calcula la deriva y conserva cualquier error de limpieza para juzgarlo fuera del finally."""
    deriva = _diferencias(huella_antes, _huella())
    fallo_limpieza = None
    if not conservar:
        try:
            _borrar_temporales(raiz)
        except OSError as exc:
            fallo_limpieza = exc
    return deriva, fallo_limpieza

TIMEOUT_S = 900

def _correr(copia, tests, basetemp, ficheros=(
        "tests/test_ref_valida.py",), limite=TIMEOUT_S):
    """Devuelve (razones {test: motivo}, línea de recuento, invalida, rc, n_passed, timeout).

    ═══ EL TIMEOUT SE TRATA, NO SE PROPAGA (M-15) ═══

    Medido el 2026-09-05: `TimeoutExpired` subía sin capturar y mataba la corrida ENTERA del arnés.
    La de referencia murió en la fila 152 de 199 tras 6 h 30; el mismo test tardó 1,86 s aislado.
    La causa del agotamiento no está demostrada. Los veredictos ya emitidos quedaron en el log —no se
    perdió evidencia—, pero la ejecución no se pudo completar y hubo que repetir el trabajo: dos
    horas.

    Ahora el límite se agota SIN tirar la corrida:
      · `subprocess.run` mata al hijo y lo espera antes de levantar la excepción (garantía de la
        stdlib), así que el proceso lanzado queda terminado y esperado. NO se afirma que no
        queden descendientes suyos: `run` no los conoce y esto no lo comprueba;
      · se conserva la salida PARCIAL que hubiera, para poder mirar en qué se atascó;
      · `timeout` no es `None` y el llamador decide: en la línea base, abortar; en una fila,
        registrar y seguir sólo tras limpiar la copia y comprobar la huella. **Nunca cuenta como
        mordida, ni como éxito, ni como salto de plataforma.**

    Se captura `TimeoutExpired` y NADA más: un `KeyboardInterrupt` o un fallo del propio arnés tienen
    que seguir subiendo. Tragarse una cancelación sería peor que el defecto que esto arregla.
    """
    try:
        return _correr_o_timeout(copia, tests, basetemp, ficheros, limite)
    except subprocess.TimeoutExpired as e:
        # LOS DOS CANALES, POR SEPARADO Y CADA UNO CON SU TIPO. La primera versión hacía
        # `(stdout or "") + (stderr or "") if isinstance(stdout, str) else ""`, y perdía la salida
        # entera en tres casos reproducibles: bytes en cualquiera de los dos, `stdout=None` con
        # `stderr` lleno, y mezcla de tipos. `TimeoutExpired` no garantiza `str` aunque el `run` lo
        # pidiera: quien construya la excepción decide.
        completa = {c: _texto(getattr(e, c, None)) for c in ("stdout", "stderr")}
        return ({}, f"TIMEOUT tras {limite}s", False, None, 0,
                {"limite": limite,
                 # COMPLETA para diagnosticar, y una MUESTRA aparte para la pantalla. Devolver solo
                 # los últimos 400 caracteres y llamarlo «conservar la salida parcial» era presentar
                 # un recorte como si fuera el diagnóstico entero.
                 "parcial": completa,
                 "muestra": (completa["stdout"] + completa["stderr"]).strip()[-400:]})

def _correr_o_timeout(copia, tests, basetemp, ficheros, limite):
    """El lanzamiento en crudo. Separado para que `_correr` sea la única que decide qué hacer con el
    límite, y para poder simular el agotamiento en los focales sin esperar quince minutos.

    `ficheros` se parametrizó el 2026-08-27 para que `tools/mutacion_ref_valida.py` pueda
    reutilizar ESTA interpretación en vez de duplicarla: la lógica que decide «inválida» y
    la que lee la causa del fallo tienen historial de sutilezas (el truncado por `COLUMNS`,
    el rc=1 con formato no reconocido), y dos copias divergirían. M-14 añade el fichero de dos
    worktrees porque las guardias del entry point público solo son observables allí. Declarar esos
    tests sin ejecutar su fichero hacía que la propia línea base quedara incompleta."""
    r = subprocess.run([sys.executable, "-m", "pytest", *ficheros, "-q",
                        "-k", " or ".join(tests), "--no-header", "--tb=no", "-rf",
                        "-p", "no:cacheprovider", f"--basetemp={basetemp}"],
                       cwd=copia, capture_output=True, text=True, timeout=limite,
                       # pytest TRUNCA el resumen al ancho de terminal: en un subproceso el motivo
                       # salía como «- Fa...» y la verificación de causa era imposible por
                       # construcción. `COLUMNS` lo fija. (Se descubrió porque el arnés se negó a
                       # acreditar nada: no vio la causa y NO certificó, que es el fallo correcto.)
                       env={**os.environ, "COLUMNS": "200"})
    # La INTERPRETACIÓN vive en `_interpretar`, que es pura y tiene tests. Aquí solo se lanza el
    # subproceso: mezclar ambas cosas era lo que dejaba sin test la lógica que decide «inválida».
    razones, linea, invalida, n_passed = _interpretar(
        (r.stdout or "") + (r.stderr or ""), r.returncode)
    return razones, linea, invalida, r.returncode, n_passed, None

def _base_nodo(nodo: str) -> str:
    """Nombre del test SIN su sufijo de parametrización: `test_x[nan-no_finita]` -> `test_x`.

    Añadido 2026-08-27. `_juzgar` comparaba nombres de nodo con nombres declarados, y un test
    PARAMETRIZADO nunca casaba: sus fallos se contaban como COLATERAL y la fila salía «test vacuo»
    aunque la mutación mordiera de verdad — lo vimos con `tools/mutacion_ref_valida.py`, donde 6 de
    8 mutaciones que SÍ rompían tests se declararon inocuas. Para las filas no parametrizadas (todas
    las de este arnés) `_base_nodo` es la identidad, así que el comportamiento no cambia."""
    return nodo.split("[", 1)[0]

def _juzgar(tests_causa, razones, n_passed):
    """¿Cumple esta mutación el criterio declarado? Devuelve (estado, detalle).

    Reglas, todas exigidas a la vez (mesa, P0-2):
      · TODOS los tests declarados deben fallar. Declarar cuatro y conformarse con uno deja a los
        otros tres libres de volverse vacuos sin que nadie se entere.
      · El resumen de cada fallo debe contener SU marcador o fragmento declarado. Esto no
        demuestra una causa única cuando la fila sólo exige un fragmento genérico.
      · Un fallo COLATERAL invalida la acreditación aunque además caiga alguno esperado: significa
        que la mutación tocó algo más y el resultado ya no es atribuible a la guardia.
    """
    razones_b: dict = {}
    for _nodo, _motivo in razones.items():          # un test parametrizado puede fallar en varios
        razones_b.setdefault(_base_nodo(_nodo), _motivo)   # nodos: basta con el primero
    razones = razones_b
    esperados, colateral = set(tests_causa), sorted(set(razones) - set(tests_causa))
    if colateral:
        return "*** COLATERAL — NO ACREDITA ***", f"falló además {colateral}: no es atribuible"
    faltan = sorted(esperados - set(razones))
    if faltan == sorted(esperados):
        return "*** VERDE — TEST VACUO ***", "la guardia se quitó y NADIE se enteró"
    if faltan:
        return "*** MORDIDA PARCIAL ***", f"no mordieron: {faltan} (pueden estar vacuos)"
    # Pytest ha usado dos grafías para el mismo modo de fallo según versión:
    # `DID NOT RAISE RuntimeError` y `DID NOT RAISE <class 'RuntimeError'>`. La comparación sigue
    # siendo de substring, pero normaliza solo esa representación sintáctica; no convierte una
    # excepción distinta ni un AssertionError genérico en la causa esperada.
    def _causa_canonica(valor):
        return re.sub(r"<class ['\"]([^'\"]+)['\"]>", r"\1", valor).lower()

    malas = {t: razones[t] for t, c in tests_causa.items()
             if _causa_canonica(c) not in _causa_canonica(razones[t])}
    if malas:
        return "*** CAUSA AJENA ***", " · ".join(
            f"{t}: esperaba «{tests_causa[t]}» y salió «{v[:44]}»" for t, v in malas.items())
    return "ROJO ✓", " · ".join(f"{t.split('_', 2)[-1][:26]}→{c}" for t, c in tests_causa.items())
