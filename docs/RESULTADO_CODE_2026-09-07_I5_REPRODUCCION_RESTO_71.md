# Code → Codex y mesa · 2026-09-07 · Reproducción de los 71 días restantes: 71 de 71 con igualdad numérica exacta en los ocho campos históricos; panel de 79 en `READY_FOR_D1_AUDIT`

Responde a `PARA_CODE_2026-09-07_I5_REPRODUCCION_RESTO_71.md`. Auditoría del incremento y **una ejecución** local,
sin red, sin clave y sin nueva descarga, en `Desktop\Laboratorio\I5_REPRODUCCION_RESTO_71_20260907_01`. Sin
inspección manual de NPZ ni de markouts: el instrumento abrió las copias de los originales y comparó, como
estaba autorizado; Code leyó recibos y conteos. Nada se declara ratificable. **La reproducción numérica no
acredita identidad de insumos con julio ni valida el +18,24.**

## 1. Auditoría del incremento

| comprobación | resultado |
|---|---|
| huellas | `i5_productor_resto.py` `74a83fae…`, `test_i5_productor_resto.py` `ad422d30…`, plan `_01` `ad7b6d58…`, verificación `e60473b2…`: todas = relevo. Los cuatro instrumentos auditados que el productor fija por constante siguen intactos (`e4011fc6…`, `e7b582f6…`, `dba1a31a…`, `d39234b2…`); especificación D1 `6e358b9c…` |
| focales | **28 passed** (34 s, basetemp nuevo); objetos git 667 antes y después |
| plan sin red | regenerado con las cuatro raíces del comando a un fichero propio: **751.869 bytes, `ad7b6d58…`, byte a byte igual** al entregado |
| ámbito | 71 fechas del manifiesto sin las ocho cerradas, todas < 30-06; 51 horas 404 fijadas por constante y exigidas exactamente en la cadena (un 404 en otra clave, o un fichero donde se declaró 404, para el plan) |
| lectores | `selected_sources`, `decode_snapshots`, `load_snapshots` y `load_trades` reutilizan el **mismo objeto de código** de los módulos auditados con un diccionario privado de globales (los 71 días y sus posiciones); los módulos importados conservan el ámbito de ocho días; `reproduce` y `compare` se llaman sin cambio |
| inventario | plan CHD `d1f38459…` y los dos intentos (`6aef7ca1…`, `9784180d…`) con sus `started`/`auth`, enlace de reanudación, cadena de 3.408 recibos con id de intento, tamaños de crudos, ausencia de huérfanos y resumen igual al del intento final; custodia de los ocho (`parent_inventory`) y 79 recibos L3 de A por hash |
| ejecución | salida fuera de repo, OneDrive, custodias y canónicos; `exigir_produccion`; plan por hash antes de abrir nada; **71 originales congelados en `originals/` antes de derivar el primer día**; cada cuerpo L3 y CHD verificado por hash al consumirlo; publicación con `AR.publicar` marcada no conforme; comparación del mismo comparador; los 71 se recorren aunque haya diferencia; al final re-hash de los 71 canónicos y del inventario de los ocho; panel solo `READY` si las 79 entradas son iguales |

**Sin defectos de corrección.** Mejora respecto al custodio: el recibo guarda `exception_type`.

**Corrección de la mesa a mi informe de custodia, comprobada y concedida:** las dos máscaras de
`i5_chd_custodia.py:347-348` hacen que `outside_requested_hour` incluya las filas `outside_requested_day`.
Recontado de los recibos por `event_time`: **79 filas fuera de hora en Lighter y 977 en Binance, 1.056 en total,
de las que 12 son del día anterior (1 y 11); dentro del día, 1.044 (78 y 966).** Mis cifras 80/988 sumaban otra
vez las filas de borde. No cambia ninguna fila custodiada ni ninguna admisión.

## 2. Ejecución

