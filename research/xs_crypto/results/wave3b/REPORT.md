# Wave 3b: leg-specific scores, parameter ensembles, minvar plateau (vs B-MV)

Research only. Data 2020-03-15..2025-12-31 (the 2026 holdout was not touched). Every book is **8-clock averaged** (rebalance offsets 0–7, with daily dfs and float32 coin matrices averaged). Costs are 5.5 bp. SR is also shown at 8 and 12 bp. The t statistic is the risk-matched `h.partition_test` t_NW vs B-MV. CVaR5 is the mean of the worst 5% of days after scaling to B-MV's daily vol. dCVaR = B-MV CVaR − candidate CVaR, so positive means better. Everything was pre-registered in `trials.csv` before it ran.

**Base B-MV (recomputed):** SR **2.77** (2.62 at 8 bp, 2.36 at 12 bp), mdd@2% −25.1, minYrSR 1.74, CVaR5 297.0 bp. It reproduces `wave2/s3_floor.pkl` exactly (max |Δnet| 2e−17). The leg split is long −1.2 / short +18.1 / hedge +4.5 bp/day.

## Bottom line
- **Leg-specific scores: all 3 fail.** A pure-idio long score and a higher short-side funding weight both hurt (t −0.8 to −2.1).
- **Idio-window ensemble E1 (168/336/720): fails.** SR 2.66, t −1.03, minYrSR 1.34, CVaR not better.
- **N-long ensemble E2 (8/12/16) formally passes the pre-declared ensemble rule:**
  - SR 2.83 (2.67 / 2.41 at 8 / 12 bp), t +1.58, minYrSR 1.84 vs 1.74, 5/6 years, dCVaR +1.3 bp.
  - The CVaR gain is only 0.4%, which is noise. For comparison, B-MV's own CVaR gain over B was 13.3 bp against a null 95th percentile of 7.1.
  - The plateau is one-sided. {6,12,18} still passes (t +1.50, dCVaR +1.4), but {10,12,14} fails (t −0.37, dCVaR −1.1, minYrSR 1.68).
  - What E2 really contains is a *mean* effect from fewer longs, not risk reduction (see the N-family below).
  - **My recommendation is not to adopt E2 as a "risk reducer".** If anything is taken forward, it is the finding that fewer longs are better, as a holdout hypothesis.
- **Minvar plateau:** SR ranges 2.65–2.82 across the 8 one-step neighbours, and every one is above B's 2.57.
  - **Worst neighbour: cap 1.5×** (SR 2.65, t −2.80, minYrSR 1.53).
  - The worst minYrSR is **cov window 168h** (1.13; 2021 is weak) with dCVaR −5.1.
  - So B-MV sits on a reasonable SR plateau, but its tail-risk benefit is window-sensitive: 168h and 720h both lose CVaR.
  - Shrink 0.25 and cap 3× pass the partition test (t +1.69 / +1.59). This is robustness information only; nothing is selected, per the pre-registration.

## Part 1: leg-specific scores (longs from ascending long score, shorts from descending short score; `ext3b.book(score_short=...)`)
| id | long fw / short fw | SR | SR 8/12 bp | t vs B-MV | yrs | grp | regime up/dn bp | mdd@2% | minYrSR | CVaR5 | dCVaR | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 0 / 0.25 | 2.56 | 2.41 / 2.16 | −2.11 | 1/6 | 3/5 | −2.3/−0.7 | −32.2 | 1.37 | 302.0 | −5.0 | FAIL |
| L2 | 0 / 0.40 | 2.57 | 2.40 / 2.13 | −1.31 | 2/6 | 2/5 | −0.5/−2.8 | −28.0 | 1.16 | 309.1 | −12.2 | FAIL |
| L3 | 0.25 / 0.40 | 2.67 | 2.50 / 2.22 | −0.79 | 2/6 | 2/5 | +0.1/−1.8 | −28.6 | 1.13 | 302.9 | −6.0 | FAIL |

