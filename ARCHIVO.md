# Archivo del código retirado

Estado al 2026-09-09: lotes 1, 2, 4 y 3 publicados en `f0fd1aa`, `0f127e3`, `e1c2757` y `ac165b9`, CI `34260532972`, `34286664630` y `34381162392` con ocho verificaciones verdes y `34388283960` con seis, según las auditorías de Code. La simplificación V2 está cerrada por el [dictamen de la mesa del 2026-09-09](docs/DICTAMEN_MESA_2026-09-09_V2_CIERRE.md). Estado vigente: [README](README.md) y [ledger actual](docs/LEDGER_ACTUAL.md).

Base completa recuperable: `408d368d3b6d9cab2fdae9d1b25f211dd907aa15`, publicada en `codex/wip-m12.20` antes de esta retirada. El [inventario del lote 1](docs/inventarios/V2_LOTE1_20260908.json) contiene SHA-256 local y del blob Git, último commit de cada fichero, imports y referencias históricas. `probe_hist.py` tenía CRLF en disco y LF en Git; se registran ambos hashes.

La aprobación y el orden están en [el dictamen de la mesa, §5](docs/DICTAMEN_MESA_2026-09-07_PUSH_CI_Y_V2.md). Este índice registra el retiro del código activo, conservando dictámenes, datos y documentos históricos. Las rutas antiguas citadas en los documentos se resuelven en el árbol Git indicado.

## Lote 1: entradas cerradas y pruebas exclusivas

| Ruta bajo `quant-system-ingesta/qs/` | Propósito | Último cambio | Motivo |
|---|---|---|---|
| `analysis/contrarian_ofi.py` | Señal OFI y cascada contrarian | `e489a94cdc9d` | Capítulo 1 cerrado; salen todos sus consumidores. |
| `analysis/contrarian_panel.py` | Panel de shocks del contrarian | `d378f9336c66` | Capítulo 1 cerrado; sale con su runner. |
| `analysis/contrarian_runner.py` | Calendario, ejecución y bloques Probe-1 | `c70fa3b34c3a` | Campaña cerrada; salen entrada, consumidores y dos excepciones del censo. |
| `analysis/download_chd_probe1.py` | Descarga del solape y Probe-1 de CHD | `14ba7ad8a882` | Preparación de la campaña retirada. |
| `analysis/episode_count.py` | Prechequeo de masa OFI | `bdf71b02b1b1` | Sonda concluida del contrarian. |
| `analysis/hl_flow_precheck.py` | Informatividad en Hyperliquid | `ad5f665e7541` | Lectura histórica concluida; consumidor del contrarian que sale con él. |
| `analysis/run_disparo.py` | Entrada al disparo Probe-1 | `25c3cb0a08b8` | Campaña cerrada; se retira sin ejecutarla. |
| `analysis/run_spread_check.py` | Entrada al contraste de spread | `950604483e6d` | Preparación del contrarian; sale con descargador y runner. |
| `analysis/flow_informativeness.py` | Informatividad mediante trades | `b4d156cde739` | Medición concluida del capítulo 2; sin consumidores activos. |
| `analysis/funding_carry.py` | Screen de prima de funding | `d42d553fea94` | Prima #2 archivada en el LEDGER. |
| `analysis/xvenue_lag.py` | Gate exploratorio Binance–Bybit | `3e1624e7fd63` | Gate archivado; sin consumidores activos de código. |
| `analysis/h2_funding_xvenue.py` | Subtest de funding multi-venue H2 | `a25741e88d05` | Subtest histórico tocado; retiro del instrumento sin cambiar su dictamen. |
| `analysis/h3_power_precheck.py` | Prechequeo de masa del setup H3 | `18078947ed2a` | H3 cerrado por masa insuficiente; salen dos excepciones de caché. |
| `analysis/h3_precheck_probe_mass.py` | Prechequeo de finura y setup H3 | `8fb5d5e6db1c` | H3 cerrado por prechequeo; no se ejecuta el screen pendiente. |
| `analysis/h6_listing_regime_precheck.py` | Prechequeo de régimen de listings H6 | `fbd0f4c6540f` | Sonda histórica retirada conforme al lote 1 aprobado. |
| `analysis/run_day26.py` | Entrada al screen H8 del día 26 | `d42d553fea94` | Prima #1 archivada; salen dos excepciones de caché. H8 permanece por screen. |
| `analysis/probe_hist.py` | Sonda histórica de actividad y funding | `eb4636b632a7` | Preparación de la campaña histórica; sin consumidores activos. |
| `analysis/spread_check.py` | Contraste de costes y spread | `df1dd0f3d611` | Sale con todos sus consumidores. Book y adaptadores permanecen. |
| `tests/test_contrarian_ofi.py` | Pruebas exclusivas de contrarian_ofi | `e005ad951610` | Se retira su módulo completo; ninguna entrada conservada depende de estas pruebas. |
| `tests/test_contrarian_panel.py` | Pruebas exclusivas de contrarian_panel | `d05495e2aa02` | Se retira su módulo completo; ninguna entrada conservada depende de estas pruebas. |
| `tests/test_contrarian_runner.py` | Pruebas exclusivas de contrarian_runner | `35a18ad7a4ef` | Se retira su módulo completo; ninguna entrada conservada depende de estas pruebas. |
| `tests/test_flow_informativeness.py` | Pruebas exclusivas de flow_informativeness | `b4d156cde739` | Se retira su módulo completo; ninguna entrada conservada depende de estas pruebas. |
| `tests/test_funding_carry.py` | Pruebas exclusivas de funding_carry | `d42d553fea94` | Se retira su módulo completo; ninguna entrada conservada depende de estas pruebas. |
| `tests/test_xvenue_lag.py` | Pruebas exclusivas de xvenue_lag | `3e1624e7fd63` | Se retira su módulo completo; ninguna entrada conservada depende de estas pruebas. |
| `tests/test_spread_check.py` | Pruebas exclusivas de spread_check | `f1f8707b8996` | Se retira su módulo completo; ninguna entrada conservada depende de estas pruebas. |

