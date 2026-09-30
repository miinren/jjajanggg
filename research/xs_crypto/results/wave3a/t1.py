# TASK 1: pseudo-holdout of the selection pipeline. Books are full-period 8-clock averages (no signal uses future data, so
# slicing = running on the window); all selection statistics use only [ST, Y-01-01); scoring uses year Y only.
from lib3 import *
SF = [0.5, 0.55, 0.6, 0.65]; STOP = [0.15, 0.2, 0.25, 0.3, 0.4]; NN = [(20, 20), (12, 20), (8, 20), (16, 20), (12, 15)]; WW = ["equal", "invvol", "minvar_floor"]
def with_(c, dim, v):
    c = dict(c)
    if dim == "N": c["N"], c["NS"] = v
    else: c[dim] = v
    return c
DIMS = [("sf", SF), ("st", STOP), ("N", NN), ("w", WW)]
Lr = run(LIVE)
EV = {}
def ev(cfg, Y, pipe):
    kk = (key(cfg), Y)
    if kk not in EV:
        r = run(cfg); a, b = ST, f"{Y}-01-01"
        s = wstats(r[0], a, b); p = ptest(r, Lr, a, b) if cfg != LIVE else dict(t=0, years="-", groups="-", up=0, dn=0, ok=False)
        EV[kk] = (s, p)
        log(dict(id=f"T1-{Y}-{len(EV)}", task="T1-select", name=key(cfg), params=json.dumps(cfg), window=f"{ST}..{Y}-01-01", SR=round(s["SR"], 3),
                 bp_day=round(s["bp"], 2), mdd2=round(s["mdd2"], 2), t_vs_LIVE=round(p["t"], 2), years=p["years"], groups=p["groups"],
                 regime_up_dn=f"{p['up']:.2f}/{p['dn']:.2f}", pass_vs_LIVE=p["ok"], note=pipe))
    return EV[kk]
def best(cands, Y, pipe, keep=None):
    """best SR among candidates passing vs LIVE on the selection window; `keep` (already-adopted cfg) competes if != LIVE."""
    P = [c for c in cands if c != LIVE and ev(c, Y, pipe)[1]["ok"]]
    if keep is not None and keep != LIVE and keep not in P: P.append(keep)
    return max(P, key=lambda c: ev(c, Y, pipe)[0]["SR"]) if P else None
def pipe_A(Y):   # independent 1-D sweeps from LIVE -> combine winners -> weighting (mirrors the historical path)
    win_ = {}
    for dim, vals in DIMS[:3]:
        b = best([with_(LIVE, dim, v) for v in vals], Y, "A-1D"); win_[dim] = b
    combo = dict(LIVE)
    for dim, _ in DIMS[:3]:
        if win_[dim] is not None:
            for f in (["N", "NS"] if dim == "N" else [dim]): combo[f] = win_[dim][f]
    if combo != LIVE and not ev(combo, Y, "A-combo")[1]["ok"]:
        combo = best([c for c in win_.values() if c is not None], Y, "A-fallback") or dict(LIVE)
    pick = best([with_(combo, "w", v) for v in WW], Y, "A-weight", keep=combo)
    return pick or dict(LIVE), win_, combo
def pipe_S(Y):   # sequential greedy: sf -> stop -> N -> weighting, each step conditional on the previous pick
    cur = dict(LIVE); path = []
    for dim, vals in DIMS:
        b = best([with_(cur, dim, v) for v in vals], Y, "S-" + dim, keep=cur)
        if b is not None: cur = b
        path.append(key(cur))
    return cur, path
res = {}
for Y in (2023, 2024, 2025, 2026):
    pA, winA, comboA = pipe_A(Y); pS, pathS = pipe_S(Y)
    res[Y] = dict(A=pA, A_1d={k: (key(v) if v else None) for k, v in winA.items()}, A_combo=key(comboA), S=pS, S_path=pathS)
    print(Y, "A pick", key(pA), "| 1D", res[Y]["A_1d"], "combo", key(comboA), "| S pick", key(pS), pathS, flush=True)
pickle.dump(dict(res=res, EV={f"{k[0]}|{k[1]}": v for k, v in EV.items()}), open(f"{OUT}/t1_select.pkl", "wb"))
