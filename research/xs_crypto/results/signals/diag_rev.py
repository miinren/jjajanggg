# DIAGNOSTIC: why does the hourly residual-reversal sleeve lose money despite a positive rank IC?
import sys, pickle; sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/signals")
import numpy as np, pandas as pd
S = pickle.load(open("sleeves.pkl", "rb"))
for k in ("rev3_h1", "rev6_h2", "rev6_h4"):
    df = S[k]["sleeve_df"]; df = df[df.index >= "2020-03-15"]
    print(k, {c: round(df[c].mean() * 1e4, 1) for c in ["net", "long", "short", "hedge", "fund", "to"]}, "gross bp/day", round((df.net + df.to * 5.5e-4).mean() * 1e4, 1))
import cloud_harness as h
D = h.Data(); e = D.resid; sig = e.rolling(3).sum().where(D.M); f = D.R1.shift(-2).where(D.M)
f = f.sub(f.mean(1), axis=0)   # xs-demeaned raw return at i+2 (what an equal-$ leg earns before hedge)
q = sig.rank(1, pct=True); hi = q.index >= "2020-03-15"
for lo_, hi_ in ((0, .05), (.05, .2), (.2, .4), (.4, .6), (.6, .8), (.8, .95), (.95, 1.01)):
    m = (q >= lo_) & (q < hi_)
    print(f"rev3 pct [{lo_:.2f},{hi_:.2f}) mean xs-demeaned R(i+2) bp/h: {f[m][hi].stack().mean()*1e4:+.3f}")
