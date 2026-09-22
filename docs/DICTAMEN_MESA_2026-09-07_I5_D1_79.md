# Mesa · Dictamen de D1/I5 sobre los 79 días de LIT

2026-09-07. **I5 queda cumplida como diagnóstico retrospectivo post hoc. La magnitud
del +18,24 no sobrevive a la ampliación de admisión especificada. El resultado no
justifica habilitar operativa ni rehabilita el programa. STOP y freezes continúan vigentes.**

Esto es un dictamen sobre la evidencia publicada, no un nuevo criterio estadístico de
aprobación o rechazo. No equivale a demostrar que toda estrategia en LIT carezca de
rentabilidad, ni a que todas las órdenes atravesadas tengan markout negativo.

## 1. Cierre y alcance de la revisión

Code auditó y ejecutó una vez el analizador con el plan fijado. Estado
D1_79_COMPLETE_POST_HOC, D1_completed=true, 79 fechas y 1.165.520 eventos de la receta.
La mesa verificó hashes del plan, cortes, resultados, lectura y 79 recibos diarios,
sus enlaces y los valores citados abajo. Leyó el código y documentos anteriores para
contrastar la interpretación. No repitió D1, la reproducción, pruebas o descargas,
ni abrió cuerpos NPZ, crudos o anexos económicos para producir otra lectura.

Anclas en <USER_HOME>/Desktop/Laboratorio/I5_D1_79_20260907_01:

| Pieza | SHA-256 |
|---|---|
| result.json | b49a0572b6e6acf430cb78eb28adc2615e5f8175a079022c7ac7f947d9515237 |
| plan.json | 185dd59c5b45fb97787261887a889edf75e1a4711eec3f484368a695d917d378 |
| quantiles.json | 70912346fd4f1d3638e313479e5b623f9826b377070238f0c59fdc5365c055a5 |
| results.json | 1d19677326e1d2a8fa6137449d3543961d2d67fe638572846aeef61f3c54d8c6 |
| lectura.md | 13607ae5d054786e678ed2458c93f2eaa6ed0c3549f04d7dfc8c4b0d85dcda61 |

La especificación conserva SHA-256
6e358b9c5f127819b8a8b805ade726f1f0bc6d8934b9279d8aa3d574fc5b91d7.
El analizador, sus funciones, pruebas, especificación y resultados no se modifican.
El informe original de Code permanece intacto; estas precisiones se registran aparte.

## 2. Errata de la mesa: horizonte del titular y jerarquía conservada

**El error fue mío:** la especificación atribuye a 5 s el antiguo titular, pero era
25 s. Ya constaba antes de D1 en LEDGER, entrada del 05-07, línea 1683, y en
PARA_LA_MESA_2026-08-26_ANATOMIA.md, líneas 90–98. No es un hallazgo nuevo producido
por buscar el horizonte favorable en los resultados de hoy.

Se retira la justificación «por ser la del antiguo titular». **La celda primaria
que se fijó sigue siendo lento-agitado a 5 s; 25 s conserva su condición de compañero
fijado.** No se cambia el plan ni se asciende ahora 25 s a primaria. Ambas se informan.
Que la errata no cambie los cálculos no la vuelve irrelevante para la interpretación.

## 3. Resultado que sostiene el dictamen

Cohorte lenta, agitado, cortes Q0. Medias equiponderadas de días. En estas cuatro
comparaciones hay los mismos 79 días; los deltas son pareados, no diferencias de
titulares redondeados.

| Horizonte y referencia | Admisión histórica | Con through-con-at | Delta pareado | t descriptivo del delta |
|---|---:|---:|---:|---:|
| 5 s, receta histórica H → A | +2,6101 | −1,0843 | −3,6944 | −0,5505 |
| 5 s, referencia validada VH → VA | +10,3795 | −0,0976 | −10,4772 | −13,4025 |
| 25 s, receta histórica H → A | +18,2368 | +2,5750 | −15,6618 | −6,9043 |
| 25 s, referencia validada VH → VA | +15,6036 | +1,4988 | −14,1048 | −9,8270 |

