import pickle, numpy as np, pandas as pd
from multiprocessing import Pool
from common import *
B = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
C = {"B": {}}
for ev in [1, 2, 4, 6, 12]: C[f"every{ev}"] = dict(every=ev)
for tp in [0.15, 0.25, 0.4]: C[f"tpS{tp}"] = dict(tp_short=tp)
for tp in [0.15, 0.3]: C[f"tpL{tp}"] = dict(tp_long=tp)
C["every4_keepx1"] = dict(every=4, keepx=1.0)
def run(k):
    return k, ext.book(D, S0, **{**B, **C[k]})
if __name__ == "__main__":
    with Pool(4) as p: out = dict(p.map(run, list(C)))
    LIVE = ext.book(D, S0); base = out["B"]
    rows = []
    for k, c in out.items():
        if k == "B": continue
        r = h.partition_test(D, c, base, verbose=False); r2 = h.partition_test(D, c, LIVE, verbose=False); st = stats(c[0])
        rows.append(dict(name=k, SR=st["SR"], mdd2=st["mdd_at2pct"], minYr=st["minYrSR"], to=cut(c[0].to).mean(), SR12bp=(lambda x: x.mean()/x.std()*np.sqrt(365))(cut(c[0].net + c[0].to*(5.5e-4-12e-4))), t_vsB=r["tNW"], yrs=r["years_won"], grp=r["coin_groups_won"], adopt_vsB=r["adopt"], t_vsLive=r2["tNW"]))
    sb = stats(base[0]); print("B", round(sb["SR"], 2), round(sb["mdd_at2pct"], 1), round(cut(base[0].to).mean(), 2))
    print(pd.DataFrame(rows).set_index("name").round(2).to_string())
