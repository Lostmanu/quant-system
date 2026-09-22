# PREREG — SONDA DE COBERTURA DEL LIBRO DE BINANCE
## Revisión 4 · PRE-CONSULTA de LIT/DOGE · pendiente de commit y sello

> **EL RÓTULO CAMBIA, y la mesa tiene razón en exigirlo.** Este documento decía «congelado
> 2026-08-27» y ya no lo era: contiene revisiones del 28 y del 29 —§4 entera, §3 bis, §5, los nombres
> de campo, S2, S4 bis— y varias de ellas están **informadas por observación**: las mediciones de
> `tools/estructura_chd_local.py` sobre diez ficheros-día de **AVAXUSDT**, que es un PROXY del feed y
> no los símbolos decisivos.
>
> Lo que sigue siendo cierto, y es lo que hace que esto siga siendo un pre-registro: **de LIT y DOGE
> no se ha observado NADA**. No se ha consultado el endpoint, no se ha pedido un objeto de orderbook
> de esos símbolos, y no se ha gastado un crédito. El proxy AVAX se declara aquí en vez de
> disimularse, porque una regla escrita mirando datos —aunque sean de otro símbolo— no puede
> presentarse como escrita a ciegas.
>
> **Congelación:** este texto no está congelado hasta que se commitee y `--sello` emita su blob. Hasta
> entonces, `--exigir` bloquea la ejecución, que es el estado correcto.

<!-- PRECEDE: docs/runs/sonda_cobertura_*.json, quant-system-ingesta/qs/tools/sonda_cobertura.py -->
<!-- IDS-IMPLEMENTADOS:  -->

## §0 — Por qué este documento SÍ es un pre-registro, y el otro no

`docs/ESPEC_POST_INCIDENTE_REF_VALIDA.md` se tituló «PREREG» y no lo era: sus reglas se escribieron
**después** de ejecutar el recálculo forense y ver que el veredicto se movía a favor de la casa (queda
registrado como E-42). Este documento es distinto en el único sentido que importa:

**De la sonda no se ha observado NADA.** No se ha consultado el endpoint de símbolos, no se ha pedido
un solo objeto de orderbook, no se conoce la cobertura de `LITUSDT` ni de `DOGEUSDT`, y no se ha
gastado un crédito. Todo lo que sigue se decide a ciegas respecto del resultado, que es lo que un
pre-registro significa.

Si alguna de estas afirmaciones dejara de ser cierta antes de la ejecución, **este documento pierde
su condición** y hay que decirlo, no re-fecharlo.

## §1 — Qué pregunta la sonda, y qué NO

**Pregunta.** ¿Existe en CryptoHFTData el **orderbook** de `LITUSDT` y `DOGEUSDT` en
**`binance_futures`**, con calidad reconstruible, durante la ventana decisiva?

**No pregunta** —y no se vuelve a comprar— la cobertura de **trades**: ya está acreditada por los
artefactos que el programa posee. Los 79 npz decisivos contienen 1.032.151 markouts finitos calculados
contra trades de `LITUSDT`; eso es imposible sin cobertura de trades en esos días.

**No pregunta** por el libro de **Lighter**. `LIT`/`DOGE` son símbolos de Lighter y `LITUSDT`/`DOGEUSDT`
de Binance (`confirm_runner.py:158` y `:164`). El libro que exige el pre-registro congelado es el de
**Binance**. El canal de orderbook de Lighter en CHD ya se probó y se declaró DEFECTUOSO e
INUTILIZABLE para reconstrucción (`docs/LEDGER.md`, apertura de Lighter 2026-07-02).

## §2 — Ventana, fuente y unidad

| campo | valor, fijado aquí |
|---|---|
| fuente | CryptoHFTData, `exchange = binance_futures`, `data_type = orderbook` |
| símbolos | `LITUSDT`, `DOGEUSDT` (nomenclatura a **confirmar** en el paso 1; si difiere, se anota y se usa la confirmada) |
| ventana | **2026-03-06 .. 2026-06-29**, ambos inclusive |
| unidad de cobertura | el **símbolo-día** |
| horizontes | {5 s, 25 s} — los del npz decisivo. El de 1 s no se compra |
| excluido | conjunto protegido: {WTI ≥ 2026-06-05} ∪ {LIT ≥ 2026-06-30}. Ni se lista ni se consulta |

## §3 — Definición de COBERTURA, con números (v2, mesa 2026-08-27)

**C0 · IDENTIDAD DEL CONTRATO, y sin ella no se sigue.** Antes de contar nada hay que fijar sin
ambigüedad qué contrato se está pidiendo: `exchange = binance_futures`, `data_type = orderbook`,
símbolo `LITUSDT` / `DOGEUSDT`, contrato **perpetuo USDT-M**. Si el endpoint de símbolos devuelve más
de un candidato, o el símbolo aparece con historia partida (renombrado, relistado), **la sonda para** y
la ambigüedad va a la mesa. No se elige «el que parece».

