# Code → Codex y mesa · 2026-09-07 · Custodia de los 71 días, intento 0: PARADA por tiempo de socket en el salto tras 1.489 de 3.408 claves; recibo devuelto, continuación lista para orden de la mesa

Responde a `PARA_CODE_2026-09-07_I5_CHD_RESTO_71.md`. Auditoría del incremento y **una ejecución** en
`Desktop\Laboratorio\I5_CHD_RESTO_71_20260907_01`. Conforme al relevo, ante `STOPPED` se devuelve el recibo:
**no se ha relanzado, no se ha reanudado, no se ha abierto otra carpeta.** Nada se declara ratificable.

## 1. Auditoría del incremento

| comprobación | resultado |
|---|---|
| huellas | `i5_resto_chd.py` `dba1a31a…`, `test_i5_resto_chd.py` `da743e17…`, `ESPEC_MESA_2026-09-07_D1_79_DIAS.md` `6e358b9c…`, plan `_01` `d1f38459…`, verificación `826a7fd8…`: todas = relevo. Instrumentos anteriores intactos: custodio `d39234b2…`, productor `e4011fc6…`, lector `e7b582f6…` |
| focales | **23 passed** (1,5 s, basetemp nuevo); objetos git 667 antes y después |
| plan sin red | emitido con el comando exacto del relevo: **844.879 bytes, `d1f38459…`, byte a byte igual** al `_01`; 3.408 claves, 71 días, `first_attempt_max` = {JWT 1, descargas 3.408, API 3.409, saltos 3.408, HTTP 6.817} |
| ámbito | 79 celdas LIT del manifiesto `0d913aae…` menos las 8 reproducidas = 71 días (07-03 → 28-06); 24 h × 2 fuentes; sin intersección con las 384 claves; todo < 30-06 |
| transporte | los bytes del custodio auditado se cargan en un módulo privado tras verificar su hash; solo se sustituyen `jobs` y `path_for`; `Client`, JWT, salto único, aislamiento de credenciales, escaneo de secretos, `.part`→enlace duro, QA y `verify_existing` son el mismo código (los focales comparan el bytecode de `open`, `_send`, `_redirect_target`, `authenticate`, `download`); el módulo importado de los ocho no cambia (384 rutas permitidas) |
| pre-vuelo del plan | anclas de CHD `_02` (plan, dos intentos, cadena de 384), cierre de la reproducción (`result.json` `3d7302b0…`, ocho recibos y manifiestos), 79 recibos L3 de A (`fe553bfd…` / `2edf0573…`): todo por hash, sin abrir cuerpos |
| ejecución | comprobación de plan por hash antes de cargar transporte, crear carpeta o abrir la clave; salida fuera de repo, OneDrive y custodias; un JWT por intento; expiración para; `--resume-from` exige el hash del último intento `STOPPED` y re-verifica plan, cadena, crudos y ausencia de parciales antes de abrir la clave; una corrida completada no se reabre |

**Sin defectos de corrección.** Nota P3, sin cambio ahora: el recibo del intento guarda `reason` pero no el
tipo de excepción (el productor sí lo hace); la atribución de una parada se apoya en los tiempos del recibo.
Cambiarlo alteraría el hash del instrumento y, con él, el plan: no procede antes de completar esta custodia.

## 2. Ejecución: intento 0, `STOPPED`

| campo | valor |
|---|---|
| comando | el del relevo, `--execute … --expected-plan-sha256 d1f38459…` |
| UTC | 10:17:52 → 11:20:29 (62,6 min) |
| JWT | emitido 10:17:53, `expires_in` 14.400 s (vigente hasta 14:17:53) |
| estado / razón / rc | **`STOPPED` · `IO_OR_SCHEMA_FAILURE` · 2** |
| `active_index` | 1489 = `binance_futures/2026-04-21/00/LITUSDT_trades.parquet.zst` |
| recorridas | **1.489 de 3.408** (índices 0–1488): 1.470 custodiadas + 19 × HTTP 404 |
| restantes | **1.919** (índices 1489–3407) |
| HTTP | 1.491 llamadas API (1 JWT + 1.490 GET) · 1.471 saltos · **2.962 de 6.817** |
| cuerpo | 105.527.660 bytes (105,5 MB); 8.214.586 filas |
| recibo del intento | `attempts/0000.json` **`6aef7ca1ab7443b0824e408c7de482ee56355440244e503bfa3b56b4651d0a65`** |

### 2.1 Atribución de la parada

El recibo conserva la última petición: `GET` inicial a las 11:18:28,302, **302 recibido a las 11:18:28,967**,
salto a `https://…r2.cloudflarestorage.com` iniciado a las **11:18:29,403** con `credentials_sent = none`,
`status` final **`null`** (el salto nunca devolvió cabeceras) y cierre del intento a las **11:20:29,507**:
**120,1 s** después de iniciar el salto, que es exactamente el `TIMEOUT` de socket de 120 s del transporte.
Lectura: **tiempo de espera agotado en el almacén de objetos del proveedor**, un fallo transitorio de red, no
de credenciales (el JWT tenía tres horas de vida), no de esquema (los 1.470 cuerpos anteriores pasaron la QA)
y no de disco (499 GB libres). La excepción de socket no es `Error` del instrumento, por eso la razón genérica.
Es la atribución que permiten los tiempos del recibo; el tipo de excepción no queda registrado (P3).

