# Code → Mesa y Codex · 2026-09-06 · Censo de cobertura I5 COMPLETO: 149/149 celdas en dos ejecuciones con procedencia separada

**Resultado: `CENSUS_QUERIES_COMPLETE`, rc 0, en la continuación; combinado con la ejecución parcial, las 149
celdas del manifiesto tienen presencia L3 en checkpoint y en tick y metadatos de cobertura válidos.** Este
documento sustituye como resultado vigente a `RESULTADO_CODE_2026-09-06_I5_CENSO.md`, que se conserva intacto
como registro de la parada. Presencia no es integridad intradía. Nada se declara ratificable.

## 0. Correcciones aceptadas del relevo de continuación

Cuatro precisiones de la mesa al informe parcial, todas ciertas: LIT tenía 44 respuestas de cobertura, no 45;
las fechas de reproducción pendientes eran cuatro, incluido el 29 de junio; las fechas compartidas con hueco
eran seis aunque el texto decía «cinco»; y las duraciones incluyen 11 y 21 minutos, no solo 12–20. El
`TIMEOUT` del recibo era el parámetro de 60 s, no una espera medida; la continuación registra ya el tiempo
monotónico de cada consulta.

## 1. Identidad de las dos ejecuciones

| | ejecución 1 (parcial) | ejecución 2 (continuación) |
|---|---|---|
| carpeta | `Desktop\Laboratorio\I5_CENSO_20260906_01` | `Desktop\Laboratorio\I5_CENSO_20260906_02` |
| celdas | 0–114 (115 recibos; la 114 con tick `TIMEOUT`) | 114–148 (35 recibos; la 114 hereda el checkpoint válido con `reused_from`) |
| instrumento | `i5_censo_cobertura.py` `f71ae8e3…` (P1 aplicado) | `b4409cdf…` (continuación; verifica por hash el resumen padre `ec9696a2…` y la lista de 115 celdas `02890b23…`) |
| UTC | 16:32:47 → 16:37:11 | 17:20:55 → 17:22:18 |
| llamadas autenticadas | 346 | 106 (34 checkpoint + 35 tick + 35 cobertura + 2 usage) |
| estado | `PARTIAL_CENSUS_STOPPED_AT_FIRST_ERROR` | `CENSUS_QUERIES_COMPLETE` |

HEAD `7df5280` en ambas; todo el instrumento es WIP sin commitear. Máquina reiniciada, sin OneDrive.

## 2. Cuenta Build

| | usados | restantes | peticiones |
|---|---|---|---|
| antes de la ejecución 1 | 1 | 79.999.999 | 48 |
| entre ejecuciones | 230 | 79.999.770 | 393 |
| después de la ejecución 2 | 299 | 79.999.701 | 498 |

Gasto del censo: **298 créditos** = 298 presencias a 1 crédito. Las 149 coberturas genéricas no movieron el
saldo ni llevan cabecera de crédito. La cabecera `x-credits-used` es un contador acumulado con desfase +9
sobre `usage`, registrado sin explicar.

## 3. Presencia por resolución, 149 celdas

| símbolo | celdas | checkpoint INDICIO | tick INDICIO | ausencias | primer snapshot del día, s tras 00:00 UTC (min / mediana / max) |
|---|---|---|---|---|---|
| LIT | 79 | 79 | 79 | 0 | 5 / 86 / 202 |
| DOGE | 70 | 70 | 70 | 0 | 0,2 / 94 / 202 |

El tick de LIT 2026-05-01, que expiró a 60 s en la ejecución 1, respondió en 0,75 s en la 2: el timeout fue
transitorio. Las 35 consultas tick nuevas tardaron entre 0,64 y 0,87 s.

## 4. Huecos declarados por el proveedor en el archivo L3

`historical_coverage`, `total_records`, `earliest` y `latest` son globales del símbolo (LIT 100 %, DOGE
99,7 % en todas sus celdas); solo los intervalos de `gaps` responden a la ventana del día. Un array vacío no
certifica continuidad. Inventario completo, hora UTC de inicio–fin y minutos:

