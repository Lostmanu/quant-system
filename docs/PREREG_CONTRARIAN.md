# PRE-REGISTRO — Reversión de OFI extremo (contrarian timing)  ·  CONGELADO PRE-TEST

*El hash de git de este commit = autoridad de fecha. Escrito ANTES de tocar ningún dato de test. Toda
desviación posterior se documenta como enmienda fechada, nunca silenciosa. SCREEN, jamás veredicto.*

---

## 0. Génesis y disclosure de contaminación (honestidad primero)

Esta hipótesis **NACIÓ de la sonda propia** (Binance, 12–25 jun 2026): correr la prima #3 (ejecución
OFI-aware) sobre esos 14 días dio un tstat de **−8 a −28** — el horario momentum-OFI empeoraba con fuerza,
implicando que el OFI **revierte** a corto horizonte. La generación de una hipótesis puede venir de
cualquier sitio (incluida la sonda); lo que debe ser limpio es el **TEST**. Por tanto:

> **La sonda 12–25 jun 2026 queda EXCLUIDA de toda selección de parámetros y de todo test.** Es el set
> que generó la hipótesis, no su prueba. No se la vuelve a mirar para esto.

## 1. Hipótesis (mecanismo + racional económico)

**H_contra:** en perps finos, un OFI causal **extremo** (presión de flujo en su cola) va seguido de un
**retorno del mid de signo OPUESTO** a horizonte corto h (reversión del impacto transitorio). Racional:
la literatura de impacto (Cont–Kukanov–Stoikov; impacto transitorio de Bouchaud et al.) dice que una
fracción grande del impacto del order-flow es **transitoria** y revierte en segundos; en libros finos el
salto es mayor y la reversión más medible. La predicción direccional es **fade** del extremo.

**Estadístico primario:** `r_contra = −sign(OFI_extremo) · (mid_{t+h} − mid_t)/mid_t`, NETO de costes,
promediado sobre eventos extremos. >0 ⇒ reversión explotable.

## 2. Arquitectura de datos (la clave de la credibilidad)

| Rol | Dataset | Uso | Sagrado? |
|---|---|---|---|
| **Generador** | Sonda Binance 12–25 jun 2026 | originó la idea | EXCLUIDO de test |
| **Exploración** | CryptoHFTData **jul–dic 2025** | fijar (W,k,h,τ) + modelo de costes | quemado (nunca test) |
| **Probe 1 (test)** | CryptoHFTData **ene–may 2026** | test OOS, mismo venue, otro periodo | held-out |
| **Probe 2 (test)** | Captura **forward** (≥27-jun 2026, ~3–4 sem) | test, régimen genuinamente futuro | held-out |
| **Robustez cross-venue** | **Bybit** L2 200 niveles (gratis, mismos 8 símbolos) | "¿se comporta sensato en otro matching engine?" | NO graduación |

Probe 1 y Probe 2 son **no solapados** (periodos y, P2, venue-instante distintos) → satisfacen el sello
("≥2 probes no solapados"). Bybit es robustez (bar = "sensato", no "mismos números"), no un probe de
graduación (otro venue).

## 3. Parámetros — fijados OFF-PROBE por PROCEDIMIENTO pre-comprometido

No puedo fijar valores que aún no he visto; fijo el **procedimiento de selección**, que corre SOLO sobre
la slice de exploración (jul–dic 2025) y se **CONGELA antes de tocar Probe 1/2**:

- **Rejillas pre-comprometidas:** W (ventana señal) ∈ {1, 5, 30} s · k (niveles OFI) ∈ {1, 5, 10} ·
  h (horizonte reversión) ∈ {0.5, 1, 2, 5, 10, 30, 60} s · τ (percentil extremo de |OFI| causal) ∈
  {90, 95, 99}.
