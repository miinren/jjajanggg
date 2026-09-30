# Wave 4: book structure under realistic accounting

Research only; no trading. Data runs 2020-03-15 to 2025-12-31, and the 2026 holdout was not touched.

**Accounting (every number in this report):**
- simple returns;
- positions drift between trades;
- W06 BTC-hedge band of 0.03;
- **BTC funding paid or received on the hedge** (new; see "Engine" below);
- 8-clock average;
- costs of 5.5 bp, with 8 and 12 bp also reported.

**Method.**
- Pre-registered: see `PREREG.md` and `trials.csv`.
- 20 book trials, under the cap of 22.
- Every choice was made by pseudo-holdout: select on data before Y, test on year Y, for Y = 2023, 2024, 2025, then pool the three test years.

## Bottom line
1. **No structural change beats B-MV. The alt short leg is where the alpha is; the long leg is not.**
   - Long-only and reduced-short books all lose (full-sample t −1.6 to −3.0 vs B-MV).
   - A funding-carry short leg also loses (t −1.2 to −1.9).
2. **Wave 3c's attribution ("the short leg earns ~0, the money is in the long leg and the hedge") is a beta illusion.** Against BTC and ETH:
   - **B-MV short leg:** alpha +15.4 bp/day, t 4.3. Per $ short that is +28 bp/day, and +17.6 even against an equal-weight alt index.
   - **Long leg:** alpha −11.8 bp/day per $ long, t −2.5.
   - The long leg's raw +4 bp/day, and the hedge's +5.6, are bull-market beta. The short leg's raw return is low because it pays for that beta.
3. **The only change the pipeline picks is 8 longs instead of 12 (B-MV-N8).**
   - Pooled out of sample 2023–25: **SR 1.54 vs B-MV 1.46** (t_rm 1.14; not significant) **vs LIVE 0.78** (t_rm 3.08).
   - The score re-check keeps fw 0.25 / L 336 under the gated rule in every year.
4. **Recommendation.**
   - B-MV stays as the structure.
   - Use N=8 longs if you want the pipeline's pick; the extra edge is unproven.
   - Realistic live SR is about **0.8–1.2**.
5. **Pumped shorts (your question).** A short that is +20% against you keeps drifting against you on average. The evidence supports **covering at +20%**, which is the B-MV rule, not holding for a recovery. Details are in the last section.

## Engine and verification
`ext5.py` is `wave3c/ext4.py` plus four additions:
- per-leg funding;
- optional BTC funding on the hedge (the hedge is a perp, so it pays or receives funding like any position; ext4 ignored this);
- an optional separate short-ranking score;
- a short adverse-move event log.

Checks (`verify.py`, `verify3.py`):
- **(1) Matches ext4** when the new options are off: max diff 0.0.
- **(2) Reproduces Wave R's realistic B-MV+W06 SR of 1.490.**
- **(3) Synthetic 50/50 two-coin book with no costs:** the engine's compounded NAV matches buy-and-hold to **3e-9** over 341 eight-hour windows. This confirms that `simple=True, drift=True` is exact.

Adding hedge funding costs B-MV about 0.09 SR (1.490 → 1.405). B-MV's hedge is long BTC, which usually pays funding.

## Stage 1: structures (full sample, for context; selection is below)
| trial | book | SR 5.5 / 8 / 12 bp | net bp/d | long / short / hedge / funding bp/d | mdd@2% | worst yr | t vs B-MV (risk-matched) |
|---|---|---|---|---|---|---|---|
| ref | LIVE | 0.72 / 0.61 / 0.44 | 6.1 | 3.7 / −0.8 / 3.9 / 1.3 | −49 | −0.14 | −3.58 |
| T01 | long-only, 8 longs | −0.13 / −0.20 / −0.30 | −1.7 | 11.0 / – / **−12.0** / 1.2 | −104 | −2.26 | −2.48 |
| T02 | long-only, 12 longs | −0.28 / −0.33 / −0.42 | −3.7 | 9.2 / – / −12.3 / 1.0 | −132 | −2.26 | −2.78 |
| T03 | long-only, 20 longs | −0.46 / −0.51 / −0.59 | −6.2 | 7.3 / – / −12.9 / 1.0 | −168 | −2.26 | −3.01 |
| T04 | L/S, short_frac 0.20 | 0.20 / 0.10 / −0.05 | 1.7 | 7.4 / 0.8 / −5.9 / 1.1 | −80 | −1.03 | −2.37 |
| T05 | L/S, short_frac 0.35 | 0.88 / 0.73 / 0.51 | 5.6 | 6.1 / 1.4 / −1.0 / 1.2 | −47 | −0.30 | −1.57 |
| **T06** | **B-MV (sf 0.55)** | **1.41 / 1.24 / 0.98** | 10.7 | 4.2 / 2.2 / 5.6 / 1.3 | −35 | 0.55 | – |
| **T07** | **B-MV, 8 longs** | **1.57 / 1.40 / 1.12** | 12.0 | 5.0 / 2.8 / 5.7 / 1.4 | −34 | 0.56 | +1.95 (4/6 yrs) |
| T08 | carry shorts (prior-day funding), sf 0.55 | 1.12 / 0.91 / 0.59 | 8.3 | 4.2 / 0.0 / 5.4 / 1.9 | −70 | −0.58 | −1.19 |
| T09 | carry shorts, sf 0.35 | 0.66 / 0.48 / 0.21 | 4.1 | 6.1 / 0.0 / −1.1 / 1.6 | −58 | −0.56 | −1.87 |
| T10 | carry shorts (7-day funding), sf 0.55 | 1.07 / 0.93 / 0.70 | 8.0 | 4.2 / −0.6 / 5.3 / 1.4 | −65 | −0.53 | −1.34 |

