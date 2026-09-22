# Relevo a Code: lote 2, retiro de I5 y entradas históricas

2026-09-09. Implementado por Codex. Pendientes: auditoría de Code, arnés completo,
commit, push y CI del lote. Sin descargas ni lectura científica.

## 1. Base, decisión y corrección de alcance

Base `f0fd1aa4cd54a48328c662a5278174c14aa6e52e`, rama `codex/wip-m12.20`.
La auditoría de Code del lote 1 documenta ocho verificaciones verdes en el run
`34260532972`: 1.965 passed, 5 skipped y 1 xfailed. Codex ha leído esa constancia;
no ha vuelto a consultar GitHub. El verde de la base no acredita este diff.

Se aplica el lote 2 aprobado en `DICTAMEN_MESA_2026-09-07_PUSH_CI_Y_V2.md`, §5.
La receta maker solo puede retirarse parcialmente: el eco aún utiliza sus funciones
y fija varias de sus fuentes por hash. No se refactorizan esos productores ni sus
controles para adelantar su retirada.

**Corrijo mi relevo anterior:** H1/H3/H8 no quedan libres al retirar I5. `screen.py`
también está en `eco_gate_b.CIERRE_DECISORIO` (línea 370 de la base). Se conservan
`screen.py`, los seis módulos H1/H3/H8 y sus seis ficheros de pruebas, todos intactos,
hasta resolver la retirada del eco en el lote 3. El índice ARCHIVO refleja esta corrección.

El orden siguiente será: este lote con su CI; lote 4 documental; lote 3 con el inventario
conjunto de la campaña. Este relevo no implementa los lotes siguientes ni autoriza
nuevas hipótesis, lecturas o accesos protegidos. STOP, freezes, pins y `main` permanecen.

## 2. Las 36 rutas del parche

La lista exacta está en `inventarios/V2_LOTE2_20260909.json`, campo `commit_paths`.

- **28 retiradas:** once instrumentos Python I5, su manifiesto de celdas, diez ficheros
  de tests I5 y su fixture del SDK; además `h2_staking`, `oxa_tick_gate2`,
  `recompute_s5_neff`, `verify_pilot_bhy_oriented` y `anatomia_del_18_24`.
  Son 16 módulos de ejecución, diez ficheros de pruebas, un fixture y un manifiesto.
- **Cinco ediciones:** `ARCHIVO.md`, `analysis/fetch_funding.py`,
  `tools/guardia_completitud.py`, `tests/test_guardia_completitud.py` y
  `tests/test_compuertas_ref_invalida.py`.
- **Tres altas:** el inventario, este relevo y `tests/test_lighter_maker_key.py`.

No se trasladan instrumentos ejecutables a una carpeta invisible al guardia.
Los documentos históricos y recibos, incluido el recibo I5 de etapa 0 versionado,
siguen en su sitio. No se modifican datos, planes ni custodias externas.

Cambios en las piezas conservadas:

1. `fetch_funding` recibe literalmente `get_funding`, `daily_funding` y `DAY_MS`
   de H2, con los imports que necesitan. Texto y AST de ambas funciones coinciden
   con la base; se conserva la entrada `main`. H2 deja de ser una dependencia.
2. Del guardia sale una excepción numpy de anatomía y las tres excepciones selladas
   de I5. Las dos tablas selladas quedan vacías; se conservan el mecanismo, sus
   pruebas sintéticas y las tres filas de mutación que lo comprueban.
3. El test del censo real exige los **quince sitios restantes**. Solo pierde las
   entradas de anatomía y las dos de I5. No se cambia su regla de inclusión ni su
   independencia de EXENTAS.
4. De `test_compuertas_ref_invalida` salen las dos pruebas exclusivas de anatomía
   y sus dos auxiliares. Las otras 16 funciones conservan su texto, incluidos
   los controles de referencia, publicación y el test real del careo.
5. La prueba de selección de clave del maker sobrevive en el nuevo fichero:
   conserva exactamente las dos aserciones del maker del test anterior, junto con
   su preparación. Solo salen las dos aserciones sobre el cliente I5 retirado.

## 3. Dependencias y restauración

El inventario contiene ruta, propósito, motivo, último commit, blob Git y hashes de
cada fichero retirado. La base completa de recuperación de este lote es `f0fd1aa`.

