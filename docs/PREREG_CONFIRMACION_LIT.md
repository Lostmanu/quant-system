# PRE-REGISTRO — CONFIRMACIÓN DECISIVA del edge maker-lento (post-piloto, post-atlas)

**Estado: CONGELADO — el hash del commit de este cambio es la AUTORIDAD DE FECHA.**

**ACTA DEL FREEZE:** firma del propietario ("FIRMO") sobre el v1 (diff exacto de la revisión de la mesa,
`46029e3`; conforme por adelantado cumplido — 4º diff exacto del historial). Verificaciones EN el acto:
DOGE re-certificada en día de la VENTANA NUEVA (2026-03-06, 1er día válido no-piloto, elegido
determinísticamente): **ρ_5m = 0,9641 ≥ 0,95 CUADRA**; límites Free desde la cuenta: 1.075/50.000
usados, 48.925 restantes (el presupuesto ~300 cabe ×160) CUADRA; fees 0/0 y Season-3 sin solapamiento en
verde de esta misma sesión (carril de la mesa; cláusula de caducidad satisfecha). El eco de julio
re-verifica S3 ANTES de tocarse (§7). Desde este commit: enmiendas fechadas; ningún markout de las
ventanas nuevas existe antes de este hash. **Naturaleza: DECISIVO, no confirmatorio** — tras la ecología
ROTATORIA (`e02fe96`), la HIPÓTESIS NULA a batir es el confound de supervivencia: *"el markout positivo
de la cohorte lenta es condicionamiento a régimen benigno + rotación de afortunadas, no habilidad de
clase"*. Si este diseño no puede matar esa nula con dientes, no se corre. Priors vigentes: mesa 45/55
(re-firmados sin colchón). Ningún markout de la ventana nueva existe antes del freeze.

## 1. Universo y ventanas

- **Símbolos:** LIT + **segundo símbolo certificable OBLIGATORIO** (DOGE, ρ_5m=0,9521 ya al acta; se
  re-certifica en el freeze sobre un día de la ventana nueva). Sin el segundo, el veredicto se llamaría
  "LIT", no "maker lento" — anécdota, no hallazgo.
- **Held-out (elección explícita):** PRIMARIA = los días de mar-jun que el piloto NO tocó (≈110 por
  símbolo, menos exclusiones de completitud); ECO = forward julio-2026 (con re-check de Season-3 en el
  freeze — si S3 solapa julio, el eco se re-corta o cae). Los 10 días del piloto quedan EXCLUIDOS de
  toda celda decisoria.
- **Masa (lección H3, escrita antes de correr): objetivo n_eff ≥ 30-50 bloques efectivos** en la celda
  primaria (bloques símbolo-día, `effective_n_autocorr`). Si el diseño no puede alcanzarlo con las
  ventanas de arriba, se declara INCONCLUSO-POR-MASA sin correr — no se corre para descubrirlo.

## 2. Instrumentación (heredada, ya validada)

Observador de cohortes (`d859cce`, 6 tests) + carriles de referencia del §7-bis (LIT/DOGE → mid Binance;
suelo 0,8 bps) + pre-filtro de completitud + sustitución determinista + logs solo-conteos. Cohortes de
resolución idénticas (PARCIAL-corroborada / FILL / CANCEL / THROUGH-diagnóstico / AMBIGUA).

## 3. El TEST DECISIVO — régimen por vol PREVIA (insumo 1)

- **Vol trailing de 20 min ANTES del fill — UNA ventana, fijada** (15 y 30 min quedan como diagnóstico,
  jamás deciden; los rangos en reglas decisivas son forking paths). Desde trades, jamás centrada — una
  ventana que incluya el post-fill mete mecánicamente los |markouts| grandes en el bucket agitado.
- **Terciles POOLED por símbolo sobre TODOS los fills de la ventana entera** (v1, severidad-máxima de la
  revisión: los terciles por-día normalizaban dentro del día — el tercil agitado de un día muerto sigue
  siendo un día muerto, y la nula habla del régimen ENTRE días; con por-día, el "positivo en agitado"
  podía construirse con los tercios movidos de días tranquilos = el condicionamiento benigno
  re-etiquetado como su refutación). Diagnóstico pre-declarado de dos ejes: clase-de-día × tercil
  intradía — informa, no decide.
