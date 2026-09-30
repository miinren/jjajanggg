# diagnostic: T17 (short_invvol) and T19 (short_minvar) vs B at all 8 rebalance clocks + 8-clock-averaged partition test
import time, pickle, numpy as np, pandas as pd, sys, gc
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/drawdown")
from common import *
import ext2
t0 = time.time()
BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
iv = D.idio(336).to_numpy(); RS = np.nan_to_num(D.resid.to_numpy())
def invvol(i, longs, shorts):
    a = 1 / np.maximum(iv[i, shorts], 1e-5); a = np.nan_to_num(a, nan=np.nanmean(a)); e = 1 / len(shorts)
    x = np.clip(a / a.sum(), 0.5 * e, 2 * e); x /= x.sum(); return np.full(len(longs), 0.45 / len(longs)), 0.55 * x
def minvar(i, longs, shorts):
    if len(shorts) < 2: return np.full(len(longs), 0.45 / len(longs)), np.full(len(shorts), 0.55 / max(1, len(shorts)))
    X = RS[max(0, i - 335):i + 1][:, shorts]; C = np.cov(X.T); C = 0.5 * C + 0.5 * np.diag(np.diag(C)); e = 1 / len(shorts)
    try: x = np.linalg.solve(C + 1e-10 * np.eye(len(shorts)), np.ones(len(shorts)))
    except np.linalg.LinAlgError: x = np.ones(len(shorts))
    x = np.maximum(x, 0); x = x / x.sum() if x.sum() > 0 else np.full(len(shorts), e)
    for _ in range(5): x = np.minimum(x, 2 * e); x /= x.sum()
    return np.full(len(longs), 0.45 / len(longs)), 0.55 * x
cfg = {"B": {}, "short_invvol": dict(leg_weights=invvol), "short_minvar": dict(leg_weights=minvar)}
acc = {k: [None, None] for k in cfg}; per = {k: {} for k in cfg}; rows = []
for off in range(8):
    cur = {}
    for k, kw in cfg.items():
        c = ext2.book(D, S0, offset=off, **BK, **kw); cur[k] = c; per[k][off] = c[0]
        acc[k][0] = c[0] / 8 if acc[k][0] is None else acc[k][0] + c[0] / 8
        acc[k][1] = c[1] / np.float32(8) if acc[k][1] is None else acc[k][1] + c[1] / np.float32(8)
    for k in ["short_invvol", "short_minvar"]:
        r = h.partition_test(D, cur[k], cur["B"], verbose=False); s = stats(cur[k][0]); sb = stats(cur["B"][0])
        rows.append(dict(offset=off, cand=k, SR=s["SR"], SR_B=sb["SR"], t=r["tNW"], yrs=r["years_won"], grp=r["coin_groups_won"], adopt=r["adopt"],
                         mdd2=s["mdd_at2pct"], mdd2_B=sb["mdd_at2pct"], minYr=s["minYrSR"], minYr_B=sb["minYrSR"]))
        print(rows[-1], flush=True)
    del cur; gc.collect()
print(pd.DataFrame(rows).round(2).to_string())
for k in ["short_invvol", "short_minvar"]:
    print("8-clock avg", k, stats(acc[k][0]), "B:", stats(acc["B"][0]))
    print(h.partition_test(D, tuple(acc[k]), tuple(acc["B"]), verbose=False))
pickle.dump(dict(rows=rows, per=per, avg={k: v[0] for k, v in acc.items()}), open("run5.pkl", "wb"))
print("done", time.time() - t0)
