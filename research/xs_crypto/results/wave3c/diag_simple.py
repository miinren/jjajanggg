# CRITICAL CHECK (diagnostic): the harness books P&L as w * log-return. Real P&L is w * simple-return. For a short, log accounting
# overstates P&L by ~|w| r^2/2 each hour, and the book shorts the most volatile names. Measure B-MV under simple-return accounting,
# with and without price drift, plus leg attribution.
import sys
sys.argv = ["x"]
from run_trials import *
rows = []
for lab, kw in (("BMV_log", {}), ("BMV_simple", dict(simple=True)), ("BMV_simple_drift", dict(simple=True, drift=True)),
                ("W12_simple_drift", dict(simple=True, drift=True, hedge_band=0.03, hedge_force=False))):
    d, _ = avg8(keep_coin=False, **kw); x = cut(d)
    yr = x.net.groupby(x.index.year).apply(srx).round(2).to_dict()
    rows.append(dict(book=lab, SR=srx(x.net), SR8=sr_at(d, 8), SR12=sr_at(d, 12), net_bp=x.net.mean() * 1e4, long_bp=x.long.mean() * 1e4,
                     short_bp=x.short.mean() * 1e4, hedge_bp=x.hedge.mean() * 1e4, fund_bp=x.fund.mean() * 1e4, to=x.to.mean(), yearly=yr)); print(rows[-1], flush=True)
o = pd.DataFrame(rows); o.to_csv("diag_simple.csv", index=False); print(o.drop(columns="yearly").round(3).to_string(index=False))
# direct estimate of the bias on B-MV (offset 0): sum_c w_c * (log(1+g) - g) per day
