# squeeze-protection + short construction trials T01-T19
import time, pickle, numpy as np, pandas as pd, sys
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/drawdown")
from common import *
import ext, ext2, ev
t0 = time.time()
BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
B = ext.book(D, S0, **BK); B2 = ext2.book(D, S0, **BK)
assert np.allclose(B[0].net.values, B2[0].net.values), "ext2 mismatch"
LIVE = ext.book(D, S0); print("validated ext2 == ext", stats(B[0]), time.time() - t0, flush=True)
out = {"B": B[0], "LIVE": LIVE[0]}; rows = []
def go(name, **kw):
    c = ext2.book(D, S0, **{**BK, **kw}); out[name] = c[0]; r = ev.row(D, name, c, B, LIVE); rows.append(r); print(r, flush=True)
    pickle.dump(out, open("run1.pkl", "wb")); ev.update_csv(rows)
# signals (all use data <= i)
z72 = (D.resid.rolling(72, min_periods=48).sum() / (D.idio(336) * np.sqrt(72))).to_numpy()
for k, n in [(1.5, "sq_r72z_1.5"), (2.0, "sq_r72z_2.0"), (2.5, "sq_r72z_2.5")]:
    go(n, short_ok=~(z72 > k))
del z72
z = np.load(h.NPZ, allow_pickle=True); Q = pd.DataFrame(z["quote_volume"], index=D.idx, columns=D.cols).astype(float); del z
vs = (Q.rolling(24).sum() / (Q.rolling(720, min_periods=400).sum() / 30)).to_numpy(); del Q
for k in [3, 5]: go(f"sq_vsurge_{k}", short_ok=~(vs > k))
del vs
lq = D.lq.to_numpy()
for q, n in [(0.8, "sq_liq_0.80"), (0.9, "sq_liq_0.90")]: go(n, short_ok=lq > q)
del lq
go("sq_guard_-2bp", guard=-2e-4); go("sq_guard_0", guard=0.0)
for b in [24, 72, 168]: go(f"ban_{b}h", ban_h=b)
for s in [0.15, 0.20, 0.25]: go(f"rstop_{s:.2f}", resid_stop=True, stop=s)
go("ladder_10_20", half_at=0.10)
iv = D.idio(336).to_numpy()
def invvol(i, longs, shorts):
    a = 1 / np.maximum(iv[i, shorts], 1e-5); a = np.nan_to_num(a, nan=np.nanmean(a)); e = 1 / len(shorts)
    x = np.clip(a / a.sum(), 0.5 * e, 2 * e); x /= x.sum()
    return np.full(len(longs), 0.45 / len(longs)), 0.55 * x
go("short_invvol", leg_weights=invvol)
RS = np.nan_to_num(D.resid.to_numpy())
def corrmat(i, shorts):
    X = RS[max(0, i - 335):i + 1][:, shorts]; C = np.cov(X.T); return C
def clusterw(i, longs, shorts):
    C = corrmat(i, shorts); sd = np.sqrt(np.maximum(np.diag(C), 1e-12)); Rh = C / np.outer(sd, sd); np.fill_diagonal(Rh, 0)
    x = 1 / (1 + np.maximum(Rh, 0).sum(1)); x /= x.sum()
    return np.full(len(longs), 0.45 / len(longs)), 0.55 * x
go("short_clusterw", leg_weights=clusterw)
def minvar(i, longs, shorts):
    C = corrmat(i, shorts); C = 0.5 * C + 0.5 * np.diag(np.diag(C)); e = 1 / len(shorts)
    try: x = np.linalg.solve(C + 1e-10 * np.eye(len(shorts)), np.ones(len(shorts)))
    except np.linalg.LinAlgError: x = np.ones(len(shorts))
    x = np.maximum(x, 0); x = x / x.sum() if x.sum() > 0 else np.full(len(shorts), e)
    for _ in range(5): x = np.minimum(x, 2 * e); x /= x.sum()
    return np.full(len(longs), 0.45 / len(longs)), 0.55 * x
go("short_minvar", leg_weights=minvar)
print("done", time.time() - t0)
