# Finalist (pre-registered rule): best dev SR among C_HEDGE/C_BAB with |ex-post beta| < 0.2 to BTC and EW -> B_EW|C_BAB|48h.
# Dev deflated SR, then ONE-LOOK 2025 holdout via pf_lib.holdout_once.
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, '.')
from common1 import *
from books1 import *
from scipy import stats
dev = pd.read_csv('b1_books_dev.csv'); daily = pickle.load(open('b1_daily_dev.pkl', 'rb'))
q = dev[dev.trial.str.contains('C_HEDGE|C_BAB') & (dev.beta_btc_multi.abs() < 0.2) & (dev.beta_ew_multi.abs() < 0.2)]
fin = q.sort_values('sharpe', ascending=False).iloc[0]; key = fin.trial; print('finalist', key, 'dev SR %.3f alpha_t %.2f' % (fin.sharpe, fin.alpha_t))
x = daily[key].net
dsr = P.deflated_sharpe(fin.sharpe, len(x), 1012, float(np.var(dev.sharpe)), float(stats.skew(x)), float(stats.kurtosis(x, fisher=False)))
print('deflated SR prob (N=1012): %.4f' % dsr)
yrs = x.groupby(x.index.year).apply(lambda v: v.mean() / v.std() * np.sqrt(365)).round(2).to_dict(); print('dev yearly SR', yrs)
m, D, R, U, ew, btc, B = setup()
ew_d = np.log1p(ew.fillna(0)).resample('D').sum().pipe(np.expm1); btc_d = np.log1p(btc.fillna(0)).resample('D').sum().pipe(np.expm1)
sig, cons, ev = key.split('|'); every = int(ev[:-1])
def fn():
    d = avg_offsets(m, B, sig, cons, every, *HOLD)
    mt = P.metrics(d, boot=True); a = alpha_stats(d.net, ew_d, btc_d)
    print('HOLDOUT 2025:', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in {**mt, **a}.items()}, flush=True)
    print('  net %.2f bp/d gross %.2f fund %.2f cost %.2f' % (d.net.mean() * 1e4, d.gross.mean() * 1e4, d.fund.mean() * 1e4, d.cost.mean() * 1e4))
    print('  monthly net %%:', (d.net.resample('ME').sum() * 100).round(2).to_dict())
    d.to_pickle('h1_holdout_daily.pkl')
    return mt
P.holdout_once('cloud1_' + key.replace('|', '_') + '_2025', fn, note='Task A BAB finalist, one look')
