# VISIÓN — la percepción rectora del proyecto

**Estado:** BORRADOR para atacar a sangre fría (2026-06-16). No es contrato todavía:
es una tesis que debe sobrevivir a la crítica ANTES de promoverla a norte del
proyecto (cambio del Plan, aprobado por el usuario). Escrita para ser destruida.

> **ACTUALIZACIÓN 2026-07-01 — META-CONCLUSIÓN: la tesis rectora, en ESTE universo, queda falsada. El norte
> se re-apunta.** Seis frentes cribados con rigor (trío de primas SCREEN-NEGATIVE; cross-venue archivado;
> **contrarian OFI SCREEN-NEGATIVE**, t=−26, held-out gastado; **H3 INCONCLUSO-POR-MASA**; **lead-lag NULL**;
> **H6 listing sin régimen fuerte** — el libro tiene MM desde el minuto 1). Veredicto agregado: **estos perps
> maduros de Binance y sus listings NO ofrecen edge direccional ni de provisión a un jugador LENTO con infra
> retail en 2025-2026** — la competencia cerró la ineficiencia. Pista dura del contrarian: el flujo es
> INFORMADO → el edge, si existe aquí, está del lado MAKER/selección-adversa, que exige baja latencia que NO
> tenemos. **Esto NO es fracaso** — es el activo que el propio documento prometió: conocimiento negativo
> mapeado + maquinaria validada (3,5×, 6 tesis cribadas gastando held-out en UNA). **El laboratorio no se
> cierra: la pregunta pasa de "¿qué mecanismo en estos 8 perps?" a "¿a qué UNIVERSO/INSTRUMENTO apunta la
> máquina donde la ineficiencia siga abierta?"** Detalle completo: META-CONCLUSIÓN en `LEDGER.md`.

> **ACTUALIZACIÓN 2026-06-19 — la muerte nº1 ha disparado (a nivel de trade).** El
> sub-test de feasibility pre-registrado (LEDGER H5, commit `1271d40`) midió sobre
> 12 meses / 320M trades si queda estructura cross-sectional TRAS neutralizar el
> factor común. Resultado: **NO** (D=−0.026, dentro del ruido; |ρ| medio 0.006;
> inestable entre mitades). Es exactamente el criterio de muerte nº1 de abajo,
> materializado — al horizonte de trade de ~14 min, la estructura cross-sectional
> es **beta de BTC**. La tesis NO se borra (honra el "escrita para ser destruida" y
> el principio del cajón): queda **rebajada y en pausa**. Salvedad pre-declarada: el
> proxy es trade-level; H5 de verdad es liquidez/L2 a 100 ms (no testeado aún), así
> que el prior baja mucho pero no es cero. **Pivote en marcha:** del cross-sectional
> caro a la **liquidez/toxicidad single-name** (H1, H3, reencuadre del objetivo) —
> ver LEDGER. Esto es la máquina funcionando: el "no" barato y temprano que el
> propio documento dijo que respetaríamos.

> **ACTUALIZACIÓN 2026-06-22 — el RUMBO se firma: de "predecir el mercado" a
> "hacer lo que el mercado no quiere hacer".** Tras 3 rondas de revisor hostil
> (Perplexity) + co-diseño, el sueño operativo se concreta y se CONGELA antes del
> dato (misma disciplina). Se **renuncia explícitamente** al edge de predicción
> direccional HFT-style (base rate ≈ 0 para un jugador pequeño en mercados casi
> eficientes) y se firma un **TRÍO DE PRIMAS DE SERVICIO** estructurales (no
> informativas):
>   1. **Provisión selectiva en SOLEDAD BENIGNA** (no toda soledad): el hallazgo de
>      H8 no es solo un riesgo — es un NICHO. En soledad el spread es anchísimo; el
>      edge está en distinguir benigna (libro vacío por desinterés, flujo inofensivo
>      → proveer) de tóxica (makers listos huyeron antes del shock → retirarse).
>      Tesis ofensiva, falsable YA con la IO de H8: clasificar episodios de soledad
>      por markout forward; si no hay partición clara, el nicho muere.
>   2. **Funding carry con H3 de OVERLAY de riesgo de cola.** El funding es una prima
>      por vender seguro de cola en el perp; H3 (cascadas) es el detector de esa cola
>      materializándose. H3 deja de ser hipótesis suelta y pasa a módulo de risk
>      management del carry (útil aunque quede "inconcluso" como edge puro).
>   3. **Ejecución óptima como HABILITADOR (el ganador silencioso):** mejor base rate
>      (1-2 bps vs VWAP naif en libros finos es plausible), cero techo de capacidad,
>      y hace viables las otras dos (sin ella, carry y spread se van en slippage).
>      Objetivo cuantitativo: reducir el coste medio de ejecución ≥X bps vs benchmark
>      con OFI + régimen cross-shock.
>
> **Recast, no descarte:** nada se tira. **H1** (OFI/MLOFI) deja de ser señal de
> dirección y pasa a ser el MOTOR del clasificador de soledad (H8) y del timing de
> ejecución. **H3** → overlay del carry. **H8** → tesis ofensiva. Las piezas sueltas
> encajan en una arquitectura coherente de 3 primas.
>
> **Tardis acelera el plan (clave):** llega al cerrar la sonda → da meses de L2
> histórico DE GOLPE, así que el "modo exploratorio honesto" no necesita 3-6 meses de
> captura en vivo. Diseño OOS temporal DURO y congelado: **explora en Tardis-A →
> CONGELA pre-registro → testea en Tardis-B (held-out) + la sonda en vivo (que Tardis
> ni vio)**. PROHIBICIÓN FUERTE: nada ideado mirando B o la sonda cuenta como test
> honesto. (Detalle técnico: Tardis es L2 reconstruido de diffs, la sonda son
> snapshots → cuidar cadencia y libros bloqueados al combinar; ingeniería, no
> bloqueo.) **Día 14:** cierra sonda → llega Tardis → 1er experimento = H8 soledad
> benigna/tóxica; en paralelo, el módulo de ejecución; luego exploración honesta en
> Tardis-A. Esto es compatible con la base rate y con el porqué (jubilar a los padres,
> paso a paso) — y la máquina sigue avisando si ni el trío compensa.

