# Code → Mesa y Codex · 2026-09-06 · Etapa B ejecutada: el tick de LIT 2026-03-06 es la serie checkpoint

**Resultado: `ALL_SOURCE_PAGINATIONS_EXHAUSTED`, rc 0, 3 llamadas, 8 s, 1 crédito.** La petición
`granularity=tick` para LIT del 2026-03-06 devolvió **una página de 527 snapshots, 36.146.223 bytes**, y su
array `data` es **idéntico objeto a objeto** al de la página checkpoint del mismo día custodiada en la etapa A:
mismos 527 timestamps en el mismo orden, mismos 500 órdenes por snapshot, mismo `truncated=true` en todos.
Solo difiere `meta.request_id`, que es por petición y explica el hash distinto con longitud igual. Nada se
declara ratificable.

## 1. Identidad

| campo | valor |
|---|---|
| comando | etapa B del relevo `PARA_CODE_2026-09-06_I5_DESCARGA_ETAPAS.md`, `--resolutions tick --cells 70` |
| instrumento | `i5_descarga_l3.py` `fcc6f6fa…` (re-verificado al arrancar); plan idéntico al `etapa_B_plan.json` de Codex |
| salida | `Desktop\Laboratorio\I5_L3_TICK_LIT_20260306_20260906_01\070_LIT_2026-03-06_tick\` |
| UTC | 22:02:02 → 22:02:10 |
| cuenta | usados 448 → 449; restantes 79.999.551 |
| peticiones | `…/l3orderbook/LIT/history?start=1772755200000&end=1772841600000&limit=1000&granularity=tick` (tick) frente a `…&granularity=checkpoint` (A); `request_id` distintos: dos respuestas reales del servidor |

## 2. Comparación con el checkpoint del mismo día (etapa A)

| | checkpoint (A) | tick (B) |
|---|---|---|
| filas | 527 | 527 |
| bytes del cuerpo | 36.146.223 | 36.146.223 |
| sha256 del cuerpo | `747a46b7…` | `de656ba5…` (difiere solo por `meta.request_id`) |
| `data` | — | **idéntico** al de A (comparación objeto a objeto tras descomprimir ambos gzip) |
| timestamps | 527 únicos | los mismos 527, mismo orden |
| órdenes por snapshot | 500 (250/lado, `truncated=true` en 527/527) | idem |
| separación máxima | 318 s | 318 s |
| primer / último snapshot | 00:02:14,791 / 23:59:35,607 UTC | idem |
| cursor terminal | omitido | omitido |

**Lectura estricta:** para este símbolo y este día, el endpoint sirve la misma serie de ~2,9 min tanto si se
pide `checkpoint` como si se pide `tick`. No hay resolución más fina disponible ahí. Es un día y un símbolo:
no generaliza por sí solo a los otros 148 días ni a otras granularidades (`30s`, `10s`, `1s`), y no dice si
el proveedor tiene tick L3 para fechas recientes.

## 3. Consecuencias, si se confirma en más días

1. **La custodia «a máxima resolución» del histórico ya está hecha con la etapa A** (3,35 GB crudos, 414 MB en
   disco): una etapa C que pida tick para las 149 celdas descargaría duplicados byte a byte salvo el
   `request_id`. Las estimaciones de terabytes quedan sin objeto para este endpoint y esta ventana.
2. **La extensión diagnóstica «tick» sobre marzo–junio no es posible vía 0xArchive**: el insumo histórico de
   L3 es una vista truncada a 250 órdenes por lado cada ~2,9 minutos. Cualquier diseño de F′ que necesite
   resolución fina tendrá que apoyarse en capturas propias hacia delante (colector L2 a 50 ms y poller L3 a
   5 s), que son las únicas que existen a esa escala, y solo desde que corren.
3. **El productor de los ocho días puede arrancar ya sobre las páginas checkpoint de A**, que es la receta
   histórica. Nada de lo anterior toca D1 ni el veredicto congelado.
4. La frase de la documentación pública «tick-level L3 individual-order depth from March 5, 2026» no se
   corresponde con lo servido para este día. Se registra como discrepancia documental del proveedor, sin
   atribuirle causa.

## 4. Propuesta para cerrar la duda antes de decidir C (barato, y es de la mesa)

Con una página de `limit=1000` por consulta, un crédito cada una, y comparación de `count` y timestamps contra A:

- **Tick en los otros siete días de reproducción de LIT** (7 créditos, ~1 min): si los siete coinciden con su
  checkpoint, C queda sin objeto para LIT; DOGE se comprueba con dos o tres días.
- **`1s`, `10s` y `30s` para LIT 2026-03-06** (3 créditos): si también devuelven 527, el parámetro se ignora en
  el histórico; si devuelven series distintas, existe una resolución intermedia real y hay que medirla.
- **Tick de un día reciente**, por ejemplo LIT 2026-09-01, misma ventana que la comprobación de XPT (1 crédito):
  dice si el tick L3 existe para datos recientes, lo que importa para cualquier cruce futuro con el poller.

Son consultas nuevas: no las lanzo sin decisión. Si la mesa las aprueba, caben en el instrumento actual con
`--cells` y un valor más de `--resolutions`, o como sonda de una página con recibo.

## 5. Estados

**Ejecutado** (B, una vez) · **verificado localmente** (comparación byte a byte y objeto a objeto de los gzip
custodiados) · **auditado independientemente**: no (informe del ejecutor) · CI: no aplica. STOP, freezes y pins
vigentes. Saldo Build 79.999.551.
