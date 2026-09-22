# Mesa · D1 sobre los 79 días de LIT: especificación retrospectiva

2026-09-07. Se cierra la reproducción numérica exacta de ocho campos en ocho fechas,
según los recibos de `I5_REPRODUCCION_OCHO_20260907_01` y la auditoría de mesa. Las cinco
correcciones están aceptadas en §6 de `RESULTADO_CODE_2026-09-07_I5_REPRODUCCION_OCHO.md`.
No se repite esa reproducción. Esta especificación se fija antes de ejecutar D1, pero
después de conocer el hallazgo, sus defectos y los conteos de los ocho días: **post hoc,
retrospectiva, no confirmatoria ni prerregistro del eco**. No modifica STOP o F′.

## 1. Pregunta y alcance

Cuánto cambian la media y el t descriptivo de la receta histórica al admitir sus órdenes
`through-con-at` como fills. No se supone que el cambio sea negativo, que la media quede
entre los resultados previos, ni que admitir todos los through proporcione una cota
matemática. Ninguna de esas desigualdades se desprende de las máscaras de admisión.

Población fija: los **79 días LIT** del manifiesto `tools/i5_celdas_20260906.json`, hash
`0d913aae3a16365501e9a60cdc74fc473c58526496bc53a55f97d6f0285ab0ce`, del 06-03 al 29-06.
No es una selección de todos los días naturales de ese intervalo. Los ocho ya producidos
se incorporan mediante sus recibos, sin volver a descargarlos ni ejecutar su differ.
Los otros 71 requieren 3.408 claves CHD: 24 horas × dos fuentes por fecha; su L3 ya está
custodiada en A. DOGE, LIT desde 30-06 y WTI no entran en este diagnóstico.

Los originales canónicos y sus reglas se conservan. Los 71 se reconstruirán con la misma
receta histórica y se compararán también contra sus originales antes de agregarlos a D1.
Una diferencia impide declarar el panel de 79 reproducido: se devuelve su atribución;
no se intercambia el original por el nuevo ni se elimina el día para lograr igualdad.

## 2. Cuatro ejes que no se deben mezclar

La última frase de §6 del informe de Code vuelve a juntar «cambio de admisión (fechar en
el primer at)». **Se corrige aquí: admitir y cambiar el reloj son operaciones distintas.**
No se altera el texto de Code. Se definen ramas con una única diferencia respecto a su
comparador; todas se publican, sin elegir la más favorable:

| Rama | Admisión | Reloj del evento / vol20 | Cortes de vol | Referencia futura |
| --- | --- | --- | --- | --- |
| H | `tipo<=1` | Julio / julio | Q0 | Julio sin validación |
| A | H más `tipo==2 & thr_con_at` | Julio / julio | Q0 | Igual que H |
| T | Igual que A | `t_at` solo para los incorporados / vol20 de julio conservada | Q0 | Misma búsqueda, objetivo desde el reloj T |
| TV | Igual que T | Reloj T / vol recalculada en ese reloj con fórmula histórica | Q0 | Igual que T |
| Q | Igual que A | Igual que A | QA recalculados sobre A | Igual que A |
| VH | Igual que H | Igual que H | Q0 | Validación R1–R3 sobre el candidato seleccionado |
| VA | Igual que A | Igual que A | Q0 | Misma validación que VH |

Contrastes: **A−H** (principal, admisión sola), T−A (reloj del markout), TV−T (ventana
de vol), Q−A (cortes), VA−VH (admisión con referencia validada), VH−H y VA−A (validación).
No se añade por defecto una rama que cambie todo a la vez. T es un puente analítico:
su vol heredada puede contener datos posteriores al at; no es una propuesta operable.
TV corrige ese anclaje con la fórmula antigua, no introduce I2. I7 tampoco se introduce.

`thr_con_at` exige through histórico y al menos un at en su intervalo estricto `(t0,t1)`;
se admiten todos esos eventos, sin exigir un orden particular entre at y through, sin
escoger una combinación después de ver su markout. `slow`, lado, owner, precio y orden
del evento se heredan. No se reescribe `tipo` o `t_fill` en el artefacto base.

En T/TV se usa el primer at guardado, incluso si es posterior al primer through. Un
timestamp ausente/inconsistente para un flag verdadero es error de integridad y para,
no razón para inventarlo o eliminar ese evento. La necesidad de prints posteriores para
la clasificación sigue existiendo: ninguna rama acredita fills verdaderos o elimina
por completo la selección con información posterior.

## 3. Estratos, horizontes y soportes

Q0 son los cuantiles lineales 1/3 y 2/3 de `vol20` finita entre eventos H **lentos**, sobre
los 79 días, reproduciendo la regla histórica y su requisito de más de 100 valores.
No se calculan mirando markouts. Se guardan valor, dtype, método, conteo y hash de origen
antes de agregar resultados. `tranquilo: v<=q1`; `medio: q1<v<=q2`; `agitado: v>q2`.
Vol no finita queda fuera de terciles con conteo explícito. Q0 se aplica también a rápidos
y a eventos nuevos. QA cambia únicamente el pool a A lento y conserva el mismo método.
Un cuantil degenerado o una celda vacía se informa; no se fuerza una partición en tercios.

La celda principal de referencia es **LIT lento, agitado, 5 s**, por ser la del antiguo
titular. Se informa simultáneamente su compañero de 25 s, y ambas duraciones en los tres
terciles. Los horizontes 1,10,60 s ya fijados son secundarios; no reemplazan 5/25 si estos
son incómodos. Las ocho fechas no se usan como nuevo piloto para escoger ramas o cortes.