**C1 · INSTANTE CUBIERTO — sin saltos, y esto zanja la contradicción.** El instante de referencia es
`t_fill + Δ`. Se toma **el punto de rejilla más cercano a ese instante**; si ESE punto no es válido
—libro de un solo lado, cruzado, pre-warmup, o en un tramo con discontinuidad de secuencia— el
instante **NO está cubierto**. **No se busca el siguiente válido dentro de la tolerancia.**

> *La v1 decía en §3 «existe un punto de rejilla válido dentro de la tolerancia» y en §4 «no se salta
> al siguiente punto válido». Era contradictorio y la mesa lo señaló. Manda §4: la regla es la misma
> que ya rige en `realized_markouts` —referencia inválida en el objetivo ⇒ descarte— y la tolerancia
> `±max(Δ/2, 500 ms)` no se toca.*

**C2 · SÍMBOLO-DÍA USABLE** ⇔ cobertura ≥ **50 %** en **ambos** horizontes. No es un número nuevo: es
el suelo de densidad que el prereg congelado ya aplica (celda INCONCLUSA-POR-DENSIDAD si los descartes
superan el 50 %). Se hereda para no inventar umbrales donde la casa ya tiene uno.

**C3 · SUELO DE DÍAS, por símbolo y en proporción** — corregido por la mesa:

```
días_usables(sym)  ≥  ceil(0,75 × días_requeridos(sym))

    LIT   ≥ 60  de 79        DOGE  ≥ 53  de 70
```

> *La v1 escribía «≥ 60 símbolo-días» para los dos. El conjunto decisivo real es **LIT = 79 y
> DOGE = 70**, así que exigir 60 a DOGE era el **85,7 %**, no el 75 % que el propio documento decía
> pretender. Era un número perezoso, no una regla.*

**C4 · SUELO DE CELDA** — el texto de esta regla vive ahora en **§3 bis**, que la endurece: decía
«se comprueba POR CELDA» y a continuación no enumeraba las celdas ni separaba el suelo de descartes,
que se evaluaba agregado. Se conserva el identificador y se remite, en vez de reescribir en dos
sitios: dos versiones de la misma regla es la duplicación que este proyecto cataloga como E-49.

## §3 bis — C4 se comprueba POR CELDA, y las celdas son doce (mesa 2026-08-27, P0-6)

La v2 decía «cada celda (símbolo × Δ × tercil)» y luego evaluaba el suelo de descartes **agregado**.
Un agregado del 50 % es compatible con una celda al 90 % compensada por otra al 10 %, y la celda al
90 % es exactamente la que no se puede promediar. Las celdas son **12** y se enumeran para que no
quepa duda de sobre qué se aplica:

```
LIT  × { 5 s, 25 s} × {tercil 1, tercil 2, tercil 3}   → 6
DOGE × { 5 s, 25 s} × {tercil 1, tercil 2, tercil 3}   → 6
```

**C4-a · descartes ≤ 50 % EN CADA UNA de las 12.** No en el agregado. Una sola celda por encima del
50 % es INCONCLUSA y **no se promedia**, aunque el total quede por debajo.
**C4-b · ≥ 200 fills con markout válido y ≥ 4 días EN CADA UNA de las 12**, tras excluir lo no
cubierto y **antes** de re-derivar, sobre la cobertura simulada.

## §4 — Snapshot, continuidad y huecos: prohibido remendar (v3, mesa 2026-08-27 P0-4)

`analysis/cryptohft_adapter.py` reconstruye desde diffs **sin snapshot semilla** y **no lee los
`*_update_id` en absoluto**: aplica diffs en orden de fila, a ciegas. Verificado leyendo el código.

> **RETRACTACIÓN (2026-08-29).** Una versión anterior de este párrafo añadía que, como CHD entrega una
> fila por nivel, «el bucle emite puntos de rejilla entre filas del mismo evento, así que un punto
> puede salir con el diff a medio aplicar». **Era falso y se retira.** Al medirlo
> (`tools/estructura_chd_local.py`, 90.987.164 filas, recibo en `docs/runs/`): `event_time` es
> constante dentro del evento en el **100 %** de los casos y **cero** eventos cruzan una frontera de
> rejilla entre su primera y su última fila. El 89 % de eventos multifila era cierto; la conclusión no
> se seguía de él. El defecto REAL que queda acreditado es el otro: **ningún id de secuencia se lee**,
> así que un hueco no se detecta de ninguna forma.

