"""analysis/fetch_metrics.py — Métricas diarias de Binance Vision (ESPEC §12 v2.2).

Descarga los ficheros `metrics` DIARIOS (OI 5min + ratios long/short) de los
símbolos del universo y los agrega en parquet MENSUALES:

    data_hist/{symbol}/metrics-{YYYY-MM}.parquet

Idempotente por mes. 404 tolerado (día sin publicar). ~365 ficheros/símbolo/año.

Uso:  python analysis/fetch_metrics.py [--months 12] [--symbols all|A,B]
"""
from __future__ import annotations
import argparse
import calendar
import io
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # → qs/
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.parquet as pq
import yaml

BASE = "https://data.binance.vision/data/futures/um/daily/metrics"
HIST_DIR = "data_hist"


def fetch(url: str, retries: int = 3) -> bytes | None:
    for i in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except Exception:
            pass
        time.sleep(1.5 * i)
    return None        # red caída persistente: el mes saldrá incompleto y se reintenta


def month_days(ym: str) -> list[str]:
    y, m = map(int, ym.split("-"))
    n = calendar.monthrange(y, m)[1]
    return [f"{ym}-{d:02d}" for d in range(1, n + 1)]


def month_range(end_ym: str, n: int) -> list[str]:
    y, m = map(int, end_ym.split("-"))
    out = []
    for _ in range(n):
        out.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return sorted(out)


def read_metrics_csv(data: bytes) -> pa.Table:
    return pacsv.read_csv(io.BytesIO(data))


def fetch_symbol(symbol: str, months: list[str], force: bool = False) -> dict:
    d = os.path.join(HIST_DIR, symbol)
    os.makedirs(d, exist_ok=True)
    res = {"symbol": symbol, "meses_nuevos": 0, "saltados": 0, "dias_404": 0,
           "filas": 0}
    for ym in months:
        out = os.path.join(d, f"metrics-{ym}.parquet")
        if os.path.exists(out) and not force:                 # `force`: re-baja un mes incompleto
            res["saltados"] += 1
            continue
        tablas = []
        for day in month_days(ym):
            blob = fetch(f"{BASE}/{symbol}/{symbol}-metrics-{day}.zip")
            if blob is None:
                res["dias_404"] += 1
                continue
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                tablas.append(read_metrics_csv(z.read(z.namelist()[0])))
        if not tablas:
            continue
        t = pa.concat_tables(tablas, promote_options="default")
        tmp = out + ".tmp"
        pq.write_table(t, tmp, compression="snappy")
        os.replace(tmp, out)
        res["meses_nuevos"] += 1
        res["filas"] += t.num_rows
        print(f"  {symbol} {ym}: {t.num_rows:,} filas", flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--months", type=int, default=12)
    ap.add_argument("--symbols", default="all")
    ap.add_argument("--month", default=None,
                    help="mes concreto YYYY-MM (p. ej. el mes EN CURSO de la sonda); ignora --months")
    ap.add_argument("--force", action="store_true",
                    help="re-descarga aunque el parquet ya exista (para extender un mes incompleto)")
    a = ap.parse_args()
    with open("config/instruments.yaml") as f:
        cfg = yaml.safe_load(f)
    symbols = (cfg["symbols"] if a.symbols.lower() == "all"
               else [s.strip().upper() for s in a.symbols.split(",")])
    if a.month:
        months = [a.month]
    else:
        t = time.gmtime()
        end = f"{t.tm_year - (t.tm_mon == 1):04d}-{(t.tm_mon - 1) or 12:02d}"
        months = month_range(end, a.months)
    print(f"metrics: {len(symbols)} símbolos × {months[0]}..{months[-1]}"
          f"{' (force)' if a.force else ''}", flush=True)
    resumen = [fetch_symbol(s, months, a.force) for s in symbols]
    print(f"\n{'symbol':10s} {'nuevos':>6s} {'saltados':>8s} {'404':>5s} {'filas':>10s}")
    for r in resumen:
        print(f"{r['symbol']:10s} {r['meses_nuevos']:6d} {r['saltados']:8d} "
              f"{r['dias_404']:5d} {r['filas']:10,d}")


if __name__ == "__main__":
    main()
