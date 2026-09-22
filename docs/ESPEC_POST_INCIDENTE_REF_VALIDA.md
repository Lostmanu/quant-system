# ESPECIFICACIÓN POST-INCIDENTE — REFERENCIA VÁLIDA Y DEFINICIÓN DEL MID

<!-- IDS-IMPLEMENTADOS: R1=analysis/ref_valida.py:clasificar,
     R2=analysis/ref_valida.py:LIMITE_ABSURDO_BPS!constante,
     R3=analysis/ref_valida.py:contadores_vacios,
     R4=analysis/ref_valida.py:linea_r4 -->
<!-- Cada regla dice DONDE vive y el guardia comprueba por AST que ese simbolo existe:
     un `grep` lo satisfacia un comentario. Las M* (mid, sonda) NO estan implementadas y
     por eso NO se declaran; el guardia las reporta como pendientes, sin fallar. -->

## §0 — POR QUÉ ESTO **NO** ES UN PRE-REGISTRO (rectificación, 2026-08-27)

Este documento nació el 2026-08-26 titulado `PREREG_REF_VALIDA.md` y abriendo con esta frase:

> *«No decide ningún número. Decide reglas, y las decide **sin haber mirado qué le hacen a ningún
> resultado**.»*

**Esa frase era falsa, y la falsedad es la que importa.** La cronología real de aquella sesión fue:

1. se construyó el censo del defecto y se ejecutó;
2. se ejecutó el **recálculo forense**, que dio la vuelta al veredicto §3 de `INCONCLUSO` a
   `NULA MUERTA` — es decir, **el resultado más favorable posible para la casa**;
3. **después** se redactó este documento y se le puso el título `PREREG`.

Las reglas de abajo las escribió alguien que **ya sabía hacia dónde se movía el dato**. Que el
congelado fuese anterior al *código* es cierto y es irrelevante: un pre-registro lo es respecto del
**resultado**, no respecto del teclado. Lo señaló la mesa (2026-08-27) y se acepta entero.

**Qué cambia y qué no.** Cambia el nombre y el estatus: esto es una **especificación post-incidente**,
y su autoridad es la de un compromiso público de aquí en adelante, no la de un pre-registro. **No
cambia el contenido**: las reglas siguen siendo las mismas, porque relajarlas ahora sería un
aflojamiento post-dato y eso sigue prohibido. Fortalecer sí; aflojar no.

**Queda registrado como E-42** en `docs/AUDITORIA_DEL_METODO.md`. No se borra reescribiendo el commit.

**Lo que sí puede ser genuinamente previo** es el protocolo de la sonda de cobertura, porque de la
sonda no se ha observado nada todavía. Por eso vive en un documento **separado** —
`docs/PREREG_SONDA_COBERTURA.md` — con sus umbrales numéricos fijados antes de la primera consulta.

---

## §0-bis — Qué ordenó la mesa

Dictamen del 2026-08-26, por ese orden: registrar el incidente e invalidar los resultados antiguos;
congelar el diseño correcto del mid; añadir validación y tests; e intentar una re-derivación completa.

---

## §1 — Los dos defectos que este prereg cierra

**P0-A, productivo.** `analysis/pilot_observer.py:122` calcula

```python
mo[i, k] = lado * (float(ref_px[best]) - e["px"]) / e["px"] * 1e4
```

sin comprobar que `ref_px[best]` sea un precio válido. Con `ref_px = 0` devuelve exactamente
`-lado·10.000,00 bps` — un valor **finito**, que `isfinite` acepta y toda la cadena promedia.

**P0-B, científico.** El pre-registro congelado (`docs/PREREG_MAKER_LIGHTER.md`, mapa de horizontes
pre-firmado) manda, para un símbolo con identidad certificada:

> *«identidad CERTIFICADA ⇔ ρ retornos-5m ≥ 0,95. Certificada → **mid de Binance como `precio_ref` en
> todos los horizontes**.»* — y *«LIT→mid Binance LITUSDT (ratio 1,001) a {1,5,25} s»*.

`analysis/confirm_runner.py:152-157` usa `chd.get_trades(...)["price"]`: el **trade más cercano**, no
el mid. LIT y DOGE están certificados (ρ_5m 0,9826 / 0,9521). **Es un incumplimiento del
pre-registro, no una errata de docstring**, y cambia el estimando. Sanear P0-A no lo corrige.

