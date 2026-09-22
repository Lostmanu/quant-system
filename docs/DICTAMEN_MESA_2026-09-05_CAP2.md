# Mesa → Manuel y Claude · decisiones D1–D4 del capítulo 2

2026-09-05. Dictamen de Codex en el papel de mesa asignado expresamente por Manuel en esta
conversación. Responde a `PARA_LA_MESA_2026-09-05_DECISIONES_CAP2.md`, leído completo.
No es una nueva auditoría independiente del código que Codex implementó en M-15 ni una firma
del propietario sobre un freeze. M-15 permanece cerrado en local.

Base comprobada: HEAD `7df52803b6db3777b23be85409ef998f879909a8`, rama `codex/wip-m12.20`.
SHA-256 del dossier recibido: `9002b923819cd3e05d7015a617a4ddc2ff404dd672b9618e07f2facc9694994e`.
Se verificaron documentos y código por lectura. No se consultó red, proveedor, NPZ ni observaciones
de mercado, ni se ejecutaron pruebas. Se conserva el dossier recibido sin editar.

## D1 · Resuelta: sí al diagnóstico retrospectivo; no a cambiar el veredicto congelado

Apruebo metodológicamente una comprobación de auditoría, nueva y fechada, sobre los 79 días de LIT
del 2026-03-06 al 2026-06-29: reconstruir la clasificación y medir la sensibilidad a incluir
through-con-at como fill. Su etiqueta será **diagnóstico retrospectivo post hoc**.

No se convierte en una prueba confirmatoria pre-registrada para aquellos 79 días ni modifica la
regla que produjo su veredicto. La obligación I5 para el eco sigue pendiente y exige su propio
diseño prospectivo. Esta distinción es la resolución de mesa de hoy; no se atribuye al prereg una
autorización retrospectiva que no contiene.

El diagnóstico podrá evaluar el sesgo señalado, pero no rehabilitar por sí solo el hallazgo ni
recalibrar automáticamente el gate B. Persisten los demás problemas del estimando, de inferencia y
de generalización. No se cambia el criterio congelado de admisión como si fuera un bug de M-15.

Fuentes: `PREREG_ECO_LIT_INSUMOS.md:3-7,54-61`; `ENCARGO_REDERIVACION_I5.md:112-136`;
`AUDITORIA_QUANT_REVIEWER_2026-08-24.md`, §§3–4.

## D2 · Etapa 0 seleccionada como siguiente acto; permiso operativo aún necesario

Apruebo la finalidad y el alcance de la sonda histórica: LIT, día UTC **2026-03-06**, endpoint
`l3orderbook/LIT/history`, solo disponibilidad y conteo de filas. Se registra el consumo observado
y se para al terminar. No autoriza las etapas 1–3, otra fecha, markouts ni una campaña.

Corrijo dos sobreafirmaciones del dossier:

- Una respuesta no vacía solo prueba disponibilidad en la consulta de ese día. No acredita los
  otros 78 días, los trades de CHD, la referencia ni la reproducibilidad de la derivación.
- Una respuesta válida vacía activa la parada del encargo histórico tal como está definido.
  No demuestra que el eco futuro sea inviable ni elimina las decisiones sobre él. Un error de
  red, cuota, permisos o esquema no equivale a ausencia de datos; también se para y se informa.

La estimación de 30–80 créditos no es una tarifa comprobada. Propongo a Manuel una autorización
operativa separada: consulta de saldo y coste, más la sonda con **tope total de 80 créditos**, sin
ampliaciones ni reintentos automáticos. Si no puede garantizarse ese tope antes de la petición
facturable, no se lanza y se devuelve el presupuesto. Un conteo truncado por presupuesto se
rotula parcial; no se presenta como el total del día.

Esta aprobación metodológica no sustituye el permiso específico de red/sonda/gasto que Manuel
mantuvo en el relevo operativo, §1. No consta concedido en esta conversación y no se ejecuta aquí.

Fuente: `ENCARGO_REDERIVACION_I5.md:46-77,136`.

## D3 · Resuelta la interpretación de «pedir» en la Regla Cero

En el texto citado, el objeto de «pedir, computar o citar» es **un primer momento del markout**.
La adquisición y custodia de crudos no son por sí mismas esa lectura. Son metodológicamente
admisibles para un cometido aprobado de captura o medición ciega al resultado; no se extiende esa
admisibilidad a calcular, inspeccionar o divulgar medias, sumas, signos, t o IC de markout, por
ningún estrato u horizonte del conjunto protegido.

Se mantienen las ventanas protegidas, la lectura única y los contratos vigentes. Esta resolución
no es una orden de descarga masiva, no habilita el productor de markouts, no modifica guardias ni
levanta el STOP de producción. Cada ejecución conserva su alcance y autorización operativa.