Estado del árbol tras la parada: 1.489 recibos, 1.470 crudos, **0 `.part`, 0 huérfanos**; cadena de recibos
íntegra (0 roturas); sha256 de los 1.470 crudos = `body_sha256` de su recibo (1.470 de 1.470).

## 3. Inventario de lo custodiado hasta la parada

| fuente | días tocados | días 24/24 | horas | 404 | filas | cuerpo MB | filas fuera de hora/día | borde | inversiones | horas 0 filas |
|---|---|---|---|---|---|---|---|---|---|---|
| LIT / lighter | 32 | 29 | 726 | **19** | 837.118 | 15,8 | 23 | 0 | 0 | 0 |
| LITUSDT / binance_futures | 31 | 31 | 744 | 0 | 7.377.468 | 89,7 | 315 | 0 | 0 | 0 |

Redirección: las 1.470 descargas saltaron al mismo host R2, todas sin credenciales; los 19 × 404 los devolvió
la API sin salto. Esquema idéntico en los 1.470 ficheros; `event_time` ms y `received_time` ns en todos.

**Días incompletos en Lighter, todos por 404 de la API (clave exacta sin resolver, no ausencia de mercado):**

| día | horas 404 | horas custodiadas | Binance el mismo día | hueco L3 declarado por 0xArchive |
|---|---|---|---|---|
| 2026-03-23 | **05–18 (14 horas seguidas)** | 10/24 | 24/24 | ninguno |
| 2026-04-14 | 18–22 (5 horas) | 19/24 | 24/24 | ninguno |
| 2026-04-21 | — | 1/24 (h00; ahí paró el intento) | 0/24 | — |

Con Binance completo esos días y sin hueco L3, son huecos de la captura de Lighter en CryptoHFTData. El de
03-23 quita la mayor parte de la sesión; se conserva como está, con trazabilidad, según §6 de la especificación.

**Combinado de 79 días hasta ahora** (`combined_79` del recibo, 384 anteriores + 1.489 nuevas): 1.873 claves
recorridas, 1.851 custodiadas, **22 × 404** (3 del 29-06 + 19 nuevas), 1 fichero de borde, 140,5 MB. Faltan
1.919 claves nuevas por recorrer. Resumen de Code, fuera de la carpeta custodiada:
`Desktop\Laboratorio\I5_CHD_RESTO_71_20260907_01_RESUMEN_CODE.json`.

## 4. Continuación, lista para la orden de la mesa

Ritmo medido del intento: 2,52 s por clave ⇒ las 1.919 restantes son **~81 min**, con JWT nuevo (uno por
intento). El comando, desde `qs`, con el hash del intento parado; el instrumento re-verifica plan, cadena,
1.470 crudos y ausencia de parciales antes de abrir la clave, y no repite ninguna clave recorrida, 404 incluidos:

```powershell
& '.\.venv\Scripts\python.exe' -B tools/i5_resto_chd.py --execute --parent-chd-root '<USER_HOME>\Desktop\Laboratorio\I5_CHD_OCHO_20260907_02' --reproduction-root '<USER_HOME>\Desktop\Laboratorio\I5_REPRODUCCION_OCHO_20260907_01' --checkpoint-root '<USER_HOME>\Desktop\Laboratorio\I5_L3_CHECKPOINT_20260906_01' --out '<USER_HOME>\Desktop\Laboratorio\I5_CHD_RESTO_71_20260907_01' --key-file '<USER_HOME>\Desktop\<KEY_DIR>\<KEY_FILE>' --expected-plan-sha256 d1f38459859763d362fc54f88ffe8078a4b88a3eb71ef9d6f0858b1fcc0c51de --resume-from 6aef7ca1ab7443b0824e408c7de482ee56355440244e503bfa3b56b4651d0a65
```

Code no lo lanza sin la orden. Si la mesa la da, Code ejecuta una vez y devuelve el inventario completo de las
3.408 claves y el combinado de 79 días antes de cualquier producción.

## 5. Especificación D1: lectura de Code, sin objeciones de fondo

Revisada `ESPEC_MESA_2026-09-07_D1_79_DIAS.md`. Las ramas cambian una sola pieza cada una respecto a su
comparador; los contrastes van pareados por día en la intersección; no hay umbral nuevo ni selección de rama.
Dos anotaciones, no objeciones:

1. **T y TV necesitan los trades de Lighter otra vez** (el `vol20` al reloj `t_at` no está en los NPZ): el plan
   de análisis tendrá que ligar por hash la custodia CHD además de los NPZ, como la especificación ya prevé al
   fijar «funciones compartidas y sus hashes» antes de ejecutar.
2. **Los huecos del proveedor ya no son solo tres horas:** 03-23 pierde 14 horas y 04-14 cinco. La
   especificación cubre el caso (cobertura informada, sin admitir ni sustituir días por resultado; «horas
   disponibles» en las tablas de soporte). Conviene que el productor de los 71 los contraste contra sus
   originales igual que el 29-06, con la misma cautela: la igualdad no identifica las horas que usó julio.

## 6. Estados

**implementado** (Codex) · **verificado localmente** (23 focales; plan byte a byte) · **auditado
independientemente** (esta lectura) · **ejecutado una vez, `STOPPED` a 1.489/3.408 con recibo** · **continuación:
pendiente de orden** · **CI: no** · **producción de los 71 y D1: no**. STOP, freezes, pins y conjunto protegido
vigentes. HEAD `7df5280`, sin commit.
