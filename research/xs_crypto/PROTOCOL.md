# Research protocol for parallel agents

The data (`xs_hourly_2020_2025.npz`) and `cloud_harness.py` are NOT in git. Download them with the presigned URLs given in your task
prompt into this folder. Never commit the URLs, the data or any credential.

## Base
- `common.py` builds the live score S0 (AR1-corrected idio vol 0.75 + funding 0.25) and `stats()`.
- `ext.py` has `book(...)`, which reproduces `cloud_harness.live_book` exactly by default. It adds per-leg attribution, `short_frac`,
  separate long/short N (`N`, `NS`), `gross` (hourly array), `hedge` ratio, `leg_weights`, and `tp_short`/`tp_long`.
- **Base to beat = B = `ext.book(D, S0, short_frac=0.55, stop=0.2, N=12, NS=20)`** (SR 2.69, 5.5 bp). Also report every result vs LIVE = `ext.book(D, S0)`.

## Adoption bar (all required)
1. `h.partition_test(D, cand, B)` returns adopt=True: risk-matched, ≥5/6 years, ≥4/5 coin groups, both BTC regimes, t_NW ≥ 1.5.
2. **t_NW ≥ 2.0 vs B.** The max of 200 placebo features was 1.79.
3. For any parameter family (>1 value tried): `h.walk_forward(family, B)` must show wf_SR > base_SR.
4. Economic rationale written *before* running, in `trials.csv`.

## Rules
- Pre-register: append each candidate to `results/<topic>/trials.csv` (name, rationale, params) BEFORE running it. Then fill in SR,
  t_vs_B, years, groups, regimes, adopt, mdd_at2pct, minYrSR. Every trial is logged, including failures.
- Budget: at most 60 trials per agent. Don't tune a winner's neighbours to squeeze SR. Do run a plateau check (±1 step per parameter)
  on anything that passes, and report its worst neighbour.
- No lookahead: every signal at hour i may use data ≤ i only (the book trades at i+2). Double-check `.shift` usage.
- Deliverable: `results/<topic>/REPORT.md` covering what was tried, the full trials table, any adopted candidate with its code, the
  plateau check, and SR at 8/12 bp. Commit and push it to your branch.
