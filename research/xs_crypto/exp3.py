import pickle, itertools, numpy as np, pandas as pd
from multiprocessing import Pool
from common import *
BASE = ext.book(D, S0)
G = {(sf, ss, nl): dict(short_frac=sf, stop=ss, N=nl, NS=20) for sf, ss, nl in itertools.product([0.55, 0.6, 0.65], [0.15, 0.2, 0.25], [8, 12, 16])}
G[("5050", 0.4, 8)] = dict(N=8, NS=20)
def run(k):
    c = ext.book(D, S0, **G[k]); r = h.partition_test(D, c, BASE, verbose=False); r.update(stats(c[0])); return k, r, c[0]
if __name__ == "__main__":
    with Pool(4) as p: out = p.map(run, list(G))
    res = {k: (r, d) for k, r, d in out}; pickle.dump(res, open("exp3.pkl", "wb"))
    df = pd.DataFrame([dict(sf=k[0], ss=k[1], nl=k[2], SR=r["SR"], mdd2=r["mdd_at2pct"], minYr=r["minYrSR"], tNW=r["tNW"], yrs=r["years_won"], grp=r["coin_groups_won"], adopt=r["adopt"]) for k, r, d in out])
    print(df.round(2).to_string())
    print("grid SR min/median/max", df.SR.min().round(2), df.SR.median().round(2), df.SR.max().round(2), "adopt", df.adopt.sum(), "/", len(df))
