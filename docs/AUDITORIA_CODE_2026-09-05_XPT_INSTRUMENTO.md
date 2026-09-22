# Code → Codex y mesa · 2026-09-05 · Auditoría del instrumento `xpt_enlace_20260905.py` — SIN DEFECTOS QUE CORREGIR

Responde al relevo «comprobación acotada de IDs en archivo propio XPT». Solo lectura y focales sintéticos:
**ninguna conexión al VPS, ningún cuerpo leído, ningún endpoint de mercado, cero créditos.** Nada se declara
ratificable; un recibo «completo» de este instrumento es un estado de procesamiento, no ciencia.

## 1. Identidad de lo auditado

| fichero (Laboratorio) | SHA-256 | coincide con el relevo |
|---|---|---|
| `xpt_enlace_20260905.py` (546 líneas) | `f82f1f53…de1f7` | sí |
| `test_xpt_enlace_20260905.py` (219 líneas) | `020ceb47…b77a1` | sí |
| `XPT_ENLACE_20260905_PREFLIGHT_01/preflight.json` | `c3593a02…b7637` | sí |

Focales: **11 passed** también aquí (0,12 s, basetemp nuevo `Laboratorio/tmp_xpt_audit_code_01`); `py_compile` ok.

## 2. Contratos contrastados en fuente (lo que los fixtures sintéticos dan por supuesto)

| supuesto del instrumento | fuente que lo confirma |
|---|---|
| Línea del colector = `{"recv_ns": <ns>, "frame": "<JSON del frame como STRING>"}` | `infra/lighter_collector/collector.py:115-116` (`msg` es `str`; se envuelve sin parsear) |
| Línea del poller = `{"recv_ns", "sym", "market_id", "resp": <JSON completo de orderBookOrders>}` | `infra/l3_poller/l3_poller.py:192` |
| `resp` trae `code`, `message`, `total_asks`, `asks`, `total_bids`, `bids`; cada orden `order_index` (int64), `order_id` (string), `owner_account_index`, `transaction_time`; `limit` máximo 250 | OpenAPI REST de Lighter, `orderBookOrders`; `LIMITE = 250` en el poller (`:49`) |
| Canal de trades en respuestas = `trade:{market_id}`; mensaje con `channel`, `type` (`update/trade`), `trades`, `liquidation_trades`; trade con `trade_id`/`_str`, `ask_id`/`_str`, `bid_id`/`_str`, `ask_account_id`, `bid_account_id`, `is_maker_ask`, `type` ∈ {trade, liquidation, deleverage, market-settlement}, `timestamp`, `transaction_time`; sin snapshot al suscribir | referencia WS pública de Lighter |
| XPT está suscrito por el colector y consultado por el poller | `collector.py:29`, `l3_poller.py:47` |
| Los ficheros `_12` contienen todo lo recibido en [12:00, 12:10): la hora del nombre se toma al ESCRIBIR, que es ≥ la de recepción | `collector.py:66-67` (hora en el flush), `l3_poller.py:121` (hora en `escribir`) |
| Conexión: `root@<VPS_IP>`, clave `~/.ssh/<SSH_KEY>`, host ya en `known_hosts` | `docs/CONTINUAR_AQUI.md:119,166`; listado local de `~/.ssh` |

## 3. Semántica del §3 del relevo, comprobada línea a línea

- Ventana semiabierta `[START, END)` por `recv_ns` en las DOS fuentes (`receive()`); unidad exigida ns; fuera de ventana se descarta sin contar como ampliación.
- Enrutamiento ANTES del payload: `sym == "XPT"` antes de mirar `resp`; `channel == "trade:<id>"` antes de recepción y trades; `market_id` del evento antes de ids, cuenta o tiempos. El mapeo sale solo de envoltorios XPT en la ventana; `AMBIGUOUS_XPT_MARKET` / `NO_XPT_MAPPING_IN_FIXED_WINDOW` paran.
- Enteros exactos (`exact_id`: rechaza bool, float, negativos, > 2⁶⁴; strings decimales ≤ 20); alias `_str` comparados y contados si discrepan; nunca float.
- Maker: `ask_id` + `ask_account_id` si `is_maker_ask`, `bid_id` + `bid_account_id` si no; solo `type == "trade"` dentro de `trades` se enlaza; liquidaciones y demás, contadas aparte.
- Deduplicación por `trade_id`; primera recepción DENTRO de la ventana; firmas discrepantes → `conflicting_trade_ids`, que se quedan en el denominador y fuera del enlace.
- Contadores separados: clave vista en cualquier punto; con cuenta; con lado; conjunta; previa por recepción del host; previa por reloj del evento (sin calibrar, con el límite escrito); tiempo del evento desconocido o fuera de ventana. **Ningún desenlace posterior interviene en la admisión.**
- Unidades por rango (`clock_value`): candidatos s/ms/µs/ns separados por 1000×, ventana ±1 día ⇒ inferencia única por construcción; ceros → `missing_zero_or_invalid`; solo conteos y mín/máx crudos.
- Cadencia y bordes declarados; `== 250` y `total_* > devueltas` contados sin semántica de iceberg.
- **No se accede a precio, tamaño, referencia, posición, fee, PnL ni markout:** esos campos no se leen en ningún sitio, y el focal comprueba que sus marcadores no aparecen en el recibo.

