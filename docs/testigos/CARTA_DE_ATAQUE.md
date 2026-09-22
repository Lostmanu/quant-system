# CARTA DE ATAQUE — el steelman contra este programa (2026-07-05)

Este documento lo escribe el propio programa ANTES de que lo escriba un tercero. Regla de redacción:
cada ataque en su versión MÁS fuerte, sin pajas; debajo, la respuesta real si existe, y un **"sin
respuesta hoy"** donde no. Un lector hostil debería encontrar aquí todas sus objeciones ya formuladas —
y alguna que no se le había ocurrido.

---

## A1. Forking paths a nivel de PROGRAMA (el ataque más fuerte)

**Ataque:** cada paso está pre-registrado, pero el PROGRAMA entero es una búsqueda secuencial: 6 frentes
en Binance (todos negativos), Hyperliquid (muere en capa 1), Lighter taker (muerto), Lighter maker capa 1
→ capa 2 → piloto → atlas → confirmación. El "primer PASA" y la "flor" llegan tras ~10 intentos. La flor
es el MÁXIMO de N búsquedas, y ningún BHY intra-familia corrige la selección ENTRE capítulos. Con 10
tiradas, encontrar una celda con t+6,7 en alguna parte no es milagro.

**Respuesta:** (a) el conteo exacto de intentos está en el LEDGER — este paquete lo declara para que el
lector aplique su propio haircut, que es lo único honesto cuando la corrección formal no existe; (b) la
flor NO nació de barrer celdas: la cohorte lenta era la hipótesis pre-registrada del piloto y el tercil
agitado era la celda pre-nombrada de la confirmación — la búsqueda fue de UNIVERSOS, no de
especificaciones dentro del dato; (c) la confirmación corrió en held-out virgen (149 símbolo-días no
tocados) y el eco de julio es forward puro. **Residuo sin respuesta hoy:** no existe un e-value de
programa que agregue la evidencia a través de capítulos; la defensa real es la replicación forward
pendiente, no una corrección estadística.

## A2. Un solo símbolo carga la replicación — y es el token del propio venue

**Ataque:** LIT lleva todo el peso (minoría estable t+3,05/t+10,83; +18,24 en agitado). LIT es el token
nativo de Lighter: incentivos del venue, flujo de farmers, market-making subvencionado — el "edge" podría
ser un subsidio disfrazado que muere con el programa de puntos. La generalización "clase paciente cobra
en la cola ancha" descansa en n=1 símbolo peculiar. **Y peor tras la errata A11: DOGE, el único
corroborador, se cae** — bajo N_eff su minoría estable es 25s NULO (t−0,05) y 5s marginal (t+2,16); el
"replica en AMBOS símbolos" era artefacto de un t iid. Queda n=1 de verdad.

**Respuesta:** declarado como cautela desde el día del piloto (LIT=token del venue, régimen peculiar a
examinar), y ahora SIN el colchón de DOGE — la errata endureció este ataque, no lo suavizó, y así queda
en el acta. **Residuo, más grande que ayer:** la réplica de habilidad fuera de ventana descansa
esencialmente en LIT solo. Si el edge de LIT es subsidio, el eco de julio post-cambios de régimen y el
colector (que mide CUALQUIER símbolo a 50ms, incluidos no-tokens del venue) son los únicos jueces. Hoy no
se puede distinguir subsidio-de-venue de habilidad-de-clase con el dato mirado, y el corroborador que
parecía existir no existía.

## A3. El 5s no acompañó — y sin el 5s esto puede ser beta, no habilidad

**Ataque:** la unanimidad de horizontes falló exactamente donde falla un artefacto: el markout a 25s en
un venue satélite puede ser reversión mecánica del basis (Lighter se desvía de Binance y vuelve), que un
maker pasivo cosecha SIN habilidad — y que desaparece neta de la volatilidad del basis. A 5s, donde la
selección adversa muerde de verdad, no hay nada significativo. El programa declara "el edge sobrevive en
agitado" cuando lo que sobrevive es el horizonte largo.

