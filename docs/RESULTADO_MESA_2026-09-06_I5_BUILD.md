# Mesa · etapa 0 de I5 con la cuenta Build — 2026-09-06

**Resultado observado: INDICIO.** Una única petición de datos devolvió HTTP 200 y un snapshot
de LIT dentro del 2026-03-06 UTC. El cambio de cuenta permite acceder a esa página de marzo.
No acredita la cobertura del día entero, de los 79 días, de tick, de CHD ni de la referencia.
No es una reproducción del decisivo ni una rehabilitación del hallazgo.

## Ejecución y recibos

La ejecución fue anterior a la mudanza de Laboratorio. Estas son las rutas vigentes de las
copias; los recibos conservan sus bytes y los datos históricos de ejecución.

| Evidencia | Observación |
| --- | --- |
| Ventana solicitada | LIT, [2026-03-06 00:00, 2026-03-07 00:00) UTC |
| Consulta | `/v1/lighter/l3orderbook/LIT/history?start=1772755200000&end=1772841600000&limit=1` |
| Resolución | Checkpoint por defecto del contrato; no se pidió tick |
| Ejecución con datos | 09:09:26.385–09:09:27.896 UTC; salida observada 0 |
| Respuesta | HTTP 200; 68.880 bytes; una fila de LIT |
| Primer timestamp | 1772755334791 ms = 2026-03-06 00:02:14.791 UTC |
| Paginación | `next_cursor` presente; no seguido |
| Saldo antes / después | 80.000.000 / 79.999.999; delta de cuenta 1 |
| Cabecera de la petición de datos | `x-credits-used=10`, `x-credits-remaining=79999990` |
| Persistencia | Recibo de metadatos y hash del cuerpo; ningún crudo de mercado guardado |

Recibo principal: `<USER_HOME>/Desktop/Laboratorio/I5_ETAPA0_BUILD_20260906_02/receipt.json`.
SHA-256: `b84d3d0a92f0bcf596441cda63018e30d2f10100927ee0af65f3177447c15229`.
Hash del cuerpo de datos: `65a021b9940761c4ea2ced35ce37ec52c80869bb10be9fc14d070962ddae5f8d`.

Se conservan ambas evidencias contables, sin resolver por conjetura su discrepancia. Un delta
de cuenta puede incluir otros consumidores. Tanto 1 como 10 están por debajo del tope 80 de
esta sonda; no son una tarifa diaria ni un presupuesto de la reconstrucción.

## Incidencia previa, sin datos ni consumo observado

A las 09:07:51 UTC, la primera invocación consultó únicamente `/v1/account/usage` y se detuvo
con `BUILD_ACCOUNT_NOT_VERIFIED` porque el código de Codex exigía `tier` o `plan`. Los campos
numéricos de usage sí confirmaban límite y saldo de 80 millones, pero la respuesta no aportó
ese nombre de plan. Fue una suposición incorrecta del instrumento; los fixtures iniciales
también la compartían. No fue un fallo de acceso histórico del proveedor.

Se corrigió y probó la validación antes de la primera petición de mercado: se exige el límite
de cuenta de 80 millones comunicado por Manuel y se rechaza un plan contradictorio si viene
en la respuesta. La etiqueta Build queda atribuida a la confirmación del propietario/Code
cuando usage la omite. Los límites no son un identificador único de cuenta; no se inventa uno
ni se usa una huella de la clave.

Recibo inicial conservado: `<USER_HOME>/Desktop/Laboratorio/I5_ETAPA0_BUILD_20260906_01/receipt.json`.
SHA-256: `9000b62bcd9a7643f19654f8ce5b8b253f21123312e320a531fef9883da9d772`.
Salida observada por PowerShell: 1; el programa codifica INDETERMINADO como 4.
En total: **cuatro llamadas autenticadas, tres de usage y una de mercado**, sin reintento de
la página de datos. Los recibos del 05-09 y la primera invocación de hoy siguen intactos.

## Consecuencia y reparto

La etapa 0 termina aquí. Se prepara el censo de las 149 celdas históricas, con checkpoint y
tick separados, y la muestra de ocho días de reproducción. El dictamen y el instrumento están
en `PARA_CODE_2026-09-06_I5_CENSO.md`. Code debe auditarlo y ejecutar el censo una vez, según
el reparto vigente. No se ha lanzado ese censo ni una rederivación.

La ruta vigente de la nueva clave es `<USER_HOME>/Desktop/<KEY_DIR>/<KEY_FILE>`.
La cuenta Free sigue siendo el valor por defecto del eco. Se recibió la confirmación de
renovación de Build para el 06-10 a las 08:49 UTC; la sonda de Codex no revalidó ese dato.

STOP, freezes y pins siguen vigentes. HEAD permanece en `7df5280`; la implementación es WIP
sin commit ni acreditación independiente todavía. No se ejecutaron suites largas, push o CI.
