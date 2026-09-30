import sys, pickle, time; sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/signals")
from common import *
import feats
names = sys.argv[1].split(",") ; ws = [float(x) for x in (sys.argv[2].split(',') if len(sys.argv) > 2 else ['0.10','0.25'])]
B = pickle.load(open("B.pkl", "rb")); LIVE = pickle.load(open("LIVE.pkl", "rb"))
try: res = pickle.load(open("scores.pkl", "rb"))
except FileNotFoundError: res = {}
for nm in names:
    t = time.time(); P = feats.pct(D, feats.feature(D, nm, PHI)).astype(np.float32)
    res.setdefault("_pct_cov", {})[nm] = float(P.where(D.M).stack().ne(0.5).mean())
    for w in ws:
        c = ext.book(D, (1 - w) * S0 + w * P, short_frac=0.55, stop=0.2, N=12, NS=20)
        r = h.partition_test(D, c, B, verbose=False); r2 = h.partition_test(D, c, LIVE, verbose=False); st = stats(c[0])
        res[(nm, w)] = dict(df=c[0], pt=r, t_live=r2["tNW"], st=st)
        print(f"{nm:12s} w={w:.2f} SR {st['SR']:.2f} t_vsB {r['tNW']:+.2f} yrs {r['years_won']} grp {r['coin_groups_won']} up {r['regime_btc_up_bp']:+.2f} dn {r['regime_btc_down_bp']:+.2f} adopt {r['adopt']} mdd2 {st['mdd_at2pct']:.1f} minYr {st['minYrSR']:.2f} t_vsLIVE {r2['tNW']:+.2f}  ({time.time()-t:.0f}s)", flush=True)
        del c
    del P
    pickle.dump(res, open("scores.pkl", "wb"))
