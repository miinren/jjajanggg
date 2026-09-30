# Wave R2: score-construction neighbours under realistic accounting (simple + drift); base = B-MV + W06 (hedge band 0.03).
import sys
sys.argv = ["x"]
from run_trials import *
from common import pF
e = D.resid; el = e.shift(1)
PHI = ((e * el).rolling(336, min_periods=200).mean() / (el * el).rolling(336, min_periods=200).mean()).clip(-0.5, 0.5)
EC = e - PHI * el
def score(fw=0.25, L=336, ar1=True):
    X = (EC if ar1 else e).rolling(L, min_periods=round(200 * L / 336)).std()   # same min_periods ratio as common.py (200 at L=336)
    p = X.where(D.M).rank(1, pct=True); return (1 - fw) * p + fw * pF
chk = score(); print("S0 rebuild max diff %.2e" % float((chk - S0).abs().max().max()), flush=True)
RB = dict(N=12, NS=20, short_frac=0.55, stop=0.2, leg_weights=minvar_floor, hedge_band=0.03, simple=True, drift=True)
def run(sc):
    df = cm = None; per = {}
    for off in range(8):
        d, c = ext4.book(D, sc, offset=off, **RB); per[off] = d
        df = d / 8 if df is None else df + d / 8; cm = c / np.float32(8) if cm is None else cm + c / np.float32(8); del c
    return df, cm, per
base = run(S0); print("BASE SR %.3f (expect 1.490)" % stats(base[0])["SR"], flush=True)
TR = {"R09": dict(fw=0.10), "R10": dict(fw=0.40), "R11": dict(L=168), "R12": dict(L=672), "R13": dict(ar1=False)}
dfs = {}
for k, kw in TR.items():
    df, cm, per = run(score(**kw)); dfs[k] = df; s = stats(df); r = h.partition_test(D, (df, cm), base[:2], verbose=False)
    clk = sum(srx(cut(per[o].net)) > srx(cut(base[2][o].net)) for o in range(8)); x = cut(df)
    print({"id": k, **kw, "SR": round(s["SR"], 3), "SR8": round(sr_at(df, 8), 3), "SR12": round(sr_at(df, 12), 3), "t": round(r["tNW"], 2), "years": r["years_won"],
           "groups": r["coin_groups_won"], "adopt": bool(r["adopt"] and r["tNW"] >= 2), "mdd2": round(s["mdd_at2pct"], 1), "minYr": round(s["minYrSR"], 2),
           "L_bp": round(x.long.mean() * 1e4, 2), "S_bp": round(x.short.mean() * 1e4, 2), "clocks_won": clk}, flush=True); del cm
for fam, ids in (("fw", ["R09", "R10"]), ("L", ["R11", "R12"]), ("ar1", ["R13"])):
    f = {i: (dfs[i], None) for i in ids}; f["base"] = (base[0], None); w = h.walk_forward(f, (base[0], None))
    print("WF %s: wf_SR %.3f base %.3f t %.2f picks %s" % (fam, w["wf_SR"], w["base_SR"], w["tNW_vs_base"], w["picks"]), flush=True)
