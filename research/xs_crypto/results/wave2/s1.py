# Part 1 trials: B, P1a minvar, P1b invvol on the 8-clock average (+ per-offset dfs); weights recorded for notional check
from lib import *
t0 = time.time(); W = {"minvar": [], "invvol": []}
def wrap(fn, key):
    def f(i, l, s):
        a, b = fn(i, l, s); W[key].append(b.copy()); return a, b
    return f
res = {}
for k, kw in (("B", {}), ("P1a_minvar", dict(leg_weights=wrap(minvar, "minvar"))), ("P1b_invvol", dict(leg_weights=wrap(invvol, "invvol")))):
    per = {}; df, cm = avg8(per_offset=per, **kw); res[k] = dict(df=df, per=per)
    np.save(f"{OUT}/coin_{k}.npy", cm); del cm; gc.collect(); print(k, stats(df)["SR"], time.time() - t0, flush=True)
res["W"] = {k: np.concatenate(v) for k, v in W.items()}
pickle.dump(res, open(f"{OUT}/s1.pkl", "wb")); print("done", time.time() - t0)
