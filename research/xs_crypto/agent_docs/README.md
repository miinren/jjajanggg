# agent_docs: start here

Machine-oriented briefing files for AI agents working on the XS crypto book. Each file stands alone. The files were written on 2026-09-30 from the repo branches, three research sub-agents and the owner's session.

| File | Read when | One-line summary |
|---|---|---|
| [PROJECT_STATE.md](PROJECT_STATE.md) | Any research or backtest task | Branch map, the B-MV spec and exact code call, authoritative realistic numbers (B-MV SR 1.41 vs LIVE 0.72), methodology rules, dead ends, traps, open items |
| [LIVE_OPS_CHECKLIST.md](LIVE_OPS_CHECKLIST.md) | Any task touching the live bot, orders, stops or deployment | 15 prioritised safeguards for the Binance USDT-M bot. **First: verify that stops use the algo-order endpoint (`-4120` since 2025-12-09)** |
| [HERDR_BRIEF.md](HERDR_BRIEF.md) | First, for any local agent | Single-file digest of everything learnt (accounting, failures, BAB result, live-ops, Optiver) |
| [OPTIVER_LESSONS.md](OPTIVER_LESSONS.md) | Designing controls, testing or monitoring | What The Pragmatic Engineer's Optiver profile says, and 10 lessons mapped to this bot (independent risk gate, reconciliation, replay parity, staged rollout) |

## Hard rules (repeated in each file)
- **Research only.** Agents here have no exchange credentials and must never place orders.
- **Accounting.** Use `simple=True, drift=True` (+ `hedge_band=0.03, hedge_fund=True`). Log-return accounting inflates Sharpe about 2×.
- **Clocks.** Average over 8 clocks, pre-register trials, adopt only at partition-pass + t ≥ 2. Never tune on the 2026 holdout.
- **Secrets.** Never commit the data, `cloud_harness.py`, pre-signed URLs or AWS keys.

## Unfinished / caveats
- **Sources.** Web research ran under a network policy that blocked most primary pages, so many citations are search-snippet level and are tagged `[SNIPPET]` in the files. Re-verify before acting on them.
- **Missing guide.** The owner's `~/projects/xs-crypto/HANDOFF_CLOUD.md` lives on their machine and was not readable from the cloud session. These files were built from the repo's `HANDOFF.md` (branch `claude/xs-realistic-redesign`) instead.
