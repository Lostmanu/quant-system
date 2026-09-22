# PREREG B — VERSIÓN-FREEZE (ensamblado (y), M-03-re4)

**Naturaleza de este documento.** Compilación NORMATIVA de lo ratificado por la mesa — cero diseño
nuevo. Ensamblado por Code por orden de la mesa (M-03-re4, 2026-07-12) tras M-07 en verde
(commit `91201f5`, CI run 29190658883 SUCCESS, suite 422); **SINCRONIZADO a M-09.1** (recompute de
pines bajo la receta M-09.2 — crudo/E-raw/rango; suite 446, §9). Cada número lleva su fuente inline
(log sellado / hash / línea de acta); ningún valor viene de memoria. Este fichero SUPERSEDE
normativamente a `docs/PREREG_B_GATE.md` (que queda inmutable como fuente histórica, con cabecera).
El freeze ocurre con la firma del propietario según §10 (regla no circular).

**Convención de citas.** `⟨log⟩` = fichero en `docs/runs/` (todos ×2 byte-idénticos salvo indicación);
`⟨acta lN⟩` = línea del acta append-only `docs/ECO_CONTEO_FASE0.md`; `⟨commit⟩` = hash git en
`Lostmanu/quant-system`.

---

## §1 — GATE DE REPLICACIÓN LIT: §G0–G11 (texto de la mesa, con placeholders rellenos y enmiendas ratificadas)

Texto base: `docs/PREREG_B_GATE.md` (comiteado verbatim en `b772ca2`). Ediciones respecto del base,
TODAS ratificadas: G7 placeholders rellenos (este §), G4/G5 sustituidos por la versión Student (§2,
ratificación (p) `e9a5ead`), §V sustituido por la versión Student implementada (§5).

**G0 — Naturaleza.** Compuerta de LECTURA del held-out WTI de A2. Se congela con el prereg B; el hash
del commit es la autoridad de fecha. Redactado por la mesa; Code comitea sin editar.

**G1 — Conjunto.** Días LIT ≥ 2026-06-30 (`FRONTERA_REPLICACION`, `eco_gate_b.py` l.43 @ `91201f5`)
hasta la fecha de disparo (G4). Held-out de la replicación: **lenguaje R10-preciso** (corrección
documental de la auditoría de la mesa sobre (y)) — el pipeline **procesa** las ventanas protegidas
**sign-blind** (computa el primer momento del markout internamente y lo descarta); **ningún primer
momento se EXPONE** (imprime/guarda/cita/retorna a una firma) antes de la lectura única (G6). No es
"no se computa" (sí se computa, ciego al signo); es "no se expone". Bloques generados con el pipeline
pinneado al hash del freeze (post-I2/I6/I7, desempate estricto).

**G2 — Receta de celda.** La receta oficial de la flor (acta `7df45b9`) con dos excepciones
pre-declaradas: `dec=(tipo≤1)&slow`; tercil POOLED sobre `vol20[dec]` finita **de la ventana de
replicación**, clasificador I2-fijo, corte estricto `>q2`; suelo I7 ≥1s; markout 25s = `mo[:,1]`
(referencia Binance); day-mean sobre markouts finitos; **día vota con ≥30 fills de celda**
(`MIN_FILLS_DAY=30`, `eco_gate_b.py` l.46 @ `91201f5`). Exclusiones admisibles: exactamente las del
pipeline, registradas, jamás silenciosas.

**G3 — Estadístico único.** t = μ_dm/(σ_dm/√n_eff), n_eff = `effective_n_autocorr`; H0: μ≤0;
unilateral; **α=0,05** (celda única, sin BHY).

**G4 — Masa y disparo (versión Student ratificada — sustituye al N_min=15 del texto base).**
**N_min = 17** day-means válidos. Sello mecánico: MC t-no-central, B=10⁶, semilla 20260711,
μ=+18,24 / σ=28,12 / t₀.₉₅;df de la tabla versionada:
N=15 → 0,7718 (falla) · N=16 → 0,7968 (falla) · **N=17 → 0,8198 (PASA)**
⟨`nmin_mc_e9a5ead_run{1,2}.log` ×2 idénticos; generador `analysis/eco_nmin_mc.py`⟩.
σ=28,12 = receta GATE I2-fija sobre los 79-npz gastados: `[GATE dia-vota>=30] N=57 |
sigma_daymean=28.12` ⟨`gate_sigma79_5daff8b.log`, ventana gastada, legal⟩. Code reporta semanalmente
SOLO conteos (`conteo_semanal`). Disparo al alcanzar N_min. **Cap: 2026-09-30** (`CAP`,
`eco_gate_b.py` l.44 @ `91201f5` — solo brazo LIT) — sin masa: INCONCLUSO-POR-MASA, nada se lee, y B
se re-congela con mesa fresca.

**G4-bis — Preflight sign-blind (verbatim del base).** Alcanzado N≥N_min, el pipeline computa n_eff
de la serie de day-means SIGN-BLIND (solo se emite n_eff; ningún primer momento expuesto al
investigador). Si n_eff<N_min: no se lee; se acumula hasta el cap. En el cap con n_eff<N_min →
INCONCLUSO-POR-MASA, jamás NO-REPLICA.

