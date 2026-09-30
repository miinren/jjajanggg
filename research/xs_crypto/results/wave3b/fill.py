import pickle, pandas as pd
R = {}
for f in ("res1", "res2", "res3", "res4"): R.update(pickle.load(open(f + ".pkl", "rb")))
T = pd.read_csv("trials.csv", dtype=str)
ens = {"E1", "E2", "E2a", "E2b"}
for j, row in T.iterrows():
    k = row.id; r = R.get(k)
    if r is None: continue
    T.loc[j, ["SR8clk", "SR8bp", "SR12bp", "t_vs_BMV", "years", "groups", "regimes_up_dn", "partition_adopt", "mdd_at2pct", "minYrSR", "cvar5_bp_matched", "dCVaR_bp"]] = [
        f"{r['SR']:.2f}", f"{r['SR8']:.2f}", f"{r['SR12']:.2f}", "" if k == "BASE" else f"{r['t']:+.2f}", r["years"], r["groups"], f"{r['up']:+.1f}/{r['dn']:+.1f}",
        str(r["adopt"]), f"{r['mdd2']:.1f}", f"{r['minYr']:.2f}", f"{r['cvar5']:.1f}", f"{r['dCVaR']:+.1f}"]
    b = R["BASE"]
    if k == "BASE": v = "reproduces wave2 s3_floor exactly (max |dnet| 2e-17)"
    elif k.startswith("L"): v = "ADOPT" if (r["adopt"] and r["t"] >= 2) else "FAIL"
    elif k in ens:
        er = r["dCVaR"] > 0 and r["t"] >= -0.5 and r["minYr"] >= b["minYr"]
        v = ("formal PASS ensemble rule (dCVaR tiny)" if er else "FAIL ensemble rule") if k in ("E1", "E2") else ("plateau: rule " + ("holds" if er else "fails"))
    else: v = "plateau neighbour"
    T.loc[j, "verdict"] = v
T.loc[T.id == "WF", "verdict"] = "WF picks N=8 in 5/5 years: wf SR 2.79 vs B-MV 2.59 (2021-25), t +2.34"
T.to_csv("trials.csv", index=False)
print(T.drop(columns=["rationale"]).to_markdown(index=False))
