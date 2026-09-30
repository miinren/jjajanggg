import time; t0 = time.time()
from w3lib import *
ref = load_ref(); R = {}; R2 = pickle.load(open(f"{OUT}/res2.pkl", "rb"))
dfs = {12: ref[0], 8: R2["N8"]["df"], 16: R2["N16"]["df"]}; cms = {}
for N in (6, 10, 14, 18):
    df, cm = avg8(bk=dict(N=N), leg_weights=MV); dfs[N] = df; cms[N] = cm
    R[f"N{N}"] = evaluate(f"comp N={N}", df, cm, ref); R[f"N{N}"]["df"] = df; print(time.time() - t0, flush=True)
for nm, Ns in (("E2a", (6, 12, 18)), ("E2b", (10, 12, 14))):
    dfE = sum(dfs[N] for N in Ns) / 3
    cmE = ref[1] / np.float32(3)
    for N in Ns:
        if N != 12: cmE += cms[N] / np.float32(3)
    R[nm] = evaluate(f"{nm} ens N{Ns}", dfE, cmE, ref); R[nm]["df"] = dfE; del cmE; gc.collect()
del cms; gc.collect()
fam = {N: (dfs[N], None) for N in (8, 12, 16)}
print("WF {8,12,16}", h.walk_forward(fam, ref)); R["WF3"] = h.walk_forward(fam, ref)
fam = {N: (dfs[N], None) for N in sorted(dfs)}
R["WF7"] = h.walk_forward(fam, ref); print("WF {6..18}", R["WF7"])
for N in sorted(dfs): print(N, "SR %.2f" % stats(dfs[N])["SR"])
pickle.dump(R, open(f"{OUT}/res4.pkl", "wb")); print("done", time.time() - t0)
