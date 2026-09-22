# Mesa · 2026-09-09 · Cierre de la V2

Responde a PARA_LA_MESA_2026-09-09_V2_CIERRE.md, petición firmada
por Manuel. Base observada: ac165b942f635cde582b33e80f10b3216b444ae9.

**D1 · Lote 3 aceptado; simplificación V2 cerrada.**

La mesa acepta la auditoría del lote 3, con las dos precisiones
documentales enumeradas abajo. No requieren cambio de código.

El commit contiene las 100 rutas exactas de la entrega: 81 retiradas,
14 modificadas y cinco nuevas. La lista NUL coincide exactamente con
el diff sin detección de renombres. Los hashes finales de la entrega
coinciden; el LEDGER histórico, su sello, la especificación de D1 y las
tres fuentes compartidas conservadas mantienen sus hashes.

La mesa comprobó directamente en GitHub la CI de ac165b9: seis
verificaciones verdes, 476 tests pasados en 16,21 segundos y 49/49
mutaciones con su marcador. El job completo duró 72 segundos.
Las verificaciones locales completas constan en la auditoría de Code;
la mesa no las repitió.

| Lote | Commit | Run | Resultado |
|---|---|---|---|
| 0, base y reparaciones | 408d368 | 34254340273 | 8/8 verdes |
| 1, entradas concluidas | f0fd1aa | 34260532972 | 8/8 verdes |
| 2, I5 e históricos | 0f127e3 | 34286664630 | 8/8 verdes |
| 4, documentación | e1c2757 | 34381162392 | 8/8 verdes |
| 3, campaña y dependencias | ac165b9 | 34388283960 | 6/6 verdes |

Balance sobre los ficheros Python versionados de analysis/ y tools/,
entre 408d368 y ac165b9: 36.946 → 5.933 líneas físicas, reducción de
31.013. Las tablas de mutación pasan de tres arneses y 412 filas a
un arnés y 49 filas. Los tests pasados en CI pasan de 2.023 a 476;
esa cifra inicial no incluye sus omisiones ni el xfail.

Los tiempos corresponden a los jobs comunicados y observados.
La comparación no demuestra por sí sola cuánto ahorro corresponde
a cada cambio. La retirada conserva los puntos de recuperación
documentados en ARCHIVO.md y los inventarios.

Code añadirá al final de su auditoría del lote 3 una sección 7 fechada,
manteniendo íntegros los apartados anteriores, con estas correcciones:

1. Donde dice «16 funciones; 15 con cuerpo idéntico», debe constar:
   «Los 16 cuerpos son idénticos por AST. Quince funciones conservan
   su AST completo; en _correr cambia únicamente el argumento por
   defecto de ficheros». La diferencia está en la firma, no en el cuerpo.

2. La explicación de los cinco mapas de mutación como «sale el testigo
   exclusivo de un módulo retirado» no describe todos los casos.
   En las filas 77 y 182 se retira un testigo del mapa de esa mutación,
   pero las pruebas del censo real y del pre-vuelo real permanecen
   en la suite, adaptadas al árbol conservado. Los testigos sintéticos
   específicos permanecen en esas filas. No debe confundirse retirar
   un testigo del mapa con borrar su prueba.

**D2 · Cierre documental autorizado.**

Se autoriza un único commit documental sobre ac165b9:

- Crear este dictamen.
- Actualizar README.md: V2 terminada en ac165b9, cinco lotes con CI
  verde; enlazar este dictamen como decisión vigente; reflejar la
  integración autorizada por D3.
- Actualizar docs/LEDGER_ACTUAL.md: declarar la simplificación cerrada
  el 2026-09-09; registrar el commit, run y auditoría del lote 3;
  sustituir la base anterior por ac165b9 y distinguir los 16,21 segundos
  de pytest de los 72 segundos del job completo.
- Actualizar ARCHIVO.md: sustituir las dos declaraciones de retirada
  pendiente por el cierre publicado del lote 3, con su commit y run.
- Incorporar los documentos aprobados en D4.

La única ejecución pendiente de este cierre es su publicación
documental y su integración según D3. Después no queda otra actuación
autorizada sobre el código ni un nuevo objeto científico aprobado.

Los textos distinguirán autorización de ejecución: este dictamen
autoriza integrar main; no afirma que esa publicación ni su CI hayan
ocurrido antes de disponer de sus recibos.

El LEDGER histórico, su sello, los inventarios, los relevos anteriores
y la evidencia científica se conservan íntegros.

**D3 · Sí: main entra en este mismo cierre.**

Se autoriza integrar por fast-forward el commit documental de D2
en main, después de que ese mismo commit tenga CI verde en
codex/wip-m12.20.

La mesa ha comprobado el remoto real:
- codex/wip-m12.20: ac165b942f635cde582b33e80f10b3216b444ae9.
- main: 7ba8c6c19d97010f408dd8563fe8dd569acb4c4d.

