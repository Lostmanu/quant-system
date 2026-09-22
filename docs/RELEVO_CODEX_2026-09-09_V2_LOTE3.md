# Relevo a Code: lote 3, retirada conjunta de la campaña

2026-09-09. Base `e1c2757b1f492637aba62ef46ffe45be91405c67`, rama `codex/wip-m12.20`.
El lote 4 tiene CI verde, run `34381162392`, según la auditoría de Code. No se vuelve
a consultar ese run. Este diff aún no está cometido, publicado ni acreditado por CI.

## 1. Alcance de la mesa y del diff

Se ejecuta el retiro conjunto aprobado en el [dictamen V2, §5](DICTAMEN_MESA_2026-09-07_PUSH_CI_Y_V2.md).
El [inventario](inventarios/V2_LOTE3_20260909.json) fija **100 rutas**: 81 antiguas que
salen, 14 existentes editadas y cinco nuevas. Dos de las 81 son rutas de tests con
pruebas compartidas trasladadas; no se cuentan esas pruebas como retiradas.

- Salen los 14 módulos `eco_*`, incluido el libro, gate, productores, lectores,
  procedencia y CAS. Salen sus dos arneses exclusivos y herramientas de medida.
- Salen la receta maker, simulador y consumidores históricos; `screen.py`, H1/H3/H8
  y lectores; `exec_sim`, que importaba `screen`; la tabla de Student y su generador,
  cuyos consumidores eran el gate y nmin.
- Salen `estructura_chd_local`, censo de anclas, cifras del paquete y pruebas exclusivas;
  careo, censo de referencias y sonda antigua de retención con su validador.
- Permanecen el núcleo genérico, los adaptadores, la ingesta, captura y respaldo.
  Los 29 ficheros de estos últimos ámbitos inventariados conservan sus hashes.

No se conserva una entrada de la campaña quitándole su control. Los imports directos
y relativos, literales con nombres de módulo o fichero y configuración operativa no
dejan referencias ejecutables a los retirados. El inventario recoge las 149 aristas
de import que antes apuntaban a esas rutas y cómo se resuelven sus consumidores mixtos.
Este análisis estático no promete resolver destinos construidos arbitrariamente en runtime.

## 2. Qué se conserva de los controles

`analysis/ref_valida.py`, `carril.py`, `artefacto.py` y los libros y adaptadores conservan
sus bytes. Ninguna prueba se elimina para tapar un fallo de esos módulos.

| Pieza | Tratamiento |
|---|---|
| Maquinaria del arnés del gate | Dieciséis funciones pasan a `tools/arnes_comun.py`: cuerpos idénticos por AST. Solo cambia el valor por defecto de `ficheros` en `_correr`, que apuntaba a los dos tests retirados del gate; ahora apunta a `test_ref_valida.py`. El ejecutor de referencias pasa su propia lista explícita. |
| Ejecutor de referencias | `_objetivo` y `main` conservan su AST. Importa la maquinaria trasladada. Sale la tabla del gate y su CLI; no se copia un segundo ejecutor. |
| Mutación de referencias | 202 → 49 filas. Las 153 retiradas mutaban módulos que salen. Se conservan los cuerpos de las mutaciones restantes; cinco mapas de tests cambian según el apartado siguiente. |
| Guardia de completitud | Salen sus 13 excepciones por sitio. Permanecen reglas, mecanismo sellado y tres filas de mutación de las selladas. El censo real contiene las dos operaciones de `artefacto`; la cobertura de `tools/` sigue probada con fixtures sintéticos. |
| Pre-vuelo | Solo declara el arnés de referencias conservado. Mantiene validación, inventario contra los arneses que existen y vigilancia de raíces históricas. |
| Conftest | Sale únicamente la redirección de consumo del módulo retirado. Sigue comprobando después de cada test que `.git/qs-*` no cambió. |
| CI | Sale el paso del arnés del libro y el del gate. Quedan seis: suite, arnés de referencias, guardia documental, completitud, registro de sonda y recuento del método. |

La maquinaria sigue observando las rutas históricas `data_hist/eco_b`; conservar esa
vigilancia no mantiene una campaña operativa. No se borran directorios de datos ni `.git`.

Los cinco mapas de tests modificados se identifican por **índice en las 202 filas de la base**:

1. Filas 1, 2 y 3: salen los testigos exclusivos del productor o de la paridad de los
   dos productores retirados. Permanecen los testigos directos de clasificación/banda.
2. Fila 77: el censo real ya no contiene un sitio bajo `tools`, así que no puede ser
   testigo de ese fallo. Se conserva el test sintético que coloca ahí una carga.
