import os, sys, time, pickle, gc, csv, numpy as np, pandas as pd
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/active")
from common import *
import ext_active as ea
BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
ids = sys.argv[1].split(",") if len(sys.argv) > 1 else None
rows = list(csv.DictReader(open("trials.csv")))
def parse(p):
    p = p.replace("redeploy=next", "redeploy='next'").replace("redeploy=scale", "redeploy='scale'")
    return eval(f"dict({p})")
B = ea.book(D, S0, **BK); LIVE = ea.book(D, S0)
sr = lambda x: x.mean() / x.std() * np.sqrt(365)
out = {"B": B[0], "LIVE": LIVE[0]}; res = {}
import os; os.makedirs("res", exist_ok=True); pickle.dump(dict(B=B[0], LIVE=LIVE[0]), open("res/base.pkl", "wb"))
def upd(rr):
    rows = list(csv.DictReader(open("trials.csv"))); flds = list(rows[0].keys())
    for q in rows:
        if q["id"] in rr:
            for k, v in rr[q["id"]].items(): q[k] = v
    w = csv.DictWriter(open("trials.csv", "w", newline=""), fieldnames=flds); w.writeheader(); w.writerows(rows)
for r in rows:
    if ids and r["id"] not in ids: continue
    if os.path.exists(f"res/{r['id']}.pkl"): continue
    kw = {**BK, **parse(r["params"])}; t = time.time()
    c = ea.book(D, S0, **kw)
    p = h.partition_test(D, c, B, verbose=False); pl = h.partition_test(D, c, LIVE, verbose=False); s = stats(c[0])
    df = c[0]
    res[r["id"]] = dict(SR=round(s["SR"], 3), bp=round(s["bp"], 2), t_vs_B=round(p["tNW"], 2), years=p["years_won"], groups=p["coin_groups_won"],
        regimes_up_dn=f"{p['regime_btc_up_bp']:.2f}/{p['regime_btc_down_bp']:.2f}", adopt=p["adopt"] and p["tNW"] >= 2.0,
        mdd_at2pct=round(s["mdd_at2pct"], 2), minYrSR=round(s["minYrSR"], 2), t_vs_LIVE=round(pl["tNW"], 2),
        SR8bp=round(sr(cut(df.net - df.to * 2.5e-4)), 2), SR12bp=round(sr(cut(df.net - df.to * 6.5e-4)), 2), turnover=round(cut(df.to).mean(), 3),
        note=f"yrdiff={p['year_diffs_bp']} grp={p['coin_group_diffs']} pt_adopt={p['adopt']}")
    out[r["id"]] = df
    pickle.dump(dict(df=df, res=res[r["id"]]), open(f"res/{r['id']}.pkl", "wb")); upd({r["id"]: res[r["id"]]})
    print(r["id"], r["name"], res[r["id"]], f"{time.time()-t:.0f}s", flush=True)
    del c; gc.collect()
tag = sys.argv[2] if len(sys.argv) > 2 else "run1"
pickle.dump(dict(dfs=out, res=res), open(f"{tag}.pkl", "wb"))
print("B", stats(B[0]))