## 4. Transporte y solo-lectura

- `ssh -T` con `BatchMode=yes`, `StrictHostKeyChecking=yes`, `UpdateHostKeys=no`, `IdentitiesOnly=yes`, `ConnectTimeout=8`, `ConnectionAttempts=1`; comando remoto fijo `python3 -B -`; el guion viaja por stdin y lo consume entero el intérprete: no hay shell exterior leyendo ese stdin (E-19 no aplica).
- Remoto: `O_RDONLY|O_NOFOLLOW|O_NOATIME`, `fstat` antes y después contra los cinco campos del preflight (`size`, `mtime_ns`, `ctime_ns`, `device`, `inode`), lectura por bloques, `signal.alarm(55)`, escribe solo a stdout. En `EXPECTED` solo se interpolan constantes y enteros validados.
- Local: cabecera `XPTARCHIVE1`, cuerpo de tamaño exacto, pie con el `fstat` posterior, rechazo de bytes sobrantes; SHA-256 de cada cuerpo al recibo. Descompresión de frames concatenados con `eof`/`unused_data`, frame o línea incompletos → parada; guardas 1 GiB / 4 MiB.
- Watchdog local: 60 s totales, mata el cliente SSH, escribe recibo `INDETERMINADO/LIMIT_60S` sin `counts`, `os._exit(4)`; el texto de excepciones nunca se persiste. `--out` exige directorio nuevo. rc 0 solo con `COUNTS_COMPLETE_PENDING_AUDIT`.

## 5. Hallazgos — ninguno bloqueante

**P1, a declarar, sin cambio de código:**

1. **Parada por línea ajena.** Cualquier línea de cualquier canal que no sea un objeto JSON o tenga una clave duplicada (también anidada) aborta el diagnóstico entero con `INVALID_JSON_ENVELOPE` / `DUPLICATE_JSON_KEY` / `JSONDecodeError`, sin poder decir de qué canal. Es fail-closed a propósito; una parada así no es evidencia sobre XPT.
2. **Razón remota perdida.** Si el remoto para por `SOURCE_CHANGED_*` o `SOURCE_SHORT_READ`, el recibo solo dice `SSH_OR_REMOTE_READ_FAILED` y el hash de stderr. Mejora opcional y sin riesgo de payload: casar esas cadenas constantes en stderr.
3. **Presupuesto, MEDIDO en vez de supuesto.** Camino caliente (doble parseo con hook de claves duplicadas) sobre 180 MiB de frames L2 sintéticos: **57 MiB/s** (96 sin hook) ⇒ 250–350 MiB descomprimidos son 4–6 s. Los 60 s los domina la transferencia SSH de 25,3 MiB: por debajo de ~0,7 MB/s de enlace la corrida acaba `LIMIT_60S` sin reintento. No es defecto; es el modo de fallo previsible.

**P2:** la pertenencia a ventana y las comparaciones «previa por reloj del evento» usan la cota SUPERIOR del intervalo de representación (`timestamp[1]`), no la inferior: un evento en `END − 1 ms` cuenta como fuera. Desviación de un tick de unidad, consistente y declarada como no calibrada.

## 6. Dictamen

Puede ejecutarse **una vez**, tal cual, con el comando del relevo. Estados: **implementado** (Codex) ·
**verificado localmente** (11 focales aquí; coste del camino caliente medido) · **auditado
independientemente** (esta lectura) · **con datos reales: no**. Tras la corrida, el recibo se lee ANTES de
interpretar nada, y una parada por P1.1 o LIMIT_60S no se convierte en «no hay enlace».

## 7. Corrección fechada — 2026-09-06, tras la corrida y la revisión de la mesa

El texto de arriba se conserva. Dos precisiones de la mesa, comprobadas y concedidas:

1. **El P2 estaba mal.** `clock_value` devuelve `(unidad, inferior, superior)`: `timestamp[1]` es la cota
   INFERIOR (`n*scale`), no la superior. La pertenencia a ventana y las comparaciones «previa por reloj del
   evento» usan la cota inferior; no hay el sesgo de un tick que describí. Error de lectura mío.
2. **«Los ficheros `_12` contienen todo lo recibido en [12:00, 12:10)» era demasiado fuerte.** El argumento
   de la hora del nombre solo prueba que un registro no puede caer en un fichero de hora ANTERIOR a su
   recepción; no prueba ausencia de pérdidas ni de interrupciones de captura. Lo que certifica la corrida es
   el procesamiento íntegro de los dos ficheros, no la cobertura del mercado.

**Lo que la corrida enseñó sobre el instrumento (no defecto de lo autorizado, sí hueco a cerrar antes de
otra muestra):** con cero frames de trades admitidos, el recibo no puede distinguir «XPT no negoció en esos
diez minutos» de «el colector no entregó el canal de XPT en esos diez minutos», porque el instrumento no
cuenta nada de los canales que no enruta. Un contador de vitalidad por nombre de canal, sin leer su carga
(p. ej. cuántos frames `order_book:147` hubo en la ventana), daría ese denominador a coste cero.
