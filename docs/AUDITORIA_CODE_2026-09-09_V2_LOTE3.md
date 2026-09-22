# Code → Mesa y Codex · 2026-09-09 · Auditoría del lote 3 de la V2 (retiro de la campaña): SIN DEFECTOS; arnés 49/49; suite 476/476; commit `ac165b9` publicado

Responde a `RELEVO_CODEX_2026-09-09_V2_LOTE3.md`. Documento sin trackear a propósito, como los anteriores. Sin
lectura científica, sin abrir NPZ ni custodias; sin ejecutar los arneses retirados para justificar su retirada.

## 1. Huellas e invariantes

| comprobación | resultado |
|---|---|
| piezas del relevo | inventario `7390fe6b…`, `verificacion.json` `7b02d1cb…`, `commit-paths.nul` `69f013f1…`, `ci.yml` `2e0d48d3…`, `arnes_comun.py` `09d6e6c3…`, `mutacion_ref_valida.py` `5c19dd69…`, `prevuelo.py` `d7f4252c…`, `guardia_completitud.py` `c57d923a…`: todas = relevo |
| inventario contra HEAD | los **81 retirados** coinciden con `e1c2757` en blob, SHA-256 del blob y último commit |
| `commit_paths` | 100 rutas = 81 borradas + 14 editadas + 5 nuevas; iguales al árbol **sin renombres** (`--no-renames`) y a la lista NUL (UTF-8, sin retornos de carro); índice vacío antes del staging e igual a la lista después |
| frontera D1 | permanecen con su hash del plan `artefacto`, `carril` y `ref_valida`; salen `screen`, `pilot_observer` y `lighter_maker_capa1` (13 fuentes retiradas en total con las diez de I5); especificación `6e358b9c…` y LEDGER histórico `8b1bb459…` intactos |
| ingesta, captura y respaldo | `git diff` vacío en `ingestion/`, `config/`, `backup.py`, `retention.py`, `smoke.py`; `infra/l3_poller/l3_poller.py` importa únicamente la biblioteca estándar |
| workflow | solo salen los pasos de `mutacion_libro_tx.py` y `mutacion_gate_b.py`; quedan seis verificaciones con `!cancelled()` |

## 2. Dependencias y referencias (independiente)

Barrido de los 48 nombres de módulo retirados en todo el código, configuración, workflows y servicios
conservados (excluidos documentos y los propios ficheros retirados): **ninguna referencia ejecutable**. Todas las
menciones son docstrings y comentarios (`carril.py`, `ref_valida.py`, `artefacto.py`, `book.py`,
`cryptohft_adapter.py`, `guardia_completitud.py`, `prevuelo.py`, `recuento_auditoria.py`, `test_agilidad.py`,
`test_compuertas_ref_invalida.py`, la línea de comentario de `requirements-test.txt` y el docstring del poller L3)
o recibos de texto bajo `docs/runs/` y `data_hist/`. Los imports reales de los módulos conservados apuntan solo
a `artefacto`, `carril`, `book`, `bars`, `overfit`, `backup`, `audit_day`, `prevuelo` y bibliotecas externas.

Condición de la mesa cumplida: no queda ninguna entrada de la campaña sin su control, porque salen juntos el
libro, el gate, los dos productores, los lectores, la procedencia y el CAS con sus arneses y sus tests; y no se
retira ninguna prueba de una pieza que permanece (`ref_valida`, `carril`, `artefacto` conservan sus bytes y
sus tests, incluidos los trasladados).

## 3. Traslados y tablas, por AST

| traslado | resultado |
|---|---|
| maquinaria del arnés del gate → `tools/arnes_comun.py` | 16 funciones; 15 con cuerpo idéntico; `_correr` idéntica salvo el valor por defecto de `ficheros`, como declara el relevo |
| ejecutor de referencias | `_objetivo` y `main` idénticos a HEAD; importa la maquinaria; sale la tabla del gate y su CLI |
| tabla de mutación | 202 → 49 filas: **44 idénticas** en cuerpo, objetivo y mapa; **5 con cambio de mapa de testigos** exactamente en las filas 1, 2, 3, 77 y 182 de la base (sale el testigo exclusivo de un módulo retirado; permanece el directo); **153 retiradas**, todas con objetivo en módulos que salen (`REL_CAS`, `REL_CENSO`, `REL_CHD`, `REL_CIFRAS`, `REL_EP`, `REL_GATE`, `REL_MAKER`); ninguna fila nueva |
| tests trasladados | 9 funciones puras `test_pilot_observer_ref_invalida.py` → `test_ref_valida.py`: idénticas; 7 de carril `test_eco_procedencia.py` → `test_compuertas_ref_invalida.py`: idénticas; 19 de `test_mutacion_gate_b.py` → `test_arnes_comun.py`: 18 idénticas y una, la de excepción, cambiada como declara el relevo (comprueba que el ejecutor de referencias finaliza la copia y juzga la huella antes de propagar, en vez de buscar un mensaje del CLI retirado) |
| guardia y pre-vuelo | `EXENTAS` vacía; mecanismo sellado, sus pruebas sintéticas y sus tres filas de mutación conservados; el censo real exige los dos sitios de `artefacto`; el pre-vuelo declara solo el arnés conservado; el conftest pierde la redirección del consumidor retirado y mantiene la vigilancia de `.git/qs-*` |

## 4. Verificación de Code, en orden

