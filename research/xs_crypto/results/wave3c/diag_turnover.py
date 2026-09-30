# Diagnostic: split turnover into coin vs BTC-hedge and P&L into pre-cost vs cost, 8-clock average, for B-MV and timing trials.
import sys
sys.argv = ["x"]
from run_trials import *
out = []
for tid in ["BMV", "E02", "E04", "E05", "E08", "E10", "E12"]:
    acc = None
    for off in range(8):
        kw = {} if tid == "BMV" else dict(execf=EXEC[tid][0], H=EXEC[tid][1])
        d, _ = ext4.book(D, S0, offset=off, leg_weights=minvar_floor, **BK, **kw); d = cut(d)
        acc = d / 8 if acc is None else acc + d / 8
    gross = acc.net + acc.to * h.COST
    out.append(dict(id=tid, net_bp=acc.net.mean() * 1e4, precost_bp=gross.mean() * 1e4, long_bp=acc.long.mean() * 1e4,
                    short_bp=acc.short.mean() * 1e4, hedge_bp=acc.hedge.mean() * 1e4, to_total=acc.to.mean(),
                    to_hedge=acc.to_hedge.mean(), to_coin=(acc.to - acc.to_hedge).mean()))
    print(out[-1], flush=True)
o = pd.DataFrame(out).round(3); o.to_csv("diag_turnover.csv", index=False); print(o.to_string(index=False))