**G5 — Veredicto mecánico, condicionado a n_eff≥N_min (versión Student ratificada — sustituye al
1,645 del texto base).** REPLICA ⇔ t ≥ t₀.₉₅;df con **df = ⌊n_eff⌋−1**, cuantil de la TABLA VERSIONADA
`analysis/t_tabla.py` (generador `gen_t_tabla.py` auditable; 4 referencias de la mesa exactas;
implementación: `_veredicto_gate`, `eco_gate_b.py` @ `91201f5`). df=⌊n_eff⌋−1 **declarado como
heurística conservadora** (salvedad ratificada, acta ciclo (p) `e9a5ead`). Sin discreción post-hoc.

**G6 — Secuencia de lectura (verbatim del base).** El gate se lee ANTES que el held-out WTI, en
lectura única que gasta su conjunto. REPLICA → se procede a la lectura única de A2 conforme a este
prereg. **NO-REPLICA → el held-out WTI NO se lee** (bala preservada); A2 se declara
ILEGIBLE-POR-RÉGIMEN. Del gate, solo el binario REPLICA/NO-REPLICA cruza hacia A2 (flag sellado sin
t/N/n_eff — implementado en `preparar_lectura`, test `test_x_fase1`).

**G7 — SESOI escala-libre de A2 (placeholders RELLENOS).**
**r\* = 0,514808** — raw completo 0,5148077528408752 = 13/25,252144957533773, day-set = LOS 79
días-npz del decisivo (pin pre-declarado de la mesa), 24/7, rejilla I2-fija
⟨`rstar79_M091_run{1,2}.log` ×2 idénticos: «r* [PRIMARIO — ENTRA AL GATE §G7] =
13.0/25.252144957533773 = 0.514808»; el mismo log sella «n_trailing_invalido=0 → r* NO se mueve por
M-09.2» (procedencia de la invariancia)⟩. Variante 105-cal = **0,474795** (sensibilidad, no decide)
⟨mismo log; ratificada en `4d23225`⟩.
Listón de A2: μ_WTI(lectura) ≥ r\*·vol25_agit_WTI(día-set = población votante de B = días que forman
day-means; sesión-activa; misma rejilla), computado y SELLADO antes de la lectura (prep A2, §5-§6).
Supuesto de transferencia DECLARADO: edge ∝ vol25 (linealidad).
**Rango calibrado: [7,22, 17,76] bps** — niveles vol25_agit_WTI por década de la sonda: 16,87 /
17,76 / 7,22 ⟨`ancla_M091_run{1,2}.log` ×2 idénticos: «RANGO CALIBRADO G7 (vol25_agit_WTI por
década, bps): [7.22, 17.76]»⟩. **Los dos límites son PINS OPERATIVOS redondeados a 2 dp** (misma
regla de presentación que la calibración original: el código construye los niveles en raw
—`eco_e_anchor.py` l.267— y solo el print redondea —l.279—): `freeze_pins.rango_calibrado` sella el
redondeado `[7.22, 17.76]`, NO el raw min/max. El crudo prospectivo `vol_guard` (raw, futuro) se
compara contra `17,76` redondeado — no contra un raw (M-09.1, convergencia de doble mesa; no hay
recompute del rango en la lectura, es pin estático comparado consigo mismo en el tamper-check).
Población del rango y de toda medición de vol de precio: **«all eligible price days», criterio 200
trades/día + 20 puntos finitos/día + 500 pool — idéntico en calibración y lectura** (rejilla de
`_day_grid`/`symbol_vols`/`_stats`, `eco_e_anchor.py` @ `118e877`; pin verbatim M-03-re4 §1).
**EXCLUSIÓN DE VENTANA (M-09.2):** cada punto de retorno cuyo precio (inicial u objetivo) sea
≤0/no-finito, o cuya ventana trailing de 20 min contenga un ≤0/no-finito, se DESCARTA y se CUENTA
(`n_precio_invalido`/`n_trailing_invalido`), validado ANTES del `log()` para no arrastrar NaN;
idéntico en principal (`eco_e_anchor`) y referencia (`eco_ref_crudos`), comparado por el differential.
vol25_agit_WTI(ventana de lectura) ∉ rango →
INCONCLUSO-POR-RÉGIMEN-NO-CALIBRADO **pre-lock, sin gastar** (§5). La inferencia del veredicto vive
en §V.

**G8 — Compuerta de potencia (contexto, sellada; no decide el veredicto — el SESOI es G7).**
E=5,90 ratificado (§7) + stress E_low=2,61 × σ_p90=1,08 → **n_eff_req_stress_cons = 1,51**: PASA
vs proyección conservadora 8 sem (n_eff_proj_cons = 10,4 → **~6,9×**)
⟨`fase2_cc72e87_run{1,2}.log`: clave `STRESS(E_low=2.61 × σ_p90, R4)` = `{'n_eff_req_stress_cons':
1.51, 'PASA(vs conservador 8sem)': True}` y `D=8sem: n_eff_proj_cons=10.4`; corrección R4 en acta
(«el "~9×" queda RETIRADO»)⟩.

**G9 — Diagnósticos que NO deciden (post-lectura; verbatim del base).** Receta legacy-v1
(continuidad con la flor); sensibilidad I5 (`thr_con_at` recontado como fill); denominador 105-cal
(0,474795); split por mitades temporales.

