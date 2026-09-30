# (1) ext5 with new options off == wave3c ext4 bit for bit (B-MV + W06, simple+drift, offset 3)
# (2) 8-clock B-MV+W06 realistic reproduces Wave R SR 1.490 (hedge_fund off), then report with hedge funding on
# (3) synthetic check of drift/simple accounting: 2 coins 50/50 long, no hedge/costs/stops -> NAV over each 8h window
#     must equal the buy-and-hold value 0.5*PA1/PA0 + 0.5*PB1/PB0 (to first order in the hourly compounding of summed P&L)
from lib4 import *
import ext4
RB = dict(N=12, NS=20, short_frac=0.55, stop=0.2, leg_weights=minvar_floor, hedge_band=0.03, simple=True, drift=True)
a, _ = ext4.book(D, S0, offset=3, **RB); b, _ = ext5.book(D, S0, offset=3, **RB)
print("(1) max |net diff| ext4 vs ext5:", float((a.net - b.net).abs().max()))
o = run8("BMV_nohf", keep_coin=False, hedge_fund=False, N=12, NS=20, stop=0.2, leg_weights=minvar_floor)
print("(2) B-MV+W06 realistic, no hedge funding: SR %.3f (Wave R 1.490)" % srx(cut(o["df"].net)))
# (3) synthetic: hourly P&L within a window, compounded, vs buy-and-hold of the same two coins
import numpy as np
cols = [D.cols.index(c) for c in ("SOLUSDT", "ADAUSDT", "XRPUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT")]
el = pd.DataFrame(False, index=D.idx, columns=D.cols); el.iloc[:, cols] = True
sc = pd.DataFrame(np.nan, index=D.idx, columns=D.cols); sc.iloc[:, cols] = np.arange(6)[None, :].astype(float)   # SOL, ADA lowest
d, cm = ext5.book(D, sc, N=2, NS=1, short_frac=0.0, stops=False, hedge=0.0, cost=0.0, elig=el, simple=True, drift=True, keepx=0.0)
hr = pd.Series(np.asarray(cm).sum(1), index=D.idx)   # hourly P&L = sum_c w_c * simple_r
C = np.exp(D.R1.iloc[:, cols[:2]].fillna(0).cumsum())
reb = np.flatnonzero((D.idx.hour + 1) % 8 == 0); errs = []
for i0 in reb[2000:2400]:
    i1 = i0 + 8; nav = np.prod(1 + hr.iloc[i0:i1].to_numpy())
    # weights set at i earn R1[i+2] -> window price ratio from row i0+1 to i1+1
    bh = 0.5 * (C.iloc[i1 + 1, 0] / C.iloc[i0 + 1, 0]) + 0.5 * (C.iloc[i1 + 1, 1] / C.iloc[i0 + 1, 1])
    errs.append(nav - bh)
print("(3) synthetic 50/50 buy-hold check over 400 windows: max |NAV - buyhold| = %.2e" % np.max(np.abs(errs)))
