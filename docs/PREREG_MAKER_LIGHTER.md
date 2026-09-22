# PRE-REGISTRO — CAPA 2 MAKER EN LIGHTER (markout de maker simulado)

**Estado: CONGELADO — el hash del commit de este cambio es la AUTORIDAD DE FECHA del pre-registro.**

**ACTA DEL FREEZE (2026-07-04):** firma dada por el propietario ("firmo", tras lectura de §4 y §6).
Re-verificaciones ejecutadas EN el turno de la firma contra los criterios de cuadre pre-firmados:
1. *Fees:* docs oficiales de Lighter — cuentas Standard a **0/0 maker/taker en todos los mercados**
   (Premium 0,004%/0,028%, no aplicable). **CUADRA.**
2. *Season-3:* S1/S2 concluyeron con el TGE (2025-12-30); a fecha de las fuentes primarias más recientes
   disponibles, S3 solo teaseada, sin arranque anunciado → **ninguna temporada solapa mar-jun. CUADRA**
   (gatillo = solapamiento, no existencia).
3. *Límites Free (desde dentro de la cuenta, `/v1/account/usage`):* **50.000 créditos/mes, 15 req/s;
   usados 26, restantes 49.974** en 2026-07; L3 histórico en Free demostrado con recibos (capa 1b).
   **CUADRA** — el presupuesto de §3 (~500-600) cabe con margen ×80.

Historia del documento: v0 tras capa 1 PASA (`0a6b85d`) con los 5 insumos de la mesa + regla sellada
(`61fb4da`, `a9906a9`); v1 con la revisión completa de la mesa (2 severidad-máxima: simetría de
unanimidad y through-prints; 3 medianos; menores); v1.1 criterios de cuadre (`98e81de`). Conforme de la
mesa otorgado al diff v1. **Desde este commit, cambios = enmiendas fechadas; fortalecer pre-dato OK,
aflojar NO. Ningún markout existe antes de este hash.**

## 1. Hipótesis y mecanismo (perdedor con nombre)

Un maker pasivo join-the-touch en la **cola ancha** de Lighter captura half-spread ≥ 1 bp con fee 0 y
sobrevive a la selección adversa, porque el flujo del venue es **neutro** (medido: +0,05 bps, t+1,2,
instrumento calibrado `b4d156c`) — no hay alpha que te corra (el alpha no visita satélites). Pierde el
taker impaciente (retail/memes) y el cierra-gaps que paga el spread por inmediatez. Anti-arbitraje: los
majors están muertos en todo venue (ley de mapa: BTC 0,01 bps); la cola es capacidad pequeña que no
compensa a un MM institucional; sin cancel-priority, pero los ~300 ms del tier standard nivelan el campo
retail. **Riesgo nombrado que este screen mide:** los cierra-gaps invisibles a 25 s muerden a 1-5 s
(sniping de quotes rancias) — por eso la familia de horizontes tiene la misma autoridad.

## 2. Universo, ventana, exclusiones

- **Universo:** los 8 candidatos de capa 1 (regla congelada, sin re-selección): ARC (⚠ etiquetado:
  símbolo del squeeze de feb — se reporta por símbolo, NO se excluye), LIT, FARTCOIN, XPT, ZEC,
  BRENTOIL, DOGE, WTI.
- **Ventana:** limpia mar-jun 2026 (~120 días). Pre-filtro de COMPLETITUD por símbolo-día ANTES de
  cualquier oráculo/markout: día válido si trades-CHD presentes (24 h de archivo) Y snapshots-0xA ≥ 300
  filas. Días inválidos se excluyen CONTADOS (data-quality de runtime, como siempre).
- **Segmentación por sesión (insumo 3):** cada fill se ETIQUETA antes de mirar: `cripto-24/7` |
  `tradfi-abierto` | `tradfi-cerrado` | `reapertura` (primeras 2 h tras apertura SEMANAL **y también tras
  los cierres DIARIOS de CME** — etiquetar cuesta nada) para XPT/BRENTOIL/WTI. Reporte por segmento
  PRE-DECLARADO (diagnóstico); el endpoint primario usa todos.

## 3. Datos e instrumentos (todos ya validados/verificados)

- **Prints/fills:** trades CHD-`lighter` (canal VALIDADO contra basis Binance; ms).
- **Quotes/libro:** snapshots 0xA (`/v1/lighter/l3orderbook/{sym}/history`, cadencia ~2,9 min,
  `spread_bps` y `orders[]` por fila; cursor `meta.next_cursor`; coste ~0,5 créditos/símbolo-día).
