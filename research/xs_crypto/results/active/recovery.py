"""-20% adverse-move recovery statistics. For each book, every position episode that first reaches a 20% adverse move
(short: price +20% since entry; long: price -20%) is recorded at the hour it happens; we then look at the coin's actual
subsequent path (whether or not the book still holds it) up to the next 8h rebalance, 24h and 72h."""
import os, sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/active")
from common import *
import ext_active as ea
BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
books = {"B (short stop 20%, long stop 40%)": dict(BK),
         "B with short stop 40% (= live stop)": dict(BK, stop=0.4),
         "B with NO stops": dict(BK, stop=10.0, long_stop=None),
         "A18 redeploy_next (best t)": dict(BK, redeploy="next")}
Rn = D.Rn; RSn = D.Rn - D.B * D.rbn[:, None]; T = len(D.idx)
reb = np.flatnonzero((D.idx.hour + 1) % 8 == 0); nxt = np.searchsorted(reb, np.arange(T), side="right")
nxt = np.where(nxt < len(reb), reb[np.minimum(nxt, len(reb) - 1)], T)
C = np.vstack([np.zeros((1, Rn.shape[1])), np.cumsum(Rn, 0)]); CR = np.vstack([np.zeros((1, Rn.shape[1])), np.cumsum(RSn, 0)])
st_i = np.searchsorted(D.idx, pd.Timestamp(ST)); en_i = np.searchsorted(D.idx, pd.Timestamp("2026-01-01"))
def fwd(Cm, i, s, j): j = min(j, T); return Cm[j, s] - Cm[i + 1, s]          # sum Rn[i+1 : j]
out = {}; rows = []
for name, kw in books.items():
    rec, rp = [], []
    c = ea.book(D, S0, rec=rec, rec_pos=rp, **kw); df = c[0]; del c
    rec = [r for r in rec if st_i <= r[0] < en_i]; rp = [r for r in rp if st_i <= r[0] < en_i]
    nep = {-1: sum(len(r[1]) for r in rp), 1: sum(len(r[2]) for r in rp)}
    ndays = (en_i - st_i) / 24
    for side, lab in ((-1, "short"), (1, "long")):
        H = [r for r in rec if r[2] == side]
        if not H: continue
        res = dict(book=name, leg=lab, episodes=nep[side], hits=len(H), hit_pct_of_episodes=100 * len(H) / max(nep[side], 1),
                   hits_per_week=len(H) / ndays * 7, med_hours_to_hit=float(np.median([r[3] for r in H])))
        for hz, lab2 in (("reb", "next_reb"), (24, "24h"), (72, "72h")):
            v, rv, ev10, ev0, w30 = [], [], [], [], []
            for (i, s, sd, hh, l0) in H:
                j = nxt[i] if hz == "reb" else i + 1 + hz
                f = fwd(C, i, s, j); fr = fwd(CR, i, s, j)
                path = C[i + 1:min(j, T) + 1, s] - C[i + 1, s] + l0      # cumulative log price since entry along the window
                pos = (1 - np.exp(path)) if sd < 0 else (np.exp(path) - 1)   # position return since entry
                v.append((1 - np.exp(f)) * np.exp(l0) if sd < 0 else (np.exp(f) - 1) * np.exp(l0))   # fwd P&L, % of entry notional
                rv.append(-fr if sd < 0 else fr)
                ev10.append(pos.max() >= -0.10); ev0.append(pos.max() >= 0); w30.append(pos.min() <= -0.30)
                if lab2 == "72h": pass
            v, rv = np.array(v), np.array(rv)
            endpos = None
            res.update({f"{lab2}_fwd_mean_%": 100 * v.mean(), f"{lab2}_fwd_median_%": 100 * np.median(v), f"{lab2}_fwd_resid_mean_%": 100 * rv.mean(),
                        f"{lab2}_pct_better_than_hit": 100 * (v > 0).mean(),
                        f"{lab2}_touch_-10%_%": 100 * np.mean(ev10), f"{lab2}_touch_breakeven_%": 100 * np.mean(ev0), f"{lab2}_touch_-30%_%": 100 * np.mean(w30),
                        f"{lab2}_mean_hours": np.mean([min(nxt[i] if hz == 'reb' else i + 1 + hz, T) - i - 1 for (i, *_ ) in H])})
        # end-of-window position level at 72h / next reb
        for hz, lab2 in (("reb", "next_reb"), (72, "72h")):
            e10 = []
            for (i, s, sd, hh, l0) in H:
                j = nxt[i] if hz == "reb" else i + 1 + hz; lv = l0 + fwd(C, i, s, j)
                pos = (1 - np.exp(lv)) if sd < 0 else (np.exp(lv) - 1); e10.append(pos)
            e10 = np.array(e10)
            res[f"{lab2}_END_better_than_-10%_%"] = 100 * (e10 >= -0.10).mean(); res[f"{lab2}_END_breakeven_%"] = 100 * (e10 >= 0).mean()
            res[f"{lab2}_END_worse_than_-30%_%"] = 100 * (e10 <= -0.30).mean()
        # unconditional baseline: every position at every rebalance, forward 8h / 72h, same leg
        b8, b72 = [], []
        for (i, ns, nl, shorts, longs) in rp[::3]:
            for s in (shorts if side < 0 else longs):
                f8 = fwd(C, i - 1, s, i + 8); f72 = fwd(C, i - 1, s, i + 72)
                b8.append(-(np.exp(f8) - 1) if side < 0 else np.exp(f8) - 1); b72.append(-(np.exp(f72) - 1) if side < 0 else np.exp(f72) - 1)
        res["baseline_all_positions_8h_mean_%"] = 100 * np.mean(b8); res["baseline_all_positions_72h_mean_%"] = 100 * np.mean(b72)
        rows.append(res); print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in res.items()}, flush=True)
    out[name] = dict(rec=rec, stats=stats(df))
R = pd.DataFrame(rows); R.to_csv("recovery.csv", index=False)
pickle.dump(dict(rows=rows, out=out), open("recovery.pkl", "wb"))
print(R.set_index(["book", "leg"]).T.round(2).to_string())
