# AUDITORÍA A11 — revisión línea-a-línea del código estadístico (la mesa, 2026-07-05)

Encargo: la CARTA_DE_ATAQUE declara en A11 que ningún tercero auditó el código línea a línea.
Esta es la mitad interna de esa auditoría — la mesa leyendo las 1.104 líneas de los 8 ficheros de
cómputo. **No cierra A11** (sigo siendo el mismo operador con dos sombreros); caza bugs reales hoy,
antes de que el eco o el colector se apoyen en ellos.

Convención: cada hallazgo lleva `fichero:línea`, severidad, y una etiqueta —
**[ERRATA]** afecta a un número YA LEÍDO (requiere corrección en el ARCO/LEDGER) ·
**[PRE-ECO]** no tocó ninguna lectura pasada pero mordería en el eco de julio si no se corrige ·
**[OPS]** operacional/seguridad · **[OK]** verificado correcto, se documenta para el auditor futuro.

---

## SEVERIDAD ALTA

### H1 — [ERRATA] `confirm_screen.py:214-220` — la minoría estable (§5) usa t-stat iid, sin bloques ni N_eff

La celda §5 —el test de habilidad cuyo verde replicó fuera de ventana— computa el t así:

```
v = d["mo"][dec, k]; v = v[np.isfinite(v)]
mu = float(np.mean(v)); t = mu / (np.std(v, ddof=1) / math.sqrt(len(v)))
```

Esto es un t-stat sobre fills **individuales**, tratándolos como independientes: `sqrt(len(v))`
con `len(v)` = número de fills. Pero los fills de una misma wallet en un mismo día están
autocorrelados (la premisa central de todo el programa — por eso §3 usa `effective_n_autocorr` sobre
day-means). La §5 **no** aplica esa maquinaria: divide por la raíz del recuento bruto de fills.

**Consecuencia:** los t de la minoría estable están **inflados** — probablemente por un factor grande.
El ARCO reporta LIT t+4,5/t+50,6 y DOGE t+2,4 para esta celda. La **dirección** (medias positivas,
persistencia predice signo) se sostiene; la **fuerza** (los t) no es comparable a los t de la casa y el
t+50,6 es un artefacto de `len(v)` grande, no una señal de fuerza-50-sigma. DOGE, ya frágil (9 wallets),
probablemente pierde significancia bajo el test correcto.

**No invierte nada:** §5 es diagnóstico de apoyo, no el veredicto formal (que fue INCONCLUSO por §3, y
§3 sí está bien construido — ver OK1). Pero es un número publicado en el ARCO con una magnitud que el
método de la casa no respalda.

**Corrección:** recomputar §5 con la maquinaria estándar — day-means por wallet-día (o por día,
agregando la cohorte), serie cronológica, `effective_n_autocorr`, t. Y **erratar el ARCO**: los t+50,6 /
t+4,5 / t+2,4 se sustituyen por los t con N_eff, o se reetiquetan como "t iid, diagnóstico no
comparable con los t-neff de la casa". Es mecánico y no requiere re-mirar outcome nuevo (los markouts de
§5 ya se leyeron; solo se recomputa su estadístico sobre los mismos datos).

---

## SEVERIDAD MEDIA

### M1 — [PRE-ECO] `confirm_screen.py:150-160` — la rama NULA MUERTA es inalcanzable por un techo de p one-sided

`_p_from_t_onesided` (heredada de `maker_capa2_screen.py:35-37`) hace `0.5*erfc(abs(t)/sqrt(2))` — usa
**`abs(t)`**. En `confirm_screen`, la familia BHY (`pv`) se alimenta con este p para TODAS las celdas,
incluyendo las de tercil agitado. Luego `agit_neg` (línea 150) exige `mean ≤ 0 AND sig`. Pero una celda
con media negativa **grande** produce, vía `abs(t)`, un p **pequeño** → puede salir `sig=True` → `agit_neg`
alcanzable. Correcto hasta aquí.

El problema es el simétrico y silencioso: `agit_pos` (línea 145) exige `mean>0 AND sig`, y el decreto
NULA MUERTA pide `agit_pos` en ambos horizontes **con el otro símbolo no-`agit_neg`**. Como `_p` no
distingue signo, el BHY mezcla en una sola familia tests de cola-alta (PES/positivo) y de cola-baja
(negativo) usando el mismo p de dos colas colapsado a una. La orientación de significancia se recupera
a mano en cada rama (`mean>0`, `mean<=0`) **después** del BHY, no dentro. Resultado: el umbral BHY se
calcula sobre p-values que no tienen signo, y una celda puede heredar significancia de la magnitud de un
efecto de signo contrario al que su rama exige.

