# Drawdown / consistency research on B (research only, 2020-03-15 to 2025-12-31; the 2026 holdout was not touched)

**Base B** = `ext.book(D, S0, short_frac=0.55, stop=0.2, N=12, NS=20)`: SR 2.69, mdd_at2pct −29.96%, minYrSR 1.41, SR 2.58 at 8 bp and 2.40 at 12 bp, worst day −1888 bp (2022-06-13).
**LIVE** = `ext.book(D, S0)`: SR 2.22, mdd_at2pct −33.12%, minYrSR 0.85.

## Bottom line
- **46 of 60 trials were run. None was adopted.** No trial reached t_NW ≥ 2.0 vs B. The best t was 1.31, from `short_invvol_p0.5`, which is below the placebo maximum of 1.79. Only one trial won ≥5/6 years, and none passed the full partition test.
- **The one consistent near-miss is risk-weighting the short leg** (T17, T19, T42–T46: inverse residual vol, or minimum variance on the 336h residual covariance).
  - All 7 variants have SR 2.76–2.90 (B 2.69) and risk-matched t 0.7–1.3. Most improve minYrSR (1.48–1.83 vs 1.41) and cut the vol-matched worst day roughly in half (2022-06-13: −750 vs −1890 bp).
  - They do not raise risk-matched mean enough to pass. The family walk-forward gives SR 2.49 vs 2.43 for base, but the raw-mean t is −1.77, because these variants lower both vol and mean.
  - **It fails the adoption bar and is not adopted.** It is the only idea worth a second look as a *risk* improvement (see §3).
- **Important side finding: B's 8h rebalance clock is the luckiest of the 8 possible clocks.** Shifting the rebalance hour by 1–7 h gives SR 2.23–2.62 (mean over all 8 clocks 2.51), mdd_at2pct −29 to −39%, and minYrSR 0.90–1.41.
  - B's headline SR and drawdown are therefore about 0.15–0.2 SR and a few MDD points optimistic from timing luck alone.
  - This also explains why tranching (T33/T34) *lowers* SR vs B: it averages B's lucky clock with unluckier ones. It is not evidence that tranching hurts.
- Hedge-tail fixes did not work. Crash-conditional, downside, 4h, Dimson and BTC+ETH betas reduced the 2022-06-13 loss in some cases (crash beta −1465, downside beta −1297 vs −1888), but every one lost on average. Dimson and BTC+ETH were clearly worse (t −3.2 / −2.1).
- Squeeze vetoes did not work. Recent residual up-move, volume surge, liquidity rank, a tighter funding guard, longer bans after stops, and a residual-return stop were all flat or worse. Liquidity restriction was strongly negative, which confirms that the alpha sits in the less-liquid jumpy names.
- Exposure overlays did not work either: dispersion, aggregate funding (crowding), and the alt-season indicator on gross or on the short leg only. This matches the earlier failures of vol targeting, DD throttles and BTC-trend throttles: **no timing overlay reduces drawdown at equal risk.**

## 1. Full trials table (pre-registered in `trials.csv` with rationale before running)
t_vs_B, years, groups and regimes come from `h.partition_test(D, cand, B)` (risk-matched). mdd_at2pct and minYrSR come from `common.stats()`. worst_day_bp is raw, not vol-matched. to/day = turnover.