**G10 — Cualificador de régimen (verbatim del base).** La sonda del ancla disparó INESTABLE
(max/min 3,54 primario / 3,84 robustez; 3ª década 0,201 ⟨acta, sección «SUB-VENTANAS INESTABLES»,
sellos `5daff8b`⟩). Motiva G7 y se declara como limitación de toda lectura en bps absolutos.

**G11 — Anti-forking (verbatim del base).** Una ventana, una celda (lenta×agitado), un horizonte
(25s), un estadístico. Nada se estratifica, re-corta ni re-ventanea post-hoc. El day-set del freeze
se lista en el prereg (§10); toda ausencia posterior, fail-loud.

## §2 — G4/G5 EN CÓDIGO (dónde vive cada pieza)

N_MIN=17, tabla Student versionada (`t_tabla.py`: T95/T80 df=1..60, 10 decimales, df>60→60, df<1
raise), preflight sign-blind (`preflight_neff`: solo (n_eff, N)), veredicto `_veredicto_gate`
(t vs t₀.₉₅;⌊n_eff⌋−1). Todo @ `91201f5`. df=⌊n_eff⌋−1 = heurística conservadora DECLARADA.

## §3 — VENTANA DE A2 (prospectiva, mecánica, sin extensión)

**[D0, D1)** con **D0 mecánico** = `primera_sesion_posterior(finalizacion_utc de R_F)` — primera
sesión WTI cuyo tramo elegible arranca estrictamente después de la finalización EXITOSA del CI del
freeze en origin/main; la fecha de autor git NO es autoridad (e2). Cadena de atestación
**F → R_F → A_F → P → R_P** (g1): `freeze_pins.json` en el ÁRBOL de F; R_F = run de CI verificado en
el SERVIDOR (headSha==F, success, workflow CI, branch main, `finalizacion_utc == updatedAt`);
A_F = `atestacion_freeze.json` = `{F, run_freeze, finalizacion_utc}` commiteada (leída SIEMPRE del
objeto git, M-06.3); P = commit del prep; R_P = primer run exitoso de CI de P por databaseId,
paginación completa (i5), `headBranch=="main"` (j7), finalización ≥ D1 (g2), id sellado en el lock.
GitHub caído = fail-closed (g1). **D1 = D0 + 8 semanas** (`SEMANAS_A2=8`, `ventana_fija_a2`).
**Cierre definitivo SIN extensión** (e4): masa insuficiente en D1 = INCONCLUSO-POR-MASA-FINA
**definitivo para este prereg**. El readiness del gate LIT jamás cambia qué días votan en A2 (e3);
sin regla de parada cruzada.

## §4 — MÍNIMOS DE A2 (masa = el recurso escaso del diseño, no la potencia)

- **n_eff ≥ 2,0** — suelo inferencial (df=⌊n_eff⌋−1 ≥ 1; `MIN_NEFF_INFERENCIAL`, l.56 @ `91201f5`).
- **n_eff ≥ 1,51** — potencia constatada = stress RATIFICADO E_low×σ_p90 (R4; `MIN_NEFF_A2`, l.60).
  Referencia nominal, que JAMÁS sostiene la lectura: n_eff_req_p90 = 0,27 (sello v7 `0596a3a`,
  ⟨acta l.302⟩) / 0,30 (sellos post-I2, ⟨`fase2_cc72e87_run1.log` clave CONSERVADOR⟩).
- **N ≥ 8** días votantes (cautela C1 de A11; `MIN_DIAS_AGITADO_A2`, l.63).
- Proyección VIGENTE bajo los filtros del productor (M-06.4, sellada ×2): sobre la ventana de diseño
  gastada, cero días excluidos por snaps≥300/span≥20h; N_votantes_vigente=10/30, wilson90_lo=0,2342 →
  8 semanas: punto 18,7 / **conservador 13,1 ≥ 8 (margen 1,64×)**
  ⟨`masa_m064_a1b5792_run{1,2}.log` ×2 idénticos⟩. Honestidad: la proyección informa; los mínimos
  mandan. N_vigente NO es comparable 1:1 con el N de fase2 v8 (umbral 300 vs 100; nota impresa en la
  propia sonda).

## §5 — §V: VEREDICTO DE A2 (trifurcado, Student, poblaciones selladas)

Implementación normativa: `_veredicto_a2` (`eco_gate_b.py` @ `91201f5`). α=0,05 unilateral;
n_eff = `effective_n_autocorr`; **crit = t₀.₉₅;⌊n_eff⌋−1 de la tabla versionada**; se = σ̂/√n_eff.

- **bar ≡ r\*·vol25_agit_WTI(población votante = días que forman day-mean, ≥30 fills de celda,
  lista SELLADA `dias_votantes`==`dias_bar` en el prep — M-06.1/j1)**, sellado pre-lectura y
  RECOMPUTADO pre-lock (bar == r\*(pins de F)·vol_votantes, M-07.1).
- **Guard de régimen PRE-LOCK** sobre all-eligible-days con **lista SELLADA `dias_guard`** +
  clasificación TOTAL del resto de [D0,D1) (`guard_descartes` — **vocabulario CERRADO**
  `{rejilla-trades<200, rejilla-puntos<20, ausente-CHD}`, validado en prep y lectura). El cierre
  **INCONCLUSO-POR-RÉGIMEN-NO-CALIBRADO sin gastar** se **DECIDE recomputando** `lo ≤ vol_guard ≤ hi`
  del crudo frontera-de-confianza + pins DE F (no del booleano `prep["rango_ok"]`); no toca el
  outcome (P0-fix). vol_guard ∉ [7,22, 17,76] → cierre pre-lock, `gasto: False`.
