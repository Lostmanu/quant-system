# Relevo a Code: lote 4 documental

2026-09-09. Base `0f127e396e5c81bef6757bc33f1fdeae46184e1d`, rama `codex/wip-m12.20`. Lote 2 cerrado: run `34286664630`, ocho verificaciones verdes según el informe y la auditoría de Code. No se ha vuelto a consultar GitHub ni a ejecutar esa CI.

## 1. Objeto y alcance exacto

Aplicar el lote documental del [mandato V2, §5](DICTAMEN_MESA_2026-09-07_PUSH_CI_Y_V2.md): conservar el ledger histórico, dar una entrada corta al expediente y separar el estado actual. **No hay un nuevo objeto científico aprobado.** El lote 3 espera al cierre de este lote.

Siete rutas de commit, enumeradas en el [inventario](inventarios/V2_LOTE4_20260909.json):

| Ruta | Cambio |
|---|---|
| `README.md` | Entrada nueva y recorrido de cuatro documentos contando esta entrada |
| `docs/LEDGER_ACTUAL.md` | V2 como trabajo activo, I5 cerrado y ningún objeto científico nuevo |
| `docs/INDICE_EXPEDIENTE_I5.md` | Navegación por la evidencia, sus límites y recuperación |
| `docs/CONGELACION_LEDGER_2026-09-09.json` | Identidad documental del LEDGER histórico por Git y SHA-256 |
| `ARCHIVO.md` | Único fichero existente editado: cierre del lote 2 y enlaces actuales |
| `docs/inventarios/V2_LOTE4_20260909.json` | Alcance, fuentes de apoyo y exclusiones |
| Este relevo | Verificación y orden de auditoría y publicación |

El LEDGER permanece en `docs/LEDGER.md`, 2.321 líneas y 196.308 bytes, SHA-256 `8b1bb45925467b831326183ec9336003ee605afd94f728f537f044c87a6f6c41`. Su último cambio es `1ca5ca6`; sus bytes locales y el blob de la base coinciden. El sello es constancia documental: no añade bloqueo automático a CI, permisos del sistema ni un freeze científico.

No se mueven o corrigen retrospectivamente `CONTINUAR_AQUI.md`, `ESTADO.md`, el LEDGER, la especificación, los dictámenes o los resultados. El README explica su contexto histórico. Las fuentes científicas, pruebas, configuración, workflows, datos, servicios y copias quedan fuera del diff. El catálogo y las propuestas posteriores al laboratorio no se convierten en encargos.

## 2. Precisiones del cierre que recoge la entrada nueva

Las 53 rutas de los dos primeros lotes son rutas retiradas. Los dos commits suman +2.691/−11.030 líneas contando toda la documentación: la reducción neta es 8.339, no 11.030. Se registra esta precisión sin editar la auditoría de Code.

La restauración científica I5 se ancla en el árbol completo `1ca5ca6`, la historia de julio y sus custodias. Las mismas fuentes también permanecen en la historia y bases posteriores; `f0fd1aa` permite recuperar además los fixtures portables. No se afirma que existan exclusivamente en un commit.

El índice mantiene 5 s como primaria y 25 s como compañero fijado. La ampliación añade through-con-at, no todos los through. Reproducción numérica exacta no significa identidad de insumos. Las cifras del índice proceden del dictamen ya emitido; no se abrió un cuerpo de datos para escribirlas.

## 3. Verificación acotada

Artefactos en `<USER_HOME>/Desktop/Laboratorio/V2_LOTE4_20260909_01/`: `baseline.json`, `verificacion.json`, logs y `commit-paths.nul`. La baseline se fijó antes de escribir y contiene los hashes de 304 ficheros de texto rastreados y de los siete untracked previos. Excluye cuerpos de datos y recibos bajo `docs/runs/`; el cotejo no es un inventario nuevo de la custodia científica.

El recibo registra las comprobaciones de identidad del LEDGER y las fuentes conservadas, alcance de Git, enlaces locales, métricas de los dos commits y whitespace. Se ejecutaron el pre-vuelo de las tres tablas y los cuatro controles rápidos del workflow. No se repitieron la colección, la suite ni el arnés completo en local por este diff exclusivamente documental. **La CI propia del lote conserva la suite y los tres arneses completos.**

| Comprobación de Codex | Resultado |
|---|---|
| Hashes antes y después de los controles | 303 textos rastreados ajenos al diff intactos, incluidos los 148 `.py` de la baseline; siete untracked previos intactos |
| LEDGER | Bytes locales iguales al blob de la base; SHA-256, tamaño, líneas y último commit coinciden con el sello |
| Alcance e índice Git | Una ruta existente editada y seis nuevas; índice vacío |
| Enlaces locales | 40 destinos de fichero existentes; no se validan anclas internas de Markdown |
| Métricas de lotes 1 y 2 | Coinciden con `git show --numstat` de ambos commits |
| Pre-vuelo | rc 0; gate 23, libro 187, referencia 202 |
| Cuatro controles rápidos | rc 0 todos; guardia de completitud sin rutas abiertas |
| Whitespace y patrones de credencial | Sin incidencias; se buscaron cabeceras de clave privada y patrones JWT en las siete rutas, sin abrir ni comparar claves reales |

