# Codex → Claude · M-15: corrección del bloqueante de limpieza Windows

2026-09-05. Retomado el relevo desde sección 4. Se leyó completa la auditoría
`<USER_HOME>/Desktop/quant-system/quant-system-ingesta/qs/docs/PARA_CODEX_2026-09-05_M15_AUDITORIA.md`.
HEAD y los tres hashes iniciales coincidían con el árbol auditado. No había procesos Python
activos en la consulta previa a la edición. No se repitieron las reproducciones largas de Claude.

## Incremento de esta intervención

Rutas relativas a `<USER_HOME>/Desktop/quant-system/quant-system-ingesta/qs`:

- `tools/mutacion_gate_b.py`: se añade `_quitar_solo_lectura` y se conecta mediante
  `shutil.rmtree(..., onexc=...)` a la limpieza compartida. Ante PermissionError aplica
  `os.chmod(ruta, stat.S_IWRITE)` y reintenta la operación una vez. Otros errores se relanzan;
  también se propaga el fallo del chmod o del reintento. Se conserva la validación previa de destinos.
- `tests/test_timeout_arnes.py`: el residuo del ejecutor sintético pasa a 0444, tanto en baseline
  como en filas. Se añaden tres focales: eliminación de temporal con archivo 0444, propagación
  por identidad de OSError ajeno sin chmod/reintento, y propagación del segundo PermissionError.
- `tools/mutacion_ref_valida.py`: sin cambios en esta intervención; consume la limpieza compartida.

El callback sigue la propuesta de la auditoría: clasifica PermissionError, no demuestra que
todo error de permisos provenga del atributo de solo lectura. Si el reintento falla, no lo oculta.
Requiere Python >= 3.12 para onexc, compatible con las versiones indicadas por Claude.

## Evidencia nueva

Ejecutado desde QS, salida directa y exit code 0:

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_timeout_arnes.py -q -p no:cacheprovider --basetemp '<USER_HOME>/OneDrive/Documents/Laboratorio/.tmp_m15_readonly_20260905_d'
```

**45 passed in 6.14s**. El archivo completo del focal de timeout se ejecutó una vez tras el
cambio. No se repitieron los otros dos archivos de la entrega anterior, ni pre-vuelo ni arneses.
`git diff --check`: exit 0; avisos de normalización LF/CRLF.

HEAD: `0147a2425a59743d08a77804b5fdedea5f54ea86`; rama comprobada `codex/wip-m12.20`.

| Archivo | SHA-256 de bytes tras el focal |
| --- | --- |
| tools/mutacion_gate_b.py | 5fb727148c8a4f8d2310d2a9eb58bbdad10db5742eb7d6511175cc6676460f94 |
| tools/mutacion_ref_valida.py | 47a94dafefb1f007c5565f150284b7a7be53e5ecf06bd62e4b265ae8ad1cf9d2 |
| tests/test_timeout_arnes.py | a21026c53881f3aaf236e7fdef1d2e18ee782c3ed507bda7ef32a78380178572 |

## Pendiente de Claude

Reauditar este incremento y comprobar la limpieza en el arnés real de Windows. Si ya no hay
bloqueantes, realizar las verificaciones largas acordadas una vez sobre árbol estabilizado,
sin editar durante la medida y con basetemp nuevo. Los 45 focales no acreditan las filas reales.
No se declara M-15 cerrado ni auto-ratificado.

Persisten los límites de descendientes de pytest, TOCTOU y huellas documentados en el relevo
anterior. No se añadieron filas ni cambiaron criterios de mordida, timeout o prioridades de salida.
Sin commit, stage, push, CI, red, limpieza de huérfanos antiguos, acceso a NPZ, freeze ni campaña.
El diff total contra HEAD conserva trabajo anterior de ambos; no atribuirlo a este incremento.

Este relevo se guarda en Laboratorio, dentro de la raíz de escritura de la sesión. Las dos
ediciones del repositorio se aplicaron con permiso del entorno mediante apply_patch. Los dos
primeros intentos con el envoltorio .bat rechazaron el formato y no modificaron archivos; el
ejecutable directo de apply_patch aplicó el parche correctamente. No se ha enviado mensaje a Claude.
