<!-- PROCEDENCIA. Producido el 2026-08-24 corriendo la checklist adversarial CONGELADA
     `.claude/agents/quant-reviewer.md` (commit a25741e, 2026-06-13 10:28) sobre el hallazgo de LIT
     (commit 74f0d606, 2026-07-05 19:04): 22 dias de ventaja. La checklist se corrio VERBATIM, sin
     reformular ni ampliar ningun punto — su autoridad viene enteramente de no haber sido tocada.
     Ocho puntos, un agente por punto, con refutacion adversarial de toda absolucion.
     NO RATIFICABLE. Code entrega auditable; la mesa ratifica. -->

# INFORME FINAL — quant-reviewer

**Objeto**: EDGE MAKER-LENTO EN LIT (+18,24 bps @25s, t +6,69, n_eff 79, ventana LIT 2026-03-06..2026-06-29, nace en `74f0d606` 2026-07-05 19:04).
**Checklist**: congelada en `5f5a74d`/`a25741e` (2026-06-12/13), 22-23 días antes de que el hallazgo existiera. Respondida tal cual, sin reformular.

---

## 1. Tabla: amenaza → veredicto + evidencia concreta

| # | Amenaza | Veredicto | Grav. | Evidencia mínima que lo sostiene |
|---|---|---|---|---|
| 1 | Pre-registro: ¿predicción y umbral fijados en el LEDGER ANTES? ¿se movió después? | **APLICA** | GRAVE | El umbral congelado (`9c8f4b1`, 11:31:59) nunca se editó —`git log --all -- docs/PREREG_CONFIRMACION_LIT.md` = 3 commits, último el freeze— pero **no se cumplió**: `LEDGER.md:1685` "INCONCLUSO por discrepancia de horizontes". Seis días después el umbral se re-fija sobre el ganador: "un horizonte (25s)" `PREREG_B_GATE.md:43` @`b772ca2` → `PREREG_B.md:116`, y N_min se dimensiona con `mu=+18,24` (`PREREG_B.md:46`). Esa elección estaba reservada: "se decide con mesa fresca…, JAMÁS retroactivamente" `PREREG_ECO_LIT_INSUMOS.md:92-93`. Sin firma (`0c50c24`: "NO firmado"). Además el bloque predicción+falsación nunca vivió en `LEDGER.md` antes: entra en `74f0d606`, el mismo commit que el resultado. |
| 2 | Look-ahead: ¿algún estadístico usa información posterior al instante que explica? | **APLICA** | **LETAL** | La regla de admisión a la cohorte lee el futuro: `confirm_runner.py:74-91` evalúa `th`/`at` sobre TODO `(t0,t1]` con `t1 > t_fill`; un evento es FILL sólo si ningún print atravesó `px` en el resto del intervalo — la dirección favorable del markout que luego se mide. Censura el **89,9%** (119.508 de 132.876 eventos lentos). Al deshacerla: **+18,24 (t+6,69) → −0,97 (t−0,27)**; con φ=0,20 ya muere (t+1,28). El 33,2% de los fills admitidos tiene cota de ventana consultada ≥25 s (más allá del horizonte completo). Firma aritmética: lado ask P(markout<0)=0,075. La casa lo nombró (I5, `PREREG_ECO_LIT_INSUMOS.md:54-61`) y declaró la sensibilidad **obligatoria y pendiente**; el acta la marca `INVIERTE=False` (`LEDGER.md:1763`), lo cual es falso. |
| 3 | Survivorship: ¿universo/ventana excluye muertos, deslistados o periodos incómodos? | **APLICA** | GRAVE | 79 de 116 días (68%). Missingness no aleatoria en el eje que gobierna la hipótesis: excluidos 2.570 tr/h vs retenidos 1.126 tr/h, Mann-Whitney z=+3,96, P(exc>inc)=0,80; 9 de los 20 días más intensos excluidos y 3 más se los llevó el piloto por regla (`PREREG_CONFIRMACION_LIT.md:23,86`). Universo de símbolos fijado por actividad de **un solo día a mitad de ventana** (`lighter_maker_capa1.py:23,35,66`; 221→163→16→8). Contra-evidencia real: Spearman(intensidad, markout)=+0,211; por cuartil 23,40/15,40/14,64/19,32 — el sesgo no se materializa en el eje medible. Daño a la INFERENCIA ("sobrevive en el tercil agitado" se probó sin los días más agitados), no al número. |
| 4 | Data snooping: ¿cuántas variantes antes de esta? ¿el LEDGER las registra todas? | **APLICA** | GRAVE | Nivel universo: sí (≈20 etapas con id en `LEDGER.md`). Nivel especificación: **no existe**. El "log inmutable de ensayos §3.5" que `LEDGER.md:7` invoca no está en el repo (`git ls-files` → un único log de corrida); `git grep -n intentos -- docs/LEDGER.md` = 0 hits; `overfit.py` (DSR/PBO) jamás se invoca sobre el Cap 2. Variante no contabilizada: el criterio de identidad ρ_1m≥0,95 tumbó a LIT (0,930) y se sustituyó por ρ_5m (LIT 0,9826 → certificada) en el acto de firma (`PREREG_MAKER_LIGHTER.md:187-207` @`946504b`). Desviación prereg-vs-código: la familia BHY declarada incluye §5, el código sólo mete las 12 celdas de tercil (`confirm_screen.py:136-137` vs `PREREG_CONFIRMACION_LIT.md:77-78`) — y §5 es donde vivió la errata H1. Defensa verificada: p=1,12e-11 pasa BHY con m hasta 10⁵-10⁶; la multiplicidad **no** explica el número. |
| 5 | Fugas train-test: ¿la conclusión se "verificó" sobre los mismos datos que la sugirieron? | **APLICA** | GRAVE | La disyunción de días es real y verificada (`confirm_runner.py:30-33`, `capa2 − pilot`; LIT 88 = 9 + 79, intersección vacía). Pero la CONCLUSIÓN no la emitió la regla congelada: `screen_output.txt:19` "VEREDICTO §3: INCONCLUSO". Los "tres diagnósticos a favor" (§3/§4/§5) salen de **una sola corrida** sobre el mismo P. La muestra gastada se re-leyó ≥3 veces (A11, I2, recompute_s5) hasta cambiarle el alcance ("DOGE 25s NULO; el 'ambos símbolos' era artefacto"). Y todo el aparato de verificación futura está calibrado sobre ella: σ=28,12 y N_min=17 con μ=+18,24 (`PREREG_B.md:45-49`), r*=0,514808 con day-set = los 79 npz (`:73`), E_LIT=13 ≈ 0,71× la flor (`ECO_CONTEO_FASE0.md:328-329`). Los npz de capa 2 de los extremos del "held-out" se escribieron 19 h antes del freeze y se leyeron pooled (`bca9ab4`), luego "ningún markout de la ventana nueva existe antes del freeze" es falso tal como está escrito. |
| 6 | **n efectivo** (autocorrelación, un solo símbolo, un solo régimen) | **APLICA** | **LETAL** *(regla fija)* | Eje autocorrelación: **no muerde** — ρ₁..ρ₇ ≈ 0, n_eff=79=N honesto (`screen.py:11-28`); clúster por owner t=+11,69; bootstrap por semana IC95 [+14,40,+23,66]. Eje símbolo: **muerde** — DOGE, el "segundo símbolo OBLIGATORIO" (`PREREG_CONFIRMACION_LIT.md:20-22`), da +0,17 / t+0,00 con sd_día 728,55 ⇒ MDE≈+267 bps, **~15× infra-potenciado**: no corrobora ni puede falsar, y satisface *vacuamente* la cláusula `not any(agit_neg(...))`. Con estimador robusto sí contradice (mediana +1,92 IC95 [−0,05,+3,89] vs LIT +15,46; signo diario 66,1% vs 98,7%). Eje régimen: los tres terciles cobran (+13,99/+9,21/+18,24) ⇒ cero variación independiente. **n=1 símbolo y 116 días < 1 año: ambas condiciones de la regla fija se cumplen.** |
| 7 | Historia post-hoc | **APLICA** | GRAVE | Diseño, celdas y reglas de veredicto sí congelados (`946504b`, `9c8f4b1`, `98e81de`), y el patrón ganador estaba pre-nombrado con autoridad DENEGADA ("rojo a 1s, verde a 25s ⇔ INCONCLUSO", `PREREG_MAKER_LIGHTER.md:100-105`) — y se honró. Pero el MECANISMO ("la capacidad de cancelar es la estructura entera") entra en `LEDGER.md:1588-1592` @`17fa8e9` **4 min 48 s después** del número (`62a7f1f` 10:39:17 → 10:44:05), invierte el racional pre-registrado ("toxicidad condicional a ser lento", `LEDGER.md:1548-1552`), se rotula "lo que el diseño CLAVÓ" y licencia la robustez ("la estructura sobrevive a la muestra pequeña"). El Cap 2 entero no contiene una sola ocurrencia de `falsaci*` ni Plantilla C1, a diferencia de H3 y H8. Y el mecanismo no predice el patrón: si es esquivar selección adversa, debería morder a 1-5 s, donde no hay nada (+2,61 t+0,29). |
| 8 | Cofundación: ¿qué variable omitida explicaría lo mismo? | **APLICA** | **LETAL** | El estimador es un NIVEL contra el precio de la propia orden, no un cambio de la referencia: `mo = lado·(ref_px − px_fill)/px_fill` (`pilot_observer.py:122`, `PREREG_MAKER_LIGHTER.md:81`) ⇒ E[markout] = E[distancia orden→ref] + E[deriva]. Control de velocidad nunca computado (`~slow` no aparece en `confirm_screen.py`, pese a estar autorizado en `PREREG_CONFIRMACION_LIT.md:77,80`): **RÁPIDA +11,78 t+8,48 n=18.727** — el 65% del titular, con t mayor y 4× masa. Por lado: bid +3,54 (t+1,68, n.s.) vs ask +25,93 (t+7,08); el término direccional es universal, aparece igual en los through (+14..+16) y la cohorte lenta es 64% asks vs 50,8%. Reconstrucción: 14,73 + 11,19 sobre mezcla 36/64 = **+17,86 vs +18,24 publicado**. Residuo lado-neutral **+2,92 bps, t=+1,30, no significativo**; a 5s, −3,14 (t−0,43). La casa nombró la mitad y la dejó abierta (`CARTA_DE_ATAQUE.md:83-85`, A5). |