**Impacto en la lectura ya hecha:** NULO. El veredicto fue INCONCLUSO por discrepancia de horizontes
(5s ruido), y esa rama no depende de este defecto. **Impacto en el eco:** real — si el eco produce una
celda agitada fuertemente negativa a 5s y positiva a 25s, la contabilidad de significancia podría
comportarse de forma no diseñada. **Corrección pre-eco:** que `_p_from_t_onesided` reciba la dirección
esperada de cada celda y devuelva p one-sided **con signo** (p alto si el efecto va en contra de la
hipótesis de esa celda), o separar la familia BHY en dos (una por dirección). Escribir antes de correr
el eco; no tocar retroactivamente la lectura de capa 2 (su regla §6 es un caso distinto — ver OK2).

### M2 — [PRE-ECO] `confirm_screen.py:193-205` — el bootstrap §4 mide fracción de WALLETS, no cuota de VOLUMEN

El prereg §4 dice "cuota-de-un-día" y el piloto reportó "61,9% del **volumen** lento en wallets de un
día". El bootstrap implementado computa:

```
n1 = sum(1 for o, s_ in wd.items() if len(s_) == 1)   # wallets con 1 solo día
obs_share = n1 / max(len(wd), 1)                       # fracción de WALLETS
```

Esto es la fracción de *wallets* que aparecen un día, no la fracción de *volumen/fills* que aportan las
wallets de un día. Son cosas distintas: 200 wallets de 1 día que hacen 1 fill cada una son 200/266
wallets pero poquísimo volumen. El número que mandó la flor al banquillo (61,9%) era de volumen; el que
el bootstrap compara contra su nulo es de conteo de wallets.

**Impacto:** el bootstrap sigue siendo *internamente consistente* — compara obs-wallets contra
nulo-wallets, misma métrica en numerador y denominador, así que su percentil es válido *para la métrica
que mide*. Lo que NO es, es la métrica que el prereg nombró y que el titular del piloto usó. La
conclusión "51,2% obs ≡ 51,0% nulo" es correcta como afirmación sobre wallets; no es directamente la
refutación del "61,9% de volumen". **Corrección pre-eco:** o (a) reetiquetar el hallazgo como
"fracción de wallets de un día, no de volumen" en el ARCO y el LEDGER, o (b) añadir la versión ponderada
por fills. La (a) es honesta y barata; la (b) es más completa. Como el veredicto §3 no depende de §4
(es decisorio-secundario por diseño), no hay inversión — pero el ARCO afirma "la rotación era mecánica"
apoyándose en un estadístico de wallets presentado como si fuera de volumen.

### M3 — [PRE-ECO] `confirm_screen.py:113-116` — el suelo de masa/densidad se aplica a la cohorte ya filtrada por vol-finita

En `main`, `dec = (tipo<=1) & slow`, y luego los terciles se calculan solo sobre `volq[fin]`
(vol finita). Pero el conteo de masa por celda (`ok.sum() < 200`, línea 113) se hace sobre `v = mo[m,k]`
donde `m = terc==t3` — y `terc` ya es -1 (excluido) para los fills con vol no-finita. Correcto. El punto
fino: un fill con markout válido pero **vol trailing NaN** (menos de 8 minutos de trades previos, común
al inicio de cada día) queda fuera de TODOS los terciles → no cuenta en ninguna celda. Eso es defendible
(sin régimen no se puede clasificar), pero **no está contado en un log**. La masa "perdida por vol-NaN"
debería reportarse junto a los descartes, o un auditor futuro no sabrá cuántos fills se evaporaron antes
de la tabla. **Corrección pre-eco:** añadir a la salida el número de fills-decisión con vol-NaN
excluidos. No afecta veredicto; es completitud de acta.

### M4 — [OPS] `confirm_runner.py:25,38` y `confirm_screen.py:38` — KEYFILE hardcodeado con ruta absoluta de usuario

`KEYFILE_CHD = r"<USER_HOME>\Desktop\<KEY_DIR>\<KEY_FILE>"` aparece literal en dos
ficheros. Esto es exactamente lo que el SANEAMIENTO redacta para el espejo público — pero en el código
vivo significa que (a) la ruta de la key está en texto plano en el repo (SANEAMIENTO ya lo cubre para
la versión pública), y (b) si algún día se rota la key a variable de entorno como se ha discutido, estos
dos scripts rompen. **Corrección:** leer de `os.environ["CHD_KEY"]` con fallback al fichero. Menor, pero
toca el mismo nervio que la rotación pendiente.

