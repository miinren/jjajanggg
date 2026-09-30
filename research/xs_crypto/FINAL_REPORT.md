# XS crypto low-idio-vol book: final research summary (2026-09-29/30)

Research only, using 2020-03 to 2025-12 data. The 2026 holdout was never touched. About 520 backtests were run across the session, and each proposal was checked with pre-registration, risk-matched partition tests, placebo nulls and walk-forward. Detailed reports:
- `report.md`: audit, round 1–2 and active variants
- `results/drawdown/REPORT.md`
- `results/signals/REPORT.md`
- `results/active/REPORT.md`
- `results/clock/REPORT.md`
- `results/wave2/REPORT.md`

## Recommended configuration ("B-MV")
Changes from the current live book:
1. **12 longs / 20 shorts** (was 20/20).
2. **Short leg = 55% of leg gross**, long leg 45% (was 50/50).
3. **Short stop at +20%** against you from entry (was +40%). After a stop, don't re-short the name at the next rebalance. The long stop stays at 40%.
4. **Short weights: minimum-variance on the 336h residual covariance**, shrunk 50% toward the diagonal, each weight between 0.4× and 2× equal weight (≥ $5 per short at $330). The code is `minvar_floor` in `results/wave2/s3_floor.py`, built on `minvar` in `results/wave2/lib.py`.

Unchanged: score (0.75 AR1-corrected idio vol + 0.25 funding), 8h rebalance, hysteresis, funding guard, BTC-beta hedge, top-1/3 liquidity universe.

### Evidence
The table is averaged over all 8 possible rebalance clocks, since single-clock results turned out to be clock-lucky. Costs are 5.5 bp.

| | LIVE | B (steps 1–3) | **B-MV (1–4)** |
|---|---|---|---|
| Sharpe | 2.19 | 2.57 | **2.77** |
| Sharpe at 8 / 12 bp | ~2.1 / ~1.95 | 2.45 / 2.27 | **2.62 / 2.36** |
| Max DD at equal vol (2%/day) | −32.0% | −30.3% | **−25.1%** |
| Worst-year Sharpe | 1.02 | 1.29 | **1.74** |
| Yearly Sharpe 2020–25 | 2.9 / 0.9 / 1.5 / 2.5 / 2.9 / 3.5 (clock 0) | – | **3.8 / 1.7 / 1.8 / 2.3 / 3.3 / 4.0** |

- **B vs LIVE:** B beats LIVE at 8/8 clocks. Risk-matched test: t 2.93, 6/6 years, 4/5 coin groups; adopted.
- **B-MV vs B:** the pre-registered tail-risk test passes. CVaR improves 13.3 bp, against a random-weighting null 95th percentile of 7.1. The risk-matched t is +1.49, so return is not improved significantly. The gain is a better risk shape.

## What did not work (all tested, none adopted)
- **BTC-beta edges:** betting-against-beta, downside beta, beta change/instability, crash beta, jump beta, BTC lead-lag (alts slightly over-react, IC ~0), Dimson and 4h betas, ETH+BTC hedge, and hedge ratios below 1. The full 168h BTC hedge is right.
- **New signals:** about 40 features (funding dynamics, illiquidity, skew, coin age, seasonality, reversal, momentum, MAX, volume shocks). All were t ≤ 0 as score tweaks. The "near 30-day high" sleeve (t 0.7) is the only one worth checking on the 2026 holdout.
- **Active management:** hourly/2/4/6h rebalancing, hourly rank exits, time stops, trailing stops, partial cuts, residual- or vol-scaled stops, squeeze detectors, take-profits, book brakes, vol targeting and DD throttles. All were worse, several strongly (t −3 to −4). Walk-forward selection among active rules loses (SR 2.19 vs 2.43).
- **Universe breadth:** wider or narrower liquidity masks were noisy and not adopted.

## Your "down 20% on many positions" question
- **Shorts at −20%:** about 25% of shorts get there (~4 per week). Only 1% recover by the next rebalance, and within 3 days 60% touch −30%. **Cut them at 20%**; that is rule 3.
- **Longs at −20%:** they tend to bounce (+2% over 3 days). **Hold them.** Tighter long stops hurt.
- **Don't cut positions by hand.** Discretionary-style exits were the worst performers in testing.

