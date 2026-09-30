# N01-N06 new-signal screen (pre-registered rule in trials.csv). Features at row i use data <= i; forward = resid rows i+2.. .
import sys, gc, numpy as np, pandas as pd
sys.path.insert(0, "/root/work")
from common import D, S0, h
T = len(D.idx); RS = np.nan_to_num(D.resid.to_numpy()).astype(np.float64); CS = np.cumsum(RS, 0)
M = D.M.to_numpy(); S = S0.to_numpy()
rows = np.flatnonzero((D.idx.hour % 8 == 7) & (np.arange(T) >= 800) & (np.arange(T) + 73 < T) & (D.idx >= "2020-03-15"))
def roll(a, n):   # rolling sum over n rows ending at i (float64)
    c = np.cumsum(np.nan_to_num(a), 0); out = c.copy(); out[n:] -= c[:-n]; return out
F = {}
z = np.load("/root/work/xs_hourly_2020_2025.npz", allow_pickle=True); Q = np.nan_to_num(z["quote_volume"].astype(np.float64)); del z
mq = pd.DataFrame(Q).rolling(168, min_periods=100).mean().shift(1).to_numpy()
qr = np.where(mq > 0, Q / np.where(mq > 0, mq, 1), 0.0); del mq
F["N02"] = roll(RS * qr, 72); del qr; gc.collect()
s1, s2 = roll(Q, 24), roll(Q * Q, 24); hhi = np.where(s1 > 0, s2 / np.where(s1 > 0, s1 ** 2, 1), np.nan); del s1, s2
F["N04"] = pd.DataFrame(hhi).rolling(168, min_periods=100).mean().to_numpy(); del hhi, Q; gc.collect()
R1 = D.R1.to_numpy(); tv = pd.DataFrame(R1).rolling(336, min_periods=200).var().to_numpy()
F["N03"] = D.idio(336).to_numpy() ** 2 / tv; del tv, R1; gc.collect()
r24 = roll(RS, 24); v24 = pd.DataFrame(r24).rolling(336, min_periods=200).var().to_numpy(); del r24
v1 = pd.DataFrame(RS).rolling(336, min_periods=200).var().to_numpy(); F["N05"] = v24 / (24 * v1); del v24, v1; gc.collect()
p0 = np.asarray(D.idx.hour % 8 == 0)[:, None].astype(float)
a = roll(RS * p0, 720) / 90.0; b = roll(RS * (1 - p0), 720) / 630.0; F["N06"] = a - b; del a, b; gc.collect()
# N01 peer momentum, computed only at screen rows
N01 = np.full((T, RS.shape[1]), np.nan)
for i in rows:
    m = np.flatnonzero(M[i] & np.isfinite(S[i]))
    if len(m) < 30: continue
    X = RS[i - 335:i + 1, m]; C = np.corrcoef(X.T); np.fill_diagonal(C, -9); C = np.nan_to_num(C, nan=-9)
    pk = np.argsort(-C, 1)[:, :10]; r72 = CS[i, m] - CS[i - 72, m]; N01[i, m] = r72[pk].mean(1)
F["N01"] = N01
def rk(x): return pd.Series(x).rank(pct=True).to_numpy()
out = []
for k, X in F.items():
    for hz in (8, 72):
        ic, icr, dts = [], [], []
        for i in rows:
            m = np.flatnonzero(M[i] & np.isfinite(S[i]) & np.isfinite(X[i]))
            if len(m) < 30: continue
            x, y = rk(X[i, m]), rk(S[i, m]); A = np.c_[np.ones(len(m)), y]; e = x - A @ np.linalg.lstsq(A, x, rcond=None)[0]
            f = rk(CS[i + 1 + hz, m] - CS[i + 1, m])
            ic.append(np.corrcoef(rk(e), f)[0, 1]); icr.append(np.corrcoef(x, f)[0, 1]); dts.append(D.idx[i])
        s = pd.Series(ic, index=dts); sr = pd.Series(icr, index=dts); L = 6 if hz == 8 else 30
        for lab, sel in (("IS", s.index < "2023-01-01"), ("OOS", s.index >= "2023-01-01")):
            out.append(dict(feat=k, hz=hz, per=lab, IC=s[sel].mean(), t=h.nw_t(s[sel].to_numpy(), L), IC_raw=sr[sel].mean(), n=int(sel.sum())))
    print(k, flush=True)
o = pd.DataFrame(out); o.to_csv("n_screen.csv", index=False)
w = o.pivot_table(index=["feat", "hz"], columns="per", values=["IC", "t", "IC_raw"]).round(4); print(w.to_string())
for k in F:
    a_, b_ = o[(o.feat == k) & (o.hz == 72) & (o.per == "IS")].iloc[0], o[(o.feat == k) & (o.hz == 72) & (o.per == "OOS")].iloc[0]
    print(k, "PROMOTE" if np.sign(a_.IC) == np.sign(b_.IC) and abs(b_.t) >= 2 else "drop", "sign", int(np.sign(a_.IC)))