El registro de sonda permanece vacío y el guardia documental conserva los símbolos pendientes no exigidos: un rc 0 de esos controles no afirma que estén implementados. El directorio temporal comprobado fuera de Git fue `<USER_HOME>/AppData/Local/Temp/`; la subcarpeta exacta consta en el recibo.

Para el pre-vuelo y controles, desde `Desktop/quant-system/quant-system-ingesta/qs`, con `PYTHONDONTWRITEBYTECODE=1` y `PYTHONUTF8=1`, temporales fuera de repositorios y de OneDrive:

```powershell
& .\.venv\Scripts\python.exe -B tools/prevuelo.py --arnes todos --permitir-sucio
& .\.venv\Scripts\python.exe -B tools/guardia_documental.py
& .\.venv\Scripts\python.exe -B tools/guardia_completitud.py
& .\.venv\Scripts\python.exe -B tools/registro_sonda.py
& .\.venv\Scripts\python.exe -B tools/recuento_auditoria.py --check
```

`--permitir-sucio` admite el diff documental deliberado para el pre-vuelo. No cambia el juicio de sus anclas ni el ámbito del lote.

## 4. Orden acotada a Code

Auditar la redacción contra el mandato y el dictamen D1; verificar el sello frente al blob Git y fichero actual, las huellas de fuentes conservadas, los enlaces y las siete rutas. Comparar la lista NUL con `commit_paths`. No repetir ciencia, descargas, pruebas de I5 o inspección de NPZ. La auditoría puede verificar los recibos rápidos existentes; si se modifican fuentes fuera del inventario, este relevo ya no cubre ese diff.

Con la auditoría conforme, quedan autorizados el commit de estas **siete rutas exactas** y un push fast-forward en `codex/wip-m12.20`. Comprobar HEAD y el remoto real en `0f127e3` antes de publicar; si difieren, conciliar primero sin force. El índice debe estar vacío al comienzo y coincidir exactamente con el inventario tras el staging. No usar `git add -A` ni integrar en `main`.

Tras verificar la huella y el contenido de la lista, desde la raíz del repositorio:

```powershell
git add --pathspec-from-file=<USER_HOME>/Desktop/Laboratorio/V2_LOTE4_20260909_01/commit-paths.nul --pathspec-file-nul
```

Mensaje propuesto: `V2 lote 4: conservar ledger histórico y ordenar la entrada documental`.

Los siete untracked previos enumerados en el inventario quedan fuera del commit y sin editar. La auditoría de Code de este lote puede quedar fuera del commit acotado, como en los anteriores. Registrar su veredicto y, tras publicar, el resultado de las ocho verificaciones de **una CI de este commit**, sin reintentos automáticos. El estado de las páginas refleja esta entrega preparada; la constancia posterior de auditoría y CI cerrará el lote por fecha y commit.

Cuando cierre verde, el siguiente tramo será el lote 3 con el inventario conjunto de dependencias. No queda implementado ni auditado por este relevo.

## 5. Huellas de entrega

Hashes de bytes locales, sin normalización de saltos de línea. El recibo contiene las seis huellas de piezas distintas de este relevo; `entrega.json` registra también la huella final de este relevo evitando una referencia circular.

| Pieza | SHA-256 |
|---|---|
| `ARCHIVO.md` | feb276010cf9d518c8cb64755494679857e9bcc49914a1d44de4478e418b4007 |
| `README.md` | 19ed108b04cb5fb7989b4d0c55ef9cdab4d461f7f85a6372c3deae66dab904c8 |
| `docs/CONGELACION_LEDGER_2026-09-09.json` | 2f4ba1c789446ca70317f5dcf3867d9899594af468b26694e54d8c2356de1f39 |
| `docs/INDICE_EXPEDIENTE_I5.md` | 774ac282f8c64d1ef86a43785cdba32283a2e77096b3a71e037605d1d1f6c977 |
| `docs/LEDGER_ACTUAL.md` | 993dbf6b072cdf05ccf580b0b36fc67626f177673c792095163c47fc0963ed1b |
| `docs/inventarios/V2_LOTE4_20260909.json` | ec8423e37e21c16101cc9bf2516c230283cec097e5295b1e814f2e61a7d6c9b9 |
| `verificacion.json`, carpeta externa del lote | 5ea247adae264ade1fd9cafa7dec0913d6aba4fb0e1b451c3b76c01b9d424a06 |
| `commit-paths.nul`, misma carpeta | 15d62006a62f30df29f9452eea40416dde062e9f88ac167862428bcef6854b49 |
