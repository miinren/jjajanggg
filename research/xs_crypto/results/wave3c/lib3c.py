"""wave3c shared setup: B-MV base, 8-clock averaging on ext4, short-horizon features (all causal: row i uses data <= i)."""
import sys, os, gc, pickle, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/wave2"); sys.path.insert(0, HERE)
from common import D, S0, stats, cut, h, ST
from lib import minvar, srx, sr_at, BK          # BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
import ext3, ext4
OUT = "/root/work/out3c"; os.makedirs(OUT, exist_ok=True)

def minvar_floor(i, longs, shorts):             # = results/wave2/s3_floor.py minus the CV bookkeeping
    a, b = minvar(i, longs, shorts); x = b / 0.55; e = 1 / len(shorts)
    for _ in range(10): x = np.clip(x, 0.4 * e, 2 * e); x /= x.sum()
    return a, 0.55 * x

def avg8(engine=ext4, per_offset=None, keep_coin=True, **kw):
    df = cm = None
    for off in range(8):
        d, c = engine.book(D, S0, offset=off, leg_weights=minvar_floor, **BK, **kw)
        if per_offset is not None: per_offset[off] = d
        df = d / 8 if df is None else df + d / 8
        if keep_coin: cm = c / np.float32(8) if cm is None else cm + c / np.float32(8)
        del c; gc.collect()
    return df, cm

def base():
    p = f"{OUT}/BMV.pkl"
    if os.path.exists(p):
        o = pickle.load(open(p, "rb")); return o["df"], np.load(f"{OUT}/BMV_coin.npy"), o["per"]
    per = {}; df, cm = avg8(per_offset=per); pickle.dump(dict(df=df, per=per), open(p, "wb")); np.save(f"{OUT}/BMV_coin.npy", cm)
    return df, cm, per

# ---- hourly features (numpy, T x K) ----
RS = np.nan_to_num(D.resid.to_numpy())
CS = np.cumsum(RS, axis=0)
def rsum(j, c, n):                                # residual summed over rows j-n+1..j (data <= j)
    return CS[j, c] - (CS[j - n, c] if j - n >= 0 else 0.0)
SIGH = D.idio(168).shift(1).to_numpy()            # hourly idio std known before row i
