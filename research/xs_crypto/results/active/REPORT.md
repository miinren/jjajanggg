# Active intra-period position management on top of B: research report

Scope: can exits, cuts or stops between the 8-hourly rebalances improve B = `ext.book(D, S0, short_frac=0.55, stop=0.2, N=12, NS=20)`?
The data runs 2020-03-15 to 2025-12-31. The 2026 holdout was not used. This is research only; no trading.
Code is in `ext_active.py` (a copy of `ext.py` with the extensions; `ext.py` is untouched), `run1.py`, `recovery.py`, `clock.py` and `wf.py`.
Results are in `trials.csv`, `walkforward.csv`, `recovery.csv`, `res/*.pkl` and `clock.pkl`.

## Bottom line

1. **No active-management rule was adopted: 0 of 31 candidates passed.** Only 3 had a positive risk-matched t vs B: redeploy-next 0.53, long rank exit 0.13, and none above 1.0. None passed the partition test.
   - Walk-forward selection over the whole active menu (pick the best in-sample variant each year) earned **SR 2.19 vs 2.43 for B over 2021-25, t −2.69**.
   - In this book, intervening between rebalances beyond B's one mechanical stop destroys value.
2. **The existing rule is the right amount of active management.** The rule is: cut a short at an adverse move of 20% since entry, and ban it until the next rebalance.
   - B with the short stop: SR 2.69, MDD −30% at 2%/day vol, worst year 1.41.
   - The same book with a 40% short stop (the old live level): SR 2.49, worst year 1.10.
   - The same book with no stops: SR 2.44, MDD −37%, worst year 0.73.
   - 20% is the best or within 0.07 SR of the best on every one of the 8 possible rebalance clocks. Mean SR over the 8 clocks: 0.15 → 2.38, **0.20 → 2.51**, 0.25 → 2.47, 0.30 → 2.37. So it is not a one-clock spike.
3. **Positions at −20%. A short that is down 20% (price +20% since entry) almost never recovers before the next rebalance, and often gets much worse.**
   - Only ~1% are back to break-even at the next rebalance and ~4% are better than −10%.
   - 17% are already worse than −30% by then.
   - Within 3 days, about half touch −10% at some point. Only 13–14% end the 3 days at break-even or better, and ~30% end worse than −30%.
   - **Cut these shorts; B already does this automatically.**
4. **A long that is down 20% should NOT be cut.**
   - Losing longs mean-revert: the forward 72h is +1.9 to +2.1% of entry notional, against +0.2% for an average long.
   - Every long stop tighter than 40% lowered SR: 20% gave t −1.36 and 30% gave t −2.66 vs B.
5. **Being down ~20% on several names at once is normal for this book.**
   - About 25% of short positions touch −20% during their life, which is roughly 4 per week in a 20-short book (median 56 h after entry).
   - About 21% of long positions touch −20%, roughly 0.8 per week (median ~10 days after entry).
   - It is not a sign the strategy has broken.

## Setup and verification
- `ext_active.book` with all new options off reproduces `ext.book` bit for bit, for both B and LIVE: daily frame and per-coin hourly matrix, max abs diff 0.0 (`verify.py`).
- It also stays bit-identical when the new options are switched on at non-binding thresholds.
- Two edge-case guards were added, both unreachable in B:
  - zero shorts when every candidate is banned;
  - a 24 h floor in the vol-scaled stop.
- **Timing:**
  - Price-level exits (stops, trails, partials, time stops) use the same accrued `lc` as the live stop. They act as resting stop orders at the hourly close.
  - Signal-based exits (rank deterioration, squeeze detector) are evaluated at the top of hour i on non-rebalance hours, using data rows ≤ i only. Like a rebalance, they are then 1 h lagged into the P&L.
  - Every exit, partial, re-deployment and hedge change pays 5.5 bp per unit of turnover.
- **Adoption bar:** all of the following are required.
  - `h.partition_test(D, cand, B)` with risk matching returns adopt=True.
  - t_NW ≥ 2.0.
  - Walk-forward over the parameter family beats B.
- **Budget:** 33 trial IDs were used, out of a maximum of 60. That is 31 candidates, 1 clock-robustness re-test and 1 diagnostic grid.
  - Every candidate was pre-registered with its rationale in `trials.csv` before it was run.
  - A27–A33 were registered after the first 26 results and after the recovery diagnostic. That is stated in their rationale.

