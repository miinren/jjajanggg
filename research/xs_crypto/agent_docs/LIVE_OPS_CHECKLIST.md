# LIVE_OPS_CHECKLIST: production safeguards for the Binance USDT-M long/short bot

> **Audience:** AI agents implementing or auditing the live bot (`bt/portfolio/idio_micro_live.py`, a repo that is not attached here).
> **Date:** 2026-09-30.
>
> **Source tags:**
> - **[OPENED]**: read directly. This covers the official Binance Python SDK on GitHub (whose docstrings mirror the docs as of 2026-09-23), ccxt `binance.py` master, and a migration guide.
> - **[SNIPPET]**: search summaries only. The sandbox blocked sec.gov, binance.com, developers.binance.com and pragmaticengineer.com.
> - **[INF]**: our inference.
>
> Re-check every [SNIPPET] item on the primary page before relying on it.

**Bot context:**
- About 32 coins (12 long / 20 short under B-MV; 20/20 in LIVE), plus a BTC hedge.
- Short stop at +20% (B-MV) or +40% (LIVE).
- Rebalances at 07/15/23 UTC. Funding settles at 00/08/16 UTC for 8h symbols.
- About $330 capital.
- **The biggest measured risk is stop slippage in short squeezes:** B-MV's edge over LIVE halves at about 2% average stop slippage and is gone at about 3.5%.

## ⚠ Check first: stop orders may be failing silently
**Since 2025-12-09, Binance USDT-M rejects conditional orders on `POST /fapi/v1/order` with error `-4120`** ("Order type not supported for this endpoint. Please use the Algo Order API endpoints instead"). This covers `STOP_MARKET`, `TAKE_PROFIT_MARKET`, `STOP`, `TAKE_PROFIT` and `TRAILING_STOP_MARKET`. They must now go to `POST /fapi/v1/algoOrder` with `algoType=CONDITIONAL`. [OPENED: SDK, ccxt error map, migration guide]
- freqtrade, nautilus_trader and Binance.Net all needed fixes. Current ccxt master routes conditional orders to `fapiPrivatePostAlgoOrder`; older pinned versions may not. [OPENED]
- Rejections now arrive as `ALGO_UPDATE` user-stream events. `CONDITIONAL_ORDER_TRIGGER_REJECT` was deprecated on 2025-12-15. [SNIPPET]
- **Action:** confirm that the live bot's stops exist on the exchange right now, via the open algo orders for every short. Then confirm the placement path and pinned library version.

