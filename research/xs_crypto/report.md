# Robustness audit: live low-idio-vol xs book (W3 + AR1 bounce correction)

Data 2020-03-15 to 2025-12-31 (the 2026 holdout was not used). Research only. Everything here comes from `cloud_harness.py` (risk-matched v2 partition test, BTC/ETH/PAXG/XAUT excluded) plus the AR1-corrected idio score.

## Plain-English summary

- **Backtest:** SR 2.22 net of 5.5 bp, 18.5 bp/day per unit gross, max drawdown −26% at 1x. The book is much weaker in 2020-22 (SR 1.64; 2021 only 0.85) than in 2023-25 (SR 2.98). Most of the headline number comes from the last three years, and 2025 alone has SR 3.5.
- **Noise floor:** 200 random features added at weight 0.10 gave paired t_NW mean −0.92 (95th pct 0.61, max 1.79). Adding noise *hurts* on average, which means the live config sits at a locally tuned point. Only 1 of 200 (0.5%) passed the full adoption rule, so the risk-matched v2 rule is stricter than the ~2.5% seen earlier today. **But random perturbations of the score alone move the full-period SR between 1.77 and 2.45 (sd 0.11).** Any variant with SR ≤ ~2.45 is indistinguishable from noise on SR alone.
- **Parameter stability:** live is on a broad plateau, not a spike. The N×L grid SR runs 1.91–2.50 (median 2.12), and every 1-D sweep stays at SR ≥ 1.75. Smaller N and L 240–504 look better in-sample, but a walk-forward pick of the best (N, L) each year earns SR 2.14 vs 2.09 for live over 2021-25 (t 1.19). **Re-tuning does not pay out of sample.** More funding weight (fw 0.4–0.5) and a tighter stop (0.2) raise SR in-sample, almost entirely from 2020-22. They are tempting but unvalidated, and were not adopted here.
- **Selection bias:** Deflated Sharpe with 255 trials is still ≥ 0.86 under conservative assumptions, so the edge is very likely real. Bayesian shrinkage (prior sd 1.0) gives SR 1.86 (90% interval 1.21–2.52). Subtracting the expected best-of-255-noise SR gives about 1.0–1.2.
- **Costs:** mild sensitivity. Turnover is 0.32 units/day, and SR goes from 2.27 at 4 bp to 1.97 at 12 bp.
- **Tail risk (1.5x):** worst day −24% (2022), worst 5 days −30%, worst 20 days −33%, max drawdown −40%. On $330 that is −$79 / −$98 / −$108 / −$131.

### Realistic live expectation
**Live Sharpe of about 0.8–1.6 (central ~1.2).** This combines the Bayesian shrink (1.86), the selection-bias haircut (~1.0–1.2), the weak 2020-22 sub-period (1.64) and the usual 25–40% backtest-to-live drag (fills, slippage, decay).
At 1.5x gross, annual vol is ~46%. That makes the expected return ~35–75%/yr (central ~55%), or **about $10–$20 per month on a $330 account (central ~$15/month)**. The spread is wide: a losing month of −$30 to −$60 is routine, and a −$130 drawdown has already happened in-sample. Check that per-position size (~$12 for 40 names at 1.5x × $330) clears exchange minimum notionals.

### Implementation notes / caveats
- The brief's phi formula arrived garbled, so I used phi = rolling-336 mean(e·e₋₁) / rolling-336 mean(e₋₁²), min_periods=200, clipped to ±0.5. Score = 0.75·pct(AR1 idio in M) + 0.25·pct(funding). This reproduces SR 2.22, which matches the stated ~2.1–2.3.
- In the L sweep, both the idio window and the gate use L. The phi window stays at 336.
- Placebo = a random uniform constant per coin, pct-ranked within M, blended as 0.9·live + 0.1·placebo.

## 1. Noise floor (placebo)

200 random constant per-coin features, pct-ranked within M, blended at weight 0.10 into the live score; partition_test (risk-matched) vs live.

- paired t_NW: mean -0.92, sd 0.89, 5/50/95/99th pct -2.30/-0.86/0.61/1.04, max 1.79
- t_NW ≥ 1.5: 0.5%;  full adoption rule passes: 1/200 = 0.5%
- years≥5/6: 2.0%, groups≥4/5: 2.5%, both regimes: 5.5%
- placebo-book SR: mean 2.10, sd 0.11, range 1.77..2.45 (live 2.22)