**Respuesta:** es la condena pendiente y está declarada como tal — el veredicto formal fue INCONCLUSO
precisamente porque la regla firmada no dejó decretar con un solo horizonte. Y el test de falsación
tiene NOMBRE, para que nadie dude de que el programa sabe dónde vive su verdugo: **markout condicional
a la desviación de basis en el instante del fill** — si el +18 se concentra en fills donde Lighter
entró desviado de Binance, es cosecha de basis; si es ortogonal a la desviación, no lo es. Más la
recomputación de la celda estrella por carril de prints propios (anotada en A5). Ambos, candidatos al
prereg de la apelación; el tick fino que los alimenta ya lo captura el colector a 50ms.
**Sin respuesta hoy; el instrumento y el test que responden están nombrados y el primero ya corre.**

## A4. Los "fills" son inferencias entre fotos separadas 2,9 minutos

**Ataque:** toda la cadena L3 (piloto, atlas, confirmación) infiere fills comparando snapshots a ~2,9
min: una orden que desaparece con print compatible se cuenta FILL; la cadencia hace invisible el 90% de
la vida intra-intervalo. Cancel+re-quote+fill de OTRO en el mismo precio se confunde con fill propio;
"lenta" (sobrevive ≥1 intervalo) es una cota grosera. El markout "realizado" es sobre eventos inferidos,
no confirmados por matching engine.

**Respuesta:** la cláusula de corroboración (sin print compatible = AMBIGUA, jamás fill) y las categorías
contadas (through/ambigua/inválido publicados por día) acotan el error en la dirección declarada
(falsos negativos, no falsos fills); el estimador de identidad se calibró con control positivo (BTC).
**Residuo real:** el sesgo de inferencia contra la verdad de stream no está CUANTIFICADO — cuantificarlo
es la primera tarea del colector certificado (mismo día, misma métrica, 50ms vs 2,9min).

## A5. La referencia Binance mezcla edge con basis

**Ataque:** los markouts se miden contra el mid de Binance (donde el símbolo está certificado por
ρ_5m≥0,95). Pero ρ se midió en ventanas ENTERAS: nada garantiza que el basis Lighter-Binance sea estable
DENTRO del tercil agitado — justo donde vive la celda estrella. DOGE certificó 0,9521 y 0,9641,
borderline dos veces. Si el basis respira con la vol, parte del "+18bps" es basis, no edge.

**Respuesta:** la regla del diapasón (todo umbral con su control positivo: BTC 0,9980) y el carril de
prints para los no certificados existen por esto. **Residuo:** el basis dinámico condicional-a-régimen no
está modelado. Mitigación disponible y barata: re-computar la celda estrella con markout contra prints
PROPIOS del venue (carril WTI) como robustez — pendiente, anotado para el prereg del eco.

## A6. El confound de supervivencia tiene una tercera cabeza, y sigue viva

**Ataque:** el decisivo mató la versión ENTRE-días (bootstrap: rotación mecánica) y la versión de
RÉGIMEN (tercil agitado POOLED positivo a 25s). Pero sobrevivir el intervalo de 2,9 min ya condiciona a
que no hubo barrido EN ese intervalo — la cohorte "lenta" está seleccionada intra-intervalo por
definición, y esa versión del confound opera a horizontes cortos… exactamente donde no hay decreto.

**Respuesta:** correcta y sin respuesta completa hoy — es la mejor objeción restante y la razón por la
que la condena pendiente es del 5s y no un fleco. El colector disuelve la selección (con stream continuo
la cohorte se define por tiempo real de vida, no por supervivencia entre fotos). **El programa declara:
la flor está fuera del banquillo por los cargos juzgados, no absuelta de los no juzgables con este
instrumento.**

**Refinamiento (auditoría A11, hallazgo N3 — la tercera cabeza ahora tiene MECANISMO):** la re-auditoría
independiente nombró una vía concreta del confound que ni la mesa ni yo habíamos aislado. En el differ de
cohortes (`pilot_observer.py:58`, idéntico en `confirm_runner.py:88`), una orden lenta que se llena
(print a su precio) en un intervalo que ADEMÁS contiene un print adverso (through, el precio barrió en
contra) se clasifica THROUGH — diagnóstico, EXCLUIDO de la cohorte de decisión — en vez de FILL. Como el
through correlaciona con la senda futura adversa de Binance, excluir esos casos **depura la cohorte
retenida de sus fills en momentos de movimiento en contra → sesga la media hacia positivo.** Es
selección sobre un correlato del outcome usando información intra-intervalo, y el decisivo la HEREDA
idéntica del piloto. Matices que la mantienen acotada (verificados adversarialmente, `INVIERTE=False`):
(a) es el SPEC CONGELADO — el prereg pre-declaró through como "diagnóstico que nunca decide", así que el
código es fiel, no un bug; (b) el subconjunto afectado (fill lento CON at Y through estrictos en el mismo
intervalo de 2,9 min) es minoría de una población ya fina; (c) re-incluir una minoría de eventos
negativos ENCOGE una media positiva, no la cruza a negativo de forma fiable; (d) no puede fabricar la
discrepancia 5s/25s. **Disposición: prueba de sensibilidad OBLIGATORIA (¿cuánto se mueve la media/t de
LIT si los through-con-at se re-cuentan como fill?) como enmienda fechada en el prereg del eco, ANTES de
correrlo — jamás retroactiva.** El colector la disuelve igual que a las otras cabezas.

