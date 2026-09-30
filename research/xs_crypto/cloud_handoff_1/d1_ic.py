# D1 IC decay + beta-adjusted IC + half-life; D2 Fama-MacBeth SML test. DEV only (labels end before 2025-01-01).
import sys, numpy as np, pandas as pd
sys.path.insert(0, '.')
from common1 import *
from scipy.optimize import curve_fit
m, D, R, U, ew, btc, B = setup()
idx = m['idx']; T = len(idx)
univ = pd.DataFrame(m['univ'], idx, m['cols'])
F = pd.DataFrame(m['F'], idx, m['cols'])
CL = np.log1p(R.fillna(0)).cumsum(); CF = F.fillna(0).cumsum()
CLe = np.log1p(ew.fillna(0)).cumsum(); CLb = np.log1p(btc.fillna(0)).cumsum()
H = [1, 4, 12, 24, 48, 72, 120, 168, 336]
end_dev = pd.Timestamp(DEV[1]); start = pd.Timestamp(DEV[0])
rows = []; slopes = {}
def ic_row(sig_name, Bm, mk_cl):
    out = []
    for h in H:
        step = 8 if h <= 24 else 24
        ts = np.arange(0, T - h - 2, step)
        ts = ts[(idx[ts] >= start) & (idx[ts + 1 + h] < end_dev)]
        ICp, ICs, ICpa, ICsa, SL = [], [], [], [], []
        for t in ts:
            el = univ.iloc[t].to_numpy() & np.isfinite(Bm.iloc[t].to_numpy())
            if el.sum() < 15: continue
            s = -Bm.iloc[t].to_numpy()[el]
            f = (np.exp(CL.iloc[t + h].to_numpy() - CL.iloc[t].to_numpy()) - 1)[el] - (CF.iloc[t + h].to_numpy() - CF.iloc[t].to_numpy())[el]
            fm = np.exp(mk_cl.iloc[t + h] - mk_cl.iloc[t]) - 1
            fa = f - (-s) * fm                                   # beta-adjusted forward return
            z = np.clip((s - s.mean()) / (s.std() + 1e-12), -3, 3)
            def clipm(v):
                md = np.median(v); mad = np.median(np.abs(v - md)) + 1e-12; return np.clip(v, md - 5 * mad * 1.4826, md + 5 * mad * 1.4826)
            fc, fac = clipm(f), clipm(fa)
            ICp.append(np.corrcoef(z, fc)[0, 1]); ICpa.append(np.corrcoef(z, fac)[0, 1])
            rs = pd.Series(s).rank().to_numpy()
            ICs.append(np.corrcoef(rs, pd.Series(f).rank().to_numpy())[0, 1]); ICsa.append(np.corrcoef(rs, pd.Series(fa).rank().to_numpy())[0, 1])
            SL.append(np.polyfit(z, fc, 1)[0] * 1e4)
        L = int(np.ceil(1.5 * h / step)) + 1
        for nm, v in (('pearson', ICp), ('spearman', ICs), ('pearson_betaadj', ICpa), ('spearman_betaadj', ICsa), ('slope_bp_per_sd', SL)):
            v = np.array(v); out.append(dict(signal=sig_name, h=h, metric=nm, mean=v.mean(), t_nw=P.nw_t(v, L), n=len(v), n_eff=len(v) * step / h))
        slopes[(sig_name, h)] = np.mean(SL)
        print(sig_name, h, 'done', flush=True)
    return out
for nm, mk in (('B_EW', CLe), ('B_BTC', CLb)):
    rows += ic_row(nm, B[nm], mk)
res = pd.DataFrame(rows); res.to_csv('d1_ic_decay.csv', index=False)
print(res.pivot_table(index=['signal', 'h'], columns='metric', values='mean').round(4).to_string())
print(res.pivot_table(index=['signal', 'h'], columns='metric', values='t_nw').round(2).to_string())
# half-life
f = lambda h, A, tau: A * tau * (1 - np.exp(-h / tau))
for nm in ('B_EW', 'B_BTC'):
    b = np.array([slopes[(nm, h)] for h in H])
    try:
        (A, tau), _ = curve_fit(f, np.array(H, float), b, p0=[b[0], 48], bounds=([-1e3, 1], [1e3, 5000]))
        print(nm, 'half-life fit: A=%.3f bp/h/sd tau=%.0fh half-life=%.0fh' % (A, tau, tau * np.log(2)), 'slopes', np.round(b, 2))
    except Exception as e:
        print(nm, 'fit failed', e, np.round(b, 2))
# D2 Fama-MacBeth SML test at 1d, daily non-overlapping grid (hour 0)
fm = []
for nm, mk in (('B_EW', CLe), ('B_BTC', CLb)):
    Bm = B[nm]; lam, mret, dts = [], [], []
    for t in np.flatnonzero((idx.hour == 0) & (idx >= start) & (idx < end_dev - pd.Timedelta('2D'))):
        if t + 25 >= T: break
        el = univ.iloc[t].to_numpy() & np.isfinite(Bm.iloc[t].to_numpy())
        if el.sum() < 15: continue
        b = Bm.iloc[t].to_numpy()[el]
        f1 = (np.exp(CL.iloc[t + 24].to_numpy() - CL.iloc[t].to_numpy()) - 1)[el] - (CF.iloc[t + 24].to_numpy() - CF.iloc[t].to_numpy())[el]
        lam.append(np.polyfit(b, f1, 1)[0]); mret.append(np.exp(mk.iloc[t + 24] - mk.iloc[t]) - 1); dts.append(idx[t])
    lam, mret = np.array(lam), np.array(mret)
    X = np.c_[np.ones(len(mret)), mret]; coef, *_ = np.linalg.lstsq(X, lam, rcond=None); e = lam - X @ coef
    g_series = lam - coef[1] * mret
    print(nm, 'FM: mean lambda %.2f bp/d (t %.2f); mean mkt %.2f bp/d; gamma %.2f bp/d (t %.2f); delta %.3f' % (
        lam.mean() * 1e4, P.nw_t(lam, 5), mret.mean() * 1e4, coef[0] * 1e4, P.nw_t(g_series, 5), coef[1]))
    s = pd.Series(g_series, index=dts)
    print('   gamma by year (bp/d, t):', {y: (round(v.mean() * 1e4, 2), round(P.nw_t(v.values, 5), 2)) for y, v in s.groupby(s.index.year)})
    fm.append(dict(signal=nm, mean_lambda_bp=lam.mean() * 1e4, t_lambda=P.nw_t(lam, 5), gamma_bp=coef[0] * 1e4, t_gamma=P.nw_t(g_series, 5), delta=coef[1], n=len(lam)))
pd.DataFrame(fm).to_csv('d2_fm_sml.csv', index=False)
