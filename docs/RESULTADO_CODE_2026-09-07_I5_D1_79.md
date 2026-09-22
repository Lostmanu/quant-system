# Code → Mesa, Codex y Manuel · 2026-09-07 · D1 ejecutado sobre el panel de 79 días: el +18,24 se reproduce en la admisión histórica y cae a +2,57 al admitir los through-con-at

Responde a `PARA_CODE_2026-09-07_I5_D1_79.md`. Auditoría del analizador y **una ejecución**, en
`Desktop\Laboratorio\I5_D1_79_20260907_01`, sobre el panel reproducido de 79 días. **D1 es retrospectivo y post
hoc** (especificación `ESPEC_MESA_2026-09-07_D1_79_DIAS.md` `6e358b9c…`): describe la sensibilidad de la receta
histórica; no confirma ni rehabilita nada. Referencia: trades de Binance, carril no conforme. Nada se declara
ratificable. Todas las ramas y contrastes fijados están publicados en `results.json`; aquí no se escoge ninguno
por su signo.

## 1. Auditoría del incremento

| comprobación | resultado |
|---|---|
| huellas | `i5_d1.py` `8713b171…`, `i5_d1_math.py` `9f916017…`, `test_i5_d1.py` `dba4d8e9…`, plan `_01` `185dd59c…`, verificación `4205c1d2…`: todas = relevo; instrumentos anteriores intactos |
| focales | **46 passed** (3,6 s, basetemp nuevo); objetos git 667 antes y después |
| plan sin red | regenerado con `--plan --panel-root`: **811.164 bytes, `185dd59c…`, byte a byte igual** |
| ramas | H, A, T, TV, Q, VH, VA construidas exactamente como la tabla de §2 de la especificación: una sola pieza cambia por rama; T y TV mueven solo los incorporados; TV recalcula la vol con el `trailing_vol` literal de julio (extraído del commit `74f0d60…`); VH/VA validan el candidato con `ref_valida.clasificar` como única regla, sin buscar el siguiente trade válido |
| candidatos | búsqueda `lower_bound` con empate al anterior y tolerancia `max(Δ//2, 500 ms)`: los focales la igualan a la función literal de julio y al llamador R1–R3 vigente en empates, duplicados, bordes y referencias cero/negativas/NaN/degeneradas |
| cortes | Q0 = cuantiles lineales 1/3 y 2/3 de la `vol20` finita de los eventos H lentos, suelo > 100, **idéntico a la regla de julio** (`confirm_screen.py:96-104` del commit: `dec = (tipo<=1) & slow; np.quantile(volq[fin], [1/3, 2/3]) if fin.sum() > 100`); QA cambia solo el pool; escritos en `quantiles.json` antes de derivar ninguna rama |
| estimadores | media diaria con mínimo 3 finitos, media equiponderada de días, `effective_n_autocorr` de la casa (`analysis/screen.py`) sobre la serie cronológica, t descriptivo nulo con < 4 días, sd 0 o n_eff ≤ 1; contrastes pareados en la intersección con ambos niveles recalculados; lado-neutral con ≥ 3 por lado; lenta−rápida en días comunes a las cuatro celdas y ambas ramas; descomposición con control aritmético a 32 eps |
| custodia | plan por hash antes de abrir nada; 79 NPZ verificados cuerpo a cuerpo contra el panel; correspondencia de `mo_ext` y `ref_t` archivados con los candidatos recalculados desde los trades custodiados; sin diferir, sin originales canónicos, sin red |

**Sin defectos de corrección.** Una discrepancia de etiqueta para la mesa, no del analizador: la
especificación designa «LIT lento, agitado, **5 s**» como celda principal «por ser la del antiguo titular».
**El +18,24 del titular vive en 25 s:** H lento agitado 25 s da 18,236789 bps; la de 5 s da 2,61. Ambas están
publicadas y fijadas de antemano, así que no cambia ninguna lectura; conviene corregir la etiqueta.

## 2. Ejecución

