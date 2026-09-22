# Mesa · verificación pública del régimen de Lighter

**2026-09-05. D4.1 ejecutada con la autorización expresa de Manuel «SI, AUTORIZO».**
Codex emite esta comprobación como mesa. Base local: HEAD
`7df52803b6db3777b23be85409ef998f879909a8`, rama `codex/wip-m12.20`.
Capturas primarias conservadas entre 15:50 y 15:52 UTC. Esta comprobación no es un freeze.

## Dictamen

**No queda acreditado un lanzamiento de Season 3 de Lighter Core en las fuentes examinadas.
Sí están acreditados puntos en Robinhood Chain y cambios recientes en la microestructura de Core.**
Por ello, la mesa no ratifica para el eco la premisa heredada «sin incentivos y régimen homogéneo».
Tampoco declara una ruptura estadística, un NO-REPLICA ni la inutilidad de los datos: no se han
leído resultados de mercado. La comprobación pública requerida se ha realizado; su resultado no
es un verde automático para F′.

## Evidencia fechada y alcance

| Hecho | Fecha de la evidencia | Fuente primaria |
| --- | --- | --- |
| El programa de Robinhood Chain tenía anunciado su inicio el 13-08 a las 16:00 UTC; el canal general confirmó que ya estaba activo a las 16:10:45 UTC de ese día. Es una instancia distinta de Core. | Anuncio técnico 12-08; confirmación 13-08-2026 | [API 157](https://t.me/lighter_api_updates/157), [anuncio 392](https://t.me/lighter_announcements/392) |
| Las condiciones del programa de Robinhood tienen fecha efectiva 10-08; la página fija el primer reparto semanal el 21-08. No confundir esa fecha contractual con el inicio operativo. | Documento vigente al consultar | [Programa Robinhood](https://docs.lighter.xyz/points-program/lighter-on-robinhood-chain-points) |
| Se anunció un nuevo reparto de puntos de Robinhood Chain. | 04-09-2026, 15:01:59 UTC | [Anuncio 423](https://t.me/lighter_announcements/423) |
| Standard pasa a pagar 0,01% = 1 bp en RFQ, Chase Limit y TWAP. Limit y Market continúan gratis. Plus y Premium conservan sus tarifas de tier. | 23-08-2026, 12:10:46 UTC | [API 163](https://t.me/lighter_api_updates/163) |
| En Core quedan desplegadas las latencias Standard: taker 300 ms, cancelación 300 ms, Post-Only sin demora añadida. Premium: taker 140 ms en todos los tiers. | 30-08-2026, 13:10:24 UTC | [API 168](https://t.me/lighter_api_updates/168) |
| El canal general confirma que la cancelación Standard cambió de 200 a 300 ms y Premium taker de 140–200 a 140 ms uniforme. | 31-08-2026, 07:32:33 UTC | [Anuncio 416](https://t.me/lighter_announcements/416) |
| Core incorpora órdenes iceberg: solo una parte de la orden queda visible en el libro. | Confirmado 31-08-2026, 18:01:54 UTC | [Anuncio 417](https://t.me/lighter_announcements/417) |

La fecha del mensaje de despliegue acredita que el cambio ya estaba operativo en ese momento;
no es una medición del instante exacto de activación. No convierto el mantenimiento anunciado
para el 30-08 a las 11:00 UTC en una frontera intradía exacta.

## Fees vigentes: concretar cuenta y tipo de orden

La [tabla oficial de trading fees](https://docs.lighter.xyz/trading/trading-fees) consultada hoy
publica:

| Cuenta | Maker | Taker |
| --- | --- | --- |
| Standard, Limit/Market ordinarias | 0 | 0 |
| Premium sin stake | 0,0040% = 0,40 bp | 0,0280% = 2,80 bp |
| Premium, máximo descuento publicado | 0,0028% = 0,28 bp | 0,0196% = 1,96 bp |
| Plus | 0,5 bp | 0,5 bp |

La tabla general debe leerse junto con la excepción de órdenes avanzadas del anuncio API 163.
«Standard 0/0» sigue siendo correcto para las órdenes ordinarias indicadas; no cubre cualquier
modalidad de ejecución. No se incluyen funding, spread, impacto ni eventuales costes del integrador.

La página general conserva una latencia maker Standard de 200 ms. El anuncio de despliegue
especifica Post-Only a 0 ms de demora añadida: no atribuyo esos 200 ms a Post-Only ni interpreto
0 ms como latencia total de red/ejecución. Los [LIT Fee Credits](https://docs.lighter.xyz/trading/trading-fees/lit-fee-credits)
permiten acceder a beneficios de tier mediante pago en LIT; no se ha medido su uso por la cohorte.

## Qué se sabe —y qué no— de Season 3

La consulta de anuncios con «season» recuperó el cierre de Season 2 y el guiño «S3e» del
[27-12-2025](https://t.me/lighter_announcements/236), sin una fecha de lanzamiento de Season 3.
La [página general de puntos](https://docs.lighter.xyz/points-program) y su
[sección retail](https://docs.lighter.xyz/points-program/retail) aún describen Season 2;
su presencia actual no demuestra que aquella temporada siga activa.

**Estado de Season 3 Core: NO ACREDITADO en esta revisión**, no «demostrado que no existe».
Se revisaron documentación oficial, anuncios públicos y búsquedas por season/points.
El acceso directo a X falló; la búsqueda de Telegram no constituye un archivo exhaustivo ni
garantiza ausencia de mensajes borrados. La procedencia del canal general está enlazada desde
[la web de Lighter](https://lighter.xyz); ese canal enlaza el canal técnico utilizado.

No denomino Season 3 de Core al programa de Robinhood. Tampoco infiero que una instancia distinta
carezca de efectos sobre Core: no se ha medido migración ni arbitraje entre ambas. Además, el
[resumen oficial del 28-08](https://t.me/lighter_announcements/414) promociona competiciones de
integradores con premios ligados a actividad. No he verificado su ejecución o participación:
basta para no tratar «sin Season 3 acreditada» como prueba de «flujo sin incentivos».

## Consecuencia para el diseño siguiente

Estas son decisiones metodológicas de la mesa, no resultados estimados:

1. **Marzo–junio e I5.** Los cambios aquí fechados en agosto no demuestran un cambio dentro de los
   79 días históricos. Se conserva D1: diagnóstico retrospectivo post hoc aprobado
   metodológicamente, con acceso y ejecución pendientes. Esta revisión tampoco prueba por sí
   sola homogeneidad completa de marzo–junio.
2. **Eco y F′.** La acumulación desde el 30-06 alcanza cambios conocidos de fees, latencias y
   visibilidad de órdenes. No se trasladará a esa acumulación la homogeneidad declarada para la
   ventana anterior. Un libro con iceberg merece atención en un estimando basado en visibilidad
   y supervivencia; el anuncio no demuestra que el differ falle ni ordena modificarlo.
3. **Siguiente trabajo de mesa: definir el objeto científico de F′.** El diseño debe explicitar
   Core como instancia si conserva las fuentes actuales, la diferencia entre cohorte observada
   y cuenta operable Standard, el tratamiento de selección/lado/basis y los cambios de régimen.
   Edad de una orden observada no identifica por sí sola su tier. La ventana prospectiva,
   horizontes y regla ante nuevos cambios se fijarán antes de leer el resultado, sin recortes
   retrospectivos para mejorar un veredicto.
4. **No se fija cap con esta consulta.** Siguen la campaña de L y el sustento de T17 y de los
   tiempos de auditoría en el orden de D4. La restricción sobre unlocks de diciembre no se ha
   vuelto a verificar en este encargo de Season 3/fees y no se ratifica aquí.

Referencias locales que motivan esta comprobación:
`LEDGER.md:1265–1274,1521–1526`, `PREREG_MAKER_LIGHTER.md:5–11`,
`DECISION_2026-08-24_CALENDARIO.md` §9.0 y `DICTAMEN_MESA_2026-09-05_CAP2.md` D4.
Los freezes históricos se conservan; este dictamen es una actualización fechada de su contexto.

## Custodia y límites de ejecución

Evidencia pública local:
[<USER_HOME>/OneDrive/Documents/Laboratorio/VERIFICACION_LIGHTER_20260905/](<USER_HOME>/OneDrive/Documents/Laboratorio/VERIFICACION_LIGHTER_20260905/).

Los manifiestos registran URL, instante de solicitud, HTTP y SHA-256 de los cuerpos descargados:

- `manifest.json`: `5c45f0fac5d2c4cdc91ac39b19df9295a963128db21dec5c9b0b385be61c0af8`.
- `manifest_additional.json`: `1682667c15b495d5fe440802c5a1b60ec490cbd0b393fe38ef5638606a3ac675`.

Los JSON de mensajes son extractos auxiliares del HTML conservado. Algunos timestamps del HTML
contienen offset +01/+02; las fechas de la tabla se han expresado en UTC. Las huellas acreditan
integridad de las copias locales, no una firma ni un sello horario externo del proveedor.

El primer descargador terminó con error de codificación al imprimir un emoji, después de guardar
los diez cuerpos y el manifiesto. Se comprobaron los archivos guardados; no se repitieron esas
descargas. El segundo bloque terminó con exit 0. No se consultó API autenticada, saldo, crudos,
NPZ ni markouts; no hubo gasto de proveedor, suites, barridos, cambios de código del repositorio,
commit, push, CI ni modificación de freezes. STOP continúa vigente.

