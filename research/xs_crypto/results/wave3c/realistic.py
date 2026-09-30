# Re-evaluate the adoption chain under REALISTIC accounting (simple returns + positions drift between trades), 8-clock averaged.
# LIVE -> B -> B-MV -> B-MV + W12 hedge band, each with a risk-matched partition test vs the previous step.
import sys
sys.argv = ["x"]
from run_trials import *
R = dict(simple=True, drift=True)
CFG = {"LIVE": dict(),                                                     # ext4 defaults = live rules (N=20/20, 50/50, stop 0.4, EW)
       "B": dict(N=12, NS=20, short_frac=0.55, stop=0.2),
       "B-MV": dict(N=12, NS=20, short_frac=0.55, stop=0.2, leg_weights=minvar_floor),
       "B-MV+W12": dict(N=12, NS=20, short_frac=0.55, stop=0.2, leg_weights=minvar_floor, hedge_band=0.03, hedge_force=False)}
res = {}
for k, kw in CFG.items():
    df = cm = None
    for off in range(8):
        d, c = ext4.book(D, S0, offset=off, **R, **kw)
        df = d / 8 if df is None else df + d / 8; cm = c / np.float32(8) if cm is None else cm + c / np.float32(8); del c
    res[k] = (df, cm); s = stats(df); x = cut(df)
    print(k, "SR %.3f @8 %.3f @12 %.3f bp %.2f (L %.2f S %.2f H %.2f F %.2f) to %.3f mdd2 %.1f minYr %.2f yearly %s" % (
        s["SR"], sr_at(df, 8), sr_at(df, 12), s["bp"], x.long.mean()*1e4, x.short.mean()*1e4, x.hedge.mean()*1e4, x.fund.mean()*1e4,
        x.to.mean(), s["mdd_at2pct"], s["minYrSR"], x.net.groupby(x.index.year).apply(srx).round(2).to_dict()), flush=True)
for a, b in (("B", "LIVE"), ("B-MV", "B"), ("B-MV+W12", "B-MV"), ("B-MV", "LIVE"), ("B-MV+W12", "LIVE")):
    r = h.partition_test(D, res[a], res[b], verbose=False)
    print("%s vs %s: t %.2f years %s groups %s regimes %.2f/%.2f adopt %s" % (a, b, r["tNW"], r["years_won"], r["coin_groups_won"], r["regime_btc_up_bp"], r["regime_btc_down_bp"], r["adopt"]), flush=True)
pickle.dump({k: v[0] for k, v in res.items()}, open(f"{OUT}/realistic.pkl", "wb"))
