"""tools/audit_day.py — Auditoría (y compactación) por día (ESPEC §6).

Uso:  python tools/audit_day.py [--day YYYY-MM-DD] [--symbols A,B] [--no-compact]
Por defecto audita el día más reciente de cada símbolo con datos. --no-compact
deja los parts intactos (solo lectura; útil mientras la ingesta sigue viva).
"""
from __future__ import annotations
import argparse
import glob
import os
import sys


def audit_table(day: str = "*", symbols: set[str] | None = None,
                compact: bool = True, data_dir: str = "data") -> list[dict]:
    from ingestion.audit import write_audit
    rows = []
    for sym_dir in sorted(glob.glob(os.path.join(data_dir, "*"))):
        sym = os.path.basename(sym_dir)
        if symbols and sym not in symbols:
            continue
        days = sorted(d for d in glob.glob(os.path.join(sym_dir, day))
                      if os.path.isdir(d))
        if not days:
            rows.append({"symbol": sym})
            continue
        dd = days[-1]
        res = write_audit(dd, os.path.join(dd, "audit.json"), compact=compact)
        rows.append({"symbol": sym, "day": os.path.basename(dd), **res})
    return rows


def print_table(rows: list[dict]) -> None:
    print(f"{'symbol':10s} {'day':10s} {'events':>7s} {'rebuilds':>8s} "
          f"{'trades':>7s} {'status':>6s}  checks_fallidos")
    for r in rows:
        if "n_events" not in r:
            print(f"{r['symbol']:10s} (sin datos)")
            continue
        bad = [k for k, v in r["checks"].items() if not v]
        print(f"{r['symbol']:10s} {r['day']:10s} {r['n_events']:7d} "
              f"{r['n_rebuilds']:8d} {r.get('n_trades', 0):7d} "
              f"{r['status']:>6s}  {bad or '-'}")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # → qs/
    sys.path.insert(0, os.getcwd())
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--day", default="*", help="YYYY-MM-DD (defecto: el más reciente)")
    ap.add_argument("--symbols", default=None, help="lista separada por comas")
    ap.add_argument("--no-compact", action="store_true",
                    help="no compactar parts (solo lectura)")
    a = ap.parse_args()
    syms = {s.strip().upper() for s in a.symbols.split(",")} if a.symbols else None
    print_table(audit_table(a.day, syms, compact=not a.no_compact))