> **POR QUÉ LA v2 ERA INSUFICIENTE, y es el fondo del asunto.** S1 declaraba un tramo utilizable
> «desde que el libro tiene ≥ top_l niveles por lado y no está cruzado (el warmup que el adaptador ya
> implementa)». Eso **no reconstruye el estado perdido**: el warmup dice «hay suficientes niveles para
> que el libro parezca plausible», que es una afirmación sobre la APARIENCIA, no sobre la corrección.
> Tras un hueco, los niveles que se borraron mientras no mirábamos siguen en el libro y los que
> aparecieron faltan; el libro tiene sus diez niveles por lado y está mal. Confundir warmup con
> snapshot es exactamente el error que este documento debía impedir.

**S1 · SNAPSHOT, y qué cuenta como uno.** Un tramo sólo puede empezar en un **estado certificado**:
un libro completo entregado como tal por la fuente, con su `lastUpdateId`. **El warmup NO es un
snapshot** y no puede sustituirlo. Si CHD no entrega snapshots para `binance_futures` / `orderbook`
—que es lo que hay que averiguar en el paso 1—, entonces:

- el instante `t_fill + Δ` **sólo está cubierto** si cae dentro de un tramo que arranca en un estado
  certificado y no ha sufrido ningún hueco desde él;
- todo lo anterior al primer estado certificado **cuenta como NO cubierto**, se cuenta aparte y se
  publica;
- y si no hay ningún estado certificado en todo el día, la cobertura de ese símbolo-día es **0**, no
  «la que salga tras el warmup».

> **CORRECCIÓN DE CAMPOS (mesa, 2026-08-29). Esta sección nombraba las columnas MAL.** Escribí
> `u = last_update_id` y `pu = prev_update_id` copiando la nomenclatura de la documentación de
> Binance, sin cotejarla contra el esquema que CHD entrega de verdad. Medido sobre 90.987.164 filas
> (`tools/estructura_chd_local.py`, recibo en `docs/runs/`): `last_update_id` existe como columna y
> está **nula en el 100 %** de las filas — está reservada al SNAPSHOT, que este feed no trae.
> Aplicar la especificación literalmente habría agrupado los updates **por una columna nula** y roto
> la reconstrucción entera. Los nombres correctos son los de abajo.

> **RETRACTACIÓN (2026-08-30) — la parte de este párrafo que habla del CANAL se retira.** «Está
> reservada al SNAPSHOT, que este feed no trae» es **FALSO**. Las 90.987.164 filas de la medición son
> **exactamente** los diez ficheros de `probe1` (AVAX, 2026-03-30..04-09), que no tienen una sola
> ancla; se generalizó de una colección al canal. Censo del caché entero (126 ficheros, 706.490.194
> filas, cero red, cero créditos, recibo en `docs/runs/`): **169 anclas**, y `overlap` (2026-06-12..25)
> las trae en **112 de 112** ficheros. Forma real de una fila `snapshot`, medida sobre 113 ficheros y
> 321.829 filas con cero violaciones: `first_update_id` y `prev_final_update_id` NULOS,
> `last_update_id` no nulo, y `final_update_id` **igual a** `last_update_id`.
>
> **Lo que SÍ se mantiene de este párrafo:** la corrección de nombres de columna, que era su objeto.
> `U = first_update_id`, `u = final_update_id`, `pu = prev_final_update_id`. Y que en las filas
> `update` el `last_update_id` está nulo — eso se sostiene en los 126 ficheros.
>
> **Lo que esta retractación NO afirma:** que el canal sea reconstruible. Que haya ancla no es que el
> tramo sea utilizable, el instrumento estructural no ratifica payload, y **nada de esto observa LIT
> ni DOGE**, de los que no hay un solo fichero de libro en disco. Sobre los decisivos, hipótesis.

**LOS CAMPOS, con el nombre que CHD usa realmente:**

| símbolo | columna CHD | qué es |
|---|---|---|
| `U` | `first_update_id` | primer id de actualización del evento |
| `u` | `final_update_id` | último id del evento |
| `pu` | `prev_final_update_id` | el `u` del evento anterior |
| `L` | `last_update_id` | id del **SNAPSHOT**. **Nulo en las filas `update`; CON VALOR en las filas `snapshot`** (corregido 2026-08-31: la tabla decía «en este feed, siempre nulo», medido sólo sobre `probe1`) |

**S2 · UN EVENTO ES ATÓMICO, y la identidad depende del TIPO.**

Un evento es el **tramo CONTIGUO MÁXIMO** de filas cuya clave de identidad concuerda. La clave no es
la misma para los dos tipos, y esto no es un detalle: en un snapshot `U` y `pu` están **nulos**, así
que aplicarle la identidad del update fundiría snapshots distintos en uno.

