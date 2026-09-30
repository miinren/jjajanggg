# Stage 2: score grid (fw x L) on the stage-1 structure picked most often by the gated rule (T07 B-MV-N8: <2024, <2025).
# Final pipeline per Y: stage-1 gated pick; if it is T07, the stage-2 gated pick among its scores. OOS chain vs B-MV and LIVE.
from lib4 import *
from tabulate import tabulate
s1 = pickle.load(open(f"{OUT}/s1_picks.pkl", "rb")); print("stage-1 gated picks:", s1["gated"])
BK8 = dict(N=8, NS=20, stop=0.2, leg_weights=minvar_floor)
G = {"T07 fw0.25-L336": run8("T07_s1", keep_coin=True, **BK8)}
for tid, (fw, L) in zip(["T11", "T12", "T13", "T14", "T15", "T16", "T17", "T18"],
                        [(0, 168), (0, 336), (0, 720), (0.25, 168), (0.25, 720), (0.5, 168), (0.5, 336), (0.5, 720)]):
    G[f"{tid} fw{fw}-L{L}"] = run8(f"{tid}_s2", score(L, fw), keep_coin=True, **BK8); print("ran", tid, flush=True)
print(tabulate(pd.DataFrame([row(k, o) for k, o in G.items()]).round(3), headers="keys", showindex=False, tablefmt="github"))
base = "T07 fw0.25-L336"
for k in G:
    if k != base:
        r = ptest(G[k], G[base], ST, "2026-01-01"); print(f"  full-sample {k} vs default: t {r['t']:.2f} yrs {r['years']} grp {r['groups']} rm-diff {r['diff_bp']:.2f}")
P1 = {k: run8(k.split()[0] + "_s1", keep_coin=True) for k in ["LIVE", "T06 B-MV"]}   # cached
final = {}
for gated in (True, False):
    picks = {}
    for Y in YEARS:
        p2, sr = select(G, base, Y, gated)
        print(f"{'gated' if gated else 'ungated'} <{Y}: score pick {p2}; " + ", ".join(f"{k.split()[1]} {v:.2f}" for k, v in sr.items()))
        s1p = s1["gated" if gated else "ungated"][Y]
        picks[Y] = p2 if s1p.startswith("T07") else s1p
    print("  final pipeline picks:", picks)
    pool = {**G, "T06 B-MV": P1["T06 B-MV"]}
    for c in (5.5, 8, 12):
        for ref in ("T06 B-MV", "LIVE"):
            print(f"  OOS {'gated' if gated else 'ungated'} @{c}bp vs {ref}:", {a: (round(b, 3) if isinstance(b, float) else b) for a, b in oos(picks, pool, P1[ref], c).items()}, flush=True)
    final["gated" if gated else "ungated"] = picks
pickle.dump(final, open(f"{OUT}/s2_picks.pkl", "wb"))
