# Mesa · decisión de acceso histórico LIT y secuencia I5 — 2026-09-06

## Decisión recibida

Manuel declara: **«He decidido que voy a pagar para los datos de lit»**, en el contexto de
contratar un mes de 0xArchive Build por el precio publicado de 49 USD/mes. Se registra su
decisión de asumir ese coste para acceder al histórico de LIT. **No consta todavía que el
plan esté activado**. La compra la realiza Manuel; esta anotación no afirma pago, acceso
comprobado, contratación anual ni firma de F′.

Se ha solicitado únicamente el estado de activación y si se trata de la misma cuenta que
usa la API existente; no otro permiso para la compra decidida. No se han abierto claves,
iniciado pagos ni realizado consultas autenticadas durante esta revisión.

## Condiciones comprobadas hoy y correcciones al argumento comercial

La [tarifa oficial](https://0xarchive.io/pricing) publica Build mensual a **49 USD**, **80 millones
de créditos/mes** y acceso histórico completo dentro del archivo retenido. El
[changelog del 31-08](https://0xarchive.io/changelog) confirma que la ventana móvil de 30 días
afecta a Free y que Build conserva acceso al histórico retenido. Esto respalda cambiar el plan
para retirar la restricción observada en el 403, no garantiza la integridad de cada día de LIT.

**No se ratifican «la compra más rentable del programa», «unos seis mil créditos bastan» ni
«un mes basta para acabar».** Son valoraciones o extrapolaciones, no presupuestos medidos.
El propio `ENCARGO_REDERIVACION_I5.md`, §4, declara desconocidos el coste diario exacto del L3
paginado, el consumo de trades CHD y sus condiciones de acceso. La
[tarifa por filas](https://docs.0xarchive.io/core-concepts/credits) no mide cuántas filas/páginas
necesita esta reconstrucción ni cubre a los otros proveedores. Estas salvedades ya estaban en
`RESULTADO_MESA_2026-09-05_I5_ETAPA0.md` y permanecen vigentes tras la decisión de compra.

## Secuencia adoptada para I5

1. **Activación de Build en la cuenta correcta.** Pendiente de confirmación de Manuel. La
   decisión de contratar no se sustituye por una comprobación repetida contra Free.
2. **Nueva etapa 0 bajo el cambio de acceso**, con el mismo alcance acotado: saldo/plan, una
   sola página `limit=1` de LIT del 2026-03-06 y saldo posterior; tope 80 créditos, sin
   paginación, ampliación ni reintento. Recibos y marcadores nuevos, conservando íntegros los
   del 05-09. Un 200 válido no vacío acredita acceso a esa página, no cobertura de los 79 días;
   un error no acredita ausencia. La finalidad de esta nueva consulta es comprobar el plan
   cambiado; la sonda anterior no se borra ni se considera fallida por haberse repetido.
3. **Preparar la etapa 1 de ocho días**, con selección previa, versiones de la receta,
   insumos identificados, salida separada y presupuesto operativo concreto. Codex implementa;
   Claude audita y ejecuta la rederivación larga. La aprobación metodológica D1 está emitida:
   no se vuelve a consultar si cabe el diagnóstico retrospectivo. Esa decisión, por sí sola,
   no era una orden ilimitada de descargas, de gasto en CHD o de ejecución de 79 días.
4. **Verificar reproducción y atribuir discrepancias antes de ampliar a los otros 71 días.**
   El núcleo actual contiene cambios posteriores al decisivo (I2/I7, entre otros); igualdad
   entre dos consumidores actuales no demuestra igualdad con la receta de julio. Una
   discrepancia debe separarse en versión, inputs, cobertura y defecto antes de declarar
   «el hallazgo estaba mal por otra razón». Se conserva el decisivo original sin sobrescribir.
5. **Etapas 2–3:** tras ese contraste, completar los días restantes y ejecutar I5 y los
   diagnósticos acordados. No hay un resultado histórico nuevo ni una corrida en marcha hoy.

El trabajo conserva la etiqueta **diagnóstico retrospectivo post hoc**. I5 cuantifica una
sensibilidad de admisión; no certifica fills verdaderos ni elimina todos los usos de información
posterior. En particular, el núcleo anota el instante del primer through y descarta el instante
del at: reclasificar el flag no reconstruye por sí solo otro tiempo de ejecución. Tampoco
soluciona la confusión de lado/basis, la generalización o los defectos de diseño del estudio.

## Campos y horizontes de la reconstrucción

Se acepta preparar la persistencia de `thr_con_at`, precio de la orden y referencia inicial
con su timestamp, y una familia de horizontes **fijada antes de la nueva lectura**, como pide
el encargo. Hay que definir qué significa `ref_t` y cómo se elige la referencia previa, y
preservar los tiempos at/through necesarios para distinguir diagnósticos temporales.

Reutilizar los mismos crudos puede evitar nuevas descargas **si cubren los horizontes y márgenes
requeridos**. No equivale a coste total cero: quedan implementación, validación, CPU y almacenamiento.
Más horizontes no crean más días independientes ni resuelven automáticamente la falta de potencia.
La reconstrucción histórica y las extensiones diagnósticas se etiquetarán por separado.

## XPT: observaciones aceptadas con alcance preciso

La corrida XPT ya terminó y **no se amplía** con esta decisión de compra de LIT. El resultado
explicita que cero frames admitidos no prueba cero negociación. Un contador por canal puede
documentar mensajes recibidos y ayudar a diagnosticar enrutamiento; que haya L2 de XPT no
certifica por sí solo que el canal de trades esté sano o completo. Tampoco demuestra la
ausencia de operaciones que no llegaron a nuestro colector.

Las intensidades de abril citadas por Claude no se han verificado aquí y no se trasladan como
expectativas ni pruebas de rareza para septiembre. Una hora sin trades seleccionados tampoco
bastaría por sí sola para declarar a XPT demasiado fino o seleccionar BRENTOIL automáticamente.

**Poller:** `infra/l3_poller/l3_poller.py:114–133` ejecuta `zstd -19 -T1` de forma síncrona al
rotar, antes de continuar el bucle de consultas (`:176–192`). Mientras esa compresión está
activa, ese poller no inicia nuevos polls. Es un mecanismo de pausa comprobado por código.
El recibo XPT mide 59,330317607 s hasta el primer snapshot seleccionado de esa hora; sin medir
la compresión o consultar evidencia temporal específica, **no se atribuye toda esa duración
a ese mecanismo ni se generaliza a «un minuto perdido en cada hora»**.

La campaña L existente mide fuentes 0xArchive/CHD/referencia; el poller propio no es
automáticamente su fuente. Su pausa debe considerarse si el diseño final utiliza esa captura,
sin confundirla con una medida de la maduración L. Se anota en ledger, sin parchear, desplegar
ni reiniciar la captura viva.

## Estado de esta entrega

Decisión registrada; condiciones públicas comprobadas; contrato y código leídos. **Sin compra
ejecutada por Codex, llamadas autenticadas, lecturas de datos, pruebas, commits, push o CI.**
Se mantiene el STOP y las decisiones de F′. La siguiente acción operativa es la nueva etapa 0
cuando se confirme la activación; XPT permanece cerrado en el alcance ya ejecutado.

## Seguimiento del 06-09: cuenta activa, etapa 0 terminada y mudanza

Manuel y Code confirmaron Build en otra cuenta, 80 millones de créditos; su clave vigente
está en `<USER_HOME>/Desktop/<KEY_DIR>/<KEY_FILE>`. La Free queda como default del eco.
Quedan superadas las menciones anteriores a activación pendiente; se conserva el texto fechado.

Codex ejecutó una única página de LIT del 06-03: **INDICIO**, HTTP 200, una fila; saldo −1 y
cabecera 10, conservados sin conciliación inventada. Una invocación previa solo consultó saldo
y se detuvo por una suposición errónea de Codex sobre el campo de plan, corregida antes de pedir
datos. Recibos y detalles en `RESULTADO_MESA_2026-09-06_I5_BUILD.md`. No repetir la etapa 0.

`PARA_CODE_2026-09-06_I5_CENSO.md` resuelve la propuesta posterior: censo de 149 celdas gastadas
LIT/DOGE con resoluciones separadas, preparación de custodia del histórico completo sin recorte
financiero, muestra de ocho días fijada antes del censo y auditoría/ejecución larga por Code.
El censo está implementado y probado en local, todavía sin ejecución real ni auditoría de Code.
El productor de rederivación será el tramo siguiente. XPT de proveedor se aplaza tras el primer
contraste de ocho días; D1 científico sigue circunscrito a LIT y F′ continúa abierto.

Laboratorio se trasladó a `<USER_HOME>/Desktop/Laboratorio`. Se leyó el relevo completo de
Code y se verificaron las copias de recibos usadas en este expediente. Las nuevas salidas se
escriben allí; las rutas dentro de recibos históricos no se reescriben. STOP, freezes y pins
siguen vigentes; sin commit, push ni CI.

## Seguimiento posterior del 06-09: censo terminado, descarga preparada

Code completó el censo en dos tramos, 149 celdas con ambas presencias y metadatos válidos,
298 créditos. La autorización de custodia ya concretada se instrumenta en
`PARA_CODE_2026-09-06_I5_DESCARGA_L3.md`: 298 recorridos L3 (checkpoint/tick), sin recorte por
coste, inventario completo de huecos y continuación explícita que conserva lo válido.
Codex implementó y verificó con 31 focales; Code audita antes de ejecutar la descarga larga.
Quedan superadas las menciones a censo pendiente; sus resultados no equivalen a descarga
completa ni a I5 calculado. No se requiere una nueva autorización del propietario dentro
de este alcance. Productor de ocho días y contraste de reproducción siguen pendientes.

## Seguimiento de auditoría: A/B antes de la continuación tick

La auditoría de Code no encuentra defectos de corrección, pero detiene la pasada única sin
ejecutarla. La mesa adopta A=checkpoint de las 149 celdas y B=tick LIT 06-03, índice 70,
tras A satisfactoria. Codex concreta en `PARA_CODE_2026-09-06_I5_DESCARGA_ETAPAS.md`, con
selectores fijados, páginas de 1.000, LIT primero y reserva 50 GiB; 37 focales verdes.
Code revisa el cambio y ejecuta A/B con el permiso vigente. La continuación C requiere
dimensionamiento con B y almacenamiento; la máxima resolución no se sustituye por defecto.
Se corrige la extrapolación de créditos de tick-L2 de julio a snapshots tick-L3; no prueba
el volumen alegado. No se han descargado datos nuevos ni medido I5 en este incremento.

## Seguimiento del 07-09: A/B cerradas; C pendiente y productor como prioridad

Code ejecutó A y B, 150 créditos combinados. La mesa contrastó recibos y el par LIT 06-03:
checkpoint y tick sirven los mismos datos, distintos solo en request_id. Se acredita ese
par, no máxima resolución custodiada para toda la ventana. No se lanza C ni nuevas sondas
ahora; LIT 01-09 propuesto está protegido y requiere cometido D3 propio antes de acceder.

Entrada L3 de ocho días implementada y verificada con 11 focales; faltan 16 insumos diarios
CHD acreditados y el productor forense con recetas diferenciadas. Estado y anclas en
`PARA_CODE_2026-09-07_I5_PRODUCTOR_INSUMOS.md`. No se vuelve a pedir permiso metodológico D1
ni se interpreta disponibilidad L3 como reproducción o I5 terminados. STOP y freezes vigentes.

## Seguimiento del 07-09: lector aceptado y adquisición CHD concretada

Code validó el lector sobre los ocho libros reales y no encontró copia local de los
dieciséis insumos diarios de trades. La mesa acepta el cierre del lector y concreta la
readquisición en `PARA_CODE_2026-09-07_I5_CHD_CUSTODIA.md`: Code audita el nuevo instrumento,
ejecuta acceso mínimo (JWT y dos horas fijas del 06-03) y, si queda acreditado, las 382 horas
restantes. Se reutilizan las dos iniciales, sin nuevos símbolos o fechas ni reintentos
automáticos. Esta secuencia usa la autorización histórica vigente; no precisa otra
autorización de Manuel. Los fallos o faltantes se documentan, sin ampliar o sustituir datos.

Codex entregó 40 focales y plan sin red. No ha usado la clave CHD o descargado trades; la
auditoría/ejecución real, el productor, la reproducción y el diagnóstico I5 siguen pendientes.

## Seguimiento del 07-09: custodia cerrada y orden de reproducción local

CHD terminó con 381 ficheros custodiados de 384 claves; Code auditó y ejecutó ambos
tramos. Se dispone conservar el 29-06 con 21/24 horas Lighter, tres 404 explícitos,
sin nueva consulta o relleno, y los bordes observados en las claves horarias originales.
La igualdad o diferencia del NPZ no identifica por sí sola las horas que tuvo julio;
el esquema histórico no guardaba un conteo de trades de entrada.

La mesa concreta la extensión antes de leer resultados reales: referencia inicial
`ref_t`/`ref_t_ms` = precio/tiempo del último trade Binance estrictamente anterior a
`t_fill`, a no más de 500 ms, o NaN/-1; familia adicional fija 1,5,10,25,60 segundos
con fórmula y tolerancia histórica. Se guardan precio de orden, cantidad visible
imputada, id, límites de intervalo, posición y primera aparición, ambos tiempos
at/through y flag, sin alterar los ocho campos históricos. Son campos diagnósticos
post hoc, no ampliación de la familia decisiva ni conversión del trade en mid.

Productor implementado, 32 focales nuevos verdes, plan sin cuerpos económicos abiertos.
Se ordena a Code auditar el incremento y ejecutar una vez la reproducción de las ocho
fechas ya fijadas según `PARA_CODE_2026-09-07_I5_REPRODUCCION_OCHO.md`. No se requiere
otra autorización del propietario. La comparación y atribución preceden al resto de
los 79 días y a I5. No se amplían muestra, acceso protegido o sondas por inferencia.
STOP/freezes/pins permanecen; ninguna reproducción real o prueba I5 declarada terminada.

## Seguimiento posterior del 07-09: reproducción cerrada; 71 días restantes

Code ejecutó la reproducción una vez y la mesa acepta las 64 comparaciones numéricas
exactas, con las correcciones de alcance de §6 de su informe. Se cierra la etapa de
ocho días; no se repite. Los tres 404 del 29-06 permanecen sin nueva consulta.

Se fija `ESPEC_MESA_2026-09-07_D1_79_DIAS.md`: diagnóstico retrospectivo, admisión sola
como contraste principal y cambios de reloj, vol, terciles y validación separados.
Esa especificación no convierte D1 en confirmatorio ni levanta el defecto de referencia.

La mesa concreta el siguiente tramo autorizado en `PARA_CODE_2026-09-07_I5_CHD_RESTO_71.md`:
Code audita la herramienta nueva y ejecuta una vez 3.408 claves CHD de las 71 fechas
restantes, reutilizando la custodia de las ocho anteriores y sin pedir L3 ya disponible.
Plan fijado por hash, máximo inicial 6.817 HTTP, JWT sin renovación automática y parada
con custodia preservada. Inventario nuevo antes de productor restante/análisis; no se
ejecuta D1 sobre las ocho como sustituto de los 79. No hace falta otra autorización
metodológica de Manuel. Productor restante y analizador siguen pendientes de esa entrega.