## 2. Parameter stability


**N** (live marked *)

| N | SR | bp/day | SR 20-22 | SR 23-25 | turnover/day |
|---|---|---|---|---|---|
| 12 | 2.30 | 21.5 | 1.67 | 2.87 | 0.36 |
| 15 | 2.23 | 19.6 | 1.60 | 2.85 | 0.34 |
| 18 | 2.18 | 18.6 | 1.56 | 2.92 | 0.33 |
| 20 | 2.22 | 18.5 | 1.64 | 2.98 | 0.32 |
| 22 | 2.19 | 18.1 | 1.64 | 2.96 | 0.32 |
| 25 | 2.10 | 16.9 | 1.64 | 2.82 | 0.31 |
| 30 | 2.08 | 16.3 | 1.64 | 2.86 | 0.30 |

**L** (live marked *)

| L | SR | bp/day | SR 20-22 | SR 23-25 | turnover/day |
|---|---|---|---|---|---|
| 168 | 2.01 | 16.8 | 1.58 | 2.55 | 0.35 |
| 240 | 1.99 | 16.9 | 1.49 | 2.65 | 0.33 |
| 336 | 2.22 | 18.5 | 1.64 | 2.98 | 0.32 |
| 504 | 2.26 | 18.5 | 1.55 | 3.13 | 0.31 |
| 720 | 2.11 | 17.7 | 1.57 | 2.80 | 0.29 |

**fw** (live marked *)

| fw | SR | bp/day | SR 20-22 | SR 23-25 | turnover/day |
|---|---|---|---|---|---|
| 0 | 1.75 | 14.7 | 1.00 | 2.73 | 0.31 |
| 0.1 | 1.86 | 15.7 | 1.12 | 2.82 | 0.31 |
| 0.25 | 2.22 | 18.5 | 1.64 | 2.98 | 0.32 |
| 0.4 | 2.40 | 19.4 | 2.00 | 2.92 | 0.37 |
| 0.5 | 2.64 | 19.8 | 2.43 | 2.91 | 0.44 |

**every** (live marked *)

| every | SR | bp/day | SR 20-22 | SR 23-25 | turnover/day |
|---|---|---|---|---|---|
| 4 | 2.09 | 17.7 | 1.46 | 2.92 | 0.33 |
| 6 | 2.13 | 17.8 | 1.62 | 2.80 | 0.32 |
| 8 | 2.22 | 18.5 | 1.64 | 2.98 | 0.32 |
| 12 | 2.20 | 18.5 | 1.62 | 2.98 | 0.31 |
| 24 | 2.01 | 16.6 | 1.30 | 2.95 | 0.30 |

**stop** (live marked *)

| stop | SR | bp/day | SR 20-22 | SR 23-25 | turnover/day |
|---|---|---|---|---|---|
| 0.2 | 2.45 | 19.9 | 2.17 | 2.82 | 0.40 |
| 0.3 | 2.23 | 18.6 | 1.71 | 2.93 | 0.35 |
| 0.4 | 2.22 | 18.5 | 1.64 | 2.98 | 0.32 |
| 0.6 | 2.33 | 19.4 | 1.81 | 3.01 | 0.30 |
| 1.0 | 2.21 | 18.6 | 1.77 | 2.80 | 0.29 |
| off | 2.24 | 19.1 | 1.72 | 2.92 | 0.28 |

**keepx** (live marked *)

| keepx | SR | bp/day | SR 20-22 | SR 23-25 | turnover/day |
|---|---|---|---|---|---|
| 0.0 | 2.07 | 17.4 | 1.62 | 2.64 | 0.37 |
| 0.25 | 2.09 | 17.5 | 1.62 | 2.69 | 0.36 |
| 0.5 | 2.22 | 18.5 | 1.64 | 2.98 | 0.32 |
| 1.0 | 2.13 | 17.2 | 1.56 | 2.86 | 0.28 |

**N x L grid – SR**

| N \ L | 168 | 240 | 336 | 504 | 720 |
|---|---|---|---|---|---|
| 12 | 2.12 | 2.50 | 2.30 | 2.41 | 2.25 |
| 16 | 2.17 | 2.21 | 2.34 | 2.32 | 2.18 |
| 20 | 2.01 | 1.99 | 2.22 | 2.26 | 2.11 |
| 25 | 1.99 | 1.98 | 2.10 | 2.14 | 2.04 |
| 30 | 1.91 | 1.91 | 2.08 | 2.06 | 2.04 |

