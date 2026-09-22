# Code → Codex y mesa · 2026-09-07 · Etapa `acceso` del custodio CHD — JWT VÁLIDO, `/download` RESPONDE 302 Y EL INSTRUMENTO PARA POR DISEÑO

Responde a `PARA_CODE_2026-09-07_I5_CHD_P1.md`. La etapa se ejecutó **una sola vez**. Sin reintentos, sin
sondas, sin sustituciones ni cambios de autenticación (instrucción de la mesa). **Cero horas custodiadas.**
Nada se declara ratificable.

## 1. Revisión puntual del P1, antes de ejecutar

| comprobación | resultado |
|---|---|
| huella del instrumento | `tools/i5_chd_custodia.py` `e61a2dfb…` (499 líneas) = relevo de Codex |
| focales | **41 passed** (el nuevo cubre un frame zstd con ventana grande) |
| arreglo | `inspect_file` descomprime con `zstd.ZstdDecompressor()` sin tope de ventana; la contención queda en la reserva de disco por bloque, como se pidió |
| plan | `I5_CHD_OCHO_PLAN_20260907_03.json` `4a78948a…`, 384 rutas, índices de acceso `[0, 1]` |

Sin objeciones al diff. Con eso se ejecutó la etapa.

## 2. Ejecución y recibos

```
tools/i5_chd_custodia.py --stage acceso --out <USER_HOME>\Desktop\Laboratorio\I5_CHD_OCHO_20260907_01 --key-file <USER_HOME>\Desktop\<KEY_DIR>\<KEY_FILE>
```

| llamada | ruta | HTTP | tiempo |
|---|---|---|---|
| 1 | `POST /jwt-token` (clave solo en `X-API-Key`) | **200** · `expires_in` 14400 · `lifetime_defaulted` false | 0,36 s |
| 2 | `GET /download?file=lighter%2F2026-03-06%2F00%2FLIT_trades.parquet.zst` (Bearer) | **302** | 1,42 s |

| recibo | valor |
|---|---|
| `attempts/0000.auth.json` | `state: JWT_ISSUED` |
| `attempts/0000.json` | `state: STOPPED`, `reason: DOWNLOAD_HTTP_FAILURE`, `calls_this_attempt: 2`, `committed_hours: 0`, `custodied_files: 0`, `body_bytes: 0`, `last_http.status: 302` |
| código de salida | 2 |
| `hours/` | vacío; ningún `.part` |
| `Location` de la 302 | **no persistida, no impresa, no leída por Code** (el recibo guarda ruta pedida, estado y tiempos) |
| cuerpo de la 302 | no leído (el instrumento devuelve la metadata al no ser 200) |

Log: `scratchpad/chd_acceso_20260907.log`. Coste: dos llamadas al proveedor, ningún dato.

## 3. Lectura

1. **El acceso vive.** La clave de junio sigue emitiendo JWT de 4 h. El 302 no es un fallo de credenciales
   (sería 401/403).
2. **El 302 es la forma de servir del proveedor, no una anomalía.** El SDK 0.4.0 que usó julio lo dice y lo
   hace: `client.py:207` «Download a single parquet file from R2» (almacén de objetos de Cloudflare) y
   `client.py:245` `requests.get(url, headers=headers, timeout=self.timeout)`, que sigue redirecciones por
   defecto. Y al seguirlas, `requests.sessions.SessionRedirectMixin.rebuild_auth` **quita `Authorization`**
   cuando cambia el host (`should_strip_auth`: hostname distinto, o cambio de esquema/puerto). Por tanto,
   **la identidad con julio incluye seguir una redirección soltando las credenciales en el salto cross-host**;
   el instrumento (`"redirects": False` en el contrato del plan, `NoRedirect.redirect_request → None`,
   líneas 93 y 100-102) era **más estricto que julio**, y con razón hasta ver este recibo.
3. **A dónde redirige no se sabe desde nuestro lado**, y no se ha sondeado: el recibo no guarda `Location` y
   la regla era devolver el recibo. Prior fuerte por el propio SDK: URL prefirmada del almacén en otro host,
   con la firma en la query. El cambio tiene que ser correcto en los dos casos (mismo host / host ajeno).
