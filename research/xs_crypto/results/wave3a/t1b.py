# TASK 1 scoring: each pipeline's pick (selected on < Y) vs LIVE on year Y only.
from lib3 import *
S = pickle.load(open(f"{OUT}/t1_select.pkl", "rb")); res = S["res"]; Lr = run(LIVE)
def score(cfg, Y, sel_a=ST):
    r = run(cfg); a, b = f"{Y}-01-01", f"{Y+1}-01-01"; s = wstats(r[0], a, b); l = wstats(Lr[0], a, b)
    x = r[0].net[(r[0].index >= a) & (r[0].index < b)]; y = Lr[0].net[(Lr[0].index >= a) & (Lr[0].index < b)]
    # risk-match using the SELECTION-window vol ratio (known ex ante)
    xs = r[0].net[(r[0].index >= sel_a) & (r[0].index < a)]; ys = Lr[0].net[(Lr[0].index >= sel_a) & (Lr[0].index < a)]; k = ys.std() / xs.std()
    return dict(SR=s["SR"], SR_L=l["SR"], dSR=s["SR"] - l["SR"], bp=s["bp"], bp_L=l["bp"], dbp=s["bp"] - l["bp"], t_raw=h.nw_t(x - y),
                t_rm=h.nw_t(x * k - y), dbp_rm=(x * k - y).mean() * 1e4, mdd2=s["mdd2"], mdd2_L=l["mdd2"], mdd_bp=s["mdd_bp"], mdd_bp_L=l["mdd_bp"])
rows = []; chains = {"A": [], "S": [], "B": [], "B-MV": []}
for Y in (2023, 2024, 2025):
    for lab, cfg in (("A", res[Y]["A"]), ("S", res[Y]["S"]), ("B", Bc), ("B-MV", BMV)):
        sc = score(cfg, Y); rows.append(dict(Y=Y, pipe=lab, pick=key(cfg), **sc))
        r = run(cfg)[0]; chains[lab].append(r.net[r.index.year == Y] * (1 if lab in ("B", "B-MV") else 1))
        if lab in ("A", "S"):
            log(dict(id=f"T1-test-{Y}-{lab}", task="T1-test", name=key(cfg), params=json.dumps(cfg), window=f"{Y}", SR=round(sc["SR"], 3), bp_day=round(sc["bp"], 2),
                     mdd2=round(sc["mdd2"], 2), t_vs_LIVE=round(sc["t_raw"], 2), years="-", groups="-", regime_up_dn="-", pass_vs_LIVE="-",
                     note=f"pipeline {lab} pick; LIVE SR {sc['SR_L']:.2f} bp {sc['bp_L']:.2f}; t_riskmatched {sc['t_rm']:.2f}"))
R = pd.DataFrame(rows); pd.set_option("display.width", 250); print(R.round(2).to_string())
y = Lr[0].net[(Lr[0].index >= "2023-01-01") & (Lr[0].index < "2026-01-01")]
for lab, ch in chains.items():
    s = pd.concat(ch); print(f"pooled 2023-25 {lab}: SR {srx(s):.2f} vs LIVE {srx(y):.2f}; dbp {1e4*(s-y).mean():.2f}; t {h.nw_t(s-y):.2f}")
for Y in (2023, 2024, 2025, 2026): print(Y, res[Y])
pickle.dump(dict(R=R), open(f"{OUT}/t1_test.pkl", "wb"))
