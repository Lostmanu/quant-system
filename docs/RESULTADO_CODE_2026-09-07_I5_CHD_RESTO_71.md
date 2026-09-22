# Code → Codex y mesa · 2026-09-07 · Custodia de los 71 días COMPLETA EN RECORRIDO: 3.357 de 3.408 claves custodiadas, 51 × 404 en Lighter; combinado de 79 días: 3.738 de 3.792

Responde a la orden de mesa de continuar el intento 0 (`RESULTADO_CODE_2026-09-07_I5_CHD_RESTO_71_INTENTO0.md`,
§4). La continuación se ejecutó **una vez**, tal como estaba escrita, ligada al intento parado
`6aef7ca1…`. Sin reintentos, sin sondas, sin reconsultar 404. Ningún parquet abierto por Code. Nada se declara
ratificable; **el recorrido completo de las claves no es completitud del archivo ni del mercado.**

Precisiones de la mesa incorporadas: los 120,1 s de la parada anterior son compatibles con un tiempo de
espera durante el salto, pero sin excepción registrada no acreditan su causa exacta ni que fuera transitoria; y
un 404 acredita una clave sin resolver, no un fallo de captura: que Binance esté completo y el L3 disponible
no lo demuestra por sí solo. Este informe se limita a los hechos de los recibos.

## 1. Intento 1 (continuación) y contabilidad de los dos intentos

| campo | valor |
|---|---|
| pre-vuelo de reanudación | hash del intento 0 = `6aef7ca1…` (comprobado por Code antes de lanzar); plan `d1f38459…`; 1.489 horas heredadas con punta `949cfa2b…`; 1.470 crudos re-verificados; 0 parciales; OneDrive parado |
| UTC | 12:25:05 → 13:42:50 (77,7 min) |
| JWT | nuevo, emitido 12:25:07, `expires_in` 14.400 s |
| estado / rc | **`CUSTODY_COMPLETE_REQUIRES_REVIEW` · rc 2** (por diseño: hay 404 y ficheros de borde) |
| recorridas en el intento | 1.919 (índices 1489–3407): 1.887 custodiadas + 32 × 404 |
| `remaining_new_hour_keys` | **0** |
| recibo | `attempts/0001.json` `9784180d…`; `.started.json` `e4b3ccbe…`; `.auth.json` `107aa2d9…` |

| intento | llamadas API | saltos | HTTP | tope HTTP |
|---|---|---|---|---|
| 0 (`STOPPED`) | 1.491 | 1.471 | 2.962 | 6.817 |
| 1 (continuación) | 1.920 | 1.887 | 3.807 | 3.839 |
| total | 3.411 | 3.358 | **6.769** | |

Los saltos que faltan hasta el tope son los 404 (sin salto) y el salto fallido del intento 0. Las 3.357
descargas saltaron al mismo host R2 (`…r2.cloudflarestorage.com`), todas con `credentials_sent = none`; ninguna
cadena `X-Amz`, `Signature`, `Credential` ni ruta del almacén en la carpeta. 0 `.part`.

## 2. Verificación de la custodia (Code, por programa)

| comprobación | resultado |
|---|---|
| recibos | 3.408 de 3.408 índices; cadena `previous_receipt_sha256` íntegra a través de los dos intentos (0 roturas) |
| crudos | 3.357 ficheros; sha256 de cada uno = `body_sha256` de su recibo (3.357 de 3.357); 6.765 ficheros en `hours/` = 3.408 recibos + 3.357 crudos |
| vacíos / horas con 0 filas | 0 / 0 |
| unidades | `event_time` ms y `received_time` ns en los 3.357; `historical_event_ms` verdadero en todos |
| inversiones de `event_time` dentro de cada fichero | 0 |
| esquema | idéntico en los 3.357 (el de los ocho días) |
| tamaño | 367,2 MB de cuerpo; 374 MB en disco con recibos |

Resumen de Code, fuera de la carpeta custodiada:
`Desktop\Laboratorio\I5_CHD_RESTO_71_20260907_01_RESUMEN_CODE.json` `6e8002ac…`.

## 3. Inventario de las 3.408 claves nuevas por fuente

| fuente | días | días 24/24 | horas custodiadas | 404 | filas | cuerpo MB | filas/día min · mediana · max | filas fuera de su hora (ev.) | borde | inversiones |
|---|---|---|---|---|---|---|---|---|---|---|
| LIT / lighter | 71 | **64** | 1.653 | **51** | 2.383.527 | 43,3 | 10.513 · 25.836 · 109.901 | 80 | 1 | 0 |
| LITUSDT / binance_futures | 71 | 71 | 1.704 | 0 | 27.181.937 | 323,9 | 45.019 · 242.886 · 3.158.163 | 988 | 3 | 0 |