- **Piloto L3-wallet (insumo 2):** mismo endpoint, campo `orders[]` (order-level con
  `owner_account_index`). **Presupuesto que SUMA (corrección de la mesa): panel = 8 símbolos × ~120 días
  × ~0,5 créditos ≈ 480; piloto = 3 × 10 × ~0,5 ≈ 15; margen de re-runs ⇒ ~500-600 créditos de 50.000
  (~1,2% del mes).** Guardia dura sin cambio: si el run real supera 5.000 créditos, se PARA y se
  re-presupuesta con el propietario.

## 4. Simulador de maker (cotas de cola)

En cada snapshot s del símbolo: el maker cotiza **join-the-touch en ambos lados** (px_bid = best bid,
px_ask = best ask del snapshot; **convención de signos: lado = +1 compra pasiva en el bid / −1 venta
pasiva en el ask**), tamaño infinitesimal (sin auto-impacto — aceptado a nivel screen, anotado). La quote
queda FIJA hasta el snapshot siguiente (staleness ~2,9 min = maker ~200× más lento que la clase viva →
regla asimétrica, §6). **Intervalo de cotización VÁLIDO solo si Δt(s→s+1) ≤ 2× la cadencia mediana del
día (~6 min); intervalos mayores (agujeros internos del feed) = EXCLUIDOS-CONTADOS** — una quote no se
extiende por un hueco de horas. Con los prints de CHD dentro del intervalo válido:

- **PRINTS A TRAVÉS (regla común, severidad-máxima de la revisión): cualquier print ESTRICTAMENTE peor
  que tu quote (por debajo de tu bid / por encima de tu ask) = FILL INCONDICIONAL en AMBAS cotas, a tu
  precio** — una orden en reposo cruzada por el precio se llena con certeza por prioridad precio-tiempo
  (las cancelaciones ajenas encima solo te MEJORAN la posición). Sin esta regla, la pesimista perdía
  precisamente los fills más tóxicos (barridos con ráfaga de cancels) → falso verde.
- Los prints AL precio exacto son los únicos cola-ambiguos, donde las cotas actúan:
  - **Cota OPTIMISTA (primero de la cola):** el primer print a tu precio te llena.
  - **Cota PESIMISTA (fondo de la cola):** te llenan solo cuando el volumen impreso acumulado a tu precio
    desde s ≥ tamaño visible del nivel en s (suma de `orders[]` al touch).
- Un fill por lado y por intervalo como máximo (re-quote en s+1). Fills etiquetados (lado, segmento,
  símbolo, tipo: through / al-precio).

## 5. Métrica, familia y estadística

- **markout(Δ) = lado · (precio_ref(t_fill + Δ) − px_fill) / px_fill − fee**, fee = 0 (re-verificar).
- **Familia PRE-DECLARADA: Δ ∈ {1, 5, 25} s × 2 cotas × 8 símbolos**, corrección BHY sobre toda la
  familia. Los tres horizontes tienen LA MISMA autoridad (petición de la mesa: la mitad corta se mide).
- **precio_ref con prints dispersos (insumo 4):** print más cercano a t_fill+Δ dentro de tolerancia
  ±max(Δ/2, 0,5 s); sin print en tolerancia → fill DESCARTADO-CONTADO para ese Δ. Si los descartes de un
  (símbolo, Δ) superan el 50% → esa celda = INCONCLUSO-POR-DENSIDAD (no se promedia lo que no se ve).
- **N_eff:** fills autocorrelados → bloques símbolo-día + `effective_n_autocorr` (la maquinaria de
  siempre). **Celda (símbolo × Δ × cota) reportable si ≥ 200 fills tras descartes; si no →
  INCONCLUSO-POR-MASA: contada, jamás promediada, y jamás usada para completar unanimidades en ninguna
  dirección — una celda muda no vota ni veta. Consecuencia escrita: si alguna celda de un horizonte es
  INCONCLUSA (por masa o por densidad), ni el verde ni el negativo pueden alcanzar su unanimidad en ese
  horizonte → empuja el veredicto global hacia INCONCLUSO.**

## 6. Regla de decisión (v1 — SIMETRÍA DE UNANIMIDAD: unanimidad para decretar, un voto para vetar, en
AMBAS direcciones; sustituye a la "rama más severa" del v0, que dejaba al negativo decretar con un solo
horizonte mientras exigía unanimidad al verde)