> **CORRECCIÓN (2026-08-31).** Este párrafo decía «los TRES campos de secuencia del update están
> nulos». Son DOS: `final_update_id` viene **con valor** en las filas `snapshot`, y vale exactamente
> `last_update_id`. Medido sobre los 113 ficheros del caché con ancla y sus 321.829 filas, cero
> violaciones. La clave de frontera del snapshot sigue siendo `(event_type, L)` y no cambia; lo que
> cambia es que la premisa que la justificaba estaba mal enunciada.

| tipo | clave de FRONTERA | invariante VALIDADO sobre el grupo |
|---|---|---|
| update | `(event_type, U, u, pu)` | `event_time` único y no nulo |
| snapshot | `(event_type, L)` | `event_time` único y no nulo |

> **`event_time` NO forma parte de la frontera** (mesa, 7º dictamen, P0-1). La versión anterior lo
> metía en la clave, y eso hace lo contrario de lo que S2 promete: si una fila del mismo `(U,u,pu)`
> trajera un `event_time` divergente, la clave partiría el evento en dos, el primer fragmento se
> aplicaría y el segundo caería como duplicado — es decir, «medio evento aplicado», que es justo el
> estado que S2 existe para prohibir.
>
> `event_time` es un **invariante del grupo**: se valida, y si diverge dentro de un evento el evento
> —y el día— quedan **inválidos ANTES de aplicar nada**. Validar e invalidar antes; nunca partir.

**Contiguo máximo, y la reaparición NO se fusiona.** Si una clave vuelve a aparecer después de que
haya aparecido otra en medio —la secuencia `A · B · A`—, la segunda `A` es **otro evento**, no una
continuación de la primera. Se trata como duplicado o desorden bajo **S4**, y se **declara**: fundir
tramos no contiguos borraría exactamente la anomalía que S4 existe para contar.

Las filas del evento se aplican **enteras o ninguna**, y está prohibido emitir un punto de rejilla
antes de haber aplicado el evento completo.

> **ALCANCE HONESTO DE S2.** Esta regla NO corrige un defecto vivo del adaptador actual: medido,
> `event_time` es constante dentro del evento en el **100 %** de los casos y **cero** eventos cruzan
> una frontera de rejilla, así que hoy no se emite a media actualización. La regla está aquí porque
> hace **explícita** una propiedad que hoy es **accidental**: si el feed dejara de cumplirla, la
> reconstrucción se rompería en silencio. Una versión anterior de este documento afirmaba que el
> adaptador sí emitía en medio; era falso y se retiró.


**S3 · LA RELACIÓN `U` / `u` / `pu`, exacta y OFICIAL:**

- el **primer** evento tras un estado certificado con `L = last_update_id` debe cumplir
  **`U ≤ L ≤ u`** — la regla oficial de Binance USDⓈ-M, no la de spot. Si ningún evento la cumple,
  el estado certificado **no se puede empalmar** y no hay tramo;

> **ENMIENDA 2026-08-31 (mesa, reauditoría del lote POST-DICTAMEN, P0-1). HAY DOS CARRILES, y lo de
> arriba es UNO.** La regla `U <= L <= u` gobierna el empalme de un snapshot tomado **FUERA DE
> BANDA** —el caso de nuestro colector, que pide el snapshot por REST y tiene que encontrar en qué
> evento encaja—. NO gobierna un ancla que el proveedor emite **DENTRO de la secuencia**, ya
> colocada: ahí no hay nada que empalmar y rige la continuidad ordinaria, `pu == L`, **incluido
> `U = L+1`**, que es la forma del ejemplo oficial del proveedor.
>
> Presentar una como universal hacía leer que `U = L+1, pu = L` es siempre inválida, y es una
> transición oficial válida. Medido en el caché local, y son TRES magnitudes que no deben confundirse:
> **censo bruto** 152 clasificables = 114 en línea + 38 fuera de banda; **máquina normativa** 145 evaluadas
> = 110 + 35; **déficit** 7 = 4 + 3, atribuidas ancla por ancla a la sustitución de candidato. La forma «de
> carril único» describe una cuarta parte del feed. Las tres cifras están firmadas en el censo cruzado de
> esquema 4 `docs/runs/censo_anclas_126f_m138.json` (sello `d51d41b467e5…`, sobre `869235b`, ligado al
> recibo `0d3b5e1eb1e0…`): las 145 evaluadas son empalmes TRAZADOS ancla por ancla —todos en el sitio del
> candidato vivo y todos caducados después por `avance_sin_digest`—, y las 7 no evaluadas se cuentan desde
> la traza con su causa (llegaron con un candidato vivo), no por resta.
>
> Lo que NO se afloja: `U = L+1` **sin** `pu == L` sigue sin valer. Es la regla de spot, que no mira
> `pu`, y lo que hace admisible la transición es la declaración explícita de cadena.

  > La versión anterior decía `U ≤ L + 1 ≤ u`, que es la regla de **spot**. Difieren en **DOS**
  > bandas, no en una (corregido por la mesa, 7º dictamen): en `U = L+1` —que spot acepta y futuros
  > no— y en `u = L` —que futuros acepta y spot **rechaza**, porque exigiría `L+1 ≤ L`—. Decir que
  > «difieren exactamente en `U = L+1`» era una explicación incompleta repetida varias veces. Se
  > aplica la oficial **literalmente** **para el ancla FUERA DE BANDA**, que es lo que esta regla
  > gobierna.
  >
  > **SUSTITUIDO (mesa, dictamen intermedio 2026-09-01).** Aquí decía: «La extensión `U = L+1 ∧
  > pu = L` queda FUERA de esta v1: se apoyaba en un barrido sin script ni recibo versionado y altera
  > la población aceptada». **Ese párrafo se retira, no se enmienda**: contradecía, veinte líneas más
  > arriba, la aceptación que la propia mesa acababa de dictar, y un pre-registro que acepta y
  > prohíbe la misma transición no norma nada. La mesa lo señaló: «hay que sustituir el bloque
  > antiguo, no añadir otra enmienda encima».
  >
  > La norma vigente, y es la única: `U = L+1 ∧ pu = L` **ENTRA**, por el carril EN LÍNEA, porque es
  > la continuidad ordinaria aplicada a un ancla que el proveedor emite dentro de la secuencia. La
  > prohibición sí se mantiene **sin** la declaración de cadena: `U = L+1` a secas es la regla de
  > spot, que no mira `pu`, y sigue cayendo en `NINGUNA`.
