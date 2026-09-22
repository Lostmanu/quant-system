# Relevo a Code: V2, primer tramo del lote 1

2026-09-08. Implementado por Codex; pendiente de auditoría de Code, arnés completo,
commit, push y CI de este lote. Sin lectura científica ni acceso remoto.

## 1. Base y decisión de la mesa

Base: `408d368d3b6d9cab2fdae9d1b25f211dd907aa15`, rama `codex/wip-m12.20`.
Code documentó ocho verificaciones verdes en el run `34254340273` sobre ese commit.
Codex ha leído esa constancia local; no ha vuelto a consultar GitHub.
El verde de la base no se atribuye al árbol modificado.

Se ejecuta el primer tramo del lote 1 aprobado en
`DICTAMEN_MESA_2026-09-07_PUSH_CI_Y_V2.md`, §5. Salen 18 módulos cerrados y sus
7 ficheros de tests exclusivos, 3.067 líneas entre ambos. No sale todo el capítulo 1:
hay dependencias conservadas que obligan a diferir una parte.

No se integra en `main`, no se inicia otro lote antes de la auditoría y la CI de este,
y no se reabre I5/D1. STOP, freezes, pins y ventanas protegidas permanecen vigentes.

## 2. Diff exacto y prueba de dependencias

El inventario `inventarios/V2_LOTE1_20260908.json` contiene las 25 rutas retiradas,
propósito, motivo, último commit, blob Git y SHA-256 local y del blob. `ARCHIVO.md`,
en la raíz, permite recuperar el árbol completo de la base. Los documentos históricos
conservan su texto, incluidas sus referencias a comandos que pasan al archivo.

Además de esas retiradas, solo cambian dos ficheros existentes:

- `tools/guardia_completitud.py`: salen seis excepciones de sitios retirados
  (`contrarian_runner`, `h3_power_precheck`, `run_day26`), y dos comentarios asociados.
  Ninguna regla, excepción sellada ni tabla de mutación cambia.
- `tests/test_guardia_completitud.py`: permanece el test del censo real con el mismo
  nombre y la misma fila de mutación. Su umbral numérico se sustituye por el inventario
  explícito de los 18 sitios que permanecen. Ese inventario no se deriva de EXENTAS
  ni de la salida del propio censo. Exige que todos sigan visibles, aunque aparezcan
  otros sitios que compensen una omisión.

Se inspeccionaron 351 rutas versionadas de código, documentación, configuración,
comandos, workflows, hooks y servicios. Las 18 sentencias de import que apuntan a
módulos retirados estaban en ficheros que también salen. En Python conservado solo
había las seis excepciones del guardia; después de retirarlas no quedan referencias
a esos nombres. Sin referencias en los comandos, workflows o servicios inventariados.
Es comprobación estática del alcance inventariado, no prueba universal de imports
dinámicos arbitrarios ni inspección del despliegue remoto.

Permanecen expresamente:

- H1/H3/H8, sus lectores y sus seis ficheros de tests: `screen.run_screen` todavía
  importa esos lectores. `screen.py` sigue fijado por el plan D1. Separar esa entrada
  requiere el retiro de I5 del lote 2, sin modificar sus fuentes congeladas ahora.
- `h2_staking.py`: `fetch_funding.py` importa `get_funding` y `daily_funding`.
  Resolver esa dependencia antes de retirar el módulo.
- `estructura_chd_local.py`: lo usan `censo_anclas`, conftest, pruebas de consumo y
  de `eco_cas`, y filas del arnés de referencia. Su retirada exige el inventario
  conjunto del lote 3, conservando las pruebas que sigan necesarias para referencia.

Los 322 ficheros de texto rastreados que permanecen fuera de las dos ediciones
conservan sus hashes del inicio. Las 16 fuentes de D1 y su especificación conservan
los hashes del plan. Los cuatro untracked previos también conservan sus hashes.
No se modificaron captura, backup, workflow, dependencias instaladas ni documentos
históricos. `probe_hist.py` tenía CRLF local y LF en Git: ambos hashes constan en el
inventario; su diferencia es exclusivamente de saltos de línea.

## 3. Verificación realizada y fallo conservado

Constancia fuera del repo:
`<USER_HOME>\Desktop\Laboratorio\V2_LOTE1_20260908_01`.
Todos los temporales de tests y del arnés se situaron bajo
`<USER_HOME>\AppData\Local\Temp\qs-v2-lote1-uuzo8ph3`;
se comprobó que esa raíz no pertenece a un repositorio Git.

1. Pre-vuelo antes de las pruebas: rc 0, tablas 23/187/202.
2. Guardia de completitud: rc 0, exclusividad y dominancia en verde.
3. Colección de la suite completa: 1.971 tests, rc 0; no se ejecutó la suite completa.
4. Primera tanda focal: 218 pasan y uno falla en 42,10 s. El fallo es el umbral
   `total >= 20`, frente a 18 sitios tras retirar seis de los 24 anteriores.
   Se conserva ese log, sin presentarlo como verde.