Para la medición de L, el contrato existente de conteos y hashes del material fuente sirve a esta
separación; no se necesita inventar otra plataforma de controles. El permiso conceptual D3 es
pertinente cuando la muestra de L cae en las fechas protegidas.

Fuentes: `MESA_ECO_PROMPT.md:19-26`; `PARA_LA_MESA_ECO_ESTRUCTURA.md:140-143`;
`qs/analysis/eco_medir_L.py:7-20,642-674` (rutas `qs/` relativas a `quant-system-ingesta/`).

## D4 · Secuencia corregida; no se fija cap ni se aprueba F′

El dossier debe corregir dos dependencias antes de servir como orden de campaña:

1. **L no requiere todo el tramo D0_LIT → hoy.** `derivar_muestra(inicio)` fija cuatro días LIT y
   cuatro sesiones WTI: 20 celdas, ocho escalones por celda, hasta +168 h. El instrumento mide
   cambios del material según su edad de captura. Descargar hoy un histórico entero no sustituye
   esas observaciones temporales. D3 precede a la captura protegida por el alcance de la muestra,
   no por una dependencia de todo el archivo histórico.
2. **Push/CI sí son dependencias de la acreditación operacional de L.** El código exige la cadena
   `instrumento → R → CI(R) → A_R → O_i → CI(O_i) → A_Oi → P`, anclada en la historia first-parent
   del remoto canónico. No basta medir localmente y dejar la publicación para un futuro indefinido.
   Esto no autoriza publicar los 27 commits actuales ni iniciar CI por inferencia.

Orden que adopta la mesa:

1. Verificación pública fechada de Season 3 y fees, y delimitación de qué régimen puede estudiarse.
   No se da por hecha ni se infiere de documentos de julio/agosto. Se ejecutará con permiso de red.
2. Definir el objeto científico de F′: hipótesis y falsación, estimando que trate los sesgos de
   selección/lado/basis, universo y horizontes. No se acepta recongelar la receta confundida con
   una fecha nueva. No se rebajan umbrales para acomodar un resultado conocido.
3. Preparar el plan concreto de L con el instrumento existente: muestra y compromiso previos,
   humo requerido sobre dato gastado, cronograma real de las capturas y su cadena de publicación/
   atestación. Obtener las autorizaciones específicas de ejecución, presupuesto y push/CI antes
   de la campaña. No se reabren suites o barridos para redactar ese plan.
4. Medir L con el protocolo autorizado y establecer un sustento explícito para T17 y para los
   tiempos de auditoría. Los «~9 días» del borrador no son una duración garantizada desde hoy.
5. Resolver conjuntamente `D0 + 56 días ≤ pin_nuevo` y `D0_LIT + L + T17 ≤ CAP_nuevo`, con las
   restricciones de régimen justificadas entonces. La referencia histórica a diciembre y a
   unlocks debe verificarse externamente; no se ratifica aquí como hecho actual.
6. Cerrar el prereg y someter F′ y su activación al acto de firma correspondiente. P0-6 y los pins
   LIT no se activan por este dictamen. Hasta entonces permanece vigente el STOP.

La ventana A2 nueva ya no cabe bajo el pin actual: D0 máximo 2026-08-05, no 2026-09-30.
La regla del cap LIT es distinta y no se predeclara su resultado.

Fuentes: `qs/analysis/eco_medir_L.py:70-101,720-750,765-824`;
`qs/analysis/eco_gate_b.py:49,92,405,762,1488`;
`C_SPEC_V7.md:136-138`; `DECISION_2026-08-24_CALENDARIO.md`, §§8–9;
`AUDITORIA_QUANT_REVIEWER_2026-08-24.md`, párrafo final.

## Entrega y siguiente paso

Las decisiones metodológicas D1 y D3 quedan emitidas; D2 queda acotada y D4 ordenada. El siguiente
permiso que se solicita a Manuel es únicamente el de red/saldo/coste y etapa 0 descrito en D2.
No se solicita un permiso global para F′, la campaña ni la rederivación completa.

Claude puede incorporar las correcciones documentales sin barrido. Codex implementará únicamente
la preparación técnica que resulte necesaria para el acto autorizado; Claude la auditará. No hay
motivo demostrado para editar ahora código productivo. El dossier original y los documentos
históricos se conservan; este dictamen no debe presentarse como una firma retroactiva de ellos.

## Seguimiento posterior a este dictamen — 2026-09-05

