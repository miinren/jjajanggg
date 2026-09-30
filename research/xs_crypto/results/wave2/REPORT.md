# Wave 2: risk-weighted short leg (placebo-tested) and universe breadth

All numbers use 8-clock-averaged books, 2020-03-15..2025-12-31. The pre-registration is in PREREG.md and all trials are in trials.csv.

- **B (8-clock):** SR 2.57 (2.45 at 8 bp, 2.27 at 12 bp); mdd@2% −30.3; minYrSR 1.29; CVaR5 366.8 bp at matched vol.

## Part 1: short-leg weighting vs a placebo null
- **Null:** short weights ∝ exp(σ·z_coin), with σ matched to each candidate's weight dispersion; 60 seeds, each seed a full 8-clock average.
- **Pre-registered rule:** dCVaR must exceed the null's 95th percentile, risk-matched t vs B ≥ −0.5, and minYrSR ≥ B's.

| | SR | SR 8/12 bp | t vs B | mdd@2% | minYrSR | dCVaR (bp) | null 95th pct | verdict |
|---|---|---|---|---|---|---|---|---|
| minvar (T19) | 2.72 | 2.55 / 2.29 | +0.85 | −26.6 | 1.74 | +15.6 | 7.1 (p 0/60) | PASS, but 18% of shorts are < $5 at $330 |
| invvol (T17) | 2.64 | 2.50 / 2.29 | +0.86 | −25.4 | 1.44 | +6.4 | 5.7 (p 2/60) | marginal pass |
| **minvar with a floor of 0.4× equal weight (s3_floor.py; ≥ $5 per short)** | **2.77** | **2.62 / 2.36** | **+1.49** (4/6 yrs, 4/5 grp) | **−25.1** | **1.74** | **+13.3** | 7.1 (mv null; floor CV 0.52 vs 0.60) | **PASS; tradable** |

- **Random reweighting hurts on average:** the mv-null mean is SR 2.37 and dCVaR −2.7. The gain comes from the covariance information.
- **Caveats:**
  - The metric was chosen after the drawdown wave had flagged minvar, and minvar was picked from about 46 trials.
  - The absolute CVaR gain is modest (−4%); the visible gains rest on a few events (2022-06-13, Oct–Nov 2021).
  - The 8 clocks are correlated with each other.
  - The floored variant was a single post-hoc practicality trial.

## Part 2: universe breadth (lq > 0.5 / 0.6 / 0.75, and longs top-1/3 with shorts lq > 0.5)
- Nothing is adopted. The best is U50 at SR 2.61 (t +0.22, 2/5 coin groups, BTC-down −7.8 bp/day). U60 is 2.27 and U75 is 2.14.
- The walk-forward is flat (2.31 vs 2.31). The results are non-monotone, which points to noise. Keep the top-1/3 liquidity mask.