| campo | valor |
|---|---|
| comando | el de §5 del relevo, `--expected-plan-sha256 ad7b6d58…` |
| UTC | 16:42:33 → 16:48:29 (**5 min 56 s**, ~5 s por día) |
| estado / rc | **`REMAINING_71_COMPARED` · rc 0** |
| `matching_new_days` | **71 de 71** · `all_79_legacy_arrays_equal: true` · `canonical_originals_unchanged: true` |
| panel | `panel_79.json` **`READY_FOR_D1_AUDIT`**, 79 entradas: 8 `reused_eight` + 71 `new_remaining_71`, cada una con su recibo, NPZ y manifiesto por hash |
| recibos | `result.json` `a665e3de…` · `panel_79.json` `59611007…` · `plan.json` `ad7b6d58…` · `originals.json` `01935958…` |
| salida | 71 carpetas `DIA/LIT_DIA.npz` + manifiesto, 71 recibos diarios, `originals/` con 71 copias; 227 MB |

Verificación de Code por programa: los 71 recibos diarios coinciden con el hash que `result.json` les asigna;
los 71 tienen `comparison.state = LEGACY_ARRAYS_EQUAL` y **ningún campo desigual** (`mo`, `descartes`, `tipo`,
`slow`, `is_bid`, `owner`, `vol20`, `t_fill`: dtype, forma, máscaras NaN y valores exactos en los 71); ningún
día excluido por la receta (`historical_status` `ok:…` en los 71). **Los 79 originales canónicos son idénticos a
antes de ejecutar** por comprobación independiente de Code (sha256 de los 79 guardado antes y comparado
después; mtime de todos 2026-07-05) y por la del propio instrumento; `originals.json` coincide con esos hashes
en los 71 días. Resumen de Code: `Desktop\Laboratorio\I5_REPRODUCCION_RESTO_71_20260907_01_RESUMEN_CODE.json`.

## 3. Conteos de la receta en los 71 días (estados y recuentos; sin valores)

| | valor |
|---|---|
| eventos producidos | **1.048.669** (mín. 3.448 el 23-03 con 10/24 h; máx. 26.755 el 03-06) |
| de ellos `through` | 984.741 (93,9 %); por día entre **85,44 % (29-03) y 98,39 % (03-06)** |
| `fill` / `parcial` | 55.873 / 8.055 |
| cancelaciones contadas | 2.793.089; ambiguas 22.541; intervalos invalidados por hueco 37 |
| umbral de exclusión 2 × mediana | 327–443 s según el día |
| inversiones de `event_time` en el Lighter concatenado por horas | **0 en los 71 días** |

Cautelas ya fijadas por la mesa y vigentes aquí: el denominador de esos porcentajes son todos los eventos de la
receta, no la población decisoria lenta; los `fill` son imputaciones corroboradas por prints al precio, no
ejecuciones acreditadas; el umbral no es la separación máxima observada.

**Los siete días incompletos también reproducen igual** (23-03 con 10/24 h, 14-04 19/24, 28-05 8/24, 29-05
22/24, 03-06 22/24, 14-06 23/24, 15-06 13/24). Lectura de Code, no conclusión: que los arrays coincidan con las
horas ausentes es compatible con que la receta de julio tampoco viera trades de Lighter en esas horas; **no
identifica la causa entonces** (404, fichero vacío u otra) ni las horas que julio usó, como fijó la mesa.

## 4. Lo que sigue

El panel de 79 (`panel_79.json`) es la entrada del analizador D1 según `ESPEC_MESA_2026-09-07_D1_79_DIAS.md`:
Codex lo implementa con fixtures sintéticos y plan de análisis ligado por hash a los 79 NPZ (que D1 debe
verificar cuerpo a cuerpo contra las huellas del panel) y a la custodia CHD (T necesita la referencia Binance
al reloj nuevo; TV además los trades de Lighter). Code audita y ejecuta con plan fijado. D1 es retrospectivo
post hoc; sus ramas se publican todas. Nada de eso está ejecutado.

## 5. Tabla por día (comparación, eventos y cobertura)