Manuel concedió el permiso operativo D2 con «autorizo». Se completó la consulta acotada de saldo,
coste y una página mínima. Resultado: HTTP 403 por límite de antigüedad del plan, INDETERMINADO
sobre retención; sin reintento. Ver `RESULTADO_MESA_2026-09-05_I5_ETAPA0.md` para recibo,
discrepancia de consumo y corrección del antecedente: ya hubo una sonda atestada el 25-08,
omitida en el dossier que motivó este dictamen. Queda superada la frase de D2 sobre permiso aún
no concedido; no se modifica retroactivamente el texto original de la decisión.

## Seguimiento de D4.1 — verificación pública completada el 2026-09-05

Con la autorización expresa de Manuel «SI, AUTORIZO», la mesa comprobó Season 3 y fees en
fuentes públicas. Ver `VERIFICACION_MESA_2026-09-05_LIGHTER_REGIMEN.md`: Season 3 de Core no
acreditada en las fuentes examinadas; puntos de Robinhood Chain activos y cambios de fees,
latencia y visibilidad de órdenes en agosto acreditados documentalmente. No se ratifica por
omisión la homogeneidad del eco. El siguiente trabajo de mesa es definir el objeto científico
de F′; no se ha fijado cap, activado campaña ni modificado un freeze.

## Avance de D4.2 — observabilidad y objeto científico, 2026-09-05

Se contrasta la valoración posterior de Claude con el código en
`DICTAMEN_MESA_2026-09-05_OBSERVABILIDAD_FPRIMA.md`. La mesa corrige la identificación de iceberg
mediante excesos trade/L2 y las exclusiones de efecto sobre cohorte, estimando y signo. Deja una
base de contraste de deriva lenta–reciente, neutralizada por lado y separada del nivel inicial,
condicionada a identificar ejecuciones y persistencia previa. No encarga un detector ni modifica
la receta histórica. D4.2 sigue abierto hasta resolver observabilidad y cerrar su especificación.

La revisión posterior de `AUDITORIA_CODE_2026-09-05_ENLACE_EJECUCION_ORDEN.md` queda en el §6 del
dictamen de observabilidad: alias textual de `order_index` documentado, despliegue histórico del
poller registrado y corrección de unidades. Se rechaza usar una tasa de matches cercana a uno
como prueba de identidad. Se selecciona una comprobación acotada del archivo propio XPT antes
de gastar en proveedor, pendiente de permiso operativo de VPS; no se ha lanzado.

**Seguimiento:** Manuel ha concedido ese permiso con «AUTORIZO». El §7 del dictamen de
observabilidad registra el alcance y la preparación. Falta el destino SSH verificable de la
máquina de captura, solicitado como dato de conexión; no falta autorización. No se ha abierto
el archivo ni ejecutado la comprobación.

**Seguimiento posterior:** conexión resuelta por `CONTINUAR_AQUI.md:119,166`. Preflight SSH
ejecutado una vez: ambos servicios activos y las dos horas comprimidas disponibles, 25,31 MiB
en total. Solo metadatos, sin abrir cuerpos. El §8 del dictamen de observabilidad y
`PARA_CODE_2026-09-05_XPT_ENLACE_ARCHIVO.md` registran el recibo y el instrumento preparado
(11 focales sintéticos verdes). Falta la auditoría de Claude antes de la lectura; no falta permiso.

**Seguimiento 2026-09-06:** auditoría recibida sin defectos y lectura única ejecutada.
`RESULTADO_MESA_2026-09-06_XPT_ENLACE_ARCHIVO.md`: **INDETERMINADO_MASA**, 17,672 s;
109 snapshots L3 / 1.125 órdenes distintas, ningún frame de trades admitido en la ventana XPT.
No permite contrastar ejecución–orden; no demuestra ausencia de negociación. Sin reintento ni
ampliación; D4.2 permanece abierto, pendiente revisión del recibo por Claude.

**Decisión 2026-09-06:** Manuel decide pagar acceso histórico LIT mediante Build. Registrado en
`DECISION_MESA_2026-09-06_ACCESO_LIT_I5.md` y en LEDGER; activación todavía no confirmada.
Siguiente acto: nueva etapa 0 mínima bajo el cambio de plan, conservando el recibo del 05-09.
No se ratifica el coste total de ~6.000 créditos ni se interpreta D1 como orden operativa
ilimitada de las etapas 1–3. XPT no se amplía por esta decisión.

**Seguimiento 06-09, después de activar Build:** etapa 0 terminada con **INDICIO** y una sola
página de mercado; ver `RESULTADO_MESA_2026-09-06_I5_BUILD.md`. El nuevo alcance de censo de
149 celdas LIT/DOGE y la muestra previa de ocho días están en
`PARA_CODE_2026-09-06_I5_CENSO.md`, preparado para auditoría y ejecución de Code. D1 conserva
su carácter retrospectivo y su objeto LIT; no se modifica F′. Nueva raíz operativa de recibos:
`<USER_HOME>/Desktop/Laboratorio`, fuera de OneDrive.
