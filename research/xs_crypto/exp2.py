import time, pickle, numpy as np, pandas as pd
from multiprocessing import Pool
from common import *
BASE = ext.book(D, S0)
C = {}
for sf in [0.55, 0.6, 0.65, 0.7, 0.8, 1.0]: C[f"sf{sf}"] = dict(short_frac=sf)
for st in [0.15, 0.2, 0.25, 0.3, 0.4, 0.6]: C[f"sstop{st}"] = dict(stop=st)
for nl in [8, 12, 16, 20]: C[f"NL{nl}_NS20"] = dict(N=nl, NS=20)
for nl in [8, 12, 16, 20]: C[f"NL{nl}_NS15"] = dict(N=nl, NS=15)
C["combo_sf0.6_ss0.2"] = dict(short_frac=0.6, stop=0.2)
C["combo_sf0.6_ss0.2_NL12"] = dict(short_frac=0.6, stop=0.2, N=12, NS=20)
def run(name):
    c = ext.book(D, S0, **C[name]); r = h.partition_test(D, c, BASE, verbose=False); r.update(stats(c[0])); return name, r, c[0]
if __name__ == "__main__":
    with Pool(4) as p: out = p.map(run, list(C))
    res = {n: (r, d) for n, r, d in out}
    pickle.dump(res, open("exp2.pkl", "wb"))
    df = pd.DataFrame([dict(name=n, SR=r["SR"], bp=r["bp"], vol=r["vol_bp"], mdd2=r["mdd_at2pct"], calmar=r["calmar"], minYr=r["minYrSR"], tNW=r["tNW"], yrs=r["years_won"], grp=r["coin_groups_won"], up=r["regime_btc_up_bp"], dn=r["regime_btc_down_bp"], adopt=r["adopt"]) for n, r, d in out]).set_index("name")
    print(df.round(2).to_string())
    base = (BASE[0], None)
    for fam in ["sf", "sstop", "NL"]:
        F = {n: (res[n][1], None) for n in res if n.startswith(fam)}
        if fam == "sf": F["sf0.5"] = base
        if fam == "sstop": F["sstop0.4"] = base
        wf = h.walk_forward(F, base); print(fam, wf)
    for n in ["sf0.6", "sstop0.2", "NL12_NS20", "combo_sf0.6_ss0.2"]:
        print(n, res[n][0]["year_diffs_bp"], res[n][0]["coin_group_diffs"])
