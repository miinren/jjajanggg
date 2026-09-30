import time; t0 = time.time()
from w3lib import *
ref = load_ref(); R = {}
P = {"P1": dict(shrink=0.25), "P2": dict(shrink=0.75), "P3": dict(win=168), "P4": dict(win=720),
     "P5": dict(floor=0.3), "P6": dict(floor=0.5), "P7": dict(cap=1.5), "P8": dict(cap=3.0)}
for k, p in P.items():
    df, cm = avg8(leg_weights=make_mv(**p)); R[k] = evaluate(f"{k} {p}", df, cm, ref); R[k]["df"] = df; del cm; gc.collect()
    print(time.time() - t0, flush=True)
pickle.dump(R, open(f"{OUT}/res3.pkl", "wb")); print("done", time.time() - t0)
