# Mesa · restricciones del instrumento y base científica de F′

**2026-09-05. Dictamen sobre la valoración remitida por Claude después de D4.1.**
Base: HEAD `7df52803b6db3777b23be85409ef998f879909a8`, rama `codex/wip-m12.20`.
Verificación por lectura de código y documentos; ninguna ejecución sobre datos.
Este documento avanza D4.2. **Es una base de diseño para auditoría, no un prereg cerrado ni una
autorización de producción.** El dictamen de régimen y los freezes históricos se conservan.

## 1. Qué acepta y qué corrige la mesa

| Afirmación recibida | Resolución |
| --- | --- |
| El differ y el atlas dependen del tamaño restante | **Sí.** El atlas pondera con decrementos o remanentes; el núcleo del eco usa el decremento para clasificar eventos. El núcleo no persiste cantidades. El significado de `remaining_size` para una iceberg no se demuestra leyendo el nombre del campo: falta verificar el contrato sobre tramo visible, total pendiente e identidad tras reposición. |
| Las latencias afectan a la cuenta operable, no a la cohorte | **La fórmula de cohorte no compara milisegundos.** Pero cambiar cancelación y ejecución puede cambiar qué órdenes sobreviven y qué fills entran: la distribución de la cohorte también puede variar. La asimetría técnica no prueba por sí sola cuánto cambia su markout. |
| Fees: nada en el estimando | **Solo se sostiene el coste directo cero de Limit/Market Standard.** Una tarifa distinta para otros participantes o modalidades puede modificar el flujo con el que se cruza el maker. No se ha demostrado invariancia del estimando a esa composición. |
| Puntos en Robinhood: afectan a masa, no a signo | **No aceptado.** Si migran participantes de distinta toxicidad, pueden cambiar masa, mezcla, media y dispersión en Core. No sabemos la magnitud ni la dirección, ni se ha medido que haya migración. |
| Homogeneidad marzo–junio intacta | **Más limitado:** los cambios aquí fechados en agosto no refutan homogeneidad dentro de marzo–junio. Tampoco la prueban. D1 conserva su aprobación como diagnóstico retrospectivo post hoc. |
| Trade mayor que nivel visible detecta iceberg | **No identifica iceberg.** Puede ser una discrepancia entre observaciones, pendiente de validar. No se adopta como filtro de régimen ni se fija ahora un umbral. |

Las afirmaciones de efectos posibles son inferencias de la mesa, no mediciones nuevas. Por
ejemplo, una media de mezcla depende de los pesos y de las medias de sus componentes; cambiar
pesos no está restringido a cambiar el número de observaciones.

La evidencia externa fechada sigue en
[la verificación de régimen](VERIFICACION_MESA_2026-09-05_LIGHTER_REGIMEN.md).
No se ha repetido su búsqueda pública en esta revisión.

## 2. Mapa ejecutable: tres capturas y una receta actual

- **Eco LIT actual:** `eco_runner_lit.py:245,263–276` obtiene snapshots 0xArchive, trades Lighter y
  precios de trades Binance, y llama a `confirm_runner._differ_core`. No consume automáticamente
  el colector L2 ni el poller L3. `CARRIL_USADO` sigue siendo `TRADE_BINANCE` y la guarda de
  producción permanece antes de IO (líneas 62 y 234–236); una docstring que diga mid no cambia esa ruta.
- **Cohorte:** `confirm_runner.py:95–105,129` usa `oid in prev_seen`, con un conjunto acumulado.
  Acredita presencia observada anterior; no comprueba un umbral fijo en segundos ni continuidad
  observada en todos los snapshots intermedios. Cambiar cadencia cambia la definición operativa.
  No se equiparará esta etiqueta a «cuenta Standard» ni a habilidad de cancelación.
- **Clasificación e I5:** `confirm_runner.py:100–128` consulta los prints de todo el intervalo,
  prioriza through al desaparecer una orden y asigna a ese caso el primer tiempo through.
  `thr_con_at` conserva si hubo algún at; no conserva el tiempo de ese at. Reclasificar el flag
  no restituye automáticamente otro instante de fill ni elimina toda dependencia del cierre
  del intervalo. I5 sigue siendo una sensibilidad necesaria, no una prueba de identificación.