---

## La tesis en una frase

> El cross-section de **8 perpetuos finos poco competidos**, observado por nosotros
> como **8 libros L2 simultáneos a 100 ms** y por casi nadie más, no son 8
> experimentos: son **un solo instrumento con estructura interna** (una red de
> liquidez). El proyecto deja de cazar UN edge grande y pasa a **industrializar la
> búsqueda de micro-edges decorrelacionados dentro de esa estructura**, con
> meta-labeling (AFML) para dimensionar, y cero autoengaño (Fases 3 y 5 del Plan).

## Por qué podría ser un paso real (no humo)

1. **Recombinación de recursos que son nuestros y de casi nadie más:** 8 libros L2
   simultáneos + el toolkit de López de Prado (barras information-driven,
   meta-labeling, CPCV/PBO/DSR) + transparencia on-chain de algunos nombres
   (ATOM/Cosmos, LINK, DOT). Nadie combina las tres cosas sobre ESTOS símbolos: a
   los HFT de élite no les compensa bajar aquí (Plan 1.1), al retail le falta infra.
2. **Geometría correcta:** un HFT ve cada nombre aislado y compite en microsegundos;
   nosotros vemos la cesta entera a 100 ms. Nuestra ventaja no es velocidad — es la
   **visión periférica** que ellos no se molestan en tener en nombres finos.
3. **Convergencia empírica, no casualidad:** la sonda histórica (ATOM 8× menos
   volumen, funding raro) y las hipótesis vivas (H2 funding, H3 cascadas, H4 CSD,
   H5 lead-lag) apuntan TODAS a la dinámica de liquidez de los nombres finos. Eso
   es señal de que ahí vive lo poco que pueda haber.

## El verdadero artefacto (lo honestamente nuevo)

El producto revolucionario de este proyecto **no será el alpha del bot** — eso lo
decide el mercado, no nosotros. Es la **máquina de descubrimiento**: una fábrica de
investigación autónoma y auto-auditada adversarialmente, operada por un par
humano+IA — pre-registro congelado en git, agentes que destruyen cada idea, un
LEDGER que acumula conocimiento NEGATIVO, el humano poniendo juicio/ambición y la IA
poniendo rigor incansable. Industrializar el método científico de LdP, en solitario,
sobre datos propios de un rincón ignorado, con esta disciplina, es genuinamente raro.

**Rol correcto de la IA en esta máquina:** no es oráculo (genera "ideas
revolucionarias" que suelen ser locura — 6 de 10 lo fueron). Es **ingeniero cuántico
+ escéptico**: implementa CPCV/embargo sin errores, pasa 10⁴ configuraciones por la
PBO sin cansarse, caza el look-ahead a las 3 a.m., sostiene los 8 nombres a la vez,
y dice "esto es beta disfrazada" cuando el humano se emociona.

## Cómo muere esta tesis (criterios de abandono, fijados ANTES)

Una visión sin condiciones de muerte es una religión. Esta se abandona si:
1. **Es solo beta de cripto:** si la estructura cross-sectional desaparece al
   neutralizar el factor común (BTC/mercado), no hay nada nuevo — hay beta. Primera
   prueba, bloqueante.
2. **Colapsa a carrera de latencia:** si los lead-lags de liquidez viven en <50 ms,
   los perdemos por diseño (Plan 5.2). Test ×10 obligatorio en cada edge.
3. **Sin masa estadística:** los eventos de liquidez son raros y agrupados; si tras
   meses el n efectivo no alcanza para la Fase 3, la tesis es inoperable aunque sea
   cierta (Plan 1.5).
4. **No supera el control anidado:** cada micro-edge cross-sectional debe aportar
   poder predictivo POR ENCIMA del mismo nombre en aislado. Si no, era autocorrelación
   ya conocida.

## Expectativa honesta

La probabilidad base sigue siendo que **NO haya edge accesible** para este perfil de
capital y latencia (Plan B.4). Esta visión no cambia esa probabilidad; solo apunta
el esfuerzo al lugar con más mecanismo y menos competencia. El éxito del proyecto se
mide por el rigor del proceso, no por validar esta tesis. La prueba final de que la
máquina es buena no es que gane: es que el día que diga "aquí no hay nada", le
creamos y pasemos a la siguiente cantera, sin arruinarnos ni mentirnos.

## Qué cambiaría en el Plan (si sobrevive a la crítica)

- Reencuadrar el universo §2 de "8 sondas" a "1 sistema cross-sectional".
- Añadir features cross-sectionales (estado de liquidez de la cesta, lead-lags,
  factor común) al laboratorio de Fase 2.
- Meta-labeling como capa estándar de dimensionado (Fase 7) sobre señales primarias
  crudas, en vez de buscar señales primarias perfectas.
- NADA de esto se implementa antes de los 14 días ni toca `ingestion/`.
