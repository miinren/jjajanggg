"""wave4 shared setup. REALISTIC accounting only: simple returns, positions drift, W06 hedge band 0.03, BTC-hedge funding.
Every book is 8-clock averaged; cached to ~/work/out4 (not committed)."""
import sys, os, gc, json, pickle, numpy as np, pandas as pd
W = os.path.expanduser("~/work"); HERE = os.path.dirname(os.path.abspath(__file__))
for p in (W, f"{W}/results/wave2", f"{W}/results/wave3c", HERE): sys.path.insert(0, p)
from common import D, S0, e as RESID, PHI, stats, cut, h, ST
from lib import minvar, srx
import ext5
OUT = f"{W}/out4"; os.makedirs(OUT, exist_ok=True)
REAL = dict(simple=True, drift=True, hedge_band=0.03, hedge_fund=True)

def minvar_floor(i, longs, shorts):             # = wave3c lib3c.minvar_floor (0.45 / 0.55 legs)
    if len(shorts) == 0: return np.full(len(longs), 0.45 / max(1, len(longs))), np.zeros(0)
    a, b = minvar(i, longs, shorts); x = b / 0.55; e = 1 / len(shorts)
    for _ in range(10): x = np.clip(x, 0.4 * e, 2 * e); x /= x.sum()
    return a, 0.55 * x
def mv_sf(sf):                                   # minvar_floor rescaled to a long/short split (wave3c realistic_sf fix)
    def f(i, longs, shorts):
        wl, ws = minvar_floor(i, longs, shorts); return wl * (1 - sf) / 0.45, ws * sf / 0.55
    return f

_SC = {}
def score(L=336, fw=0.25):
    """AR1-corrected idio vol at window L (PHI fixed at 336 as in common.py) blended with funding pct. (336, 0.25) == S0."""
    if (L, fw) == (336, 0.25): return S0
    if (L, fw) not in _SC:
        EC = RESID - PHI * RESID.shift(1)
        pI = EC.rolling(L, min_periods=int(L * 0.6) if L != 336 else 200).std().where(D.M).rank(1, pct=True)
        pF = D.F.where(D.M).rank(1, pct=True).fillna(0.5)
        _SC[(L, fw)] = pI if fw == 0 else (1 - fw) * pI + fw * pF
    return _SC[(L, fw)]

def run8(tag, score_=None, keep_coin=False, **kw):
    """8-clock average of ext5.book with REAL accounting unless overridden. Cached by tag."""
    p = f"{OUT}/{tag}.pkl"
    if os.path.exists(p): return pickle.load(open(p, "rb"))
    sc = S0 if score_ is None else score_
    df = cm = None; per = {}
    for off in range(8):
        d, c = ext5.book(D, sc, offset=off, **{**REAL, **kw}); per[off] = d
        df = d / 8 if df is None else df + d / 8
        if keep_coin:               # per-coin P&L aggregated to days (for coin-group partition tests)
            c = pd.DataFrame(c, index=D.idx).resample("D").sum().to_numpy(np.float32) / np.float32(8)
            cm = c if cm is None else cm + c
        del c; gc.collect()
    o = dict(df=df, per=per, cm=cm); pickle.dump(o, open(p, "wb")); return o

def sr_c(df, c, a=ST, b="2026-01-01"):          # SR at cost c bp over [a, b)
    x = df.net + df.to * (h.COST - c * 1e-4); x = x[(x.index >= a) & (x.index < b)]; return srx(x)
def win(x, a, b): return x[(x.index >= a) & (x.index < b)]

GROUPS = np.array_split(np.random.default_rng(7).permutation(len(D.cols)), 5)
BTC30 = D.rb.resample("D").sum().rolling(30).sum().shift(1)
def ptest(cand, base, a, b):
    """harness partition test on [a,b) (as wave3a lib3.ptest): risk-matched on the window; years rule = at most one losing year.
    cand/base: run8 dicts with daily cm."""
    dc, db = cand["df"], base["df"]; m = np.asarray((dc.index >= a) & (dc.index < b))
    k = db.net[m].std() / dc.net[m].std(); dd = dc.net[m] * k - db.net[m]
    yrs = dd.groupby(dd.index.year).mean(); ny = len(yrs); yw = int((yrs > 0).sum())
    grp = [float(cand["cm"][m][:, g].sum() * k - base["cm"][m][:, g].sum()) for g in GROUPS]; gw = sum(x > 0 for x in grp)
    r30 = BTC30.reindex(dd.index); up, dn = dd[r30 > 0].mean(), dd[r30 <= 0].mean(); t = h.nw_t(dd)
    return dict(t=t, years=f"{yw}/{ny}", groups=f"{gw}/5", up=up * 1e4, dn=dn * 1e4, diff_bp=dd.mean() * 1e4,
                ok=bool(yw >= ny - 1 and gw >= 4 and up > 0 and dn > 0 and t >= 1.5), k=k)
def mdd2(x):
    k = 0.02 / x.std(); cum = k * x.cumsum(); return (cum - cum.cummax()).min() * 100
def row(tag, o, a=ST, b="2026-01-01"):
    df = win(o["df"], a, b); x = df.net
    return dict(id=tag, SR=srx(x), SR8=sr_c(df, 8, a, b), SR12=sr_c(df, 12, a, b), bp=x.mean() * 1e4, L=df.long.mean() * 1e4, S=df.short.mean() * 1e4,
                H=df.hedge.mean() * 1e4, F=df.fund.mean() * 1e4, Fl=df.fund_l.mean() * 1e4, cost=-(df.to * h.COST).mean() * 1e4, to=df.to.mean(),
                vol=x.std() * 1e4, mdd2=mdd2(x), minYr=x.groupby(x.index.year).apply(srx).min(),
                yearly="/".join(f"{v:.2f}" for v in x.groupby(x.index.year).apply(srx)))

YEARS = (2023, 2024, 2025)
def select(pool, incumbent, Y, gated=True):
    """pseudo-holdout pick on [ST, Y): best SR; if gated, a non-incumbent must also pass ptest vs incumbent on the window."""
    a, b = ST, f"{Y}-01-01"; sr = {k: srx(win(o["df"].net, a, b)) for k, o in pool.items()}
    cands = [k for k in pool if k == incumbent or not gated or ptest(pool[k], pool[incumbent], a, b)["ok"]]
    return max(cands, key=lambda k: sr[k]), sr
def oos(picks, pool, ref, cost=5.5):
    """chain year-Y results of picks[Y]; risk-matched paired t vs ref (scale = selection-window vol ratio)."""
    xs, rs, ds = [], [], []
    for Y in YEARS:
        o = pool[picks[Y]]["df"]; r = ref["df"]
        c = o.net + o.to * (h.COST - cost * 1e-4); rr = r.net + r.to * (h.COST - cost * 1e-4)
        k = win(r.net, ST, f"{Y}-01-01").std() / win(o.net, ST, f"{Y}-01-01").std()
        x = c[c.index.year == Y]; y = rr[rr.index.year == Y]; xs.append(x); rs.append(y); ds.append(x * k - y)
    x, y, d = pd.concat(xs), pd.concat(rs), pd.concat(ds)
    return dict(SR=srx(x), ref_SR=srx(y), bp=x.mean() * 1e4, ref_bp=y.mean() * 1e4, d_rm_bp=d.mean() * 1e4, t_rm=h.nw_t(d),
                yearly={Y: (round(srx(x[x.index.year == Y]), 2), round(srx(y[y.index.year == Y]), 2)) for Y in YEARS})