- **Cantidad y atribución:** `pilot_observer.py:51–66` imputa cantidades con `rem−nrem` o `rem`;
  `wallet_atlas.py:82–96` las convierte en volumen lento. Los prints corroboran por precio;
  estas funciones no enlazan un identificador de ejecución a una orden concreta. Varias órdenes
  pueden compartir ese precio. El esquema del eco (`eco_runner_lit.py:99–101`) no persiste
  `oid`, `px`, `qty` ni referencia en el instante de fill.
- **Colector WS:** `infra/lighter_collector/collector.py:14–16,97–115` documenta L2 nominal a
  50 ms y trades con cuentas; guarda frames enteros y `recv_ns`. No reconstruye ni sincroniza el
  libro, no impone desde ese bucle una cadencia exacta y no certifica la completitud de la captura
  actual. Cuenta no equivale a identificador de orden.
- **Poller L3 separado:** `infra/l3_poller/l3_poller.py:5–19,48–49,183–192,208–210` archiva
  respuestas order-level completas, con cadencia nominal de 5 s y límite 250 por lado.
  `remaining_base_amount` es distinto del nombre 0xArchive. Una ausencia en una respuesta
  limitada tampoco demuestra por sí sola ejecución o cancelación. No se ha comprobado aquí la
  cobertura de su archivo ni su representación de iceberg.

Rutas de `*.py` de análisis relativas a
`quant-system-ingesta/qs/analysis/`; rutas `infra/` relativas a la raíz del repositorio.

## 3. Por qué el proxy propuesto no identifica iceberg

Dos contraejemplos lógicos, sin datos del proyecto:

- Último L2 observado: 10 unidades. Entra liquidez visible nueva antes del siguiente mensaje L2;
  después aparece un trade de 15. Hay exceso respecto al último tamaño observado sin iceberg.
- Una iceberg repone clips visibles de 10 y se ejecuta en prints de 5. Ningún print tiene por qué
  superar el tamaño visible observado, aunque exista reserva oculta.

También hay que resolver orden temporal entre canales, unidades, precio/nivel, agrupación de
prints, huecos y reanclajes. Un `recv_ns` común no acredita por sí solo sincronía del evento
económico. **Ausencia de excesos no certifica ausencia de iceberg; presencia no la demuestra.**
La literatura del problema o un umbral elegido antes de mirar markouts no sustituyen la
validación del instrumento en estas fuentes.

La propuesta admisible sería describir discrepancias volumen–L2, con denominador y tratamiento de
huecos explícitos. Su medición y eventual uso para excluir periodos no quedan ordenados aquí.
Para conocer cola y volumen por orden hacen falta semántica e identidad, no solo ese estadístico.

## 4. Base de F′: qué queremos medir y qué todavía no podemos prometer

**Objeto propuesto:** asociación entre persistencia observada antes de una ejecución identificada
y la deriva posterior de la referencia, comparada con órdenes de aparición reciente bajo
condiciones comparables. Es observacional. No identifica el efecto causal de esperar/cancelar,
ni el beneficio que obtendría una cuenta Standard.

Para un evento identificable `e`, lado maker `s=+1` bid / `−1` ask, precio `p`, referencia
inmediatamente anterior a la ejecución `R0` y referencia en el horizonte `Rh`:

```text
M_e(h) = 10^4 · s · (Rh − p) / p
B_e    = 10^4 · s · (R0 − p) / p
D_e(h) = 10^4 · s · (Rh − R0) / R0
M_e(h) = B_e + (R0 / p) · D_e(h)
```

Es una identidad algebraica, no un resultado del expediente. `B_e` contiene el nivel inicial
orden–referencia, que mezcla distancia al mid local y basis entre venues; no se le llamará
«basis puro». `D_e` separa la deriva de la referencia de ese término aditivo, pero no elimina
confusión de selección, diferencias temporales o cambios dinámicos del basis.

El contraste candidato será **lenta menos reciente dentro de cada lado**, con pesos 1/2 bid y
1/2 ask y una distribución de condiciones previa común a ambas cohortes. Debe comparar sesiones,
volatilidad e información inicial de libro/basis, con soporte compartido; no restar dos medias
globales de oportunidades distintas. Días o celdas sin comparación no reciben ceros ni se
renormalizan por el lado disponible. Ponderación temporal, soporte mínimo y tratamiento de
faltantes se cerrarán antes de medir.

