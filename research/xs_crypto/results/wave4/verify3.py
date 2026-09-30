# (3b) same synthetic check with funding zeroed: NAV must equal buy-and-hold to machine precision if drift/simple are exact
from lib4 import *
cols = [D.cols.index(c) for c in ("SOLUSDT", "ADAUSDT", "XRPUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT")]
el = pd.DataFrame(False, index=D.idx, columns=D.cols); el.iloc[:, cols] = True
sc = pd.DataFrame(np.nan, index=D.idx, columns=D.cols); sc.iloc[:, cols] = np.arange(6)[None, :].astype(float)
Fh0 = D.Fh; D.Fh = np.zeros_like(Fh0)
d, cm = ext5.book(D, sc, N=2, NS=1, short_frac=0.0, stops=False, hedge=0.0, cost=0.0, elig=el, simple=True, drift=True, keepx=0.0)
D.Fh = Fh0
hr = np.asarray(cm, float).sum(1); C = np.exp(D.R1.iloc[:, cols[:2]].fillna(0).cumsum()).to_numpy()
reb = np.flatnonzero((D.idx.hour + 1) % 8 == 0); errs = []
for i0 in reb[2000:2400]:
    i1 = i0 + 8; nav = np.prod(1 + hr[i0:i1]); bh = 0.5 * C[i1 + 1, 0] / C[i0 + 1, 0] + 0.5 * C[i1 + 1, 1] / C[i0 + 1, 1]; errs.append(nav - bh)
print("(3b) funding off: max |NAV - buyhold| = %.2e (float32 coin matrix)" % np.max(np.abs(errs)))
g = np.expm1(D.Rn[:, cols]); cmn = np.asarray(cm, float)[:, cols]
bad = [i0 for i0, e in zip(reb[2000:2400], errs) if abs(e) > 1e-6]
print("windows with error:", len(bad), "of 400")
i0 = bad[0] if bad else reb[2000]
with np.errstate(all="ignore"): print("implied weights first hours of a bad window:\n", np.round(cmn[i0:i0 + 3] / g[i0:i0 + 3], 4))
ok = [e for i0, e in zip(reb[2000:2400], errs) if (cmn[i0, 2:] == 0).all() and abs(cmn[i0, :2]).min() > 0]
print("windows with only SOL/ADA held: %d, max err %.2e" % (len(ok), np.max(np.abs(ok))))
good = []
for i0, e in zip(reb[2000:2400], errs):
    with np.errstate(all="ignore"): wimp = cmn[i0, :2] / g[i0, :2]
    if np.all(np.abs(wimp - 0.5) < 1e-4): good.append(e)
print("(3c) windows starting at exactly 50/50: %d, max |NAV - buyhold| = %.2e" % (len(good), np.max(np.abs(good))))
