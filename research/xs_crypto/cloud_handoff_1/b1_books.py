# 12 pre-registered book trials on DEV (2 signals x 3 constructions x 2 rebalance), each averaged over 4 clock offsets.
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, '.')
from common1 import *
from books1 import *
m, D, R, U, ew, btc, B = setup()
ew_d = np.log1p(ew.fillna(0)).resample('D').sum().pipe(np.expm1); btc_d = np.log1p(btc.fillna(0)).resample('D').sum().pipe(np.expm1)
rows, daily = [], {}
for sig in ('B_EW', 'B_BTC'):
    for cons in ('C_RAW', 'C_HEDGE', 'C_BAB'):
        for every in (24, 48):
            k = f'{sig}|{cons}|{every}h'
            d = avg_offsets(m, B, sig, cons, every, *DEV); daily[k] = d
            mt = P.metrics(d, boot=True); a = alpha_stats(d.net, ew_d, btc_d)
            yr = d.net.groupby(d.index.year).apply(lambda v: v.mean() / v.std() * np.sqrt(365)).round(2).to_dict()
            rows.append(dict(trial=k, sharpe=mt['sharpe'], t_nw=mt['t_nw'], boot_p=mt['boot_p'], net_bp=d.net.mean() * 1e4,
                             gross_bp=d.gross.mean() * 1e4, fund_bp=d.fund.mean() * 1e4, cost_bp=d.cost.mean() * 1e4, to=d.turnover.mean(),
                             net_exp=d.net_exp.mean(), maxdd=mt['maxdd'], worst_day=mt['worst_day'], **a, yearly=yr))
            print({x: (round(y, 3) if isinstance(y, float) else y) for x, y in rows[-1].items()}, flush=True)
out = pd.DataFrame(rows); out.to_csv('b1_books_dev.csv', index=False)
pickle.dump(daily, open('b1_daily_dev.pkl', 'wb'))
srs = out.sharpe.values
print('trial SR var (ann):', np.var(srs))
fam = {k: v.net for k, v in daily.items()}
wf = P.walk_forward(fam, ['2021-01-01', '2022-01-01', '2023-01-01', '2024-01-01'], embargo_days=30)
print('walk-forward: SR %.2f t %.2f picks %s' % (wf['sharpe'], wf['t_nw'], wf['picks']))
