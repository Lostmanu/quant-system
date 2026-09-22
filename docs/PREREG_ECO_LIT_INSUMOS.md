# INSUMOS PARA EL PREREG DEL ECO (LIT) — fortalecimientos pre-dato de la auditoría A11

**Estado: BORRADOR de insumos, NO congelado.** Este documento acumula los fortalecimientos que deben
entrar en el prereg del ECO de julio (el forward de la apelación del 5s), a congelar con MESA FRESCA
antes de que el eco tenga masa. Origen: auditoría A11 (mesa + re-auditoría independiente de 5 agentes,
workflow `wf_071d788c`, 2026-07-05). Regla: NINGUNO se aplica retroactivamente a lo ya leído; todos
endurecen o aclaran el eco. "Aflojar NO."

Cada ítem: `fichero:línea` · qué · fix · por qué no invierte lo leído.

## Correcciones de código a aplicar ANTES del eco (fortalecimientos)

### I1 — [de M1 / N2] familia BHY ciega al signo → orientarla
- **Dónde:** `confirm_screen.py:133` y `pilot_screen.py:79` alimentan `_p_from_t_onesided(st["t"])` que usa
  `abs(t)` (`maker_capa2_screen.py:37`). La orientación se recupera SOLO después del BHY.
- **Fix:** pasar la dirección esperada por celda (p=1.0 si el efecto va contra la hipótesis de la celda,
  como `maker_capa2_screen.py:124`/OK7), o separar la familia BHY en dos (positiva/negativa).
- **No invierte:** el decisivo fue INCONCLUSO por discrepancia de horizontes (no por sig); el piloto se
  RE-VERIFICÓ con familia orientada (`verify_pilot_bhy_oriented.py`) y el sig-BHY de LIT es idéntico —
  ninguna celda cambia. Es hazard PROSPECTIVO (en el eco una celda de signo contrario podría heredar sig).

### I2 — [de N1, bug NUEVO que la mesa se dejó] `trailing_vol` comprime minutos vacíos
- **Dónde:** `confirm_runner.py:42-48`. Construye `close[]` por minuto, `c = close[isfinite]` ELIMINA
  huecos, `np.diff(np.log(c))` toma retornos sobre el array comprimido → un salto a lo largo de un hueco
  de k minutos se cuenta como retorno de 1 min → **infla la vol de tramos ilíquidos**.
- **Impacto:** la vol es el EJE que clasifica el tercil AGITADO del §3. Fills ilíquidos-pero-tranquilos
  pueden empujarse al bucket agitado. Sistemático (correlaciona con iliquidez), no aleatorio.
- **Fix (propuesto):** escalar cada retorno por `sqrt(Δminutos)` (dividir `diff(log(c))` por
  `sqrt(diff(índice_minuto))`) para normalizar a vol-por-minuto real. NO usar LOCF (inyecta ceros,
  deflacta, sobre-corrige). Reportar en acta cuántas ventanas tenían huecos.
- **No invierte lo LEÍDO** (verificado adversarial, `INVIERTE=False`): el argumento de dirección es que la
  contaminación METE fills tranquilos (markout ~0) en la celda AGITADO → DILUYE el +18,24 en vez de
  fabricarlo. **CAUTELA de la mesa (2026-07-05): "un fix lo haría igual o más fuerte" es una PREDICCIÓN
  sobre el propio resultado, y esta casa no firma predicciones sobre su resultado sin dato.** El fix entra
  al eco con su dirección de efecto declarada como **HIPÓTESIS A VERIFICAR, no hecho establecido**: si al
  aplicarlo el +18 BAJA en vez de subir, eso es INFORMACIÓN, no un accidente. "Verificamos que diluye lo
  leído" ≠ "sabemos que el fix lo refuerza" — son afirmaciones distintas; solo la primera está probada.
  Mismo patrón menor en `pilot_runner.daily_vol` (rejilla 5-min fija, menos expuesto).

### I3 — [de N4] bootstrap §4 construye el nulo de `slow_ev` pero mide el observado de `dec`
- **Dónde:** `confirm_screen.py:183` usa `m = (days_arr==dd) & slow_ev` (incluye through, tipo=2) para
  `owner_first`/probabilidades del nulo, mientras `fills_by_day` (180) y el observado (188) usan `dec`
  (solo parcial+fill). Pool del nulo ≠ población observada.
- **Fix:** construir `owner_first` desde `dec`, no desde `slow_ev` (línea 183 → `& dec`).
- **No invierte:** §4 es decisorio-secundario; el veredicto §3 no depende. Pero contamina el mismo
  estadístico que M2 cuestiona ("rotación mecánica").

### I4 — [de M2] bootstrap §4 mide fracción de WALLETS, no de VOLUMEN
- **Dónde:** `confirm_screen.py:191-192`. El 61,9% del titular del piloto era de VOLUMEN; el bootstrap
  compara fracción de wallets-de-un-día. Internamente consistente pero mide otra cosa que la nombrada.
- **Fix:** (a) reetiquetar honestamente "fracción de wallets, no de volumen" (ya hecho en espíritu), o
  (b) añadir la versión ponderada por fills/volumen. Para el eco: correr AMBAS y reportar las dos.

### I5 — [de N3, a la CARTA §A6] orden through-antes-que-fill = selección sobre correlato del outcome
- **Dónde:** `pilot_observer.py:58` (≡ `confirm_runner.py:88`): `if t_th is not None: THROUGH` se evalúa
  ANTES de `elif t_at: FILL`. Una orden lenta con at Y through en el mismo intervalo → THROUGH (excluida
  de decisión) → sesga la media retenida hacia positivo.
