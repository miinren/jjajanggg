# F00 DIAGNOSTIC: residual return by hour of day (phase vs 00/08/16 UTC funding settlement) for funding / score groups inside M.
# Group return at row j = mean over the group of resid[j] minus the M-average resid[j]. Group membership uses F (prior-day
# funding, known) and S0 at row j-1 (known before bar j). Index convention: row label = bar timestamp as stored.
from lib3c import *
M = D.M.to_numpy(); F = D.F.to_numpy(); S = S0.to_numpy(); R = D.resid.to_numpy()
T = len(D.idx); hr = D.idx.hour.to_numpy()
def grp_series(mask_prev):
    out = np.full(T, np.nan)
    for j in range(1, T):
        m = M[j - 1] & np.isfinite(R[j]); g = mask_prev[j - 1] & m
        if g.sum() >= 3 and m.sum() >= 20: out[j] = np.nanmean(R[j, g]) - np.nanmean(R[j, m])
    return out
Fm = np.where(M, F, np.nan); Sm = np.where(M, S, np.nan)
q80 = np.nanquantile(Fm, 0.8, axis=1)[:, None]; q20 = np.nanquantile(Fm, 0.2, axis=1)[:, None]
rkS = pd.DataFrame(Sm).rank(1, ascending=False).to_numpy(); rkL = pd.DataFrame(Sm).rank(1).to_numpy()
G = {"fund_top20%": Fm >= q80, "fund_top20%_pos": (Fm >= q80) & (Fm > 1e-4), "fund_bot20%": Fm <= q20,
     "S0_top20(short cands)": rkS <= 20, "S0_bot12(long cands)": rkL <= 12}
hi = D.idx >= pd.Timestamp(ST)
rows = []
for k, m in G.items():
    s = pd.Series(grp_series(m), index=D.idx)[hi]
    for hh in range(24):
        x = s[s.index.hour == hh].dropna()
        rows.append(dict(group=k, hour=hh, phase=hh % 8, bp=x.mean() * 1e4, t=h.nw_t(x.to_numpy(), 5), n=len(x)))
    print(k, "done", flush=True)
R_ = pd.DataFrame(rows); R_.to_csv("f00_phase_by_hour.csv", index=False)
ph = R_.groupby(["group", "phase"]).apply(lambda d: pd.Series(dict(bp=d.bp.mean(), t=d.t.sum() / np.sqrt(3)))).reset_index()
print(R_.pivot(index="hour", columns="group", values="bp").round(2).to_string())
print(R_.pivot(index="hour", columns="group", values="t").round(1).to_string())
print(ph.pivot(index="phase", columns="group", values="bp").round(2).to_string())
print(ph.pivot(index="phase", columns="group", values="t").round(1).to_string())