## Base reference
| Book | SR | bp/day | MDD @2%/day vol | worst-year SR | SR @8bp | SR @12bp | turnover/day |
|---|---|---|---|---|---|---|---|
| B | 2.69 | 24.5 | −30.0% | 1.41 | 2.58 | 2.40 | 0.41 |
| B, short stop 0.40 | 2.49 | 23.3 | −30.6% | 1.10 | | | |
| B, no stops at all | 2.44 | 23.4 | −37.0% | 0.73 | | | |

## Evidence already on file from the parallel drawdown agent (`results/drawdown/trials.csv`), not re-run here
| Idea | Result vs B |
|---|---|
| Pure residual (beta-adjusted) short stop at 15 / 20 / 25% (T13–15) | t −0.95 / −1.43 / −1.02, fail |
| Longer ban after a stop: 24 / 72 / 168 h (T10–12) | t −0.09 / −0.37 / −0.56, fail |
| Stop ladder: halve at 10%, exit at 20% (T16) | t 0.21, fail |
| Per-name stop scaled by idio vol, fixed at rebalance (T39) | t 0.28, fail |

This study tested different variants of the same families:
- a residual *filter* on the raw stop;
- a residual z-stop that grows with holding time;
- 15/25 and 20/30 ladders;
- no ban at all.

