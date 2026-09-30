# New signals and edges vs B (BTC-beta, funding dynamics, liquidity, seasonality)

Research only. Data 2020-03-15..2025-12-31 (2026 holdout not touched). Base **B = `ext.book(D, S0, short_frac=0.55, stop=0.2, N=12, NS=20)`**:
SR 2.69 at 5.5 bp, 2.58 at 8 bp, 2.40 at 12 bp. Every candidate was run through the risk-matched `h.partition_test` vs B and vs LIVE.

## Bottom line
**Nothing is adopted. 51 pre-registered trials, 0 passed. The best t vs B was +0.73 (near-high sleeve at a 20% risk weight), and no score-component trial had t > 0.**
- **Score blends always hurt B.** The 38 blends at w = 0.10/0.25/0.50 had mean t −1.88 (−1.59 at w = 0.10) and max −0.08. The placebo noise floor vs live is −0.92. So B sits at a locally tuned optimum, and a 10–25% perturbation of its ranks costs more than any of these features add.
- **No BTC lead-lag edge is tradable.**
  - At hourly lags 1–3 the average alt beta to *lagged* BTC is **negative** (−0.05, −0.03, −0.02). Alts over-react and partly revert. They do not catch up late.
  - The delayed-beta forecast has a rank IC of only 0.0025.
  - The "not-yet-reflected" gap (−residual over the last 1–6 h) has a positive rank IC of ~0.018 at i+2. The IC comes from the middle of the distribution, though. **Both extreme tails underperform:** the bottom 5% of 3h residual earns −2.8 bp/h and the top 5% −1.5 bp/h (`diag_rev.py`). So a reversal book loses money even before costs: −5 bp/day gross, −87 bp/day net at 1h rebalance.
  - Shorting extreme absolute movers makes about +4 bp/day gross, but turnover of 2–15×/day eats it.
- **Sleeves:**
  - Near-high sleeve: stand-alone SR 1.54, corr 0.37 with B.
  - Coin-age sleeve: SR 1.70, but corr 0.68 with B. New listings simply are the high-idio-vol names.
  - Both are real stand-alone premia that are already mostly spanned by B. Blended at 20–30% risk they give t −1.2 to +0.7 and win only 2–3 of 6 years.
- **Funding dynamics** (change, 30d z-score, 30d vol, dispersion timing) add nothing beyond the funding level already in S0.
  - The funding-dispersion gross overlay had t −4.3.
  - Its post-hoc inverse had t −0.2, and walk-forward over {B, G01, G02} picked B in 4 of 5 years: wf SR 2.37 vs 2.43.
  - The asymmetry (−4.3 vs −0.2) shows that time-varying gross mostly adds noise at matched risk. It is not a hidden inverse signal.

## Method
- **Score component:** `sc = (1-w)*S0 + w*pct(feature within D.M)` (NaN → 0.5), lower = long, same book parameters as B.
- **Sleeve:** `ext.book(D, pct(feature), every, N=NS, short_frac=.5, stop=.2)` (1h/2h/4h/8h rebalance as registered).
  - Its daily net and coin matrix are scaled to B's vol and blended: `(1-rw)*B + rw*k*S`, with pre-registered rw = 0.25 and 0.20/0.30 shown as sensitivity.
  - The blended coin matrix feeds `partition_test`.
  - Sleeves use an empty-leg-safe `leg_weights`; the default path divides by zero when the funding guard empties the short leg at hourly rebalance. Weights are otherwise identical to the default.
- **Overlay:** the hourly `gross` array of `ext.book`.
- **Causality:**
  - Every feature uses rolling windows ending at hour i.
  - Funding is `D.F` (prior-day).
  - The seasonal forecasts for the held hours i+2..i+9 use only residuals ≥ 24 h (hour-of-day) or ≥ 168 h (day-of-week) old, so the newest input is ≤ i−1.
  - The book earns `R1[i+2]`.
  - No trial had t > 3 in the favourable direction, so no leak-hunt was triggered. Lagging the G02 dispersion overlay by 24h and 72h moved its t between +0.9 and −1.1, i.e. noise, with no sign of look-ahead.
- `trials.csv` was written before each batch was run. Four rows were added mid-study and are labelled:
  - S06/S07 follow a pre-set rule: "next-best w=0.10 features get a sleeve".
  - G02 and T35/T36/S10/S11 are **post-hoc** and are marked as such.

## Trial accounting
- 38 score blends (T01–T38), 11 sleeves (S01–S11, each at rw 0.20/0.25/0.30) and 2 gross overlays (G01–G02): **51 trials**, within the 60 budget.
- Plus 6 plateau/lag-check books on G02.
- Plus 2 diagnostics that are not trials: `diag_leadlag.py` (IC and lagged betas) and `diag_rev.py` (bucket returns).