- **GENERALIZA** ⇔ LB90 ≡ μ̂ − crit·se ≥ bar.
- **NO-GENERALIZA** ⇔ UB90 ≡ μ̂ + crit·se < bar, con potencia constatada (n_eff ≥ 1,51 ∧ N ≥ 8).
- **INCONCLUSO** ⇔ resto. Degeneración (σ=0, n_eff≤1, no-finitos) = raise, jamás veredicto.
- **Regla general ratificada (M-03-re4 §5): toda población que alimente una cantidad decisoria lleva
  lista sellada** (votantes/bar/guard: hecho; el conjunto del gate: manifiesto de Fase 1).
- Diagnósticos no decisorios: posición de μ̂ vs 0 (existencia sin escala) y lectura en bps absolutos,
  ambos con el cualificador INESTABLE (G10).

## §6 — SECUENCIA OPERATIVA (bifásica, orden canónico g4)

**Fase prep (post-D1, j4 — antes de D1 no se crea NI UN artefacto):** `preparar_lectura_a2(chd)` —
todo DERIVADO (i1): atestación del objeto git → D0/D1 → pins del árbol de F → manifiesto-inventario →
`_paths_validados` (puerta única: SHA + procedencia, M-06.2) → votantes (j1) → rejilla con igualdad
EXACTA (`dias_usados == |votantes| ∧ ausentes == [] ∧ per_day == votantes`, M-06.1) → guard sellado +
clasificación total (M-07.1) → preflight (N, n_eff) → prep sellado O_EXCL → **STOP** → commit humano
(=P) + push → CI (=R_P).

**Fase lectura:** `leer_a2(expected_commit=P)` — y NADA MÁS por firma (f1/f5). Orden canónico
(**reordenado por el P0 de la auditoría de la mesa sobre (y): ningún retorno definitivo descansa en un
booleano sellado; cada cierre se decide sobre valores RECOMPUTADOS de la fuente, antes de su check**):
40-hex exacto (g3) → estado del lock (v) → ancestría origin/main → cadena F→R_F→A_F ejecutada (i2:
finalizacion==updatedAt, d0==primera_sesion_posterior, d1==d0+8sem, F ancestro de P) → artefactos DEL
ÁRBOL de P con esquemas estrictos y cross-links (g3/m) → hash del manifiesto vs prep (i1) → pins
RECARGADOS del árbol de F: r\*/rango vs prep (j3) → `dias_bar == dias_votantes` (M-06.1) →
**TAMPER-DETECTORS pre-lock (M-07.1, raise si el prep miente sobre sus propios derivados):**
bar == r\*·vol_votantes · rango_ok == (lo≤guard≤hi) · potencia_ok == mínimos · N == |dias_votantes| ·
crit_t95 == t95(⌊n_eff⌋−1) · cobertura dias_guard ∪ descartes == calendario · guard_descartes ∈
vocabulario cerrado → **REPLICA** (G6; NO-REPLICA = no-lectura) → **R_P** derivado ≥ D1 (g2/j7) →
**(a) RÉGIMEN: cierre decidido recomputando `lo≤vol_guard≤hi` (crudo+pins de F), NO toca `mo`, sin
gasto** → **(b)** `_paths_validados` (lee bytes para el SHA-256 y metadatos de procedencia, JAMÁS
interpreta `mo`) → votantes re-derivados == sellados (j1) → **N/n_eff recomputados de los npz**
(preflight sign-blind) == sellados o **raise** (tamper) → **(c) MASA: cierre decidido de neff_rec/n_rec
recomputados (NO de `prep["potencia_ok"]`), sin gasto** → **LOCK O_EXCL (v) = frontera EXACTA del
gasto** → cargador único autorizado (k1) → day-means → `_veredicto_a2` → sello del resultado.
**Crash post-lock = GASTADA-PENDIENTE-DE-MESA; jamás reintento silencioso.**

**FRONTERA DE CONFIANZA EXPLÍCITA (M-07.1 refinada + P0, verbatim M-03-re4 §6):** todo cierre y todo
veredicto se DECIDE sobre valores recomputados de la fuente (npz para N/n_eff/votantes; crudo+pins
para régimen/bar). Lo único NO recomputable sin red son las **dos mediciones crudas de nuisance**
(`vol25_agit` votantes y all-days), aceptadas como artefactos de Fase prep. Su custodia:
1. **SHA** — el prep viaja en el árbol de P, hash-linkado vía i1.
2. **Doble corrida byte-idéntica sobre el PAYLOAD CANÓNICO** — la comparación ×2 excluye los campos
   DINÁMICOS (`fecha`, timestamps): dos corridas del prep difieren solo en `fecha`, así que el
   byte-idéntico se exige sobre el prep SIN ese campo (payload determinista = todo salvo `fecha`).
3. **Validación DIFERENCIAL (B-ampliada)** — una implementación de referencia INDEPENDIENTE recomputa
   ambos crudos sobre el MISMO payload en la Fase prep y BLOQUEA si difieren de la principal (cierra el
   bug de implementación; el de especificación lo audita la mesa — §9).
4. **Procedimiento de auditoría** — la mesa re-corre `symbol_vols` sobre las listas selladas
   `dias_bar`/`dias_guard` con el criterio 200/20/500 y compara los dos crudos.