En la primaria cruda de 5 s el t del contraste es −0,55; no se presenta como una
prueba confirmatoria concluyente. La rama de validación permite ver su contaminación
por referencias no positivas, sin cambiar su horizonte o recalibrar los cortes.

A 25 s la admisión sola reduce la media un **85,8803 %**. A−H es negativo en 73 de
79 días. Validar referencias no elimina esa caída: VA−VH es negativo en 75 de 79.
La misma operación de admisión produce descensos en los otros terciles fijados;
sus soportes son los de las tablas pareadas, no necesariamente los 79 días.

Estos resultados acreditan sensibilidad material de la media de la receta a la regla
de admisión. El residuo positivo a 25 s se conserva en el informe; no se redondea a
cero, no se declara pérdida de signo donde no la hay y no es una estimación de PnL
neto ejecutable. No se inventa un umbral posterior para «rescatar» ese residuo.

Denominadores: hay 132.876 eventos lentos en la receta. H admite 13.368 (10,06 %);
A admite 115.302 (86,77 %), que incluyen **101.934 incorporaciones**. Son eventos
imputados de esta receta, no porcentajes de todas las órdenes o fills verdaderos.
En lento-agitado a 25 s: H tiene 4.413 finitos; A 58.784, de los cuales 54.371 son
incorporados. La ampliación no iguala artificialmente masas: esa diferencia es su objeto.

## 4. Correcciones y límites de la interpretación de Code

### 4.1 Admisión no equivale a todas las órdenes atravesadas ni a una cola identificada

A incorpora exclusivamente through-con-at; conserva fuera los through sin at.
El código congelado de julio, confirm_runner.run_day, admite históricamente:

- Parciales: la orden sigue visible, baja su remanente y hay un print al precio
  dentro de la tolerancia relativa. Esta rama no exige ausencia de through.
- Desapariciones con at y sin through: el estado histórico denominado fill.

Por tanto, «H solo admite órdenes que desaparecen sin que el mercado las atraviese»
es falso como descripción de H. Tampoco at significa igualdad binaria exacta de
precios: se calcula con la tolerancia relativa de la receta.

La regla de desaparición sí selecciona por lo que ocurrió dentro del intervalo.
El contraste prueba cuánto altera el resultado ampliar esa admisión. **No demuestra
que cada through sea un fill real adversamente seleccionado, ni identifica por sí solo
un mecanismo causal o el markout de la cola de una orden.** La cola real, las cantidades
ocultas, la ejecución propia y el mid de referencia no aparecen acreditados por D1.
La explicación de selección es compatible con lo observado; su formulación fuerte
como exclusión de todos los fills adversos «por construcción» no queda concedida.

### 4.2 Reloj, vol y cortes: efectos acotados en una celda, no irrelevancia general

En lento-agitado a 25 s, los efectos pareados T−A, TV−T y Q−A son respectivamente
+0,1102, +0,1924 y +1,1534 bps, sobre sus soportes fijados. Son menores que la caída
de admisión en esa celda. Esa es la conclusión que se sostiene.

La frase «ningún efecto supera 2 bps» no vale para toda la salida fijada:

- T−A en lento-tranquilo a 5 s: **+2,4019 bps**, 75 días.
- T−A en lento-agitado a 1 s: **−8,8871 bps**, horizonte secundario ya fijado.
- Q−A en lento-agitado a 60 s: **+12,2012 bps**, también ya fijado.

Incluso en lento-agitado a 5 s, T−A = +1,8762 mueve la media de −1,0843 a +0,7919:
es relevante para el signo pequeño residual. No demuestra rentabilidad; impide llamar
irrelevante al reloj. No se encarga una nueva combinación de ramas tras ver esto.

### 4.3 Cohorte y lado: conservar los soportes y no confundir falta de evidencia con igualdad