- para dos eventos **consecutivos**, `pu_actual == u_anterior`. Cualquier otra cosa es un **hueco**.

**S4 bis · SNAPSHOTS: partición DISJUNTA sobre `L`** (mesa, 9º dictamen, P0-4).

S2 remitía cualquier reaparición a S4, y S4 sólo hablaba de `u`/`pu` de **updates**: un snapshot no
tiene ninguno de los dos, así que la remisión apuntaba al vacío. La primera versión de esta tabla
tampoco servía, porque **no era una partición**: «mismo `L` repetido → duplicado» y «`L ≤ L_vigente`
→ inválido» se solapaban justo en la igualdad, que es el caso interesante.

Sea `L_vigente` el `L` del último estado certificado **aceptado** (inicialmente indefinido). Los casos
son mutuamente excluyentes y cubren todo:

| condición | veredicto |
|---|---|
| `L_vigente` indefinido y payload válido | **nuevo estado certificado**: abre tramo |
| `L > L_vigente` y payload válido | **nuevo estado certificado**: cierra el tramo anterior y abre uno |
| `L > L_vigente` y payload **inválido** | **inválido**: invalida hasta el siguiente inequívoco |
| `L == L_vigente` y payload **equivalente** | **duplicado**: se descarta y se cuenta. No reabre tramo |
| `L == L_vigente` y payload **distinto** | **contradictorio**: inválido |
| `L < L_vigente` | **obsoleto**: inválido. No se retrocede el libro |

Y por encima de la tabla, una regla que no depende de `L`:

**Reaparición `A · B · A`** —un snapshot cuya identidad ya apareció con otra en medio— es **inválida
por stale**, se evalúe como se evalúe su `L`. No hay una segunda regla que la rescate.

**`L_vigente` se arrastra ENTRE FICHEROS.** Una frontera cuyo segundo fichero empieza por snapshot
**no es un reinicio automático**: hay que evaluar ese snapshot contra el `L_vigente` que venía. Dar
por bueno cualquier snapshot inicial admitiría uno obsoleto, contradictorio o reaparecido.

> **LO QUE UN INSTRUMENTO ESTRUCTURAL NO PUEDE DECIDIR.** `tools/estructura_chd_local.py` lee
> identificadores, tiempo y símbolo — **no** lee `side`, `price` ni `quantity`. Puede por tanto
> decidir las filas de esta tabla que dependen de `L` y de la identidad, y **no puede** acreditar que
> un payload sea «válido» o «equivalente»: eso exige mirar el libro (bilateral, no cruzado, niveles
> > 0). Donde la tabla dice «payload válido», el instrumento estructural informa **`indeterminado`** y
> no emite veredicto. Presentarlo como implementación completa de S4 sería atribuirle una capacidad
> que no tiene.

**S4 · DUPLICADOS Y DESORDEN, que no son lo mismo.** Un evento con `u ≤ u_ya_aplicado` es un
**duplicado**: se descarta y se cuenta. Un evento con `u > u_ya_aplicado` pero `pu != u_anterior` es
un **hueco**: cierra el tramo. **No se reordena**, porque reordenar presupone que lo que falta acabará
llegando, y eso no se sabe.

