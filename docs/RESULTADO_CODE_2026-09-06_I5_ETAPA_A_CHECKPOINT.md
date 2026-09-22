# Code → Mesa y Codex · 2026-09-06 · Etapa A ejecutada: custodia checkpoint de las 149 celdas — 149/149 agotadas

**Resultado: `ALL_SOURCE_PAGINATIONS_EXHAUSTED`, rc 0.** 149 recorridos checkpoint, una página cada uno, 151
llamadas autenticadas, 21 minutos, 149 créditos. Los bytes originales de las 149 respuestas están custodiados
en gzip con recibos encadenados. Agotar la paginación del proveedor no es completitud del archivo; presencia no es
integridad intradía. Nada se declara ratificable.

## 1. Identidad

| campo | valor |
|---|---|
| comando | el de la etapa A del relevo `PARA_CODE_2026-09-06_I5_DESCARGA_ETAPAS.md`, `--resolutions checkpoint --cells all` |
| instrumento | `i5_descarga_l3.py` `fcc6f6fa…` (re-verificado al arrancar), `i5_oxa_io.py` `9a96fecb…`, inventario de huecos `625928f0…`, manifiesto `0d913aae…` |
| plan emitido por Code sin red | idéntico como objeto JSON al `etapa_A_plan.json` guardado por Codex |
| salida | `Desktop\Laboratorio\I5_L3_CHECKPOINT_20260906_01\` (plan.json, attempts/0000.json, 149 carpetas de recorrido con `page_000000.json.gz`, su recibo y `job_receipt.json`) |
| UTC | 21:39:52 → 22:00:48 |
| máquina | sin OneDrive; 500,4 GB libres antes, 499,6 después |

## 2. Cuenta Build

| | usados | restantes | peticiones |
|---|---|---|---|
| antes | 299 | 79.999.701 | 499 |
| después | 448 | 79.999.552 | 649 |

Delta 149 = una página por recorrido, un crédito por página.

## 3. Medidas por símbolo (recibos de recorrido, agregadas por programa)

| | LIT (79 días) | DOGE (70 días) |
|---|---|---|
| snapshots/día min / mediana / max | 389 / 495 / 527 | 390 / 491 / 531 |
| snapshots totales | 37.984 | 33.190 |
| crudo por día, MB min / mediana / max | 26,7 / 34,1 / 36,1 | 5,7 / 10,5 / 16,9 |
| crudo total · gzip total · ratio | 2,61 GB · 354 MB · 7,4 | 0,74 GB · 61 MB · 12,2 |
| descarga por día, s min / mediana / max | 4,4 / 6,5 / 70,4 | 1,8 / 2,6 / 17,1 |
| caudal mediano | 5,1 MB/s | 3,8 MB/s |
| snapshots truncados a 250/lado | **37.984 de 37.984** | 71 de 33.190 |
| separación máxima entre snapshots, s min / mediana / max | 172 / 201 / 1.286 | 167 / 204 / 1.286 |
| primer snapshot tras 00:00 UTC, mediana / max | 85 s / 202 s | 94 s / 202 s |
| último snapshot antes de 24:00 UTC, mediana / max | 94 s / 216 s | 83 s / 214 s |

Total custodiado: **3,35 GB crudos, 414 MB en disco.** Todas las páginas terminaron con cursor omitido: cada
día cupo en una página de 1.000.

**LIT está siempre truncado**: los 37.984 snapshots llevan `truncated=true`, es decir, el libro servido está
recortado a 250 órdenes por lado en todo momento. Es un dato para el productor y para cualquier medida de cola:
el L3 de LIT que se conserva es una vista parcial por construcción.

## 4. Contraste de los huecos declarados con lo descargado

Separaciones consecutivas > 600 s en la serie checkpoint descargada, frente a los intervalos declarados por el
proveedor en el censo:

| | LIT | DOGE |
|---|---|---|
| días con separación > 600 s | 14 | 8 |
| separaciones > 600 s | 17 | 8 |
| de ellas que contienen un hueco declarado | **17 de 17** | **8 de 8** |
| huecos declarados con filas interiores | 0 de 17 | 0 de 8 |
| huecos declarados con ambos extremos observados como snapshots | 17 de 17 | 8 de 8 |

Lectura: a resolución checkpoint, **el proveedor declara exactamente los huecos que sirve y no hay ninguno sin
declarar** mayor de 10 minutos. Los extremos de cada hueco son el último snapshot antes y el primero después,
como define su contrato. Esto acredita coherencia interna del archivo del proveedor en checkpoint; no dice nada
de tick, ni de lo que ocurrió en el mercado durante esos minutos.

## 5. Etapa B

Con A terminada, contabilidad válida y sin fallos, Code ha lanzado la etapa B según el relevo: tick de LIT
2026-03-06 (índice 70), carpeta `I5_L3_TICK_LIT_20260306_20260906_01`. Su recibo dará snapshots, bytes, ratio y
tiempos reales del tick; hasta entonces ninguna cifra de volumen tick está acreditada.

Estados: **ejecutado** (A, una vez) · **verificado localmente** (recibos íntegros, agregado por programa) ·
**auditado independientemente**: no (informe del ejecutor) · CI: no aplica.
