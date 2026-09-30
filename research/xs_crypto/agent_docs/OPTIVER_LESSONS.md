# OPTIVER_LESSONS: what The Pragmatic Engineer's Optiver profile teaches a small crypto bot

> **Audience:** AI agents working on the live bot or its tooling.
> **Research date:** 2026-09-30.
>
> **Source caveat.** The sandbox's network policy blocked every page fetch: Substack, optiver.com, X, archives and Reddit/HN. Only web-search snippets were available, and the article's testing, monitoring and risk sections are paywalled anyway. Tags:
> - **[S]** = seen in search snippets or summaries; wording not verified.
> - **[UNVERIFIED]** = one summary only.
> - **[INF]** = our inference.
>
> Re-verify quotes before citing them externally.

## Sources
| # | Source | URL | Access |
|---|---|---|---|
| 1 | "Software engineering at a proprietary trading company: Optiver", The Pragmatic Engineer (Gergely Orosz), Aug 2026 | https://newsletter.pragmaticengineer.com/p/optiver | Partly paywalled; snippets only |
| 2 | "The Pragmatic Engineer profiles Optiver", Optiver news, 21 Aug 2026 | https://www.optiver.com/insights/news/the-pragmatic-engineer-profiles-optiver/ | Snippets |
| 3 | Optiver tech blog: platform engineering (Pat Cooney) | https://www.optiver.com/insights/technology-blog/platform-engineering-end-to-end/ | Snippets |
| 4 | Optiver tech blog: "Engineering the Agentic SDLC" | https://www.optiver.com/insights/technology-blog/engineering-the-agentic-sdlc/ | Snippets |
| 5 | David Gross, CppCon 2024 keynote "When Nanoseconds Matter" | https://cppcon.org/2024-keynote-david-gross/ | Snippets |
| 6 | Optiver "Risk and Control" page | https://optiver.com/what-we-do/control-risk/ | Snippets |

The article's interviewees were Alex Itkin (CTO, Optiver US), Pat Cooney (Head of Global Platform Engineering) and David Gross (Technology Lead, Options). [S]

## What the article says (readable parts)
- **Stakes.** The firm has no external customers, but "a single, unfortunate enough software bug could wipe out the whole company." Knight Capital, which lost $440M from one bug, is the cautionary tale. [S]
- **Four eras of trading:** pre-electronic, then electronification, then automated (late 1990s to about 2015), then quantitative/ML (about 2015 to now). "Latency is the floor and AI models are becoming a differentiator"; slow models use fast triggers. [S]
- **Structure.** Engineering "builds and owns the full trading-platform stack", working closely with Research and Trading. Roles overlap. The culture is "build and own": treat your project as if you were its CEO, with "no notion of throwing work over the wall to a QA team." [S] The claim that 30–40% of about 950 engineers work on the platform is [UNVERIFIED].
- **Stack.** C++ for low latency; Python for modelling, prototyping and tooling. Standard CI/CD, Kubernetes, Kafka and Postgres, plus bespoke hardware, custom kernels, own data centres and colocation. CI is being rebuilt globally, from 2025, to standardise deploys across regions. [S]
- **Latency.** Decisions are made in microseconds or less, the fastest paths are sub-nanosecond, and latency "cannot be an afterthought" (Gross). [S]
- **Risk.** "All strategies are enveloped by a risk management system that can block trades and stop individual strategies … it has a broader view of the combined risk level of multiple strategies." It adds automated monitoring "that checks if apps are outputting orders within expected parameters, **regardless of what the algorithm wants**." Optiver's own risk page lists pre-trade limits, reconciliation, incident review and escalation. [S]
- **Testing and release.** Optiver goes from idea to release in hours or days while measuring live impact, relying on automated testing, simulations and peer review. Its simulation platforms produce deterministic results on terabytes a day. [S] It is unclear whether this is in the article or only on Optiver's blog.
- **AI.** Roles are shifting towards decomposing workflows and orchestrating agents, so that "everyone becomes a manager of agents". The agentic SDLC means tight specs, programmatic tooling, and pushing failures to where they are detected automatically, with human review focused on design. [S]

