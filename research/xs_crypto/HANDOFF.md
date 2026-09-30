# Handoff: xs-crypto low-idio-vol book: robustness audit and redesign

**Date:** 2026-09-30 · **Repo/branch:** `miinren/jjajanggg` @ `claude/great-ride-mj88zk`, folder `research/xs_crypto/`
**Status:** research complete. Nothing is running or scheduled, and no live trading was touched.

---

## 1. TL;DR
1. **The backtest harness has an accounting bug that inflates every Sharpe about 2x.** P&L is booked as weight × **log** return instead of weight × **simple** return. For a book that shorts the most volatile coins, this manufactures profit.
   - The live config's backtest SR drops from **2.2 to about 0.7–0.8** once corrected.
   - **Fix this in any harness you keep using** (see §4).
2. **Recommended change: switch the live book to "B-MV"** (spec in §3).
   - Under correct accounting it beats the live config in every year: realistic SR **1.41 vs 0.72**.
   - Pooled out-of-sample 2023–25 with pick-then-test selection: **1.46–1.54 vs 0.78**, t 3.08.
3. **Realistic live expectation for B-MV:**
   - Sharpe **0.8–1.2**, versus about 0.4–0.7 for the current config.
   - About **$9–14 per month on a $330 account at 1.5x gross**.
   - Plan for a **−35% drawdown** and occasional **−15 to −20% days**.
4. **Searched and found nothing:** ~60 new signals, ~15 BTC-beta ideas, higher-frequency timing and signals, active intra-period management, universe changes, and alternative book structures. The only improvements that survived are structural (§3) plus two cost savings.

---

## 2. What was done (chronological)
Each wave has its own `REPORT.md`, `trials.csv` and scripts under `results/`.

| Stage | Question | Outcome |
|---|---|---|
| Audit (`report.md`) | Noise floor, parameter stability, realistic SR, costs | The live config sits on a plateau. A random-feature placebo gives t up to 1.79, so we set the adoption bar at t ≥ 2.0 |
| Rounds 1–2 (`report.md`) | Drawdown and EV improvements, number of positions, active variants | Found "B": 12 longs / 20 shorts, 55% short, 20% short stop |
| `drawdown/` | Squeeze filters, hedge fixes, construction | Nothing passed. Min-variance short weights improved tail shape |
| `signals/` | ~50 new signals, BTC lead-lag | Nothing. BTC lead-lag is not tradable |
| `active/` | Stops, cuts, hourly exits, and what happens to −20% positions | The 20% short stop is the right amount of intervention; everything more active was worse |
| `clock/` | Is B's result luck of the rebalance hour? | B beats LIVE at 8/8 clocks; B's headline number is about 0.15 SR lucky |
| `wave2/` | Placebo-test the min-var short leg; universe breadth | Min-var passes the pre-registered tail-risk test, and a $5-floored version is tradable. Breadth: nothing |
| `wave3a/` | Pseudo-holdout of the whole selection process; realistic costs; stop slippage | The process picks the same config in every window, and about 45% of the in-sample uplift survives. Stop slippage ≥ 2% largely erases the edge |
| `wave3b/` | Leg-specific scores, ensembles, min-var plateau | Nothing adopted. N=8 longs is a borderline lead |
| `wave3c/` (cloud session) | Higher-frequency timing and signals | **Found the log-return bug.** Adopted a 0.03 hedge no-trade band (cost-only). TWAP over ~3h is harmless and slightly positive |
| `wave4/` (cloud session) | Redesign under correct accounting | No structure beats B-MV. The short leg carries the alpha (+15 bp/day vs BTC+ETH, t 4.3); the long leg is beta. N=8 is the pipeline pick |

About 700 backtests were run in total, most of them 8-clock averaged. Every adoption used pre-registration, risk-matched partition tests, placebo or walk-forward checks, and from wave 3 on, pseudo-holdout.

---

## 3. Recommended live configuration: B-MV
Changes relative to the current live book (`live_book(N=20, every=8, L=336, fw=0.25, keepx=0.5, guard=-5e-4, stop=0.40)`):

| # | Setting | Current | B-MV |
|---|---|---|---|
| 1 | Long / short count | 20 / 20 | **12 / 20** (8 / 20 optional; see §6) |
| 2 | Leg split of gross | 50 / 50 | **45 long / 55 short** |
| 3 | Short stop (from entry) | +40% | **+20%**; don't re-short that name at the next rebalance |
| 4 | Long stop | 40% | 40% (unchanged; tighter long stops hurt) |
| 5 | Short weights | equal | **Min-variance** on the 336h residual (beta-adjusted) covariance of the chosen shorts, **50% shrink toward the diagonal**, each weight clipped to **[0.4×, 2×] equal weight** and renormalised. The 0.4× floor keeps each short ≥ $5 at $330 × 1.4 |
| 6 | BTC hedge | re-traded every hour | Re-trade at rebalances and stops; otherwise only when \|target − current\| > **0.03 of NAV** |
| 7 | Execution | at once | Optional: split each rebalance over about 3 hours (TWAP) |
| 8 | Gross leverage | 1.5x | About 1.15× the current risk-equivalent. B-MV runs 15–20% less volatile, so ~1.5–1.7x gross matches today's risk. Staying at 1.5x means slightly less risk |

Unchanged: the score (`0.75·pct(AR1-corrected idio vol, 336h) + 0.25·pct(funding)` within the liquid tercile), the 8h rebalance clock, hysteresis, the funding guard, the BTC-beta hedge itself, and BTC/ETH/PAXG/XAUT exclusions.

