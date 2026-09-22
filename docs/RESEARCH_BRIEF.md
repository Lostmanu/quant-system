# Research brief — quant microstructure lab for thin crypto perps

*A self-contained brief for a deep-research assistant (Perplexity et al.). Read it, then go as
deep as you can on the questions in §7. Be a hostile reviewer, not a cheerleader: our goal is a
**real, durable edge**, and the fastest way there is for you to tell us where we are wrong.*

---

## 1. What we want from you

1. **Stress-test the whole approach.** Where is our reasoning weak, naive, or already-arbitraged?
2. **Surface edges we might be missing** — specifically in *thin / illiquid* crypto perpetuals
   (not BTC/ETH), reachable by a small player from a desktop + cheap VPS.
3. **Point us to literature, data sources, and practitioner evidence** that would sharpen or kill
   each hypothesis in §6.
4. **Give an honest verdict** on §7.8: is there plausibly a durable edge here at all, and if not,
   where should we redirect?

Cite sources. Distinguish peer-reviewed evidence from practitioner folklore. Flag capacity and
decay realities, not just "does the signal exist in-sample."

---

## 2. The project in one paragraph

We are building a disciplined research **laboratory** (not a bot first) to hunt for small but
durable inefficiencies in **thin Binance USDT-M perpetual futures** — AVAX, LINK, DOT, NEAR, ATOM,
LTC, FIL, UNI. The thesis: elite HFT ignores these names (too little capacity for them), so a
small, patient, *information-structural* (not speed-based) player might find corners they leave
alone. The product that matters is the **machine + the discipline** that can find and *validate*
an edge without fooling itself — and honestly conclude "nothing here" when that's the truth. We
follow López de Prado's *Advances in Financial Machine Learning* (AFML) plus a written constitution
of pre-registration and falsification rules.

---

## 3. The discipline (non-negotiable core)

- **Pre-registration.** Every hypothesis's prediction *and* falsification thresholds are frozen in
  a git commit (the hash is the date authority) **before** the test data exists. No tuning
  thresholds after seeing results.
- **Named-loser rule.** A hypothesis is only admitted if we can name *who is forced to lose money
  and cannot stop* (e.g., margin-driven liquidations, forced redemptions). No clear forced loser →
  it's a mirage, not an edge.
- **Anti-speed filter.** Any signal must survive a **latency ×10** stress test. If it dies when we
  act 10× slower, it was a speed game we cannot win — archive it.
- **Nested controls.** A signal must add predictive power *beyond* the obvious contemporaneous
  state (e.g., "the book is already thin"), or it is a tautology, not anticipation.
- **Causality everywhere.** All features are strictly-prior (no look-ahead); all thresholds use
  causal rolling/expanding estimates; the clock split is `event_ts` for labels (market truth) and
  `recv_ts` for the actionable information set + latency.
- **We have killed 4+ hypotheses honestly** (see §6). That is the machine working, not failing.

---

## 4. The unique data asset

A 14-day probe (live now on a VPS) capturing, for the 8 names:
- **L2 order book**: `@depth10@100ms` (top-10 levels each side, 100 ms snapshots). ~0.5 M
  snapshots/symbol/day, validated (zero crossed/locked books, zero update-id gaps).
- **aggTrades**: every aggressive trade with real aggressor side (`is_buyer_maker`).
- **Double timestamp** per record (`event_ts_ms` from the matching engine, `recv_ts_ns` at our
  capture server). Measured feed latency ≈ 113 ms median, 265 ms p99.
- Off-site backup (checksum-verified). Historical: 12 months of 5-min open interest +
  long/short ratios + funding, and 12 months of aggTrades.

Almost nobody records L2 microstructure *on these specific thin names*. That is our differentiated
input. We do **not** capture `@forceOrder` (liquidations) and Binance throttles that feed anyway.

---

## 5. The validation engine (already built, ~217 passing tests)

Built faithfully from AFML + Bailey/López de Prado + Harvey-Liu, no look-ahead, no scipy/pandas:
- **CPCV** (combinatorial purged cross-validation) with purge + embargo (embargo ≥ feature
  lookback), combinatorial backtest paths.
- **Deflated Sharpe Ratio**, PSR, expected-max-Sharpe (Euler-Mascheroni), effective N trials
  (for correlated trials), **MinTRL**, and **PBO** (probability of backtest overfitting, CSCV).
- **Multiple-testing haircut**: Bonferroni / Holm / **BHY (Benjamini-Hochberg-Yekutieli)**,
  non-linear Harvey-Liu haircut.
- **Meta-labeling**: triple-barrier + bet sizing (sigmoid of model confidence).
- **Feasibility gate**: clears-costs, supports-detection (MinTRL), latency-degradation,
  the §4.1 feasibility filter.
- An **acceptance gate (C7)**: a tradeable claim must clear CPCV φ≥9 backtest paths, DSR≥0.95,
  PBO≤0.10, BHY haircut t≥3.2, latency degradation ≤30%, meta-labeling F1 OOS≥IS.

---

## 6. The hypotheses and their honest status

