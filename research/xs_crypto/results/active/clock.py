import sys, pickle, gc, numpy as np, pandas as pd
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/active")
from common import *
import ext_active as ea
BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
sr = lambda x: x.mean() / x.std() * np.sqrt(365)
acc = {"B": [None, None], "A18": [None, None]}; per = []
for off in range(8):
    for k, kw in (("B", {}), ("A18", dict(redeploy="next"))):
        c = ea.book(D, S0, offset=off, **BK, **kw)
        acc[k][0] = c[0] / 8 if acc[k][0] is None else acc[k][0] + c[0] / 8
        acc[k][1] = c[1] / np.float32(8) if acc[k][1] is None else acc[k][1] + c[1] / np.float32(8)
        per.append(dict(off=off, book=k, SR=sr(cut(c[0].net)))); del c; gc.collect()
    print(per[-2:], flush=True)
p = h.partition_test(D, tuple(acc["A18"]), tuple(acc["B"]), verbose=True)
print("8clock avg SR B", sr(cut(acc["B"][0].net)), "A18", sr(cut(acc["A18"][0].net)), stats(acc["A18"][0]))
avg = {k: v[0] for k, v in acc.items()}; del acc; gc.collect()
grid = []
for off in range(8):
    for stp in (0.15, 0.2, 0.25, 0.3):
        c = ea.book(D, S0, offset=off, **{**BK, "stop": stp}); grid.append(dict(off=off, stop=stp, SR=sr(cut(c[0].net)))); del c
G = pd.DataFrame(grid).pivot(index="off", columns="stop", values="SR"); print(G.round(2).to_string()); print("mean", G.mean().round(3).to_dict())
pickle.dump(dict(per=per, p=p, avg=avg, grid=G), open("clock.pkl", "wb"))
