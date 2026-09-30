from lib import *
import glob, json
P = pickle.load(open(f"{OUT}/s1.pkl", "rb")); Q = pickle.load(open(f"{OUT}/s2.pkl", "rb"))
Bdf = P["B"]["df"]; Bc = np.load(f"{OUT}/coin_B.npy"); B = (Bdf, Bc); vB = cut(Bdf.net).std()
rB = risk(Bdf, vB)
def ddwin(df, a, b, v):
    x = cut(df.net); x = x * (v / x.std()); y = x[(x.index >= a) & (x.index < b)]; c = y.cumsum()
    return dict(ret=y.sum() * 1e4, maxdd=-(c - c.cummax()).min() * 1e4)
def rowfor(name, df, coin):
    s = stats(df); r = risk(df, vB); pt = h.partition_test(D, (df, coin), B, verbose=False)
    raw = cut(df.net); on = ddwin(df, "2021-10-01", "2021-12-01", vB); onr = ddwin(df, "2021-10-01", "2021-12-01", raw.std())
    return dict(name=name, SR=s["SR"], SR8=sr_at(df, 8), SR12=sr_at(df, 12), vol_bp=s["vol_bp"], bp=s["bp"], t_vs_B=pt["tNW"], years=pt["years_won"],
                groups=pt["coin_groups_won"], reg=f"{pt['regime_btc_up_bp']:.2f}/{pt['regime_btc_down_bp']:.2f}", adopt=pt["adopt"],
                mdd2=s["mdd_at2pct"], minYr=s["minYrSR"], cvar5=r["cvar5"], dCVaR=rB["cvar5"] - r["cvar5"], w20=r["w20"], dW20=rB["w20"] - r["w20"],
                mddB=r["mdd"], d0613_raw=raw.get(pd.Timestamp("2022-06-13")) * 1e4, d0613_mv=r["d20220613"],
                ON21_ret_mv=on["ret"], ON21_dd_mv=on["maxdd"], ON21_dd_raw=onr["maxdd"], to=cut(df.to).mean(),
                yrdiff=pt["year_diffs_bp"], grpd=pt["coin_group_diffs"])
rows = [rowfor("B", Bdf, Bc)]
for k in ("P1a_minvar", "P1b_invvol"):
    rows.append(rowfor(k, P[k]["df"], np.load(f"{OUT}/coin_{k}.npy")))
# per-clock risk comparison (each vs B at same clock, matched to that clock's B vol)
pc = []
for off in range(8):
    b = P["B"]["per"][off]; vb = cut(b.net).std(); rb = risk(b, vb)
    for k in ("P1a_minvar", "P1b_invvol"):
        r = risk(P[k]["per"][off], vb); pc.append(dict(off=off, k=k, dCVaR=rb["cvar5"] - r["cvar5"], dW20=rb["w20"] - r["w20"]))
pc = pd.DataFrame(pc)
# nulls
NULL = {}
for kind in ("mv", "iv"):
    d = {}
    for f in sorted(glob.glob(f"{OUT}/null_{kind}_*.pkl")): d.update(pickle.load(open(f, "rb")))
    NULL[kind] = pd.DataFrame([dict(seed=s, SR=stats(df)["SR"], dCVaR=rB["cvar5"] - risk(df, vB)["cvar5"], dW20=rB["w20"] - risk(df, vB)["w20"],
                                    dMDD=rB["mdd"] - risk(df, vB)["mdd"], minYr=stats(df)["minYrSR"], d0613_mv=risk(df, vB)["d20220613"],
                                    t_vs_B=h.nw_t(cut(df.net) * vB / cut(df.net).std() - cut(Bdf.net))) for s, df in sorted(d.items())])
# Part 2
rows2 = []; fam = {}
for k in ("U50", "U60", "U75", "SPLIT"):
    c = np.load(f"{OUT}/coin2_{k}.npy"); r = rowfor(k, Q[k]["df"], c); r.update(Q[k]["held"]); rows2.append(r); fam[k] = (Q[k]["df"], None); del c
rows2.insert(0, dict(name="B(held)", **Q["B"]["held"]))
wf = h.walk_forward(fam, B)
# notional check
EQ = 330 * 1.4
W = P["W"]
notion = {k: dict(frac_short_w_below_5usd=float((v * EQ < 5).mean()), frac_zero=float((v < 1e-9).mean()), median_usd=float(np.median(v * EQ)), p10_usd=float(np.percentile(v * EQ, 10))) for k, v in W.items()}
out = dict(rows=rows, rows2=rows2, pc=pc, NULL=NULL, wf=wf, notion=notion, rB=rB)
pickle.dump(out, open(f"{OUT}/analysis.pkl", "wb"))
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 50)
print(pd.DataFrame(rows).drop(columns=["yrdiff", "grpd"]).round(3).to_string())
for r in rows: print(r["name"], r["yrdiff"], r["grpd"])
print(pc.round(2).to_string())
for kind, n in NULL.items():
    print(kind, len(n)); print(n.describe(percentiles=[.05, .5, .9, .95, .99]).round(3).to_string())
    for r in rows[1:]:
        print("  ", r["name"], "p(dCVaR null>=cand)=%.3f" % (n.dCVaR >= r["dCVaR"]).mean(), "p(dW20)=%.3f" % (n.dW20 >= r["dW20"]).mean(), "p(SR)=%.3f" % (n.SR >= r["SR"]).mean())
print(pd.DataFrame(rows2).drop(columns=["yrdiff", "grpd"], errors="ignore").round(3).to_string())
for r in rows2[1:]: print(r["name"], r["yrdiff"], r["grpd"])
print("WF", wf); print("notional", notion); print("rB", rB)
