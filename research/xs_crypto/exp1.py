import sys, time, pickle, numpy as np, pandas as pd
from multiprocessing import Pool
from common import *
M = D.M
def pct(X): return X.where(M).rank(1, pct=True)
rb = D.rb; R1 = D.R1
# --- signal panels (all use data up to hour i; book trades at i+2)
def rcov(y, x, n):
    mp = int(n*0.6); return y.mul(x, axis=0).rolling(n, min_periods=mp).mean() - y.rolling(n, min_periods=mp).mean().mul(x.rolling(n, min_periods=mp).mean(), axis=0)
xd = rb.where(rb < 0, 0.0)
beta720 = rcov(R1, rb, 720).div(rb.rolling(720, min_periods=432).var(), axis=0)
bdown = rcov(R1, xd, 720).div(xd.rolling(720, min_periods=432).var(), axis=0)
P = {"beta": pct(D.bB), "beta720": pct(beta720), "dbeta": pct(bdown - beta720),
     "rev72": pct(EC.rolling(72, min_periods=48).sum()), "mom720": 1 - pct(EC.rolling(720, min_periods=432).sum()),
     "max168": pct(D.resid.rolling(168, min_periods=100).max())}
z = np.load(h.NPZ, allow_pickle=True); Q = pd.DataFrame(z["quote_volume"], index=D.idx, columns=D.cols).astype(float); del z
P["vshock"] = pct(Q.rolling(24).sum() / (Q.rolling(168, min_periods=100).sum() / 7)); del Q
# hedge variants: B arrays swapped in worker
Bs = {"b720": beta720.fillna(1).to_numpy(), "shrink50": (0.5*D.bB + 0.5).fillna(1).to_numpy(),
      "cap2": D.bB.clip(0, 2).fillna(1).to_numpy()}
BASE = ext.book(D, S0)
bn = BASE[0].net
sig = cut(bn).rolling(30, min_periods=20).std().reindex(bn.index).shift(1)
def gross_from_daily(g):  # daily gross (known at start of day) -> hourly
    return g.reindex(D.idx.floor("D")).fillna(1).to_numpy()
tgt = cut(bn).std()
btc30 = rb.rolling(720, min_periods=500).sum()
ivol = IDIO_RAW.to_numpy()
def invvol(i, longs, shorts):
    a = 1/np.maximum(ivol[i, longs], 1e-4); b = 1/np.maximum(ivol[i, shorts], 1e-4)
    return 0.5*a/a.sum(), 0.5*b/b.sum()
def cands():
    C = {}
    for hr in [0, 0.5, 0.75]: C[f"hedge{hr}"] = dict(hedge=hr)
    for k in Bs: C[f"hedgeB_{k}"] = dict(B=k)
    for s, wt in [("beta", .1), ("beta", .25), ("beta720", .1), ("dbeta", .1), ("rev72", .1), ("mom720", .1), ("max168", .1), ("vshock", .1)]:
        C[f"sig_{s}_{wt}"] = dict(sig=(s, wt))
    C["neg_beta_0.1"] = dict(sig=("beta", -.1))
    for cap in [1.5, 2.0]:
        g = (tgt/sig).clip(0.3, cap).fillna(1); C[f"voltgt_cap{cap}"] = dict(gross=g)
    cum = bn.cumsum(); dd = (cum - cum.rolling(60, min_periods=1).max()).shift(1)
    C["ddthrottle"] = dict(gross=pd.Series(np.where(dd < -0.10, 0.5, 1.0), index=bn.index))
    C["btcup_half"] = dict(gross_h=np.where(btc30.to_numpy() > 0.25, 0.5, 1.0))
    C["invvol_legs"] = dict(leg_weights=invvol)
    for sf in [0.4, 0.6]: C[f"shortfrac{sf}"] = dict(short_frac=sf)
    C["shortstop0.2"] = dict(stop=0.2)
    for n in [8, 10, 12, 15, 25, 30, 40]: C[f"N{n}"] = dict(N=n)
    for nl, ns in [(30, 15), (15, 30), (20, 12), (20, 30), (12, 20)]: C[f"NL{nl}_NS{ns}"] = dict(N=nl, NS=ns)
    return C
C = cands()
def run(name):
    kw = dict(C[name]); sc = S0
    if "sig" in kw:
        s, wt = kw.pop("sig"); sc = (1-abs(wt))*S0 + (wt*P[s] if wt > 0 else abs(wt)*(1-P[s])).fillna(0.5*abs(wt))
    if "gross" in kw: kw["gross"] = gross_from_daily(kw.pop("gross"))
    if "gross_h" in kw: kw["gross"] = kw.pop("gross_h")
    Bold = None
    if "B" in kw: Bold = D.B; D.B = Bs[kw.pop("B")]
    c = ext.book(D, sc, **kw)
    if Bold is not None: D.B = Bold
    r = h.partition_test(D, c, BASE, verbose=False)
    r.update(stats(c[0]))
    return name, r, c[0]
if __name__ == "__main__":
    t = time.time()
    with Pool(4) as p: out = p.map(run, list(C))
    print("done", time.time()-t)
    pickle.dump(dict(base=(BASE[0], stats(BASE[0])), res={n: (r, d) for n, r, d in out}), open("exp1.pkl", "wb"))
    rows = []
    for n, r, d in out:
        rows.append(dict(name=n, SR=r["SR"], bp=r["bp"], mdd2=r["mdd_at2pct"], calmar=r["calmar"], minYr=r["minYrSR"], tNW=r["tNW"], yrs=r["years_won"], grp=r["coin_groups_won"], up=r["regime_btc_up_bp"], dn=r["regime_btc_down_bp"], adopt=r["adopt"]))
    df = pd.DataFrame(rows).set_index("name"); b = stats(BASE[0])
    print("BASE", {k: round(float(v), 2) for k, v in b.items()})
    print(df.round(2).to_string())
