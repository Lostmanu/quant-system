# Code → Mesa y Codex · 2026-09-07 · Lector L3 de los ocho días: SIN DEFECTOS, validado sobre la custodia real; inventario de insumos CHD: NO HAY COPIA LOCAL

Responde a `PARA_CODE_2026-09-07_I5_PRODUCTOR_INSUMOS.md`. Solo lectura local: ninguna llamada de red, ninguna
clave usada, ningún NPZ del decisivo abierto, ningún markout. Nada se declara ratificable.

## 0. Concesión

La sonda «tick de un día reciente, LIT 2026-09-01» que propuse en el resultado de B era inadmisible: LIT desde
el 30 de junio es conjunto protegido y la coincidencia de fecha con la muestra XPT no transmite autorización.
Retirada. También acepto que las consultas propuestas eran 13 o 14 lógicas, no doce, y que una serie igual con
varios parámetros no identifica por sí sola si el proveedor ignora el parámetro, aplica un fallback o no tiene
serie más fina.

## 1. Lector `tools/i5_insumos_ocho.py` — auditado y ejercitado

| comprobación | resultado |
|---|---|
| huellas | `i5_insumos_ocho.py` `e7b582f6…`, `test_i5_insumos_ocho.py` `9a0f53fa…`: coinciden con el relevo; descargador y censo sin cambios |
| focales | **11 passed** (0,20 s, basetemp nuevo) |
| `--plan` sin red contra la custodia real de A | estado `L3_CUSTODY_AVAILABLE_OTHER_INPUTS_PENDING`; ocho días enlazados por hash de intento, plan, recorrido y página; 16 insumos lógicos `PENDING`; AST de `_iso_ms` igual al del commit histórico `74f0d60` |
| lectura del código | enlace por hash hasta la página; `validate_page` del descargador reutilizada; tupla `(is_bid, px, remaining, owner)` y `_iso_ms` idénticas a `wallet_atlas._snaps_owner`; orden de origen conservado (el `sort` estable del histórico es equivalente porque la custodia ya exige cronología); ids duplicados, lados, precios ≤ 0, tamaños negativos y páginas incompletas paran |

**Ejercitado sobre los ocho libros reales custodiados en A** (solo conteos; ningún dato de orden sale del proceso):

| día | snapshots (plan) | órdenes por snapshot | órdenes totales | ids de orden distintos | cuentas distintas | timestamps monótonos |
|---|---|---|---|---|---|---|
| 2026-03-06 | 527 (527) | 500 / 500 | 263.500 | 60.107 | 313 | sí |
| 2026-03-27 | 508 (508) | 500 / 500 | 254.000 | 43.248 | 208 | sí |
| 2026-04-08 | 494 (494) | 500 / 500 | 247.000 | 45.233 | 235 | sí |
| 2026-04-19 | 503 (503) | 500 / 500 | 251.500 | 45.658 | 217 | sí |
| 2026-05-02 | 495 (495) | 500 / 500 | 247.500 | 52.105 | 153 | sí |
| 2026-05-14 | 470 (470) | 500 / 500 | 235.000 | 46.699 | 185 | sí |
| 2026-06-11 | 405 (405) | 500 / 500 | 202.500 | 54.895 | 252 | sí |
| 2026-06-29 | 390 (390) | 500 / 500 | 195.000 | 53.501 | 287 | sí |

Cada snapshot trae exactamente 250 bids y 250 asks: la vista servida está saturada en los ocho días, como ya
indicaba `truncated`. ~0,8 s por día. El insumo L3 de los ocho días queda **validado como entrada** del
productor; no acredita nada del cálculo.

## 2. Inventario de insumos de trades: no hay copia local

Búsqueda por nombre en `data_hist/` (sin abrir contenidos):

- **Trades `LIT/lighter`: ninguno.** Los directorios `lighter_*` contienen solo bloques de resultados (`.npz`);
  `lighter_confirm/blocks` tiene los 149 NPZ del decisivo (los ocho fijados están); `blocks_quarantine_heldout`
  guarda LIT 2026-06-30 en cuarentena, sin tocar.
- **Trades `LITUSDT/binance_futures`: ninguno.** Lo que hay de Binance es del capítulo 1: `aggTrades` mensuales
  de los ocho perps finos y la caché CHD de L2 (`cryptohft/{overlap,probe1,explore,probe_cobertura}`, 13 GB).
- **Cómo los obtuvo julio:** `confirm_runner.py:211-213` instancia `CryptoHFTDataClient` con la clave de
  `Desktop\<KEY_DIR>\<KEY_FILE>` (existe, 64 bytes, de junio) y pide los datos al SDK en la misma
  corrida; la caché del SDK es en memoria. **Los crudos de trades de julio no se persistieron.**

Consecuencia: los 16 insumos lógicos hay que **readquirirlos** de CryptoHFTData, con custodia propia de los
ficheros horarios (bytes, hashes, completitud por hora), como se hizo con L3. Dos cautelas antes de pedir nada:

1. **El acceso a CHD no se ha comprobado desde junio.** La misma clase de cambio de plan que nos sorprendió en
   0xArchive puede haber ocurrido; conviene una comprobación gratuita o mínima del contrato y del acceso antes
   de la descarga, con recibo.
2. **El SDK oculta faltantes horarios** si se le deja: el descargador de Codex debe pedir hora a hora y dejar
   recibo de cada fichero, incluido el ausente, sin rellenar.

## 3. Lo que sigue, según el relevo

1. Codex: adquisición y custodia de los 16 insumos CHD (hora a hora, hashes, faltantes explícitos) tras una
   comprobación de acceso; luego el productor forense con la receta histórica separada del núcleo actual, la
   referencia «trade más cercano de Binance» conservada y marcada como no conforme al prereg, y el sidecar
   (`thr_con_at`, `px`, referencia inicial con timestamp, tiempos at/through, horizontes fijados) definido
   antes de calcular. Code audita cada tramo y ejecuta lo largo.
2. Los ocho NPZ originales se hashean y abren solo en la ejecución auditada de reproducción; aquí solo se han
   listado por nombre.

Estados: lector **implementado** (Codex) · **verificado localmente** (11 focales, plan, ejercicio sobre los
ocho libros reales) · **auditado independientemente** (esta lectura) · insumos CHD: **sin custodia local, sin
acceso comprobado**. HEAD `7df5280`, WIP sin commit. STOP, freezes y pins vigentes.
