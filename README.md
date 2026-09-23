<p align="center">
  <img src="assets/banner.svg" alt="quant-system: a one-person research programme on crypto perpetual-futures microstructure, June to September 2026. It found no trading edge." width="100%">
</p>

<p align="center">
  <a href="https://github.com/Lostmanu/quant-system/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Lostmanu/quant-system/ci.yml?branch=main&style=flat-square&labelColor=12161C&label=six%20checks%20in%20CI" alt="status of the six CI checks"></a>
</p>

<p align="center">
  <a href="docs/DICTAMEN_MESA_2026-09-07_I5_D1_79.md">The ruling</a> ·
  <a href="docs/AUDITORIA_DEL_METODO.md">Register of 93 false claims</a> ·
  <a href="https://github.com/Lostmanu/ninety-three-wrong-claims">The paper</a> ·
  <a href="docs/README.md">English map of the record</a> ·
  <a href="#limits">Limits</a> ·
  <a href="CITATION.cff">Cite</a>
</p>

> [!NOTE]
> **Status: closed.** The research stopped on 9 September 2026 at commit `93f3e35` of the private
> repository, and this copy was published on 22 September 2026. The research and the code are frozen;
> only the publication files listed in [`MANIFEST.md`](MANIFEST.md) change.

I looked for a trading edge in crypto perpetual futures between June and September 2026 and did not
find one. The programme's headline estimate, +18.24 basis points per filled order on the Lighter LIT
perpetual, was invalidated as a confirmatory result on 26 August 2026 and withdrawn as evidence of an
edge on 7 September, after a post hoc re-analysis also counted the orders that vanished while trades
printed both at and through their price, which brought it down to +2.575. The programme ran to 457
commits, and the withdrawal needed a rebuild of 79 days of order-book data from re-acquired files, which
matched the original run on all 632 recorded numbers.

