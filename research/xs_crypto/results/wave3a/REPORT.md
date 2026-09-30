# Wave 3a: stress test of the recommended config (B-MV) before going live

Research only. All books are 8-clock averages, built exactly as in `results/wave2/lib.py` `avg8`. `ext4.book` is a trimmed copy of `wave2/ext3.book` and was checked against it: identical net P&L (max diff 0 on LIVE and B-MV, offset 3), and B-MV reproduces SR 2.773.

Code is in `lib3.py`, `ext4.py`, `t1.py` (selection), `t1b.py` (holdout scoring) and `t2.py` (costs). Every evaluation is logged in `trials.csv`. Books are cached in `cache/`.

- **LIVE** = default book.
- **B** = sf 0.55, short stop 0.20, 12 longs / 20 shorts.
- **B-MV** = B with the `minvar_floor` short leg.

## Task 1: pseudo-holdout of the selection pipeline

**Method.** Scores and books use only trailing data, so a full-period book sliced to a window is the same as a book run on that window. Selection statistics use only [2020-03-15, Y-01-01), and scoring uses year Y only, for Y = 2023, 2024, 2025. A full-sample run (to 2026) is included as a reference.

**Grids:**
- short_frac {0.5, 0.55, 0.6, 0.65}
- short stop {0.15, 0.2, 0.25, 0.3, 0.4}
- (N long, N short) {(20,20), (12,20), (8,20), (16,20), (12,15)}
- short weighting {equal, invvol, minvar_floor}

**Rule at each step:**
- The candidate is risk-matched to LIVE's vol on the selection window, then must pass the window partition test vs LIVE:
  - at most one losing year;
  - at least 4 of 5 coin groups (seed 7);
  - both BTC regimes;
  - t_NW ≥ 1.5.
- The winner is the best selection-window SR among the passers. If nothing passes, the current value is kept.

**Two pipelines:**
- **A (the historical path):** independent 1-D sweeps from LIVE, then combine the winners (falling back to the best single passer if the combination fails), then a weighting step.
- **S:** sequential greedy, in the order sf → stop → N → weighting.

**Picks:**

| selection window | pipeline A pick | pipeline S pick |
|---|---|---|
| < 2023 | sf 0.50, stop 0.20, 8L/20S, minvar_floor | same |
| < 2024 | same | same |
| < 2025 | same | same |
| < 2026 (full sample, reference) | sf 0.55, stop 0.40, 8L/20S, minvar_floor | sf 0.55, stop 0.20, 8L/20S, minvar_floor |

- Before 2025, short_frac never passed vs LIVE, so the historically adopted 0.55 would not have been chosen.
- The stop 0.20 and the fewer-longs choices were stable picks. So was minvar_floor, which was always the best-SR passer.
- A and S agree in every holdout.

**Out-of-sample score of the pick vs LIVE (year Y only):**
- dbp_rm is the risk-matched difference, scaled by the vol ratio known at selection time (about 1.2–1.3, because the pick runs at lower vol).
- t is Newey-West.

| Y | in-sample dSR at selection | OOS SR pick / LIVE | dSR | bp/day pick / LIVE (raw) | raw t | dbp_rm | t_rm | mdd@2% pick / LIVE |
|---|---|---|---|---|---|---|---|---|
| 2023 | +0.79 | 2.27 / 2.32 | **−0.06** | 11.0 / 12.1 | −0.45 | +2.1 | 0.61 | −27.1 / −27.7 |
| 2024 | +0.66 | 3.44 / 2.61 | **+0.83** | 23.0 / 17.7 | 2.08 | +11.3 | 3.51 | −20.6 / −18.7 |
| 2025 | +0.73 | 3.73 / 3.51 | **+0.22** | 28.0 / 30.6 | −0.63 | +3.5 | 0.80 | −23.1 / −19.0 |
| pooled 2023–25 | +0.73 | 3.20 / 2.86 | **+0.34** | | 0.29 | +5.6 | **2.59** | |

For reference, the actual recommendations are scored on the same years below. They are not clean out-of-sample, since they were chosen with these years in the data.

