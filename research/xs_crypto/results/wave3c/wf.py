# Walk-forward over each pre-registered parameter family (8-clock-averaged daily dfs), base = B-MV.
import sys, pickle, pandas as pd
sys.path.insert(0, "/root/work")
import cloud_harness as h
OUT = "/root/work/out3c"
B = pickle.load(open(f"{OUT}/BMV.pkl", "rb"))["df"]
FAM = {"TWAP": ["E01", "E02", "E03"], "SE_delay": ["E05", "E06", "E07"], "VOLSPIKE_both": ["V04", "V01", "V05"],
       "JUMP_both": ["V09", "V06", "V10"], "EXEC_menu_all": [f"E{i:02d}" for i in range(1, 14)],
       "FILTER_menu_all": [f"V{i:02d}" for i in range(1, 12)]}
rows = []
for k, ids in FAM.items():
    fam = {i: (pickle.load(open(f"{OUT}/{i}.pkl", "rb"))["df"], None) for i in ids}
    fam_b = dict(fam, BMV=(B, None))            # menu including 'stay with B-MV'
    for lab, f in ((k, fam), (k + "+BMV", fam_b)):
        r = h.walk_forward(f, (B, None)); rows.append(dict(family=lab, wf_SR=round(r["wf_SR"], 3), base_SR=round(r["base_SR"], 3),
                                                        t=round(r["tNW_vs_base"], 2), picks=" ".join(f"{y}:{p}" for y, p in r["picks"].items())))
out = pd.DataFrame(rows); out.to_csv("walkforward.csv", index=False); print(out.to_string(index=False))
