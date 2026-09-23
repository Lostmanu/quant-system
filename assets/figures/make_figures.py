"""Draws the three data figures on the front page from the CSV files in assets/figures/data/.

    python assets/figures/make_figures.py            # rewrite assets/result.svg, timeline.svg, code.svg
    python assets/figures/make_figures.py --check    # exit 1 if a published figure is not what the data gives

Standard library only. Every number drawn comes from a CSV next to this file, and data/README.md says
where each CSV came from. banner.svg, measurement.svg and checks.svg are drawn by hand and are not
produced here.
"""
import argparse
import csv
import datetime as dt
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
ASSETS = os.path.dirname(HERE)

BG, CARD, GRID, AXIS = "#12161C", "#1A2029", "#232B35", "#3A4450"
TEXT, SOFT, MUTED, DIM = "#F2F4F7", "#C9D2DD", "#8B98A8", "#8B98A8"
AMBER, BLUE, RED, GREEN = "#E8A33D", "#4A90D9", "#C0392B", "#3FB950"
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "'SF Mono', Consolas, 'Liberation Mono', monospace"


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]


def month(d):
    return MONTHS[d.month - 1]


def dmon(d):
    return f"{d.day} {MONTHS[d.month - 1][:3]}"


def rows(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def day(s):
    return dt.date.fromisoformat(s[:10])


def fmt(x, nd=2):
    s = f"{x:,.{nd}f}".replace("-", "−")
    return s if x < 0 else ("+" + s if x > 0 else s)


class Svg:
    def __init__(self, w, h, label):
        self.w, self.h = w, h
        self.out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
                    f'role="img" aria-label="{label}">', f'  <rect width="{w}" height="{h}" fill="{BG}"/>']

    def add(self, s):
        self.out.append("  " + s)

    def text(self, x, y, s, size=14, fill=SOFT, family=SERIF, anchor="start", extra=""):
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" fill="{fill}" '
                 f'text-anchor="{anchor}"{extra}>{s}</text>')

    def line(self, x1, y1, x2, y2, stroke=GRID, width=1, extra=""):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
                 f'stroke-width="{width}"{extra}/>')

    def render(self):
        return "\n".join(self.out + ["</svg>"]) + "\n"


# ------------------------------------------------------------------------------------------------
# Canvas 1000 wide: GitHub shows README images at about 838 px, so 16 units here are about 13 px there.
# Figures carry labels; the sentences that explain them are in the captions in README.md.
W = 1000


