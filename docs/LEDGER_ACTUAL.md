# Ledger actual

Actualizado el 2026-09-09. Entrada vigente desde [README](../README.md). Este registro continúa al [LEDGER histórico](LEDGER.md), cuyos bytes se conservan según el [sello documental](CONGELACION_LEDGER_2026-09-09.json).

## Simplificación V2: cerrada el 2026-09-09

Mandato: [dictamen de la mesa del 2026-09-07, §5](DICTAMEN_MESA_2026-09-07_PUSH_CI_Y_V2.md). Retirar instrumentos concluidos sin romper dependencias conservadas ni reescribir su evidencia. No es una campaña de medición. Cierre: [dictamen de la mesa del 2026-09-09](DICTAMEN_MESA_2026-09-09_V2_CIERRE.md), que acepta el lote 3 y autoriza el commit documental de cierre y la integración en `main`.

| Tramo | Estado | Referencia |
|---|---|---|
| Lote 0, base y reparaciones | Cerrado; CI verde | `408d368`, run `34254340273` |
| Lote 1, entradas cerradas | Publicado; CI verde | `f0fd1aa`, run `34260532972`; [inventario](inventarios/V2_LOTE1_20260908.json) |
| Lote 2, I5 y herramientas históricas | Publicado; CI verde | `0f127e3`, run `34286664630`; [inventario](inventarios/V2_LOTE2_20260909.json) |
| Lote 4, documentación | Publicado; CI verde | `e1c2757`, run `34381162392`; [inventario](inventarios/V2_LOTE4_20260909.json) |
| Lote 3, campaña y dependencias | Publicado; CI verde | `ac165b9`, run `34388283960`; [auditoría de Code](AUDITORIA_CODE_2026-09-09_V2_LOTE3.md); [relevo](RELEVO_CODEX_2026-09-09_V2_LOTE3.md) e [inventario conjunto](inventarios/V2_LOTE3_20260909.json) |

Las CI cerradas se registran a partir de los informes de Code, incorporados a `docs/` con el cierre. La base es `ac165b9`, con seis verificaciones verdes en el run `34388283960`: `pytest` con 476 tests pasados en 16,21 segundos, el arnés de referencias con 49/49 mutaciones detectadas y los cuatro controles generales (documental, completitud, registro de sonda y recuento); el job completo de CI duró 72 segundos. Salieron únicamente los dos arneses de la campaña retirada. Una CI verde acredita los controles ejecutados, no una lectura científica.

Los lotes 1 y 2 retiraron 53 rutas. Sus commits suman 11.030 líneas eliminadas y 2.691 añadidas, incluidas documentación y pruebas: reducción neta de 8.339 líneas. [ARCHIVO](../ARCHIVO.md) conserva los motivos y puntos de recuperación. El lote 3 retiró 81 rutas antiguas, dos de ellas con pruebas compartidas trasladadas a rutas nuevas, en un commit de 100 rutas con +4.294/−45.775 líneas. Salieron la campaña, la receta maker, `screen.py`, H1/H3/H8 y sus consumidores exclusivos. Permanecen los módulos genéricos y los servicios de captura y respaldo. Balance entre `408d368` y `ac165b9` sobre los ficheros Python versionados de `analysis/` y `tools/`: de 36.946 a 5.933 líneas físicas; las tablas de mutación, de tres arneses y 412 filas a un arnés y 49; los tests pasados en CI, de 2.023 a 476. La comparación no atribuye el ahorro de tiempo a cada cambio.

Siguiente actuación autorizada: ninguna sobre el código. El dictamen de cierre autoriza un único commit documental sobre `ac165b9` y su integración en `main` por fast-forward una vez que ese commit tenga CI verde en `codex/wip-m12.20`; la ejecución, sus runs y las referencias finales constan en el recibo de Code. No queda otra actuación autorizada ni un nuevo objeto científico aprobado.

## Objeto cerrado: I5/D1

**Cerrado el 2026-09-07**, como diagnóstico retrospectivo post hoc, por el [dictamen final](DICTAMEN_MESA_2026-09-07_I5_D1_79.md). No queda una corrida pendiente sobre sus 79 días. La reproducción numérica exacta de la receta permite estudiar su sensibilidad; no acredita identidad de insumos, ejecuciones reales ni rentabilidad operable.

El [índice del expediente](INDICE_EXPEDIENTE_I5.md) reúne especificación, resultados, correcciones, custodias y restauración. Se conservan tanto el titular histórico como los residuos positivos y las limitaciones de la lectura. No se ajusta el analizador después del resultado.

## Nuevo objeto científico

**Ninguno aprobado.** No se abre una lectura desde el residuo de D1 ni desde una propuesta sin decisión propia. Cuando exista un objeto aprobado, tendrá una entrada separada que enlace su pregunta y falsación, estimando, fuentes y ventanas autorizadas, decisión fechada, plan fijado y recibo de lectura. Este registro no crea ahora ese objeto ni su diseño.

## Límites que continúan vigentes

STOP, freezes y pins se mantienen. LIT desde el 2026-06-30 y WTI desde el 2026-06-05 siguen siendo conjunto protegido; cualquier acceso debe respetar el cometido aprobado y las condiciones de D3. Ni saldo de proveedor, ni recuperación de una herramienta, ni CI verde autorizan por sí solos una lectura o descarga.

Esta simplificación conserva datos, recibos, historia Git y documentos científicos. La captura, las copias y los servicios no forman parte del lote documental. Codex implementa; Code audita y ejecuta las suites largas. Cada tramo conserva su propia procedencia y resultado.
