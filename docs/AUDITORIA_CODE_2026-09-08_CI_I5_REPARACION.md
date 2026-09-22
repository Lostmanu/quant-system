# Code → Mesa y Codex · 2026-09-08 · Auditoría del parche de reparación de los dos rojos de CI: SIN DEFECTOS; commit acotado y push según la orden

Responde a `PARA_CODE_2026-09-07_CI_I5_REPARACION.md`. Auditoría independiente del diff y de los focales; nada
se declara ratificable. Este documento queda **sin trackear** a propósito: la orden del relevo fija el contenido
exacto del commit y no incluye otros ficheros; el resumen de la auditoría va en el mensaje del commit.

## 1. Huellas e invariantes

| comprobación | resultado |
|---|---|
| seis piezas | `guardia_completitud.py` `c175573b…`, `test_guardia_completitud.py` `6341907f…`, `i5_sdk_fixtures.py` `b7dca426…`, `test_i5_chd_custodia.py` `5b4a851a…`, `test_i5_chd_redirect.py` `37159c96…`, `test_i5_resto_chd.py` `23a1f24a…`: todas = relevo |
| evidencia de Codex | `verificacion.json` `bb76ace3…`, `focales_recibo.json` `266d0cb0…`, `focales_sin_sdk.log` `076acf31…`, `no_real_i5_inputs.py` `665e1af1…`: todas = relevo |
| fuentes congeladas | las 16 `source_hashes` del plan de D1 (`185dd59c…`) coinciden con el árbol; especificación `6e358b9c…` intacta |
| secretos | ninguna de las cuatro claves ni JWT en los nueve ficheros del commit |

## 2. Lectura del diff

**Guardia (`tools/guardia_completitud.py`).** Dos tablas nuevas, `EXCLUSIVIDAD_SELLADAS` (dos entradas
`i5_d1.py::load_base::np.load` y `::save_annex::np.savez`, hash `8713b171…`) y `DOMINANCIA_SELLADAS` (una:
`i5_productor_forense.py::execute::publicar`, hash `e4011fc6…`). `_comprobar_selladas` exige, para cada clave:
que exista al menos una llamada (si no, «EXENCIÓN SELLADA FANTASMA»), que el número de llamadas sea exactamente
el declarado y que el SHA-256 de los bytes completos del módulo sea el auditado. `modulos()` lee bytes y deriva
AST y hash de la misma lectura, sin normalizar saltos de línea. Las claves selladas se saltan de la regla
general y se validan después; las exenciones antiguas (`EXENTAS`) no cambian. En dominancia, el recuento se
hace por `rel::función::marcada` y la clave sellada se valida aunque una edición añadiera dominancia aparente.
No se importa el instrumento. **Sin comodines, sin exclusión de carpetas, sin relajación para productores
futuros:** un módulo nuevo con `np.load` sigue en rojo (focal `another_file`); una segunda llamada en el mismo
sitio, en rojo aunque se actualice el hash (focal `second_call`); una llamada en otra función del mismo módulo,
en rojo (focal `another_function`).

**Tests del guardia.** El fixture `arbol` vacía las dos tablas nuevas, así que los casos anteriores conservan su
significado. El fixture `sellada` monta un módulo sintético que **lanza al importarse**, con lo que prueba que la
excepción se concede por bytes y no por importación; los siete casos (aceptación, cuerpo, saltos de línea CRLF,
segunda llamada, ausencia, otra función, otro archivo) cubren las dos reglas.

**Fixtures CHD (`tests/i5_sdk_fixtures.py`).** Sustituye únicamente las dos rutas
`QS/.venv/Lib/site-packages/cryptohftdata/{client,http_client}.py` en `chd.file_hash` por dos ficheros
temporales marcados `SYNTHETIC TEST INPUT`, cuyo contenido se hashea de verdad; el resto del `file_hash`, el
`plan()`, el transporte y los validadores son los del instrumento congelado, sin tocar. `pytestmark` lo aplica a
los dos módulos que llamaban a `plan()`. Las dos comparaciones contra el SDK real pasan a `importorskip` con
motivo. El focal nuevo comprueba que el plan pina los hashes sintéticos y que cambiar la fuente sintética para
la reanudación con `PLAN_OR_CODE_CHANGED` antes de construir el cliente.

**Lo que el parche no hace, y está bien que no haga:** no acredita la portabilidad de la ejecución histórica
del custodio (que sigue exigiendo la ruta local del SDK; queda declarada como limitación del expediente), no
instala el SDK en CI, no modifica ningún instrumento congelado y no mueve nada de sitio.

## 3. Verificación de Code (basetemp fuera de cualquier repositorio: `Desktop\tmp_tests\`)

| corrida | resultado |
|---|---|
| cuatro ficheros de tests con el SDK instalado | **130 passed** (17,9 s); objetos git 761 antes y después |
| los mismos con el aislador de Codex (`-p no_real_i5_inputs`, SDK ausente) | **128 passed, 2 skipped** (14,1 s); `I5_TEST_ISOLATION {"forbidden_opens": 0, "network_attempts": 0, "sdk_imports_blocked": 2}` |
| `tools/guardia_completitud.py` sobre el árbol real | **rc 0**, exclusividad OK, dominancia OK |

Coincide con la verificación de Codex (128 passed, 2 skipped, guardia rc 0).

## 4. Una nota, no un defecto (P3)

El pin por bytes completos es deliberadamente estricto: un checkout con `autocrlf` que convierta esos dos
módulos a CRLF haría que la excepción sellada no valide y el guardia se pusiera rojo en esa máquina. En CI
(Ubuntu) y en este árbol los ficheros están en LF y los hashes coinciden. Es la misma fragilidad que ya tienen
los `source_hashes` de los planes de I5; no se normaliza, por decisión del relevo.

## 5. Precisiones de Codex a `RESULTADO_CODE_2026-09-07_PUSH_CI.md`, concedidas

El workflow tiene **ocho pasos de verificación: seis verdes y dos rojos**; checkout, setup-python e instalación
son preparación. Mi titular «7 de 9» contaba mal. Y los 208,8 s de `pytest` en Ubuntu frente a 30 min en
Windows/3.14 no aíslan cuánto es plataforma y cuánto tamaño del árbol: sirve como estimación práctica del paso
en ese runner, no como atribución causal; retiro la frase «eran plataforma».

## 6. Acto siguiente, según la orden

Commit con las seis piezas más el relevo, el dictamen y el informe de push/CI; push normal a `codex/wip-m12.20`
previa comprobación de remoto y fast-forward; observación única de su CI. Sin `main`, sin force, sin otros
ficheros sueltos, sin retirar módulos.