**Reference code:**
- min-var weights: `results/wave2/lib.py` (`minvar`) and `results/wave2/s3_floor.py` (`minvar_floor`);
- hedge band: `results/wave3c/ext4.py` (`hedge_band=`);
- the full realistic engine: `results/wave4/ext5.py`.

### Evidence (realistic accounting, 8-clock average, 5.5 bp; from wave4)
| Book | SR 5.5 / 8 / 12 bp | Max DD at 2%/day vol | Worst-year SR |
|---|---|---|---|
| Current live | 0.72 / 0.61 / 0.44 | −49% | −0.14 |
| B-MV (12 longs) | 1.41 / 1.24 / 0.98 | −35% | 0.55 |
| B-MV (8 longs) | 1.57 / 1.40 / 1.12 | −34% | 0.56 |

Pooled out-of-sample 2023–25 (each year selected on earlier data only):

| Book | SR |
|---|---|
| Pipeline pick | 1.54 |
| B-MV | 1.46 |
| LIVE | 0.78 |

---

## 4. The accounting bug (fix before trusting any backtest)
- **The bug.** `cloud_harness.py` sets `D.Rn = log(C).diff().shift(-2)` and books `pnl = w * Rn`. Real P&L is `w * (exp(Rn) - 1)`. For a short, log accounting overstates P&L by about |w|·r²/2 per hour; for a long it understates it.
- **Why it matters here.** The book shorts the highest idio-vol coins, so the bias looks like alpha: about 16 bp/day of phantom short-leg P&L.
- **Minimal fix:** `D.Rn = np.expm1(D.Rn); D.rbn = np.expm1(D.rbn)`. This reproduces LIVE at SR 0.78.
- **Fully realistic fix:** let positions drift between trades (`simple=True, drift=True` in `results/wave3c/ext4.py` / `wave4/ext5.py`), and charge funding on the BTC hedge too (ext5).
- **Consequence.** Every number in `report.md` and in waves 1–3b is log-accounted and should be read as relative only. `FINAL_REPORT.md` has a correction box at the top.

---

## 5. Operating guidance
- **Pumped shorts:** cover at +20% against you. About 25% of shorts reach it, roughly 4 a week. Only about 1% recover by the next rebalance, and 60% touch −30% within 3 days.
- **Losing longs:** hold them at −20%; they tend to bounce slightly.
- **Don't intervene by hand.** Discretionary-style exits (time stops, rank exits, book brakes) were the worst performers (t −3 to −4).
- **Monitor stop slippage.** Log each short-stop fill against its 20% trigger. B-MV's edge over LIVE holds at 1% average slippage (t 2.2), weakens at 2% (t 1.3), and is gone at about 3.5%. If live slippage averages ≥ 2%, reconsider.
- **Minimum notional.** At $330 × 1.4 gross, shorts are about $8–30 and longs about $17 (≥ $5 guaranteed by the floor). At 8 longs, longs are about $26.

---

## 6. Open items / next steps (in priority order)
1. **2026 holdout test (most important).** Run B-MV (12 and 8 longs) vs the current config on 2026 data, which was never used in this research. Use realistic accounting. Switch only if B-MV is at least not worse.
2. **Implement in the bot.** The bot's code was not accessible; the harness docstring references `bt/portfolio/idio_micro_live.py`. Add its repo, or paste the strategy file, and the changes in §3 can be written as a patch.
3. **Fix the accounting** in your own research harness (§4) and re-baseline.
4. **Leads to check on 2026 only; don't tune them in-sample:**
   - N = 8 longs;
   - funding weight fw = 0.5 (OOS SR 1.88, but weak in 2023 and +35% turnover);
   - a "near 30-day high" sleeve.
5. **Unresolved data question:** whether `funding_1d` is stamped same-day or prior-day. The worst case costs about −0.06 SR for every book and doesn't change the ranking.
6. **Not done:** the S3 upload of the report. The upload URL in the original brief was truncated.

---

## 7. Reproducing
- **Data:** `xs_hourly_2020_2025.npz` and `cloud_harness.py` come from presigned S3 URLs, which are in the original brief and are not committed here (they contain an AWS key ID). Put them in the working folder.
- **Library chain:** `common.py` builds the data object and the live score S0 (AR1-corrected), and `ext.py` is the book engine. The extensions chain `ext.py → wave2/ext3.py (clock offset) → wave3c/ext4.py (execution, simple/drift, hedge band) → wave4/ext5.py (hedge funding, leg funding)`.
- **Runtime:** each Python process uses about 4.6 GB RAM, and a single book takes about 8 s on one core.
- **Evaluate 8-clock averaged** (`wave2/lib.py:avg8`). Single-clock results can be off by ±0.2 SR.
- **Adoption rule:** `PROTOCOL.md`.

---

## 8. File map (`research/xs_crypto/`)
- `HANDOFF.md`: this file.
- `FINAL_REPORT.md`: running summary with the correction box and wave 3–4 updates.
- `report.md`: original audit and rounds 1–2 (log accounting).
- `PROTOCOL.md`: the research and adoption protocol used by all agents.
- `common.py`, `ext.py` and the root `*.py` files: the base library and early experiment scripts.
- `results/<wave>/REPORT.md`, `trials.csv` and scripts: `drawdown`, `signals`, `active`, `clock`, `wave2`, `wave3a`, `wave3b`, `wave3c`, `wave4`.