---

## SEVERIDAD BAJA / VERIFICADO CORRECTO

### OK1 — [OK] `confirm_screen.py:117-130` — los terciles SÍ son POOLED ventana-entera

Verificado contra la acusación de A5/revisión. Líneas 99-105: `qs = np.quantile(volq[fin], [1/3, 2/3])`
sobre `volq = d["vol"][dec]` — todos los fills-decisión de la ventana entera del símbolo, sin partición
por día. Los terciles son pooled como el prereg §3 exige. **No hay normalización por día escondida.** El
diagnóstico de dos ejes (clase-día × tercil) no está implementado en este fichero, pero está declarado
como diagnóstico que no decide, así que su ausencia no viola el prereg (solo habría que no afirmar que
se computó).

### OK2 — [OK] `confirm_screen.py:144-167` — la unanimidad de horizontes está bien implementada

`muerta` exige `all(agit_pos(sym,k) for k in range(2))` — ambos horizontes {5s,25s} — con
`not any(agit_neg(other,k))`. `viva` exige `all(tranq_pos and not agit_pos for k in range(2))` para todo
símbolo medible. Un horizonte no medible hace `agit_meas` falso → el símbolo no contribuye a `viva`, y
no puede completar `muerta`. Discrepancia entre horizontes → ninguna rama se satisface → INCONCLUSO. Esto
es exactamente la doctrina firmada: unanimidad para decretar, un horizonte bloquea. **Correcto.** (El
defecto M1 vive dentro de `sig`, no en esta lógica de agregación.)

### OK3 — [OK] `confirm_runner.py:36-48` — la vol trailing es estrictamente PRE-fill

`trailing_vol`: `j0 = searchsorted(tts, t_fill - VOL_MS)`, `j1 = searchsorted(tts, t_fill)`. La ventana
es `[t_fill − 20min, t_fill)` — cerrada por debajo, abierta en el fill. `searchsorted` por defecto
(`side='left'`) en j1 excluye el print del propio instante del fill. **Jamás centrada, jamás incluye
post-fill.** Correcto y es el punto que la revisión marcó como crítico. El estimador de vol es
std(diff(log(close-por-minuto))) — razonable, y su NaN-si-<8-min es conservador.

### OK4 — [OK] `confirm_runner.py:79` / `pilot_observer.py:46` — `slow` no tiene fugas

`slow = oid in prev_seen`, y `prev_seen` se actualiza con `|= set(prev.keys())` **después** de procesar
el intervalo (líneas 97 y 90 respectivamente). Es decir: una orden es "lenta" solo si ya se había visto
en un intervalo ANTERIOR al de su resolución — la definición §7b.3 exacta (sobrevivió ≥1 intervalo
completo). No hay contaminación look-ahead: el snapshot de apertura del propio intervalo de resolución
no cuenta como "vista antes". Correcto.

### OK5 — [OK] `confirm_runner.py:82-87` — la cláusula AMBIGUA está bien

Decremento de `remaining_size` sin print corroborante a precio (`at.any()` falso) → `cnt["ambigua"]`, no
fill. Con print → PARCIAL. Es la cláusula de corroboración de la mesa, y trata la semántica de
modificación no verificada de la única forma segura (sin print = no es fill en ninguna parte). Correcto,
y es robusto a que Lighter permita reduce-in-place.

### OK6 — [OK] `maker_capa2_screen.py:40-56` — el BHY es el de dependencia arbitraria, bien implementado

`_bhy`: `c_m = sum(1/i for i in 1..m)` es la constante armónica de Benjamini-Yekutieli, y el umbral
`pvals[i] <= rank*alpha/(m*c_m)` es la forma BY correcta para dependencia arbitraria. El `k_max` toma el
rango más alto que pasa (step-up correcto). **Correcto.** Este es el corazón estadístico que M1 alimenta
con p-values sin signo — el BHY en sí está bien; lo que entra mal es el p.

### OK7 — [OK] `maker_capa2_screen.py:122-124` — la orientación direccional de capa 2 SÍ distingue signo

A diferencia de `confirm_screen`, aquí `p = _p_from_t_onesided(s["t"]) if t_dir>0 else 1.0`, donde
`t_dir = t*direction` y `direction = -1 para OPT, +1 para PES`. Es decir: capa 2 SÍ impone un p=1
(no significativo) cuando el efecto va en contra de la dirección de la cota. Esto es lo que
`confirm_screen` NO hace (M1). Curiosamente el fichero más viejo tiene la orientación correcta y el más
nuevo la perdió. La lectura de capa 2 (INCONCLUSO) es por tanto robusta a M1.

