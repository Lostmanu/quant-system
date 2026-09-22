# Codex → Code · M-14 post-auditoría (2026-09-04)

> HISTÓRICO SUPERADO COMO RELEVO OPERATIVO. Code auditó este corte el 5 de septiembre. El incremento
> y las tareas actuales están en `PARA_CODE_2026-09-05_M14_COBERTURA_FINAL.md`. Se conserva lo que
> sigue como registro de aquel árbol y de las comprobaciones realizadas entonces.

**Entrega WIP para auditoría independiente y corridas largas. No está ratificada.** Este documento
registra únicamente los cambios posteriores al dictamen de Code sobre M-14; debe leerse junto al
diff, nunca como sustituto suyo.

## Autoridad y límites

- Rama: `codex/wip-m12.20`.
- HEAD/base sin reescribir: `58ea72e82c457aa393d868990beec679837a4a8c`.
- Todo sigue sin commit y sin push; no se lanzó CI.
- No se usó red, sonda ni créditos; no se creó ningún freeze ni se abrió ningún `.npz` protegido de
  LIT/DOGE.
- STOP de producción vigente.
- Los recibos antiguos y demás untracked preexistentes son ajenos: no borrar, mover, añadir ni
  presentar como acreditados.
- Por orden de Manuel, Codex ejecutó sólo focales cortos. Code debe ejecutar las suites y arneses
  completos después de auditar el diff.

## Decisión normativa adoptada

Se conserva la **convergencia idempotente** del CAS en lugar de restaurar el rechazo absoluto de una
segunda copia. La regla exacta es:

> Un token produce un único efecto durable. Un reintento con el mismo token, el mismo preestado y la
> misma intención adopta el postestado ya sellado sin repetir el efecto. Cualquier divergencia de
> esquema, preestado, intención o postestado se rechaza.

Esto cierra el prefijo «CAS durable, estado en memoria todavía no adoptado» sin autorizar un segundo
consumo. No se acepta “parecido”: se comparan esquema, intención serializada, preestado y hash del
postestado. Se añadieron focales y mutaciones para cada negativa.

## Reparaciones del dictamen

### P0-1 y P0-2 · contrato real del recibo y fixture no circular

- `tools/censo_anclas.py` admite los cuatro campos que el productor emite siempre y que faltaban:
  `snapshots_candidatos`, `snapshots_obsoletos`, `snapshots_igual_L` y
  `reapariciones_snapshot`.
- El contrato del recibo de la máquina sube de esquema 3 a **esquema 4**. Los recibos antiguos de
  esquema 3 quedan obsoletos y no pueden cruzarse ni citarse como evidencia del árbol nuevo.
- `_recibo_coherente` ya no proyecta la salida del productor sobre `_FICHERO_CLAVES`: construye la
  entrada con la salida íntegra de `medir_bytes` y deja que el consumidor detecte cualquier
  divergencia.
- La lectura, parseo, autosello, esquema completo y procedencia del recibo se validan **antes** de
  llamar a `censar`; un recibo ilegible o incompatible no puede gastar el barrido de parquets.
- Los bytes del recibo validados en el pre-vuelo son los mismos que se ligan al resultado; no hay una
  segunda lectura que abra una carrera.

### P0-3 · replay exacto, no segundo efecto

- Se añadieron negativos para replay con otro preestado y para registro resellado con esquema ajeno.
- El registro durable de consumo pasa a esquema 3 e incorpora la identidad interna de su temporal
  CAS.
- La comparación `postestado_sha256` que Code señaló como redundante permanece por ahora como defensa
  explícita; no se presenta como una propiedad adicional ni como mutación aislable.

### P0-4 · prefijo `link + temporal` convergente

- El nombre impredecible exacto del temporal se incorpora al cuerpo **antes de sellarlo**. No se
  infiere autoridad de un nombre que sólo coincida con `.cas_*.tmp`.
- `leer_autenticado` sólo reconcilia `nlink == 2` si el temporal sellado existe en el mismo
  directorio, es el mismo inodo, es regular, contiene los mismos bytes y explica exactamente el
  segundo enlace. Cualquier alias externo o multiplicidad distinta permanece en STOP.
- La recuperación persiste el alta, retira ese alias autenticado, persiste la baja y comprueba la
  postcondición de exclusividad y bytes.
- También se cubre el prefijo «unlink hecho, fsync de baja pendiente»: una lectura que retorna en
  POSIX ha vuelto a persistir el directorio.
