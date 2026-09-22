#!/usr/bin/env python3
"""lighter-collector — archivo tick PROPIO de Lighter (CAP 2; permiso del propietario en `9c8f4b1`).

Diseño = docs/COLECTOR_LIGHTER.md, con las lecciones del catálogo COSIDAS:
 · CRUDO Y COMPLETO: cada frame WS se persiste TAL CUAL llega, envuelto solo en {"recv_ns": <reloj
   local ns>, "frame": <texto crudo>} — cero parsing en ingest; el yo-futuro pregunta lo que quiera.
   El mapeo market_id↔symbol del arranque también se persiste crudo (los datos que tiras hoy...).
 · RELOJES CON APELLIDO: recv_ns es NUESTRO reloj en ns; los timestamps del venue viajan dentro del
   frame tal cual, con sus unidades sin tocar.
 · VENUE-AGNÓSTICO: este fichero solo sabe conectar, suscribir y volcar. Otro venue = otro par
   (WS_URL, suscripciones), mismo esqueleto.
 · WATCHDOG de disco: >85% usado → CRITICAL y salida limpia (systemd Restart=always reintenta; si el
   disco sigue lleno, vuelve a salir — jamás borra datos en silencio).
Canales (WS oficial verificado 2026-07-05): order_book/{id} (L2 diffs @50ms + snapshot inicial en cada
(re)conexión = re-anclaje gratis en cada seam) y trade/{id} (¡con ask/bid_account_id → dimensión wallet
en tiempo real!). Keepalive: ping cada 60s (exigencia: ≥1 frame/2min)."""
import asyncio
import json
import os
import shutil
import sys
import time
import urllib.request

import zstandard as zstd
# `websockets` se importa dentro de run() (no en el import del módulo) para que el writer sea testeable
# en entornos sin esa dependencia (el core de tests no la necesita).

SYMBOLS = ["BTC", "LIT", "DOGE", "FARTCOIN", "WTI", "ARC", "XPT", "ZEC", "BRENTOIL"]
WS_URL = "wss://mainnet.zklighter.elliot.ai/stream?readonly=true"
REST_MARKETS = "https://mainnet.zklighter.elliot.ai/api/v1/orderBooks"
DATA = os.environ.get("COLLECTOR_DATA", "/opt/lighter-collector/data")
DISK_CRIT = 0.85
FLUSH_S = 5.0


def market_map() -> dict:
    req = urllib.request.Request(REST_MARKETS, headers={"User-Agent": "qs-collector"})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, f"market_map_{time.strftime('%Y%m%d_%H%M%S', time.gmtime())}.json"), "w") as f:
        json.dump(d, f)                                     # el mapeo, crudo, fechado
    return {ob["symbol"]: ob["market_id"] for ob in d.get("order_books", [])}


class HourlyZstWriter:
    """Frames zstd CONCATENADOS por hora (lighter_YYYYMMDD_HH.ndjson.zst) — append-only, decodificable
    en streaming. Watchdog de disco en cada flush."""

    def __init__(self):
        self.buf: list[bytes] = []
        self.comp = zstd.ZstdCompressor(level=6)
        self.n_lines = 0

    def add(self, line: bytes) -> None:
        self.buf.append(line)
        if len(self.buf) >= 5000:
            self.flush()

    def flush(self) -> None:
        if not self.buf:
            return
        # Escribir SIEMPRE el buffer PRIMERO. A 85 % de disco quedan ~15 % libres (~28 GB en 193) = espacio
        # de sobra para unos MB: el watchdog JAMÁS debe matar con datos sin flushear (bug cazado en revisión
        # externa 2026-07-06 — antes salía por sys.exit ANTES de escribir → pérdida del buffer).
        h = time.strftime("%Y%m%d_%H", time.gmtime())
        path = os.path.join(DATA, f"lighter_{h}.ndjson.zst")
        blob = self.comp.compress(b"".join(self.buf))
        with open(path, "ab") as f:
            f.write(blob)
        self.n_lines += len(self.buf)
        self.buf = []
        # Watchdog DESPUÉS de asegurar el buffer: si el disco está crítico, salida limpia (systemd Restart
        # reintenta; si sigue lleno, re-sale). Lo ya bufferizado queda a salvo en disco.
        u = shutil.disk_usage(DATA)
        if 1 - u.free / u.total > DISK_CRIT:
            print(f"CRITICAL: disco >{DISK_CRIT:.0%} tras flush — salida limpia, buffer a salvo", flush=True)
            sys.exit(3)


W = HourlyZstWriter()


async def flusher():
    last_report = time.time()
    while True:
        await asyncio.sleep(FLUSH_S)
        W.flush()
        if time.time() - last_report > 600:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}Z] líneas acumuladas: {W.n_lines}", flush=True)
            last_report = time.time()


async def run():
    import websockets
    mm = market_map()
    chans = []
    for s in SYMBOLS:
        if s in mm:
            chans += [f"order_book/{mm[s]}", f"trade/{mm[s]}"]
        else:
            print(f"WARN: {s} no está en el mapeo del venue", flush=True)
    print(f"canales a suscribir: {len(chans)} ({len(chans)//2} símbolos)", flush=True)
    asyncio.get_event_loop().create_task(flusher())
    while True:
        try:
            async with websockets.connect(WS_URL, ping_interval=60, ping_timeout=30,
                                          max_queue=None) as ws:
                for ch in chans:
                    await ws.send(json.dumps({"type": "subscribe", "channel": ch}))
                print(f"conectado y suscrito ({len(chans)} canales)", flush=True)
                async for msg in ws:
                    if isinstance(msg, bytes):
                        msg = msg.decode("utf-8", errors="replace")
                    W.add(json.dumps({"recv_ns": time.time_ns(), "frame": msg},
                                     separators=(",", ":")).encode() + b"\n")
        except SystemExit:
            raise
        except Exception as e:
            W.flush()
            print(f"reconexión tras {type(e).__name__}: {str(e)[:120]}", flush=True)
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run())
