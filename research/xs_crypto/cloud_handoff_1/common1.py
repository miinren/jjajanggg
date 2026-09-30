"""cloud_handoff_1 shared setup: pf_crypto market (pf_lib accounting), EW market, 30d betas. All inputs known at t."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'code'))
import pf_crypto as PC, pf_lib as P
DEV = ('2020-03-15', '2025-01-01'); HOLD = ('2025-01-01', '2026-01-01')

def setup():
    m = PC.load('dev'); D = m['_D']
    idx, cols = m['idx'], m['cols']
    R = pd.DataFrame(m['R'], idx, cols)                     # simple return over (t, t+1]
    U = D.U.copy()                                          # tradable names (BTC/ETH/gold excluded by harness)
    Rv = R.where(U)                                         # only names in the universe at t
    ew = Rv.mean(1)                                         # EW alt-market simple return over (t, t+1]
    btc = R['BTCUSDT']
    y = R.shift(1).where(U.shift(1, fill_value=False))      # returns known at t
    def beta(x, n=720, mp=168):
        xk = x.shift(1)
        mx = xk.rolling(n, min_periods=mp).mean(); vx = xk.rolling(n, min_periods=mp).var(ddof=0)
        cov = y.mul(xk, axis=0).rolling(n, min_periods=mp).mean() - y.rolling(n, min_periods=mp).mean().mul(mx, axis=0)
        return cov.div(vx, axis=0).clip(-3, 6)
    B = {'B_EW': beta(ew), 'B_BTC': beta(btc)}
    return m, D, R, U, ew, btc, B