| id | name | family | SR | t_vs_B | years | groups | regimes_up_dn | adopt | mdd_at2pct | minYrSR | t_vs_LIVE | SR8bp | SR12bp | worst_day_bp | to/day |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T01 | sq_r72z_1.5 | SQZ_R72 | 2.699 | 0.05 | 3/6 | 2/5 | -0.10/0.26 | False | -31.7 | 1.3 | 2.49 | 2.57 | 2.37 | -1859 | 0.426 |
| T02 | sq_r72z_2.0 | SQZ_R72 | 2.693 | -0.0 | 3/6 | 3/5 | 0.23/-0.29 | False | -32.09 | 1.62 | 2.57 | 2.57 | 2.38 | -1760 | 0.413 |
| T03 | sq_r72z_2.5 | SQZ_R72 | 2.695 | 0.02 | 2/6 | 1/5 | -0.82/1.08 | False | -29.11 | 1.49 | 2.86 | 2.58 | 2.39 | -1888 | 0.410 |
| T04 | sq_vsurge_3 | SQZ_VOL | 2.542 | -0.96 | 2/6 | 0/5 | -1.50/-1.24 | False | -34.65 | 1.39 | 1.6 | 2.42 | 2.22 | -1532 | 0.409 |
| T05 | sq_vsurge_5 | SQZ_VOL | 2.743 | 0.39 | 3/6 | 3/5 | 1.21/-0.47 | False | -29.35 | 1.27 | 2.78 | 2.63 | 2.44 | -1551 | 0.400 |
| T06 | sq_liq_0.80 | SQZ_LIQ | 1.855 | -3.51 | 0/6 | 0/5 | -8.64/-6.46 | False | -45.4 | 0.21 | -1.32 | 1.73 | 1.54 | -2728 | 0.437 |
| T07 | sq_liq_0.90 | SQZ_LIQ | 1.343 | -3.96 | 0/6 | 0/5 | -14.58/-9.57 | False | -53.76 | 0.11 | -2.47 | 1.22 | 1.02 | -3226 | 0.527 |
| T08 | sq_guard_-2bp | SQZ_GUARD | 2.447 | -2.13 | 1/6 | 1/5 | -1.46/-3.24 | False | -39.15 | 0.84 | 1.19 | 2.33 | 2.14 | -2826 | 0.438 |
| T09 | sq_guard_0 | SQZ_GUARD | 2.518 | -1.26 | 0/6 | 3/5 | -1.54/-1.68 | False | -35.37 | 1.16 | 1.52 | 2.38 | 2.17 | -2104 | 0.485 |
| T10 | ban_24h | BAN | 2.683 | -0.09 | 4/6 | 2/5 | -1.26/1.38 | False | -29.44 | 1.6 | 2.56 | 2.57 | 2.38 | -1676 | 0.406 |
| T11 | ban_72h | BAN | 2.639 | -0.37 | 3/6 | 2/5 | -1.69/1.02 | False | -30.49 | 1.56 | 2.09 | 2.52 | 2.33 | -1612 | 0.404 |
| T12 | ban_168h | BAN | 2.572 | -0.56 | 3/6 | 2/5 | -4.50/3.15 | False | -39.25 | 1.45 | 1.41 | 2.45 | 2.25 | -854 | 0.402 |
| T13 | rstop_0.15 | RSTOP | 2.573 | -0.95 | 1/6 | 1/5 | -2.36/0.49 | False | -37.96 | 0.95 | 2.15 | 2.45 | 2.26 | -1043 | 0.422 |
| T14 | rstop_0.20 | RSTOP | 2.507 | -1.43 | 3/6 | 0/5 | -2.06/-1.24 | False | -38.83 | 0.68 | 1.94 | 2.4 | 2.22 | -1127 | 0.393 |
| T15 | rstop_0.25 | RSTOP | 2.553 | -1.02 | 2/6 | 1/5 | -1.93/-0.46 | False | -36.66 | 0.96 | 2.45 | 2.45 | 2.28 | -1386 | 0.373 |
| T16 | ladder_10_20 | single | 2.698 | 0.21 | 2/6 | 4/5 | 0.01/0.10 | False | -29.89 | 1.5 | 2.93 | 2.57 | 2.35 | -1802 | 0.468 |
| T17 | short_invvol | single | 2.776 | 0.99 | 4/6 | 3/5 | 0.53/1.07 | False | -28.92 | 1.54 | 3.03 | 2.65 | 2.44 | -1123 | 0.423 |
| T18 | short_clusterw | single | 2.77 | 0.95 | 4/6 | 4/5 | 0.33/1.18 | False | -30.05 | 1.51 | 3.35 | 2.65 | 2.45 | -2068 | 0.462 |
| T19 | short_minvar | single | 2.837 | 0.76 | 4/6 | 3/5 | 0.40/2.49 | False | -29.63 | 1.59 | 2.67 | 2.68 | 2.42 | -760 | 0.481 |
| T20 | hedge_crashbeta | single | 2.684 | -0.1 | 2/6 | 5/5 | -0.68/0.67 | False | -31.42 | 1.34 | 2.51 | 2.59 | 2.44 | -1465 | 0.324 |
| T21 | hedge_downbeta | single | 2.574 | -1.18 | 3/6 | 0/5 | -1.92/-0.03 | False | -33.18 | 1.17 | 2.02 | 2.47 | 2.29 | -1297 | 0.390 |
| T22 | hedge_4hbeta | single | 2.665 | -0.34 | 3/6 | 0/5 | -0.36/-0.11 | False | -30.4 | 1.37 | 2.46 | 2.57 | 2.42 | -1914 | 0.334 |
| T23 | hedge_dimson | single | 2.391 | -3.24 | 0/6 | 0/5 | -2.71/-2.82 | False | -48.63 | 0.79 | 0.91 | 2.27 | 2.08 | -3030 | 0.450 |
| T24 | hedge_btceth | single | 2.436 | -2.1 | 1/6 | 0/5 | -1.43/-3.50 | False | -30.44 | 1.34 | 1.25 | 2.26 | 1.97 | -2241 | 0.652 |
| T25 | pc_adj_0.5 | single | 2.736 | 0.74 | 4/6 | 2/5 | 0.80/-0.11 | False | -28.97 | 1.57 | 3.26 | 2.63 | 2.45 | -1660 | 0.373 |
| T26 | pc_riskparity_legs | single | 0.724 | -4.82 | 1/6 | 0/5 | -20.82/-14.53 | False | -52.34 | -0.18 | -4.12 | 0.61 | 0.44 | -1353 | 0.325 |
| T27 | ex_disp | single | 2.567 | -1.39 | 1/6 | 3/5 | -2.30/0.30 | False | -32.33 | 1.24 | 1.9 | 2.41 | 2.15 | -1307 | 0.484 |
| T28 | ex_fund_q0.8 | EX_FUND | 2.605 | -0.88 | 2/6 | 3/5 | -2.27/1.03 | False | -32.64 | 1.35 | 1.93 | 2.48 | 2.29 | -1888 | 0.406 |
| T29 | ex_fund_q0.9 | EX_FUND | 2.654 | -0.5 | 3/6 | 2/5 | -1.13/0.63 | False | -31.2 | 1.31 | 2.34 | 2.53 | 2.34 | -1888 | 0.410 |
| T30 | ex_altseason_q0.8 | EX_ALT | 2.551 | -1.6 | 0/6 | 1/5 | -1.04/-1.63 | False | -30.94 | 1.28 | 1.8 | 2.43 | 2.24 | -1888 | 0.406 |
| T31 | ex_altseason_q0.9 | EX_ALT | 2.697 | 0.07 | 3/6 | 3/5 | 0.24/-0.20 | False | -30.73 | 1.47 | 2.76 | 2.58 | 2.4 | -1888 | 0.405 |
| T32 | ex_altseason_short | single | 2.575 | -1.22 | 2/6 | 1/5 | -0.20/-2.17 | False | -30.38 | 1.47 | 2.12 | 2.46 | 2.26 | -1888 | 0.410 |
| T33 | tranche2 | TRANCHE | 2.654 | -0.49 | 3/6 | 3/5 | -0.84/0.26 | False | -29.08 | 1.29 | 2.84 | 2.54 | 2.36 | -1996 | 0.406 |
| T34 | tranche4 | TRANCHE | 2.55 | -1.5 | 1/6 | 1/5 | -2.35/0.01 | False | -29.88 | 1.22 | 2.09 | 2.44 | 2.25 | -1988 | 0.407 |
| T35 | short_corrveto_0.5 | CORRVETO | 2.36 | -1.72 | 2/6 | 1/5 | -5.48/0.01 | False | -33.12 | 0.98 | 0.65 | 2.22 | 1.98 | -1810 | 0.497 |
| T36 | short_corrveto_0.7 | CORRVETO | 2.632 | -0.9 | 2/6 | 2/5 | -0.96/-0.05 | False | -29.51 | 1.41 | 2.35 | 2.51 | 2.33 | -1888 | 0.415 |
| T37 | NS25 | NS | 2.595 | -1.45 | 3/6 | 1/5 | -1.87/0.33 | False | -30.86 | 1.41 | 2.09 | 2.48 | 2.3 | -1888 | 0.398 |
| T38 | NS30 | NS | 2.559 | -1.6 | 4/6 | 1/5 | -1.81/-0.49 | False | -31.5 | 1.41 | 1.84 | 2.45 | 2.26 | -1888 | 0.387 |
| T39 | volstop | single | 2.721 | 0.28 | 4/6 | 3/5 | -0.38/1.05 | False | -28.88 | 1.47 | 3.25 | 2.61 | 2.43 | -1888 | 0.402 |
| T40 | minvar_adj | single | 2.62 | -0.32 | 3/6 | 2/5 | -2.43/1.54 | False | -32.62 | 1.57 | 1.59 | 2.48 | 2.25 | -781 | 0.390 |
| T41 | short_invbeta | single | 2.567 | -0.85 | 3/6 | 2/5 | -1.86/-0.25 | False | -35.77 | 1.01 | 1.83 | 2.44 | 2.23 | -1268 | 0.489 |
| T42 | short_invvol_p0.5 | SHORT_RISKW | 2.757 | 1.31 | 5/6 | 3/5 | 0.47/0.74 | False | -29.49 | 1.48 | 3.15 | 2.63 | 2.44 | -1314 | 0.413 |
| T43 | short_invvol_p2 | SHORT_RISKW | 2.776 | 0.71 | 3/6 | 3/5 | 0.32/1.32 | False | -28.15 | 1.63 | 2.81 | 2.64 | 2.41 | -1017 | 0.440 |
| T44 | short_invvol_noclip | SHORT_RISKW | 2.788 | 1.02 | 4/6 | 3/5 | 0.60/1.22 | False | -29.07 | 1.55 | 3.03 | 2.66 | 2.45 | -874 | 0.423 |
| T45 | short_minvar_s0.25 | SHORT_RISKW | 2.898 | 0.99 | 4/6 | 3/5 | 1.00/2.99 | False | -30.41 | 1.83 | 2.78 | 2.73 | 2.45 | -770 | 0.508 |
| T46 | short_minvar_s0.75 | SHORT_RISKW | 2.887 | 1.17 | 4/6 | 4/5 | 1.08/2.65 | False | -29.0 | 1.7 | 3.06 | 2.73 | 2.49 | -753 | 0.457 |