**N x L grid – bp/day**

| N \ L | 168 | 240 | 336 | 504 | 720 |
|---|---|---|---|---|---|
| 12 | 19.5 | 23.1 | 21.5 | 22.0 | 20.8 |
| 16 | 18.5 | 19.1 | 20.2 | 19.7 | 18.6 |
| 20 | 16.8 | 16.9 | 18.5 | 18.5 | 17.7 |
| 25 | 15.9 | 16.1 | 16.9 | 16.9 | 16.5 |
| 30 | 15.0 | 15.1 | 16.3 | 15.8 | 16.0 |

Grid SR: min 1.91, median 2.12, max 2.50; live (20,336) = 2.22.

Walk-forward over the N x L family (pick best SR on years < Y, trade year Y): picks {2021: ('NxL', 12, 240), 2022: ('NxL', 16, 504), 2023: ('NxL', 16, 504), 2024: ('NxL', 12, 240), 2025: ('NxL', 12, 240)}, WF SR 2.14 vs live-config SR 2.09 over 2021-25, t_NW(diff) 1.19.

## 3. Realistic expectation

Daily returns (1x gross, 5.5 bp): n=2118, mean 18.5 bp/day, SR 2.22, skew -0.56, kurtosis 10.8, SE(SR ann.) 0.43.

| Deflated Sharpe (N_trials=255) | SR* (expected max of 255 null trials, ann.) | DSR = P(true SR > SR*) |
|---|---|---|
| V[SR] = sampling var of SR (pure-noise trials) | 1.24 | 0.9878 |
| V[SR] = dispersion of today's sweep variants | 0.45 | 1.0000 |
| V[SR] = 2x sampling var (conservative) | 1.75 | 0.8582 |

Bayesian shrinkage (prior SR ~ N(0, 1.0²)): posterior mean 1.86, 90% interval [1.21, 2.52] (shrink factor 0.84).
Selection-bias haircut (SR − expected max-of-255-noise SR, same variance): 0.98.

| Period | SR | bp/day | ann. return @1.5x | worst day @1x (bp) |
|---|---|---|---|---|
| 2020 | 2.92 | 28.1 | 154% | -849 |
| 2021 | 0.85 | 9.3 | 51% | -776 |
| 2022 | 1.52 | 11.6 | 64% | -1602 |
| 2023 | 2.47 | 13.0 | 71% | -375 |
| 2024 | 2.91 | 19.6 | 107% | -430 |
| 2025 | 3.50 | 31.5 | 172% | -784 |
| 2020-22 | 1.64 | 15.5 | 85% | -1602 |
| 2023-25 | 2.98 | 21.4 | 117% | -784 |
| all | 2.22 | 18.5 | 101% | -1602 |

Annualised arithmetic return at 1.5x gross, 5.5 bp: 101% (ann. vol 46%).

Worst rolling losses (sum of daily log-ish returns, per unit gross; bp and $ at 1.5x on $330):

| Window | worst @1x (bp) | worst @1.5x | $ on $330 @1.5x |
|---|---|---|---|
| 1d | -1602 | -24.0% | $-79 |
| 5d | -1990 | -29.8% | $-98 |
| 20d | -2187 | -32.8% | $-108 |
| max drawdown | -2646 | -39.7% | $-131 |

## 4. Cost sensitivity (live config)

| cost bp/unit | SR | bp/day | SR 20-22 | SR 23-25 | ann @1.5x |
|---|---|---|---|---|---|
| 4 | 2.27 | 19.0 | 1.69 | 3.04 | 104% |
| 5.5 | 2.22 | 18.5 | 1.64 | 2.98 | 101% |
| 8 | 2.12 | 17.7 | 1.55 | 2.86 | 97% |
| 12 | 1.97 | 16.4 | 1.42 | 2.68 | 90% |

Mean turnover 0.32 units/day → each +1 bp cost ≈ −0.32 bp/day.



---

# Part 2: Improvement search (requested follow-up)

