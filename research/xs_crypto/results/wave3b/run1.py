import time; t0 = time.time()
from w3lib import *
ref = load_ref(); R = {"BASE": evaluate("BASE B-MV", ref[0], ref[1], ref)}
old = pickle.load(open("/root/work/results/wave2/s3_floor.pkl", "rb"))["df"]
print("check vs wave2 s3_floor: max|dnet|", float((old.net - ref[0].net).abs().max()), "old SR", stats(old)["SR"], time.time() - t0, flush=True)
for nm, fl, fs in (("L1", 0, 0.25), ("L2", 0, 0.40), ("L3", 0.25, 0.40)):
    SL = score_fw(fl); SSh = score_fw(fs)
    df, cm = avg8(score=SL, score_short=SSh, leg_weights=MV)
    R[nm] = evaluate(nm, df, cm, ref); R[nm]["df"] = df; del cm, SL, SSh; gc.collect()
    print(time.time() - t0, flush=True)
pickle.dump(R, open(f"{OUT}/res1.pkl", "wb"))
