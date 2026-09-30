# Rebalance-clock robustness: B vs LIVE

Setup: every=8 books evaluated at all 8 clock offsets (rebalance hour shifted by 0..7 h). SR at 5.5 bp.

| offset | LIVE | B | 8L/20S | short stop 0.2 | short 55% |
|---|---|---|---|---|---|
| 0 (live clock) | 2.22 | 2.69 | 2.46 | 2.46 | 2.37 |
| 1 | 2.23 | 2.62 | 2.53 | 2.40 | 2.40 |
| 2 | 2.22 | 2.54 | 2.50 | 2.35 | 2.38 |
| 3 | 2.23 | 2.59 | 2.60 | 2.39 | 2.40 |
| 4 | 2.20 | 2.53 | 2.42 | 2.35 | 2.35 |
| 5 | 1.99 | 2.35 | 2.21 | 2.15 | 2.14 |
| 6 | 1.93 | 2.23 | 2.24 | 1.98 | 2.11 |
| 7 | 2.12 | 2.51 | 2.47 | 2.22 | 2.28 |

8-clock-averaged books:
- LIVE: SR 2.19, mdd_at2pct −32.0, minYrSR 1.02.
- **B: SR 2.57, mdd_at2pct −30.3, minYrSR 1.29. Risk-matched partition test vs LIVE: t 2.93, 6/6 years, 4/5 coin groups, adopt=True.**
- 8L/20S: SR 2.48 (t 3.10 vs LIVE).
- Short stop 0.2 alone: SR 2.35 (t 1.62).
- Short 55% alone: SR 2.35 (t 2.59).

Conclusions:
- B beats LIVE at 8/8 clocks (+0.30 to +0.47 SR).
- The live clock (offset 0) is B's luckiest, so quote B's backtest SR as about 2.55, not 2.69.
- The live clock is average for LIVE itself (2.22 vs a 2.19 mean).
