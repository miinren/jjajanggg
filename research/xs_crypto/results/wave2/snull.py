# placebo null: random fixed-per-coin short weightings exp(sigma z), 8-clock average; args: kind lo hi
from lib import *
kind, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
SIG = {"mv": (0.859, None), "iv": (0.266, 0.5)}[kind]   # calibrated to minvar CV 0.604 / invvol CV 0.257 (n=20 draws)
t0 = time.time(); out = {}
for s in range(lo, hi):
    df, _ = avg8(keep_coin=False, leg_weights=placebo(SIG[0], s, SIG[1])); out[s] = df[["net", "to", "short"]]
    print(kind, s, round(stats(df)["SR"], 3), round(time.time() - t0), flush=True)
pickle.dump(out, open(f"{OUT}/null_{kind}_{lo}_{hi}.pkl", "wb"))
