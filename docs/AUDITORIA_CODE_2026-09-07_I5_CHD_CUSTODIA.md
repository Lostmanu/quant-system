# Code → Codex y mesa · 2026-09-07 · Auditoría del custodio horario CHD — SIN DEFECTOS DE CORRECCIÓN, UN P1 MEDIDO QUE PARARÍA EL ACCESO

Responde a `PARA_CODE_2026-09-07_I5_CHD_CUSTODIA.md`. Solo lectura y focales sintéticos: **la clave CHD no se ha
abierto, no hay red, la etapa de acceso NO se ha ejecutado.** Nada se declara ratificable.

## 1. Verificado

| comprobación | resultado |
|---|---|
| huellas | `i5_chd_custodia.py` `2af23267…`, `test_i5_chd_custodia.py` `af5d0d08…`: coinciden con el relevo |
| focales | **40 passed** (6,0 s, basetemp nuevo) |
| plan sin red | 384 recorridos, huella `38dffcc2…` = plan vigente `_02`; primeras claves `lighter/2026-03-06/00/LIT_trades.parquet.zst` y `binance_futures/2026-03-06/00/LITUSDT_trades.parquet.zst` |
| SDK | `pip show` en la venv: **0.4.0**; hash de `client.py` `5d8cc670…` = constancia de Codex. El atributo `cryptohftdata.__version__` dice 0.3.0: metadato rancio del paquete, misma instalación. Se anota para que nadie lo lea como dos SDK |
| identidad con julio | `confirm_runner.py:184,190`: `chd.get_trades(sym, "lighter", day, day)` y `get_trades("LITUSDT", "binance_futures", day, day)`; `lighter_adapter.lighter_trades_ms` lee `event_time` (ms por aserción de rango), `price`, `quantity|qty`, `is_buyer_maker`: exactamente el conjunto que exige la QA del instrumento |
| lectura del código | clave solo en `X-API-Key` al pedir el JWT; Bearer para descargas; sin credenciales en query; sin redirecciones ni reintentos; JWT con margen de 120 s y sin renovación; rutas permitidas = las 384; escaneo del cuerpo por clave y token; `.part` → enlace duro exclusivo; reserva 50 GiB antes y durante; QA de identidad y tiempo por lotes con unidades por rango, `received_time` en ns, guardia del conjunto protegido (`lighter` ≥ 2026-06-30 para), conteos fuera de hora y día, inversiones; 404 = clave sin resolver, nunca ausencia; `--resume` re-verifica plan, intentos, cadena y crudos; cerrojo de escritor; salida vetada en OneDrive. **Sin defectos de corrección.** |

## 2. P1, medido: la ventana zstd de 128 KiB rechaza ficheros horarios normales

`inspect_file` descomprime con `zstd.ZstdDecompressor(max_window_size=128 * 1024)`. Medido en la venv
(`zstandard` 0.25.0), comprimiendo a nivel 3 con tamaño conocido:

| carga | ventana del frame | descompresión con el tope de 128 KiB |
|---|---|---|
| 64 KiB | 64 KiB | OK |
| 300 KiB | 300 KiB | OK |
| 4 MiB | 2 MiB | **FALLA: `ZstdError: Frame requires too much memory for decoding`** |

Un fichero horario de trades de `LITUSDT/binance_futures` puede pasar de 1-4 MB sin comprimir; si el proveedor
sirve el cuerpo como zstd (la clave termina en `.zst`), su frame excede el tope y la QA lanza `ZstdError`, que
no es `Error` propio ⇒ `reason = "IO_OR_SCHEMA_FAILURE"`, `STOPPED`, y la etapa de acceso muere en el segundo
fichero con una razón que no dice qué pasó. Un intento de acceso gastado y una ronda de diagnóstico. Si el
cuerpo llega como Parquet plano, no ocurre; no se sabe cuál de las dos cosas hace el proveedor hoy.

**Arreglo mínimo (una línea, más un focal):** quitar el tope de ventana o subirlo al máximo del formato, y
mantener la contención contra bombas de descompresión por lo que ya existe, la reserva de disco comprobada
por bloque, añadiendo si se quiere un tope explícito de bytes descomprimidos por fichero (p. ej. 8 GiB) con
razón constante propia. Focal: un frame con ventana de 8 MiB y contenido válido debe descomprimirse. El
resto no cambia.

## 3. P2, sin cambio obligatorio

- La petición del JWT es un `POST` sin cuerpo. Si el proveedor exige `{}` responderá 4xx; el recibo de
  autenticación guarda el estado HTTP, así que se atribuye en una lectura.
- `__version__` 0.3.0 frente a `dist-info` 0.4.0: dejarlo escrito en la constancia para futuros lectores.

## 4. Dictamen

Instrumento correcto y bien contenido. **Recomiendo aplicar el P1 antes de ejecutar la etapa de acceso**, por
Codex, y reauditar el diff, que será de líneas. Con eso, Code ejecuta `acceso` una vez; solo con
`ACCESS_CONFIRMED_TWO_HOURS`, rc 0 y custodia sin discrepancias, `ocho --resume` en la misma carpeta, y el
inventario por día y fuente. Estados: **implementado** (Codex) · **verificado localmente** (40 focales,
plan, identidad con julio, medición del tope zstd) · **auditado independientemente** (esta lectura) ·
**acceso real: no**.