### OK8 — [OK] `maker_sim.py:58-76` — las dos cotas y los through-prints implementan el §4 congelado

`through = (p<qpx and not at_price) if lado==+1` → fill incondicional en ambas cotas. `at_price` →
OPT llena al primer print, PES cuando `cum >= qsz`. Un fill por lado/cota/intervalo (`filled` flags,
break en línea 75). Es exactamente el texto del prereg de capa 2. Convención de signos correcta
(+1 bid pasivo / −1 ask pasivo, línea 49). **Correcto.**

### OK9 — [OK] `lighter_adapter.py:46-49,155-159` — la trampa ns/ms está bien defendida

`_assert_range` grita `LighterUnitsError` si el orderbook no está en rango ns (1e17-1e20) o los trades
no están en ms (1e12-1e14). Es la lección de unidades-mixtas como código, y falla fuerte en ambos
sentidos. El oráculo estructural (`_oracle`, líneas 91-109) mide membresía top-K robusta al skew y lanza
`LighterSeamError` si el mismatch medio supera 0.20. Bien construido — es la maquinaria que condenó al
canal de CHD. **Correcto.** Nota menor: el adapter de LIBRO (`lighter_to_book`) es el que quedó
descartado por el veredicto n=2; el que está en la ruta viva es solo `lighter_trades_ms`, que es trivial
y correcto.

### OK10 — [OK] `flow_informativeness.py` — el estimador calibrado es sólido y su sesgo es conservador

La señal (dólar firmado en ventana trasera), el umbral causal (P95/P5 rolling), y el outcome (retorno
VWAP-a-VWAP) están construidos sin look-ahead: `flow_w` usa suma trasera, `causal_rolling_percentile` es
causal por nombre y el VWAP-LOCF (líneas 48-50) sólo mira hacia atrás. El sesgo del bid-ask bounce
empuja hacia REVERSIÓN (declarado en el docstring), así que un veredicto de CONTINUACIÓN es conservador
— exactamente el argumento de atenuación que la mesa pidió afilar en A10. La calibración (≥5/6 y
t≤−3 contra la verdad de Binance) es una barra empírica ganada, no asumida. **Correcto**, y es el
instrumento cuya credencial (6/6, t−4,11) es la evidencia más fuerte contra A11 — un estimador que
reproduce el t=−26 canónico está validado de extremo a extremo, no sólo en estilo.

---

## RESUMEN EJECUTIVO PARA EL LEDGER

| # | fichero:línea | sev | etiqueta | efecto |
|---|---|---|---|---|
| H1 | confirm_screen.py:214-220 | ALTA | ERRATA | t-stats de §5 (minoría estable) inflados: iid en vez de N_eff. ARCO debe erratar t+50,6/t+4,5/t+2,4. No invierte el veredicto (§5 es diagnóstico) |
| M1 | confirm_screen.py:150-160 | MEDIA | PRE-ECO | p one-sided sin signo en la familia BHY del decisivo; NULA MUERTA/agit_neg pueden heredar significancia de signo contrario. No tocó la lectura (INCONCLUSO por 5s); corregir antes del eco |
| M2 | confirm_screen.py:193-205 | MEDIA | PRE-ECO | bootstrap §4 mide fracción de wallets, no de volumen. Internamente consistente pero no es el 61,9% del titular. Reetiquetar o ponderar |
| M3 | confirm_screen.py:113-116 | MEDIA | PRE-ECO | fills con vol-NaN se evaporan sin contarse en log. Completitud de acta |
| M4 | confirm_runner.py:25,38 | MEDIA | OPS | KEYFILE hardcodeado; rompe si se rota la key a env var |
| OK1-10 | — | — | OK | terciles pooled ✓, unanimidad de horizontes ✓, vol pre-fill ✓, slow sin fugas ✓, AMBIGUA ✓, BHY-BY ✓, orientación capa 2 ✓, cotas/through ✓, ns-ms ✓, estimador calibrado ✓ |

**Veredicto de la auditoría:** el código implementa lo firmado en lo que decidió los veredictos ya
leídos. El único hallazgo que toca un número publicado es H1 (t-stats de la minoría estable), y es una
errata de fuerza, no de dirección ni de veredicto. Los tres PRE-ECO son fortalecimientos que deben
entrar en el prereg del eco antes de correrlo — exactamente el tipo de cosa que se corrige pre-dato.
Ninguno aflojaría una regla; todos la endurecen o la aclaran.
