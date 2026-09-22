# Code → Mesa y Codex · 2026-09-06 · Censo de cobertura I5: ejecución única — PARCIAL por timeout en la celda 115 de 149

**Resultado: `INDETERMINADO` / `PARTIAL_CENSUS_STOPPED_AT_FIRST_ERROR`, rc 4.** 115 celdas medidas (DOGE 70/70,
LIT 45/79), 346 llamadas autenticadas en 4 min 24 s, sin reintentos ni ampliación. Paró en la celda 114
(LIT 2026-05-01) porque la petición de presencia **tick** no recibió respuesta HTTP en 60 s; la de checkpoint
del mismo día había respondido (primer snapshot a las 00:00:30 UTC). Un timeout no es ausencia. Quedan sin
censar el tick de ese día y las 34 celdas LIT del 2026-05-02 al 2026-06-29. Nada se declara ratificable.

## 1. Identidad de la ejecución

| campo | valor |
|---|---|
| comando | el del relevo `PARA_CODE_2026-09-06_I5_CENSO_P1.md`, desde `qs/`, `--key-file` de Build, `--out I5_CENSO_20260906_01` |
| HEAD / instrumento | `7df5280`; `i5_censo_cobertura.py` `f71ae8e3…` (re-verificado en el instante del arranque), `i5_oxa_io.py` `028c8268…`, `etapa0_validador.py` `a3f60606…`, manifiesto `0d913aae…` |
| inicio / fin (UTC) | 16:32:47 → 16:37:11 |
| máquina | reiniciada, `OneDrive.exe` ausente, 115 GB de commit libres; Codex vivo, árbol no tocado |
| recibos | `Desktop\Laboratorio\I5_CENSO_20260906_01\receipt.json` + 115 `cell_NNN_*.json` + `RESUMEN_CODE_censo.json` (agregado de Code, solo lectura) |
| log | `scratchpad/censo_i5_20260906.log` de la sesión de Code |

## 2. Cuenta y créditos

| | límite | usados | restantes | peticiones |
|---|---|---|---|---|
| antes | 80.000.000 | 1 | 79.999.999 | 48 |
| después | 80.000.000 | 230 | 79.999.770 | 392 |

Delta de saldo **229** = 115 celdas × 2 presencias − 1 (la presencia tick de la celda 114 no llegó a
contarse). **Las llamadas de cobertura genérica no llevan cabecera de crédito ni mueven el saldo: son
gratuitas.** La cabecera `x-credits-used` de las presencias sube de uno en uno (11 → 239): es un contador
acumulado, no un coste por petición; lleva un desfase constante de 9 respecto a `credits_used` de `usage`,
que se registra sin explicar (misma familia que el «10 frente a 1» de la etapa 0).

## 3. Presencia por resolución (lo que la etapa 1 necesita)

| símbolo | celdas medidas | checkpoint INDICIO | tick INDICIO | tick sin medir | primer snapshot del día, s tras 00:00 UTC (min / mediana / max) |
|---|---|---|---|---|---|
| DOGE | 70 / 70 | 70 | 70 | 0 | 0,2 / 94 / 202 |
| LIT | 45 / 79 (03-06 → 05-01) | 45 | 44 | 1 (05-01, TIMEOUT) | 10 / 101 / 167 |

Ninguna `AUSENCIA_VALIDA`: todos los días medidos tienen al menos un snapshot en checkpoint, y en tick
salvo el no medido. Una página positiva acredita presencia, no cobertura intradía.

## 4. Cobertura genérica del proveedor: qué es del día y qué no

114 de 115 respuestas válidas (la de la celda 114 no se pidió porque la corrida paró antes). Lectura de los
recibos, que corrige la expectativa del plan:

- **`historical_coverage`, `total_records`, `earliest` y `latest` son del SÍMBOLO, no del día:** DOGE
  devuelve 99,7 % y 81.094 registros L3 en las 70 celdas, idénticos; LIT devuelve 100,0 % en las 45.
  `from/to` no acota esas cuatro métricas. No sirven como cobertura diaria.
- **Los `gaps` sí son del día** (`from/to` acota la detección): varían por celda.
- `earliest` L3: DOGE 2026-03-05 03:33 UTC, LIT 2026-03-05 17:29 UTC. `completeness` es de las últimas 24 h.

Huecos declarados dentro de los días medidos (cadencia de checkpoint ≈ 2,9 min; un hueco de 12–20 min son
unos 4–7 checkpoints ausentes):

| símbolo | días con huecos | detalle (día: huecos, minutos) |
|---|---|---|
| LIT (45 días) | 11 | 03-08: 1, 17 · 03-27: 1, 13 · 03-28: 1, 20 · 03-29: 1, 18 · 04-01: 1, 12 · **04-02: 4, 54** · 04-05: 1, 18 · 04-08: 1, 12 · 04-12: 1, 18 · 04-24: 1, 19 · 04-27: 1, 12 |
| DOGE (70 días) | 8 | 03-08: 1, 17 · 03-29: 1, 16 · 04-05: 1, 14 · 04-12: 1, 15 · 04-24: 1, 19 · 04-27: 1, 11 · 05-13: 1, 21 · 05-30: 1, 21 |

Cinco fechas de hueco coinciden en los dos símbolos (03-08, 03-29, 04-05, 04-12, 04-24, 04-27): huecos
del archivo del proveedor, no del mercado. De las ocho fechas de reproducción fijadas, dos tienen hueco
declarado (03-27 y 04-08) y tres no están censadas todavía (05-02, 05-14, 06-11).

## 5. La parada

`cell_114_LIT_2026-05-01.json`: checkpoint HTTP 200, 68.782 B, INDICIO; **tick: sin respuesta en 60 s
(`TIMEOUT`)**. La vecina 04-30 respondió al tick en ~1 s con 69.135 B. Es la misma clase de latencia que se
anticipó para la cobertura genérica, que no se manifestó allí (las 114 coberturas fueron rápidas), sino en
una presencia tick. Por contrato, un fallo en una presencia detiene el censo y no se reintenta. Se
conserva la evidencia; no se ha repetido nada.

## 6. Lo que propongo a la mesa

1. **Completar el censo sobre las 35 mediciones que faltan** (tick de LIT 05-01 y las 34 celdas LIT
   05-02 → 06-29) en una segunda ejecución autorizada, con un `--resume-from 114` explícito o un
   manifiesto-tramo, en un directorio nuevo, y con timeout de 120 s también en las presencias. No es
   ampliación de alcance: es el mismo manifiesto aprobado. Codex implementa el tramo; Code audita el diff y
   ejecuta.
2. **Descargador:** los recibos ya dicen lo que hay que custodiar: checkpoint y tick presentes en todos los
   días medidos; los huecos declarados por día son la lista de tramos que la descarga debe verificar
   explícitamente en vez de suponer continuidad.
3. Registrar en el contrato del descargador que `historical_coverage` y `total_records` son globales del
   símbolo y no se citan como cobertura diaria.

Estados: **ejecutado** (una vez, parcial por contrato) · **verificado localmente** (recibos íntegros,
agregado por programa) · **auditado independientemente**: no (esto es el informe del ejecutor) · CI: no aplica.
