"""tools/smoke.py — Test de humo de la ingesta (herramienta oficial; /smoke).

Orquestación real (run_symbol_feed + fallback REST + drain + heartbeat) sin
add_signal_handler, con parada limpia automática tras --seconds y tabla de
auditoría del día al final. No modifica la lógica de ingesta: la reutiliza.

Uso:  python tools/smoke.py [--seconds 600] [--symbols all|BTCUSDT,ETHUSDT]
"""
from __future__ import annotations
import argparse
import asyncio
import logging
import os
import sys
import time

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # → qs/
sys.path.insert(0, os.getcwd())

import yaml

# logging a fichero+consola ANTES de importar ingestion.main (force=True para
# ganarle a su basicConfig de nivel de módulo)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("smoke.log", mode="w", encoding="utf-8"),
              logging.StreamHandler()],
    force=True,
)
log = logging.getLogger("smoke")

from ingestion.feed_binance import (FALLBACK_POLL_SECS, FALLBACK_SILENCE_SECS,
                                    TradeState, run_symbol_feed, run_trade_fallback,
                                    run_trade_ws)
from ingestion.writer import ParquetBuffer, DEPTH_SCHEMA, TRADE_SCHEMA
from ingestion.main import drain, heartbeat, send_alert, supervise
from tools.audit_day import audit_table, print_table


async def amain(symbols: list[str], base: str, seconds: int, fb: dict) -> None:
    stop = asyncio.Event()
    last_seen: dict[str, float] = {}
    counters: dict[str, int] = {}

    def mk_drain(q, kind, schema, key, s):
        def factory():   # buffer NUEVO en cada (re)arranque, como en producción
            return drain(q, ParquetBuffer(base, s, kind, schema, auto_flush=False),
                         last_seen, key, stop, counters=counters)
        return factory

    tasks = [asyncio.create_task(
        supervise("heartbeat",
                  lambda: heartbeat(last_seen, stop, counters=counters), stop))]
    for s in symbols:
        dq = asyncio.Queue(maxsize=100_000)
        tq = asyncio.Queue(maxsize=100_000)
        last_seen[f"{s}:depth"] = last_seen[f"{s}:trades"] = time.monotonic()
        counters[f"{s}:depth"] = counters[f"{s}:trades"] = 0
        st = TradeState()
        tasks += [
            asyncio.create_task(supervise(
                f"{s}:book",
                lambda s=s, dq=dq: run_symbol_feed(s, dq, stop), stop)),
            asyncio.create_task(supervise(
                f"{s}:trades-ws",
                lambda s=s, tq=tq, st=st:
                    run_trade_ws(s, tq, stop, trade_state=st), stop)),
            asyncio.create_task(supervise(
                f"{s}:fallback",
                lambda s=s, tq=tq, st=st:
                    run_trade_fallback(s, tq, st, stop, alert=send_alert, **fb),
                stop)),
            asyncio.create_task(supervise(
                f"{s}:depth-writer",
                mk_drain(dq, "depth", DEPTH_SCHEMA, f"{s}:depth", s), stop)),
            asyncio.create_task(supervise(
                f"{s}:trades-writer",
                mk_drain(tq, "trades", TRADE_SCHEMA, f"{s}:trades", s), stop)),
        ]
    log.info("smoke arrancado: symbols=%s run=%ds", symbols, seconds)
    await asyncio.sleep(seconds)
    log.info("tiempo cumplido (%ds) -> parada limpia", seconds)
    stop.set()
    await asyncio.gather(*tasks, return_exceptions=True)
    log.info("smoke detenido limpiamente")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seconds", type=int, default=600)
    ap.add_argument("--symbols", default="all",
                    help='"all" = universo de instruments.yaml, o lista por comas')
    a = ap.parse_args()
    with open("config/instruments.yaml") as f:
        cfg = yaml.safe_load(f)
    symbols = (cfg["symbols"] if a.symbols.lower() == "all"
               else [s.strip().upper() for s in a.symbols.split(",")])
    fb_cfg = cfg.get("trade_fallback") or {}
    fb = {"silence": fb_cfg.get("silence_secs", FALLBACK_SILENCE_SECS),
          "poll": fb_cfg.get("poll_secs", FALLBACK_POLL_SECS)}
    asyncio.run(amain(symbols, cfg["data_dir"], a.seconds, fb))
    day = time.strftime("%Y-%m-%d", time.gmtime())
    print_table(audit_table(day, set(symbols), compact=False))
