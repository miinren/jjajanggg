import time; t0 = time.time()
from w3lib import *
ref = load_ref(); R = {}
def idio_score(L):
    e = D.resid; el = e.shift(1); mp = int(0.6 * L)
    PHI = ((e * el).rolling(L, min_periods=mp).mean() / (el * el).rolling(L, min_periods=mp).mean()).clip(-0.5, 0.5)
    EC = e - PHI * el; del PHI, el; gc.collect()
    I = EC.rolling(L, min_periods=mp).std(); del EC; gc.collect()
    pI = I.where(D.M).rank(1, pct=True); del I; gc.collect()
    S = np.asarray(0.75 * pI + 0.25 * pF, dtype=np.float32); del pI; gc.collect(); return S
# sanity: idio_score(336) must equal S0
S336 = idio_score(336); print("S336 vs S0 max diff", np.nanmax(np.abs(S336 - np.asarray(S0, np.float32))), "nan mismatch", int((np.isnan(S336) != np.isnan(np.asarray(S0))).sum()), flush=True); del S336
comp = {336: ref}
for L in (168, 720):
    S = idio_score(L); df, cm = avg8(score=S, leg_weights=MV); del S; gc.collect()
    R[f"L{L}"] = evaluate(f"comp L={L}", df, cm, ref); R[f"L{L}"]["df"] = df
    comp[L] = (df, cm); print(time.time() - t0, flush=True)
dfE = sum(comp[L][0] for L in (168, 336, 720)) / 3
cmE = comp[168][1] / np.float32(3); cmE += comp[336][1] / np.float32(3); cmE += comp[720][1] / np.float32(3)
del comp; gc.collect()
R["E1"] = evaluate("E1 ens L", dfE, cmE, ref); R["E1"]["df"] = dfE
R["E1"]["corr"] = None; del cmE; gc.collect()
comp = {12: ref}
for N in (8, 16):
    df, cm = avg8(bk=dict(N=N), leg_weights=make_mv())
    R[f"N{N}"] = evaluate(f"comp N={N}", df, cm, ref); R[f"N{N}"]["df"] = df; comp[N] = (df, cm); print(time.time() - t0, flush=True)
dfE = sum(comp[N][0] for N in (8, 12, 16)) / 3
cmE = comp[8][1] / np.float32(3); cmE += comp[12][1] / np.float32(3); cmE += comp[16][1] / np.float32(3)
del comp; gc.collect()
R["E2"] = evaluate("E2 ens N", dfE, cmE, ref); R["E2"]["df"] = dfE
pickle.dump(R, open(f"{OUT}/res2.pkl", "wb")); print("done", time.time() - t0)