**Trial accounting:** 36 candidates in round 1, 22 in round 2 and a 27-point robustness grid, about 85 books in total on top of the ~255 earlier today. Every candidate was run through the risk-matched `partition_test` against live. With the placebo false-pass rate of 0.5–2.5%, **0.5–2 false adoptions are expected by chance.**

## Where drawdowns come from (live)
- Leg P&L: long leg −2.2 bp/day, **short leg +17.6**, BTC hedge +3.4, funding +1.5. All of the alpha is in shorting jumpy / high-funding names. The long leg mostly offsets beta.
- The max drawdown (Mar 2021, −26% at 1x) was an **alt-season short squeeze**: the short leg alone lost −26.6%.
- The worst day (2022-06-13, −16% at 1x) was mostly the **BTC hedge** (−10.6%). The 168h betas of the shorts overstated how much they would fall, so the book was net long BTC into the crash.

## Round 1 (36 candidates, 0 adopted)
| Idea | Result |
|---|---|
| BTC-beta signals: betting-against-beta (w 0.10/0.25), 720h beta, downside-minus-total beta, reversed BAB | all t ≤ 0; **no exploitable beta edge beyond the existing hedge** |
| Hedge ratio 0 / 0.5 / 0.75, shrunk or capped or 720h hedge betas | all worse or flat. The full 168h hedge is right on average, despite the 2022 tail |
| BTC-trend gross throttle, 60d drawdown throttle, 30d vol targeting | flat or worse. **No overlay reduced MDD at equal risk** |
| Other signals (72h residual reversal, 720h residual momentum, 7d MAX, volume shock) at w 0.10 | all t ≤ 0 |
| Inverse-idio-vol leg weights | t 1.29, not adopted |
| Short/long allocation, short-only stop, N and long/short counts | near-misses, followed up in round 2 |

## Number of positions
Symmetric N (5.5 bp, risk-matched t vs live N=20):

| N | 8 | 10 | 12 | 15 | **20 (live)** | 25 | 30 | 40 |
|---|---|---|---|---|---|---|---|---|
| SR | 2.10 | 2.25 | 2.30 | 2.23 | **2.22** | 2.10 | 2.08 | 1.99 |
| t vs live | −0.48 | 0.15 | 0.56 | 0.08 | – | −1.52 | −1.38 | −2.23 |

Symmetric N is flat between 10 and 20; **don't go above 20**. The asymmetric split is what matters: **fewer longs (8–12), keep 20 shorts.** 8L/20S passes the adoption rule (t 2.17, 5/6 years, 4/5 coin groups), and the walk-forward pick of the long/short counts earns SR 2.22 vs 2.09 for live (t 1.28).
The long leg only needs to be the calmest few names: the low-idio-vol effect sits at the extreme. The short leg benefits from diversification against squeezes: 12–15 shorts is worse.
Account size: at 1.5x × $330, 12 longs ≈ $16 each and 20 shorts ≈ $15 each, above Binance's $5 minimum notional on alt perps.

## Round 2 and robustness grid
- **Short allocation 55–60% of leg gross** (instead of 50%): risk-matched t 2.2–2.5 and wins 5/6 years, but only 3/5 coin groups on its own. Walk-forward picking from this family *under*performs in SR (1.85), so don't push it to 0.7–1.0.
- **Short stop 0.20** (long stop stays 0.40): walk-forward picks 0.20 in every year (WF SR 2.21 vs 2.09). It cuts squeeze losses; the worst-year SR goes from 0.85 to 1.38.
- **Combined** (short allocation × short stop × number of longs, 3×3×3 grid around 0.6 / 0.20 / 12): SR 2.40–2.80 everywhere, and every point beats live. 8 of 27 pass the full rule, and all 8 have short stop 0.20. **It is a plateau, but the stop is the sensitive dimension.**

