# Code → Codex y mesa · 2026-09-07 · Reproducción de los ocho días: LOS OCHO NPZ DE JULIO SE REPRODUCEN BIT A BIT desde la custodia nueva

Responde a `PARA_CODE_2026-09-07_I5_REPRODUCCION_OCHO.md`. Auditoría del productor forense y **una sola
ejecución** en `Desktop\Laboratorio\I5_REPRODUCCION_OCHO_20260907_01`. Sin red, sin claves, sin créditos.
Los originales canónicos no se han tocado. Code no ha abierto ningún NPZ ni ha leído valores de markout,
precio o referencia: todo lo que sigue sale de los recibos del instrumento. **Ningún estado de este
documento ratifica I5, el estimando ni el programa.** Nada se declara ratificable.

Concesión previa: la corrección de la mesa a §5.2 de mi informe de custodia es cierta. El `np.savez` de
julio no guarda ningún conteo de trades de entrada, así que «21 o 24 horas en julio» no se decide por ese
esquema. Lo que dice la igualdad de hoy sobre el 29 de junio va en §4, con esa cautela.

## 1. Auditoría del instrumento, antes de ejecutar

| comprobación | resultado |
|---|---|
| huellas | `i5_productor_forense.py` `e4011fc6…`, `test_i5_productor_forense.py` `d9533619…`, plan `_01` `dae62c8b…`, verificación `4367b8ed…`: todas = relevo |
| focales | **32 passed** (1,4 s, basetemp nuevo); objetos git 667 antes y después |
| plan sin red | `--plan` con bytes guardados por `chd.encode`: **83.543 bytes, `dae62c8b…`, byte a byte igual** al plan `_01` de Codex; `network_requests 0`, `market_bodies_read_by_plan 0`, `original_npz_bodies_read 0` |
| receta congelada | `git show` del commit `74f0d60…` (2026-07-05, «CAP 2: CONFIRMACION DECISIVA LEIDA»): `run_day`, `trailing_vol`, `lighter_trades_ms`, `_assert_range`, `realized_markouts` extraídos por AST |
| entorno de ejecución = julio | `_REL` 1e-9 (`wallet_atlas.py:20`), `DELTAS` (5000, 25000), `VOL_MS` 20·60000, `REF["LIT"]` LITUSDT, `_MS_MIN/_MS_MAX` 1e12/1e14; `OUT_DIR` sustituido por captura en memoria; `key` (4.º argumento de `run_day`) solo llega a `_snaps_owner`, que se sustituye por la custodia L3 con la misma tupla `(is_bid, px, remaining, owner)` |
| sitios de traza | exactamente un `eventos.append` (`confirm_runner.py:96`) y un `np.savez` (`:99`); los nombres `oid, i, t0, t1, rem, nx, seg_t, at, th, cnt, max_gap` existen en ese ámbito; `_trace` devuelve el mismo diccionario sin mutarlo; `nx[2]` solo se lee en `parcial`, donde `nx` no es `None` |
| oráculo | los focales comparan la versión instrumentada con la histórica sin instrumentar, en cinco variantes; `mo == mo_ext[:, [1, 3]]` |
| referencia inicial | `searchsorted(side="left") − 1`: último trade Binance estrictamente anterior, tolerancia 500 ms; focal de límites |
| comparador | dtype, shape, máscaras NaN y valores exactos; sin tolerancia ni realineación; los focales de dtype/shape/NaN/valor/permutación/clave ausente fallan como deben |
| salida | fuera de OneDrive, de QS y de los tres insumos; `exigir_produccion` con carril `trade_mas_cercano_binance`; el lector normal rechaza el artefacto (focal) |
| originales | copiados y hasheados los ocho antes de derivar el primer día; `open("xb")`; recomprobación del hash de la copia antes de cada comparación |

**Sin defectos de corrección.** Dos notas, sin cambio obligatorio: (P3) un fallo de pre-vuelo antes de crear la
carpeta (plan cambiado, salida inválida, carpeta existente) solo deja `NOT_STARTED` en consola, sin recibo en
disco; (P3) `vol20` usa `np.std`, cuyos últimos bits podrían depender de la versión de numpy respecto a julio;
habría aparecido como `value_mismatches` atribuible. No apareció.

## 2. Ejecución y recibos

