# HERDR_BRIEF: everything the cloud session learnt (2026-09-30 → 10-01)

> **Audience:** the owner's local agents (herdr on the Mac).
> **What this is:** a single-file digest. Details live in the linked files on branch `claude/xs-hf-signals` of `miinren/jjajanggg`.
> **Scope:** research only. No exchange access was ever used.
> **Secrets:** never commit data, `cloud_harness.py`, or presigned S3 URLs.

## 0. Bottom line
1. **No crypto strategy currently has a demonstrated edge.** Keep the live bot **off**; $329 is in USDT.
   - The old live book's apparent Sharpe of 2.2 was an accounting artefact.
   - Under correct dollar accounting it is about 0.5–0.9 in dev and **−1.2 on the 2026 holdout** (owner's `pf_lib`).
2. **Accounting rule.** Summing weight × log return fakes short-side alpha on volatile coins (about |w|·r²/2 per hour). Always use simple returns with share-hold (drifting-weight) dollar P&L.
   - Engines: owner's `rh_research/code/pf_lib.py`, or this repo's `ext4`/`ext5` with `simple=True, drift=True`.
   - Treat any high Sharpe as a bug first.
3. **Multiple testing.** About 1,000+ variants have been tried across all agents, so a new result needs **t ≥ 3**.
4. **Best remaining lead: weak, unproven, paper-trade only.** A beta-neutral betting-against-beta book (§3).

## 1. The book and its research history (repo `research/xs_crypto/`)
- **LIVE strategy.** Every 8h, on Binance USDT-M perps in the liquid top third:
  - long the 20 lowest and short the 20 highest of `0.75·pct(AR1-corrected 336h BTC-residual idio vol) + 0.25·pct(funding)`;
  - equal weight, BTC-beta hedge, ±40% stops, funding guard −5 bp, hysteresis;
  - rebalances at 07/15/23 UTC (15:00/23:00/07:00 SGT).
- **B-MV**, the "recommended" upgrade under the in-repo harness:
  - 12 long / 20 short, 55% short;
  - +20% short stop;
  - min-variance short weights;
  - W06 hedge no-trade band 0.03.
  - Realistic SR (harness costs 5.5 bp flat) is **1.41** for B-MV vs 0.72 for LIVE, in wave 4 with hedge funding.
- **Caution.** The owner's stricter `pf_lib` (spreads by ADV, impact, share-hold) gives the old LIVE rules SR 0.53 in dev and −1.17 on the 2026 holdout. Treat in-repo harness levels as optimistic. The **relative** findings below still hold.
- **Authoritative branch for in-repo research:** `claude/xs-realistic-redesign` (wave 4, `ext5`).
  - This branch has wave 3c, Wave R/R2, `agent_docs/` and `cloud_handoff_1/`.
  - Wave R2 is not yet merged into `xs-realistic-redesign`.

## 2. What was tested and failed (do not repeat without a new reason)
- **Execution timing (wave 3c, E01–E16).** Delaying entries or exits on 1–3h residual signals loses.
  - Most of that loss was extra BTC-hedge re-trading.
  - Even with it fixed, the gain is about +0.03 SR and not robust.
  - TWAP over 3–4h gives about +0.03 SR: harmless, not significant.
- **Funding settlement.** The bar after 00/08/16 UTC shows a real cross-sectional effect:
  - long candidates +2.4 bp/h (t 5.2);
  - negative-funding coins −3.4 bp/h (t −5.4).

  No clock choice exploits it, because every 8h hold spans one settlement bar.
- **Hourly entry filters** (volume spike, jump, gap reversal; V01–V11): all lose.
- **New signals** (flow72, idio-share, peer momentum and others): some have strong out-of-sample IC, but every one hurts in the book.
  - The flow72 effect is U-shaped.
  - A holistic 17-feature gradient-boosted model has a real in-candidate IC of 0.065 (t 11.7, leak-checked), yet the book still loses (SR 2.50 vs 2.77 log; t −1.7). It mostly re-orders names already held.
- **Lesson:** changing *which* names are held keeps failing. Only cost and structure fixes (hedge band) and risk shape (min-variance shorts) helped.
- **Parameter re-check under correct accounting (Wave R, R2):**
  - short 55%, NS 20, stop 20%, funding weight 0.25, L 336h and AR1 all confirmed;
  - N = 8 longs is borderline (SR 1.66 vs 1.49, t 1.98).

## 3. Task A result (`cloud_handoff_1/report.md`, also uploaded to S3 `research/results/cloud_handoff_1.md`)
**Question:** is `beta_30d` / anti-beta a real betting-against-beta premium? Setup: `pf_lib` accounting, dev 2020-03 → 2024, one look at 2025.
- **Rank IC is strong.** Low beta beats high beta even beta-adjusted: Spearman about +0.06 at 1 day, t ≈ 10, half-life about 27 days. **Pearson IC is about half that**: squeezes in high-beta names eat the dollar P&L.
- **The Fama–MacBeth SML is flat, not inverted:** γ t −1.1 (EW market) and −0.8 (BTC), δ about 0.6.
- **The original quintile long/short is a market bet.** The BTC-hedged version leaves about 0.3–0.4 BTC beta.
- **Finalist: Frazzini-Pedersen BAB** (EW beta, 48h, ex-post beta about 0.09).
  - Dev: SR 1.06, **alpha t 1.53**, deflated SR probability 0.56 at N = 1,012.
  - Walk-forward SR 0.27.
  - **2025 holdout: SR 1.84 (t 1.66)**, but about 45% of it came from funding and April lost −22%.
- **Verdict:** not adoptable. At most a paper-trade on data after 2026-10 with a pre-set kill rule.

## 4. Live-ops findings (`agent_docs/LIVE_OPS_CHECKLIST.md`)
- **Check first.** Since **2025-12-09**, Binance rejects STOP_MARKET/TAKE_PROFIT/TRAILING stops on `/fapi/v1/order` (error **−4120**). They must go to `POST /fapi/v1/algoOrder` with `algoType=CONDITIONAL`.
  - Bots silently lost their stops (freqtrade and others).
  - Verify that the bot's stops actually exist before any restart.
- **Squeeze and delisting risk.** The ALPACA delisting squeeze (Apr 2025: −80%, then ×33 from the low, about $42M of shorts liquidated).
  - Watch `exchangeInfo` status and `deliveryDate`.
  - Close shorts on any delisting notice.
- **Funding interval.** Since May 2025 a coin can switch to **1h funding** after hitting its cap. Check `/fapi/v1/fundingInfo` before shorting.
- **Margin.** Use USDT-only margin, one-way mode and multi-assets OFF (after the 10-Oct-2025 depeg event).
- **Order handling:**
  - idempotent client order IDs, no blind POST retries;
  - reconcile exchange state against intended state after every rebalance;
  - an independent risk gate, a kill switch and a pre-tested `flatten_all`;
  - don't use `countdownCancelAll` (it would cancel your stops);
  - staged rollout via testnet.

## 5. Optiver / Pragmatic Engineer lessons (`agent_docs/OPTIVER_LESSONS.md`)
- **Core idea:** a risk system that sits outside the strategy and blocks orders "regardless of what the algorithm wants".
- **For this bot that means:**
  - an independent risk gate;
  - a portfolio-level squeeze stress test;
  - a kill switch;
  - reconciliation;
  - deterministic replay or backtest–live parity tests;
  - owner-run testing;
  - staged rollout;
  - paging alerts;
  - post-mortems.
- Latency and FPGA work are irrelevant at an 8h cadence.
- Sources were mostly search snippets: the sandbox network blocked page fetches, and the article is paywalled.

## 6. Open items for the local agents
1. If you ever restart a book, implement §4 first. The stop endpoint is critical.
2. To pursue BAB, freeze the finalist spec in `cloud_handoff_1/PREREG.md` and paper-trade it on fresh data (after 2026-10). Separate price alpha from funding carry.
3. Untested ideas that need data the cloud lacked (and that is in your lake): open interest, liquidations, token unlocks and listings as short-side vetoes. Use `pf_lib` accounting with t ≥ 3.
4. Merge Wave R2 (`results/wave3c/realistic_score.*`, R09–R13) into `claude/xs-realistic-redesign`.

## Fetch
```bash
cd <your clone of miinren/jjajanggg> && git fetch origin claude/xs-hf-signals
git show origin/claude/xs-hf-signals:research/xs_crypto/agent_docs/HERDR_BRIEF.md
git checkout origin/claude/xs-hf-signals -- research/xs_crypto/agent_docs research/xs_crypto/cloud_handoff_1
```