Ni un bit de confianza más. Nota de precisión (auditoría (y)): `_paths_validados` **sí lee los bytes
del npz** para el SHA-256 (crudos, sin interpretar) y los metadatos de procedencia — lo que jamás hace
es interpretar el array `mo`.

## §7 — COMPUERTA DE B

**E = 5,90** — pin RATIFICADO (dirección del menor entre primario y robustez). Raw documentado:
robustez a precisión completa = **5,908334763956463** = 13·15,338476446843648/33,74896680286289
⟨`ancla_M091_run{1,2}.log`: WTI agit raw 15.338476446843648 (M-09.2: excluidos los 23 puntos con un
≤0 en la ventana trailing, TODOS del 06-15 = 2ª década) / LIT@horas-WTI agit raw 33.74896680286289
(0 inválidos, invariante); el log presenta «5.91»⟩; primario 6,46 (raw 6,464983296090528). NOTA R12
⟨acta l.507⟩: mantener «5,90» es marginalmente MÁS duro; decisión de la mesa en M-03-re4 §7 =
pin 5,90 + raw documentado. **Stress E_low = 2,61** (peor década de la sonda: 13·0,201 —
⟨acta §E-2, `463ed91`⟩). **Aproximación z de la compuerta explícitamente RATIFICADA por márgenes**
(la compuerta no decide el veredicto; G8): con márgenes ~6,9× (conservador) el error z-vs-t es
inmaterial; el VEREDICTO usa Student (§5), la compuerta usa z — declarado.

## §8 — SECCIÓN DE EXPOSICIÓN (incidente nº3, P0)

Copiado del acta (sellos `894ee90` P0 y `2c3bdd3` P0-v2; ⟨acta l.554 ss.⟩):

- **E1 (directa, MISMA FAMILIA DE OUTCOME que B — lenguaje ratificado e6; "mismo objeto" sobreafirma,
  ⟨acta l.638⟩):** `lighter_pilot/screen_output.txt`, impresa **2026-07-05 10:38** — celdas WTI de la
  cohorte LENTA de terceros, pooled sobre 10 días que INCLUYEN 06-14 y 06-30. **Valores NO reproducidos
  aquí** (higiene de firewall: no se re-imprimen primeros momentos del held-out en el documento de
  freeze) — constan por hash en ⟨`docs/ECO_CONTEO_FASE0.md` l.625-627, sello `894ee90`⟩.
- **E2 (indirecta, objeto sim-maker):** `lighter_capa2/screen_output.txt`, impresa **2026-07-04
  18:18** — celdas pooled 25s que INCLUYEN markouts WTI de días protegidos (el screen consume todos
  los candidatos; a 25s solo excluyó ARC/FARTCOIN/XPT por densidad; contribución no separable).
  **Valores NO reproducidos aquí**; por hash en ⟨acta l.629-631, sello `2c3bdd3`⟩.
- **Cronología normativa** ⟨acta l.642-644⟩: E2 07-04 18:18 → E1 07-05 10:38 → … → **elección de
  ventana 06-05..07-04: `fd065be` 2026-07-08 00:54** → norma `229a2a2` 07-10. Ambas exposiciones son
  PRE-elección-de-ventana → **riesgo de SELECCIÓN formal** (no brecha del firewall post-norma; WTI
  era símbolo de diseño del piloto — colisión de diseño).
- **Lenguaje ratificado:** E1 = «misma familia de outcome» (e6); exposiciones pooled, jamás per-día;
  estrato AGITADO no estratificado por el piloto.
- **Respuesta de diseño:** VENTANA PROSPECTIVA [D0, D1) con D0 mecánico posterior al freeze (§3) —
  los días expuestos (≤07-08) quedan estructuralmente fuera de A2; franja expuesta [2026-06-05, D0)
  infranqueable por tripwires ejecutables (e1/f2: primera sentencia de `fetch_day_snapshots`,
  `run_symbol_day`, `_snapshots_full`; spy=0 en tests).
- **Custodia:** 93 npz inventariados a ciegas (SHA-256 sin abrir: `p0_inventario_wti.txt`,
  `p0v2_inventario_custodia.txt`); **20 npz con fecha ≥06-05 CUARENTENADOS** en
  `data_hist/blocks_quarantine_heldout/{capa2,pilot}/` ⟨acta l.559⟩; 73 pre-06-05 registrados.
- **Bala = «intacta por protocolo auditable»** (e6/acta l.639: los npz cuarentenados siguen siendo
  legibles localmente; la garantía es protocolo + custodia + auditoría, no imposibilidad física).

## §9 — PROCEDENCIA Y CUSTODIA (maquinaria VIGENTE: código M-09, último commit de código `118e877`; cadena de sellos M-02→M-09)

- **Productor** `eco_runner_wti.py`: pineado a F (j2: `rev-parse HEAD == F`, manifiesto
  `commit_productor == F`), **receta operativa M-06.3**: worktree-en-F para el código +
  atestación del objeto git A_F (ref local de origin/main; autoridad = contenido verificado contra
  R_F en el SERVIDOR); entrada única `producir_ventana(chd, key)` (i3) con autorización interna
  (j8) — **documentada como barrera de API convencional, no seguridad (M-06.5)**; huella h1 completa
  de entradas (snapshots: ts+oid+is_bid+px+rem+owner, struct `<q?ddq`, little-endian declarado;
  trades `<i8/<f8`); cero defaults de producción (h3); `max_gap_ms` = campo DERIVADO del npz, fuera
  de `params` (j6/M-06). Humo ×2 byte-idéntico vigente: sha256
  `333e155bafbc2cb35d466d501fcf9ba64a6ec953c482a07ecc82b1d3def34631` ⟨`humo_a1b5792.log`⟩.
