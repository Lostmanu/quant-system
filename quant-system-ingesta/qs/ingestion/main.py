"""main.py — Orquestador de la ingesta (ESPEC §7, v2.0).

Cada task crítico (feed, fallback, writer/drain, heartbeat) corre bajo un
supervisor que lo relanza con backoff y alerta si muere. El flush a Parquet se
ejecuta en un thread executor: un disco lento no detiene la captura.
Ejecutar: python -m ingestion.main
"""
from __future__ import annotations
import asyncio
import logging
import os
import random
import signal
import time
import aiohttp
import yaml
from .feed_binance import (FALLBACK_POLL_SECS, FALLBACK_SILENCE_SECS, TradeState,
                           run_symbol_feed, run_trade_fallback, run_trade_ws)
from .writer import ParquetBuffer, PartialWriteError, DEPTH_SCHEMA, TRADE_SCHEMA

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("main")
HEARTBEAT_SECS = 60
ALERT_SILENCE_SECS = 120
SUPERVISOR_STABLE_SECS = 300   # si la vida duró esto, el backoff se resetea


async def _sleep_or_stop(stop: asyncio.Event, secs: float) -> None:
    """Duerme `secs` o hasta que llegue stop: parada rápida ante SIGTERM
    (TimeoutStopSec=30 en systemd; un sleep ciego de 60s acabaría en SIGKILL)."""
    try:
        await asyncio.wait_for(stop.wait(), timeout=secs)
    except asyncio.TimeoutError:
        pass


async def drain(q: asyncio.Queue, buf: ParquetBuffer, last_seen: dict, key: str,
                stop: asyncio.Event, counters: dict | None = None) -> None:
    """Consume la cola y escribe parts. El flush (parquet+fsync, bloqueante) se
    despacha a un thread executor; si falla, las filas NO publicadas vuelven al
    buffer y se reintenta (cero pérdida silenciosa, sin duplicados), con alerta
    al romperse la escritura y al recuperarse."""
    loop = asyncio.get_running_loop()
    write_broken = False

    async def _write_failed(e: Exception, restored: list) -> None:
        nonlocal write_broken
        buf.rows = restored + buf.rows         # al frente: orden preservado
        log.error("%s writer error: %s (%d filas retenidas, reintento)",
                  key, e, len(restored))
        if not write_broken:                   # debounce: 1 alerta por incidencia
            write_broken = True
            await send_alert(f"⚠️ quant-ingesta: fallo de escritura en {key}: {e} "
                             f"(filas retenidas en memoria hasta recuperar disco)")

    try:
        while not (stop.is_set() and q.empty()):
            try:
                rec = await asyncio.wait_for(q.get(), timeout=1.0)
            except asyncio.TimeoutError:
                rec = None
            if rec is not None:
                buf.add(rec)                       # solo encola (auto_flush=False)
                last_seen[key] = time.monotonic()
                if counters is not None:
                    counters[key] = counters.get(key, 0) + 1
            if buf.due():
                rows = buf.take()
                try:
                    await loop.run_in_executor(None, buf.write_rows, rows)
                    if write_broken:
                        write_broken = False
                        await send_alert(f"✅ quant-ingesta: escritura de {key} recuperada")
                except PartialWriteError as e:     # multi-día: solo lo no publicado
                    await _write_failed(e, e.pending)
                except Exception as e:             # defensa: nada llegó a publicarse
                    await _write_failed(e, rows)
    finally:
        try:
            buf.close()    # también ante cancelación (Ctrl+C): flush final síncrono
        except Exception as e:
            log.error("%s writer error al cerrar: %s", key, e)


async def send_alert(text: str) -> None:
    """Notificación de alerta por Telegram (ESPEC §7). Configurable por entorno:
    TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID. Si faltan, no-op (solo log) para que la
    ingesta funcione sin notificaciones. Nunca propaga excepciones: un fallo de red
    en la alerta no puede tumbar la captura."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        log.warning("alerta NO enviada (TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID sin configurar): %s", text)
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        async with aiohttp.ClientSession() as s:
            async with s.post(url, json={"chat_id": chat, "text": text},
                              timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    body = await r.text()
                    log.error("Telegram devolvió %s: %s", r.status, body[:200])
    except Exception as e:
        log.error("fallo enviando alerta Telegram: %s", e)


def _parse_chrony_tracking(csv_out: str) -> float | None:
    """Campo 'System time' (offset del reloj en segundos, con signo) de la
    salida CSV de `chronyc -c tracking`. None si el formato no cuadra."""
    f = csv_out.strip().split(",")
    try:
        return float(f[4]) if len(f) > 6 else None
    except ValueError:
        return None


async def _ntp_offset_s() -> float | None:
    """Offset NTP vía chrony (ESPEC §7). None si no hay chronyc (dev Windows)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "chronyc", "-c", "tracking",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        return _parse_chrony_tracking(out.decode())
    except Exception:
        return None


def _rates_line(counters: dict, prev: dict, dt_s: float) -> str:
    """'SYM 612d/19t' por símbolo: eventos depth/trades POR MINUTO desde el
    último latido (ESPEC §7: tasas de eventos por símbolo)."""
    if dt_s <= 0:
        return ""
    por_simbolo: dict[str, dict[str, float]] = {}
    for k, v in counters.items():
        sym, kind = k.rsplit(":", 1)
        por_simbolo.setdefault(sym, {})[kind] = (v - prev.get(k, 0)) * 60 / dt_s
    return " ".join(
        f"{sym} {por_simbolo[sym].get('depth', 0.0):.0f}d/"
        f"{por_simbolo[sym].get('trades', 0.0):.0f}t"
        for sym in sorted(por_simbolo))