3. Fila 182: sale el testigo del pre-vuelo real de tres arneses. Permanece el test
   sintético que exige semántica de subcadena. La comprobación del arnés real sigue
   en la suite con su nombre actualizado.

No se cambia una ancla o un sustituto de las 49 mutaciones conservadas. La corrida
completa pendiente debe acreditar las 49; el pre-vuelo por sí solo no lo hace.

## 3. Pruebas que sobreviven a sus antiguos ficheros

- Nueve funciones puras de referencia pasan literalmente de
  `test_pilot_observer_ref_invalida.py` a `test_ref_valida.py`.
- Siete funciones de `carril` pasan literalmente de `test_eco_procedencia.py` al fichero
  conservado de compuertas, incluidas rutas relativas, mayúsculas y controles positivos.
- Las pruebas de interpretación, baseline y causas del antiguo arnés pasan a
  `test_arnes_comun.py`. La prueba de excepción verifica el cierre real del ejecutor de
  referencias antes de propagar, en vez de buscar un mensaje del CLI retirado.
- Los focales de timeout conservan el caso del ejecutor de referencias y las pruebas
  de la primitiva común. Sale la parametrización del gate. El caso `conservar=True`
  prueba directamente que la primitiva aborta y deja los temporales intactos; ese
  argumento permanece en la función aunque salga el CLI del gate.
- Las propiedades de productores y recibos retirados salen con ellos. Permanecen
  clasificación total, contaminación exacta y referencia aceptada → fórmula de
  markout acotada. Esta última consulta la fórmula del módulo genérico conservado.

El delta de colección está en `comprobacion_estructura.json`: **1.699 → 476 nodos**,
74 nodos trasladados o renombrados, 1.223 retirados y ningún alta sin explicar.
La base de comparación es el log del lote 2; su código de tests coincide con el de
`e1c2757`, cuyo lote 4 solo modificó documentos. No se repite esa colección histórica.

## 4. Evidencia científica y recuperación

La base completa del lote es `e1c2757b1f492637aba62ef46ffe45be91405c67`.
[ARCHIVO](../ARCHIVO.md) contiene ruta, propósito, último commit y motivo; el inventario
añade blob y SHA-256 local y Git. Se retiran cuerpos originales, sin modificarlos antes.

De las seis fuentes compartidas que D1 aún tenía activas, salen `screen.py`,
`pilot_observer.py` y `lighter_maker_capa1.py`; permanecen `artefacto.py`, `carril.py`
y `ref_valida.py` con sus hashes. Las diez fuentes I5 salieron en el lote 2. El
[índice del expediente](INDICE_EXPEDIENTE_I5.md) actualiza esta disposición sin cambiar
la restauración científica: árbol completo `1ca5ca6`, historia de julio y custodias externas.

El LEDGER histórico conserva el sello `8b1bb45925467b831326183ec9336003ee605afd94f728f537f044c87a6f6c41`.
La especificación D1 y los documentos científicos conservan sus hashes. Las decisiones
vigentes se anotan en [LEDGER_ACTUAL](LEDGER_ACTUAL.md), no en el histórico.
STOP, freezes, pins y D3 continúan: retirar la campaña no habilita datos protegidos,
operativa o un nuevo objeto. No se ejecutó una lectura científica ni se accedió a claves o red.

## 5. Verificación de Codex y límites

Artefactos: `<USER_HOME>/Desktop/Laboratorio/V2_LOTE3_20260909_01/`.
Temporales: subcarpeta propia bajo `AppData/Local/Temp`, comprobada fuera de Git y OneDrive.

| Comprobación | Resultado |
|---|---|
| Pre-vuelo de la base | 23 / 187 / 202, rc 0; árbol limpio antes de editar |
| Pre-vuelo del diff | Referencias 49, rc 0 |
| Colección completa | 476 tests, rc 0 |
| Focales de piezas modificadas y conservadas | Primer pase: 263 passed, dos fixtures aún ligados al CLI retirado fallaron. Tras corregir únicamente esos dos casos: 2 passed. No se presenta como una corrida única de 265. |
| Cuatro controles rápidos | rc 0 todos |
| Traslado de maquinaria | Dieciséis cuerpos idénticos por AST; diferencia de firma declarada |
| Ejecutor de referencias | Funciones idénticas por AST |
| `analysis/` y `tools/` activos | 21 + 12 módulos; 3.221 + 2.712 = 5.933 líneas físicas, incluidos comentarios |
| Ingesta | Seis módulos, 1.016 líneas, sin cambios |
| Conservación documental y del árbol | 240 textos rastreados ajenos al diff intactos, incluidos 142 documentos históricos; ocho untracked previos intactos; índice vacío y `main` sin cambios |
| Enlaces y whitespace | 46 destinos locales existentes; `git diff --check` conforme |

