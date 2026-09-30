# Diagnostic (not a trial): how much turnover/cost does the constant-weight engine hide? B-MV and W06 with drift=True.
import sys
sys.argv = ["x"]
from run_trials import *
rows = []
for lab, kw in (("BMV", {}), ("BMV_drift", dict(drift=True)), ("W06", dict(hedge_band=0.03)), ("W06_drift", dict(hedge_band=0.03, drift=True))):
    d, _ = avg8(keep_coin=False, **kw); x = cut(d)
    rows.append(dict(book=lab, SR=srx(x.net), SR8=sr_at(d, 8), SR12=sr_at(d, 12), net_bp=x.net.mean() * 1e4, precost_bp=(x.net + x.to * h.COST).mean() * 1e4,
                     to=x.to.mean(), to_hedge=x.to_hedge.mean(), to_coin=(x.to - x.to_hedge).mean())); print(rows[-1], flush=True)
o = pd.DataFrame(rows).round(3); o.to_csv("diag_drift.csv", index=False); print(o.to_string(index=False))