## Full trials table (risk-matched partition test vs B; adopt = partition adopt AND t ≥ 2.0)
| id | name | family | params | SR | bp | t_vs_B | years | groups | regimes_up_dn | adopt | mdd_at2pct | minYrSR | t_vs_LIVE | SR8bp | SR12bp | turnover |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A01 | hyb_r10 | HYB | resid_hyb=0.10 | 2.527 | 23.17 | -1.76 | 1/6 | 1/5 | -2.45/-0.35 | False | -45.42 | 0.86 | 1.99 | 2.42 | 2.24 | 0.394 |
| A02 | hyb_r15 | HYB | resid_hyb=0.15 | 2.541 | 23.24 | -1.62 | 2/6 | 1/5 | -2.05/-0.56 | False | -38.06 | 1.04 | 2.08 | 2.43 | 2.26 | 0.389 |
| A03 | vz3 | VZ | vz=3 | 2.379 | 22.66 | -2.41 | 2/6 | 0/5 | -3.79/-1.72 | False | -41.5 | 0.59 | 1.15 | 2.29 | 2.16 | 0.325 |
| A04 | vz4 | VZ | vz=4 | 2.455 | 23.47 | -1.96 | 2/6 | 0/5 | -2.54/-1.71 | False | -40.36 | 0.71 | 1.61 | 2.37 | 2.24 | 0.318 |
| A05 | vz3_plus_raw | single | vz=3, vz_raw=True | 2.666 | 24.28 | -0.73 | 2/6 | 3/5 | -0.17/-0.34 | False | -29.9 | 1.41 | 2.77 | 2.55 | 2.37 | 0.409 |
| A06 | half_15_25 | HALF | half_at=0.15, stop=0.25 | 2.471 | 22.7 | -2.18 | 0/6 | 2/5 | -2.07/-1.99 | False | -33.33 | 1.32 | 1.86 | 2.35 | 2.16 | 0.427 |
| A07 | half_20_30 | HALF | half_at=0.20, stop=0.30 | 2.478 | 23.02 | -2.01 | 1/6 | 1/5 | -2.41/-1.41 | False | -28.05 | 1.2 | 1.97 | 2.37 | 2.19 | 0.4 |
| A08 | trail20 | TRAIL | trail=0.20 | 2.527 | 21.69 | -1.15 | 3/6 | 2/5 | -0.46/-2.85 | False | -29.45 | 1.64 | 1.55 | 2.35 | 2.08 | 0.578 |
| A09 | trail25 | TRAIL | trail=0.25 | 2.51 | 21.97 | -1.49 | 2/6 | 1/5 | -1.79/-1.52 | False | -32.38 | 1.38 | 1.67 | 2.36 | 2.13 | 0.51 |
| A10 | trail30 | TRAIL | trail=0.30 | 2.488 | 21.79 | -1.8 | 1/6 | 1/5 | -2.94/-0.54 | False | -29.92 | 1.33 | 1.56 | 2.35 | 2.13 | 0.472 |
| A11 | rankS30 | RANKS | rank_exit_s=30 | 2.475 | 22.51 | -3.71 | 1/6 | 1/5 | -1.67/-2.40 | False | -30.1 | 1.24 | 1.49 | 2.32 | 2.07 | 0.555 |
| A12 | rankS40 | RANKS | rank_exit_s=40 | 2.55 | 23.19 | -2.96 | 1/6 | 2/5 | -1.42/-1.17 | False | -30.09 | 1.24 | 1.91 | 2.42 | 2.2 | 0.479 |
| A13 | rankL24 | single | rank_exit_l=24 | 2.694 | 24.5 | 0.13 | 4/6 | 3/5 | 0.12/-0.12 | False | -30.22 | 1.43 | 2.9 | 2.58 | 2.39 | 0.422 |
| A14 | time3 | TIME | time_stop=3 | 2.272 | 20.83 | -3.61 | 0/6 | 2/5 | -4.37/-3.21 | False | -30.52 | 1.25 | 0.33 | 2.07 | 1.75 | 0.726 |
| A15 | time7 | TIME | time_stop=7 | 2.642 | 24.09 | -0.5 | 2/6 | 3/5 | -0.21/-0.77 | False | -28.83 | 1.42 | 2.54 | 2.49 | 2.26 | 0.536 |
| A16 | sqz_z3 | SQZ | sqz=(3,3) | 2.562 | 22.66 | -1.14 | 1/6 | 1/5 | -1.53/-0.79 | False | -34.0 | 1.16 | 1.79 | 2.43 | 2.22 | 0.461 |
| A17 | sqz_z4 | SQZ | sqz=(4,3) | 2.578 | 23.14 | -1.3 | 1/6 | 1/5 | -1.52/-0.46 | False | -31.87 | 1.03 | 2.04 | 2.46 | 2.26 | 0.433 |
| A18 | redeploy_next | REDEPLOY | redeploy=next | 2.724 | 24.8 | 0.53 | 4/6 | 3/5 | -0.75/1.60 | False | -29.23 | 1.4 | 3.15 | 2.62 | 2.45 | 0.375 |
| A19 | redeploy_scale | REDEPLOY | redeploy=scale | 2.685 | 24.55 | -0.42 | 4/6 | 1/5 | -0.21/0.11 | False | -28.99 | 1.35 | 2.9 | 2.57 | 2.38 | 0.421 |
| A20 | lc_reset | single | lc_reset=True | 2.54 | 22.88 | -1.36 | 1/6 | 1/5 | -1.61/-1.13 | False | -34.28 | 0.99 | 2.11 | 2.44 | 2.28 | 0.357 |
| A21 | brake3 | BRAKE | brake=0.03 | 2.553 | 23.09 | -3.87 | 0/6 | 2/5 | -0.77/-1.92 | False | -31.08 | 1.07 | 2.04 | 2.39 | 2.13 | 0.565 |
| A22 | brake5 | BRAKE | brake=0.05 | 2.676 | 24.28 | -1.34 | 2/6 | 2/5 | -0.07/-0.27 | False | -30.01 | 1.35 | 2.79 | 2.55 | 2.36 | 0.432 |
| A23 | confirm2 | single | confirm=2 | 2.554 | 23.37 | -1.43 | 1/6 | 1/5 | -1.40/-1.10 | False | -33.77 | 1.35 | 2.34 | 2.44 | 2.27 | 0.399 |
| A24 | lstop20 | LSTOP | long_stop=0.20 | 2.666 | 24.23 | -1.36 | 1/6 | 1/5 | -0.23/-0.26 | False | -30.07 | 1.41 | 2.72 | 2.55 | 2.36 | 0.426 |
| A25 | lstop30 | LSTOP | long_stop=0.30 | 2.652 | 24.11 | -2.66 | 0/6 | 1/5 | -0.22/-0.56 | False | -30.2 | 1.39 | 2.69 | 2.54 | 2.35 | 0.412 |
| A26 | lstop_off | LSTOP | long_stop=None | 2.681 | 24.44 | -0.92 | 1/6 | 3/5 | -0.27/0.09 | False | -29.88 | 1.45 | 2.8 | 2.57 | 2.39 | 0.402 |
| A27 | noban | BAN | ban=False | 2.494 | 23.44 | -1.96 | 2/6 | 1/5 | -2.58/-0.86 | False | -35.0 | 0.86 | 1.86 | 2.38 | 2.21 | 0.408 |
| A28 | sstop15 | SSTOP | stop=0.15 | 2.577 | 23.31 | -1.02 | 0/6 | 2/5 | -1.42/-0.61 | False | -31.92 | 1.41 | 2.04 | 2.45 | 2.25 | 0.446 |
| A29 | sstop25 | SSTOP | stop=0.25 | 2.503 | 23.15 | -1.9 | 0/6 | 2/5 | -2.08/-1.30 | False | -32.66 | 1.24 | 2.15 | 2.4 | 2.23 | 0.387 |
| A30 | reb_dw10 | single | reb_dw=0.10 | 2.664 | 24.37 | -0.86 | 2/6 | 3/5 | -0.27/-0.25 | False | -30.56 | 1.46 | 2.65 | 2.54 | 2.34 | 0.447 |
| A31 | half_20_40 | single | half_at=0.20, stop=0.40 | 2.491 | 23.2 | -1.63 | 2/6 | 2/5 | -3.35/0.04 | False | -30.28 | 1.17 | 2.69 | 2.39 | 2.22 | 0.382 |
| A32 | redeploy_next_8clock | single | redeploy=next (8 offsets) | 2.566 (8-clock avg; B 2.566) |  | -0.0 | 4/6 | 2/5 | 0.00/-0.01 | False | -30.39 | 1.19 |  |  |  |  |
| A33 | sstop_8clock | diagnostic | stop in {.15..30} x 8 offsets | 8-clock mean SR: stop.15 2.375, .20 2.508, .25 2.472, .30 2.373 |  |  |  |  |  | n/a (diagnostic) |  |  |  |  |  |  |
Notes:
- A32 is A18 (immediate re-deployment into the next-ranked short) re-tested as the average over all 8 rebalance clocks. Its edge disappears completely: t −0.00, SR 2.566 vs 2.566.
- A33 is the short-stop grid on 8 clocks, from `clock.log`:

