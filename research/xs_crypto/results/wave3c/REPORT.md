# Wave 3c: higher-frequency (1–8h) execution timing, settlement timing and entry filters; plus wave 4 (new signals, a holistic model and a hedge band)

Research only. Data runs 2020-03-15..2025-12-31 (the 2026 holdout was not touched). Every book is **8-clock averaged** and compared with **B-MV**
(`ext3.book(D, S0, short_frac=0.55, stop=0.2, N=12, NS=20, leg_weights=minvar_floor)`). The new engine `ext4.py` reproduces B-MV
**bit for bit** at all 8 offsets (`verify.py`: max diff 0.0), giving SR **2.773** at 5.5 bp, **2.616** at 8 bp and **2.364** at 12 bp.
Adoption means the risk-matched `h.partition_test` returns adopt=True **and** t ≥ 2.0 (the placebo max was 1.79), plus a walk-forward for parameter families and a plateau check on any pass.

## Bottom line
1. **None of the three pre-registered HF topics produced an adoptable change: 0 of 40 wave-3c trials.**
   - **Execution timing: TWAP comes closest.** Splitting each rebalance over 2/3/4 h gives SR 2.79/2.80/2.81 (t 1.81/2.03/1.95) and beats B-MV on 7–8 of 8 clocks. It fails the coin-group test (4/5, 3/5, 2/5). The walk-forward picks 4h TWAP every year: 2.63 vs 2.59, t 1.17. **About +0.03 SR, not significant**, but it costs nothing to do, so splitting live orders over about 3h is harmless and slightly helpful.
   - **Signal-timed entries and exits lose.** These delayed short entries until the residual stops rising, short covers until a dump stops, and long entries until the fall stops (t −0.4 to −3.9). The loss is mostly an artefact of hedge re-trading (next item), but even with that fixed they add only ~+0.03 SR and win just 1–2 of 6 years (E14/E15).
   - **Funding-settlement timing.** The bar right after 00/08/16 UTC does carry a strong cross-sectional effect (long candidates +2.4 bp/h t 5.2, short candidates −1.9 bp/h t −3.8, bottom-quintile-funding coins −3.4 bp/h t −5.4). It **does not explain the clock dispersion**: the pre-registered mechanism clock (offset 3) scores 2.74 and the post-hoc one (offset 1) 2.81, against the 2.77 8-clock mean. The live clock (offset 0, 2.91) is simply the luckiest.
   - **Hourly event filters** (volume spikes, residual jumps, gap reversals): 11 trials, t −1.4 to +0.3, and every family loses in walk-forward.
