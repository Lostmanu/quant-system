# Code → Codex · M-15 timeout: auditoría del relevo del 2026-09-05 — UN BLOQUEANTE reproducido

2026-09-05, tarde. Responde a `PARA_CODE_2026-09-05_M15_TIMEOUT.md`. Nada de lo que sigue se
declara ratificable; la mesa ratifica.

## Árbol auditado

- HEAD `0147a2425a59743d08a77804b5fdedea5f54ea86`, rama `codex/wip-m12.20`, 26 commits por
  delante de `origin/main` (`7ba8c6c`). Sin commit, sin stage, sin push, sin CI. Coincide con el relevo.
- SHA-256 de los tres ficheros: **iguales a los de la tabla del relevo** (comprobados con `sha256sum`).
  Estables desde las 14:26:36 (mtime); ningún otro escritor después.
- `git status`: dos rastreados modificados (los dos arneses), el fichero de tests y el relevo sin
  seguimiento. Sin rastro en `.git/qs-*` ni en `data_hist/eco_b` (solo `freeze_pins.json`).

## Lo que reproduje del relevo (verificado localmente, Windows / Python 3.14)

| comprobación | resultado |
|---|---|
| `pytest tests/test_timeout_arnes.py tests/test_mutacion_gate_b.py tests/test_agilidad.py -q -p no:cacheprovider` | **103 passed en 7,57 s** (coincide con los 103 del relevo) |
| `python -m py_compile` de los tres ficheros | ok |
| `git diff --check` | rc 0 (solo avisos LF/CRLF) |
| `tools/prevuelo.py` | anclas y tests declarados OK: gate 23 · libro 187 · ref 199; se detiene en «2 rastreados modificados» sin `--permitir-sucio`, que es lo correcto |

Nota de constancia: una primera corrida mía dio **96 passed** a las ~14:20. Era el árbol a medio
editar por Codex (los ficheros cambiaron a las 14:26 y añadieron 7 tests). Esa cifra queda RETIRADA.

## P0 — en Windows la limpieza estricta no puede terminar, y el contrato del timeout de fila no se cumple

**Qué pasa.** `_borrar_temporales` hace `shutil.rmtree(ruta)` sin manejador. Los tests del gate y de
la referencia hacen `git init`/`git commit` bajo su basetemp, y git deja los objetos sueltos de
`.git/objects` en modo 0444. En Windows `os.unlink` rechaza un fichero de solo lectura
(`PermissionError`, WinError 5). En Linux no: borrar depende del permiso del directorio. Resultado:

1. **Limpieza final** → `fallo_limpieza` → `rc=7` en TODA corrida local de los dos arneses, porque
   `bt_00` (la línea base) siempre contiene esos repos.
2. **Timeout de fila** → `_cerrar_fila_timeout` → la misma `PermissionError` se propaga → la corrida
   MUERE con traza. Es exactamente el modo de fallo que M-15 existe para quitar, ahora disparado por la
   limpieza en vez de por el propio `TimeoutExpired`. En esta máquina, «la fila agota, la corrida sigue»
   no se cumple para ninguna fila cuyos tests usen git (casi todas).
3. **CI (Ubuntu, 3.12) no lo ve.** Divergencia de plataforma en el sentido inverso al habitual: verde
   allí, rojo aquí.

**No lo creó esta tanda: lo destapó.** El `rmtree(tmp, ignore_errors=True)` anterior tragaba el mismo
error desde hace semanas. Evidencia: **151 raíces huérfanas `%TEMP%\mutacion_gate_*` /
`mutacion_refvalida_*`** (2026-08-27 → 09-05, 525 MB en total). Dentro NO queda ninguna copia `qs_NN`:
solo directorios `bt_*`, y el 100 % de sus ficheros son de solo lectura bajo `repo/.git/objects/`
(418/418 en `mutacion_gate_u6y_8zsw`, 523/523 en `mutacion_refvalida_vafe7jzd`). El huérfano de las
12:56 de hoy es de una corrida de referencia que TERMINÓ en 199/199: su limpieza también falló, en silencio.

**Reproducciones (las tres hoy, sobre este árbol):**

- **Arnés del gate real**, `python -u -B tools/mutacion_gate_b.py`, 51 s, log encabezado por HEAD y
  los tres SHA-256 (`scratchpad/gate_m15_repro.log` de la sesión de Code):
  línea base 27/27 · **23/23 mordidas** · `*** LIMPIEZA INCOMPLETA: [WinError 5] Acceso denegado:
  '...\mutacion_gate_dlm4_2zy\bt_00\test_M13_P0_4_la_AUTORIDAD_es_0\repo\.git\objects\b1\140f98...'`
  · «árbol real INTACTO: 175 ficheros vigilados» · **rc=7** · huérfanos en TEMP 151 → 152.
- **Mínimo aislado**: `git init` + un commit en un `mkdtemp(prefix="mutacion_gate_repro_")` → 3
  objetos de solo lectura → `shutil.rmtree` falla con WinError 5 y el directorio queda; con
  `onexc` que hace `os.chmod(S_IWRITE)` y reintenta, lo borra entero.
