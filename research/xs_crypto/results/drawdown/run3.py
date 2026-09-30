# round 2: T33-T41
import time, pickle, numpy as np, pandas as pd, sys, gc
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/drawdown")
from common import *
import ext, ext2, ev
t0 = time.time()
BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
B = ext.book(D, S0, **BK); LIVE = ext.book(D, S0)
assert np.allclose(B[0].net.values, ext2.book(D, S0, **BK)[0].net.values)
out = {}; rows = []
def rec(name, c):
    out[name] = c[0]; r = ev.row(D, name, c, B, LIVE); rows.append(r); print(r, flush=True)
    pickle.dump(out, open("run3.pkl", "wb")); ev.update_csv(rows)
def go(name, **kw): rec(name, ext2.book(D, S0, **{**BK, **kw}))
# tranches
bk = {0: B}
for off in [2, 4, 6]: bk[off] = ext2.book(D, S0, offset=off, **BK)
def avg(offs):
    df = sum(bk[o][0] for o in offs) / len(offs); cm = sum(bk[o][1] for o in offs) / np.float32(len(offs)); return df, cm
rec("tranche2", avg([0, 4])); rec("tranche4", avg([0, 2, 4, 6])); del bk; gc.collect()
RS = np.nan_to_num(D.resid.to_numpy())
def corrveto(rho):
    def f(i, lst):
        c = lst[:80]
        if len(c) < 2: return lst
        X = RS[max(0, i - 335):i + 1][:, c]; C = np.corrcoef(X.T); C = np.nan_to_num(C)
        acc = []
        for j in range(len(c)):
            if all(C[j, a] <= rho for a in acc): acc.append(j)
            if len(acc) >= 40: break
        return [c[j] for j in acc]
    return f
for rho in [0.5, 0.7]: go(f"short_corrveto_{rho}", short_pick=corrveto(rho))
go("NS25", NS=25); go("NS30", NS=30)
iv = D.idio(336).to_numpy()
def vstop(i, shorts):
    a = iv[i, shorts]; a = np.nan_to_num(a, nan=np.nanmedian(a)); return np.clip(0.2 * a / np.median(a), 0.1, 0.4)
go("volstop", stop_fn=vstop)
def minvar(i, longs, shorts):
    X = RS[max(0, i - 335):i + 1][:, shorts]; C = np.cov(X.T); C = 0.5 * C + 0.5 * np.diag(np.diag(C)); e = 1 / len(shorts)
    try: x = np.linalg.solve(C + 1e-10 * np.eye(len(shorts)), np.ones(len(shorts)))
    except np.linalg.LinAlgError: x = np.ones(len(shorts))
    x = np.maximum(x, 0); x = x / x.sum() if x.sum() > 0 else np.full(len(shorts), e)
    for _ in range(5): x = np.minimum(x, 2 * e); x /= x.sum()
    return np.full(len(longs), 0.45 / len(longs)), 0.55 * x
go("minvar_adj", leg_weights=minvar, adj=0.5)
Bb = D.B
def invbeta(i, longs, shorts):
    a = 1 / np.maximum(Bb[i, shorts], 0.3); e = 1 / len(shorts); x = np.clip(a / a.sum(), 0.5 * e, 2 * e); x /= x.sum()
    return np.full(len(longs), 0.45 / len(longs)), 0.55 * x
go("short_invbeta", leg_weights=invbeta)
print("done", time.time() - t0)
