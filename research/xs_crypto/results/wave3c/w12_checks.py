# W12 checks: plateau (band 0.02 / 0.05 without forced re-hedge) vs W06, and residual BTC beta / tracking.
import sys
sys.argv = ["x"]
from run_trials import *
W6 = cut(pickle.load(open(f"{OUT}/W06.pkl", "rb"))["df"]); btc = D.rb.resample("D").sum()
for band in (0.02, 0.03, 0.05):
    d, _ = avg8(keep_coin=False, hedge_band=band, hedge_force=False); x = cut(d); dd = x.net - W6.net
    pc = (x.net + x.to * h.COST) - (W6.net + W6.to * h.COST); b = btc.reindex(x.index)
    print("band %.2f: SR %.3f (8bp %.3f 12bp %.3f) vs W06 %+.3f bp/day t %.2f, pre-cost %+.3f t %.2f, hedge_to %.3f, daily beta %.4f, track vs W06 %.2f bp" % (
        band, srx(x.net), sr_at(d, 8), sr_at(d, 12), dd.mean() * 1e4, h.nw_t(dd.to_numpy()), pc.mean() * 1e4, h.nw_t(pc.to_numpy()), x.to_hedge.mean(),
        np.cov(x.net, b)[0, 1] / b.var(), dd.std() * 1e4), flush=True)
b = btc.reindex(W6.index); print("W06 daily beta %.4f" % (np.cov(W6.net, b)[0, 1] / b.var()))