## A7. El régimen no es estacionario y la ventana ya caducó

**Ataque:** todo lo medido es mar-jun 2026, pre-Season-3. Cuando el farming arranque (o los unlocks de
dic-2026), el flujo cambia de naturaleza. El edge medido puede haber muerto el día que se midió.

**Respuesta:** ventana de régimen congelada PRE-dato con fronteras nombradas; S3-recheck obligatorio en
cada freeze (corrió en los 3); el eco de julio es el test forward del régimen vigente. Esto no es
residuo sino diseño: ningún edge de microestructura se posee, se alquila — la pregunta operativa es la
velocidad de re-verificación, y la maquinaria la da (~300 créditos y horas por re-lectura).

## A8. La "verificación externa" es el mismo humano con dos sombreros

**Ataque:** la mesa es otro modelo hablado por el mismo operador. Sus priors fallaron el modal 3 veces en
días clave (registrado). Sin un tercero con incentivos independientes, todo el protocolo es
autodisciplina elaborada — impresionante, pero no auditoría.

**Respuesta:** cierto, y el LEDGER lo registra contra sí mismo (aciertos Y fallos de la mesa puntuados;
dos freezes DETENIDOS por regla propia; una auto-denuncia de colchón emocional en los priors). La
defensa no es negar el ataque sino este paquete: espejo + manifiesto + carta existen exactamente para
que el tercero real pueda llegar, verificar los hashes y re-derivar los números. La autodisciplina se
convierte en auditable; auditada será cuando alguien la audite.

## A9. Capacidad ridícula: aunque todo sea verdad, no paga

**Ataque:** el volumen lento total del hábitat es ~$288k/día ENTRE 266 wallets. La fracción capturable
por un entrante es un goteo; +15bps sobre un goteo son céntimos. El programa ha gastado meses de
ingeniería en un edge que, de existir, no paga ni el VPS.

**Respuesta:** existencia≠edge está escrito desde el día del piloto y capa 3 (tamaño, capacidad,
ejecución real) JAMÁS se corrió — a propósito: dimensionar antes de confirmar es la trampa clásica en
sentido inverso. El valor entregado a día de hoy se declara sin inflarse: una maquinaria de medición
validada, un mapa de dónde NO hay edge (que ahorró capital real), y UNA celda viva pendiente de
apelación. Si la apelación confirma y capa 3 da céntimos, el programa lo escribirá con la misma letra.

## A10. La fe en los vendors se auditó tarde y de forma desigual

**Ataque:** el canal orderbook de CHD-Lighter resultó INUTILIZABLE (88% de ventanas malas un día) y se
descubrió DESPUÉS de haber montado el capítulo encima. La certificación de Binance-CHD fue
spread-céntrica (fidelidad de spread vs sonda propia), no integral. ¿Cuántos veredictos de Cap 1
descansan en canales no certificados con la dureza que Lighter enseñó a exigir?

**Respuesta:** el orden histórico es el declarado: la dureza de certificación CRECIÓ con las lecciones
(Binance: spread-check |bias|<1% + guard de días corruptos + solape con sonda propia de 14 días; Lighter:
cadena de 4 oráculos, n≥2 días, y aún así el defecto se cazó ANTES de mirar informatividad con libro no
certificado — cero conclusiones se apoyaron en el canal malo). **Residuo:** los veredictos de Cap 1 son
robustos a la clase de defecto que Lighter enseñó (dropout/staleness) por FÍSICA, no por fe: el ruido
de medición en el regresor es errores-en-variables de manual — **ATENÚA hacia cero; no fabrica un
t=−26, lo esconde.** Un canal defectuoso podría haber ocultado un edge (falso negativo del programa,
pérdida nuestra), pero no pudo fabricar el veredicto negativo con esa magnitud. Es un argumento de
dirección del sesgo, no una re-certificación integral; se declara como tal.

