# Code → Codex y mesa · 2026-09-07 · Custodia horaria CHD de los ocho días: 381 de 384 ficheros, tres 404 sin resolver en LIT/lighter 2026-06-29

Responde a `PARA_CODE_2026-09-07_I5_CHD_REDIRECT.md`. Revisión del diff, etapa `acceso` y continuación `ocho`
ejecutadas **una vez cada una**, en `Desktop\Laboratorio\I5_CHD_OCHO_20260907_02`. Sin reintentos, sin sondas,
sin tocar `_01`. Ningún parquet abierto por Code fuera de la QA del instrumento; ningún precio mirado. Nada se
declara ratificable.

## 1. Revisión del diff (antes de ejecutar)

| comprobación | resultado |
|---|---|
| huellas | `i5_chd_custodia.py` `d39234b2…`, `test_i5_chd_custodia.py` `c181227a…`, `test_i5_chd_redirect.py` `0ae70fb4…`, `patch.diff` `f154485e…`, `receipt.json` `54027cab…`, plan `_04` `85ad3b71…`: todas = relevo |
| `_01` intacta | `attempts/0000.json` `11bbd643…` = relevo; mtimes 09:38 sin cambios |
| focales | **22 passed** (`test_i5_chd_redirect.py`, 1,8 s) y **41 passed** (suite completa anterior, 4,9 s), basetemps nuevos; objetos git 667 antes y después |
| plan sin red | 384 recorridos, huella `85ad3b71…` = `_04`; topes `access_http_requests_max` 5 y `remaining_http_requests_max_after_access` 765 |
| lectura del código | `NoRedirect` sigue desactivando el automático; un solo `GET` explícito tras 301/302/303/307/308 y solo para `/download`; `Location` absoluta HTTPS con host DNS/IPv4, sin usuario, fragmento, controles ni barras inversas; rechazo si contiene clave o JWT aunque vayan codificados; Bearer solo con mismo esquema, host y puerto efectivo; segunda 3xx = `REDIRECT_CHAIN`; URL firmada solo en memoria y añadida al escaneo de secretos del cuerpo; recibo con `scheme_host`, puerto, `same_host`, `same_origin`, `credentials_sent`; contadores `calls` / `redirect_fetches` / `http_requests`; secretos reiniciados por descarga (clave, JWT) para que la lista no crezca con los 382 |

**Sin defectos de corrección.** Dos notas para la mesa, sin cambio obligatorio:

- **P2, decisión ya tomada por la mesa:** una `Location` relativa para como `REDIRECT_INVALID`. Habría sido una
  ronda más; no ocurrió, el proveedor redirige con URL absoluta.
- **P3:** todo valor de query de 16 o más caracteres entra en la lista de secretos (p. ej. una fecha
  `X-Amz-Date`). Si un cuerpo lo contuviera por casualidad, el fichero pararía como `SECRET_IN_RESPONSE`: falla
  cerrado y con recibo. No ocurrió en 381 cuerpos.

## 2. Ejecución

| etapa | UTC | estado | rc | llamadas API | saltos | HTTP | tope HTTP |
|---|---|---|---|---|---|---|---|
| `acceso` | 08:03:24 → 08:03:29 | `ACCESS_CONFIRMED_TWO_HOURS` | 0 | 3 (JWT + 2) | 2 | 5 | 5 |
| `ocho --resume` | 08:04:22 → 08:20:05 | `CUSTODY_COMPLETE_REQUIRES_REVIEW` | 2 | 383 (JWT + 382) | 379 | 762 | 765 |
| total | | | | 386 | 381 | **767** | 770 |

Los tres saltos que faltan hasta 765 son los tres 404: la API los devolvió directamente, sin redirección. El rc 2
es el diseñado para «completa con revisión»: hay 404 y un fichero de borde. Pre-vuelo: OneDrive parado, 500 GB
libres, clave de 64 B, carpeta `_02` inexistente. Recibos: `attempts/0000.json` `d91751e2…`,
`attempts/0001.json` `c7f633cf…`. Logs en el scratchpad de Code (`chd_acceso_02_20260907.log`,
`chd_ocho_02_20260907.log`).

**Destino de la redirección, ahora sí conocido:** las 381 descargas redirigieron a
`https://<VENDOR_BUCKET>.r2.cloudflarestorage.com` (Cloudflare R2, host ajeno) y en todas
`credentials_sent = none`. Ninguna cadena `X-Amz`, `Signature`, `Credential` ni ruta del almacén aparece en
ningún fichero de la carpeta. Cero `.part`.

## 3. Verificación de la custodia (Code, por programa, sin abrir parquet)

Script `inventario_chd_ocho.py` (scratchpad); resumen `Desktop\Laboratorio\I5_CHD_OCHO_20260907_02_RESUMEN_CODE.json`
`6c39efc7…`, fuera de la carpeta custodiada.

| comprobación | resultado |
|---|---|
| recibos | 384 de 384 índices del plan; cadena `previous_receipt_sha256` íntegra (0 roturas) |
| crudos | 381 ficheros, sha256 de cada uno = `body_sha256` de su recibo; 381 de 381 |
| vacíos / 0 filas | 0 / 0 |
| unidades | `event_time` ms y `received_time` ns en los 381; `historical_event_ms` verdadero en todos |
| inversiones de `event_time` | 0 |
| `Content-Encoding` | `identity` en todos; cuerpo = parquet comprimido zstd (`ZSTD_PARQUET`), un row group por fichero |
| esquema (idéntico en los 381) | `event_time` int64, `trade_time` int64, `received_time` int64, `trade_id` int64, `price` string, `quantity` string, `is_buyer_maker` bool, `order_type` string, `symbol` string |
| tamaño | 34.989.153 bytes de cuerpo; 36 MB en disco con recibos |

