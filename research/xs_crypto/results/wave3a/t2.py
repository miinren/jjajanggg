# TASK 2: realistic per-coin costs, stop slippage, funding checks for LIVE, B, B-MV (8-clock averages).
from lib3 import *
# --- calibrate k: median held name (LIVE, clock 0, all rebalances 2020-03-15..2025) costs 5.5 bp
held = []; ext4.book(D, S0, offset=0, IQ=IQ, held=held, dayb=DAYB)
reb_idx = D.idx[((D.idx.hour + 1) % 8 == 0)]
med_iq = float(np.median(np.concatenate(held))); K1 = 2.5 / med_iq
print("median held IQ %.4f -> median held 24h vol $%.1fM ; k=%.2f bp*sqrt($M)" % (med_iq, 1 / med_iq**2, K1))
books = {"LIVE": run(LIVE), "B": run(Bc), "B-MV": run(BMV)}
a, b = ST, "2026-01-01"
def gross(df): return df.net + df.to * h.COST
SETTINGS = {"flat5.5": dict(k=None, X=0, f2=False)}
for k_lab, k in (("k", K1), ("2k", 2 * K1)): SETTINGS[f"pc_{k_lab}"] = dict(k=k, X=0, f2=False)
for X in (0.005, 0.01, 0.02): SETTINGS[f"flat5.5+slip{X*100:g}%"] = dict(k=None, X=X, f2=False)
SETTINGS["pc_k+slip1%"] = dict(k=K1, X=0.01, f2=False)
SETTINGS["pc_2k+slip2%"] = dict(k=2 * K1, X=0.02, f2=False)
SETTINGS["flat5.5+fund_sameday"] = dict(k=None, X=0, f2=True)
SETTINGS["pc_2k+slip2%+fund_sameday"] = dict(k=2 * K1, X=0.02, f2=True)
def netof(df, s):
    g = gross(df)
    if s["f2"]: g = g - df.fund + df.fund2
    c = df.to * h.COST if s["k"] is None else df.to * 3e-4 + df.tinv * s["k"] * 1e-4
    return g - c - s["X"] * df.slip_s
rows = []
for sl, s in SETTINGS.items():
    nets = {n: netof(df, s) for n, (df, cm) in books.items()}
    for n, (df, cm) in books.items():
        st = wstats(df, a, b, net=nets[n]); x = nets[n][(nets[n].index >= a) & (nets[n].index < b)]
        yr = x.groupby(x.index.year).apply(srx)
        effc = (df.to * 3 + df.tinv * s["k"]).sum() / df.to.sum() if s["k"] else 5.5
        r = dict(setting=sl, book=n, SR=st["SR"], bp=st["bp"], mdd2=st["mdd2"], minYrSR=yr.min(), eff_cost_bp=effc)
        for ref in ("LIVE", "B"):
            if n != ref:
                dx, dr = x, nets[ref][(nets[ref].index >= a) & (nets[ref].index < b)]
                dd = dx * dr.std() / dx.std() - dr; r[f"t_vs_{ref}"] = h.nw_t(dd); r[f"d_bp_vs_{ref}"] = dd.mean() * 1e4
                r[f"yrs_vs_{ref}"] = int((dd.groupby(dd.index.year).mean() > 0).sum())
        rows.append(r)
        p = ptest(books[n], books["LIVE"], a, b) if n != "LIVE" else None
        log(dict(id=f"T2-{sl}-{n}", task="T2-costs", name=n, params=json.dumps(s), window=f"{a}..{b}", SR=round(st["SR"], 3), bp_day=round(st["bp"], 2),
                 mdd2=round(st["mdd2"], 2), t_vs_LIVE=round(r.get("t_vs_LIVE", np.nan), 2), years=f"{r.get('yrs_vs_LIVE', '-')}/6", groups=(p["groups"] if p else "-"),
                 regime_up_dn="-", pass_vs_LIVE="-", note=f"eff_cost {effc:.2f}bp; coin groups are gross-of-cost"))
R = pd.DataFrame(rows); pd.set_option("display.width", 250); print(R.round(2).to_string())
# --- turnover / stop stats and funding by year
aux = {}
for n, (df, cm) in books.items():
    x = df[(df.index >= a) & (df.index < b)]
    aux[n] = dict(to_day=x.to.mean(), stop_s_day=x.slip_s.mean(), stop_l_day=x.slip_l.mean(),
                  fund_yr=(x.fund.groupby(x.index.year).mean() * 1e4).round(2).to_dict(), fund2_yr=(x.fund2.groupby(x.index.year).mean() * 1e4).round(2).to_dict(),
                  net_yr=(x.net.groupby(x.index.year).mean() * 1e4).round(2).to_dict(),
                  fund_share=x.fund.sum() / x.net.sum(), corr_f_f2=np.corrcoef(x.fund, x.fund2)[0, 1])
    print(n, aux[n])
# funding guard check: how often the guard removes a would-be short (LIVE clock 0 top-20 jumpy names)
Fg = D.FND; E = np.array(D.M & D.idio(336).notna() & D.bB.notna(), bool); E[:, D.ib] = False; SC = np.asarray(S0, float)
blk = []; tot = []
for i in np.flatnonzero(((D.idx.hour + 1) % 8 == 0) & (D.idx >= ST)):
    el = np.flatnonzero(E[i] & np.isfinite(SC[i]))
    if len(el) < 40: continue
    top = el[np.argsort(-SC[i, el], kind="stable")][:20]; blk.append((Fg[i, top] < -5e-4).sum()); tot.append(20)
print("guard blocks %.2f of top-20 jumpy names per rebalance (%.1f%%)" % (np.mean(blk), 100 * np.sum(blk) / np.sum(tot)))
pickle.dump(dict(R=R, aux=aux, K1=K1, med_iq=med_iq, guard=np.mean(blk)), open(f"{OUT}/t2.pkl", "wb"))