## A11. La corrección de implementación por IA (añadido por exigencia de la mesa en su contrafirma)

**Ataque:** todo el código estadístico —N_eff, BHY, CPCV, el differ de cohortes— lo escribieron LLMs
dirigidos por un ingeniero junior. El propio catálogo del programa documenta media docena de
confabulaciones cazadas internamente; ¿quién caza las que no se cazaron? Un `effective_n_autocorr`
plausible pero sutilmente mal pasaría todos los freezes del mundo: el rastro documental prueba
disciplina de PROCESO, no corrección de IMPLEMENTACIÓN.

**Respuesta:** tres capas, en orden de fuerza creciente: (a) suites de tests por instrumento (~350
tests, incluidos los que cazaron los bugs documentados); (b) controles positivos obligatorios — la
regla del diapasón exige que todo umbral y todo estimador demuestre que ENCUENTRA lo que existe (BTC
ρ_5m=0,9980) antes de usarse donde no se sabe; (c) la más fuerte: **calibración contra verdad
conocida de extremo a extremo** — el estimador hermano-de-trades reproduciendo el veredicto canónico
de Binance 6/6 con t−4,11, y el disparo contrarian dando t=−26 coherente con costes medidos contra
sonda propia. Eso es evidencia de corrección del pipeline COMPLETO, no de estilo del código.
**Residuo, sin anestesia: no existe auditoría externa línea a línea de este código. El espejo saneado
existe precisamente para que pueda existir** — este ataque es, literalmente, la invitación.

**ACTUALIZACIÓN 2026-07-05 — la invitación se aceptó a medias, y cazó algo.** Se ejecutó la auditoría
interna en DOS capas: la mesa leyó las 1.104 líneas, y 5 agentes de contexto fresco la re-auditaron
desconfiando de la mesa (workflow `wf_071d788c`). Encontraron **una errata de FUERZA real (H1): §5
computaba su t-stat como iid en vez de N_eff, inflando ~7-30× dos números publicados.** Corregida sobre
los mismos datos (LIT sobrevive sólido t+3,05/t+10,83; DOGE se cae a nulo — ver A2). La re-auditoría
independiente además cazó bugs que la mesa se dejó (N1 `trailing_vol`, N3 la 3ª cabeza de A6), mató
adversarialmente 4 falsos "inversores", **y corrigió a la propia mesa: la mesa entregó H1 como "errata de
fuerza, la dirección aguanta en ambos símbolos"; el pase independiente demostró que era peor — DOGE 25s no
tenía solo el t inflado, su media misma era un espejismo de concentración (+55 fill vs −3,41 día-a-día) →
el corroborador no existe.** La mesa acertó el bug y subestimó su consecuencia; el acta lo registra así.

**LÍMITE DURO de lo que esta ronda demuestra (para que no se sobreinterprete):** los agentes frescos matan
la correlación de CONVERSACIÓN (no arrastran el marco emocional, no están enamorados de la flor) — pero
comparten mi ARQUITECTURA. Un modo de fallo que viva en el sustrato y no en el contexto lo cometeríamos
los diez a la vez, y el consenso SE SENTIRÍA como validación siendo un punto ciego coordinado. **Confundir
"nueve lecturas de IA que concuerdan" con "auditoría independiente" es exactamente el A8 de esta carta con
un disfraz más sofisticado.** Lo que la ronda demuestra es más modesto y más real, verificable en el diff:
que el protocolo PUBLICA sus errores en vez de enterrarlos. La corrección del código es un HECHO; la
ausencia de OTROS errores de la misma clase que los diez compartimos, NO — eso solo lo cierra el tercero
humano con el espejo. El residuo de A11 mejora ("auditado internamente en dos capas, con una errata cazada
y publicada con el número viejo al lado"); no se cierra.

---

## Lo que esta carta NO ataca (porque no hay grieta que el programa conozca)

El pipeline de p-hacking clásico: parámetros congelados pre-dato con hash de git, held-out gastado una
sola vez y declarado, familias BHY pre-nombradas, reglas de veredicto escritas antes de mirar, negativos
publicados con el mismo detalle que positivos, y dinero gastado: $0. Si hay una grieta ahí, será un
error, no una trampa — y el espejo permite buscarla.