## 2. Walk-forward for parameter families (`h.walk_forward(family, B)`; only the tried values, B not included)
| family | members | wf_SR | base_SR (2021-25) | t_NW (raw diff) | pass (wf_SR>base_SR) |
|---|---|---|---|---|---|
| SQZ_R72 | 3 | 2.39 | 2.43 | −1.09 | no |
| SQZ_VOL | 2 | 2.41 | 2.43 | −1.11 | no |
| SQZ_LIQ | 2 | 1.50 | 2.43 | −3.59 | no |
| SQZ_GUARD | 2 | 2.16 | 2.43 | −1.52 | no |
| BAN | 3 | 2.32 | 2.43 | −1.47 | no |
| RSTOP | 3 | 2.32 | 2.43 | −1.08 | no |
| EX_FUND | 2 | 2.39 | 2.43 | −1.81 | no |
| EX_ALT | 2 | 2.45 | 2.43 | −0.70 | marginal SR, fails partition anyway |
| TRANCHE | 2 | 2.37 | 2.43 | −1.02 | no |
| CORRVETO | 2 | 2.40 | 2.43 | −0.84 | no |
| NS | 2 | 2.27 | 2.43 | −3.06 | no |
| SHORT_RISKW (T17,T19,T42-46) | 7 | 2.49 | 2.43 | −1.77 | SR yes, mean no |

