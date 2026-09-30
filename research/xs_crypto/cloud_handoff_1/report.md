# cloud_handoff_1: Task A. Beta-neutral rebuild of `beta_30d` / anti-beta (betting-against-beta) on Binance USDT-M perps

Cloud Claude session, 2026-09-30. The data is `xs_hourly_2020_2025.npz` (608 perps, hourly), with accounting from **pf_lib**: simple returns, share-hold dollar P&L, funding cash, 5 bp taker fee plus ADV-bucket half-spread plus square-root impact at $15k gross, and a 1h execution delay.

- **Development window:** 2020-03-15 → 2024-12-31.
- **Holdout:** 2025, one look, for the finalist only. It is recorded in `code/pf_holdout_ledger.csv` under key `cloud1_B_EW_C_BAB_48h_2025`.
- **Pre-registration:** written before any result and kept in `cloud1/PREREG.md`.

## Verdict
**No adoptable edge. It is not a clean negative either: it is a weak, economically plausible betting-against-beta premium that stays below the evidence bar.**

1. **Ranks versus dollars.**
   - In ranks, low-beta perps reliably beat high-beta perps, even after adjusting for beta. The Spearman IC of −beta is about +0.06 at 1 day with NW t of about 10, and the half-life is about 27 days.
   - In dollars the effect is small and fat-tail-dominated. Pearson IC is half of Spearman, and dollar-neutral books suffer drawdowns of up to −94% of gross. High-beta names rip in squeezes and alt seasons.
2. **The SML is flat, not inverted.** In the Fama–MacBeth test, the CAPM intercept γ is −20 bp/d (t −1.1) against the EW alt market and −12 bp/d (t −0.8) against BTC. The slope on the market is δ ≈ 0.6–0.7, below 1. This is consistent with the literature, e.g. Liu–Tsyvinski–Wu (JF 2022), who find beta insignificant in the crypto cross-section.
3. **The original `beta_30d` long/short is a disguised market bet.** The dollar-neutral quintile book (C_RAW) has an ex-post alt-market beta of −0.25 and SR 0.30–0.42.
   - Hedging with BTC (C_HEDGE) raises SR to about 1.0, but only by leaving the book **about +0.3–0.4 long BTC**; its alpha t is 1.0–1.6. That fails the pre-registered |β| < 0.2 rule.
4. **The properly beta-neutral Frazzini–Pedersen BAB book is the pre-registered finalist:** EW beta, 48h rebalance, ex-post β of 0.09 to BTC and 0.06 to the alt market.
   - **Dev:** SR 1.06, t 2.00. **Alpha t is 1.53** against a required **3.0**.
   - **Deflated SR probability is 0.56** at N = 1,012 trials, against 0.95 required.
   - **Dev years** 2020–2024: SR 2.6, 1.8, 0.2, −0.4, 1.3 (4 of 5 positive).
   - **Walk-forward** over the 12-trial family: SR 0.27 (t 0.52).
5. **The one-look 2025 holdout is positive:** SR 1.84, t 1.66, alpha 12.7 bp/d at t 1.72, ex-post β 0.09 / 0.01. Two caveats:
   - About **45% of 2025 net came from funding** (+5.6 of 12.4 bp/d). The book is net long about 0.44 in dollars and received funding from crowded high-beta shorts.
   - **April 2025 lost −22%.**

   One positive year cannot rescue a dev t of 1.5. Also, 2025 is only "fresh" for this idea: earlier waves on this dataset used it.

**Recommendation:**
- Do **not** trade it at size.
- If you want a live experiment, paper-trade or micro-size the finalist as specified (EW beta, BAB, 48h, pf_lib costs). Judge it on data after 2026-10 against a pre-set kill rule, for example stop if 6-month alpha t < 0.
- The handoff's t ≥ 3 bar would need roughly 4× more independent history at the same effect size.

## Method
- **Universe and conventions:** `pf_crypto.load()`, i.e. the liquid tercile; BTC/ETH/PAXG/XAUT are never ranked and BTC is the hedge instrument.
- **Signals.** Both are the 720h OLS beta (minimum 168 observations) of hourly simple returns known at t:
  - **B_EW:** beta on the equal-weight return of all tradable perps. This is the IC agent's `beta_30d`.
  - **B_BTC:** beta on BTC.

  The book signal is −β.
- **Diagnostics.** These are not counted as trials.
  - **D1:** Pearson (z-clipped) and Spearman IC against **simple forward returns net of long funding**, at 1h–14d with a 1h delay. Also against beta-adjusted forward returns (r_i − β_i·r_mkt). The grid is every 8h (every 24h for h > 1d), and NW lags are ⌈1.5h/step⌉ + 1. Half-life comes from fitting b(h) = Aτ(1 − e^(−h/τ)) to the cross-sectional slope in bp per standard deviation.
  - **D2:** a Fama–MacBeth SML test on non-overlapping daily cross-sections, λ_t = γ + δ·mkt_t.