| Book | SR | SR 20-22 | SR 23-25 | worst yr SR | bp/day @1x | vol-matched gross (≙ live 1.5x) | ann. return at that gross | MDD at that gross | worst day | worst 20d | SR @8bp | SR @12bp | turnover/day |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LIVE (20/20, 50/50, stop .40) | 2.22 | 1.64 | 2.98 | 0.85 | 18.5 | 1.50x | 101% | -39.7% | -24.0% | -32.8% | 2.12 | 1.97 | 0.32 |
| A: 8L/20S only | 2.46 | 1.85 | 3.16 | 0.94 | 21.1 | 1.46x | 113% | -39.6% | -22.6% | -34.0% | 2.35 | 2.18 | 0.36 |
| B: sf.55 ss.20 12L/20S | 2.69 | 2.25 | 3.20 | 1.41 | 24.5 | 1.38x | 123% | -35.9% | -26.1% | -33.0% | 2.58 | 2.40 | 0.41 |
| C: sf.60 ss.20 12L/20S | 2.75 | 2.27 | 3.28 | 1.32 | 27.8 | 1.24x | 126% | -35.7% | -26.7% | -34.5% | 2.64 | 2.46 | 0.44 |

Yearly SR:

| Book | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| LIVE (20/20, 50/50, stop .40) | 2.92 | 0.85 | 1.52 | 2.47 | 2.91 | 3.50 |
| A: 8L/20S only | 2.94 | 0.94 | 2.09 | 2.66 | 3.42 | 3.43 |
| B: sf.55 ss.20 12L/20S | 4.19 | 1.41 | 1.58 | 2.64 | 3.44 | 3.51 |
| C: sf.60 ss.20 12L/20S | 4.38 | 1.32 | 1.59 | 2.80 | 3.48 | 3.59 |

Leg attribution bp/day (live → C): long -2.2→-0.8, short 17.6→23.3, hedge 3.4→5.5, fund 1.5→2.3
Correlation of daily PnL live vs C: 0.91

**Drawdown result: modest.** At equal risk, MDD improves from −39.7% to about −36% and the worst year SR from 0.85 to 1.3–1.4. The worst single day (the 2022 hedge event) is not fixed. **The gain is mainly consistency and expected value, not tail protection.**
The candidates are 91% correlated with live, so this is a refinement, not a new edge.

## Recommendation
1. **Adopt B, the conservative version:** 12 longs / 20 shorts, short leg 55% of leg gross, short stop 0.20 (long stop 0.40), everything else unchanged. Pick B rather than C because it is the grid centre on the allocation dimension and needs less dollar imbalance.
   - Run it at **~1.4x** leg gross to keep live's risk level.
   - It passes the adoption rule (t 2.90, 6/6 years, 4/5 coin groups, both BTC regimes).
2. **Before committing capital, check it on the 2026 holdout,** which I don't have. That is the only test this search hasn't contaminated. If B doesn't beat live there, stay with live.
3. **Don't adopt any of the BTC-beta ideas or drawdown overlays.**

## Realistic expectation for B
- In-sample SR is 2.69 vs 2.22 for live. Out of sample, expect well under half of that +0.47 to survive: the walk-forward uplifts per dimension were only +0.12 to +0.13.
- **Realistic live SR ≈ 0.9–1.7 (central ~1.3)**, vs 0.8–1.6 (central ~1.2) for the current live book.
- At live-equivalent risk on $330 that is **≈ $11–22/month (central ~$16)**.
- Drawdown risk is essentially unchanged: plan for a **−35 to −40% drawdown (−$115 to −$130)**, and a single −25% day is possible.

## Part 3: More active variants (tested on top of B; 11 more trials)
| Variant | SR | risk-matched t vs B | years / coin groups won | verdict |
|---|---|---|---|---|
| Rebalance every 1 / 2 / 4 / 6 / 12 h (B = 8 h) | 2.35 / 2.29 / 2.43 / 2.59 / 2.59 | −2.25 / −2.85 / −2.19 / −0.82 / −0.75 | ≤3/6, ≤3/5 | **worse; keep 8 h** |
| Every 4 h with wider hysteresis | 2.45 | −1.51 | 1/6, 1/5 | worse |
| Take profit on shorts at −15% / −25% / −40% | 2.70 / 2.79 / 2.84 | 0.07 / 0.78 / 1.55 | 2/6, 5/6, 3/6 | not adopted (placebo-level) |
| Take profit on longs at +15% / +30% | 2.62 / 2.66 | −2.99 / −1.99 | ≤2/6 | worse |

Faster rebalancing chases hourly noise in the idio-vol ranks. Turnover barely changes because hysteresis holds names anyway, but selection quality drops. Profit-taking cuts winners, and the edge comes from holding the short leg through its drift. **No active variant is adopted; B at 8 h stays the recommendation.**
Session total: about 96 books tested on top of the earlier ~255.
