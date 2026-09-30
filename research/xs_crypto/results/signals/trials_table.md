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