## Prioritised checklist
| # | Safeguard | Risk addressed | Implementation | Motivated by |
|---|---|---|---|---|
| 1 | **Stops via algo endpoint, verified** | Stops silently not placed | `POST /fapi/v1/algoOrder`, `algoType=CONDITIONAL`, `type=STOP_MARKET`, `side=BUY`, `closePosition=true` for shorts. Treat `-4120` or any non-2xx response as fatal and page. On startup or in CI, place and cancel one stop on testnet. Pin library versions and upgrade deliberately | Dec-2025 migration [OPENED] |
| 2 | **Reconcile, don't remember** | Naked shorts, orphan stops, state drift | After every rebalance and every 5–15 min: `GET /fapi/v3/positionRisk` plus open algo orders. Assert each short has exactly one closePosition stop at the right trigger, and that no stop exists without a position. Auto-repair; if that fails, flatten the symbol and alert. Drive actions from exchange state, never local memory | Knight Capital [SNIPPET SEC order]; Optiver reconciliation [SNIPPET] |
| 3 | **Squeeze-aware stop trigger** | Stop slippage, the #1 measured risk | Semantics [OPENED]: a BUY `STOP_MARKET` fires when the chosen price ≥ `triggerPrice`; `workingType` is `MARK_PRICE` or `CONTRACT_PRICE` (last); with `priceProtect=true` it triggers only when the mark–last gap is within the symbol's `triggerProtect`. [INF] In squeezes, last price leads mark, and `priceProtect` can *block* the trigger when divergence is largest. So consider `CONTRACT_PRICE` with `priceProtect=false`, but test it first. Log trigger time, fill, and the mark–last gap for every stop | SDK docs [OPENED]; ALPACA 2025, May-2021 outage [SNIPPET] |
| 4 | **Delisting / squeeze watchdog** | Delisting-announcement squeezes, forced settlement | At least hourly, diff `exchangeInfo` for each held symbol: `status != TRADING`, a changed `deliveryDate`, or the symbol gone. Also poll Binance delisting announcements. On a hit, close the short at once and exclude the coin; don't wait for the next rebalance | ALPACA Apr-2025: after the delisting notice it went −80%, then ×33 from the low, with about $42M of shorts liquidated [SNIPPET]; RVV/YALA auto-settlement [SNIPPET] |
| 5 | **Funding-interval guard** | Crowded shorts paying capped funding **hourly** | Before each rebalance, call `GET /fapi/v1/fundingInfo` and `premiumIndex`. Flag shorts with `fundingIntervalHours < 8` or at the funding cap; down-weight or skip them. Record `FUNDING_FEE` and `SPECIAL_FUNDING_FEE` (a new income type from 2026-09-10) per symbol | Since 2 May 2025, a contract switches to 1h settlement after hitting its cap; since 2 Jan 2026 it reverts to 4h after 16 calm settlements [SNIPPET]; `fundingInfo` [OPENED] |
| 6 | **Idempotent orders, no blind POST retries** | Duplicate fills after timeout or 5xx | Deterministic `newClientOrderId`/`clientAlgoId` (e.g. `rb{YYYYMMDDHH}-{SYM}-{leg}`, regex `^[.A-Z:/a-z0-9_-]{1,36}$`). On a timeout, query by ID before retrying. Use `newOrderRespType=RESULT` | The official SDK retries only GET/DELETE [OPENED]; Knight |
| 7 | **Independent risk gate** | Runaway orders from a bug | Hard limits outside the strategy: symbol notional ≤ 1.5× target, gross ≤ N× equity, net within ±10% of gross, orders per run ≤ 3× the coin count, price within X% of mark, symbol whitelist. A failure rejects the whole rebalance and alerts. A `HALT` kill flag is checked before every order. A pre-tested `flatten_all` script closes reduce-only in chunks | Optiver "risk system … regardless of what the algorithm wants" [SNIPPET]; Knight violated Rule 15c3-5 [SNIPPET] |
| 8 | **Startup invariants** | Collateral depeg, hedge-mode errors | Assert multi-assets mode is OFF (`GET /fapi/v1/multiAssetsMargin`), dual-side is false (one-way mode), margin is USDT only, and margin type and leverage per symbol are as expected. Refuse to trade on a mismatch | 10-Oct-2025 depegs (USDe to about $0.66 on Binance, about $283M compensation) [SNIPPET]; `-4061`/`-4067`/`-4068` [OPENED] |
| 9 | **Filter pre-checks** | At about $330 over 33 legs, many legs sit near the minimum notional | Read MIN_NOTIONAL, LOT_SIZE and PERCENT_PRICE from `exchangeInfo`. Round quantities; merge or drop sub-minimum legs; exit dust with reduce-only. Handle `-4164` (notional below minimum) and `-4131` (PERCENT_PRICE) explicitly | ccxt error map [OPENED] |
| 10 | **Alerts that page** | Warnings nobody reads | Push alerts (Telegram or ntfy) on any reject, reconciliation diff, stop fired, missed-rebalance heartbeat, `ALGO_UPDATE` reject, or 418/429. External dead-man ping after each successful run (e.g. healthchecks.io) | Knight's 97 unread "BNET rejects" emails [SNIPPET]; Pragmatic Engineer oncall and postmortem pieces [SNIPPET] |
| 11 | **Staged rollout, config as code** | Bad deploy or config | Universe, stop % and weights live in git with a reviewed diff and schema-validated bounds. Roll out on testnet (`https://testnet.binancefuture.com`) first, then live with 1–2 symbols at minimum size, then 25% size, then full. Log the version hash at start. Never deploy near 07/15/23 UTC. Ship the B-MV book change first and the hedge band second | CrowdStrike lessons [SNIPPET]; Knight's manual 7-of-8 deploy [SNIPPET] |
| 12 | **Rate limits and clock** | IP bans; `-1021` blocking exits | Read `x-mbx-used-weight-1m` / `X-MBX-ORDER-COUNT-*` and back off at about 70%. Sync with NTP and use a modest `recvWindow`. Batch at most 5 orders (a batch costs 5 on the 10s counter, 1 on the 1-min counter, 5 IP weight; batches run concurrently). Keep the listenKey alive every 30–50 min (it expires after 60) | SDK docs [OPENED]; IP limit 2400 weight/min and order limit 300 per 10s [SNIPPET] |
| 13 | **Do NOT use `countdownCancelAll`** as a dead-man switch | It would cancel the stops that protect you when the bot dies | Rely on exchange-resident closePosition stops. A watchdog should *flatten* on staleness, not cancel. Whether it also cancels algo orders is unverified | Endpoint semantics [OPENED]; May-2021 outage |
| 14 | **Outage plan** | Unable to exit in a crash | Keep leverage low enough that stops, not liquidation (which uses mark price), are the binding exit. Skip or retry a rebalance rather than half-execute it. Keep timestamped logs for compensation claims | 19-May-2021 futures outage of about 1h; Binance compensates only "actual losses due to our system's issues" [SNIPPET] |
| 15 | **Post-mortem every stop-out** | Unexamined slippage losses repeat | Short template: trigger vs fill slippage, cause, fix. Feed measured slippage back into the backtest; the edge is gone at about 3.5% | Pragmatic Engineer postmortem best practices [SNIPPET] |

