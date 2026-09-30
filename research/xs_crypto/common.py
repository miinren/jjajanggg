import numpy as np, pandas as pd, cloud_harness as h, ext
D = h.Data()
e = D.resid; el = e.shift(1)
PHI = ((e*el).rolling(336, min_periods=200).mean() / (el*el).rolling(336, min_periods=200).mean()).clip(-0.5, 0.5)
EC = e - PHI*el
IDIO_RAW = EC.rolling(336, min_periods=200).std()
pI = IDIO_RAW.where(D.M).rank(1, pct=True)
pF = D.F.where(D.M).rank(1, pct=True).fillna(0.5)
S0 = 0.75*pI + 0.25*pF
ST = "2020-03-15"
def cut(x): return x[(x.index >= ST) & (x.index < "2026-01-01")]
def stats(df):
    x = cut(df.net); cum = x.cumsum(); v = x.std()
    k = 0.02/v  # scale to 2%/day vol for comparable MDD
    yr = x.groupby(x.index.year).apply(lambda y: y.mean()/y.std()*np.sqrt(365))
    return dict(SR=x.mean()/v*np.sqrt(365), bp=x.mean()*1e4, vol_bp=v*1e4, mdd_bp=(cum-cum.cummax()).min()*1e4,
                mdd_at2pct=(k*cum-(k*cum).cummax()).min()*100, calmar=x.mean()*365/-(cum-cum.cummax()).min(),
                minYrSR=yr.min(), SR2022=yr.get(2022), worst5=x.rolling(5).sum().min()*1e4/v/1e4)