**Pseudo-holdout selection** (`s1.txt`). The primary rule takes the best selection-window SR, but a challenger must also pass the risk-matched partition test vs B-MV on that window.

| window | primary (gated) pick | ungated pick | notes |
|---|---|---|---|
| < 2023 | B-MV | B-MV-N8 | N8 fails the gate on coin groups (3/5), t 1.29 |
| < 2024 | B-MV-N8 | B-MV-N8 | N8 t 1.71, 4/4 yrs |
| < 2025 | B-MV-N8 | B-MV-N8 | N8 t 2.09, 4/5 yrs |

- No long-only, reduced-short or carry structure passed the gate in any window.
- None was the best-SR structure in any window either.

## Stage 2: score re-check on B-MV-N8 (fw × L, `s2.txt`)
| L \ fw | 0 | 0.25 | 0.5 |
|---|---|---|---|
| 168 | 0.55 (t −4.2) | 0.81 (t −3.6) | 0.97 (t −2.3) |
| 336 | 0.85 (t −4.1) | **1.57 (default)** | 1.66 (t +0.3) |
| 720 | 1.23 (t −1.5) | 1.52 (t −0.2) | 1.92 (t +1.2, 4/6 yrs) |

- **Gated rule:** keeps the default in every window, since no alternative passes the partition test.
- **Ungated rule:** picks fw 0.5 in every window (L 336, 336, 720).
  - Pooled out of sample it scores SR 1.88 vs B-MV 1.46 (t_rm 1.77), but 2023 is 0.57 vs 1.05.
  - Turnover is 35% higher, so at 12 bp it is only 1.12 vs 0.99 (t 0.65).
  - **Not adopted.** It is the one lead worth re-checking on 2026.
- **Readings:**
  - A short idio window (168) is clearly worse.
  - **Dropping funding from the score (fw 0) wrecks the short leg:** raw −3.5 bp/day per $ short vs +5.0 at fw 0.25.

## Pooled out-of-sample result (2023–25; each year uses the pick made on earlier data only)
| | SR 5.5 bp | 8 bp | 12 bp | bp/day | yearly SR 2023 / 24 / 25 |
|---|---|---|---|---|---|
| **Pipeline pick** (B-MV in 2023, then B-MV-N8) | **1.54** | **1.34** | **1.03** | 10.9 | 1.05 / 1.94 / 1.54 |
| B-MV | 1.46 | 1.28 | 0.99 | 10.2 | 1.05 / 1.72 / 1.55 |
| LIVE | 0.78 | 0.65 | 0.44 | 5.6 | 1.08 / 0.97 / 0.48 |

- **Pick vs B-MV:** +0.66 bp/day risk-matched, t 1.14 (0.97 at 8 bp, 0.69 at 12 bp).
- **Pick vs LIVE:** +6.95 bp/day, t 3.08 (2.33 at 12 bp).
- **Ungated pipeline** (N8 every year): SR 1.61, t 1.87 vs B-MV.

**One-step check on N=8** (T19/T20):
- N=6: SR 1.55, t −0.18 vs N=8.
- N=10: SR 1.48, t −1.12.
- N=12 (B-MV): SR 1.41.

N=8 is on a mild plateau, not a spike.

## Long-leg economics (`diag.txt`, `diag2.txt`)
Regression of the daily leg P&L on daily BTC and ETH simple returns, optionally adding an equal-weight index of the liquid alts. t values are Newey-West.

| B-MV series | alpha bp/d (t), BTC+ETH | β BTC | β ETH | alpha bp/d (t), +ALT index |
|---|---|---|---|---|
| long leg, per $ long | **−11.8 (−2.5)** | 0.30 | 0.66 | −5.6 (−1.6) |
| long leg including its funding | −14.1 (−3.0) | | | −8.0 (−2.3) |
| short leg (0.55 gross) | **+15.4 (+4.3)** | −0.18 | −0.42 | +9.7 (+4.3) |
| hedge | +1.4 (1.4) | +0.20 | 0.02 | |
| whole book, pre-funding and pre-cost | +11.5 (3.7) | 0.16 | −0.10 | +8.7 (3.2) |

- **The low-vol long leg is beta, not a low-vol anomaly.**
  - Per $ it carries about 0.96 of BTC+ETH beta, and it underperforms that beta by about 12 bp/day.
  - It roughly matches the alt index (t −1.6).
  - In long-only form the 168h BTC hedge offsets the beta almost exactly (hedge β −0.93), and nothing is left: LO12's alpha vs BTC+ETH+ALT is 0.1 bp/day.