This repository is the laboratory as it stood when it closed: the code that survived the final
cleanup, 476 tests, six checks that run on every push, and the written record of what was tried and
decided, mostly in Spanish. It contains no market data, so the result cannot be re-run from here; the
tests and the checks can. Most of the code was written and audited by AI agents under a protocol I set
up, and [How it was built](#how-it-was-built) says who did what. The companion repository
[ninety-three-wrong-claims](https://github.com/Lostmanu/ninety-three-wrong-claims) holds a paper on the
register of false claims the programme kept.

## The question

Can a small participant with no speed advantage earn a lasting edge in crypto perpetual futures?

The programme worked through eight lines of inquiry before it closed. The record gives each a verdict,
and only one of the six Binance fronts spent held-out data
([`LEDGER.md` 30](docs/LEDGER.md?plain=1#L30)).

| # | line of inquiry | data | how it ended | source |
|---|---|---|---|---|
| 1 | three service premia: provision, execution against order flow, funding carry | Binance recordings and downloaded history | three screens, all negative | [`LEDGER.md` 31](docs/LEDGER.md?plain=1#L31) |
| 2 | cross-venue lead, Binance to Bybit | Binance, Bybit | a lead of about 50 ms: a speed game, archived | [`LEDGER.md` 32](docs/LEDGER.md?plain=1#L32) |
| 3 | fading extreme order-flow imbalance | eight thin Binance perpetuals, held-out | −10.71 bps per event after costs, t −26 | [`LEDGER.md` 33](docs/LEDGER.md?plain=1#L33) |
| 4 | liquidation cascades | Binance perpetuals | inconclusive: the condition occurred in 0.57 % of cases, under the 1 % floor | [`LEDGER.md` 36](docs/LEDGER.md?plain=1#L36) |
| 5 | cross-asset lead-lag | Binance perpetuals | null, D = −0.026, in the opposite direction | [`LEDGER.md` 37](docs/LEDGER.md?plain=1#L37) |
| 6 | the window after a new listing | new Binance listings | closed on a low prior: market makers were in the book from the first minute | [`LEDGER.md` 39](docs/LEDGER.md?plain=1#L39) |
| 7 | passive quoting on Hyperliquid | one day of Hyperliquid books | failed its first layer: 6 candidate symbols against a floor of 30 fixed in advance | [`ARCO.md` 40](docs/testigos/ARCO.md?plain=1#L40) |
| 8 | patient resting orders on Lighter | Lighter order-level archive, 79 days | +18.24 bps, formally inconclusive; withdrawn on 7 September | [`LEDGER.md` 1681](docs/LEDGER.md?plain=1#L1681) |

On Lighter, a taker idea died first, and a maker idea then went through a screen, a simulated maker, a
pilot, an atlas of wallets and the confirmation test before the +18.24 appeared. The programme's own attack letter counts
about ten attempts in all and says no statistical correction spans them
([`CARTA_DE_ATAQUE.md` 12](docs/testigos/CARTA_DE_ATAQUE.md?plain=1#L12)).

## How a fill was inferred

<p align="center" id="figure-1">
  <img src="assets/measurement.svg" alt="Diagram: a resting bid at price p followed across two order-book snapshots, five of the things that can happen between them, and which of them the July rule and the wider rule count as fills." width="100%">
</p>

**Figure 1.** Five of the cases the July code distinguished for a resting order between two snapshots,
and which of them each rule counts as a fill. Drawn by hand from the rule as coded in July.

The programme never placed an order. It followed other participants' orders through a commercial
archive of Lighter's order book and matched them with the trades printed between snapshots.

| | |
|---|---|
| venue and instrument | Lighter LIT perpetual; standard accounts paid no trading fees at the time |
| order data | order-level snapshots about 2.9 minutes apart, from a commercial archive |
| trade data | trade files without order ids, so a fill had to be inferred |
| sample | 79 days with data between 6 March and 29 June 2026 |
| cohort | slow orders: seen in an earlier snapshot, so they had rested at least one full interval |
| regime | the agitated third of trailing 20-minute volatility |
| horizons | 1, 5, 10, 25 and 60 s; 5 s was the primary horizon of the re-analysis, 25 s the headline cell |
| reference price | the nearest trade on Binance's LIT perpetual; the preregistration asked for the mid price |
| orders placed | none |

A fill was scored as a markout, `side × (reference − p) / p × 10,000` basis points, with side +1 for a
bid and −1 for an ask, the reference taken at the fill time plus the horizon, and the fill time at the
first trade at p (for through events, the first trade below it). Over the 79 days there were 132,876
slow-order events with a trade at or through the order's price; cancellations are not among them. The
July rule counted 13,368 of them as fills (10.1 %) and the wider rule 115,302 (86.8 %).

**Why the rule mattered.** On 6 July, one day after the +18.24, an internal audit added a passage to the
programme's attack letter. It named the third row of Figure 1, called through-with-at below: an order
that fills in an interval where the price also trades through it is set aside, and because a trade
through the price goes with a later move against the order, setting those orders aside pushes the mean
up. The letter made a sensitivity test mandatory, and expected the affected orders to be a minority
whose return would shrink the mean without turning it negative
([`CARTA_DE_ATAQUE.md` 100-115](docs/testigos/CARTA_DE_ATAQUE.md?plain=1#L100)). The test ran on
7 September. The orders it added were 101,934, three quarters of the slow-order events, and at the
5-second primary horizon the mean changed sign.

## What happened to the positive result

<p align="center" id="figure-2">
  <img src="assets/result.svg" alt="Per-day markouts at 25 seconds for 79 days under the July rule and the wider rule, with the means +18.24 and +2.575, and the mean at five horizons under both rules." width="100%">
</p>

**Figure 2.** Left: each day's mean markout at 25 seconds under the two rules, days in date order (79
of the 116 calendar days had data). 1 May, at +223, is drawn at the top of the scale; it is the day
with the one zero-price reference at 25 seconds. Right: the mean at each horizon, each averaged over its
own events; at 5 seconds three invalid references pull the July-rule mean from +10.38 to +2.61.
Post hoc diagnostic, run once on 7 September 2026. Data:
[`d1_per_day_25s.csv`](assets/figures/data/d1_per_day_25s.csv), from the run whose hash is recorded in the
[ruling](docs/DICTAMEN_MESA_2026-09-07_I5_D1_79.md?plain=1#L27); drawn by
[`make_figures.py`](assets/figures/make_figures.py) and checked against its data on every push.

On 5 July 2026 the preregistered confirmation test gave +18.24 bps at 25 seconds for slow orders in the
most volatile third of the sample (t +6.69, 79 days). The same test required the 5-second horizon to
agree, and it did not (+2.61, t +0.29), so its formal verdict was inconclusive
([`LEDGER.md` 1681](docs/LEDGER.md?plain=1#L1681)). The estimate was withdrawn in three steps.

1. On 24 August an adversarial checklist, frozen on 13 June when the finding did not yet exist, was run
   against it for the first time, by AI agents working one threat each. It returned DESTROYED, with all 8
   of its threats applying ([report](docs/AUDITORIA_QUANT_REVIEWER_2026-08-24.md),
   [checklist](.claude/agents/quant-reviewer.md)).
2. On 26 August the markout pipeline was found to accept reference prices of zero. Dropping the one
   affected fill in the headline cell moved it from +18.24 to +15.60 and its effective n from 79 to 14.7,
   and the incident report invalidated the +18.24 as a confirmatory result without putting another figure
   in its place ([incident](docs/INCIDENTE_2026-08-26_REF_INVALIDA.md)).
3. On 7 September the 79 days were rebuilt, the July number came back exactly, and the re-analysis
   counted the through-with-at orders. Among slow-order events with a trade at or through the order's
   price, the share admitted as fills went from 10.1 % to 86.8 %, and the 25-second mean fell to +2.575.

| horizon and reference | July rule (bps) | wider rule (bps) | paired difference (bps) | descriptive t |
|---|---:|---:|---:|---:|
| 5 s, July reference | +2.6101 | −1.0843 | −3.6944 | −0.5505 |
| 5 s, validated reference | +10.3795 | −0.0976 | −10.4772 | −13.4025 |
| **25 s, July reference** | **+18.2368** | **+2.5750** | **−15.6618** | **−6.9043** |
| 25 s, validated reference | +15.6036 | +1.4988 | −14.1048 | −9.8270 |

The validated reference drops events whose reference or fill price is not a finite positive number, or
whose markout reaches 9,000 bps in absolute value, which is the correction for the 26 August defect.

The [ruling](docs/DICTAMEN_MESA_2026-09-07_I5_D1_79.md) withdrew the +18.24 as evidence of a tradable
edge, kept the +2.575 on the record without calling it profit, and left in place the standing halt on
production and trading. The re-analysis had fixed 5 seconds as its primary horizon, and there the paired
difference has t −0.55, so the withdrawal rests on the 25-second rows. It was also decided after the
result was known. The reference price was the nearest Binance trade, where the preregistration had asked
for the mid price. And fast orders scored +11.78 bps under the July rule as well, so the effect was never
specific to slow orders.

## Timeline

<p align="center" id="figure-3">
  <img src="assets/timeline.svg" alt="Commits per week from June to September 2026, with thirteen numbered events on the time axis, listed in the table below." width="100%">
</p>

**Figure 3.** Commits per week in the private repository, with the events below numbered on the time
axis. Data: [`commits_per_week.csv`](assets/figures/data/commits_per_week.csv) and
[`timeline.csv`](assets/figures/data/timeline.csv); drawn by
[`make_figures.py`](assets/figures/make_figures.py).

| # | date | event | source |
|---:|---|---|---|
| 1 | 12 Jun | Repository created; Binance collector starts recording | git log (first commit c6f1c9e); collector start is logged in a private build diary |
| 2 | 13 Jun | Adversarial checklist written and frozen, never edited again | [`quant-reviewer.md`](.claude/agents/quant-reviewer.md) |
| 3 | 1 Jul | Six ideas screened on Binance; no edge for a slow trader | [`LEDGER.md` 23](docs/LEDGER.md?plain=1#L23) |
| 4 | 5 Jul | Lighter LIT: +18.24 bps at 25 s, formally inconclusive | [`PREREG_CONFIRMACION_LIT.md`](docs/PREREG_CONFIRMACION_LIT.md); [`LEDGER.md` 1681](docs/LEDGER.md?plain=1#L1681) |
| 5 | 6 Jul | Attack letter names the through-with-at weakness | [`CARTA_DE_ATAQUE.md` 100](docs/testigos/CARTA_DE_ATAQUE.md?plain=1#L100) |
| 6 | 6 Jul–6 Sep | Ledger silent for two months | [`LEDGER.md` 1820](docs/LEDGER.md?plain=1#L1820) |
| 7 | 17 Jul | A hardened results log begins; 59 commits, deleted 9 Sep | git log -- quant-system-ingesta/qs/analysis/eco_libro_tx.py (7ff4822 to d15cf94, deleted in ac165b9); [`ARCHIVO.md` 107](ARCHIVO.md?plain=1#L107) |
| 8 | 13 Aug–22 Aug | Unpaid hosting bill: no capture from 13 Aug 08:57 to 22 Aug 20:15 | [`AUDITORIA_DEL_METODO.md` 140](docs/AUDITORIA_DEL_METODO.md?plain=1#L140) |
| 9 | 24 Aug | June checklist run on the finding: destroyed, 8 of 8 | [`AUDITORIA_QUANT_REVIEWER_2026-08-24.md` 28](docs/AUDITORIA_QUANT_REVIEWER_2026-08-24.md?plain=1#L28) |
| 10 | 26 Aug | Zero-price references found in the markout pipeline | [`INCIDENTE_2026-08-26_REF_INVALIDA.md`](docs/INCIDENTE_2026-08-26_REF_INVALIDA.md) |
| 11 | 7 Sep | 79 days rebuilt from new data; 632 of 632 numbers match | [`LEDGER.md` 2249](docs/LEDGER.md?plain=1#L2249) |
| 12 | 7 Sep | Wider fill rule: +18.24 falls to +2.575; withdrawn | [`DICTAMEN_MESA_2026-09-07_I5_D1_79.md` 57](docs/DICTAMEN_MESA_2026-09-07_I5_D1_79.md?plain=1#L57) |
| 13 | 9 Sep | Code cut to 5,933 lines on 8-9 Sep; closing ruling | [`DICTAMEN_MESA_2026-09-09_V2_CIERRE.md` 31](docs/DICTAMEN_MESA_2026-09-09_V2_CIERRE.md?plain=1#L31) |

The ledger has no entry between 6 July and 6 September, a stretch of 248 commits. Fifty-nine of them
went into a hardened log for recording results, which was deleted in September. From 13 to 22 August
nothing was captured, because a hosting bill had not been paid.

## The checks

<p align="center" id="figure-4">
  <img src="assets/checks.svg" alt="The six CI steps, what each checks and the failure or review behind it; one of them cannot fail today." width="100%">
</p>

**Figure 4.** The six steps of [`ci.yml`](.github/workflows/ci.yml), each with the failure or review that
added it. Drawn by hand. None of these steps looks at an estimate: the +18.24 was withdrawn by a
checklist review, an incident report and a post hoc re-analysis, none of which runs in CI.

```bash
git clone https://github.com/Lostmanu/quant-system
cd quant-system/quant-system-ingesta/qs
pip install -r requirements-test.txt -c requirements-lock.txt

python -m pytest tests/ -q                    # 476 passed
python tools/mutacion_ref_valida.py           # 49/49 rows bite
python tools/guardia_documental.py            # preregistration dates, spec against code
python tools/guardia_completitud.py           # numpy I/O only where it is wrapped
python tools/registro_sonda.py                # probe registry (empty)
python tools/recuento_auditoria.py --check    # register count is current
```

On its last two runs in GitHub Actions (Ubuntu, Python 3.12.14) the whole job took 68 and 72 seconds:
about 13 for installing, 13 for the 476 tests, 35 for the mutation harness and under a second for each of
the four guards.

Each of the harness's 49 rows disables a guarded check, in the guard tools themselves or in
`analysis/` and `ingestion/`, and passes only if a named test fails with the marker declared for it. A
red test is not enough, because a test can fail for an unrelated reason. On its first run the harness
found two defects in the shared code it was built on: the regular expression that parsed pytest failures
missed parametrised test ids, and the function that judged the results counted them as collateral
failures ([`ci.yml` 34](.github/workflows/ci.yml?plain=1#L34)).

<details>
<summary>What the harness prints (CI run 35822218188, excerpt)</summary>

```text
49 mutaciones · copia nueva para cada una · 67 ficheros vigilados
pre-vuelo sobre las 49 filas: OK
  linea base (sin mutar): 111 passed, 153 deselected in 1.19s
  linea base VERDE y valida: 111/55 tests, rc=0
  los 55 tests declarados EXISTEN en la coleccion
  ROJO ✓                                 R1 quitar el rechazo de NO FINITA (NaN / +-inf pasan a ser markouts)
                                         asigna_la_clase_correcta→assert
  ROJO ✓                                 CENSO: aceptar la compuerta dentro de una RAMA (un `except` que se la traga)
                                         compuerta_que_NO_domina→assert
  ...
49/49 comprobaciones MUERDEN con su marcador o fragmento declarado
  LIMITES, y son los mismos que los del arnes hermano:
   · acredita la SENSIBILIDAD de los tests, NO la CORRECCION del codigo.
   · cada mutacion corre con `-k` sobre SUS tests declarados: un test no seleccionado que
     la mutacion rompiera seria invisible aqui. No se afirma que no exista.
```

In English: 49 mutations, each on a fresh copy of the tree; the unmutated baseline passes; every row
turns its named tests red with the declared marker. The harness then states its own limits: it shows
that the tests are sensitive to these changes, not that the code is correct, and a test outside a row's
selection that the mutation would break is not seen.

</details>

One of the six steps cannot fail at present: the probe registry is empty, and an empty registry passes.
Half of the documentation guard is in a similar position. Its chronology check exempts six of the seven
preregistrations as older than its rule, and the seventh declares two artefacts that do not exist yet,
so there is nothing to date. Its other half checks that four rules declared as implemented still name a
function or constant in `ref_valida.py`.

## The code, and what was removed

<p align="center" id="figure-5">
  <img src="assets/code.svg" alt="Lines of Python in analysis and tools, and in tests, at every commit from June to September 2026." width="100%">
</p>

**Figure 5.** Lines of Python (`wc -l`) under `analysis/` with `tools/`, and under `tests/`, at each of
the 455 commits on the main line of the private repository. Data:
[`code_history.csv`](assets/figures/data/code_history.csv); drawn by
[`make_figures.py`](assets/figures/make_figures.py).

The cleanup of 8 and 9 September retired the modules that only closed studies used. `analysis/` and
`tools/` went from 36,946 to 5,933 lines, and the CI suite from 2,023 tests to 476
([closing ruling](docs/DICTAMEN_MESA_2026-09-09_V2_CIERRE.md)). Each removed file is listed in
[`ARCHIVO.md`](ARCHIVO.md) with the commit that recovers it. What is left in `analysis/` is the
reference validator with its artefact and lane layers, which the mutation harness guards; a set of
tested libraries (purged and embargoed cross-validation, PSR, DSR and PBO, multiple-testing haircuts,
bars, toxicity, regimes, cross-section, venue adapters), most of which no code outside the tests calls
any more; and four download scripts without tests.

## What is where

```text
.
├── README.md                   this page
├── ARCHIVO.md                  every file retired on 8-9 September, with the commit that recovers it (Spanish)
├── EXCLUIDO.md                 the 171 original files not copied here, by category (Spanish)
├── MANIFEST.md                 SHA-256 of the 173 copied files (Spanish)
├── CITATION.cff
├── .claude/agents/
│   └── quant-reviewer.md       the adversarial checklist frozen on 13 June; kept because it is evidence
├── .github/workflows/
│   ├── ci.yml                  the six checks
│   └── figures.yml             the charts against their data
├── assets/                     the six figures; figures/ holds make_figures.py and its CSV files
├── docs/                       the record: ledger, preregistrations, rulings, incidents, audits
│   ├── README.md               an English map of every document, with a glossary
│   ├── testigos/               the attack letter, the sanitisation act, the story of June and July
│   └── inventarios/            machine-readable inventories of the cleanup
├── infra/lighter_collector/
│   └── collector.py            the Lighter collector that ran on the server
└── quant-system-ingesta/qs/    the original layout, kept so the hashes and links in the record resolve
    ├── ingestion/              the Binance collector: websocket feed, order book, writer, audit
    ├── analysis/               reference validation, artefacts, lanes, statistics libraries, adapters
    ├── tools/                  the guards, the mutation harness, the pre-flight, the register counter
    ├── tests/                  476 tests
    ├── config/                 instrument list
    └── docs/                   work orders and run receipts that the record links to
```

## Reading the record

The record is in Spanish. [`docs/README.md`](docs/README.md) maps every document in English and has a
glossary of the terms that appear in file names. A reader with an hour could take them in this order:

1. [`RESEARCH_BRIEF.md`](docs/RESEARCH_BRIEF.md), in English: what the programme set out to do.
2. [`testigos/ARCO.md`](docs/testigos/ARCO.md): the story of June and July, chapter by chapter, with commits.
3. [`PREREG_CONFIRMACION_LIT.md`](docs/PREREG_CONFIRMACION_LIT.md): the test that produced the +18.24.
4. [`testigos/CARTA_DE_ATAQUE.md`](docs/testigos/CARTA_DE_ATAQUE.md): the eleven strongest attacks on the programme, written by the programme; docs/README.md has an English summary.
5. [`AUDITORIA_QUANT_REVIEWER_2026-08-24.md`](docs/AUDITORIA_QUANT_REVIEWER_2026-08-24.md): the checklist review.
6. [`DICTAMEN_MESA_2026-09-07_I5_D1_79.md`](docs/DICTAMEN_MESA_2026-09-07_I5_D1_79.md): the re-analysis and the ruling.
7. [`AUDITORIA_DEL_METODO.md`](docs/AUDITORIA_DEL_METODO.md): the register of 93 false claims.

## Lessons, with dates

1. The adversarial checklist was frozen on 13 June and first run against the finding on 24 August, ten
   weeks after it was written and seven after the finding. It returned DESTROYED
   ([report](docs/AUDITORIA_QUANT_REVIEWER_2026-08-24.md)).
2. The weakness that decided the withdrawal was written down on 6 July in the programme's own attack
   letter, and the test that measured it ran on 7 September
   ([`CARTA_DE_ATAQUE.md` 100](docs/testigos/CARTA_DE_ATAQUE.md?plain=1#L100)).
3. New checks were once placed after a CI step that had been red for three days, which meant GitHub
   would have skipped them without reporting. Every verification step now runs unless the job is
   cancelled ([`ci.yml` 21](.github/workflows/ci.yml?plain=1#L21)).
4. Data capture stopped from 13 to 22 August because a hosting bill went unpaid
   ([register, D-09](docs/AUDITORIA_DEL_METODO.md?plain=1#L140)). In the same weeks the engineering effort
   was going into the integrity of a results log, which was deleted in September.
5. The calculation of what the programme's goal would have required was written last, in
   [`feasibility_objetivo.py`](quant-system-ingesta/qs/tools/feasibility_objetivo.py), whose own
   docstring says it should have been the first.

## About this copy

This is a snapshot without history of the original repository at commit `93f3e35`, which stays
private. It has 173 of that repository's 344 files; [`EXCLUIDO.md`](EXCLUIDO.md) lists the other 171
by category, and [`MANIFEST.md`](MANIFEST.md) gives the SHA-256 of every file as exported. Server
addresses, account names, key locations and local paths were replaced by markers such as `<VPS_IP>` and
`<USER_HOME>` in 35 files, following a sanitisation act written on 5 July 2026
([`SANEAMIENTO.md`](docs/testigos/SANEAMIENTO.md)). One link, to a custody folder on my machine, points
outside the repository on purpose.

One of the 173 copied files has changed since the snapshot: two collector tests read the real disk and
failed on any machine whose temporary folder was more than 85 % full, so a fixture now reports the disk
to them as half full. Hashes and seals quoted inside the record refer to the private originals, so the
35 files with markers will not match them byte for byte.

Three of the figures (2, 3 and 5) are drawn from CSV files by
[`assets/figures/make_figures.py`](assets/figures/make_figures.py), and a second workflow fails if a
published chart no longer matches its data. [`assets/figures/data/README.md`](assets/figures/data/README.md)
says where each number comes from. The banner and Figures 1 and 4 are drawn by hand.

## How it was built

I chose the questions, paid for the data and signed the decisions. The code was written by AI agents.
Most commits carry the signature of Claude Code (Anthropic), 383 of 457. Codex (OpenAI) appears in the
record from late July, and by September it implemented while Claude Code audited and ran the long jobs.
A review role, called *la mesa* in the documents, issued the rulings. Another AI model filled it, Codex
in the September documents, and I signed the result, so the rulings are not independent reviews. The
agents account for part of the register of 93 false claims; the record does not attribute its entries to
a named person or system, and it records who or what caught each one.

## Limits

1. No edge was found, and nothing here supports a strategy. The repository documents how the search was
   run.
2. The trading result cannot be reproduced from this repository, which contains no market data.
3. The re-analysis that withdrew the estimate was post hoc, and the reference price in every branch of it
   departs from the preregistration.
4. There is one laboratory and one author, no second implementation and no control group.
5. No one outside the programme has reviewed the rulings.

## Licence

Code under [Apache 2.0](LICENSE), documents under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
To cite it, use [`CITATION.cff`](CITATION.cff).

Manuel Beardo Campo ·
[LinkedIn](https://www.linkedin.com/in/manuel-beardo-campo-804a9b201/) ·
[the paper](https://github.com/Lostmanu/ninety-three-wrong-claims)
