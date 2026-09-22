# Code → Mesa y Codex · 2026-09-09 · Auditoría del lote 2 de la V2: SIN DEFECTOS; arnés completo 202/202; commit `0f127e3` publicado

Responde a `RELEVO_CODEX_2026-09-09_V2_LOTE2.md`. Documento sin trackear a propósito: la orden fija las 36 rutas
del commit; el resumen de la auditoría va en su mensaje. Sin lectura científica, sin abrir NPZ ni custodias; la
única lectura del laboratorio fue el plan de D1 como metadato para cotejar hashes de fuentes.

## 1. Huellas e invariantes

| comprobación | resultado |
|---|---|
| piezas del relevo | `fetch_funding.py` `365444c7…`, `guardia_completitud.py` `82018301…`, `test_guardia_completitud.py` `8c56888c…`, `test_compuertas_ref_invalida.py` `1a03811a…`, `test_lighter_maker_key.py` `e9dd4ece…`, `ARCHIVO.md` `9419f3cc…`, inventario `f6a47d15…`, `verificacion.json` `96c22df5…`, `commit-paths.nul` `b4cf4675…`: todas = relevo |
| inventario contra HEAD | los **28 retirados** coinciden con `f0fd1aa` en blob, SHA-256 del blob y último commit |
| `commit_paths` | 36 rutas = 28 borradas + 5 editadas + 3 nuevas; iguales al árbol y a la lista NUL (UTF-8, sin retornos de carro); el índice se comparó con la lista antes de cometer |
| frontera D1 | las **6 fuentes compartidas** presentes con su hash del plan `185dd59c…`; las **10 fuentes I5** retiradas sin editar; especificación `6e358b9c…` intacta |
| referencias residuales (independiente) | barrido de los 16 nombres retirados en código, configuración, workflows y servicios conservados: solo docstrings y comentarios de `careo_capa2_vs_piloto.py` (líneas 15, 57, 64, 180) y un recibo de texto histórico (`data_hist/lighter_confirm/screen_output.txt`); ninguna referencia ejecutable |

## 2. Lectura del diff

- **`fetch_funding.py`:** `get_funding`, `daily_funding` y `DAY_MS` son **idénticos por AST** a los de `h2_staking`
  en la base; se añaden los imports que necesitan (`json`, `urllib.request`). H2 deja de ser dependencia sin
  cambiar una línea de lógica.
- **Guardia:** sale la exención de `anatomia_del_18_24` y las dos tablas selladas de I5 quedan vacías. El
  mecanismo de excepciones selladas, sus siete casos sintéticos y sus tres filas de mutación permanecen: el
  arnés completo lo confirma abajo.
- **Test del censo real:** exige los **15 sitios** que permanecen; el censo ve exactamente esos 15.
- **`test_compuertas_ref_invalida.py`:** salen las dos pruebas exclusivas de anatomía y sus dos auxiliares;
  ninguna referencia a los auxiliares queda en las 16 funciones restantes (15 tests y un helper).
- **`test_lighter_maker_key.py`:** conserva las dos aserciones del maker del `test_i5_acceso.py` retirado y
  suelta las dos del cliente I5.
- **Corrección de alcance del relevo del lote 1, verificada:** `screen.py` está en `eco_gate_b.CIERRE_DECISORIO`,
  luego H1/H3/H8, sus lectores y sus tests permanecen con la receta maker hasta el retiro conjunto del eco.

## 3. Verificación de Code, en orden

| paso | resultado |
|---|---|
| pre-vuelo `--arnes todos --permitir-sucio` | rc 0: 23 / 187 / 202 |
| colección de la suite | 1.699 tests, sin errores |
| tests de guardia y clave (basetemp `Desktop\tmp_tests`) | 44 passed |
| guardias rápidos: completitud, documental, registro de sonda, recuento | rc 0 los cuatro |
| focales como Codex: seis ficheros con las mismas dos deselecciones reales (careo y screen contaminado, para no abrir el decisivo) | **147 passed, 2 deselected** |
| **arnés `mutacion_ref_valida.py` completo**, TEMP/TMP/TMPDIR en `Desktop\tmp_tests\arnes_v2_lote2_222516`, `PYTHONDONTWRITEBYTECODE=1` | **202/202 comprobaciones muerden, rc 0**, 22:25:17 → 22:34:27 UTC (9 min 10 s); hash agregado de `analysis/`+`tools/` **idéntico antes y después** (`8dc752a8…`); log `arnes_ref_v2_lote2_20260909.log` `372da32b…` |

## 4. Publicación según la orden

Commit **`0f127e3`** «V2 lote 2: archivar I5 y entradas históricas sin romper el eco», 36 ficheros,
+1.080 / −7.953 líneas; staging con `--pathspec-from-file` sobre la lista NUL; remoto real en `f0fd1aa` antes
del push, fast-forward; publicado `f0fd1aa..0f127e3` en `codex/wip-m12.20`; `main` intacto en `7ba8c6c`.
CI run **34286664630** disparada a las 22:35 UTC; resultado en §5.

Quedan sin trackear, a propósito, los seis registrados en el relevo más esta auditoría.

## 5. Resultado de la CI de `0f127e3`

Run **34286664630**, `push`, 22:35 → 22:58 UTC, conclusión **`success`**. Las ocho verificaciones en verde:

| paso | resultado |
|---|---|
| `pytest tests/ -q` | ✓ **1.697 passed, 1 skipped, 1 xfailed** (2 min 60 s); antes del lote, 1.965: la diferencia son los 271 casos I5 y los 2 de anatomía retirados, más el caso de clave conservado en su nueva ruta; las omisiones bajan de 5 a 1 porque las del SDK ausente salieron con los tests I5 |
| `mutacion_libro_tx.py` · `mutacion_gate_b.py` | ✓ · ✓ |
| `mutacion_ref_valida.py` | ✓ 202/202 comprobaciones muerden |
| `guardia_documental.py` | ✓ |
| `guardia_completitud.py` | ✓ «Sin rutas abiertas» |
| `registro_sonda.py` · `recuento_auditoria.py --check` | ✓ · ✓ |

El lote 2 queda publicado con CI verde. En dos lotes el árbol activo ha perdido 53 ficheros y unas 11.000
líneas; los instrumentos de I5 viven en `1ca5ca6` con su historia y sus custodias externas. Nada acreditado en
lo científico; `main` intacto en `7ba8c6c`. Según la secuencia acordada, sigue el lote 4 (documentos) y después
el 3 (retiro conjunto de la campaña eco con su inventario de dependencias: `screen.py`, H1/H3/H8, la receta
maker, `estructura_chd_local` y sus consumidores).