- **Manifiesto-inventario**: clasificación TOTAL de [D0, min(hoy,D1)) con **enum cerrado
  `{producido, ausente-CHD, ausente-0xA, excluido-snaps<300, excluido-span<20h}`** (j5; M-07:
  `excluido-baja-actividad` RETIRADO por la mesa); producidas ↔ SHA-256 uno-a-uno (i6);
  hueco sin razón = fail-closed.
- **`_paths_validados`** = puerta única de prep y lectura (M-06.2): nombre → jaula realpath →
  existencia → SHA vs manifiesto (u) → procedencia interna (h3/i4: commit pineado; j6: `params` ==
  `params_productor` de freeze_pins POR IGUALDAD). Precisión (auditoría (y)): **lee los bytes del npz
  para el SHA-256** (crudos, sin interpretar) y los arrays de metadatos de procedencia; lo que jamás
  interpreta es el array `mo` — nada INTERPRETA el outcome antes del lock.
- **Prep** nacido del manifiesto+atestación (i1), firma sin inyección (TypeError por construcción);
  igualdad de rejilla exigida (M-06.1) y **listas selladas**: `dias_votantes`, `dias_bar`,
  `dias_guard` + `guard_descartes` (clasificación total, M-07.1), `crit_t95` sellado.
- **Lectura**: revalidación de pins de F (j3), R_P con `headBranch=="main"` y paginación completa
  (j7/i5), igualdades `dias_bar==dias_votantes` y cobertura `dias_guard` pre-lock, recomputación
  M-07.1 completa, lock O_EXCL como frontera del gasto (v), cargador único k1.
- **Muros sign-free = {`phase2`, `_day_vols_conteos`}** (M-07.2, RATIFICADO): los arrays de markout
  viven solo dentro; añadir un llamador exige firma de la mesa.
- **B-ampliada — validación DIFERENCIAL de los dos crudos** (`vol_guard_all_days`, `vol_votantes`):
  la frontera de confianza los sella sin recomputar de fuente, así que un bug DETERMINISTA en
  `symbol_vols` los falsearía. Defensa: una implementación de REFERENCIA independiente
  (`eco_ref_crudos.py`, sin importar symbol_vols/_day_grid/trailing_vol/session/_stats — reimplementa
  rejilla, anclaje 25s, vol trailing I2, sesión CME, elegibilidad 200/20/500, tercil P66,7 estricto,
  dispersión) corre sobre EL MISMO payload (una descarga, `descargar_payload`) y el prep BLOQUEA si
  |principal−referencia| > `TOL_DIFERENCIAL=1e-9` (calibrada con datos gastados: |diff| real = 0,000e+00
  ⟨`bampliada_calib_run{1,2}.log`⟩). El prep sella ambos pares, sus diffs, la tol, las listas y los
  SHA de las dos impl. **PIN REAL a F (corrección de auditoría — el SHA del objeto de F contra sí
  mismo era tautológico):** la lectura exige que las dos impl en el árbol de P sean BYTE-IDÉNTICAS a
  las de F, atando el código ejecutado a la versión congelada; una impl debilitada post-freeze muere
  ahí. LÍMITE DECLARADO (refuerzo 10): el differential cierra el bug de IMPLEMENTACIÓN, NO el de
  ESPECIFICACIÓN (modo común — dos impl que codifican la misma definición ambigua coinciden en el valor
  equivocado); la corrección de la DEFINICIÓN la audita la mesa (T6), aparte.
- **M-08 — cierre de procedencia/finitud/determinismo/spec** (lote final):
  1. **Pineado de TODA la maquinaria load-bearing** (M-08.1): el pin abarca los DOS crudos Y sus
     dependencias que tocan payload/vol/sesión (`lighter_adapter`, `confirm_runner`, `eco_fase2_wti`,
     `lighter_maker_capa1`) — una deriva en `lighter_trades_ms` (el payload que AMBAS impl consumen)
     engañaría al differential; la lectura exige árbol_P==árbol_F de la lista COMPLETA. El prep/productor
     rehúsan si algún módulo del working tree ≠ F (`git diff --quiet F -- <módulo>`), cerrando el vector
     runtime (modificar sin commitear). NOTA: el «HEAD==F» literal del encargo es incompatible con la
     cadena F→A_F→P (A_F es posterior a F); se enforce la propiedad equivalente-y-más-fuerte
     «módulos del working tree == F», por módulo.
  2. **Finitud** (M-08.2): NaN/Inf en cualquier crudo, diff o tol → BLOQUEA (un `NaN>tol`=False no
     puede colarse); estrato agitado vacío → raise (no NaN silencioso); `allow_nan=False` en todo
     `json.dumps` de artefactos.
  3. **Doble corrida** (M-08.3): el prep se computa DOS veces y se exige forma canónica idéntica
     (excluyendo `fecha`) antes de escribir; determinismo probado en la línea, no confiado; la
     calibración fail-loud (`sys.exit(1)`).
  4. **Spec en AMBAS impl** (M-08.4): precio ≤0/no-finito en CUALQUIER extremo del retorno (inicial u
     objetivo) invalida ESE punto (se descarta y se CUENTA `n_precio_invalido`), no el día; ts NO
     DECRECIENTE exigido (empates del mismo-ms legítimos); calendario CME congelado hasta 2026-09-30
     (`CALENDARIO_PINEADO_HASTA`) con Labor Day 09-07 en ambas impl, y D1 más allá → fail-closed.