| campo | valor |
|---|---|
| comando | el de §5 del relevo, `--expected-plan-sha256 185dd59c…` |
| UTC | 17:31:07 → 17:35:44 (4 min 37 s) |
| estado / rc | **`D1_79_COMPLETE_POST_HOC` · rc 0** · `D1_completed: true` |
| recibos | `plan.json` `185dd59c…` · `quantiles.json` `70912346…` · `results.json` `1d196773…` (17,2 MB) · `lectura.md` `13607ae5…`; 79 recibos diarios, los 79 con hash = `result.json`; 79 anexos NPZ con recibo; 461 MB |

## 3. Cortes de terciles (fijados antes de agregar)

| | cortes q1 / q2 (bps de vol20) | pool finito | lentos admitidos | vol no finita |
|---|---|---|---|---|
| Q0 (H lento) | 10,63 / 16,04 | 13.273 | 13.368 | 95 |
| QA (A lento) | 13,02 / 20,62 | 114.814 | 115.302 | 488 |

## 4. Niveles con soporte propio, cohorte lenta (media equiponderada de días; t descriptivo; k = días con ≥ 3 finitos)

| rama | agitado 5 s | agitado 25 s | medio 5 s | medio 25 s | tranquilo 5 s | tranquilo 25 s |
|---|---|---|---|---|---|---|
| **H** | 2,61 (t 0,29; k 79) | **18,24 (t 6,69; k 79)** | −0,48 (t −0,09; 76) | 9,21 (t 17,46; 76) | 13,99 (t 1,91; 70) | 13,99 (t 2,12; 70) |
| **A** | −1,08 (t −0,37; 79) | **2,57 (t 2,00; 79)** | −2,08 (t −0,74; 78) | −1,06 (t −0,99; 78) | −3,27 (t −1,03; 75) | 0,09 (t 0,05; 75) |
| T | 0,79 (t 0,38; 79) | 2,69 (t 1,46; 79) | −1,87 (−0,98; 78) | −1,36 (−0,53; 78) | −0,87 (−0,37; 75) | 0,31 (0,18; 75) |
| TV | 0,94 (t 0,47; 79) | 2,88 (t 1,11; 79) | −1,89 (−0,97; 78) | −1,43 (−1,08; 78) | −0,95 (−0,39; 74) | 0,03 (0,02; 74) |
| Q | 0,32 (t 0,30; 77) | 3,51 (t 2,18; 77) | −3,44 (−0,45; 79) | −0,54 (−0,38; 79) | −1,36 (−0,47; 77) | 0,22 (0,18; 77) |
| VH | 10,38 (t 11,90; 79) | 15,60 (t 9,22; 79) | 6,05 (11,50; 76) | 9,21 (17,47; 76) | 5,27 (5,91; 70) | 7,50 (9,44; 70) |
| VA | −0,10 (t −0,13; 79) | 1,50 (t 1,75; 79) | −0,79 (−1,33; 78) | 0,10 (0,11; 78) | −1,73 (−1,56; 75) | −1,07 (−0,93; 75) |

Eventos finitos en lento agitado: H 4.125 (5 s) y 4.413 (25 s), todos históricos; A 57.284 y 58.784, de los que
53.159 y 54.371 son through-con-at incorporados. **H admite el 10,1 % de los eventos lentos de la receta; A el
86,8 %.** Días excluidos por < 3 finitos: H tranquilo 9 (04-09, 04-10, 05-18, 05-20, 05-22, 05-28, 05-29, 06-03,
06-11), H medio 3 (05-20, 05-22, 06-03), agitado 0.

## 5. Contrastes pareados, cohorte lenta (izquierda − derecha en la intersección de días; ambos niveles recalculados)