| clock offset | stop .15 | .20 | .25 | .30 |
|---|---|---|---|---|
| 0 (live) | 2.58 | **2.69** | 2.50 | 2.45 |
| 1 | 2.45 | 2.51 | 2.48 | 2.42 |
| 2 | 2.20 | 2.23 | 2.24 | 2.02 |
| 3 | 2.26 | 2.35 | 2.32 | 2.24 |
| 4 | 2.36 | 2.53 | 2.60 | 2.41 |
| 5 | 2.36 | 2.59 | 2.58 | 2.45 |
| 6 | 2.38 | 2.54 | 2.50 | 2.47 |
| 7 | 2.42 | 2.62 | 2.55 | 2.54 |
| mean | 2.38 | **2.51** | 2.47 | 2.37 |

Caveat: B's live clock (offset 0) is the luckiest of the 8 clocks. The mean over the 8 clocks is 2.51, not 2.69.

## What each idea did, in short
- **Residual filter on the stop (A01–02):** fail, t −1.6 to −1.8, and MDD worse (−38 to −45%). The raw 20% stop catches market-wide alt squeezes. Those are exactly the ones the BTC hedge does *not* cover. The likely reason, not tested here, is that the alt-season co-movement is not captured by 168h BTC betas.
- **Residual vol-scaled z-stop (A03–05):**
  - As a replacement for the raw stop it is clearly worse: t −2.4 / −2.0, 0/5 coin groups, MDD −40%.
  - As an add-on to the raw stop it is neutral: t −0.7.
- **Partial de-risking (A06, A07, A31):** every ladder is worse (t −1.6 to −2.2). Keeping half of a squeezing short keeps half of the continuation tail.
- **Trailing stops (A08–10):** worse (t −1.2 to −1.8). They turn into profit-taking on winning shorts and raise turnover to 0.47–0.58.
- **Hourly rank-deterioration exit (A11–13):**
  - For shorts it is strongly worse: t −3.7 / −3.0. The same failure as faster re-ranking: hourly idio-vol ranks are noise.
  - For longs it is neutral: t +0.13.
- **Time stops (A14–15):** 3 days is strongly worse (t −3.6). 7 days is neutral (t −0.5). Under-water shorts keep earning the drift.
- **Squeeze detector, 4h residual z plus volume surge (A16–17):** worse (t −1.1 / −1.3). By the time volume confirms, the 20% stop is usually the better exit, and false alarms cut good shorts.
- **Re-deploying freed capital (A18–19):**
  - Next-ranked name: t +0.53. This was the best in-sample result, but it falls to 0.00 on the 8-clock average.
  - Pro-rata scaling of the remaining shorts: t −0.42.