- **Es el SPEC CONGELADO** (prereg pre-declaró through como diagnóstico), NO un bug de código.
- **Fix para el eco = PRUEBA DE SENSIBILIDAD OBLIGATORIA:** cuantificar cuánto se mueve la media/t de LIT
  si los "through-con-at" se re-cuentan como FILL (o etiquetados fill-con-through incluidos en decisión).
  Enmienda fechada al prereg del eco, jamás retroactiva. Ver CARTA_DE_ATAQUE §A6.

### I6 — [de M3 + N-runner] masa perdida por vol-NaN y AMBIGUA persistente sin contar
- **Dónde:** `confirm_screen.py:113` (fills vol-NaN caen fuera de todo tercil sin log) y
  `confirm_runner.py:83` (AMBIGUA persistente no se persiste por símbolo-día más allá del string agregado).
- **Fix:** reportar en el output el nº de fills-decisión con vol-NaN excluidos, y persistir `amb` como
  escalar en el npz. Completitud de acta.

### I7 — [de N-runner MED] `max_gap` desde mediana de diffs de snapshots sin deduplicar
- **Dónde:** `confirm_runner.py:67` `np.diff([s[0] for s in snaps])`; `_snaps_owner` (`wallet_atlas.py`)
  no deduplica → timestamps duplicados de paginación 0xA meten diffs=0 → mediana sesgada a la baja →
  `max_gap` pequeño → más intervalos marcados inválidos → menos masa.
- **Fix:** deduplicar snapshots por timestamp tras el sort, o `np.median(diffs[diffs>0])`.
- **No invierte:** deflacta masa (empuja a INCONCLUSO), no infla el edge.

## Cautelas de estimador (documentar, no necesariamente cambiar)

- **C1 — [N screen.py:25]** `effective_n_autocorr` con series MUY cortas (len 4) puede devolver `n_eff=n`
  si el primer ρ≤0 por ruido (sin descuento). Conservador (nunca `n_eff>n`), pero al filo del suelo puede
  dejar pasar un t sin descuento real. **Para el eco:** considerar suelo de ≥8 días (no 4) en celdas que
  VOTEN el decreto, y/o reportar `n_eff` junto a `n` crudo. (§5 corregido ya usa ≥4 como §3.)
- **C2 — [N lighter_adapter.py:46]** `_assert_range` valida solo `arr[0]`. Validar min y max (barato).
- **C3 — [N flow_informativeness.py:68]** VWAP-a-VWAP inyecta ceros exactos en celdas-segundo sin trades
  (LOCF), atenuando hacia 0 e inflando N. Conservador; marcar `fr=NaN` si no hubo trade real en (t,t+H].
- **C4 — [N maker_sim.py:45 / capa2 pooling]** prints exactamente en un ts de snapshot se pierden de
  ambos intervalos (borde `right`/`left`); simétrico, impacto nulo. Higiene de borde para futuros venues.
- **C5 — [N pilot_observer.py:74]** variables muertas `seen`/`first_snap_oids`: ELIMINAR antes del eco
  (para que nadie las "arregle" conectándolas e introduzca look-ahead marcando slow al snapshot 0).

## Decisión de diseño del eco (para mesa fresca, NO prejuzgada aquí)

- ¿El decreto pasa a **5s-céntrico** (la condena pendiente) o **25s-céntrico** (donde LIT vive)? Se decide
  con mesa fresca al leer el eco, JAMÁS retroactivamente.

### REQUISITO BLINDADO — el 2º símbolo del eco NO puede ser DOGE (es lo más importante que salió de A11)

Con la errata A11, **DOGE cayó como corroborador** (25s nulo, 5s marginal) → el ataque A2 queda DESNUDO:
**n=1 símbolo carga la hipótesis entera, y es el token nativo del propio venue.** Consecuencia de peso —
al acta con su importancia real:

- Un 2º símbolo que **NO sea nativo de Lighter**, medido con el **colector propio a 50 ms**, no es una
  mejora incremental: **es lo ÚNICO que convierte "existe un edge en LIT" en "existe un edge para el maker
  lento".** La generalización es ahora el eslabón más fino del expediente.
- **Un eco que solo añada más LIT es más masa de la MISMA anécdota — NO responde A2, y A2 es la objeción
  viva más fuerte que queda.** Un eco sin 2º símbolo no-token se declara de antemano como
  INSUFICIENTE-para-A2 aunque salga verde en LIT.
- El colector permite exactamente esto (cualquier símbolo, incluidos no-tokens, a 50 ms con wallet) — por
  eso su certificación provisional y su acumulación son ahora ruta crítica, no lujo.

**Actualización del número grande (mesa, 2026-07-05): se mantiene ~18-24%.** No baja pese a debilitarse la
evidencia porque el veredicto formal no dependía de DOGE (§3 intacto) y la señal de existencia se verificó
robusta: **cambió el ANCHO DE LA BASE, no la ALTURA DEL PICO.** La flor sigue igual de viva en LIT (una
pata en vez de dos, pero la pata no se debilitó). Lo que sube no es la probabilidad central sino la
**VARIANZA**: el resultado del eco importa MÁS que ayer, porque la generalización pasó a ser el eslabón
crítico y el 2º símbolo no-token es quien lo prueba o lo rompe.