- Un fallo de limpieza ya no sustituye la excepción primaria. Se relanza la causa original con la
  incidencia de limpieza anotada/encadenada.
- Los valores del llamador se validan como JSON **antes** de crear el temporal y la identidad del
  objeto de `mkstemp` se captura inmediatamente. Así un valor no serializable o un fallo de escritura
  puede retirar sólo el temporal propio sin dejar un prefijo sin autoridad.

## P1/P2 del dictamen atendidos

- El wrapper público vuelve a tener una mutación que exige el artefacto canónico.
- `_leer_lock_gate_autenticado` tiene focales y mutaciones para forma del SHA, tipo no regular,
  ausencia, sustitución entre `lstat/open`, JSON malformado, esquema extra, otro freeze y contenido
  inválido.
- La carrera real de dos worktrees sincroniza ambos contendientes justo antes del `O_EXCL`; el
  perdedor debe ser exactamente `FileExistsError`, no cualquier `RuntimeError`.
- El recibo cambió de forma y por eso su etiqueta cambió a esquema 4.
- `.gitignore` deja visible **todo** intruso dentro de `gate_sellado`, incluso si casa con patrones
  globales posteriores como `*.tmp`, `*.pyc` o `smoke.log`. La excepción está al final del fichero y
  hay una prueba con esas tres formas.
- La autoridad bajo `git-common-dir` sigue siendo una limitación arquitectónica deliberada: coordina
  worktrees del mismo repositorio, no clones distintos. No se presenta como artefacto reproducible
  desde un clon limpio.
- Los recibos y censos firmados anteriores quedan obsoletos por el cambio del instrumento. Deben
  reemitirse y volver a cruzarse sólo después de commit/identidad estable; hasta entonces sus cifras
  no son citables.

## Evidencia corta ejecutada por Codex

- AST de 11 ficheros relevantes: `AST_OK 11`.
- `tests/test_eco_cas.py`: **18 passed**.
- `tests/test_censo_anclas.py + tests/test_cruce_ancla_por_ancla.py`: **47 passed** en el corte de
  reparación del censo.
- `tests/test_gate_dos_worktrees.py` más el focal del wrapper: **18 passed**; el focal adicional de
  patrones globales de `.gitignore`: **1 passed**.
- `tools/prevuelo.py --permitir-sucio`: rc 0; gate **22**, libro **187**, referencia **199**; sin
  anclas muertas ni tests inexistentes.
- Verificación manual con `git check-ignore --no-index`: intrusos `.tmp`, `.pyc`, `smoke.log` y un
  descendiente bajo `tx_control/` quedan visibles.

No se ejecutaron la suite completa ni ninguno de los tres arneses completos después de esta
reparación. Los verdes largos del dictamen anterior describen el árbol **anterior** a estos cambios.

## Trabajo de Code, en orden

1. Auditar el diff post-dictamen sin confiar en este relato. En particular, intentar romper la
   autoridad del temporal CAS, el replay exacto y el pre-vuelo del recibo.
2. Ejecutar desde `quant-system-ingesta/qs`, registrando rc y HEAD:

   - `.venv\\Scripts\\python.exe tools\\prevuelo.py --permitir-sucio`
   - `.venv\\Scripts\\python.exe -m pytest tests/ -q`
   - `.venv\\Scripts\\python.exe tools\\mutacion_libro_tx.py`
   - `.venv\\Scripts\\python.exe tools\\mutacion_gate_b.py`
   - `.venv\\Scripts\\python.exe tools\\mutacion_ref_valida.py`
   - `git diff --check` y `git status --short`

3. Atribuir cualquier fallo antes de editar. No aflojar mensajes, tests ni mutantes para obtener
   verde; si una defensa resulta redundante, declararlo y retirar guardia/fila juntas.
4. Si lo anterior queda sano, **todavía no citar las magnitudes históricas**: primero estabilizar y
   commitear el instrumento, después reemitir el barrido y el censo con identidad ligada a ese
   commit. Esa corrida larga requiere la autorización operativa correspondiente.
5. No hacer push ni CI sin orden expresa de Manuel.

## Formato de devolución

HEAD/base, `git status`, diffstat, hallazgos P0/P1/P2, cambios adicionales por fichero y causa, todos
los resultados con rc, y lista explícita de lo no acreditado. Code audita; no ratifica su propio
arreglo ni presenta el verde como argumento de ausencia de defectos.