| contraste | agitado 5 s | agitado 25 s | medio 25 s | tranquilo 25 s | all 25 s |
|---|---|---|---|---|---|
| **A−H** (admisión sola) | **−3,69 (t −0,55; 79 d)** | **−15,66 (t −6,90; 79 d)** | −10,56 (t −10,05; 76) | −13,12 (t −2,35; 70) | −12,33 (t −7,86; 79) |
| T−A (reloj) | +1,88 (t 1,92; 79) | +0,11 (t 0,37; 79) | −0,30 (−0,23; 78) | +0,22 (0,45; 75) | −0,18 (−0,42; 79) |
| TV−T (ventana de vol) | +0,15 (t 0,88; 79) | +0,19 (t 0,24; 79) | −0,08 (−0,10; 78) | −0,15 (−1,30; 74) | 0,00 (sd 0) |
| Q−A (cortes) | +1,64 (t 0,62; 77) | +1,15 (t 1,06; 77) | +0,63 (0,69; 78) | −0,29 (−0,31; 75) | 0,00 (sd 0) |
| VA−VH (admisión con referencia validada) | **−10,48 (t −13,40; 79)** | **−14,10 (t −9,83; 79)** | −9,38 (−13,59; 76) | −7,87 (−8,58; 70) | −11,13 (−8,64; 79) |
| VH−H (validación, admisión histórica) | +7,77 (t 0,88; 79) | −2,63 (t −1,00; 79) | 0,00 (t 1,00; 76) | −6,49 (−1,00; 70) | −1,43 (−1,37; 79) |
| VA−A (validación, admisión ampliada) | +0,99 (t 0,39; 79) | −1,08 (t −1,31; 79) | +1,16 (1,69; 78) | −1,16 (−0,90; 75) | −0,24 (−0,43; 79) |

Signo por día en lento agitado: H > 0 en 78 de 79 días a 25 s (76 de 79 a 5 s); A > 0 en 46 de 79 (39 de 79);
**A−H < 0 en 73 de 79 días a 25 s** (74 de 79 a 5 s), mediana de la diferencia diaria −14,3 bps (−10,5 a 5 s).
Desviación típica diaria: H 24,2 bps (25 s) y 78,8 (5 s); A 10,9 y 23,8.

## 6. Referencias, lado, cohorte rápida y descomposición

**Validación del candidato (conteo diagnóstico, no aplicado en H/A).** En H lento agitado a 5 s: 4.122 válidas,
299 sin referencia en tolerancia, **3 con referencia no positiva** (precio cero ⇒ ±10.000 bps); a 25 s: 4.412,
11 y 1. Esas tres celdas rotas explican que H a 5 s dé 2,61 (t 0,29) y VH 10,38 (t 11,90): el defecto conocido
de referencias degeneradas contamina la celda de 5 s y apenas la de 25 s. En A: 18 y 10 celdas no positivas
sobre 57–59 mil.

**Lado neutral, lento agitado** (medias bid/ask por día con ≥ 3 por lado; simétrico = (ask+bid)/2):

| rama | 5 s simétrico | 5 s antisimétrico | 25 s simétrico | 25 s antisimétrico |
|---|---|---|---|---|
| H | 1,30 (t 0,18; k 74) | 18,12 (t 2,55) | 14,72 (t 7,84; k 77) | 11,26 (t 4,46) |
| A | −4,16 (t −1,82; k 79) | 13,76 (t 6,14) | −0,73 (t −0,83; k 79) | 12,08 (t 6,77) |
| VH | 7,67 (t 8,99; k 74) | 10,26 (t 5,12) | 12,92 (t 7,71; k 77) | 9,46 (t 5,14) |
| VA | −2,63 (t −6,74; k 79) | 10,23 (t 6,39) | −1,16 (t −2,20; k 79) | 10,61 (t 5,87) |

**Cohorte rápida, agitado:** H 4,82 (t 2,93) a 5 s y **11,78 (t 8,48) a 25 s**; A −1,84 (t −2,25) y −1,11
(t −1,09); VH 6,84 y 12,82; VA −1,80 y −0,93. **Lenta−rápida en soporte común de lado y cohorte** (componente
simétrica, 25 s): H +2,92, A +0,88, diferencia −2,04 (t −0,78; 77 d); a 5 s: H −3,14, A −2,01.

**Descomposición** `mo = orden−trade + movimiento`, lento agitado, soporte común a los cinco horizontes:

