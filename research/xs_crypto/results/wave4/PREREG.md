# Wave 4 pre-registration (written before any wave-4 book was run)

**Accounting (all books):** `ext5.book` with simple returns, positions drifting between trades, the W06 hedge band 0.03 (forced re-hedge at rebalances/stops) and BTC funding paid/received on the hedge. 8-clock average. Selection at 5.5 bp; 8/12 bp reported.
`ext5` = `wave3c/ext4` + per-leg funding + hedge funding + an optional separate short score. Verified (`verify.py`, `verify3.py`): identical to ext4 with the new options off (max diff 0.0), reproduces Wave R SR 1.490, and a synthetic 50/50 buy-and-hold matches the engine NAV to 3e-9.

**References (not trials):** LIVE (live rules + band) and B-MV (T06).

**Stage 1, structure.** Pool T01–T10 (B-MV included). For Y ∈ {2023, 2024, 2025}, using only [2020-03-15, Y):
- *Primary (gated):* the best-SR structure replaces B-MV only if it also passes the risk-matched partition test vs B-MV on the selection window (≤1 losing year, ≥4/5 coin groups, both BTC regimes, NW t ≥ 1.5). Otherwise B-MV is kept.
- *Secondary (ungated):* best selection-window SR.

**Stage 2, score.** Runs on the structure the primary rule picks most often (ties go to the < 2025 pick). Grid fw ∈ {0, 0.25, 0.5} × L ∈ {168, 336, 720}, where (0.25, 336) is the default. Per Y, same gated rule vs the default score.

**Out of sample.** Each Y's final pick is scored on year Y only, and the three years are chained (2023–25). This is compared with B-MV and LIVE on the same days: SR, bp/day, and the paired NW t of the risk-matched difference (candidate scaled by the selection-window vol ratio).

**Diagnostics (not trials):**
- **Long-leg economics:** daily long-leg P&L regressed on BTC, ETH and an equal-weight liquid-alt index; funding split by leg.
- **Pumped shorts:** under live rules with the short stop disabled, log each short's first crossing of +20/30/50/75/100% against entry. Then measure forward simple returns and the probability of a further +20%.

**Hard cap: 22 book trials.** No placebo, clock-luck or plateau studies beyond the ≤4 one-step neighbours of the final pick.
