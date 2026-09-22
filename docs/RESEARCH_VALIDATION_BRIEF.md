# Research brief — validation methodology for the day-14 runner

*Focused follow-up to `RESEARCH_BRIEF.md`. We are about to build the orchestration layer that runs
our pre-registered hypotheses over the probe and reports verdicts. Before we code it, we want the
**honest aggregation/reporting methodology** for a panel of correlated assets over a SHORT,
non-stationary window. Be a hostile reviewer; tell us where we'd over-claim.*

---

## 1. Context

- 8 thin Binance USDT-M perps (AVAX, LINK, DOT, NEAR, ATOM, LTC, FIL, UNI). They **co-move
  strongly** (BTC-driven); liquidity shocks across them are **highly correlated in time**.
- A **14-day** probe of our own L2 (`@depth10@100ms`) + aggTrades. That is the test sample.
- Validation engine already built: **CPCV** (purge + embargo), **DSR**, **PBO**, **PSR**,
  effective-N, **MinTRL**, **BHY** haircut, meta-labeling, feasibility/latency gate.
- Three pre-registered hypotheses, each with a per-symbol or panel entry point:
  - **H1** (liquidity-shock anticipation, OFI/MLOFI), **H3** (liquidation cascades, OI clusters +
    market-factor neutralization), **H8** (selective liquidity provision, RiskAdverse maker sim,
    lower-bound PnL).
- We want to add two cross-cutting controls (already pre-registered, not yet coded):
  - **cross-shock regime dummy** = "≥3 of 8 symbols have OFI < P5 simultaneously";
  - **conditional latency** = degradation measured when `recv − event > P95` *and* the signal fires
    (latency is heavy-tailed and may be worst exactly at shocks; we have the double timestamp).

## 2. What the runner must do

Loop the 8 symbols × days, run H1/H3/H8 with the **frozen** criteria, apply the cross-cutting
controls, and produce ONE verdict report — **without over-claiming from 14 correlated, non-stationary
days.**

---

## 3. Questions (go deep)

1. **Regime-aware / adaptive CPCV when folds are NOT exchangeable.** Crypto has structural breaks;
   our 14 days may contain 0–2 cross-shock episodes that dominate. How do we keep CPCV honest when
   some folds are calm and one contains a market-wide deleveraging? Is "Adaptive CPCV" (weighting
   folds by regime similarity to OOS) real and sound? With so little regime variation in 14 days,
   how should REE/stability be reported so it is not falsely reassuring?

2. **Correlated cross-asset events and effective sample size.** Purge+embargo handle *temporal*
   leakage, but our 8 symbols share *contemporaneous* shocks. What is the right **effective N** when
   "events" cluster in time across symbols (a BTC dump fragilizes all 8 at once)? Should the unit of
   analysis be the panel/cross-section rather than per-symbol? How do practitioners avoid counting
   one market-wide event as 8 independent observations?

3. **Operationalizing the cross-shock regime.** Is "≥3/8 with OFI < P5 simultaneously" a sound
   regime definition, or is a PCA first component / BTC-return threshold / formal change-point (HMM)
   better? And how should it be USED — as a control covariate, a fold-stratification variable, or an
   exclusion? Which keeps the test honest without throwing away the events that matter most?

4. **Conditional latency test.** Best practice to test latency robustness when latency is
   heavy-tailed AND correlated with the signal (exchange congestion at shocks). Given our
   double-timestamp, how do we operationalize "the worst case is exactly when you most want to act"
   — beyond a uniform ×10 stress?

5. **What 14 days can HONESTLY conclude.** With a short, non-stationary window, when is a result a
   *screen* (worth continuing) vs a *verdict* (durable)? Minimum-sample guidance for these
   microstructure tests; how to report *calibrated* confidence and avoid the classic over-claim from
   a lucky short window. We would rather under-claim.

6. **e-values / anytime-valid for the hypothesis stream.** Concrete recipe to compose evidence
   across H1 → H3 → H8 (overlapping data, sequential): e-process per CPCV path (threshold 1/α = 20),
   e-HC for correlated streams, StepC for the final batch. How to integrate with our existing CPCV +
   per-hypothesis verdicts without double-counting.

---

## 4. What we want back

- A recommended **honest aggregation + reporting design** for a panel of correlated assets over a
  short non-stationary window: how to combine per-symbol results, the right effective-N, and how to
  present stability so it is not falsely reassuring.
- The soundest **cross-shock regime** definition and how to use it.
- The right **conditional-latency** operationalization.
- Calibrated guidance on **screen vs verdict** at N = 14 days.
- Citations; peer-reviewed vs practitioner. If the honest answer is "14 days can only ever be a
  screen for these hypotheses — do not report a verdict," say so plainly. We will believe it.
