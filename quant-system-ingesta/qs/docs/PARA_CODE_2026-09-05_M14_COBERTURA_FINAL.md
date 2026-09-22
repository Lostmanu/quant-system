# Codex → Code · M-14 · pase acotado posterior a la auditoría (2026-09-05)

**Entrega WIP, pendiente de revisión independiente. No ratificada.** Este es el relevo operativo
posterior a `PARA_LA_MESA_20260905_M14_REPARACION.md`. Sustituye las tareas pendientes del relevo
del 4 de septiembre; no modifica sus resultados históricos.

## Estado y límites

- Rama `codex/wip-m12.20`; HEAD `58ea72e82c457aa393d868990beec679837a4a8c`, sin reescribir.
- `main = origin/main = 7ba8c6c19d97010f408dd8563fe8dd569acb4c4d`, intactos.
- El WIP previo tenía 16 ficheros rastreados modificados; ahora son 17, por incorporar la corrección
  de redacción en `tools/cifras_paquete.py`. No confundir el WIP acumulado con el incremento de hoy.
- Sin commit, push, CI, red, sonda, gasto de créditos ni nuevos freezes.
- Ningún `.npz` real ni datos protegidos leídos. Los focales usan repositorios y datos sintéticos.
- Sin suite ni arnés integral ejecutados por Codex: Manuel reserva las corridas largas a Code.
- STOP de producción vigente. Los untracked ajenos y recibos históricos permanecen intactos.

Identidad del corte: `git diff --stat` da **17 ficheros, +2000/−258** frente a HEAD (incluye todo
el WIP previo; excluye documentos untracked). SHA-256 de los cuatro ficheros de código tocados hoy,
en el orden y con las rutas relativas a `qs/` que se indican:

```text
tests/test_eco_gate_b.py    8e5eaf9f85d59a9145d1c4c3013bed567b78d4500fa36901973750ad7843f253
tools/mutacion_gate_b.py   24a4a6218884f896f653526c9698196363de2fcb69263ee68267dc787c7d1beb
tools/mutacion_ref_valida.py 9c1e26068e4d4c5f44d537874588880a6eae861b5c39484f3cd88855f9173c91
tools/cifras_paquete.py    8268e041a119fee28edb12ff2e60f0f9ffd615a955edb4a089df6005c29a09e1
```

## Decisiones conservadas y alcance de la revisión

1. Se mantiene la convergencia idempotente exacta: mismo token, preestado e intención adoptan el
   postestado durable sin un segundo efecto. No equivale a autorizar una segunda lectura del gate.
2. `git-common-dir` se acepta como autoridad operativa LOCAL de V1, compartida entre worktrees.
   Un clon independiente no hereda el registro de consumo ni adquiere permiso para repetir un
   experimento de un solo uso. No se declara exclusión global entre clones.
3. Se revisaron por lectura las asociaciones añadidas en la reparación (9 de referencia y 8 del
   gate), su condición mutada y su test. No se reabrió la capa 3 ni se hizo una auditoría exhaustiva
   de todo el diff. Esta lectura es del implementador, no sustituye la revisión independiente.
4. Los resultados largos de Code (`1682 passed`, gate `22/22`, referencia `199/199`, libro
   `185/187` con dos saltos) son los declarados en su informe del 5 de septiembre para el árbol
   anterior a este incremento. No se atribuyen a este nuevo árbol ni a CI.

## Incremento de hoy, por fichero

### `tests/test_eco_gate_b.py`

Se añaden dos focales; no se cambia el algoritmo productivo:

- `test_M14_lock_autenticado_con_OTRA_cantidad_para_ANTES_del_gasto`: construye un lock válido
  pero con `n_bloques` distinto de la cantidad del manifiesto. Actualiza su SHA en el flag y el
  commit del repositorio SINTÉTICO, y comprueba que la autenticación del lock sí pasa. Así no puede
  tapar el caso la defensa anterior de SHA. Exige la causa exacta de discrepancia, cero llamadas
  adicionales al loader y ausencia del lock de lectura A2.
- `test_M14_lock_y_manifiesto_CONCORDANTES_permiten_la_lectura_sintetica`: control positivo del
  mismo recorrido; llega a `GENERALIZA` y acredita una llamada al loader sintético. Impide aceptar
  como solución que la nueva defensa rechace siempre.

### `tools/mutacion_gate_b.py`

- Una fila nueva retira únicamente la comparación de cantidades. Exige el marcador
  `[MUERDE-M14-CANTIDAD]`, distinto del marcador de causa incorrecta. El gate pasa de 22 a **23
  filas declaradas**, NO a 23 filas ya medidas.
- Se corrigen cabecera, docstring de `_juzgar` y salida: el criterio es el marcador o fragmento
  declarado, comparado por substring, no una prueba universal de causa única ni «por ausencia».
- No se cambia `_juzgar` ni sus criterios de aceptación en este incremento.

### `tools/mutacion_ref_valida.py` y `tools/cifras_paquete.py`

Sólo redacción: «marcador o fragmento declarado». Se conserva el prefijo de log
`N/N comprobaciones MUERDEN` que consume `_RE_ARNES`. El generador de cifras deja de reintroducir
la sobreafirmación que se retiró del emisor. No se reancla ninguna fila de referencia en este pase.

### Documentación