**8/8 APLICA. Ninguna INDETERMINADO. Tres LETAL (2, 6, 8), cinco GRAVE.**
Nota: dentro del punto 3, la sub-pregunta "muertos/deslistados" queda **INDETERMINADA dentro de un APLICA**: sólo se estableció la mecánica del sesgo, no su magnitud (haría falta el histórico diario del universo, con STOP de producción vigente).

---

## 2. Reproducción: ¿salen los mismos números?

**Sí — el número publicado es reproducible dígito a dígito, y eso es precisamente lo que agrava el informe.**

| Comprobación | Resultado |
|---|---|
| Baseline titular desde los 79 npz LIT (`confirm_screen.py:96-140`) | 25s AGITADO **mean=+18,24 · t=+6,69 · n_eff=79,0 · k=79 · fills=4.413** — exacto. Reproducido de forma independiente por tres auditores (puntos 2, 3, 6). |
| Las otras 5 celdas de LIT | 5s tranq +13,99/+1,91 · 5s medio −0,48/−0,09 · 5s AGIT +2,61/+0,29 · 25s tranq +13,99/+2,12 · 25s medio +9,21/+17,46 — todas idénticas al `screen_output.txt` de `74f0d606`. |
| n_eff | ρ₁..ρ₇ = −0,069/+0,001/+0,003/+0,027/−0,034/+0,032/−0,008 ⇒ factor de deflación **1,000 (NO-OP honesto)**: no hay autocorrelación diaria que descontar. |
| Variantes de receta ya commiteadas (`docs/runs/gate_sigma79_5daff8b.log:164-169`) | v1-flor +18,24/t+6,69 · I2-flor +18,04/t+6,55 · v1-gate +19,71/t+5,67 · I2-gate +20,35/t+5,47. El número no vive en el filo del clasificador. |
| Terciles causales (expansivos) en vez de POOLED | +17,84 / t+7,24 / n_eff 77 — **ese vector de look-ahead queda refutado**. |
| Estratificador y cohorte | `trailing_vol` estrictamente pre-fill; `slow = oid in prev_seen` actualizado al cierre del bucle — **limpios**. |
| Deshacer la censura through (punto 2) | **+18,24 → −0,97 (t−0,27)**; φ=0,20 ⇒ t+1,28. |
| Residuo lado-neutral LENTA−RÁPIDA (punto 8) | **+2,92 bps, t=+1,30** (77 días). A 5s: −3,14 (t−0,43). |
| DOGE, misma celda | +0,17 / t+0,00 / sd_día 728,55 ⇒ MDE ≈ +267 bps. |