2. **Wave 4 has one adoption: W06, a BTC-hedge no-trade band (0.03 of NAV).** It is a pure cost saving (≈ +0.27 bp/day, **SR 2.773 → 2.811**; 2.668 at 8 bp and 2.438 at 12 bp), explained under "W06" below.
3. **New signals (added at the user's request).**
   - Two of six features passed a strict out-of-sample IC screen: volume-signed 72h residual flow (OOS IC −0.043) and idiosyncratic share (−0.027).
   - Inside the book **both hurt**: blend t −3.3 and −1.9, and the flow sleeve alone has SR −0.76.
   - Candidate-set tie-breaks and vetoes (W01–W04) all flip sign between 2020–22 and 2023–25.
   - The one "holistic" model trained on all 17 features is reported in the W08 section.
4. **Why things keep failing.** B-MV trades the extreme tails of S0. Features with real predictive power across the whole cross-section (flow, idio-share) are U-shaped or concentrated mid-distribution, so they do not help inside the tails. Anything that changes *which* names are held costs more than it adds, which matches waves 1–2.

## Topic 1: execution timing (E01–E16)
- **Engine.** `ext4.book(..., execf, H)`. The target portfolio is unchanged. Each coin's weight moves to target at a later step j ∈ [i0, i0+H] according to a policy that sees only rows ≤ j, and weights set at j earn R1[j+2]. Turnover is charged when the weight actually moves, and stops act on filled weights.
- **Turnover decomposition** (`diag_turnover.csv`, found with the red-team agent):
  - Coin turnover is **identical** for every policy (0.314/day).
  - The delay policies raised **BTC-hedge** turnover from 0.155 to 0.23–0.28/day. Delaying only one kind of trade leaves a temporary net beta, and the hedge makes a round trip each window.
  - Pre-cost, the short-cover delay E08 made 23.65 and E12 23.72 bp/day, against 23.40 for B-MV.
  - E14–E16 re-run the policies with the hedge traded once to the *target* beta. The turnover disappears, but the gain is small and not robust (E14 t 1.17, 2/6 years; E15 t 0.89, 1/6).
- **E05–E07.** Delaying new shorts until the pump stops is worse even pre-cost (23.21 bp/day). Shorting straight into strength is right, consistent with the prior finding that the top 3h-residual tail mean-reverts.
- **E11.** Delaying the exit of pumping longs has t −3.9; pumped names mean-revert, so exit immediately.

## Topic 2: funding settlement (F00 diagnostic, F01/F02)
`f00_phase.py`, `f00_phase_by_hour.csv`. The table gives the group-minus-M residual return in bp/h by hour mod 8, where phase 0 is the bar labelled 00/08/16 UTC (t is the sum of the three hourly NW t divided by √3):

| phase | long cands (S0 bottom 12) | short cands (S0 top 20) | funding bottom 20% | funding top 20% |
|---|---|---|---|---|
| 0 | **+2.36 (t 5.2)** | **−1.93 (t −3.8)** | **−3.39 (t −5.4)** | +0.31 (0.5) |
| 1 | +1.39 (3.6) | −1.02 (−2.3) | +0.10 | −0.80 (−1.8) |
| 6 | +0.68 | −1.71 (−3.4) | +0.37 | −1.50 (−3.0) |
| 2–5, 7 | +0.8 … −0.4 | −1.2 … 0.0 | ±1.3 | ±1.0 |

- **Mechanism.** Holders on the paying side of funding leave before the snapshot and come back after it. Negative-funding coins, where shorts pay, get sold in the first bar after settlement.
- **Why the clock doesn't matter.** Every 8h-held position spans exactly one settlement bar whichever clock is used, so the effect mostly nets out.
- **F01.** The pre-registered rule required |t| ≥ 3 for high-funding coins. It fired only through the positive-funding variant (−3.18); the main group reached −2.96, which is marginal (red-team caveat). It chose offset 3: SR 2.74, t −0.36 vs the 8-clock mean.
- **F02** (post-hoc, offset 1): SR 2.81, t 0.31. Noise.
- **Caveat.** Whether the stored bar timestamp is bar-open or bar-close shifts the phase-to-clock mapping by 1h. It does not change the conclusion.

## Topic 3: hourly event entry filters (V01–V11)
- **Mechanics.** The masks act only on names *not already held*, at the next rebalance, and create no extra trades.
- **Results.** None helps: best V05 t +0.25, worst V07 t −1.42.
- **Walk-forward.** It picks the loosest filters and still loses (volume spike 2.45, jump 2.50, against 2.59).
- **Red-team note.** The gains that do appear are concentrated in 2020.

## Wave 4 (own budget, opened after wave 3c's 40 trials were spent; ideas from an idea-generator agent, audited by a red-team agent)
### New-signal screen (N01–N06) and book tests
The pre-registered screen used S0-neutral rank IC inside M, with the sign fixed on 2020–22 and OOS t ≥ 2 required at 72h (`n_screen.py`, `n_screen.csv`).

| feature | IS IC72 | OOS IC72 (t) | verdict |
|---|---|---|---|
| N01 peer momentum (top-10 residual-correlated peers) | −0.010 | −0.007 (−1.2) | drop |
| **N02 volume-signed 72h residual flow** | −0.033 | **−0.043 (−6.7)** | promote |
| **N03 idiosyncratic share 1−R²** | −0.042 | **−0.027 (−3.7)** | promote |
| N04 hourly volume concentration | −0.031 | −0.016 (−1.99) | drop |
| N05 24h variance ratio | −0.006 | 0.000 | drop |
| N06 coin-level settlement drift | +0.017 | +0.006 | drop |

- **Book tests of the two promoted signals.**
  - N02 as a 0.15 score blend: SR 2.34 (t −3.3).
  - N03 as a 0.15 score blend: SR 2.56 (t −1.9).
  - N02 as a sleeve: SR −0.76 alone, and −4.3 t when blended in.
- **Why N02 fails.** It is **U-shaped** (`n02_deciles.log`, S0-neutral deciles in bp per 8h): −10.2, +2.1, +4.8, +3.6, +3.2, +2.9, +1.0, −2.3, −3.1, −3.4.
  - Heavy-volume selling (the bottom decile) is the worst, so a "long low flow" rule buys it.

### Candidate-set tie-breaks and vetoes (pre-screen, `w4_prescreen.csv`)
Each value is the effect of the rule's swap on forward 8h residual returns (bp), with long legs net of funding received.

| rule | predicted sign | 2020–22 | 2023–25 | verdict |
|---|---|---|---|---|
| W01 veto longs with funding < −5 bp | + | −9.8 | −3.5 | fail |
| W02 short tie-break: prefer high flow | − | +18.9 (t 2.7) | +5.1 | fail (opposite sign) |
| W03 near-high tie-break, longs / shorts | + / − | +10.6 / −16.0 | −4.0 / +7.2 | fail (flips sign) |
| W04 veto longs in the bottom flow decile | + | +17.2 | −9.0 | fail (flips sign) |

- **W09.** The post-hoc *reverse* of W02 (prefer low-flow shorts) gave book SR 2.48 (t −1.68). Hourly-changing ranks raised turnover to 0.58.
- **W05.** Min-variance weights on the long leg: SR 2.74, t −0.54, minYrSR 1.42 < 1.74. This fails the wave-2 risk-shape rule.
- **W07.** The new-long delay (E10) with the target hedge: t 1.06. Fail.

### W06: hedge no-trade band, **ADOPTED** (cost-only)
- **Rule.** The BTC hedge `h = −w·β` is re-traded at every rebalance and stop, and otherwise only when |h_target − h_current| > 0.03 of NAV. Code: `ext4.book(..., hedge_band=0.03)`.
- **Why.** The live rule re-trades the hedge every hour as the 168h β drifts. That is noise-trading costing 0.155 turnover/day.

| | B-MV | **W06 (band 0.03)** | band 0.02 (plateau) | band 0.05 (plateau) |
|---|---|---|---|---|
| SR 5.5 bp | 2.773 | **2.811** | 2.800 | 2.817 |
| SR 8 / 12 bp | 2.616 / 2.364 | **2.668 / 2.438** | 2.655 / 2.422 | 2.674 / 2.446 |
| risk-matched t vs B-MV | – | **7.28** | 7.02 | 6.21 |
| years / groups / clocks won | – | 6/6 / 5/5\* / 8/8 | 6/6 / 5/5\* / 8/8 | 6/6 / 5/5\* / 8/8 |
| hedge turnover/day | 0.155 | 0.114 | 0.119 | 0.110 |
| mdd@2% / minYrSR | −25.1 / 1.74 | −24.9 / 1.77 | −25.0 / 1.76 | −24.8 / 1.78 |

**Sanity checks for t > 3** (`w06_checks.py`, `w06_checks.txt`). The gain is a near-deterministic cost saving, which makes the paired difference very smooth; there is no leak.
- **Net vs pre-cost.** Net is +0.274 bp/day. Pre-cost is only **+0.047 bp/day (t 1.2)**, so the hedge P&L is unchanged and the gain is the cost of 0.041/day less hedge turnover.
- **\*The coin-group wins are an artefact of risk matching.** Without risk matching, all five group differences are exactly 0: hedge P&L is not attributed to coins. The pre-registration exempted W06 from this criterion; years 6/6, regimes and t are what carry it.
- **Beta unchanged.** Daily beta to BTC is 0.045 in both books. Daily tracking vs B-MV is 1.8 bp, against a daily vol of 143 bp.
- **Lower BTC cost.** BTC is the most liquid perp, so it probably trades cheaper than 5.5 bp. At a 2 bp hedge cost the saving is still +0.13 bp/day (t 3.3), at 3.5 bp +0.19 (t 4.9).
- **Plateau.** Band 0.02 to 0.05 are all better; the worst neighbour is 0.02 (t 7.0).
- **Size of the gain.** It is modest: about +0.04 SR. Implement it only if the live bot currently re-hedges hourly; it is a two-line change.

### W08: holistic model (the user asked for "all data together")
W08_PLACEHOLDER

## Caveats (red-team audit summary)
- **Lookahead.** None found: every feature and policy uses rows ≤ i, forward windows start at R1[i+2], and `np.roll` wrap-around is masked.
- **Hedge-turnover artefact.** Confirmed. It inflated the losses of the signal-timed delays in E05–E13; E14/E15 correct it.
- **Multiple testing.** 40 + 10 book trials and 6 + 5 screens. With this many correlated near-null tests, TWAP's t 2.03 is about the expected maximum. The 8-clock-average t is a single series and is valid, but "8/8 clocks" is not 8 independent confirmations.
- **`results_raw.csv` is ragged.** Rows with extra fields were appended unlabelled; the V01 row is the re-run after the empty-leg fix. **`results.csv` (built from the logs by `build_table.py`) is the clean table.**

## Full results table (8-clock averaged; t = risk-matched NW t vs B-MV; adopt = partition adopt AND t ≥ 2)
| id           |    SR |   SR8 |   SR12 |      t | years   | groups   | reg         | padopt   | adopt   |    mdd2 |   minYr |    to |   clocks_won |
|:-------------|------:|------:|-------:|-------:|:--------|:---------|:------------|:---------|:--------|--------:|--------:|------:|-------------:|
| E01          | 2.788 | 2.631 |  2.381 |  1.811 | 5/6     | 4/5      | 0.15/0.05   | True     | False   | -24.699 |   1.758 | 0.465 |            7 |
| E02          | 2.802 | 2.646 |  2.397 |  2.033 | 5/6     | 3/5      | 0.30/0.11   | False    | False   | -24.356 |   1.769 | 0.462 |            8 |
| E03          | 2.812 | 2.656 |  2.408 |  1.951 | 5/6     | 2/5      | 0.40/0.15   | False    | False   | -23.992 |   1.768 | 0.46  |            8 |
| E04          | 2.793 | 2.635 |  2.381 |  0.738 | 5/6     | 4/5      | 0.40/-0.16  | False    | False   | -25.415 |   1.71  | 0.471 |            4 |
| E05          | 2.703 | 2.518 |  2.224 | -1.929 | 0/6     | 1/5      | -0.79/-0.21 | False    | False   | -26.938 |   1.639 | 0.547 |            1 |
| E06          | 2.714 | 2.53  |  2.235 | -1.573 | 2/6     | 2/5      | -0.75/-0.07 | False    | False   | -25.86  |   1.638 | 0.545 |            1 |
| E07          | 2.743 | 2.559 |  2.265 | -0.738 | 2/6     | 3/5      | -0.07/-0.42 | False    | False   | -24.685 |   1.678 | 0.544 |            2 |
| E08          | 2.714 | 2.527 |  2.226 | -2.945 | 1/6     | 4/5      | -0.49/-0.38 | False    | False   | -24.957 |   1.689 | 0.566 |            0 |
| E09          | 2.777 | 2.618 |  2.365 |  0.308 | 1/6     | 3/5      | -0.07/0.15  | False    | False   | -25.01  |   1.742 | 0.473 |            5 |
| E10          | 2.768 | 2.603 |  2.34  | -0.443 | 1/6     | 3/5      | 0.03/-0.12  | False    | False   | -24.984 |   1.724 | 0.49  |            2 |
| E11          | 2.757 | 2.595 |  2.338 | -3.902 | 1/6     | 1/5      | -0.13/-0.12 | False    | False   | -25.175 |   1.718 | 0.48  |            1 |
| E12          | 2.707 | 2.511 |  2.197 | -2.794 | 0/6     | 5/5      | -0.48/-0.53 | False    | False   | -24.881 |   1.669 | 0.591 |            1 |
| E13          | 2.655 | 2.443 |  2.104 | -2.761 | 0/6     | 2/5      | -1.16/-0.56 | False    | False   | -26.866 |   1.585 | 0.635 |            1 |
| E14          | 2.812 | 2.655 |  2.405 |  1.166 | 2/6     | 5/5      | 0.03/0.63   | False    | False   | -23.911 |   1.725 | 0.469 |            6 |
| E15          | 2.799 | 2.642 |  2.392 |  0.893 | 1/6     | 4/5      | -0.14/0.62  | False    | False   | -23.967 |   1.747 | 0.469 |            7 |
| E16          | 2.79  | 2.633 |  2.38  |  1.244 | 4/6     | 3/5      | 0.27/-0.05  | False    | False   | -24.333 |   1.721 | 0.468 |            5 |
| F01_o3       | 2.737 | 2.586 |  2.344 | -0.36  | 1/6     | 3/5      | -0.56/0.08  | False    | False   | -25.461 |   1.609 | 0.462 |          nan |
| F02_o1       | 2.806 | 2.652 |  2.407 |  0.31  | 3/6     | 3/5      | -0.29/0.92  | False    | False   | -23.496 |   1.821 | 0.47  |          nan |
| V01          | 2.735 | 2.575 |  2.319 | -0.332 | 2/6     | 3/5      | 0.65/-1.48  | False    | False   | -25.16  |   1.58  | 0.459 |            3 |
| V02          | 2.724 | 2.564 |  2.307 | -0.463 | 1/6     | 3/5      | 0.53/-1.50  | False    | False   | -24.244 |   1.513 | 0.46  |            2 |
| V03          | 2.773 | 2.615 |  2.363 | -0.002 | 4/6     | 3/5      | 0.01/-0.02  | False    | False   | -24.571 |   1.649 | 0.468 |            4 |
| V04          | 2.69  | 2.529 |  2.27  | -0.641 | 2/6     | 3/5      | 1.16/-2.88  | False    | False   | -23.815 |   1.33  | 0.454 |            3 |
| V05          | 2.791 | 2.632 |  2.378 |  0.254 | 3/6     | 3/5      | 0.97/-0.91  | False    | False   | -22.618 |   1.554 | 0.463 |            5 |
| V06          | 2.682 | 2.524 |  2.27  | -1.252 | 2/6     | 2/5      | -0.11/-1.41 | False    | False   | -23.562 |   1.736 | 0.463 |            2 |
| V07          | 2.674 | 2.515 |  2.261 | -1.42  | 2/6     | 1/5      | -0.10/-1.56 | False    | False   | -23.115 |   1.646 | 0.464 |            0 |
| V08          | 2.773 | 2.616 |  2.365 | -0.007 | 3/6     | 2/5      | -0.07/0.09  | False    | False   | -24.835 |   1.736 | 0.468 |            4 |
| V09          | 2.665 | 2.508 |  2.256 | -0.988 | 2/6     | 1/5      | 0.71/-2.73  | False    | False   | -27.011 |   1.381 | 0.462 |            0 |
| V10          | 2.736 | 2.578 |  2.325 | -0.762 | 3/6     | 3/5      | 0.31/-1.03  | False    | False   | -24.961 |   1.637 | 0.467 |            2 |
| V11          | 2.755 | 2.597 |  2.344 | -0.459 | 3/6     | 2/5      | 0.29/-0.68  | False    | False   | -24.688 |   1.624 | 0.467 |            4 |
| N02b         | 2.336 | 2.163 |  1.886 | -3.325 | 1/6     | 1/5      | -3.74/-2.77 | False    | False   | -34.422 |   0.986 | 0.517 |            0 |
| N03b         | 2.556 | 2.396 |  2.141 | -1.878 | 2/6     | 2/5      | -2.17/-0.99 | False    | False   | -34.274 |   0.962 | 0.466 |            0 |
| N02s         | 2.267 | 2.02  |  1.626 | -4.266 | 0/6     | 1/5      | -4.50/-2.98 | False    | False   | -34.21  |   0.858 | 0.615 |            0 |
| N02s_rw0.15  | 2.52  | 2.31  |  1.976 | -3.837 | 0/6     | 1/5      | -2.26/-1.49 | False    | False   | -28.131 |   1.252 | 0.556 |            0 |
| N02s_rw0.35  | 1.937 | 1.653 |  1.2   | -4.721 | 0/6     | 0/5      | -7.45/-4.92 | False    | False   | -44.371 |   0.44  | 0.673 |            0 |
| W05          | 2.736 | 2.572 |  2.309 | -0.538 | 3/6     | 3/5      | -0.03/-0.60 | False    | False   | -26.013 |   1.416 | 0.508 |            0 |
| W06          | 2.811 | 2.668 |  2.438 |  7.284 | 6/6     | 5/5      | 0.28/0.30   | True     | True    | -24.872 |   1.772 | 0.427 |            8 |
| W06_band0.02 | 2.8   | 2.655 |  2.422 |  7.019 | 6/6     | 5/5      | 0.18/0.23   | True     | True    | -25.001 |   1.764 | 0.432 |            8 |
| W06_band0.05 | 2.817 | 2.674 |  2.446 |  6.209 | 6/6     | 5/5      | 0.34/0.31   | True     | True    | -24.807 |   1.778 | 0.424 |            8 |
| W07          | 2.787 | 2.629 |  2.377 |  1.064 | 3/6     | 4/5      | 0.17/0.02   | False    | False   | -25.009 |   1.719 | 0.469 |            5 |
| W09          | 2.476 | 2.263 |  1.922 | -1.682 | 1/6     | 1/5      | -0.26/-4.74 | False    | False   | -27.415 |   1.072 | 0.578 |            0 |

Rationales and pre-registration are in `trials.csv`. Walk-forward results are in `walkforward.csv`.

## Files
- **Engine and setup:** `ext4.py` (engine), `lib3c.py` (B-MV setup and features), `verify.py`.
- **Runners:** `run_trials.py` (all book trials), `f00_phase.py`, `n_screen.py`, `n02_deciles.py`, `w4_prescreen.py`, `w08_gbm.py`.
- **Checks and tables:** `diag_turnover.py`, `w06_checks.py`, `wf.py`, `build_table.py`.
- **Not committed:** no data or pickles. Books are cached under /root/work/out3c.