| día | comparación | eventos | parcial | fill | through | through % | h Lighter |
|---|---|---|---|---|---|---|---|
| 03-07 | igual | 13.605 | 54 | 1.241 | 12.310 | 90,5 | 24 |
| 03-08 | igual | 19.535 | 80 | 1.081 | 18.374 | 94,1 | 24 |
| 03-09 | igual | 23.176 | 68 | 1.029 | 22.079 | 95,3 | 24 |
| 03-10 | igual | 20.949 | 151 | 930 | 19.868 | 94,8 | 24 |
| 03-11 | igual | 19.020 | 122 | 1.155 | 17.743 | 93,3 | 24 |
| 03-21 | igual | 17.533 | 189 | 957 | 16.387 | 93,5 | 24 |
| 03-22 | igual | 14.114 | 75 | 846 | 13.193 | 93,5 | 24 |
| 03-23 | igual | 3.448 | 33 | 269 | 3.146 | 91,2 | **10** |
| 03-24 | igual | 9.654 | 29 | 768 | 8.857 | 91,7 | 24 |
| 03-26 | igual | 6.981 | 31 | 629 | 6.321 | 90,5 | 24 |
| 03-28 | igual | 5.161 | 67 | 675 | 4.419 | 85,6 | 24 |
| 03-29 | igual | 5.034 | 105 | 628 | 4.301 | 85,4 | 24 |
| 03-30 | igual | 5.553 | 97 | 555 | 4.901 | 88,3 | 24 |
| 03-31 | igual | 9.482 | 131 | 735 | 8.616 | 90,9 | 24 |
| 04-01 | igual | 8.317 | 66 | 599 | 7.652 | 92,0 | 24 |
| 04-02 | igual | 13.180 | 61 | 668 | 12.451 | 94,5 | 24 |
| 04-03 | igual | 14.621 | 137 | 604 | 13.880 | 94,9 | 24 |
| 04-04 | igual | 10.632 | 86 | 683 | 9.863 | 92,8 | 24 |
| 04-05 | igual | 8.630 | 33 | 559 | 8.038 | 93,1 | 24 |
| 04-06 | igual | 11.862 | 45 | 559 | 11.258 | 94,9 | 24 |
| 04-09 | igual | 11.476 | 32 | 609 | 10.835 | 94,4 | 24 |
| 04-10 | igual | 12.228 | 62 | 423 | 11.743 | 96,0 | 24 |
| 04-11 | igual | 9.735 | 58 | 382 | 9.295 | 95,5 | 24 |
| 04-12 | igual | 9.251 | 84 | 415 | 8.752 | 94,6 | 24 |
| 04-13 | igual | 13.581 | 67 | 522 | 12.992 | 95,7 | 24 |
| 04-14 | igual | 9.450 | 24 | 446 | 8.980 | 95,0 | **19** |
| 04-15 | igual | 14.050 | 124 | 697 | 13.229 | 94,2 | 24 |
| 04-16 | igual | 14.570 | 212 | 766 | 13.592 | 93,3 | 24 |
| 04-17 | igual | 16.142 | 193 | 643 | 15.306 | 94,8 | 24 |
| 04-18 | igual | 11.773 | 291 | 669 | 10.813 | 91,8 | 24 |
| 04-20 | igual | 12.674 | 310 | 859 | 11.505 | 90,8 | 24 |
| 04-21 | igual | 13.887 | 244 | 1.058 | 12.585 | 90,6 | 24 |
| 04-23 | igual | 16.505 | 241 | 1.071 | 15.193 | 92,1 | 24 |
| 04-24 | igual | 13.403 | 239 | 836 | 12.328 | 92,0 | 24 |
| 04-25 | igual | 9.508 | 233 | 1.026 | 8.249 | 86,8 | 24 |
| 04-26 | igual | 10.431 | 232 | 1.108 | 9.091 | 87,2 | 24 |
| 04-27 | igual | 14.604 | 345 | 1.224 | 13.035 | 89,3 | 24 |
| 04-28 | igual | 15.456 | 285 | 1.268 | 13.903 | 90,0 | 24 |
| 04-29 | igual | 17.579 | 223 | 1.020 | 16.336 | 92,9 | 24 |
| 04-30 | igual | 12.916 | 221 | 1.057 | 11.638 | 90,1 | 24 |
| 05-01 | igual | 12.759 | 198 | 1.016 | 11.545 | 90,5 | 24 |
| 05-03 | igual | 15.084 | 234 | 1.129 | 13.721 | 91,0 | 24 |
| 05-04 | igual | 15.799 | 271 | 1.067 | 14.461 | 91,5 | 24 |
| 05-05 | igual | 15.927 | 231 | 977 | 14.719 | 92,4 | 24 |
| 05-06 | igual | 15.760 | 78 | 1.050 | 14.632 | 92,8 | 24 |
| 05-08 | igual | 15.887 | 112 | 809 | 14.966 | 94,2 | 24 |
| 05-09 | igual | 15.146 | 147 | 812 | 14.187 | 93,7 | 24 |
| 05-10 | igual | 12.616 | 147 | 851 | 11.618 | 92,1 | 24 |
| 05-11 | igual | 15.008 | 116 | 898 | 13.994 | 93,2 | 24 |
| 05-12 | igual | 13.096 | 122 | 999 | 11.975 | 91,4 | 24 |
| 05-13 | igual | 11.449 | 98 | 1.071 | 10.280 | 89,8 | 24 |
| 05-15 | igual | 16.648 | 115 | 1.035 | 15.498 | 93,1 | 24 |
| 05-16 | igual | 9.523 | 76 | 965 | 8.482 | 89,1 | 24 |
| 05-17 | igual | 9.034 | 44 | 945 | 8.045 | 89,1 | 24 |
| 05-18 | igual | 17.261 | 106 | 820 | 16.335 | 94,6 | 24 |
| 05-20 | igual | 25.457 | 99 | 504 | 24.854 | 97,6 | 24 |
| 05-22 | igual | 26.265 | 65 | 500 | 25.700 | 97,8 | 24 |
| 05-23 | igual | 23.185 | 135 | 564 | 22.486 | 97,0 | 24 |
| 05-28 | igual | 6.721 | 18 | 231 | 6.472 | 96,3 | **8** |
| 05-29 | igual | 22.302 | 46 | 601 | 21.655 | 97,1 | **22** |
| 06-03 | igual | 26.755 | 75 | 356 | 26.324 | 98,4 | **22** |
| 06-14 | igual | 21.636 | 122 | 630 | 20.884 | 96,5 | **23** |
| 06-15 | igual | 13.749 | 54 | 315 | 13.380 | 97,3 | **13** |
| 06-18 | igual | 23.988 | 134 | 577 | 23.277 | 97,0 | 24 |
| 06-19 | igual | 19.251 | 140 | 616 | 18.495 | 96,1 | 24 |
| 06-20 | igual | 16.680 | 121 | 768 | 15.791 | 94,7 | 24 |
| 06-21 | igual | 19.482 | 102 | 692 | 18.688 | 95,9 | 24 |
| 06-22 | igual | 25.302 | 167 | 668 | 24.467 | 96,7 | 24 |
| 06-26 | igual | 26.049 | 170 | 597 | 25.282 | 97,1 | 24 |
| 06-27 | igual | 20.879 | 180 | 698 | 20.001 | 95,8 | 24 |
| 06-28 | igual | 20.265 | 157 | 638 | 19.470 | 96,1 | 24 |

## 6. Estados

**implementado** (Codex) · **verificado localmente** (28 focales; plan byte a byte; recibos y originales
re-verificados por programa) · **auditado independientemente** (esta lectura) · **ejecutado una vez**
(`REMAINING_71_COMPARED`, rc 0) · **panel de 79: `READY_FOR_D1_AUDIT`** · **D1: no ejecutado** · **CI: no**.
STOP, freezes, pins y conjunto protegido vigentes. HEAD `7df5280`, sin commit.
