# PROJECT_STATE: XS crypto low-idio-vol book (as of 2026-09-30)

> **Audience:** AI agents continuing this work. **Scope:** research only. No agent has exchange credentials or access to the live bot.
> **Sources:** `git show` of the branches below; numbers are quoted from the files cited. Where sources disagree, this file says which wins.

## 0. Rules to follow before doing anything
1. **Accounting.** Always use `simple=True, drift=True`, and from wave 4 on also `hedge_band=0.03, hedge_fund=True` (= `lib4.REAL`). Log-return accounting (the harness default) inflates Sharpe about 2× and invents about 16–17 bp/day of short alpha.
2. **Clocks.** Always average over the 8 rebalance clocks (`lib4.run8`). The live clock, offset 0, is the luckiest.
3. **Pre-registration.** Pre-register every trial in the wave's `trials.csv` with a rationale, under a hard trial cap, before running it.
4. **Adoption bar.** A change needs risk-matched `ptest` ok **and** full-sample NW t ≥ 2.0 (the placebo max was 1.79). Parameter families also need a walk-forward, and any pass needs a ±1-step plateau check.
5. **Holdout.** Never touch or tune on the 2026 holdout. It exists only locally with the owner.
6. **Secrets.** Never commit the data (`xs_hourly_2020_2025.npz`), `cloud_harness.py`, pre-signed S3 URLs, or anything containing `AKIA` or `Signature=`.
7. **Memory.** About 4.6 GB RAM per Python process that imports `common`, and about 40–60 s per 8-clock book. Run one or two processes at a time.

## 1. Branch map (repo `miinren/jjajanggg`, dir `research/xs_crypto/`)
| Branch | Status | Contains |
|---|---|---|
| `claude/xs-realistic-redesign` | **Authoritative, newest** (`eb1be83`) | Everything through **wave 4**: `results/wave4/` (`ext5.py`, `lib4.py`, `s1`/`s2`/`diag`/`verify`, `PREREG.md`), `HANDOFF.md`, updated `FINAL_REPORT.md` |
| `claude/great-ride-mj88zk` | Parallel write-up of the same work (`8fb9545`) | Same code and results; only `HANDOFF.md` and `FINAL_REPORT.md` differ |
| `claude/xs-hf-signals` | Wave 3c branch (`7f6cce9` and later) | Wave 3c, Wave R, **Wave R2 (not merged anywhere else)**, and these `agent_docs/` |
| `main` | No research | — |

**To consolidate:** start from `xs-realistic-redesign` and add the Wave R2 pieces from `xs-hf-signals`:
- `results/wave3c/realistic_score.py` and `realistic_score.txt`;
- trials R09–R13 in `results/wave3c/trials.csv`;
- the "Wave R2" section of `results/wave3c/REPORT.md`.

It is a clean add.

## 2. The strategy (LIVE, the current bot)
The bot is a market-neutral long/short book on Binance USDT-M perps. Its rules are `cloud_harness.live_book(N=20, every=8, L=336, fw=0.25, keepx=0.5, guard=-5e-4, stop=0.40)`, which mirrors `bt/portfolio/idio_micro_live.py` in a repo not attached here.
- **Universe:** the liquid top third of perps by 168h quote volume. BTC, ETH, PAXG and XAUT are excluded.
- **Score:** `0.75·pct(AR1-corrected 336h BTC-residual idio vol) + 0.25·pct(prior-day funding)`.
- **Positions:** long the 20 lowest scores, short the 20 highest, equal weight, 50/50 legs, hysteresis `keep = n + max(4, 0.5n)`. Shorting is not allowed when funding is below −5 bp/day.
- **BTC hedge:** a 168h-beta hedge, re-traded every hour.
- **Stops:** ±40% vs entry. A stopped short is banned until the next rebalance.
- **Clock:** rebalance at 07/15/23 UTC (15:00/23:00/07:00 SGT). Funding settles at 00/08/16 UTC.

## 3. Recommended configuration: B-MV
| Rule | LIVE | B-MV |
|---|---|---|
| Longs / shorts | 20 / 20 | **12 / 20** (8 longs is the pseudo-holdout pick; its edge over 12 is not significant, t 1.14) |
| Leg split | 50 / 50 | **45 long / 55 short** |
| Short stop | +40% | **+20%**, with no re-short until the next rebalance |
| Long stop | −40% | −40% |
| Short weights | equal | **minvar_floor**: min-variance on 336h residual covariance, 50% shrink to diagonal, each weight in [0.4×, 2×] equal weight |
| BTC hedge | hourly re-trade | **W06 no-trade band 0.03 NAV**, with a forced re-hedge at rebalances and stops |
| Score | 0.75 idio + 0.25 funding, 336h, AR1 | unchanged (re-confirmed in Wave R2 and wave 4) |

