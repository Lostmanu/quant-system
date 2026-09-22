# LEDGER de experimentos — quant-system

**Append-only** (Plan v2.2, C2): una entrada por hipótesis, viva desde su
registro hasta su muerte. Prohibido borrar o editar entradas cerradas — el
conocimiento negativo es el activo. El `id` de cada entrada es la **etiqueta de
familia de hipótesis** que exige el §3.3 del Plan (N efectivo del DSR) y enlaza
con el log inmutable de ensayos (§3.5).

Estados: `propuesta → en curso → (falsada | viva) → muerta`.
Regla n=1: conclusión con 1 símbolo o 1 año = hipótesis, jamás hallazgo.
Las columnas de alpha-decay (C3) se rellenan SOLO desde telemetría de
producción (§8.2, Fase 7) — hasta entonces quedan vacías a propósito.

**REGLA DURA de pre-registro (añadida 2026-06-13 tras la auditoría de H2):** el
bloque de predicción + falsación debe **commitearse a git ANTES** de ejecutar la
descarga/análisis que lo evalúa. El hash de git es la única autoridad de fecha
válida; un pre-registro persistido pero sin commitear (o commiteado junto al
resultado) NO cuenta como pre-registro — es narrativa retrospectiva. El
quant-reviewer verifica esto con `git log -S`.

---

## META-CONCLUSIÓN DEL PROGRAMA (2026-07-01) — resultado positivo, no fracaso

**Los perps maduros USDT-M de Binance (los 8 finos) y sus listings nuevos NO ofrecen edge direccional ni de
provisión a un jugador LENTO con infra retail en 2025-2026.** Esto es un resultado ACCIONABLE — saber dónde
NO buscar, con evidencia — no una racha de mala suerte. La eficiencia de estos mercados es mayor de lo que la
cola asumía.

**La evidencia (6 frentes cribados; held-out GASTADO en UNO solo — el contrarian):**
1. **Trío de primas de servicio** (provisión-soledad, ejecución-OFI, funding-carry) → 3 SCREEN-NEGATIVE.
2. **Cross-venue Binance→Bybit** → archivado (~50 ms = juego de velocidad, no operable para lento).
3. **Contrarian OFI (reversión)** → SCREEN-NEGATIVE, t=−26, −10,71 bps tras costes. **Pista dura: el flujo es
   INFORMADO (continúa, no revierte) → el que pierde es el MAKER (selección adversa), no el taker direccional
   lento.** [[quant-system-ingesta]]
4. **H3 cascadas** → INCONCLUSO-POR-MASA (condición C demasiado rara, 0,57% < 1%).
5. **Lead-lag cross-asset** (feasibility de H5) → NULL, D=−0,026 (dirección opuesta). La propagación
   cross-asset es RUIDO arbitrado, no información.
6. **H6 ventana de listing** → cerrada sobre prior bajo: régimen NO fuertemente ineficiente; **el libro tiene
   MM desde el minuto 1 (nsnap 1,00×)** → la ventana de descubrimiento ancha de 2017-2019 ya no existe.

**El patrón:** en DIRECCIÓN, estos mercados son eficientes-para-un-lento — se pierde contra eficiencia +
costes + la ventaja de selección adversa del maker. La competencia ya cerró estas ineficiencias.

**Lo que esto NO es: un fallo de la maquinaria.** El motor está validado, es 3,5× más rápido, y cribó 6 tesis
plausibles **gastando held-out en UNA sola** — la disciplina (pre-registro, pre-checks de dos capas, higiene
de held-out) funcionó exactamente para lo que se diseñó: matar tesis barato, sin autoengaño, $0 (solo dato
gratis). El activo entregado = **conocimiento negativo mapeado + infraestructura reutilizable.**

**La pregunta del próximo capítulo NO es "¿qué mecanismo probar en estos 8 perps?" sino "¿a qué UNIVERSO o
INSTRUMENTO apunta esta maquinaria donde la competencia no haya cerrado la ineficiencia?"** Pistas que deja la
evidencia: (a) el edge, si existe aquí, está del lado MAKER/selección-adversa — requiere infra de baja latencia
que NO tenemos; (b) venues/instrumentos menos maduros, o menos competidos, son el terreno natural del stack L2
validado. El laboratorio no se cierra: se re-apunta con un prior honesto.

---

## H1 — Predicción de calidad de liquidez

- **Alta:** 2026-06-12 · **Estado:** **PRE-REGISTRADA / CONGELADA 2026-06-21** (predicción y
  falsación fijadas ANTES de tocar el L2 propio; el hash de este commit es la autoridad de
  fecha). Ejecuta al cerrar la sonda (~2026-06-26), con el motor de validación (compuerta C7).
- **Mecanismo económico:** los proveedores de liquidez algorítmicos retiran
  cotizaciones ante toxicidad creciente del flujo (Aït-Sahalia–Saglam; patrón
  del Flash Crash). Quien paga: el tomador que llega al libro ya vaciado y
  cruza un spread degradado. Alineada con la alerta VPIN del §8.2 — esto la
  convierte en hipótesis de investigación operacionalizada.
- **Anti-arbitraje:** anticipar evaporación no es una carrera de velocidad
  (sobrevive a latencia ×10) sino de información estructural del libro; los
  HFT la explotan PARA retirarse, no para corregir el precio — la ineficiencia
  recae sobre los tomadores lentos, que no pueden dejar de serlo.
- **PREDICCIÓN OBSERVABLE (CONGELADA 2026-06-21, ANTES de tocar el L2 propio):**
  - *Evento a predecir (SHOCK de liquidez), causal:* un instante t es un shock si en la ventana
    FORWARD [t, t+W] (W ≈ 5 s, ~40-50 snapshots a 100 ms) ocurre CUALQUIERA: (a) el spread relativo
    supera su **percentil-95 causal** (rolling estrictamente anterior, ventana ~1 h), o (b) la
    profundidad D_δ (δ=0,1 %, `book.depth_within`) cae por debajo de su **percentil-5 causal**.
    Los percentiles se estiman SOLO con historia anterior a t (sin look-ahead, como en `regime.py`).
  - *Predictor (señal adelantada), causal en t:* (i) toxicidad del flujo (VPIN adaptado /
    imbalance firmado normalizado, `toxicity.py`) y (ii) RESILIENCIA del libro (vida media de
    recuperación, `book.book_resilience`) — ambos sobre historia ESTRICTAMENTE anterior a t.
    Hipótesis: toxicidad ALTA + resiliencia BAJA preceden al shock.
  - *Predicción cuantitativa:* P[shock en [t,t+W] | toxicidad > P80 causal Y resiliencia < P20
    causal] **>** la incondicional. Métrica: **AUC** de la señal sobre el outcome forward.
  - *Control anidado OBLIGATORIO (anti-trampa "ya estaba fino"):* la señal debe aportar AUC POR
    ENCIMA del baseline del NIVEL contemporáneo (spread/profundidad actuales). Si añadir la señal
    no mejora el AUC sobre "el libro ya está fino ahora", NO anticipa nada → es nivel, no predicción.
- **CRITERIO DE FALSACIÓN (CONGELADO, ligado a la compuerta C7):** FALSADA si CUALQUIERA:
  (a) AUC de la señal sobre el shock forward **≤ 0,55** (apenas mejor que el azar);
  (b) NO supera el control anidado (ΔAUC sobre el baseline de nivel ≤ 0 → no aporta anticipación);
  (c) el poder predictivo se degrada **> 30 % a latencia ×10** (Plan §5.2 → era velocidad, archivar);
  (d) frecuencia de "alta toxicidad" o de shocks **< 1 %** del régimen (Plan §2.3): en 14 días los
  shocks son raros — si la masa es insuficiente, se EXTIENDE con L2 histórico de Tardis ANTES de
  concluir (jamás un veredicto con n ridículo);
  (e) no aguanta en AMBAS mitades de la muestra (REE/estabilidad).
- **DOS ETAPAS:** (1) *relación predictiva* (esta predicción + control anidado + latencia, sobre el
  L2 propio ya validado + trades) = el gate científico barato. (2) SOLO si pasa: convertirla en
  señal OPERABLE (taker que evita/retrasa cuando dispara, o maker que ensancha/retira — enlaza con
  H6) y pasar la **compuerta C7 completa** (CPCV φ≥9, DSR≥0,95, PBO≤0,10, BHY t≥3,2, viabilidad/
  costes) = el gate del dinero. *Honestidad:* confirmar que la señal ANTICIPA no es aún un edge —
  el dinero se decide en la etapa 2.
- **NOTA DE OPERACIONALIZACIÓN (2026-06-21, antes de tocar el dato).** Decisiones que *implementan*
  la predicción/falsación ya congeladas (no las cambian); registradas antes del L2. Código:
  `analysis/h1.py` + `analysis/h1_io.py` (entrada `run_h1_symbol`), 193/193 tests.
  - *Split de relojes (co-diseñado con Manuel; refs Databento ts_event/ts_recv, microestructura en
    event time):* la ETIQUETA (estado del libro y shock) vive en **`event_ts_ms`** — verdad de
    mercado, para no contaminar el shock con jitter de red propio; el INFORMATION SET, la latencia y
    la accionabilidad viven en **`recv`** (`lat_ms = recv − event`, base del test ×10). Refinamiento:
    en el tiempo de decisión t solo se conoce lo de `recv ≤ t`, y un shock es *legalmente anticipable*
    solo si `event_shock ≥ t + lat_modelada` (feed medido + envío modelado).
  - *Rejilla:* event-time regular de **1 s** por LOCF (casa W≈5 s y ventana≈1 h del pre-registro).
  - *Toxicidad (arquitectura OFI/VPIN, co-diseñada con Manuel; refs Cont-Kukanov-Stoikov 2014,
    Andersen-Bondarenko 2014):* predictor PRIMARIO = **OFI firmado de CKS** (3 ramas de movimiento
    del mejor precio, no ΔQ ingenuo) en **MLOFI** sobre los 5 primeros niveles, normalizado por
    profundidad, acumulado por celda de 1 s; se usa `|OFI|` (el shock es no-direccional). El **VPIN**
    pasa a **variable de RÉGIMEN** (no trigger): su MA(50) sobre cubos de volumen es estructuralmente
    lenta (~50 min) = telón de toxicidad, no señal a 5 s (pica *tras* el shock, Andersen-Bondarenko).
    `run_h1` reporta la INTERACCIÓN (¿predice mejor el OFI en régimen tóxico?). Dentro de la cláusula
    congelada "imbalance firmado normalizado" → sin deriva.
  - *Resiliencia:* **vida media de recuperación ROLLING** por-t (ventana trasera + stride) — captura
    la DINÁMICA de rebote, distinta del nivel, así que aporta señal que el control anidado no absorbe.
    **Corrección de signo (2026-06-21, pre-dato, revisión):** `resilience` = half-life (valor ALTO =
    recuperación lenta = libro FRÁGIL = resiliencia baja); la señal **SUMA** `z(resilience)` (frágil →
    más shock), alineado con "resiliencia baja precede al shock" del freeze. El código restaba (signo
    invertido) — corregido + test de regresión. No cambia la hipótesis, la implementa bien.
  - *Optimización:* el percentil de umbral se recalcula cada ~60 s + LOCF (`stride`); reduce coste,
    no cambia la semántica del percentil.
  - *VPIN (régimen):* `vpin_buckets_per_day=1440` (~1 bucket/min) + `n=50` (telón ~50 min), lado real
    del agresor (`is_buyer_maker`), forward-fill causal. Calibración por regla tiempo-volumen, NO
    ajustada a resultado. (El VPIN clásico de 50 buckets/día daba ~1 lectura/día = inútil.)
- **VALIDACIÓN EN DATO REAL + DISCIPLINA (2026-06-21).** Smoke test del pipeline sobre 1 día real
  (ATOM 2026-06-19, descargado read-only): ✅ cero libros bloqueados (captura limpia), ✅ latencia de
  feed sana (mediana 113 ms, p99 265 ms), ✅ resiliencia/toxicidad computan. 🔴 encontró y arregló el
  bug de granularidad de VPIN (todo-NaN → 84 k/86 k finito). **Disciplina de pre-registro:** ATOM
  2026-06-19 es dato de test; al correr el pipeline se vio el AUC del *baseline de nivel* (control),
  pero el AUC de la SEÑAL salió NaN (por el bug) → el resultado de H1 NO se vio. Para mantener el
  análisis final prístino: (a) NO se re-ajusta ningún umbral congelado a lo visto; (b) ATOM
  2026-06-19 se EXCLUYE del análisis final de H1 (1 de ~112 símbolo-días). El veredicto se computa el
  día 14 sobre la sonda completa con los criterios congelados.
- **Muerte esperada:** cambio en el mix de makers del símbolo (p. ej. programa
  de market making patrocinado) o compresión estructural de spreads.
- **EVR:** coste ≈ 2-3 semanas de análisis sobre datos ya capturados (0 € de
  datos). Valor si cierta: filtro de feasibility mejorado (§4.1) + feature de
  régimen — capacidad indirecta (mejora todas las estrategias tomadoras), no
  estimable en €/año por sí sola; prior pesimista declarado.
- **Resultado:** —
- **Qué aprendimos:** —
- **Alpha-decay (C3, Fase 7):** nacimiento — · Sharpe/capacidad inicial — ·
  degradación — · muerte/causa —

---

## H2 — Funding estructural de ATOM

- **Alta:** 2026-06-12 · **Estado:** propuesta
- **Observación origen (n=1):** funding medio -1,08 bps/8h = **-11,8 % anual
  sostenido durante 12 meses** (sonda histórica 2026-06-11, data_hist). Los
  cortos pagan a los largos de forma persistente.
- **⚠️ Cofundación registrada DE ANTEMANO:** ATOM tiene 8× menos volumen que
  LINK/AVAX (36 vs ~300 M$/día). El funding negativo persistente puede ser
  síntoma de mercado fino (prima de inventario/liquidez de la pata corta), no
  anomalía explotable. La plantilla exige separar ambas explicaciones con una
  predicción observable ANTES de mirar más datos.
- **Mecanismo económico:** PENDIENTE — candidatos a investigar: hedgers
  estructurales cortos (¿stakers de ATOM cubriendo?), restricciones de
  inventario de los makers en mercado fino. Sin mecanismo articulado, no entra
  al laboratorio.
- **Anti-arbitraje:** PENDIENTE — ¿por qué el carry largo-perp no se llena de
  capital? (candidatos: capacidad pequeña, riesgo de cola del subyacente,
  coste de oportunidad).
- **Predicción observable / falsación:** PENDIENTE de pre-registro completo.
  (Esbozo a formalizar: si es prima de liquidez, el funding debería correlacionar
  con D_10/spread del propio libro al tener L2; si es presión de hedgers, debería
  persistir controlando por liquidez y verse en OI.)
- **PRE-REGISTRO sub-test multi-venue (fijado 2026-06-12, ANTES de descargar
  datos de Bybit/OKX):**
  - *Sub-pregunta:* ¿el funding negativo es estructural del ACTIVO (aparece en
    todos los venues) o específico de Binance?
  - *Ventana y métrica:* 2025-06-01 → 2026-06-01 UTC. Funding anualizado =
    suma de tasas observadas en la ventana × (365 / días cubiertos) — agnóstico
    al intervalo de cada venue. El de Binance se recalcula con la MISMA fórmula
    sobre `data_hist/ATOMUSDT/fundingRate.parquet` (manzanas con manzanas).
  - *Predicción si estructural:* anualizado ≤ **-3 %** (≈¼ de la magnitud de
    Binance) en AMBOS venues: Bybit `ATOMUSDT` (linear) y OKX `ATOM-USDT-SWAP`.
  - *Falsación:* anualizado ≥ **-1 %** (≈cero o positivo) en al menos uno →
    explicación estructural TOCADA; en ambos → FALSADA (fenómeno específico de
    Binance: su microestructura, su base de usuarios o su mecánica de funding).
  - *Zona gris* (-3 %…-1 %): no concluyente; se documenta sin promover.
- **Muerte esperada:** entrada de capital de carry (funding → 0), cambio del
  régimen de staking, o listado en venues con más liquidez.
- **EVR:** coste ≈ 1 semana con datos ya disponibles (funding + trades
  históricos; OI descargable gratis). Valor si cierta: carry ~11 %/año bruto
  sobre capacidad limitada por el propio tamaño de ATOM — modesto; lo que la
  hace valiosa es su simpleza (pocas piezas móviles) como primera prueba
  completa del pipeline.
- **Resultado (sub-test multi-venue, 2026-06-12) → RECLASIFICADO a TOCADO por
  la auditoría quant-reviewer 2026-06-13 (ver bloque AUDITORÍA abajo; esta línea
  se conserva append-only como lo afirmado en su momento):** PREDICCIÓN CUMPLIDA
  con salvedad. Anualizado misma fórmula: Binance **-11,84 %** (1.095 fundings,
  364,7 d), Bybit **-8,94 %** (1.095, 364,7 d), OKX **-5,21 %** (241, **solo
  80 d** — su API pública no sirve más histórico: sub-ventana reciente, no la
  ventana completa). Ambos venues ≤ -3 % → compatible con funding estructural
  del ACTIVO; la evidencia fuerte es Bybit (ventana completa); OKX corrobora
  débil. Crudos: `data_hist/xvenue/`. Script: `analysis/h2_funding_xvenue.py`.
  Estado: sigue **en curso** (descarta "artefacto de Binance"; el mecanismo
  sigue pendiente).
- **Candidato a mecanismo (post-hoc, anotado 2026-06-12 — POR VERIFICAR, no
  promovido):** cobertura delta-neutral de stakers: largo spot stakeado
  (~15-20 % APR de staking de ATOM) + corto perp (paga el funding) = carry
  neto positivo → demanda estructural de cortos dispuesta a pagar.
  Verificación futura: funding ↔ staking APR histórico; y con los 14 días de
  L2, funding ↔ D_10/spread (separarlo de la prima de liquidez).
- **AUDITORÍA quant-reviewer (2026-06-13) — VEREDICTO: TOCADO.** Números
  reproducidos exactos y crudos verificados contra las APIs en vivo (el hecho
  empírico es sólido). Pero cuatro heridas rebajan el alcance:
  1. *Pre-registro no válido por proceso:* `git log -S "PRE-REGISTRO sub-test"`
     → vacío. El bloque se escribió ~90 s DESPUÉS de tener los crudos y nunca se
     commiteó antes. No es pre-registro (de ahí la REGLA DURA nueva arriba).
     Atenuante: el umbral -3 % se deriva solo de Binance y el resultado (-8,94 %)
     está lejísimos de él; no hay olor a umbral afinado para aprobar.
  2. *n efectivo ≈ 1, no 3:* el arbitraje de base acopla los venues. En la
     sub-ventana común de 80 d, Binance -5,20 % vs OKX -5,21 % (idénticos);
     r(Binance,Bybit) ≈ 0,88. Los "3 venues" son ≈ una observación del basis
     global de ATOM + espejos con fricción (la brecha anual de 2,9 pp
     Binance-Bybit prueba que el acople no es perfecto: n_eff entre 1 y 2).
  3. *Sobreclamación de alcance:* el test SOLO descarta "artefacto mecánico o de
     pipeline de Binance". NO descarta flujo originado en Binance y exportado por
     arbitraje, NI la cofundación de prima de mercado fino (ATOM es 8× menor en
     todos los venues — la prima de liquidez predice exactamente la misma firma
     cross-venue; INTACTA).
  4. *OKX inadmisible según protocolo:* la cantidad pre-registrada (anualizado
     de la ventana completa) es INMEDIBLE en OKX (su API solo da ~80 d desde
     2026-03-12). El -5,21 % es otra cantidad y, además, espejo de Binance →
     ~cero información independiente. Reclasificado: "no evaluable; espejo
     direccional en 80 d". El veredicto descansa solo en Bybit.
  5. *"Sostenido" es episódico:* solo 62,9 % de fundings negativos en Binance
     (55,5 % en Bybit, con 3 meses POSITIVOS jul-sep 2025); el 74 % de la
     magnitud anual se concentra en 4 meses (oct-nov 2025, feb-mar 2026); y los
     **2 últimos meses corren a ≈ -2 %/año** — dentro de la zona gris/falsación
     del propio pre-registro. El carry de ~11 % del EVR es media retrospectiva
     dominada por episodios; el run-rate ACTUAL es -2 a -5 %. La "muerte
     esperada (funding→0)" podría estar ya en curso.
- **Qué aprendimos:** (a) el funding negativo de ATOM no es un fallo de NUESTRO
  pipeline ni mecánica exclusiva de Binance — eso queda descartado. (b) NO está
  demostrado que sea "estructural del activo": el cross-venue, al estar acoplado
  por arbitraje, no añade la independencia que parecía. (c) Metodológico doble:
  fijar la ventana antes evita racionalizar; y un pre-registro sin commit es
  papel mojado (regla dura nueva). Tests que SÍ discriminarían (pendientes, no
  ejecutar aún): funding↔staking-APR histórico; corte transversal de monedas PoS
  de APR alto; funding↔OI/liquidez con `data_hist/*/metrics-*.parquet` (ya
  descargado) y con el L2 propio a los 14 días; y si los episodios oct-25 /
  feb-mar-26 coinciden con eventos de mercado generales o son propios de ATOM.
- **Estado:** **en curso, TOCADO.** Promoción a "viva" CONDICIONADA a (i) un
  pre-registro commiteado de uno de los tests discriminantes y (ii) telemetría
  de run-rate (el régimen reciente está en zona de falsación).
- **PRE-REGISTRO del test discriminante (mecanismo staking-hedge basis trade) —
  CONGELADO 2026-06-19 (hash de este commit), ANTES de descargar/cruzar APR/inflación/
  profundidad-stATOM con el funding. CIERRA la condición (i). Identificación
  co-desarrollada con el propietario (fuentes on-chain + el diseño intra-ATOM con
  instrumento de gobernanza).**
  - *Mecanismo (afinado):* el funding negativo de ATOM es el PRECIO DE EQUILIBRIO del
    basis trade staking-hedge (largo stATOM cobrando ~13-17% APR + corto perp pagando
    funding). En equilibrio funding ≈ staking_yield − prima_de_riesgo(iliquidez/unbonding
    21d) → el funding se hace MÁS negativo cuando el carry es más explotable (APR alto ×
    LST profundo) y MENOS cuando el hedge no escala (LST fino). NO es anomalía arbitrable,
    es el precio. **Implicación honesta:** confirmarlo valida el MECANISMO y el método,
    NO entrega edge (el funding ya está priceado); el edge, si existe, está aguas abajo
    (masificación/desmasificación del carry, o prima de unbonding mal valorada).
  - *Exposición declarada:* vistos los NIVELES de funding ATOM/Bybit/OKX (sub-test
    multi-venue). NO examinada ninguna relación funding↔APR/profundidad, ni el gradiente
    cross-coin, ni nada alrededor de las fechas de los Props.
  - *Identificación PRIMARIA — within-ATOM, 2SLS con instrumento casi-exógeno:*
    funding_residual_ATOM ~ β·(inflación × profundidad_stATOM) + controles, con
    funding_residual = funding ATOM − factor de mercado (cesta BTC/ETH). La profundidad
    realizada del pool es ENDÓGENA (funding muy negativo → carry más jugoso → más hedging
    → más demanda de profundidad); se INSTRUMENTA con las inyecciones de POL de gobernanza
    del Cosmos Hub —Prop 800 (jun-2023, 450k ATOM) y Prop 858 (oct-2023, 900k ATOM, pool
    #1136)—, shocks discretos casi-exógenos al funding del perp (2SLS + event-study del
    funding_residual alrededor de esas fechas). Se usa la INFLACIÓN (schedule de
    protocolo, cuasi-exógena) y NO el APR realizado (=inflación/staked_ratio×0.9, con
    staked_ratio endógeno al yield). Predicción: **β < 0** y discontinuidad del funding
    alrededor de los Props. TIA/INJ DESCARTADOS como turn-off limpio (TIA: "APR alto" era
    prima de airdrop, no inflación → no exógeno, + cliff unlock oct-2024 contamina; INJ:
    pool stINJ marginal hasta 2025) → solo gradiente auxiliar.
  - *Confirmación SECUNDARIA — dosis-respuesta cross-coin:* panel efectos fijos de dos
    vías {BTC, ETH, DOT, ATOM} × semana (semana-FE = régimen de mercado; moneda-FE =
    nivel). Orden PRE-COMPROMETIDO de |sesgo negativo del funding_residual|: BTC≈0 <
    ETH(débil, ~3-4% + stETH) < ATOM(fuerte). TIA/INJ solo auxiliar (nota stack incompleto).
  - *Controles:* momentum/tendencia de precio (en un token que cae, los cortos
    direccionales hunden el funding solos = explicación rival), OI/cap, % staked, dummies
    de unlock, liquidez del perp.
  - *Falsación (PRE-FIJADA):* FALLA si CUALQUIERA: (a) β no significativamente negativo
    tras controles (sobre todo momentum + factor de mercado); (b) event-study plano
    alrededor de Prop 800/858; (c) el orden dosis-respuesta se invierte o BTC muestra el
    efecto; (d) no aguanta en ambas mitades. *Ambigüedad declarada:* un null puede ser
    "sin mecanismo" O "la residualización se llevó la señal" O "exclusion restriction
    violada" (los Props movieron sentimiento/precio por un canal ≠ profundidad) → se
    reporta un PLACEBO (¿movieron los Props el precio de ATOM fuera del canal de carry?)
    para acotar cuál.
  - *Datos (fuentes ya localizadas por el propietario):* funding ATOM/BTC/ETH/DOT/TIA/INJ
    (tenemos ATOM; resto descargable); APR/inflación/%staked vía CF Benchmarks + REST
    Cosmos (x/mint, x/staking) + Staking Rewards (ATOMSRB); profundidad stATOM vía
    DeFiLlama (api.llama.fi) + pools Osmosis #803/#1136; fechas de Props (gobernanza,
    fijas); calendario de unlocks. Remuestrear a diario antes de cruzar.
  - *EVR:* coste ≈ días, fuentes gratuitas. Valor: cierra H2 y es el PRIMER test del
    laboratorio con identificación casi-experimental real (instrumento de gobernanza) —
    prueba de que la máquina puede hacer causalidad, no solo correlación.