**Conclusión de reproducción**: la aritmética de la casa es correcta y su código implementa el prereg literalmente. Lo que no sobrevive no es el cálculo: es **el estimando**. El +18,24 es un nivel medido sobre una población seleccionada por el futuro, sin contrafactual, sin neutralizar lado, contra una referencia que sólo se certificó por co-movimiento (ρ_5m) y es ciega a un desplazamiento de nivel de +11..+16 bps.

Dos limitaciones de reproducción declaradas: (i) la prueba exacta de I5 (`through-con-at` re-contado como FILL) **no es ejecutable** sobre los npz decisivos —el flag `thr_con_at` no existe en ellos, se añadió en I2/I5 el 2026-07-10—, así que la re-admisión total es una **cota superior**, no la corrección; la verdad está entre +18,24 y ≈0 y la curva φ es la lectura honesta. (ii) Nadie recomputó desde crudos (snapshots 0xA + trades): un sesgo aguas arriba en la inferencia de fills sería común a los 79 días y a los 487 wallets e invisible aquí.

**Regla cero**: los ocho puntos declaran no haber pedido, computado, impreso ni citado ningún primer momento de markout sobre {WTI × ≥2026-06-05} ∪ {LIT × ≥2026-06-30}. Se registra **un incidente declarado por el propio auditor del punto 4**: apertura de `lighter_pilot/screen_output.txt` (`62a7f1f`), que arrastra markouts de WTI de días protegidos según el incidente nº3 (`894ee90`); no se citó ni reprodujo ninguna cifra de WTI y no se reabrió. Se registra también una **desviación de la regla 2** declarada por el auditor del punto 1: dos `git diff` commit-a-commit con ruta explícita; ninguna conclusión depende de ellos y no quedó lock.

