# Mesa → Manuel y Claude · etapa 0: acceso denegado por antigüedad del plan

**2026-09-05, 15:19:45 UTC. Resultado: INDETERMINADO sobre la retención de marzo.**
Manuel respondió «autorizo» al permiso acotado de D2: consultar saldo/coste y una sonda de LIT
2026-03-06, tope total 80 créditos, sin reintentos, parando si no podía justificarse el límite.
La consulta se realizó una vez y terminó. No queda ninguna corrida en segundo plano.

## Respuesta observada

| Campo | Evidencia de esta ejecución |
| --- | --- |
| HEAD local | `7df52803b6db3777b23be85409ef998f879909a8` |
| Fecha/símbolo pedidos | LIT, 2026-03-06 UTC; `[1772755200000,1772841600000)` |
| Ruta | `/v1/lighter/l3orderbook/LIT/history?start=1772755200000&end=1772841600000&limit=1` |
| Alcance | Una página mínima, como máximo un snapshot; sin cursor ni reintento |
| Respuesta | **HTTP 403**, límite de antigüedad del plan |
| Restricción declarada por API | Últimos 30 días; fecha más antigua accesible en ese instante: `2026-08-06T15:19:45Z` |
| Recuento del día | **NO MEDIDO**: el 403 no es una respuesta válida vacía |
| Request ID de la sonda | `75433a3e-000f-438c-9f28-94830bb885d6` |
| Saldo antes, `/v1/account/usage` | 50.000; consumidos en el mes: 0 |
| Saldo después, `/v1/account/usage` | 49.999; consumidos en el mes: 1 |
| Diferencia entre saldos | **1 crédito**, según las dos consultas de saldo |
| Cabecera del rechazo | `x-credits-used: 10`, `x-credits-remaining: 49990` |

Las dos superficies de consumo **discrepan**. Se conservan ambas, sin afirmar que se hayan
conciliado ni realizar otra consulta tras el STOP. Los importes observados están por debajo del
tope autorizado. No se compró un plan, un export ni un suplemento de créditos.

La respuesta de acceso limita esta clave/cuenta; no demuestra que 0xArchive haya borrado marzo.
No se declara AUSENCIA_VALIDA ni se ejecuta la regla de muerte del encargo por respuesta vacía.
Las etapas 1–3 permanecen sin ejecutar. Una suscripción o compra distinta requeriría otra decisión.

## Comprobación del coste antes de la sonda

Se consultó la documentación pública vigente y el OpenAPI. El contrato permite `limit=1` snapshot;
la documentación L3 limita cada snapshot a 250 órdenes por lado. La tarifa publicada aplica
`max(1, ceil(rows_returned / 1000))` a Lighter L3: una página mínima queda en 1 crédito según esa
regla, incluso contando sus hasta 500 órdenes como filas. Las consultas de saldo devolvieron HTTP
200; la previa informó `x-credits-used: 0`. No se basó el permiso de gasto en el suelo de saldo del
script antiguo, que expresamente no impone un límite duro.

Fuentes públicas consultadas:

