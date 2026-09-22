# Research brief — H8 IO layer: simulating a passive maker from captured public feeds

*Focused follow-up to `RESEARCH_BRIEF.md`. Read it, then go deep on §4. Be a hostile reviewer:
the goal is an **honest** maker-fill reconstruction, not an optimistic one. Cite sources and point
us to reference implementations.*

---

## 1. The task

We are building the IO layer (`h8_io`) for a pre-registered hypothesis (H8): **selective liquidity
provision** as a small passive maker on 8 thin Binance USDT-M perpetuals (AVAX, LINK, DOT, NEAR,
ATOM, LTC, FIL, UNI). We have **no live order placement** — we must *simulate* a hypothetical
passive maker from our own captured public market-data feeds, and we must do it **honestly** (an
optimistic fill assumption would fabricate an edge that does not exist).

The science layer (`run_h8`) is already built and tested. It needs, per simulated fill:
`half_spread`, `adverse_markout` (own-impact-corrected), the OFI/toxicity signal, the quoting-level
size, and a queue-aware fill probability. The IO layer must produce these from raw feeds. **This
brief is about getting the IO methodology right.**

---

## 2. Exactly what data we have (the constraints)

Captured by us, validated (zero crossed books, zero update-id gaps):

- **L2 depth** — Binance `@depth10@100ms` snapshots: top-10 levels each side
  (`bid_prices/bid_volumes/ask_prices/ask_volumes` as length-10 arrays), plus `first_update_id`,
  `final_update_id`, `prev_final_update_id`, `event_ts_ms`, `recv_ts_ns`. **Snapshots, not
  order-by-order** — ~150 ms median spacing, bursty. We do NOT see individual order IDs or queue
  composition; only aggregate size per price level every ~100 ms.
- **aggTrades** — `price`, `qty`, `is_buyer_maker` (aggressor side: `True` ⇒ seller aggressed),
  `agg_trade_id`, `trade_ts_ms`, `event_ts_ms`, `recv_ts_ns`. aggTrades **aggregate** consecutive
  fills at the same price/side into one record.
- **Double timestamp** everywhere: `event_ts_ms` (matching engine) vs `recv_ts_ns` (our capture
  server). Measured feed latency ≈ 113 ms median, 265 ms p99.

Two separate feeds (depth and trades), each with its own sequence/timestamps. ~0.5 M depth
snapshots/symbol/day; 14-day probe.

---

## 3. What `h8_io` must do (and the honest hard parts)

For a hypothetical passive maker quoting size `Q` at the best (or near-best) level:

1. **Fill identification.** Decide which aggTrades would have filled our resting quote, on which
   side, at what price. Hard part: with snapshot (not order-by-order) data we cannot see our exact
   queue position; the naive assumption "every trade at our price fills us" is optimistic.
2. **Queue position & fill probability.** Estimate `P(fill | queue position)` causally from
   snapshots (volume-delta bookkeeping). Two regimes: deep queue (we are one of many → fills are a
   *subset*, discount needed) vs **solitude** (the level is nearly empty and we would be the
   dominant/only resting size → `P(fill) → 1`, and those fills are the toxic ones).
3. **Own-impact-corrected markout.** Adverse markout = move of a *reference mid* against our
   position over horizons {500 ms, 1 s, 5 s, 30 s, 5 min}. The naive `(bid0+ask0)/2` mid jumps
   discretely when a fill consumes the best level → it would make markout look negative *by
   construction*, overstating toxicity. We plan to use a weighted-mid (VWAP of k levels) or the
   post-fill mid.
4. **Trade→level mapping.** A single aggTrade can sweep multiple levels; reconstruct which resting
   levels it consumed from the book delta between adjacent snapshots.
5. **Feed alignment.** Reliably place each trade on the depth timeline (event-time) using update IDs
   / timestamps, so "trade T consumed level L at time t" is trustworthy.

---

## 4. Questions (go deep)

1. **Honest maker-fill simulation from public L2 + trades (no own orders).** What is the accepted
   methodology to simulate a passive maker's fills from a public feed? What are the standard
   optimism biases (front-of-queue assumption, ignoring cancellations, sweeping trades) and the
   accepted corrections? Is there a consensus "conservative fill model" for research backtests?

2. **Queue position from snapshot (not order-by-order) data.** Concrete bookkeeping to estimate our
   queue position and fill probability from `@depth@100ms` snapshots: the volume-delta /
   trade-vs-cancel decomposition between snapshots, handling multiple events inside one 100 ms gap,
   and the Rigtorp / Moallemi-Saglam style estimators. How wrong is it, and how to bound the error?

3. **The dual regime (deep queue vs solitude).** How should fill probability be modeled when the
   level is nearly empty and our quote is the dominant size (we *are* the book)? Evidence on the
   adverse-selection profile of fills in near-empty thin books.

4. **aggTrades decomposition & trade→level mapping.** Best practice to map an aggregated trade to
   the levels it consumed, using the depth delta between snapshots; pitfalls of `is_buyer_maker`;
   handling trades that occur between snapshots.

5. **Depth/trade feed alignment on Binance USDT-M.** Correct linkage of the `@depth` stream
   (`first/final/prev_final_update_id`) and the `aggTrade` stream (`agg_trade_id`), in event-time,
   so fills attach to the right book state. Known gotchas.

6. **Markout mechanics on irregular ~150 ms snapshots.** Best practice for multi-horizon markout
   (500 ms / 1 s / 5 s) when snapshots are irregular; weighted-mid vs post-fill mid vs micro-price;
   how to avoid the own-impact artifact rigorously.

7. **Reference implementations.** Open-source frameworks that already do queue-aware maker-fill
   simulation from L2 feeds (e.g., **hftbacktest**, nautilus_trader, Databento examples, Rigtorp's
   writings). Which are credible, which match our snapshot-data constraint, and what do they get
   right/wrong that we should copy or avoid?

---

## 5. What we want back

- A recommended **conservative fill model** we can implement from `@depth@100ms` + aggTrades, with
  the explicit assumptions and where it is optimistic/pessimistic.
- Concrete bookkeeping for queue-position / fill-probability estimation from snapshots.
- The right **markout reference price** and horizons to avoid the own-impact artifact.
- Reference implementations to study, with an honest note on their limitations for thin perps.
- Citations. Distinguish peer-reviewed from practitioner sources.

*If the honest conclusion is "you cannot reliably simulate maker fills from snapshot data and you
need order-by-order (L3) or your own live quoting to test H8 properly" — say so plainly. That is a
decision we need to make before building the IO, not after.*