- **Funding tilt on longs helps.** Dropping it (L1) costs −5.6 bp/day in 2020 and −3.3 in 2021, and the long leg goes from −1.2 to −1.7 bp/day.
- **Short fw 0.40 does the opposite of the earlier sweeps.** It *loses* in 2020–23 (−1 to −6 bp/day) and wins only in 2024–25 (+1 to +3). The old "fw 0.4–0.5 looked better in 2020-22" does not survive at the B-MV construction level. It also worsens CVaR by 6–12 bp, because crowded-funding shorts are the squeeze-prone ones.

## Part 2: ensembles (1/3 average of daily df and coin matrices)
| id | members | SR | SR 8/12 bp | t vs B-MV | yrs | grp | regime up/dn | mdd@2% | minYrSR | CVaR5 | dCVaR | ensemble rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | idio L 168/336/720 | 2.66 | 2.50 / 2.23 | −1.03 | 2/6 | 2/5 | +0.3/−2.3 | −29.7 | 1.34 | 297.3 | −0.3 | FAIL |
| **E2** | **N long 8/12/16** | **2.83** | **2.67 / 2.41** | **+1.58** | 5/6 | 3/5 | +0.9/−0.1 | −25.3 | **1.84** | 295.7 | **+1.3** | **formal PASS** |
| E2a (plateau) | N 6/12/18 | 2.85 | 2.69 / 2.43 | +1.50 | 5/6 | 3/5 | +1.1/−0.1 | −24.9 | 1.81 | 295.6 | +1.4 | holds |
| E2b (plateau) | N 10/12/14 | 2.76 | 2.60 / 2.35 | −0.37 | 2/6 | 2/5 | +0.2/−0.4 | −23.2 | 1.68 | 298.1 | −1.1 | fails |

**Ensemble components** (not trials, shown for interpretation):

| member | SR | SR 8/12 bp | t vs B-MV | yrs | grp | adopt | mdd@2% | minYrSR | CVaR5 | long bp/day |
|---|---|---|---|---|---|---|---|---|---|---|
| idio L=168 | 2.17 | 1.99 / 1.72 | −3.27 | 1/6 | 0/5 | F | −31.2 | 0.82 | 308.4 | −0.7 |
| idio L=720 | 2.61 | 2.47 / 2.24 | −0.70 | 1/6 | 3/5 | F | −37.7 | 1.11 | 300.9 | −0.2 |
| N=6 | 2.96 | 2.79 / 2.53 | +1.67 | 5/6 | 3/5 | F | −23.8 | 1.81 | 289.5 | +0.6 |
| N=8 | 2.95 | 2.78 / 2.52 | +2.06 | 5/6 | 4/5 | **T** | −25.5 | 1.83 | 294.8 | −0.2 |
| N=10 | 2.86 | 2.70 / 2.44 | +1.17 | 4/6 | 2/5 | F | −23.2 | 1.77 | 296.6 | −1.2 |
| N=12 (B-MV) | 2.77 | 2.62 / 2.36 | – | – | – | – | −25.1 | 1.74 | 297.0 | −1.2 |
| N=14 | 2.61 | 2.45 / 2.20 | −3.10 | 0/6 | 2/5 | F | −25.0 | 1.29 | 299.8 | −2.2 |
| N=16 | 2.69 | 2.53 / 2.28 | −1.18 | 2/6 | 1/5 | F | −25.1 | 1.56 | 299.4 | −2.1 |
| N=18 | 2.72 | 2.56 / 2.31 | −0.75 | 3/6 | 1/5 | F | −25.3 | 1.52 | 300.2 | −1.9 |

- **E1 does not work.** L=336 is clearly the best window, and 168h is poor (SR 2.17). Averaging in worse members dilutes the book without reducing tail risk.
- The L-component scores use AR1-corrected idio exactly as in `common.py`, with phi and std on the same window L and min_periods 0.6L. Book eligibility stays at 336h. At L=336 this reproduces S0 except for 44 cells, where min_periods is 201 instead of 200.
- **N family:** SR declines roughly monotonically in N from 6 to 14 (2.96 → 2.61), with a noisy bump at 16–18. The long leg becomes less negative with fewer, calmer names: +0.6 bp/day at N=6 vs −1.2 at N=12.
  - The walk-forward over N∈{6,…,18} (and over {8,12,16}) **picks N=8 in all 5 years**: wf SR 2.79 vs B-MV 2.59 over 2021-25, t +2.34.
  - **N=8 alone passes the full adoption bar** (partition adopt=True, t 2.06), **but it was not pre-registered as a stand-alone trial.**
  - N was already tuned 20→12 on this data, and 2.06 is only slightly above the placebo max of 1.79. So this is a post-hoc lead, not an adoption.
  - Notional is fine at N=8: $330 × 1.4 × 0.45 / 8 ≈ $26 per long.