| rama | 1 s | 5 s | 10 s | 25 s | 60 s | eventos |
|---|---|---|---|---|---|---|
| H | 10,58 = 5,15 + 5,43 | 14,13 = 5,15 + 8,98 | 43,71 = 5,15 + 38,55 | 20,08 = 5,15 + 14,93 | 22,09 = 5,15 + 16,93 | 2.139 de 4.424 (k 71) |
| A | −2,65 = −0,97 − 1,68 | 0,41 = −0,97 + 1,38 | 2,32 = −0,97 + 3,29 | 1,66 = −0,97 + 2,63 | −15,28 = −0,97 − 14,30 | 40.951 de 58.901 (k 79) |
| VH | 7,71 = 5,14 + 2,57 | 12,68 = 5,14 + 7,54 | 15,58 = 5,14 + 10,44 | 20,07 = 5,14 + 14,93 | 24,52 = 5,14 + 19,38 | 2.133 de 4.424 (k 71) |
| VA | −2,21 = −0,99 − 1,22 | −1,65 = −0,99 − 0,67 | −1,59 = −0,99 − 0,61 | 0,27 = −0,99 + 1,26 | 2,58 = −0,99 + 3,57 | 40.891 de 58.901 (k 79) |

Curva de horizontes en soporte propio, lento agitado: H 10,05 / 2,61 / 18,40 / 18,24 / 20,83 bps a 1/5/10/25/60 s;
A −1,26 / −1,08 / 2,86 / 2,57 / −9,17.

## 7. Lectura de Code (descriptiva; opinión donde se indica)

1. **El titular se reproduce y es estable dentro de su admisión.** H lento agitado 25 s = 18,24 bps, t 6,69,
   positivo en 78 de 79 días. Con referencia validada, 15,60 (t 9,22). Ese es el número de julio, ahora con
   insumos re-adquiridos y receta congelada.
2. **El contraste principal, admisión sola, lo desmonta en magnitud.** Admitir los through-con-at, sin tocar
   reloj, fórmula, cortes ni referencia, baja la celda de 18,24 a 2,57 bps (−15,66; t −6,90; 73 de 79 días
   negativos). Con referencia validada, de 15,60 a 1,50 (−14,10; t −9,83). A 5 s pasa a negativo. El mismo
   patrón en los tres terciles y en la cohorte rápida. El signo a 25 s sobrevive en A (2,57, t 2,00) siete
   veces más pequeño; con validación 1,50 (t 1,75). Ninguno de los dos es un edge rehabilitado: referencia no
   conforme, fills imputados, t descriptivo sin corrección.
3. **Reloj, ventana de vol y cortes casi no importan** (|efecto| ≤ 1,9 bps, ninguno con t > 2,2). La sensibilidad
   está en la admisión, no en la mecánica.
4. **El positivo histórico no es específico de la cohorte lenta.** Bajo la admisión H, la cohorte rápida también
   da +11,78 (t 8,48) a 25 s; lenta−rápida simétrica es +2,9 bps en H y +0,9 en A. La «lentitud como
   cualificación» apenas aparece una vez neutralizado el lado.
5. **Descomposición.** Bajo H, los eventos admitidos parten con el precio de la orden 5 bps mejor que el último
   trade de Binance, y el movimiento posterior suma. Bajo A, parten 1 bps peor y el movimiento es pequeño o
   negativo. **Opinión de Code sobre el mecanismo, no conclusión de D1:** H admite solo las órdenes que
   desaparecen con un print exactamente a su precio y sin que el mercado la atraviese (10 % de los eventos
   lentos); esa regla excluye por construcción los fills adversamente seleccionados, que son los through. El
   +18,24 sería el markout de los fills que sobrevivieron a esa selección, no el de la cola de la orden.
6. **Tres referencias con precio cero** (±10.000 bps) bastan para llevar la celda H de 5 s de 10,38 a 2,61: el
   defecto de referencias degeneradas que la mesa documentó en agosto está en los datos históricos y es visible.

## 8. Estados

**implementado** (Codex) · **verificado localmente** (46 focales; plan byte a byte) · **auditado
independientemente** (esta lectura, regla de julio incluida) · **ejecutado una vez** (`D1_79_COMPLETE_POST_HOC`,
rc 0, 79 recibos) · **CI: no** · **confirmatorio: no** · **I5 medido como diagnóstico retrospectivo: sí**. STOP,
freezes, pins y conjunto protegido vigentes; ningún cambio de gate ni de calendario. HEAD `7df5280`, sin commit.
Corresponde a la mesa el dictamen.