- **VEREDICTO PRE-ESCRITO (v1, con la regla de horizontes SIN corrientes de aire — unanimidad para
  decretar, doctrina de la casa):**
  - **NULA MUERTA** (el edge es habilidad → capa 3) ⇔ cohorte LENTA neta positiva significativa
    post-BHY en el tercil agitado POOLED **en AMBOS horizontes legibles {5s, 25s}**, en ≥1 símbolo con
    el otro no-negativo.
  - **NULA VIVA** (tilt de supervivencia → la flor muere como edge operable) ⇔ patrón
    positiva-solo-en-tranquilos **en ambos horizontes**.
  - Un horizonte INCONCLUSO bloquea cualquier decreto; discrepancia entre horizontes → INCONCLUSO.
  - Resto → INCONCLUSO (por masa u otra configuración), con escalada nombrada: extender eco de julio.

## 4. MODELO NULO DE PARTICIPACIÓN (insumo 2 — convierte la rotación de vibra en estadístico)

Bootstrap sobre la ventana nueva, **CONDICIONADO A LA PRESENCIA POR DÍA (v1):** los fills lentos se
permutan DENTRO de cada día entre las órdenes lentas presentes ESE día (un nulo que deja cobrar a una
wallet un día en que no tenía órdenes infra-produce la cuota-de-un-día y absuelve a la rotación por
construcción), proporcional a actividad × 1.000 réplicas → distribución nula de la cuota-de-un-día. **Si el nulo
produce ~60% solo, la rotación observada no acusa a nadie; si produce ~30%, el 61,9% del piloto era
evidencia real.** Se reporta el percentil del observado bajo el nulo. Diagnóstico decisorio-secundario:
no decide el veredicto §3, pero SÍ decide cómo se lee la ecología en el acta final.

## 5. MINORÍA ESTABLE como test de habilidad (insumo 3 — la línea roja respetada)

Las wallets con fills lentos en ≥2-3 días DEL PILOTO se seleccionan por FISONOMÍA de la ventana vieja
(comportamiento — legal) y sus markouts se miden SOLO en la ventana nueva. **Persistencia pasada que
predice edge futuro = habilidad que ningún confound fabrica; si no predice nada, la rotación era ruido
con suerte.** La caja de la ventana vieja sigue prohibida; la de la nueva la autoriza este pre-registro.

## 6. Familia, multiplicidad y regla global

Familia declarada: 2 símbolos × horizontes legibles {5s, 25s} × cohorte-velocidad × tercil-de-régimen +
la celda minoría-estable. BHY sobre toda la familia. Celdas <200 fills o >50% descartes = INCONCLUSAS
(no votan, no vetan, bloquean unanimidades — la maquinaria de siempre). Diagnósticos pre-declarados que
NUNCA deciden: through, rápida, estratos, sesión (para DOGE: cripto-24/7).

## 7. Presupuesto y guardias

**Cuentas que suman (v1):** primaria ≈ 110 días × 2 símbolos ≈ 220 cr + eco julio ≈ 31 × 2 ≈ 62 cr ⇒
**~280-300 créditos TOTAL, eco incluido** + trades CHD $0 + klines Binance $0. **Nota al acta (v1): la
primaria está DEPLETA de los 3 días top-vol por símbolo** (el piloto se los llevó) — resta conocida, no
anomalía, para el auditor futuro. Guardia de 5.000 heredada. En el freeze se re-verifican: fees, Season-3 (solapamiento con
las ventanas ELEGIDAS, incluido julio), identidad DOGE (ρ_5m ≥ 0,95 en día de la ventana nueva), y
límites Free desde la cuenta.

## 8. Exposición declarada

Visto: piloto completo (markouts de 10 días leídos), atlas (fisonomía + persistencia), capa 1/2.
NO visto: ningún markout de los días primaria/eco. El resultado de este pre-registro está sin examinar.
SCREEN decisivo, jamás veredicto de estrategia (capa 3 tendrá el suyo).