- **Stop measured from the last rebalance instead of from entry (A20):** worse (t −1.4).
- **Book-level brake (A21–22):** worse (t −3.9 / −1.3).
- **Stop confirmation over 2 consecutive hours (A23):** worse (t −1.4). Waiting an hour loses more in continuations than it saves on wicks.
- **Long stops (A24–26):** 20% and 30% are worse. No long stop at all is roughly neutral (t −0.9). The 40% long stop is harmless but adds nothing.
- **No ban after a stop (A27):** worse (t −2.0, MDD −35%). The one-rebalance ban matters. Longer bans (drawdown agent) do not help either.
- **Short stop 15% / 25% (A28–29):** both worse than 20% (t −1.0 / −1.9).
- **Down-weighting kept shorts that are already 10% adverse at the rebalance (A30):** neutral to slightly worse (t −0.9).

## Walk-forward over parameter families (pick the best in-sample member for each year; years 2021–25)
| family | includes B | n | WF SR | B SR (2021-25) | t vs B | beats B | picks |
|---|---|---|---|---|---|---|---|
| HYB | False | 2 | 2.27 | 2.43 | -1.34 | False | {2021: 'A01', 2022: 'A02', 2023: 'A02', 2024: 'A02', 2025: 'A02'} |
| HYB | True | 3 | 2.43 | 2.43 |  | False | {2021: 'B', 2022: 'B', 2023: 'B', 2024: 'B', 2025: 'B'} |
| VZ | False | 2 | 2.21 | 2.43 | -0.75 | False | {2021: 'A04', 2022: 'A04', 2023: 'A04', 2024: 'A04', 2025: 'A04'} |
| VZ | True | 3 | 2.43 | 2.43 |  | False | {2021: 'B', 2022: 'B', 2023: 'B', 2024: 'B', 2025: 'B'} |
| HALF | False | 2 | 2.22 | 2.43 | -1.81 | False | {2021: 'A06', 2022: 'A06', 2023: 'A06', 2024: 'A06', 2025: 'A06'} |
| HALF | True | 3 | 2.43 | 2.43 |  | False | {2021: 'B', 2022: 'B', 2023: 'B', 2024: 'B', 2025: 'B'} |
| TRAIL | False | 3 | 2.18 | 2.43 | -2.33 | False | {2021: 'A08', 2022: 'A08', 2023: 'A08', 2024: 'A08', 2025: 'A08'} |
| TRAIL | True | 4 | 2.33 | 2.43 | -1.27 | False | {2021: 'A08', 2022: 'A08', 2023: 'A08', 2024: 'A08', 2025: 'B'} |
| RANKS | False | 2 | 2.26 | 2.43 | -3.08 | False | {2021: 'A11', 2022: 'A11', 2023: 'A11', 2024: 'A12', 2025: 'A12'} |
| RANKS | True | 3 | 2.43 | 2.43 |  | False | {2021: 'B', 2022: 'B', 2023: 'B', 2024: 'B', 2025: 'B'} |
| TIME | False | 2 | 2.49 | 2.43 | 0.65 | True | {2021: 'A15', 2022: 'A15', 2023: 'A15', 2024: 'A15', 2025: 'A15'} |
| TIME | True | 3 | 2.40 | 2.43 | -1.08 | False | {2021: 'B', 2022: 'A15', 2023: 'B', 2024: 'B', 2025: 'B'} |
| SQZ | False | 2 | 2.21 | 2.43 | -2.43 | False | {2021: 'A16', 2022: 'A16', 2023: 'A16', 2024: 'A16', 2025: 'A16'} |
| SQZ | True | 3 | 2.37 | 2.43 | -1.05 | False | {2021: 'A16', 2022: 'B', 2023: 'B', 2024: 'B', 2025: 'B'} |
| REDEPLOY | False | 2 | 2.43 | 2.43 | 0.06 | False | {2021: 'A19', 2022: 'A19', 2023: 'A18', 2024: 'A18', 2025: 'A18'} |
| REDEPLOY | True | 3 | 2.42 | 2.43 | -0.11 | False | {2021: 'A19', 2022: 'B', 2023: 'A18', 2024: 'A18', 2025: 'A18'} |
| BRAKE | False | 2 | 2.34 | 2.43 | -3.37 | False | {2021: 'A21', 2022: 'A22', 2023: 'A22', 2024: 'A22', 2025: 'A22'} |
| BRAKE | True | 3 | 2.35 | 2.43 | -3.19 | False | {2021: 'A21', 2022: 'B', 2023: 'B', 2024: 'B', 2025: 'B'} |
| LSTOP | False | 3 | 2.40 | 2.43 | -1.26 | False | {2021: 'A25', 2022: 'A26', 2023: 'A26', 2024: 'A26', 2025: 'A26'} |
| LSTOP | True | 4 | 2.40 | 2.43 | -1.26 | False | {2021: 'A25', 2022: 'A26', 2023: 'A26', 2024: 'A26', 2025: 'A26'} |
| SSTOP | False | 2 | 2.35 | 2.43 | -0.81 | False | {2021: 'A28', 2022: 'A28', 2023: 'A28', 2024: 'A28', 2025: 'A28'} |
| SSTOP | True | 3 | 2.43 | 2.43 |  | False | {2021: 'B', 2022: 'B', 2023: 'B', 2024: 'B', 2025: 'B'} |
| BAN | True | 2 | 2.43 | 2.43 |  | False | {2021: 'B', 2022: 'B', 2023: 'B', 2024: 'B', 2025: 'B'} |
| ALL_ACTIVE | False | 31 | 2.19 | 2.43 | -2.69 | False | {2021: 'A16', 2022: 'A08', 2023: 'A08', 2024: 'A08', 2025: 'A13'} |
| ALL_ACTIVE | True | 32 | 2.19 | 2.43 | -2.69 | False | {2021: 'A16', 2022: 'A08', 2023: 'A08', 2024: 'A08', 2025: 'A13'} |
- Only one family has a walk-forward SR above B: TIME without B in the family (2.49 vs 2.43). It always picks A15 (time7), and A15 fails the partition test (t −0.50, 2/6 years). So it is not adopted.
- **Menu-wide walk-forward: SR 2.19 vs 2.43, t −2.69.** Choosing an active rule by past performance would have hurt out of sample.