**S5 · TRAS UN HUECO, INVÁLIDO HASTA EL SIGUIENTE ESTADO CERTIFICADO.** No hasta el siguiente warmup.
Lo que va entre el hueco y el siguiente estado certificado **no está cubierto**, por muchos niveles
que tenga el libro.

**S6 · PROHIBIDO REMENDAR.** No se interpola, no se arrastra el último libro válido y no se salta a
otro punto de rejilla (C1). Los tramos descartados **se cuentan y se publican**, desglosados por
causa: `sin_estado_certificado`, `hueco`, `duplicado`, `dia_corrupto`, `pre_warmup`.

**S7 · DÍA CORRUPTO.** Los días que marque `is_corrupt_day` del propio adaptador se excluyen enteros
y se cuentan. Es una comprobación **independiente** de S1-S6: un libro puede ser continuo y estar
congelado.

**S8 · REJILLA COMPLETA.** La rejilla se construye **entera, con máscara de validez**; omitir los
puntos inválidos haría que «el más cercano» pudiera estar a 12 s del objetivo sin que nada lo dijera.

> **CONSECUENCIA QUE NO SE OCULTA.** Si CHD no entrega snapshots, S1 puede hacer que la cobertura sea
> **baja o nula** por construcción, y entonces la sonda FALLA por §6. Eso no es un defecto del
> criterio: es el criterio funcionando. La alternativa —aceptar el warmup— daría una cobertura alta
> sobre libros que no sabemos si son correctos, que es precisamente cómo se fabrica un resultado
> irrefutable y falso.

## §5 — Topes duros: crédito, reintentos y tiempo (v3, mesa 2026-08-27 P0-6)

> **POR QUÉ SE REESCRIBE.** «Máximo 20 llamadas» **no es un límite de crédito**. Una sola llamada
> puede paginar cien veces, traerse gigabytes o colgarse una hora, y el tope de llamadas se cumpliría
> mientras el gasto real es desconocido. Un tope que no acota lo que se quiere acotar es un adorno.

| paso | qué | tope duro |
|---|---|---|
| 1 | endpoint de símbolos (`binance_futures` + `orderbook`) | **1** consulta |
| 2 | existencia de objetos, uno por MES (4 meses × 2 símbolos) | **8** consultas de metadatos |
| 3 | **muestra diagnóstica**, 8 símbolo-días CONGELADOS (abajo) | y se **MIDE el coste real** |
| 4 | lote completo | **sólo** tras publicar el coste del paso 3 y con autorización expresa |

**LAS 8 FECHAS DIAGNÓSTICAS, congeladas aquí y no elegidas después** — la primera fecha de cada mes
presente en el manifiesto, por símbolo, que es una regla y no una preferencia:

```
LIT_2026-03-06  LIT_2026-04-01  LIT_2026-05-01  LIT_2026-06-03
DOGE_2026-03-06 DOGE_2026-04-01 DOGE_2026-05-01 DOGE_2026-06-01
```

Elegirlas después de ver la cobertura permitiría escoger los días buenos y publicar un coste que no
es el coste. Si alguna resultara inaccesible, **se declara y se para** — no se sustituye por otra.

**TOPES DE GASTO, y cada uno acota una dimensión distinta:**

| tope | valor | por qué existe |
|---|---|---|
| `MAX_LLAMADAS` | **20** en las fases 1-3 | el de la v2, conservado |
| `MAX_PAGINAS_POR_LLAMADA` | **4** | una llamada paginada es N llamadas con un solo nombre |
| `MAX_BYTES_TOTAL` | **512 MiB** | el volumen es lo que se paga; se acumula y se comprueba **antes** de cada petición |
| `MAX_BYTES_POR_OBJETO` | **64 MiB** | un objeto anómalo no puede consumir el presupuesto entero |
| `TIMEOUT_POR_PETICION` | **60 s** | una petición colgada gasta reloj y no da señal |
| `TIMEOUT_TOTAL_FASE` | **900 s** | cota de la fase completa, independiente de las peticiones |
| `MAX_REINTENTOS` | **2 por objeto**, espera fija 4 s | T1 de la v2 |
| `SALDO_MINIMO` | se **consulta antes** de la fase 3 y **después**; la diferencia es el coste medido | sin lectura antes/después no hay «coste real», hay una estimación |

- **T1 · REINTENTOS sólo ante error de red o respuesta vacía.** Un error de esquema **no se
  reintenta**: se para y se declara.
- **T2 · CUALQUIER tope alcanzado es PARAR**, no pedir más ni «probar con menos». El tope que se toca
  se nombra en el recibo.
