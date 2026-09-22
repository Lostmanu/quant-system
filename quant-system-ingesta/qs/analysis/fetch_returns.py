"""analysis/fetch_returns.py — cierres diarios (klines 1d, Binance Futures público) de los 8 perps de
la sonda + BTC (factor de mercado para la neutralización H5). Escribe data_hist/returns/{symbol}.parquet
con [day, close, logret]. `day` = openTime//86.4M = epoch-día (alinea con data_hist/funding/)."""
from __future__ import annotations
import json
import os
import sys
import time
import urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # qs/ al path
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

OUT = "data_hist/returns"
START_MS = 1_577_836_800_000                                   # 2020-01-01
DAY_MS = 86_400_000
SYMS = ["AVAXUSDT", "LINKUSDT", "DOTUSDT", "NEARUSDT", "ATOMUSDT", "LTCUSDT", "FILUSDT", "UNIUSDT", "BTCUSDT"]


def get_klines(symbol: str, start_ms: int, end_ms: int) -> list:
    """Klines 1d de Binance Futures (público, paginado 1500/llamada)."""
    out, cur = [], start_ms
    while cur < end_ms:
        url = (f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1d"
               f"&startTime={cur}&endTime={end_ms}&limit=1500")
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
        if not data:
            break
        out += data
        last = int(data[-1][0])
        if last <= cur or len(data) < 1500:
            break
        cur = last + 1
        time.sleep(0.25)
    return out


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    os.makedirs(OUT, exist_ok=True)
    now_ms = int(time.time() * 1000)
    for s in SYMS:
        kl = get_klines(s, START_MS, now_ms)
        if not kl:
            print(f"{s}: SIN DATOS"); continue
        day = np.array([int(k[0]) // DAY_MS for k in kl], "int64")
        close = np.array([float(k[4]) for k in kl], "float64")
        logret = np.concatenate([[0.0], np.diff(np.log(close))])
        pq.write_table(pa.table({"day": day, "close": close, "logret": logret}),
                       os.path.join(OUT, f"{s}.parquet"))
        print(f"{s:9} {len(day):5} días  ret_medio={np.mean(logret[1:])*100:6.3f}%/día  "
              f"vol={np.std(logret[1:])*100:5.2f}%")
    print("LISTO")


if __name__ == "__main__":
    main()