## §2 — Regla de REFERENCIA VÁLIDA (P0-A)

Se distingue, a propósito, entre lo **mecánicamente inválido** (se rechaza) y lo **sospechoso** (se
cuenta y se emite, pero **no se filtra**). Mezclarlas daría a un filtro post-dato la capacidad de
mover el resultado, que es justo lo que no puede pasar.

**R1 — RECHAZO (→ descarte contado, `NaN`, jamás un markout).** Tres clases, en este orden:

| clase | condición | por qué |
|---|---|---|
| `no_finita` | `NaN`, `+inf`, `-inf` | no es un número |
| `no_positiva` | `ref ≤ 0`, el cero incluido | no es un precio |
| `degenerada` | finita y `> 0` pero `\|markout\| ≥ 9.000 bps` | no es un markout: es un dato roto |

Idéntica regla para el **precio del fill**: si no es finito o no es positivo, la celda es descarte
(y además evita la división por cero). El orden de comprobación importa: un `NaN` debe salir
`no_finita`, no `degenerada`, o el diagnóstico diría lo que no es.

> **La tercera clase se añadió el 2026-08-27, y se dice cuándo.** La versión del 26 sólo rechazaba lo
> no finito y lo no positivo — así que **un `ref` positivo diminuto (`1e-9`) seguía pasando el
> guardia** y producía la misma firma de −10.000 bps. El agujero central sobrevivía a su propio
> arreglo. Se endurece **después** de mirar el censo, comprobando que es un **no-op demostrable**:
> 15.540 celdas con firma exacta, **0** celdas con `\|mo\| ≥ 9.000` que no la tengan, **0** entre 3.000
> y 9.000. Rechaza exactamente lo que R1 ya rechazaba y ni una más. Se endurece porque cierra un
> agujero futuro sin mover ningún resultado presente, **no** porque mejore ninguna cifra.

**R2 — EL LÍMITE NO ES UN FILTRO DE PLAUSIBILIDAD.** Los 9.000 bps no opinan sobre qué movimiento es
razonable: son la frontera donde el markout **deja de ser un markout** (±90 % en el horizonte de
medida). Un movimiento del 30 % pasa. Un límite estrecho (5 %, 20 %) sería un filtro post-dato capaz
de mover resultados y **está prohibido** sin su propio pre-registro con umbral justificado pre-dato.

> **La decisión se toma sobre el MARKOUT, no sobre un ratio, y hubo que aprenderlo dos veces.** La
> primera versión fijó una banda de ratio `[0,1 ; 10]` afirmando que fuera de ella `|markout| ≥ 9.000`.
> Era **falso por arriba**: ratio 10 da **+90.000 bps**. La regla toleraba markouts diez veces más
> absurdos en un sentido que en el otro. Lo cazó el falsificador por propiedades
> (`tests/propiedades.py`) en su primera corrida, con `ref = 45,68 · px = 6,13` — **E-51**. Y el
> primer arreglo, derivar `1,0 ∓ 0,9`, tampoco era simétrico: `1.0 - 0.9 = 0.09999999999999998` en
> float64 mientras `1.0 + 0.9 = 1.9` es exacto, así que un borde quedaba dentro y el otro fuera. La
> forma definitiva compara `abs(markout)` contra el límite: la simetría es imposible de romper.

> *La versión del 26 decía «se cuenta, y **se emite en el npz** junto a los descartes». **El código no
> lo hacía**: los contadores eran efímeros. La mesa lo señaló — una especificación no puede prometer
> campos que el código descarta. Ver R3 para lo que sí se persiste y dónde.*

**R3 — CONTABILIDAD Y PERSISTENCIA.** Los rechazos se suman a `descartes[k]` y además se cuentan
**por causa** (`sin_tfill`, `px_invalido`, `tiempo`, `ref_no_finita`, `ref_no_positiva`,
`ref_degenerada`), de modo que «no había referencia cerca» y «la que había estaba rota» nunca se
confundan. El cuadre `finitos + Σ causas = n_eventos` es una **aserción viva** dentro de la función,
no sólo un test: si deja de cumplirse en una corrida real, revienta ahí y no publica en silencio.

**Dónde se persisten, y por qué no en el npz.** En un **fichero lateral** `{sym}_{day}.contadores.json`
junto al bloque. **No** dentro del `.npz`: su esquema y el ORDEN de sus claves están sujetos a la
prueba de identidad-byte de M-10, y añadir campos la rompería. El lateral es versionable, auditable y
no toca el artefacto histórico.