## Error codes worth handling explicitly
Source: ccxt map [OPENED].

| Code | Meaning |
|---|---|
| `-4120` | Conditional order sent to the wrong endpoint (use algoOrder) |
| `-1021` | Timestamp outside recvWindow |
| `-1003` | Too much request weight |
| `-1008` | Server overloaded |
| `-2019` | Margin insufficient |
| `-2022` | ReduceOnly rejected |
| `-4061` | Position side mismatch |
| `-4131` | PERCENT_PRICE filter |
| `-4164` | Notional below minimum (not applied to reduce-only) |
| `-4067` / `-4068` | Position mode change blocked by open orders or positions |

HTTP 418 means an IP ban.

## Sources
- **Binance Python SDK (USDⓈ-M module):** https://github.com/binance/binance-connector-python [OPENED]
- **ccxt `binance.py`:** https://raw.githubusercontent.com/ccxt/ccxt/master/python/ccxt/binance.py [OPENED]
- **Algo-endpoint migration guide:** https://github.com/MankhongGarden/binance-futures-algo-endpoint-migration [OPENED]
- **Binance docs** [SNIPPET]:
  - Change log: https://developers.binance.com/docs/derivatives/change-log
  - New Algo Order: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/New-Algo-Order
  - General info: https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info
- **Funding FAQ** [SNIPPET]: https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031
- **Knight Capital, SEC order 34-70694** [SNIPPET]: https://www.sec.gov/files/litigation/admin/2013/34-70694.pdf
- **ALPACA delisting squeeze** [SNIPPET]: https://www.theblock.co/post/355730/alpaca-finance-binance-delisting
- **Binance 10-Oct-2025 compensation** [SNIPPET]: https://www.theblock.co/post/374295/binance-pays-283-million-in-compensation-following-fridays-depegs-covering-user-losses
- **Binance May-2021 outage** [SNIPPET]: https://www.cnbc.com/amp/2021/08/19/cryptocurrency-traders-seek-damages-from-binance-after-major-outage.html
- **Pragmatic Engineer pieces** [SNIPPET]:
  - https://newsletter.pragmaticengineer.com/p/optiver
  - https://newsletter.pragmaticengineer.com/p/incident-review-best-practices
  - https://newsletter.pragmaticengineer.com/p/shipping-to-production
  - https://newsletter.pragmaticengineer.com/p/the-biggest-ever-global-outage-lessons