```python
# one clock (results/wave4/lib4.py, ext5.py):
ext5.book(D, S0, N=12, NS=20, stop=0.2, leg_weights=minvar_floor,
          simple=True, drift=True, hedge_band=0.03, hedge_fund=True)
# canonical 8-clock form (REAL is injected):
lib4.run8("T06_s1", keep_coin=True, N=12, NS=20, stop=0.2, leg_weights=minvar_floor)
```

## 4. Authoritative numbers (wave 4 `results/wave4/REPORT.md`; realistic, 8-clock, SR at 5.5 / 8 / 12 bp)
| Book | Full 2020–25 | Pseudo-OOS 2023–25 | Worst yr | mdd at 2%/day vol |
|---|---|---|---|---|
| LIVE\* | 0.72 / 0.61 / 0.44 | 0.78 / 0.65 / 0.44 | −0.14 | −49% |
| **B-MV (T06)** | **1.41 / 1.24 / 0.98** | 1.46 / 1.28 / 0.99 | 0.55 | −35% |
| B-MV-N8 (T07) | 1.57 / 1.40 / 1.12 | 1.54 / 1.34 / 1.03 (pipeline pick) | 0.56 | −34% |

\* Wave 4's LIVE gets the hedge band and hedge funding, so it slightly flatters the real bot, which re-hedges hourly. The wave-3c realistic LIVE was 0.71 / 0.58 / 0.36.

- **Paired tests:**
  - Pick vs LIVE: t_rm 3.08 (2.33 at 12 bp).
  - Pick vs B-MV: t 1.14. Not significant.
- **Attribution** (regression on BTC and ETH, B-MV):
  - Short leg alpha **+15.4 bp/day (t 4.3)**.
  - Long leg −11.8 bp/day per $ (t −2.5), which is beta.
  - Net +10.1 bp/day (t 3.25).
  - Raw leg P&L is misleading, because bull-market BTC drift flows through the long leg and the hedge.
- **Expected live SR:** about 0.8–1.2, vs about 0.3–0.6 for LIVE. At 1.5× gross on $330 that is about $7–12/month, with −35% to −50% drawdowns.

### Why other B-MV numbers differ (not contradictions)
| Source | Accounting | B-MV SR |
|---|---|---|
| wave3c MAJOR box, "B-MV" | simple + drift, no band, no hedge funding | 1.44 / 1.25 / 0.95 |
| wave3c MAJOR box, "B-MV + hedge band" | **the W12 variant** (band without forced re-hedge, *not adopted*); mislabelled in `xs-realistic-redesign/FINAL_REPORT.md` | 1.50 / 1.34 / 1.09 |
| Wave R base (real W06) | simple + drift + W06, no hedge funding | 1.490 / 1.327 / 1.067 |
| **wave 4 (authoritative)** | + `hedge_fund=True` (hedge is net long BTC and usually pays funding) | **1.405** |

Every figure from waves 1–3b, and the pre-correction parts of 3c (for example SR 2.77 or 2.19), is **log-accounted**. Use those only as relative comparisons.

## 5. What has been tested and failed (do not repeat without a new reason)
- **Execution timing** (wave 3c E01–E16): signal-timed delays of entries and exits lose.
  - TWAP over 3–4h gives about +0.03 SR (t ≈ 2 but fails coin groups), which is harmless to use live.
- **Funding-settlement clock choice** (F00–F02): the settlement-bar effect is real (long candidates +2.4 bp/h, t 5.2), but no clock choice exploits it.
- **Hourly entry filters** (V01–V11): volume spikes, residual jumps and gap reversals all lose.
- **New signals** (about 60, including N01–N06): flow72 has a strong out-of-sample IC but hurts in the book (U-shaped). Idio share, peer momentum, vol-concentration and variance-ratio signals also failed.
- **Tie-breaks and vetoes inside candidate sets** (W01–W04, W09): sign flips between periods.
- **Holistic boosted model on 17 features** (W08): real in-candidate IC of 0.065 (t 11.7, leak-checked), yet the book SR is 2.50 log (t −1.68). It mostly re-orders names the book already holds.
- **Structure** (wave 4): long-only, reduced short leg and funding-carry shorts all lose to B-MV.
- **Also dead:**
  - weight no-trade band (W10);
  - hedge band without forced re-hedge (W12: plateau fails);
  - min-variance long leg (W05);
  - BTC-beta variants (betting-against-beta, downside, Dimson, ETH hedge, hedge ratio below 1);
  - active management (faster rebalancing, trailing stops, take-profit, vol targeting, drawdown brakes);
  - short idio windows (168h: SR 0.74);
  - funding weight 0.10 (0.91).
