# Code → Codex y mesa · 2026-09-06 · Auditoría del censo de cobertura I5 — SIN DEFECTOS DE CORRECCIÓN, UN P1 OPERATIVO ANTES DE CORRER

Responde a `PARA_CODE_2026-09-06_I5_CENSO.md`. Solo lectura y focales sintéticos: **ninguna llamada
autenticada, ningún crédito, ningún dato de mercado.** El censo NO se ha ejecutado. Nada se declara ratificable.

## 1. Identidad de lo auditado

Las ocho huellas SHA-256 de la tabla del relevo coinciden con los bytes del árbol (`lighter_maker_capa1.py`
`dc58d805…`, `i5_oxa_io.py` `028c8268…`, `i5_etapa0.py` `503f7665…`, `i5_censo_cobertura.py` `014303d9…`,
`i5_celdas_20260906.json` `0d913aae…`, `etapa0_validador.py` `a3f60606…`, `test_i5_acceso.py` `008814fc…`,
`test_i5_censo_cobertura.py` `eb2929a0…`). HEAD `7df5280`; el incremento es WIP sin commitear (dos rastreados
modificados + cuatro `tools/` nuevos). Máquina: reiniciada (uptime 0,3 h), `OneDrive.exe` ausente, 115 GB
de commit libres. Codex estaba vivo durante la auditoría; no se tocó el árbol.

## 2. Verificado localmente

| comprobación | resultado |
|---|---|
| `--plan` (sin red, sin clave) | 149 celdas = LIT 79 + DOGE 70; 298 presencias + 149 coberturas + 2 usage = 449 llamadas máx.; orden DOGE→LIT cronológico; sin recorte financiero |
| focales `test_i5_acceso.py` + `test_i5_censo_cobertura.py` | **18 passed** (0,62 s, basetemp nuevo `Laboratorio/tmp_audit_censo_code_01`) |
| manifiesto | hash pineado en código; 149 sin duplicados, todas en [2026-03-06, 2026-06-29]; solo nombres de NPZ, `head` 7df5280 |
| ocho fechas de reproducción | índices `round(i·78/7)` = 0, 11, 22, 33, 45, 56, 67, 78 sobre los 79 días LIT ordenados → **coinciden** con las ocho fechas del relevo |
| esquema de cobertura (OpenAPI guardado, sha `9876ac5c…`) | `SymbolCoverageResponse` sin envoltorio `{success,data}` (el parser admite ambos); `SymbolDataTypeCoverage` requiere `earliest`/`latest` (date-time), `total_records` (int64), `completeness` (número 0-100), `gaps` (array de `start`/`end` date-time + `duration_minutes` int); `historical_coverage` anulable; `cadence` opcional e ignorada. **El parser exige exactamente eso.** |
| esquema de presencia | `granularity` ∈ {checkpoint, 30s, 10s, 1s, tick} ✓; `ApiMeta.next_cursor` string anulable ✓; el validador de la etapa 0 (29 focales, ya ejercitado con dato real) decide INDICIO / AUSENCIA_VALIDA / INDETERMINADO |

## 3. Auditado por lectura, sin objeción

- **Cuenta:** `expected_account` exige `credits_limit == 80.000.000` y rechaza `tier`/`plan` distintos de
  Build si vienen; con la clave Free por defecto el censo se detiene ANTES de la primera petición de datos.
  La ruta de la clave no se escribe en ningún recibo; `render` redacta la clave por defensa en profundidad.
- **Transporte:** host fijo, sin redirecciones (`NoRedirect`), sin reintentos, `timeout=60` por petición,
  pausa de 0,1 s (≤ 10 rps frente a 50 permitidos), cabeceras de crédito allowlist, `usage` por lista de campos.
- **Persistencia:** un recibo por celda con creación exclusiva (`open("x")`), estados y conteos, primer
  timestamp, presencia de cursor, hashes de cuerpos; ningún libro, precio ni cantidad; ningún markout.
- **Parada:** primer error HTTP, de transporte o de esquema; un vacío válido (`AUSENCIA_VALIDA`) continúa;
  `limit=1` violado → `LIMIT_NOT_RESPECTED`; saldo que sube → `ACCOUNT_BALANCE_INCREASED`. `receipt.json`
  se escribe en `finally` con `authenticated_requests_attempted`.
- **Alcance:** no selecciona días, no pagina, no descarga cuerpos. `CENSUS_QUERIES_COMPLETE` = consultas
  terminadas, no datos completos, como dice el relevo.

## 4. Hallazgos

**P1 (operativo, no de corrección): la cobertura genérica puede matar la única corrida en la celda 0.**
El contrato dice del endpoint de cobertura: «*May take 30-60 seconds on first request (gap detection
results are cached server-side for 1 hour)*». El cliente corta a 60 s; una primera respuesta de 60 s da
`OSError` (timeout) → `inspect_cell` devuelve con esa razón → `run` para con
`PARTIAL_CENSUS_STOPPED_AT_FIRST_ERROR`. Y ese endpoint es el PRIMERO de los tres por celda, así que
un fallo suyo deja la celda sin ninguna de las dos presencias, que son las medidas que la etapa 1 necesita.
Además es el único de los tres endpoints **no ejercitado nunca con dato real** (la etapa 0 ejercitó la
presencia). No se sabe si la caché de una hora es por símbolo o por ventana `from/to`; si es por
ventana, 149 primeras peticiones lentas ⇒ hasta ~75 min y 149 ocasiones de timeout.

Arreglo mínimo que propongo (unas diez líneas y un focal), sin cambiar lo que se mide ni el orden de celdas:

1. Por celda, consultar **primero checkpoint, luego tick, y la cobertura genérica al final**.
2. Para la ruta `generic_coverage`, `timeout=120` y **fallo NO fatal para el censo**: se registra la
   observación como `INDETERMINADO` con su razón (`TIMEOUT`, `HTTP_<código>`, `INVALID_COVERAGE_METADATA`)
   y la celda queda `CELL_QUERIES_COMPLETE_COVERAGE_INDETERMINADO`; las presencias siguen contando. Los
   errores HTTP/transporte en las DOS presencias siguen siendo parada dura, como está.
3. Un focal: cobertura que expira o devuelve esquema inválido ⇒ la celda conserva sus dos presencias y el
   censo continúa; y el control de que un error HTTP en una presencia sigue parando.

Si la mesa prefiere correrlo tal cual, es legítimo: el código es correcto y fail-closed; solo que un
timeout en la celda 0 obligaría a otra decisión y otra ronda.

**P2, sin cambio obligatorio:**
- `presence()` descarta el `detalle` del validador (texto constante con `coin`/`timestamp`, sin dato
  económico): conservarlo en el recibo ahorraría una ronda de diagnóstico si una celda cae por esquema.
- Coste de la cobertura genérica no publicado; con 80 M de créditos es irrelevante, pero el recibo lo dirá.
- Duración esperada si las coberturas son rápidas: ~5 min (447 llamadas × ~0,6 s).

## 5. Dictamen

Sin defectos de corrección. **Recomiendo aplicar el P1 antes de la ejecución única**, por Codex, y
reauditar el diff (será corto) antes de correr. Con el P1 aplicado, Code ejecuta el comando del relevo una
vez sobre `Desktop\Laboratorio\I5_CENSO_20260906_01`, con OneDrive cerrado, y lee cada recibo antes de
interpretar. Estados: **implementado** (Codex) · **verificado localmente** (18 focales, plan, hashes) ·
**auditado independientemente** (esta lectura, contra el OpenAPI guardado) · **con datos reales: no**.