Se revisaron 328 rutas versionadas de código, configuración, comandos, hooks,
workflows, servicios y documentos; se excluyeron datos, recibos e inventarios históricos
de la búsqueda de dependencias. El único import desde un módulo conservado hacia
uno retirado era `fetch_funding -> h2_staking`, resuelto por el traslado literal.
No quedan imports ni comandos operativos hacia los retirados. Sí se conservan tres
referencias históricas a anatomía en comentarios/docstrings de `careo_capa2_vs_piloto`
(líneas 15, 57 y 64), además de las referencias documentales. No confundirlas con
dependencias ejecutables. El alcance es estático; no prueba imports dinámicos arbitrarios
ni el estado del despliegue remoto.

Frontera D1: las **16 fuentes** se cotejaron antes de retirar nada contra el plan
`185dd59c5b45fb97787261887a889edf75e1a4711eec3f484368a695d917d378`
y contra el árbol `1ca5ca6674ce55ad0aca149b7b5757a87f83f25e`:

- Diez fuentes I5 se retiran, sin editarlas previamente.
- Seis compartidas permanecen idénticas: `artefacto`, `carril`, `lighter_maker_capa1`,
  `pilot_observer`, `ref_valida` y `screen`.
- La especificación D1 conserva el hash
  `6e358b9c5f127819b8a8b805ade726f1f0bc6d8934b9279d8aa3d574fc5b91d7`.

La restauración científica requiere el árbol completo `1ca5ca6`, su historia de julio
y las custodias externas por hash. Para recuperar también los arreglos posteriores
de tests y guardias, usar el árbol completo `f0fd1aa`; no atribuirlos a `1ca5ca6`.
Recuperar una fuente no autoriza ejecutarla. Los seis untracked registrados al fijar la base permanecen
intactos, al igual que 295 ficheros de texto rastreados ajenos al parche.

Quedan para el retiro conjunto del eco: `confirm_runner`, `wallet_atlas`, `pilot_observer`,
los makers de capa 1, `maker_capa2_runner`, y los lectores/productores con consumidores
conservados (`confirm_screen`, `maker_capa2_screen`, `pilot_runner`, `pilot_screen`,
careo y censo de referencias). `pilot_runner` todavía remite al comando `pilot_screen`.
`estructura_chd_local` sigue requerido por el censo de anclas, consumo y arnés de referencia.

## 4. Verificación de Codex, sin suite larga ni lectura real

Artefactos: `<USER_HOME>\Desktop\Laboratorio\V2_LOTE2_20260909_01`.
Temporales comprobados fuera de Git y OneDrive:
`<USER_HOME>\AppData\Local\Temp\qs-v2-lote2-v8fuoko1`.

| Comprobación | Resultado |
|---|---|
| Pre-vuelo antes de los tests | rc 0; tablas 23 / 187 / 202 |
| Colección completa | 1.699 tests, sin errores |
| Delta de colección frente al log del lote 1 | salen 271 casos I5 y dos de anatomía; entra un caso de clave conservado en su nueva ruta; ningún otro cambio de nodos |
| Focales | 147 passed, 2 deselected, 12,55 s |
| Traslado de funding | texto y AST idénticos; paginación 1000+1, cursor, pausa, timeout, agregación diaria y vacío comprobados con respuestas sintéticas; cero red |
| Mutación focal `--solo CENSO` | 32/32 muerden, rc 0, 101,07 s; **no sustituye las 202 filas completas** |
| Guardia de completitud y tres controles documentales | rc 0 todos |
| Tres fuentes de arneses y sus tablas | hashes intactos frente a la base |

Los focales cubren guardia, selección de clave, compuertas sintéticas conservadas,
screen, agilidad y timeout. Las dos deselecciones son los tests reales conservados
del screen contaminado y el careo: no se ejecutan localmente para no abrir el decisivo.
Sus funciones permanecen idénticas y siguen incluidas en CI. No son omisiones añadidas
al código ni a su workflow.

