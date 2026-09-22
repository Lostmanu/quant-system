"""analysis/fetch_funding.py — baja funding diario anualizado de los símbolos de la sonda que faltan,
con get_funding/daily_funding conservadas del instrumento H2 retirado. Formato [day, funding_annual] = el ya existente
en data_hist/funding/ (ATOM, BTC, DOT, ETH...). Para prima #2 (funding carry) y su neutralización H5."""
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

DAY_MS = 86_400_000


def get_funding(symbol: str, start_ms: int, end_ms: int) -> list:
    """Funding histórico de Binance Futures (público, paginado 1000/llamada)."""
    out, cur = [], start_ms
    while cur < end_ms:
        url = (f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}"
               f"&startTime={cur}&endTime={end_ms}&limit=1000")
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
        if not data:
            break
        out += data
        last = int(data[-1]["fundingTime"])
        if last <= cur or len(data) < 1000:
            break
        cur = last + 1
        time.sleep(0.25)
    return out


def daily_funding(records: list) -> tuple[np.ndarray, np.ndarray]:
    """Agrega a día: día (epoch-día) y funding medio ANUALIZADO (tasa·3·365)."""
    if not records:
        return np.array([], "int64"), np.array([])
    t = np.array([int(r["fundingTime"]) for r in records], "int64")
    rate = np.array([float(r["fundingRate"]) for r in records]) * 3 * 365
    day = t // DAY_MS
    ud, inv = np.unique(day, return_inverse=True)
    mean = np.bincount(inv, weights=rate) / np.bincount(inv)
    return ud, mean

OUT = "data_hist/funding"
START_MS = 1_577_836_800_000                                   # 2020-01-01
MISSING = ["AVAXUSDT", "LINKUSDT", "NEARUSDT", "LTCUSDT", "FILUSDT", "UNIUSDT"]


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    os.makedirs(OUT, exist_ok=True)
    now_ms = int(time.time() * 1000)
    for s in MISSING:
        recs = get_funding(s, START_MS, now_ms)
        ud, fund = daily_funding(recs)
        if len(ud) == 0:
            print(f"{s}: SIN DATOS"); continue
        pq.write_table(pa.table({"day": ud, "funding_annual": fund}), os.path.join(OUT, f"{s}.parquet"))
        print(f"{s:9} {len(ud):5} días  medio={np.mean(fund)*100:6.2f}%/año  "
              f"rango[{np.min(fund)*100:6.1f}%, {np.max(fund)*100:6.1f}%]")
    print("LISTO")


if __name__ == "__main__":
    main()