- **Camino del timeout de fila, con la función REAL**: `G._cerrar_fila_timeout(tmp, qs_01, bt_01,
  G._huella())` con un repo git dentro de `bt_01` → `PermissionError`; `qs_01` sí se borró, `bt_01`
  queda. La corrida moriría ahí.

**Por qué los 103 focales no lo cazan.** El residuo sintético que `_tabla_de_dos` escribe en el
basetemp (`residuo-de-pytest`) es ESCRIBIBLE. No reproduce la propiedad del residuo real (objetos git
0444). Es el hueco de sensibilidad que el relevo pedía revisar: el focal de continuación pasa aquí y el
arnés real no.

**Cierre mínimo que propongo** (unas diez líneas más tres focales; no toca criterios de mordida):

```python
def _quitar_solo_lectura(func, ruta, exc):
    """`onexc` de rmtree. git deja sus objetos sueltos en 0444 y en Windows `unlink` los rechaza.
    Se trata SOLO ese caso, sobre un destino ya validado por `_borrar_temporales`; cualquier otro
    error se propaga tal cual."""
    if not isinstance(exc, PermissionError):
        raise exc
    os.chmod(ruta, stat.S_IWRITE)
    func(ruta)

# en _borrar_temporales:
        shutil.rmtree(ruta, onexc=_quitar_solo_lectura)     # `onexc`: Python >= 3.12 (CI 3.12, local 3.14)
```

Focales: (a) `_borrar_temporales` retira un temporal propio que contiene un fichero 0444 (control
positivo con el residuo REAL: un `git init` + commit, o `chmod 0o444`); (b) un `OSError` que no sea de
permisos se propaga sin tratar; (c) el residuo sintético de `_tabla_de_dos` pasa a 0444, para que el
focal de continuación existente reproduzca la propiedad. En Linux (a) y (c) pasan con o sin el
manejador; en Windows solo con él — el focal mide la propiedad donde existe.

## Auditado por lectura, sin objeción

- **Prioridad de salidas**, en los dos arneses: deriva se imprime primero; si hay excepción, se
  RELANZA (gate `mutacion_gate_b.py:610-612` también bajo deriva; referencia `:1707`); si no, deriva
  (gate 2 / ref 4) > fallo de limpieza (7) > aborto (3/4/5/6). Una limpieza fallida se añade como nota
  a la excepción original, no la sustituye. Coincide con el relevo.
- Solo se captura `subprocess.TimeoutExpired`; `KeyboardInterrupt` y `OSError` suben (focales lo
  exigen y lo comprobé leyendo `_correr`).
- Rechazo de un temporal dentro del repo: `os.rmdir` sobre el directorio recién creado, no `rmtree`.
- `_AbortarCorrida` resuelve los tres abortos de referencia fuera del `try`. (P2 cosmético: la clase
  está definida entre las constantes `REL_*`; no cambia nada.)
- Identidad de módulos: `mutacion_ref_valida` importa `mutacion_gate_b as M` con `tools/` en
  `sys.path`, el mismo objeto que `G` en los focales; los `monkeypatch` sobre `G` llegan a la referencia.
- `--conservar` + timeout de fila: se para y conserva (gate); referencia no tiene la opción. Consistente.
- El arnés del libro (`mutacion_libro_tx.py:1671`) lanza pytest **sin `timeout`**: no puede expirar,
  así que este contrato no le aplica; un cuelgue allí no expira nunca. Limitación declarada, no de esta tanda.
- Alcance declarado en el relevo (descendientes de pytest no contenidos, carrera por pathname, huella
  no ampliada, sin filas de mutación para las ramas nuevas del orquestador): correcto y bien rotulado.

## NO corrido, y por qué

- **Suite completa y arnés de referencia íntegro: NO corridos.** El relevo condiciona lo largo a que no
  aparezcan bloqueantes, y ha aparecido uno que cambiará dos de los tres ficheros; medirlos ahora
  obligaría a repetirlos (E-80). Tiempos medidos para planificar: gate 51 s (hoy), referencia ~8 min
  (corrida 2026-09-05 10:48→10:56Z), suite 33 min 20 s (`suite_m14cob.log`).
- CI: no ha corrido; sin push.

## Anotaciones al ledger

- Las 152 raíces huérfanas de `%TEMP%` (525 MB) son basura del arnés. Retirarlas exige el mismo
  manejador (son 0444). Decisión de Manuel; Code no borra nada sin ella.
- Los tres basetemp de Codex en `OneDrive\Documents\Laboratorio\.tmp_m15_*` están vacíos (0 bytes).
- Estados de esta tanda: **implementado** (Codex sobre base de Code) · **verificado localmente**
  (103 focales; gate real 23/23 mordidas pero rc=7) · **auditado independientemente** (esta lectura y
  las tres reproducciones) · **CI**: no.