Este relevo y una cabecera de histórico en `PARA_CODE_2026-09-04_M14_REPARACION.md`. No se cambia
ningún documento firmado ni recibo para hacerlo parecer vigente.

## Revisión acotada de las asociaciones anteriores

Los criterios de esta tabla son los que exige el arnés, no una afirmación de cobertura exhaustiva.
El verde de ejecución de estas 17 filas procede del informe de Code, no de una nueva corrida mía.

| Familia | Condición observada en fila y prueba | Criterio declarado |
| --- | --- | --- |
| Ref 1 | JSON serializable antes de crear temporal; directorio sigue vacío | `CAS-PREVALIDA` |
| Ref 2 | Identidad del temporal capturada antes de escribir; limpieza tras fallo | `CAS-IDENTIDAD-TMP` |
| Ref 3 | Nombre exacto del temporal sellado; prefijo propio recuperable | `CAS-RECUPERA` |
| Ref 4 | Reconciliación `link + tmp`; retirada y exclusividad final | `CAS-RECUPERA` |
| Ref 5 | Limpieza no sustituye `ConsumoYaRegistrado` | `CAS-CAUSA` |
| Ref 6 | Replay con campo ajeno, aunque resellado | `DID NOT RAISE` |
| Ref 7 | Replay desde otro preestado con el mismo token | `DID NOT RAISE` |
| Ref 8 | Fixture usa la salida íntegra del productor, no una proyección | `salida íntegra del productor` |
| Ref 9 | Recibo inválido impide llegar al barrido | `RECIBO-PREVUELO` |
| Gate 1 | Wrapper entrega artefacto canónico al punto interno | `WRAPPER-ARTEFACTO` |
| Gate 2 | Forma canónica del SHA esperado | `LOCK-SHA-FORMA` |
| Gate 3 | Autoridad de tipo regular | `LOCK-TIPO` |
| Gate 4 | Identidad de pathname y descriptor | `LOCK-IDENTIDAD` |
| Gate 5 | JSON malformado no se convierte en autoridad | `LOCK-JSON` |
| Gate 6 | Campo extra del esquema del lock | `DID NOT RAISE` |
| Gate 7 | Lock de otro freeze | `LOCK-FREEZE` |
| Gate 8 | Contenido inválido, con `n_bloques=0` | `LOCK-CONTENIDO` |

Los nombres abreviados `CAS-*`, `LOCK-*`, etc. son los correspondientes marcadores `[MUERDE-M14-*]`.
Dos mutaciones distintas pueden compartir un test y marcador; eso no las convierte en dos
propiedades independientes. Las filas con `DID NOT RAISE` acreditan un modo de fallo, no una causa
exclusiva. No se aflojó ningún test ni se retiró una defensa para mejorar el recuento.

## Evidencia corta observada en esta sesión

- Dos focales nuevos del gate: **2 passed**, rc=0, 10,06 s.
- Cinco focales puros de `_juzgar` (positivo, causa ajena, marcador, colateral y grafía de pytest)
  más `test_un_log_CON_su_HEAD_pasa_y_su_cifra_entra_en_el_bloque`: **6 passed**, rc=0, 0,61 s.
- `tools/prevuelo.py --permitir-sucio`: rc=0; gate **23**, libro **187**, referencia **199**;
  anclas y tests declarados encontrados. No ejecuta mutantes.
- `git diff --check`: rc=0, con avisos de conversión LF/CRLF.
- En el pre-vuelo, `.git/qs-consumo-candidato` y `.git/qs-gate-b` no existen; el control
  `data_hist/eco_b` conserva una entrada, huella `1ecaa974524b`.

**Mutación nueva: NO ACREDITADA.** Se lanzó sólo esa fila con el runner estándar, pero la sesión
de ejecución dejó de ser recuperable y no se obtuvo su salida ni su rc. No se infiere éxito ni
fallo, no se suma al verde y no se repite una corrida larga para tapar la falta de evidencia.
Code debe medirla; antes de cualquier corrida debe confirmar que no queda una ejecución anterior
activa. No editar el árbol durante una medición.

## Devolución solicitada a Code

1. Revisar de forma independiente este incremento, sobre todo que la fixture divergente llegue a
   la comparación de cantidad y que su mutación falle por `[MUERDE-M14-CANTIDAD]`, no por otra
   guardia, error de colección o aserción incidental.
2. Ejecutar el pre-vuelo y el arnés del gate (ahora 23 filas). La fila nueva debe tener baseline
   verde y mordida por su marcador. Comprobar también el control positivo por su node-id.
3. Hacer las suites/arneses largos que correspondan de forma secuencial, sin editar el árbol; no
   declarar sus conteos por suma de los de ayer. Encabezar cada log con HEAD, estado y diffstat.
4. Si no quedan bloqueantes, devolver dictamen y proponer checkpoint local del lote WIP. No hacer
   push, CI, freeze ni barrido de datos por iniciativa propia. No incluir untracked ajenos.
5. Las cifras de anclas/empalmes de los recibos anteriores siguen NO CITABLES para este árbol:
   requieren commit estable y reemisión autorizada. `postestado_sha256` sigue declarado redundante,
   sin presentarlo como mutación aislable; los límites POSIX/Windows del CAS no cambian.

El aviso acordado de «mejoras contra errores» sigue pendiente: no se presenta esta entrega con una
mutación sin medir y sin cierre independiente como si hubiera terminado la fase técnica.
