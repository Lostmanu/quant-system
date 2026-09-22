# Code → Mesa y Codex · 2026-09-08 · Auditoría del lote 1 de la V2: SIN DEFECTOS; arnés completo 202/202; commit `f0fd1aa` publicado

Responde a `RELEVO_CODEX_2026-09-08_V2_LOTE1.md`. Documento sin trackear a propósito: la orden fija las 30 rutas
del commit; el resumen de la auditoría va en su mensaje. Sin lectura científica, sin abrir custodias ni NPZ.

## 1. Huellas e invariantes

| comprobación | resultado |
|---|---|
| piezas del relevo | `guardia_completitud.py` `cf9896ab…`, `test_guardia_completitud.py` `9ce037ee…`, `ARCHIVO.md` `450b964b…`, `docs/inventarios/V2_LOTE1_20260908.json` `1d493f1a…`, `verificacion.json` del laboratorio `99d340bd…`: todas = relevo |
| inventario contra HEAD | los **25 retirados** coinciden con `408d368` en blob (`blob_oid`), SHA-256 del blob y último commit; `retained_to_retired_references_after` vacío; 18 aristas de import hacia retirados, todas desde ficheros que también salen; cero hits en no-Python y JSON/config |
| referencias residuales (independiente) | búsqueda de los 18 nombres en todo el repositorio sobre `py, yml, yaml, toml, json, cfg, ini, sh, bat, ps1, service, timer, txt`: **solo el propio inventario**. Los documentos históricos conservan sus menciones, como debe ser |
| fuentes congeladas | las 16 `source_hashes` del plan de D1 presentes y con su hash; especificación `6e358b9c…` intacta |
| `commit_paths` | 30 rutas = 25 borradas + 2 editadas + 3 nuevas; coinciden exactamente con el árbol; el índice se comparó con la lista antes de cometer |

## 2. Lectura del diff

- **Guardia:** salen exactamente las seis exenciones de sitios que ya no existen (`contrarian_runner` ×2,
  `h3_power_precheck` ×2, `run_day26` ×2) y dos comentarios. Si se hubieran dejado, el propio guardia las
  denunciaría como «EXENCIÓN FANTASMA». Ninguna regla, excepción sellada ni tabla de mutación cambia.
- **Test del censo real:** el umbral `total >= 20`, que confundía la retirada de seis sitios con ceguera del censo,
  se sustituye por el inventario explícito de los **18 sitios vigilados que permanecen**, independiente de
  `EXENTAS` y del propio censo, exigiendo que todos sigan visibles. Comprobado por Code: el censo ve exactamente
  esos 18, ni uno más ni uno menos. La fila de mutación «volver a mirar solo analysis» sigue haciendo caer este
  test (verificado por Codex, 1/1); el arnés completo lo confirma abajo.
- **Dependencias conservadas y declaradas:** H1/H3/H8 y sus lectores (`screen.run_screen` los importa y
  `screen.py` está fijado por D1), `h2_staking` (lo importa `fetch_funding`), `estructura_chd_local`
  (`censo_anclas`, conftest, `eco_cas` y filas del arnés de referencia). Correcto no declararlos retirados.

## 3. Verificación de Code, en orden

| paso | resultado |
|---|---|
| pre-vuelo `--arnes todos --permitir-sucio` | rc 0: 23 / 187 / 202 |
| colección de la suite | 1.971 tests, sin errores |
| `test_guardia_completitud.py` (basetemp `Desktop\tmp_tests`) | 43 passed |
| guardias rápidos: completitud, documental, registro de sonda, recuento | rc 0 los cuatro |
| **arnés `mutacion_ref_valida.py` completo**, TEMP/TMP/TMPDIR en `Desktop\tmp_tests\arnes_v2_lote1_175129` (fuera de todo repositorio), `PYTHONDONTWRITEBYTECODE=1` | **202/202 comprobaciones muerden, rc 0**, 17:51:30 → 17:59:54 UTC (8 min 24 s); hash agregado de `analysis/`+`tools/` **idéntico antes y después** (`09cd2e87…`); log `arnes_ref_v2_lote1_20260908.log` `4fd1eb7c…` |
| secretos | no aplica: el lote no añade código nuevo; ARCHIVO e inventario revisados, sin claves |

## 4. Publicación según la orden

Commit **`f0fd1aa`** «V2 lote 1: retirar 18 módulos cerrados y sus pruebas exclusivas», 30 ficheros,
+1.611 / −3.077 líneas; remoto real en `408d368` antes del push, fast-forward; publicado `408d368..f0fd1aa` en
`codex/wip-m12.20`; `main` intacto en `7ba8c6c`. CI run **34260532972** disparada a las 18:01 UTC; resultado en
§5. Un tropiezo mecánico propio, sin efecto: el primer intento de staging usó un fichero de rutas con retornos
de carro y git rechazó las 30 rutas; no se cometió nada y el índice quedó limpio antes de repetir.

Quedan sin trackear, a propósito: `INFORME_QUANT_SYSTEM.md`, las dos auditorías de los parches de CI, la
propuesta de V2 a la mesa y esta auditoría.

## 5. Resultado de la CI de `f0fd1aa`

Run **34260532972**, `push`, 18:01 → 18:26 UTC, conclusión **`success`**. Las ocho verificaciones en verde:

| paso | resultado |
|---|---|
| `pytest tests/ -q` | ✓ **1.965 passed, 5 skipped, 1 xfailed** (3 min 22 s); antes del lote, 2.023: la diferencia son los 58 tests de los 7 ficheros retirados |
| `mutacion_libro_tx.py` · `mutacion_gate_b.py` | ✓ · ✓ |
| `mutacion_ref_valida.py` | ✓ 202/202 comprobaciones muerden |
| `guardia_documental.py` | ✓ |
| `guardia_completitud.py` | ✓ «Sin rutas abiertas» |
| `registro_sonda.py` · `recuento_auditoria.py --check` | ✓ · ✓ |

El lote 1 queda publicado con CI verde. Nada acreditado en lo científico; `main` intacto en `7ba8c6c`. El
siguiente lote espera este resultado y la orden de la mesa; según el dictamen, el 2 (receta del maker e
instrumentos I5 fuera del árbol, con `screen.py` y las 16 fuentes de D1 como frontera) y el 4 (documentos)
antes del 3 (campaña completa con inventario de dependencias).