- **T3 · Entre el paso 3 y el 4 hay una parada obligatoria.** No se descargan cuatro meses para
  averiguar si existen. Si el coste medido hace inviable el paso 4, la sonda **falla por coste** y
  aplica §6 — no se descarga «un poco a ver».
- **T4 · El recibo publica el gasto REAL** —llamadas, páginas, bytes, segundos y saldo antes/después—
  aunque la sonda PASE. Un coste que sólo se publica cuando sale mal no es un control.

## §6 — Las dos salidas, decididas antes de mirar

**PASA** ⇔ nomenclatura confirmada **y** C2/C3/C4 se cumplen en **ambos** símbolos.
→ Se re-deriva marzo-junio moviendo **exclusivamente la referencia** (trade más cercano → mid).
**No se toca** el estimador, ni los horizontes, ni la selección de fills, ni los criterios de
exclusión, ni la tolerancia. Mover dos cosas a la vez haría inseparables sus efectos.

**FALLA** ⇔ cualquiera de las condiciones anteriores.
→ El estimando pre-registrado queda **NO RECONSTRUIBLE para esa ventana y esos símbolos**, y se dice
así. **Prohibido** sustituir en silencio por otra ventana, otro activo o un sucedáneo «lo más parecido
posible». Una ventana prospectiva posterior sería un **estudio SEPARADO**, con su propio pre-registro
y fecha de inicio posterior a esta decisión: no hereda la historia de marzo-junio ni puede presentarse
como su réplica.

**En AMBOS casos** — y esto se declara ahora, no después — cualquier número que salga de re-analizar
la ventana decisiva es **forense/exploratorio**. El held-out está gastado. Una confirmación auténtica
exige ventana nueva. Se dice por adelantado precisamente porque el primer re-cálculo ya hecho salió
favorable a la casa.

## §7 — Recibo previsto, y a qué queda ligado

La sonda emite, con la mecánica de `tools/censo_ref_invalida.py`: manifiesto canónico
`ruta lógica → fecha → bytes → SHA-256`, leyendo cada objeto **una sola vez** y analizando **esos
mismos bytes**; la configuración (ventana, símbolos, C0-C4, S1-S5, T1-T3, tolerancia, conjunto
protegido); las exclusiones con su motivo; el coste medido; y un recibo que **ligue ruta con bytes**
—permutar dos hashes entre rutas tiene que cambiarlo—.

**A QUÉ QUEDA LIGADO, y es lo que impide citarlo fuera de contexto:**

- al **blob SHA-1 del texto vigente de este pre-registro** y al commit en que ese texto entró en la
  historia —lo que emite `tools/guardia_documental.py --sello docs/PREREG_SONDA_COBERTURA.md`—, para
  que no pueda presentarse como respaldado por una versión distinta de las reglas.

  **Corrección (mesa, 2026-08-27, P0-5).** La versión anterior de esta línea decía «el commit que lo
  introdujo», y eso ataba el recibo a la **v1**: este documento nació en `546148e` y sus reglas
  vigentes se escribieron en `807d0fe`. Un recibo que citara `546148e` certificaría un texto que ya
  no rige. Lo que identifica un prerregistro congelado es su **contenido**, no su nombre de fichero
  ni la fecha en que apareció;
- al **manifiesto exacto de 149 entradas** — **LIT 79 + DOGE 70**, el conjunto decisivo completo. Un
  manifiesto con otro número de entradas es otra sonda, y el recibo tiene que decirlo.

**EL MANIFIESTO, ENUMERADO AQUÍ** (mesa 2026-08-27, P0-6: «congelar el manifiesto exacto de 149
entradas»). Va dentro del documento y no en un fichero aparte a propósito: así queda cubierto por el
blob que sella `--sello`, y no puede cambiar sin cambiar el sello. Comprobado listando NOMBRES de
`data_hist/lighter_confirm/blocks/` — ningún `.npz` abierto —: 149 ficheros, LIT 79 y DOGE 70, todos
≤ 2026-06-29, que es exactamente lo que este documento venía afirmando.

