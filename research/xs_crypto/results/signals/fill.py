import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/root/work")
T = pd.read_csv("trials.csv", dtype=str)
sc = pickle.load(open("scores.pkl", "rb")); sl = pickle.load(open("sleeves.pkl", "rb"))
g1 = pickle.load(open("gross.pkl", "rb")); g2 = pickle.load(open("gross2.pkl", "rb"))
B = pickle.load(open("B.pkl", "rb"))
s = lambda y: y.mean() / y.std() * np.sqrt(365)
cutf = lambda x: x[(x.index >= "2020-03-15") & (x.index < "2026-01-01")]
def row(df, pt, st, tl):
    return dict(SR=f"{st['SR']:.2f}", t_vs_B=f"{pt['tNW']:+.2f}", years=pt["years_won"], groups=pt["coin_groups_won"],
                regimes=f"{pt['regime_btc_up_bp']:+.1f}/{pt['regime_btc_down_bp']:+.1f}", adopt=str(pt["adopt"]),
                mdd_at2pct=f"{st['mdd_at2pct']:.1f}", minYrSR=f"{st['minYrSR']:.2f}", t_vs_LIVE=f"{tl:+.2f}",
                SR8=f"{s(cutf(df.net + df.to*(5.5e-4-8e-4))):.2f}", SR12=f"{s(cutf(df.net + df.to*(5.5e-4-12e-4))):.2f}")
extra = []
for i, r in T.iterrows():
    nm, p = r["name"], r["params"]
    if r["kind"] == "score":
        w = float(p.split(";")[0].split("=")[1]); d = sc[(nm, w)]; x = row(d["df"], d["pt"], d["st"], d["t_live"])
    elif r["kind"] == "sleeve":
        d = sl[nm]["comb"][0.25]; x = row(d["df"], d["pt"], d["st"], d["t_live"])
        x["sleeve_SR"] = f"{sl[nm]['sleeve_st']['SR']:.2f}"; x["corr_B"] = f"{sl[nm]['corrB']:+.2f}"
        x["t_rw20/30"] = f"{sl[nm]['comb'][0.2]['pt']['tNW']:+.2f}/{sl[nm]['comb'][0.3]['pt']['tNW']:+.2f}"
    else:
        if nm == "fund_disp_gross": x = row(g1["df"], g1["pt"], g1["st"], g1["t_live"])
        else:
            df, pt, st, _, _ = g2["G02 inv 90d [.5,1.5]"]; x = row(df, pt, st, np.nan)
    for k, v in x.items(): T.loc[i, k] = v
T.to_csv("trials.csv", index=False)
cols = ["id", "name", "params", "SR", "SR8", "SR12", "t_vs_B", "years", "groups", "regimes", "adopt", "mdd_at2pct", "minYrSR", "t_vs_LIVE", "sleeve_SR", "corr_B", "t_rw20/30"]
tab = T[cols].fillna("")
md = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n" + "\n".join("| " + " | ".join(str(v).replace("|", "/") for v in rr) + " |" for rr in tab.values)
open("trials_table.md", "w").write(md)
tt = T[T.kind == "score"].t_vs_B.astype(float); print("score trials: n", len(tt), "mean t", tt.mean().round(2), "max", tt.max(), "n>0", (tt > 0).sum())
tb = cutf(B[0]); print("B SR", s(tb.net).round(2), "SR8", s(tb.net + tb.to*(5.5e-4-8e-4)).round(2), "SR12", s(tb.net + tb.to*(5.5e-4-12e-4)).round(2))