## 3. Near-miss: minimum-variance / inverse-vol short leg (NOT adopted)
**Robustness check across rebalance clocks.** This is a diagnostic, not a new trial: the same T17/T19 configurations run at each of the 8 clock offsets and compared with B at the same offset.

| offset | B SR | invvol SR / t | minvar SR / t | B mdd@2% | invvol mdd@2% | minvar mdd@2% | B minYr | invvol minYr | minvar minYr |
|---|---|---|---|---|---|---|---|---|---|
| 0 (B) | 2.69 | 2.78 / 0.99 | 2.84 / 0.76 | −30.0 | −28.9 | −29.6 | 1.41 | 1.54 | 1.59 |
| 1 | 2.62 | 2.69 / 0.83 | 2.78 / 0.88 | −33.0 | −28.5 | −24.1 | 1.30 | 1.65 | 2.02 |
| 2 | 2.54 | 2.55 / 0.08 | 2.45 / −0.50 | −31.4 | −26.9 | −27.7 | 1.17 | 1.28 | 1.31 |
| 3 | 2.59 | 2.61 / 0.22 | 2.67 / 0.42 | −39.1 | −32.7 | −23.6 | 1.02 | 1.21 | 1.58 |
| 4 | 2.53 | 2.61 / 0.95 | 2.74 / 1.12 | −29.1 | −23.3 | −24.6 | 1.11 | 1.26 | 1.49 |
| 5 | 2.35 | 2.46 / 1.29 | 2.52 / 0.95 | −33.9 | −28.2 | −30.0 | 1.12 | 1.37 | 1.50 |
| 6 | 2.23 | 2.32 / 1.10 | 2.36 / 0.69 | −35.8 | −36.7 | −30.9 | 0.90 | 1.07 | 1.37 |
| 7 | 2.51 | 2.57 / 0.77 | 2.64 / 0.73 | −30.5 | −31.4 | −28.3 | 1.37 | 1.56 | 1.56 |
| 8-clock average book | 2.57 | 2.64 / 0.86 | 2.72 / 0.85 | −30.3 | −25.4 | −26.6 | 1.29 | 1.44 | 1.74 |