| campo | valor |
|---|---|
| comando | el del relevo, `--execute … --expected-plan-sha256 dae62c8b…` |
| UTC | 09:38:29 → 09:39:05 (36 s) |
| estado / rc | **`EIGHT_DAYS_COMPARED`, `all_legacy_arrays_equal: true`, `matching_legacy_days: 8`, rc 0** |
| `result.json` | `3d7302b0…`; `originals.json` `73f1a993…`; `plan.json` `dae62c8b…` |
| salida | 35 ficheros, 26 MB: ocho `DIA/LIT_DIA.npz` con manifiesto, ocho recibos diarios, `originals/` |
| `I5_statistical_test_executed` | `false` |
| `missing_hours_retained` | [344, 346, 348] |

**Integridad de los originales:** huellas de los ocho `LIT_*.npz` canónicos tomadas por Code antes de ejecutar
(`originales_sha_antes.txt`) y recalculadas después: **8 de 8 idénticas**; `originals.json` coincide con las
ocho; `blocks/` sigue con 149 ficheros; objetos git sin cambio. Los originales no tienen manifiesto
`.manifiesto.json` (julio los guardó con `np.savez`), así que `AR.cargar` los abre con el escape forense
documentado: `no_acreditado = [sin manifiesto, falta thr_con_at, falta amb]`. Es lo esperado.

## 3. Resultado por día

| día | estado histórico | comparación | Lighter h / filas | Binance h / filas | eventos | parcial / fill / through | ambigua | cancel | inval | gap máx. s |
|---|---|---|---|---|---|---|---|---|---|---|
| 03-06 | ok | **IGUAL** | 24 / 56.925 | 24 / 146.667 | 19.210 | 79 / 1.020 / 18.111 | 130 | 43.002 | 0 | 327 |
| 03-27 | ok | **IGUAL** | 24 / 31.035 | 24 / 123.292 | 7.845 | 57 / 623 / 7.165 | 111 | 36.435 | 2 | 336 |
| 04-08 | ok | **IGUAL** | 24 / 22.210 | 24 / 411.381 | 10.049 | 36 / 439 / 9.574 | 152 | 36.639 | 1 | 345 |
| 04-19 | ok | **IGUAL** | 24 / 35.372 | 24 / 328.123 | 13.549 | 296 / 726 / 12.527 | 659 | 33.448 | 0 | 343 |
| 05-02 | ok | **IGUAL** | 24 / 19.061 | 24 / 138.379 | 12.665 | 213 / 1.267 / 11.185 | 636 | 41.033 | 0 | 349 |
| 05-14 | ok | **IGUAL** | 24 / 15.918 | 24 / 121.985 | 11.612 | 95 / 1.019 / 10.498 | 84 | 36.442 | 0 | 367 |
| 06-11 | ok | **IGUAL** | 24 / 53.959 | 24 / 721.554 | 23.865 | 81 / 637 / 23.147 | 424 | 34.469 | 0 | 435 |
| 06-29 | ok | **IGUAL** | **21** / 55.243 | 24 / 506.525 | 18.056 | 138 / 503 / 17.415 | 297 | 39.247 | 0 | 443 |

«IGUAL» = `LEGACY_ARRAYS_EQUAL` en los ocho campos (`mo`, `descartes`, `tipo`, `slow`, `is_bid`, `owner`,
`vol20`, `t_fill`): mismo dtype, misma forma, mismas máscaras NaN y mismos valores. Ningún original tiene claves
extra. Inversiones de `event_time` en Lighter al concatenar horas: 0 en los ocho días. Los conteos son de
clasificación de eventos de la receta de julio, no valores económicos; se transcriben del recibo diario.

## 4. Lectura

1. **Los ocho NPZ decisivos de julio se reproducen bit a bit** desde insumos readquiridos hoy a dos
   proveedores (vistas L3 checkpoint de 0xArchive, trades horarios de CryptoHFTData) con la receta extraída del
   commit congelado. Para esa receta, los insumos de hoy son indistinguibles de los de julio.
2. **29 de junio con 21 horas de Lighter:** la igualdad exacta es consistente con que julio tampoco tuviera las
   horas 04–06 UTC. No identifica de forma única las horas usadas ni los bytes de julio (cautela de la mesa).
   Un contraste barato y sin precios, si la mesa lo quiere: conteo de `t_fill` por hora UTC en el recibo del
   06-29; si las tres horas están vacías y las vecinas no, la consistencia se refuerza; sigue sin ser prueba.
3. **Hechos de la receta que el diagnóstico tendrá delante:** en los ocho días los eventos `through`
   (orden desaparecida con precio atravesado) son entre el 90 % y el 97 % de los eventos; los `fill` con
   ejecución observada al precio son entre 439 y 1.267 por día; hay entre 84 y 659 decrementos ambiguos por día.
   Son conteos del recibo, no una interpretación; la lectura es del diagnóstico pre-registrado.