async def heartbeat(last_seen: dict, stop: asyncio.Event,
                    counters: dict | None = None) -> None:
    """Latido cada 60s (ESPEC §7): tasas por símbolo + offset NTP + alerta
    debounced de streams en silencio."""
    alerted: set[str] = set()           # streams ya notificados como caídos (debounce)
    prev: dict[str, int] = dict(counters) if counters else {}
    prev_t = time.monotonic()
    while not stop.is_set():
        await _sleep_or_stop(stop, HEARTBEAT_SECS)
        if stop.is_set():
            break
        now = time.monotonic()           # v2: liveness con monotónico (inmune a NTP)
        silent = {k for k, t in last_seen.items() if now - t > ALERT_SILENCE_SECS}
        ntp = await _ntp_offset_s()
        ntp_txt = f"{ntp:+.6f}s" if ntp is not None else "n/a"
        if counters is not None:
            tasas = _rates_line(counters, prev, now - prev_t)
            prev, prev_t = dict(counters), now
            log.info("heartbeat | streams=%d silenciosos=%s ntp_offset=%s | "
                     "tasas/min: %s", len(last_seen),
                     sorted(silent) or "ninguno", ntp_txt, tasas or "-")
        else:
            log.info("heartbeat | streams=%d silenciosos=%s ntp_offset=%s",
                     len(last_seen), sorted(silent) or "ninguno", ntp_txt)
        nuevos = silent - alerted        # transición sano → caído
        recuperados = alerted - silent   # transición caído → sano
        if nuevos:
            log.error("ALERTA: sin eventos >%ss en %s", ALERT_SILENCE_SECS, sorted(nuevos))
            await send_alert(f"⚠️ quant-ingesta: sin eventos >{ALERT_SILENCE_SECS}s en {sorted(nuevos)}")
        if recuperados:
            log.info("recuperados: %s", sorted(recuperados))
            await send_alert(f"✅ quant-ingesta: recuperados {sorted(recuperados)}")
        alerted = silent


async def supervise(name: str, factory, stop: asyncio.Event,
                    max_backoff: int = 60) -> None:
    """Mantiene vivo un task crítico (ESPEC §7 v2.0): si su coroutine muere por
    excepción — o retorna sin que haya stop — alerta y la relanza con backoff
    exponencial + jitter; el backoff se resetea tras una vida estable."""
    backoff = 1
    while not stop.is_set():
        t0 = time.monotonic()
        try:
            await factory()
            if stop.is_set():
                return
            log.error("%s terminó sin stop → reinicio", name)
            await send_alert(f"⚠️ quant-ingesta: task {name} terminó solo → reinicio")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.error("%s murió: %s → reinicio", name, e)
            await send_alert(f"⚠️ quant-ingesta: task {name} murió: {e} → reinicio")
        if time.monotonic() - t0 > SUPERVISOR_STABLE_SECS:
            backoff = 1
        await _sleep_or_stop(stop, backoff * (0.5 + random.random() * 0.5))
        backoff = min(backoff * 2, max_backoff)


def _install_signal_handlers(loop, stop: asyncio.Event) -> bool:
    """SIGINT/SIGTERM → parada limpia (VPS/systemd manda SIGTERM). En Windows el
    Proactor no lo soporta: devolvemos False y la parada es Ctrl+C
    (KeyboardInterrupt en asyncio.run; drain cierra los writers en finally)."""
    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop.set)
        return True
    except (NotImplementedError, RuntimeError):
        return False


async def amain() -> None:
    with open("config/instruments.yaml") as f:
        cfg = yaml.safe_load(f)
    symbols, base = cfg["symbols"], cfg["data_dir"]
    fb_cfg = cfg.get("trade_fallback") or {}
    fb = {"silence": fb_cfg.get("silence_secs", FALLBACK_SILENCE_SECS),
          "poll": fb_cfg.get("poll_secs", FALLBACK_POLL_SECS)}
    stop = asyncio.Event()
    if not _install_signal_handlers(asyncio.get_running_loop(), stop):
        log.info("add_signal_handler no soportado (Windows): parar con Ctrl+C")

    last_seen: dict[str, float] = {}
    counters: dict[str, int] = {}      # eventos acumulados por stream (tasas §7)

    def mk_drain(q, kind, schema, key, s):
        def factory():   # buffer NUEVO en cada (re)arranque del task
            return drain(q, ParquetBuffer(base, s, kind, schema, auto_flush=False),
                         last_seen, key, stop, counters=counters)
        return factory

    tasks = [asyncio.create_task(
        supervise("heartbeat",
                  lambda: heartbeat(last_seen, stop, counters=counters), stop))]
    for s in symbols:
        dq, tq = asyncio.Queue(maxsize=100_000), asyncio.Queue(maxsize=100_000)
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
                    run_trade_fallback(s, tq, st, stop, alert=send_alert, **fb), stop)),
            asyncio.create_task(supervise(
                f"{s}:depth-writer",
                mk_drain(dq, "depth", DEPTH_SCHEMA, f"{s}:depth", s), stop)),
            asyncio.create_task(supervise(
                f"{s}:trades-writer",
                mk_drain(tq, "trades", TRADE_SCHEMA, f"{s}:trades", s), stop)),
        ]
    log.info("ingesta arrancada: %s", symbols)
    await asyncio.gather(*tasks, return_exceptions=True)
    log.info("ingesta detenida limpiamente")


if __name__ == "__main__":
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt → parada (parts publicados intactos; "
                 "se pierde como mucho el buffer en memoria ≤60s)")