- **REVISIÓN v2 del test discriminante — CONGELADA 2026-06-20, ANTES del 2SLS definitivo.
  Correcciones de verificación ON-CHAIN INDEPENDIENTE del propietario (timestamps de
  voting end), NO de los resultados — corrigen un error fáctico de fecha. (Transparencia:
  la etapa-1 forma reducida SÍ se corrió antes, con fecha APROXIMADA de Prop 858 —
  dosis-respuesta a favor, Prop 800 a favor, Prop 858@oct-1 en contra/confundido; el 2SLS
  estructural definitivo NO se ha corrido. Estas correcciones NO se eligieron para ajustar
  ese resultado.):**
  - *Fechas exactas (corrigen "oct-2023"):* Prop 800 ejecutada **2023-06-28** (voting end
    06-27T15:18:13Z), pool #803. Prop 858 ejecutada **2023-12-16/17** (voting end
    12-16T23:57:26Z; spike TVL +$4.9M al día siguiente), pool concentrado #1136.
    Redirección de incentivos #803→#1136: 2024-01-14.
  - *NUEVO confounder Y segundo instrumento — Prop 848* (max inflación 20%→10%, voting end
    **2023-11-25**), 21 días ANTES de 858 → shock de YIELD a la baja, predicción OPUESTA a
    la de profundidad (menos yield → menos hedge → funding MENOS negativo). (a) Ventana
    PRE-COMPROMETIDA del event-study de 858: pre=[−60,−30], post=[0,+30] respecto a
    2023-12-16, para NO contaminar con 848. (b) Prop 848 se explota como SEGUNDO
    instrumento (yield-down) con su propio event-study de signo opuesto pre-comprometido.
  - *Neutralización BETA-AJUSTADA (no resta simple):* la etapa-1 mostró que restar BTC con
    β=1 deja beta residual (ATOM sube más que BTC en el bull → falso "menos negativo"). Se
    regresa funding ATOM sobre funding BTC (y ETH) y se usan los RESIDUOS; momentum/
    tendencia de precio como control obligatorio.
  - *Inflación DETERMINISTA (no hace falta serie histórica de inflación):* es función del
    bonded_ratio + mint params. APR = inflación/bonded_ratio×0.98 (2% community tax);
    inflación_max = 20% hasta 2023-11-25 y 10% después (Prop 848). Solo se necesita la
    serie de **bonded_ratio** (Flipside `cosmos.core.fact_staking` o Numia BigQuery, gratis).
  - *Profundidad stATOM (instrumentada):* proxy = ATOM en custodia de Stride vía DeFiLlama
    `api.llama.fi/protocol/stride` → tokensInUsd→ATOM (2022→2023, gratis, sin auth; clave
    verificada: 2023-06-28 $25.8M, 2023-12-16 $43.4M→$48.3M); pools Osmosis #803/#1136 vía
    yields.llama.fi (2024+).
  - El resto (primario within-ATOM 2SLS, dosis-respuesta secundaria, falsación, placebo de
    exclusion restriction) se hereda. Co-desarrollado con el propietario.
- **RESULTADO (forma reducida BETA-AJUSTADA, 2026-06-20; el 2SLS estructural con depth
  pool-level + bonded_ratio sigue pendiente) → INCLINA A FALSACIÓN:** datos DeFiLlama
  validados (ATOM-in-Stride $25.5M en Prop 800, $48.8M en 2023-12-16, cuadran con la
  verificación on-chain). Beta de ATOM al régimen de funding cripto = **1.42** (no 1): la
  resta simple de BTC de la etapa-1 dejaba beta residual → falso "Prop 800 a favor". Con
  beta-ajuste + fechas buenas + ventanas pre-comprometidas, las predicciones de PROFUNDIDAD
  NO se cumplen: Prop 800 Δ=+0.8 %, Prop 858 Δ=+0.9 % (ambas predecían Δ<0);
  corr(funding_residual, log TVL-proxy)=+0.05 (predecía <0). Solo el shock de YIELD (Prop
  848, Δ=+1.9 %) es débilmente consistente. **El canal de profundidad del staking-hedge
  NO aparece en la forma reducida bien hecha** (criterio b → falsación). La dosis-respuesta
  (ATOM tiene funding estructuralmente más negativo) es REAL, pero su causa NO se confirma
  como el carry de staking. *Salvedades antes del veredicto final:* (1) el proxy es TVL
  AGREGADO de Stride, no la profundidad NEGOCIABLE del pool (#803/#1136) — posible medida
  equivocada; (2) falta el 2SLS con inflación×depth + control de momentum. Decisión
  pendiente: completar el 2SLS (depth pool-level + bonded_ratio) o aceptar la inclinación
  negativa. Código: `analysis/h2_staking.py`.
- **VEREDICTO con profundidad POOL-LEVEL (2026-06-20; datos del propietario, DeFiLlama
  yields pool #803 continuo sep-2022→hoy) → MECANISMO FALSADO (canal de profundidad).**
  La salvedad del proxy queda cerrada y el resultado se ENDURECE, por dos razones
  independientes:
  1. *PRIMERA ETAPA FALLA (instrumento irrelevante):* los Props NO movieron la profundidad
     negociable. Prop 800 inyectó 450k ATOM al #803 pero su TVL CAYÓ −16% ($26.5M→$22.4M);
     Prop 858 fue al #1136 (sin tracking hasta ene-2024) → primera etapa inmedible y #803
     quedó plano (−1%). Sin primera etapa, el IV de gobernanza —la identificación elegante—
     colapsa: el instrumento no mueve la variable instrumentada.
  2. *CONTINUO de signo OPUESTO:* corr(funding_residual, log profundidad #803)=**+0.13**
     (n=1336; predecía <0); patrón por cuartiles no-monótono (Q1 baja-profundidad el más
     negativo, confundido con el bear 2022). Más profundidad NO da funding más negativo.
  **Conclusión:** el carry staking-hedge (carry = APR × profundidad) NO explica el funding
  negativo de ATOM — la profundidad, la pieza que escala el hedge, ni la mueven los Props ni
  covaría en el signo predicho. La dosis-respuesta (ATOM funding estructuralmente más
  negativo) sigue siendo un HECHO, pero su CAUSA queda sin identificar (candidatos abiertos:
  bajismo estructural, short interest persistente, otros carries). Único hilo no-falsado: el
  canal de YIELD (Prop 848, débil), que necesitaría el 2SLS con bonded_ratio — prior bajo
  (sin profundidad el hedge no escala). El dato pool-level del propietario (+ su detección
  del gap de tracking de #1136) hizo el veredicto DECISIVO, no un "inclina a".
- **Estado:** TOCADO → **mecanismo staking-hedge FALSADO (canal de profundidad).** El hecho
  empírico (funding negativo) persiste sin mecanismo confirmado → NO promover. Cierra el
  ciclo del test discriminante. Aprendido: identificación causal real ejecutada de punta a
  punta; el instrumento de gobernanza falló la primera etapa (razón sofisticada que la
  mayoría no comprobaría) → rechazo limpio. La máquina hizo causalidad, no correlación.
- **DISPOSICIÓN DE ENTIERRO (2026-06-22, trío convergido) — NO se re-entierra; se cosecha el residuo.**
  Matar barato = NO construir panel de dos vías + event-study Prop 848 + serie ICS para certificar un
  muerto. H2 queda CERRADA tal cual (TOCADO/falsada, +0,13 *wrong-sign*). **H2 ≡ H7** (misma tesis:
  "el staking del Cosmos Hub deja huella micro tradable") → enterradas JUNTAS, sin gastar más pólvora.
  El ÚNICO trabajo (post-día-14, $0, en cola DETRÁS de H8-soledad y ejecución): **caracterización
  EXPLORATORIA del régimen de funding del ladder** — gradiente de yield DENTRO de los 8 (ATOM~15% /
  DOT~8% / AVAX~7% / NEAR~5% / LINK~4,5% vs ceros limpios LTC PoW + UNI gobernanza), skew/persistencia/
  profundidad de cola — para alimentar la **prima #2 (funding carry)** y el overlay de cola de H3.
  Vive en los 12 meses que ya tenemos (jun-2025→); **CERO pull** (al soltar Prop 848 desaparece el
  agujero de dato). **REGLAS DURAS (de la convergencia):** (a) *cicatriz de H5 baked-in* — toda
  comparación de funding neutraliza el factor común y sobrevive el mismo test-D que mató a H5, o es
  alt-beta otra vez; cesta de neutralización = SOLO nombres SIN yield (LTC/UNI/BTC), NUNCA el gradiente
  (circular), NUNCA ETH (su funding lleva el basis stETH = el propio mecanismo). (b) *línea roja
  anti-lavado* — exploratoria mientras sea DESCRIPTIVA; en el instante en que un número de funding
  dimensione o gatee la #2 VIVA → **pre-registro + gate de neutralización de H5 obligatorios** (como
  H8). (c) *asimetría de un sentido* — un negativo confirma el entierro gratis; un positivo NO
  resucita H2 (claim direccional con perdedor con nombre, muerto pase lo que pase) → se apunta como
  una LÍNEA en esta entrada CERRADA, jamás reapertura.
- **Alpha-decay (C3, Fase 7):** nacimiento — · Sharpe/capacidad inicial — ·
  degradación — · muerte/causa —

---

## H3 — Cascadas de liquidación en perpetuos finos  (idea I3 de IDEAS_LAB)

- **Alta:** 2026-06-16 · **Estado:** PRE-REGISTRO CONGELADO — **NO ejecutar antes
  del día 14 de captura (~2026-06-26)**, cuando exista el L2 propio.
- **Por qué se pre-registra HOY y no el día 14 (REGLA DURA):** el dato de TEST
  (nuestro L2 depth@100ms, del que sale el outcome) NO existe aún → congelar la
  predicción y la falsación hoy, con el hash de este commit como autoridad de
  fecha, es la forma MÁS limpia de pre-registro (cero margen para afinar umbrales
  tras ver el resultado). Cualquier cambio a los buckets o umbrales DESPUÉS de
  este commit cuenta como hipótesis nueva (C1.4) y reinicia el reloj.
- **Honestidad sobre qué se ha visto ya** (para el quant-reviewer): inputs YA
  VISTOS = OI 5min + ratios long/short (`data_hist/*/metrics-*.parquet`, 12
  meses), funding, precio (aggTrades). Input NO VISTO hasta el día 14 = el L2
  propio (D_10, spread, drift forward por nivel). El OUTCOME del test (¿predice
  el drift adverso?) está en el dato no visto. Los umbrales de abajo **se toman
  tal cual de la constitución del Plan (Apéndice A)**, no se ajustan a este caso.

### Plantilla C1
1. **Mecanismo económico:** una liquidación forzosa es una orden a mercado de
   signo conocido (largos liquidados → ventas forzadas) que golpea un libro fino
   → impacto desproporcionado → puede disparar más liquidaciones (cascada). Quien
   pierde: el trader sobreapalancado liquidado, que transacciona a precio pésimo y
   **no puede evitarlo** (es mecánico, dirigido por el margen, price-insensitive).
   Quien cobra: quien provee liquidez a la cascada o se posiciona para la
   continuación, capturando el descuento de la venta forzada.
2. **Anti-arbitraje:** capacidad acotada por el propio libro fino (no cabe mucho
   capital); requiere L2 en tiempo real + estimación de OI; los HFT de élite no
   bajan a ATOM/FIL/DOT (Plan 1.1, competencia mínima). La ineficiencia persiste
   porque el flujo forzado es insensible al precio y el capital absorbente es poco.
3. **Predicción observable (CONGELADA):** se estiman niveles de liquidación de
   largos por debajo del precio desde OI + un modelo de apalancamiento PRE-FIJADO
   (tramos {10×, 25×, 50×, 100×}, precio de entrada ≈ VWAP causal de las últimas
   24 h, ponderado por el cambio de OI en cada tramo). Condición C = (a) `D_10` <
   percentil-5 causal del régimen activo (libro fino) **Y** (b) precio dentro de
   δ = 0,5 % de un cluster de liquidación estimado por debajo. Predicción: bajo C,
   el retorno forward a k ticks (k∈{5,10,20,50}, medido al ritmo de 100 ms) tiene
   **drift negativo** (continuación a la baja) que **excede** al drift incondicional.
   Simétrico para cortos/al alza.
4. **Criterio de falsación (CONGELADO, umbrales de la constitución del Plan):**
   FALSADA si se cumple CUALQUIERA de:
   - El efecto NO supera, en un **modelo anidado**, lo que ya explica la finura del
     libro por sí sola (control: `D_10` bajo SIN proximidad a cluster). Es decir,
     la proximidad al cluster debe aportar poder predictivo ADICIONAL — si el
     drift condicionado a (a)+(b) ≈ el condicionado solo a (a), la cascada no
     añade nada y la "señal" era solo impacto en libro fino (cofundación, FALSADA).
   - Cohen's d del exceso de drift (condicional vs incondicional) **< 0,2** (umbral
     del Plan para "efecto pequeño pero real", Apéndice A / §2.4).
   - REE entre 5 bloques temporales **< 1,5** (Plan §2.4: efecto inestable).
   - El exceso **se degrada > 30 % al multiplicar la latencia ×10** (Plan §5.2):
     sería un edge de velocidad disfrazado de cascada → archivar.
   - Frecuencia de la condición C **< 1 %** de las observaciones del régimen (Plan
     §2.3: masa estadística insuficiente).
   *Ambigüedad declarada de antemano:* un FALSADA por el modelo anidado puede
   significar "no hay efecto" O "la estimación de clusters desde OI es demasiado
   ruidosa". No se podrá distinguir sin datos de liquidación reales (`@forceOrder`,
   que NO capturamos hoy — añadirlo es post-sonda, jamás durante los 14 días).
   - **FORTALECIMIENTO DEL PRE-REGISTRO (2026-06-21, antes del L2 — ENDURECE el test, no lo
     afloja; co-diseñado con Manuel).** El control anidado congelado aísla la proximidad-a-cluster
     de la FINURA del libro (`D_10`), pero NO del **factor de mercado común** (desapalancamiento
     market-wide: la cesta cae → todo driftea junto → beta, no cascada idiosincrática). **Es el
     confound que mató a H5.** Se AÑADE a la falsación: el exceso de drift bajo C debe sobrevivir a
     la **neutralización por factor de mercado** — residualizar el drift forward del símbolo contra
     la cesta **leave-one-out** de los otros 7, con **β CAUSAL** (estrictamente anterior; no la β
     in-sample de `xsection.neutralize`, que tendría look-ahead en un test predictivo). Si el exceso
     de drift desaparece al neutralizar → era beta de mercado → **FALSADA**. Como SOLO endurece el
     test y se fija ANTES del dato, es fortalecimiento legítimo, no movimiento de portería. *Caveat
     honesto:* el factor es la cesta de nuestros 8 finos (no capturamos BTC); proxy del componente
     común, BTC sería más limpio. Código: `analysis/h3.py` (loo_basket, causal_beta,
     neutralized_forward_panel), 5 tests; clave validada: anula el mercado, conserva lo idiosincrático.
   - **HARNESS DE CLUSTERS (operacionalización, 2026-06-21, antes del dato).** Implementa la
     predicción/falsación congeladas; supuestos PRE-FIJADOS y declarados (no ajustados al resultado):
     (i) precio de liquidación `P·(1−1/L)` por tramo {10,25,50,100}× (SIN margen de mantenimiento —
     fiel al freeze); (ii) entrada ≈ VWAP causal de ventana trasera; (iii) combustible = acumulación
     NETA de OI en la ventana (`max(OI_t−OI_{t−w},0)`, operacionaliza "cambio de OI"); (iv) la
     condición C es de PROXIMIDAD (≤δ=0,5 % de un cluster) → la ponderación de apalancamiento NO la
     gatilla (las weights/crowding L/S quedan para un diagnóstico de tamaño, no congelado). `run_h3`
     evalúa los 6 criterios: (1) control anidado cluster-vs-finura, (2) |d|≥0,2 vs incondicional,
     (3) sobrevive a neutralizar mercado, (4) REE≥1,5, (5) latencia ≤30 %, (6) frecuencia C≥1 %.
     **REE CONFIRMADA por Manuel** (= `|media|/desv` entre bloques ≥1,5; razón de estabilidad
     estándar, variante del signal-to-noise entre bloques). Parámetros de instanciación PINCHADOS
     (son "constitución", se fijan antes del dato): (a) *bloque* = 5 ventanas temporales contiguas de
     igual longitud por símbolo (NO por episodio: las cascadas son raras → n ridículo); bloques con
     <2 obs de C se descartan; (b) *x̄* = la Cohen's d ADVERSA del drift condicional vs incondicional
     (mismo estadístico que el efecto primario, coherencia; no magnitud bruta ni coef. de OFI); (c)
     *dirección* = REE<1,5 ⇒ FALSADA de H3 (uno de los 6 criterios OR del freeze). Código
     `analysis/h3.py` (causal_vwap, liquidation_clusters, near_cluster, oi_buildup, condition_C,
     cohens_d, ree, run_h3), 13 tests; guardarraíl: nulo→FALSADA, idiosincrática→detectada,
     mercado→muere al neutralizar. Falta solo la capa IO (cargar L2+OI+trades) para el día 14.
   - **BLINDAJE DE REPORTING (3ª revisión, pre-dato):** "Un primer probe de 14 días solo puede
     ejercer una función de SCREEN para H3. Ningún resultado en esta ventana, por sí solo, se
     interpreta como evidencia duradera a favor o en contra; el veredicto requiere observar un número
     material de cascadas en probes adicionales." N_eff(H3) ≈ nº de cascadas ≈ 0-2 en 14 días → el
     día 14 dará casi seguro "masa insuficiente / inconcluso", y eso NO es fracaso, es el N diciendo
     la verdad. (Disciplina general: docs/RUNNER_DESIGN.md.)
   - **4ª MITIGACIÓN ADOPTADA — cross-check funding+OI (2026-06-22, pre-dato):** robustez al ruido de
     OI (Guo et al.: OI mal-reportado en >70% de intervalos de 1 min). `crowded_positioning` confirma
     un cluster solo si el funding es persistente del signo correcto (largos crowded → funding>0, los
     largos PAGAN) Y la OI sube. Se reporta el efecto de H3 bajo C vs C∩confirmación: si el edge solo
     vive en clusters CONFIRMADOS por funding, son más creíbles (se aísla del ruido de OI puro).
     Diagnóstico de robustez, NO cambia la falsación congelada. Código: `h3.crowded_positioning`,
     test. Enlaza con el rumbo (VISION 2026-06-22): H3 como overlay de riesgo del funding carry.
5. **Muerte esperada:** Binance cambia la mecánica de liquidación (liquidación
   parcial, ADL); los símbolos ganan liquidez (más capital absorbente → cascadas
   amortiguadas); o se llena de gente cazando los mismos clusters (crowding →
   el descuento desaparece). Alimenta la telemetría de §8.1.
6. **EVR:** *Coste* ≈ 10-15 días (modelo de estimación de clusters + test anidado
   + control de latencia + masa estadística), sobre datos ya disponibles + el L2
   de los 14 días. *Valor si cierta:* capacidad limitada por el tamaño de los
   símbolos finos (modesto en €/año), pero es el **camino más limpio a un primer
   edge real** porque tiene mecanismo económico verdadero y vive donde hay menos
   competencia (Plan 1.1). Prior pesimista declarado.
- **Resultado (multi-año CHD, 2026-07-01) → SCREEN-INCONCLUSO-POR-MASA (criterio 6). NO reconstruido:
  cerrado por PRE-CHECK, no por el screen completo.** Tras el contrarian NEGATIVE, H3 pasó a frente activo.
  Pre-check de potencia en dos capas (análogo a `episode_count`; miró SOLO los condicionantes, jamás el
  drift-outcome → held-out de H3 INTACTO):
  1. *Setup abundante:* `near_cluster(VWAP24h)+oi_buildup` dispara al **8,25%** (OI+precio 12m; `h3_power_precheck.py`)
     → ~711 episodios independientes cross-asset. El miedo de la cola ("8-15 cascadas") era error de encuadre
     (confundía N del outcome con N del setup). En N de episodios, H3 parecía testeable.
  2. *Pero el filtro libro-fino mata la MASA:* sobre los 14 días del probe (L2 real → D_10), `fino=D_10<P5` y
     `setup` son **~independientes** (lift 0,88), recorte ~14× → **freq(C) = 0,57%**, por DEBAJO del suelo
     frozen del criterio 6 (`freq < 1% → masa insuficiente`). Robusto: setup estable (8,26% probe ≈ 8,25% 12m,
     con estrés capturado), fino es percentil P5 (regime-estable), independientes → freq(C) ≈ 0,4-0,6% en todo
     régimen. El filtro fino salió *flojo* (7,84% vs 5% objetivo) → con P5 exacto freq(C) bajaría a ~0,36%,
     fallando MÁS. Evidencia: `analysis/h3_power_precheck.py` + pre-check probe (scratchpad, commit del cierre).
  **DECISIÓN: no gastar la reconstrucción (~4-6h).** freq(C) es una tasa estable; reconstruir no la subiría
  salvo que jun-2025→jun-2026 fuera atípicamente tranquilo EN la dimensión fino+cluster+OI simultánea —
  improbable con 12m de regímenes variados. Apostar 4-6h a "improbable" no es la disciplina del proyecto (la
  misma lógica del pre-check: no gastar cómputo caro en algo que va a fallar). **Categoría distinta de
  SCREEN-NEGATIVE:** el contrarian fue TESTEABLE y no superó costes (efecto ausente/insuficiente); H3 es
  **INCONCLUSO** — el mecanismo PUEDE existir, pero la condición C es demasiado rara (freq 0,57%) para testearla
  con esta infra/ventana. No se falsó el mecanismo; se declaró intesteable por masa. Held-out del drift SIN gastar.
- **Qué aprendimos (LECCIÓN METODOLÓGICA, para el próximo pre-registro de H3-equivalentes):** el criterio de
  masa frozen (`freq(C) < 1% de observaciones → insuficiente`) está **mal calibrado para multi-año**: como
  FRACCIÓN, 0,57% suena poco, pero 0,57% de 12m ≈ 49 episodios independientes = masa ABSOLUTA potencialmente
  testeable. El suelo correcto es **N_eff ABSOLUTO ≥ X (p.ej. ≥30-50 episodios independientes), NO una
  fracción.** PERO cambiarlo AHORA (visto ya freq=0,57%) sería mover la portería (aflojar §7) → NO se toca el
  criterio de H3; la corrección se hereda al DISEÑO del próximo mecanismo episódico. Segunda lección: separar
  N-del-setup de N-del-outcome ANTES de gastar cómputo (el pre-check en dos capas fue lo que lo cazó barato).
- **Disposición:** **H3 CERRADA — SCREEN-INCONCLUSO-POR-MASA.** No promover, no reconstruir. Frente activo pasa
  a **#4 (cross-asset lead-lag)**, cuyo perfil es el OPUESTO: N abundante por construcción (cada par genera
  señal continua, no episodios raros); su riesgo es overfitting de lookback / cointegración espuria, atacable
  con el rigor ya rodado. $0 gastados en H3 (ni un byte de reconstrucción).
- **Alpha-decay (C3, Fase 7):** nacimiento — · Sharpe/capacidad inicial — ·
  degradación — · muerte/causa —

---

## H4 — Critical Slowing Down como aviso de ruptura de liquidez  (idea I9)

- **Alta:** 2026-06-16 · **Estado:** ANOTADA, **NO pre-registrada** (a propósito).
- **Por qué no se pre-registra aún:** la validación exige observar muchas
  transiciones de régimen, y en 14 días hay poquísimas → se necesita la masa de
  12-18 meses de L2 propio (Plan §1.5) antes de fijar predicción/falsación. Pre-
  registrar con 14 días sería garantizar un n efectivo ridículo.
- **Núcleo a desarrollar (cuando haya datos):** las 3 señales universales de la
  teoría de bifurcaciones (varianza inter-evento ↑, autocorrelación lag-1 ↑,
  tiempo de retorno del precio ↑) deberían dispararse ANTES de una ruptura de
  liquidez. Mecanismo económico (a articular): los makers se retiran ante toxicidad
  → el libro pierde capacidad de absorción → resiliencia decreciente (enlaza con
  VPIN/§8.2 y con H1). Reto sin resolver: CSD avisa de que VIENE una transición,
  no de la DIRECCIÓN — sin dirección no hay dinero. Track record predictivo de CSD
  en mercados: pobre (muchos falsos positivos). Cuidado con el look-ahead al
  etiquetar qué fue "transición".
- **Convergencia:** H3, el núcleo de H2 (mecanismo) y H4 apuntan al mismo sitio —
  la dinámica de liquidez en instrumentos finos. No es casualidad: es donde hay
  mecanismo real y competencia mínima (Plan 1.1).

---

## H5 — Lead-lag de retirada de liquidez en la cesta  (idea-buque; ver docs/VISION.md)

- **Alta:** 2026-06-16 · **Estado:** ANOTADA, **NO pre-registrada** (necesita meses
  de L2 cross-sectional; con 14 días el n efectivo de eventos de liquidez es
  ridículo). Es la concreción de la tesis rectora de `docs/VISION.md`.
- **Hipótesis (a formalizar cuando haya datos):** la retirada de liquidez está
  correlacionada entre los 8 nombres (los makers corren modelos de inventario/riesgo
  COMPARTIDOS sobre la cesta), y los nombres más líquidos (LINK, AVAX) **lideran** a
  los más finos (ATOM, FIL) por un retardo medible a 100 ms — porque el maker retira
  primero donde tiene más exposición/mejor señal y después abandona los finos
  correlacionados.
- **Mecanismo económico (borrador):** pierde el taker lento en el nombre fino que
  cruza el spread justo cuando el libro ya se vació pero el precio aún no lo refleja;
  o el maker que llega tarde a retirar. Ganas viendo el libro de LINK adelgazar y
  anticipando el de ATOM. Contraparte estructural (atención/capital del maker
  repartidos). NO es carrera de microsegundos SI el retardo es >100 ms-segundos
  (plausible justo en finos, donde la lentitud es nuestra aliada).
- **Por qué es exclusivamente nuestra:** requiere los 8 libros L2 a la vez. Un HFT no
  baja a estos nombres; un retail no tiene la infra. Nosotros sí.
- **Las 4 formas de morir (a pre-registrar contra ellas, NO ahora):**
  1. Es solo **beta de cripto** → controlar por el factor común; si el lead-lag
     muere al neutralizar BTC/mercado, FALSADA.
  2. **Carrera de latencia** → si muere a ×10 latencia, era velocidad, archivar (§5.2).
  3. **n efectivo bajo** (eventos raros/agrupados) → submuestreo independiente; necesita
     meses (§1.5).
  4. **Cofundación con H3** → separar "retirada liderada por la cesta" de "cascada
     idiosincrática"; control anidado (cesta+nombre vs nombre solo).
- **EVR (preliminar):** coste alto (modelo cross-sectional + meta-labeling), pero es
  el edge candidato más alineado con la tesis rectora y el menos competido. Datos:
  necesita meses de L2 propio + bookTicker (mid real, ver ROADMAP) para evitar el
  bid-ask bounce.