---

## 3. Veredicto

# DESTRUIDO

**Razón dominante, en una frase**: la regla que decide qué fills entran en la cohorte lee los prints posteriores a `t_fill` en la dirección exacta del markout que después mide —censurando el 89,9% de la masa— y al deshacerla el +18,24 (t+6,69) cae a −0,97 (t−0,27), mientras que, aun aceptando la censura, el nivel no es de la clase paciente (control rápido +11,78 con t mayor) y el residuo lado-neutral es +2,92 bps t+1,30: el número mide un nivel de libro confundido, no un edge.

**Por qué DESTRUIDO y no TOCADO** (Cap 1 salió TOCADO y el programa siguió; TOCADO no es guillotina, pero aquí no aplica):

- **Lo que degrada el ESTATUS** (hallazgo → hipótesis) y por sí solo daría TOCADO: puntos 1, 3, 4, 5, 6, 7. La regla fija del punto 6 —"conclusión con n=1 símbolo o 1 año = hipótesis, JAMÁS hallazgo"— se dispara mecánicamente: LIT es un símbolo, DOGE está ~15× infra-potenciado y no corrobora, la ventana son 116 días. Consecuencia escrita de antemano, no negociable: **el objeto no puede llamarse hallazgo**. El propio prereg congelado ya lo había dicho: "sin el segundo, el veredicto se llamaría 'LIT', no 'maker lento' — anécdota, no hallazgo".
- **Lo que DESTRUYE** (el número está mal, no sólo mal etiquetado): puntos 2 y 8, y son independientes entre sí. El punto 2 muestra que la población está seleccionada sobre un correlato del outcome; el punto 8 muestra que, incluso dentro de esa población, el nivel no es específico de la cohorte que la hipótesis nombra y se reconstruye aritméticamente (+17,86 vs +18,24) con dos variables omitidas. Cualquiera de los dos basta; los dos juntos no dejan estimando en pie.
- **La distinción importa y se respeta**: nada de esto dice que la casa calculara mal. La aritmética reproduce exacta. Lo destruido es la interpretación causal del número, que es lo que se estaba reclamando.