| Y | B dSR | B raw t | B-MV dSR | B-MV raw t | B-MV t_rm | B-MV mdd@2% vs LIVE |
|---|---|---|---|---|---|---|
| 2023 | +0.15 | 1.21 | −0.08 | −0.20 | 0.40 | −29.3 vs −27.7 |
| 2024 | +0.44 | 2.66 | +0.69 | 2.33 | 3.04 | −22.2 vs −18.7 |
| 2025 | +0.25 | 2.51 | +0.48 | 0.62 | 1.50 | −17.2 vs −19.0 |
| pooled | +0.28 | 3.71 | +0.40 | 1.46 | 2.75 | |

**Findings:**
1. **The pick beats LIVE on out-of-sample Sharpe in 2 of 3 years, and on risk-matched return in 3 of 3.** The pooled out-of-sample uplift is +0.34 SR (risk-matched t 2.59), against about +0.73 SR in-sample at selection time. That is about 45% retention: mean +0.33, median +0.22.
2. **Raw bp/day is *lower* than LIVE in 2023 and 2025.** The picked configs carry about 20% less vol. At equal vol they earn more, but you only collect the uplift if you size up (about 1.2–1.3x gross) to LIVE's risk.
3. **Most of the out-of-sample uplift comes from one year (2024).** In 2023, a moderate year for the strategy, there was none. Year-level dispersion is large: dSR ranges from −0.06 to +0.83.
4. **Caveat:** the grids themselves were designed after seeing 2020–25, so this test is somewhat generous to the pipeline.
5. **Implication for live:** take roughly **+0.15 to +0.35 SR over LIVE**, with a meaningful chance (about 1 in 3 years) of no improvement. This is consistent with the FINAL_REPORT central estimate of +0.2 (1.4 vs 1.2). The in-sample +0.58 (2.77 vs 2.19) should not be expected.

## Task 2: realistic costs, fills and funding (full 2020-03-15..2025, 8-clock)

**Per-coin cost model.** Cost in bp = 3 + k/√(24h quote volume in $M), charged per unit of turnover. The hedge leg is charged at BTC's cost, which is about 3 bp.
- **Calibration:** k = 32.0, set so that the median held name costs 5.5 bp. The median held name has $164M of 24h volume (LIVE, clock 0, all rebalances).
- **Turnover-weighted effective cost:**

  | | LIVE | B | B-MV |
  |---|---|---|---|
  | at k | 5.00 bp | 4.85 bp | 5.13 bp |
  | at 2k | 6.99 bp | 6.70 bp | 7.25 bp |

  B-MV's minvar puts more weight on smaller, less liquid shorts, and trades more (0.47 units/day vs 0.41 for B and 0.32 for LIVE).

**Stop slippage.** At each short stop there is an extra adverse fill of X × |position|. Stopped short gross per day is 0.0084 for LIVE, 0.0229 for B and 0.0196 for B-MV. The backtest already fills at the close of the hour in which the stop is crossed, so X is on top of the modelled overshoot.

| setting | LIVE SR / bp / mdd@2% | B SR / bp / mdd@2% | B-MV SR / bp / mdd@2% | B-MV vs LIVE t_rm (dbp) | B vs LIVE t_rm | B-MV vs B t_rm |
|---|---|---|---|---|---|---|
| flat 5.5 bp (baseline) | 2.19 / 18.0 / −32.0 | 2.57 / 22.9 / −30.3 | **2.77 / 20.8 / −25.1** | 3.09 (+4.8) | 2.93 | 1.49 |
| per-coin k | 2.21 / 18.2 / −31.8 | 2.60 / 23.2 / −30.2 | 2.80 / 21.0 / −24.8 | 3.12 (+4.8) | 3.02 | 1.45 |
| per-coin 2k | 2.13 / 17.6 / −32.0 | 2.51 / 22.4 / −30.5 | 2.66 / 20.0 / −25.1 | 2.83 (+4.4) | 2.96 | 1.10 |
| slip 0.5% | 2.14 / 17.6 / −32.5 | 2.43 / 21.8 / −30.9 | 2.63 / 19.8 / −26.1 | 2.63 (+4.1) | 2.27 | 1.47 |
| slip 1% | 2.08 / 17.2 / −33.0 | 2.29 / 20.6 / −31.9 | 2.50 / 18.9 / −27.0 | 2.17 (+3.4) | 1.62 | 1.44 |
| slip 2% | 1.97 / 16.4 / −34.1 | 2.02 / 18.4 / −34.3 | 2.22 / 16.9 / −29.0 | 1.27 (+2.0) | 0.37 | 1.38 |
| per-coin k + slip 1% ("realistic") | 2.10 / 17.4 / −32.8 | 2.32 / 20.9 / −31.7 | **2.52 / 19.0 / −26.8** | 2.19 (+3.5) | 1.70 | 1.40 |
| per-coin 2k + slip 2% ("harsh") | 1.92 / 15.9 / −34.1 | 1.97 / 17.9 / −34.0 | **2.11 / 16.1 / −29.1** | 1.01 (+1.6) | 0.40 | 1.01 |
| harsh + same-day funding | 1.85 / 15.3 / −34.0 | 1.91 / 17.3 / −34.3 | 2.05 / 15.6 / −29.3 | 1.05 | 0.42 | 1.03 |