## What does NOT transfer
FPGAs, custom silicon and kernels, colocation, nanosecond C++, bare-metal CI capacity planning and platform-team ratios do not transfer. The bot rebalances every 8h in Python on $330. **Correctness and control beat speed completely.** Don't spend effort on latency.

## Transferable lessons, mapped to this bot
The core idea is **controls that do not depend on the strategy being correct**. Each lesson below is in priority order.

1. **An independent risk gate outside the strategy code** (Optiver: "regardless of what the algorithm wants").
   - The strategy only proposes target weights. A separate `risk_gate` module with its own config checks every order. The strategy cannot raise these hard limits:
     - maximum notional per symbol (for example 12% of equity);
     - maximum gross (for example 2× equity);
     - maximum net (for example ±10% of gross);
     - maximum orders per rebalance;
     - maximum order size relative to the symbol's recent volume;
     - price within X% of mark;
     - a symbol whitelist.
   - Any failure rejects the whole rebalance and raises an alert.
2. **A portfolio-level view, not just per-position** (the "combined risk level").
   - Before each rebalance, stress-test the book: the top-3 shorts +30% and the longs −10% must stay below a set fraction of equity. Also cap exposure to correlated narrative clusters.
   - This targets the book's main risk, short squeezes. Wave 4 found that about a third of +20% shorts rip another +20% within 3 days.
3. **Kill switch and per-symbol disable** ("block trades and stop individual strategies").
   - A `HALT` flag checked before every order.
   - A pre-tested `flatten_all` script: cancel all orders, then reduce-only closes in chunks.
   - Auto-halt on a drawdown breach, a reconciliation mismatch, or repeated API errors.
   - A deny-list so one symbol can be disabled without stopping the book.
4. **Reconciliation** (Optiver's risk page lists it).
   - After every rebalance, and every 15 min, compare exchange positions, orders and balances with the intended state.
   - Reconcile funding and fee payments against expectations.
   - Alert on any mismatch; halt above a threshold.
5. **Deterministic replay and backtest–live parity** ("deterministic results").
   - Log every live input snapshot and decision. CI replays them and asserts identical target weights.
   - A parity test runs the backtest engine (`ext5`, realistic accounting) and the live code on the same day.
   - Golden-file tests for signals, plus edge-case tests for the gate: NaN, missing symbol, delisting, zero volume.
6. **You are the QA team** ("no throwing over the wall").
   - Every change gets a PR with tests and a **dry-run order diff**: "orders this change would have sent at the last rebalance".
   - Treat config as code, schema-validated with bounds at startup, so a leverage of 20 instead of 2 fails to load.
7. **Staged rollout** ("measure real impact in live trading").
   - Go paper, then testnet, then 25% size through a config multiplier, then full size after N clean rebalances.
   - Deploy away from rebalance times (07/15/23 UTC), pin dependencies, and keep a one-command rollback.
   - For B-MV specifically: switch the book first, then the hedge band.
8. **Monitoring and incident detection** (the article has a section on it; paywalled).
   - A dead-man's-switch heartbeat that pages if a rebalance is missed.
   - Alerts on rejects, reconciliation diffs, drawdown, margin ratio and liquidation distance, funding spikes, and API or data staleness.
   - A daily P&L split into price, funding and fees.
   - **Stop-slippage log** (fill vs trigger): B-MV's edge halves at about 2% average slippage.
9. **Post-mortems** ("incident review"; Knight Capital).
   - After any surprise, write a short note: timeline, root cause, and the automated check that would have caught it. Add a regression test each time.
   - Verify that every deploy actually reached the running host, and delete dead code paths and flags. Knight's root cause was a reused flag and stale code on one server.
10. **AI agents with verification** (agentic SDLC).
    - Agents work from tight specs, and their changes pass the automatic checks: types, tests, and the dry-run order diff.
    - A human reviews design and every risk-gate change by hand.

See `LIVE_OPS_CHECKLIST.md` for the concrete, Binance-specific implementation checklist.
