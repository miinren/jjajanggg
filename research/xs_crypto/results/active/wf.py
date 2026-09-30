import sys, glob, pickle, csv, numpy as np, pandas as pd
sys.path.insert(0, "/root/work"); import cloud_harness as h
base = pickle.load(open("res/base.pkl", "rb")); B = (base["B"], None)
d = {f.split("/")[-1][:-4]: pickle.load(open(f, "rb"))["df"] for f in glob.glob("res/A*.pkl")}
fams = dict(HYB=["A01", "A02"], VZ=["A03", "A04"], HALF=["A06", "A07"], TRAIL=["A08", "A09", "A10"], RANKS=["A11", "A12"],
            TIME=["A14", "A15"], SQZ=["A16", "A17"], REDEPLOY=["A18", "A19"], BRAKE=["A21", "A22"], LSTOP=["A24", "A25", "A26"],
            SSTOP=["A28", "A29"], BAN=["A27"], ALL_ACTIVE=sorted(d))
rows = []
for k, names in fams.items():
    for incl in (False, True):
        fam = {n: (d[n], None) for n in names}
        if incl: fam["B"] = B
        if len(fam) < 2: continue
        w = h.walk_forward(fam, B)
        rows.append(dict(family=k, includes_B=incl, n=len(fam), wf_SR=round(w["wf_SR"], 3), base_SR=round(w["base_SR"], 3), t_vs_B=round(w["tNW_vs_base"], 2),
                         beats_B=w["wf_SR"] > w["base_SR"], picks=w["picks"]))
R = pd.DataFrame(rows); print(R.to_string()); R.to_csv("walkforward.csv", index=False)
