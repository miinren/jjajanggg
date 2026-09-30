# W06 hedge band: sanity checks for a t > 3 pass + plateau (band 0.02 / 0.05).
import sys
sys.argv = ["x"]
from run_trials import *
per0 = {}; B0, cB0 = avg8(per_offset=per0)                  # B-MV again, now with the to_hedge column
W, cW = avg8(hedge_band=0.03)
for band in (0.02, 0.05):                                    # plateau neighbours (+-1 step)
    p = {}; d, c = avg8(per_offset=p, hedge_band=band); evaluate(f"W06_band{band}", d, c, p, dict(hedge_to=round(float(cut(d.to_hedge).mean()), 4)))
b, w = cut(B0), cut(W)
print("net bp/day  B-MV %.3f  W06 %.3f  diff %.3f" % (b.net.mean() * 1e4, w.net.mean() * 1e4, (w.net - b.net).mean() * 1e4))
pc = lambda x: x.net + x.to * h.COST
print("pre-cost    B-MV %.3f  W06 %.3f  diff %.3f (t %.2f)" % (pc(b).mean() * 1e4, pc(w).mean() * 1e4, (pc(w) - pc(b)).mean() * 1e4, h.nw_t((pc(w) - pc(b)).to_numpy())))
print("hedge P&L diff %.3f bp/day; hedge turnover %.3f -> %.3f" % ((w.hedge - b.hedge).mean() * 1e4, b.to_hedge.mean(), w.to_hedge.mean()))
r = h.partition_test(D, (W, cW), (B0, cB0), verbose=False, risk_match=False)
print("NOT risk-matched: t %.2f years %s groups %s (coin diffs %s) adopt %s" % (r["tNW"], r["years_won"], r["coin_groups_won"], r["coin_group_diffs"], r["adopt"]))
for hc in (2.0, 3.5):                                        # BTC hedge at a lower cost than alts
    adj = lambda x: x.net + x.to_hedge * (h.COST - hc * 1e-4)
    d = adj(w) - adj(b); print("hedge cost %.1fbp: SR B-MV %.3f W06 %.3f  diff %.3f bp/day t %.2f" % (hc, srx(adj(b)), srx(adj(w)), d.mean() * 1e4, h.nw_t(d.to_numpy())))
btc = D.rb.resample("D").sum().reindex(b.index)
for lab, x in (("B-MV", b), ("W06", w)):
    beta = np.cov(x.net, btc)[0, 1] / btc.var(); print("%s daily beta to BTC %.4f, corr %.3f" % (lab, beta, np.corrcoef(x.net, btc)[0, 1]))
print("tracking: std of daily (W06 - B-MV) = %.2f bp vs B-MV daily vol %.1f bp" % ((w.net - b.net).std() * 1e4, b.net.std() * 1e4))
