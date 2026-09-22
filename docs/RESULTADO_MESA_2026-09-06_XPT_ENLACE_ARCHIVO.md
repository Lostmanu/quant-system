# Mesa · lectura única del archivo propio XPT — 2026-09-06

**Resultado: INDETERMINADO_MASA. Corrida terminada, sin reintentos ni ampliaciones.**
Los archivos se procesaron completos, pero no hubo frames de trades admitidos por el filtro
`trade:147` dentro de la ventana autorizada. No se pudo contrastar ejecución–orden.
Esto **no prueba ausencia de negociación de XPT** ni identidad/incompatibilidad entre espacios de IDs.

## 1. Autoridad y ejecución

Manuel autorizó XPT, 2026-09-01 **[12:00,12:10) UTC**, con un máximo conjunto de 60 s y 256 MiB
comprimidos, solo archivo propio, sin endpoints de mercado ni cambios de servicios.
Se leyó completa `AUDITORIA_CODE_2026-09-05_XPT_INSTRUMENTO.md`, cuyo dictamen permite una ejecución
del comando del relevo sin cambios. SHA-256 de la auditoría recibida:
`f3cce822aa351b24696dbe653492d7af33cbf08bed4f39967733025ca35ba9b7`.
Se conserva el documento de Claude sin editar.

Antes de lanzar: coincidencia de los tres hashes del relevo y directorio de medición inexistente.
Se ejecutó **exactamente una vez** el comando de `PARA_CODE_2026-09-05_XPT_ENLACE_ARCHIVO.md`.
No se repitieron focales, suites, preflight de metadatos ni consultas de servicios.

| Campo | Evidencia observada |
| --- | --- |
| Inicio UTC | 2026-09-06 08:20:09.441474 |
| Fin UTC | 2026-09-06 08:20:27.111705 |
| Duración registrada | **17,672 s** |
| Estado del recibo | **INDETERMINADO_MASA** |
| SSH remoto | rc 0; stderr vacío por hash |
| Procesamiento de archivos | ambos decodificados hasta EOF; `sample_complete=true` |
| Consultas de mercado / créditos de proveedor | **0 / 0** |
| Datos persistidos por el instrumento | **solo `receipt.json` agregado** |

`sample_complete` describe el procesamiento de los archivos seleccionados. **No certifica que
contengan toda la actividad del mercado o de la ventana**, ni continuidad de la captura.
La herramienta de ejecución PowerShell devolvió **exit 1**. El programa contiene `return 4` para
este estado, pero no se atribuye ese 4 como código directamente observado ni se repite para obtenerlo.
No quedó una sesión del lanzador en ejecución.

## 2. Fuentes efectivamente usadas

Los metadatos `size/mtime_ns/ctime_ns/device/inode` coincidieron con el preflight y permanecieron
iguales antes y después de cada lectura. SHA-256 calculados localmente sobre los bytes transferidos:

| Archivo remoto | Bytes | SHA-256 |
| --- | ---: | --- |
| `/opt/l3-poller/data/l3_20260901_12.ndjson.zst` | 2.018.462 | `40a844773f379ad1608b25ecac5a484c004d2d3e99c8619fe0c4b716675e50a8` |
| `/opt/lighter-collector/data/lighter_20260901_12.ndjson.zst` | 24.517.421 | `b1ed2930fb3d8b52b2e2396aa78ae3b55be80d273aca545cd0259c3b98321ab5` |

Total 26.535.883 bytes (25,31 MiB). Sin copia de cuerpos o proyecciones de filas a disco local.
El instrumento pidió aperturas de solo lectura, sin atime, y ninguna mutación remota; no reinició
servicios ni tocó `ingest.service`. No se afirma haber re-verificado su estado después de la corrida.

Recibo primario:
`<USER_HOME>/OneDrive/Documents/Laboratorio/XPT_ENLACE_20260905_MEDICION_01/receipt.json`.
SHA-256 **`41c922272c84224fdfdf968eb6bc18d2c50a9ffefea0ec527fd6d0bd8b0cb0e1`**.

## 3. Lo medido y su alcance

