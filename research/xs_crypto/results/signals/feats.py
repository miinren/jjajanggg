"""Feature definitions. Every feature at row i uses data <= hour i only (R1[i] = log C[i]/C[i-1]; D.F = prior-day funding)."""
import numpy as np, pandas as pd, cloud_harness as h

def rbeta(y, x, n, mp=None):
    mp = mp or int(0.6 * n)
    return (y.mul(x, axis=0).rolling(n, min_periods=mp).mean() - y.rolling(n, min_periods=mp).mean().mul(x.rolling(n, min_periods=mp).mean(), axis=0)).div(x.rolling(n, min_periods=mp).var(), axis=0)

def loadQ(D):
    z = np.load(h.NPZ, allow_pickle=True)
    return pd.DataFrame(z["quote_volume"], index=D.idx, columns=D.cols).astype(float)

def season(e, lag, n):
    """mean of e at t-lag, t-2lag, ..., t-n*lag (a seasonal forecast for hour t using data <= t-lag), then summed over the
    hours the book will hold after a rebalance at i: rows i+2..i+9 (needs lag >= 10 to stay causal)."""
    a = e.to_numpy(np.float32); s = np.zeros_like(a); c = np.zeros_like(a)
    for d in range(1, n + 1):
        sh = np.full_like(a, np.nan); sh[d * lag:] = a[:-d * lag]
        ok = np.isfinite(sh); s[ok] += sh[ok]; c += ok
    m = pd.DataFrame(np.where(c >= n // 2, s / np.maximum(c, 1), np.nan), index=e.index, columns=e.columns)
    return m.rolling(8, min_periods=6).sum().shift(-9)   # row i -> m[i+2..i+9]; m[i+9] uses e <= i+9-lag <= i-1

def feature(D, name, PHI=None):
    R1, e, rb, F = D.R1, D.resid, D.rb, D.F
    if name == "beta_chg": return D.bB - rbeta(R1, rb, 720)
    if name == "beta_instab": return D.bB.rolling(720, min_periods=400).std()
    if name == "iskew": return e.rolling(336, min_periods=200).skew()
    if name == "phi": return PHI
    if name == "fund_chg": return F - F.rolling(168, min_periods=120).mean()
    if name == "fund_z30":
        m, s = F.rolling(720, min_periods=480).mean(), F.rolling(720, min_periods=480).std()
        return (F - m) / s.where(s > 1e-6)
    if name == "fund_vol": return F.rolling(720, min_periods=480).std()
    if name == "amihud":
        Q = loadQ(D); am = (R1.abs() / Q.where(Q > 0)).rolling(336, min_periods=200).mean(); return -am
    if name == "turn_trend":
        Q = loadQ(D); return np.log(Q.rolling(168, min_periods=100).sum() / Q.rolling(720, min_periods=400).sum())
    if name == "age": return -(R1.notna().cummax().cumsum())
    if name == "volvol_div":
        Q = loadQ(D)
        return np.log(D.idio(168) / e.rolling(720, min_periods=400).std()) - np.log(Q.rolling(168, min_periods=100).sum() / Q.rolling(720, min_periods=400).sum())
    if name == "hod_season": return -season(e, 24, 30)
    if name == "dow_season": return -season(e, 168, 12)
    if name == "btc_delay": return -sum(rbeta(R1, rb.shift(k), 336) for k in (1, 2, 3))
    if name == "coskew":
        return e.mul(rb ** 2, axis=0).rolling(720, min_periods=400).mean() / (e.rolling(720, min_periods=400).std().mul(rb.rolling(720, min_periods=400).var(), axis=0))
    if name == "near_high":
        lc = R1.fillna(0).cumsum().where(R1.notna())   # log price up to a per-coin constant
        return -(lc - lc.rolling(720, min_periods=400).max())
    if name == "jump_beta":
        sd = rb.rolling(720, min_periods=400).std().shift(1); J = (rb.abs() > 2 * sd).astype(float); N_ = 1 - J
        def b(I):
            x = rb * I
            return R1.mul(x, axis=0).rolling(720, min_periods=400).sum().div((x * x).rolling(720, min_periods=400).sum(), axis=0)
        return -(b(J) - b(N_))
    if name == "idio_2f":
        eE = e["ETHUSDT"]; g = rbeta(e, eE, 168, 100); return (e - g.mul(eE, axis=0)).rolling(336, min_periods=200).std()
    if name.startswith("absmove"): return e.rolling(int(name[7:]), min_periods=1).sum().abs()
    if name.startswith("rev"):   # rev3 / rev6: residual sum over last k hours (low = long)
        return e.rolling(int(name[3:]), min_periods=1).sum()
    raise KeyError(name)

def pct(D, x): return x.where(D.M).rank(1, pct=True).fillna(0.5)
