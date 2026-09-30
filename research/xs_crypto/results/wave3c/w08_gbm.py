# W08 holistic model (pre-registered in trials.csv). Step 1: features (pct inside M, rows <= i) -> long format over M cells.
# Step 2: walk-forward HistGradientBoosting (fixed params) per year 2021..2025, trained only on rows whose 72h target ends before Jan 1 of Y.
# Step 3: pre-screen = OOS rank IC inside the candidate sets. Step 4: re-ranked score W08_score.npy for the book (S0 values permuted inside sets).
import sys, gc, numpy as np, pandas as pd
sys.path.insert(0, "/root/work")
from common import D, S0, pI, pF, h
from sklearn.ensemble import HistGradientBoostingRegressor
OUT = "/root/work/out3c"; T, K = len(D.idx), len(D.cols)
M = D.M.to_numpy(); Mi = np.flatnonzero(M.ravel()); r_, c_ = np.divmod(Mi, K)
RS = np.nan_to_num(D.resid.to_numpy()); CS = np.cumsum(RS, 0)
def pm(df): return df.where(D.M).rank(1, pct=True)
feats = {}
def add(name, frame): feats[name] = np.asarray(frame, dtype=np.float32).ravel()[Mi]; gc.collect()
add("S0", S0); add("p_idio336", pI); add("p_fund", pF)
add("p_fundchg3d", pm(D.F - D.F.shift(72)))
z = np.load("/root/work/xs_hourly_2020_2025.npz", allow_pickle=True); Q = pd.DataFrame(z["quote_volume"], index=D.idx, columns=D.cols).astype(float)
C = pd.DataFrame(z["close"], index=D.idx, columns=D.cols).astype(float); del z
qr = (Q / Q.rolling(168, min_periods=100).mean().shift(1)).replace([np.inf, -np.inf], np.nan)
add("p_flow72", pm(pd.DataFrame(RS * qr.fillna(0).to_numpy(), index=D.idx, columns=D.cols).rolling(72, min_periods=1).sum()))
add("p_vspike8", pm(qr.rolling(8, min_periods=1).max())); del qr
add("p_qv24", pm(Q.rolling(24).sum())); del Q; gc.collect()
R = pd.DataFrame(RS, index=D.idx, columns=D.cols)
for n in (24, 72, 168): add(f"p_ret{n}", pm(R.rolling(n).sum()))
add("p_idioshare", pm(D.idio(336) ** 2 / D.R1.rolling(336, min_periods=200).var()))
lc = np.log(C); add("p_nearhigh", pm(lc - lc.rolling(720, min_periods=400).max())); del lc, C; gc.collect()
add("p_beta168", pm(D.bB))
sig = D.idio(168).shift(1); add("p_zmax8", pm((R.abs() / sig).rolling(8, min_periods=1).max())); del sig
r24 = R.rolling(24).sum(); add("p_varratio", pm(r24.rolling(336, min_periods=200).var() / (24 * R.rolling(336, min_periods=200).var()))); del r24
p0 = np.asarray(D.idx.hour % 8 == 0, float)[:, None]
add("p_settledrift", pm(pd.DataFrame(RS * p0, index=D.idx, columns=D.cols).rolling(720).sum() / 90 - pd.DataFrame(RS * (1 - p0), index=D.idx, columns=D.cols).rolling(720).sum() / 630))
add("univ_n", np.repeat(M.sum(1)[:, None], K, 1)); del R; gc.collect()
X = np.column_stack([feats[k] for k in feats]); names = list(feats); del feats; gc.collect()
# target: pct rank of 72h forward residual inside M
fwd = np.full(T, np.nan)[:, None] * np.ones((1, 1))
Y = pd.DataFrame(np.where(np.arange(T)[:, None] + 73 < T, CS[np.minimum(np.arange(T) + 73, T - 1)] - CS[np.minimum(np.arange(T) + 1, T - 1)], np.nan)).where(M).rank(1, pct=True).to_numpy().ravel()[Mi].astype(np.float32)
hr = D.idx.hour.to_numpy()[r_]; yr = D.idx.year.to_numpy()[r_]; tend = r_ + 73
print("features", names, X.shape, "Y finite", int(np.isfinite(Y).sum()), flush=True)
assert all(np.isfinite(X[:, k]).mean() > 0.5 for k in range(X.shape[1])), "degenerate feature"
np.savez(f"{OUT}/W08_XY.npz", X=X, Y=Y, r_=r_, c_=c_)
pred = np.full(len(Mi), np.nan, np.float32)
for Yy in range(2021, 2026):
    y0 = np.searchsorted(D.idx, pd.Timestamp(f"{Yy}-01-01"))
    tr = (hr % 8 == 7) & (tend < y0) & np.isfinite(Y) & (D.idx[r_] >= pd.Timestamp("2020-03-15"))
    m = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=200, l2_regularization=1.0, early_stopping=False, random_state=0)
    print(Yy, 'n_train', int(tr.sum()), flush=True)
    m.fit(X[tr], Y[tr]); te = yr == Yy; pred[te] = m.predict(X[te]); print(Yy, "trained on", int(tr.sum()), flush=True)
