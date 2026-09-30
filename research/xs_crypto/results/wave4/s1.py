# Stage 1: structures T01-T10 (+ LIVE reference), realistic accounting, 8-clock; pseudo-holdout selection.
from lib4 import *
from tabulate import tabulate
F7 = D.F.rolling(168, min_periods=120).mean()
BMVk = dict(N=12, NS=20, stop=0.2)
CARRY = dict(N=12, NS=20, stop=0.2, short_guard=False)
S = {"LIVE": dict(),
     "T01 LO8": dict(N=8, NS=8, short_frac=0.0), "T02 LO12": dict(N=12, NS=12, short_frac=0.0), "T03 LO20": dict(N=20, NS=20, short_frac=0.0),
     "T04 LS-sf0.20": dict(BMVk, leg_weights=mv_sf(0.20)), "T05 LS-sf0.35": dict(BMVk, leg_weights=mv_sf(0.35)),
     "T06 B-MV": dict(BMVk, leg_weights=minvar_floor), "T07 B-MV-N8": dict(BMVk, N=8, leg_weights=minvar_floor),
     "T08 CARRY-55": dict(CARRY, short_frac=0.55, score_s=D.F.where(D.M)), "T09 CARRY-35": dict(CARRY, short_frac=0.35, score_s=D.F.where(D.M)),
     "T10 CARRY7-55": dict(CARRY, short_frac=0.55, score_s=F7.where(D.M))}
P = {}
for k, kw in S.items():
    P[k] = run8(k.split()[0] + "_s1", keep_coin=True, **kw); print("ran", k, flush=True)
rows = [row(k, o) for k, o in P.items()]
print(tabulate(pd.DataFrame(rows).round(3), headers="keys", showindex=False, tablefmt="github"))
print("\nfull-sample risk-matched ptest vs B-MV:")
for k in P:
    if k != "T06 B-MV":
        r = ptest(P[k], P["T06 B-MV"], ST, "2026-01-01"); print(f"  {k}: t {r['t']:.2f} years {r['years']} groups {r['groups']} regimes {r['up']:.2f}/{r['dn']:.2f} rm-diff {r['diff_bp']:.2f} bp")
pool = {k: v for k, v in P.items() if k != "LIVE"}
out = {}
for gated in (True, False):
    picks = {}
    for Y in YEARS:
        p, sr = select(pool, "T06 B-MV", Y, gated); picks[Y] = p
        print(f"{'gated' if gated else 'ungated'} <{Y}: pick {p}; selection SRs " + ", ".join(f"{k.split()[0]} {v:.2f}" for k, v in sr.items()))
        if gated:
            for k in pool:
                if k != "T06 B-MV":
                    r = ptest(pool[k], pool["T06 B-MV"], ST, f"{Y}-01-01"); print(f"     {k}: t {r['t']:.2f} yrs {r['years']} grp {r['groups']} ok {r['ok']}")
    for c in (5.5, 8, 12):
        for ref in ("T06 B-MV", "LIVE"):
            print(f"  OOS {'gated' if gated else 'ungated'} @{c}bp vs {ref}:", {a: (round(b, 3) if isinstance(b, float) else b) for a, b in oos(picks, pool, P[ref], c).items()})
    out["gated" if gated else "ungated"] = picks
pickle.dump(out, open(f"{OUT}/s1_picks.pkl", "wb"))
