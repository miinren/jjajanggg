# D1b: short-leg alpha (BTC+ETH, +ALT) for carry and score variants; D2b: t-stats of D2 forward returns (events clustered by day).
from lib4 import *
import numpy.linalg as la
g = np.expm1(D.Rn); ib, ie = D.ib, D.cols.index("ETHUSDT")
alt = np.nanmean(np.where(D.M.to_numpy(), g, np.nan), 1)
F = cut(pd.DataFrame({"BTC": g[:, ib], "ETH": g[:, ie], "ALT": np.nan_to_num(alt)}, index=D.idx).resample("D").sum())
def reg(y, cols):
    y = cut(y).reindex(F.index); X = np.column_stack([np.ones(len(y))] + [F[c].to_numpy() for c in cols]); b = la.lstsq(X, y.to_numpy(), rcond=None)[0]
    return b[0] * 1e4, h.nw_t(pd.Series(y.to_numpy() - X @ b + b[0]))
for tag, lab, sf in (("T06_s1", "B-MV idio+fund shorts", 0.55), ("T08_s1", "CARRY-55 shorts", 0.55), ("T10_s1", "CARRY7-55 shorts", 0.55),
                     ("T12_s2", "N8 fw0 L336 shorts", 0.55), ("T07_s1", "N8 fw0.25 L336 shorts", 0.55), ("T17_s2", "N8 fw0.5 L336 shorts", 0.55)):
    df = run8(tag)["df"]; a1, t1 = reg(df.short / sf, ["BTC", "ETH"]); a2, t2 = reg(df.short / sf, ["BTC", "ETH", "ALT"])
    x = cut(df); print(f"{lab:26s} per $ short: raw price {x.short.mean()/sf*1e4:6.2f}  funding(short+hedge) {x.fund_s.mean()*1e4:5.2f} bp/day | alpha BTC+ETH {a1:6.2f} (t {t1:.2f})  +ALT {a2:6.2f} (t {t2:.2f})")
# D2b
TH = [0.0, 0.2, 0.3, 0.5, 0.75, 1.0]
L = dict(th=TH, seen=set(), ev=[]); ext5.book(D, S0, offset=0, **{**REAL, "stop": 100.0}, log_short=L)
CL = np.nan_to_num(D.R1.to_numpy()).cumsum(0); T = len(D.idx)
print("\nD2b LIVE rules: mean forward return, t with events clustered by calendar day (SE of daily means)")
for th in TH:
    ev = [(i, s) for (i, s, t) in L["ev"] if t == th and i + 2 + 168 < T]
    for H in (72, 168):
        fr = pd.Series([np.expm1(CL[i + 2 + H, s] - CL[i + 2, s]) for i, s in ev], index=[D.idx[i].floor("D") for i, s in ev])
        dm = fr.groupby(level=0).mean(); print(f"  +{int(th*100):3d}%  H={H:3d}h  n={len(fr):4d} days={len(dm):4d}  mean {fr.mean()*100:6.2f}%  t {dm.mean()/dm.std()*np.sqrt(len(dm)):5.2f}")