P = np.full((T, K), np.nan, np.float32); P.ravel()[Mi] = pred; np.save(f"{OUT}/W08_pred.npy", P)
# pre-screen: IC of prediction vs realised 72h fwd inside candidate sets (offset-0 rows)
S = S0.to_numpy(); F = D.F.to_numpy(); ics = []
for i in np.flatnonzero((D.idx.hour % 8 == 7) & (D.idx >= "2021-01-01") & (np.arange(T) + 73 < T)):
    m = np.flatnonzero(M[i] & np.isfinite(S[i]) & np.isfinite(P[i]))
    if len(m) < 18: continue
    nS = 20 if len(m) >= 40 else max(1, len(m) // 3); nL = 12 if len(m) >= 24 else max(1, len(m) // 3); x = min(8, max(2, (len(m) - nS - nL) // 2))
    o = m[np.argsort(S[i, m])]; cS = [c for c in o[::-1] if not F[i, c] < -5e-4][:nS + x]; cL = list(o[:nL + x]); f = CS[i + 73] - CS[i + 1]
    for cs in (cS, cL):
        a = pd.Series(P[i, cs]).rank().to_numpy(); b = pd.Series(f[cs]).rank().to_numpy(); ics.append((D.idx[i], np.corrcoef(a, b)[0, 1]))
ic = pd.Series(dict(ics)) if False else pd.Series([v for _, v in ics], index=[d for d, _ in ics])
print("in-candidate IC by year:", ic.groupby(ic.index.year).mean().round(4).to_dict())
tIC = h.nw_t(ic.dropna().to_numpy(), 30); print("mean IC %.4f NW t %.2f -> %s" % (ic.mean(), tIC, "PASS" if ic.mean() > 0 and tIC >= 1.5 else "FAIL"), flush=True)
# re-ranked score for the book: inside each candidate set, permute the set's S0 values by prediction (shorts: lowest pred gets highest S0)
SC = S.copy()
for i in np.flatnonzero(D.idx >= "2021-01-01"):
    m = np.flatnonzero(M[i] & np.isfinite(S[i]) & np.isfinite(P[i]))
    if len(m) < 18: continue
    nS = 20 if len(m) >= 40 else max(1, len(m) // 3); nL = 12 if len(m) >= 24 else max(1, len(m) // 3); x = min(8, max(2, (len(m) - nS - nL) // 2))
    o = m[np.argsort(S[i, m])]; cS = o[::-1][:nS + x]; cL = o[:nL + x]
    SC[i, cS[np.argsort(P[i, cS])]] = np.sort(S[i, cS])[::-1]      # lowest predicted return -> highest score (short first)
    SC[i, cL[np.argsort(-P[i, cL])]] = np.sort(S[i, cL])           # highest predicted return -> lowest score (long first)
np.save(f"{OUT}/W08_score.npy", SC.astype(np.float32)); print("saved score", flush=True)