## Adopted candidates
**None.** No candidate met even condition (1) of the adoption bar, so no plateau check of a winner was needed.
- The closest were A18 `redeploy='next'` (t 0.53, 4/6 years, 3/5 groups, BTC-up regime negative; 8-clock t 0.00) and A13 `rank_exit_l=24` (t 0.13).
- Both are placebo-level; the 200-placebo t distribution has a 95th percentile of 0.61.
- The only "plateau check" that mattered was on B's own 20% stop (A28, A29, A33). It holds on every clock.

## −20% adverse positions: frequency and recovery
Method (`recovery.py`, `recovery.csv`):
- For every position episode, the first hour its raw move since entry reaches 20% adverse is recorded. For a short that is price +20%; for a long it is price −20%.
- We then follow the coin's actual price path, whether or not the book still holds it.
- Forward P&L is expressed in % of entry notional.
- "Resid" is the BTC-beta-hedged forward P&L, with beta taken at the hit hour.
- The next rebalance is on average only ~3.3 h after the hit.

**Shorts (price +20% since entry)**

| | B (stop 20%) | B, stop 40% (live-style) | B, no stops | A18 (best t) |
|---|---|---|---|---|
| episodes reaching −20% | 1247 of 5025 (24.8%) | 1003 of 4252 (23.6%) | 799 of 3767 (21.2%) | 1270 of 3818 (33.3%) |
| per week | 4.1 | 3.3 | 2.6 | 4.2 |
| median hours after entry | 56 | 56 | 57 | 54 |
| **at next rebalance:** back to breakeven | 1.0% | 1.4% | 0.9% | 1.0% |
| at next rebalance: better than −10% | 4.4% | 4.2% | 3.8% | 3.9% |
| at next rebalance: worse than −30% | 18.0% | 17.2% | 16.4% | 17.7% |
| mean fwd P&L to next reb (raw / hedged) | −1.0% / −0.3% | −0.7% / −0.1% | −1.0% / −0.3% | −1.0% / −0.3% |
| **within 3 days:** ever touched −10% | 50% | 51% | 50% | 50% |
| within 3 days: ever touched breakeven | 24% | 24% | 23% | 25% |
| within 3 days: ever touched −30% | 64% | 62% | 59% | 63% |
| **at +72h:** better than −10% | 31% | 33% | 31% | 31% |
| at +72h: breakeven or better | 14% | 14% | 13% | 14% |
| at +72h: worse than −30% | 31% | 30% | 30% | 31% |
| mean / median fwd P&L over 72h (raw) | −5.8% / +3.9% | −3.6% / +5.1% | −4.3% / +4.5% | −6.0% / +4.2% |
| mean fwd P&L over 72h (hedged) | +2.1% | +2.9% | +1.7% | +1.8% |
| (all short positions, unconditional, 72h) | −0.1% | −0.2% | −0.2% | −0.2% |