## 4. Inventario por día y fuente

| día | LIT/lighter horas | filas | primer / último trade UTC | LITUSDT/binance_futures horas | filas | primer / último trade UTC | filas fuera de su hora (ev.) |
|---|---|---|---|---|---|---|---|
| 03-06 | 24/24 | 56.925 | 00:00:04,4 / 23:59:58,9 | 24/24 | 146.667 | 00:00:00,8 / 23:59:51,2 | 4 |
| 03-27 | 24/24 | 31.035 | 00:00:40,3 / 23:54:46,0 | 24/24 | 123.292 | 00:00:02,9 / 23:59:57,6 | 0 |
| 04-08 | 24/24 | 22.210 | 00:00:00,7 / 23:58:41,2 | 24/24 | 411.381 | **04-07 23:59:59,96** / 23:59:58,6 | 35 (8 del día anterior) |
| 04-19 | 24/24 | 35.372 | 00:00:01,3 / 23:59:58,9 | 24/24 | 328.123 | 00:00:01,2 / 23:59:59,8 | 1 |
| 05-02 | 24/24 | 19.061 | 00:00:06,2 / 23:59:58,1 | 24/24 | 138.379 | 00:00:02,3 / 23:59:59,1 | 2 |
| 05-14 | 24/24 | 15.918 | 00:00:01,0 / 23:59:51,3 | 24/24 | 121.985 | 00:00:00,4 / 23:59:58,9 | 0 |
| 06-11 | 24/24 | 53.959 | 00:00:00,1 / 23:59:58,7 | 24/24 | 721.554 | 00:00:00,1 / 23:59:56,1 | 13 |
| 06-29 | **21/24** | 55.243 | 00:00:00,2 / 23:59:58,4 | 24/24 | 506.525 | 00:00:00,6 / 23:59:59,4 | 3 |
| total | 189/192 | 289.723 | | 192/192 | 2.497.906 | | 66 (4 en lighter) |

Filas totales: **2.787.629**.

### 4.1 Los tres 404

`lighter/2026-06-29/{04,05,06}/LIT_trades.parquet.zst`: HTTP 404 de la API, sin redirección, recibos
`hours/0344.json`, `0346.json`, `0348.json`, estado `HTTP_404_UNRESOLVED`. Tres horas consecutivas, 04:00–07:00
UTC, en un día de reproducción. Por contrato del instrumento es **clave exacta sin resolver, no ausencia de
mercado**: las horas 03 y 07 del mismo día están custodiadas con filas, y el censo L3 de 0xArchive no declaró
ningún hueco para LIT el 06-29. Es un hueco del archivo de CryptoHFTData o de su captura; no se ha reintentado ni
sondeado, por regla.

### 4.2 Partición horaria por reloj de recepción

66 filas tienen `event_time` fuera de la hora de su fichero (62 en Binance, 4 en Lighter): trades con
`event_time` 16:59:59,9 recibidos a las 17:00:00,0 van al fichero de las 17. El instrumento las cuenta y no las
filtra. El único fichero con `boundary_review_required` es `LITUSDT 04-08 h00` (`hours/0097.json`): 8 filas
con `event_time` del 04-07 23:59:59,96. Simétricamente, los últimos trades de cada día pueden estar en la hora
00 del día siguiente, que no está en el plan.

## 5. Identidad con julio, dos hechos del SDK 0.4.0

1. `client.py:385`: julio pedía **los mismos 24 ficheros por día** (`range(24)`, día a día): el borde de
   recepción es idéntico al nuestro.
2. `client.py:419-421`: en julio, una hora que fallaba (404 → `None`; cualquier otra excepción → aviso)
   **se saltaba en silencio** y el día se ensamblaba con las horas que llegaron. Nuestra custodia para y anota. Por
   tanto, si el NPZ original del 06-29 se calculó con 21 horas de Lighter, el contraste de reproducción lo
   dirá por el conteo de trades; si se calculó con 24, el proveedor ha perdido esas tres horas desde julio.

## 6. Lo que sigue y una decisión de la mesa

- **Productor forense (Codex)** sobre `_02` y la custodia L3 de A, según el relevo `PARA_CODE_2026-09-07_I5_PRODUCTOR_INSUMOS.md`.
- **Decisión de la mesa sobre 06-29:** recomiendo **no** volver a consultar las tres horas ahora, reproducir el
  día con la marca «21/24 lighter» y contrastar contra el NPZ original primero (§5.2). Una nueva consulta, si se
  quiere, sería un intento nuevo con recibo fechado, no un reintento dentro de este.
- Los saltos con `credentials_sent = none` a un host ajeno y la ausencia de material firmado en disco quedan
  acreditados en los 381 recibos; el contrato de transporte no necesita más cambios.

## 7. Estados

**implementado** (Codex: salto único) · **verificado localmente** (63 focales; plan; recibos y crudos
re-verificados por programa) · **auditado independientemente** (diff, esta lectura) · **ejecutado una vez**
(`acceso` + `ocho`) · **CI: no** · **reproducción de los ocho NPZ: pendiente**. STOP, freezes y pins vigentes.
HEAD `7df5280`, sin commit.
