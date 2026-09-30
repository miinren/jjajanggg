# Diagnostic for N02s gate: forward 8h residual return (rows i+2..i+9, bp) by decile of flow72 inside M, raw and S0-neutral.
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/root/work")
from common import D, S0, h
T = len(D.idx); RS = np.nan_to_num(D.resid.to_numpy()); CS = np.cumsum(RS, 0); M = D.M.to_numpy(); S = S0.to_numpy()
z = np.load("/root/work/xs_hourly_2020_2025.npz", allow_pickle=True); Q = pd.DataFrame(z["quote_volume"]).astype(float); del z
qr = (Q / Q.rolling(168, min_periods=100).mean().shift(1)).replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy(); del Q
X = pd.DataFrame(RS * qr).rolling(72, min_periods=1).sum().to_numpy(); del qr
rows = np.flatnonzero((D.idx.hour % 8 == 7) & (np.arange(T) >= 800) & (np.arange(T) + 10 < T) & (D.idx >= "2020-03-15"))
acc = {k: [[] for _ in range(10)] for k in ("raw", "neutral", "S0top20_flowhi", "S0top20_flowlo")}
for i in rows:
    m = np.flatnonzero(M[i] & np.isfinite(S[i]) & np.isfinite(X[i]))
    if len(m) < 30: continue
    f = CS[i + 9, m] - CS[i + 1, m]; f = f - f.mean()
    x = pd.Series(X[i, m]).rank(pct=True).to_numpy(); y = pd.Series(S[i, m]).rank(pct=True).to_numpy()
    A = np.c_[np.ones(len(m)), y]; e = x - A @ np.linalg.lstsq(A, x, rcond=None)[0]; e = pd.Series(e).rank(pct=True).to_numpy()
    for k, v in (("raw", x), ("neutral", e)):
        d = np.minimum((v * 10).astype(int), 9)
        for q in range(10): acc[k][q].append(f[d == q].mean() if (d == q).any() else np.nan)
    top = np.argsort(-y)[:20]; med = np.median(x[top])      # within S0's short candidates: high vs low flow
    acc["S0top20_flowhi"][0].append(f[top][x[top] > med].mean()); acc["S0top20_flowlo"][0].append(f[top][x[top] <= med].mean())
for k in ("raw", "neutral"):
    print(k, " ".join(f"{np.nanmean(a)*1e4:+.1f}" for a in acc[k]))
hi, lo = np.array(acc["S0top20_flowhi"][0]), np.array(acc["S0top20_flowlo"][0]); d = hi - lo
print("within S0 top-20 shorts: high-flow %.1f bp, low-flow %.1f bp, diff %.1f bp/8h t %.2f" % (np.nanmean(hi)*1e4, np.nanmean(lo)*1e4, np.nanmean(d)*1e4, h.nw_t(d[np.isfinite(d)], 6)))
