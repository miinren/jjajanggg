# cloud_handoff_1 — Task A pre-registration: beta-neutral rebuild of beta_30d / anti-beta
Written 2026-09-30 BEFORE any result on the npz is computed. Data: xs_hourly_2020_2025.npz (Binance USDT-M perps).
DEV = 2020-03-15 .. 2024-12-31. HOLDOUT = 2025-01-01 .. 2025-12-31, ONE look, finalist(s) only (max 2), via pf_lib.holdout_once.
Accounting: pf_lib (simple returns, share-hold drift, funding cash, 5bp taker + ADV-bucket half-spread + sqrt impact at $15k
gross, 1h delay). Universe: pf_crypto.load() (liquid tercile M; BTC/ETH/PAXG/XAUT never ranked; BTC = hedge instrument).

## Question
Is the negative cross-sectional beta->return relation (IC agent: beta_30d rank IC -0.02..-0.03, 2024-26) a genuine
betting-against-beta premium (flat security market line) that survives beta-neutral construction, or merely a short-market bet?

## Signals (2)
- B_EW  : 720h OLS beta of hourly simple returns on the equal-weight return of the universe U (known at t; min 168 obs), as ic_crypto_baselines.beta_30d
- B_BTC : same, on BTC simple returns
Signal for the book = -beta (long low beta).

## Diagnostics (not trials; reported for both signals)
D1 IC decay: Pearson + Spearman IC of -beta vs SIMPLE forward returns net of long funding, 1h,4h,12h,1d,2d,3d,5d,7d,14d,
   1h delay, NW t, half-life fit b(h)=A tau (1-exp(-h/tau)); plus IC vs forward BETA-ADJUSTED returns (r_i - beta_i * r_mkt over the same window).
D2 Fama-MacBeth SML test at 1d: lambda_t = cross-sectional slope of fwd 1d return on beta; regress lambda_t = gamma + delta * mkt_t.
   CAPM: gamma=0, delta~1. BAB premium <=> gamma < 0 (NW t). Report per year.

## Book trials (counted; family = 2 signals x 3 constructions x 2 rebalance = 12 book trials max, + 1 finalist robustness set)
Constructions (quintile legs, q=0.2, inverse-vol weights with lagged EWMA vol (halflife 168h) inside legs):
- C_RAW : dollar-neutral long low-beta / short high-beta, no hedge  (reference; expected beta ~ -0.6)
- C_HEDGE: C_RAW + BTC hedge sized by ex-ante 168h BTC beta of the book (pf_lib hedge='BTCUSDT')
- C_BAB : Frazzini-Pedersen: long leg scaled to ex-ante beta 1 (weights / beta_L), short leg scaled to beta 1 (weights/beta_H),
          ex-ante beta 0, net dollars absorbed (leverage cap 3x per leg); gross re-normalised to 1.
Rebalance: 24h and 48h (portfolio agent: <8h loses to costs; 24-48h preferred). Delay 1h. Stops: none (pre-registered; stops are a
separate family already explored).
Primary statistic: net daily Sharpe, NW t, stationary-bootstrap p; plus EX-POST alpha t from daily net ~ BTC_ret + EW_ret regression.

## Decision rule (pre-registered)
Finalist = best dev net SR among C_HEDGE/C_BAB trials whose ex-post |beta| < 0.2 to BOTH BTC and EW market.
Adopt as "edge" only if: dev ex-post alpha NW t >= 3 (handoff bar, ~1000 prior variants), deflated SR prob >= 0.95 at the global
trial count used below, positive in >= 4/5 dev years, AND 2025 one-look holdout net SR > 0 with alpha t > 0.
Walk-forward (yearly folds 2021..2024, 30d embargo) over the 12-trial family must beat 0 (reported).
Global trial count for deflation: 1000 (handoff) + trials here.
A clean negative is an acceptable outcome.