- **Book trials (12, pre-registered)** = 2 signals × 3 constructions × {24h, 48h}.
  - All use quintile legs (q = 0.2) with inverse-vol weights from a lagged EWMA (half-life 168h), and no stops.
  - Each trial is averaged over 4 rebalance-clock offsets.
  - Constructions:
    - **C_RAW:** dollar-neutral.
    - **C_HEDGE:** C_RAW plus a BTC hedge sized by the ex-ante 168h BTC beta, using pf_lib's `hedge`.
    - **C_BAB:** Frazzini–Pedersen. Each leg is scaled to ex-ante β = 1 (1/β_leg, capped at 3×) and gross is normalised to 1, so the book is net long in dollars.
  - Ex-post α and β come from regressing daily net on daily BTC and EW-market returns, with NW t.
- **Adoption rule (pre-registered).** All of the following:
  - dev α t ≥ 3;
  - DSR ≥ 0.95 at N = 1,012 (about 1,000 prior plus 12);
  - at least 4 of 5 dev years positive;
  - 2025 holdout SR > 0 with α t > 0.

## D1: IC decay, dev (−β signal; positive IC = low beta outperforms)
**B_EW (beta to the EW alt market):**

|   h (hours) |   pearson IC |    t |   spearman IC |    t  |   spearman beta-adj |   t   |   slope bp/sd |   n_eff |
|------------:|-------------:|-----:|--------------:|------:|--------------------:|------:|--------------:|--------:|
|           1 |       0.0192 | 4.89 |        0.027  |  6.49 |              0.031  |  9.57 |          1.53 |   36096 |
|           4 |       0.0202 | 5    |        0.0343 |  8.19 |              0.0388 | 11.33 |          2.53 |    9024 |
|          12 |       0.0258 | 5.33 |        0.0498 | 10    |              0.0531 | 12.31 |          5.34 |    3007 |
|          24 |       0.0292 | 4.55 |        0.0614 |  9.38 |              0.0597 | 10.46 |          7.69 |    1503 |
|          48 |       0.0362 | 4.04 |        0.0672 |  7.31 |              0.0659 |  8.07 |         12.74 |     751 |
|          72 |       0.0411 | 3.8  |        0.0763 |  7.01 |              0.0705 |  7.33 |         18.91 |     500 |
|         120 |       0.0426 | 3.11 |        0.0812 |  5.97 |              0.0739 |  5.98 |         29.12 |     300 |
|         168 |       0.046  | 2.96 |        0.0885 |  5.67 |              0.0773 |  5.26 |         36.69 |     214 |
|         336 |       0.0615 | 3.08 |        0.106  |  5.17 |              0.087  |  4.39 |         72.64 |     106 |

Half-life fit: A = 0.255 bp/h/sd, τ = 934h, **half-life about 648h (27 days)**.

**B_BTC:**

|   h (hours) |   pearson IC |    t |   spearman IC |   t  |   spearman beta-adj |   t   |   slope bp/sd |   n_eff |
|------------:|-------------:|-----:|--------------:|-----:|--------------------:|------:|--------------:|--------:|
|           1 |       0.0121 | 3.14 |        0.0179 | 4.48 |              0.0211 |  5.94 |          0.82 |   36096 |
|           4 |       0.0121 | 3.07 |        0.0221 | 5.43 |              0.0271 |  7.37 |          1.07 |    9024 |
|          12 |       0.0144 | 3.03 |        0.0296 | 6.1  |              0.0344 |  7.58 |          2.36 |    3007 |
|          24 |       0.0164 | 2.61 |        0.0372 | 5.83 |              0.0393 |  6.71 |          3.02 |    1503 |
|          48 |       0.0234 | 2.64 |        0.0428 | 4.79 |              0.0476 |  5.73 |          5.77 |     751 |
|          72 |       0.027  | 2.56 |        0.0501 | 4.78 |              0.0546 |  5.58 |          9.99 |     500 |
|         120 |       0.0271 | 2.06 |        0.053  | 4.11 |              0.0598 |  4.72 |         17.13 |     300 |
|         168 |       0.0292 | 1.95 |        0.0585 | 3.95 |              0.0671 |  4.45 |         20.82 |     214 |
|         336 |       0.0423 | 2.17 |        0.073  | 3.58 |              0.0798 |  3.58 |         49.89 |     106 |

Half-life: τ hits the 5000h bound, so no decay is visible within 14 days.