- [Créditos REST](https://docs.0xarchive.io/core-concepts/credits), actualizada el 2026-08-29.
- [Contrato OpenAPI](https://docs.0xarchive.io/openapi.json), obtenido a las 15:17:29 UTC.
- [Planes](https://0xarchive.io/pricing), que también limita Free a los últimos 30 días.

El coste publicado y la cabecera del rechazo difieren; el saldo posterior es una tercera
observación, registrada arriba. No se presenta una garantía contractual del proveedor como
contención técnica local de facturación.

## Corrección de una premisa del dossier y de mi dictamen previo

**La etapa 0 no estaba inédita.** `PARA_LA_MESA_2026-08-25_RONDA2.md:82-105` y
`docs/runs/etapa0_oxa_2026-08-25.txt` declaran una ejecución el 25-08: 500 filas y un crédito.
Quedó como **atestación del operador**, sin captura primaria de salida y sin validación completa
de símbolo/intervalo. No se eleva hoy esa evidencia a un recibo verificable.

El dossier del 05-09 omitió ese antecedente, y mi dictamen anterior no lo detectó. Retiro la
presentación de D2 como primera sonda aún no realizada. La ejecución autorizada hoy es una nueva
comprobación de acceso actual, con página mínima y recibo generado durante la consulta. La
rederivación completa continúa pendiente. El resultado antiguo y el rechazo actual no bastan
para fechar un cambio de plan ni para concluir pérdida de retención.

## Evidencia y límites de esta entrega

- Recibo generado por el lanzador durante la ejecución:
  `quant-system-ingesta/qs/docs/runs/i5_etapa0_20260905_151944.json`.
- Copia original y preparación en
  `<USER_HOME>/OneDrive/Documents/Laboratorio/I5_ETAPA0_20260905/`:
  `usage_before.json`, `contract_selected.json`, `openapi.json`, `probe.started`, `receipt.json`.
- Lanzadores locales: `<USER_HOME>/OneDrive/Documents/Laboratorio/i5_preflight_20260905.py`
  e `i5_sonda_20260905.py`. Sus hashes y el del validador del repo figuran en el recibo.
- Se reutilizó el validador existente; no se modificó código del repositorio ni se repitieron tests.
- Hubo tres llamadas autenticadas: saldo previo, sonda, saldo posterior. Sin redirecciones,
  paginación ni reintentos. Las demás lecturas fueron documentación pública.
- El recibo conserva metadatos, error, hashes de respuestas y request IDs; no es un recibo firmado
  por el proveedor ni guarda cuerpos completos. No se guardaron credenciales ni contenido de órdenes.
- La herramienta de ejecución devolvió código **1** para el comando PowerShell. El lanzador está
  escrito para salir con 4 ante INDETERMINADO; no se atribuye ese 4 como exit code directamente
  observado ni se repite la consulta para verificarlo. El JSON persistido registra el 403 y el estado.

**Siguiente decisión productiva:** si se quiere acceder al histórico de marzo, hace falta resolver
el acceso comercial a ese rango. Esta sonda no autoriza comprarlo, no justifica otra consulta
idéntica y no abre la campaña de L ni F′. STOP de producción, push y CI permanecen vigentes.

## Dictamen posterior sobre la recomprobación pública de Claude — 2026-09-05

Leídos completos `RECOMPROBACION_2026-09-05_0XA_MARZO.md` y
`PARA_LA_MESA_2026-09-05_DECISIONES_CAP2_ADENDA.md`. Contrastados por la mesa contra las páginas
públicas citadas y el OpenAPI guardado durante la preparación. Sin llamadas autenticadas nuevas,
sin datos de mercado, código, pruebas, commit ni compras.

**Acepto la explicación del rechazo.** El [changelog v2.8.0](https://0xarchive.io/changelog),
fechado el 31-08-2026, declara el límite móvil de 30 días de Free y que este cambio no retiró
datos del archivo. Es coherente con el 403 de nuestra cuenta. La afirmación de retención es del
proveedor; no sustituye evidencia de completitud de LIT en cada uno de los 79 días. La ejecución
del 25-08 conserva su categoría de atestación del operador, sin elevarla a comprobación primaria.

Correcciones resolutivas al informe comercial:

1. **D1 ya está emitida**, como la propia adenda recoge. No se devuelve a Manuel la misma decisión
   metodológica. El diagnóstico retrospectivo está aprobado en ese plano; la ejecución de las
   etapas 1–3 y cualquier compra conservan su autorización operativa pendiente.
2. **Retiro como conclusión acreditada «un mes bastaría» / «cabe cientos de veces».** Build publica
   $49/mes y 80M créditos, pero esa cuota no mide las páginas, cobertura, truncamiento ni la
   reproducción del differ. Tampoco resuelve por sí sola los trades CHD ni la referencia Binance.
   Los ~79 créditos/día usados en la extrapolación no son un presupuesto medido de toda la receta.
3. **El Data Catalog no quedó afectado por el límite de Free**, según el mismo changelog. Esa
   incertidumbre del informe puede cerrarse documentalmente. Queda por obtener una cotización
   concreta: para L3 la tarifa publicada es $3/GB con mínimo de $5, no el intervalo de precios de
   todos los tipos de datos. No se conoce el tamaño ni el total de LIT marzo–junio. Fuente:
   [tarifas oficiales](https://0xarchive.io/pricing).
4. **La cobertura es metadato del proveedor, no prueba de rederivación.** El OpenAPI de
   `/v1/data-quality/coverage/{exchange}/{symbol}` admite `from`/`to` en milisegundos; sin ellos
   inspecciona los últimos 30 días. Su cobertura histórica tiene resolución horaria, y
   `completeness` describe 24 horas. Si se autoriza esa consulta, deberá pedir explícitamente
   marzo–junio y examinar el tipo L3. Ni un porcentaje verde ni unos extremos earliest/latest
   prueban integridad de snapshots ni suficiencia para I5. No se ejecuta esa consulta aquí.

La documentación general también advierte que disponibilidad de una ruta no garantiza cobertura
por mercado: [cobertura del proveedor](https://docs.0xarchive.io/venue-coverage).

**Decisión de mesa:** se acepta la adenda D1–D4 y la causa del 403; se mantienen estas salvedades
sobre el informe comercial. No recomiendo comprar aún con la extrapolación presentada ni repetir
la sonda. Para D4, la siguiente comprobación sigue siendo Season 3 y fees mediante fuentes públicas
fechadas. Su permiso de red es distinto del permiso D2 ya ejecutado; no se invoca D1 como bloqueo.
No hace falta otro barrido ni un commit documental para resolver ese paso. Una fecha de commit
tampoco constituye por sí sola una firma del propietario ni un sello horario externo.
