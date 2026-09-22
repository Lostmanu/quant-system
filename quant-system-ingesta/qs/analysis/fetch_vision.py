"""analysis/fetch_vision.py — Histórico oficial gratuito de Binance (ESPEC §12, v1.6).

Descarga aggTrades mensuales y fundingRate de data.binance.vision (futuros USDT-M,
repositorio público, sin credenciales) y los convierte a Parquet/Snappy:

    data_hist/{symbol}/aggTrades-{YYYY-MM}.parquet
    data_hist/{symbol}/fundingRate.parquet

Idempotente: los meses ya convertidos se saltan. Verifica filas y rango temporal.
Sin recv_ts_ns/event_ts_ms: no existen en el histórico y no se fabrican.

Uso:  python analysis/fetch_vision.py [--months 12] [--symbols all|A,B] [--end YYYY-MM]
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

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.parquet as pq
import yaml

BASE = "https://data.binance.vision/data/futures/um/monthly"
AGG_COLS = ["agg_trade_id", "price", "quantity", "first_trade_id",
            "last_trade_id", "transact_time", "is_buyer_maker"]
HIST_DIR = "data_hist"


def month_range(end_ym: str, n: int) -> list[str]:
    y, m = map(int, end_ym.split("-"))
    out = []
    for _ in range(n):
        out.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return sorted(out)


def fetch(url: str, retries: int = 3) -> bytes | None:
    """None = 404 (mes no publicado: símbolo joven o aún sin cerrar)."""
    for i in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            print(f"  HTTP {e.code} intento {i}/{retries}", flush=True)
        except Exception as e:
            print(f"  error intento {i}/{retries}: {e}", flush=True)
        time.sleep(2 * i)
    raise RuntimeError(f"descarga imposible tras {retries} intentos: {url}")


def unzip_csv(blob: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        return z.read(z.namelist()[0])


def _has_header(data: bytes) -> bool:
    """Los CSV antiguos del repo no traen cabecera; detectar por el primer campo
    (agg_trade_id/calc_time numéricos en datos, alfabéticos en cabecera)."""
    first_field = data.split(b"\n", 1)[0].split(b",", 1)[0].strip()
    return not first_field.isdigit()


def read_agg_csv(data: bytes) -> pa.Table:
    tbl = pacsv.read_csv(
        io.BytesIO(data),
        read_options=pacsv.ReadOptions(column_names=AGG_COLS,
                                       skip_rows=1 if _has_header(data) else 0),
        convert_options=pacsv.ConvertOptions(
            column_types={"agg_trade_id": pa.int64(), "price": pa.float64(),
                          "quantity": pa.float64(), "first_trade_id": pa.int64(),
                          "last_trade_id": pa.int64(), "transact_time": pa.int64(),
                          "is_buyer_maker": pa.bool_()},
            true_values=["true", "True", "TRUE"],
            false_values=["false", "False", "FALSE"]))
    ts = tbl["transact_time"]
    # algunos tramos del repo publican microsegundos; normalizar a ms
    if tbl.num_rows and pc.max(ts).as_py() > 10 ** 14:
        ts = pc.divide(ts, 1000)
    return pa.table({"trade_ts_ms": ts,
                     "agg_trade_id": tbl["agg_trade_id"],
                     "price": tbl["price"], "qty": tbl["quantity"],
                     "is_buyer_maker": tbl["is_buyer_maker"]})


def read_funding_csv(data: bytes) -> pa.Table:
    if _has_header(data):
        names = [s.strip() for s in
                 data.split(b"\n", 1)[0].decode("ascii", "ignore").split(",")]
        skip = 1
    else:
        names, skip = ["calc_time", "funding_interval_hours", "last_funding_rate"], 0
    return pacsv.read_csv(io.BytesIO(data),
                          read_options=pacsv.ReadOptions(column_names=names,
                                                         skip_rows=skip))


def check_month(tbl: pa.Table, ym: str) -> None:
    """Filas > 0 y trade_ts_ms dentro del mes (±1 día de holgura)."""
    if tbl.num_rows == 0:
        raise RuntimeError(f"{ym}: 0 filas")
    y, m = map(int, ym.split("-"))
    ini = calendar.timegm((y, m, 1, 0, 0, 0)) * 1000
    fin = calendar.timegm((y + (m == 12), m % 12 + 1, 1, 0, 0, 0)) * 1000
    lo, hi = pc.min(tbl["trade_ts_ms"]).as_py(), pc.max(tbl["trade_ts_ms"]).as_py()
    if lo < ini - 86_400_000 or hi > fin + 86_400_000:
        raise RuntimeError(f"{ym}: timestamps fuera de rango ({lo}..{hi})")


def write_atomic(tbl: pa.Table, path: str) -> None:
    tmp = path + ".tmp"
    pq.write_table(tbl, tmp, compression="snappy")
    os.replace(tmp, path)


def fetch_symbol(symbol: str, months: list[str]) -> dict:
    d = os.path.join(HIST_DIR, symbol)
    os.makedirs(d, exist_ok=True)
    res = {"symbol": symbol, "nuevos": 0, "saltados": 0, "sin_publicar": 0,
           "filas": 0}
    funding_tables = []
    for ym in months:
        out = os.path.join(d, f"aggTrades-{ym}.parquet")
        if os.path.exists(out):
            res["saltados"] += 1
            res["filas"] += pq.read_metadata(out).num_rows
        else:
            blob = fetch(f"{BASE}/aggTrades/{symbol}/{symbol}-aggTrades-{ym}.zip")
            if blob is None:
                res["sin_publicar"] += 1
                continue
            tbl = read_agg_csv(unzip_csv(blob))
            check_month(tbl, ym)
            write_atomic(tbl, out)
            res["nuevos"] += 1
            res["filas"] += tbl.num_rows
            print(f"  {symbol} {ym}: {tbl.num_rows:,} trades", flush=True)
        fblob = fetch(f"{BASE}/fundingRate/{symbol}/{symbol}-fundingRate-{ym}.zip")
        if fblob is not None:
            funding_tables.append(read_funding_csv(unzip_csv(fblob)))
    if funding_tables:
        write_atomic(pa.concat_tables(funding_tables),
                     os.path.join(d, "fundingRate.parquet"))
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--months", type=int, default=12)
    ap.add_argument("--symbols", default="all")
    ap.add_argument("--end", default=None, help="último mes YYYY-MM (defecto: cerrado)")
    a = ap.parse_args()
    with open("config/instruments.yaml") as f:
        cfg = yaml.safe_load(f)
    symbols = (cfg["symbols"] if a.symbols.lower() == "all"
               else [s.strip().upper() for s in a.symbols.split(",")])
    if a.end:
        end = a.end
    else:  # último mes UTC cerrado
        t = time.gmtime()
        end = (f"{t.tm_year - (t.tm_mon == 1):04d}-"
               f"{(t.tm_mon - 1) or 12:02d}")
    months = month_range(end, a.months)
    print(f"histórico: {len(symbols)} símbolos × {months[0]}..{months[-1]}", flush=True)
    resumen = [fetch_symbol(s, months) for s in symbols]
    print(f"\n{'symbol':10s} {'nuevos':>6s} {'saltados':>8s} {'sin_pub':>7s} {'filas':>13s}")
    for r in resumen:
        print(f"{r['symbol']:10s} {r['nuevos']:6d} {r['saltados']:8d} "
              f"{r['sin_publicar']:7d} {r['filas']:13,d}")


if __name__ == "__main__":
    main()
