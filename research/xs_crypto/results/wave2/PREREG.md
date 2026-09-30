# Wave 2 pre-registration (written 2026-09-29 BEFORE any wave-2 code was run)

All evaluation is on the **8-clock-averaged book**: daily df and coin matrix averaged over rebalance offsets 0..7 (as in
results/clock/clock.py), sample 2020-03-15 .. 2025-12-31. Base B = ext.book(D, S0, short_frac=0.55, stop=0.2, N=12, NS=20),
8-clock averaged (known: SR 2.57, mdd@2% -30.3, minYrSR 1.29). 2026 holdout untouched.

## PART 1 - Is the risk-weighted short leg's drawdown improvement real?

Trials (exactly 2, code frozen from results/drawdown/run5.py):
- P1a = T19 short_minvar (336h residual covariance, 0.5 shrink to diagonal, long-only, cap 2x equal weight)
- P1b = T17 short_invvol (1/idio-vol, clipped to [0.5x, 2x] equal weight)

**Primary risk metric (single, pre-registered):** CVaR_5% of daily net returns at matched vol =
mean of the worst 5% of daily returns of the candidate after scaling it to B's daily vol (reported in bp at B's vol, and as
"vol units" = divided by vol). Improvement dCVaR = CVaR_B - CVaR_cand (positive = thinner left tail).

**Secondary (reported, confirmatory, NOT gating):** worst 20-day rolling cumulative loss at matched vol (same scaling);
also mdd@2%, 2022-06-13 loss, the Oct-Nov 2021 drawdown, SR at 8/12 bp.

**Placebo null:** short-leg weights w_s proportional to exp(sigma * z_c), z_c ~ N(0,1) drawn once per coin per seed (fixed over
time), then the same "cap at 2x equal weight, renormalise (5 passes)" step as minvar, short gross 0.55, long leg unchanged
(0.45 equal weight). sigma is calibrated so that the mean within-rebalance coefficient of variation (std/mean) of the placebo
short weights matches minvar's (measured on offset-0 run of P1a before the null is run; calibration uses random draws
of 20 z's, no returns). Seeds: >= 30, each evaluated on the 8-clock average (same as the trials). If invvol's weight CV
differs from minvar's by more than 30%, a second null calibrated to invvol's CV (with invvol's [0.5x,2x] clip) is run
for P1b; otherwise P1b is judged against the minvar-calibrated null.

**Adoption (all required):**
1. dCVaR_cand > 95th percentile of dCVaR over the placebo seeds.
2. Risk-matched mean t_NW vs B (h.partition_test, 8-clock avg) >= -0.5.
3. minYrSR (8-clock avg) >= B's minYrSR.
Result is a "risk-shape improvement adopted/not adopted"; it does not claim a mean improvement.

## PART 2 - Universe breadth (4 trials, one family "BREADTH")

Mask Mx = D.U & (D.lq > thr). The score is rebuilt within Mx exactly like S0 (0.75*pct(AR1-corrected idio 336h within Mx)
+ 0.25*pct(funding within Mx), funding NaN -> 0.5), and elig=Mx is passed to the book. Book params = B's.
- U50: thr = 0.5
- U60: thr = 0.6
- U75: thr = 0.75 (narrower; control for the direction)
- SPLIT: score/elig on lq > 0.5, but longs restricted to the top-1/3 (D.M); shorts from lq > 0.5.
Rationale: the drawdown work found the alpha lives in less-liquid jumpy names (liquidity restriction was strongly negative),
so a wider pool of shortable jumpy names could raise the short leg's carry; longs (calm names) likely gain little and
are the most execution-sensitive at $5 min notional, hence SPLIT.

**Adoption:** 8-clock-averaged h.partition_test(cand, B) adopt=True AND t_NW >= 2.0, AND h.walk_forward over the 4-member
family (8-clock-averaged) gives wf_SR > base_SR. Also reported: SR at 8 and 12 bp (must stay > B's at 12 bp to be
practically interesting), position notionals at $330 x 1.4 gross, and median 24h $ volume / lq percentile of held shorts.