## Realistic expectation (B-MV)
- **Backtest:** Sharpe 2.77 (8-clock). About 520 variants were tested, the historical period has strong 2024–25 years, and fills during squeezes will be worse than modelled.
- **Realistic live Sharpe: ≈ 1.0–1.8, central ~1.4.** Current live is ≈ 0.8–1.6, central ~1.2.
- **At 1.5x gross:**
  - Daily vol is ~2.15% (~41%/yr), slightly less risk than live at 1.5x.
  - Expected return ≈ 40–75%/yr, i.e. **~$11–21/month on $330 (central ~$16)**.
  - Plan for a **−30% drawdown (~−$100)** and single days of −15 to −20%.
- **Before switching:** run B-MV and LIVE side by side on the 2026 holdout data you hold. Only switch if B-MV is at least not worse. That is the one clean test left.

## Research status
The accessible search space looks exhausted. Two full waves of new signal, hedge, active-management and construction ideas produced no mean improvement. The only adoptions were B's reallocation and a risk-shape change. More in-sample search would mostly generate false positives: the placebo max t was 1.79, and ~2.5% of random features pass the adoption rule. The best remaining uses of time are the 2026 holdout check and live paper-trading of B-MV alongside LIVE.

---

## Update (wave 3, 2026-09-30)

### Would the selection process have worked in advance? (results/wave3a)
- The whole selection was re-run using only data before 2023, 2024 and 2025, then tested on the next year. **The picked config was the same all three times:** 8 longs / 20 shorts, short stop 0.20, minvar_floor short weights, and a 50/50 short allocation. B's 55% short allocation would not have been picked before 2025.
- **Out of sample**, the pick beat LIVE on risk-matched return in 3/3 years and on SR in 2/3 years:

  | Year | SR uplift vs LIVE |
  |---|---|
  | 2023 | −0.06 |
  | 2024 | +0.83 |
  | 2025 | +0.22 |
  | Pooled 2023–25 | +0.34 (t 2.59) |

- About 45% of the in-sample uplift survived. **Realistic live uplift: about +0.15 to +0.35 SR over LIVE**, with roughly a 1-in-3 chance of no gain in a given year.

### Realistic costs and fills (results/wave3a)
- **Per-coin costs** (liquidity-scaled) barely matter: the edge survives at 2x the cost level.
- **Stop slippage is the key risk.** The 20% short stop fires about 2.7x more exposure than LIVE's stop, and squeezes gap.

  | Stop slippage | B-MV vs LIVE |
  |---|---|
  | 1% | t 2.17 |
  | 2% | t 1.27 |
  | Break-even | about 3.5% |

  Plain B's edge dies at about 2.3% slippage, so **don't run plain B, only B-MV.** B-MV keeps its drawdown advantage in every setting.
- **Funding** is about 9% of P&L. It is unclear whether daily funding is stamped same-day; the worst case costs every book about −0.06 SR and doesn't change the ranking.

### Structural ideas (results/wave3b)
- Separate long/short scores all failed.
- An ensemble across idio windows failed.
- An ensemble across long counts passed only by noise.
- The minvar settings sit on a plateau: SR 2.65–2.82 for all neighbours.
- **8 longs vs 12:** SR 2.95 vs 2.77, t 2.06, and walk-forward picks 8 every year. The pseudo-holdout pipeline also picked 8. Still, this is post hoc and borderline.

### Revised recommendation
1. Go live with **B-MV next to LIVE**, sized about **1.15x** to match LIVE's volatility (B-MV runs about 15–20% less volatile).
   - Candidate for the 2026 holdout: B-MV with **8 longs and a 50/50 short allocation**. This is the clean pipeline's pick, and N=8 is also supported by wave 3b.
2. **Log every short-stop fill vs the 20% trigger.** If slippage averages ≥ 2%, the case for switching largely disappears.
3. Expected live SR: LIVE about 1.2 → B-MV about **1.35–1.55**, i.e. **about $13–19/month on $330** at matched risk. Drawdown planning is unchanged: about −30%.