```
sha256(lista canónica, un `SIMBOLO_FECHA` por línea, orden lexicográfico, LF final)
  = 7918e97c1e06ba56bb47e023efc604ccf931a188ffabf61e9d1db8e2782c2198

LIT (79):
2026-03-06 2026-03-07 2026-03-08 2026-03-09 2026-03-10 2026-03-11 2026-03-21 2026-03-22
2026-03-23 2026-03-24 2026-03-26 2026-03-27 2026-03-28 2026-03-29 2026-03-30 2026-03-31
2026-04-01 2026-04-02 2026-04-03 2026-04-04 2026-04-05 2026-04-06 2026-04-08 2026-04-09
2026-04-10 2026-04-11 2026-04-12 2026-04-13 2026-04-14 2026-04-15 2026-04-16 2026-04-17
2026-04-18 2026-04-19 2026-04-20 2026-04-21 2026-04-23 2026-04-24 2026-04-25 2026-04-26
2026-04-27 2026-04-28 2026-04-29 2026-04-30 2026-05-01 2026-05-02 2026-05-03 2026-05-04
2026-05-05 2026-05-06 2026-05-08 2026-05-09 2026-05-10 2026-05-11 2026-05-12 2026-05-13
2026-05-14 2026-05-15 2026-05-16 2026-05-17 2026-05-18 2026-05-20 2026-05-22 2026-05-23
2026-05-28 2026-05-29 2026-06-03 2026-06-11 2026-06-14 2026-06-15 2026-06-18 2026-06-19
2026-06-20 2026-06-21 2026-06-22 2026-06-26 2026-06-27 2026-06-28 2026-06-29

DOGE (70):
2026-03-06 2026-03-07 2026-03-08 2026-03-20 2026-03-21 2026-03-22 2026-03-23 2026-03-24
2026-03-25 2026-03-26 2026-03-27 2026-03-29 2026-03-30 2026-03-31 2026-04-01 2026-04-02
2026-04-03 2026-04-04 2026-04-05 2026-04-06 2026-04-07 2026-04-08 2026-04-09 2026-04-11
2026-04-12 2026-04-13 2026-04-14 2026-04-15 2026-04-22 2026-04-23 2026-04-24 2026-04-27
2026-04-28 2026-04-30 2026-05-01 2026-05-03 2026-05-04 2026-05-07 2026-05-08 2026-05-09
2026-05-12 2026-05-13 2026-05-14 2026-05-15 2026-05-16 2026-05-19 2026-05-21 2026-05-22
2026-05-24 2026-05-25 2026-05-29 2026-05-30 2026-05-31 2026-06-01 2026-06-02 2026-06-03
2026-06-11 2026-06-12 2026-06-14 2026-06-15 2026-06-16 2026-06-17 2026-06-18 2026-06-19
2026-06-20 2026-06-21 2026-06-22 2026-06-27 2026-06-28 2026-06-29
```

## §7 bis — La ejecución queda BLOQUEADA hasta que todas las reglas tengan código

Antes de gastar un solo crédito, el ejecutor de la sonda invoca:

```bash
python tools/guardia_documental.py --exigir PREREG_SONDA_COBERTURA.md
```

y **no arranca con `rc != 0`**. Bloquea si alguna regla `C*`, `S*` o `T*` de este documento no declara
dónde vive su implementación, si esa implementación no está donde dice, o si el texto vigente de este
documento no está commiteado — un pre-registro que puede cambiar mientras corre el protocolo no
congela nada.

**Por qué esto es distinto del guardia general** (mesa, P0-5). Ahí una regla pendiente es normal y no
puede poner rojo el build: un pre-registro habla de lo que aún no existe. Aquí la pregunta es otra
—¿está esto listo para EJECUTARSE?— y entonces una regla sin código es un impedimento absoluto:
gastar bajo un protocolo a medio implementar produce un resultado que nadie puede verificar después.

Y el ejecutor resuelve además el **registro** antes de tocar la red:

```python
from tools.registro_sonda import exigir_listo
exigir_listo(IDS_DE_ESTE_PRERREGISTRO)      # importa y comprueba que TODAS son invocables
```

Son dos cosas distintas y hacen falta las dos. La declaración `C1=analysis/mod.py:regla_uno` acredita
por AST que **existe un símbolo con ese nombre**; el registro acredita que ese símbolo **se importa y
se puede llamar**. Un AST no distingue una función de un nombre suelto — hasta 2026-08-28 una
variable local dentro de otra función satisfacía la declaración—, y aunque lo distinguiera, seguiría
sin decir que alguien la invoca. `exigir_listo` resuelve **todas de golpe**: descubrir a mitad de
campaña que la quinta regla no importa deja media campaña gastada y ningún resultado utilizable.

Hoy `--exigir` devuelve **`rc=2` con 13 reglas sin ligar** y el registro está **vacío**. Es el estado
correcto: la sonda **no puede correr**, y lo impide una máquina y no un acuerdo.

## §8 — Cómo se falsa este pre-registro

Si el resultado de la sonda se publicase sin su recibo; si C3 se relajara tras verlo; si se
descargara el lote completo sin la parada del §5; o si una ventana posterior se presentara como
reconstrucción de marzo-junio — este documento se habrá incumplido, y el incumplimiento se registra
en `docs/AUDITORIA_DEL_METODO.md` como cualquier otro.