| # | Idea | Forced loser | Status |
|---|------|--------------|--------|
| **H1** | The L2 book **anticipates its own liquidity evaporation** — order-flow toxicity + falling book resilience precede a spread blow-out / depth collapse. | The slow taker who crosses a degraded book. | **Pre-registered, machinery complete.** Predictor = **signed OFI / MLOFI** (Cont-Kukanov-Stoikov, multi-level) as imminent trigger; **VPIN** demoted to a slow *toxicity regime* variable; book resilience = rolling recovery half-life. Awaits the probe's L2 (day 14). |
| **H2** | Staking-hedge / cross-venue funding-depth channel. | — | **FALSIFIED** (first stage failed; correlation +0.13, wrong sign). |
| **H3** | **Liquidation cascades**: forced liquidations (price-insensitive market orders) hit a thin book → disproportionate impact → more liquidations. Predict adverse forward drift when the book is thin *and* price approaches an OI-estimated liquidation cluster. | The over-leveraged, margin-liquidated trader. | **Pre-registered, machinery complete.** Liquidation clusters estimated from OI + a fixed leverage model {10×,25×,50×,100×}, entry ≈ causal 24h VWAP. Now **also controls for the market factor** (BTC/basket beta) to avoid the H5 confound. Awaits day 14. |
| **H5** | Cross-sectional lead-lag (liquid → thin names). | — | **FAILED** the feasibility filter: residual cross-sectional structure was essentially **BTC beta** (D=−0.026). Death-criterion #1 fired → pivoted to single-name liquidity/toxicity. |
| **H6** | Liquidity provision around new-listing events (event study / RDD). | — | **Parked, data-gated** (needs historical L2 around many listings; n likely binding). |
| **H7** | On-chain **forced supply** (Cosmos unbonding, 21-day, with a known completion date) leaves a tradeable footprint on the perp (funding / depth). | The unbonding whale forced to wait then (maybe) sell. | **Parked.** Make-or-break assumption "unbonding ≠ selling" is unverified; a 71-day public-RPC peek showed ~nothing; full-history data is gated (Flipside dead, Numia behind authorized views). |

**Strategic reframe after H5's death:** we increasingly doubt *direction prediction* (near-efficient)
and lean toward **"provide a better service"** — optimal execution, *selective* liquidity provision,
and harvesting structural premia (funding, etc.) with less risk. We want your view on whether that
reframe is right.

---

## 7. Open research questions (go deep here)

1. **Thin-perp edges specifically.** What persistent microstructure inefficiencies are documented
   in *illiquid* crypto perps (not BTC/ETH)? What is the realistic **capacity** and **decay
   half-life** of each? Which are practitioner folklore vs evidenced?

2. **OFI / liquidity-shock prediction.** State of the art on Order Flow Imbalance (Cont-Kukanov-
   Stoikov), multi-level OFI, and short-horizon liquidity-shock prediction in crypto perps. Is the
   `|OFI| → spread blow-out / depth collapse` link real *and* tradeable at ~100-300 ms latency, or
   does it collapse to a speed race? What improves it (deflation, regime conditioning, queue
   dynamics)?

3. **Liquidation-cascade prediction.** How valid is **estimating liquidation clusters from OI +
   leverage tranches** versus using actual liquidation prints? Known biases of OI-based estimates;
   the censoring/throttling of Binance `forceOrder`; better proxies (e.g., funding spikes, OI
   deleveraging signatures, exchange liquidation indices). Does the cascade edge survive once you
   neutralize the market-wide deleveraging factor?

4. **The "better service" reframe.** Evidence that **optimal execution**, **selective liquidity
   provision** (as a small maker in thin books), or **structural-premium harvesting** are more
   attainable for a small player than direction prediction. Where is the realized money, net of
   adverse selection and inventory risk?

5. **On-chain → CEX footprint (H7).** Does the literature support that on-chain *forced* flows
   (unbonding, unlocks, forced redemptions) leave a *tradeable* footprint on CEX perps? What is the
   empirical conversion rate of "unbonded/unlocked supply → actual selling"? Best data routes now
   that Flipside self-serve is dead and Numia is access-gated.

6. **Validation methodology gaps.** Beyond CPCV / DSR / PBO / BHY / meta-labeling, what are we
   missing for a **low-N, non-stationary, single-researcher** setting? Regime-aware CV? Sequential /
   alpha-spending testing across our hypothesis stream? Better controls for *time-series* (not iid)
   overfitting? Pitfalls specific to crypto's non-stationarity and structural breaks.

7. **Structural niche.** Which edges are *structurally* available to a desktop/VPS player
   (10-300 ms latency, small capital) precisely because elite HFT ignores thin names — and which
   look available but are mirages (they were speed all along)?

8. **Devil's advocate (most important).** Make the **strongest possible case that no durable edge
   exists** in this setup. If you had to bet, where would the one survivable edge be — and where are
   we wasting our time?

---

## 8. What we are NOT looking for

- Not direction-prediction hype, TA indicators, or "signals" without a named forced loser.
- Not anything that needs us to win a latency race against co-located HFT.
- Not in-sample backtest curiosities — only things with a credible mechanism, capacity, and a path
  through our acceptance gate (§5).
- Not get-rich-quick. We will believe every honest "no". The discipline is the point.

---

## 9. Hard constraints

- Capital: small (retail). Latency: ~100-300 ms from VPS to Binance. Capacity per name: tiny (the
  thin book is both the moat and the ceiling).
- We trade nothing until a hypothesis clears the C7 acceptance gate on out-of-sample, costed,
  latency-stressed, multiple-testing-corrected terms.

*If something here is wrong, say so plainly. A well-argued "this corner is empty, look there
instead" is worth more to us than a hopeful maybe.*
