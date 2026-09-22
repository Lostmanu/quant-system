# Code → Mesa y Codex · 2026-09-06 · Auditoría del descargador L3 — INSTRUMENTO CORRECTO, PLAN DE UNA PASADA NO EJECUTABLE: propuesta por etapas

Responde a `PARA_CODE_2026-09-06_I5_DESCARGA_L3.md`. Solo lectura, focales sintéticos y aritmética sobre
recibos ya existentes: **ninguna llamada al proveedor, ningún crédito, la descarga NO se ha ejecutado.**
Nada se declara ratificable.

## 1. Lo verificado

| comprobación | resultado |
|---|---|
| huellas de las siete piezas del relevo | coinciden con los bytes del árbol (`i5_descarga_l3.py` `06fd6760…`, `i5_oxa_io.py` `9a96fecb…`, tests `d110ead2…`, resto sin cambios) |
| focales `test_i5_descarga_l3.py` + `test_i5_acceso.py` | **31 passed** (1,6 s, basetemp nuevo) |
| `--plan` sin red contra el inventario real | 149 celdas, 298 recorridos, hashes del inventario `625928f0…` y del manifiesto; `limit` 100, timeout 120, reserva 5 GiB, sin corte financiero ni de páginas |
| lectura del código | custodia de bytes originales en gzip con SHA-256 doble; recibo por página encadenado por hash con cursor entrante/saliente y todos los timestamps; validación de ámbito `[inicio, fin)`, símbolo, cronología y estructura ANTES de persistir; cursor literal del proveedor con rechazo de regresiones; QA por intervalo declarado y separaciones > 600 s como bandera; `--resume` que re-verifica cada página desde sus bytes y se para ante `.part` o recibos incompletos; cerrojo de escritor; salida vetada dentro de OneDrive; clave nunca persistida y cuerpo rechazado si la contiene; `get_raw` compartido conserva la interfaz de `get`. **Sin defectos de corrección.** |

## 2. El problema es de volumen y de tiempo, y sale de los recibos del censo y del contrato

Hechos, con su fuente:

- **Bytes por snapshot** (páginas `limit=1` del censo, 149 celdas): LIT mediana **68.816 B** (68.291–69.774: el libro de LIT
  siempre llena el tope de 250 órdenes por lado); DOGE mediana **21.140 B** (14.188–34.736).
- **A resolución tick las filas son snapshots completos**, no deltas: el contrato define una sola respuesta
  `ApiResponseL3OrderBookArray` de `L3OrderBookSnapshot` para cualquier `granularity`; los esquemas de deltas
  (`OrderbookDelta`, `L2OrderBookDiff`) pertenecen a rutas L2.
- **Checkpoint por día**: cadencia ≈ 2,9 min ⇒ ~440–500 snapshots/día (coherente con los 81.094 `total_records`
  de DOGE en 185 días = 438/día).
- **Tick por día**: sin medir con este contrato. Única cifra propia: la diligencia del 2026-07-06 (`LEDGER:1803`),
  «LIT ~550–800 cr/día, DOGE ~3.700 cr/día» a 1 crédito por 1.000 filas ⇒ **~0,55–0,8 millones de snapshots/día
  en LIT y ~3,7 millones en DOGE.** Es estimación documental, y es el número que hay que medir primero.
- **`limit` admite hasta 1.000** («effective values are clamped to 1–1000»); el instrumento pide 100.

Con eso, la pasada única «149 celdas × checkpoint + tick» pesa así (crudo transferido; el gzip de un libro L3 en
JSON puede dar 5–10×):

| tramo | snapshots | crudo | comprimido (5–10×) | páginas a `limit=100` |
|---|---|---|---|---|
| checkpoint, 149 celdas | ~70 k | **~3,3 GB** | ~0,3–0,7 GB | ~750 |
| tick LIT, 79 días | 43–63 M | **3,0–4,3 TB** | 300–870 GB | 430–630 k |
| tick DOGE, 70 días | ~260 M | **~5,5 TB** | 550 GB–1,1 TB | ~2,6 M |

