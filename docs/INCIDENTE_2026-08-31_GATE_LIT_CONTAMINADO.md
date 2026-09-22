# INCIDENTE · 2026-08-31 · El gate de lectura única del brazo LIT, sellado por un test

**Qué pasó.** Un test añadido por Code el 2026-08-30 —
`tests/test_eco_gate_b.py::test_el_gate_LIT_con_su_freeze_EXACTO_no_muere_por_esquema`— ejecutó el
camino completo de `preparar_lectura_gate` contra el árbol REAL y **publicó el conjunto sellado y el
lock de un gate de UN SOLO USO**, contra un freeze inventado por la fixture.

**Cómo se detectó.** Revisión adversarial del propio lote (2026-08-31), antes de entregarlo a la
mesa. No lo detectó ninguna guardia: lo detectó un atacante leyendo el árbol.

**Reincidencia declarada.** Es el mismo incidente que `tools/mutacion_gate_b.py` documenta como
E-32. La contramedida existente (`_huella()`) no lo vio porque se toma al arrancar el arnés, después
de que `pytest tests/` ya haya escrito.

---

## Causa

Tres cosas a la vez, y hacen falta las tres:

1. `analysis/eco_gate_b.py` — `GATE_SELLADO` es **relativo al cwd**, no a `repo_root`.
2. `preparar_lectura_gate` pasa `dest_dir=GATE_SELLADO` aunque reciba `repo_root`, así que el destino
   del sellado **no sigue** al repositorio que se le indica.
3. El test envolvía la llamada en `try/except RuntimeError` para comprobar que *no* moría por
   esquema — y con eso dejaba correr el camino BUENO entero hasta publicar.

## Los artefactos, con su huella EXACTA tomada antes de tocarlos

| ruta (relativa a `quant-system-ingesta/qs/data_hist/eco_b/`) | bytes | sha256 |
|---|---|---|
| `gate_read_lock.json` | 121 | `aa52b370de915ea03cefbbe3637e5289f3a0aeb813e6df5d5afef019ef6cc178` |
| `gate_sellado/flag.json` | 208 | `9c18fe5e218ffcfc09e73614f73f82b150e2425e05d47f41f0a63512df646712` |
| `gate_sellado/bar.json` | 655 | `86be8c76f9a7c04657e88b91efabaac3fea3b7a2db6e7da0041c42f83c0b4612` |
| `gate_sellado/manifiesto.json` | 1955 | `05545d6a58d7cdcce1572857ced6593b0a482e92b590a4c72ba733af1ff8f66f` |

Los cuatro con `mtime` **2026-08-31T01:10:38**, dentro del mismo segundo.

Contenido del lock, íntegro:

```json
{"fecha": "2026-08-30T23:10:38.741399+00:00", "hash_freeze": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "n_bloques": 18}
```

**NO se toca** `freeze_pins.json` (285 bytes, sha256
`43d77b07fdad66217a84777e549a9c37079389fa838233bc373ed8483cde5d2e`), que es el único artefacto
versionado del directorio y el freeze histórico real del brazo A2.

## Por qué son contaminación sintética y no un consumo legítimo

Cuatro razones, todas comprobables sobre los propios bytes:

- **No están versionados.** `git ls-files data_hist/eco_b/` devuelve únicamente `freeze_pins.json`.
- **Se crearon en el mismo instante**, dentro del mismo segundo.
- **`hash_freeze` es `"a" * 40`** — el `F` de fixture de `tests/test_eco_gate_b.py`, no un commit.
- **`n_bloques = 18`** son exactamente los días que fabrica `_set_replica(..., n_dias=18)`.

Su presencia fuerza `estado_lock_gate()` a devolver **LEIDA-Y-SELLADA**: la Fase 1 del brazo LIT
constaba como gastada. Restaurarlos restauraría el estado contaminado, no uno productivo válido.

## Limpieza controlada ejecutada (dictamen de la mesa, 2026-08-31)

1. **Vigilancia reforzada.** `_huella_eco_b()` en `tests/test_eco_gate_b.py` compara ANTES/DESPUÉS la
   existencia, el tipo y el SHA-256 de los **seis** artefactos operativos. La versión anterior sólo
   comparaba el `mtime` del lock y su comprobación del sellado quedaba anulada por un `or` en cuanto
   el lock existía — dejaba de vigilar justo cuando el árbol ya estaba contaminado.
2. **Corral en el test.** `GATE_SELLADO`, `FLAG_GATE`, `MANIFIESTO` y `BAR_GATE` se redirigen a
   `tmp_path` antes de llamar. Verificado: el sellado sale en el temporal de pytest.
3. **Acta.** Este documento, con las huellas de arriba.
4. **Custodia.** Los cuatro se mueven fuera de la ruta operativa antes de retirarlos.
5. **Retirada** de `data_hist/eco_b`, sin tocar `freeze_pins.json`.
6. **Verificación**: `SIN-LOCK`, focal, arnés, y árbol real idéntico al esperado.

## Lo que este incidente NO cierra

`GATE_SELLADO` **sigue siendo relativo al cwd** en producción. La receta ratificada manda correr en
un worktree: hoy el sello caería en el cwd de ESE worktree mientras el repositorio principal seguiría
diciendo SIN-LOCK, con la bala ya gastada. Derivarlo de `repo_root` es una corrección de producción
que **no** se hace aquí y queda declarada abierta.