- **Why the raw legs mislead.**
  - The short leg carries more beta than the long leg, so B-MV's hedge is net *long* BTC. The hedge's "+5.6 bp/day" is BTC's 2020–25 drift.
  - Longs and the hedge collect market drift, and the short leg pays it. Only the short leg beats its beta.
  - **This is why long-only and reduced-short books fail: they remove the alpha and keep the beta.**
- **Funding** (B-MV, +1.34 bp/day in total):
  - longs pay −1.05;
  - shorts net of the hedge receive +3.03.
  - fw 0.25 already tilts longs toward cheap-funding names. Funding is about 13% of net P&L.
- **Is carry the real short-side edge? Partly, but not alone.** Per $ short, alpha vs BTC+ETH+ALT:

  | short leg | alpha bp/d (t) | raw price bp/d |
  |---|---|---|
  | idio + funding blend (B-MV) | +17.6 (4.3) | +4.1 |
  | pure carry | +13.8 (3.5) | 0.0 |
  | idio only (fw 0) | +9.6 (2.3) | −3.5 |

  Both ingredients carry alpha and the blend is best. As a stand-alone short leg, pure carry has worse drawdowns (−70% at 2% vol) and loses the book test.

## Realistic live expectations
- **Backtest:** B-MV(-N8) pseudo-OOS SR about 1.5 at 5.5 bp and about 1.0 at 12 bp.
- **Haircuts still to apply:**
  - stop-fill slippage (wave 3a: B-MV's edge over LIVE roughly halves at 2% slippage);
  - funding timing;
  - the size of the search programme.
- **Live expectation:**
  - **SR about 0.8–1.2 for B-MV or B-MV-N8, vs about 0.3–0.6 for LIVE.**
  - At 1.5x gross on $330 (about 2.2% daily vol), that is roughly **$7–12/month**.
  - Plan for **−35 to −50% drawdowns**.
- **For the 2026 holdout:** B-MV (N=12) vs B-MV-N8, with fw 0.5 as the one secondary lead.

## Pumped shorts: what to do about shorts that are deep underwater
Event study (`diag.txt`, `diag2.txt`):
- Setup: live rules with the short stop switched off, clock 0.
- Event: each short's first crossing of +X% against entry.
- Outcome: the coin's forward simple return (+ is bad for the short).

| adverse move | n | fwd 72h mean | fwd 7d mean | fwd 7d median | 7d beta-adjusted | P(another +20% within 72h) | t (72h, day-clustered) |
|---|---|---|---|---|---|---|---|
| any (≈ all shorts) | 3473 | −0.7% | −0.1% | −3.6% | −1.4% | 14% | −0.3 |
| +20% | 796 | **+3.3%** | +2.7% | −6.4% | +1.2% | 27% | 1.3 |
| +30% | 510 | **+6.3%** | +5.9% | −5.4% | +3.6% | 33% | 1.7 |
| +50% | 285 | +8.3% | +4.2% | −6.9% | +2.6% | 33% | 1.5 |
| +75% | 163 | +10.7% | +5.9% | −6.2% | +5.8% | 37% | 1.4 |
| +100% | 113 | +9.2% | +3.0% | −10.8% | +2.6% | 38% | 1.0 |

- **What happens after a pump.**
  - The *typical* pumped coin fades: the median is −5 to −11% over 7 days. That is why holding feels right.
  - The *average* outcome is adverse at every level, because the right tail is fat: a third of them rip another +20% within 3 days.
  - A normal short loses nothing on average; a short at +20–75% loses a further 3–11% over 3 days.
  - Each row alone is only t 1.0–1.7. The consistent sign across all levels is the evidence.
- **Book-level tests are stronger** (Wave R, realistic accounting): a +20% short stop beats +30% by t 2.72, in 0/6 years for +30%, and beats +15%.
- **Where you are down does not matter.** Your entry price is sunk, and the forward expectation is adverse whether a short is +25% or +80%.

What the research supports:
1. **Cover every short that is ≥ +20% against its entry.** Don't wait for a pullback. The median pullback is real, but the tail losses outweigh it.
2. **Don't re-short a stopped name at the next rebalance** (B-MV rule 3).
3. **Split the covers over a few hours** rather than one market order in a squeeze. Slippage on these fills is the main live risk (wave 3a).
4. **Going forward, run the B-MV short rules:**
   - 20% stop instead of LIVE's 40%;
   - minvar short weights, which already down-weight the names most likely to squeeze together.

These are research findings from 2020–25 data, not a guarantee about any particular coin.

## Files
- `PREREG.md`, `trials.csv`: pre-registration and results.
- `ext5.py`, `lib4.py`: the engine and shared setup.
- `verify.py`, `verify3.py`: the engine checks.
- `s1.py` / `s1.txt`: structures.
- `s2.py` / `s2.txt`: score grid and final out-of-sample result.
- `diag.py` / `diag.txt`, `diag2.py` / `diag2.txt`: N-step check, leg regressions and pumped-short events.
- Book caches are in `~/work/out4` and are not committed.