Se usó el aislador de pytest ya existente, hash
`665e1af13fcca2f2f66c7149c49007fd0585a82f5d4869e4289444f74f6026ea`:
cero aperturas prohibidas y cero intentos de red en esos procesos instrumentados.
Ese contador no acredita todos los subprocesos del arnés. No se abrió ningún NPZ;
solo código y el plan D1 como metadato para cotejar fuentes. No se ejecutó ninguna
suite I5 ni se tocaron cuentas, servicios o claves reales.

## 5. Huellas de entrega

Rutas de código relativas a `quant-system-ingesta/qs/`:

| Pieza | SHA-256 |
|---|---|
| analysis/fetch_funding.py | 365444c7362d02f880f34291b9463da0eb624554a79d331369fdb100ed475e39 |
| tools/guardia_completitud.py | 8201830149dffe1dce1430752f730d2d38a6cf2d232cabee2bec8c4e26e6957b |
| tests/test_guardia_completitud.py | 8c56888cb437239aedd5a794ad52440e77889fbc19e31e2f8dd594a8799869cc |
| tests/test_compuertas_ref_invalida.py | 1a03811ad4c4409bf7c448a68070cdf3877112b67f2e709ddc32cc521f84b0ef |
| tests/test_lighter_maker_key.py | e9dd4ecef6c03dddb564092837802b6951673472cd1ec5995b993cae6fb8c6b8 |
| ARCHIVO.md (raíz) | 9419f3cca12ba5d4c94925c17f7adc7655611cfaf411391083cd37bdf3972485 |
| docs/inventarios/V2_LOTE2_20260909.json (raíz) | f6a47d15f5bdc59b6493026e37370a7e128257bfca15ba812f65121c91fd35ad |
| verificacion.json (carpeta de este lote en el laboratorio) | 96c22df57d4055c69f9893672b7c2d0a9ed54057ec6c6521cd50958d35a6f0e0 |
| commit-paths.nul (misma carpeta) | b4cf46756ba09ea76ef7b2054949f6eabbcf470a9610c7443849c738d08ad4ce |

## 6. Orden acotada a Code

Auditar diff, inventario, traslados literales, funciones de tests que permanecen y
frontera D1. Pre-vuelo primero con `--permitir-sucio`, porque el objeto es este diff
deliberado sobre `f0fd1aa`. No editar fuentes o documentos históricos para acomodar
una retirada. No ejecutar herramientas científicas archivadas.

Con el diff conforme, ejecutar **una vez el arnés completo de referencia, 202 filas**,
con árbol quieto y huellas antes/después, TEMP/TMP/TMPDIR fuera de repositorios y
PYTHONDONTWRITEBYTECODE=1. Desde `Desktop\quant-system\quant-system-ingesta\qs`:

```powershell
& .\.venv\Scripts\python.exe -B tools/prevuelo.py --arnes todos --permitir-sucio
& .\.venv\Scripts\python.exe -B tools/mutacion_ref_valida.py
```

Si cierra 202/202, rc 0 y sin deriva, quedan autorizados el commit de las **36 rutas
exactas** de `commit_paths` y el push fast-forward en `codex/wip-m12.20`.
Antes de publicar, comprobar el remoto real en la base esperada `f0fd1aa`; si cambió,
detener la publicación y conciliar el estado sin force. Comparar el índice completo
contra el inventario antes del commit; no usar `git add -A` ni integrar en `main`.

Para evitar el incidente CRLF del lote 1, la lista de rutas se entrega codificada
en UTF-8 y separada por NUL. Tras verificar su hash y su igualdad con `commit_paths`,
desde la raíz del repo:

```powershell
git add --pathspec-from-file=<USER_HOME>/Desktop/Laboratorio/V2_LOTE2_20260909_01/commit-paths.nul --pathspec-file-nul
```

Mensaje propuesto: `V2 lote 2: archivar I5 y entradas históricas sin romper el eco`.
Los seis untracked registrados quedan fuera: informe de julio, dos auditorías CI,
auditoría del lote 1, propuesta de V2 y `OPCIONES_POST_LAB_2026-09-08.md`.
Este último también es ajeno al lote y se conserva sin editar. La auditoría nueva de Code puede quedar
fuera del commit acotado, con su resultado identificado en el informe.

Observar una CI del commit y devolver sus ocho verificaciones. No se ordena otra
suite completa local además del arnés. Ante un fallo, conservar y atribuir antes
de reintentar. El lote documental espera la CI de este lote.