- **M-09 — cierre de la cadena de PROCEDENCIA (capa decisoria + productor)** (`a77d6ff`→`118e877`):
  1. **Listas CERRADAS del grafo de llamadas** (no del import transitivo) — `CIERRE_DECISORIO` (10) =
     los 6 módulos de crudo + `eco_gate_b` (**la guardia se pinea a SÍ MISMA**) + `screen` + `t_tabla`
     + `hl_maker_capa1`; `CIERRE_PRODUCTOR` (10) = `eco_runner_wti` + `wallet_atlas` + `pilot_observer`
     + `lighter_adapter` + `confirm_runner` + `eco_fase2_wti` + `lighter_maker_capa1` + `hl_maker_capa1`
     + `maker_capa2_runner` + `eco_gate_b`. El pin sha(P)==sha(F) y el `git diff --quiet F` recorren
     TODA la lista.
  2. **`leer_a2` INVOCA el worktree-check** antes de gastar (antes lo declaraba pero no lo llamaba
     —«gastaba la bala con código no congelado»—); prep y productor, igual. Contadores
     `n_precio_invalido`/`n_trailing_invalido` comparados por el differential (población distinta con
     el mismo escalar NO puede pasar).
  - **M-09.1** (`118e877`) — recompute OBLIGATORIO de TODOS los pines bajo la receta M-09.2 (mi
    «no afecta r\*/rango» del reporte M-09 fue una AFIRMACIÓN no reproducida — el fallo «lo reportado
    ≠ lo verificado» que Code existe para cazar; corregido). Resultado ×2 byte-idéntico
    (`ancla_M091`, `rstar79_M091`): **r\* EXACTO** (79-npz LIT-decisivo `n_trailing_invalido=0` ⇒
    13,0/25,252144957533773 = 0,514808 raw a raw); **E-pin 5,90 aguanta** (raws movidos:
    prim 6,462905990101446→6,464983296090528, rob 5,906436318341285→5,908334763956463);
    **E_low 2,61 intacto** (los 23 inválidos son TODOS del 06-15 = 2ª década; la 3ª —ratio 0,201, que
    fija E_low— intacta); **rango [7,22, 17,74]→[7,22, 17,76]** (2ª década) — ratificado por doble mesa.
- **`freeze_pins.json` = `{r_star, rango_calibrado, params_productor}`** EXACTO (esquema
  `_CLAVES_PINS`): `r_star = 0.5148077528408752` (**raw, precisión completa** — es multiplicador del
  listón, R12); `rango_calibrado = [7.22, 17.76]` (**redondeado 2 dp** — es banda de comparación
  operativa, §1); `params_productor == PARAMS_PRODUCTOR` del runner @ `91201f5`:
  deltas_ms=[5000, 25000], min_snaps=300, min_span_h=20.0, session=CME-exacto, vol=I2,
  tercil=n/a(productor). Sellado en el árbol de F (force-add: `data_hist` está en `.gitignore`).
- **Regla R11 + protocolo M-nn**: pins de la mesa POR ESCRITO; el árbol lo toca CODE; otra mano se
  anuncia ANTES del commit; cero commits en ventanas de auditoría; acuse por número de mensaje.
- **Incidentes del proceso de B (esquema cronológico RESUELTO por la mesa, M-03-re4):**
  · **Incidente nº1** — custodia «ediciones externas» (ciclo `463ed91`→`4d23225`): no fueron de la
    mesa (cero bytes suyos en el repo en su sesión); origen lado-propietario; regla de custodia R11
    al acta ⟨acta l.427⟩.
  · **Incidente nº2** — tests borrados sin relevo a Code; narrativa reconciliada: el asesor anunció a
    Manuel, Manuel ordenó revertir, a Code no se le relevó — fallo de PROTOCOLO DE RELEVO, fix R11
    ⟨acta l.460, sello `b772ca2`⟩.
  · **Incidente nº3** — P0, exposición pre-elección-de-ventana — §8 ⟨sellos `894ee90`, `2c3bdd3`⟩.
  · **Pérdidas de relevo = CUATRO** (M-01, M-03, M-03-re2, M-03-re3 — cada una citada como entregada
    y no relevada a Code; re4 es la primera de la serie que llegó): constancias en acta (M-02, M-04,
    M-05, M-06). Cualquier «cinco» en el corpus es errata de conteo → CUATRO.
- **Cadena de maquinaria (commits):** bifásica+locks `e9a5ead`→`0749669`; productor/atestación
  `30e6069`→`2e62d38`; M-02 `e98b55e`; M-04 `8ffd7c2`; M-05 `0e79710`; M-06 `a1b5792`+sellos
  `732d018`; M-07 `91201f5` (CI 29190658883); B-ampliada `22ac9ef`; M-08 (lote de cierre: pin
  6 módulos load-bearing + finitud + doble-corrida + spec); M-09 `a77d6ff`→`118e877` (procedencia +
  recompute M-09.1). Suite tras M-09.1: **446 verde**.

