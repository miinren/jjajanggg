# T42-T46 + timing-offset diagnostic (not trials)
import time, pickle, numpy as np, pandas as pd, sys, gc
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/drawdown")
from common import *
import ext, ext2, ev
t0 = time.time()
BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
B = ext.book(D, S0, **BK); LIVE = ext.book(D, S0)
out = {}; rows = []
def go(name, **kw):
    c = ext2.book(D, S0, **{**BK, **kw}); out[name] = c[0]; r = ev.row(D, name, c, B, LIVE); rows.append(r); print(r, flush=True)
    pickle.dump(out, open("run4.pkl", "wb")); ev.update_csv(rows)
iv = D.idio(336).to_numpy()
def invvol(p, clip=True):
    def f(i, longs, shorts):
        a = np.maximum(iv[i, shorts], 1e-5) ** -p; a = np.nan_to_num(a, nan=np.nanmean(a)); e = 1 / len(shorts); x = a / a.sum()
        if clip: x = np.clip(x, 0.5 * e, 2 * e); x /= x.sum()
        return np.full(len(longs), 0.45 / len(longs)), 0.55 * x
    return f
go("short_invvol_p0.5", leg_weights=invvol(0.5)); go("short_invvol_p2", leg_weights=invvol(2)); go("short_invvol_noclip", leg_weights=invvol(1, False))
RS = np.nan_to_num(D.resid.to_numpy())
def minvar(sh):
    def f(i, longs, shorts):
        X = RS[max(0, i - 335):i + 1][:, shorts]; C = np.cov(X.T); C = (1 - sh) * C + sh * np.diag(np.diag(C)); e = 1 / len(shorts)
        try: x = np.linalg.solve(C + 1e-10 * np.eye(len(shorts)), np.ones(len(shorts)))
        except np.linalg.LinAlgError: x = np.ones(len(shorts))
        x = np.maximum(x, 0); x = x / x.sum() if x.sum() > 0 else np.full(len(shorts), e)
        for _ in range(5): x = np.minimum(x, 2 * e); x /= x.sum()
        return np.full(len(longs), 0.45 / len(longs)), 0.55 * x
    return f
go("short_minvar_s0.25", leg_weights=minvar(0.25)); go("short_minvar_s0.75", leg_weights=minvar(0.75))
diag = {}
for off in range(8):
    d = B[0] if off == 0 else ext2.book(D, S0, offset=off, **BK)[0]; diag[off] = d; print("offset", off, {k: round(float(v), 2) for k, v in stats(d).items()}, flush=True)
pickle.dump(diag, open("offsets.pkl", "wb"))
print("done", time.time() - t0)
