# Research brief — ¿es sólido tirar la ventana de cancelación (C2) y fiarlo al markout?

*Revisión hostil de UNA decisión que tomé en tiempo real y que CONTRADICE una decisión vinculante
previa. Sé escéptico: dime claramente si he reintroducido el optimismo que C2 evitaba.*

---

## Contexto

Simulamos un **maker pasivo** sobre nuestro L2 propio `@depth10@100ms` + aggTrades, para 8 perps
USDT-M finos de Binance. Modelo de cola = **RiskAdverse** (siempre último). Todo se vende como
**COTA INFERIOR** de fills/P&L.

**Decisión VINCULANTE previa (C2, de una revisión hostil):** hay que modelar una **ventana de
cancelación** — tras moverse el best, el quote viejo queda "rancio pero ejecutable" durante
`p95(recv−event)≈265 ms`; cualquier trade a ese precio = fill TÓXICO. El argumento: *"sin la ventana,
los resultados son cota inferior en NÚMERO de fills pero NO en P&L, porque te saltas exactamente los
fills que más recortan (los que te llenan a precio rancio porque no cancelaste a tiempo)."*

## El hallazgo empírico (ensayo sobre ATOM real, 2026-06-22)

Al validar sobre dato real, la ventana de cancelación produjo **70% de fills "stale" ESPURIOS** y
half_spread NEGATIVO. Causa raíz: ATOM tiene **spread de 1 TICK** (5,5 bps) y el best cambia solo el
1% entre snapshots. Con depth MUESTREADO a 100 ms, un trade al **ask viejo (= bid actual, por el
spread de 1 tick)** se confunde con un fill rancio. La ventana de cancelación **no es implementable de
forma fiable con spread de 1 tick + depth muestreado.**

## Mi resolución (la que hay que revisar)

`cancel_window_ms = 0` por defecto → half_spread **+2,76 bps, 100% positivo**, fills realistas
(~520-926/día). Mi argumento: **la toxicidad de latencia que C2 buscaba la captura el MARKOUT** — un
fill que te hace daño (informado, te llenó porque el precio iba a moverse) muestra **markout adverso**
a horizonte h. Así que el P&L neto (half_spread − markout − fee) sigue contabilizando esa toxicidad;
solo se mueve de un *label* dudoso a una *medición* robusta.

## La pregunta (sé hostil)

1. **¿Subsume el markout a la ventana de cancelación, o reintroduzco optimismo?** Un fill rancio = me
   llenaron a un precio que el mercado YA dejó atrás (vendí al ask viejo, ahora más bajo). El markout
   = movimiento del fair value DESPUÉS del fill. ¿Capturan lo mismo, o hay una toxicidad de "ya
   estabas mal al ejecutar" que el markout post-fill NO ve?
2. **¿Hay un sesgo residual?** Al tratar todos los fills como "normales" (half_spread positivo), ¿
   sobre-cuento fills favorables que en realidad eran latency-tóxicos, aunque el markout los penalice?
3. **¿Refuerza esto que H8 necesita L3 / live tiny-size?** O, con `cancel_window=0` + markout, ¿es el
   sim sobre snapshots un SCREEN defendible (cota inferior aún razonable)?
4. **Calibración:** la fracción de soledad depende mucho de Q (0,7% a Q=1 ATOM ~$1,8 vs 44% a Q=30
   ~$54). ¿Qué Q es realista para un maker diminuto (mínimo notional de Binance), y cómo afecta a la
   interpretación?

## Qué quiero

Una revisión hostil de MI resolución. Si dropear C2 reintroduce el optimismo que evitaba, **dilo
claro** — preferimos un sim más pesimista pero honesto. Si el markout sí lo subsume, confírmalo con el
mecanismo. Y si la conclusión honesta es "este edge solo se testea de verdad con L3/live", dilo.