- **Regla de selección (una sola config gana):** la (W,k,h,τ) que maximiza el **Sharpe contrarian NETO
  de costes OUT-OF-SHOCK** en la slice de exploración, **sujeta a pasar el gate de latencia ×10 ahí**.
  (Out-of-shock a propósito: evita seleccionar un artefacto de gamma corta — ver §5.)
- Tras la selección: **CONGELADA**. Cero re-tuning mirando Probe 1/2. Si la config no sirve, el screen
  es negativo; no se busca otra.

## 4. Falsación CONGELADA (criterios duros)

`H_contra` queda **SCREEN-NEGATIVE** si CUALQUIERA:
1. `r_contra` neto de costes ≤ 0 en el agregado de los probes de test.
2. No es **estable** en los DOS probes (signo consistente y >0 en ambos).
3. No supera el **gate de latencia ×10** (`feasibility.py`) ni la **degradación condicional en alta
   latencia** (`screen.conditional_latency_degradation`): si el edge se desvanece/negativiza ahí = juego
   de velocidad, muerto.
4. Es **gamma/vol corta disfrazada** (ver §5).
5. **e-value agregado < 1/α (≈20)** sobre los caminos / probes (SCREEN-POSITIVE solo si ≥20).

## 5. Gates obligatorios (NO opcionales) — y la RED LINE de short-vol

- **Costes round-trip explícitos:** modelo fijado en exploración (taker/maker fee Binance VIP0 + medio
  spread por leg). El edge se mide SIEMPRE neto. Sin esto no hay número.
- **Latencia ×10 + degradación condicional** (§4.3).
- **Estratificación in-shock vs out-of-shock** (`screen.cross_shock_dummy`, ≥3/8 símbolos OFI<P5): el
  **detector de short-vol**. **RED LINE:** si `r_contra` es >0 out-of-shock pero **<0 in-shock** (te
  arrollan en los shocks) → NO es alfa, es **gamma corta** (cobras la prima en calma, pagas el siniestro
  en el shock). Se **clasifica como short-vol y se ARCHIVA como edge**, aunque el promedio salga positivo.
- **Vol realizada como covariable:** regresar `r_contra` sobre vol realizada; si el edge carga ENTERO en
  vol → es una posición de vol, no timing. Declarado.
- **e-value / N_eff por EPISODIOS** (no por nº de eventos crudo; `effective_n_autocorr`,
  `aggregate_by_episode`).

## 6. SCREEN, nunca veredicto · graduación

Resultado etiquetado SCREEN-POSITIVE / SCREEN-NEGATIVE / INCONCLUSO (N_eff bajo). Lenguaje de veredicto
PROHIBIDO. **Sello "tradable claim"** solo si: (a) ≥2 probes no solapados PASAN el mismo pipeline; (b)
e-value agregado ≥20; (c) coherencia inter-régimen (in/out-shock sin la patología short-vol); (d) sensato
cross-venue en Bybit. Nada se llama "edge" sin los cuatro.

## 7. Compromisos anti-p-hacking (vinculantes)

- **UN solo análisis.** Una config congelada, un pase por cada probe de test, un resultado agregado. No
  se re-corre con parámetros retocados tras ver el test.
- El orden es **inviolable:** (1) este pre-registro commiteado → (2) adapter + exploración jul–dic 2025 →
  congelar → (3) Probe 1 ene–may 2026 → (4) Probe 2 forward (≥3–4 sem de masa) → (5) SOLO entonces se mira
  el agregado. Mirar un probe antes de tiempo lo quema.
- Cualquier cambio a este documento = **enmienda fechada y commiteada**, justificada como corrección de
  bug metodológico (no como búsqueda de un resultado), con el diff visible.

---

## ENMIENDA 1 (`2026-06-27`) — parámetros FIJADOS POR TEORÍA (sustituye la selección por grid de §3)

*Cambio PRE-TEST (antes de tocar Probe-1/2), STRENGTHENING (no result-seeking): en vez de SELECCIONAR
(W,k,h,τ) por grid en la slice de exploración (§3 original), se FIJAN por teoría/consistencia, con CERO
grados de libertad de selección. Diff visible, justificado abajo.*

