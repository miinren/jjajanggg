import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/drawdown")
from common import *
import ext2
cfg = {"LIVE": {}, "B": dict(short_frac=0.55, stop=0.2, N=12, NS=20), "A_8L20S": dict(N=8, NS=20), "sstop0.2": dict(stop=0.2), "sf0.55": dict(short_frac=0.55)}
acc = {}; rows = []
for off in range(8):
    for k, kw in cfg.items():
        c = ext2.book(D, S0, offset=off, **kw)
        s = stats(c[0]); rows.append(dict(off=off, cfg=k, SR=s["SR"], mdd2=s["mdd_at2pct"], minYr=s["minYrSR"]))
        cm = c[1] if k in ("LIVE", "B") else np.zeros((1, 1), np.float32)
        if k not in acc: acc[k] = [c[0].copy(), cm.copy()]
        else: acc[k][0] += c[0]; acc[k][1] += cm
        del c
    print(off, flush=True)
df = pd.DataFrame(rows); print(df.pivot(index="off", columns="cfg", values="SR").round(2).to_string())
for k in cfg: acc[k][0] /= 8; acc[k][1] /= 8
L = tuple(acc["LIVE"])
out = {}
for k in cfg:
    s = stats(acc[k][0]); cn, ln = cut(acc[k][0].net), cut(acc["LIVE"][0].net)
    r = h.partition_test(D, tuple(acc[k]), L, verbose=False) if k == "B" else ({"tNW": h.nw_t(cn * ln.std() / cn.std() - ln)} if k != "LIVE" else {})
    out[k] = (s, r); print(k, "8-clock avg SR %.2f mdd2 %.1f minYr %.2f" % (s["SR"], s["mdd_at2pct"], s["minYrSR"]), "| vs LIVE t %.2f yrs %s grp %s adopt %s" % (r.get("tNW", np.nan), r.get("years_won"), r.get("coin_groups_won"), r.get("adopt")) if r else "")
# per-clock paired t of B vs LIVE
for off in range(8):
    pass
pickle.dump(dict(rows=rows, out=out), open("clock.pkl", "wb"))
