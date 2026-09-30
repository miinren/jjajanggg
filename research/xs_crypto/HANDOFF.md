# Handoff: XS crypto low-idio-vol book (as of 2026-09-30)

This is research only. No code here trades, and nobody working on this research has access to the live bot or the exchange.

Read this first. Then read `results/wave4/REPORT.md`, which holds the current numbers, and the top of `FINAL_REPORT.md`.

## 1. The one-paragraph version
The live book (**LIVE**) is a market-neutral Binance USDT-M perp strategy. Every 8h it:
- goes long the calmest coins and short the most volatile, by idiosyncratic vol blended with funding;
- hedges net beta with BTC.

About 540 backtests have settled two things:
- **B-MV** is a better version of LIVE. Pseudo-out-of-sample 2023–25, SR **1.54 vs 0.78** at 5.5 bp; risk-matched t **3.08**.
- **Nothing structurally different beats B-MV.** That covers long-only, a smaller short leg and funding-carry shorts.

**Expected live SR is about 1.0** (range 0.8–1.2), vs about 0.3–0.6 for LIVE. The last clean test, B-MV vs LIVE on 2026 data, hasn't been run.

## 2. Recommended configuration (B-MV)
| Rule | LIVE (current) | B-MV (recommended) |
|---|---|---|
| Longs / shorts | 20 / 20 | **12 / 20**. 8 longs is the pseudo-holdout pick, but its edge over 12 is not significant (t 1.1). |
| Leg split | 50 / 50 | **45 long / 55 short** of leg gross |
| Short stop | +40% vs entry | **+20%**, with no re-short of that coin at the next rebalance |
| Long stop | −40% | −40% (unchanged) |
| Short weights | equal | **Minimum variance** on the 336h residual covariance, shrunk 50% to the diagonal, each weight in [0.4×, 2×] equal weight (`minvar_floor`) |
| BTC hedge | re-traded every hour | **no-trade band 0.03 of NAV**, forced re-hedge at rebalances and stops (W06) |
| Score | 0.75 × pct(AR1-corrected idio vol, 336h) + 0.25 × pct(funding) | unchanged; re-confirmed in wave 4 |
| Other | 8h rebalance, hysteresis, funding guard −5e-4, liquid top-third universe | unchanged |

In code, B-MV is:

```python
ext5.book(D, S0, N=12, NS=20, stop=0.2, leg_weights=minvar_floor, simple=True, drift=True, hedge_band=0.03, hedge_fund=True)
```

It is defined in `results/wave4/lib4.py`, and should be averaged over the 8 clock offsets.

### Operational rules for going live
- **Cover any short at ≥ +20% against entry.** Spread the orders over a few hours rather than one market order.
  - Wave 4 event study: after +20/+30/+50%, the coin's average next-72h move is +3.3/+6.3/+8.3% against the short.
  - The median does fade, but about a third rip another +20% within 3 days.
- **Log every stop fill against its trigger.** B-MV's edge over LIVE halves at about 2% average stop slippage and is gone at about 3.5%. This is the main live risk.
- **Size about 1.15× LIVE** for matched volatility.
  - At 1.5× gross on $330: about 2.2% daily vol, about $7–12/month expected, and −35 to −50% drawdowns.

## 3. Key numbers
All use realistic accounting, 8 clocks and 5.5 bp; figures after a slash are at 8 and 12 bp.

| | SR (full 2020–25) | SR (pseudo-OOS 2023–25) | Worst year | mdd at 2%/day vol |
|---|---|---|---|---|
| LIVE | 0.72 / 0.61 / 0.44 | 0.78 / 0.65 / 0.44 | −0.14 | −49% |
| B-MV | 1.41 / 1.24 / 0.98 | 1.46 / 1.28 / 0.99 | 0.55 | −35% |
| B-MV, 8 longs | 1.57 / 1.40 / 1.12 | 1.54 / 1.34 / 1.03 (pipeline pick) | 0.56 | −34% |

**Where the money comes from** (regression on BTC and ETH, B-MV):
- Short leg: alpha **+15.4 bp/day** (t 4.3).
- Long leg: **−11.8 bp/day** per $ (t −2.5); it is beta.
- Whole book: +10 bp/day (t 3.3).
- Funding: about 13% of P&L.
- Raw leg P&L is misleading. The long leg's and hedge's raw profit is bull-market BTC drift, which the short leg pays for.

## 4. History and the traps already found (don't repeat these)
1. **Log-return accounting bug.** The original harness booked P&L as weight × **log** return. That inflates every Sharpe about 2× and invents short-leg alpha, because volatile shorts gain about |w|·r²/2 per hour.
   - Every number before wave 3c's correction box is log-accounted. Use those only as relative comparisons.
   - **Always use `simple=True, drift=True`.**