## §10 — DAY-SET DEL GATE Y FIRMA

**Calibración (79-npz del decisivo, tupla CONGELADA en código — `DIAS_79_NPZ`, `eco_e_anchor.py`
l.49-64 @ `91201f5`; el glob solo VERIFICA, fail-closed):**
2026-03-06 · 03-07 · 03-08 · 03-09 · 03-10 · 03-11 · 03-21 · 03-22 · 03-23 · 03-24 · 03-26 · 03-27 ·
03-28 · 03-29 · 03-30 · 03-31 · 04-01 · 04-02 · 04-03 · 04-04 · 04-05 · 04-06 · 04-08 · 04-09 ·
04-10 · 04-11 · 04-12 · 04-13 · 04-14 · 04-15 · 04-16 · 04-17 · 04-18 · 04-19 · 04-20 · 04-21 ·
04-23 · 04-24 · 04-25 · 04-26 · 04-27 · 04-28 · 04-29 · 04-30 · 05-01 · 05-02 · 05-03 · 05-04 ·
05-05 · 05-06 · 05-08 · 05-09 · 05-10 · 05-11 · 05-12 · 05-13 · 05-14 · 05-15 · 05-16 · 05-17 ·
05-18 · 05-20 · 05-22 · 05-23 · 05-28 · 05-29 · 06-03 · 06-11 · 06-14 · 06-15 · 06-18 · 06-19 ·
06-20 · 06-21 · 06-22 · 06-26 · 06-27 · 06-28 · 06-29 (79 días).

**Conjunto de replicación:** LIT ≥ 2026-06-30, cap 2026-09-30 (G1/G4). Day-set del disparo: se lista
al alcanzar N_min (G11 — toda ausencia posterior, fail-loud).

**CAVEAT DE FIRMA — DEBILIDAD DE DISEÑO (no de implementación), que el propietario firma SABIÉNDOLA,
no descubriéndola después (auditoría de la mesa sobre (y)).** El SESOI escala-libre (G7) descansa en
"edge ∝ vol25 con r\* UNIVERSAL entre regímenes". Pero la sonda del propio ancla muestra el ratio
vol25_agit_WTI / vol25_agit_LIT variando **~3,8×** entre sub-ventanas (de ~0,20 a ~0,71 según década
⟨`ancla_M091`; décadas WTI 16,87/17,76/7,22 sobre LIT 29,59/24,86/35,84⟩) → régimen **INESTABLE**
(G10). `bar = r*·vol25_agit_WTI(ventana de lectura)` AMORTIGUA la parte del cambio que es de nivel de
vol; PERO si **r\* mismo no transfiere** entre regímenes (si la razón edge/vol no es constante), el
listón calibrado sobre el decisivo puede no valer en la ventana prospectiva de A2. Mitigaciones ya en
el diseño: rango calibrado G7 (fuera de [7,22, 17,76] → INCONCLUSO-RÉGIMEN, sin leer) y el cualificador
G10 sobre toda lectura en bps. Residual DECLARADO: dentro del rango, la transferencia de r\* es un
supuesto, no un hecho medido — es la debilidad de diseño de A2, y la firma la asume.

**FIRMA (regla no circular, M-03-re4; cronología CORREGIDA por la 2ª mesa, M-09).** La firma del
propietario = línea «FIRMO» + fecha + **SHA-256 sobre los bytes canónicos de este fichero** — los
bytes LF tal como viven en el árbol del **commit de ENSAMBLADO AUDITADO** (`git show
<ensamblado>:docs/PREREG_B.md`).

**El commit de ensamblado NO es F.** F es el commit SIGUIENTE que **registra la firma consciente del
propietario** — la línea «FIRMO» + hash en un **artefacto de firma SEPARADO** (no en este fichero;
sin tocar el prereg, los pins ni el código), distinto de `atestacion_freeze.json` (= A_F, que es
posterior a R_F). Con esto: (a) el prereg firmado es **byte-idéntico en el ensamblado y en F** (F no
lo toca); (b) el documento **no contiene su propio hash** (lo porta el artefacto de firma, detached);
y (c) **R_F = CI(F) y D0 quedan por construcción DESPUÉS de la decisión de firmar** — nunca antes.

Secuencia INEQUÍVOCA (sin circularidad):

  ensamblado auditado → auditoría única y entera de la mesa → STOP levantado →
  **el propietario firma `hash(bytes canónicos del ensamblado)`** → el commit que registra esa firma
  es **F** → **R_F** = CI(F) → **A_F** = `atestacion_freeze.json` (atestación de R_F) →
  **D0** = primera sesión posterior al timestamp de R_F en el **servidor** (ancla de D0 en `leer_a2`).

**Ninguna A2 puede preceder a la firma:** D0 se deriva de R_F, R_F es la CI de F, y F es el commit de
la firma. El commit de ensamblado tiene su propia CI verde, pero esa CI es **solo evidencia de que el
paquete compila antes de firmar — NO es R_F** (no ancla ninguna ventana).

**Estado: ENSAMBLADO AUDITADO con cronología ya corregida — NO congelado. Pendiente de la pasada final
de la mesa (que esta corrección no tocó ningún número) y de la firma. El STOP sigue en pie.**