**Findings:**
- **Per-coin costs barely matter.** Effective costs are close to 5.5 bp, and the ranking and t-stats are essentially unchanged even at 2k.
- **Stop slippage is the real threat to B.** B stops out about 2.7x as much short gross as LIVE. B's risk-matched edge over LIVE falls from +3.1 bp/day (t 2.93) to +1.75 (t 1.62) at 1% slippage and to about 0 (t 0.37) at 2%. The break-even is about 2.3%.
- **B-MV is more robust.** Its edge over LIVE survives 1% slippage (t 2.2, +3.4 bp/day, 5/6 years) and is still positive at 2% (t 1.3, +2.0 bp/day). The break-even is about 3.5%. It keeps its drawdown advantage in every setting: mdd@2% of −25 to −29 vs −32 to −34 for LIVE.
- **Under the harsh setting B-MV is only marginally better than LIVE** (SR 2.11 vs 1.92, t 1.0), and B is no better than LIVE at all.

**Funding.** How it is applied in `cloud_harness`/`ext.book`:
- **Funding P&L:** P&L = −w · Fh with Fh[i] = F[i+1]/24, where F is the *prior day's* `funding_1d`, forward-filled to hours. Longs pay positive funding.
- **Guard:** it excludes shorts whose prior-day funding is below −5 bp/day. That is known at decision time, so there is no lookahead. It blocks about 2.3 of the top 20 jumpy names per rebalance (11%).
- **Contribution:** funding is about 9% of net P&L for all three books: 0.9–2.4 bp/day for LIVE by year, and 1.2–3.8 for B-MV.
- **Proxy bias:** the P&L uses the prior day's funding as a proxy for what is actually paid. Recomputing with *same-day* funding (`fund2`) gives:
  - LIVE: 0.5–2.0 bp/day, vs 0.9–2.4 with the proxy;
  - 2025: 0.9 vs 2.2 bp/day;
  - correlation between the two series: 0.59–0.71.
- **Why the proxy is biased:** the funding score and the guard select on yesterday's funding, which then mean-reverts. So the proxy overstates funding income by about 0.3–0.5 bp/day, costing about −0.06 SR for every book. Relative comparisons are unaffected.
- **Caveat:** I could not verify the day-stamp convention of `funding_1d` from the npz alone. If it is already the realized same-day sum, the harness's lag is the source of the bias described above.

## Bottom line
- **The selection process does generalize, but only about half of the in-sample uplift survives.** Pseudo-holdout uplift is +0.34 SR pooled (risk-matched t 2.6). It came in 2 of 3 years, and nearly all of it in 2024.
- **Realistic uplift of B-MV over LIVE is about +0.15 to +0.3 SR,** after:
  - out-of-sample shrinkage (about 45% retention);
  - realistic fills (per-coin costs plus 1% stop slippage, which cuts the full-sample uplift from +0.58 to +0.42 SR);
  - you must size about 1.15x to LIVE's vol to see it in dollars.
- **B-MV's edge survives realistic costs.** It is fragile only if short-stop fills gap by 2% or more on average.
- **Plain B (equal-weight shorts) is not robust to stop slippage and should not be deployed without the minvar leg.**
- **Monitor the average stop fill vs the trigger level in live trading.** If it exceeds about 2%, the case for the change largely disappears.