2. **Clock luck.** Single-clock results vary a lot; the live clock (offset 0) is the luckiest. Always average the 8 rebalance offsets.
3. **`minvar_floor` hard-codes the 45/55 split.** Use `mv_sf(sf)` in `lib4.py` to change `short_frac`, or the change silently does nothing.
4. **Hedge funding.** ext4 ignored funding on the BTC hedge. `ext5` adds it (`hedge_fund=True`), which costs B-MV about 0.09 SR. It matters for any structure with a large hedge.
5. **Multiple testing.** The placebo max t is 1.79, and about 2.5% of random features pass the adoption rule. Require t ≥ 2 and a pseudo-holdout pick before adopting anything.
6. **Already tested and dead:**
   - about 40 new signals;
   - BTC-beta variants: betting-against-beta, downside beta, Dimson betas, an ETH hedge, hedge ratios below 1;
   - active management: faster rebalancing, trailing stops, take-profits, vol targeting, drawdown brakes;
   - execution-timing tricks;
   - a boosted all-feature model;
   - long-only, reduced-short and carry-short books;
   - short idio windows.
   
   Details are in each wave's REPORT.md.

## 5. Open items, in priority order
1. **2026 holdout.** Run LIVE, B-MV (N=12) and B-MV-N8 side by side on 2026 data the user holds. Use realistic accounting and never tune on it. Switch only if B-MV is at least not worse than LIVE.
   - Secondary lead: score funding weight **fw = 0.5** (L 336 or 720). It was the ungated pseudo-holdout pick (OOS SR 1.88), but failed the gate, lost 2023, and is fragile at 12 bp.
2. **Implement B-MV in the live bot.** The bot is `bt/portfolio/idio_micro_live.py` in a repo not attached to this session. `cloud_harness.live_book` documents the exact live rules to diff against.
3. **Stop-slippage monitoring** once live (see §2).
4. **Engine caveat to check in live data:** funding is booked evenly across hours (F/24), but it is actually paid at 00/08/16 UTC. Tests show this doesn't change rankings, but any settlement-timing idea needs it modelled properly.

## 6. How to reproduce
**Setup.** Data and harness are **not in git**. They come from pre-signed S3 links supplied with each task; the links expire, so ask the owner for fresh ones. **Never commit** the data, `cloud_harness.py`, those URLs, or anything containing AWS keys.

```bash
mkdir -p ~/work && cp -r research/xs_crypto/* ~/work/ && cd ~/work
# fetch cloud_harness.py and xs_hourly_2020_2025.npz into ~/work from the supplied URLs
pip install numpy pandas scipy tabulate
cd results/wave4
python verify.py && python verify3.py   # engine checks: ext4 parity 0.0, Wave R SR 1.490, synthetic NAV 3e-9
python s1.py   # structures + pseudo-holdout   (~7 min)
python s2.py   # score grid + pooled OOS       (~7 min)
python diag.py && python diag2.py   # N-step check, leg regressions, pumped-short events
```

**Resources and caching.**
- Each 8-clock book takes about 40–60 s and about 4.6 GB of RAM. Run one Python process at a time.
- Books are cached in `~/work/out4/` (`run8(tag, ...)`). Delete the cache if you change the engine.
- Older waves hard-code `sys.path` entries for `/root/work`; wave 4 uses `~/work`.

**Evaluation method** (validated in wave 3a, used in wave 4):
- **Pseudo-holdout:** select on data before 2023/24/25, test on the next year, pool the test years.
- **Adoption:** risk-matched `ptest`, with ≤1 losing year, ≥4/5 coin groups, both BTC regimes and NW t ≥ 1.5 on the selection window. For a final adoption, also require t ≥ 2 full-sample.
- **Pre-registration:** pre-register in the wave's `trials.csv` with a hard trial cap before running anything.

## 7. File map
| Path | What it is |
|---|---|
| `FINAL_REPORT.md` | Programme summary; the wave 4 and correction boxes at the top supersede older text |
| `PROTOCOL.md`, `report.md` | Original protocol and audit (log-accounted) |
| `common.py` | Loads `D`; builds the score `S0`; `stats`, `cut` |
| `results/wave2/` | `minvar`, `ext3` engine, B-MV adoption (log-accounted) |
| `results/wave3a/` | Pseudo-holdout method; cost and slippage stress |
| `results/wave3b/` | Leg scores, ensembles, minvar plateau |
| `results/wave3c/` | HF timing, hedge band W06, **the log-vs-simple correction**, `ext4` engine, Wave R realistic parameter check |
| `results/wave4/` | **Current.** `ext5` engine, `lib4` (B-MV spec, `run8`, `ptest`, `select`, `oos`), structure study, score check, leg regressions, pumped-short study |

**Git branch:** `claude/xs-realistic-redesign` (pushed; no PR opened).