**Reading:**
- The rank ICs are highly significant and beta adjustment barely changes them. Crypto has a genuine cross-sectional low-beta tilt in *typical* names.
- Pearson ICs are only about half the Spearman values, so the dollar edge is much weaker than the rank edge. The losses come from the tails, the high-beta names that squeeze.
- The IC agent's 2024–26 result (rank IC about −0.02 to −0.03 for +β) is reproduced with the same sign over 2020–24.

## D2: Fama–MacBeth SML test (daily, dev)
| market | mean λ (bp/d) | t | mean mkt (bp/d) | γ (bp/d) | t(γ) | δ |
|---|---|---|---|---|---|---|
| EW alts | −6.3 | −0.33 | 20.0 | **−19.6** | **−1.10** | 0.67 |
| BTC | −2.7 | −0.17 | 16.5 | **−12.0** | **−0.79** | 0.57 |

γ by year, EW (bp/d): 2020 −122, 2021 −42, 2022 −19, 2023 +3, 2024 −8. The magnitude has shrunk over time, and no year is significant.

## Book trials (dev 2020-03-15 → 2024-12-31, net of pf_lib costs; 4-offset average)
Units: `net_bp`, `gross_bp`, `fund_bp` and `cost_bp` are bp/day; `maxdd` is a fraction of gross.

| trial             |   sharpe |   t_nw |   boot_p |   net_bp |   gross_bp |   fund_bp |   cost_bp |    to |   net_exp |   maxdd |   alpha_bp |   alpha_t |   beta_btc_multi |   beta_ew_multi | yearly                                                          |
|:------------------|---------:|-------:|---------:|---------:|-----------:|----------:|----------:|------:|----------:|--------:|-----------:|----------:|-----------------:|----------------:|:----------------------------------------------------------------|
| B_EW|C_RAW|24h    |    0.297 |  0.617 |    0.283 |    3.628 |      5.279 |     0.145 |     1.796 | 0.254 |     0     |  -0.929 |      6.502 |     1.2   |            0.117 |          -0.266 | {2020: 1.34, 2021: -0.02, 2022: 1.67, 2023: -1.25, 2024: -0.12} |
| B_EW|C_RAW|48h    |    0.416 |  0.853 |    0.195 |    4.954 |      6.051 |     0.251 |     1.348 | 0.19  |     0.001 |  -0.943 |      7.838 |     1.454 |            0.11  |          -0.253 | {2020: 1.32, 2021: 0.55, 2022: 1.53, 2023: -1.36, 2024: 0.03}   |
| B_EW|C_HEDGE|24h  |    0.813 |  1.686 |    0.05  |    9.556 |     12.458 |    -0.798 |     2.104 | 0.304 |     0.339 |  -0.674 |      6.491 |     1.218 |            0.391 |          -0.237 | {2020: 3.0, 2021: 0.27, 2022: 0.44, 2023: -0.15, 2024: 1.15}    |
| B_EW|C_HEDGE|48h  |    0.989 |  2.022 |    0.021 |   11.341 |     13.622 |    -0.709 |     1.572 | 0.226 |     0.339 |  -0.609 |      8.273 |     1.573 |            0.388 |          -0.231 | {2020: 3.07, 2021: 0.85, 2022: 0.23, 2023: -0.25, 2024: 1.38}   |
| B_EW|C_BAB|24h    |    0.864 |  1.687 |    0.052 |    8.768 |     11.05  |    -0.676 |     1.606 | 0.237 |     0.318 |  -0.64  |      6.013 |     1.195 |            0.092 |           0.05  | {2020: 2.07, 2021: 1.3, 2022: 0.4, 2023: -0.29, 2024: 1.16}     |
| B_EW|C_BAB|48h    |    1.055 |  2     |    0.027 |   10.521 |     12.378 |    -0.649 |     1.208 | 0.177 |     0.318 |  -0.649 |      7.75  |     1.532 |            0.089 |           0.057 | {2020: 2.6, 2021: 1.76, 2022: 0.15, 2023: -0.41, 2024: 1.34}    |
| B_BTC|C_RAW|24h   |    0.151 |  0.291 |    0.378 |    1.768 |      3.09  |     0.605 |     1.927 | 0.274 |     0     |  -1.082 |      5.55  |     0.975 |           -0.012 |          -0.182 | {2020: 1.9, 2021: -0.55, 2022: 1.11, 2023: -1.23, 2024: -0.3}   |
| B_BTC|C_RAW|48h   |    0.383 |  0.762 |    0.211 |    4.348 |      5.125 |     0.651 |     1.428 | 0.202 |     0     |  -1.044 |      8.1   |     1.513 |           -0.02  |          -0.168 | {2020: 2.4, 2021: 0.11, 2022: 1.08, 2023: -1.31, 2024: -0.26}   |
| B_BTC|C_HEDGE|24h |    0.767 |  1.426 |    0.075 |    8.516 |     11.388 |    -0.66  |     2.213 | 0.321 |     0.373 |  -0.711 |      5.744 |     1.002 |            0.305 |          -0.165 | {2020: 3.76, 2021: -0.26, 2022: -0.11, 2023: 0.06, 2024: 1.08}  |
| B_BTC|C_HEDGE|48h |    1.062 |  2.033 |    0.022 |   11.467 |     13.723 |    -0.62  |     1.637 | 0.237 |     0.374 |  -0.641 |      8.6   |     1.603 |            0.303 |          -0.156 | {2020: 4.44, 2021: 0.39, 2022: -0.24, 2023: 0.01, 2024: 1.15}   |
| B_BTC|C_BAB|24h   |    0.421 |  0.811 |    0.209 |    4.11  |      6.199 |    -0.291 |     1.798 | 0.264 |     0.298 |  -0.823 |      2.371 |     0.473 |            0.018 |           0.071 | {2020: 1.57, 2021: 0.63, 2022: 0.07, 2023: -0.5, 2024: 0.63}    |
| B_BTC|C_BAB|48h   |    0.611 |  1.192 |    0.111 |    5.79  |      7.428 |    -0.3   |     1.338 | 0.196 |     0.297 |  -0.846 |      4.056 |     0.853 |            0.013 |           0.078 | {2020: 2.1, 2021: 1.17, 2022: -0.12, 2023: -0.57, 2024: 0.59}   |