## Full trials table
Sleeve rows show the rw = 0.25 blend. `sleeve_SR` is the stand-alone sleeve and `t_rw20/30` is the blend t at rw 0.20/0.30. Regimes are the candidate − B difference in bp/day with BTC 30d up / down. SR8/SR12 are the candidate's SR at 8/12 bp cost (B: 2.58/2.40).

| id | name | params | SR | SR8 | SR12 | t_vs_B | years | groups | regimes | adopt | mdd_at2pct | minYrSR | t_vs_LIVE | sleeve_SR | corr_B | t_rw20/30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T01 | beta_chg | w=0.10; beta168-beta720; high=short | 2.39 | 2.27 | 2.08 | -2.34 | 0/6 | 2/5 | -3.3/-2.2 | False | -29.8 | 1.05 | +0.84 |  |  |  |
| T02 | beta_chg | w=0.25 | 2.09 | 1.96 | 1.76 | -3.60 | 0/6 | 1/5 | -5.9/-5.2 | False | -32.6 | 0.85 | -0.59 |  |  |  |
| T03 | beta_instab | w=0.10; std over 720h of 168h beta; high=short | 2.43 | 2.32 | 2.14 | -2.59 | 0/6 | 0/5 | -3.0/-1.7 | False | -35.5 | 0.76 | +1.29 |  |  |  |
| T04 | beta_instab | w=0.25 | 2.35 | 2.24 | 2.07 | -2.07 | 0/6 | 2/5 | -5.1/-0.6 | False | -35.6 | 0.45 | +0.68 |  |  |  |
| T05 | iskew | w=0.10; 336h skew of BTC-residual; high=short | 2.57 | 2.45 | 2.27 | -1.05 | 1/6 | 2/5 | -1.0/-1.2 | False | -33.5 | 1.21 | +2.10 |  |  |  |
| T06 | iskew | w=0.25 | 2.21 | 2.09 | 1.89 | -3.16 | 0/6 | 1/5 | -5.8/-2.7 | False | -34.9 | 0.82 | -0.02 |  |  |  |
| T07 | phi | w=0.10; residual AR1 phi (336h); high=short | 2.53 | 2.42 | 2.23 | -1.23 | 3/6 | 1/5 | -1.0/-2.1 | False | -31.4 | 0.64 | +1.79 |  |  |  |
| T08 | phi | w=0.25 | 2.22 | 2.09 | 1.89 | -2.81 | 0/6 | 1/5 | -4.8/-3.8 | False | -33.2 | 0.42 | +0.00 |  |  |  |
| T09 | fund_chg | w=0.10; F - mean(F, 7d); high=short | 2.59 | 2.46 | 2.27 | -0.98 | 1/6 | 2/5 | -2.2/+0.6 | False | -34.3 | 1.30 | +2.05 |  |  |  |
| T10 | fund_chg | w=0.25 | 2.30 | 2.13 | 1.88 | -2.23 | 2/6 | 0/5 | -5.2/-1.7 | False | -32.1 | 1.59 | +0.39 |  |  |  |
| T11 | fund_z30 | w=0.10; (F-mean30d)/std30d; high=short | 2.61 | 2.48 | 2.28 | -0.71 | 2/6 | 1/5 | -1.2/-0.3 | False | -35.1 | 1.07 | +2.09 |  |  |  |
| T12 | fund_z30 | w=0.25 | 2.41 | 2.25 | 2.00 | -1.42 | 2/6 | 0/5 | -4.0/-0.8 | False | -32.3 | 1.29 | +0.99 |  |  |  |
| T13 | fund_vol | w=0.10; std(F,30d); high=short | 2.55 | 2.44 | 2.26 | -1.24 | 2/6 | 2/5 | -1.6/-0.9 | False | -34.9 | 0.81 | +1.86 |  |  |  |
| T14 | fund_vol | w=0.25 | 2.54 | 2.42 | 2.23 | -0.83 | 1/6 | 2/5 | -1.0/-1.9 | False | -33.9 | 1.22 | +1.39 |  |  |  |
| T15 | amihud | w=0.10; -mean(/r//qv,336h); illiquid=long | 2.33 | 2.21 | 2.02 | -2.64 | 1/6 | 1/5 | -4.2/-2.2 | False | -40.8 | 0.14 | +0.60 |  |  |  |
| T16 | amihud | w=0.25 | 2.31 | 2.19 | 1.99 | -1.98 | 0/6 | 0/5 | -3.8/-3.1 | False | -33.0 | 0.73 | +0.45 |  |  |  |
| T17 | turn_trend | w=0.10; log(Q168/Q720); high=short | 2.50 | 2.38 | 2.20 | -1.74 | 2/6 | 1/5 | -0.6/-3.2 | False | -33.8 | 1.01 | +1.52 |  |  |  |
| T18 | turn_trend | w=0.25 | 2.04 | 1.91 | 1.72 | -3.92 | 1/6 | 0/5 | -8.1/-3.4 | False | -34.2 | 0.64 | -0.82 |  |  |  |
| T19 | age | w=0.10; -(hours since first close); young=short | 2.62 | 2.51 | 2.33 | -0.58 | 1/6 | 2/5 | -1.9/+0.9 | False | -38.0 | 1.06 | +2.27 |  |  |  |
| T20 | age | w=0.25 | 2.51 | 2.41 | 2.24 | -1.01 | 2/6 | 2/5 | -3.5/+0.8 | False | -50.5 | 0.90 | +1.40 |  |  |  |
| T21 | volvol_div | w=0.10; log(idio168/idio720)-log(Q168/Q720); high=short | 2.54 | 2.43 | 2.25 | -1.20 | 2/6 | 1/5 | -2.6/+0.1 | False | -36.8 | 0.77 | +1.71 |  |  |  |
| T22 | volvol_div | w=0.25 | 2.44 | 2.32 | 2.13 | -1.32 | 1/6 | 2/5 | -3.5/-0.8 | False | -44.0 | 0.57 | +0.94 |  |  |  |
| T23 | hod_season | w=0.10; sum over the next held hours (i+2..i+9) of each coin's 30d same-hour mean residual; high=long | 2.57 | 2.45 | 2.26 | -1.14 | 1/6 | 1/5 | -1.9/-0.2 | False | -29.9 | 1.37 | +1.91 |  |  |  |
| T24 | hod_season | w=0.25 | 2.68 | 2.49 | 2.20 | -0.08 | 2/6 | 3/5 | +2.8/-3.8 | False | -31.8 | 1.50 | +1.88 |  |  |  |
| T25 | dow_season | w=0.10; same with 12-week same-weekday-hour mean residual; high=long | 2.57 | 2.45 | 2.26 | -1.05 | 1/6 | 2/5 | -0.9/-1.3 | False | -37.5 | 1.21 | +2.05 |  |  |  |
| T26 | dow_season | w=0.25 | 2.38 | 2.19 | 1.88 | -2.19 | 1/6 | 1/5 | -3.7/-1.8 | False | -34.1 | 1.07 | +0.84 |  |  |  |
| T27 | btc_delay | w=0.10; sum of 336h lag-1..3 BTC betas; high=long | 2.57 | 2.45 | 2.27 | -1.07 | 3/6 | 2/5 | -1.4/-0.9 | False | -37.5 | 1.06 | +2.00 |  |  |  |
| T28 | btc_delay | w=0.25 | 2.50 | 2.38 | 2.19 | -1.05 | 2/6 | 1/5 | -1.9/-1.5 | False | -37.8 | 1.23 | +1.30 |  |  |  |
| T29 | coskew | w=0.10; 720h mean(e*rb^2)/(sd e*var rb); high=short | 2.32 | 2.20 | 2.02 | -3.17 | 1/6 | 1/5 | -5.2/-1.2 | False | -35.0 | 0.17 | +0.53 |  |  |  |
| T30 | coskew | w=0.25 | 2.24 | 2.13 | 1.95 | -2.50 | 1/6 | 0/5 | -4.4/-3.8 | False | -31.8 | 0.68 | +0.13 |  |  |  |
| S01 | rev3_h1 | score=3h resid sum, every=1, N=NS=12, sf .5, stop .2; 25% risk weight vs B | -0.30 | -1.64 | -3.77 | -17.77 | 0/6 | 0/5 | -28.0/-26.7 | False | -203.7 | -2.20 | -10.30 | -9.03 | -0.03 | -17.61/-17.93 |
| S02 | rev6_h2 | score=6h resid sum, every=2, N=NS=12 | 1.02 | 0.27 | -0.92 | -11.00 | 0/6 | 0/5 | -15.7/-14.9 | False | -51.7 | -0.45 | -5.18 | -4.88 | -0.01 | -10.82/-11.18 |
| S03 | rev6_h4 | score=6h resid sum, every=4, N=NS=12 | 1.30 | 0.71 | -0.25 | -9.55 | 0/6 | 0/5 | -12.8/-12.7 | False | -49.3 | -0.15 | -4.09 | -4.00 | -0.03 | -9.34/-9.76 |
| S04 | age_sleeve | score=-age, every=8, N=NS=20, sf .5, stop .2; 25% risk weight | 2.61 | 2.49 | 2.30 | -1.02 | 2/6 | 2/5 | -0.9/-0.6 | False | -31.3 | 1.26 | +2.14 | 1.70 | +0.68 | -0.90/-1.15 |
| S05 | fundz_sleeve | score=fund_z30, every=8, N=NS=20; 25% risk weight | 2.59 | 2.40 | 2.09 | -0.69 | 2/6 | 2/5 | -2.4/+1.0 | False | -32.5 | 1.11 | +1.90 | 0.24 | +0.05 | -0.47/-0.93 |
| S06 | fund_chg_sleeve | pre-registered rule (best T-features at w=0.10 by t vs B get a 25% sleeve; age and fund_z30 already = S04/S05 so next in line): fund_chg, every=8, N=NS=20 | 2.45 | 2.25 | 1.92 | -1.88 | 1/6 | 1/5 | -3.2/-1.1 | False | -33.2 | 0.97 | +1.22 | -0.04 | +0.13 | -1.67/-2.11 |
| S07 | dow_season_sleeve | next in line after fund_chg (t -1.0522 vs iskew -1.0525): dow_season, every=8, N=NS=20 | 2.12 | 1.64 | 0.88 | -4.14 | 1/6 | 3/5 | -6.6/-3.6 | False | -34.3 | 0.63 | -0.44 | -1.49 | -0.06 | -3.92/-4.38 |
| T31 | near_high | w=0.10; log C - log max(C,720h), negated; near 30d high=long | 2.45 | 2.34 | 2.16 | -1.99 | 0/6 | 2/5 | -2.8/-1.5 | False | -31.6 | 1.27 | +1.23 |  |  |  |
| T32 | near_high | w=0.25 | 2.54 | 2.43 | 2.25 | -0.82 | 2/6 | 2/5 | -1.1/-1.7 | False | -29.6 | 1.57 | +1.48 |  |  |  |
| T33 | jump_beta | w=0.10; 720h beta on hours /rb/>2sd minus beta on other hours, negated; high jump beta=long | 2.54 | 2.43 | 2.25 | -1.31 | 1/6 | 0/5 | -2.4/-0.2 | False | -29.6 | 1.08 | +1.96 |  |  |  |
| T34 | jump_beta | w=0.25 | 2.20 | 2.09 | 1.91 | -2.51 | 1/6 | 2/5 | -2.7/-6.8 | False | -34.0 | 0.71 | -0.07 |  |  |  |
| S08 | near_high_sleeve | near_high as own book every=8 N=NS=20; 25% risk weight | 2.75 | 2.62 | 2.40 | +0.54 | 3/6 | 3/5 | +2.6/-2.0 | False | -29.5 | 1.35 | +2.75 | 1.54 | +0.37 | +0.73/+0.34 |
| S09 | jump_beta_sleeve | jump_beta as own book every=8 N=NS=20; 25% risk weight | 2.46 | 2.33 | 2.12 | -2.16 | 1/6 | 0/5 | -1.5/-2.9 | False | -32.1 | 1.22 | +1.24 | 0.63 | +0.42 | -1.99/-2.34 |
| G01 | fund_disp_gross | B with hourly gross = clip(xs std of funding in M / its 90d rolling median, 0.5, 1.5) | 2.10 | 1.93 | 1.66 | -4.33 | 0/6 | 0/5 | -6.3/-4.4 | False | -35.2 | 0.79 | -0.57 |  |  |  |
| G02 | fund_disp_gross_inv | POST-HOC (after G01 gave t -4.3): gross = clip(90d median / disp, 0.5, 1.5); validated only via walk-forward over {B, G01, G02} and plateau | 2.66 | 2.48 | 2.19 | -0.21 | 3/6 | 3/5 | -0.1/-0.5 | False | -35.9 | 1.63 | +nan |  |  |  |
| T35 | absmove6 | w=0.10; /6h residual sum/; high=short. NOTE: motivated by diag_rev.py (full-sample bucket means), so partly data-snooped | 2.39 | 2.27 | 2.07 | -2.60 | 1/6 | 1/5 | -3.5/-1.9 | False | -36.4 | 0.56 | +0.99 |  |  |  |
| T36 | absmove6 | w=0.25 | 2.04 | 1.88 | 1.60 | -3.80 | 1/6 | 2/5 | -6.6/-5.1 | False | -38.0 | 0.58 | -0.84 |  |  |  |
| S10 | absmove6_h4 | score=/6h resid/, every=4, N=NS=12, 25% risk weight | 1.36 | 0.81 | -0.07 | -11.96 | 0/6 | 0/5 | -14.1/-9.9 | False | -35.5 | -0.16 | -4.93 | -3.18 | +0.51 | -11.88/-12.04 |
| S11 | absmove24_h8 | score=/24h resid/, every=8, N=NS=20, 25% risk weight | 2.10 | 1.82 | 1.36 | -5.74 | 0/6 | 1/5 | -5.4/-5.4 | False | -33.2 | 0.30 | -0.60 | -0.52 | +0.49 | -5.60/-5.88 |
| T37 | idio_2f | w=0.25; 336h std of residual after BTC and ETH (ETH-residual factor, 168h betas); high=short | 2.38 | 2.26 | 2.08 | -2.65 | 2/6 | 1/5 | -3.9/-1.6 | False | -31.1 | 0.82 | +0.91 |  |  |  |
| T38 | idio_2f | w=0.50 | 2.29 | 2.18 | 2.01 | -2.78 | 1/6 | 1/5 | -5.7/-1.1 | False | -31.6 | 0.70 | +0.38 |  |  |  |

## G02 plateau and lag checks (post-hoc inverse funding-dispersion gross)
| variant | SR | t vs B | years |
|---|---|---|---|
| G02 (90d median, clip .5–1.5) | 2.66 | −0.21 | 3/6 |
| median 30d / 180d | 2.44 / 2.64 | −1.77 / −0.33 | 1/6, 4/6 |
| clip .67–1.33 / .33–2.0 | 2.75 / 2.50 | +0.51 / −0.93 | 3/6, 2/6 |
| lagged 24h / 72h | 2.84 / 2.50 | +0.86 / −1.10 | 3/6, 2/6 |
| walk-forward {B, G01, G02} | wf SR 2.37 vs B 2.43 | −0.63 | picks B in 4/5 years |

## Near-misses worth knowing about (not adoptable)
- **Near-30d-high sleeve (S08):**
  - Long names near their 720h high, short names far below it, 20/20, 8h.
  - Stand-alone SR 1.54, 12 bp/day, turnover 0.45/day, corr 0.37 with B.
  - At rw 0.20 the blend has SR 2.76 vs 2.69 and t +0.73, but wins only 3/6 years and 3/5 coin groups and loses in BTC-down regimes.
  - It is the only genuinely low-correlation positive edge found. Its t is well inside the placebo band, max 1.79.
- **Coin-age sleeve (S04):**
  - Short the youngest listings, long the oldest. Stand-alone SR 1.70, but corr 0.68 with B, so it adds nothing (t −1.0).
  - As a score blend at w = 0.25 it raises MDD at 2% vol from −30% to −50%.
- **hod_season at w = 0.25 (T24):** t −0.08, 2/6 years. Noise.

## Honest caveats
- The main risk in this study is **false negatives from the blending design**. The placebo study showed that *any* 10% perturbation of S0 costs about 0.9 t. A feature with a small real edge therefore needs t ≈ +1 of standalone value just to break even inside a blend. Sleeves avoid that, but they only win if they are both good and uncorrelated, and none was good enough.
- The coin-age feature is left-censored: coins listed before 2020-03 all look "old" in 2020. This mainly affects the 2020 ranks.
- The two-factor idio (T37/T38) uses sequential BTC-then-ETH residualisation with rolling betas. That is an approximation to a joint OLS.
- Several features in this list are mutually correlated (e.g. absmove, iskew and idio vol), so the 51 trials are not 51 independent tests. That doesn't matter here, since none passed.

## Files
- `feats.py`: all feature definitions, causal.
- `run_scores.py`: score blends.
- `run_sleeves.py`: sleeves and blends.
- `run_gross.py`, `run_gross2.py`: overlays, walk-forward and plateau.
- `diag_leadlag.py`, `diag_rev.py`: diagnostics.
- `fill.py`: builds the table.
- Results pickles: `scores.pkl`, `sleeves.pkl`, `gross*.pkl`, `B.pkl`, `LIVE.pkl`.

## Recommendation
Keep B unchanged. The BTC-beta family (lead-lag, beta change, beta instability, jump beta, price delay, coskewness) is now exhausted on top of the earlier BAB, 720h and downside-beta tests. None of it beats the existing hedge-plus-idio-vol book. If more research time is spent, the only lead is the near-high sleeve. Test it on the 2026 holdout as a stand-alone book, not as a blend, before investing more trials.