- **PRE-REGISTRO sub-test de FEASIBILITY cross-sectional (trade-level) — CONGELADO
  2026-06-19 (hash de este commit), ANTES de ejecutar ningún análisis cross-sectional:**
  - *Qué es y qué NO es:* NO evalúa H5 (que necesita L2 + meses; sigue SIN
    pre-registrar). Es una PUERTA de viabilidad (§4.1) sobre los 12 meses de
    `aggTrades` que YA tenemos (solo trades, sin L2): ¿queda estructura cross-sectional
    residual entre los 8 nombres TRAS neutralizar el factor común? Condición
    ~necesaria, no suficiente: si ni a nivel de trade y con 12 meses la hay, el prior
    de H5 (mucho más caro: L2, meses, infra R1/R4) se desploma.
  - *Honestidad de exposición (para el quant-reviewer):* ya se vieron barras/curtosis/
    régimen de AVAX (trades de 1 símbolo); NO se ha mirado NINGUNA relación
    cross-sectional ni lead-lag. El outcome de este test está sin examinar.
  - *Muestreo — Reloj de Información Cross-Sectional (CSIC):* una barra del panel
    cierra cuando el dólar AGREGADO de los 8 alcanza V* (fijado para ~100 barras/día
    sobre la ventana común solapada). Los 8 se muestrean en los MISMOS límites (panel
    síncrono). Por nombre y barra: flujo firmado normalizado f = Σ(b·v)/Σv (OFI) y
    retorno log close-to-close r.
  - *Neutralización del factor de mercado:* residualizar cada nombre contra la cesta
    equiponderada de los OTROS 7 (leave-one-out, sin sesgo mecánico de auto-resta):
    r̃_{i,t} = r_{i,t} − β_i·b^{(-i)}_t, β_i por OLS sobre la ventana. Es un probe
    ESTRUCTURAL in-sample, NO un backtest (la versión causal/CPCV solo si pasa); el
    nulo de abajo se computa idéntico, así que cualquier inflación in-sample está
    también en el nulo. Igual para el flujo.
  - *Estadístico:* matriz dirigida 8×8 ρ_{i→j} = corr(f̃_{i,t}, r̃_{j,t+1}). S = media
    de ρ² sobre los 56 pares dirigidos fuera de la diagonal.
  - *Nulo (comparaciones múltiples + pesca in-sample):* 1.000 desplazamientos
    circulares aleatorios del tiempo del predictor; se recomputa S → distribución nula.
  - *Falsación (PRE-FIJADA):*
    · FALLA (cross-sectional DESPRIORIZADO) si S < percentil-95 del nulo (ruido).
    · PASA (luz verde al programa L2) si S > percentil-99 del nulo **Y** ≥5 pares
      dirigidos superan su propio percentil-99 **Y** el efecto aparece en AMBAS
      mitades (primeros vs últimos 6 meses; estabilidad estilo REE §2.4).
    · ZONA GRIS (en medio, o solo en una mitad): no concluyente, no promueve.
  - *Asimetría de conclusiones (declarada):* PASA NO prueba H5 (trade-level, in-sample,
    sin L2, sin costes) — solo justifica invertir en el L2. FALLA es más informativo:
    evidencia fuerte de que la estructura cross-sectional es sobre todo beta de BTC →
    pivotar a liquidez single-name (H1/H3) y al reencuadre "predecir liquidez/toxicidad".
  - *EVR:* coste ≈ pocos días sobre datos ya descargados; valor = altísimo (decide si
    comprometer meses + infra R1/R4 en la tesis rectora). El test más barato del bet
    más caro.
- **REVISIÓN del pre-registro (v2) — CONGELADA 2026-06-19, ANTES de ejecutar. Supera a
  la v1 de arriba; git PRUEBA que no se ejecutó análisis entre ambas (no hay commit de
  datos/código cross-sectional entre el de v1 y el de v2). La v1 se conserva append-only
  como lo afirmado en su momento:**
  - *Por qué se revisa:* la v1 usaba como estadístico PRIMARIO la media de ρ² sobre los
    56 pares — mal alineado con la hipótesis. H5 NO predice estructura difusa uniforme;
    predice un efecto CONCENTRADO y DIRECCIONAL (líquidos LINK/AVAX lideran a finos
    ATOM/FIL). Promediar sobre 56 pares DILUYE justo la señal esperada (baja potencia
    contra la propia hipótesis). Se sustituye por un estadístico que testea el MECANISMO.
  - *Split de liquidez (regla DETERMINISTA, sin libertad post-hoc):* líquidos = los 4
    de mayor dólar total en la ventana; finos = los 4 menores (corte por mediana). El
    volumen es propiedad del PREDICTOR, no el outcome (lead-lag) → definir grupos con él
    no es peeking. La membresía la fija la regla al ejecutar; verificable.
  - *Estadístico PRIMARIO (direccional):* D = Σ_{i∈líq, j∈fino} ρ_{i→j} −
    Σ_{i∈fino, j∈líq} ρ_{i→j}, con ρ_{i→j} = corr(f̃_{i,t}, r̃_{j,t+1}). Mide si el flujo
    de los líquidos adelanta el retorno residual de los finos MÁS que al revés (la flecha
    de H5). *Nulo:* 1.000 desplazamientos circulares del tiempo, COMUNES a todo el panel
    de predictores (preservan la correlación cross-sectional contemporánea, rompen solo
    el timing del lead-lag) → distribución de D bajo "sin lead-lag".
  - *Veredicto por el PRIMARIO (una sola decisión, sin inflación múltiple):*
    · PASA si D > percentil-99 del nulo (una cola: H5 predice D>0) **Y** mismo signo y
      > percentil-95 en AMBAS mitades del año (estabilidad estilo REE §2.4).
    · FALLA si D < percentil-95 del nulo (sin lead-lag direccional).
    · ZONA GRIS en medio, o si solo aparece en una mitad.
  - *Secundarios (DESCRIPTIVOS, NO deciden):* max|ρ| y qué pares dirigidos superan su
    propio nulo-99 (dónde vive la estructura); media de ρ² (estructura difusa). Informan
    la interpretación, no cambian el veredicto.
  - El resto (muestreo CSIC, neutralización leave-one-out β-ajustada, ventana común,
    exposición declarada, asimetría de conclusiones PASA/FALLA, EVR) se HEREDA idéntico
    de la v1.
- **RESULTADO del sub-test de feasibility (ejecutado 2026-06-19; código + resultado en
  commit POSTERIOR al pre-registro v2 `8024f8c`, verificable por `git log`) → FALLA:**
  - *Datos:* 8 símbolos, 320M trades, 2025-06..2026-05 (365 d), 36.499 barras CSIC
    (100/día; 0 % ausencias → todos operan en cada barra). Split determinista por dólar:
    LÍQUIDOS {AVAX, LINK, LTC, UNI}; FINOS {DOT, NEAR, ATOM, FIL}.
  - *Primario:* D = **−0.026** (se predijo D>0); supera solo al **2,6 %** del nulo
    (μ≈0, σ=0.014; p95=+0.023, p99=+0.031) → **D < p95 = FALLA**. La asimetría, si acaso,
    es ligeramente OPUESTA a la predicha y débil.
  - *Estabilidad:* 1ª mitad D=+0.010 (p70, no sig.); 2ª mitad D=−0.051 (p0,6, signo
    opuesto) → ni mismo signo entre mitades. Sin efecto estable.
  - *Descriptivos:* |ρ| medio fuera de diagonal = **0.0058** (≈ruido); par más fuerte
    FIL→ATOM ρ=+0.031 (diminuto); autocorr propia media −0.005 (bid-ask bounce, esperado).
  - *Validez (anti-bug):* la maquinaria está testeada en sintético — detecta lead-lag
    inyectado, NO alucina sin él, acierta el signo, y la neutralización preserva el
    lead-lag (`tests/test_xsection.py`, 8 tests). La ausencia es GENUINA, no de medida.
