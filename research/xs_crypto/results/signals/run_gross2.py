import sys, pickle; sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/signals")
from common import *
B = pickle.load(open("B.pkl", "rb")); LIVE = pickle.load(open("LIVE.pkl", "rb")); G1 = pickle.load(open("gross.pkl", "rb"))
disp = D.F.where(D.M).std(1)
out = {}
def run(lab, G):
    c = ext.book(D, S0, short_frac=0.55, stop=0.2, N=12, NS=20, gross=G)
    r = h.partition_test(D, c, B, verbose=False); r2 = h.partition_test(D, c, LIVE, verbose=False); st = stats(c[0])
    x = cut(c[0].net); s = lambda y: y.mean()/y.std()*np.sqrt(365)
    sr8 = s(cut(c[0].net + c[0].to*(5.5e-4 - 8e-4))); sr12 = s(cut(c[0].net + c[0].to*(5.5e-4 - 12e-4)))
    print(f"{lab:28s} SR {st['SR']:.2f} SR8 {sr8:.2f} SR12 {sr12:.2f} t_vsB {r['tNW']:+.2f} yrs {r['years_won']} {r['year_diffs_bp']} grp {r['coin_groups_won']} up {r['regime_btc_up_bp']:+.2f} dn {r['regime_btc_down_bp']:+.2f} adopt {r['adopt']} mdd2 {st['mdd_at2pct']:.1f} minYr {st['minYrSR']:.2f} t_vsLIVE {r2['tNW']:+.2f}", flush=True)
    out[lab] = (c[0], r, st, sr8, sr12); return c
def G(med_days=90, lo=0.5, hi=1.5, inv=True, lag=0):
    d = disp.shift(lag)
    med = d.rolling(24 * med_days, min_periods=24 * min(30, med_days)).median()
    return ((med / d) if inv else (d / med)).clip(lo, hi).fillna(1.0).to_numpy()
cG2 = run("G02 inv 90d [.5,1.5]", G())
fam = {"B": B, "G01": (G1["df"], None), "G02": cG2}
print("walk-forward {B,G01,G02}:", h.walk_forward(fam, B))
if len(sys.argv) > 1:   # plateau + leakage checks
    for md in (30, 180): run(f"plateau med {md}d", G(md))
    for lo, hi in ((0.67, 1.33), (0.33, 2.0)): run(f"plateau clip [{lo},{hi}]", G(lo=lo, hi=hi))
    run("leak-check lag 24h", G(lag=24)); run("leak-check lag 72h", G(lag=72))
pickle.dump(out, open("gross2.pkl", "wb"))
