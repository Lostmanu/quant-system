"""feed_binance.py — Conexión WS a Binance USDT-M Futures (ESPEC §3, §7, v2.1).

v2.1: Binance segmentó el fan-out WS en rutas (/public, /market) y las URLs
legacy solo sirven /public desde 2026-04-23 — la "incidencia aggTrade" de la
bitácora era eso. Dos conexiones por símbolo: libro (depth, /public) en
run_symbol_feed y trades (aggTrade, /market) en run_trade_ws; las rutas no se
mezclan en una conexión. Fallback REST como red de seguridad (watermark común).
"""
from __future__ import annotations
import asyncio
import json
import logging
import random
import time
import aiohttp
from .book import LocalBook, GapError, BookRecord

log = logging.getLogger("feed")
WS_PUBLIC = "wss://fstream.binance.com/public/stream?streams="   # depth (v2.1)
WS_MARKET = "wss://fstream.binance.com/market/stream?streams="   # aggTrade (v2.1)
REST_DEPTH = "https://fapi.binance.com/fapi/v1/depth"
REST_AGG_TRADES = "https://fapi.binance.com/fapi/v1/aggTrades"
BACKOFF_MAX = 60
FALLBACK_SILENCE_SECS = 120   # WS de trades mudo este tiempo → fallback REST (ESPEC §3, v1.1)
FALLBACK_POLL_SECS = 5        # entre polls REST; peso 20/req → 8 símbolos ≈ 1920/2400 por min


class TradeState:
    """Estado compartido WS↔REST por símbolo. `last_id` es un watermark CONTIGUO:
    todo agg_trade_id <= last_id está encolado, sin huecos. Un trade WS que llega
    tras un hueco NO se encola fuera de orden (lo repone el poller REST): avanzar
    el watermark saltando ids perdería ese tramo para siempre (ESPEC §1)."""
    __slots__ = ("last_id", "ws_ts", "ws_mono", "ws_max")

    def __init__(self) -> None:
        self.last_id = -1              # mayor agg_trade_id encolado SIN huecos previos
        self.ws_ts = time.time()       # pared: solo para el startTime del REST
        self.ws_mono = time.monotonic()  # liveness del WS (v2: inmune a NTP)
        self.ws_max = -1               # mayor agg_trade_id visto por el WS

    def ws_accept(self, a: int) -> bool:
        """Al recibir un trade por WS: True → encolar ya (contiguo); False →
        duplicado, o tras hueco (el poller REST repone last_id+1..a en orden)."""
        self.ws_ts = time.time()
        self.ws_mono = time.monotonic()
        if a > self.ws_max:
            self.ws_max = a
        if a <= self.last_id:
            return False             # ya encolado (dedup WS/REST)
        if self.last_id >= 0 and a > self.last_id + 1:
            return False             # hueco detectado: lo rellena el poller REST
        self.last_id = a
        return True

    @property
    def hole(self) -> bool:
        """Quedan trades vistos por el WS aún no repuestos en orden."""
        return self.ws_max > self.last_id


async def fetch_snapshot(session: aiohttp.ClientSession, symbol: str) -> dict:
    async with session.get(REST_DEPTH, params={"symbol": symbol, "limit": 1000}) as r:
        r.raise_for_status()
        return await r.json()


async def run_symbol_feed(symbol: str, depth_q: asyncio.Queue,
                          stop: asyncio.Event) -> None:
    """Mantiene el libro L2 sincronizado (depth@100ms, ruta /public) y empuja
    BookRecord a la cola. Reconexión con backoff; re-snapshot tras (re)conexión
    o gap. Los trades van por conexión aparte (run_trade_ws, v2.1)."""
    streams = f"{symbol.lower()}@depth@100ms"
    backoff = 1
    while not stop.is_set():
        snap_task = None
        try:
            async with aiohttp.ClientSession() as session:
                buffer: list[dict] = []
                book = LocalBook(symbol)
                async with session.ws_connect(WS_PUBLIC + streams, heartbeat=30) as ws:
                    backoff = 1
                    snap_task = asyncio.create_task(fetch_snapshot(session, symbol))
                    snapshot = None
                    async for msg in ws:
                        if stop.is_set():
                            break
                        if msg.type != aiohttp.WSMsgType.TEXT:
                            continue
                        data = json.loads(msg.data)["data"]
                        if data.get("e") != "depthUpdate":
                            continue
                        # fase de sincronización: bufferizar hasta tener snapshot
                        if snapshot is None:
                            buffer.append(data)
                            if snap_task.done():
                                snapshot = snap_task.result()
                                book.load_snapshot(snapshot)
                                # ESPEC §3 paso 4 / §7: marcador BOOK_REBUILD tras cada
                                # (re)snapshot. Sin él, la auditoría C2 contaría la
                                # discontinuidad post-gap como secuencia rota (día FAIL).
                                await depth_q.put(book.rebuild_record())
                                for ev in buffer:           # drenar buffer
                                    rec = _apply(book, ev)
                                    if rec:
                                        await depth_q.put(rec)
                                buffer.clear()
                            continue
                        rec = _apply(book, data)
                        if rec:
                            await depth_q.put(rec)
        except GapError as e:
            log.warning("%s gap: %s → re-snapshot", symbol, e)
            await asyncio.sleep(0.5)        # reconecta y re-sincroniza (loop)
        except Exception as e:              # red, HTTP, etc.
            log.error("%s feed error: %s → backoff ~%ss", symbol, e, backoff)
            # jitter (§7 v1.4): evita que los 8 símbolos martilleen a la vez tras
            # una caída común; duerme en [backoff/2, backoff]
            await asyncio.sleep(backoff * (0.5 + random.random() * 0.5))
            backoff = min(backoff * 2, BACKOFF_MAX)
        finally:
            # no dejar fetch de snapshot huérfano en gaps/reconexiones: cancelarlo
            # o consumir su excepción (evita "Task exception was never retrieved")
            if snap_task is not None:
                if not snap_task.done():
                    snap_task.cancel()
                elif not snap_task.cancelled():
                    snap_task.exception()


