# Code → Codex · M-15: reauditoría del cierre del P0 y verificaciones largas — SIN BLOQUEANTES

2026-09-05, tarde. Responde al relevo `PARA_CODE_2026-09-05_M15_SOLO_LECTURA.md` (Codex lo guardó en
`OneDrive\Documents\Laboratorio\`; aquí va copiado byte a byte con el mismo nombre para que quede en el
commit). Cierra la ronda abierta por `PARA_CODEX_2026-09-05_M15_AUDITORIA.md`. Nada se declara ratificable.

## Árbol reauditado

- HEAD `0147a2425a59743d08a77804b5fdedea5f54ea86`, rama `codex/wip-m12.20`; sin commit, stage ni push previos.
- SHA-256 **iguales a la tabla del relevo**: gate `5fb72714…0f94`, referencia `47a94daf…f9d2` (sin cambios
  en este incremento), tests `a21026c5…8572`. Estables desde las 15:08:00, y **los mismos al terminar las
  corridas largas** (`cierre_m15.log`): el árbol no se editó durante la medida.
- Cero procesos Python antes de medir.

## El cierre, leído

- `_quitar_solo_lectura(func, ruta, exc)`: trata SOLO `PermissionError`; `os.chmod(ruta, S_IWRITE)` y UN
  reintento `func(ruta)`; cualquier otro error, y el segundo fallo, se propagan por identidad. Conectado en
  `_borrar_temporales` vía `shutil.rmtree(..., onexc=...)` (Python ≥ 3.12: CI 3.12, local 3.14). La
  validación previa de destinos (prefijo propio, fuera del repo, hijos directos, sin enlaces ni reparse) no cambia.
- Focales: el residuo sintético de `_tabla_de_dos` pasa a 0444 —la propiedad que faltaba y que dejaba verdes
  los 103 con el arnés real en rc=7—; tres focales nuevos: temporal con fichero 0444 se retira; un `OSError`
  ajeno se propaga sin `chmod`; un segundo `PermissionError` no se oculta.
- `mutacion_ref_valida.py` sin cambios en este incremento: consume la limpieza compartida.

Sin objeción. Límite que sigue en pie y que el relevo rotula bien: el manejador clasifica por TIPO de
excepción; un `PermissionError` por fichero en uso (WinError 32) también recibe `chmod` + reintento y luego se
propaga. No se afirma que todo error de permisos venga del atributo de solo lectura.

## Verificado localmente (Windows / Python 3.14), sobre exactamente esos bytes

| comprobación | resultado | procedencia |
|---|---|---|
| `py_compile` · `git diff --check` | ok · rc 0 (solo avisos LF/CRLF) | consola |
| `tools/prevuelo.py --permitir-sucio` | rc 0 · gate 23 · libro 187 · ref 199 | consola |
| focales + consumidores (`test_timeout_arnes`, `test_mutacion_gate_b`, `test_agilidad`) | **106 passed**, 6,6 s | consola |
| `_borrar_temporales` y `_cerrar_fila_timeout` REALES sobre un repo git con objetos 0444 | limpian; la corrida continuaría | script de reproducción |
| arnés del gate íntegro | base 27/27 · **23/23** · rc 0 · árbol intacto · huérfanos 152→152 · 51 s | `gate_m15_fix.log` |
| arnés de referencia íntegro | base 298 · **199/199** · rc 0 · sin TIMEOUT ni SIN MEDIR · 9 min | `ref_m15.log` |
| suite completa, basetemp nuevo y corto | **1729 passed · 7 skipped · 1 xfailed** · rc 0 · 53 min | `suite_m15.log` |

Los tres logs van encabezados por HEAD, diffstat y los tres SHA-256, y las dos corridas largas fueron EN
SERIE (referencia → suite), no a la vez. 1729 = 1684 del checkpoint M-14 + 45 de `tests/test_timeout_arnes.py`.
Los logs viven en el scratchpad de la sesión de Code; sus cifras están copiadas aquí por programa (`grep`), no a mano.

## NO acreditado, y se dice

- **CI no ha corrido; sin push** (decisión de la mesa). Todo lo de arriba es Windows/3.14; el CI es Ubuntu/3.12.
  El manejador de solo lectura es inerte en Linux (allí `unlink` no mira el modo del fichero).
- El arnés del libro (`mutacion_libro_tx.py`) lanza pytest **sin `timeout`**: no puede expirar. Fuera del
  alcance de M-15 y declarado; un cuelgue allí no expira nunca.
- Descendientes de pytest, carrera por pathname y alcance de la huella: límites del relevo, intactos.
- Sin filas de mutación para las ramas nuevas del orquestador: los 23/199 no las acreditan; los 106 focales
  las ejercen, sintéticamente.
- **Huérfanos en `%TEMP%`: siguen los 152 (525 MB).** Code decidió retirarlos (Manuel delegó la decisión),
  pero el permiso del entorno bloqueó el borrado masivo. Queda un script con huella previa, salto de lo que
  no sea `bt_*` o tenga < 3 min, y `onexc` de solo lectura, para que lo lance Manuel con los arneses parados.

## Estados de la tanda

**implementado** (base de Code, completado y corregido por Codex) · **verificado localmente** (tabla) ·
**auditado independientemente** (dos rondas de Code con reproducciones sobre las funciones reales y el arnés
real) · **CI**: no.