The minvar short leg is better on vol-matched MDD in **8/8** clocks, on minYrSR in **8/8** and on SR in 7/8. Its worst 5-day loss (vol units) is −7.4 vs −15.1 for B on the 8-clock average.
Yet its risk-matched mean t never exceeds 1.12, it wins only 3–5/6 years, and the coin groups split roughly 3/5. **The improvement is in risk shape (tails, consistency), not in mean return per unit of vol.**
The protocol's adoption rule is built on risk-matched mean, so it is correctly not adopted. If the team wants a rule that rewards drawdown reduction directly, that rule has to be pre-registered and validated (e.g. placebo distribution of Δmdd_at2pct) before minvar can be judged on it. The clocks are highly correlated with each other, so "8/8" is weaker evidence than it sounds.

Plateau (shrink to diagonal 0.25 / 0.5 / 0.75): SR 2.90 / 2.84 / 2.89, t 0.99 / 0.76 / 1.17, mdd@2% −30.4 / −29.6 / −29.0, minYr 1.83 / 1.59 / 1.70. The result is flat, so it is not a spike. Cost: turnover rises from 0.41 to 0.46–0.51/day. SR is 2.68–2.73 at 8 bp and 2.42–2.49 at 12 bp, still above B (2.58 / 2.40).

Exact code (T19, `leg_weights` hook of `ext.book`/`ext2.book`; RS = `np.nan_to_num(D.resid.to_numpy())`):
```python
def minvar(i, longs, shorts):          # uses residual returns up to hour i only; book trades at i+2
    if len(shorts) < 2: return np.full(len(longs), 0.45/len(longs)), np.full(len(shorts), 0.55/max(1, len(shorts)))
    X = RS[max(0, i-335):i+1][:, shorts]; C = np.cov(X.T); C = 0.5*C + 0.5*np.diag(np.diag(C)); e = 1/len(shorts)
    try: x = np.linalg.solve(C + 1e-10*np.eye(len(shorts)), np.ones(len(shorts)))
    except np.linalg.LinAlgError: x = np.ones(len(shorts))
    x = np.maximum(x, 0); x = x/x.sum() if x.sum() > 0 else np.full(len(shorts), e)
    for _ in range(5): x = np.minimum(x, 2*e); x /= x.sum()
    return np.full(len(longs), 0.45/len(longs)), 0.55*x
cand = ext.book(D, S0, short_frac=0.55, stop=0.2, N=12, NS=20, leg_weights=minvar)
```
(The version in run1.py lacks the `len(shorts) < 2` guard. That case never occurs at offset 0, and the results are identical.)

