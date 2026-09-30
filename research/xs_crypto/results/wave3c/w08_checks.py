# W08 leak/robustness checks from the cached feature matrix (no full data load).
# (a) baseline in-candidate IC (offset-0 rows, candidate sets from the S0 column; funding guard ignored);
# (b) permutation importance (permute a feature within each row's candidate set, IC drop);
# (c) placebo: retrain on targets permuted within each row -> IC must be ~0;
# (d) all features lagged 8h (same coin, row r-8) -> IC should decay, not jump.
import numpy as np, pandas as pd, sys
sys.path.insert(0, "/root/work"); import cloud_harness as h
from sklearn.ensemble import HistGradientBoostingRegressor
z = np.load("/root/work/out3c/W08_XY.npz"); X, Y, r_, c_ = z["X"], z["Y"], z["r_"], z["c_"]
idx = pd.to_datetime(np.load("/root/work/xs_hourly_2020_2025.npz", allow_pickle=True)["hours"]); T = len(idx); K = int(c_.max()) + 1
names = ['S0','p_idio336','p_fund','p_fundchg3d','p_flow72','p_vspike8','p_qv24','p_ret24','p_ret72','p_ret168','p_idioshare','p_nearhigh','p_beta168','p_zmax8','p_varratio','p_settledrift','univ_n']
hr = idx.hour.to_numpy()[r_]; yr = idx.year.to_numpy()[r_]
P = dict(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=200, l2_regularization=1.0, early_stopping=False, random_state=0)
rng = np.random.default_rng(0)
def fit_predict(Xm, Ym):
    pred = np.full(len(Ym), np.nan, np.float32)
    for Yy in range(2021, 2026):
        y0 = np.searchsorted(idx, pd.Timestamp(f"{Yy}-01-01"))
        tr = (hr % 8 == 7) & (r_ + 73 < y0) & np.isfinite(Ym) & (idx[r_] >= pd.Timestamp("2020-03-15"))
        m = HistGradientBoostingRegressor(**P).fit(Xm[tr], Ym[tr]); te = (yr == Yy) & (hr % 8 == 7); pred[te] = m.predict(Xm[te])
    return pred
# candidate sets per offset-0 row (from S0 column), test years only
ev = np.flatnonzero((hr % 8 == 7) & (yr >= 2021) & np.isfinite(Y))
rows = pd.Series(ev).groupby(r_[ev]).apply(list)
def cand_sets():
    out = []
    for r, ii in rows.items():
        ii = np.array(ii); s = X[ii, 0]; ok = np.isfinite(s); ii, s = ii[ok], s[ok]; n = len(ii)
        if n < 18: continue
        nS = 20 if n >= 40 else max(1, n // 3); nL = 12 if n >= 24 else max(1, n // 3); x = min(8, max(2, (n - nS - nL) // 2))
        o = ii[np.argsort(s)]; out.append((idx[r], o[::-1][:nS + x])); out.append((idx[r], o[:nL + x]))
    return out
CS_ = cand_sets()
def ic(pred):
    v = [(d, np.corrcoef(pd.Series(pred[s]).rank(), pd.Series(Y[s]).rank())[0, 1]) for d, s in CS_]
    x = pd.Series([b for _, b in v], index=[a for a, _ in v]).dropna(); return x.mean(), h.nw_t(x.to_numpy(), 30), x.groupby(x.index.year).mean().round(3).to_dict()
base = fit_predict(X, Y); b = ic(base); print("baseline IC %.4f t %.1f %s" % b, flush=True)
imp = {}
# refit once per year keeping the models, for proper permutation importance
models = {}
for Yy in range(2021, 2026):
    y0 = np.searchsorted(idx, pd.Timestamp(f"{Yy}-01-01"))
    tr = (hr % 8 == 7) & (r_ + 73 < y0) & np.isfinite(Y) & (idx[r_] >= pd.Timestamp("2020-03-15"))
    models[Yy] = HistGradientBoostingRegressor(**P).fit(X[tr], Y[tr])
def predict(Xm):
    pred = np.full(len(Y), np.nan, np.float32)
    for Yy, m in models.items():
        te = (yr == Yy) & (hr % 8 == 7); pred[te] = m.predict(Xm[te])
    return pred
for k, n in enumerate(names):
    Xp = X.copy()
    for _, s in CS_: Xp[s, k] = X[rng.permutation(s), k]
    imp[n] = b[0] - ic(predict(Xp))[0]
print("permutation importance (IC drop):", {k: round(v, 4) for k, v in sorted(imp.items(), key=lambda z: -z[1])}, flush=True)
# placebo: targets permuted within each row (all rows used for training)
Yp = Y.copy()
for r, ii in pd.Series(np.arange(len(Y))).groupby(r_).apply(list).items():
    ii = np.array(ii); Yp[ii] = Y[rng.permutation(ii)]
pl = fit_predict(X, Yp); print("placebo (shuffled-target) IC %.4f t %.1f %s" % ic(pl), flush=True)
# features lagged 8h: row r uses features of the same coin at row r-8
pos = np.full((T, K), -1, np.int64); pos[r_, c_] = np.arange(len(r_))
lag = pos[np.maximum(r_ - 8, 0), c_]; Xl = np.where((lag >= 0)[:, None], X[np.maximum(lag, 0)], np.nan).astype(np.float32)
lg = fit_predict(Xl, Y); print("features lagged 8h IC %.4f t %.1f %s" % ic(lg), flush=True)