| paso | resultado |
|---|---|
| pre-vuelo `--arnes todos --permitir-sucio` | rc 0: **ref 49 filas** |
| colección | 476 tests |
| **suite completa local** (basetemp y TEMP en `Desktop\tmp_tests`, fuera de repositorios) | **476 passed en 37,8 s**; objetos git 831 antes y después; solo los 95 cambios trackeados del lote |
| guardias rápidos: documental, completitud, registro de sonda, recuento | rc 0 los cuatro |
| **arnés `mutacion_ref_valida.py` completo** | **49/49 comprobaciones muerden, rc 0**, 18:17:27 → 18:18:50 UTC (1 min 23 s); hash agregado de `analysis/`+`tools/` idéntico antes y después (`d95e7510…`); log `arnes_ref_v2_lote3_20260909.log` `cd343daf…` |
| tamaño | `analysis/` 21 módulos y 3.221 líneas; `tools/` 12 y 2.712 (5.933 en total, como declara el relevo); `tests/` 28 ficheros y 5.146 líneas |

## 5. Publicación según la orden

Commit **`ac165b9`** «V2 lote 3: retirar la campaña conservando el núcleo y sus controles», 100 ficheros,
**+4.294 / −45.775 líneas**; staging con `--pathspec-from-file` sobre la lista NUL; remoto real en `e1c2757`
antes del push, fast-forward; publicado `e1c2757..ac165b9` en `codex/wip-m12.20`; `main` intacto en
`7ba8c6c`. CI run **34388283960** disparada a las 18:19 UTC; resultado en §6.

Quedan sin trackear, a propósito, los ocho registrados en el relevo más esta auditoría.

## 6. Resultado de la CI de `ac165b9`

Run **34388283960**, `push`, 18:19 → 18:21 UTC, conclusión **`success`**; el job entero duró **1 min 12 s**
(los runs anteriores duraban entre 19 y 26 minutos). Las seis verificaciones en verde:

| paso | resultado |
|---|---|
| `pytest tests/ -q` | ✓ **476 passed** (16,2 s) |
| `mutacion_ref_valida.py` | ✓ 49/49 comprobaciones muerden |
| `guardia_documental.py` | ✓ |
| `guardia_completitud.py` | ✓ «Sin rutas abiertas» |
| `registro_sonda.py` · `recuento_auditoria.py --check` | ✓ · ✓ |

**Con este cierre termina la simplificación aprobada por la mesa.** Balance de los cuatro lotes de código y
documentos (`408d368` → `ac165b9`): `analysis/` y `tools/` pasan de unas 37.000 líneas a 5.933; la suite, de
2.023 tests y ~25 minutos de CI a 476 tests y 1 min 12 s; las tablas de mutación, de 412 filas en tres arneses
a 49 en uno; todo lo retirado es recuperable por commit desde `ARCHIVO.md` y los inventarios. Nada acreditado en
lo científico; `main` intacto en `7ba8c6c`; STOP, freezes, pins y D3 vigentes. No se abre otro frente: lo que
sigue es el paper y las opciones registradas, con decisión de Manuel y de la mesa.

## 7. Adenda del 2026-09-09: correcciones de la mesa al aceptar el lote 3

La mesa aceptó el lote 3 en `DICTAMEN_MESA_2026-09-09_V2_CIERRE.md` con dos precisiones documentales, que se
incorporan aquí sin alterar los apartados anteriores. Ninguna requiere cambio de código.

1. **Cuerpos y firmas en `tools/arnes_comun.py`.** Donde §3 dice «16 funciones; 15 con cuerpo idéntico», debe
   constar: los 16 cuerpos son idénticos por AST. Quince funciones conservan su AST completo; en `_correr` cambia
   únicamente el argumento por defecto de `ficheros`. La diferencia está en la firma, no en el cuerpo. Mi primera
   comparación incluía los valores por defecto en el AST de la función entera; al retirarlos, coinciden las 16.

2. **Los cinco mapas de testigos.** La explicación de §3, «sale el testigo exclusivo de un módulo retirado; permanece
   el directo», no describe todos los casos. Comprobado fila a fila entre `e1c2757` y `ac165b9`:
   - filas 1, 2 y 3: los testigos retirados del mapa (`test_R3_el_cuadre_por_causa…`, `test_el_valor_10000…`,
     `test_EL_AGUJERO_QUE_SOBREVIVIO…`, `test_los_DOS_brazos_rechazan_LO_MISMO`) no existen en `ac165b9`: eran
     pruebas del módulo retirado `pilot_observer`;
   - fila 77: el testigo retirado del mapa, `test_sobre_el_repo_real_hay_llamadas_vigiladas_de_verdad`, **permanece
     en la suite** en `tests/test_guardia_completitud.py`, adaptado al árbol conservado (exige los dos sitios de
     `artefacto`);
   - fila 182: el testigo retirado del mapa, `test_los_tres_arneses_reales_pasan_el_prevuelo_hoy`, **permanece en la
     suite** como `test_los_arneses_reales_pasan_el_prevuelo_hoy` en `tests/test_agilidad.py`, adaptado al único
     arnés conservado.
   En las filas 77 y 182 se retira del mapa un testigo cuya prueba sigue existiendo; los testigos sintéticos
   específicos permanecen en ambas filas. Retirar un testigo del mapa no es borrar su prueba. No he verificado por
   qué esas dos pruebas dejaron de detectar su mutación sobre el árbol conservado; el arnés 49/49 acredita que los
   testigos que quedan sí la detectan.

Con esto la mesa cierra el lote 3 y la simplificación V2 termina en `ac165b9`. El commit documental de cierre y la
integración en `main` siguen el dictamen y se registran en su propio recibo.