def _apply(book: LocalBook, ev: dict) -> BookRecord | None:
    """Aplica diff; ante gap lanza GapError (capturado arriba → rebuild)."""
    rec = book.apply_diff(ev)
    return rec


async def run_trade_ws(symbol: str, trade_q: asyncio.Queue, stop: asyncio.Event,
                       trade_state: TradeState | None = None) -> None:
    """Trades en tiempo real vía WS aggTrade (ruta /market, v2.1). Comparte el
    watermark contiguo con el poller REST (TradeState): duplicados y huecos se
    gestionan igual que siempre. Reconexión con backoff exponencial + jitter."""
    stream = f"{symbol.lower()}@aggTrade"
    backoff = 1
    while not stop.is_set():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(WS_MARKET + stream, heartbeat=30) as ws:
                    backoff = 1
                    async for msg in ws:
                        if stop.is_set():
                            break
                        if msg.type != aiohttp.WSMsgType.TEXT:
                            continue
                        data = json.loads(msg.data)["data"]
                        if data.get("e") != "aggTrade":
                            continue
                        if trade_state is not None and \
                                not trade_state.ws_accept(data["a"]):
                            continue     # duplicado o tras hueco (lo repone REST)
                        await trade_q.put({
                            "recv_ts_ns": time.time_ns(),
                            "recv_mono_ns": time.monotonic_ns(),
                            "event_ts_ms": data["E"],
                            "trade_ts_ms": data["T"], "agg_trade_id": data["a"],
                            "price": float(data["p"]), "qty": float(data["q"]),
                            "is_buyer_maker": data["m"]})
        except Exception as e:
            log.error("%s trade-ws error: %s → backoff ~%ss", symbol, e, backoff)
            await asyncio.sleep(backoff * (0.5 + random.random() * 0.5))
            backoff = min(backoff * 2, BACKOFF_MAX)


async def run_trade_fallback(symbol: str, trade_q: asyncio.Queue, state: TradeState,
                             stop: asyncio.Event,
                             silence: float = FALLBACK_SILENCE_SECS,
                             poll: float = FALLBACK_POLL_SECS,
                             alert=None) -> None:
    """Plan B de trades (ESPEC §3, v1.1/v1.4): actúa si el WS aggTrade lleva
    `silence` s mudo O si hay hueco de ids con el WS vivo (state.hole). Recupera
    por REST con paginación fromId sobre el watermark contiguo, hasta ponerse al
    día. `alert`: coroutine opcional (main.send_alert) para notificar ON/OFF.
    Es una red de seguridad: nunca propaga excepciones."""
    active = False

    async def _notify(text: str) -> None:
        if alert is None:
            return
        try:
            await alert(text)
        except Exception as e:
            log.error("%s fallback: alerta falló: %s", symbol, e)

    async with aiohttp.ClientSession() as session:
        while not stop.is_set():
            await asyncio.sleep(poll)
            silent = time.monotonic() - state.ws_mono >= silence
            if not (silent or state.hole):
                if active:
                    log.info("%s fallback REST OFF (trades al día)", symbol)
                    await _notify(f"✅ {symbol}: trades al día (fallback REST OFF)")
                    active = False
                continue
            if not active:
                motivo = "WS de trades mudo" if silent else "hueco de ids con WS vivo"
                log.warning("%s fallback REST ON (%s)", symbol, motivo)
                await _notify(f"⚠️ {symbol}: fallback REST ON ({motivo})")
                active = True
            try:
                total = 0
                while not stop.is_set():          # paginar hasta ponerse al día
                    params = {"symbol": symbol, "limit": 1000}
                    if state.last_id >= 0:
                        params["fromId"] = state.last_id + 1
                    else:                         # primera vez: desde el último latido WS
                        params["startTime"] = int(state.ws_ts * 1000)
                    async with session.get(REST_AGG_TRADES, params=params) as r:
                        r.raise_for_status()
                        trades = await r.json()
                    for t in trades:
                        if t["a"] <= state.last_id:
                            continue              # solape WS/REST → dedup
                        state.last_id = t["a"]
                        total += 1
                        await trade_q.put({
                            "recv_ts_ns": time.time_ns(),     # momento de la descarga
                            "recv_mono_ns": time.monotonic_ns(),
                            "event_ts_ms": t["T"],            # REST no expone E; T≈E
                            "trade_ts_ms": t["T"], "agg_trade_id": t["a"],
                            "price": float(t["p"]), "qty": float(t["q"]),
                            "is_buyer_maker": t["m"]})
                    if len(trades) < 1000:
                        break
                if total:
                    log.info("%s fallback REST: %d trades recuperados (hasta id %d)",
                             symbol, total, state.last_id)
            except Exception as e:                # red/429/json → reintento en próximo poll
                log.error("%s fallback REST error: %s", symbol, e)