El criterio de volumen se cumple para `analysis/` y `tools/`. El tiempo de la suite
completa y la mordida de las 49 filas todavía no se han medido en este diff. Los focales
y la colección no los sustituyen. No se ha lanzado un arnés completo ni una suite larga local.

## 6. Orden acotada a Code

1. Verificar las huellas de entrega, scope, imports, comandos, configuración y servicios;
   cotejar los 81 cuerpos retirados con Git, los traslados de funciones/pruebas y cada
   fila que sale o cambia testigo. Usar `git diff --no-renames` para comparar las rutas:
   la detección visual de renombres no debe ocultar un origen o destino del inventario.
2. Pre-vuelo **primero**, sobre el diff deliberado con `--permitir-sucio`. No abrir datos
   o repetir I5. Si la auditoría es conforme, ejecutar **una vez las 49 filas completas**
   del arnés de referencias, con árbol quieto, huellas antes/después y temporales fuera
   de repositorios. No ejecutar los arneses retirados para justificar su retirada.

Desde `Desktop/quant-system/quant-system-ingesta/qs`, con `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONUTF8=1` y TEMP/TMP/TMPDIR en la carpeta comprobada:

```powershell
& .\.venv\Scripts\python.exe -B tools/prevuelo.py --arnes todos --permitir-sucio
& .\.venv\Scripts\python.exe -B tools/mutacion_ref_valida.py
```

3. Si cierra **49/49**, rc 0 y sin deriva, quedan autorizados el commit de las **100 rutas
   exactas** y el push fast-forward de `codex/wip-m12.20`. Verificar antes el remoto real
   en `e1c2757`; ante divergencia, conciliar sin force. El índice debe empezar vacío y
   coincidir con el inventario usando `--no-renames`. No integrar en `main`.
4. Verificar la lista NUL contra `commit_paths` y su hash antes del staging. No usar
   `git add -A`. Desde la raíz del repositorio:

```powershell
git add --pathspec-from-file=<USER_HOME>/Desktop/Laboratorio/V2_LOTE3_20260909_01/commit-paths.nul --pathspec-file-nul
```

Mensaje propuesto: `V2 lote 3: retirar la campaña conservando el núcleo y sus controles`.

Los ocho untracked previos enumerados en el inventario quedan fuera, incluida la
auditoría del lote 4. La auditoría nueva de Code puede quedar fuera del commit acotado.
Observar **una CI de este commit** y devolver sus seis verificaciones, duración de la
suite y recuentos, sin reintentos automáticos. Una CI roja se conserva y atribuye antes
de corregir. Con cierre verde termina la simplificación aprobada; no se abre otro frente.

## 7. Huellas de entrega

SHA-256 de bytes locales, sin normalizar saltos de línea. `verificacion.json` registra
las huellas de las 18 piezas existentes o nuevas distintas de este relevo y del código
final; `entrega.json` registra además la huella final del relevo, evitando una referencia
circular. Ambos están en la carpeta externa del lote, junto a la lista NUL.

| Pieza | SHA-256 |
|---|---|
| `docs/inventarios/V2_LOTE3_20260909.json` | 7390fe6b5532a6fe3d616623f1464cad1b20ff7ccaa312167629d72f675001f8 |
| `verificacion.json` | 7b02d1cbdb283c154d572431c743a1b90409439a572b3b569b37046e70df15b7 |
| `commit-paths.nul` | 69f013f1e45ab830f2192d4db97f428447a8bb7fe4124b018ddb48fad49ed78e |
| `.github/workflows/ci.yml` | 2e0d48d3b2fb25d815ff80a8b3c90da0f4575fecac2067f3c03106c2308ec6a6 |
| `tools/arnes_comun.py`, bajo `qs/` | 09d6e6c37c248e8bb89f832727f4001f82b7786bd4f8580b84c526c5495a2a4b |
| `tools/mutacion_ref_valida.py`, bajo `qs/` | 5c19dd69e70511ca978bb58c96b41e4887ae06e5e5a113fb185bd785ae88342b |
| `tools/prevuelo.py`, bajo `qs/` | d7f4252cc57e1e04d259eaae2cc33a22be343a2edbe7c17d6e97f32a23660f78 |
| `tools/guardia_completitud.py`, bajo `qs/` | c57d923ae929181750c63d1f509d6ffab3b7f1ef713e0496a2f0d491c746dd86 |