Note on A18: the 33% is overstated. Names added between rebalances by re-deployment are hits but are not counted as episodes.

**Longs (price −20% since entry)**

| | B | B, no stops |
|---|---|---|
| episodes reaching −20% | 245 of 1127 (21.7%), 0.8/week | 218 of 1063 (20.5%), 0.7/week |
| median hours after entry | 248 | 249 |
| at next rebalance: breakeven / better than −10% / worse than −30% | 0% / 0.8% / 3.3% | 0% / 0.9% / 3.7% |
| within 3 days: touched −10% / breakeven / −30% | 25% / 7% / 35% | 22% / 5% / 34% |
| at +72h: better than −10% / breakeven / worse than −30% | 14% / 2% / 13% | 13% / 2% / 14% |
| mean fwd P&L 24h / 72h (raw) | +2.2% / +2.1% | +1.8% / +1.9% |
| (all long positions, unconditional, 72h) | +0.2% | +0.2% |

**How to read this:**
- **Shorts at −20% have a fat continuation tail.**
  - The median path reverts a little: +4–5% of notional over 3 days.
  - The mean is −4 to −6%. Nearly 1 in 3 is worse than −30% three days later, and almost none recover before the next rebalance.
  - Hedged, the 3-day mean is slightly positive, but the variance is huge. The backtest settles the trade-off: cutting at 20% beats both 40% and no stop on SR, MDD and worst year, on every clock.
- **Longs at −20% grind down slowly** (median ~10 days after entry) **and then mean-revert** (+2% vs +0.2% baseline). Cutting them is a small loss, which is why long stops hurt.

## Answer to the user's question
- Beyond B's existing mechanical rule, active management **does not help** this book. Of 31 exit, cut, stop, trail, detector, brake and redeploy variants, none beats B, and choosing among them by past performance loses (walk-forward t −2.69).
- What does help is **already in B**:
  - Close any short the moment it is 20% against you (from entry), and do not re-short it at the very next rebalance.
  - If you are still running the old 40% short stop, moving to 20% is the one change the data support: SR +0.20, worst year 1.10 → 1.41, robust across clocks.
  - Leave −20% longs alone.
- Many positions being at −20% is expected: about a quarter of shorts and a fifth of longs get there at some point.
- Beyond the stop, the fix is diversification and sizing, not discretionary intervention. Hand-cutting on a feeling is, in this data, closest to A14 (time stop), A11 (rank exit) or A21 (brake), all of which were clearly harmful: t −3.6 to −3.9.

## Caveats
- **Stop fills:** the backtest exits at the hourly close at which the move is at least 20% (including the overshoot) and pays 5.5 bp. Real stop orders in squeezes can slip more.
  - At 12 bp, B still has SR 2.40.
  - The stop's advantage over no-stop is ~1 bp/day of mean plus a large variance and MDD reduction, so it survives moderate extra slippage. Extreme squeeze slippage was not modelled.
- **In-sample:** 20% was chosen on this same data. It holds on all 8 clocks and at 15/25%, but the 2026 holdout is the only clean test.
- **Clock luck:** B's live clock has the highest SR of the 8 (2.69 vs a mean of 2.51). Expect the lower number.
- **Recovery statistics** follow the coin's path and are not the book's P&L. They measure hit-and-hold outcomes before costs.
  - Episodes overlap in time (clustered squeezes), so the effective sample is much smaller than the counts suggest.
- **Multiple testing:** 33 IDs here, plus ~350 earlier books across agents. A t ≈ 0.5 is noise, and no result here comes near the placebo maximum of 1.79.
- **Memory:** everything was run in one process at a time. Two runs were OOM-killed by other agents' usage and resumed from per-trial pickles (`res/`). No results were affected.
