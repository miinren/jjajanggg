# DIAGNOSTIC (not a trial): is there any hourly BTC lead-lag in the cross-section at a tradable lag (i+2)?
import sys; sys.path.insert(0, "/root/work")
import numpy as np, pandas as pd, cloud_harness as h
D = h.Data()
R1, rb, M = D.R1, D.rb, D.M
e = D.resid
def ic(sig, fwd):
    s = sig.where(M).rank(1); f = fwd.where(M).rank(1)
    s = s.sub(s.mean(1), axis=0); f = f.sub(f.mean(1), axis=0)
    c = (s*f).sum(1)/np.sqrt((s*s).sum(1)*(f*f).sum(1))
    c = c[(c.index >= "2020-03-15")].dropna()
    return c.mean(), c.mean()/c.std()*np.sqrt(len(c))
f1 = e.shift(-2)                       # residual return earned by a position set at i (book convention)
f8 = e.rolling(8).sum().shift(-9)      # residual return i+2..i+9
# lagged betas: regress R1_t on rb_{t-k}; mean across coins
for k in range(0, 5):
    x = rb.shift(k)
    g = (R1.mul(x, axis=0).rolling(336, min_periods=200).mean() - R1.rolling(336, min_periods=200).mean().mul(x.rolling(336, min_periods=200).mean(), axis=0)).div(x.rolling(336, min_periods=200).var(), axis=0)
    gm = g.where(M).mean(1); print(f"lag{k} beta: mean xs-avg {gm.mean():.4f}  2020-22 {gm[:'2022'].mean():.4f} 2023-25 {gm['2023':].mean():.4f}", flush=True)
    if k == 2: G2 = g
    if k == 3: G3 = g
for k in (1, 3, 6):
    gap = -(e.rolling(k).sum())   # beta*btc - coin over last k hours (catch-up gap)
    print(f"gap{k}h: IC1 {ic(gap, f1)}  IC8 {ic(gap, f8)}", flush=True)
    # BTC move-conditional: only the beta-scaled part, i.e. gap interacted with sign of BTC move
    btck = rb.rolling(k).sum()
    big = btck.abs() > btck.abs().rolling(720, min_periods=200).quantile(0.8)
    g2 = gap.where(big.values[:, None].repeat(gap.shape[1], 1))
    print(f"gap{k}h on big-BTC-move hours: IC1 {ic(g2, f1)}  IC8 {ic(g2, f8)}", flush=True)
pred = G2.mul(rb, axis=0) + G3.mul(rb.shift(1), axis=0)   # predictable delayed response to known BTC moves
print("delayed-beta prediction: IC1", ic(pred, f1), "IC8", ic(pred, f8))
