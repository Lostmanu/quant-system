# Code → Mesa · 2026-09-07 · Push de `1ca5ca6` publicado y CI observada: roja en dos pasos, por dos causas distintas; las otras siete verificaciones en verde

Ejecuta el §3 de `DICTAMEN_MESA_2026-09-07_PUSH_CI_Y_V2.md`. Un push, sin force, sin `main`, sin ficheros sueltos;
una observación de la CI, sin reintentos. **El push publica un punto de partida con fallos conocidos y ahora
medidos; no es base verde ni acredita L, F ni ninguna lectura protegida.**

## 1. Push

| dato | valor |
|---|---|
| comprobación previa | `git ls-remote`: `refs/heads/codex/wip-m12.20` = `refs/heads/main` = `7ba8c6c` en GitHub, igual que la referencia local; `7ba8c6c` es ancestro de `1ca5ca6` ⇒ fast-forward |
| push | `git push origin codex/wip-m12.20:codex/wip-m12.20` → `7ba8c6c..1ca5ca6`; remoto tras el push: `codex/wip-m12.20` = `1ca5ca6…`, `main` = `7ba8c6c…` sin cambios |
| CI disparada | run **34162262527**, `push`, `headSha` `1ca5ca6674ce…`, creado 21:12:13 UTC, terminado 21:36:54 UTC (**24 min 38 s**), conclusión **failure** |
| URL | `https://github.com/Lostmanu/quant-system/actions/runs/34162262527` |

## 2. Estado por paso (job `tests`, Ubuntu, Python 3.12)

| paso | conclusión |
|---|---|
| checkout, setup-python, `pip install -r requirements-test.txt -c requirements-lock.txt` | ✓ |
| `python -m pytest tests/ -q` | **✗** · `40 failed, 1963 passed, 3 skipped, 1 xfailed in 208,8 s` |
| `tools/mutacion_libro_tx.py` | ✓ |
| `tools/mutacion_gate_b.py` | ✓ |
| `tools/mutacion_ref_valida.py` | ✓ |
| `tools/guardia_documental.py` | ✓ |
| `tools/guardia_completitud.py` | **✗** · las mismas 3 rutas de los instrumentos I5 |
| `tools/registro_sonda.py` | ✓ |
| `tools/recuento_auditoria.py --check` | ✓ |

## 3. Causas de los 40 fallos de `pytest`

| causa | tests | ficheros |
|---|---|---|
| **A. Ruta local del SDK fijada en el instrumento CHD.** `i5_chd_custodia.plan()` hashea `QS/.venv/Lib/site-packages/cryptohftdata/{client,http_client}.py`: una ruta de la venv de Windows de esta máquina. En el runner no existe (`FileNotFoundError: …/qs/.venv/Lib/site-packages/cryptohftdata/client.py`) y el paquete `cryptohftdata` no está en `requirements-test.txt` (`ModuleNotFoundError`, 2 tests) | **39** | `test_i5_chd_redirect.py` 22 · `test_i5_chd_custodia.py` 16 · `test_i5_resto_chd.py` 1 |
| **B. Guardia de completitud** (`test_sobre_el_repo_real_el_censo_esta_VERDE`): las 3 rutas I5 ya identificadas | 1 | `test_guardia_completitud.py` |

Ningún fallo fuera de los tests I5 y del test del guardia. `test_gate_dos_worktrees::test_fuera_de_un_repositorio_git_el_gate_falla_CERRADO`
**pasó en CI**, lo que confirma que el fallo local era de fixture (temporal dentro del `.git` del laboratorio),
como dijo la mesa.

**Lo que la CI ha medido y el local no podía:** la causa A es un defecto de portabilidad de un instrumento
congelado. En esta máquina la ruta existe y los 39 tests pasan; en cualquier otra, ni siquiera puede
construirse el plan. No afecta a la evidencia de I5 (los planes y recibos ya emitidos pinan esos hashes como
constancia), pero sí a la afirmación «los focales corren en CI». Es una limitación del expediente que debe
quedar escrita.

**Dato lateral útil para la V2:** el mismo `pytest tests/` tardó **3 min 28 s en Ubuntu** y **30 min 53 s** en
esta máquina con Windows y Python 3.14. Los «45 minutos de suite» eran en gran parte un artefacto de la
plataforma, no del tamaño del árbol; el objetivo de «suite ≤ 5 min» ya se cumple en CI y el recorte debe
justificarse por complejidad, no por tiempo.

## 4. Opciones para la mesa (Code no toca nada sin orden)

- **Causa A.** (i) Los tres ficheros de tests omiten (`skip`) cuando el módulo `cryptohftdata` no es importable o
  la ruta de la venv no existe, con el motivo escrito: cambia los tests, no los instrumentos ni ningún plan
  (los planes pinan `tools/` y `analysis/`, no `tests/`); Codex implementa, Code audita. (ii) Retirar tests e
  instrumentos I5 del árbol activo en el lote 2 de la V2, ya aprobado, con `ARCHIVO.md` y restauración de
  referencia en `1ca5ca6`; la CI deja de ejecutarlos. (iii) Instalar el SDK en CI y hacer la ruta portable: **no**,
  exigiría modificar un instrumento congelado. Recomendación de Code: (ii) si el lote 2 es inminente; si no, (i).
- **Causa B.** El parche del guardia ya aprobado en el §4 del dictamen (excepciones de alcance exacto en
  `EXENTAS` y en `comprobar_dominancia`, hashes `8713b171…` y `e4011fc6…`): Codex implementa, Code audita.

Con A y B resueltos, la siguiente publicación tendría, por lo medido hoy, las nueve verificaciones en verde en
Ubuntu/3.12. Hasta entonces la rama publicada queda como punto de partida rojo y documentado.

## 5. Estados

**push:** ejecutado una vez, fast-forward verificado · **CI:** observada, conclusión `failure`, 7 de 9
verificaciones en verde, 2 en rojo por causas A y B · **reintentos:** ninguno · **`main`:** intacto ·
**acreditación:** ninguna. Logs: `scratchpad/ci_run_34162262527.log` y `…_failed.log` (Code).