Por rama/celda se publican admisiones H, incorporaciones through-con-at, población lenta
y rápida, lados, días previstos/producidos, horas disponibles, referencias ausentes y
rechazadas, vol no finita, días por debajo del suelo y motivos. El porcentaje de todos los
through sobre todos los eventos no sustituye esos denominadores específicos de I5.

## 4. Estimador y comparación

Se conserva la media por día de eventos con markout finito (mínimo tres), y después la
media equiponderada entre días. No se pondera por número de eventos, wallets o `qty`.
Se informan `k`, número de eventos, dispersión diaria, `effective_n_autocorr` de la casa
y `t = media / (sd_diaria / sqrt(n_eff))`, como descriptores históricos; no se presenta
ese t como inferencia confirmatoria validada. Con menos de cuatro días, sd cero o
n_eff<=1, el t se declara no disponible; no se rellena ni se interpreta vacío como cero.

Cada rama tiene primero su tabla con soporte propio, para mostrar la composición. El
contraste principal A−H se calcula además **pareado por día en la intersección** de días
con al menos tres valores finitos en ambas ramas, con ambos niveles recalculados sobre
esa misma intersección y la serie de diferencias diarias. Igual para los otros contrastes.
Se lista exactamente qué días entran/salen y por qué. No se resta el +18,24 redondeado
de una media obtenida en otro soporte. No se iguala artificialmente el número de eventos:
la ampliación de admisión es precisamente el objeto de A−H.

Se publican magnitud y signo de cada cambio, incluso si A−H es positivo. Media corregida
no positiva o inversión de signo documentan sensibilidad descriptiva del signo; conservar
signo positivo no acredita robustez general, y un t no significativo no prueba ausencia
de efecto. No hay umbral nuevo para declarar éxito del programa, BHY nuevo, búsqueda de
subgrupos ganadores ni cambio de gate/calendario derivado de esta lectura.

## 5. Referencia, lado y nivel: diagnósticos delimitados

VH/VA conservan el trade Binance más cercano y la tolerancia `max(Δ/2,500 ms)`. Validan
**ese candidato** con `analysis.ref_valida.clasificar` y el llamador R1–R3 vigente: precio
no finito/no positivo y referencia no finita/no positiva o markout absoluto >=9.000 bps.
No buscan el siguiente trade válido. Se registran todas las causas, sin imputar precios,
sin estimar invalidez desde una banda escogida alrededor del markout observado. Las ramas
H/A/T/TV/Q conservan explícitamente el defecto histórico para aislar sus cambios.
La comparación de validación usa los mismos Q0; no recalibra terciles al perder referencias.

Todas las ramas siguen usando **trades Binance, no mid**. R1 no resuelve ese incumplimiento.
No se reutiliza el arnés antiguo que detecta corrupción y para como si fuera un estimador
limpio, ni se elimina su parada para ejecutar D1. Las funciones compartidas y sus hashes
se fijarán en el plan de análisis antes de su ejecución, sin relajar reglas.

Lado-neutral: para H/A y VH/VA, medias diarias bid y ask por cohorte con >=3 eventos
finitos **en cada lado**; simétrico `(ask+bid)/2` y antisimétrico `(ask-bid)/2`. Lenta−rápida
se compara sobre días comunes a las cuatro combinaciones lado/cohorte y a ambas ramas,
con Q0 común. Se publica mezcla de lados y masa perdida. Es neutralización de mezcla,
no prueba de habilidad ni corrección suficiente de basis/selección.

Con referencia inicial válida y disponible se descompone, sobre los mismos eventos:
`mo = s*(ref_t-px)/px*1e4 + s*(ref_futura-ref_t)/px*1e4`, donde s=+1 bid, −1 ask.
`ref_t` sigue siendo el último trade estrictamente anterior en <=500 ms. Es desviación
orden–trade entre venues, no basis medido contra un mid. No se reemplaza ref_t ausente
por el precio de la orden, ni se mezcla la muestra con referencia inicial disponible con
la principal. La curva 1,5,10,25,60 se presenta también en soporte de eventos/días común
a todos los horizontes, con la pérdida de masa visible. No se atribuye causalidad a la
erosión ni se elige el horizonte que dé el mejor signo. Este bloque no redefine A−H.

## 6. Custodia, faltantes y orden operativo

Las tres horas sin resolver del 29-06 quedan como están, con trazabilidad. Las claves nuevas
que devuelvan 404 también se conservan como indeterminadas; no se reconsultan ni se tratan
como mercado vacío. Bordes temporales, unidades distintas, ficheros vacíos o errores de QA
se devuelven para revisión antes de producir; no se autorizan reparaciones silenciosas.
Las diferencias de cobertura se informan, no se usa un resultado de markout para admitir
un fichero o sustituir un día. No se añaden horas vecinas a la ventana protegida.

1. Codex entrega esta especificación y el custodio **solo de los 71 días nuevos**. Code
   audita el incremento y ejecuta una vez la custodia dentro de D1 autorizado.
2. Se revisa el inventario resultante, antes de abrir resultados. Con sus hashes se
   concreta el productor restante y el panel de 79, enlazando los ocho existentes.
3. Se implementan y auditan las ramas/estimadores anteriores con fixtures sintéticos;
   Code ejecuta producción restante y, tras concordancia, el análisis con plan fijado.
   Los cambios necesarios de reloj/referencia se guardan en anexos con procedencia, sin
   reejecutar el differ de los ocho ni sobrescribir sus campos históricos.

Este documento **no afirma que el productor de 71 días o el analizador D1 estén ya
implementados**. La entrega inmediata hace ejecutable la adquisición pendiente; las
huellas de esa custodia son una entrada necesaria de la siguiente entrega. No se pide
a Manuel otra autorización metodológica ni se amplía el objeto por disponer de saldo.