**R4 — FALLO RUIDOSO.** Si la fracción de descartes **por referencia** (las tres clases sumadas, no
una) supera el **5 %**, se registra como anomalía visible; por debajo, como aviso. No aborta: abortar
borraría el dato del incidente. Vive en `analysis/ref_valida.linea_r4`, es una **función pura** —
invocable desde un test— y está cableada en **los cinco** puntos de llamada, no en uno.

> *La versión del 26 metía R4 como un `print` dentro de `confirm_runner`, contaba una sola clase de
> rechazo y dejaba fuera a `pilot_runner`, `eco_runner_wti`, `eco_fase2_wti` y `maker_capa2_runner`.*

## §3 — Definición del MID (P0-B)

**M1 — Qué es `precio_ref`.** Para un símbolo con identidad certificada, `precio_ref(t)` es el
**mid del top-of-book de Binance futures**, `(best_bid + best_ask)/2`, en el instante de referencia.
No es el último trade, ni un trade cercano, ni un weighted-mid.

**M2 — De dónde sale.** De la maquinaria **ya existente y validada** del capítulo 1:
`analysis/cryptohft_adapter.py` (`reconstruct_timegrid` / `cryptohft_to_book_guarded`), que
reconstruye el libro desde los diffs de CHD y trae su propia guardia de día corrupto
(`is_corrupt_day`). **No se escribe un reconstructor nuevo**: uno nuevo sería una fuente de error
nueva, y este ya pasó por el capítulo 1.

**M3 — Anclaje temporal.** El mid se toma del punto de rejilla más cercano a `t_fill + Δ` dentro de
la MISMA tolerancia que hoy usa `realized_markouts` (`±max(Δ/2, 500 ms)`). La tolerancia **no se
cambia en este prereg**: cambiarla a la vez que la referencia haría inseparables los dos efectos.

**M4 — Libro no válido = descarte contado.** Si en el instante de referencia el libro no tiene ambos
lados, está cruzado (`best_bid ≥ best_ask`), o no ha superado el warmup que exige el adaptador, la
celda es **descarte contado**, no un markout.

**M5 — SONDA DE COBERTURA, obligatoria y previa.** Antes de re-derivar nada se corre una sonda que
establezca si CHD tiene orderbook de `LITUSDT` y `DOGEUSDT` en la ventana. **Resultado y consecuencia,
declarados aquí y no después:**

- **Cobertura suficiente** → se re-deriva contra mid y se compara con el carril de trades. La
  diferencia entre ambos es la magnitud del incumplimiento P0-B, y se publica.
- **Cobertura insuficiente o ausente** → **el estimando pre-registrado NO es reconstruible sobre la
  ventana decisiva.** No se sustituye por un sucedáneo ni se declara «lo más parecido posible»: se
  abre **ventana prospectiva nueva** con el colector propio, que sí registra libro. Es la salida que
  la mesa nombró y se acepta por adelantado.

**M6 — Lo que NO se puede hacer con el resultado.** Cualquier re-cálculo sobre la ventana decisiva —
saneada, re-referenciada, o ambas— es **forense/exploratorio**. El held-out está gastado. Ningún
número que salga de ahí puede reclamar carácter confirmatorio, gane o pierda. Esto se declara **antes**
de mirar, precisamente porque el primer re-cálculo ya hecho salió favorable a la casa.

## §3-bis — ENMIENDA del 2026-08-27, pre-dato y solo endurecedora

Se añade tras una revisión externa (Perplexity, vía el propietario) y la verificación de sus premisas
contra el repositorio. **No se ha mirado ningún dato nuevo**: todo lo de abajo restringe, ninguna
regla se relaja. La revisión partía de un error de venue —auditaba la cobertura del libro de
**Lighter** en CHD— y por eso se fija primero la nomenclatura.

**M0 — NOMENCLATURA, para que la confusión no se repita.** `LIT` y `DOGE` son símbolos de **Lighter**
(`confirm_runner.py:158`). `LITUSDT` y `DOGEUSDT` son símbolos de **Binance futures**
(`confirm_runner.py:164`). El mid que este prereg exige es **el de Binance**, no el de Lighter. El
libro de Lighter en CHD **no está en juego**: el propio programa lo declaró DEFECTUOSO para
reconstrucción y INUTILIZABLE (`docs/LEDGER.md`, apertura de Lighter 2026-07-02), y por eso se escaló
a 0xArchive.

