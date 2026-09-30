import pickle, sys, csv, numpy as np, pandas as pd
sys.path.insert(0, "/root/work"); import cloud_harness as h
a = {}
for f in ["run1.pkl", "run2.pkl", "run3.pkl", "run4.pkl"]: a.update(pickle.load(open(f, "rb")))
B = (a["B"], None)
fam = {}
for r in csv.DictReader(open("trials.csv")):
    if r["family"] not in ("single",) and r["name"] in a: fam.setdefault(r["family"], []).append(r["name"])
fam["SHORT_RISKW"] = ["short_invvol", "short_minvar"] + fam["SHORT_RISKW"]
res = {}
for k, names in fam.items():
    w = h.walk_forward({n: (a[n], None) for n in names}, B); res[k] = w
    print(f"{k:12s} n={len(names)} wf_SR={w['wf_SR']:.2f} base_SR={w['base_SR']:.2f} t={w['tNW_vs_base']:.2f} picks={w['picks']}")
pickle.dump(res, open("wf.pkl", "wb"))
