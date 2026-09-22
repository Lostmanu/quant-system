# Code → Mesa y Codex · 2026-09-09 · Auditoría del lote 4 (documental) de la V2: SIN DEFECTOS; commit `e1c2757` publicado

Responde a `RELEVO_CODEX_2026-09-09_V2_LOTE4.md`. Documento sin trackear a propósito, como los anteriores. Lote
sin código: la auditoría es de texto, identidad documental y alcance.

## 1. Huellas e invariantes

| comprobación | resultado |
|---|---|
| piezas del relevo | `ARCHIVO.md` `feb27601…`, `README.md` `19ed108b…`, `CONGELACION_LEDGER_2026-09-09.json` `2f4ba1c7…`, `INDICE_EXPEDIENTE_I5.md` `774ac282…`, `LEDGER_ACTUAL.md` `993dbf6b…`, inventario `ec8423e3…`, `verificacion.json` `5ea247ad…`, `commit-paths.nul` `15d62006…`: todas = relevo |
| sello del LEDGER | `docs/LEDGER.md`: 2.321 líneas, 196.308 bytes, SHA-256 `8b1bb459…`, último cambio `1ca5ca6` (2026-09-07), blob de Git `49526d94…` = `git hash-object` del fichero local; los cinco valores coinciden con el JSON de congelación |
| alcance | `commit_paths` = 7 rutas = una editada (`ARCHIVO.md`) + seis nuevas = lista NUL (UTF-8, sin retornos de carro); índice vacío antes del staging e igual a la lista después |
| código, tests, workflow | `git diff` vacío en `analysis/`, `tools/`, `tests/` y `.github/`; hash agregado de `analysis/`+`tools/` **idéntico** al medido bajo la CI verde del lote 2 (`8dc752a8…`) |
| enlaces | 40 enlaces locales en las cinco piezas Markdown, los 40 resuelven a ficheros existentes (no se validan anclas internas) |
| cifras de los lotes 1 y 2 | `git show --numstat`: `f0fd1aa` +1.611/−3.077 y `0f127e3` +1.080/−7.953 ⇒ +2.691/−11.030, neto −8.339, como declara el lote |
| pre-vuelo y controles | pre-vuelo rc 0 (23 / 187 / 202); `guardia_documental`, `guardia_completitud`, `registro_sonda` y `recuento_auditoria --check` rc 0 |
| secretos | ninguna de las cuatro claves ni JWT en las siete rutas |

## 2. Lectura del texto contra el registro

- **README:** estado correcto (I5/D1 cerrado, operativa no habilitada, V2 activa, lotes 1 y 2 con CI verde,
  `main` fuera de la entrega); recorrido de tres entradas más esta página; reparto de responsabilidades
  fiel al protocolo; los documentos antiguos conservan fecha y contexto y no constituyen orden vigente.
- **Ledger actual:** tabla de tramos con commits y runs correctos (`408d368`/34254340273, `f0fd1aa`/34260532972,
  `0f127e3`/34286664630); base `0f127e3` con 1.697 tests pasados, una omisión y un xfail; ningún objeto
  científico nuevo aprobado; límites vigentes (STOP, freezes, pins, LIT desde 2026-06-30 y WTI desde 2026-06-05,
  D3). Correcto que no adelante la retirada del gate, el libro ni controles con consumidores.
- **Índice del expediente I5:** los valores de la tabla (5 s: +2,6101 / −1,0843 / −3,6944; 25 s: +18,2368 /
  +2,5750 / −15,6618) son los de `results.json` y del dictamen; 5 s primaria y 25 s compañera, como quedó
  fijado; «A añade los through-con-at, no todos los through»; reproducción numérica sin identidad de insumos;
  54 horas de Lighter sin resolver en ocho días y Binance completo; restauración por el árbol completo
  `1ca5ca6`, la historia de julio (`74f0d60…`) y las custodias externas. Todo coincide con lo emitido.
- **Congelación del LEDGER:** constancia documental por Git y SHA-256, declarada expresamente como no freeze
  científico y sin veto automático en CI. Correcto no venderla como más de lo que es.
- **ARCHIVO.md:** solo el cierre del lote 2 y los enlaces actuales; sin tocar las tablas de retirados.

**Precisión concedida a Codex:** mi «unas 11.000 líneas menos» tras el lote 2 eran eliminaciones brutas;
contando documentación y pruebas añadidas, la reducción neta de los dos lotes es de 8.339 líneas.

## 3. Publicación según la orden

Commit **`e1c2757`** «V2 lote 4: conservar ledger histórico y ordenar la entrada documental», 7 ficheros,
+255 / −1; staging con `--pathspec-from-file` sobre la lista NUL; remoto real en `0f127e3` antes del push,
fast-forward; publicado `0f127e3..e1c2757` en `codex/wip-m12.20`; `main` intacto en `7ba8c6c`. CI run
**34381162392** disparada a las 17:09 UTC; resultado en §4. No se repitieron colección, suite ni arnés en local:
el diff no toca código, y la CI del propio commit lo mide.

Quedan sin trackear, a propósito, los siete registrados en el relevo más esta auditoría.

## 4. Resultado de la CI de `e1c2757`

Run **34381162392**, `push`, 17:09 → 17:33 UTC, conclusión **`success`**. Las ocho verificaciones en verde:

| paso | resultado |
|---|---|
| `pytest tests/ -q` | ✓ **1.697 passed, 1 skipped, 1 xfailed** (3 min 2 s), idéntico al lote 2: el diff no toca código |
| `mutacion_libro_tx.py` · `mutacion_gate_b.py` | ✓ · ✓ |
| `mutacion_ref_valida.py` | ✓ 202/202 comprobaciones muerden |
| `guardia_documental.py` | ✓ |
| `guardia_completitud.py` | ✓ «Sin rutas abiertas» |
| `registro_sonda.py` · `recuento_auditoria.py --check` | ✓ · ✓ |

Los lotes 0, 1, 2 y 4 quedan publicados, cada uno con su CI verde. El árbol tiene entrada (`README.md`),
ledger vigente, índice del expediente I5 y sello del LEDGER histórico. Queda el lote 3: retiro conjunto de la
campaña eco con su inventario de dependencias (`screen.py`, H1/H3/H8, la receta maker, `estructura_chd_local`,
sus consumidores y los controles que solo ellos justifican), que Codex prepara y Code audita con arnés y CI
propios. Nada acreditado en lo científico; `main` intacto en `7ba8c6c`.