## 9. Dictamen de la mesa (2026-09-07) y correcciones concedidas

`DICTAMEN_MESA_2026-09-07_I5_D1_79.md`: **I5 cumplida como diagnóstico retrospectivo post hoc; el +18,24 es
reproducible pero su magnitud no sobrevive a la ampliación de admisión especificada (caída del 85,9 % a 25 s,
A−H negativo en 73 de 79 días, VA−VH negativo en 75 de 79); no justifica habilitar operativa; el +18,24 queda
retirado como soporte de una ventaja operable; los residuos positivos de A y VA se conservan como resultado con
sus límites; STOP y no ratificación se mantienen; no queda otra corrida de I5.** El cuerpo de este informe se
mantiene intacto; esta sección lo enmienda con las correcciones de la mesa, todas contrastadas por Code contra
`results.json` y concedidas:

1. **Horizonte del titular (errata de la mesa, no de Code):** el titular era 25 s, como ya constaba en
   `LEDGER.md:1683` y en `PARA_LA_MESA_2026-08-26_ANATOMIA.md:90-98`. La celda primaria fijada sigue siendo
   lento-agitado 5 s y 25 s su compañera; no se asciende ninguna después de ver resultados.
2. **§7.3 era falso como afirmación general.** «|efecto| ≤ 1,9 bps» vale para la celda de 25 s (T−A +0,11, TV−T
   +0,19, Q−A +1,15, muy por debajo de la caída de admisión) pero no para la salida fijada completa: T−A en
   lento-tranquilo 5 s **+2,40** (t 2,12; 75 d); T−A en lento-agitado 1 s **−8,89** (t −0,91); Q−A en
   lento-agitado 60 s **+12,20** (t 1,20). Y en la primaria de 5 s el reloj **cambia el signo del residuo**: A
   −1,08 → T +0,79 (+1,88, t 1,92). Conclusión que se sostiene: efectos acotados en la celda de 25 s, no
   irrelevancia general; relevantes para el signo de un residuo pequeño.
3. **§7.5 excedía lo demostrado.** Descripción incorrecta de H: la rama «parcial» admite órdenes que siguen
   visibles con remanente reducido y un print al precio dentro de la **tolerancia relativa** de la receta, sin
   exigir ausencia de through; solo la rama «fill» exige desaparición con at y sin through. Y un through no
   acredita por sí solo una ejecución adversa de esa orden: los eventos son imputados. Lo que D1 demuestra es
   **sensibilidad material de la media a la regla de admisión**; la explicación por selección es compatible con
   lo observado y no queda concedida en su forma fuerte («excluye por construcción todos los fills adversos»).
   La cola real, las cantidades ocultas, la ejecución propia y el mid no están acreditados por D1.
4. **§6, referencias defectuosas:** son **tres celdas evento-horizonte con referencia no positiva** (la clase
   incluye cero y negativos); los recibos no acreditan tres trades distintos ni precios exactamente cero. Su
   efecto: +7,77 bps a 5 s y −2,63 a 25 s (14,4 % del titular), no despreciable aunque la admisión domine.
5. **§6, descomposición:** la columna «eventos» daba supervivientes de las condiciones (H 2.139; VH 2.133);
   el soporte efectivo de las medias tras el suelo diario es 2.128 y 2.122 en 71 días. En A y VA coinciden
   (40.951 y 40.891 en 79 días). Los soportes de H y A no son los mismos días ni eventos; la descomposición
   describe cada conjunto completo y no atribuye por sí sola la caída al nivel inicial ni al movimiento.
6. **§7.4, lenta−rápida:** en soporte común a 25 s, histórica +2,92 (H) y +0,88 (A); validada +0,20 (VH) y
   +0,12 (VA), 77 días. «El positivo no es exclusivo de lentos» se sostiene; no se deduce equivalencia de
   cohortes ni inexistencia de toda cualificación por persistencia.

Cierre: el encargo histórico I5 termina aquí. Cualquier hito posterior requiere objeto y decisión propios; no
se abre por inercia desde el residuo de D1.
