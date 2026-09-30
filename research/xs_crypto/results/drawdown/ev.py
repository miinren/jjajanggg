import numpy as np, pandas as pd, sys, pickle, csv
sys.path.insert(0, "/root/work")
import cloud_harness as h
from common import stats, cut
def srx(x): return x.mean() / x.std() * np.sqrt(365)
def sr_at(df, c): return srx(cut(df.net + df.to * (h.COST - c * 1e-4)))
def row(D, name, c, B, LIVE):
    r = h.partition_test(D, c, B, verbose=False); r2 = h.partition_test(D, c, LIVE, verbose=False); st = stats(c[0])
    return dict(name=name, SR=round(st["SR"], 3), t_vs_B=round(r["tNW"], 2), years=r["years_won"], groups=r["coin_groups_won"],
                regimes_up_dn=f"{r['regime_btc_up_bp']:.2f}/{r['regime_btc_down_bp']:.2f}", adopt=r["adopt"],
                mdd_at2pct=round(st["mdd_at2pct"], 2), minYrSR=round(st["minYrSR"], 2), t_vs_LIVE=round(r2["tNW"], 2),
                SR8bp=round(sr_at(c[0], 8), 2), SR12bp=round(sr_at(c[0], 12), 2),
                note=f"worst_day_bp={cut(c[0].net).min()*1e4:.0f} to={cut(c[0].to).mean():.3f} yrdiff={r['year_diffs_bp']} grp={r['coin_group_diffs']}")
def update_csv(rows, path="/root/work/results/drawdown/trials.csv"):
    with open(path) as f: R = list(csv.DictReader(f))
    by = {r["name"]: r for r in rows}
    for x in R:
        if x["name"] in by:
            for k, v in by[x["name"]].items():
                if k != "name": x[k] = v
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(R[0].keys())); w.writeheader(); w.writerows(R)
