# Expediente I5/D1 cerrado

Índice del 2026-09-09. Resume documentos ya emitidos; no contiene una lectura nueva. Estado vigente y siguiente trabajo: [ledger actual](LEDGER_ACTUAL.md).

## Conclusión y alcance

El [dictamen final de la mesa](DICTAMEN_MESA_2026-09-07_I5_D1_79.md) cierra I5 el 2026-09-07 como diagnóstico retrospectivo post hoc sobre 79 días de LIT, del 6 de marzo al 29 de junio. El +18,24 se reproduce, pero su magnitud no sobrevive a la ampliación de admisión especificada. STOP y la no ratificación continúan.

Cohorte lenta, agitada, cortes Q0; medias equiponderadas de los mismos 79 días, en bps. A añade los **through-con-at**, no todos los through. Se conserva la jerarquía fijada antes de leer:

| Horizonte, referencia histórica | H: admisión histórica | A: admisión ampliada | Delta pareado |
|---|---:|---:|---:|
| 5 s, celda primaria | +2,6101 | −1,0843 | −3,6944 |
| 25 s, compañero fijado y antiguo titular | +18,2368 | +2,5750 | −15,6618 |

Los soportes, referencias validadas, otras ramas y correcciones están en el dictamen y el informe completo. El contraste es descriptivo y post hoc; la primaria cruda de 5 s no se presenta como prueba confirmatoria concluyente. Los fills siguen imputados y la referencia de la receta es por trades, no por mid. El residuo positivo a 25 s queda registrado; no es PnL neto ejecutable ni rehabilita una ventaja.

## Ruta de evidencia

| Pieza | Fuente y función |
|---|---|
| Diseño de D1 | [Especificación original](ESPEC_MESA_2026-09-07_D1_79_DIAS.md), conservada sin corregir retroactivamente |
| Adquisición L3 | [Checkpoint de las 149 celdas](RESULTADO_CODE_2026-09-06_I5_ETAPA_A_CHECKPOINT.md); los 79 días LIT alimentan D1 |
| Trades readquiridos | Custodia de [ocho días](RESULTADO_CODE_2026-09-07_I5_CHD_CUSTODIA_OCHO.md) y [71 restantes](RESULTADO_CODE_2026-09-07_I5_CHD_RESTO_71.md) |
| Reproducción de julio | [Ocho días](RESULTADO_CODE_2026-09-07_I5_REPRODUCCION_OCHO.md) y [71 restantes](RESULTADO_CODE_2026-09-07_I5_REPRODUCCION_RESTO_71.md): igualdad numérica exacta en los ocho campos históricos, 632 comparaciones en total |
| Diagnóstico ejecutado una vez | [Resultado de Code](RESULTADO_CODE_2026-09-07_I5_D1_79.md), con todas las ramas fijadas |
| Interpretación y correcciones | [Dictamen de mesa](DICTAMEN_MESA_2026-09-07_I5_D1_79.md), incluido el error sobre el horizonte del titular y los denominadores |
| Constancia histórica | [LEDGER](LEDGER.md), inalterado; [sello por commit y SHA-256](CONGELACION_LEDGER_2026-09-09.json) |

Las 54 claves horarias de Lighter sin resolver en ocho días permanecen visibles; Binance está completo en el panel. La igualdad numérica de los NPZ no identifica qué horas vio julio ni demuestra identidad de insumos. Los informes originales y las correcciones fechadas se conservan separados.

## Custodia y recuperación

Los crudos, NPZ, planes y recibos completos permanecen fuera del repositorio, bajo `<USER_HOME>/Desktop/Laboratorio/`. Los informes anteriores describen sus cadenas de custodia. Las carpetas principales son:

- `I5_L3_CHECKPOINT_20260906_01`: L3 histórico.
- `I5_CHD_OCHO_20260907_02` e `I5_CHD_RESTO_71_20260907_01`: trades horarios y recibos de las claves ausentes.
- `I5_REPRODUCCION_OCHO_20260907_01` e `I5_REPRODUCCION_RESTO_71_20260907_01`: derivados y comparaciones.
- `I5_D1_79_20260907_01`: plan, cuantiles, resultados y lectura; sus hashes terminales están en el dictamen final.

La referencia de restauración científica es el **árbol completo** `1ca5ca6674ce55ad0aca149b7b5757a87f83f25e`, con la historia de julio que extrae del commit `74f0d6069efdc7be73693dd18ca39e9167892202` y las custodias externas ligadas por hash. Recuperar solo los once instrumentos no reconstruye el entorno. Para inspeccionar también los fixtures portables y controles posteriores, usar el árbol completo `f0fd1aa4cd54a48328c662a5278174c14aa6e52e`; esos arreglos no pertenecen al cierre original.

[ARCHIVO](../ARCHIVO.md) y el [inventario del lote 2](inventarios/V2_LOTE2_20260909.json) identifican las fuentes retiradas entonces y las seis compartidas que permanecían. El [lote 3](inventarios/V2_LOTE3_20260909.json) retira, sin editar sus cuerpos, `screen.py`, `pilot_observer.py` y `lighter_maker_capa1.py`; `artefacto.py`, `carril.py` y `ref_valida.py` conservan sus hashes activos. La especificación y las referencias de restauración anteriores no cambian. Recuperar código permite inspeccionarlo; no autoriza repetir la lectura. No queda otro encargo I5 abierto.
