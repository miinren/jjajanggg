import sys, os, gc, pickle, time, numpy as np, pandas as pd
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/wave2")
from common import D, S0, IDIO_RAW, stats, cut, h, ST
import ext3
OUT = "/root/work/results/wave2"
BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
iv = D.idio(336).to_numpy(); RS = np.nan_to_num(D.resid.to_numpy())
CV = {"minvar": [], "invvol": []}   # within-rebalance coefficient of variation of short weights (x / mean)
def _eq_long(longs): return np.full(len(longs), 0.45 / len(longs))
def invvol(i, longs, shorts, rec=False):
    a = 1 / np.maximum(iv[i, shorts], 1e-5); a = np.nan_to_num(a, nan=np.nanmean(a)); e = 1 / len(shorts)
    x = np.clip(a / a.sum(), 0.5 * e, 2 * e); x /= x.sum()
    if rec: CV["invvol"].append(x.std() / x.mean())
    return _eq_long(longs), 0.55 * x
def minvar(i, longs, shorts, rec=False):
    if len(shorts) < 2: return _eq_long(longs), np.full(len(shorts), 0.55 / max(1, len(shorts)))
    X = RS[max(0, i - 335):i + 1][:, shorts]; C = np.cov(X.T); C = 0.5 * C + 0.5 * np.diag(np.diag(C)); e = 1 / len(shorts)
    try: x = np.linalg.solve(C + 1e-10 * np.eye(len(shorts)), np.ones(len(shorts)))
    except np.linalg.LinAlgError: x = np.ones(len(shorts))
    x = np.maximum(x, 0); x = x / x.sum() if x.sum() > 0 else np.full(len(shorts), e)
    for _ in range(5): x = np.minimum(x, 2 * e); x /= x.sum()
    if rec: CV["minvar"].append(x.std() / x.mean())
    return _eq_long(longs), 0.55 * x
def placebo(sigma, seed, clip_lo=None):
    z = np.random.default_rng(1000 + seed).standard_normal(len(D.cols)); g = np.exp(sigma * z)
    def f(i, longs, shorts):
        e = 1 / len(shorts); x = g[shorts] / g[shorts].sum()
        if clip_lo is not None: x = np.clip(x, clip_lo * e, 2 * e); x /= x.sum()
        else:
            for _ in range(5): x = np.minimum(x, 2 * e); x /= x.sum()
        return _eq_long(longs), 0.55 * x
    return f
def avg8(keep_coin=True, score=S0, per_offset=None, **kw):
    """8-clock-averaged book. Returns (daily df, coin matrix float32 or None)."""
    df = cm = None
    for off in range(8):
        d, c = ext3.book(D, score, offset=off, **BK, **kw)
        if per_offset is not None: per_offset[off] = d
        df = d / 8 if df is None else df + d / 8
        if keep_coin: cm = c / np.float32(8) if cm is None else cm + c / np.float32(8)
        del c; gc.collect()
    return df, cm
def srx(x): return x.mean() / x.std() * np.sqrt(365)
def sr_at(df, c): return srx(cut(df.net + df.to * (h.COST - c * 1e-4)))
def risk(df, vref):
    """risk metrics after scaling to daily vol vref (bp at vref)."""
    x = cut(df.net); x = x * (vref / x.std()); q = x.quantile(0.05)
    cum = x.cumsum()
    return dict(cvar5=-x[x <= q].mean() * 1e4, w20=-x.rolling(20).sum().min() * 1e4, mdd=-(cum - cum.cummax()).min() * 1e4,
                d20220613=x.get(pd.Timestamp("2022-06-13"), np.nan) * 1e4)