- **W (ventana de acumulación de OFI) = 5 s.**
- **k (niveles MLOFI) = 5** — consistencia con todo el proyecto (`book.ofi`, `h8_io`, `exec_sim`).
- **τ (umbral extremo) = P95 / P5 del OFI causal rodante en W** (percentil móvil, como `feasibility.py`;
  evita el artefacto de z-score con colas gruesas de alts finos). OFI≥P95 → fade SHORT; OFI≤P5 → fade LONG.
- **h (horizonte de reversión) = 5×W = 25 s** — vida media de impacto transitorio ~3-10×W (Cont-Kukanov-
  Stoikov). **NO derivado de la sonda** (la sonda mostró ~10 s a 10 s de spacing, pero es in-sample y NO se
  usa; 25 s es deliberadamente distinto del valor in-sample).
- *(Secundario, por consistencia, no es DoF tuneado:* ventana de lookback del percentil = 3600 s; datos
  @100 ms uniforme.)*

**Justificación:** fijar por teoría elimina TODA la libertad de selección (cero overfitting, sin multiple-
testing), a cambio de **mayor riesgo de Type-II** (si la h real ≠ 25 s, se "falla por no mirar"). Para un
SCREEN de prior modesto (20-30%) preferimos un resultado LIMPIO sin ambigüedad de "lo tuneamos". La slice
de exploración jul-dic 2025 **deja de usarse para SELECCIÓN**; queda como robustez/sanidad opcional. Los
dos probes de test (CryptoHFTData ene-may 2026 + forward) y todos los GATES (§4/§5) intactos.

---

## NOTA DE ESPECIFICACIÓN (`2026-06-28`) — ventana de coincidencia del `shock_mask` (cross-shock del panel)

*Pre-comprometida ANTES de tocar Probe-1. Especifica un detalle del gate short-vol (§5) que el pre-registro
dejaba implícito: la tolerancia de alineación temporal de `cross_shock_dummy`. Clarificación/strengthening
(NO result-seeking; cero DoF de selección sobre dato), diff visible.*

El gate RED LINE estratifica in/out-shock con `shock_mask` = `cross_shock_dummy` (≥3/8 símbolos OFI<P5 **a
la vez**). En el PANEL real los 8 símbolos se reconstruyen INDEPENDIENTES de diffs CHD @100 ms → "a la vez"
tiene un margen real de alineación de rejilla (el evento de un símbolo puede caer en t y el de otro en
t+100 ms). Se fija:

- **`SHOCK_COINCIDENCE_MS = 100`** (±1 rejilla @100 ms): un símbolo cuenta en la fila t si tiene OFI<P5 en
  **[t−100 ms, t+100 ms]**. Implementado dilatando cada columna del panel ±1 fila ANTES de
  `cross_shock_dummy` (no se toca su semántica). Código: `analysis/contrarian_panel.py`.

**Justificación:** ±1 rejilla es el MÍNIMO para no ser frágil a la alineación de 8 reconstrucciones
independientes, sin abrir una ventana tan ancha que agrupe eventos genuinamente independientes (validado en
test: eventos a 100 ms coinciden, a 300 ms NO, y sin ventana no coincide nada). Valor fijado por la
rejilla/teoría, no buscado en dato. `k = 3/8` y `τ = P5` intactos (pre-reg / ENMIENDA 1).

---

## NOTA DE VENTANAS DE TEST (`2026-06-28`) — Probe-1 = cobertura CHD completa + política de exclusión

*Pre-comprometida ANTES de tocar Probe-1 (el hash de git = fecha → las exclusiones quedan EX-ANTE, NO
ex-post). Reconcilia el split del §2 con ENMIENDA 1: al fijar los params por teoría (cero DoF de selección),
la antigua slice de exploración jul-dic 2025 NUNCA se usó para seleccionar nada → puede servir de test sin
contaminación de selección. Decisión del usuario: maximizar potencia antes de gastar el held-out (descartar
~6 meses de dato limpio nunca-mirado-en-outcomes sería falsa modestia, no rigor).*