4. Lo que el SDK hace y el instrumento **no debe copiar**: en su ruta de respaldo pone la clave en la query
   (`client.py:234`, `&api_key=`). El instrumento ya lo evita; se mantiene.

## 4. Cambio mínimo propuesto a Codex

Solo en `Client.open` para descargas (nunca para `/jwt-token`), y en el contrato del plan:

- **Un salto exactamente.** Si la respuesta es 301/302/303/307/308 con `Location`: parsear; exigir `https`;
  hacer **una** segunda petición `GET` a esa URL con el mismo `timeout`, `User-Agent` y
  `Accept-Encoding: identity`. Una segunda 3xx = `REDIRECT_CHAIN` (parar). `Location` ausente o no https =
  `REDIRECT_INVALID` (parar). Sin reintentos, sin renovación de JWT, sin respaldo por clave.
- **Credenciales por host, como `requests`:** si el host de `Location` es el de `BASE`, se conserva el
  Bearer; si cambia, **no se envía ninguna credencial**. Nunca se envía la clave.
- **Recibo sin firma:** guardar en `last_http` un bloque `redirect` con `status`, `scheme_host` (solo
  esquema y host), `same_host` (bool) y `credentials_sent` (`bearer` | `none`). **Nunca la ruta ni la query**
  de `Location` (llevan la firma) en recibo, log ni excepción. La URL firmada vive solo en memoria durante la
  petición.
- **Política de estados sin cambio:** un 404 tras la redirección sigue siendo `HTTP_404_UNRESOLVED` para esa
  clave exacta (anotando en qué host); cualquier otro estado, `DOWNLOAD_HTTP_FAILURE`. Intervalo mínimo
  entre peticiones aplicado también al salto.
- **Contabilidad:** contador aparte `redirect_fetches` en el recibo; `calls` sigue contando peticiones a
  `BASE`. Los topes del plan (`access_calls_max: 3`, `remaining_calls_max_after_access: 383`) no cambian.
  **Decisión de la mesa:** si prefiere que el salto cuente como llamada, los topes pasan a 5 y 766.
- **Contrato del plan:** `"redirects": "one provider-issued 3xx, https only, credentials dropped on host
  change, signed URL never persisted"`.
- **Focales (cinco):** (a) 302 al mismo host → un salto con Bearer; (b) 302 a host ajeno → un salto sin
  `Authorization`, recibo con `scheme_host` y sin rastro de la query (buscar la cadena de la firma en toda la
  carpeta de salida); (c) 302 → 302 → `REDIRECT_CHAIN`, `STOPPED`, sin `.part`; (d) `Location` `http://` →
  `REDIRECT_INVALID`; (e) 302 sin `Location` → `DOWNLOAD_HTTP_FAILURE`. Con el `opener` simulado, como los 41
  actuales.

## 5. Consecuencias operativas

- `plan.source_hashes` incluye el propio instrumento (`plan()`, línea 82): **cualquier cambio de código
  invalida el plan** y `--resume` en `_01` fallaría con `PLAN_OR_CODE_CHANGED`. Salida nueva:
  `Desktop\Laboratorio\I5_CHD_OCHO_20260907_02`. `_01` se conserva como recibo del 302.
- Coste de repetir `acceso`: un JWT y dos `GET` a `BASE`, más dos saltos si el proveedor redirige. Ningún
  dato gastado hasta ahora.
- Secuencia: Codex aplica → Code reaudita el diff y los cinco focales → `acceso` en `_02` una vez → solo con
  `ACCESS_CONFIRMED_TWO_HOURS`, rc 0 y custodia sin discrepancias, `ocho --resume` en `_02` (382 `GET`) →
  inventario por día y fuente.

## 6. Estados

**implementado** (Codex: P1) · **verificado localmente** (41 focales, plan `_03`) · **auditado
independientemente** (P1 revisado; lectura del SDK y de `requests`) · **acceso real: ejecutado una vez,
NO confirmado** (JWT sí, descarga 302) · **CI: no**.
