"""wave3b helpers. Copies of wave2/lib.py pieces, parameterised minvar_floor, B-MV reference, evaluation vs B-MV."""
import sys, os, gc, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/wave3b")
from common import D, S0, IDIO_RAW, stats, cut, h, ST
import ext3b
OUT = "/root/work/results/wave3b"
BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
RS = np.nan_to_num(D.resid.to_numpy())
pI336 = IDIO_RAW.where(D.M).rank(1, pct=True)
pF = D.F.where(D.M).rank(1, pct=True).fillna(0.5)
def score_fw(fw, pI=None):
    pI = pI336 if pI is None else pI
    return np.asarray(pI if fw == 0 else (1 - fw) * pI + fw * pF, dtype=float)

def make_mv(shrink=0.5, win=336, floor=0.4, cap=2.0, sf=0.55):
    """minvar_floor of wave2 (lib.minvar + s3_floor), parameterised. Defaults reproduce B-MV exactly."""
    def f(i, longs, shorts):
        wl = np.full(len(longs), (1 - sf) / len(longs))
        if len(shorts) < 2: return wl, np.full(len(shorts), sf / max(1, len(shorts)))
        X = RS[max(0, i - win + 1):i + 1][:, shorts]; C = np.cov(X.T); C = (1 - shrink) * C + shrink * np.diag(np.diag(C)); e = 1 / len(shorts)
        try: x = np.linalg.solve(C + 1e-10 * np.eye(len(shorts)), np.ones(len(shorts)))
        except np.linalg.LinAlgError: x = np.ones(len(shorts))
        x = np.maximum(x, 0); x = x / x.sum() if x.sum() > 0 else np.full(len(shorts), e)
        for _ in range(5): x = np.minimum(x, cap * e); x /= x.sum()
        for _ in range(10): x = np.clip(x, floor * e, cap * e); x /= x.sum()
        return wl, sf * x
    return f
MV = make_mv()

def avg8(score=None, keep_coin=True, bk=None, **kw):
    score = S0 if score is None else score
    b = dict(BK, **(bk or {})); df = cm = None
    for off in range(8):
        d, c = ext3b.book(D, score, offset=off, **b, **kw)
        df = d / 8 if df is None else df + d / 8
        if keep_coin: cm = c / np.float32(8) if cm is None else cm + c / np.float32(8)
        del c; gc.collect()
    return df, cm

def srx(x): return x.mean() / x.std() * np.sqrt(365)
def sr_at(df, c): return srx(cut(df.net + df.to * (h.COST - c * 1e-4)))
def risk(df, vref):
    x = cut(df.net); x = x * (vref / x.std()); q = x.quantile(0.05); cum = x.cumsum()
    return dict(cvar5=-x[x <= q].mean() * 1e4, cvar1=-x[x <= x.quantile(0.01)].mean() * 1e4, w20=-x.rolling(20).sum().min() * 1e4, mdd=-(cum - cum.cummax()).min() * 1e4)

def load_ref():
    p = f"{OUT}/BMV.pkl"
    if not os.path.exists(p):
        df, cm = avg8(leg_weights=MV); np.save(f"{OUT}/coin_BMV.npy", cm); pickle.dump(df, open(p, "wb")); return df, cm
    return pickle.load(open(p, "rb")), np.load(f"{OUT}/coin_BMV.npy")

def evaluate(name, df, cm, ref):
    dB, cB = ref; vref = cut(dB.net).std()
    st = stats(df); r = h.partition_test(D, (df, cm), (dB, cB), verbose=False); rk, rb = risk(df, vref), risk(dB, vref)
    yr = cut(df.net).groupby(cut(df.net).index.year).apply(srx).round(2).to_dict()
    out = dict(name=name, SR=st["SR"], SR8=sr_at(df, 8), SR12=sr_at(df, 12), t=r["tNW"], years=r["years_won"], groups=r["coin_groups_won"],
               up=r["regime_btc_up_bp"], dn=r["regime_btc_down_bp"], adopt=r["adopt"], mdd2=st["mdd_at2pct"], minYr=st["minYrSR"],
               cvar5=rk["cvar5"], dCVaR=rb["cvar5"] - rk["cvar5"], cvar1=rk["cvar1"], w20=rk["w20"], yearly=yr,
               long_bp=cut(df.long).mean() * 1e4, short_bp=cut(df.short).mean() * 1e4, hedge_bp=cut(df.hedge).mean() * 1e4, to=cut(df.to).mean(),
               year_diffs=r["year_diffs_bp"], grp=r["coin_group_diffs"])
    print(f"{name:22s} SR {out['SR']:.2f} @8 {out['SR8']:.2f} @12 {out['SR12']:.2f} t {out['t']:+.2f} yrs {out['years']} grp {out['groups']} "
          f"reg {out['up']:+.1f}/{out['dn']:+.1f} adopt {out['adopt']} mdd2 {out['mdd2']:.1f} minYr {out['minYr']:.2f} CVaR5 {out['cvar5']:.1f} dCVaR {out['dCVaR']:+.1f} "
          f"L/S/H {out['long_bp']:.1f}/{out['short_bp']:.1f}/{out['hedge_bp']:.1f} to {out['to']:.2f}", flush=True)
    print("   yearly", yr, "ydiff", out["year_diffs"], flush=True)
    return out