**Predicción comprobable:** esa diferencia de deriva favorece a la cohorte persistente por al
menos un efecto relevante fijado antes de la lectura. Un límite superior compatible solo con
efectos inferiores a ese mínimo refutaría esa predicción; falta de potencia no la refuta. Un
efecto de signo positivo tampoco acredita rentabilidad neta.

La elección final de horizonte, efecto mínimo y regla inferencial sigue abierta: no se heredan
25 s, +18,24, sigma ni N_min=17 como calibración válida de un estimando distinto. Los suelos y
reglas congelados permanecen vigentes para sus objetos; cualquier nuevo diseño debe justificar
los suyos sin rebajar los compromisos anteriores. No se elige aquí un símbolo nuevo para ganar masa.

### Condición de medición que precede a implementar

La admisión del evento, su lado, identidad y persistencia previa deben quedar determinados por la
ejecución y su historia previa, **sin vetarlo por un through posterior**. Procesar tarde un registro
no es lo mismo que usar sucesos posteriores para seleccionar qué ejecución se admite.

El contrato debe resolver cómo se enlaza ejecución–orden y cómo se trata la reposición iceberg;
qué significa el tamaño devuelto; y qué referencia y reloj se usan en `R0` y `Rh`. La referencia
inicial será previa; las tolerancias y reglas ante huecos deberán quedar explícitas. El esquema
actual de bloques no contiene estos insumos, y el differ descrito no acredita ese enlace.

**Decisión de mesa:** no encargar un detector iceberg ni parchear la receta congelada para llamar
«fill identificado» a un proxy. Primero cerrar esta cuestión de observabilidad por contrato y
auditoría de las fuentes existentes. Si no puede resolverse, este contraste de fills será
NO IDENTIFICABLE con ese instrumento. Un análisis de eventos imputados tendría otro objeto y
debería nombrarse como tal, no sustituirlo silenciosamente.

Claude puede auditar esta base y documentar qué campos resuelven cada enlace, distinguiendo lo que
dice el código de lo que confirma el contrato del feed. No se solicita una suite ni una lectura de
datos. Codex implementará solo el cambio concreto que resulte necesario tras cerrar el objeto.

## 5. Estado de la entrega

Se crea este dictamen y se enlaza desde D4. No se ha alterado código del repositorio, ejecutado
tests o barridos, accedido a proveedor o VPS, ni abierto crudos/NPZ. STOP, pins, lectura única,
D1 y el resultado de la sonda histórica mantienen su estado. Sin commit ni push.

La base científica queda escrita y sus límites de medición identificados. **D4.2 no se declara
cerrado**: falta resolver el enlace ejecución–orden y cerrar horizonte, efecto relevante,
inferencia, potencia y ventana antes de que exista un prereg firmable.


## 6. Revisión de la auditoría de Claude sobre el enlace — 2026-09-05

Leída completa `AUDITORIA_CODE_2026-09-05_ENLACE_EJECUCION_ORDEN.md`
(SHA-256 `932dc949463c8aa83cddaf5e45d07fe51d99d508042d8518b3306be4ccaa01f5`).
Se conserva sin editar. Acepto el mapa de la receta y sus campos perdidos; **no ratifico la sonda
propuesta ni la afirmación de que queda una sola identidad que un porcentaje próximo a uno cerraría**.

### Correcciones comprobadas en fuentes

