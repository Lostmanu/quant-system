# Code → Mesa · 2026-09-05 · Auditoría documental: enlace ejecución–orden y persistencia previa

Encargo del `DICTAMEN_MESA_2026-09-05_OBSERVABILIDAD_FPRIMA.md` §4: antes de implementar el contraste de
F′ (deriva posterior, lenta frente a reciente, dentro de cada lado), acreditar **cómo se enlaza una
ejecución con una orden concreta** y **cómo se acredita la persistencia previa**, distinguiendo lo que
dice el código de lo que confirma el contrato del feed. Método: lectura del código del repo en HEAD
`7df5280` y de la documentación pública de Lighter y 0xArchive (URLs abajo). **Sin datos, sin llamadas
autenticadas, sin gasto, sin cambios de código.** Nada se declara ratificable.

## 0. Resultado en cuatro frases

1. **El enlace ejecución→orden EXISTE en el feed del venue y en los trades canónicos de 0xArchive; NO
   existe en la fuente de trades que consume hoy el eco (CHD).** El differ actual no enlaza: imputa por
   precio, intervalo y decremento de tamaño (`confirm_runner._differ_core`).
2. **Queda UNA identidad sin acreditar por contrato:** que `ask_id`/`bid_id` del trade (y el `order_id`
   de 0xArchive) sean el mismo identificador que `order_index` del libro por órdenes. Ningún documento
   leído lo afirma ni lo niega. Se acredita con una comprobación empírica de conteo sobre un símbolo NO
   protegido; requiere autorización.
3. **La persistencia previa solo es observacional por seguimiento de `order_index` entre snapshots**, con
   resolución igual a la cadencia (≈2,9 min en los checkpoints de 0xArchive que usa el eco). No hay
   tiempo de creación utilizable en ninguna fuente.
4. **Las iceberg no están en la documentación pública de Lighter:** ni la semántica de `remaining_size`
   (visible o total) ni la identidad tras reposición. No se puede cerrar leyendo.

## 1. Enlace ejecución→orden: qué campo lo resuelve en cada fuente

