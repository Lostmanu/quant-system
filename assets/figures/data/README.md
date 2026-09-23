# Where the numbers in the charts come from

`make_figures.py` draws `result.svg`, `timeline.svg` and `code.svg` from the files in this folder and
from nothing else. `python assets/figures/make_figures.py --check` fails if a published chart differs
from what these files produce, and a workflow runs that check on every push.

## d1_per_day_25s.csv

One row per day for the 79 days of the September re-analysis (6 March to 29 June 2026, Lighter LIT
perpetual, slow cohort, most volatile third): the day's mean markout in basis points under the July fill
rule (`H`), under the wider rule (`A`), their difference, and `n_H`, the number of July-rule markouts
that day.

They were copied from the run's output file `results.json`, key
`paired_contrasts['A-H|slow|agitado|25000']`, which is kept with the raw data outside
this repository. Its SHA-256, `1d19677326e1d2a8fa6137449d3543961d2d67fe638572846aeef61f3c54d8c6`, is the
anchor recorded at line 27 of [`DICTAMEN_MESA_2026-09-07_I5_D1_79.md`](../../../docs/DICTAMEN_MESA_2026-09-07_I5_D1_79.md).
Each daily value was also checked against the 79 daily receipts of the same run, with no difference.

The file reproduces the ruling: mean `H` 18.2368, mean `A` 2.5750, mean difference −15.6618
with t −6.9043, and `A` below `H` on 73 of 79 days.

The chart marks 1 May (`H` +223) as the day with the zero-price reference. The record does not name the
day, but it follows from its numbers. At 25 seconds there is one non-positive reference, and validating it
changes the mean by −2.6332 bps ([ruling](../../../docs/DICTAMEN_MESA_2026-09-07_I5_D1_79.md), lines
153-155), with t −1.00 over 79 days (RESULTADO_CODE_2026-09-07_I5_D1_79.md, line 70), which only one
changed day can produce. That day's mean therefore moved by 79 × 2.6332 = 208.02 bps. A zero reference
gives a markout of +10,000 bps on an ask. On 1 May the run recorded `n_H` = 48 markouts; removing one
+10,000 from them changes that day's mean by exactly 208.02. No other day comes within 4 bps of that
figure: the next closest, with 50 markouts, gives 203.91.

These are daily averages of inferred markouts. The programme publishes summary statistics of its own
analysis like these, and keeps out anything closer to market data, such as per-symbol volatility, trade
counts, volumes or spreads.

## horizon_curve.csv

The mean at 1, 5, 10, 25 and 60 seconds under both rules for the same cohort and tercile, each level on
its own days, transcribed from lines 107-108 of
[`RESULTADO_CODE_2026-09-07_I5_D1_79.md`](../../../docs/RESULTADO_CODE_2026-09-07_I5_D1_79.md).

## code_history.csv

For each of the 455 commits on the first-parent line of the original repository (the other 2 of the
457 came in through the one merge), from `c6f1c9e`
(12 June 2026) to `93f3e35` (9 September 2026): lines of Python under `qs/analysis/` and `qs/tools/`
together, lines under `qs/tests/`, and the number of `def test_` functions. Dates are given as days,
without the time of day. Lines are counted as
`wc -l` counts them, on the blobs of each commit, read with `git cat-file`. The counts reproduce the
figures the programme itself published: 36,946 at `408d368` and 5,933 at `ac165b9`
([closing ruling](../../../docs/DICTAMEN_MESA_2026-09-09_V2_CIERRE.md), lines 31-32).

## commits_per_week.csv

Commits on the main branch of the original repository per ISO week, 457 in total. Weeks start on
Monday.

## timeline.csv

The thirteen events in the timeline, each with the document that records it. The first event also
relies on a build diary that stayed in the private repository.