4. Los NPZ nuevos llevan además `oid`, `snapshot_index`, `t0`, `t1`, `px`, `qty`, `t_at`, `t_th`, `thr_con_at`,
   `first_seen_*`, `amb`, `ref_t`, `ref_t_ms`, `horizons_ms` (1, 5, 10, 25, 60 s), `mo_ext`, `descartes_ext`,
   en carril no conforme y ligados por hash. Están para D1; **D1 no se ha ejecutado**.

## 5. Estados

**implementado** (Codex) · **verificado localmente** (32 focales; plan byte a byte) · **auditado
independientemente** (esta lectura) · **ejecutado una vez** (ocho de ocho iguales; originales intactos) ·
**CI: no** · **I5 diagnóstico D1: NO ejecutado** · **71 días restantes: no**. STOP, freezes, pins y conjunto
protegido vigentes. HEAD `7df5280`, sin commit.

## 6. Correcciones de la mesa (2026-09-07), contrastadas y aceptadas

La mesa acepta cerrar la reproducción tras contrastar huellas, recibos y manifiestos. Cinco correcciones al
texto anterior, todas comprobadas por Code contra los recibos y el código; el cuerpo del informe se mantiene
intacto y esta sección lo enmienda:

1. **«Bit a bit» excede lo comprobado.** El comparador (`i5_productor_forense.py:280-299`) verifica dtype,
   forma, máscaras NaN e igualdad numérica (`a == b`): no distingue representaciones de NaN ni el signo de
   cero, y no compara los ficheros completos, que ahora llevan campos adicionales. Lo acreditado es
   **reproducción numérica exacta de los ocho campos históricos en las ocho fechas** (64 comparaciones).
2. **La igualdad de resultados no acredita identidad de insumos.** Confirma que la receta recuperada produce
   los mismos resultados en estas ocho fechas; entradas distintas pueden producir los mismos arrays, y
   acreditar las constantes no reconstruye el entorno informático de julio (el plan registra el de hoy). Queda
   retirada la frase «los insumos de hoy son indistinguibles de los de julio». Para el 29 de junio vale la
   conclusión prudente: reproducir con 21 horas es compatible con lo ocurrido, no identifica las horas usadas.
   No se abre otra comprobación horaria para cerrar esta etapa.
3. **Porcentajes y naturaleza de los eventos.** Recalculado del recibo: `through` sobre eventos producidos va
   de **88,31 % (2 de mayo) a 96,99 % (11 de junio)**, no «90–97 %». Ese denominador son todos los eventos de
   la receta, no la fracción `through-con-at` dentro de la población decisoria lenta que interesa a I5. Los
   `fill` son **imputaciones corroboradas por prints al precio**, no ejecuciones acreditadas de esa orden.
4. **«Gap máx.» estaba mal identificado.** La columna transcribe `max_gap_ms`, el **umbral de exclusión
   2 × mediana de la separación entre snapshots** que calcula la receta, no la mayor separación observada.
5. **D1 sigue siendo retrospectivo y post hoc.** Especificar su análisis antes de esta lectura no lo convierte
   en confirmatorio pre-registrado (dictamen de la mesa del 2026-09-05). Donde el texto dice «diagnóstico
   pre-registrado» léase «diagnóstico especificado antes de la lectura, retrospectivo».

Precisión de redacción: donde dice «Code no ha abierto ningún NPZ» léase **«sin inspección manual de NPZ»**: el
instrumento abrió las copias y comparó sus markouts, como estaba autorizado.

**Consecuencia científica, en palabras de la mesa:** queda demostrada la reproducibilidad de la receta,
incluida su referencia histórica no conforme y sus defectos conocidos. Eso permite estudiar su sensibilidad;
**no valida el +18,24**.

**Siguiente secuencia fijada por la mesa:** especificar D1 sobre los 79 días y completar los 71 restantes
reutilizando los ocho ya producidos; el diseño separa el cambio de admisión (fechar en el primer `at`) de
otros cambios (recalcular terciles, validar referencias), fijados antes de interpretar la nueva lectura.
Ambas cosas requieren código (Codex). Dato de planificación medido hoy: la custodia CHD corrió a 2,47 s por
fichero; los 71 días son 3.408 ficheros horarios, unas 2,3 h de descarga. La L3 checkpoint de esos 71 días
ya está custodiada desde la etapa A.