| fuente | identificador de orden en el TRADE | identificador en el LIBRO | lo confirma | quién lo consume hoy |
|---|---|---|---|---|
| Lighter REST `GET /api/v1/trades` | `ask_id`, `bid_id` (int64, «Order identifier for the asking/bidding side»), `ask_account_id`, `bid_account_id`, `is_maker_ask`, `trade_id`, `size`, `price`, `timestamp`, `transaction_time`, `tx_hash`, `type` | — | [contrato](https://apidocs.lighter.xyz/reference/trades.md) | nadie |
| Lighter WS `trade/{market_id}` | mismo objeto; el ejemplo oficial trae `ask_id`, `bid_id`, `ask_account_id`, `bid_account_id`, `is_maker_ask` | `order_book/{id}` es L2 agregado `(price, size)` con `nonce/begin_nonce`: **sin ids** | [contrato WS](https://apidocs.lighter.xyz/docs/websocket-reference.md) | el colector propio guarda los frames ENTEROS (`collector.py:110-115`) desde 2026-07-05; el acta de despliegue verificó `ask/bid_account_id`, no los `*_id` (`COLECTOR_LIGHTER.md:54-56`) |
| Lighter REST `GET /api/v1/orderBookOrders` | — | `order_index` (int64), **`order_id` (string)**, `owner_account_index`, `initial_base_amount`, `remaining_base_amount`, `price`, `order_expiry`, `transaction_time`; ≤250 por lado | [contrato](https://apidocs.lighter.xyz/reference/orderbookorders.md) | `infra/l3_poller/l3_poller.py` (escrito y versionado el 2026-08-24; su despliegue NO consta en el repo: INVENTARIO fila 11) |
| 0xArchive `/v1/lighter/trades/{symbol}` (canónico, `source=bucket`) | **dos filas por fill, una por contraparte**, cada una con `account_index`, **`order_id` («Order ID of this account's order. Canonical rows only»)**, `is_maker`, `side`, `trade_id`, `tx_hash`, `timestamp` UTC; las filas `ws` preliminares NO traen `order_id` | — | [esquema](https://docs.0xarchive.io/schemas/operations/get-lighter-trades) | nadie |
| 0xArchive `/v1/lighter/l3orderbook/{symbol}/history` | — | por orden: `order_index`, `owner_account_index`, `price`, `remaining_size`, `original_size`, `side`; por snapshot: `timestamp` UTC, `truncated` («True when the stored checkpoint reached the 250-orders-per-side ingestion cap»), `ask_count`, `bid_count`; granularidad `checkpoint` (defecto), `30s`, `10s`, `1s`, `tick` | [esquema](https://docs.0xarchive.io/schemas/operations/get-lighter-l3-orderbook-history) | el eco y el atlas (`wallet_atlas._snaps_owner`: `oid=order_index`, `side`, `price`, `remaining_size`, `owner_account_index`) |
| CHD `lighter` trades | `event_time` (ms), `price`, `quantity`, `is_buyer_maker`, `order_type` — **sin id de orden ni de cuenta** | — | `lighter_adapter.lighter_trades_ms`; LEDGER:1237 (verificación 2026-06-20) | **el eco** (`eco_runner_lit.py:252-259`) y la confirmación decisiva |

**Lo que hace el código hoy** (`confirm_runner.py:82-135`, idéntico en `pilot_observer.diff_interval`):
para cada orden del snapshot `s`, busca prints del intervalo `(t0, t1]` con precio igual (tolerancia
1e-9) o que lo atraviesan; si la orden sigue en `s+1` con menos tamaño y hubo print a su precio →
`parcial` (t del primer at); si desaparece y hubo through → `through` (t del **primer through**; el at,
si lo hubo, solo queda como flag `thr_con_at`); si desaparece con at y sin through → `fill`; si
desaparece sin prints → `cancel`. **Ninguna rama consulta un identificador de la ejecución.** Varias
órdenes al mismo precio y lado se resuelven con los mismos prints. Confirma el hallazgo de la mesa sobre
I5: reclasificar `thr_con_at` no restituye el instante del at, que no se guarda.

**La identidad que falta.** El struct `Order` del WS de Lighter expone `OrderIndex` (`"i"`),
`ClientOrderIndex` (`"u"`) y `OwnerAccountId` (`"a"`), y `OrderExecution` referencia `MakerOrder` y
`TakerOrder` como `Order`
([data structures](https://apidocs.lighter.xyz/docs/data-structures-constants-and-errors.md)). Es
verosímil que `ask_id`/`bid_id` sean `OrderIndex`, pero `orderBookOrders` publica ADEMÁS un `order_id`
string distinto de `order_index`, y ningún texto leído fija la correspondencia. Tampoco 0xArchive dice si
su `order_id` (int64) es el `order_index` de su propio L3.

**Comprobación que la cerraría** (conteo, sign-blind, sin markout; requiere autorización de red y
gasto): sobre un símbolo FUERA del conjunto protegido (por ejemplo XPT o BRENTOIL, que el poller ya
lista), tomar N fills maker de los trades canónicos de 0xArchive y medir la fracción cuyo `order_id`
aparece como `order_index` en reposo, al mismo precio y lado, en el último snapshot L3 anterior al
`timestamp` del fill, y desaparece o decrece en el siguiente. Denominador explícito, snapshots
`truncated` excluidos y contados. Una fracción ≈1 acredita la identidad; una fracción baja la refuta o
delata un desfase de reloj que también hay que declarar. Coste: unas pocas páginas (mínimo 1 crédito
cada una); saldo y coste exacto se comprueban antes, como en la etapa 0.

**Unidades, para que no se repita la trampa ns/ms:** REST `trades.timestamp` está documentado en
segundos y el ejemplo del WS lo muestra en milisegundos (`1773854156654`); `transaction_time` en ns;
0xArchive sirve `timestamp` como texto ISO en trades y en L3; CHD sirve `event_time` en ms. Toda
frontera exige assert de rango, como ya hace `lighter_adapter`.

## 2. Persistencia previa: qué acredita el código y qué permite el contrato

- **Código.** `slow = oid in prev_seen`, y `prev_seen` acumula TODOS los `order_index` de todos los
  snapshots anteriores del día, también los que preceden a un intervalo inválido
  (`confirm_runner.py:95-105, 129`; `pilot_observer.observe_day` arranca con el conjunto vacío a
  propósito). «Lenta» significa **vista al menos una vez en un snapshot anterior del mismo día**: no es
  continuidad, no es edad, y depende de la cadencia. Con los checkpoints de 0xArchive (≈2,9 min medidos
  en julio) el mínimo de edad implícito es un intervalo; con `granularity=1s|tick` o con el poller (5 s)
  la resolución cambia y con ella la cohorte. La misma etiqueta no es comparable entre cadencias.
- **Contrato.** Ninguna fuente da tiempo de creación utilizable: `transaction_time` de
  `orderBookOrders` «viene 0 en vivo» (medido, `l3_poller.py:10-12`); el L3 de 0xArchive no publica campo
  de creación; `original_size` frente a `remaining_size` informa de ejecución o modificación acumulada,
  no de edad. **La persistencia solo puede definirse por primera aparición observada del `order_index`**,
  con la cadencia declarada, y por continuidad entre snapshots si se exige.
- **Truncamiento.** Con el tope de 250 órdenes por lado, una orden puede salir de la vista sin haberse
  ejecutado ni cancelado; hoy el differ la contaría como `cancel` (desaparece sin prints). 0xArchive
  marca el snapshot con `truncated`; el eco no lo lee. Un contrato de F′ debe condicionar a `truncated`
  y a la distancia al mejor precio, o excluir y contar.
- **Iceberg.** La página oficial de tipos de orden no las menciona
  ([order types](https://docs.lighter.xyz/trading/order-types-and-matching)); solo consta el anuncio del
  31-08. `remaining_base_amount`/`remaining_size` no tienen semántica publicada para el tramo oculto, y no
  se sabe si el `order_index` persiste al reponer el clip visible. **No se cierra leyendo**: hace falta
  declaración del proveedor o una prueba empírica pre-registrada (por ejemplo, volumen ejecutado por
  `trade_id` contra una orden superior a su `remaining_size` visible mientras su `order_index` sigue).
  Retiro mi proxy «trade mayor que nivel visible»: como dijo la mesa, no identifica.

## 3. Qué no persiste el esquema actual y qué necesita el estimando de F′

`_ESQUEMA_NPZ_LIT` guarda `mo, descartes, tipo, slow, is_bid, owner, vol20, t_fill, thr_con_at, amb` y
procedencia. **No guarda** `oid`, `px`, `qty`, referencia en el instante del fill, primera aparición ni
`truncated`. Para `B_e = 10^4·s·(R0 − p)/p` y `D_e(h)` hacen falta, por evento: `p` (precio de la orden),
`R0` (última referencia estrictamente anterior a `t_fill`, con tolerancia declarada; hoy
`realized_markouts` solo busca la referencia más cercana a `t_fill+Δ` dentro de ±max(Δ/2, 500 ms)),
`Rh`, `t_fill` exacto del trade enlazado, `oid`, `qty` ejecutada por `trade_id`, edad observada y el
estado de truncamiento. Nada de esto altera el decisivo ni sus bloques: sería un productor nuevo con
esquema propio.

## 4. Lo que se puede decidir ya y lo que no

- **Decidible por contrato:** cambiar la fuente de trades del estimando de F′ a una que lleve id de orden
  (0xArchive canónico o los frames WS del colector); leer `truncated`; definir la persistencia por
  primera aparición con cadencia explícita; guardar los campos del §3.
- **Decidible solo con una medición autorizada:** la identidad `ask_id/bid_id ≡ order_id ≡ order_index`
  (§1) y la representación de las iceberg (§2). Sin la primera, el enlace sigue siendo imputado y el
  contraste de fills queda **NO IDENTIFICABLE** con este instrumento, como fija el dictamen.
- **No decidible aquí:** horizonte, efecto mínimo, inferencia, potencia y ventana. Siguen abiertos en D4.2.
- **Estado del poller L3:** el código está en el repo; su despliegue y la cobertura de su archivo no
  constan (INVENTARIO fila 11, 2026-08-24). Si está corriendo, aporta 5 s de resolución y el campo
  `order_id` string junto a `order_index`, útil para la identidad del §1 sin gasto de proveedor.

## 5. Fuentes leídas hoy

Lighter: [trades](https://apidocs.lighter.xyz/reference/trades.md) ·
[orderBookOrders](https://apidocs.lighter.xyz/reference/orderbookorders.md) ·
[WebSocket](https://apidocs.lighter.xyz/docs/websocket-reference.md) ·
[data structures](https://apidocs.lighter.xyz/docs/data-structures-constants-and-errors.md) ·
[order types](https://docs.lighter.xyz/trading/order-types-and-matching).
0xArchive: [trades schema](https://docs.0xarchive.io/schemas/operations/get-lighter-trades) ·
[L3 history schema](https://docs.0xarchive.io/schemas/operations/get-lighter-l3-orderbook-history) ·
[Lighter REST](https://docs.0xarchive.io/rest-api/lighter.md).
Repo: `analysis/confirm_runner.py`, `analysis/pilot_observer.py`, `analysis/eco_runner_lit.py`,
`analysis/wallet_atlas.py`, `analysis/lighter_adapter.py`, `infra/lighter_collector/collector.py`,
`infra/l3_poller/l3_poller.py`, `docs/COLECTOR_LIGHTER.md`, `docs/INVENTARIO_2026-08-24.md`,
`docs/LEDGER.md:1237`, `docs/PREREG_ECO_LIT_INSUMOS.md:54-61`.

Estados: **verificado por lectura** (código y contratos citados) · **no verificado** (identidad de ids,
semántica iceberg, despliegue del poller, contenido real de los frames del colector) · ninguna medición.

## 6. Corrección fechada — 2026-09-05, tras la revisión de la mesa (§6 del dictamen de observabilidad)

El texto de arriba se conserva tal cual. Lo que sigue lo corrige, comprobado en fuente por Code:

1. **`order_id` textual ES `order_index`.** El contrato WS, sección Order JSON, dice «`order_id`: STRING,
   same as order_index but string». La duda string/entero del §1 queda resuelta por contrato. Sigue sin
   acreditar la correspondencia de `ask_id`/`bid_id` con `order_index` y la del `order_id` canónico de
   0xArchive; los IDs se tratan como enteros sin pasar por float.
2. **El despliegue del poller SÍ consta.** `REVISION_COMPLETA_2026-08-24.md:3291-3298` cierra F.2.11: «el
   poller L3 existe, corre, y YA ESTÁ VERSIONADO; sha repo == VPS» (despliegue 23-08, commit `6fe16a0`).
   La fila 11 del inventario que cité es anterior a ese cierre. Que siga activo hoy y conserve cada hora
   de archivo sigue sin comprobar.
3. **El criterio «fracción ≈ 1» del §1 estaba mal planteado.** El denominador de todos los fills incluye
   órdenes nacidas y ejecutadas entre snapshots y órdenes fuera del recorte de 250: una fracción baja no
   refuta la identidad, y una alta no prueba unicidad ni cobertura. Exigir desaparición o decremento
   posterior como admisión condicionaría la muestra a lo sucedido después del fill, que es justo lo que
   el dictamen prohíbe. La comprobación debe separar integridad y tipos, concordancia de claves,
   concordancia de cuenta y lado, cobertura de órdenes observadas antes y situación temporal desconocida.
4. **Retiro «`transaction_time` en ns».** El OpenAPI de trades declara int64 sin unidad; su ejemplo
   `1771943742851429` (16 dígitos) y el del WS `1773854156686065` apuntan a microsegundos; los ejemplos de
   `timestamp` mezclan 10 y 13 dígitos. 0xArchive sí nombra `transaction_time_us`. La unidad se comprueba
   por rango sobre el payload elegido, no se asume por canal. La atribución venía de una paráfrasis de
   herramienta, no de una cita: error de método mío.
5. **Truncamiento:** una orden que sale del recorte puede acabar como `cancel`, `fill` o `through` según los
   prints, no solo como `cancel`; y excluir todos los snapshots truncados selecciona otro universo, que hay
   que declarar.
6. **«No hay tiempo de creación en ninguna fuente» era demasiado amplio:** Order JSON publica `created_at`
   en canales de cuenta autenticados que el colector no suscribe. Lo que se sostiene: nuestras capturas
   públicas no lo traen.
7. **Precisión sobre CHD:** el adaptador devuelve cuatro arrays, lo que prueba qué consume el eco, no que
   la tabla del proveedor carezca de otras columnas. Y `order_id`/`is_maker` de 0xArchive son anulables, no
   obligatorios en el esquema.

**Decisión de la mesa que sustituye a mi sonda de proveedor:** comprobar primero el archivo propio (frames
WS del colector y `orderBookOrders` del poller) sobre XPT, 2026-09-01 12:00–12:10 UTC, en solo lectura, con
conteos y parada sin ampliar; requiere permiso específico de Manuel según el relevo §1.
