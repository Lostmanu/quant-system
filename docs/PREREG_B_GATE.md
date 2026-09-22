> **SUPERSEDIDO NORMATIVAMENTE POR `docs/PREREG_B.md`** (ensamblado (y), commit
> `9e8d56c5b782704ca5211637c3fe781c576103e9`; el hash de FREEZE sobre los bytes canónicos se registra
> en el commit notarial de la firma del propietario, patrón F→A_F). Este fichero queda INMUTABLE como
> fuente histórica del texto verbatim del gate: su §G0-G11 vive relleno y con las enmiendas Student en
> el §1 de PREREG_B.md. No editar (práctica del barrido OBSOLETO).

# §G DEL PREREG B — GATE DE REPLICACIÓN LIT (texto de la mesa, comiteado VERBATIM por Code)

[Marco de Code, ÚNICO texto propio de este fichero: lo que sigue tras la línea es el texto LITERAL de
la mesa — dictamen 2026-07-11 con las ENMIENDAS VERBATIM del encargo consolidado del mismo día
aplicadas: G4-bis nuevo, G5 sustituido, G7 ampliado, G8 corregido (R4), §V nuevo. Placeholders que se
sustituyen por valores sellados en la versión de FREEZE (únicas ediciones futuras autorizadas, con hash
propio): en G7, «⟨pendiente: corrida 79-npz⟩» → r* del retrofit (a) re-sellado, y «⟨log de (d)⟩» → el
log sellado de la sonda per-década en bps. Este fichero NO es el freeze: el prereg B completo se
congela con la firma del propietario.]

---

**G0 — Naturaleza.** Compuerta de LECTURA del held-out WTI de A2. Se congela con el prereg B; el hash del commit es la autoridad de fecha. Redactado por la mesa (2026-07-11); Code comitea sin editar.

**G1 — Conjunto.** Días LIT ≥ 2026-06-30 hasta la fecha de disparo (G4). Held-out de la replicación: ningún primer momento del markout se computa/imprime/guarda/cita antes de la lectura única (G6). Bloques generados con el pipeline pinneado al hash del freeze (post-I2/I6/I7, desempate estricto).

**G2 — Receta de celda.** La receta oficial de la flor (acta `7df45b9`) con dos excepciones pre-declaradas: `dec=(tipo≤1)&slow`; tercil POOLED sobre `vol20[dec]` finita **de la ventana de replicación**, clasificador I2-fijo, corte estricto `>q2`; suelo I7 ≥1s; markout 25s = `mo[:,1]` (referencia Binance); day-mean sobre markouts finitos; **día vota con ≥30 fills de celda**. Exclusiones admisibles: exactamente las del pipeline (ausencia CHD/0xA, <100 snaps, <30 fills-celda), registradas, jamás silenciosas.

**G3 — Estadístico único.** t = μ_dm/(σ_dm/√n_eff), n_eff = `effective_n_autocorr`; H0: μ≤0; unilateral; **α=0,05** (celda única, sin BHY).

**G4 — Masa y disparo.** **N_min = 15** day-means válidos (potencia 80% vs μ=+18,24, σ=28,12, factor=1,0 — sellado en `900d102`; riesgo residual si factor>1: declarado). Code reporta semanalmente **solo conteos**. Disparo al alcanzar 15. **Cap: 2026-09-30** — sin masa: INCONCLUSO-POR-MASA, nada se lee (ni gate ni WTI), y B se re-congela con mesa fresca.

**G4-bis — Preflight sign-blind.** "Alcanzado N≥15, el pipeline computa n_eff de la serie de day-means SIGN-BLIND (solo se emite n_eff; ningún primer momento expuesto al investigador). Si n_eff<15: no se lee; se acumula hasta el cap. En el cap con n_eff<15 → INCONCLUSO-POR-MASA, jamás NO-REPLICA."

**G5 — Veredicto mecánico, condicionado a n_eff≥15.** REPLICA ⇔ t≥1,645. NO-REPLICA ⇔ t<1,645. Sin N≥15 o sin n_eff≥15 → G4/G4-bis. Sin discreción post-hoc.

**G6 — Secuencia de lectura.** El gate se lee ANTES que el held-out WTI, en lectura única que gasta su conjunto. REPLICA → se procede a la lectura única de A2 conforme al prereg B. **NO-REPLICA → el held-out WTI NO se lee** (bala preservada); A2 se declara ILEGIBLE-POR-RÉGIMEN. Del gate, solo el binario REPLICA/NO-REPLICA cruza hacia A2.

**G7 — SESOI escala-libre de A2.** r* ≡ 13 / vol25_agit_LIT(**day-set = los 79 días-npz del decisivo**, 24/7, rejilla I2-fija) — valor sellado por corrida ×2 antes del freeze ⟨pendiente: corrida 79-npz⟩; variante 105-cal (0,4748, `4d23225`) = sensibilidad, no decide. Listón de A2: μ_WTI(lectura) ≥ r* · vol25_agit_WTI(día-set = días que forman day-means en la lectura de B; sesión-activa; misma rejilla), computado y sellado ANTES de la lectura de A2. Variante todos-los-días = sensibilidad. Supuesto de transferencia DECLARADO: edge ∝ vol25 (linealidad). Rango calibrado: si vol25_agit_WTI(ventana de lectura) ∉ [min, max] de las tres décadas de la sonda (niveles en bps sellados en ⟨log de (d)⟩), el SESOI no se extrapola: la celda de A2 se declara INCONCLUSO-POR-RÉGIMEN-NO-CALIBRADO. La inferencia del veredicto vive en §V.

**G8 — Compuerta de potencia (contexto, sellada).** E=5,90 ratificado + stress E_low=2,61 cruzado con σ_p90=1,08 → n_eff_req_stress_cons=1,51: PASA ~6,9× vs proyección conservadora. La compuerta no decide el veredicto; el SESOI es G7.

**G9 — Diagnósticos que NO deciden (post-lectura).** Receta legacy-v1 (continuidad con la flor); sensibilidad I5 (`thr_con_at` recontado como fill); denominador 105-cal; split por mitades temporales.

**G10 — Cualificador de régimen.** La sonda del ancla disparó INESTABLE (max/min 3,54 primario / 3,84 robustez; 3ª década 0,201). Motiva G7 y se declara como limitación de toda lectura en bps absolutos.

**G11 — Anti-forking.** Una ventana, una celda (lenta×agitado), un horizonte (25s), un estadístico. Nada se estratifica, re-corta ni re-ventanea post-hoc. El day-set del freeze se lista en el prereg; toda ausencia posterior, fail-loud.

**§V — Veredicto de A2.** "α=0,05 unilateral; n_eff = effective_n_autocorr; bar ≡ r*·vol25_agit_WTI (G7, sellado pre-lectura). GENERALIZA ⇔ LB90 ≡ μ̂−1,645·σ̂/√n_eff ≥ bar. NO-GENERALIZA ⇔ UB90 ≡ μ̂+1,645·σ̂/√n_eff < bar, con potencia constatada (n_eff ≥ n_eff_req_p90 sellado en el freeze). INCONCLUSO ⇔ resto (el IC cruza el bar, o potencia no constatada). Diagnósticos no decisorios: posición de μ̂ vs 0 (existencia sin escala) y lectura en bps absolutos, ambas con el cualificador INESTABLE."