- **Qué aprendimos (conocimiento negativo = activo, C2):** a nivel de TRADE y con 12
  meses, TRAS neutralizar el factor común, NO hay lead-lag cross-sectional direccional
  robusto entre los 8 alts. La estructura cross-sectional al horizonte ~14 min es sobre
  todo beta de BTC. Es el riesgo nº1 de H5 (sus "4 formas de morir", #1) materializado.
- **Alcance (asimetría pre-declarada):** NO mata H5 definitivamente — H5 es RETIRADA DE
  LIQUIDEZ con L2 (depth/resiliencia) a 100 ms, no flujo-de-trade→retorno a 14 min. Pero
  baja MUCHO su prior: el proxy más barato de "estructura cross-sectional" da ~cero.
- **Decisión (pre-registrada en la asimetría):** DESPRIORIZAR el programa cross-sectional
  caro (L2 multi-nombre dedicado + R1/R4 motivados por H5). PIVOTAR a liquidez
  single-name (H1, H3) y al reencuadre "predecir liquidez/toxicidad", más defendibles y
  que NO dependen de esta estructura ausente.
- **Estado:** ANOTADA → **TOCADA / despriorizada.** Reactivable solo con una razón fuerte
  para esperar estructura en L2 ausente en trades (p. ej. resiliencia del libro), con
  prior bajo y nuevo pre-registro.
- **Alpha-decay (C3, Fase 7):** nacimiento — · Sharpe/capacidad inicial — ·
  degradación — · muerte/causa —

---

## H6 — Provisión selectiva de liquidez en la ventana de listing de perps nuevos

- **Alta:** 2026-06-20 · **Estado:** ANOTADA, **NO pre-registrada** (a pre-registrar al
  fijar el universo de listings + el plan de test sobre Tardis). Semilla del research de
  comisiones del propietario.
- **Origen:** los primeros **10 días** de un perp USDⓈ-M nuevo tienen **0 % maker fee para
  todos** (y −0,006 % para LPs). Esto ELIMINA la barrera de coste que mata la provisión de
  liquidez a nuestro tamaño (a VIP 0-2 pagamos 1,4-2 bps de maker) — justo en el momento en
  que el spread es más ancho.
- **Mecanismo económico (perdedor con nombre):** en un listing nuevo el libro es fino e
  inmaduro y el flujo retail entra con órdenes A MERCADO (FOMO / descubrimiento de precio),
  pagando un impacto desproporcionado → overshoot y reversión violenta. Pierde el
  momentum-chaser retail que cruza un libro delgado y **no puede evitarlo** (impaciente,
  price-insensitive). Gana quien provee liquidez / desvanece el overshoot.
- **Anti-arbitraje:** capacidad ACOTADA por el libro fino (no cabe capital institucional →
  a los grandes no les compensa); los MM de élite pueden tardar en desplegar en listings
  oscuros (integración, riesgo de inventario). El 0 % fee es público, pero la VENTAJA no es
  el fee — es **leer el libro** (toxicidad/resiliencia) para proveer solo cuando es seguro,
  y eso requiere nuestro stack L2, que casi nadie monta en estos nombres.
- **El giro que lo hace NUESTRO (y lo distingue del patrón conocido):** NO es "fadear el
  pump del listing" (eso lo sabe y compite todo el mundo). Es **proveer liquidez
  SELECTIVAMENTE**, usando H1 (VPIN-adaptado + resiliencia del libro) como filtro: maker en
  ambos lados solo cuando el flujo NO es tóxico; retirarse cuando sí. El 0 % fee + capacidad
  pequeña + nuestro read L2 = la combinación. **Conecta con H1** (le da un caso de uso real).
- **Predicción observable (a concretar antes de pre-registrar):** durante la ventana de
  listing, condicionar la provisión a "libro seguro" (toxicidad baja, resiliencia alta) da
  un PnL maker neto de selección adversa POSITIVO que **supera** al de proveer
  incondicionalmente; en alta toxicidad el signo se invierte. La señal DEBE discriminar.
- **Falsación (a pre-registrar):** FALSADA si (a) el PnL condicionado a "seguro" no supera
  al incondicional (la toxicidad no discrimina — modelo anidado); (b) la selección adversa
  + slippage de salida + riesgo de inventario se comen el spread en TODOS los regímenes,
  incluso con 0 % maker; (c) muere a ×10 latencia (era velocidad, §5.2); (d) frecuencia de
  "libro seguro" < umbral de masa estadística.
- **Muerte esperada:** Binance quita el 0 % fee / pone caps de posición en listings; los MM
  despliegan day-1 en todos los listings (crowding); o el overshoot retail desaparece.
- **EVR:** coste = días sobre Tardis (cubre L2 desde el día de listing). Valor: **RECURRENTE**
  (Binance lista perps con frecuencia → buena masa estadística, a diferencia de H3/H4 que
  son eventos raros) y de **capacidad pequeña** (perfecto para escritorio). Es el candidato
  más alineado con el reencuadre "prestar un servicio" + nuestro stack L2 + la realidad de
  comisiones. **NO depende de la sonda** (se testea en Tardis histórico de listings pasados).
- **Por qué es mejor candidato que H3/H4/H5:** mecanismo real + capacidad pequeña (moat) +
  RECURRENTE con buen n + testable YA en Tardis + conecta con H1 + el 0 % fee resuelve la
  barrera de coste que encontramos. Riesgos honestos: patrón en parte conocido/competido;
  la selección adversa puede empequeñecer el ahorro de fee; los MM pueden estar presentes.
- **Datos necesarios (research del propietario):** el UNIVERSO de listings USDⓈ-M (fechas
  de listing de los perps, para construir la muestra de test) y las reglas exactas de la
  ventana (duración del 0 % maker, caps de apalancamiento/posición, tags de monitorización).
- **Resultado (2026-07-01) → CERRADA sobre PRIOR BAJO: la PREMISA de régimen no se sostiene. Held-out de
  PnL de provisión SIN gastar** (se decidió NO ejecutar el test caro, no se miró el outcome — como H3).
  Pre-check de dos capas sobre CHD (que **SÍ cubre el día-de-listing**: 174 listings desde 2025-06-28, 100%
  cubiertos, primer tick a +3-9 min del onboard → infra de test resuelta):
  1. *Capa 1 (N/cobertura) — decisiva a favor:* 174 listings independientes por construcción (no co-mueven
     con BTC → N_eff no colapsa como H3), todos con dato. La N NUNCA fue el problema de H6.
  2. *Capa 2 (firma del régimen, iteración limpia pre-especificada; `scratchpad/h6_capa2_limpia.py`) —
     PREMISA DÉBIL.* Listing-primeros-30min vs día+7 (baseline pre-fade), 4 perps, métricas de liquidez SIN
     tocar retornos: **spread 1,88× (arrastrado por RAVE 29×, un fade puro; sin él ~1,5×), depth USD 0,60×
     (mild), imbalance-vol 1,34× (débil), y el dato más limpio: nsnap 1,00×** — el libro llega a 5 niveles
     TAN a menudo al listing como a día+7. **Los MM cotizan desde el minuto 1** → la ventana de descubrimiento
     ancha/thin de 2017-2019 ya no existe a escala relevante, y el anti-arbitraje de H6 ("los MM tardan en
     desplegar") FALLA. Métrica limpia primera pasada (spread 4h) también débil (1,35×).
  **Decisión (bayesiana, pre-comprometida):** tras 4 pantallas negativas el UMBRAL de evidencia para
  comprometer pre-registro + build sube, no baja. Premisa débil → posterior sobre "edge de provisión tradeable
  para lento" materialmente < prior inicial (15-25%) → **no se pre-registra.** Además la contaminación por
  fade es SISTÉMICA (fracción de los 174 son pump-and-fade → baseline día+7 inválido para parte del universo);
  definir "listings legítimos" tras ver que los fades distorsionan sería sesgo de selección disfrazado de
  limpieza. **CERRADA. $0, held-out intacto.** Ver META-CONCLUSIÓN (cabecera del LEDGER).
- **Alpha-decay (C3, Fase 7):** nacimiento — · Sharpe/capacidad inicial — ·
  degradación — · muerte/causa —

---

## H7 — Footprint de oferta forzada por unbonding del Cosmos Hub en el perp fino

- **Alta:** 2026-06-20 · **Estado:** ANOTADA (research on-chain del propietario; explota el
  recurso (3) de VISION —transparencia on-chain— hasta ahora ABANDONADO). A pre-registrar
  tras un gate de feasibility barato.
- **Distinción de H2 (FALSADA), crítica:** H2 era el NIVEL de equilibrio del funding por el
  canal de profundidad del staking-hedge (muerto). H7 es EVENT-DRIVEN: shocks DISCRETOS de
  oferta (unbondings que maduran) dejan un footprint TRANSITORIO en L2/funding. Claim
  distinto, event-study, no el nivel. No es reabrir H2.
- **Mecanismo (perdedor con nombre):** un `MsgUndelegate` grande es visible on-chain con
  `completion_time` EXACTO (21 días) → oferta futura anunciada e IRREVERSIBLE. Perdedor
  candidato: el whale (cohorte 100k-1M ATOM) que liquida en un libro de ~$2-5M a ±2 % →
  impacto. Bloqueado 21 días: no puede adelantar su propia venta.
- **Tres señales (del research):** S1 unbonding completion = el INSTRUMENTO casi-exógeno
  (el "cuándo", 21 d antes). S2 secuencia IBC Hub→Osmosis→Binance = el TIMING fino (5-15 min
  antes del impacto; la MÁS accionable, el oro). S3 redelegación a validador "parking" =
  especulativa, low-N, exploratoria.
- **Identificación (elegante):** RDD/event-study sobre `completion_time` (fijado al unbonding,
  exógeno al mercado contemporáneo) → discontinuidad en T+21 difícil de confundir. Instrumento
  de DOS etapas: S1 da el día con 21 d de antelación, S2 da el minuto exacto.
- **RIESGOS HONESTOS (los que la matan — escéptico):**
  1. **Unbonding ≠ venta.** EL supuesto que sostiene todo: el ATOM desbloqueado puede
     re-stakearse, ir a LSD/DeFi, o holdearse — no necesariamente venderse. Si la conversión
     a venta es baja, NO hay señal. Es la PRIMERA prueba.
  2. **N bajo.** Eventos grandes raros + holders concentrados (Gini 0.81, Nakamoto 4) → poca
     masa estadística (el problema que frenó H3/H4).
  3. **Stats de terceros sin verificar** ("30 % del sell pressure", "$2-5M de profundidad") →
     verificar con NUESTROS datos, no asumir.
  4. **Apuesta direccional** (predecir ventas) = el tipo difícil; y front-runnear en libro fino
     mueve el propio libro (capacidad diminuta = moat pero también techo).
  5. **Parcialmente priceado:** el unbonding es público on-chain; el mercado puede anticiparlo.
     El argumento "nadie construye el calendario de maduración" es más débil que la capacidad.
- **GATE DE FEASIBILITY BARATO (PRIMERO, antes de pre-registrar el full):** event-study sobre el
  funding de ATOM (lo TENEMOS) alrededor de las fechas de `completion` de unbondings > P90,
  controlando por BTC (beta-ajustado). ¿Hay ALGÚN footprint (funding más negativo / mayor
  |retorno|) en [completion−3d, +3d]? Si no, la conversión a venta es demasiado baja → H7 muere
  barato. Necesita la serie histórica de unbondings (on-chain; indexer/archive — research del
  propietario).
- **Test full (si pasa el gate):** DiD/RDD sobre `completion_time`; dependiente = Δfunding 24h +
  Δprofundidad L2 (Tardis); independiente = monto unbonding z-scored vs media 90 d; controles =
  APR, retorno BTC, spread; instrumento = `completion_time`. Compuerta C7 (CPCV/DSR/PBO/BHY/
  latencia).
- **Datos:** unbondings históricos (Cosmos LCD `/cosmos/staking/v1beta1/.../unbonding_delegations`
  + indexer para historia), funding ATOM (tenemos), L2 ATOM (Tardis). S2 requiere indexar
  transfers IBC Hub→Osmosis→Binance (`osmo1n8qj0h0swxf8x0pj3k4uh0y53szth7wv09grfe`).
- **EVR:** coste medio (sourcing on-chain). Valor: explota el recurso único ABANDONADO,
  capacidad pequeña (moat de escritorio), identificación casi-experimental (`completion` exógeno).
  El candidato más alineado con "ver antes de que pase".
- **Prueba de olfato preliminar (2026-06-20, datos MENSUALES + magnitud MUESTREADA del
  propietario — INADECUADOS para el gate, no es veredicto):** Spearman(unbonding,
  funding_residual ATOM~BTC) ≈ +0.14 (lag0, signo contrario) / −0.02 (lag+1 mes); 60 meses
  pero los 2 mayores = 26 % de la varianza → n_efectivo ~2-3. Inconcluyente por dos límites
  del dato: (1) la magnitud de ATOM es `count × media(200 txs)` → ruido enorme en cola pesada
  (el avg/tx salta ×10-38 mes a mes = el muestreo, no la realidad; el "24 % del bonded en
  2025-01" puede ser artefacto); (2) mensual no soporta el event-study/RDD diario sobre
  `completion_time`. NO se concluye nada sobre H7 — se necesita el dato correcto.
- **DATO AFINADO que se necesita (research del propietario):** NO el agregado (fuerza
  muestreo), sino la COLA: cada `MsgUndelegate` GRANDE (≥ ~50k ATOM) con monto EXACTO y FECHA
  EXACTA (día/bloque → completion = inicio+21d), 2021→hoy. Son pocos (cientos en 5 años),
  exactos, sin muestreo, y soportan el RDD diario. Es la señal real (oferta de ballena) y es
  MÁS fácil que muestrear 200/mes. Bonus: dirección del delegador (para enlazar con S2/CEX).
- **Resultado / Qué aprendimos:** — (pendiente; gate real con el dato afinado)
- **Alpha-decay (C3, Fase 7):** nacimiento — · Sharpe/capacidad inicial — ·
  degradación — · muerte/causa —

---

## H8 — Provisión selectiva de liquidez con filtro OFI de toxicidad de flujo  (del Research Brief + revisión hostil externa, 2026-06-21)

- **Alta:** 2026-06-21 · **Estado:** PRE-REGISTRO CONGELADO — **NO ejecutar antes del L2 de la
  sonda (día 14)**. Surge de la revisión hostil (Perplexity) como el candidato MÁS prometedor:
  reusa todo el OFI de H1 con una barra MÁS BAJA (clasificar toxicidad del flujo, no predecir
  dirección) y es **latency-robusto** (retirar cotización no es carrera de velocidad). Generaliza la
  provisión selectiva de H6 (solo la ventana de listing) a operación CONTINUA en los 8 nombres.
- **Por qué se pre-registra HOY (regla dura):** el outcome (markout adverso por fill sobre el L2
  propio) NO existe hasta el día 14 → congelar predicción y falsación ahora (hash = autoridad de
  fecha) es la forma limpia. Cualquier cambio de umbrales tras ver el resultado = hipótesis nueva
  (C1.4).

### Plantilla C1
1. **Mecanismo económico (perdedor con nombre):** un maker que cotiza en un libro fino gana el
   medio-spread del flujo NO informado — el taker lento/retail que cruza sin información (el MISMO
   perdedor de H1, ahora subvencionando al maker). El riesgo es la SELECCIÓN ADVERSA: el flujo
   tóxico (informado, a punto de mover el precio) golpea su cotización a precio malo. El edge: usar
   la señal OFI/toxicidad para RETIRAR/ensanchar la cotización antes del flujo tóxico y cotizar fino
   cuando es benigno. NO es predicción de dirección — es clasificar "¿el próximo taker es
   informado?", barra más baja.
2. **Anti-arbitraje:** estructural, no de velocidad. La selección adversa se filtra con información
   del libro (OFI/MLOFI), no con co-locación; retirar cotización SOBREVIVE a latencia. Los HFT de
   élite ignoran estos nombres (capacidad). La ineficiencia: flujo retail no informado cruza spreads
   en libros finos y no hay suficientes makers sofisticados para competirla a ~200 ms. Capacidad
   acotada por el libro fino (moat Y techo).
3. **Predicción observable (CONGELADA):** por cada TRADE que cruza (aggTrades) con agresor de lado
   s, un maker del lado opuesto se llena al best quote. Por fill:
   - *medio-spread capturado* = |best_quote − mid| en t (>0).
   - *markout adverso* a horizonte h (h∈{5,10,20,50} ticks @100 ms) = movimiento del mid CONTRA la
     posición del maker: si el maker VENDE (agresor comprador), adverso = mid[t+h] − best_ask;
     simétrico si compra. >0 = taker informado (maker pierde).
   - *P&L neto por fill* = medio-spread − markout_adverso − **maker_fee** (Binance USDT-M ~0,02 %,
     SIN rebate para retail; pre-fijado).
   PREDICCIÓN: la señal de toxicidad en t (|OFI| / OFI firmado en dirección del agresor, con VPIN
   como régimen) PREDICE markout adverso alto (AUC > 0,55). Y el maker SELECTIVO (salta los fills
   con señal > umbral causal τ) logra P&L neto/fill MAYOR que el maker NAIVE (siempre cotiza), y > 0
   tras costes.
4. **Criterio de falsación (CONGELADO):** FALSADA si CUALQUIERA:
   - La señal NO predice el markout adverso (AUC ≤ 0,55, o markout_tóxico ≈ markout_benigno).
   - El selectivo NO bate al naive (P&L neto selectivo ≤ naive → el filtro no aporta).
   - P&L neto del selectivo ≤ 0 tras costes realistas → sin edge.
   - Se DEGRADA > 30 % a latencia ×10 (la protección se evapora si solo puedes retirar 10× más tarde
     y el flujo tóxico ya te golpeó — el test CLAVE; la revisión ASUME robustez, aquí se MIDE).
   - Frecuencia de oportunidades de fill < 1 % / masa insuficiente.
   - No aguanta en AMBAS mitades de la muestra (REE/estabilidad).
5. **DOS ETAPAS:** (1) *validez del filtro de toxicidad por-fill* (esta predicción: ¿la señal
   discrimina fills tóxicos? ¿el selectivo bate al naive net?) sobre L2+trades propios = gate
   barato. (2) SOLO si pasa: estrategia OPERABLE con INVENTARIO (Avellaneda-Stoikov + skew por
   inventario + retirada por OFI) y la compuerta C7 completa = el gate del dinero.
6. **PROBLEMAS DUROS DECLARADOS DE ANTEMANO (de la revisión hostil):**
   - *La sim de fills asume que nos habríamos llenado de los trades que ocurrieron* → ignora cola y
     competencia → SOBREESTIMA la tasa de fill (los reales son un subconjunto). La etapa 1 mide la
     VALIDEZ del filtro, no el P&L absoluto.
   - *El markout por-fill ignora el INVENTARIO* (acumulación/unwind en cascada) → etapa 1 necesaria
     pero NO suficiente; el inventario es la etapa 2.
   - *Retirar la cotización no cambia si el trade ocurre* (golpea a otro maker) → "saltar fills
     tóxicos" es un modelo de primer orden; al retirar, el residual se vuelve MÁS tóxico para makers
     lentos — ese es el PUNTO, pero el backtest no modela la competencia.
- **OPERACIONALIZACIÓN (2ª revisión hostil, 2026-06-21, pre-dato — afina CÓMO se mide, no la
  hipótesis):**
  - *Markout corregido por impacto PROPIO:* el mid (bid0+ask0)/2 salta en discreto; si el fill
    consume el mejor nivel, el nuevo mid baja por CONSTRUCCIÓN (no por selección adversa). Se mide el
    markout contra el **weighted-mid** (VWAP de los k niveles) o el mid POST-fill, no el mid naive.
    Sin esto se SOBREESTIMA la toxicidad (artefacto que domina los primeros 1-2 s de la curva).
  - *Curva de markout multi-horizonte + downside:* se reporta a {500 ms, 1 s, 5 s, 30 s, 5 min}
    (revierte antes de 30 s = ruido/latencia; monótona = selección adversa estructural), el
    **adverse-selection ratio a 500 ms** como KPI operativo, y la COLA IZQUIERDA del P&L diario
    (P5 / Sortino ajustado por fill), no solo la media — el edge es delgado (~2,5 bps neto a fee VIP0
    SIN rebate: el retail no entra al Liquidity Hub, req. ≥$100 M/30 d) y lo que decide la
    supervivencia es el downside.
  - *Sim de fills HONESTA (resuelve el problema duro declarado):* probabilidad de fill por posición
    en cola con el estimador volume-delta de Rigtorp sobre nuestros snapshots (sin order-by-order) +
    tabla empírica fill-prob por (posición, tamaño, hora); descuento conservador ×0,6-0,7 para
    posición ≥2 (14 días bastan para top-of-book, no para cola profunda).
- **CONTROLES CROSS-CUTTING (2ª revisión, pre-dato; aplican a H1/H3/H8):**
  - *Dummy de cross-shock:* régimen causal = "≥3 de los 8 símbolos con OFI < P5 a la vez". Los
    shocks de los 8 finos están MUY correlacionados (BTC −3 % → los 8 se fragilizan juntos) = riesgo
    de inventario NO diversificable y rompe la independencia que asumen CPCV/REE. Control/diagnóstico
    (a H1/H3 como control MÁS estricto, sin tocar sus criterios congelados; a H8 de fábrica).
  - *Latencia condicional (no solo ×10 uniforme):* la latencia tiene cola pesada y puede correlar
    con los shocks (el libro estalla cuando Binance se congestiona). Con el doble timestamp se mide
    la degradación cuando `recv−event > P95` Y la señal dispara. Diagnóstico ADICIONAL al ×10
    congelado (más realista; no lo reemplaza en H1/H3).
  - *Criterio de ABANDONO por OI (CONGELADO con dato, 2026-06-22):* si `OI_value_30d_medio` de un
    símbolo cae bajo **$15 M** (suma de OI en USD), sale del basket. Nivel de VIGILANCIA: **$25 M**.
    Umbral **ABSOLUTO** (no relativo: un suelo relativo nunca dispararía si TODO el mercado se seca,
    que es justo el riesgo). Dato jun-2026 (~20 d): ATOM $16,3M (el más fino, EN VIGILANCIA), DOT
    $28,4M, FIL $36,5M, LTC $47,4M, UNI $52,9M, AVAX $59,1M, LINK $67,2M, NEAR $97,5M (mediana $50M).
    Por debajo de ~$15M el libro es demasiado fino para MM selectivo incluso a tamaño diminuto; al
    marchitarse, el spread sube PERO el adverse-selection ratio TAMBIÉN (sube la fracción informada) =
    la peor dinámica. Recalibrable contra el L2 del día 14 (el punto patológico real se mide en
    spread/profundidad/AS-ratio, no solo en OI). El riesgo no es crowding, es que el mercado se seque.
- **CONDICIÓN OPERATIVA "SOY EL ÚNICO MAKER" (insight de Manuel, 2026-06-21, pre-dato — NO es
  hipótesis, es una condición de operación que faltaba en H1/H3/H8):** en libros finos con OI
  cayendo hay momentos en que eres el ÚNICO maker activo en el nivel. Ahí no capturas spread —
  escribes una OPCIÓN GRATIS: cualquier taker ejecuta contra ti y no cancelas a tiempo. *Síntoma
  observable:* fill rate ANORMALMENTE ALTO en OFI extremo = el libro estaba vacío y TÚ eras el
  precio (no es que la señal fallara). *Filtro causal (desde D_10), polo OPUESTO al de toxicidad:*
  "fracción de dominancia" = `quote_size/(level_size+quote_size)`; si el nivel está bajo su P10
  causal de tamaño Y serías gran parte del nivel (dominancia > umbral) → alta P(eres el único) → NO
  cotizar (o ensanchar mucho). *Consecuencia para la sim de fills:* la fill-prob → ~1 cuando eres
  dominante (eres el libro), y esos fills son los TÓXICOS → la sim modela AMBOS regímenes (cola
  profunda: fills = subconjunto con descuento; soledad: fill ≈ 1). Toxicidad y soledad gatean AMBAS
  la cotización.
- **MODELO DE FILL = COTA INFERIOR (constitución, 2ª ronda IO con revisor hostil, 2026-06-21,
  pre-dato):** sin L3 no hay fill exacto. Se adopta el **RiskAdverseQueueModel** (hftbacktest):
  `queue_ahead = depth_at_price` al insertar; baja SOLO con trades a tu precio
  (`max(queue_ahead − trade_qty, 0)`); los cambios de profundidad SIN trade NUNCA te benefician
  (siempre último en cola). Soledad (depth ≤ c·Q, c≈2): P(fill)=1 a cualquier toque, fill completo,
  marcado y tratado como el más tóxico. aggTrades→niveles: del mejor hacia abajo; lo no reconciliable
  = consumo de niveles altos primero (peor para ti). Markout estilo Databento: weighted-mid (k=2-3)
  con LOCF en **event_ts**, referencia POST-fill, horizontes {500 ms,1 s,5 s,30 s,5 min}, se ignora
  <100-200 ms (impacto propio). recv_ts solo para latencia. **TODOS los resultados de H8 son COTAS
  INFERIORES de fills/P&L: si el edge no sobrevive a esta cota pesimista, se considera inexistente.**
- **IMPLICACIÓN ESTRUCTURAL A VIGILAR (observación propia, pre-dato):** bajo "siempre último en
  cola", en colas PROFUNDAS casi nunca te llenas → los fills que SÍ obtienes se concentran en niveles
  FINOS/soledad = los TÓXICOS. El modelo honesto puede revelar que, del lado pasivo en libros finos,
  los fills BENIGNOS que quieres raramente se consiguen y los que se consiguen son la opción gratis.
  Si H8 sobrevive a esto, es robusto; si muere, era selección adversa estructural. Métrica a reportar:
  la fracción de fills que caen en régimen de soledad y su markout vs los de cola.
- **REVISIÓN 2 DEL DISEÑO IO (correcciones CONGELADAS, 2026-06-21, pre-dato).** El revisor hostil
  validó el enfoque: la sim cota-inferior ES suficiente para un NO-GO honesto; un GO fuerte = sim +
  piloto live de tamaño mínimo DESPUÉS (nunca en vez de). Correcciones:
  (1) *trade→niveles:* el overflow de un aggTrade (qty > profundidad visible) va FUERA del top-10 /
  niveles bajos, NUNCA al mejor; `queue_ahead` baja SOLO por el volumen confirmado EXACTAMENTE a tu
  precio (sin "volumen fantasma" que te adelante — era optimista, viola RiskAdverse).
  (2) *ventana de cancelación (latencia):* tras moverse el best, el quote queda "rancio pero
  ejecutable" durante `cancel_window = p95(recv−event)`; cualquier trade a tu precio ahí = fill
  TÓXICO. Sin esto era cota inferior en nº de fills pero NO en P&L (te saltabas justo los que recortan).
  (3) *half_spread* vs mid SIMPLE top-of-book post-fill (NO el weighted-mid, que inflaría el spread
  capturado); el weighted-mid solo para el markout y el OFI.
  (4) *soledad:* `c_solitude` justificado por dato = `depth ≤ min(2·Q, P25 causal de profundidad)`.
  (5) *min_h del markout* ≥ 0,2-0,3 s.
  (6) *MÉTRICAS DE RÉGIMEN (el go/no-go fino):* `PNL_non_solitude`, `PNL_solitude`,
  `solitude_fill_fraction` — separan "no hay edge / eres el punching bag" de "edge existe pero
  INALCANZABLE a tu cola/latencia" de "el edge está en RETIRAR liquidez, no proveerla". Más
  informativo que un Sharpe global. Todos los parámetros congelados aquí, no se tunean tras ver dato.
- **Relación con H6:** H6 = provisión selectiva en la VENTANA de listing (evento discreto, data-
  gated). H8 = la misma idea en operación CONTINUA sobre los 8 nombres, con el L2 que YA tenemos.
- **Muerte esperada:** programa de market making patrocinado (más makers sofisticados → spread
  comprimido); cambio de fees/rebate de Binance; o crowding del filtro OFI.
- **EVR:** coste ≈ 1-2 semanas (markout + sim de maker, reusa el OFI de H1). Valor si cierta: el
  candidato con barra MÁS BAJA, latency-robusto y perdedor claro — la dirección del reframe "mejor
  servicio". Prior: cauteloso, pero el más alto de los vivos.
- **Datos:** L2 propio (mid, best quotes) + aggTrades (trades que cruzan + lado + señal OFI), todo
  de la sonda. Reusa `book.py` (mid, spread) + `book.ofi`. Nuevo: cómputo de markout + sim de maker
  + P&L selectivo vs naive.
- **ENSAYO sobre dato REAL (ATOM 2026-06-19, dress-rehearsal pre-día-14, 2026-06-22) — HALLAZGO:**
  validar `h8_io` sobre dato real (única IO sin validar) cazó un problema serio y lo resolvió.
  *Síntoma:* half_spread NEGATIVO (−2,76 bps, 20% positivo) por **70% de fills "stale" ESPURIOS**.
  *Causa raíz* (tras 5 hipótesis erróneas y un debug decisivo): el ask de ATOM tiene **spread de 1
  tick** (5,5 bps) y cambia solo el 1% entre snapshots, pero con depth MUESTREADO a 100 ms, un trade
  al ask viejo (= bid actual, por el spread de 1 tick) se confunde con un fill rancio → la **ventana
  de cancelación (C2) NO es implementable de forma fiable con este dato.** *Resolución (honesta):*
  `cancel_window_ms=0` por defecto → half_spread **+2,76 bps, 100% positivo**, fills realistas
  (~520-926/día). La **toxicidad de latencia que C2 buscaba la captura el MARKOUT** (un fill tóxico
  muestra markout adverso), así que no se pierde — solo se mueve de un label dudoso a la medición
  robusta. El parámetro se mantiene >0 para dato L3 / spread ancho donde C2 sí es medible. *Es el
  ensayo haciendo su trabajo:* el fallo se cazó GRATIS sobre dato real ANTES del día 14, no después
  creyéndonos un P&L contaminado. (También: half_spread corregido a mid AL fill, no post-fill.)
  ATOM 06-19 EXCLUIDO del run final (peek de salud, como en H1).
- **REVISIÓN HOSTIL de mi resolución (cancel_window=0) — matiz CONGELADO (2026-06-22):** la revisión
  confirmó que el P&L POR FILL (bps) es cota inferior (el markout SÍ captura la toxicidad post-fill),
  PERO cazó un sesgo que se me escapó: C2 también penalizaba la PROBABILIDAD de fill → sin él se
  SOBRE-CUENTAN fills (algunos los habrías cancelado a tiempo). Precisión honesta: C2 no es "no
  implementable"; es que MI implementación fue demasiado agresiva para spread de 1 tick. **DECLARACIÓN
  (constitución):** el sim es cota inferior en P&L/FILL, **NO** en NÚMERO de fills; el P&L TOTAL puede
  estar inflado en VOLUMEN hasta la fracción de fills en ventana de latencia. **Medido y declarado,
  no oculto:** diagnóstico `fraccion_fills_en_ventana_latencia` = **10,7% en ATOM real** (Q=5,5 ATOM
  calibrado al notional mínimo ~$10 vía `calibrate_Q`; soledad 18%). Lo que YA NO se puede decir: "el
  nº de fills es cota inferior". Lo que SÍ: "el P&L/fill es cota inferior; el nº de fills puede
  sobreestimarse hasta ~11%". Si el sobre-conteo llega a importar: afinar C2 (stale solo si el best
  cruzó ≥1 tick MÁS allá del quote viejo) o ir a L3/live.
- **RESULTADO DEL GATE (día 26, 2026-06-26) — SCREEN-NEGATIVE, prima #1 ARCHIVADA:** sonda cerrada
  (14 días limpios, 0 corruptos), 8 perps, `analysis/run_day26.py` (solo orquesta funciones CONGELADAS;
  Q por símbolo vía `calibrate_Q`; ATOM 06-19 peekeado EXCLUIDO). **Pool 268.537 fills, 10,3% soledad:**
  `AUC_predice_tóxica = 0,503` (el OFI NO separa soledad benigna de tóxica — el corazón de la tesis
  ofensiva), `pnl_benigna −0,79 bps` < `pnl_toda −0,71` (la partición no ayuda; benigna incluso PEOR),
  selectivo (−0,64) PEOR que naive (−0,61), `AUC_tox 0,498`, estable=False. **Tesis viva 0/8 símbolos;
  selectivo sobrevive 0/8.** Ningún símbolo llega a AUC 0,55. Los únicos PnL/fill positivos (DOT +2,7,
  FIL +5,8) son sobre ~150 fills/día (finísimos, N_eff irrisorio, viva=no igual). **TAG: SCREEN-NEGATIVE
  (falsada → archivada).** ALCANCE HONESTO de la falsación: esta operacionalización (OFI-predice-soledad-
  tóxica, 14 días, 8 alts Binance, sim sobre snapshots @100ms) — NO las primas #2 (funding carry) ni #3
  (ejecución óptima), que siguen vivas. **DECISIÓN: $0 en datos, Tardis intacto.** El gate hizo
  exactamente su trabajo (DATA_PLAN §1): mató la apuesta barata GRATIS antes de comprar nada. Caché de
  inputs en `data_hist/probe/_cache/` (recálculo instantáneo para slices in/out-shock futuros).
- **Resultado / Qué aprendimos:** prima #1 falsada en screen; el maker pasivo sobre estos finos es
  adversamente seleccionado (PnL/fill ≤0 en los líquidos) y el filtro OFI no aporta señal. Maquinaria
  validada en real. Siguiente: caracterizar funding (prima #2, con neutralización H5) sobre el mismo dato.
- **Alpha-decay (C3, Fase 7):** nacimiento — · Sharpe/capacidad inicial — · degradación — · muerte —

## PRIMA #3 — Ejecución óptima (ahorro vs TWAP con horario OFI-aware)  (rumbo VISION; gate día-26, 2026-06-26)

- **Tesis:** el "ganador silencioso" — NO predice dirección, solo ejecuta MEJOR un trade ya decidido
  (mejor base rate). `analysis/exec_sim.py` + `tests/test_exec_sim.py` (6/6 verde): orden madre de
  tamaño S en K hijas market (caminan el libro L2); TWAP vs horario **OFI-aware ONLINE causal** (acelera
  antes de movimiento adverso). Métrica = bps ahorrados vs mid de LLEGADA. Falsación CONGELADA: ahorro>0
  + estable ambas mitades + tstat_Neff>2. K=6, H=60 s, lam=1, window=30 s, hija≈1,5× top (fijados ANTES
  de ver el panel; el preview de 1 día NO los cambió).
- **RESULTADO (8 perps × 14 días) — SCREEN-NEGATIVE, 0/8:** ahorro NEGATIVO en los 8 (−0,09 a −1,72 bps),
  pos%<44, tstat_Neff de **−8,6 a −27,9** (significativamente PEOR que TWAP, no ruido). Esta
  operacionalización ARCHIVADA.
- **Dos caveats honestos (LEADS para pre-registro NUEVO, NO rescates):**
  (a) *anti-señal:* el tstat tan negativo dice que el OFI **anti-predice a 10 s** (revierte, no momentum)
  → un horario CONTRARIAN es una HIPÓTESIS NUEVA que exige su propio pre-registro ANTES de testear
  (voltear el signo ahora = p-hacking, prohibido).
  (b) *confound de convexidad:* el horario OFI-aware usa hijas de tamaño DESIGUAL → camina más hondo →
  paga un impuesto de convexidad (Jensen) que el TWAP (hijas iguales) no paga, máximo en los finos
  (DOT/FIL, los peores: −1,0 y −1,7). Un test que AÍSLE el timing (hijas de igual tamaño / fills
  mid-only) es la operacionalización limpia siguiente.
- **Disposición:** 2 de las 3 primas del rumbo (#1 provisión, #3 ejecución-OFI) SCREEN-NEGATIVE sobre la
  sonda. Viva #2 (funding carry) — pero es OTRO régimen de dato (años de funding, no el L2 de 14 días).
  $0 gastados. La sonda de 14 días ha "hablado" para las dos primas microestructurales: negativo.

## PRIMA #2 — Funding carry cross-sectional (neutralización H5)  (rumbo VISION; corrida 2026-06-26)

- **Tesis:** factor de carry dólar-neutral — cada día CORTO los perps de funding alto (cobras lo que
  pagan los largos hacinados), LARGO los de funding bajo; ¿deja alfa que SOBREVIVE a neutralizar la beta
  de BTC (cicatriz H5), o es solo alt-beta corto? `analysis/funding_carry.py` + test (3/3). Dato: funding
  diario anualizado + retornos klines 1d de Binance, **~5,5 años** (1997 días comunes, 8 alts + BTC) —
  potencia REAL, bajado gratis a `data_hist/funding/` y `data_hist/returns/` (`fetch_funding.py`,
  `fetch_returns.py`). Falsación CONGELADA: carry NEUTRAL >0 + estable ambas mitades + tstat_Neff>2.
- **RESULTADO — SCREEN-NEGATIVE:** carry CRUDO Sharpe **+0,12** (tstat +0,26, no significativo); NEUTRAL
  full-sample Sharpe **+0,13** (tstat +0,27); beta-BTC de la cartera **−0,013** (~0). **NO es alt-beta —
  simplemente NO hay carry significativo.** Falsada (tstat≪2, no estable). Archivada.
- **BUG metodológico CAZADO (disciplina h8):** la neutralización con beta RODANTE causal daba Sharpe
  −0,41 (parecía "alt-beta confirmada"). Validado → **artefacto**: beta ~0 pero ruidosa × factor
  contemporáneo = deriva espuria (−3,4 bps). Corregido a beta FULL-SAMPLE (hedge ratio limpio, ≈ crudo).
  La rodante queda como diagnóstico. Lección reafirmada: validar SIEMPRE el número sorprendente en real.
- **Disposición — EL TRÍO COMPLETO ESTÁ CRIBADO, LAS 3 PRIMAS SCREEN-NEGATIVE:** #1 provisión, #3
  ejecución-OFI, #2 funding-carry. La premisa del rumbo (un jugador pequeño cosecha primas de servicio
  estructurales en perps finos de Binance) NO sobrevive a los screens. $0 gastados, Tardis intacto. El
  valor entregado = la DISCIPLINA + la infraestructura (captura L2 limpia, motor de validación, screening
  honesto), que mató 3 tesis plausibles barato y sin autoengaño. Leads exploratorios abiertos (pre-registro
  NUEVO): OFI contrarian a 10 s (§PRIMA #3), ejecución timing-aislado, otras venues/frecuencias/mecanismos.

## GATE-0 cross-venue lead-lag (Binance→Bybit) — ARCHIVADO  (candidato #1 de MECHANISM_QUEUE, 2026-06-27)

- **Cata de dato (cazó un error de intel):** el orderbook 200niv gratis de Bybit es de **SPOT**, no perp;
  el OB de **perp** de Bybit NO es gratis. Sí gratis: **trades de perp** (`public.bybit.com/trading/`).
- **Gate barato (trades-vs-trades, gratis):** `analysis/xvenue_lag.py`. El mid de la sonda muestreado
  @100ms vs trades tiempo-real de Bybit dio un artefacto "−100ms Bybit lidera" (cazado → SIEMPRE trades-
  vs-trades). Control limpio (BTC 06-20, Binance Vision aggTrades + Bybit perp trades, 0,8M+1,2M trades):
  **Binance LIDERA a Bybit ~50ms** (pico +50ms a grid 50ms; corr sube 0,41→0,55 de mediana a P99 stress
  = lead genuino). PERO el lag **NO se ensancha en stress** (sigue ~50ms en P99).
- **Veredicto: ARCHIVADO.** Lead real pero **~50ms = juego de velocidad puro, no operable** para jugador
  pequeño (carrera de latencia vs HFT colocalizado). Los 700ms de Hyperliquid (descentralizado) NO
  transfieren a Bybit (CLOB rápido) — a-priori confirmado por medición. **Coste: $0 + 1 sesión.** No se
  paga el OB de perp de Bybit. Frente activo pasa a #2 (contrarian OFI, ya pre-registrado).

## CONTRARIAN OFI — reversión tras OFI extremo  (candidato #2 MECHANISM_QUEUE; EL DISPARO Probe-1, 2026-07-01)

- **Tesis:** fadear el OFI extremo (P95 causal, **down-only** por la RED LINE anti-short-vol) esperando
  reversión a h=25 s, sobre 8 perps finos de Binance Futures. Params **W5/k5/P95/h25 CONGELADOS** en el
  PREREG (`docs/PREREG_CONTRARIAN.md`, commit `5942640`) ANTES del disparo — hash = autoridad de fecha.
- **Datos:** CHD Binance Futures reconstruido @100ms, ventana 2025-06-29→2026-05-30. **318/328 días**
  (10 pre-registrados fuera por disciplina; **10 data-unavailable** por hueco de archivo CHD en LINK,
  30-mar→09-abr 2026 — verificado por diagnóstico, ver PREREG nota 2026-07-01). `n_bloques = 696.637`,
  `n_eff = 433,8` (corregido cross-seccional + autocorrelación). Reconstructor optimizado byte-idéntico ese
  día (verificado, 43/43 tests) — no cambia el resultado.
- **RESULTADO — SCREEN-NEGATIVE (no supera costes, `stopped_at=costs`):** media neta **−10,71 bps/evento**,
  Sharpe_evento **−1,26**, **tstat_neff = −26,16**. Decisivo, NO marginal ni por falta de potencia (n_eff
  sano). Fadear OFI extremo en estos finos **pierde tras costes por amplio margen**; la reversión, si
  existe, está bajo el suelo de costes (~fee 8 bps + spread). Evidencia: `data_hist/probe1_run/screen.json`
  + `logs/disparo_probe1_20260701T133022Z.log` (commiteados).
- **Disciplina:** params congelados → **cae con ellos, NO hay v1.1** con params ajustados post-dato.
  **Probe-2 (captura forward) NO se tocó — INTACTO:** un Probe-1 negativo ya mata la graduación (regla AND),
  gastar Probe-2 no lo resucita. El veredicto es robusto a los 10 días ausentes (~3% no voltean un t=−26).
- **Qué aprendimos:** el lead más fuerte que quedaba (reversión tras OFI extremo) **NO sobrevive al screen
  sobre ~11 meses** con params pre-comprometidos. Cae limpio, sin autoengaño. La infraestructura (loader CHD
  con fail-loud, reconstructor, panel de bloques con N_eff honesto, disparo resumible) queda probada de punta
  a punta. $0 gastados.
- **Disposición:** **SCREEN-NEGATIVE, mecanismo CRIBADO.** El frente contrarian cae. Pasa al siguiente
  candidato de `MECHANISM_QUEUE` — con prior real, no esperanza (disciplina de familia: N variantes sin
  ganador ⇒ la siguiente no tiene prior, tiene hope).

---

## CAPÍTULO 2 — HYPERLIQUID: candidato a nuevo universo  (alta 2026-07-01; esta entrada 2026-07-02, EN CURSO)

- **Por qué HL (filtro de la META-CONCLUSIÓN):** buscar flujo DESINFORMADO + capturable por un jugador
  lento. HL es perp-DEX on-chain, cubierto por CHD (`hyperliquid_futures`, 372 símbolos; también `lighter`
  y `aster_futures` como alternativas más jóvenes).
- **Loader (`analysis/hl_adapter.py` + tests):** el OB de HL en CHD es **100% snapshots** (libro completo
  por push ~0,5s), NO diffs → agrupar por `event_time`; `cryptohft_to_book` (Binance) producía libros
  cruzados y ~0 emisiones (así se cazó el formato). Validado: 0% cruzado, BTC spread 0,10 bps / AIXBT
  4,95 bps. **Lección: verificar el FORMATO del dato antes de asumir que la maquinaria transfiere.**
- **Pre-check #1 — informatividad del flujo (2026-01-15, subset dev; el RESTO de HL = held-out):** sig·fr
  del contrarian (W5/k5/P95/h25, grid 500 ms): BTC **−0,82 bps (t=−9,0)**, HYPE −1,08 (−5,4), SOL −0,62
  (−5,6), AIXBT −0,45 (−1,7). **0/4 revierten → flujo INFORMADO como en Binance → la dirección
  taker/reversión muere también en HL.** Gradiente débil hacia lo retail (AIXBT ≈ ruido). Código:
  `analysis/hl_flow_precheck.py`.
- **CORRECCIÓN DE PREMISA (2026-07-02; auditoría externa del propietario + verificación propia).** La
  premisa "suelo de latencia ~0,7s para todos" era FALSA:
  (a) *Histograma de deltas de snapshots* (`hl_adapter.snapshot_cadence`, BTC+AIXBT 2026-01-15): mediana
  542 ms, p1 408 / p99 694, y **distribución IDÉNTICA entre BTC y AIXBT (a 2 decimales) ⇒ calendario
  GLOBAL del feed, no eventos por símbolo** — la cadencia es de la cámara (feed), no del coche (matching).
  No es throttle duro (5,6% de deltas <480 ms): cadencia ~0,5s con jitter.
  (b) *Docs HL verificados:* bloques ~0,1-0,2s; priority fees en el tier taker (~45 ms/bp, cap 8 bp) ⇒
  EXISTE carrera de velocidad residual; desventaja estimada desde París ~2-3× (vs ~1000× en Binance).
  (c) **La protección estructural REAL del maker (verificada en docs/Medium oficial; más fuerte que la
  premisa original): CANCELS y POST-ONLY se ordenan ANTES que GTC/IOC dentro de cada bloque, enforced
  onchain por el propio L1, y una priority fee (aunque pague el cap) NO puede adelantar un cancel**
  ("cancel-first design… to reduce toxic flow"). Literatura aplicable: speed bump asimétrico pro-maker
  (Baldauf-Mollner; Brolley-Cimon) — predice menor selección adversa del maker y competencia desplazada
  de velocidad a calidad de cotización/cola. **Fortalecimiento pre-dato del experimento maker (ningún
  outcome tocado). La cadena lógica de la hipótesis sobrevive a la corrección con mejor fundamento.**
- **Economía maker (VERIFICADA, docs de fees):** base **0,015% maker (1,5 bps/fill)** / 0,045% taker;
  rebate maker exige >0,5% de cuota de volumen maker del venue (inalcanzable) ⇒ 1,5 bps en piedra.
  Cruzado con nuestros spreads: BTC half-spread 0,05 − 1,5 = **muerto**; AIXBT ~2,5 − 1,5 ≈ **+1,0 bps**
  ⇒ **el hábitat viable es la COLA ANCHA de spread (finos/memes)** — converge con el gradiente de
  informatividad (donde el flujo es menos informado). Dos evidencias independientes, mismo rincón.
- **Datos desbloqueados:** trades de HL en CHD **verificado en sesión** (BTC 228-478k prints/día);
  **Reservoir/Hydromancer** (S3 gratis: TODOS los fills + velas 1s + L2 20 niv @1min, historia completa);
  oficial `node_fills_by_block` (requester-pays; fills alineados al bloque = validador de relojes);
  **0xArchive** (L4 con atribución de wallet, free tier a evaluar — mediría la selección adversa
  REALIZADA de makers reales, sustituyendo el supuesto de cola por observación). HLP vault como contexto
  (según auditoría externa, no verificado aquí: Sharpe ~5 sobre $500M+, con flujos privilegiados — 1% del
  revenue + backstop de liquidaciones): demuestra que el pastel maker existe; la pregunta es si queda
  porción sin privilegios en la cola ancha.
- **▶ PRE-CHECK MAKER v0 — DISEÑO CONGELADO (2026-07-02, hash de este commit, ANTES de ejecutar):**
  - **Capa 1 (condicionantes, sin outcome; código `analysis/hl_maker_capa1.py`):** barrido del universo
    HL (1 día reciente). **Regla: CANDIDATO si (half-spread mediano − 1,5 bps) ≥ +1,0 bps Y ≥5.000
    prints/día Y volumen ≥ $1M/día. Masa (lección H3, suelo ABSOLUTO): ≥30 símbolos candidatos.** Si no
    hay masa → la hipótesis maker muere barata y Lighter/Aster asciende. Etapa A = actividad (trades);
    etapa B = spread (L2 solo para los que pasan actividad).
  - **Capa 2 (outcome; SOLO si capa 1 pasa; subset dev primero, resto held-out):** maker simulado
    join-the-touch, requote por snapshot (~0,5s), fills desde prints reales, **DOS cotas de cola**:
    optimista (cualquier print a tu precio te llena) / pesimista (llenas solo tras volumen impreso ≥
    tamaño visible del nivel al cotizar). Métrica: **markout(Δ) = lado·(mid_{t+Δ} − px_fill) − 1,5 bps**.
    **Familia pre-registrada: Δ ∈ {1, 5, 25}s × 2 cotas; endpoint PRIMARIO = markout(5s) en cota
    PESIMISTA** (un requoter a 0,5s pierde prioridad FIFO en cada cancel-replace: el fondo de la cola es
    su régimen operativo real, no paranoia); BHY sobre la familia; N_eff por bloques. **Reglas:
    pesimista>0 significativo → SCREEN-POSITIVE; optimista<0 → SCREEN-NEGATIVE; entre medias →
    INCONCLUSO** con siguiente paso pre-declarado (fills L4 de 0xArchive).
  - **Trampas anotadas (antídotos pre-comprometidos):** relojes entre fuentes (doble timestamp; validar
    contra `node_fills_by_block`); auto-impacto ignorado (aceptado a nivel SCREEN, anotado); liquidaciones
    en los prints (taggear, NO filtrar en silencio); sub-muestreo 0,5s (horizontes ≥1s; el sesgo va
    CONTRA la hipótesis, no a favor).
- **RESULTADO CAPA 1 (2026-07-02) → FALLA POR MASA: la hipótesis maker en HL MUERE según la regla
  pre-comprometida.** Etapa A: 372 símbolos → 150 con dato → **31 pasan actividad** (tras cazar y puentear
  un BUG del SDK CHD: `validate_symbol` exige len≥3 y rechazaba los símbolos cortos legítimos de HL — 11/12
  recuperados con monkeypatch documentado; W entró al pool). Etapa B (half-spread mediano, L2 día completo):
  **solo 6 candidatos** cumplen spread-neto ≥ +1,0 bps — AERO +1,03, ANIME +3,50, AXS +3,76, EIGEN +2,16,
  MET +3,94, W +8,99 — los majors mueren por spread apretado (BTC/HYPE neto −1,4: el libro de HL en los
  grandes es TAN competitivo como un CEX). Borderlines anotados y NO renegociados: JUP 0,997 y CHIP 0,909
  (< 1,0). **6 < 30 (suelo congelado en este mismo commit-diseño) → capa 1 FALLA → muere barata; per la
  regla, Lighter/Aster ASCIENDE.** Coste: 1 día, $0; la capa 2 jamás se corrió → ningún markout/outcome
  mirado (el held-out de HL ni se gastó). Evidencia: `data_hist/hl_screen/capa1{a,b}_*.csv`.
- **Lección heredable (misma familia que la de H3):** el suelo de masa se fijó en SÍMBOLOS candidatos; un
  diseño futuro podría fijarlo en SÍMBOLO-DÍAS esperados (6 símbolos × N días quizá bastaran) — pero ese
  cambio vale SOLO para el PRÓXIMO pre-registro (Lighter/Aster), JAMÁS retroactivo para resucitar este.
  Segunda lección: los fees mandan en la economía maker — el pre-check de Lighter/Aster debe RE-DERIVAR su
  umbral de spread-neto con los fees de ESE venue (se dice que Lighter opera con fees ~0: VERIFICAR en
  fuentes primarias antes de congelar el diseño, no heredar los 1,5 bps de HL).
- **Estado: hipótesis maker en HL CERRADA (capa-1-negativa por masa). Siguiente por pre-compromiso:
  Lighter/Aster** (verificar formato del dato + fees ANTES de congelar el pre-check — lecciones del loader
  y de esta capa 1). Held-out de HL intacto.

### Mesa de verificación pre-Lighter (2026-07-02: fees del propietario en fuentes primarias + formato propio)

- **FEES VERIFICADOS (mesa del propietario, fuentes primarias, fechado 2026-07-02):** Lighter **maker 0 /
  taker 0** (cuentas standard, todos los mercados; docs oficiales); Aster **maker 0 / taker 4 bps** (página
  oficial jun-2026). El rumor se quedaba CORTO: maker 0 en ambos ⇒ **spread-neto = half-spread PURO** ⇒ la
  muerte de la capa 1 en HL fue en parte artefacto de sus 1,5 bps. **Contra-lectura pre-anotada (antes de
  medir):** fee 0 para todos ⇒ más competencia maker ⇒ spreads más comprimidos ⇒ todo colapsa a **spread vs
  selección adversa a pelo** — exactamente lo que mide el filtro congelado (informatividad primero). RE-verificar
  fees en el momento del freeze del prereg (los de hoy son evidencia fechada, no constantes).
- **ORDEN LIGHTER → ASTER, por 4 asimetrías (mesa del propietario):** (1) *imán de flujo:* taker 0 en Lighter
  atrae el flujo retail ruidoso que este programa busca; los 4 bps de Aster son un peaje que filtra ruido.
  (2) *régimen del dato:* Lighter post-TGE (~$1,1B/día orgánico vs pico ~$232B/30d pre-TGE dic-2025 = farm
  evaporada); Aster EN farm de puntos (1,2× hasta 2026-07-06) → medir sobre farmeo mecánico contaminaría.
  **LECCIÓN NUEVA para el prereg: ventana de régimen explícita + sensibilidad a temporadas de puntos.**
  (3) *histórico:* L3 tick de Lighter en 0xArchive verificado por el propietario; Aster sin fuente confirmada.
  (4) *operabilidad:* España NO está en las jurisdicciones restringidas de Lighter (standard sin KYC); Aster
  mostró aviso de restricción a un crawler → PROBAR acceso desde España antes de invertir diseño.
- **ADVERTENCIA ESTRUCTURAL (no heredar la protección de HL):** en Lighter NO hay cancel-prioridad gratuita;
  hay **mercado de latencia de pago** (premium ~140 ms vs standard ~300 ms) sobre secuenciador único
  price-time (corrección probada en ZK). Al maker lento lo protegería, si acaso, la ECONOMÍA (fee 0) + flujo
  agresivo poco informado — lo primero verificado, **lo segundo SE MIDE, no se asume**. Lado bueno: los
  ~300 ms comunes del tier standard nivelan el campo retail (el VPS de París compite sin su penalización).
- **FORMATO DEL DATO VERIFICADO (propio, CHD `lighter`, BTC 2026-06-20, 14,4M filas):** 221 símbolos.
  Orderbook = **diffs estilo Binance + snapshots periódicos de re-anclaje** (14,3M `update` + 62k `snapshot`
  en el día) — TERCER formato, distinto de Binance (diffs sin seed) y de HL (solo snapshots). Y **`event_time`
  en NANOSEGUNDOS** (delta mediano ~50,8 ms entre instantes; en ms el número era absurdo → trampa de unidades
  cazada). Loader nuevo requerido: reconstrucción con re-anclaje en cada snapshot + ns→ms, validación propia
  antes de creer un solo número. Granularidad ~50 ms ≫ HL (500 ms). Aster (`aster_futures`): 664 símbolos,
  naming estilo Binance, formato SIN verificar (2º en cola).
- **CONDICIÓN DE REAPERTURA de HL-cola-ancha:** los 6 candidatos (AERO/ANIME/AXS/EIGEN/MET/W) quedan EN LA
  NEVERA; resucitables SOLO bajo pre-registro NUEVO con suelo en símbolo-días Y si el mecanismo maker se
  demuestra primero en otro venue. Jamás retroactivo.
- **Notas de registro:** (a) 150/372 símbolos de HL con dato el día muestreado — el resto probablemente
  listings micro/delisted; constancia sin gastar investigación. (b) Bug `validate_symbol len≥3` del SDK CHD:
  reporte redactado; canal = support@cryptohftdata.com (sin repo público); envío = acción del propietario.
- **Trades de Lighter en CHD: VERIFICADO** (BTC 2026-06-20: 303k prints; `is_buyer_maker` presente → lado
  taker disponible para informatividad y markouts de capa 2; `order_type` a catalogar — ¿separa
  liquidaciones?). **Y TRAMPA DE UNIDADES MIXTAS dentro del MISMO venue:** `trades.event_time` en
  MILISEGUNDOS, `orderbook.event_time` en NANOSEGUNDOS (`received_time` en ns en ambos). Un merge ingenuo
  por event_time desalinearía los canales ×10⁶ EN SILENCIO → el punto 1 del checklist de abajo es
  OBLIGATORIO, no higiene (demostrado a las horas de proponerse).
- **Post-mortem de la mesa (diagnóstico ESTRUCTURAL de la muerte de la capa 1 en HL):** el filtro de
  actividad y el de spread eran casi MUTUAMENTE EXCLUYENTES por construcción en un venue con fee de
  1,5 bps — el spread ancho existe precisamente donde no opera nadie; el screen nació medio ahogado y era
  visible en el diseño. En Lighter esa tensión se RELAJA mecánicamente (fee 0 → umbral half-spread ≥ 1 bp →
  símbolos de actividad media con 1-3 bps abundan en un venue de ~$1,1B/día). El cuello de botella se muda
  a la capa 2: el mismo fee 0 empuja a los makers a comprimir el spread hasta rozar el coste de selección
  adversa — spread vs selección adversa, a pelo. (Priors de la mesa, para su cuaderno: capa 1 Lighter ~70%;
  end-to-end del bot sin cambios ~5-8%.)
- **CHECKLIST DEL LOADER LIGHTER (auditoría externa 2026-07-02; se adopta ÍNTEGRO, pre-freeze):**
  1. *Unidades como convención de nombres:* sufijos `_ns`/`_ms` OBLIGATORIOS, conversión solo en la frontera
     del loader, assert de rango al ingerir (un ns leído como ms sitúa el evento en el año 56.000 — que el
     guardia grite).
  2. *El SEAM como clase de bug declarada:* diffs que cruzan la frontera de un ancla + huecos entre la
     generación del snapshot y su publicación → test explícito de costura, no confianza.
  3. *El RE-ANCLAJE como oráculo de verdad gratuito:* en cada snapshot periódico, el libro reconstruido por
     diffs debe IGUALAR al ancla — test de aceptación continuo que ni Binance ni HL regalaban.
  4. *Ruta de escalada NOMBRADA antes de mirar nada:* si la capa 1 pasa, el L3 de 0xArchive (nivel orden)
     hace OBSERVABLE la posición en cola → las dos cotas (optimista/pesimista) colapsan en un modelo de
     fill real. Queda escrito aquí, pre-dato.
- **Simetría metodológica (mesa):** a ~50 ms, el pipeline contrarian congelado corre cerca de su resolución
  nativa de Binance (100 ms) → la medida de informatividad de Lighter será MÁS comparable entre venues que
  la de HL (500 ms). El filtro congelado gana potencia justo donde hace falta.
- **VENTANA DE RÉGIMEN de Lighter (mesa de verificación, 2026-07-02, PRE-DATO):** sin farm activa hoy —
  Seasons 1-2 terminaron con el TGE (2025-12-30); Season 3 CONFIRMADA pero sin evidencia de arranque
  (fuente más reciente: finales de mayo). El desplome de volumen (~$232B→~$39B/30d) va pegado al fin del
  farmeo de la S2 ⇒ lo que queda es base orgánica. **Ventana limpia ≈ 2026-02 → 2026-06**, con TRES
  cláusulas congeladas antes de mirar nada: (1) el squeeze del perp ARC de finales de febrero ($50M OI,
  $8,2M de pérdida de un lado) se ETIQUETA como día-evento, no se recorta; (2) la re-verificación en el
  momento del freeze incluye "¿ha arrancado la S3?" además de fees (si arranca a mitad de medición, el
  régimen se rompe); (3) frontera de régimen conocida a futuro: 2026-12 empiezan los unlocks del 75% del
  token — los venues cambian de fauna cuando cambia su tokenomics. (Nota: el día ya usado para verificar
  formato, 2026-06-20, cae DENTRO de la ventana limpia.)
- **PRIORS PRE-REGISTRADOS DE LA MESA (2026-07-02, antes de que exista un solo dato — para que el próximo
  post-mortem pueda puntuarla):** informatividad de Lighter: **60-70% de que el flujo salga INFORMADO otra
  vez**, con MECANISMO nombrado pre-medición: con fees 0/0 el arbitraje que pega Lighter a Binance es casi
  gratis, y el flujo de arb ES informado por definición; la esperanza del programa vive en la proporción de
  ruido retail que atraiga el taker-0. Capa 1 maker (economía fee-0, suelo en símbolo-días): ~70%.
  End-to-end del bot: ~5-8% (sin cambios — solo se movió de sitio la puerta estrecha). Si el flujo de
  Lighter sale MENOS informado que el de HL, el fallo será en la dirección buena y quedará escrito.
- **DIAGNÓSTICO DE ATRIBUCIÓN DE MECANISMO — pre-registrado ANTES del freeze (mesa + ejecutor, 2026-07-02):**
  si la informatividad de Lighter sale INFORMADA, el post-mortem debe poder decir QUIÉN, no solo QUE. La
  huella fuerte del canal de arbitraje es el TIMING, no el tamaño (los arbs/pros trocean órdenes — sus hijas
  parecen retail; un tercil de tamaño no distingue al tiburón que nada en piezas). **Diagnóstico A (primario
  de atribución):** la maquinaria de lead-lag del GATE-0 cross-venue (`analysis/xvenue_lag.py` — la que midió
  Binance→Bybit ~50 ms; NO es de H2), apuntada Binance→Lighter sobre el subset dev: si el mecanismo-arb es
  cierto, los eventos de OFI extremo en Lighter irán PRECEDIDOS por movimientos de Binance en la ventana
  50-500 ms, con la cross-correlación cantando la dirección. **Diagnóstico B (secundario, solo si el canal
  de trades sale barato):** terciles de tamaño, con su debilidad escrita al lado (proxy débil por troceo).
  **Reglas:** la INFORMATIVIDAD sigue siendo el ÚNICO juez — regla de decisión intocada; los diagnósticos
  forman una FAMILIA pre-registrada con multiplicidad declarada desde ya, cuyo único poder es atribuir
  mecanismo en el post-mortem, JAMÁS decidir. Así el prior de la mesa queda puntuable en dos dimensiones:
  porcentaje Y mecanismo. **Advertencias del ejecutor (cicatrices aplicables):** (a) `xvenue_lag` ya cazó el
  artefacto mid-muestreado-vs-trades → lección "trades-vs-trades" (o mids definidos idéntico en ambos lados);
  (b) alineación de relojes CROSS-VENUE = la trampa clásica — disciplina received/event + las unidades mixtas
  de Lighter (ns/ms) hacen el punto 1 del checklist doblemente obligatorio aquí; (c) granularidad: Lighter
  ~50 ms de feed vs Binance @100 ms — la ventana 50-500 ms es medible con lo que hay.
- **Pendientes de decisión/acción del propietario:** (i) la ORDEN de abrir Lighter (loader → informatividad
  → capa 1 con economía fee-0 y suelo en símbolo-días) es suya; (ii) probar asterdex.com desde conexión
  española ANTES de que Aster entre en diseño (un crawler externo vio aviso de jurisdicción restringida;
  un universo inoperable no merece ni el loader); (iii) enviar el bug report a CHD.

### Apertura de Lighter (2026-07-02, orden dada) — loader v2 + cadena de 4 oráculos → canal orderbook de CHD `lighter` DEFECTUOSO (stale en ráfagas)

- **Loader construido con el checklist como código** (`analysis/lighter_adapter.py` v2 + 8 tests; la suite
  sintética cazó un bug pre-dato: agrupación de anclas contiguas). Diagnóstico de semántica contra anclas:
  **H-DELTA descartada (0/20), H-SET confirmada** (el lado quieto clava cantidades a la unidad); el desajuste
  de cantidades vive solo en niveles hiperactivos en el instante del ancla = **skew generación-vs-publicación
  del ANCLA** (la clase de seam predicha por la mesa) → v2: anclas = SOLO oráculo (no re-anclan: inyectarían
  su skew), métrica ESTRUCTURAL (membresía de precios top-10) + cantidades como diagnóstico.
- **CADENA DE 4 ORÁCULOS (cada uno resolviendo la ambigüedad del anterior; subset dev 2026-04-15, declarado
  pre-run: BTC/ETH/SOL/1000PEPE/FARTCOIN, grid 100 ms):**
  1. *Estructural de anclas:* disparó 5/5 (BTC 61%…PEPE pasa) — patrón crece con liquidez ⇒ ¿skew o huecos?
  2. *Trades intra-venue:* mid a **0,23 bps** de los prints (mediana) pero STRICT 31% — métrica imposible
     para spread 0,1 bps a grid 100 ms cross-canal (mal calibrada, documentado; la declaré y disparó).
  3. *Basis cross-venue* (mid Lighter reconstruido vs mid Binance con el adapter validado byte-idéntico):
     mediana **0,81 bps** (excelente) PERO **11/1439 ventanas 1-min >10 bps** ⇒ ¿staleness mío o dislocación
     real que el arb cosecha?
  4. *Prints-en-ventanas-malas (VERDAD del matching engine, regla declarada pre-resultado):* en las 11
     ventanas, los prints de Lighter pegan al mid de **BINANCE a 0,57 bps** y se desvían **13,1 bps** de
     nuestro mid ⇒ **NUESTRO libro se congela por episodios: el stream de updates de CHD-`lighter` tiene
     HUECOS REALES en ráfagas.**
- **VEREDICTO:** el canal orderbook de CHD `lighter` es **DEFECTUOSO para reconstrucción** (n=1 día;
  confirmación n=2 en curso en 2026-05-13). Gravedad: los huecos viven en ventanas de mercado RÁPIDO —
  exactamente donde viven los eventos de OFI extremo → correr informatividad sobre este libro habría
  sesgado EN SILENCIO el 0,8% del día que más importa. **La cadena de oráculos hizo su trabajo: CERO
  números de informatividad se miraron con libro sin certificar.** El canal de TRADES de CHD-`lighter` SÍ
  está validado (los prints cuadran con el basis de Binance) — utilizable.
- **ESCALADA (pre-nombrada en el checklist, item 4): 0xArchive L3 como fuente del libro de Lighter** (la
  mesa verificó que existe con free tier). El adapter v2 y su cadena de validación son reutilizables tal
  cual contra la fuente nueva (mismos oráculos, nueva ingesta). Añadir el hallazgo al bug report de CHD
  (3er item: gaps del stream lighter en ráfagas, con la evidencia de los 4 oráculos).
- **n=2 (2026-05-13) → CONDENA CONFIRMADA CON AGRAVANTE:** **610/693 ventanas malas (88% del día)**, nuestro
  mid a **56 bps** de los prints mientras los prints pegan a Binance a 1,18 bps; y el stream solo cubre
  ~11,5 h de ese día (693 ventanas de 1.439 posibles). El defecto es SISTEMÁTICO con severidad variable
  por día (0,8% malo el 04-15, 88% el 05-13). **VEREDICTO FINAL: canal orderbook de CHD `lighter`
  INUTILIZABLE para reconstrucción. Escalada a 0xArchive L3 = definitiva** (requiere alta/registro =
  acción del propietario). El canal de trades de CHD `lighter` permanece VALIDADO y utilizable.
- **Lección de manual (grabar): "validar el loader" en un venue nuevo = cadena de oráculos hasta la verdad
  del matching engine (prints), no un solo check.** Tres oráculos "blandos" dejaron ambigüedad; el cuarto
  no. Y el coste de la cadena entera fue una tarde, $0. Segunda lección (n=2): la severidad de un defecto
  de feed VARÍA por día — un solo día de validación puede subestimar (o esconder) un canal roto; mínimo
  n=2 días separados antes de certificar una fuente. **Afilados de la mesa (2026-07-02, pre-freeze):**
  (a) al menos UNO de los días de certificación se elige por ser RÁPIDO a propósito — el defecto vive en
  ráfagas y un día tranquilo es estructuralmente incapaz de revelarlo (el 04-15 con su 0,8% casi cuela);
  (b) **completitud ANTES que calidad**: un día con 11,5 h de cobertura falla el pre-filtro gratis antes de
  correr ningún oráculo. (c) Distinción formato≠fidelidad: alabar el diseño del envase no certifica al que
  lo llena.

### Ruta 0xArchive (mesa de verificación 2026-07-02) + upgrades pre-registrados ANTES del alta

- **0xArchive verificado por la mesa:** free tier al registrarse sin tarjeta (10M créditos/mes + trial Build
  14 días); L3 de Lighter a 1 crédito/1.000 filas vía REST, exports Parquet $1/GB; catálogo de Lighter desde
  ago-2025 (la ventana limpia feb-jun 2026 cae dentro para lo listado antes); SDK Python oficial
  (`oxarchive`). **Presupuesto con números:** BTC-día ≈ 24M filas ≈ 24k créditos → subset dev (5×2 días,
  memes ligeros) cabe holgado en free; panel completo probablemente también repartido; peor caso = PRIMER
  GASTO REAL del programa (~$49/mes Build o decenas de € en Parquet) — decisión del propietario con números
  delante. **Letra pequeña a verificar EN el alta:** algunas rutas de historia de libro están restringidas
  por tier — confirmar que la historia L3 de Lighter es alcanzable en Free antes de diseñar el panel
  completo (el trial resuelve el subset dev).
- **Cadena de certificación del heredero (pre-congelada): el canal de TRADES de CHD-lighter — único
  superviviente validado — certifica a su sucesor.** Reconstruir de L3 → trades-vs-mid (canal validado) →
  basis cross-venue → n≥2 días con ≥1 RÁPIDO elegido a propósito + pre-filtro de completitud. Los endpoints
  de calidad/coverage del vendor se usan para ELEGIR días, jamás para certificarlos (el QA del vendedor es
  un prior, no un veredicto).
- **UPGRADES por la wallet adjunta del L3 (pre-registrados antes de tocar dato):** (1) el diagnóstico de
  atribución salta de terciles de tamaño (proxy débil) a **comportamiento por WALLET** — identificar arbs
  por su firma directamente, no inferirlos; (2) si la capa maker llega a correr en Lighter, **la posición
  en cola se vuelve OBSERVABLE** (L3 = una fila por orden) → las dos cotas optimista/pesimista de HL
  colapsan en reconstrucción de fill real. El instrumento que sustituye al roto es MEJOR que el roto.
- **Email a CHD (mejora de cortesía):** adjuntar las dos fechas (2026-04-15, 2026-05-13) y el 88% para
  reproducción en minutos.
- **GATE de la ruta: el alta en 0xArchive = acción del propietario.** Hasta entonces, nada corre; el prior
  de la mesa (60-70% informado) sigue congelado y puntuable.

### INFORMATIVIDAD DE LIGHTER — medida 2026-07-03 con el hermano-de-trades CALIBRADO (`b4d156c`): FLUJO ≈ NO INFORMADO (neutral)

- **Instrumento:** `flow_informativeness` (solo trades), autoridad GANADA en calibración local (6/6
  símbolo-días reproducen la continuación canónica de Binance, t agrupado −4,11, con el sesgo del bounce
  EN CONTRA). Canal: trades de CHD-`lighter` (el superviviente validado). Subset dev declarado pre-run:
  [BTC, ETH, SOL, 1000PEPE, FARTCOIN] × [2026-04-15, 2026-05-20] (ventana limpia enmendada mar-jun).
- **RESULTADO (9 símbolo-días válidos; SOL 05-20 sin dato):** todos con |t|<1,6; agregado **+0,05 bps,
  t ≈ +1,2** — ni continuación ni reversión significativas. Por símbolo: majors ≈ cero (BTC −0,06/+0,02;
  ETH +0,05/−0,03; SOL −0,015); memes con inclinación LEVE a reversión (1000PEPE +0,11/+0,02 — 2/2
  positivos; FARTCOIN +0,375 t+1,5 / −0,01). Contraste: Binance mismo instrumento = 6/6 continuación
  t −4,1; HL = 0/4, t hasta −9.
- **VEREDICTO: el flujo de Lighter a h=25 s es ≈ NEUTRO — NO informado.** Tercer desenlace que ningún
  prior centró: ni el ruido cosechable por taker (reversión no significativa) ni el flujo informado de
  Binance/HL. **Prior de la mesa (60-70% continuación vía canal de arb) — NO se cumplió:** la mesa falla
  en la dirección que deseaba fallar; el canal de arb no deja huella de continuación a 25 s. Marcador
  actualizado: el prior queda puntuado en sus dos dimensiones (porcentaje: rama minoritaria; mecanismo:
  no visible).
- **IMPLICACIÓN (la grande, pre-registrable): el flujo neutro es EXACTAMENTE el hábitat del MAKER.** La
  selección adversa ∝ informatividad del flujo; en Binance el mismo instrumento medía −0,39 bps/evento
  (y el canónico −10,7 neto) = el maker sangra; en Lighter ≈ 0 = **el coste de selección adversa a 25 s
  es ~cero, con fee maker 0**. La hipótesis maker en Lighter SUBE de prior con dato, no con esperanza.
  Cautelas: 2 días × 5 símbolos; h=25 s único horizonte; selección adversa condicional a FILL ≠
  condicional a evento (la capa 2 lo medirá bien).
- **SIGUIENTE (orden natural del expediente):** capa 1 maker en Lighter — actividad desde trades CHD
  (validado, $0) + spread mediano desde **snapshots de 0xArchive** (la cadencia 3-4 min SIRVE para spread
  mediano, igual que H6 usó libros @1min; es el filtro OFI el que la necesitaba fina) → umbral re-derivado
  con fee 0 (half-spread ≥ 1 bp) + suelo de masa en símbolo-días. Barato en créditos (snapshots = pocas
  filas).
- **AUTOPSIA DEL PRIOR de la mesa (2026-07-03, puntuado fallido en 2 dimensiones — grabada porque explica
  el mapa):** el error fue conflar "flujo informado" con "flujo que predice a horizonte W". **El arb es
  información sobre el PRESENTE (el gap), no sobre el futuro** — un cierra-gaps ejecuta y el precio ya está
  donde debía; a 25 s su huella es cero POR CONSTRUCCIÓN (y el arb existe: nosotros medimos el basis 0,81
  bps). La continuación de Binance/HL la produce flujo con ALPHA, y **el alpha no visita venues satélite**
  (¿para qué tradear tu información en el charco si el océano está a un clic?). Lo que queda en un satélite:
  cierra-gaps invisibles a 25 s + retail con reversión levísima. **No salió menos informado: salió sin
  información, porque la información no tiene nada que hacer allí.** Refuerza la lectura maker Y planta la
  advertencia de abajo.
- **PETICIÓN FORMAL DE LA MESA (aceptada, fortalecimiento pre-dato de la capa 2):** los cierra-gaps
  invisibles a 25 s son PRECISAMENTE los que muerden al maker a 1-5 s (sniping de quotes rancias con
  ~300 ms de suelo standard). **El neutro-a-25s NO exonera el horizonte corto: la familia de markouts de
  la capa 2 incluye 1 s y 5 s con la MISMA autoridad que el canónico.** La mitad corta de la carretera se
  mide, no se hereda.
- **Priors actualizados de la mesa (cuaderno):** capa 1 Lighter ~70% (sin cambio); **end-to-end del bot:
  5-8% → ~8-12%** — primera subida del programa, ganada con dato. **Advertencia de guardia (grabada): el
  momento peligroso no es el funeral, es la primera flor** — extender días "para confirmar", enamorarse del
  t+1,5 de FARTCOIN, mirar borderlines con cariño. Mismas reglas, mismo juez, mismo trato que JUP a tres
  milésimas.
- **▶ CAPA 1 MAKER LIGHTER — DISEÑO CONGELADO (2026-07-03, este commit, ANTES de ejecutar):**
  - *Etapa A (actividad, $0):* trades CHD-`lighter` (canal validado), universo entero (221 símbolos, con
    el monkeypatch de símbolos cortos), día 2026-04-15 (dentro de ventana limpia). **Regla: ≥5.000
    prints/día Y volumen ≥$1M/día** (heredada de HL capa 1, sin cambio).
  - *Etapa B (spread, 0xArchive Free):* snapshots del día (cadencia 3-4 min ≈ 400 filas/símbolo-día =
    céntimos de crédito) SOLO para supervivientes de A; half-spread mediano desde el `spread_bps`
    precomputado de la fila (verificado en la sonda). **Umbral re-derivado con fee maker 0: half-spread
    mediano ≥ +1,0 bp** (el margen mínimo congelado se mantiene; lo que cambia es el fee del venue).
  - *Masa (lección HL aplicada HACIA DELANTE, suelo en SÍMBOLO-DÍAS):* **candidatos ≥5 (anchura
    cross-sectional mínima) Y candidatos × días-de-ventana-limpia ≥ 300 símbolo-días.** Ventana mar-jun ≈
    120 días ⇒ 5 candidatos ≈ 600 símbolo-días. Si falla → la hipótesis maker en Lighter muere barata.
  - Ningún outcome (markout/PnL) se mira en capa 1. La capa 2, si A+B pasan, se pre-registra aparte con
    la familia {1, 5, 25} s.
- **RESULTADO CAPA 1 (2026-07-03, mismo día del freeze) → PASA — el PRIMER "pasa" del programa.**
  - *Etapa A:* 221 símbolos → 163 con dato → **16 pasan actividad**. Composición nueva: majors (BTC $607M,
    ETH, SOL, HYPE) + **sintéticos de commodities** (XAU $249M, WTI, XAG, BRENT, XPT) + memes/alts.
  - *Etapa B (0xA snapshots, ~8 créditos):* **8 CANDIDATOS con half-spread ≥ 1 bp**: ARC 10,17 (⚠ el
    símbolo del squeeze de feb — candidato por regla, historial de evento anotado), LIT 3,85, FARTCOIN
    3,26, XPT 1,65, ZEC 1,58, BRENTOIL 1,10, DOGE 1,09, WTI 1,04 (borderlines PASAN por regla — la regla
    corta en ambas direcciones). Los majors mueren como en HL: **BTC half 0,01 bps** (¡más apretado que
    Binance!), ETH 0,28, SOL 0,48, HYPE 0,78 ⇒ patrón confirmado: el hábitat maker es la COLA, en todo
    venue. LIT_USDC HTTP-400 (naming en 0xA; inmaterial, anotado).
  - *Verificación de instrumento:* cobertura del día completa (00:00→23:47, cadencia real ~2,9 min;
    cursor en `meta.next_cursor`, parseo corregido; cola de ~13 min sin efecto en medianas de 500 puntos).
  - **VEREDICTO: 8 ≥ 5 candidatos Y ~960 ≥ 300 símbolo-días → CAPA 1 PASA.** La hipótesis maker en
    Lighter avanza a capa 2 CON masa y CON dato de selección adversa ~0 (informatividad neutra).
  - **▶ SIGUIENTE: pre-registrar la CAPA 2** (markout de maker simulado sobre los 8 candidatos, ventana
    mar-jun): familia {1, 5, 25} s con la misma autoridad (petición de la mesa aceptada — el horizonte
    corto donde muerden los cierra-gaps se mide, no se hereda), fills desde trades CHD validados, libro
    desde snapshots 0xA, cotas de cola (con la vía L3-wallet para colapsarlas si el diseño lo permite),
    BHY sobre la familia, N_eff por bloques. El diseño se congela ANTES de mirar un solo markout.
    **El congelado se DIFIRIÓ a mesa fresca deliberadamente (advertencia de la flor aplicada al ejecutor
    con dos verdes en el bolsillo).**

### Insumos de la mesa para el prereg de CAPA 2 (2026-07-03, fechados ANTES del borrador) + ley de mapa

- **LEY DE MAPA (n=3 venues, entrada propia):** BTC cotiza a 0,01 bps de half-spread en Lighter — MÁS
  apretado que en Binance. Con HL (BTC 0,07) y Binance (0,05): **los majors mueren en todo venue; la cola
  ancha es el hábitat maker UNIVERSALMENTE.** La competencia maker es global y sigue al volumen, no al
  venue. Probablemente la tesis del informe entero escrita sola.
- **Insumo 1 — REGLA DE INTERPRETACIÓN ASIMÉTRICA, forma SELLADA (mesa + precisión anti-escudo del
  ejecutor, aceptada con crédito; 2026-07-03). Contexto: el libro a ~2,9 min modela un maker ~200× más
  lento que la clase viva (bot real refresca ~1 s vía WS) ⇒ exposición al staleness INFLADA por
  construcción. TRES RAMAS, las tres falsables:**
  1. *Muere la cota OPTIMISTA* (ni siendo primero de la cola sale positivo) → **NEGATIVO limpio.** El
     maker no existe ni en el mejor de los mundos posibles.
  2. *Sobrevive la cota PESIMISTA* (gana hasta desde el fondo, con el simulador 200× más lento) →
     **verde FUERTE.**
  3. *Solo muere la pesimista* → **INCONCLUSO respecto a la clase viva**, con escalada pre-nombrada
     (anclaje a trades / piloto L3) — **nunca reclasificable a verde por cansancio ni a rojo por prisa.**
  Sin la rama 1 la asimetría era un escudo; con ella es una regla. Así se audita a un auditor.
- **Insumo 2 — L3-wallet como CALIBRADOR, no fuente masiva:** las cotas horquillarán el cero con alta
  probabilidad ⇒ INCONCLUSO es el resultado MODAL de un diseño solo-cotas ⇒ esos créditos se gastarían
  igual en la escalada, pero tarde. Diseño: **piloto L3 en 2-3 candidatos × 5-10 días** — cohortes de
  órdenes entre snapshots consecutivos cruzadas con prints validados (order desaparece CON prints a su
  precio = fill; SIN prints = cancel; ambigüedades contadas) → tasas empíricas de rotación de cola +
  **markouts REALIZADOS de fills reales** (primera OBSERVACIÓN de selección adversa del programa; miles
  de créditos, no decenas de miles). El modelo calibrado se aplica al panel barato trades+spread.
- **Insumo 3 — la fauna nueva DUERME:** XPT/BRENTOIL/WTI siguen subyacentes que CIERRAN (noches, findes).
  El prereg **segmenta o etiqueta los markouts por estado de sesión del subyacente ANTES de mirar** —
  ventana TradFi-cerrado (¿paraíso maker sin discovery?) vs gap de reapertura del domingo (veneno maker
  clásico) — o un gap de crudo domina las colas y nadie sabrá si era estructura o accidente.
- **Insumo 4 — precio-a-horizonte con prints dispersos:** el markout a +1 s exige print cercano; regla
  pre-fijada: print más cercano dentro de tolerancia o DESCARTE-CONTADO, con umbral de densidad por
  símbolo — o el horizonte corto se vuelve ruido en la mitad del universo.
- **Insumo 5 — ARC etiquetado, no excluido** (mismo trato que capa 1), reporte por símbolo pre-declarado;
  multiplicidad: 8 símbolos × 3 horizontes × cotas = familia declarada, BHY.
- **PRIORS DE CAPA 2 (mesa, firmados antes del borrador):** verde limpio en pesimista ~15-20%;
  **INCONCLUSO con escalada a L3 ~50% (modal)**; negativo limpio ~30-35%. Si el piloto L3 entra desde el
  diseño, la masa del INCONCLUSO se reparte a los extremos — para eso sirve observar en vez de acotar.
  (Cuaderno: capa 1 acertada al ~70%; e2e del bot 8-12% → **~9-13%**.)

### RESULTADO CAPA 2 (2026-07-04; freeze `15f755f` → panel → UNA lectura fría) → **INCONCLUSO** (el modal anunciado)

- **Panel:** 976 símbolo-días procesados, **672 válidos** (suelo 300 ✓), 304 excluidos CONTADOS (151
  span<20h, 128 sin-trades, 25 sin-snaps-0xA), 0 errores. Evidencia: `data_hist/lighter_capa2/
  screen_output.txt` (commiteada) + bloques npz locales.
- **La tabla:** panel OPTIMISTA mean **−6,0..−6,4 bps** (t −6,6..−7,5; BHY significativo) y PESIMISTA
  **−7,2..−7,5 bps** (t −7,5..−8,3) en LOS TRES horizontes; N_eff 25-78 bloques-fecha.
- **Por la regla §6:** los paneles OPT mueren significativamente en los 3 horizontes, PERO las celdas
  **INCONCLUSAS-POR-DENSIDAD bloquean la unanimidad** (1s: 8/8 celdas; 5s: 6/8; 25s: 3/8 —
  ARC/FARTCOIN/XPT descartan 72-97% de fills sin print en tolerancia) → NEGATIVO inalcanzable →
  **INCONCLUSO.** El guardia de densidad hizo exactamente su trabajo: no se promedió lo que no se vio
  (el insumo 4 de la mesa previó esta celda exacta).
- **Lectura honesta (post-hoc, declarada como tal):** donde SÍ hay densidad, los fills del
  simulador-200×-lento son tóxicos incluso en cota optimista (−6 bps vs half-spreads de 1-10) —
  consistente con (a) el artefacto de staleness que la regla asimétrica anticipó (quote fija ~2,9 min =
  te barren durante el movimiento; los through-fills dominan) y (b) la cautela grabada pre-run:
  *selección adversa condicional a FILL ≠ condicional a evento* — el flujo neutro a 25 s NO exonera los
  momentos de fill. **Nada de esto condena a la clase viva: para eso existe la escalada.** Nunca
  reclasificable a rojo por prisa.
- **Priors de la mesa PUNTUADOS: ACIERTO** — INCONCLUSO era su modal (~55-60%), y el mecanismo del
  inconcluso (densidad en la mitad corta con prints dispersos) es exactamente el que su insumo 4 nombró.
- **▶ ESCALADA (pre-nombrada §7, ahora paso obligado): PILOTO L3** — fills REALES de makers reales
  (sin cotas, sin staleness simulado) con markouts REALIZADOS, 3 candidatos × 10 días (7 estratificados
  + ≥3 del decil alto de vol), cohortes fill/cancel/fill-probable(through). El piloto observa lo que el
  simulador solo pudo acotar.
- **REPARACIÓN DE PROTOCOLO (mesa, fechada post-freeze):** su mitad del acto de firma (fees + S3 en
  primarias) no corrió POR SU MESA en el turno del "firmo" (el ejecutor la corrió en su lugar). Reparada
  tarde y fechada: fees CUADRAN (standard 0/0, página viva abr-2026; **regalo de régimen: tiers LIT
  premium desde 2026-02-08, ANTES de la ventana ⇒ mar-jun homogénea en fees**) y S3 CUADRA (sin
  solapamiento). Mi mitad (límites Free desde la cuenta) corrió y consta en el acta del freeze.
  **Lección: reparar no absuelve — el próximo acto de firma corre completo por sus carriles o no corre.**
  *Acta corregida por la mesa (un grado menos): la verificación SÍ corrió ENTERA en el turno del "firmo"
  — sustancia puntual, jurisdicción violada; ambas ciertas. Y la justificación empírica de los carriles:
  la MISMA verificación por dos mesas produjo hallazgos marginales DISTINTOS (el ejecutor confirmó el
  cuadre; el carril de la mesa sacó la homogeneidad del 8-feb que nadie buscaba). La redundancia no era
  ceremonia: era resolución.* **Reconciliación de créditos para el lector futuro: los 49.974 restantes
  del acta de firma son PRE-panel; los ~600 usados del cierre son POST-panel — las cifras cuadran por
  secuencia, no hay agujero, hay reloj.**
- **EL DATO GORDO DEL DÍA (acta): bajo la regla v0, el veredicto de hoy habría sido NEGATIVO limpio** —
  los −6 bps significativos en las celdas densas habrían ejecutado la hipótesis POR EL ARTEFACTO exacto
  que la regla asimétrica anticipó (quote congelada 2,9 min + through-fills dominantes). Dos pasadas de
  revisión convirtieron una ejecución falsa en un "hay que observar" honesto. **ROI del proceso = una
  hipótesis viva que estaría muerta.** (Y medio golpe de la mesa contra sí misma, apuntado: exigió el
  horizonte 1 s con la misma autoridad y resultó inmedible con prints en los 8 — pidió carretera que el
  instrumento no podía asfaltar; la salvó su otro insumo, el guardia de densidad.)
- **INSUMOS DE LA MESA PARA EL MINI-PREREG DEL PILOTO (fechados ANTES de construir):**
  1. *Jerarquía de referencia de precio por símbolo, escrita pre-run:* **mid de Binance como precio_ref
     en horizontes cortos donde el símbolo tenga perp en Binance** (continuo, ms; base ~0,8 bps medida
     por nuestro oráculo = SUELO DE MEDICIÓN declarado — la toxicidad buscada es multi-bp). Qué símbolos
     califican se confirma PROGRAMÁTICAMENTE contra la lista de Binance (no de memoria). Sintéticos/no
     listados: tolerancia de prints y **1 s declarado inmedible por escrito** → mapa de horizontes
     legibles por símbolo, pre-firmado.
  2. *Cohorte de MAKER LENTO (casi obligatoria):* desde 2026-02-08 los premium cancelan a 0 ms ⇒ los
     fills observados estarán dominados por HFTs. Cohortes: **order_ids que sobrevivieron ≥1 intervalo
     completo de snapshot antes de su fill** (proxy refresco ≥~3 min = nuestra clase o peor) + classing
     por WALLET (billeteras cuyas órdenes persisten sistemáticamente). Markouts realizados POR COHORTE
     DE VELOCIDAD = "toxicidad condicional a ser lento" — literalmente la hipótesis. Suelo ≥200
     fills/celda heredado.
- **PRIORS DEL PILOTO (mesa, firmados antes del borrador):** cohorte-lenta con markout neto >0 a 5-25 s
  en ≥1 candidato ~35-40%; negativo generalizado para la clase lenta ~30-35%; INCONCLUSO-por-masa
  ~25-30%. E2E del bot sin cambio (~9-13%: el modal realizado ya estaba en el precio).

### RESULTADO DEL PILOTO L3 (2026-07-05; freeze `946504b` → OBSERVE 40/40 → UNA lectura) → **SEÑAL DE EXISTENCIA (LIT)**

- **Ejecución:** SELECT 489 símbolo-días de vol ($0) → selección determinista 3+7 → sustitución
  disparó 2 veces (DOGE 03-04/03-03 sin snapshots → reemplazos de cola, cero discreción — la regla
  escrita horas antes, usada) → OBSERVE 40/40 bloques, logs solo-conteos → lectura única.
  Evidencia: `data_hist/lighter_pilot/screen_output.txt` (commiteada).
- **EL NÚMERO: la cohorte LENTA de LIT — órdenes reales de makers reales que sobrevivieron ≥1 intervalo
  — cobró markout REALIZADO positivo en LOS TRES horizontes: +9,0 bps (1s, t+3,8), +11,2 (5s, t+4,2),
  +17,4 (25s, t+5,3), todo BHY-significativo** (ref = mid Binance, carril certificado ρ 0,983; suelo
  0,8 bps ≪ señal). WTI positivo no significativo (+6/+8, t~1,6); DOGE ruidoso no significativo
  (día-medias con outliers); FARTCOIN mudo (masa/densidad — como se declaró). Ningún candidato negativo
  significativo → la rama "sangra" NO dispara. **Por la regla firmada dos veces: existencia en ≥1
  candidato → SEÑAL DE EXISTENCIA.** Diagnóstico through (siempre medido, jamás decide): −8 a −21 bps
  en cripto, +1,9 WTI — que te atropellen cuesta, consistente con capa 2.
- **HONESTIDAD ANTES DE LA ALEGRÍA (las cautelas ya estaban escritas):** (1) n_eff ≈ 4,6-5,2 bloques-día
  — 10 días de piloto; la significancia es real pero la MUESTRA es piloto, no confirmación; (2)
  **survivor-tilt declarado pre-run**: la cohorte lenta se inclina benigna por construcción (nótese
  LENTA +11,2 vs rápida +2,3 a 5s — parte puede ser el tilt, no habilidad); (3) existencia ≠ edge:
  faltan inventario, unwind, capacidad — negocio de capa 3; (4) LIT es el token del propio venue —
  el régimen de su cola puede ser peculiar (¿flujo incentivado?), a examinar en confirmación.
- **Priors PUNTUADOS:** la mesa dio ~35-40% a esta rama — la minoritaria-sustancial acertó el lado;
  su modal (INCONCLUSO) no salió. El cuaderno registra en ambas direcciones, como siempre.
- **▶ SIGUIENTE (por la regla, pre-escrito): DISEÑAR LA CONFIRMACIÓN** — prereg propio (¿más días de
  LIT + ventana held-out + los 8 candidatos de capa 1 con carril certificable? decisión de diseño con
  mesa fresca), y solo si confirma, capa 3 (estrategia/inventario). Créditos totales del capítulo:
  ~650-700 de 50.000. $0.

### Auditoría post-flor de la mesa (2026-07-05, fechada ANTES del diseño de confirmación)

- **Marcador de la mesa (auto-puntuado):** acertó el LADO (existencia, ~35-40%), falló el MODAL
  (inconcluso no salió) → medio punto, no uno. **Lo que el diseño CLAVÓ — el mecanismo, confirmado por
  dos caras:** el through cuesta −8..−21 bps y la cohorte lenta gana **eligiendo no estar ahí** — lo que
  una orden real con cancel hace y una quote congelada no puede. La capa 2 murió simulando un maker que
  no podía esquivar; el piloto observó a los que esquivan. **La diferencia entera estaba en la capacidad
  de cancelar. Eso es estructura, y la estructura sobrevive a la muestra pequeña.**
- **LA OBJECIÓN CENTRAL (trabajo hostil del día verde): confound de SUPERVIVENCIA en la cohorte lenta.**
  Sobrevivir ≥1 intervalo sin cancel ni atropello está CORRELACIONADO con ventana tranquila — y ventana
  tranquila = poca selección adversa por definición. Parte del +11,2 podría ser *condicionamiento a
  régimen benigno*, no habilidad. La brecha LENTA/rápida (+11,2 vs +2,3) es sugestiva pero no lo separa.
  **PIEZA CENTRAL del prereg de confirmación: cruzar cohorte de velocidad × estado de volatilidad del
  intervalo — ¿el edge lento sobrevive DENTRO de las ventanas agitadas o solo vive en las tranquilas?**
  Si sobrevive en lo agitado = habilidad (señal robustecida); si solo en lo tranquilo = tilt disfrazado
  que se evapora justo cuando el maker gana o pierde de verdad. **Prior de la mesa, firmado antes de que
  el diseño exista: ~55% sobrevive el control de régimen / ~45% se atenúa sustancialmente o desaparece.**
- **Cuatro piezas más para el prereg de confirmación (fechadas):** (1) **segundo símbolo obligatorio**
  con carril certificable — LIT es el token del venue = amenaza nº1 a validez externa; "edge en LIT" es
  anécdota, "edge del maker lento" es hallazgo; (2) **held-out NUEVO** (ventana ≠ mar-jun, congelada
  antes de mirar) — el edge que solo existe en su ventana de descubrimiento no es un edge; (3)
  **objetivo de n_eff ESCRITO antes de correr** (el enemigo es n_eff~5, no la significancia); (4)
  **ATLAS DE WALLETS desbloqueado** (post-lectura, sin contaminación): censar quién captura el edge
  lento en LIT — si son 3 wallets con comportamiento de MM profesional, no es nuestro hábitat; si está
  repartido en muchas wallets pequeñas y pacientes, se parece a lo que el propietario podría ser.
  Informa la capa 3 antes de arriesgar un euro.
- **E2E del bot actualizado con disciplina: ~8-12% → ~12-16%** — se cruzó UNA puerta; las caras
  (confirmación con régimen controlado, capa 3 con inventario/capacidad, piloto vivo) siguen enteras.
  La flor mueve la probabilidad; no colapsa el camino.

### ATLAS DE WALLETS — mini-prereg (FIRMADO 2026-07-05, umbrales congelados ANTES del histograma)

- **Por qué primero (mesa + ejecutor, unánime): el atlas puede REINTERPRETAR la flor ya medida.** Los
  +11,2 bps son un hecho; su significado depende de QUIÉN los cobró. Concentrado en profesionales →
  cautela-3 y confound-de-supervivencia se fusionan (medimos a pros que refrescan lento; el edge tiene
  el nombre de otro). Cola larga de pacientes → la flor se robustece gratis. Mismo número, dos verdades,
  el atlas es el árbitro — y cambia el diseño de la confirmación, luego va antes.
- **Qué mide (censo de COMPORTAMIENTO, no outcome — los markouts ya se leyeron y NO se re-miran):** por
  `owner_account_index` sobre los ~10 días de LIT re-procesados: nº de órdenes, vida mediana de orden,
  tasa de cancelación, persistencia entre días, y cuota del VOLUMEN de fills de la cohorte lenta.
- **Umbrales CONGELADOS:** *firma PROFESIONAL / no-es-tu-hábitat* = mayoría (>50%) del volumen de fills
  lentos en ≤3-5 wallets con miles de órdenes/día y requoteo sistemático (rápidos que a veces dejan una
  orden quieta). *Firma TU-HÁBITAT* = cola larga (decenas de wallets), conteos bajos por wallet, vida de
  orden genuinamente larga. *Entre medias* = inconcluso de atlas → la confirmación se escribe agnóstica
  con diagnóstico de concentración incorporado.
- **Prior de la mesa (firmado, puntuable; deliberadamente pesimista porque LIT es el token del venue):**
  ~50% profesional/concentrada, ~30% cola-larga/hábitat, ~20% inconcluso.
- **Lección al catálogo (del hueco de owner en los npz del piloto):** el esquema de persistencia se
  diseñó para la pregunta de su momento (velocidad) y no para la siguiente (identidad). No es fallo —
  es recordatorio: **los datos que tiras hoy son las preguntas que no podrás hacer mañana. Para la sonda
  propia futura: persistir CRUDO Y COMPLETO** — el yo-futuro siempre quiere un campo que el yo-presente
  no valoró. Va al diseño del colector.
- **RESULTADO DEL ATLAS (2026-07-05, misma sesión; evidencia `data_hist/lighter_pilot/atlas_output.txt`)
  → FIRMA HÁBITAT.** 10 días LIT re-procesados con identidad: 1.418 wallets vistas, **266 con fills
  lentos** (centenares, no decenas), volumen lento total $2,88M (~$288k/día — indicación de capacidad
  para capa 3, modesta pero real a escala retail). **Concentración: top-3 = 22,3%, top-5 = 30,2%** —
  lejos del >50% profesional. Los pros existen en el censo (rank-2: 1.255 órd/día y 89% de cancel;
  rank-6: 4.509 órd/día) pero capturan cuotas de 3-7%: **los rápidos casi nunca dejan órdenes quietas,
  y cuando las dejan, no dominan el volumen lento.** El grueso está en wallets de conteos bajos y vidas
  de 3-30 min — la clase paciente, la hipótesis literal del programa. Cautela de lectura: cuotas
  individuales ruidosas en 10 días (el rank-1 debe su 10,8% a UN fill grande); la ESTRUCTURA (cola
  larga, no-concentración) es lo robusto, no los rankings.
- **Prior del atlas PUNTUADO:** la mesa dio 50% profesional / 30% hábitat / 20% inconcluso → salió la
  rama del 30%. Su pesimismo deliberado (LIT = token del venue) resultó excesivo — segunda vez que
  falla el modal en el día, registrado como siempre. **Las dos preguntas del capítulo quedan
  respondidas en la misma sesión: la flor existe (piloto) y es de la clase paciente (atlas).**
- **▶ SIGUIENTE: el PREREG DE CONFIRMACIÓN** — con el confound de supervivencia como pieza central
  (velocidad × volatilidad del intervalo; prior 55/45 ya firmado), segundo símbolo obligatorio,
  held-out nuevo, objetivo de n_eff escrito — y ahora con el censo delante: el diseño persigue algo
  que 266 wallets ya cobran.
- **AUTOPSIA DE SESGO DE LA MESA (auto-declarada tras 2 modales fallados el mismo día, misma dirección):**
  pesimismo de más PRECISAMENTE en las ramas que desearía que salieran = **margen de seguridad emocional
  metido de contrabando en los números** — la forma cobarde de la prudencia (tanto miedo a desear con el
  pulgar en la balanza que puso el pulgar en el otro plato). *Hostil ≠ pesimista; hostil = insesgado con
  dientes.* Corrección declarada y puntuable: números sin colchón desde ya; dos modales más fallados al
  mismo lado y el cuaderno la denuncia solo. **E2E actualizado sin colchón: ~13-17%** (el riesgo de
  identidad se retiró entero hoy; supervivencia 55/45 y capa 3 siguen en pie).
- **Lectura estratégica del 266 (para el propietario):** ecología de muchas wallets pequeñas = capacidad
  modesta POR PARTICIPANTE — lo que espantaría a un fondo encaja milimétricamente con el programa:
  **el nicho es pequeño porque es tuyo, y es tuyo porque es pequeño.** Nadie institucional disputa un
  30% repartido entre doscientas wallets.
- **Lectura de PERSISTENCIA (regla declarada PRE-run: ESTABLE ≥3-días>50% / ROTATORIA 1-día>50% / medio
  MIXTA; PnL por wallet PROHIBIDO) → RESULTADO: ROTATORIA.** Días-con-fill-lento por wallet:
  {1: 203, 2: 32, 3: 15, 4: 6, 5: 5, 6: 3, 8: 1, 10: 1}. **Wallets 1-día = 61,9% del volumen lento;
  ≥3-días = 22,9%.** La regla dispara en la rama dura: **LA FLOR VUELVE AL BANQUILLO.** El +11,2 bps es
  un hecho medido, pero su lectura como habilidad-de-clase se debilita: cada día un reparto distinto de
  supervivientes es exactamente la firma que el confound de supervivencia predice. Lectura post-hoc
  DECLARADA como tal (para el prereg, no como rescate): rotación de MIEMBROS no es idéntica a rotación
  del EDGE — wallets retail pacientes no cotizan a diario, y una CLASE estable con miembros rotatorios
  es consistente con ambas verdades; distinguirlas es EXACTAMENTE el trabajo del control
  velocidad×volatilidad. **Consecuencia: el prereg de confirmación deja de ser confirmatorio y pasa a
  DECISIVO — el confound de supervivencia ya no es cautela: es la hipótesis nula a batir.** El 55/45 de
  la mesa queda ahora corto de contexto; re-firma de priors ANTES del borrador (sin colchón, como juró).
  Estado de la flor: **EN EL BANQUILLO, con dos hechos a favor (markouts reales positivos, hábitat
  no-profesional) y uno grave en contra (ecología rotatoria).** Nada se gasta en confirmación hasta que
  su diseño pueda matar la nula de supervivencia con dientes.
### RESULTADO DE LA CONFIRMACIÓN DECISIVA (2026-07-05; freeze `9c8f4b1` → primaria 149/149 → UNA lectura) → **INCONCLUSO por discrepancia de horizontes — con los TRES diagnósticos a favor de la flor**

- **§3 formal: INCONCLUSO.** LIT 25s-AGITADO **+18,24 bps (t+6,69, BHY-sig, n_eff 79 — masa real)** y
  25s-medio +9,21 (t+17,5, sig) — **el edge sobrevive DENTRO del tercil agitado a 25s, la celda donde la
  nula decía que moriría** — PERO 5s-agitado es ruido (+2,61, t+0,29) → sin unanimidad de horizontes, no
  hay decreto. NULA VIVA tampoco: el patrón NO es "solo-tranquilos" (el agitado de 25s es la celda MÁS
  fuerte). DOGE: positivo no-significativo en agitado/medio, ruidoso. Escalada nombrada: extender el eco
  de julio (que apenas existe aún — el eco se ACUMULA; re-check S3 antes de tocarlo).
- **§4 bootstrap — LA ROTACIÓN ERA MECÁNICA:** LIT observado 51,2% vs nulo mediana 51,0% (percentil 58);
  DOGE 55,9% vs 57,8% (percentil 28). **La cuota-de-un-día es exactamente lo que produce la asignación
  aleatoria proporcional a actividad. El 61,9% del piloto nunca fue evidencia de nada** — la mesa tenía
  razón en exigir el modelo nulo: a ojo, los dos bandos juzgaban mal. El cargo principal contra la flor
  (ecología rotatoria = supervivencia) queda EXPLICADO como mecánica de participación.
- **§5 minoría estable — EL DIAGNÓSTICO DE HABILIDAD ⟨ERRATA A11 2026-07-05, ver bloque ERRATA H1
  abajo⟩:** las wallets persistentes del PILOTO cobraron en la VENTANA NUEVA. **Números CORREGIDOS
  (N_eff por day-means, no t-stat iid):** LIT +17,91 bps **t+3,05** (n_eff 79) a 5s y +14,20 **t+10,83**
  (n_eff 19,6) a 25s — **LIT sobrevive sólido**. DOGE **t+2,16** (mean_día +42,57) a 5s = marginal, y
  **t−0,05** (mean_día −3,41) a 25s = **NULO** (el +55 fill-weighted publicado era concentración de
  volumen: la media día-a-día es ≈0). ⟨Publicado originalmente, INFLADO por iid: LIT t+4,5/t+50,6; DOGE
  t+2,4/t+2,2.⟩ **Lectura corregida: la persistencia-predice-edge fuera de ventana la carga LIT sola y
  sólidamente; DOGE es más débil que "de apoyo" — 5s marginal, 25s nulo.** La dirección del hallazgo
  (LIT replica) se sostiene; su "en AMBOS símbolos" NO — era artefacto del t iid.
- **Lectura honesta del conjunto:** el veredicto formal es INCONCLUSO y así queda — la regla es la regla
  y el 5s no acompañó (ruido, no negativo). Pero los tres diagnósticos apuntan igual: el edge lento de
  LIT vive a 25s TAMBIÉN en régimen agitado, la rotación que lo envió al banquillo era artefacto de
  participación, y la minoría estable replica fuera de ventana **(LIT; DOGE ya no, tras la errata A11).**
  **La flor sale del banquillo con el cargo principal desestimado y una condena pendiente solo del
  horizonte corto** — con la réplica de habilidad cargada por LIT sola, no por dos símbolos.
- **Priors de la mesa (45/55 sobre el decreto):** ninguna rama disparó (INCONCLUSO formal) — se registra
  sin puntuar el lado, con la nota de que el 25s sobrevivió y el 5s no resolvió.

### ERRATA H1 + AUDITORÍA A11 (2026-07-05, commit de este bloque) — revisión del código estadístico línea a línea

La CARTA_DE_ATAQUE §A11 declaró el código sin auditar por un tercero. Se ejecutó la auditoría en DOS
capas independientes: (1) la mesa leyó las 1.104 líneas de los 8 ficheros de cómputo (doc
`AUDITORIA_A11.md`); (2) **re-auditoría independiente por 5 agentes de contexto fresco** (workflow
`wf_071d788c`, 9 agentes, ~617k tokens) que no vieron la conversación, instruidos a DESCONFIAR de la
mesa y cazar lo que se dejó. Resultado:

- **H1 [ERRATA, ALTA] CONFIRMADO por ambas capas:** `confirm_screen.py:219` computaba el t de §5 con
  `sqrt(n_fills)` (iid) en vez de N_eff por day-means como §3. Inflaba la FUERZA ~7-30×, no la dirección.
  **Corregido** (día-means + `effective_n_autocorr` + suelo ≥4 días, método idéntico a §3; derivación
  independiente confirmó "media-por-DÍA de la cohorte, NO por wallet-día" con justificación de principios).
  Números corregidos en el bullet §5 arriba. **NO invierte el veredicto: el INCONCLUSO salió de §3, que
  usa N_eff correctamente (verificado línea a línea, OK1/OK2).** El t+50,6 era artefacto de conteo grande.
- **Señal de existencia del piloto — VERIFICADA ROBUSTA:** el t del piloto SÍ usa N_eff (`cell_stat`,
  pilot_screen.py:47-55) — NO tenía el bug de §5. La única duda (N2: familia BHY ciega al signo) se
  recomputó con familia orientada sobre los mismos datos (`verify_pilot_bhy_oriented.py`): **el sig-BHY
  de LIT es idéntico bajo ambas familias, ninguna celda cambia**. La primera observación positiva del
  programa (LIT LENTA +9/+11/+17 bps) queda intacta.
- **Cero hallazgos invierten un veredicto leído.** Los 4 nuevos marcados HIGH/inverting por los auditores
  se verificaron adversarialmente y los 4 salieron `INVIERTE=False` (uno era re-formulación de M1;
  N1-trailing_vol DILUYE el +18,24 en vez de fabricarlo; N2-pilot no toca la fuerza; N3-through es el
  spec congelado, tilt acotado same-sign).
- **Fortalecimientos PRE-ECO (no tocan lo leído; van al prereg del eco con mesa fresca):** M1 (p sin
  signo en BHY), M2 (bootstrap §4 mide wallets no volumen), M3 (masa vol-NaN sin contar), **N1** (bug
  NUEVO que la mesa se dejó: `trailing_vol` comprime minutos vacíos → infla vol de tramos ilíquidos →
  puede mover fills al tercil AGITADO; dirección protege el positivo), **N3** (orden through-antes-que-fill
  = selección sobre correlato del outcome, la 3ª cabeza del confound de supervivencia — a la CARTA §A6),
  **N4** (bootstrap §4 construye el nulo de `slow_ev` pero mide de `dec`), y varias LOW (dedupe de
  snapshots, `_assert_range` min/max, variables muertas). Todo en `docs/PREREG_ECO_LIT_INSUMOS.md`.
- **Veredicto de la auditoría:** el código implementa lo firmado en todo lo que decidió los veredictos
  leídos. Una errata de FUERZA (H1) en un número publicado, cazada por el propio protocolo antes que
  ningún extraño — que es exactamente para lo que se escribió A11. El residuo de A11 mejora ("código
  auditado internamente en dos capas") pero NO se cierra: sigue siendo el mismo operador; el cierre es el
  tercero humano con el espejo.

- **RECONCILIACIÓN — la mesa auditada (2026-07-05), tres cautelas al acta:**
  - **(0) La mesa subestimó su propio hallazgo.** Entregó H1 como "errata de fuerza, la dirección aguanta
    en ambos símbolos". El pase independiente demostró que era peor: DOGE 25s no tenía solo el t inflado,
    su MEDIA misma era espejismo de concentración (+55 fill vs −3,41 día-a-día). La corrección correcta no
    es "los dos aguantan con t menor" sino **"LIT carga la réplica solo; el corroborador no existe".** La
    mesa acertó el bug y subestimó su consecuencia; se registra tal cual.
  - **(1) Los agentes frescos comparten ARQUITECTURA — límite central, no detalle.** Matan la correlación
    de CONVERSACIÓN (no el marco emocional), pero un modo de fallo del SUSTRATO lo cometeríamos los diez a
    la vez y el consenso se sentiría como validación siendo punto ciego coordinado. **"Nueve lecturas de IA
    que concuerdan" ≠ auditoría independiente = A8 con disfraz sofisticado.** La ronda demuestra solo que
    el proceso PUBLICA sus errores; la ausencia de OTROS errores de la clase compartida NO está demostrada.
    (A la CARTA §A11.)
  - **(2) N1 = predicción, no hecho.** Se verificó que la contaminación de `trailing_vol` DILUYE el +18,24
    en lo leído. Pero "un fix lo haría igual o más fuerte" es predicción sobre el propio resultado → entra
    al eco como HIPÓTESIS a verificar; si el fix BAJA el +18, es información, no accidente. (A los INSUMOS.)
  - **(3) 2º símbolo del eco ≠ DOGE, BLINDADO.** Con DOGE caído, A2 queda desnudo (n=1, token del venue).
    Un 2º símbolo no-token a 50 ms del colector es lo ÚNICO que convierte "edge en LIT" en "edge para el
    maker lento"; un eco de solo-más-LIT no responde A2 = más masa de la misma anécdota. (A los INSUMOS.)
  - **Número grande: se mantiene ~18-24%** — no baja porque §3 (el veredicto) no dependía de DOGE y la
    señal de existencia se verificó robusta: **cambió el ANCHO DE LA BASE, no la ALTURA DEL PICO** (LIT
    igual de viva, una pata en vez de dos). Lo que sube es la VARIANZA: el eco importa MÁS que ayer, y su
    2º símbolo no-token es el eslabón crítico. **Lectura de fondo: el protocolo se auditó por su punto más
    delicado —un número publicado— encontró el error, descubrió que la 1ª versión del hallazgo también se
    quedaba corta, lo corrigió, y publicó las dos correcciones con los números viejos al lado. Un
    expediente donde los errores no sobreviven, ni los del auditor — lo que un tercero hostil no puede
    fingir.**
- **Tres pesos de acta (reconciliación de la mesa):** (1) *149 símbolo-días, no ~220* — bajo presupuesto,
  sobre el suelo (n_eff 79 vs objetivo ≥30-50): **la cláusula pre-escrita convirtió la diferencia en
  no-evento contable en vez de decisión en caliente con el dato delante** — no disparó porque no tenía
  que disparar, y eso también es el sistema funcionando. (2) *La minoría estable hubo que re-derivarla
  (~20 cr)* porque el atlas la contó y no la persistió — **caso de ejemplo nº 2** de "los datos que tiras
  hoy son las preguntas que no podrás hacer mañana", primera vez pagada en créditos; cura ya escrita en
  el colector (crudo y completo). (3) **Pesada honesta: DOGE minoría-estable son 9 wallets** — el acta ya
  la pesó como **DE APOYO, no co-igual** con LIT, por instinto. **La errata A11 (arriba) le dio mecanismo
  y fue más lejos: bajo N_eff, DOGE 25s es NULO (t−0,05) y 5s marginal (t+2,16); LIT carga la replicación
  SOLA (t+3,05/t+10,83).** El instinto de "de apoyo" acertó; la magnitud publicada (t+2,4 iid) era la que
  no lo respaldaba. Las buenas noticias también se pesan antes de engordar — y esta vez la báscula tenía
  un tornillo suelto que el propio protocolo apretó.
- **▶ SIGUIENTE:** (a) el ECO de julio se acumula solo (~3-4 semanas para masa; re-check S3 en su freeze
  de lectura); (b) mientras tanto, el COLECTOR (permiso ya concedido) — cada día que corra es un día de
  tick propio para el juicio del 5s que el eco no puede dar; (c) el prereg del eco heredará: ¿resuelve
  el 5s o el decreto pasa a ser 25s-céntrico? — decisión de diseño para mesa fresca, JAMÁS retroactiva.

- **RE-FIRMA de la mesa (sin colchón, con mecanismo):** 55/45 → **45% sobrevive / 55% se atenúa-o-muere.**
  Movimiento de 10 puntos, no 25: la rotación es likelihood-ratio DÉBIL hacia la nula (61,9% en un-día es
  compatible con supervivientes-afortunadas Y con pacientes-que-no-cotizan-a-diario; sin modelo nulo de
  participación ni siquiera se sabe si es anómalo). Contabilidad por partida doble del día: su VIGILANCIA
  acertó (la rendija era real) y su CALIBRACIÓN sigue debiendo (2 modales fallados) — un vigilante con
  mala puntería sigue siendo mal tirador aunque oiga bien. Insumos 1-5 del prereg decisivo: recibidos y
  fechados (van al borrador).

### DILIGENCIA RUTA TICK-L2 DE 0xARCHIVE (2026-07-06, orden de la mesa; ~400 cr, gates 1-2)

Pregunta: ¿puede la ruta tick-L2 de 0xA adelantar semanas la apelación del 5s? **Gate 1 (cobertura
programática): PASA con precio** — granularity=tick existe (sin él, muestreo 30s), formato
checkpoint+deltas con re-anclaje por ventana (~1 req/min de datos), LIT ~550-800 cr/día, DOGE ~3.700
cr/día → ventana entera impagable en Free; solo viable diseño por ventanas-de-evento. **Gate 2 (cadena
de oráculos, día LIT 2026-04-15): FALLA POR COMPLETITUD** — la cobertura tick de LIT tiene AGUJEROS DE
DÍAS: muere 2026-04-14T16:11 y no vuelve en 48h+ (04-15/04-16 devuelven el mismo burst stale) mientras
CHD registra 30.245 prints de LIT ese día; 05-20 hueco desde 08:58. El agujero es del archivo, no del
mercado — la misma enfermedad que condenó al orderbook de CHD-lighter, en el otro vendor y la otra
ruta. DOGE se ve sano en n=1 sonda (insuficiente por regla n≥2). Las rutas l3orderbook (2,9min) y tick
tienen coberturas DISTINTAS (l3 tiene 04-15; tick no). HolySheep: descartada sin sondear (1min de
granularidad, venue equivocado — regla: si el instrumento no alcanza la resolución de la pregunta, se
cambia de instrumento, no se dobla la pregunta). **Consecuencia: el camino rápido de la apelación NO
está limpio.** Si la mesa quisiera evaluarlo más, el siguiente paso barato sería un censo de cobertura
por día (~140 sondas, ~150-300 cr) + decidir si un subconjunto días-con-cobertura es admisible
(preocupación de selección) — decisión que pertenece al prereg del eco con mesa fresca, no a hoy. El
colector propio sigue siendo el juez limpio del 5s; el eco sigue siendo el calendario. ROI de la
diligencia: ~400 cr por saber ANTES de diseñar — el gate mordió exactamente donde debía, tercera vez
que "folleto ≠ certificación" paga.

### REVISIÓN EXTERNA DE ENTORNO (2026-07-06) — la primera auditoría que EJECUTÓ en vez de leer

Un revisor externo clonó/ejecutó la suite y miró el CI (no solo leyó líneas). Cazó exactamente la clase
de fallo invisible a la lectura — los de reproducibilidad y entorno. **Lección al acta sobre la mesa: la
mesa verifica que el código es CORRECTO, no que el proyecto es REPRODUCIBLE — son cosas distintas, y la
mesa (y los 5 agentes frescos de A11) solo hicieron la primera.** Este es el primer mordisco real al
residuo de A11 (un tercero con entorno propio), no otra lectura correlacionada. Seis hallazgos, todos
correctos; arreglos (ninguno toca un veredicto):

1. **[ALTA] `replicate.sh` cantaba "ok" por fe.** Imprimía `replica ok pendientes=$PEND`
   incondicionalmente → el `pendientes=0` citado en este LEDGER era verdad por SUERTE, no por
   verificación — una garantía FALSA sobre el notario, el mismo fallo que la casa condena en los datos.
   **CORREGIDO:** cada rsync se sigue de una 2ª pasada `--checksum`; si falla o quedan pendientes, ALERTA
   y SALE con error; "ok" solo se escribe con pendientes=0 verificado. Probado en vivo (happy path exit 0;
   fallo forzado exit 1 + ERROR logueado, sin crash). Alerta Telegram: replicate corre como `quant` (no
   puede leer el token 600-root) → el **heartbeat (root, cada 10 min) vigila `replica.log` y alerta** del
   delta de ERROR.
2. **[ALTA] Reproducibilidad rota / CI latentemente ROJO.** `requirements.txt` no incluía `pandas` pero 2
   tests de adapters lo importaban en duro → un clon limpio falla al colectar. Además el repo no se empuja
   desde 2026-06-17: **todo el Cap 2 + auditoría nunca pasó por CI**, y el próximo push habría salido rojo.
   **CORREGIDO:** `requirements-test.txt` (-r requirements + pandas + zstandard), CI lo instala, y los 2
   imports pasan a `importorskip` (el core corre solo; los de infra se saltan sin romper). Suite 345 verde.
3. **[MEDIA] Claim inexacto en ESTADO.md** ("Python 3.14, sin pandas" cuando CI usa 3.12 y la venv tiene
   pandas). Primo del error "afirmar de un todo lo cierto de una parte". **CORREGIDO** a la distinción
   core (numpy+pyarrow) vs infra/vendor (+pandas/zstandard), CI 3.12.
4. **[elevado a ALTA por contexto] El colector no tenía tests — y ahora es RUTA CRÍTICA** (el eco necesita
   su 2º símbolo no-token a 50 ms). Auditando para escribir tests se respondió por fin la pregunta abierta
   de la mesa ("¿el watchdog puede matar con el buffer sin flushear?"): **SÍ podía** — `flush()` hacía
   `sys.exit(3)` ANTES de escribir el buffer → pérdida silenciosa al llegar el disco al 85 %. **CORREGIDO:**
   escribir el buffer PRIMERO, watchdog después (a 85 % quedan ~28 GB, sobra). + 4 tests (zstd concatenado
   decodable, flush por umbral, y el bug: watchdog sale código 3 PERO el buffer se escribe). Colector
   redesplegado, `ingest.service` intocado.
5. **[bonus, hallado hoy] Test flaky bajo carga.** `test_fallo_de_escritura_no_pierde_filas` pasaba en
   aislado y caía en el suite completo (sleep fijo 0,3 s vencido por la carga). **CORREGIDO** a poll
   determinista (misma aserción). Suite 2×345 estable.
6. **[MEDIA, ya conocido] Rutas de clave hardcodeadas** (`confirm_runner.py:25` etc.) = el M4 de A11;
   cae con la rotación de keys pendiente (en `PREREG_ECO_LIT_INSUMOS.md`).

Lo que el revisor hizo MEJOR que ningún hallazgo: llegó por su cuenta a que el riesgo real es n=1 LIT
token-del-venue con el 5s pendiente y sin auditor humano — la debilidad que el expediente ya declara. Que
un extraño con entorno propio la repita sin ayuda = la carta de ataque funcionando con su primer lector
real. Ningún arreglo toca el veredicto; todos tocan si un extraño puede confiar en lo que ve — la fase en
la que el laboratorio entra ahora.

**Cierre adicional post-push (2026-07-06):** `dface77` subido a GitHub y CI remoto **verde** en CPython
3.12.13 / Ubuntu 24.04 (`345 passed in 38.75s`, run `28789409400`). Para cerrar la pega de reproducibilidad
de segundo orden, se añade `requirements-lock.txt` con las versiones EXACTAS instaladas por ese run y CI pasa
a instalar con `pip install -r requirements-test.txt -c requirements-lock.txt`. No congela la venv local; congela el entorno que el auditor remoto ya ejecutó.

### 2026-09-06 · decisión de Manuel: acceso histórico LIT para I5

Manuel declara «He decidido que voy a pagar para los datos de lit»: decisión de contratar un mes
de 0xArchive Build (tarifa pública comprobada hoy: 49 USD/mes), sin constancia aún de activación.
D1 sigue aprobado como diagnóstico retrospectivo, no como rehabilitación del hallazgo. Secuencia,
límites y presupuesto todavía no medido en `DECISION_MESA_2026-09-06_ACCESO_LIT_I5.md`.
Ninguna nueva sonda, compra por Codex ni rederivación ejecutada en esta anotación.

Observación de captura, sin corrección ni despliegue: el poller L3 comprime síncronamente con
`zstd -19 -T1` al rotar (`infra/l3_poller/l3_poller.py:114–133`) y pausa sus nuevas consultas
mientras tanto. El archivo XPT leído mostró un borde inicial de 59,330317607 s sin snapshot
seleccionado; no se ha medido la duración de esa compresión ni se generaliza a cada hora.
La comprobación XPT permanece terminada con INDETERMINADO_MASA; no se amplía automáticamente.

### 2026-09-06 · Build abre marzo; censo I5 preparado y Laboratorio fuera de OneDrive

Superada la activación pendiente: Manuel/Code confirman Build en otra cuenta. Codex observa
límite 80.000.000 en usage y una única página L3 de LIT del 06-03 válida, HTTP 200, una fila:
**INDICIO**. Saldo −1 frente a cabecera 10; no se concilian por conjetura. Una invocación previa
solo consultó usage y paró por exigir nombre de plan; defecto de supuesto de Codex corregido
antes de pedir datos. Cuatro llamadas autenticadas en total, una de mercado; ningún crudo
guardado. Detalle y hashes: `RESULTADO_MESA_2026-09-06_I5_BUILD.md`.

Mesa aprueba censo de las 149 celdas gastadas (79 LIT/70 DOGE), checkpoint y tick separados,
y preparación de custodia completa sin recorte por coste; ocho días de reproducción fijados
antes del censo. I5 sigue siendo diagnóstico retrospectivo de LIT. Instrumento y orden de
auditoría/ejecución de Code en `PARA_CODE_2026-09-06_I5_CENSO.md`; no se ha ejecutado el censo.
Key loader parametrizado con default Free intacto, clave Build vigente fuera del repo; ningún
secreto ni huella de clave en recibos. Focales finales: acceso 8/8, censo 10/10; sin suite larga.

Leído el relevo completo de la mudanza: nueva raíz `<USER_HOME>/Desktop/Laboratorio`;
hashes de los dos recibos de etapa 0 y contrato público comprobados allí. Las salidas nuevas
se escriben fuera de OneDrive. No se repitió el diagnóstico de memoria, no se parcheó prevuelo
ni se tocó la captura. STOP, freezes y pins intactos. Sin commit, push ni CI.

### 2026-09-06 · auditoría del censo recibida; P1 operativo aplicado

Code auditó las ocho piezas, plan y 18 focales sin defectos de corrección; señaló el riesgo
de consultar primero cobertura genérica con timeout de 60 s frente a 30–60 s publicados.
Codex contrastó y aplicó: checkpoint → tick → cobertura; 120 s solo para cobertura, cuyo
fallo se registra como indeterminado y no invalida las presencias ni detiene las siguientes.
Fallos de presencias y contabilidad final siguen siendo fatales. Recibo v2 con contador
separado y estado explícito de presencias completas/cobertura indeterminada, sin verde de
cobertura inferido del rc. 17 focales del censo pasan (3,64 s); sin suites ni red autenticada.

Orden y hashes: `PARA_CODE_2026-09-06_I5_CENSO_P1.md`. Code revisa únicamente este cambio y
ejecuta el comando ya autorizado, sin otra consulta de permiso a Manuel. El censo aún no ha
corrido. Manuel reafirma adquirir y medir todo el ámbito acordado sin recorte por coste;
descarga completa de las 149 celdas tras el censo, antes de las rederivaciones escalonadas.

### 2026-09-06 · censo parcial recibido y continuación acotada preparada

Code ejecutó una vez: 115 celdas (DOGE 70, LIT 45), checkpoint 115 INDICIO, tick 114 INDICIO
y un TIMEOUT en LIT 01-05. 114 coberturas válidas; saldo −229; ninguna ausencia válida.
Codex contrastó resumen y celdas locales: faltan 69 presencias y 35 coberturas. Se aprueba
continuar desde índice 114 conservando el checkpoint de ese día, máximo 106 llamadas con
usage y timeout configurado 120 s. Sin repetir DOGE ni presencias válidas. El padre queda
fijado por hashes; los conteos nuevos y combinados se distinguen. 22 focales verdes, 4,29 s.
No se ha ejecutado la continuación. Code audita el cambio y la ejecuta con el permiso vigente.

Detalles y comando: `PARA_CODE_2026-09-06_I5_CENSO_CONTINUACION.md`. Correcciones documentales:
44 coberturas LIT, seis fechas de hueco compartidas y cuatro fechas de reproducción todavía
pendientes (incluye 29-06). TIMEOUT con parámetro 60 no es duración medida 60: los relojes
del recibo dejan 21,527209 s entre último checkpoint y final; no se infiere causa. El nuevo
recibo mide duración monotónica por petición.

Inventario parcial de huecos para verificar contra la descarga, fuera de OneDrive:
`Desktop/Laboratorio/HUECOS_L3_PARA_DESCARGA_20260906_01.json`, hash y contrato en el relevo.
22 intervalos declarados en 19 celdas; 35 celdas sin metadatos quedan desconocidas. Las métricas
globales del símbolo no son cobertura diaria, ni los gaps sin resolución acreditan por sí solos
ausencias en tick/checkpoint o su causa. Custodia completa sigue aprobada sin recorte por coste;
la receta de reproducción no se altera silenciosamente por los huecos. STOP y freezes intactos.

### 2026-09-06 · censo cerrado; inventario completo y descargador L3 entregado a auditoría

Code terminó la continuación: 35 celdas nuevas, 106 llamadas, 69 créditos; combinado único
de 149 celdas (LIT 79/DOGE 70), ambas presencias y metadatos válidos. Censo total 298 créditos;
último saldo observado 79.999.701. Codex verificó recibos y checkpoint heredado sin repetir
consultas. Censo y etapa 0 cerrados. El éxito posterior de tick 01-05 no acredita la causa
del timeout previo. Informe original de Code y ambos tramos se conservan intactos.

Inventario nuevo `Desktop/Laboratorio/HUECOS_L3_PARA_DESCARGA_20260906_02.json`, SHA-256
`625928f0386380af73c4f9a95b7de277c917c54c43fa472a7fc56b8f81d348c3`: 25 intervalos en
22 celdas; LIT 14 días/17 intervalos/257 minutos reportados, DOGE 8/8/134. Corrige al informe
combinado: solo dos de las siete fechas compartidas están cerca de las 13 UTC, no cinco.
Las coincidencias no prueban mantenimiento ni ausencia de mercado o huecos idénticos en las
dos resoluciones. El inventario parcial anterior queda conservado.

Entregado `tools/i5_descarga_l3.py`: las 149 celdas, checkpoint y tick separados, 298
recorridos hasta agotar el cursor del proveedor, sin techo financiero ni de páginas. Custodia
de bytes originales gzip, hashes del cuerpo/comprimido y cadena de recibos; ámbito y
cronología comprobados antes de guardar. QA de intervalos declarados y separaciones >600 s
por resolución, descriptiva y sin modificar admisión. Continuación explícita verifica páginas
locales sin volver a pedirlas; escrituras incompletas paran para inspección, no se borran.
Cuenta Build por usage, reserva de disco 5 GiB, un escritor, transporte 120 s y sin retry
automático. Agotar paginación no certifica archivo íntegro. Cambio compartido de IO conserva
la interfaz previa y añade acceso al cuerpo original; default Free del eco sin cambios.

31 focales sintéticos pasan en 1,53 s (23 descargador + 8 acceso), rc 0; plan sin red verifica
149/298 y el inventario completo. **No se ha ejecutado la descarga ni calculado I5.**
Orden, contrato, comandos, límites y hashes: `PARA_CODE_2026-09-06_I5_DESCARGA_L3.md`.
Code audita el incremento y ejecuta la descarga larga con el permiso ya vigente; no falta
otra autorización de Manuel. Tras ello queda el productor y reproducción de ocho días,
insumos CHD/Binance y recetas diferenciadas antes de otros 71 días e I5. STOP/freezes/pins
intactos; sin suite larga, red autenticada, VPS, commit, push o CI en este incremento.

### 2026-09-06 · auditoría de custodia recibida; ejecución dividida en A/B

Code auditó la entrega anterior sin defectos de corrección (31 focales), pero no ejecutó la
pasada única por volumen no dimensionado. Mesa acepta separar etapas y elevar la reserva
de disco. Corrige la justificación numérica: los créditos de julio citados en LEDGER 1799–1810
eran de tick-L2 con deltas; no acreditan millones de snapshots tick-L3. No se ratifican
8–9 TB, días de transferencia o ratios de compresión sin medir. Los bytes de las primeras
páginas sí se comprobaron por recibos: medianas HTTP LIT 68.816 B/DOGE 21.139,5 B, incluyendo
envoltorio. A son 149 recorridos checkpoint, no 298; páginas y coste se observarán.

**Mesa ordena A: checkpoint de las 149 celdas, LIT primero; B: tick LIT 06-03, índice 70,
después de leer el resultado satisfactorio de A.** Code audita el cambio y ejecuta A/B con
el permiso vigente, sin otra autorización de Manuel. C queda pendiente de la medida B y
capacidad de almacenamiento. Máxima resolución sigue como objetivo; no se sustituye por
una granularidad intermedia ni se dimensiona DOGE con un día LIT por inferencia.

Codex implementa selectores obligatorios de celdas/resolución fijados en plan v2, orden por
resolución y LIT/DOGE cronológico conservando índices originales, limit 1.000 y reserva
50 GiB. Recibos v2 de página/recorrido miden bytes originales/gzip y tiempos monotónicos;
el intento distingue métricas nuevas/heredadas al reanudar. Mismo manifiesto e inventario,
IO intacto; solo descargador y sus pruebas cambian. No hay tope financiero o de páginas.

37 focales pasan en 1,38 s, rc 0; no se repiten ocho focales IO, censo ni suites largas.
Planes sin red A=149/149, B=1/1, ambos con los parámetros anteriores, guardados fuera de
OneDrive en `I5_DESCARGA_PLANES_20260906_02`. Relevo vigente con comandos, hashes y límites:
`PARA_CODE_2026-09-06_I5_DESCARGA_ETAPAS.md`. Pasada única retirada; auditoría original y
recibos preservados. **Sin descarga real ni gasto en este incremento.** Productor de ocho
días y diagnóstico I5 pendientes. STOP/freezes/pins/conjunto protegido intactos.

### 2026-09-07 · A/B ejecutadas y contrastadas; entrada L3 de ocho días preparada

Leídos los informes de Code, coincidentes por hash con los adjuntos de Manuel. A: 149
recorridos checkpoint agotados, 151 llamadas, 149 créditos. B: tick LIT 06-03, un recorrido,
tres llamadas, un crédito. Mesa verificó cadenas de recibos y hashes de los 150 gzip; solo
descomprimió los dos cuerpos del par LIT 06-03, no volvió a procesar todo A. Recibo local
`Desktop/Laboratorio/VERIFICACION_MESA_I5_AB_20260907_01.json`, SHA-256
`630a1f25a0f779253930ce83ae1c8b75dde68d92d53ed14a2de6b6852c8c81cc`.

A: 3.353.499.851 B crudos / 414.413.178 B gzip. LIT 37.984 snapshots marcados truncados;
DOGE 33.190, 71 marcados. QA: 17/8 separaciones >600 s, todas con intervalo declarado y
extremos observados. Coherencia para esa serie y ese umbral, no completitud de mercado.
B: 527 snapshots, 36.146.223 B, cuerpos idénticos tras sustituir únicamente request_id;
los cuerpos originales tienen hashes distintos. Acredita igualdad servida en LIT 06-03,
no máxima resolución ya adquirida en 149 días ni inexistencia de otras fuentes más finas.

**Mesa no lanza ahora C ni la batería adicional de sondas.** Prioridad: insumos y productor
de ocho días sobre checkpoint ya custodiado. La máxima resolución del resto sigue pendiente,
no descartada. LIT 01-09 propuesto por Code está protegido; requiere cometido D3 previo,
no hereda permiso de la muestra XPT. No se toca por esta continuación histórica.

Codex añade `tools/i5_insumos_ocho.py` y sus pruebas: plan local de ocho días e índices
70,81,92,103,115,126,137,148, lector de páginas de A con hashes y mapeo del wallet_atlas,
sin reimplementar differ ni descargar. Preserva orden/duplicados temporales y rechaza
órdenes ambiguas. 11 focales pasan (0,23 s). Plan real sin crudos/NPZ abiertos:
`Desktop/Laboratorio/I5_OCHO_INSUMOS_PLAN_20260907_01.json`, SHA-256
`5edb29a83919929ef4f68f6b850c0dd0b43c74079dd8e421b1cb609910f67e12`.

Faltan 16 insumos diarios CHD acreditados (trades LIT/lighter y LITUSDT/binance_futures
para ocho fechas), no una estimación de 16 peticiones. El SDK tiene caché en memoria; no
acredita crudos históricos recuperables. La receta de julio usa trades Binance, no el mid
exigido: reproducción forense con receta histórica separada del actual I2/I7/referencia,
fuera del decisivo. Productor, campos/horizontes extendidos, contraste e I5 siguen pendientes.
Relevo vigente `PARA_CODE_2026-09-07_I5_PRODUCTOR_INSUMOS.md`. No repetir censo/A/B/suites.
Sin nuevas consultas, claves abiertas, NPZ leídos, VPS o cambio del STOP/freezes/pins.

### 2026-09-07 · lector L3 auditado; readquisición horaria CHD instrumentada

Code entregó `AUDITORIA_CODE_2026-09-07_I5_LECTOR_E_INSUMOS.md`: lector sin defectos,
once focales y ejercicio sobre los ocho libros reales. Se acepta esa validación; no se
repite. Su inventario por nombres no encuentra trades LIT/lighter o LITUSDT/binance_futures
custodiados. Los dieciséis insumos diarios de julio deben readquirirse, sin confundirlos
con los bytes originales que el SDK no persistió.

Codex añade `tools/i5_chd_custodia.py`: alcance fijo 384 claves horarias de las mismas ocho
fechas; etapa acceso = JWT y dos ficheros 06-03 hora 00, después 382 horas restantes con
reutilización de los dos crudos. Mesa ordena a Code auditar y ejecutar ambos tramos si el
acceso queda confirmado, dentro de la autorización histórica vigente, sin otra consulta
a Manuel. 404 es indeterminado para la clave exacta, nunca ausencia de operaciones;
errores de transporte/auth paran, sin reintentos o fallback anónimo. Custodia por hashes,
reserva 50 GiB, reanudación explícita y QA de identidad/relojes sin filtrar filas o leer
valores económicos. Se distinguen bytes custodiados de completitud del mercado.

Contrato público y SDK 0.4.0 contrastados: la solicitud conserva las rutas/claves del SDK;
su acceso actual no se da por vigente. `event_time` tiene escala dependiente del exchange
según el contrato, por lo que se observa por rango y se marca si difiere de los ms de julio.
El reloj que particiona cada hora no está acreditado; los cruces de día requieren revisión.
No se pide LIT desde 30-06 ni se cambia fuente o ventana automáticamente.

40 focales sintéticos pasan (6,73 s); CLI/plan sin red verificados. Plan vigente
`Desktop/Laboratorio/I5_CHD_OCHO_PLAN_20260907_02.json`, SHA-256
`38dffcc2d505bb09d0b9ebb2664a718f0977ce28f781c01339680c56bb9d247a`.
Relevo con comandos/huellas: `PARA_CODE_2026-09-07_I5_CHD_CUSTODIA.md`. Auditoría independiente
y ejecución CHD pendientes. Se leyeron fuentes públicas, no la clave CHD: cero peticiones
autenticadas/de mercado, ningún cuerpo NPZ o nueva lectura L3. Productor, reproducción e
I5 siguen pendientes. C/sondas siguen aplazadas; STOP/freezes/pins intactos; sin commit.

### 2026-09-07 · auditoría CHD recibida; P1 de ventana zstd corregido

Code auditó la base (40 focales y plan `_02` conformes), sin ejecutar acceso. Detectó
que el valor explícito `max_window_size=128 * 1024` rechaza frames de varios MiB. Codex
reprodujo el fallo con un Parquet válido de ventana 8 MiB y retiró ese argumento en una
línea. Se usa el límite predeterminado de zstd; reserva de disco 50 GiB y lectura por
bloques intactas. No se confunde esa reserva con un límite de memoria del decodificador.

Regresión falla antes (1,20 s) y pasa tras el cambio; 10 focales pertinentes pasan en
1,07 s, 31 deseleccionados. No se repite la suite original de 40 ni pruebas del proyecto.
Consta distribución CHD 0.4.0 con atributo `__version__` 0.3.0 obsoleto; SDK sin cambios.
Plan vigente `Desktop/Laboratorio/I5_CHD_OCHO_PLAN_20260907_03.json`, SHA-256
`4a78948a4cd70ff2ad10870ba2bb133f4b8288839317f8e0ecf8389da6b38ec2`: solo cambia la huella
del instrumento respecto de `_02`; las 384 claves y la secuencia son idénticas.

Relevo puntual `PARA_CODE_2026-09-07_I5_CHD_P1.md`, con diff, huellas, evidencia y comandos.
Code revisa el cambio y ejecuta acceso una vez; solo si acredita los dos ficheros, continúa
con los 382 restantes bajo la autorización vigente. No falta otra decisión de Manuel.
Clave real sin abrir y cero peticiones autenticadas/de mercado en este incremento.
Reproducción e I5 pendientes. STOP/freezes/pins y auditoría de Code intactos; sin commit.

### 2026-09-07 · acceso CHD devuelve 302; transporte con un salto preparado

Code auditó P1 y ejecutó acceso una vez: JWT 200 con duración 14.400 s y GET inicial 302;
dos llamadas API, cero horas, carpeta `I5_CHD_OCHO_20260907_01` sin parciales. Codex leyó
el informe y los cuatro JSON, verificando sus hashes antes/después sin modificarlos.
SHA-256 del intento `11bbd643dad749ec751f3d2cd5edd8c5e9592ea9ed45d247c93abf70979e22c9`.
El JWT fue emitido; la descarga sigue sin confirmar y el destino del salto sigue desconocido.

Mesa concreta un salto manual HTTPS solo para download, sin redirects automáticos/JWT.
Bearer solo al mismo origen, incluido puerto efectivo; a otro host o puerto va un Request
nuevo sin autenticación. URL de destino solo en memoria, recibo con esquema/host/puerto;
segundo 3xx para. 404 final sigue indeterminado para la clave original. Se mantiene pacing,
timeout y ausencia de reintentos. La reserva de disco y límite predeterminado zstd son
controles distintos y permanecen vigentes.

Contabilidad decidida: iniciales API 3/383, saltos máximos 2/382 y total HTTP 5/765 para
acceso/continuación. 765, no 766: el JWT no sigue salto. No se equiparan llamadas y créditos.
Se cuenta un salto al mismo host como salto adicional, sin doble contabilizarlo como inicial.

Codex implementa transporte, contadores y plan v2; 22 casos nuevos pasan (1,75 s), más
14 focales pertinentes (6,58 s; 27 deseleccionados), sin repetir la suite de 41 completa.
Plan vigente `Desktop/Laboratorio/I5_CHD_OCHO_PLAN_20260907_04.json`, SHA-256
`85ad3b7176f7ab8985d3b9c69f59c051340e5a69fec6b1e351c4dbe442d1cbf8`: mismas 384 claves.
Relevo `PARA_CODE_2026-09-07_I5_CHD_REDIRECT.md` con diff y huellas. Code revisa y ejecuta
acceso una vez en `_02`; solo si confirma, continúa con 382. La `_01` no se migra ni reanuda.
La autorización histórica ya cubre esta secuencia; no falta otra decisión del propietario.
Codex no usa clave real ni hace peticiones autenticadas/de mercado en este incremento.
Trades custodiados, productor, reproducción e I5 pendientes. STOP/freezes/pins intactos.

### 2026-09-07 · custodia CHD aceptada; productor forense de ocho días entregado

Code cerró acceso y continuación en `I5_CHD_OCHO_20260907_02`: 384 recibos encadenados,
381 ficheros, 767 HTTP totales, tres 404 de LIT/lighter 29-06 horas 04,05,06. Aceptada
su verificación de hashes de crudos; no repetida por Codex. El plan local contrasta
anclas/cadena/metadatos y confirma 289.723 filas Lighter y 2.497.906 Binance.

Mesa dispone reproducir 29-06 con cobertura 21/24, sin volver a consultar ni rellenar
los tres faltantes. Se conservan todos los registros de las mismas 24 claves horarias,
incluidas las ocho filas Binance del 07-04 en la hora 00 del 08-04. Mismo borde lógico
no prueba mismos bytes que julio. El guardado histórico contiene ocho arrays y ningún
conteo de trades: se corrige la inferencia de §5.2 del informe de Code sobre poder
decidir 21/24 horas por ese conteo, o atribuir automáticamente los 404 a pérdida posterior.
Cero inversiones por fichero no acredita cero entre horas; el productor lo registra.

Codex añade `tools/i5_productor_forense.py` y sus pruebas. Extrae funciones históricas
del commit `74f0d6069efdc7be73693dd18ca39e9167892202`, con entradas locales y observadores
pasivos de eventos/contadores. Conserva las reglas anteriores a I2/I7/validación de
referencia y compara ocho arrays contra originales custodiados al comenzar la ejecución.
Salida separada con `AR.publicar`, carril trade Binance no conforme y procedencia por
hash; no se modifica el differ, la acreditación existente ni ningún productor oficial.

Extensión fijada por la mesa antes de abrir resultados reales: oid, px, cantidad visible
imputada, límites y posición de snapshot, primera aparición, tiempos at/through,
thr_con_at y amb. `ref_t`/`ref_t_ms`: último trade Binance estrictamente anterior al fill,
dentro de 500 ms, NaN/-1 si no existe; no mid. Familia diagnóstica post hoc fija
{1,5,10,25,60} segundos con la fórmula histórica desde px y su tolerancia. Los ocho
campos originales no cambian; el through conserva su instante through aun con at previo.

32 focales nuevos pasan (3,22 s), incluyendo oráculo histórico sin instrumentar, insumos
corruptos, frames sin tamaño, cobertura/bordes, comparador estricto, no conformidad y
preservación del primer recibo tras una parada posterior. No se repiten suites cerradas.
Plan real con guardas contra cuerpos NPZ/mercado y conexiones, cero lecturas económicas:
`Desktop/Laboratorio/I5_REPRODUCCION_OCHO_PLAN_20260907_01.json`, SHA-256
`dae62c8bd425d174748c762293d1af33b31016bc2388f0a48f0c02064ee57e1f`.

Relevo vigente `PARA_CODE_2026-09-07_I5_REPRODUCCION_OCHO.md`: Code audita este incremento
y, si no hay defectos, ejecuta una vez el contraste local de ocho días; el comando exige
el hash del plan auditado. Autorización D1 vigente, no falta otra decisión de Manuel.
No reintentos automáticos; parada conserva originales y recibos diarios para revisión.
Implementación lista; auditoría independiente, reproducción real, resto de 71 días e I5
pendientes. Sin red, claves, NPZ originales abiertos, cambios de STOP/freezes/pins, VPS,
CI/push o commit en este incremento. C y nuevas sondas siguen aplazadas.

### 2026-09-07 · ocho días reproducidos; D1 especificado y custodia de 71 preparada

Code auditó y ejecutó el productor una vez, 36 s, sin red: ocho fechas y ocho campos
históricos por fecha con dtype/shape/máscaras/valores numéricamente iguales. Recibo final
`I5_REPRODUCCION_OCHO_20260907_01/result.json`, SHA-256
`3d7302b05d3a42e910b982b05fd40553346518df661c773b9ed1421be8790172`.
Mesa verificó anclas/recibos/manifiestos y aceptó cerrar esa etapa. Originales preservados
según la verificación antes/después de Code; no se repite su reproducción o sus suites.

Code concedió cinco correcciones en §6 de su informe: igualdad numérica, no bit a bit;
salidas iguales no prueban entradas idénticas; through 88,31–96,99 % con denominador
de todos los eventos, fills imputados; max_gap_ms es umbral de exclusión; D1 post hoc.
Sin inspección manual de NPZ no significa que el instrumento no los abriera. Ninguno
de estos cierres valida el +18,24 ni el carril de trade Binance frente al mid exigido.

Tras avisar a Manuel del paso a implementación, Codex fija
`ESPEC_MESA_2026-09-07_D1_79_DIAS.md`. La última adenda de Code volvía a identificar
admisión con fechar al primer at: se separan expresamente. Principal A−H añade
through-con-at conservando reloj/vol/cortes/referencia histórica; ramas distintas para
reloj, ventana de vol, recalcular cuantiles y R1–R3. Soportes diarios pareados, masa,
5/25 y horizontes secundarios fijos, lado-neutral y descomposición orden–trade/movimiento.
No se presenta como preregistro ni se afirma que el analizador esté ya implementado.

Nuevo `tools/i5_resto_chd.py`: diferencia exacta de manifiesto, 71 fechas y 3.408 claves
nuevas CHD, sin intersección con las 384 previas. Enlaza ocho NPZ ya reproducidos y los
79 L3 de A (37.984 snapshots), solo por metadatos en el plan. Transporte auditado
`i5_chd_custodia.py` intacto, cargado en ámbito privado con únicamente jobs/path_for
del nuevo alcance. Cadena/QA/redirect/secretos conservados; nuevo ejecutor por tramos.
JWT por intento, sin refresh o reintento automáticos; continuación exige hash del último
STOPPED y custodia íntegra. 404 comprometidos no se vuelven a pedir. `combined_79`
mantiene visibles los tres faltantes anteriores aunque cierre el tramo nuevo.

23 focales nuevos pasan (1,89 s). Plan real generado con guardas contra cuerpos/clave/
lectores económicos/sockets, 844.879 bytes, cero red o NPZ reales leídos:
`Desktop/Laboratorio/I5_CHD_RESTO_71_PLAN_20260907_01.json`, SHA-256
`d1f38459859763d362fc54f88ffe8078a4b88a3eb71ef9d6f0858b1fcc0c51de`.
Máximos iniciales: 3.409 API, 3.408 saltos, 6.817 HTTP; sin inferir créditos CHD de Build.
2 h 20 min es extrapolación de 2,47 s por clave, no duración garantizada.

Relevo vigente `PARA_CODE_2026-09-07_I5_CHD_RESTO_71.md`. Mesa ordena a Code auditar este
incremento y ejecutar una vez el comando con el plan fijado, dentro de D1 ya autorizado.
No falta otra autorización metodológica de Manuel. Recibo/inventario nuevo antes del
productor restante y analizador D1; ambos aún pendientes. Codex no ha usado claves reales,
descargado ni ejecutado D1 en este incremento. C/protegido/STOP/freezes/pins, VPS, SO y
productores anteriores intactos; sin CI/push/commit.

### 2026-09-07 · custodia completa revisada; productor restante listo para Code

Code cerró la continuación CHD con 3.408 claves recorridas: 3.357 ficheros y 51
respuestas 404 sin resolver. Recibo final 0001.json SHA-256
9784180d27d1942d32e9c700d4ade0d459ab39deb8de3f2052119b6c4747762d,
ligado al intento STOPPED 6aef7ca1ab7443b0824e408c7de482ee56355440244e503bfa3b56b4651d0a65.
Combinado con los ocho: 3.738/3.792 ficheros/claves, 54 faltantes, cinco ficheros
de borde, 402.232.869 bytes. No reintentar 404 ni repetir QA/descargas cerradas.
Mesa verificó metadatos, anclas, cadena y tamaños sin repetir los hashes de cuerpos
comprobados por Code. Los 404 siguen siendo claves sin resolver, sin causa acreditada.

Siete fechas incompletas entre los 71 nuevos; la octava es 29-06 y se reutiliza.
Corrección contable de §3/§3.2 del informe de Code: 79+977=1.056 filas nuevas fuera de
hora, incluidas 1+11=12 fuera de día. Dentro del día: 1.044. Las cifras 80/988 sumaban
los bordes dos veces. No cambia ninguna fila o admisión; informe de Code intacto.

Tras avisar a Manuel, Codex implementó tools/i5_productor_resto.py. Reutiliza receta,
traza y comparador auditados sin alterar sus bytes; lectores literales con ámbito
privado de 71 días. Conserva faltantes, bordes, orden de horas y exclusiones de julio.
Congela los 71 originales antes de derivar; recorre todas las fechas ante diferencias
numéricas, para ante fallos de integridad/IO. No publica sobre canónicos. Panel de
79 con ocho salidas reutilizadas; solo queda listo para auditar D1 si las 71 nuevas
comparaciones son iguales. No mide aún I5 ni valida el carril trade frente a mid.

28 focales sintéticos nuevos pasan en 35,80 s; suites anteriores sin repetir. Plan
real de 751.869 bytes emitido con guardas contra cuerpos, claves, NPZ y conexiones,
cero intentos bloqueados: I5_REPRODUCCION_RESTO_71_PLAN_20260907_01.json, SHA-256
ad7b6d589059b49278b1675395435c224729c34b428544377b48a338348106ee.
Verificación I5_REPRODUCCION_RESTO_71_VERIFICACION_20260907_01.json, SHA-256
e60473b21ff883792fc7c85253e8b3d69e44029f462b4b46073edaf93a9049f7.
Ambos en Desktop/Laboratorio. Especificación D1 intacta, ligada por hash.

Relevo vigente PARA_CODE_2026-09-07_I5_REPRODUCCION_RESTO_71.md: mesa ordena a Code
auditar este incremento y ejecutar una vez el comando local con el plan fijado si
no hay defectos. Reproducción real de 71 y analizador D1 pendientes; no falta otra
autorización de Manuel. No se abrieron NPZ/mercado reales ni claves en este incremento.
STOP/freezes/pins, conjuntos protegidos, VPS/SO y productores anteriores intactos.

### 2026-09-07 · 79 días reproducidos; analizador D1 entregado a Code

Code auditó y ejecutó el productor restante en 5 min 56 s, sin red. 71 de 71 días
iguales en ocho campos, sin exclusiones. Mesa contrastó anclas/recibos/manifiestos
sin repetir la reproducción: 79 fechas, 632 comparaciones numéricas iguales,
1.165.520 eventos según recibos. Se conservan los 54 faltantes y los cinco bordes.
No se acredita identidad de insumos de julio ni validez del +18,24.

Cierre nuevo: result.json a665e3de4a7ef83978ce10839c95c328d2ab7d9d67f36915fea705feb6018942;
panel_79.json 59611007166197f03d08aebbd3e5f63ae82deab9c871d786c840f4ae089ded53,
en I5_REPRODUCCION_RESTO_71_20260907_01. El rehash de los 71 canónicos lo hace el
instrumento; el de los 79 antes/después es la verificación independiente de Code.

Tras avisar a Manuel, Codex implementó tools/i5_d1.py y tools/i5_d1_math.py. Siete
ramas y siete contrastes fijados por ESPEC_MESA_2026-09-07_D1_79_DIAS.md, sin modificar
la especificación. H/A/Q conservan markouts archivados; T cambia solo reloj de
through-con-at; TV añade vol histórica en ese reloj; Q cambia cortes; VH/VA validan
el candidato seleccionado mediante RV. Todos los soportes, masas y causas visibles.
Media diaria >=3, media equiponderada de días, t descriptivo de la casa; contrastes
pareados, lado-neutral, lenta−rápida y descomposición en soporte común de cinco horizontes.
No se incorpora I2, I7, mid, BHY o un umbral de éxito. T sigue siendo puente analítico.

46 focales sintéticos nuevos pasan en 3,62 s, incluidos oráculos literal de julio y
R1–R3; no se repiten suites cerradas. Plan de 811.164 bytes emitido con guardas contra
cuerpos/NPZ/claves/decodificadores/conexiones, sin intentos bloqueados ni datos reales:
I5_D1_79_PLAN_20260907_01.json, SHA-256
185dd59c5b45fb97787261887a889edf75e1a4711eec3f484368a695d917d378.
Recibo I5_D1_79_VERIFICACION_20260907_01.json, SHA-256
4205c1d26240ee11b09468ea76e607667c3ea8e3e5eaec114b112a0692b4739e.
Ambos en Desktop/Laboratorio; plan ligado al panel, cada NPZ/manifiesto, custodia,
receta, especificación, funciones compartidas y entorno.

Relevo vigente PARA_CODE_2026-09-07_I5_D1_79.md. Mesa ordena auditoría independiente
y una ejecución local por Code con el plan fijado si no hay defectos; no falta otra
autorización de Manuel. D1 real todavía pendiente. Codex no abrió NPZ/mercado reales,
canónicos ni claves. STOP/freezes/pins, protegido, VPS/SO y productores auditados
intactos; sin CI/push/commit.

### 2026-09-07 · I5/D1 ejecutada y dictaminada: cierre histórico, no ratificación

Code auditó fórmula por fórmula y ejecutó una vez D1 con el plan 185dd59c…:
D1_79_COMPLETE_POST_HOC, 79 fechas, 1.165.520 eventos. Mesa verificó anclas y los
79 recibos diarios y leyó las tablas publicadas; no volvió a ejecutar el analizador, suites,
reproducciones o descargas ni abrió cuerpos económicos para otra lectura.
result.json SHA-256 b49a0572b6e6acf430cb78eb28adc2615e5f8175a079022c7ac7f947d9515237;
results.json 1d19677326e1d2a8fa6137449d3543961d2d67fe638572846aeef61f3c54d8c6.

Dictamen vigente DICTAMEN_MESA_2026-09-07_I5_D1_79.md. I5 cumplida como diagnóstico
retrospectivo post hoc; la magnitud del +18,24 es sensible a la admisión. A 25 s,
lento-agitado, H 18,2368 → A 2,5750; delta pareado −15,6618 bps en 79 días,
negativo en 73. Caída del 85,8803 %. Validando referencia: VH 15,6036 → VA 1,4988,
delta −14,1048. A 5 s: H 2,6101 → A −1,0843, delta −3,6944, t descriptivo −0,5505;
VH 10,3795 → VA −0,0976. No se convierte ningún t en inferencia confirmatoria.

Errata propia de la mesa: el titular estaba en 25 s, ya registrado en julio.
La especificación lo atribuía erróneamente a 5 s. Se retira esa justificación,
pero 5 s conserva su prioridad fijada y 25 s la condición de compañero. No se toca
el hash de la especificación, plan o analizador después de conocer resultados.

El dictamen precisa la interpretación de Code: H incluye parciales además de
desapariciones; A añade through-con-at, no todos los through ni fills acreditados.
No se demuestra una exclusión causal de todo fill adverso. Reloj/vol/cortes no son
irrelevantes en todas las celdas; T cambia el signo residual a 5 s. La descomposición
compara conjuntos/soportes distintos y A no es la cohorte aislada de incorporados.
Se distinguen eventos supervivientes de los que entran en medias tras el suelo diario.
Tres celdas no positivas no equivalen por conteo a tres trades distintos con precio cero.

Decisión: cerrar I5 histórica; retirar el +18,24 como fundamento de ventaja operable,
conservar todos los resultados, residuos y limitaciones. No ratificación y STOP
siguen vigentes. No encargar otra corrida, ajuste posterior o rescate del residuo.
Próximo objeto científico requiere decisión propia; no se abre un frente nuevo.
Solo dictamen y estado documental actualizados; informe de Code, fuentes, resultados,
especificación, freezes/pins y código intactos. Sin CI/push/commit.