- **Trial SR variance** (annualised) is 0.091.
- **Yearly walk-forward** over the 12 trials (30-day embargo) picked C_HEDGE three times and C_BAB once. OOS SR is 0.27 (t 0.52).

## Finalist and one-look holdout: B_EW | C_BAB | 48h
| | dev 2020–24 | **holdout 2025** |
|---|---|---|
| Net SR (NW t) | 1.06 (2.00) | **1.84 (1.66)**; bootstrap p 0.053; 90% CI 0.09–3.68 |
| α vs BTC + EW (t) | 7.8 bp/d (1.53) | 12.7 bp/d (1.72) |
| Ex-post β (BTC / EW) | 0.09 / 0.06 | 0.09 / 0.01 |
| Net = gross + funding − cost (bp/d) | 10.5 = 12.4 − 0.6 − 1.2 | 12.4 = 8.0 + 5.6 − 1.1 |
| Turnover/day; net dollar exposure | 0.18; +0.32 | 0.16; +0.44 |
| Max DD (fraction of gross) | −0.65 | −0.31 |
| Deflated SR probability (N = 1,012) | 0.56 | – |

Monthly holdout net (%): Jan +5.3, Feb +3.2, Mar +10.4, **Apr −22.0**, May −6.1, Jun +4.2, Jul +8.7, Aug +9.8, Sep +17.2, Oct +0.3, Nov +4.4, Dec +10.0.

## Why the verdict stays negative despite the positive holdout
- **The dev evidence is weak.**
  - α t is 1.5, against the t ≥ 3 the handoff requires given about 1,000 prior variants.
  - DSR is 0.56.
  - The walk-forward over the family does not beat 0 significantly.
- **The FM test shows a flat SML** rather than a robust negative intercept. The BAB return is partly the leverage mechanics that profit from a flat SML, which is not an anomaly one can count on.
- **2025's result leans on funding carry** (45%) and has a −22% month. A single year cannot supply the missing t-stat.
- **Squeeze tails dominate dollar outcomes.** Every construction has drawdowns of 60–100% of gross in dev, so sizing would have to be tiny.

## Next steps (only if you want to pursue it)
1. **Forward test.** Paper-trade or micro-size the frozen finalist on data after 2026-10, with a kill rule set before starting.
2. **Honest improvements**, each to be pre-registered and counted:
   - Shrunk or Dimson betas. Beta forecastability in crypto is low, about 20% R².
   - A cap on the short-leg names' MAX/squeeze exposure.
   - Maker execution at 48h.
3. **Explain the funding component** before trusting any BAB P&L. Separate the price-only α from the funding carry; carry is a known but regime-dependent crypto premium.

## Files (in the bundle's `rh_research/cloud1/`)
- `PREREG.md`
- `common1.py`: setup and betas.
- `books1.py`: constructions, including the BAB runner through pf_lib's simulate and cost path.
- `d1_ic.py`: IC decay and the FM test.
- `b1_books.py`: the 12 trials and the walk-forward.
- `h1_holdout.py`: DSR and the one-look holdout.
- Outputs: `d1_ic_decay.csv`, `d2_fm_sml.csv`, `b1_books_dev.csv`, `h1_holdout_daily.pkl`.