- **The lesson:** changing *which* names are held keeps failing, because S0's extreme tails carry the premium. Only cost and structure fixes (the W06 hedge band) and risk shape (minvar shorts) have helped.

## 6. Known traps
1. Log-return accounting (see §0).
2. Without `drift=True`, turnover is hidden: 0.469 → 0.571/day.
3. `minvar_floor` hard-codes 45/55 and ignores `short_frac`. Use `lib4.mv_sf(sf)`.
4. ext4 ignores hedge funding. Use ext5 with `hedge_fund=True` (about −0.09 SR for B-MV).
5. W06 vs W12 label confusion (see §4).
6. Funding is booked evenly across hours (F/24) with prior-day `funding_1d`; the real payment happens at 00/08/16 UTC. The stamp convention is unverified (about −0.06 SR effect). Model it before any settlement-timing idea.
7. W06's coin-group wins are a risk-matching artefact, because hedge P&L is not coin-attributed.
8. `wave3c/results_raw.csv` is ragged. Use `results.csv`.
9. "8/8 clocks" is not 8 independent confirmations.
10. Delete cached books (`~/work/out4/`, `/root/work/out3c`) after any engine change.
11. `lib4.score` uses `min_periods = 0.6L`, while S0 uses 200 at L=336. Wave R2 matched S0 exactly.
12. A `pkill -f <script>` inside a bash command also kills the calling shell, because it matches its own command line. `pgrep -f` wait-loops self-match the same way. Kill by PID instead.

## 6b. Latest: owner's lake research + cloud_handoff_1 (2026-09-30)
- **Owner's lake research** (`rh_research` bundle; engine `pf_lib`) is stricter than ours. It adds realistic spreads and impact and share-hold accounting.
  - The old live book: dev SR 0.53, **2026 holdout SR −1.17**. The live bot is **stopped**; $329 sits in USDT.
  - About 1,000 variants have been tried across agents, so new results need **t ≥ 3**.
- **`cloud_handoff_1/report.md`, Task A (beta-neutral betting-against-beta):**
  - Rank IC is strong: low beta beats high beta even beta-adjusted, Spearman t ≈ 10 at 1 day.
  - The Fama–MacBeth SML is flat (γ t ≈ −1).
  - The beta-neutral BAB finalist has dev alpha t 1.53 (DSR 0.56). The 2025 one-look is SR 1.84, but about 45% of that is funding and it had a −22% month.
  - **Not adoptable.** At most a paper-trade candidate.

## 7. Open items (priority order)
1. **2026 holdout:** LIVE vs B-MV (N=12) vs B-MV-N8, realistic accounting, no tuning. Switch only if B-MV is not worse than LIVE.
   - Secondary lead: fw = 0.5, which was the ungated OOS pick (1.875 vs 1.462, t 1.77). It failed the gate, lost 2023 and is fragile at 12 bp.
2. **Merge Wave R2** into `xs-realistic-redesign` and fix the W12 label in `FINAL_REPORT.md`.
3. **Implement B-MV in the live bot:** diff `bt/portfolio/idio_micro_live.py` against `cloud_harness.live_book`, then roll out in stages (book first, then hedge band). See `LIVE_OPS_CHECKLIST.md`.
4. **Monitor stop slippage** once live, logging every stop fill against its trigger. B-MV's edge halves at about 2% average slippage and is gone at about 3.5%.
5. **Engine realism:** discrete funding settlement, and resolve the `funding_1d` stamp.
6. **New data** (open interest, token unlocks, listings) as short-side risk vetoes. `data.minrei.com` is blocked by the cloud network policy until allowed.

## 8. Reproduce
```bash
mkdir -p ~/work && cp -r research/xs_crypto/* ~/work/ && cd ~/work
# place cloud_harness.py + xs_hourly_2020_2025.npz here (pre-signed URLs from the owner; never commit)
pip install numpy pandas scipy tabulate
cd results/wave4 && python verify.py && python verify3.py   # ext4 parity 0.0, Wave R SR 1.490, synthetic NAV 3e-9
python s1.py; python s2.py; python diag.py; python diag2.py
```
- **Read first:**
  - `HANDOFF.md` and `results/wave4/REPORT.md` on `xs-realistic-redesign`;
  - the Wave R and Wave R2 sections of `results/wave3c/REPORT.md` on `xs-hf-signals`.
- **Engine chain:** `ext.py` → `wave2/ext3.py` → `wave3c/ext4.py` → `wave4/ext5.py`.
