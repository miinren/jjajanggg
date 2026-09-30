# hedge (T20-T24) + construction/exposure (T25-T32)
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
    pickle.dump(out, open("run2.pkl", "wb")); ev.update_csv(rows)
R1, rb = D.R1, D.rb
def fb(X): return X.where(np.isfinite(X)).fillna(D.bB).fillna(1).to_numpy()
def mbeta(m, n, mp):   # beta of R1 on rb using only hours where mask m (Series bool), rolling n
    mf = m.astype(float); x = rb * mf
    cnt = mf.rolling(n, min_periods=1).sum()
    Sy = R1.mul(mf, axis=0).rolling(n, min_periods=1).sum(); Sxy = R1.mul(x, axis=0).rolling(n, min_periods=1).sum()
    Sx = x.rolling(n, min_periods=1).sum(); Sxx = (x * x).rolling(n, min_periods=1).sum()
    cov = Sxy.div(cnt, axis=0) - Sy.div(cnt, axis=0).mul(Sx / cnt, axis=0); var = Sxx / cnt - (Sx / cnt) ** 2
    b = cov.div(var, axis=0); b[cnt < mp] = np.nan
    return b.where(R1.rolling(n, min_periods=mp).count() >= mp)
hb = fb(mbeta(rb.abs() > rb.rolling(720, min_periods=400).std(), 720, 40)); gc.collect()
go("hedge_crashbeta", HB=hb); del hb; gc.collect()
hb = fb(mbeta(rb < 0, 336, 100)); go("hedge_downbeta", HB=hb); del hb; gc.collect()
def rbeta(y, x, n, mp):
    return (y.mul(x, axis=0).rolling(n, min_periods=mp).mean() - y.rolling(n, min_periods=mp).mean().mul(x.rolling(n, min_periods=mp).mean(), axis=0)).div(x.rolling(n, min_periods=mp).var(), axis=0)
hb = fb(rbeta(R1.rolling(4).sum(), rb.rolling(4).sum(), 672, 400)); go("hedge_4hbeta", HB=hb); del hb; gc.collect()
hb = fb(D.bB + rbeta(R1, rb.shift(1), 168, 100)); go("hedge_dimson", HB=hb); del hb; gc.collect()
re = R1["ETHUSDT"]; n, mp = 168, 100
mean = lambda s: s.rolling(n, min_periods=mp).mean()
vbb = rb.rolling(n, min_periods=mp).var(ddof=0); vee = re.rolling(n, min_periods=mp).var(ddof=0); vbe = mean(rb * re) - mean(rb) * mean(re)
my = R1.rolling(n, min_periods=mp).mean()
cyb = R1.mul(rb, axis=0).rolling(n, min_periods=mp).mean() - my.mul(mean(rb), axis=0)
cye = R1.mul(re, axis=0).rolling(n, min_periods=mp).mean() - my.mul(mean(re), axis=0); del my
det = vbb * vee - vbe ** 2
bBt = (cyb.mul(vee, axis=0) - cye.mul(vbe, axis=0)).div(det, axis=0); bEt = (cye.mul(vbb, axis=0) - cyb.mul(vbe, axis=0)).div(det, axis=0); del cyb, cye
ok = np.isfinite(bBt.to_numpy()) & np.isfinite(bEt.to_numpy())
HB = np.where(ok, bBt.to_numpy(), D.B); HE = np.where(ok, bEt.to_numpy(), 0.0); del bBt, bEt, ok; gc.collect()
ren = re.shift(-2).fillna(0).to_numpy()
go("hedge_btceth", HB=HB, HE=HE, ren=ren); del HB, HE; gc.collect()
print("hedges done", time.time() - t0, flush=True)
go("pc_adj_0.5", adj=0.5)
iv = D.idio(336).to_numpy()
def rp(i, longs, shorts):
    aL = np.nanmean(iv[i, longs]); aS = np.nanmean(iv[i, shorts]); gL = (1 / aL) / (1 / aL + 1 / aS)
    return np.full(len(longs), gL / len(longs)), np.full(len(shorts), (1 - gL) / len(shorts))
go("pc_riskparity_legs", leg_weights=rp)
def hourly(g): return g.reindex(D.idx.floor("D")).fillna(1.0).to_numpy()
r24 = D.resid.rolling(24).sum().where(D.M); disp = r24.std(1).resample("D").last().shift(1); del r24
g = (disp.rolling(90, min_periods=30).median() / disp).clip(0.5, 1.0).fillna(1.0)
go("ex_disp", gross=hourly(g))
fm = D.F.where(D.M).mean(1).resample("D").last().shift(1)
for q in [0.8, 0.9]:
    thr = fm.expanding(60).quantile(q).shift(1); go(f"ex_fund_q{q}", gross=hourly(pd.Series(np.where(fm > thr, 0.5, 1.0), index=fm.index)))
A = D.resid.rolling(336, min_periods=200).sum().where(D.M).median(1).resample("D").last().shift(1)
for q in [0.8, 0.9]:
    thr = A.expanding(60).quantile(q).shift(1); go(f"ex_altseason_q{q}", gross=hourly(pd.Series(np.where(A > thr, 0.5, 1.0), index=A.index)))
thr = A.expanding(60).quantile(0.8).shift(1); flag = hourly(pd.Series(np.where(A > thr, 1.0, 0.0), index=A.index).replace(1.0, 2.0)) == 2.0
def altw(i, longs, shorts):
    sf = 0.30 if flag[i] else 0.55
    return np.full(len(longs), 0.45 / len(longs)), np.full(len(shorts), sf / len(shorts))
go("ex_altseason_short", leg_weights=altw)
pickle.dump(dict(disp=disp, fm=fm, A=A), open("run2_sig.pkl", "wb"))
print("done", time.time() - t0)