- **Probe-1 (held-out) = cobertura CHD Binance Futures COMPLETA: `2025-06-28` → ~`2026-05` (~11 meses)**, un
  ÚNICO SCREEN agregado sobre el panel de los 8 símbolos. Sustituye al "ene–may 2026" del §2 (que asumía
  selección sobre jul–dic 2025; con ENMIENDA 1 ya no la hay).
- **Probe-2 (held-out) = captura FORWARD propia** (≥`2026-06`, ~3–4 semanas de masa). No solapa con Probe-1
  (periodo y mecanismo de captura distintos) → cumple el sello "≥2 probes no solapados".

**POLÍTICA DE EXCLUSIÓN dentro de Probe-1 — ENMENDADA a (B) MÁXIMA CAUTELA (`2026-06-28`):**

*Principio:* **cualquier día con acceso de CUALQUIER tipo (incluido solo-feasibility / metadata) sale de
Probe-1** — para que ningún auditor hostil deba CONFIAR en la naturaleza del acceso ("¿el 08-01 fue solo
métricas de congelación o miraste outcomes?" → "ese día no está en el test, punto"). Coherente con el resto
del proyecto (regla AND del guard, pre-registro commiteado, latencia como constante nombrada, suspenso
automático de Probe-2): eliminar toda superficie donde alguien deba confiar. *Esto REVIERTE la versión inicial
de esta nota (que mantenía los toques de solo-feasibility por "no miran outcomes"); "puede que sea verdad" NO
es el estándar del proyecto. Coste = ~10/300 días (ruido); la eliminación de la superficie de ataque es
permanente.*

1. **Días CORRUPTOS** — mecánico, vía `cryptohft_adapter.is_corrupt_day`; el runner los salta con registro.
2. **Los 10 días TOCADOS** (ÚNICA fuente de verdad: `contrarian_runner.PROBE1_EXCLUDED_DAYS`; el calendario de
   Probe-1 sale de ahí vía `probe1_calendar()`, NO hardcodeado en los scripts). Enumeración EX-ANTE, cada uno
   con la naturaleza del acceso: `2025-06-28` (cobertura), `2025-07-01` (episode_count + corrupto),
   `2025-07-02`, `2025-07-03` (episode_count), `2025-08-01`, `2025-10-01` (cobertura + validación del guard),
   `2025-12-01`, `2026-02-01`, `2026-04-01` (cobertura), `2026-05-01` (validación del adapter).

Gates (§4/§5), params (ENMIENDA 1) y la ventana de coincidencia (nota anterior) intactos.

---

## NOTA — modelo de latencia de Probe-1 (`2026-06-28`)

*Pre-comprometida. Especifica QUÉ latencia alimenta el gate de §5 (`retraso = 10·p95(recv − event)`) sobre
dato CHD histórico, donde no existe "nuestra" latencia real.*

- **`recv = event + FEED_LATENCY_P95_MS`**, con **`FEED_LATENCY_P95_MS = 113` ms** = el p95 medido de
  NUESTRA propia sonda (latencia de feed retail documentada; constante conocida, cero DoF). Constante
  nombrada en `analysis/contrarian_runner.py` — referenciada aquí por **NOMBRE, no por valor** (trazabilidad
  PREREG↔código directa). Retraso resultante del gate ≈ **1.13 s**.
- **`CHD.received_time` se IGNORA DELIBERADAMENTE.** No "no se usa": se ignora porque representa la latencia
  de captura del VENDOR en su colo (≈0 ms para nosotros), NO la de nuestro feed. Alimentar el gate con eso lo
  dejaría VACUO (cribaría velocidad inexistente) → sería deshonesto. El único campo de latencia honesto es el
  nuestro, medido.

*Nota honesta (queda en el registro): con `h = 25 s`, un retraso de 1.13 s es ~4.5% del horizonte → para
ESTE mecanismo el gate de latencia es un SUELO de sanidad, no el cuchillo principal. Los cuchillos reales son
los COSTES (neto sobre spread reconstruido) y la RED LINE de short-vol. Documentado para no sobre-atribuirle
poder de criba.*

---

## NOTA — la RED LINE down-only es DELIBERADA (`2026-06-28`)

*Ratificación pre-dato, NO herencia accidental.*

El detector de shock sistémico (`cross_shock_dummy`, §5) usa **OFI < P5** → solo marca ventas sistémicas
(down-shocks). El contrarian fadea AMBOS extremos, así que un short-squeeze sistémico (OFI > P95 cross-símbolo)
en el que fadear la compra extrema te arrolla NO se marca `in_shock`. **Es deliberado:** el riesgo de cola en
perps cripto es ASIMÉTRICO por diseño del mercado — funding, liquidaciones en cadena y la estructura de las
perps crean presión vendedora sistémica sin equivalente alcista de la misma magnitud; un squeeze sistémico
simultáneo en 8 alts finos es mucho más raro y de menor duración. La decisión queda fijada ANTES de mirar
Probe-1 → si el resultado sale positivo, la RED LINE down-only NO es cherry-pick del sentido: la asimetría está
documentada y es pre-dato. (No se prueba la variante simétrica `|OFI|` precisamente para no abrir esa puerta.)

---

## NOTA — corrección de bias de spread CHD (`2026-06-28`)

*Pre-comprometida ANTES de correr `spread_check` y de tocar Probe-1. El MECANISMO y el umbral se fijan
pre-dato; SOLO el valor por símbolo se rellena tras medir → corrección pre-comprometida por diseño, no
post-hoc (la decisión de corregir y el cómo son anteriores al dato; solo el cuánto es posterior).*

El coste = 2·half_spread + 2·fee usa el half-spread del top-of-book CHD reconstruido. Si CHD infraestima el
spread real en alts finos → costes infraestimados → edge FALSO cruza (y, a diferencia del N_eff inflado que
el e-value caza, un spread sesgado 1-2 bps durante 11 meses NO tiene quién lo cace). Se pre-compromete:
- **Medición** (`analysis/spread_check.py`): mediana del half-spread CHD vs la de NUESTRA sonda por símbolo
  en los días SOLAPADOS (sonda 12-25 jun 2026, dentro de cobertura CHD; comparar SPREAD no mira outcomes).
- **Corrección:** `contrarian_runner.SPREAD_CORRECTION_BPS[symbol]` (bps) = `probe_median − chd_median`,
  ADITIVO al half-spread en COSTES (no toca la señal). Constante init a CERO; el valor se rellena tras el
  check y se commitea ANTES del disparo.
- **Exclusión:** símbolo FUERA si `|bias_frac| > MAX_SPREAD_BIAS_FRAC = 0.5` (reconstrucción cualitativamente
  ROTA, no un offset constante). Anclado al SPREAD (medible pre-dato), NO al edge (desconocido → no
  pre-comprometible). *(Refinación explícita de "50% del edge", que no es pre-comprometible.)*
- **Supuesto declarado:** el bias se mide en el solape (jun-2026) y se asume ~estacionario por símbolo a lo
  largo de Probe-1 (~11 meses). Si derivara mucho, la corrección es imperfecta (limitación honesta).

---

## NOTA — maquinaria de GRADUACIÓN: diseño FIJADO pre-disparo (`2026-06-28`)

*Especificada y congelada ANTES del disparo (NO ejecutada). Motivo: si se diseñara DESPUÉS de ver Probe-1,
cada decisión (paths CPCV, fusión de probes, umbral) podría estar inconscientemente sesgada por el signo del
resultado — el sesgo más difícil de detectar por involuntario. Fijar el diseño ahora lo elimina: si Probe-1
sale POSITIVE, los pasos a "graduado" son mecánicos, sin decisión nueva; si sale NEGATIVE, no hay tentación
de retocar criterios.*

Un SCREEN-POSITIVE NO es "graduado". El sello "tradable claim" (§6) exige TODO, con estos params CONGELADOS:
1. **Probe-1 — CPCV** (`analysis/cv.py`): bloques **estratificados por régimen** (vol + cross-shock dummy,
   RUNNER_DESIGN §2), **N=6** grupos cronológicos, **k=2** de test → **C(6,2)=15** paths; purga + embargo ≥
   lookback (`pct_window_s`=3600 s + `h`=25 s). *Criterio de N=6 (no solo el valor): 6 grupos sobre ~11 meses =
   bloques de ~55 días, lo bastante largos para contener 2-3 regímenes de vol independientes por bloque (la vol
   tiene memoria de SEMANAS, no de días) sin que el PBO se vuelva inestable por tener pocos paths.* Ningún fold
   mezcla regímenes arbitrariamente ni concentra todos los shocks.
2. **Probe-2 — split único estratificado por RÉGIMEN, NO CPCV** (forward ~3-4 sem: demasiado corto para
   estratificación cronológica múltiple sin bloques ruidosos). Se parte en dos estratos — **in-shock** y
   **out-of-shock** —; e-value sobre CADA estrato; **`E(Probe-2)` = PRODUCTO de los dos** (regímenes
   ~independientes → producto válido bajo la dependencia interna de cada estrato). Un único split maximiza la
   masa por subgrupo. **Suelo de masa:** si ALGÚN estrato tiene `N_eff < 10` → Probe-2 = "masa insuficiente"
   (evita que un Probe-2 anémico infle el producto).
3. **e-value (común):** el `net` de BLOQUES del subgrupo → tstat con `effective_n_autocorr` → p one-sided →
   e-value vía `screen.p_to_evalue` (κ=0.5). Agregado **intra-Probe-1 = MEDIA** de los 15 e-values
   (`screen.aggregate_evalue`; válida bajo dependencia de paths CPCV — el producto sobre-contaría).
   Intra-Probe-2 = PRODUCTO de los 2 estratos (item 2).
4. **Fusión = PRODUCTO** `E(P1)·E(P2)` (probes DISJUNTOS → independientes). **Sello solo si `E(P1)·E(P2) ≥
   1/α = 20`**, Y AMBOS probes SCREEN-POSITIVE (los 4 gates) + coherencia inter-régimen (RED LINE sin short-vol)
   + sensato cross-venue en Bybit (§6). Un probe NEGATIVE mata el sello aunque el e-value salga alto.
   - **Probe-2 "masa insuficiente" → NO entra en la fusión y el SELLO queda EN SUSPENSO** (se sigue acumulando
     captura forward). §6 exige ≥2 probes y §7 "aflojar NO" → NO se relaja a 1 probe (RATIFICADO por el usuario
     2026-06-28; la variante "Probe-1 solo con E≥20 sella" queda DESCARTADA por aflojar §6 sin necesidad — el
     suelo de N_eff ya neutraliza el Probe-2 anémico).
   - **El suspenso se LEVANTA AUTOMÁTICAMENTE** en cuanto AMBOS estratos (in/out-shock) de Probe-2 superan
     `N_eff ≥ 10` — mecánico, SIN decisión activa. Así la elección de CUÁNDO intentar la fusión no puede
     contaminarse por haber visto Probe-1 (si fuera una decisión manual, el signo de Probe-1 podría sesgar el
     momento). En cuanto se cumple, se ejecuta la fusión del item 4 una sola vez.
5. **Cross-check secundario (no decide, informa):** DSR (`overfit.deflated_sharpe`) y PBO (CSCV) sobre los 15
   paths de Probe-1; reportados, nunca usados para re-etiquetar.

*Implementación: mecánica (todas las piezas existen en `cv.py`/`overfit.py`/`screen.py`); se codifica cuando
haga falta, SIN decisiones nuevas — el diseño ya está aquí. NO se ejecuta hasta tener los 2 probes.*

---

*Plan de datos asociado (Bybit 200-niveles gratis, Crypto-Lake $64/mes como puente pre-jul-2025 si hiciera
falta, Tardis fuera hasta haber edge+ingresos) → se actualiza en `DATA_PLAN.md`. Coste hasta validar: $0–$64.*

---

## EL DISPARO — ejecución de Probe-1 (2026-07-01, POST-DATO; el held-out ya se gastó)

Registro honesto de lo ocurrido al ejecutar `run_disparo.py` sobre el calendario congelado (params
W5/k5/P95/h25, PREREG congelado en commit `5942640` ANTES del disparo). Se miró UNA vez, en frío.

- **VEREDICTO: SCREEN-NEGATIVE (no supera costes; `stopped_at=costs`).** `gate_costs`: media neta
  **−10,71 bps/evento**, Sharpe_evento **−1,26**, **tstat_neff = −26,16** sobre **n_eff = 433,8**
  (de `n_bloques = 696.637` crudos → corregido por dependencia cross-seccional + autocorrelación). Decisivo,
  no marginal: n_eff sano ⇒ NO es problema de potencia. Fadear el OFI extremo (down-only) en estos 8 perps
  finos PIERDE tras costes por amplio margen. La reversión, si existe, está por debajo del suelo de costes.

- **10 días DATA-UNAVAILABLE (no confundir con exclusión de disciplina), verificados por diagnóstico
  2026-07-01 — hueco de ARCHIVO de CHD en LINK, periodo 30-mar→09-abr 2026:**
  - 5 días `No data files found` (LINK n=0, dataframe vacío → el KeyError 'event_time' era el síntoma):
    2026-03-31, 04-03, 04-04, 04-06, 04-07.
  - 5 días LINK PARCIAL (3-17 de 24 h): 2026-03-30, 04-02, 04-05, 04-08, 04-09.
  - Los otros 6-7 símbolos venían completos (24/24 h) esos días; el agujero es de LINK (y LTC algún día).
  - **Manejo:** el fail-loud del loader (verificación 24 h + `IncompleteDownloadError`) RECHAZÓ el dato
    incompleto en vez de corromper en silencio — la guardia haciendo su trabajo, mismo patrón que los
    corruptos. Se registran en `screen.json` → `diag.errores`. **Calendario congelado SIN tocar** (no se
    edita `PROBE1_EXCLUDED_DAYS`): son data-quality de runtime, no exclusión pre-registrada.
  - **Dataset efectivo = 318/328 días.** El veredicto es ROBUSTO sin ellos: 10 días contiguos (~3%) no
    pueden voltear un tstat de −26. NO se sustituye por otra fuente (rompería la consistencia de
    reconstrucción) ni se usa LINK parcial (violaría el fail-loud) ni se cae a 7 símbolos (cambio de
    metodología post-dato). "328" honesto = **318 procesados + 10 data-unavailable documentados**.

- **Optimización del reconstructor (2026-07-01, `cryptohft_adapter.py`): BYTE-IDÉNTICA, no cambia ningún
  resultado.** `to_pydict()`→cast pyarrow a numpy, y `sorted(...)[:k]`+lambda→`heapq.nlargest/nsmallest`.
  Verificado idéntico bit a bit contra la versión validada en días reales del solape (ATOM, LINK); 43/43
  tests verdes. ~3,5× en días pesados. Es aceleración pura, no toca la semántica.

- **Disciplina:** params CONGELADOS → cae con ellos. **NO hay contrarian v1.1** con params ajustados
  post-dato. **Probe-2 (captura forward) NO se tocó — intacto:** un Probe-1 SCREEN-NEGATIVE ya mata la
  graduación (regla AND del §fusión); gastar Probe-2 no lo resucita. Mecanismo CRIBADO. Ver LEDGER.