**Prefiero un falso DESTRUIDO a un falso SOSTENIDO** y aquí ni siquiera hace falta ese margen: el vector letal es medible con el dato ya gastado, se midió, e invierte el signo.

---

## 4. Qué haría falta EXACTAMENTE para levantar cada amenaza

| # | Levantamiento exacto (una línea) |
|---|---|
| 1 | Que la mesa fresca firme —según §10— la elección 25s-céntrica *o* la revierta al decreto 5s-céntrico, y que el gate se re-dimensione con σ y N_min de una fuente distinta de los 79 npz. |
| 2 | Re-diferenciar los 79 días desde los snapshots 0xA persistiendo `thr_con_at`, ejecutar la sensibilidad I5 declarada obligatoria, y mostrar que la celda se mantiene positiva-significativa con los through-con-at re-contados como FILL. |
| 3 | Recuperar los 17 días de cobertura parcial con archivo completo (o acotar su markout por otra vía) y demostrar que la celda AGITADO conserva signo y significación cuando los días más intensos del venue vuelven a la muestra. |
| 4 | Materializar el log inmutable de ensayos §3.5 con recuento de intentos a nivel de especificación, y correr DSR/PBO sobre el Cap 2 con ese `n_trials` — más re-medir la celda contra el carril de prints propios del venue (A5), que decide si la sustitución ρ_1m→ρ_5m fue material. |
| 5 | Un test genuinamente forward sobre una ventana posterior no expuesta, con σ, N_min, E y r* calibrados **sin** los 79 días, y con el instrumento (clasificador de vol) fijado antes de ver el descubrimiento. |
| 6 | Un segundo símbolo con potencia suficiente para detectar +18 bps (sd_día compatible con MDE ≤ +18, no +267) **y** una época independiente: sin ambos, la regla fija sigue disparando y el estatus máximo alcanzable es *hipótesis*. |
| 7 | Congelar un criterio de falsación del mecanismo "capacidad de cancelar" —con umbral y muerte esperada, Plantilla C1— antes de la siguiente lectura, y ejecutar el test ya nombrado: markout condicional a la desviación de basis en el instante del fill. |
| 8 | Publicar la celda de control `~slow`, la descomposición bid/ask y el residuo lado-neutral como salida estándar del screen, y medir el markout contra la referencia **en t_fill** (no contra `px_fill`) para separar nivel de libro/basis de efecto de cohorte; el hallazgo sólo revive si ese residuo es positivo-significativo. |

**Observación final, no negociable con el resto**: el gate B tal como está congelado (`PREREG_B.md:34-46`) hereda la receta íntegra —`dec=(tipo≤1)&slow`, sin control de cohorte, sin neutralizar lado, sin control de basis— y está dimensionado sobre μ=+18,24. Está, por construcción, **potenciado para volver a detectar el número confundido**. Ejercerlo sin arreglar los puntos 2 y 8 no verificaría nada: reproduciría el mismo artefacto en datos nuevos y lo llamaría réplica.