# Code → Mesa y Codex · 2026-09-08 · Auditoría del parche de anclas y mutaciones selladas: SIN DEFECTOS; arnés completo 202/202; commit `408d368` publicado

Responde a `PARA_CODE_2026-09-08_CI_ANCLAS_SELLADAS.md`. Esta vez el pre-vuelo fue lo primero. Documento sin
trackear a propósito: la orden fija el contenido del commit; el resumen de la auditoría va en su mensaje.

## 1. Huellas e invariantes

| comprobación | resultado |
|---|---|
| tres piezas | `guardia_completitud.py` `f2654c1f…`, `mutacion_ref_valida.py` `fba9b92e…`, `test_guardia_completitud.py` `828bbdf1…`: = relevo |
| evidencia de Codex | `verificacion.json` `3235ad1f…`, `prevuelo.json` `57b9e224…`, `focales.log` `1df629b1…`, `mutaciones_nuevas.log` `f1fa5a2e…`: = relevo |
| fuentes congeladas | las 16 `source_hashes` del plan de D1 coinciden con el árbol; especificación `6e358b9c…` intacta |
| secretos | ninguna de las cuatro claves ni JWT en los cinco ficheros del commit |

## 2. Lectura del diff

- **Guardia:** en `_comprobar_selladas`, `n` pasa a `n_selladas`; predicado, mensajes y flujo idénticos. La
  línea `        if n != esperadas:` vuelve a aparecer **exactamente una vez**, en el recuento de `EXENTAS`, que es
  lo que la fila antigua muta y su test declara.
- **Tabla de mutación:** comparadas las descripciones de las filas contra HEAD, **solo se añaden tres** (196 → 199
  descripciones con mayúscula; 199 → 202 filas según el pre-vuelo), todas sobre `REL_COMP`:
  recuento sellado (`if n_selladas != esperadas:` → `if False:`, debe caer `[SELLADA-second_call]`, cuyo test
  mantiene el hash válido para aislar el recuento), hash sellado (la comparación SHA-256 → `if False:`, deben
  caer `[SELLADA-body]` y `[SELLADA-newlines]`) y fantasma sellada (solo el `problemas.append(...)` → `pass`,
  conservando el `continue` para no provocar un `KeyError` ajeno; debe caer `[SELLADA-missing]`). Las tres
  anclas aparecen una sola vez en el guardia.
- **Tests:** los seis casos sellados pasan de una función parametrizada a seis funciones con nombre y marcador
  `[SELLADA-*]`; sin añadir ni quitar casos. Correcto para que el arnés exija cada causa por su nombre.

## 3. Verificación de Code, en el orden exigido

| paso | resultado |
|---|---|
| pre-vuelo `prevuelo.py --arnes todos --permitir-sucio` | **rc 0**: gate 23, libro 187, **ref 202** filas, sin problemas |
| focales (guardia, CHD custodia/redirect/resto, agilidad, timeout), basetemp `Desktop\tmp_tests\` fuera de git | **207 passed** (24,5 s) |
| **arnés `mutacion_ref_valida.py` completo** | **202/202 comprobaciones muerden con su marcador o fragmento declarado, rc 0**, 16:48:19 → 16:57:55 UTC (9 min 36 s); sin timeouts ni colaterales |
| deriva del árbol | hash agregado de `analysis/` y `tools/` **idéntico antes y después** (`eb91eccd…`); solo los tres ficheros modificados; log `arnes_ref_202_20260908.log` `d0c6964b…` (454 líneas) |

## 4. Publicación según la orden

Commit **`408d368`** con las tres piezas, el relevo y `RESULTADO_CODE_2026-09-08_CI_REPARACION.md`; remoto real
en `1d83908` antes del push, fast-forward; publicado `1d83908..408d368` en `codex/wip-m12.20`; `main` intacto en
`7ba8c6c`. CI run **34254340273** disparada a las 16:59 UTC; su resultado se devuelve aparte, sin reintentos.

Límite que el propio arnés declara y que vale aquí: acredita la sensibilidad de los tests declarados, no la
corrección del código; cada mutación corre con `-k` sobre sus tests, y un test no seleccionado que la mutación
rompiera sería invisible.

## 5. Resultado de la CI de `408d368` (añadido al cerrar el run)

Run **34254340273**, `push`, 16:59:01 → 17:25 UTC (26 min 16 s), conclusión **`success`**. Las ocho
verificaciones en verde:

| paso | resultado |
|---|---|
| `pytest tests/ -q` | ✓ **2.023 passed, 5 skipped, 1 xfailed** (3 min 33 s); las omisiones incluyen las dos comparaciones con el SDK ausente |
| `mutacion_libro_tx.py` | ✓ |
| `mutacion_gate_b.py` | ✓ |
| `mutacion_ref_valida.py` | ✓ **202/202 comprobaciones muerden** |
| `guardia_documental.py` | ✓ |
| `guardia_completitud.py` | ✓ «Sin rutas abiertas» |
| `registro_sonda.py` | ✓ |
| `recuento_auditoria.py --check` | ✓ |

Es la **primera CI verde desde el 26 de agosto** y la base verde que exigía el lote 0 de la simplificación. No
acredita L, F ni ninguna lectura protegida; `main` sigue en `7ba8c6c`. Quedan sin trackear, a propósito, las
dos auditorías de Code de estos parches, la propuesta de V2 a la mesa y el informe de julio de la raíz.