### 3.1 Claves sin resolver (HTTP 404 de la API, sin salto): todas en LIT/lighter, 7 días

| día | horas 404 | horas custodiadas | Binance el mismo día | hueco L3 declarado (censo 0xArchive) |
|---|---|---|---|---|
| 2026-03-23 | 05–18 (14) | 10/24 | 24/24 | ninguno |
| 2026-04-14 | 18–22 (5) | 19/24 | 24/24 | ninguno |
| 2026-05-28 | 02–17 (16) | 8/24 | 24/24 | ninguno |
| 2026-05-29 | 18–19 (2) | 22/24 | 24/24 | ninguno |
| 2026-06-03 | 00–01 (2) | 22/24 | 24/24 | ninguno |
| 2026-06-14 | 00 (1) | 23/24 | 24/24 | ninguno |
| 2026-06-15 | 01–11 (11) | 13/24 | 24/24 | ninguno |

51 horas en 7 días; siempre bloques de horas consecutivas. Se conservan como claves sin resolver, sin
reconsultar, sin rellenar y sin tratar como mercado vacío (§6 de la especificación). Con las tres del 29-06,
el panel de 79 días tiene **54 horas de Lighter sin resolver en 8 días** de 1.896 horas posibles (2,8 %); los
tres días más afectados son 05-28 (8/24), 03-23 (10/24) y 06-15 (13/24).

### 3.2 Bordes por reloj de recepción

Cuatro ficheros nuevos con `boundary_review_required` (más el de 04-08 ya conocido: cinco en el combinado),
todos hora 00 con filas cuyo `event_time` es del día anterior a 23:59:59,9: 05-04 LIT (1 fila), 05-28 LITUSDT
(4), 06-03 LITUSDT (6), 06-18 LITUSDT (1). Y 1.068 filas con `event_time` fuera de su hora dentro del mismo día
(80 Lighter, 988 Binance). Es la partición por reloj de recepción ya documentada; no se filtra nada.

## 4. Combinado de 79 días (`combined_79` del recibo: 384 anteriores + 3.408 nuevas)

| | valor |
|---|---|
| claves recorridas | **3.792 de 3.792** |
| ficheros custodiados | **3.738** |
| HTTP 404 sin resolver | **54** (todos LIT/lighter; 8 días) |
| vacíos | 0 |
| ficheros de borde | 5 |
| unidades no históricas | 0 |
| cuerpo | 402,2 MB |
| Lighter: días 24/24 | 71 de 79 |
| Binance: días 24/24 | 79 de 79 |

Tener recibo de las 3.792 claves no significa tener sus 3.792 ficheros: faltan 54, visibles y sin resolver.

## 5. Tabla por día de las 71 fechas nuevas (horas custodiadas y filas; 404 en Lighter)

