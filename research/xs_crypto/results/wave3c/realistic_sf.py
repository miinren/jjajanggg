# Wave R fix: R01/R02 (short_frac) - minvar_floor hard-codes 0.45/0.55, so rescale its legs to the requested split.
import sys
sys.argv = ["x"]
from run_trials import *
def mv_sf(sf):
    def f(i, longs, shorts):
        wl, ws = minvar_floor(i, longs, shorts); return wl * (1 - sf) / 0.45, ws * sf / 0.55
    return f
RB = dict(N=12, NS=20, stop=0.2, hedge_band=0.03, simple=True, drift=True)
def run(sf):
    df = cm = None; per = {}
    for off in range(8):
        d, c = ext4.book(D, S0, offset=off, leg_weights=mv_sf(sf), **RB); per[off] = d
        df = d / 8 if df is None else df + d / 8; cm = c / np.float32(8) if cm is None else cm + c / np.float32(8); del c
    return df, cm, per
base = run(0.55); print("base check SR %.3f (expect 1.490)" % stats(base[0])["SR"], flush=True)
dfs = {}
for k, sf in (("R01", 0.50), ("R02", 0.45)):
    df, cm, per = run(sf); dfs[k] = df; s = stats(df); r = h.partition_test(D, (df, cm), base[:2], verbose=False)
    clk = sum(srx(cut(per[o].net)) > srx(cut(base[2][o].net)) for o in range(8))
    print({"id": k, "short_frac": sf, "SR": round(s["SR"], 3), "SR8": round(sr_at(df, 8), 3), "SR12": round(sr_at(df, 12), 3), "t": round(r["tNW"], 2), "years": r["years_won"],
           "groups": r["coin_groups_won"], "adopt": bool(r["adopt"] and r["tNW"] >= 2), "mdd2": round(s["mdd_at2pct"], 1), "minYr": round(s["minYrSR"], 2), "clocks_won": clk}, flush=True)
f = {k: (v, None) for k, v in dfs.items()}; f["base"] = (base[0], None); w = h.walk_forward(f, (base[0], None))
print("WF short_frac: wf_SR %.3f base %.3f t %.2f picks %s" % (w["wf_SR"], w["base_SR"], w["tNW_vs_base"], w["picks"]), flush=True)