**M5-bis — LA COBERTURA DE TRADES YA ESTÁ PROBADA, y no se vuelve a comprar.** Los 79 npz decisivos
contienen 1.032.151 markouts finitos calculados contra trades de `LITUSDT` en `binance_futures`; eso
es imposible sin cobertura de trades en esos días. **La sonda de §3-M5 pregunta ÚNICAMENTE por el
ORDERBOOK** de `LITUSDT` y `DOGEUSDT`. Comprar de nuevo lo ya acreditado sería gastar créditos en una
pregunta contestada.

**M5-ter — LA RECONSTRUCCIÓN CAMBIA UNA SOLA COSA.** Si la sonda pasa, se re-deriva moviendo
**exclusivamente la referencia** (trade más cercano → mid). **No se toca** el estimador, ni los
horizontes, ni la selección de fills, ni los criterios de exclusión, ni la tolerancia de anclaje
(§3-M3). Mover dos cosas a la vez haría inseparables sus efectos, que es como se llegó aquí.

**M5-quater — UNA VENTANA NUEVA NO ES LA RECONSTRUCCIÓN.** Si la sonda falla, el estimando queda
**no reconstruible para esa ventana y esos símbolos**, y se dice así. Una ventana prospectiva
posterior es un **estudio SEPARADO**, con fecha de inicio posterior a esta decisión y su propio
pre-registro. **No sustituye** a marzo-junio, no hereda su historia y no puede presentarse como su
réplica. Prohibido sustituir en silencio por otra ventana o por otro activo.

**M7 — CONTINUIDAD DE SECUENCIA, requisito NUEVO.** `analysis/cryptohft_adapter.py` reconstruye el
libro desde los diffs **sin snapshot semilla**, con warmup y exigencia de libro no cruzado — pero **no
comprueba la continuidad de los `*_update_id`**, que sí trae en las columnas. La documentación de CHD
es explícita en que una discontinuidad de secuencia obliga a **reiniciar y esperar snapshot nuevo**, no
a seguir aplicando diffs. Por tanto:

- antes de usar un tramo, se **verifica la continuidad** de `update_id`;
- un tramo con discontinuidad **se excluye y se cuenta** bajo el trato de huecos ya vigente (I6), no
  se remienda;
- si tras excluir no queda masa por encima del suelo ya pre-registrado, **la sonda falla** y aplica
  M5-quater.

Este requisito no existía cuando §3-M2 dijo «reutilizar el adaptador porque ya está validado». Estaba
validado para el capítulo 1 —OFI y mid sobre 8 perpetuos líquidos: ATOM, AVAX, DOT, FIL, LINK, LTC,
NEAR, UNI—, **ninguno de ellos LIT ni DOGE**. Validado para un uso no es validado para éste.

**M8 — LA SONDA ES BARATA Y VA POR ESE ORDEN.** (1) endpoint de símbolos de CHD para
`binance_futures` + `orderbook`, para confirmar que `LITUSDT`/`DOGEUSDT` existen con ese
identificador en la ventana; (2) existencia de objetos en **cada uno** de los cuatro meses; (3) una
muestra diagnóstica por mes, con verificación de M7 sobre ella; (4) sólo entonces, el lote completo.
**No se descargan cuatro meses para averiguar si existen.**

## §4 — Lo que este prereg NO decide

- No decide si `+18,24`, `+15,60` o cualquier otra cifra es el número. Ninguna lo es hoy.
- No levanta el STOP de producción ni autoriza gasto de créditos.
- No reabre DOGE como evaluable: la mesa lo dejó en **NO EVALUABLE** y aquí sigue.
- No toca la capa 2 (marcada contra Lighter, ajena a P0-B) ni la capa 3 transaccional.
- No modifica el conjunto protegido, que permanece intacto y verificado.

## §5 — Cómo se falsa este prereg

Si tras aplicar §2 y §3 apareciera cualquier celda con `|mo|` compatible con `-lado·10.000`, o el
cuadre de R3 no diese exacto, **la regla no se ha aplicado** y hay que pararlo. Los tests de
`tests/test_pilot_observer_ref_invalida.py` existen para que eso sea imposible de publicar en verde.
