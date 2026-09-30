# Part 2: universe breadth. Score + elig rebuilt within the new mask. Records held names at offset 0 for liquidity/notional.
from lib import *
t0 = time.time()
z = np.load(h.NPZ, allow_pickle=True)
Q24 = pd.DataFrame(z["quote_volume"], index=D.idx, columns=D.cols).astype(float).rolling(24).sum().to_numpy(np.float32); del z
LQ = D.lq.to_numpy(np.float32)
def mk_score(Mx):
    pI = IDIO_RAW.where(Mx).rank(1, pct=True); pF = D.F.where(Mx).rank(1, pct=True).fillna(0.5); return 0.75 * pI + 0.25 * pF
assert (mk_score(D.U & (D.lq > 2 / 3)).fillna(-1).to_numpy() == S0.fillna(-1).to_numpy()).all(); print("S0 reproduced", flush=True)
REC = []
def recw(i, longs, shorts):
    REC.append((i, list(longs), list(shorts))); return np.full(len(longs), 0.45 / len(longs)), np.full(len(shorts), 0.55 / len(shorts))
def held_stats():
    ls, ss = [], []
    for i, l, s in REC:
        ls += [(Q24[i, c], LQ[i, c]) for c in l]; ss += [(Q24[i, c], LQ[i, c]) for c in s]
    L, S = np.array(ls), np.array(ss)
    return dict(long_medQ24=float(np.nanmedian(L[:, 0])), long_p10Q24=float(np.nanpercentile(L[:, 0], 10)), long_medlq=float(np.nanmedian(L[:, 1])),
                short_medQ24=float(np.nanmedian(S[:, 0])), short_p10Q24=float(np.nanpercentile(S[:, 0], 10)), short_medlq=float(np.nanmedian(S[:, 1])),
                n_long=np.mean([len(l) for _, l, _ in REC]), n_short=np.mean([len(s) for _, _, s in REC]))
res = {}
cfgs = [("B", 2 / 3, False), ("U50", 0.5, False), ("U60", 0.6, False), ("U75", 0.75, False), ("SPLIT", 0.5, True)]
for k, thr, split in cfgs:
    Mx = D.U & (D.lq > thr); sc = mk_score(Mx); lo = D.M.to_numpy() if split else None
    REC.clear(); d0, _ = ext3.book(D, sc, offset=0, elig=Mx, long_ok=lo, leg_weights=recw, **BK); hs = held_stats(); del _
    per = {}; df, cm = avg8(score=sc, elig=Mx, long_ok=lo, per_offset=per)
    np.save(f"{OUT}/coin2_{k}.npy", cm); del cm, sc, Mx; gc.collect()
    res[k] = dict(df=df, per=per, held=hs, check_off0_SR=stats(d0)["SR"]); print(k, round(stats(df)["SR"], 3), hs, round(time.time() - t0), flush=True)
pickle.dump(res, open(f"{OUT}/s2.pkl", "wb")); print("done", time.time() - t0)