Disco libre en `C:` hoy: **500 GB**, y es el disco del sistema. Tiempo: a `limit=100` y ~1 s por página son
**semanas** en serie; a `limit=1000` el cuello pasa a ser la transferencia (una página de LIT son ~69 MB), del
orden de **10 días continuos** para ~9 TB. Créditos: ~0,3 millones de 80 millones — irrelevantes, como dijo el
propietario; el cuello es disco y calendario, no dinero.

Y el orden actual agrava el fallo: DOGE va primero y el tick sigue al checkpoint dentro de cada celda, así que la
reserva de 5 GiB se alcanzaría con tick de DOGE antes de haber bajado un solo día de LIT, dejando el disco del
sistema al límite. **Por eso no ejecuto el comando del relevo.**

## 3. Propuesta: mismas 149 celdas, por etapas, y medir antes de comprometer el disco

**Etapa A — checkpoint de las 149 celdas, ahora.** Es lo que consumió la receta decisiva (páginas de
`l3orderbook/history` sin `granularity`, es decir checkpoint) y lo que necesita la reproducción de los ocho días.
Con `limit=1000` es **una página por recorrido: 298 páginas, ~3,3 GB crudos, minutos, ~300 créditos.**

**Etapa B — tick de UN día de reproducción de LIT (2026-03-06), con `limit=1000`,** para medir de verdad
snapshots/día, bytes/día, ratio de compresión y tiempo por día. Con ese recibo la mesa decide con números.

**Etapa C — alcance del tick, decidido con la medida:** los ocho días de reproducción de LIT caben casi seguro
(~8 × 4–6 GB comprimidos); los 79 de LIT y el tick de DOGE exigen almacenamiento externo (2–4 TB) o una
resolución intermedia (`1s`, `10s`, `30s`, que el contrato ofrece) para la extensión diagnóstica. No es recorte
por coste: es que no cabe, y decirlo antes vale más que descubrirlo con el disco lleno.

**Cambios que esto pide al instrumento** (Codex implementa, Code audita el diff, unas decenas de líneas):

1. Selector de alcance explícito y registrado en `plan.json`: `--resolutions checkpoint|tick|ambas` y
   `--cells` por símbolo o rango de índices, sin tocar el manifiesto ni el orden cronológico dentro del tramo.
2. `LIMIT` = 1.000, el máximo del contrato (`validate_page` ya rechaza páginas mayores).
3. Reserva de disco ≥ 50 GiB en el disco del sistema; los 5 GiB actuales dejan Windows sin margen.
4. Orden LIT antes que DOGE, y por resolución antes que por celda, para que lo prioritario entre primero.
5. Que el recibo de intento resuma bytes crudos y comprimidos por recorrido, para que la Etapa B sea la medida.

## 4. Riesgos que quedan aunque se haga por etapas

- La Etapa B puede revelar que un día tick de LIT no cabe en 120 s por página a 69 MB si el enlace es lento: el
  timeout es de transporte, no de duración; se leerá el recibo antes de seguir.
- Un tick de LIT de decenas de GB por día no es un problema de créditos sino de custodia: hay que decidir dónde
  vive antes de bajarlo, y fuera de OneDrive.
- `PAGE_NOT_CHRONOLOGICAL` usa `<` estricto y `same_timestamp_rows` cuenta iguales: correcto para tick, donde
  varios snapshots comparten milisegundo.

## 5. Dictamen

Instrumento **sin defectos de corrección**, con 31 focales y plan conformes. **No ejecutable como pasada única
en esta máquina**: por volumen (tick ≈ 8–9 TB crudos, del orden de 1 TB comprimido frente a 500 GB libres) y
por tiempo (semanas a `limit=100`). Recomiendo aprobar la Etapa A ya, la Etapa B como medida, y decidir la C con
el recibo de la B. Estados: **implementado** (Codex) · **verificado localmente** (31 focales, plan) · **auditado
independientemente** (esta lectura y esta aritmética) · **ejecutado: no**.