1. **NEGATIVO limpio ⇔ la cota OPTIMISTA muere (markout ≤ 0 significativo post-BHY) en LOS TRES
   horizontes** — muerto a toda paciencia, incluso desde el frente de la cola.
2. **VERDE FUERTE ⇔ la cota PESIMISTA sobrevive (markout > 0 significativo) en LOS TRES horizontes** —
   gana hasta desde el fondo con el simulador 200× más lento que la clase viva.
3. **Cualquier otra configuración — incluida la discrepancia entre horizontes ("rojo a 1 s, verde a
   25 s" = muerde-y-recupera, que el maker paciente sobrevive) — ⇔ INCONCLUSO**, con escalada
   PRE-NOMBRADA: (a) calibrar con el piloto L3 (§7) el modelo de cola realista intermedio, y/o (b)
   cotización anclada a trades (refresco a frecuencia de print con el canal validado). **Nunca
   reclasificable a verde por cansancio ni a rojo por prisa.**

Resultado modal anunciado (priors de la mesa v1, firmados pre-freeze): **INCONCLUSO ~55-60% (modal);
verde ~10-15%; negativo ~25-30%.** (La corrección de through-prints movió masa del verde falso a donde
siempre estuvo la verdad.)

## 7. Piloto L3-wallet (calibrador, no fuente masiva)

**3 candidatos × 10 días** (propuesta: FARTCOIN, LIT, WTI — meme/alt/commodity, una por fauna).
**Selección de días ESCRITA: 7 estratificados por la ventana + ≥3 del decil ALTO de vol realizada del
símbolo** — la toxicidad vive en ráfagas; calibrar solo en días tranquilos subestima el hazard (la
lección del 04-15 vs 05-13 aplicada al diseño). Los fills del piloto HEREDAN el etiquetado de sesión de
§2 (WTI en finde ≠ WTI en sesión). Entre snapshots consecutivos, cohortes de órdenes por `order_id`, con
TRES etiquetas (no binario): desaparece SIN prints a su precio = **CANCEL**; desaparece CON prints a su
precio y SIN trade-through = **FILL inferido**; desaparece con TRADE-THROUGH en el intervalo =
**FILL-PROBABLE (through)** — no clasificable limpiamente (¿canceló justo antes o lo barrieron?), contada
aparte y JAMÁS forzada al binario (forzarla sesga los markouts realizados hacia los fills tranquilos =
dirección falso-verde). Ambigüedades restantes (modificaciones, parciales) contadas. Produce: (a) tasas
empíricas de rotación/cancelación de cola por símbolo; (b) **markouts REALIZADOS de fills reales**
(primera observación directa de selección adversa del programa); (c) distribución de posición-en-cola.
El modelo calibrado se aplica al panel barato (§4) si la rama 3 dispara — **y su extrapolación a ARC es
A TRAVÉS DE FAUNA (ARC no está en el piloto): aceptable a nivel screen, y queda escrito aquí.**

## 8. Exposición declarada y alcance

- **Visto ya:** spreads medianos de capa 1 (día 2026-04-15), informatividad neutra (2 días), prints de
  Binance/Lighter usados en calibración del hermano-de-trades. **NINGÚN markout de maker, de nadie, en
  ningún venue.** El outcome de este pre-registro está sin examinar.
- **Alcance honesto:** esto mide la SELECCIÓN ADVERSA del fill (¿el spread capturado sobrevive al
  movimiento post-fill?). NO mide el PnL completo de una estrategia (gestión de inventario, sizing,
  riesgo de cola, unwind) — eso sería una capa 3 con su propio pre-registro. SCREEN, jamás veredicto.
- **Multiplicidad:** familia única declarada (§5); los segmentos de sesión y el reporte por símbolo son
  DIAGNÓSTICOS pre-declarados, no deciden.

## 9. EVR

Coste: ~días de código (simulador + piloto) + ~500-600 créditos (≈1,2% del Free mensual) + $0. Valor:
decide si la única hipótesis del programa con tres patas de dato (masa medida, toxicidad medida,
economía verificada) merece una capa 3 — o muere con recibos como las seis anteriores.

---

## §7-bis — MINI-PREREG DEL PILOTO L3 (enmienda que FORTALECE §7) — **CONGELADO: el hash del commit de este cambio es la autoridad de fecha**

**ACTA DEL FREEZE (2ª firma):** primer acto DETENIDO por regla (identidad v1 falló → control positivo →
enmienda v2, `b138326`/`6465db3`). Segunda firma dada tras diff exacto y conforme de la mesa cumplido.
Verificaciones en verde EN el acto: fees 0/0 standard + S3 sin solapamiento (carril de la mesa, esta
sesión); identidades v2 al acta (LIT 0,9826 ✓, DOGE 0,9521 ✓, FARTCOIN 0,9319 → carril de prints; control
BTC ρ_5m 0,9980). Desde este commit: cambios = enmiendas fechadas; ningún markout realizado existe antes
de este hash.

Disparada por el INCONCLUSO de capa 2 (rama 3, `bca9ab4`). Insumos fechados pre-borrador: `d006a97`.
**Ningún markout realizado se mira antes del freeze de esta enmienda.**

1. **Universo y días:** FARTCOIN, LIT, WTI **+ DOGE (4º símbolo, AÑADIDO no sustituido — enmienda v2:
   con FARTCOIN degradada al carril de prints, la métrica de decisión quedaba en dos patas; DOGE, del
   universo congelado de los 8, certificó identidad ρ_5m = 0,9521 ≥ 0,95 — borderline que PASA por
   regla, mismo trato que JUP al otro lado del filo; la familia se re-declara a 4 símbolos con su
   multiplicidad)** × 10 días de mar-jun que pasen el pre-filtro §2 — 7 estratificados por la ventana +
   **≥3 del decil ALTO de vol realizada diaria del símbolo** (vol desde trades-CHD, $0; la toxicidad
   vive en ráfagas). **FORTALECIMIENTO post-freeze (fechado, ANTES de mirar ningún snapshot): la
   selección ve solo la mitad CHD del pre-filtro; día elegido que falle el filtro de snapshots-0xA
   (≥300 filas) → lo SUSTITUYE el siguiente del mismo estrato/decil por orden determinista (vol desc,
   luego fecha) — colas de reemplazo pre-computadas en `pick_days`, cero discreción post-fallo.**
2. **Cohortes de RESOLUCIÓN** (entre snapshots consecutivos s→s+1, por `order_index`):
   **FILL-PARCIAL** (remaining_size decrece sin desaparecer) — **CLÁUSULA DE CORROBORACIÓN (mesa): exige
   print corroborante a su precio en el intervalo; decremento SIN print = AMBIGUA (modificación probable),
   en TODAS partes — markouts Y tasas de rotación** (robusto a cualquier semántica de modificación del
   venue, que NO hemos verificado y no se asume); **FILL inferido** (desaparece CON prints a su precio,
   sin through); **CANCEL** (desaparece sin prints a su precio); **FILL-PROBABLE(through)** (desaparece
   con trade-through — contada aparte, JAMÁS forzada al binario; **sus markouts SE MIDEN SIEMPRE como
   diagnóstico pre-declarado — que no decida nada no significa que no se mida**). Ambigüedades restantes
   contadas. Cada fill lleva además **etiqueta de ESTRATO de día** (estratificado vs decil-alto), con
   reporte por estrato pre-declarado: "sangra en todos" se lee como *sangra en muestra vol-cargada*, no
   como *sangra siempre* (la retirada en régimen volátil es negocio de capa 3, puerta legible).
3. **Cohortes de VELOCIDAD (la hipótesis literal):** **LENTA** = la orden sobrevivió ≥1 intervalo
   completo de snapshot antes de su fill (proxy refresco ≥~3 min); RÁPIDA = resto. Diagnóstico
   adicional: classing por wallet (`owner_account_index` con persistencia sistemática). Fills del
   piloto heredan las etiquetas de sesión §2.
4. **Markout realizado:** desde el precio de la orden, t_fill = ts del print casante (parciales sin
   print casante: descartados-contados). **Mapa de horizontes PRE-FIRMADO (identidad verificada por
   NIVEL DE PRECIO, no ticker):** FARTCOIN→mid Binance FARTCOINUSDT (ratio 0,9933) y LIT→mid Binance
   LITUSDT (ratio 1,001) a {1,5,25} s, con la base cross-venue (~0,8 bps mediana) declarada SUELO DE
   MEDICIÓN; **WTI sin perp Binance → tolerancia de prints y 1 s INMEDIBLE por escrito.**
   **ENMIENDA DE IDENTIDAD (fechada; sustituye al criterio ρ_1m≥0,95 tras DETENERSE el primer acto de
   firma por regla):** el test v1 (ρ retornos-1m ≥ 0,95) DISPARÓ en el turno del "firmo" (FARTCOIN 0,824,
   LIT 0,930 → freeze detenido, no se congeló sobre verificación fallida). Control positivo con el MISMO
   estimador (BTC, identidad cierta por el oráculo de basis): **ρ_1m = 0,9933, ρ_5m = 0,9980** → el
   estimador alcanza el umbral en mismo-activo DENSO; la atenuación es de escasez de prints (bounce +
   desincronía intra-minuto), no de identidad distinta. **Criterio v2 (MÁS estricto en consecuencia, no
   más laxo): identidad CERTIFICADA ⇔ ρ retornos-5m ≥ 0,95 (control BTC al acta). Certificada → mid de
   Binance como precio_ref en todos los horizontes. NO certificada → el símbolo cae al carril de
   tolerancia-de-prints (el de WTI) — no se dropea, pierde la referencia buena.** Valores al acta:
   **LIT ρ_5m = 0,9826 → CERTIFICADA (Binance-ref). FARTCOIN ρ_5m = 0,9319 → NO certificada → carril de
   prints, con sus horizontes cortos probablemente inmedibles-por-densidad (ya observado en capa 2:
   ~96% de descartes a 1 s) — declarado por escrito.** **DOGE ρ_5m = 0,9521 → CERTIFICADA (Binance-ref).**
   **ACTA TÉCNICA de las certificaciones:** día 2026-04-15 completo UTC; lado Lighter = cierre por
   último-print del bloque (trades CHD validados); lado Binance = klines 1m fapi; **control positivo BTC
   en la escala que certifica: ρ_5m = 0,9980** (y ρ_1m = 0,9933). **Dirección de error declarada:** en
   símbolos finos este test solo produce FALSOS NEGATIVOS de identidad (la atenuación por escasez de
   prints hunde ρ, jamás lo infla — dos activos distintos no sostienen ρ_5m ≥ 0,95 un día entero) ⇒
   certificar es SUFICIENTE pero no necesario; el no-certificado hereda el carril conservador sin
   afirmar que sea otro activo.
   **POR QUÉ LA v2 NO ES MOVER PORTERÍA (los 4 rasgos, al acta):** (1) el fallo fue diagnosticado por
   CONTROL POSITIVO como fallo del instrumento, no descubierto por inconveniencia del resultado; (2)
   ningún outcome visto — todo es instrumentación pre-dato; (3) la consecuencia es monótonamente MÁS
   dura (FARTCOIN no se rescata: falla también la v2 y pierde la referencia buena); (4) la dirección de
   error queda declarada (arriba). **REGLA DE LA CASA (catálogo, junto al n≥2): todo umbral pre-fijado
   se entrega CON su control positivo** — o no puede distinguir "instrumento descalibrado" de
   "hipótesis falsa". Hoy BTC hizo de diapasón; desde hoy es obligatorio, no afortunado.
   **Priors v2 (mesa, firmados con la enmienda):** existencia ~35-40% (con DOGE dentro) /
   sangra-en-todos ~30-35% / INCONCLUSO ~30-35%. E2E ~8-12% sin cambio.
5. **Estadística y suelo:** familia declarada = 3 símbolos × horizontes legibles × 2 cohortes de
   velocidad, BHY; N_eff por bloques símbolo-día; **≥200 fills/celda o INCONCLUSO-POR-MASA** (no vota,
   no veta).
6. **Regla de lectura (pre-escrita; SCREEN, jamás veredicto):** cohorte LENTA con markout neto >0
   significativo a 5-25 s en ≥1 candidato = **señal de existencia** (→ diseñar confirmación/capa 3);
   ≤0 significativo en todos = **la clase lenta sangra** (negativo del piloto); resto = **INCONCLUSO
   (por masa u otra configuración — no-significativos y signos mixtos incluidos)**. Priors de la mesa
   ya firmados: 35-40% / 30-35% / 25-30%, con nota direccional: la cláusula de corroboración mueve masa
   FILL-PARCIAL→AMBIGUA y empuja marginalmente al INCONCLUSO-por-masa en celdas finas — el precio de no
   medir disfraces, pagado por adelantado. **Exposición (survivor-tilt, declarado):** la cohorte LENTA
   mide fills de órdenes que SOBREVIVIERON ≥3 min — inclinación leve hacia condiciones benignas por
   construcción; no toca la lectura de existencia, y la extrapolación a quotes recién puestas es negocio
   de la capa 3.
7. **Presupuesto:** ~15-30 créditos (snapshots 3×10×~0,5) + klines Binance gratis + trades CHD $0.
   Guardia de 5.000 heredada.