## 4. What the diagnostics say about the drawdowns
- 2022-06-13 on B: long leg −625 bp, short leg only +105 bp, hedge −1358 bp. The shorts (0.55 gross, 168h beta ≫ 1) behaved as if their beta was about 0.2 while BTC fell about 15%. The long hedge was sized on betas that did not show up in the crash.
  - Beta re-estimation does not fix this on average. The crash or downside beta helps that day but loses elsewhere (squeeze and rally days need the full beta).
  - What does reduce it is *holding fewer dollars in the highest-vol, highest-beta shorts*: minvar/invvol give −750 to −1100 bp that day. Sizing shorts directly by 1/β (T41) was worse, though, so the effect comes from the vol/covariance side, not the beta side.
- B's max DD is Oct–Nov 2021 (an alt-season cluster squeeze), not Mar 2021. Squeeze vetoes, correlation vetoes and alt-season de-risking all failed, because the same names and regimes also produce the short leg's alpha. Removing them removes the carry.

## 5. Caveats
- 46 trials were run on top of the ~350 books already run in this project. With a placebo false-pass rate of 0.5–2.5%, about 0.2–1 false passes would be expected here, and none occurred.
- **B itself sits on a lucky rebalance clock** (§3), and B was selected in-sample. Every "vs B" comparison is against an optimistic base. Realistic B across clocks is SR ≈ 2.5 with mdd@2% ≈ −30 to −35%.
- worst_day_bp in the table is raw, not vol-matched. Candidates with lower vol look slightly better on it (minvar vol is about 18% below B's).
- All exposure thresholds used expanding, lagged quantiles (walk-forward by construction). All signals use data ≤ hour i, and the book trades at i+2. The daily overlays were computed from the day-d close and applied from day d+1.
- Crash, downside and 4h betas were not clipped (fallback to the 168h beta where NaN). The BTC+ETH hedge doubles hedge turnover (0.65/day), which explains part of its cost drag.
- The 2026 holdout was not used.

## Files (all in this folder)
`ext2.py` (ext.book plus hooks; reproduces B exactly, asserted), `ev.py` (evaluation/CSV), `run1.py`–`run4.py` (trials), `run5.py` (clock diagnostic), `wf.py` (walk-forwards), `trials.csv`, `run*.log`, `run*.pkl` / `offsets.pkl` / `wf.pkl` (daily results).
