# Code → Mesa y Codex · 2026-09-08 · CI de `1d83908`: las dos causas anteriores resueltas y una regresión nueva, el ancla de una fila del arnés de mutación del guardia quedó ambigua; vuelve a Codex

Continúa `AUDITORIA_CODE_2026-09-08_CI_I5_REPARACION.md` y ejecuta el §5 del relevo de reparación. Un push,
una observación de CI, sin reintentos. **El parche corrige lo que decía corregir y rompe una pieza que ni Codex
ni Code comprobaron: el pre-vuelo de los arneses de mutación.** Reproducido en local en segundos.

## 1. Publicación y CI

| dato | valor |
|---|---|
| commit | `1d83908` (nueve piezas exactas del relevo); remoto antes `1ca5ca6`, fast-forward; push `1ca5ca6..1d83908` a `codex/wip-m12.20`; `main` intacto en `7ba8c6c` |
| run | **34216477842**, `push`, 10:38 → 10:57 UTC (18 min 39 s), conclusión **failure** |

| paso de verificación | `1ca5ca6` (run anterior) | `1d83908` (este run) |
|---|---|---|
| `pytest tests/` | ✗ 40 failed / 1.963 passed | **✗ 16 failed / 2.007 passed / 5 skipped / 1 xfailed** (3 min 31 s) |
| `mutacion_libro_tx.py` | ✓ | ✓ |
| `mutacion_gate_b.py` | ✓ | ✓ |
| `mutacion_ref_valida.py` | ✓ | **✗ rc 5: pre-vuelo, ancla ambigua** |
| `guardia_documental.py` | ✓ | ✓ |
| `guardia_completitud.py` | ✗ 3 rutas | **✓ «Sin rutas abiertas»** |
| `registro_sonda.py` | ✓ | ✓ |
| `recuento_auditoria.py --check` | ✓ | ✓ |

**Resueltas:** la causa A (los 39 tests CHD por la ruta local del SDK: ahora 0 fallos, 2 omisiones declaradas) y
la causa B (el guardia de completitud, en verde también dentro de la suite). Ocho verificaciones: seis verdes,
dos rojas, por una sola causa nueva.

## 2. Causa C, nueva: un ancla del arnés `ref_valida` dejó de ser única

`tools/mutacion_ref_valida.py:687` tiene la fila «CENSO: ignorar el numero de llamadas de una exencion (la
exencion se hereda en silencio)», que muta en `tools/guardia_completitud.py` la línea exacta
`        if n != esperadas:` por `        if False:` y exige que caiga
`test_una_SEGUNDA_llamada_en_una_funcion_eximida_rompe_el_build`. El parche añadió en `_comprobar_selladas` una
segunda línea **textualmente idéntica** para el recuento de las excepciones selladas. El pre-vuelo del arnés
encuentra **dos ocurrencias**, declara «ANCLA AMBIGUA» y falla cerrado antes de mutar nada (rc 5 en CI).

Los 16 fallos de `pytest` son la misma causa vista desde los tests que ejercitan los arneses reales:
`test_agilidad.py::test_los_tres_arneses_reales_pasan_el_prevuelo_hoy` («el arnés 'ref' tiene problemas de
pre-vuelo») y 15 casos de `test_timeout_arnes.py` parametrizados con `[referencia]`, que esperan que el arnés
arranque y ahora reciben el abort del pre-vuelo (`assert 5 == 7`, «la base agotada tiene que abortar con su
propio código», etc.). Ninguno es un fallo de la lógica del guardia ni de los tests CHD.

**Reproducido en local** con la herramienta que existe para esto, en 2 segundos:

```
python -B tools/prevuelo.py --arnes todos
  arnes gate   23 fila(s) · OK
  arnes libro  187 fila(s) · OK
  arnes ref    199 fila(s) · 1 PROBLEMA(S)
*** [ref] ANCLA AMBIGUA (2 ocurrencias) en tools\guardia_completitud.py · fila: CENSO: ignorar el numero de llamadas…
rc=3
```

## 3. Lo que falló en el método, y es de Code tanto como de Codex

El relevo decía «no repetir arneses» y ninguno de los dos corrió el **pre-vuelo** de los arneses, que no es el
arnés: son segundos, no horas, y está escrito precisamente para «lo que se comprueba en segundos antes de lanzar
algo que tarda horas». Un cambio en un fichero que las tablas de mutación referencian (`guardia_completitud.py`
lo está en `mutacion_ref_valida.py`) obliga a pasar `prevuelo.py --arnes todos` antes de publicar. Queda como
regla de la lista de auditoría de Code para cualquier diff en `analysis/` o `tools/`. La CI hizo su trabajo:
es un control que existe, se dispara solo y ha informado.

## 4. Propuesta para la corrección (Codex implementa; Code audita con pre-vuelo esta vez)

1. **Desambiguar las dos anclas** sin cambiar la semántica: que el recuento de las selladas no repita
   textualmente la línea del recuento de `EXENTAS` (por ejemplo, un nombre de variable propio en
   `_comprobar_selladas`), o que la fila de mutación lleve el contexto de línea que la haga única. Cualquiera
   de las dos hace único el ancla; conviene además que la fila existente siga apuntando al recuento de
   `EXENTAS`, que es lo que su test declara.
2. **Cubrir las protecciones nuevas con el arnés**, porque la doctrina de la casa es que un test verde no
   prueba que la guardia que dice cubrir sea la que lo mantiene verde: tres filas nuevas en
   `mutacion_ref_valida.py` para el recuento sellado (`n != esperadas` de las selladas → debe caer
   `test_sellada_no_se_hereda…[second_call]`), el hash sellado (comparación SHA-256 → `[body]` y `[newlines]`) y la
   sellada fantasma (`if not n` → `[missing]`).
3. **Verificación exigible antes de publicar:** `prevuelo.py --arnes todos` rc 0, el arnés `ref` completo en
   local (199 filas, minutos), los cuatro ficheros de tests del parche, y `test_agilidad.py` +
   `test_timeout_arnes.py`. Después, commit acotado, push fast-forward y una CI.

Con eso, por lo medido en estos dos runs, las ocho verificaciones quedarían en verde. Hasta entonces la rama
publicada sigue siendo un punto de partida rojo y documentado; nada acreditado.

## 5. Estados

**push:** hecho · **CI:** observada, `failure`, 6 de 8 verificaciones verdes; A y B resueltas; C nueva y
reproducida · **reintentos:** ninguno · **`main`:** intacto · **instrumentos congelados:** intactos ·
**corrección:** devuelta a Codex.
