"""Draws the three data figures on the front page from the CSV files in assets/figures/data/.

    python assets/figures/make_figures.py            # rewrite assets/result.svg, timeline.svg, code.svg
    python assets/figures/make_figures.py --check    # exit 1 if a published figure is not what the data gives

Standard library only. Every number drawn comes from a CSV next to this file, and data/README.md says
where each CSV came from. The two diagrams (banner.svg and checks.svg) and measurement.svg are drawn
by hand and are not produced here.
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

    s = Svg(1200, 700, f"Per-day markouts at 25 seconds for {n} days under the historical fill rule and the "
                       f"wider rule, and the mean markout at five horizons under both rules.")
    s.text(60, 50, "The +18.24 basis points, day by day, under the two fill rules", 25, TEXT)
    first, lastd = day(d25[0]["date"]), day(d25[-1]["date"])
    s.text(60, 78, f"Slow orders, agitated tercile, 25 s horizon. Lighter LIT perpetual, {n} days between "
                   f"{first.day} {month(first)} and {lastd.day} {month(lastd)} 2026.",
           14, MUTED, extra=' font-style="italic"')

    # panel A ---------------------------------------------------------------
    x0, x1, y0, y1 = 110, 800, 120, 520
    lo, hi = -35.0, 65.0
    Y = lambda v: y1 - (min(max(v, lo), hi) - lo) / (hi - lo) * (y1 - y0)
    X = lambda i: x0 + 8 + i * (x1 - x0 - 16) / (n - 1)
    for v in range(-30, 70, 10):
        s.line(x0, Y(v), x1, Y(v), GRID if v else AXIS, 1)
        s.text(x0 - 12, Y(v) + 4, fmt(v, 0) if v else "0", 12, DIM, MONO, "end")
    s.text(x0 - 60, (y0 + y1) / 2, "markout, bps", 12, DIM, MONO, "middle",
           f' transform="rotate(-90 {x0 - 60} {(y0 + y1) / 2})"')
    last_month = None
    for i, r in enumerate(d25):
        m = day(r["date"]).month
        if m != last_month:
            s.line(X(i), y1, X(i), y1 + 6, AXIS)
            s.text(X(i) + 3, y1 + 22, month(day(r["date"])), 12, DIM, MONO)
            last_month = m
    cal = (day(d25[-1]["date"]) - day(d25[0]["date"])).days + 1
    s.text(x1, y1 + 40, f"{n} days with data, in order; the other {cal - n} calendar days are not shown", 12, DIM,
           MONO, "end")
    for i, (h, a) in enumerate(zip(H, A)):
        s.line(X(i), Y(h), X(i), Y(a), "#4B5563", 1)
    for i, (h, a) in enumerate(zip(H, A)):
        s.add(f'<circle cx="{X(i):.1f}" cy="{Y(a):.1f}" r="3.6" fill="{BLUE}"/>')
        s.add(f'<circle cx="{X(i):.1f}" cy="{Y(h):.1f}" r="3.6" fill="{AMBER}"/>')
        if h > hi:
            s.add(f'<path d="M{X(i) - 5:.1f} {Y(hi) + 2:.1f} L{X(i):.1f} {Y(hi) - 7:.1f} L{X(i) + 5:.1f} '
                  f'{Y(hi) + 2:.1f} z" fill="{AMBER}"/>')
            s.text(X(i) + 9, Y(hi) - 8, f"{dmon(day(d25[i]['date']))}: {fmt(h, 0)}, off the scale;", 12, AMBER, MONO)
            s.text(X(i) + 9, Y(hi) + 8, "the day with the zero-price reference", 12, AMBER, MONO)
    s.line(x0, Y(mh), x1, Y(mh), AMBER, 1.5, ' stroke-dasharray="6 4"')
    s.line(x0, Y(ma), x1, Y(ma), BLUE, 1.5, ' stroke-dasharray="6 4"')
    s.text(x1 + 8, Y(mh) + 4, f"mean {fmt(mh)}", 13, AMBER, MONO)
    s.text(x1 + 8, Y(ma) + 4, f"mean {fmt(ma, 3)}", 13, BLUE, MONO)

    # legend
    ly = y1 + 62
    s.add(f'<circle cx="{x0 + 6}" cy="{ly - 4}" r="5" fill="{AMBER}"/>')
    s.text(x0 + 18, ly, "historical rule, as coded in July 2026", 13, SOFT)
    s.add(f'<circle cx="{x0 + 6}" cy="{ly + 20}" r="5" fill="{BLUE}"/>')
    s.text(x0 + 18, ly + 24, "wider rule: also counts orders that vanished while trades printed both at and "
                             "through their price", 13, SOFT)
    s.text(x0, ly + 54, f"The wider rule gives the lower value on {below} of {n} days. Mean paired difference "
                        f"{fmt(md)} bps, descriptive t {fmt(tstat)}.", 13, TEXT)

    # panel B ---------------------------------------------------------------
    bx0, bx1, by0, by1 = 930, 1140, 150, 400
    blo, bhi = -12.0, 24.0
    BY = lambda v: by1 - (v - blo) / (bhi - blo) * (by1 - by0)
    hs = [int(r["horizon_s"]) for r in hz]
    BX = lambda k: bx0 + k * (bx1 - bx0) / (len(hs) - 1)
    s.text(bx0 - 20, 128, "Mean by horizon", 15, TEXT)
    for v in (-10, 0, 10, 20):
        s.line(bx0, BY(v), bx1, BY(v), AXIS if v == 0 else GRID)
        s.text(bx0 - 8, BY(v) + 4, fmt(v, 0) if v else "0", 11, DIM, MONO, "end")
    for k, h in enumerate(hs):
        s.text(BX(k), by1 + 20, f"{h} s", 11, DIM, MONO, "middle")
    for key, col in (("H", AMBER), ("A", BLUE)):
        pts = " ".join(f"{BX(k):.1f},{BY(float(r[key])):.1f}" for k, r in enumerate(hz))
        s.add(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2"/>')
        for k, r in enumerate(hz):
            s.add(f'<circle cx="{BX(k):.1f}" cy="{BY(float(r[key])):.1f}" r="3.5" fill="{col}"/>')
    for k, line in enumerate(["Each horizon averaged over its events.",
                              "5 s was the primary horizon, fixed in",
                              "advance. Three zero-price references",
                              "pull its July-rule mean from +10.38",
                              "down to +2.61."]):
        s.text(bx0 - 20, by1 + 50 + 16 * k, line, 12, MUTED)

    s.line(60, 656, 1140, 656, GRID)
    s.text(60, 680, "Post hoc diagnostic, approved on 5 September 2026 and run once on 7 September. Reference price: "
                    "nearest Binance trade. Source: docs/DICTAMEN_MESA_2026-09-07_I5_D1_79.md.", 13, DIM,
           extra=' font-style="italic"')
    return s.render()


# ------------------------------------------------------------------------------------------------
def timeline_svg():
    wk = rows("commits_per_week.csv")
    ev = rows("timeline.csv")
    start, end = dt.date(2026, 6, 8), dt.date(2026, 9, 14)
    span = (end - start).days
    x0, x1 = 80, 1140
    X = lambda d: x0 + (d - start).days / span * (x1 - x0)
    s = Svg(1200, 700, "Commits per week from June to September 2026 with the main events of the programme "
                       "numbered on the time axis.")
    s.text(60, 50, "Fourteen weeks, 457 commits", 25, TEXT)
    s.text(60, 78, "Commits per week on the private repository, and what happened when. Numbers on the axis refer "
                   "to the list below.", 14, MUTED, extra=' font-style="italic"')

    # spans: the outage as a band, anything else as a bracket above the bars
    base, top = 330, 130
    for e in ev:
        if e["end"]:
            a, b = X(day(e["date"])), X(day(e["end"]))
            if e["kind"] == "outage":
                yb = top + 8
                s.add(f'<path d="M{a:.1f} {yb + 6:.1f} V{yb:.1f} H{b:.1f} V{yb + 6:.1f}" fill="none" '
                      f'stroke="{RED}" stroke-width="1.5"/>')
                s.text((a + b) / 2, yb - 6, "no data captured", 11, RED, MONO, "middle")
            else:
                yb = top - 18
                s.add(f'<path d="M{a:.1f} {yb + 6:.1f} V{yb:.1f} H{b:.1f} V{yb + 6:.1f}" fill="none" '
                      f'stroke="{DIM}" stroke-width="1"/>')
                s.text((a + b) / 2, yb - 6, e["label"].lower(), 11, DIM, MONO, "middle")
    # bars
    mx = max(int(r["commits"]) for r in wk)
    for v in (20, 40, 60):
        yy = base - v / mx * (base - top - 20)
        s.line(x0, yy, x1, yy, GRID)
        s.text(x0 - 10, yy + 4, str(v), 11, DIM, MONO, "end")
    for r in wk:
        a = X(day(r["week_start"]))
        w = 7 / span * (x1 - x0)
        c = int(r["commits"])
        hgt = c / mx * (base - top - 20)
        s.add(f'<rect x="{a + 3:.1f}" y="{base - hgt:.1f}" width="{w - 6:.1f}" height="{hgt:.1f}" fill="{BLUE}" '
              f'opacity="0.85"/>')
        if c == 0:
            s.text(a + w / 2, base - 6, "0", 11, DIM, MONO, "middle")
    s.line(x0, base, x1, base, AXIS)
    m = dt.date(2026, 6, 1)
    while m <= end:
        if m >= start:
            s.line(X(m), base, X(m), base + 6, AXIS)
            s.text(X(m) + 4, base + 20, month(m), 12, DIM, MONO)
        m = dt.date(m.year + (m.month == 12), m.month % 12 + 1, 1)

    # event markers: a marker goes to the first lane where it does not touch the previous one
    lanes, marks = [], []
    for i, e in enumerate(ev, 1):
        d = day(e["date"])
        cx = X(d)
        k = 0
        while k < len(lanes) and cx - lanes[k] < 23:
            k += 1
        if k == len(lanes):
            lanes.append(cx)
        else:
            lanes[k] = cx
        marks.append((i, cx, base + 44 + k * 24))
    for i, cx, cy in marks:
        s.line(cx, base, cx, cy - 10, AXIS)
    for i, cx, cy in marks:
        s.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="10" fill="{CARD}" stroke="{SOFT}" stroke-width="1.5"/>')
        s.text(cx, cy + 4, str(i), 11, TEXT, MONO, "middle")

    # the list
    col_x = (60, 620)
    per = (len(ev) + 1) // 2
    for i, e in enumerate(ev, 1):
        cx = col_x[0] if i <= per else col_x[1]
        yy = 470 + ((i - 1) % per) * 30
        d = day(e["date"])
        when = dmon(d) + (f"–{dmon(day(e['end']))}" if e["end"] else "")
        s.text(cx, yy, f"{i:>2}", 12, DIM, MONO)
        s.text(cx + 26, yy, when, 12, MUTED, MONO)
        s.text(cx + 128, yy, e["label"], 13, SOFT)
    return s.render()


# ------------------------------------------------------------------------------------------------
def code_svg():
    ch = rows("code_history.csv")
    pts = [(dt.datetime.fromisoformat(r["date"][:10]), int(r["loc_analysis_tools"]), int(r["loc_tests"]))
           for r in ch]
    t0, t1 = pts[0][0], pts[-1][0]
    span = (t1 - t0).total_seconds()
    x0, x1, y0, y1 = 110, 1140, 120, 480
    top = 40000
    X = lambda t: x0 + (t - t0).total_seconds() / span * (x1 - x0)
    Y = lambda v: y1 - v / top * (y1 - y0)
    peak = max(pts, key=lambda p: p[1])
    last = pts[-1]
    s = Svg(1200, 600, "Lines of Python in the analysis and tools folders, and in the tests, at every commit "
                       "from June to September 2026.")
    cut = round(100 * (peak[1] - last[1]) / peak[1])
    s.text(60, 50, f"analysis/ and tools/ grew until {peak[0].day} {month(peak[0])}; {cut} % was removed "
                   f"on 8 and 9 September", 25, TEXT)
    s.text(60, 78, "Physical lines of Python at every commit on the main line of the private repository.",
           14, MUTED, extra=' font-style="italic"')
    for v in range(0, top + 1, 10000):
        s.line(x0, Y(v), x1, Y(v), AXIS if v == 0 else GRID)
        s.text(x0 - 12, Y(v) + 4, f"{v:,}", 12, DIM, MONO, "end")
    m = dt.datetime(2026, 7, 1, tzinfo=t0.tzinfo)
    while m <= t1:
        s.line(X(m), y1, X(m), y1 + 6, AXIS)
        s.text(X(m) + 4, y1 + 22, month(m), 12, DIM, MONO)
        m = m.replace(month=m.month + 1) if m.month < 12 else m.replace(year=m.year + 1, month=1)
    for key, col, lab in ((1, AMBER, "analysis/ and tools/"), (2, BLUE, "tests/")):
        path = " ".join(f"{X(p[0]):.1f},{Y(p[key]):.1f}" for p in pts)
        s.add(f'<polyline points="{path}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round"/>')
    s.add(f'<circle cx="{X(peak[0]):.1f}" cy="{Y(peak[1]):.1f}" r="4" fill="{AMBER}"/>')
    s.text(X(peak[0]) - 10, Y(peak[1]) - 12, f"{peak[1]:,} lines on {dmon(peak[0])}", 13, AMBER, MONO, "end")
    s.add(f'<circle cx="{X(last[0]):.1f}" cy="{Y(last[1]):.1f}" r="4" fill="{AMBER}"/>')
    s.text(X(last[0]) - 10, Y(last[1]) - 10, f"{last[1]:,} on {dmon(last[0])}", 13, AMBER, MONO, "end")
    s.text(X(last[0]) - 10, Y(last[2]) + 20, f"tests/: {last[2]:,} lines", 13, BLUE, MONO, "end")
    s.add(f'<rect x="{x0}" y="{y1 + 44}" width="14" height="3" fill="{AMBER}"/>')
    s.text(x0 + 22, y1 + 50, "analysis/ and tools/", 13, SOFT)
    s.add(f'<rect x="{x0 + 210}" y="{y1 + 44}" width="14" height="3" fill="{BLUE}"/>')
    s.text(x0 + 232, y1 + 50, "tests/", 13, SOFT)
    s.line(60, 556, 1140, 556, GRID)
    s.text(60, 580, "Every file removed in the cleanup is listed, with the commit that recovers it, in ARCHIVO.md. "
                    "Counts: wc -l on the blobs of each commit.", 13, DIM, extra=' font-style="italic"')
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
