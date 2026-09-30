import sys, pickle; sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/signals")
from common import *
B = pickle.load(open("B.pkl", "rb")); LIVE = pickle.load(open("LIVE.pkl", "rb"))
disp = D.F.where(D.M).std(1)                       # F = prior-day funding -> known at i
med = disp.rolling(24 * 90, min_periods=24 * 30).median()
G = (disp / med).clip(0.5, 1.5).fillna(1.0).to_numpy()
c = ext.book(D, S0, short_frac=0.55, stop=0.2, N=12, NS=20, gross=G)
r = h.partition_test(D, c, B, verbose=False); r2 = h.partition_test(D, c, LIVE, verbose=False); st = stats(c[0])
print(f"G01 SR {st['SR']:.2f} t_vsB {r['tNW']:+.2f} yrs {r['years_won']} grp {r['coin_groups_won']} up {r['regime_btc_up_bp']:+.2f} dn {r['regime_btc_down_bp']:+.2f} adopt {r['adopt']} mdd2 {st['mdd_at2pct']:.1f} minYr {st['minYrSR']:.2f} t_vsLIVE {r2['tNW']:+.2f} meanG {G.mean():.2f}")
pickle.dump(dict(df=c[0], pt=r, t_live=r2["tNW"], st=st), open("gross.pkl", "wb"))
