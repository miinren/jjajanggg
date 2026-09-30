import sys, os, gc, pickle, time, hashlib, json, numpy as np, pandas as pd
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/wave3a")
from common import D, S0, stats, cut, h, ST
import ext4
OUT = "/root/work/results/wave3a"; CACHE = f"{OUT}/cache"
iv = D.idio(336).to_numpy(); RS = np.nan_to_num(D.resid.to_numpy())
DAYB = np.unique(D.idx.floor("D"), return_index=True)[1]
# 24h quote volume ($M) -> IQ = 1/sqrt(vol); funding with same-day stamp (Fh2)
_z = np.load(h.NPZ, allow_pickle=True)
_Q = pd.DataFrame(_z["quote_volume"], index=D.idx, columns=D.cols).astype(np.float32)
V24 = (_Q.rolling(24, min_periods=1).sum() / 1e6).to_numpy(np.float32); del _Q
IQ = (1 / np.sqrt(np.clip(np.nan_to_num(V24, nan=0.5), 0.5, None))).astype(np.float32)
_Fd = pd.DataFrame(_z["funding_1d"], index=pd.to_datetime(_z["days"]), columns=D.cols).astype(float)
Fh2 = (_Fd.reindex(D.idx.floor("D")).set_axis(D.idx).shift(-2).fillna(0) / 24).to_numpy(np.float32)
del _z, _Fd; gc.collect()

def W_equal(sf): return None
def W_invvol(sf):
    def f(i, longs, shorts):
        a = 1 / np.maximum(iv[i, shorts], 1e-5); a = np.nan_to_num(a, nan=np.nanmean(a)); e = 1 / len(shorts)
        x = np.clip(a / a.sum(), 0.5 * e, 2 * e); x /= x.sum()
        return np.full(len(longs), (1 - sf) / len(longs)), sf * x
    return f
def W_minvar_floor(sf):   # = wave2 minvar (shrink .5, cap 2e) then floor 0.4e (s3_floor.py), scaled to sf
    def f(i, longs, shorts):
        wl = np.full(len(longs), (1 - sf) / len(longs)); e = 1 / max(1, len(shorts))
        if len(shorts) < 2: return wl, np.full(len(shorts), sf * e)
        X = RS[max(0, i - 335):i + 1][:, shorts]; C = np.cov(X.T); C = 0.5 * C + 0.5 * np.diag(np.diag(C))
        try: x = np.linalg.solve(C + 1e-10 * np.eye(len(shorts)), np.ones(len(shorts)))
        except np.linalg.LinAlgError: x = np.ones(len(shorts))
        x = np.maximum(x, 0); x = x / x.sum() if x.sum() > 0 else np.full(len(shorts), e)
        for _ in range(5): x = np.minimum(x, 2 * e); x /= x.sum()
        for _ in range(10): x = np.clip(x, 0.4 * e, 2 * e); x /= x.sum()
        return wl, sf * x
    return f
WF = {"equal": W_equal, "invvol": W_invvol, "minvar_floor": W_minvar_floor}

def key(cfg): return "sf{sf}_st{st}_N{N}_NS{NS}_{w}".format(**cfg)
LIVE = dict(sf=0.5, st=0.4, N=20, NS=20, w="equal")
Bc = dict(sf=0.55, st=0.2, N=12, NS=20, w="equal")
BMV = dict(Bc, w="minvar_floor")

def run(cfg, verbose=True):
    """8-clock-averaged book for cfg, cached. Returns (daily df, daily per-coin gross pnl float32)."""
    p = f"{CACHE}/{key(cfg)}.pkl"
    if os.path.exists(p): return pickle.load(open(p, "rb"))
    t0 = time.time(); df = cm = None
    for off in range(8):
        d, c = ext4.book(D, S0, short_frac=cfg["sf"], stop=cfg["st"], N=cfg["N"], NS=cfg["NS"], leg_weights=WF[cfg["w"]](cfg["sf"]),
                         offset=off, IQ=IQ, Fh2=Fh2, dayb=DAYB)
        df = d / 8 if df is None else df + d / 8; cm = c / np.float32(8) if cm is None else cm + c / np.float32(8)
        del c; gc.collect()
    df = df[df.index >= ST]; cm = cm[-len(df):] if len(cm) != len(df) else cm
    pickle.dump((df, cm), open(p, "wb"))
    if verbose: print("ran", key(cfg), "SR %.3f" % srx(cut(df.net)), "%.0fs" % (time.time() - t0), flush=True)
    return df, cm

def srx(x): return x.mean() / x.std() * np.sqrt(365)
GROUPS = np.array_split(np.random.default_rng(7).permutation(len(D.cols)), 5)
BTC30 = D.rb.resample("D").sum().rolling(30).sum().shift(1)

def win(df, cm, a, b):
    m = (df.index >= a) & (df.index < b); return df[m], cm[np.asarray(m)]

def ptest(cand, base, a, b):
    """harness partition_test restricted to [a,b): risk-matched on the window; years rule = at most one losing year."""
    (dc, cc), (db, cb) = win(*cand, a, b), win(*base, a, b)
    k = db.net.std() / dc.net.std(); dd = dc.net * k - db.net
    yrs = dd.groupby(dd.index.year).mean(); ny = len(yrs); yw = int((yrs > 0).sum())
    grp = [float(cc[:, g].sum() * k - cb[:, g].sum()) for g in GROUPS]; gw = sum(x > 0 for x in grp)
    r30 = BTC30.reindex(dd.index); up, dn = dd[r30 > 0].mean(), dd[r30 <= 0].mean(); t = h.nw_t(dd)
    return dict(t=t, years=f"{yw}/{ny}", groups=f"{gw}/5", up=up * 1e4, dn=dn * 1e4, diff_bp=dd.mean() * 1e4,
                ok=bool(yw >= ny - 1 and gw >= 4 and up > 0 and dn > 0 and t >= 1.5))

def wstats(df, a, b, net=None):
    x = (df.net if net is None else net); x = x[(x.index >= a) & (x.index < b)]; cum = x.cumsum(); k = 0.02 / x.std()
    return dict(SR=srx(x), bp=x.mean() * 1e4, mdd_bp=(cum - cum.cummax()).min() * 1e4, mdd2=(k * cum - (k * cum).cummax()).min() * 100)

TRIALS = f"{OUT}/trials.csv"
COLS = ["id","task","name","params","window","SR","bp_day","mdd2","t_vs_LIVE","years","groups","regime_up_dn","pass_vs_LIVE","note"]
def log(row):
    new = not os.path.exists(TRIALS)
    pd.DataFrame([row]).reindex(columns=COLS).to_csv(TRIALS, mode="a", header=new, index=False)
