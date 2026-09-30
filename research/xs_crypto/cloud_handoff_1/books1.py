"""Book constructions for Task A on pf_lib accounting. C_RAW / C_HEDGE via pf_lib.backtest; C_BAB via custom targets
run through the same pf_lib simulation + cost code (run_targets mirrors pf_lib.backtest after target construction)."""
import numpy as np, pandas as pd, math
from dataclasses import asdict
from common1 import P, PC

BASE = dict(scheme='ivol', q=0.2, delay=1, beta_neutral=False, fee_bp=5.0, name_cap=1.0, adv_frac=0.0, aum=1.5e4, impact_Y=0.5)

def run_targets(mkt, Wt, cfg, start, end):
    """Wt: (T,K) targets at rebalance rows (NaN elsewhere). Same execution/cost/funding code path as pf_lib.backtest."""
    idx = mkt['idx']; T, K = Wt.shape
    R = np.asarray(mkt['R'], float); F = np.asarray(mkt['F'], float)
    vol = mkt['_vol']; beta = mkt['_beta']; adv = np.asarray(mkt['adv'], float); hs = np.asarray(mkt['hs_bp'], float) / 1e4
    lo = int(np.searchsorted(idx, pd.Timestamp(start))); hi = int(np.searchsorted(idx, pd.Timestamp(end)))
    Wt = Wt.copy(); Wt[:lo] = np.nan; Wt[hi:] = np.nan
    eff = np.full((T, K), np.nan); eff[cfg.delay:] = Wt[:-cfg.delay]
    eff[:lo] = np.nan
    if hi < T: eff[hi:] = np.nan; eff[hi] = 0.0
    stopmask = np.ones(K, bool)
    Wh, dW = P._simulate(eff, R, True, None, stopmask)
    gross = (Wh * R).sum(1); fund = -(Wh * F).sum(1); to = dW.sum(1)
    sig_d = np.nan_to_num(vol) * np.sqrt(24)
    with np.errstate(invalid='ignore', divide='ignore'):
        part = np.where(adv > 0, dW * cfg.aum / adv, 0.0)
    impact = cfg.impact_Y * sig_d * np.sqrt(np.clip(part, 0, None))
    unit = cfg.fee_bp / 1e4 + np.nan_to_num(hs, nan=8e-4) + np.nan_to_num(impact)
    cost = (dW * unit).sum(1); net = gross + fund - cost
    h = pd.DataFrame({'gross': gross, 'fund': fund, 'cost': cost, 'net': net, 'turnover': to, 'gross_exp': np.abs(Wh).sum(1),
                      'net_exp': Wh.sum(1), 'beta_exp': (Wh * np.nan_to_num(beta)).sum(1), 'lev': 1.0,
                      'n_long': (Wh > 0).sum(1), 'n_short': (Wh < 0).sum(1)}, index=idx).iloc[lo:hi]
    d = h.resample('D').agg({'gross': 'sum', 'fund': 'sum', 'cost': 'sum', 'net': 'sum', 'turnover': 'sum', 'gross_exp': 'mean',
                             'net_exp': 'mean', 'beta_exp': 'mean', 'lev': 'mean', 'n_long': 'mean', 'n_short': 'mean'})
    return P.BTResult(cfg, h, d[d.gross_exp > 0])

def bab_targets(mkt, Bm, every, offset, q=0.2, lev_cap=3.0):
    idx = mkt['idx']; cols = mkt['cols']; T, K = len(idx), len(cols)
    U = np.asarray(mkt['univ'], bool).copy()
    for c in mkt['exclude_rank']:
        if c in cols: U[:, cols.index(c)] = False
    vol = mkt['_vol']; Bv = Bm.to_numpy()
    hours = np.asarray((idx - pd.Timestamp(0)) // pd.Timedelta('1h'), dtype=np.int64)
    reb = (hours + 1 - offset) % every == 0
    Wt = np.full((T, K), np.nan)
    for i in np.flatnonzero(reb):
        el = np.flatnonzero(U[i] & np.isfinite(Bv[i]) & np.isfinite(vol[i]) & (vol[i] > 0))
        w = np.zeros(K)
        if len(el) >= 10:
            n = max(1, int(math.floor(q * len(el)))); o = el[np.argsort(Bv[i, el], kind='stable')]
            lo_b, hi_b = o[:n], o[-n:]
            wl = (1 / vol[i, lo_b]); wl /= wl.sum(); ws = (1 / vol[i, hi_b]); ws /= ws.sum()
            bl = float(wl @ Bv[i, lo_b]); bh = float(ws @ Bv[i, hi_b])
            if bl > 0.05 and bh > 0.05:
                kl = min(1 / bl, lev_cap); kh = min(1 / bh, lev_cap)
                w[lo_b] = wl * kl; w[hi_b] = -ws * kh
                w /= np.abs(w).sum()
        Wt[i] = w
    return Wt

def run_book(mkt, B, sig, cons, every, offset, start, end):
    if cons == 'C_BAB':
        cfg = P.PFConfig(**{**BASE, 'every_h': every, 'offset_h': offset, 'label': f'{sig}_{cons}_{every}'})
        return run_targets(mkt, bab_targets(mkt, B[sig], every, offset), cfg, start, end)
    kw = {**BASE, 'every_h': every, 'offset_h': offset, 'hedge': 'BTCUSDT' if cons == 'C_HEDGE' else None, 'label': f'{sig}_{cons}_{every}'}
    return P.backtest(mkt, -B[sig], P.PFConfig(**kw), start=start, end=end)

def avg_offsets(mkt, B, sig, cons, every, start, end, offsets=None):
    offsets = offsets or [0, every // 4, every // 2, 3 * every // 4]
    dd = None
    for o in offsets:
        d = run_book(mkt, B, sig, cons, every, o, start, end).daily
        dd = d / len(offsets) if dd is None else dd.add(d / len(offsets), fill_value=0)
    return dd

def alpha_stats(net, ew_d, btc_d):
    df = pd.concat([net.rename('y'), btc_d.rename('b'), ew_d.rename('e')], axis=1).dropna()
    X = np.c_[np.ones(len(df)), df.b, df.e]; coef, *_ = np.linalg.lstsq(X, df.y.values, rcond=None)
    resid_alpha = df.y.values - X[:, 1:] @ coef[1:]
    bb = np.polyfit(df.b, df.y, 1)[0]; be = np.polyfit(df.e, df.y, 1)[0]
    return dict(alpha_bp=coef[0] * 1e4, alpha_t=P.nw_t(resid_alpha), beta_btc_multi=coef[1], beta_ew_multi=coef[2], beta_btc=bb, beta_ew=be)