main es ancestro de ac165b9: 34 commits de avance y ninguna divergencia.
Code volverá a comprobar las referencias inmediatamente antes de
publicar. No se autoriza commit de fusión, force push, rebase ni
publicación de otros cambios.

La integración exige su propia CI en main. La autorización de esta
secuencia está completa; no requiere otra consulta a Manuel.
No incluye cambiar la visibilidad del repositorio.

**D4 · Destino de los documentos.**

Rutas de origen relativas a quant-system:

| Documento | Decisión |
|---|---|
| docs/AUDITORIA_CODE_2026-09-08_CI_I5_REPARACION.md | Incorporar íntegro. |
| docs/AUDITORIA_CODE_2026-09-08_CI_ANCLAS_SELLADAS.md | Incorporar íntegro. |
| docs/AUDITORIA_CODE_2026-09-08_V2_LOTE1.md | Incorporar íntegro. |
| docs/AUDITORIA_CODE_2026-09-09_V2_LOTE2.md | Incorporar íntegro. |
| docs/AUDITORIA_CODE_2026-09-09_V2_LOTE4.md | Incorporar íntegro. |
| docs/AUDITORIA_CODE_2026-09-09_V2_LOTE3.md | Incorporar conservando el cuerpo y añadiendo exclusivamente el apartado 7 dispuesto en D1. |
| docs/PARA_LA_MESA_2026-09-07_PUSH_CI_Y_V2_SUSTRACCION.md | Incorporar íntegro como propuesta histórica, subordinada al dictamen posterior. |
| docs/OPCIONES_POST_LAB_2026-09-08.md | Conservar fuera de quant-system, sin modificar. |
| INFORME_QUANT_SYSTEM.md | Conservar fuera de quant-system, sin modificar; no reescribir el briefing de julio ni presentarlo como estado vigente. |
| docs/PARA_LA_MESA_2026-09-09_V2_CIERRE.md | Incorporar íntegra la petición firmada que origina este dictamen. |

La petición de hoy es el décimo documento sin versionar, adicional
a los nueve enumerados en ella. Su contenido coincide con el adjunto
salvo la representación de los saltos de línea.

Destinos externos de los dos documentos excluidos:
- <USER_HOME>/Desktop/Laboratorio/docs/OPCIONES_POST_LAB_2026-09-08.md
- <USER_HOME>/Desktop/Laboratorio/docs/INFORME_QUANT_SYSTEM_2026-07-02.md

Conservar sus bytes, comprobar la copia mediante SHA-256 y retirar
después únicamente los dos originales no versionados de quant-system.
No sobrescribir un destino existente. No alterar ni hacer staging en
el .git del laboratorio.

**Estado científico y límites.**

I5/D1 sigue cerrado como diagnóstico retrospectivo post hoc.
El +18,24 permanece retirado como fundamento de una ventaja operable.

En la celda compañera de 25 segundos, la ampliación que añade
through-con-at lleva 18,2368 a 2,5750 bps. Se conserva ese residuo
positivo con sus límites; no rehabilita la estrategia. La primaria
de cinco segundos pasa de 2,6101 a −1,0843 bps. Las referencias por
trades, las imputaciones de fills y la inferencia descriptiva siguen
siendo limitaciones del diagnóstico. Reproducción numérica exacta
no acredita identidad de insumos ni ejecuciones reales.

Continúan STOP, freezes, pins, Regla Cero y la D3 histórica de acceso
a datos. LIT desde 2026-06-30 y WTI desde 2026-06-05 permanecen
protegidos. La retirada de la campaña y la integración en main
no levantan esas restricciones.

No se abre otro frente. Un paper reencuadrado o cualquiera de las
opciones registradas exige su propia decisión con Manuel y la mesa.

**Orden de ejecución: opción A.**

Code aplica el cierre documental. El commit tendrá exactamente
12 rutas: los tres documentos existentes que D2 actualiza, este
dictamen y los ocho documentos que D4 incorpora. Los traslados
externos no forman parte del commit.

Antes de publicar:
- Comprobar el diff documental y los enlaces.
- Usar una lista NUL explícita y cotejar el índice con sus 12 rutas.
- Comprobar que no se incorpora ninguna credencial.
- Ejecutar una vez los cuatro controles rápidos: documental,
  completitud, registro de sonda y recuento.

No se repiten localmente la suite ni el arnés completo por este cambio
documental. No se modifica código, tests, configuración ni workflows.

Publicar el commit por fast-forward en codex/wip-m12.20 y esperar
su CI. Solo con ese commit en verde, avanzar main por fast-forward,
publicarlo y observar su CI propia.

Ante una divergencia o un resultado rojo, detener la secuencia
y devolver la causa; sin reintentos automáticos ni ampliación del diff.

El recibo final de Code identificará el commit, las 12 rutas,
los dos runs con sus resultados por paso, las referencias finales
de ambas ramas y los hashes de los dos documentos trasladados.
No se añade otro commit solo para registrar los runs.

Codex revisará después el commit y ese recibo.