1. **El segundo identificador del libro no es una incógnita independiente por ser string.**
   El [contrato WS, Order JSON](https://apidocs.lighter.xyz/docs/websocket-reference#order-json)
   dice de `order_id`: «same as order_index but string». Distingue además el identificador
   asignado por el cliente. Queda resuelta esa relación documental en el objeto descrito;
   no demuestra por sí sola todas las correspondencias con `ask_id/bid_id` y con la
   transformación canónica de 0xArchive. No se comprará dato para comprobar solo string frente
   a entero. Los IDs se tratarán sin pérdida de precisión, nunca a través de float.
2. **El despliegue del poller sí consta históricamente.**
   `REVISION_COMPLETA_2026-08-24.md:3291–3298` cierra F.2.11. El mensaje de
   `6fe16a064b04f4fc0766150a9c80ffdab9f961d4` registra despliegue el 23-08 y comparación de hashes
   repo/VPS. La fila 11 del inventario es anterior a ese cierre. Es evidencia documental del
   antecedente, no una comprobación de que hoy siga activo o de que conserve cada hora de archivo.
3. **«No hay tiempo de creación en ninguna fuente» es demasiado amplio.**
   Order JSON publica `created_at`; lo usan canales de órdenes de cuenta que requieren
   autenticación y que nuestro colector no suscribe. No acredita que tengamos ese campo para
   el universo ni que identifique la edad económica tras una modificación/reposición.
   La conclusión útil sigue siendo: nuestras capturas públicas descritas no acreditan una
   creación exacta. Un cero observado en `transaction_time` tampoco demuestra una ausencia
   universal de otros campos de creación.
4. **Se retira la atribución de nanosegundos al contrato de trades.**
   El [OpenAPI REST de Lighter](https://apidocs.lighter.xyz/reference/trades.md) declara enteros
   int64 y ejemplos, sin fijar en esos campos la unidad mediante descripción. Su ejemplo de
   `transaction_time` tiene magnitud de microsegundos. El ejemplo WS empareja timestamp de
   13 dígitos con transaction_time de 16; hay otros ejemplos de timestamp con 10 dígitos.
   Esto evidencia documentación no uniforme, no licencia una conversión por canal asumida.
   0xArchive sí denomina y describe explícitamente
   [`transaction_time_us` en microsegundos](https://docs.0xarchive.io/schemas/operations/get-lighter-trades).
   Las unidades y coherencia entre relojes deben comprobarse sobre el payload elegido.
5. **Truncamiento puede producir más de una clasificación errónea.**
   `wallet_atlas._snaps_owner` descarta ese metadato al mapear el snapshot. En el núcleo,
   una orden que sale del recorte puede terminar como cancel, fill o through según los prints.
   No es solo pérdida de cancels. El
   [flag de 0xArchive](https://docs.0xarchive.io/schemas/operations/get-lighter-l3-orderbook-history)
   indica que se alcanzó el tope; no señala qué orden salió. Excluir todos los snapshots
   truncados seleccionaría además otro universo: hay que declarar el alcance, no llamarlo
   automáticamente inocuo.
6. **Contrato actual no equivale a archivo histórico verificado.**
   El writer guarda frames completos; no se han abierto aquí los frames de julio.
   El adaptador CHD devuelve solo cuatro arrays, lo que prueba qué consume el eco, no que
   cualquier versión de la tabla del proveedor carezca de otras columnas. Los campos
   `order_id` e `is_maker` canónicos de 0xArchive son anulables y no pertenecen al conjunto
   required del esquema leído. Una fila canónica no garantiza por sí sola que ambos estén presentes.
   La ruta histórica también limita el final efectivo a `finalized_through`.
7. **La nueva prueba propuesta de iceberg tampoco la identifica por sí sola.**
   Acumular ejecuciones por encima del remanente visto mientras reaparece el ID puede ser
   compatible con reposición iceberg, pero necesita descartar modificaciones y resolver la
   semántica del campo/identidad. No hay etiqueta de verdad de iceberg en ese conteo.
   La laguna precisa es la representación contractual en las fuentes examinadas; «no se
   puede cerrar leyendo» no es una conclusión general demostrada.

### Por qué se rechaza el criterio «fracción aproximadamente uno»

El denominador de todos los fills incluye órdenes nacidas y ejecutadas entre snapshots, órdenes
fuera del recorte y tramos sin observaciones utilizables. Incluso con IDs idénticos, muchas no
tienen por qué aparecer en el último snapshot previo. Una fracción baja **no refuta la identidad**.

Una fracción alta aporta concordancia en una muestra, pero no prueba unicidad, representación de
iceberg ni cobertura general. Y exigir desaparición o decremento en el snapshot posterior como
criterio de admisión volvería a condicionar la muestra a lo sucedido después del fill. Puede
estudiarse como diagnóstico separado; no decide qué ejecución fue real.

La comprobación debe separar: integridad/tipos y duplicados; concordancia de claves; concordancia
de cuenta y lado; cobertura de órdenes previamente observadas; y situación temporal desconocida.
El precio anterior puede haber sido modificado antes de ejecutar: una diferencia no demuestra
por sí sola que el espacio de IDs sea distinto. Los desenlaces posteriores no serán filtro.

### Decisión y siguiente acto acotado

**Se pospone gasto de proveedor. Se selecciona primero comprobar el archivo propio existente.**
Esto es una selección metodológica; el acceso nuevo al VPS conserva el permiso operativo
específico del relevo §1. No se ha ejecutado ni se presenta esta selección como permiso de Manuel.

Propuesta concreta para ese permiso:

- Lectura del estado de `l3-poller.service` y `lighter-collector.service`, sin reiniciarlas,
  y metadatos de sus archivos en `/opt/l3-poller/data` y `/opt/lighter-collector/data`.
- Muestra fija **XPT, 2026-09-01 de 12:00 a 12:10 UTC**, posterior al anuncio de iceberg.
  No se sustituye símbolo ni intervalo si falta archivo o masa.
- Con los archivos correspondientes a esa hora, extraer solo los registros de XPT y el mapeo
  necesario para identificar su canal. No exportar registros de otros símbolos, ni consultar
  precios de referencia, markouts o campos de PnL.
- Comparar campos de ID de las órdenes del poller con los IDs maker de los trades WS
  (`ask_id` si `is_maker_ask`, `bid_id` en otro caso), conservando venue/mercado, cuenta,
  lado, tipo de evento y procedencia. Informar conteos, no tablas de órdenes ni resultados
  económicos. Separar coincidencia de ID de evidencia de observación previa.
- Máximo 60 s para la lectura/proceso de archivos y 256 MiB de entrada comprimida, con parada
  si se alcanza un límite. El recibo declarará muestra completa/parcial, ausencias, límites
  y hashes de los archivos efectivamente usados. Una muestra parcial, vacía o ambigua da
  **INDETERMINADO**, sin ampliar ni reintentar automáticamente.
- Cero endpoints de mercado, cero créditos y cero escrituras en el VPS. Herramienta y recibo
  locales; ninguna modificación de colectores, productor, pins o datos originales.

Una coincidencia acreditada en este carril propio no acreditaría la transformación de 0xArchive.
Tampoco esta muestra identifica iceberg o valida la población futura de F′. Su utilidad es decidir,
con evidencia existente, si el carril propio permite avanzar el enlace sin comprar otra sonda.
Si hace falta una corrida más larga, corresponderá a Claude bajo el reparto vigente.

Fuentes públicas capturadas para esta revisión, siete cuerpos con hashes y URLs:
`<USER_HOME>/OneDrive/Documents/Laboratorio/CONTRATOS_ENLACE_20260905/manifest.json`,
SHA-256 `f6a534b681e21e591fc40d3ee14f4433f8b0fa35792c9628dadf93bb71891374`.
Las capturas son de 19:17:52–19:17:54 UTC. La búsqueda de posibles copias de archivo en Laboratorio
no encontró coincidencias en las rutas accesibles; tuvo denegaciones en directorios temporales
antiguos y no acredita ausencia exhaustiva. No se tocaron sus permisos.

D4.2 sigue abierto. Esta revisión solo modifica este dictamen y su enlace de seguimiento;
no ejecutó código del proyecto, pruebas, acceso al VPS, consultas autenticadas o gasto.

## 7. Autorización operativa recibida — 2026-09-05

Manuel respondió **«AUTORIZO»** a la comprobación acotada del archivo propio, con la muestra XPT
2026-09-01 12:00–12:10 UTC y los límites del §6. El permiso está concedido; no debe volver a
solicitarse para ese mismo alcance. No autoriza una sonda de proveedor, ampliar la muestra ni
modificar servicios.

Dos precisiones sobre las condiciones posteriores de Claude:

- Copiar por scp las dos horas multiplexadas a disco local conservaría también registros de
  símbolos protegidos. La vía elegida es transmitir el archivo rotado al proceso local,
  descomprimir/filtrar en memoria y persistir únicamente la proyección de XPT y el recibo.
  Los registros descartados no se escriben a disco. Se mantiene el límite de lectura/proceso;
  no se descomprime ni analiza en el VPS ni se llama a endpoints de mercado.
- `infra/lighter_collector/replicate.sh:53–54` replica `lighter-data` y `testigos`; no incluye
  `/opt/l3-poller/data`. Esa versión no acredita una réplica completa de las dos fuentes en la
  almacenamiento externo. Tampoco la periodicidad de un timer prueba que un lote concreto esté disponible.

Preparado el lanzador local de **solo metadatos**
`<USER_HOME>/OneDrive/Documents/Laboratorio/xpt_preflight_20260905.py`: consulta propiedades
de las dos unidades y hace `lstat` de los archivos exactos de la hora autorizada. No abre sus
cuerpos. Exige host SSH explícito y confianza previa de su clave, modo BatchMode, una conexión,
timeout local 20 s; no reintenta ni cambia claves conocidas. Produce un recibo local de la
consulta y comprueba tipo de archivo, ambigüedad de formatos y tope de 256 MiB antes de leer
contenido. `--help` ejecutado con exit 0; **SSH y el script remoto no se han ejecutado**.

Falta identificar la conexión: no existe `<USER_HOME>/.ssh/config`; las búsquedas acotadas
en repo y workspace no aportaron un alias o usuario@host verificablemente asociado al VPS de
captura. Hay archivos de claves locales, cuyos contenidos no se han abierto. Se ha pedido a
Manuel el alias/destino y, si procede, la ruta de la clave; **es información de conexión, no
otro permiso**. No se ha probado un host por conjetura ni se ha declarado un resultado de datos.

El filtrado y la comprobación de IDs siguen pendientes de preparar/ejecutar tras ese preflight,
respetando la auditoría de Claude antes del lanzamiento del análisis. Hasta entonces no hay
recibo de medición ni conclusión nueva sobre identidad, cobertura o persistencia.

## 8. Conexión resuelta y preflight ejecutado — 2026-09-05

Manuel aportó el destino y la clave, contrastados con `docs/CONTINUAR_AQUI.md:119,166`:
`root@<VPS_IP>` y `<USER_HOME>/.ssh/<SSH_KEY>`. El dato sí estaba en el repo;
la búsqueda referida en el §7 no lo encontró. Ya no falta información de conexión.

Se ejecutó una sola consulta SSH de metadatos, 20:41:21–20:41:27 UTC, exit 0. Ambos servicios
están loaded/active/running. Existen las dos horas comprimidas: poller 2.018.462 bytes y colector
24.517.421 bytes; total 26.535.883 bytes (25,31 MiB), dentro del límite de 256 MiB. El poller
sin comprimir no existe. Archivos regulares y sin symlink según `lstat`.

Recibo: `<USER_HOME>/OneDrive/Documents/Laboratorio/XPT_ENLACE_20260905_PREFLIGHT_01/preflight.json`,
SHA-256 `c3593a0274eb1f19e3077eea900625e5ca0fc3aa380fe34a4fc1c8aee5bb7637`.
No se abrió ningún cuerpo, no se tocó `ingest.service` ni se reinició ningún servicio.
El resultado es **METADATA_AVAILABLE**, no evidencia de cobertura ni concordancia de IDs.

El filtro y los conteos ya están implementados fuera del árbol de producción y entregados en
`docs/PARA_CODE_2026-09-05_XPT_ENLACE_ARCHIVO.md`, con hashes, alcance, límites y comando único.
Evidencia local: **11 passed in 0.06s**, solo sintéticos; ninguna suite del proyecto.
Pendiente la auditoría independiente de Claude antes de abrir los cuerpos, conforme al reparto
acordado. La autorización de Manuel sigue vigente y no debe pedirse otra vez.

## 9. Lectura única XPT terminada — 2026-09-06

Recibida y leída la auditoría independiente de Claude, sin defectos que corregir; hashes
coincidentes. Se ejecutó una vez el comando del relevo, sin repetir pruebas ni preflight.
**INDETERMINADO_MASA**, 17,672 s: 109 snapshots L3 y 1.125 órdenes distintas, pero ningún frame
de trades admitido por el filtro XPT (`trade:147`) en [12:00,12:10). Ambos archivos se procesaron
hasta EOF. No es evidencia de cero negociación del mercado, ni de incompatibilidad de IDs.

Resultado detallado y recibo primario con hashes en
`RESULTADO_MESA_2026-09-06_XPT_ENLACE_ARCHIVO.md`. El alias textual `order_id=order_index`
concuerda en 9.668 observaciones L3, pero **el enlace ejecución–orden y su cobertura previa siguen
sin medirse**. Se corrige documentalmente el P2 de Claude: `timestamp[1]` es el extremo inferior
de la tupla `(unidad,inferior,superior)`; no hubo cambio de código ni trades seleccionados.

Corrida cerrada sin reintento, ampliación, gasto ni cambio de servicios. Solo se conservó el recibo
agregado; ningún cuerpo ni fila. Pendiente revisión de Claude sobre el resultado; D4.2 sigue abierto.