**LIT — 14 días, 17 intervalos, 257 minutos**

| día | intervalos |
|---|---|
| 03-08 | 11:00–11:17 (17) |
| 03-27 | 19:42–19:55 (13) |
| 03-28 | 18:33–18:53 (20) |
| 03-29 | 10:59–11:17 (18) |
| 04-01 | 22:30–22:42 (12) |
| 04-02 | 14:45–15:04 (19) · 15:10–15:23 (13) · 16:04–16:15 (11) · 18:17–18:28 (11) |
| 04-05 | 12:59–13:17 (18) |
| 04-08 | 23:30–23:42 (12) |
| 04-12 | 12:58–13:16 (18) |
| 04-24 | 09:59–10:18 (19) |
| 04-27 | 08:15–08:27 (12) |
| 05-10 | 12:58–13:10 (12) |
| 05-13 | 18:53–19:14 (21) |
| 05-17 | 12:59–13:10 (11) |

**DOGE — 8 días, 8 intervalos, 134 minutos**

| día | intervalo |
|---|---|
| 03-08 | 10:58–11:15 (17) |
| 03-29 | 10:59–11:15 (16) |
| 04-05 | 13:00–13:14 (14) |
| 04-12 | 12:59–13:14 (15) |
| 04-24 | 09:57–10:16 (19) |
| 04-27 | 08:14–08:25 (11) |
| 05-13 | 18:51–19:12 (21) |
| 05-30 | 12:57–13:18 (21) |

**Siete fechas coinciden en los dos símbolos con el mismo intervalo horario** (03-08, 03-29, 04-05, 04-12,
04-24, 04-27, 05-13): huecos de la captura del proveedor, no del mercado. Cinco de ellos caen en la franja
12:57–13:18 UTC y otros dos cerca de las 11:00, lo que sugiere una ventana de mantenimiento; es una
observación, no una causa acreditada. No se sabe todavía si tick y checkpoint comparten cada hueco ni cuántos
snapshots faltan: eso lo mide el descargador.

## 5. Las ocho fechas de reproducción

| fecha | checkpoint | tick | cobertura | huecos L3 declarados |
|---|---|---|---|---|
| 03-06 | INDICIO | INDICIO | válida | 0 |
| 03-27 | INDICIO | INDICIO | válida | 1 (13 min, 19:42–19:55) |
| 04-08 | INDICIO | INDICIO | válida | 1 (12 min, 23:30–23:42) |
| 04-19 | INDICIO | INDICIO | válida | 0 |
| 05-02 | INDICIO | INDICIO | válida | 0 |
| 05-14 | INDICIO | INDICIO | válida | 0 |
| 06-11 | INDICIO | INDICIO | válida | 0 |
| 06-29 | INDICIO | INDICIO | válida | 0 |

Las ocho se conservan tal cual: un hueco declarado no cambia la muestra.

## 6. Lo que sigue, según lo aprobado

1. Codex completa su inventario `HUECOS_L3_PARA_DESCARGA_20260906_01.json` con las 35 celdas nuevas: ya no
   queda ninguna con `reported_intervals=null`. El agregado de Code está en
   `I5_CENSO_20260906_02\RESUMEN_CODE_censo_combinado.json`.
2. Descargador con custodia de las 149 celdas, checkpoint y tick separados, páginas a disco fuera de OneDrive
   con hashes y cadena de cursores, sin recorte por coste; contraste de cada intervalo declarado con los
   timestamps descargados, por resolución, y búsqueda de huecos no anunciados. Code audita antes de la
   descarga larga y la ejecuta.
3. Después, el productor de los ocho días y el contraste de reproducción contra los npz originales; solo
   entonces los 71 restantes e I5 como diagnóstico retrospectivo.

Estados: **ejecutado** (dos veces, con procedencia separada y sin repetir consultas válidas) · **verificado
localmente** (recibos íntegros; agregado por programa) · **auditado independientemente**: no (informe del
ejecutor) · CI: no aplica. STOP, freezes y pins vigentes.