| día | LIT h | LIT filas | LITUSDT h | LITUSDT filas | 404 LIT (horas) |
|---|---|---|---|---|---|
| 03-07 | 24 | 34.597 | 24 | 62.559 | - |
| 03-08 | 24 | 50.856 | 24 | 105.754 | - |
| 03-09 | 24 | 68.260 | 24 | 165.868 | - |
| 03-10 | 24 | 57.437 | 24 | 150.943 | - |
| 03-11 | 24 | 34.172 | 24 | 80.752 | - |
| 03-21 | 24 | 37.741 | 24 | 103.385 | - |
| 03-22 | 24 | 36.041 | 24 | 107.651 | - |
| 03-23 | **10** | 16.311 | 24 | 131.004 | 05–18 |
| 03-24 | 24 | 12.778 | 24 | 90.147 | - |
| 03-26 | 24 | 14.481 | 24 | 77.373 | - |
| 03-28 | 24 | 13.578 | 24 | 49.559 | - |
| 03-29 | 24 | 10.513 | 24 | 45.019 | - |
| 03-30 | 24 | 12.422 | 24 | 53.754 | - |
| 03-31 | 24 | 17.108 | 24 | 80.303 | - |
| 04-01 | 24 | 18.048 | 24 | 118.877 | - |
| 04-02 | 24 | 34.128 | 24 | 460.875 | - |
| 04-03 | 24 | 31.744 | 24 | 521.073 | - |
| 04-04 | 24 | 21.325 | 24 | 247.177 | - |
| 04-05 | 24 | 22.186 | 24 | 244.372 | - |
| 04-06 | 24 | 26.830 | 24 | 390.225 | - |
| 04-09 | 24 | 16.247 | 24 | 283.703 | - |
| 04-10 | 24 | 25.514 | 24 | 578.631 | - |
| 04-11 | 24 | 21.626 | 24 | 445.803 | - |
| 04-12 | 24 | 29.832 | 24 | 465.676 | - |
| 04-13 | 24 | 25.011 | 24 | 490.186 | - |
| 04-14 | **19** | 16.313 | 24 | 443.358 | 18–22 |
| 04-15 | 24 | 30.245 | 24 | 290.984 | - |
| 04-16 | 24 | 22.183 | 24 | 265.775 | - |
| 04-17 | 24 | 33.461 | 24 | 421.441 | - |
| 04-18 | 24 | 19.967 | 24 | 223.761 | - |
| 04-20 | 24 | 25.836 | 24 | 181.480 | - |
| 04-21 | 24 | 16.520 | 24 | 193.900 | - |
| 04-23 | 24 | 24.471 | 24 | 252.137 | - |
| 04-24 | 24 | 18.585 | 24 | 183.505 | - |
| 04-25 | 24 | 11.301 | 24 | 118.009 | - |
| 04-26 | 24 | 13.762 | 24 | 101.625 | - |
| 04-27 | 24 | 27.101 | 24 | 178.211 | - |
| 04-28 | 24 | 28.665 | 24 | 160.051 | - |
| 04-29 | 24 | 29.913 | 24 | 384.066 | - |
| 04-30 | 24 | 17.852 | 24 | 242.886 | - |
| 05-01 | 24 | 12.072 | 24 | 191.895 | - |
| 05-03 | 24 | 22.916 | 24 | 122.540 | - |
| 05-04 | 24 | 25.504 | 24 | 168.835 | - |
| 05-05 | 24 | 24.632 | 24 | 279.847 | - |
| 05-06 | 24 | 21.973 | 24 | 153.424 | - |
| 05-08 | 24 | 35.437 | 24 | 331.424 | - |
| 05-09 | 24 | 33.125 | 24 | 251.284 | - |
| 05-10 | 24 | 23.427 | 24 | 182.672 | - |
| 05-11 | 24 | 18.137 | 24 | 216.868 | - |
| 05-12 | 24 | 21.867 | 24 | 139.390 | - |
| 05-13 | 24 | 12.065 | 24 | 145.796 | - |
| 05-15 | 24 | 38.104 | 24 | 188.463 | - |
| 05-16 | 24 | 12.939 | 24 | 102.044 | - |
| 05-17 | 24 | 12.149 | 24 | 106.146 | - |
| 05-18 | 24 | 42.461 | 24 | 241.320 | - |
| 05-20 | 24 | 93.711 | 24 | 2.427.354 | - |
| 05-22 | 24 | 66.571 | 24 | 1.436.207 | - |
| 05-23 | 24 | 78.342 | 24 | 983.298 | - |
| 05-28 | **8** | 17.768 | 24 | 463.719 | 02–17 |
| 05-29 | **22** | 55.653 | 24 | 1.207.499 | 18–19 |
| 06-03 | **22** | 109.901 | 24 | 3.158.163 | 00–01 |
| 06-14 | **23** | 46.567 | 24 | 543.633 | 00 |
| 06-15 | **13** | 35.781 | 24 | 687.472 | 01–11 |
| 06-18 | 24 | 97.340 | 24 | 864.752 | - |
| 06-19 | 24 | 52.197 | 24 | 484.168 | - |
| 06-20 | 24 | 36.142 | 24 | 294.582 | - |
| 06-21 | 24 | 31.742 | 24 | 350.704 | - |
| 06-22 | 24 | 52.891 | 24 | 583.996 | - |
| 06-26 | 24 | 109.781 | 24 | 836.923 | - |
| 06-27 | 24 | 66.217 | 24 | 400.770 | - |
| 06-28 | 24 | 51.154 | 24 | 444.891 | - |

Las 71 fechas son las del manifiesto, no todos los días naturales del intervalo.

## 6. Lo que sigue, según la especificación

Productor de los 71 días (Codex) sobre esta custodia y la L3 de A, con la misma receta y el mismo comparador
que los ocho, contrastando cada día contra su original **incluidos los ocho días incompletos**, con la cautela ya
fijada: la igualdad no identifica las horas que usó julio. Con el panel de 79 contrastado, el analizador D1 con
plan de análisis ligado por hash (NPZ y custodia CHD, porque T necesita la referencia Binance al reloj nuevo y TV
además los trades de Lighter). Nada de eso está ejecutado.

## 7. Estados

**implementado** (Codex) · **verificado localmente** (23 focales; plan byte a byte; cadena y 3.357 crudos
re-verificados por programa) · **auditado independientemente** (intento 0) · **ejecutado**: intento 0
(`STOPPED`, 1.489) + intento 1 por orden de mesa (`CUSTODY_COMPLETE_REQUIRES_REVIEW`, 3.408 recorridas) ·
**CI: no** · **producción de los 71 y D1: no**. STOP, freezes, pins y conjunto protegido vigentes. HEAD
`7df5280`, sin commit.