## Part 3: minvar plateau (one step each side of shrink 0.5 / cov 336h / floor 0.4e / cap 2e)
| id | change | SR | SR 8/12 bp | t vs B-MV | yrs | grp | partition adopt | mdd@2% | minYrSR | CVaR5 | dCVaR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | shrink 0.25 | 2.82 | 2.65 / 2.40 | +1.69 | 5/6 | 5/5 | True | −25.2 | 1.75 | 296.3 | +0.7 |
| P2 | shrink 0.75 | 2.72 | 2.56 / 2.32 | −1.95 | 2/6 | 0/5 | False | −24.7 | 1.65 | 298.2 | −1.2 |
| P3 | cov 168h | 2.68 | 2.51 / 2.25 | −0.93 | 2/6 | 2/5 | False | −26.5 | **1.13** | 302.1 | −5.1 |
| P4 | cov 720h | 2.70 | 2.55 / 2.30 | −0.87 | 3/6 | 1/5 | False | −25.1 | 1.80 | 300.9 | −3.9 |
| P5 | floor 0.3e | 2.76 | 2.60 / 2.34 | −0.89 | 2/6 | 2/5 | False | −25.8 | 1.72 | 296.1 | +0.9 |
| P6 | floor 0.5e | 2.79 | 2.63 / 2.39 | +0.72 | 3/6 | 3/5 | False | −24.4 | 1.72 | 298.0 | −1.0 |
| P7 | cap 1.5e | **2.65** | 2.51 / 2.27 | **−2.80** | 1/6 | 2/5 | False | −24.1 | 1.53 | 299.0 | −2.0 |
| P8 | cap 3e | 2.82 | 2.66 / 2.40 | +1.59 | 5/6 | 4/5 | True | −24.3 | 1.80 | 295.8 | +1.2 |

- **Worst neighbour by SR/t:** cap 1.5e (2.65, t −2.80).
- **Worst by minYrSR and CVaR:** cov 168h (1.13, dCVaR −5.1).
- **Direction of the neighbours:**
  - Less shrink and a higher cap (moving toward pure minvar) are mildly better.
  - Moving toward equal weight (more shrink, lower cap) is worse.
  - This is consistent with the covariance information being real.
- **Window sensitivity:** the covariance window matters for tails. Both 168h and 720h give up 4–5 bp of CVaR, so the 336h choice carries some luck.
- No neighbour is adopted; this was a robustness check only.

## Trial accounting
- **15 registered trials:** L1–L3, E1, E2, P1–P8, and E2a/E2b. E2a/E2b were registered after seeing E2, as its plateau.
- **Not counted as trials:** 1 reference (BASE) and 1 diagnostic (the walk-forward).
- **Book count:** about 170 individual books, including the ensemble components.

## Recommendation
- Keep **B-MV** as specified. None of the pre-registered structural changes gives a credible improvement.
- E2 passes the ensemble rule only on a 1.3 bp CVaR margin, and its plateau fails on one side.
- The one new lead is **fewer longs (N≈8)**. It has walk-forward support (picked 5/5 years, t +2.34) and passes the partition test post hoc, but it comes on top of an earlier N tuning.
- Put N=8 vs N=12 on the 2026 holdout alongside B-MV vs LIVE, rather than adopting it in-sample. If you want a hedge between the two, E2's graded long weights are the conservative way to express it. Implement it as one book with summed target weights; do not run three sub-books with ~$4 slices.

## Files
- `ext3b.py`: ext3.book plus `score_short`.
- `w3lib.py`: parameterised `make_mv`, avg8, evaluate, and the B-MV reference.
- `run1.py`–`run4.py` and their logs.
- `res1..4.pkl`: result dicts with daily dfs.
- `BMV.pkl` and `coin_BMV.npy`: the B-MV 8-clock reference.
- `trials.csv`.
- `fill.py`.