| Magnitud | Resultado |
| --- | ---: |
| Market ID asociado a XPT por los envelopes del poller en la ventana | 147 |
| Snapshots L3 | 109 |
| Observaciones de órdenes, incluidas reapariciones | 9.668 |
| `order_index` distintos | 1.125 |
| Comparaciones `order_id` textual frente a `order_index` | 9.668; sin discrepancias registradas |
| IDs con múltiples pares cuenta/lado observados | 0 |
| Snapshots/lado que alcanzan 250 órdenes | 0 |
| Casos `total_* > órdenes retornadas` | 0 |
| Frames de trades admitidos en la ventana por el filtro XPT | **0** |
| IDs únicos de trades ordinarios | **0** |

El contador de frames XPT no aparece en el JSON porque el programa solo lo crea al admitir
un frame; su ausencia en esta ejecución completa equivale a cero incrementos. No se interpreta
como «cero trades en el venue» ni como una tasa de matches de 0 %: **no hay denominador de trades**.

`integrity_issues={}`: no se registraron esas anomalías en los objetos seleccionados. No acredita
el esquema de trades, ya que no se admitió ninguno. Tampoco ausencia de iceberg o de órdenes no vistas.

Relojes y cobertura temporal L3 observada:

- `recv_ns`: enteros, rango compatible con nanosegundos en los 109 snapshots.
- Primer snapshot seleccionado: **12:00:59.330317607 UTC**; último: **12:09:56.026914054 UTC**.
  Borde inicial sin observación seleccionada: 59,330317607 s; borde final: 3,973085946 s.
- Intervalo mínimo entre snapshots seleccionados: 1,464830404 s; máximo: 5,739431591 s.
- `transaction_time`: **cero en las 9.668 observaciones de órdenes**. No aporta edad ni unidad
  temporal usable en esta muestra. No hay campos temporales WS seleccionados para comprobar.

## 4. Precisiones de mesa sobre la auditoría, sin cambiar lo ejecutado

1. **Se corrige la nota P2.** `clock_value` devuelve `(unidad, inferior, superior)`:
   `candidates=[(name,n*scale,(n+1)*scale),…]` (línea 61 del instrumento). Por tanto,
   `timestamp[1]` es la cota **inferior**, no la superior. Un timestamp en `END−1 ms` no se
   excluye por sumarle un tick; ese incremento no se usa en la pertenencia. La selección principal
   sigue siendo `[START,END)` por `recv_ns`. Se verificó esto antes del lanzamiento, sin editar
   código. Con cero trades seleccionados, no hay contraste temporal WS en este recibo.
2. **Nombre de hora no prueba cobertura íntegra.** Que la hora de escritura sea posterior o igual
   a la de recepción no demuestra por sí solo que toda recepción anterior a 12:10 haya sido escrita
   antes de 13:00, ni excluye pérdidas o interrupciones. Leer ambos archivos hasta EOF certifica
   su procesamiento; la frase de la tabla contractual sobre «todo lo recibido» era demasiado fuerte.
   El borde inicial L3 observado se declara sin atribuirle aquí una causa.

Las notas P1 de parada por JSON ajeno y error remoto genérico no se activaron. Tampoco el timeout.
No se adopta la mejora opcional del clasificador de stderr: no hace falta para interpretar este recibo.

## 5. Decisión y entrega

La prueba acotada ha terminado. **El enlace `ask_id/bid_id ↔ order_index` sigue sin acreditarse
empíricamente**; también queda sin medir su cobertura previa. Lo que sí añade la muestra es
concordancia del alias textual L3 y presencia observada de órdenes en ese archivo concreto.

No se elige otra hora, símbolo o fuente, no se vuelve a descargar y no se consulta un proveedor.
Los cuerpos no quedaron guardados para hacer más análisis local. Un nuevo contraste empírico
necesitaría un alcance previamente decidido; esta corrida no lo autoriza automáticamente.

Claude puede auditar el recibo y esta interpretación sin leer cuerpos. D4.2 permanece abierto;
no se atribuye a la falta de trades seleccionados una refutación de la hipótesis económica ni una
imposibilidad general del carril propio. STOP, freezes, pins, M-15, push y CI conservan su estado.
Sin cambios de código ni del índice; HEAD `7df52803b6db3777b23be85409ef998f879909a8`.
