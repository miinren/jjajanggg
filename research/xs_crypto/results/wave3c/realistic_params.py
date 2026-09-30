# Wave R: one-at-a-time parameter re-check under realistic accounting (simple + drift), base = B-MV + W06 hedge band (0.03, forced re-hedges).
import sys
sys.argv = ["x"]
from run_trials import *
RB = dict(N=12, NS=20, short_frac=0.55, stop=0.2, leg_weights=minvar_floor, hedge_band=0.03, simple=True, drift=True)
def run(kw):
    df = cm = None; per = {}
    for off in range(8):
        d, c = ext4.book(D, S0, offset=off, **{**RB, **kw}); per[off] = d
        df = d / 8 if df is None else df + d / 8; cm = c / np.float32(8) if cm is None else cm + c / np.float32(8); del c
    return df, cm, per
base = run({}); sb = stats(base[0]); pickle.dump(base[0], open(f"{OUT}/R_base.pkl", "wb"))
print("BASE realistic B-MV+W06: SR %.3f @8 %.3f @12 %.3f mdd2 %.1f minYr %.2f to %.3f" % (sb["SR"], sr_at(base[0], 8), sr_at(base[0], 12), sb["mdd_at2pct"], sb["minYrSR"], cut(base[0]).to.mean()), flush=True)
TR = {"R01": dict(short_frac=0.50), "R02": dict(short_frac=0.45), "R03": dict(NS=15), "R04": dict(NS=25), "R05": dict(N=8), "R06": dict(N=16), "R07": dict(stop=0.30), "R08": dict(stop=0.15)}
dfs = {}
for k, kw in TR.items():
    df, cm, per = run(kw); dfs[k] = df; s = stats(df); r = h.partition_test(D, (df, cm), base[:2], verbose=False)
    clk = sum(srx(cut(per[o].net)) > srx(cut(base[2][o].net)) for o in range(8))
    row = dict(id=k, params=json.dumps(kw), SR=s["SR"], SR8=sr_at(df, 8), SR12=sr_at(df, 12), t=r["tNW"], years=r["years_won"], groups=r["coin_groups_won"],
               adopt=bool(r["adopt"] and r["tNW"] >= 2), mdd2=s["mdd_at2pct"], minYr=s["minYrSR"], to=cut(df).to.mean(), clocks_won=clk)
    pd.DataFrame([row]).to_csv("realistic_params.csv", mode="a", header=not os.path.exists("realistic_params.csv"), index=False)
    print({a: (round(b, 3) if isinstance(b, float) else b) for a, b in row.items()}, flush=True); del cm
for fam, ids in (("short_frac", ["R01", "R02"]), ("NS", ["R03", "R04"]), ("N", ["R05", "R06"]), ("stop", ["R07", "R08"])):
    f = {i: (dfs[i], None) for i in ids}; f["base"] = (base[0], None); w = h.walk_forward(f, (base[0], None))
    print("WF %s: wf_SR %.3f base %.3f t %.2f picks %s" % (fam, w["wf_SR"], w["base_SR"], w["tNW_vs_base"], w["picks"]), flush=True)
