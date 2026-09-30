# T19/T20 one-step check on the final pick (N=6, N=10 around B-MV-N8); D1 long-leg economics; D2 pumped-shorts event study.
from lib4 import *
from tabulate import tabulate
import numpy.linalg as la
base = run8("T07_s1", keep_coin=True)
for tid, n in (("T19", 6), ("T20", 10)):
    o = run8(f"{tid}_s3", keep_coin=True, N=n, NS=20, stop=0.2, leg_weights=minvar_floor); r = ptest(o, base, ST, "2026-01-01"); x = row(f"{tid} N={n}", o)
    print(f"{tid} N={n}: SR {x['SR']:.3f} @8 {x['SR8']:.3f} @12 {x['SR12']:.3f} mdd2 {x['mdd2']:.1f} minYr {x['minYr']:.2f} yearly {x['yearly']} | vs N=8 t {r['t']:.2f} yrs {r['years']} grp {r['groups']}")

# ---------- D1: long-leg economics ----------
g = np.expm1(D.Rn); ib, ie = D.ib, D.cols.index("ETHUSDT")
Mn = D.M.to_numpy()
alt = np.where(Mn, g, np.nan); alt = np.nanmean(alt, 1)
F = pd.DataFrame({"BTC": g[:, ib], "ETH": g[:, ie], "ALT": np.nan_to_num(alt)}, index=D.idx).resample("D").sum()
F = cut(F)
def reg(y, cols):
    y = cut(y).reindex(F.index); X = np.column_stack([np.ones(len(y))] + [F[c].to_numpy() for c in cols]); b = la.lstsq(X, y.to_numpy(), rcond=None)[0]
    e = y.to_numpy() - X @ b; r2 = 1 - e.var() / y.var()
    t_a = h.nw_t(pd.Series(e + b[0]))            # NW t of alpha (residual + intercept)
    return dict(alpha_bp=b[0] * 1e4, t_alpha=t_a, **{f"b_{c}": v for c, v in zip(cols, b[1:])}, R2=r2)
rows = []
for tag, lab in (("T06_s1", "B-MV"), ("T07_s1", "B-MV-N8"), ("T02_s1", "LO12"), ("LIVE_s1", "LIVE")):
    df = run8(tag, keep_coin=True)["df"]; gl = {"B-MV": 0.45, "B-MV-N8": 0.45, "LO12": 1.0, "LIVE": 0.5}[lab]
    for leg, y in (("long (per $ long)", df.long / gl), ("long+fund_l (per $)", (df.long + df.fund_l) / gl), ("short", df.short), ("hedge", df.hedge),
                   ("long+short+hedge (pre-fund, pre-cost)", df.long + df.short + df.hedge), ("net", df.net)):
        for cols in (["BTC", "ETH"], ["BTC", "ETH", "ALT"]):
            rows.append(dict(book=lab, series=leg, factors="+".join(cols), **reg(y, cols)))
print(tabulate(pd.DataFrame(rows).round(3), headers="keys", showindex=False, tablefmt="github"))
# funding split (bp/day)
for tag, lab in (("T06_s1", "B-MV"), ("T07_s1", "B-MV-N8"), ("T02_s1", "LO12")):
    df = cut(run8(tag)["df"]); print(f"{lab}: funding total {df.fund.mean()*1e4:.2f} = long {df.fund_l.mean()*1e4:.2f} + short&hedge {df.fund_s.mean()*1e4:.2f} bp/day; long price {df.long.mean()*1e4:.2f}")

# ---------- D2: pumped shorts (live rules, short stop disabled, clock 0) ----------
TH = [0.0, 0.2, 0.3, 0.5, 0.75, 1.0]
for lab, kw in (("LIVE rules", dict()), ("B-MV rules", dict(N=12, NS=20, short_frac=0.55, leg_weights=minvar_floor))):
    L = dict(th=TH, seen=set(), ev=[])
    ext5.book(D, S0, offset=0, **{**REAL, **kw, "stop": 100.0}, log_short=L)
    lp = np.log(D.R1.fillna(0).to_numpy().cumsum(0)[:, :] + 0) if False else None
    CL = np.nan_to_num(D.R1.to_numpy()).cumsum(0); B = D.B; T = len(D.idx)
    out = []
    for th in TH:
        ev = [(i, s) for (i, s, t) in L["ev"] if t == th and i + 2 + 168 < T]
        if not ev: continue
        r = {}
        for H in (24, 72, 168):
            fr = np.array([np.expm1(CL[i + 2 + H, s] - CL[i + 2, s]) for i, s in ev])
            fb = np.array([np.expm1(CL[i + 2 + H, ib] - CL[i + 2, ib]) for i, s in ev])
            rr = fr - np.array([B[i, s] for i, s in ev]) * fb
            r[H] = (fr.mean() * 100, np.median(fr) * 100, rr.mean() * 100)
        up72 = np.array([np.expm1((CL[i + 3:i + 2 + 73, s] - CL[i + 2, s]).max()) for i, s in ev])
        f7 = np.array([np.expm1(CL[i + 2 + 168, s] - CL[i + 2, s]) for i, s in ev])
        out.append(dict(adverse_move=f"+{int(th*100)}%", n=len(ev), fwd24_mean=r[24][0], fwd72_mean=r[72][0], fwd7d_mean=r[168][0], fwd7d_median=r[168][1],
                        fwd7d_beta_adj=r[168][2], P_further20_in72h=(up72 >= 0.2).mean() * 100, P_fall20_in7d=(f7 <= -0.2).mean() * 100))
    print(f"\nD2 {lab} (short stop off, clock 0): forward simple return of the coin after a short first reaches the adverse move (%, + = bad for the short)")
    print(tabulate(pd.DataFrame(out).round(2), headers="keys", showindex=False, tablefmt="github"))