En el lote 1 el guardia perdió las seis excepciones de los sitios retirados; sus reglas y arneses permanecieron. El commit incorporó +1.611/−3.077 líneas contando documentos: 3.077 son eliminaciones brutas, no reducción neta del repositorio.

## Lote 2: expediente I5 y herramientas históricas

Base completa recuperable de este lote: `f0fd1aa4cd54a48328c662a5278174c14aa6e52e`. El [inventario del lote 2](docs/inventarios/V2_LOTE2_20260909.json) registra los 28 ficheros retirados, sus objetos y hashes, los traslados parciales y la frontera de las 16 fuentes de D1.

| Ruta bajo `quant-system-ingesta/qs/` | Propósito | Último cambio | Motivo |
|---|---|---|---|
| `analysis/h2_staking.py` | analysis/h2_staking.py — ejecución del test discriminante de H2 (LEDGER, pre-registro | `a5fdcd2360f5` | Campaña H2 retirada; get_funding y daily_funding se trasladan literalmente a fetch_funding. |
| `analysis/oxa_tick_gate2.py` | analysis/oxa_tick_gate2.py — GATE 2 de la ruta tick-L2 de 0xArchive (orden de la mesa 2026-07-06). | `14b8d7c2af3a` | Herramienta histórica concluida; sin consumidores operativos conservados. |
| `analysis/recompute_s5_neff.py` | analysis/recompute_s5_neff.py — CORRECCIÓN H1 (auditoría A11): recomputar §5 (minoría estable) con | `7bc8d1f5231d` | Herramienta histórica concluida; sin consumidores operativos conservados. |
| `analysis/verify_pilot_bhy_oriented.py` | analysis/verify_pilot_bhy_oriented.py — ERRATA-CHECK N2 (auditoría A11): la familia BHY del piloto | `7e4da1134f86` | Herramienta histórica concluida; sin consumidores operativos conservados. |
| `tests/i5_sdk_fixtures.py` | Synthetic provenance inputs for CHD unit tests; never a historical SDK substitute. | `1d8390818fab` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tests/test_i5_acceso.py` | Short offline tests for account separation and one-page I5 access. No real keys. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. Las aserciones del maker sobre la clave se conservan en test_lighter_maker_key.py. |
| `tests/test_i5_censo_cobertura.py` | Offline contract checks for fixed scope, missing data and census receipts. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tests/test_i5_chd_custodia.py` | Focal checks for the new hourly CHD instrument; no network or real trade inputs. | `1d8390818fab` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tests/test_i5_chd_redirect.py` | Bounded redirect transport regressions. Synthetic HTTPS responses only. | `1d8390818fab` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tests/test_i5_d1.py` | Synthetic D1 oracles, supports and custody boundaries. Never read real NPZ/trade bodies. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tests/test_i5_descarga_l3.py` | Offline custody, pagination, restart, gap comparison and account tests. No real credentials. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tests/test_i5_insumos_ocho.py` | test_i5_insumos_ocho | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tests/test_i5_productor_forense.py` | Only synthetic market data. The git recipe is the independent uninstrumented oracle. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tests/test_i5_productor_resto.py` | Synthetic custody and outputs only; no historical market body or credential is opened. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tests/test_i5_resto_chd.py` | New-scope/orchestration checks; shared transport suites are not rerun. | `1d8390818fab` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/anatomia_del_18_24.py` | ¿QUE ES, EXACTAMENTE, EL +18,24? — anatomia del unico resultado positivo del programa. | `546148ea35f2` | Herramienta histórica concluida; sin consumidores operativos conservados. |
| `tools/i5_celdas_20260906.json` | Manifiesto de las 149 celdas I5 | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_censo_cobertura.py` | Fixed metadata census: 149 spent cells, checkpoint/tick presence and generic coverage. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_chd_custodia.py` | Hourly CHD custody for the eight fixed forensic days; no differ or result reads. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_d1.py` | Hash-bound, offline D1 analysis of the closed 79-day forensic panel. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_d1_math.py` | Pure retrospective D1 branches and daily estimators. No IO, discovery or market access. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_descarga_l3.py` | Explicit staged custody within the 149 spent cells. No markouts. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_etapa0.py` | One minimal LIT 2026-03-06 checkpoint page with a parameterized Build account. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_insumos_ocho.py` | Local input contract for the eight fixed forensic days. No network, keys or markouts. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_oxa_io.py` | Small read-only 0xArchive client for I5 jobs. No retries, redirects or key logging. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_productor_forense.py` | Offline eight-day reproduction of the frozen July recipe. Code audits before running. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_productor_resto.py` | Offline reproduction of the remaining 71 LIT days; reuse the eight closed outputs. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |
| `tools/i5_resto_chd.py` | Custody of the 3,408 NEW CHD hour keys after the successful eight-day reproduction. | `1ca5ca6674ce` | Expediente I5 cerrado; retiro conjunto de instrumentos, manifiesto y pruebas exclusivas. |

La selección de clave del maker conserva su prueba en `tests/test_lighter_maker_key.py`; solo se retiran sus aserciones sobre el cliente I5. `fetch_funding.py` conserva literalmente `get_funding`, `daily_funding` y `DAY_MS` de H2. Salen las dos pruebas y los dos auxiliares exclusivos de anatomía de `test_compuertas_ref_invalida.py`; todas sus demás funciones permanecen idénticas.

El guardia elimina una excepción de anatomía y las tres excepciones selladas de I5. Las tablas selladas quedan vacías; el mecanismo y sus pruebas sintéticas permanecen. El test del censo exige los quince sitios que siguen activos. Los tres arneses conservan sus tablas (23/187/202).

El lote 2 se publicó en `0f127e3` con 36 rutas: 28 retiradas, cinco editadas y tres nuevas. El commit incorporó +1.080/−7.953 líneas. Junto con el lote 1, son 53 rutas retiradas, 11.030 eliminaciones brutas y una reducción neta de 8.339 líneas contando todas las adiciones. El [índice de I5](docs/INDICE_EXPEDIENTE_I5.md) reúne la evidencia científica cerrada; el [sello del LEDGER](docs/CONGELACION_LEDGER_2026-09-09.json) identifica sus bytes históricos sin reescribirlos.

## Dependencias del lote 2 resueltas en el lote 3

- `screen.py` pertenecía también a `eco_gate_b.CIERRE_DECISORIO`; ahora salen juntos el eco, `screen.py`, H1/H3/H8, sus lectores y el consumidor `exec_sim`.
- Salen los productores, lectores y simulador de la receta maker, con el careo, censo de referencias y sonda antigua de retención que los consumían. Los adaptadores genéricos permanecen.
- `estructura_chd_local` sale con el censo de anclas, el CAS y los informes ejecutables exclusivos. Su fixture de redirección de consumo desaparece; la vigilancia de `.git/qs-*` sigue activa.
- La maquinaria compartida del arnés pasa a `tools/arnes_comun.py`: dieciséis cuerpos de función idénticos por AST. El argumento por defecto de `_correr` apunta a pruebas conservadas. Las funciones del ejecutor de referencias conservan su AST.
- Las 49 filas conservadas de referencias protegen módulos activos; las 153 retiradas apuntaban a módulos que salen. Los dos arneses exclusivos del libro y gate salen de código y CI. El guardia de completitud conserva sus reglas y pruebas con dos sitios reales y ninguna excepción histórica.

La retirada conjunta se publicó en `ac165b9` con el run de CI `34388283960` verde y la auditoría de Code del lote 3. El inventario registra las dependencias, funciones y pruebas trasladadas para no retirar controles de módulos que permanecen.

## Lote 3: campaña y dependencias

Base recuperable completa: `e1c2757b1f492637aba62ef46ffe45be91405c67`. El [inventario conjunto](docs/inventarios/V2_LOTE3_20260909.json) registra las 81 rutas antiguas, hashes de blob y de bytes locales, imports, traslados y filas de mutación. Dos rutas de tests se sustituyen por las de las piezas compartidas; no se presentan sus pruebas como eliminadas.

| Ruta bajo `quant-system-ingesta/qs/` | Propósito | Último cambio | Motivo |
|---|---|---|---|
| `analysis/confirm_runner.py` | analysis/confirm_runner.py — runner de la CONFIRMACIÓN DECISIVA (prereg CONGELADO 9c8f4b1). | `d85b3313b0d5` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `analysis/confirm_screen.py` | analysis/confirm_screen.py — LA LECTURA DECISIVA (prereg CONGELADO 9c8f4b1). UNA vez, en frío. | `7bc8d1f5231d` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `analysis/eco_bampliada_calib.py` | analysis/eco_bampliada_calib.py — CALIBRACIÓN de TOL_DIFERENCIAL (B-ampliada cond 5). | `a77d6ff2e234` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_cas.py` | LA PRIMITIVA DE PUBLICACIÓN DE UN SOLO USO, en un sitio y con sus límites medidos. | `0147a2425a59` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_conteo_wti.py` | analysis/eco_conteo_wti.py — CONTEO pre-freeze de masa/referencia de WTI para A2/B (25s, 0xArchive). | `5daff8b047c6` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_e_anchor.py` | analysis/eco_e_anchor.py — pendiente #1 de la mesa (2026-07-10): E_WTI RE-COMPUTADO EN CÓDIGO. | `118e877f9d70` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_fase2_wti.py` | analysis/eco_fase2_wti.py — FASE 2 del conteo pre-freeze de WTI (A2/B, 25s). FIRMADO 2026-07-07. | `546148ea35f2` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_gate_b.py` | analysis/eco_gate_b.py — MAQUINARIA DECISORIA DE B, v2 BIFÁSICA (encargo (k)-(s), mesa 2026-07-11). | `0147a2425a59` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_gate_sigma79.py` | analysis/eco_gate_sigma79.py — encargo 2 de la mesa (2026-07-10): σ de la receta del GATE sobre los | `7bc8d1f5231d` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_libro_tx.py` | analysis/eco_libro_tx.py — LIBRO TRANSACCIONAL C (M-11, C-SPEC v7 congelada en 7be9b6a). | `d15cf94ba788` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_medir_L.py` | analysis/eco_medir_L.py — INSTRUMENTO de medición de la LATENCIA DE MADURACIÓN L (M-10, B). | `45d3b05ac6b2` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_nmin_mc.py` | analysis/eco_nmin_mc.py — SELLO MECÁNICO de N_min por potencia t-NO-CENTRAL (encargo (p), mesa 2026-07-11). | `e9a5eada230d` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_procedencia.py` | analysis/eco_procedencia.py — UN SOLO validador de procedencia para el eco: productor y gate. | `2d6ab30acdf4` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_ref_crudos.py` | analysis/eco_ref_crudos.py — REFERENCIA INDEPENDIENTE de los dos crudos de nuisance de A2 | `a77d6ff2e234` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_runner_lit.py` | analysis/eco_runner_lit.py — PRODUCTOR OFICIAL de la RÉPLICA LIT del gate de B (M-10, Frente 1b). | `2d6ab30acdf4` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/eco_runner_wti.py` | analysis/eco_runner_wti.py — PRODUCTOR OFICIAL del outcome de B (encargo (u), mesa 2026-07-11). | `2d6ab30acdf4` | Retiro completo de la campaña eco con sus productores, lectores, dependencias y controles específicos. |
| `analysis/exec_sim.py` | analysis/exec_sim.py — PRIMA #3 (ejecución óptima): ¿ahorra bps un horario OFI-aware vs TWAP? | `d42d553fea94` | Cierre de dependencias de screen y del capítulo 1; exec_sim consumía screen. |
| `analysis/gen_t_tabla.py` | analysis/gen_t_tabla.py — GENERADOR de la tabla de cuantiles de Student (encargo (p), mesa 2026-07-11). | `e9a5eada230d` | Generador y tabla del gate/nmin retirados junto con sus únicos consumidores. |
| `analysis/h1.py` | analysis/h1.py — harness del test predictivo de H1 (pre-registro CONGELADO, LEDGER, 780e7d2). | `293c64a268c8` | Cierre de dependencias de screen y del capítulo 1; exec_sim consumía screen. |
| `analysis/h1_io.py` | analysis/h1_io.py — carga/ensamblado del L2 propio para el harness de H1 (etapa 1). | `ef47c4ded251` | Cierre de dependencias de screen y del capítulo 1; exec_sim consumía screen. |
| `analysis/h3.py` | analysis/h3.py — control de FACTOR DE MERCADO para H3 (cascadas de liquidación). | `fb5e569469ea` | Cierre de dependencias de screen y del capítulo 1; exec_sim consumía screen. |
| `analysis/h3_io.py` | analysis/h3_io.py — carga/ensamblado del panel para H3 (cascadas de liquidación). | `635aabea5c0f` | Cierre de dependencias de screen y del capítulo 1; exec_sim consumía screen. |
| `analysis/h8.py` | analysis/h8.py — núcleo del test de H8 (provisión selectiva de liquidez con filtro OFI). | `6a8172244d31` | Cierre de dependencias de screen y del capítulo 1; exec_sim consumía screen. |
| `analysis/h8_io.py` | analysis/h8_io.py — simulación HONESTA (cota inferior) de un maker pasivo para H8. | `9089edccb659` | Cierre de dependencias de screen y del capítulo 1; exec_sim consumía screen. |
| `analysis/hl_maker_capa1.py` | analysis/hl_maker_capa1.py — CAPA 1 del pre-check maker en Hyperliquid (condicionantes, SIN outcome). | `24ba26898bc5` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `analysis/lighter_maker_capa1.py` | analysis/lighter_maker_capa1.py — CAPA 1 del pre-check maker en LIGHTER (condicionantes, SIN outcome). | `1ca5ca6674ce` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `analysis/maker_capa2_runner.py` | analysis/maker_capa2_runner.py — runner de la CAPA 2 maker Lighter (PREREG congelado 15f755f). | `d85b3313b0d5` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `analysis/maker_capa2_screen.py` | analysis/maker_capa2_screen.py — EL NÚMERO de la capa 2 (PREREG congelado 15f755f, §5-§6). | `7bc8d1f5231d` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `analysis/maker_sim.py` | analysis/maker_sim.py — simulador de maker join-the-touch con DOS COTAS de cola. CAP 2, CAPA 2. | `807d0fe1adce` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `analysis/pilot_observer.py` | analysis/pilot_observer.py — OBSERVADOR de cohortes del piloto L3 (§7-bis CONGELADO 946504b). | `546148ea35f2` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `analysis/pilot_runner.py` | analysis/pilot_runner.py — runner del piloto L3 (§7-bis congelado 946504b). | `d85b3313b0d5` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `analysis/pilot_screen.py` | analysis/pilot_screen.py — LA LECTURA del piloto L3 (§7-bis congelado 946504b). UNA vez, en frío. | `7bc8d1f5231d` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `analysis/screen.py` | analysis/screen.py — primitivas del RUNNER del día 14 (ver docs/RUNNER_DESIGN.md). | `dd529ba62b0c` | Cierre de dependencias de screen y del capítulo 1; exec_sim consumía screen. |
| `analysis/t_tabla.py` | analysis/t_tabla.py — TABLA VERSIONADA de cuantiles de Student (encargo (p), mesa | `e9a5eada230d` | Generador y tabla del gate/nmin retirados junto con sus únicos consumidores. |
| `analysis/wallet_atlas.py` | analysis/wallet_atlas.py — ATLAS DE WALLETS de la cola lenta de LIT (mini-prereg 3c53818). | `b6eb9d6912ad` | Receta maker retirada junto con todos sus consumidores y pruebas exclusivas. |
| `tests/test_censo_anclas.py` | EL CENSO BRUTO DE ANCLAS, acreditado sobre parquets sintéticos con el esquema REAL. | `0147a2425a59` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_censo_ref_invalida.py` | Tests del censo de referencia inválida y de las puertas del careo. | `546148ea35f2` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_cruce_ancla_por_ancla.py` | EL CRUCE ANCLA POR ANCLA, segunda vuelta (mesa, M-13, P0-5) y lo que la revision adversarial | `0147a2425a59` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_eco_anchor.py` | tests/test_eco_anchor.py — tercil estricto y rango legal de r* (RECONSTRUIDO 2026-07-11). | `cc72e870c759` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_eco_cas.py` | LA PRIMITIVA DE PUBLICACIÓN DE UN SOLO USO, y el registro de consumo que la usa. | `0147a2425a59` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_eco_gate_b.py` | tests/test_eco_gate_b.py — v7 (M-06: igualdad de población del bar, puerta única a los npz, | `0147a2425a59` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_eco_procedencia.py` | EL VALIDADOR ÚNICO DEL ECO, y el escape que dejó de ser puerta principal (mesa, P0-2 y P0-3). | `2d6ab30acdf4` | Salen el consumidor o control de campaña y sus pruebas exclusivas; las siete pruebas compartidas de carril se extraen de test_eco_procedencia. |
| `tests/test_eco_runner_lit.py` | M-10 Frente 1b — unidades PURAS del productor LIT (eco_runner_lit). El ciclo completo con dato real | `2d6ab30acdf4` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_estructura_chd.py` | EL INSTRUMENTO DE ESTRUCTURA CHD, acreditado sobre parquets SINTÉTICOS. | `0147a2425a59` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_etapa0_validador.py` | Tests del validador de la etapa 0 — los diez casos que la mesa exigió (2026-08-25). | `d3d00ef8814e` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_exec_sim.py` | Tests de analysis/exec_sim.py — el ahorro de ejecución OFI-aware vs TWAP, causal y honesto. | `d42d553fea94` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_gate_dos_worktrees.py` | EL GATE DE UN SOLO USO, CONTRA DOS WORKTREES DE VERDAD. | `0147a2425a59` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_h1.py` | Tests de analysis/h1.py — harness predictivo de H1 (anticipación de shock de liquidez). | `293c64a268c8` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_h1_io.py` | Tests de analysis/h1_io.py — carga/ensamblado del L2 propio (parquet sintético del esquema real). | `ef47c4ded251` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_h3.py` | Tests de analysis/h3.py — control de factor de mercado (β causal) para H3. | `fb5e569469ea` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_h3_io.py` | Tests de analysis/h3_io.py — carga/ensamblado del panel de H3 (parquet sintético del esquema real). | `635aabea5c0f` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_h8.py` | Tests de analysis/h8.py — núcleo de provisión selectiva (filtros de toxicidad + soledad). | `6a8172244d31` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_h8_io.py` | Tests de analysis/h8_io.py — la simulación de cola RiskAdverse encarna C1/C2/C4. | `9089edccb659` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_libro_tx.py` | M-11 (C) capa 1 — validador PURO del MANIFIESTO v2 (eco_libro_tx). Extensión aditiva del v1 del gate: | `4598482eb2ec` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_libro_tx_git.py` | M-11 (C) capa 2 — primitivas GIT + autoridad remota + guardia PRE-PUBLICACIÓN + CAS/lease. | `93e61616f959` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_libro_tx_recuperacion.py` | M-11 (C) capa 3, bloque 3 — CLASIFICADOR E0-E14 + INVENTARIO TOTAL + ABORTO AUDITADO (§8) + GC (§7) | `63461dd8c636` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_libro_tx_writer.py` | M-11 (C) capa 3, bloque 1 — LOCK S1/S11 + liveness/adopción (§5) + JOURNAL S4/S9b/S10 (3 esquemas) | `26ecd882763d` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_lighter_maker_key.py` | La selección de clave del maker permanece al retirar el custodio I5. | `0f127e396e5c` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_m10_differ_core.py` | M-10 Frente 1a — prueba de IGUALDAD (no solo determinismo) del núcleo puro _differ_core. | `5da1321af91a` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_maker_sim.py` | Tests del simulador de maker (§4-§5 del PREREG congelado 15f755f) — cada regla, un test. | `8ba825d21130` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_medir_L.py` | M-10 (B) — instrumento de L (eco_medir_L): núcleo de decisión + MAQUINARIA PROBATORIA. | `00885daa9ce3` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_mutacion_gate_b.py` | Tests FOCALES del arnés de mutación del gate — el verificador también se verifica. | `0147a2425a59` | Sale esta ruta; las pruebas del núcleo conservado se trasladan según el mapa de funciones y nodos. |
| `tests/test_pilot_observer.py` | Tests del observador de cohortes (§7-bis congelado 946504b) — cada regla, un test. | `d859cce4f254` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_pilot_observer_ref_invalida.py` | Guardias de REFERENCIA INVÁLIDA — analysis/ref_valida.py y sus DOS puntos de uso. | `807d0fe1adce` | Sale esta ruta; las pruebas del núcleo conservado se trasladan según el mapa de funciones y nodos. |
| `tests/test_recibo.py` | M-10 (A) — validador COMPARTIDO del recibo acumulativo: eco_gate_b.validar_recibo / parsear_recibo_canonico. | `836f9ff1bfb9` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_screen.py` | Tests de analysis/screen.py — primitivas del runner (N_eff, cross-shock, e-values, latencia). | `dd529ba62b0c` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_session_active_wti.py` | tests/test_session_active_wti.py — calendario CME EXACTO de eco_fase2_wti (#2 mesa, eco A2/B). | `149991c8a9a2` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tests/test_trailing_vol_i2.py` | tests/test_trailing_vol_i2.py — I2 e I7 del insumo A11 (pendiente #5 de la mesa, 2026-07-10). | `2572d67b1597` | Pruebas exclusivas de módulos retirados; los consumidores compartidos se verifican aparte. |
| `tools/careo_capa2_vs_piloto.py` | EL CAREO: el maker SIMULADO de capa 2 contra los fills REALES del piloto — mismo LIT, misma ventana. | `546148ea35f2` | Instrumento exclusivo del libro, gate, CAS o diagnósticos retirados; sin consumidor operativo conservado. |
| `tools/censo_anclas.py` | CENSO BRUTO DE ANCLAS — cuenta desde el DATO y cruza, ancla por ancla, con la traza de la máquina. | `0147a2425a59` | Instrumento exclusivo del libro, gate, CAS o diagnósticos retirados; sin consumidor operativo conservado. |
| `tools/censo_ref_invalida.py` | CENSO VERSIONADO del defecto de REFERENCIA INVÁLIDA, con manifiesto canónico y recibo ligado. | `807d0fe1adce` | Instrumento exclusivo del libro, gate, CAS o diagnósticos retirados; sin consumidor operativo conservado. |
| `tools/cifras_paquete.py` | CIFRAS DEL PAQUETE — el bloque de números firmados, emitido POR PROGRAMA desde los artefactos. | `0147a2425a59` | Instrumento exclusivo del libro, gate, CAS o diagnósticos retirados; sin consumidor operativo conservado. |
| `tools/comprobador_destrucciones.py` | COMPROBADOR DE DESTRUCCIONES — pone precio al criterio de parada de la capa 3. | `6fe16a064b04` | Instrumento exclusivo del libro, gate, CAS o diagnósticos retirados; sin consumidor operativo conservado. |
| `tools/estructura_chd_local.py` | ESTRUCTURA DEL FEED CHD, medida sobre el CACHÉ LOCAL. Sin red, sin créditos, sin sonda. | `0147a2425a59` | Instrumento exclusivo del libro, gate, CAS o diagnósticos retirados; sin consumidor operativo conservado. |
| `tools/etapa0_retencion_oxa.py` | ETAPA 0 — ¿0xArchive todavía sirve el 2026-03-06? Sonda de VIABILIDAD, nada más. | `63461dd8c636` | Sonda histórica concluida; sale con el cliente maker que importaba y su validador exclusivo. |
| `tools/etapa0_validador.py` | VALIDADOR de la respuesta de 0xArchive para la etapa 0 — PURO, sin red, testeable. | `63461dd8c636` | Sonda histórica concluida; sale con el cliente maker que importaba y su validador exclusivo. |
| `tools/medida.py` | FUENTE ÚNICA de los números que se presentan. Ningún recuento se teclea a mano. | `44afb5626e61` | Instrumento exclusivo del libro, gate, CAS o diagnósticos retirados; sin consumidor operativo conservado. |
| `tools/mutacion_gate_b.py` | ARNÉS DE MUTACIÓN DEL GATE — ¿muerden sus tests, y muerden POR LA CAUSA QUE DICEN? | `7df52803b6db` | Salen tabla y entrada del gate; dieciséis cuerpos de función compartidos pasan a arnes_comun. |
| `tools/mutacion_libro_tx.py` | ARNES DE MUTACION del libro transaccional C (M-11 capa 3) — versionado y ejecutable en CI. | `63461dd8c636` | Instrumento exclusivo del libro, gate, CAS o diagnósticos retirados; sin consumidor operativo conservado. |
| `tools/probe_no_aislable_6130.py` | REFUTADA — esta probe sostuvo una conclusión FALSA. Se conserva como registro, no como evidencia. | `63461dd8c636` | Instrumento exclusivo del libro, gate, CAS o diagnósticos retirados; sin consumidor operativo conservado. |
| `tools/retirar_lock_espurio.py` | RETIRADA ADJUDICADA del gate_read_lock.json espurio — por resolución explícita de la mesa. | `63461dd8c636` | Instrumento exclusivo del libro, gate, CAS o diagnósticos retirados; sin consumidor operativo conservado. |

## Recuperación y límites

Para inspección: `git show 408d368:ruta/completa` para el lote 1 y `git show f0fd1aa:ruta/completa` para el lote 2, o un checkout separado del árbol completo correspondiente. No se autoriza ejecutar una pieza por haberla recuperado.

La restauración científica de I5 sigue siendo el árbol completo `1ca5ca6674ce55ad0aca149b7b5757a87f83f25e`, la historia de julio que extrae y las custodias externas ligadas por hash. Las diez fuentes I5 de D1 salieron en el lote 2. De las seis compartidas, el lote 3 retira tres sin editar y conserva activas tres con sus hashes; la especificación, planes, datos y recibos históricos se conservan. Para recuperar también los fixtures portables y controles posteriores, usar el árbol completo `f0fd1aa`; no atribuir esos arreglos posteriores a `1ca5ca6`. La base de recuperación conjunta del lote 3 es `e1c2757b1f492637aba62ef46ffe45be91405c67`.

STOP, freezes, pins y las ventanas protegidas LIT desde 2026-06-30 y WTI desde 2026-06-05 permanecen vigentes. Este retiro no habilita lecturas, descargas ni cambios de infraestructura.