5. Tras corregir únicamente ese test: nuevo pre-vuelo 23/187/202, rc 0;
   los 43 tests del guardia pasan en 4,83 s. Los otros 176 focales, de código
   conservado sin cambios, no se repitieron.
6. Mutación focal de la fila «CENSO: volver a mirar solo analysis»: 1/1 muerde,
   rc 0; fallan por `assert` los dos tests declarados, incluido el actualizado.
   Esto comprueba la sensibilidad del cambio; no sustituye las 202 filas completas.
7. Guardia documental, registro de la sonda y recuento de auditoría: rc 0.

La tanda focal cubrió guardia, H1/H3/H8 y sus lectores, book, screen, adaptadores
L2/CHD/HL/Lighter, agilidad y timeout. Pytest usó el aislador de la reparación anterior,
fijado a `665e1af13fcca2f2f66c7149c49007fd0585a82f5d4869e4289444f74f6026ea`;
sus procesos instrumentados registraron cero aperturas prohibidas y cero intentos
de red. Ese contador no se atribuye a todos los subprocesos del arnés.

No se ejecutó ninguna suite I5 ni se abrió un NPZ. Del laboratorio científico solo
se leyó el plan de D1 para cotejar los hashes de sus fuentes, sin abrir su custodia.

## 4. Huellas de entrega

Rutas de código relativas a `quant-system-ingesta/qs/`:

| Pieza | SHA-256 |
|---|---|
| tools/guardia_completitud.py | cf9896ab671c07a9ff058258ec1c93c965b3f7c8a0f7ed6412841f660fc6a6e1 |
| tests/test_guardia_completitud.py | 9ce037ee820f56f78cc79d9f1fa07ff8fca1486f47c68dada79fab6bd6a10155 |
| ARCHIVO.md (raíz) | 450b964bd703d0e1c98422dc3a737fb1660f7088a751d6732c1caa911c4fa736 |
| docs/inventarios/V2_LOTE1_20260908.json (raíz) | 1d493f1a2e7749abef15eaf514aee22cd7b82c770f71f6751033d26f1d064d04 |
| V2_LOTE1_20260908_01/verificacion.json (laboratorio) | 99d340bd60a1cde09225dc038164df85636ec638e0190d584eab8089987ab8c4 |

`verificacion.json` conserva los comandos, rc, tiempos y hashes de los logs, incluido
el intento focal que encontró el umbral obsoleto. El pre-vuelo final y las tres tablas
siguen íntegros; no se ha ajustado ningún ancla para acomodar esta retirada.

## 5. Orden acotada a Code

Auditar este diff, el inventario de dependencias y las huellas. El pre-vuelo va primero,
con `--permitir-sucio` porque se audita deliberadamente este diff sobre `408d368`.
Verificar que no se cuelen cambios ajenos y que el inventario del test cubra los sitios
conservados. Sin reconstruir ni releer el expediente científico.

Con el diff conforme, ejecutar **una vez el arnés completo de referencia, 202 filas**,
con el árbol quieto y huellas de `analysis/` y `tools/` antes y después. Esta corrida
larga corresponde a Code; la mutación focal de Codex no la sustituye. Usar una raíz
temporal nueva fuera de repositorios, no el laboratorio con su `.git`.

Comandos desde `<USER_HOME>\Desktop\quant-system\quant-system-ingesta\qs`,
tras fijar TEMP/TMP/TMPDIR a esa raíz y PYTHONDONTWRITEBYTECODE=1:

```powershell
& .\.venv\Scripts\python.exe -B tools/prevuelo.py --arnes todos --permitir-sucio
& .\.venv\Scripts\python.exe -B tools/mutacion_ref_valida.py
```

Si el arnés cierra 202/202 con rc 0 y sin cambio de huellas, la mesa autoriza el commit
acotado y su push fast-forward en `codex/wip-m12.20`. La lista exacta de **30 rutas**
está en `commit_paths` del inventario: 25 eliminaciones, dos ediciones y tres documentos
nuevos (ARCHIVO, inventario y este relevo). Comparar el índice contra esa lista antes
del commit; no usar `git add -A`. Comprobar el remoto real antes de publicar; si no
está en la base esperada, detener la publicación y conciliar el estado, sin force.

Mensaje propuesto: `V2 lote 1: retirar 18 módulos cerrados y sus pruebas exclusivas`.
La auditoría nueva de Code puede quedar fuera del commit acotado, como en la ronda
anterior, con su resultado identificado en el informe de ejecución.

Los cuatro untracked previos quedan fuera: `INFORME_QUANT_SYSTEM.md`, las dos auditorías
de los parches CI del 08-09 y `PARA_LA_MESA_2026-09-07_PUSH_CI_Y_V2_SUSTRACCION.md`.
Sus bytes quedan conservados. No tocar `main`.

Observar una CI de este commit y devolver commit, run y estado de las ocho verificaciones.
No se ordena otra suite completa local además del arnés indicado. Si aparece un fallo,
conservarlo y atribuirlo antes de reintentar. El siguiente lote espera ese resultado.