En soporte común de las dos cohortes, ambos lados y ambas ramas, a 25 s:

| Referencia | Lenta−rápida histórica | Lenta−rápida ampliada | Días |
|---|---:|---:|---:|
| Histórica, H/A | +2,9208 | +0,8816 | 77 |
| Validada, VH/VA | +0,1951 | +0,1231 | 77 |

La afirmación «el positivo no es exclusivo de lentos» se sostiene: la cohorte rápida
tiene un nivel positivo histórico. No se deduce que ambas cohortes sean equivalentes
o que toda cualificación por persistencia sea inexistente.

En el mismo soporte común, la media simétrica lenta a 25 s es −0,5595 en A y −1,0029
en VA. Sus tablas con soporte propio de 79 días dan −0,7324 y −1,1645. No se mezclan
estos dos soportes al citar niveles o restarlos de H/VH.

### 4.4 Descomposición: A es el conjunto ampliado; sus soportes no son los de H

El +5,1503 de orden–trade en H y el −0,9728 en A describen **cada conjunto completo**
en su soporte común a cinco horizontes. El segundo no es una medida aislada de los
eventos incorporados. H y A tampoco tienen aquí los mismos días o eventos.

H: 2.139 eventos sobreviven las condiciones, pero **2.128 entran efectivamente en
las medias de 71 días** tras el suelo diario. A: 40.951 eventos y 79 días.
VH: 2.133 sobreviven, 2.122 entran en 71 días. VA: 40.891 en 79 días.
La columna «eventos» del informe de Code usa supervivientes; conviene distinguirla
del soporte efectivo de las medias que acompaña.

Esta descomposición no atribuye por sí sola la caída de A−H al nivel inicial, al
movimiento posterior o al basis. Su referencia es un trade entre venues, no un mid.

### 4.5 Referencias defectuosas: celdas, causas y magnitud

Los recibos acreditan **tres celdas evento-horizonte con referencia no positiva**
en H lento-agitado a 5 s; validarlas cambia la media +7,7694 bps. A 25 s hay una y
el efecto es −2,6332 bps, aproximadamente el 14,4 % del titular. No se califica de
inexistente o despreciable, aunque la admisión siga dominando la caída a 25 s.

La clase no_positiva incluye cero y negativos. El conteo no acredita por sí solo que
sean tres trades distintos ni tres precios exactamente cero. La revisión de mesa
no reabre anexos para aumentar esa afirmación: conserva el nivel de evidencia de
los recibos. En todo caso, validar esas referencias no sana el carril trade/mid.

## 5. Decisión y cierre operativo

1. **Aceptar el cierre de I5/D1** como diagnóstico retrospectivo completo según el
   plan fijado. No queda pendiente otra corrida de I5 sobre este panel.
2. **Retirar el +18,24 como soporte de una ventaja operable o robusta frente a la
   admisión especificada.** Conservar el número como resultado histórico reproducido
   y conservar también los residuos positivos de A/VA, con todas sus limitaciones.
3. **Mantener la no ratificación y STOP.** No se autoriza producción, cambio de gate,
   lectura protegida, ajuste del analizador o nueva búsqueda para recuperar el signo.
4. **Conservar el expediente completo y esta errata separada.** La especificación
   original, su prioridad de 5 s, el plan y las siete ramas publicadas permanecen
   tal como estaban antes de la lectura. No se modifica el informe de Code.

Este dictamen cierra el encargo histórico. Cualquier hito científico posterior requiere
un objeto y una decisión propios; no se abre por inercia desde el residuo de D1.

Fuentes del dictamen: resultados y recibos anclados arriba;
[informe de Code](RESULTADO_CODE_2026-09-07_I5_D1_79.md),
[especificación congelada](ESPEC_MESA_2026-09-07_D1_79_DIAS.md),
[registro histórico del titular](LEDGER.md?plain=1#L1683)
y receta de julio en el commit 74f0d6069efdc7be73693dd18ca39e9167892202.