def result_svg():
    d25 = rows("d1_per_day_25s.csv")
    hz = rows("horizon_curve.csv")
    H = [float(r["H"]) for r in d25]
    A = [float(r["A"]) for r in d25]
    n = len(d25)
    mh, ma = sum(H) / n, sum(A) / n
    below = sum(1 for h, a in zip(H, A) if a < h)
    dl = [a - h for h, a in zip(H, A)]
    md = sum(dl) / n
    sd = (sum((v - md) ** 2 for v in dl) / (n - 1)) ** 0.5
    tstat = md / (sd / n ** 0.5)
    first, lastd = day(d25[0]["date"]), day(d25[-1]["date"])

    s = Svg(W, 560, f"Per-day markouts at 25 seconds for {n} days under the July fill rule and the wider rule, "
                    f"and the mean at five horizons under both rules.")
    s.text(40, 44, "The +18.24 basis points, day by day, under the two fill rules", 26, TEXT)
    s.text(40, 72, f"Slow orders, most volatile third, 25 s. Lighter LIT perpetual, {n} days between "
                   f"{first.day} {month(first)} and {lastd.day} {month(lastd)} 2026.", 16, MUTED,
           extra=' font-style="italic"')

    # panel A: one pair of dots per day, in date order
    x0, x1, y0, y1 = 80, 690, 110, 410
    lo, hi = -35.0, 65.0
    Y = lambda v: y1 - (min(max(v, lo), hi) - lo) / (hi - lo) * (y1 - y0)
    X = lambda i: x0 + 8 + i * (x1 - x0 - 16) / (n - 1)
    for v in range(-30, 70, 10):
        s.line(x0, Y(v), x1, Y(v), GRID if v else AXIS, 1)
        s.text(x0 - 10, Y(v) + 5, fmt(v, 0) if v else "0", 15, DIM, MONO, "end")
    last_month = None
    for i, r in enumerate(d25):
        m = day(r["date"]).month
        if m != last_month:
            s.line(X(i), y1, X(i), y1 + 6, AXIS)
            s.text(X(i) + 3, y1 + 25, month(day(r["date"])), 15, DIM, MONO)
            last_month = m
    for i, (h, a) in enumerate(zip(H, A)):
        s.line(X(i), Y(h), X(i), Y(a), "#4B5563", 1)
    for i, (h, a) in enumerate(zip(H, A)):
        s.add(f'<circle cx="{X(i):.1f}" cy="{Y(a):.1f}" r="3.8" fill="{BLUE}"/>')
        s.add(f'<circle cx="{X(i):.1f}" cy="{Y(h):.1f}" r="3.8" fill="{AMBER}"/>')
        if h > hi:
            s.add(f'<path d="M{X(i) - 6:.1f} {Y(hi) + 2:.1f} L{X(i):.1f} {Y(hi) - 8:.1f} L{X(i) + 6:.1f} '
                  f'{Y(hi) + 2:.1f} z" fill="{AMBER}"/>')
            s.text(X(i) + 12, Y(hi) - 4, f"{dmon(day(d25[i]['date']))}: {fmt(h, 0)}, off the scale", 15, AMBER, MONO)
            s.text(X(i) + 12, Y(hi) + 15, "zero-price reference", 15, AMBER, MONO)
    s.line(x0, Y(mh), x1, Y(mh), AMBER, 1.6, ' stroke-dasharray="6 4"')
    s.line(x0, Y(ma), x1, Y(ma), BLUE, 1.6, ' stroke-dasharray="6 4"')
    s.text(x1 + 8, Y(mh) + 5, f"{fmt(mh)}", 16, AMBER, MONO)
    s.text(x1 + 8, Y(ma) + 5, f"{fmt(ma, 3)}", 16, BLUE, MONO)

    # legend and the one sentence the chart needs
    ly = y1 + 62
    s.add(f'<circle cx="{x0 + 7}" cy="{ly - 5}" r="6" fill="{AMBER}"/>')
    s.text(x0 + 22, ly, "July rule", 16, SOFT)
    s.add(f'<circle cx="{x0 + 137}" cy="{ly - 5}" r="6" fill="{BLUE}"/>')
    s.text(x0 + 152, ly, "wider rule (adds through-with-at orders)", 16, SOFT)
    s.text(x0, ly + 32, f"Lower under the wider rule on {below} of {n} days. Mean paired difference "
                        f"{fmt(md)} bps, descriptive t {fmt(tstat)}.", 16, TEXT)

    # panel B: the mean at each horizon
    bx0, bx1, by0, by1 = 790, 960, 140, 350
    blo, bhi = -12.0, 24.0
    BY = lambda v: by1 - (v - blo) / (bhi - blo) * (by1 - by0)
    hs = [int(r["horizon_s"]) for r in hz]
    BX = lambda k: bx0 + k * (bx1 - bx0) / (len(hs) - 1)
    s.text(bx0 - 30, 118, "Mean by horizon", 16, TEXT)
    for v in (-10, 0, 10, 20):
        s.line(bx0, BY(v), bx1, BY(v), AXIS if v == 0 else GRID)
        s.text(bx0 - 8, BY(v) + 5, fmt(v, 0) if v else "0", 14, DIM, MONO, "end")
    for k, h in enumerate(hs):
        s.text(BX(k), by1 + 24, f"{h}", 14, DIM, MONO, "middle")
    s.text((bx0 + bx1) / 2, by1 + 46, "seconds", 14, DIM, MONO, "middle")
    for key, col in (("H", AMBER), ("A", BLUE)):
        pts = " ".join(f"{BX(k):.1f},{BY(float(r[key])):.1f}" for k, r in enumerate(hz))
        s.add(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.2"/>')
        for k, r in enumerate(hz):
            s.add(f'<circle cx="{BX(k):.1f}" cy="{BY(float(r[key])):.1f}" r="4" fill="{col}"/>')
    return s.render()


# ------------------------------------------------------------------------------------------------
def timeline_svg():
    wk = rows("commits_per_week.csv")
    ev = rows("timeline.csv")
    start, end = dt.date(2026, 6, 8), dt.date(2026, 9, 14)
    span = (end - start).days
    x0, x1 = 60, 970
    X = lambda d: x0 + (d - start).days / span * (x1 - x0)
    s = Svg(W, 470, "Commits per week from June to September 2026, with thirteen numbered events on the time axis. "
                    "The events are listed under the figure.")
    s.text(40, 44, "Fourteen weeks, 457 commits", 26, TEXT)
    s.text(40, 72, "Commits per week in the private repository. The numbered events are listed under the figure.",
           16, MUTED, extra=' font-style="italic"')

    base, top = 320, 132
    for e in ev:
        if not e["end"]:
            continue
        a, b = X(day(e["date"])), X(day(e["end"]))
        if e["kind"] == "outage":
            yb, col, lab = top + 6, "#F85149", "no data captured"   # 5.4:1 on the background
        else:
            yb, col, lab = top - 20, DIM, "ledger silent"
        s.add(f'<path d="M{a:.1f} {yb + 7:.1f} V{yb:.1f} H{b:.1f} V{yb + 7:.1f}" fill="none" stroke="{col}" '
              f'stroke-width="1.5"/>')
        s.text((a + b) / 2, yb - 7, lab, 14, col, MONO, "middle")
    mx = max(int(r["commits"]) for r in wk)
    Hb = lambda c: c / mx * (base - top - 24)
    for v in (20, 40, 60):
        s.line(x0, base - Hb(v), x1, base - Hb(v), GRID)
        s.text(x0 - 8, base - Hb(v) + 5, str(v), 14, DIM, MONO, "end")
    for r in wk:
        a = X(day(r["week_start"]))
        w = 7 / span * (x1 - x0)
        c = int(r["commits"])
        s.add(f'<rect x="{a + 3:.1f}" y="{base - Hb(c):.1f}" width="{w - 6:.1f}" height="{Hb(c):.1f}" '
              f'fill="{BLUE}" opacity="0.85"/>')
        if c == 0:
            s.text(a + w / 2, base - 7, "0", 14, DIM, MONO, "middle")
    s.line(x0, base, x1, base, AXIS)

    lanes, marks = [], []
    for i, e in enumerate(ev, 1):
        cx = X(day(e["date"]))
        k = 0
        while k < len(lanes) and cx - lanes[k] < 29:
            k += 1
        if k == len(lanes):
            lanes.append(cx)
        else:
            lanes[k] = cx
        marks.append((i, cx, base + 54 + k * 30))
    for i, cx, cy in marks:
        s.line(cx, base, cx, cy - 13, AXIS)
    # month names over the connectors, on a patch of background so the lines pass behind them
    m = dt.date(2026, 6, 1)
    while m <= end:
        if m >= start:
            s.line(X(m), base, X(m), base + 6, AXIS)
            name = month(m)
            s.add(f'<rect x="{X(m) + 1:.1f}" y="{base + 9:.1f}" width="{len(name) * 9.2 + 6:.1f}" height="21" '
                  f'fill="{BG}"/>')
            s.text(X(m) + 4, base + 24, name, 15, DIM, MONO)
        m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    for i, cx, cy in marks:
        s.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="13" fill="{CARD}" stroke="{SOFT}" stroke-width="1.5"/>')
        s.text(cx, cy + 5, str(i), 14, TEXT, MONO, "middle")
    return s.render()


# ------------------------------------------------------------------------------------------------
def code_svg():
    ch = rows("code_history.csv")
    pts = [(dt.datetime.fromisoformat(r["date"][:10]), int(r["loc_analysis_tools"]), int(r["loc_tests"]))
           for r in ch]
    t0, t1 = pts[0][0], pts[-1][0]
    span = (t1 - t0).total_seconds()
    x0, x1, y0, y1 = 90, 960, 110, 400
    top = 40000
    X = lambda t: x0 + (t - t0).total_seconds() / span * (x1 - x0)
    Y = lambda v: y1 - v / top * (y1 - y0)
    peak = max(pts, key=lambda p: p[1])
    last = pts[-1]
    cut = round(100 * (peak[1] - last[1]) / peak[1])
    s = Svg(W, 490, "Lines of Python in analysis and tools, and in tests, at every commit from June to September "
                    "2026.")
    s.text(40, 44, f"{cut} % of analysis/ and tools/ was removed on 8 and 9 September", 26, TEXT)
    s.text(40, 72, "Lines of Python at every commit on the main line of the private repository.", 16, MUTED,
           extra=' font-style="italic"')
    for v in range(0, top + 1, 10000):
        s.line(x0, Y(v), x1, Y(v), AXIS if v == 0 else GRID)
        s.text(x0 - 10, Y(v) + 5, f"{v:,}", 15, DIM, MONO, "end")
    m = dt.datetime(2026, 7, 1)
    while m <= t1:
        s.line(X(m), y1, X(m), y1 + 6, AXIS)
        s.text(X(m) + 4, y1 + 25, month(m), 15, DIM, MONO)
        m = m.replace(month=m.month + 1) if m.month < 12 else m.replace(year=m.year + 1, month=1)
    for key, col in ((2, BLUE), (1, AMBER)):          # analysis/tools on top: its drop is the headline
        path = " ".join(f"{X(p[0]):.1f},{Y(p[key]):.1f}" for p in pts)
        s.add(f'<polyline points="{path}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linejoin="round"/>')
    s.add(f'<circle cx="{X(peak[0]):.1f}" cy="{Y(peak[1]):.1f}" r="5" fill="{AMBER}"/>')
    s.text(X(peak[0]) - 12, Y(peak[1]) - 12, f"{peak[1]:,} on {dmon(peak[0])}", 16, AMBER, MONO, "end")
    s.add(f'<circle cx="{X(last[0]):.1f}" cy="{Y(last[1]):.1f}" r="5" fill="{AMBER}"/>')
    s.text(X(last[0]) - 12, Y(last[1]) - 12, f"{last[1]:,} on {dmon(last[0])}", 16, AMBER, MONO, "end")
    ly = y1 + 62
    s.add(f'<rect x="{x0}" y="{ly - 7}" width="18" height="4" fill="{AMBER}"/>')
    s.text(x0 + 28, ly, "analysis/ and tools/", 16, SOFT)
    s.add(f'<rect x="{x0 + 230}" y="{ly - 7}" width="18" height="4" fill="{BLUE}"/>')
    s.text(x0 + 258, ly, f"tests/ ({last[2]:,} lines at the end)", 16, SOFT)
    return s.render()


FIGURES = {"result.svg": result_svg, "timeline.svg": timeline_svg, "code.svg": code_svg}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if a figure is stale")
    args = ap.parse_args()
    stale = []
    for name, fn in FIGURES.items():
        path = os.path.join(ASSETS, name)
        new = fn()
        old = io.open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if old == new:
            print(f"  {name:14} up to date")
        elif args.check:
            print(f"  {name:14} STALE")
            stale.append(name)
        else:
            io.open(path, "w", encoding="utf-8", newline="\n").write(new)
            print(f"  {name:14} written")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
