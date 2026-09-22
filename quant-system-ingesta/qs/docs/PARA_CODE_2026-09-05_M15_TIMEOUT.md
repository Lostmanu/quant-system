# Codex → Code · M-15 timeout: cierre local pendiente de auditoría independiente

2026-09-05. Manuel autorizó a Codex a modificar; Code audita y ejecuta las corridas largas.
No se declara ratificado este código por haber pasado sus focales.

## Base y alcance

HEAD permanece en `0147a2425a59743d08a77804b5fdedea5f54ea86`, rama `codex/wip-m12.20`.
Las referencias locales `main` y `origin/main` permanecen en
`7ba8c6c19d97010f408dd8563fe8dd569acb4c4d`. No se consultó el remoto.

Al entrar ya existían cambios de Code en los dos arneses y el fichero de tests del timeout
sin seguimiento. Se conservaron y completaron: el diff contra HEAD contiene trabajo de ambos,
no es un diff atribuible íntegramente a Codex. No se hizo commit, stage ni push.

Sólo se modificaron estos tres ficheros, más este relevo:

Rutas y comandos relativos a `<USER_HOME>/Desktop/quant-system/quant-system-ingesta/qs`.

- `tools/mutacion_gate_b.py`: salida completa del timeout, limpieza comprobada, veto por fallo
  de limpieza y juicio final sin retornos anticipados en el tramo protegido.
- `tools/mutacion_ref_valida.py`: mismo tratamiento compartido; también se eliminan los
  retornos anticipados preexistentes de base no utilizable y tests huérfanos.
- `tests/test_timeout_arnes.py`: focales ampliados y copia mínima para probar el orquestador
  sin copiar ni ejecutar toda la batería científica.

No se modificaron `_juzgar`, los criterios de mordida, las tablas de mutaciones ni el arnés
del libro (tiene ejecutor propio). Tampoco producción científica, freezes, controles de lectura,
datos protegidos o archivos ajenos. No hubo red, sonda, créditos externos ni apertura de NPZ.

## Qué aportó cada parte

De Code se conserva la captura exclusiva de `TimeoutExpired`, el sexto valor del resultado,
los canales normalizados con `_texto`, la base que aborta con 6 y el timeout de fila que no
acredita. No se aumenta el límite de 900 s ni se introduce un reintento automático.

Codex completa:

1. **Todas las salidas del tramo protegido pasan por el juicio final.** Referencia usa una
   excepción interna con código para los tres abortos esperados. La deriva mantiene sus códigos
   existentes (gate 2, referencia 4), con prioridad sobre un aborto normal. Las excepciones ajenas
   y cancelaciones se relanzan; un fallo de limpieza adicional se anota, no sustituye la original.
2. **No continuar con una limpieza fallida.** Tras timeout se comprueba la huella, se retiran
   estrictamente la copia y su basetemp y se vuelve a comprobar la huella antes de otra fila.
   Un fallo detiene. La limpieza final tampoco usa `ignore_errors`; si falla sin excepción
   primaria ni deriva, devuelve 7. Se validan todos los destinos antes del primer borrado,
   limitados a los temporales del arnés fuera del repo. El rechazo inicial de una ubicación
   dentro del repo sólo intenta `rmdir` sobre el directorio recién creado y aún vacío.
3. **Los dos canales completos llegan a la salida del proceso**, con nombre de fila, límite y
   etiquetas de canal. `muestra` sigue siendo sólo el recorte del resumen. Es texto normalizado
   con UTF-8/reemplazo, no conservación byte-idéntica ni un recibo persistido automáticamente.
4. **`--conservar` + timeout de fila detiene el gate** y conserva sus temporales. Continuar
   afirmando que se limpiaron sería contradictorio. Referencia no tiene esa opción.
5. **Focales del orquestador explícitamente sintéticos.** Se duplica una fila real de cada tabla;
   se simulan los resultados de base y mutaciones. La colección auxiliar usa funciones mínimas
   con sus nombres. El validador de base y el clasificador sí son los reales. Esto prueba flujo,
   recuentos y vetos; NO acredita semánticamente las mutaciones reales de esas filas.

## Evidencia de esta entrega

Corrida corta conjunta, salida directa de pytest sin pipe, exit code 0:

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_timeout_arnes.py tests/test_mutacion_gate_b.py tests/test_agilidad.py -q -p no:cacheprovider --basetemp "<USER_HOME>/OneDrive/Documents/Laboratorio/.tmp_m15_focales_20260905_c"
```

**103 passed in 7.53s**. Incluye continuidad/no-continuidad, control positivo sin timeout,
deriva antes y durante limpieza, fallos de retirada, aborto por huérfanos, cancelación con
fallo secundario, canales completos en base y fila, bytes/texto/ausencia, y `--conservar`.
Es evidencia local observada en la salida de la herramienta, no log de CI ni recibo firmado.

`python -B tools/prevuelo.py --permitir-sucio`: rc 0; gate 23, libro 187, referencia 199,
sin anclas ausentes ni declaraciones huérfanas detectadas. Es pre-vuelo estático, no mordida.
`git diff --check`: rc 0, sólo avisos de normalización LF/CRLF de Git.

SHA-256 de los bytes del árbol medido (antes de añadir únicamente este relevo):

| Fichero | SHA-256 |
| --- | --- |
| `tools/mutacion_gate_b.py` | `9bbbbb23f72fd155e997b13c21fc51ee8080f3a488f46ec36f2389b8e9fda671` |
| `tools/mutacion_ref_valida.py` | `47a94dafefb1f007c5565f150284b7a7be53e5ecf06bd62e4b265ae8ad1cf9d2` |
| `tests/test_timeout_arnes.py` | `455321a9af776de9abbfd77a95c2b983d431b6c648a390b52580cacbc10c25bf` |

## Límites y revisión que se solicita

- No se ha ejecutado la suite completa ni ningún arnés íntegro durante esta intervención.
  Los verdes íntegros anteriores de Code no se trasladan automáticamente a este árbol.
- **No se acredita contención de todos los procesos descendientes de pytest.** `subprocess.run`
  termina y espera al hijo directo; limpieza y huellas sólo comprueban el estado local observado.
  No se añadió un gestor de procesos/Job Object. La carrera por pathname tampoco desaparece.
  Code debe revisar este alcance sin renombrarlo «limpieza segura absoluta».
- Los errores de inspección de huella pueden abortar la medición; este lote no transforma la
  huella en aislamiento absoluto ni amplía sus rutas vigiladas.
- No se han añadido filas de mutación para estas nuevas ramas del orquestador: los 23/187/199
  no las acreditan. Revisar los focales y su sensibilidad antes de afirmar cierre independiente.

Code: audita especialmente los caminos combinados de fallo, la prioridad de resultados y el
alcance real de los tests sintéticos. Si no aparecen bloqueantes, corre las verificaciones largas
una vez sobre el árbol estabilizado, sin editarlo durante la medida; registra HEAD y hashes del
diff. Usar un basetemp nuevo (no reutilizar los de arriba). Sin push ni CI sin autorización.

Los otros huecos de eficiencia siguen en el ledger; no se abre otra plataforma de controles.
