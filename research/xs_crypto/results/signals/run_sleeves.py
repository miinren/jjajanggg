import sys, pickle, time; sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/signals")
from common import *
import feats
B = pickle.load(open("B.pkl", "rb")); LIVE = pickle.load(open("LIVE.pkl", "rb"))
SPEC = {  # name: (feature, book kwargs)
    "rev3_h1": ("rev3", dict(every=1, N=12, NS=12, short_frac=0.5, stop=0.2)),
    "rev6_h2": ("rev6", dict(every=2, N=12, NS=12, short_frac=0.5, stop=0.2)),
    "rev6_h4": ("rev6", dict(every=4, N=12, NS=12, short_frac=0.5, stop=0.2)),
    "age_sleeve": ("age", dict(every=8, N=20, NS=20, short_frac=0.5, stop=0.2)),
    "fundz_sleeve": ("fund_z30", dict(every=8, N=20, NS=20, short_frac=0.5, stop=0.2)),
    "fund_chg_sleeve": ("fund_chg", dict(every=8, N=20, NS=20, short_frac=0.5, stop=0.2)),
    "near_high_sleeve": ("near_high", dict(every=8, N=20, NS=20, short_frac=0.5, stop=0.2)),
    "jump_beta_sleeve": ("jump_beta", dict(every=8, N=20, NS=20, short_frac=0.5, stop=0.2)),
    "absmove6_h4": ("absmove6", dict(every=4, N=12, NS=12, short_frac=0.5, stop=0.2)),
    "absmove24_h8": ("absmove24", dict(every=8, N=20, NS=20, short_frac=0.5, stop=0.2)),
    "dow_season_sleeve": ("dow_season", dict(every=8, N=20, NS=20, short_frac=0.5, stop=0.2)),
}
for a in sys.argv[2:]:   # extra ad-hoc specs "name=feature:every:N:rw"
    n, v = a.split("="); f, ev, N = v.split(":")[:3]; SPEC[n] = (f, dict(every=int(ev), N=int(N), NS=int(N), short_frac=0.5, stop=0.2))
RW = 0.25
def safe_lw(sf):
    def f(i, longs, shorts):
        return (np.full(len(longs), (1 - sf) / max(len(longs), 1)), np.full(len(shorts), sf / max(len(shorts), 1)))
    return f
def combine(S, rw=RW):
    k = cut(B[0].net).std() / cut(S[0].net).std()
    df = B[0].copy()
    for c in ["net", "to"]: df[c] = (1 - rw) * B[0][c] + rw * k * S[0][c]
    return df, (1 - rw) * B[1] + np.float32(rw * k) * S[1]
try: res = pickle.load(open("sleeves.pkl", "rb"))
except FileNotFoundError: res = {}
for nm in sys.argv[1].split(","):
    f, kw = SPEC[nm]; t = time.time()
    S = ext.book(D, feats.pct(D, feats.feature(D, f, PHI)), **kw, leg_weights=safe_lw(kw['short_frac'])); ss = stats(S[0])
    corr = cut(S[0].net).corr(cut(B[0].net))
    out = {}
    for rw in (0.20, 0.25, 0.30):
        c = combine(S, rw); r = h.partition_test(D, c, B, verbose=False); r2 = h.partition_test(D, c, LIVE, verbose=False); st = stats(c[0])
        out[rw] = dict(df=c[0], pt=r, t_live=r2["tNW"], st=st)
        print(f"{nm:18s} sleeveSR {ss['SR']:.2f} bp {ss['bp']:.1f} to {cut(S[0].to).mean():.2f} corrB {corr:+.2f} | rw {rw:.2f} combSR {st['SR']:.2f} t_vsB {r['tNW']:+.2f} yrs {r['years_won']} grp {r['coin_groups_won']} up {r['regime_btc_up_bp']:+.2f} dn {r['regime_btc_down_bp']:+.2f} adopt {r['adopt']} mdd2 {st['mdd_at2pct']:.1f} minYr {st['minYrSR']:.2f} t_vsLIVE {r2['tNW']:+.2f} ({time.time()-t:.0f}s)", flush=True)
    res[nm] = dict(sleeve_df=S[0], sleeve_st=ss, corrB=corr, comb=out, spec=(f, kw))
    del S
    pickle.dump(res, open("sleeves.pkl", "wb"))
