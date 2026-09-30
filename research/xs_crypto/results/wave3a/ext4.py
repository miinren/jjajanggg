"""wave3a copy of wave2/ext3.book, trimmed to the hooks used here (offset, leg_weights, short_frac, N/NS, stop) plus
cost/fill/funding bookkeeping columns (none of which change positions):
  tinv   : sum over trades of |dw| * IQ[i,coin]  (IQ = 1/sqrt(24h quote vol in $M)); hedge trades use the BTC column.
           Per-coin cost = 3bp*to + k*tinv (k in bp units -> *1e-4).
  slip_s : sum of |w| of SHORT positions stopped out this hour (stop-slippage X% => extra loss X*slip_s)
  slip_l : same for long stops
  fund2  : funding P&L using same-day funding_1d (Fh2) instead of the harness's prior-day proxy
  held   : optional list collecting IQ of held names at each rebalance (for k calibration)
Returns (daily df, daily per-coin gross pnl matrix float32 (days x K))."""
import numpy as np, pandas as pd, sys
sys.path.insert(0, "/root/work")
import cloud_harness as h

def book(D, score, N=20, NS=None, every=8, L=336, keepx=0.5, guard=-5e-4, stop=0.40, long_stop=0.40, stops=True,
         hedge=1.0, leg_weights=None, short_frac=0.5, cost=h.COST, offset=0, IQ=None, Fh2=None, held=None, dayb=None):
    NS = N if NS is None else NS
    idx = D.idx; T, K = len(idx), len(D.cols)
    SC = np.asarray(score, dtype=float)
    E = np.array(D.M & D.idio(L).notna() & D.bB.notna(), dtype=bool); E[:, D.ib] = False
    reb = ((idx.hour + 1 + offset) % every == 0)
    w = np.zeros(K); held_l, held_s, banned = [], [], set(); lc = np.zeros(K); hp = 0.0
    lp, sp, hpnl, fund, to, tinv, sls, sll, f2 = (np.zeros(T) for _ in range(9)); coin = np.zeros((T, K), np.float32)
    ln_up = np.log(1 + stop); ln_dn = np.log(1 - long_stop) if long_stop is not None and long_stop < 1 else -np.inf
    ib = D.ib
    for i in range(T):
        if reb[i]:
            el = np.flatnonzero(E[i] & np.isfinite(SC[i]))
            if len(el) >= 6:
                nl = N if len(el) >= 2 * N else max(1, min(N, len(el) // 3)); kl = nl + max(4, int(keepx * nl))
                ns = NS if len(el) >= 2 * NS else max(1, min(NS, len(el) // 3)); ks = ns + max(4, int(keepx * ns))
                order = el[np.argsort(SC[i, el], kind="stable")]
                calm = list(order); jumpy = calm[::-1]
                ok_short = [s for s in jumpy if D.FND[i, s] >= guard and s not in banned]
                rs = {s: j for j, s in enumerate(ok_short)}; rk = {s: j for j, s in enumerate(calm)}
                longs = sorted([s for s in held_l if s in set(calm[:kl])], key=lambda z: rk[z])[:nl]
                for s in calm:
                    if len(longs) >= nl: break
                    if s not in longs: longs.append(s)
                ls = set(longs)
                shorts = sorted([s for s in held_s if s in set(ok_short[:ks]) and s not in ls], key=lambda z: rs[z])[:ns]
                for s in ok_short:
                    if len(shorts) >= ns: break
                    if s not in shorts and s not in ls: shorts.append(s)
                nw = np.zeros(K)
                if leg_weights is None:
                    nw[longs] = (1 - short_frac) / len(longs)
                    if len(shorts): nw[shorts] = -short_frac / len(shorts)
                else:
                    wl, ws = leg_weights(i, longs, shorts); nw[longs] = wl; nw[shorts] = -ws
                new = (np.sign(nw) != np.sign(w)) & (nw != 0); lc[new] = 0.0; lc[nw == 0] = 0.0
                dw = np.abs(nw - w); to[i] += dw.sum()
                if IQ is not None: tinv[i] += dw @ IQ[i]
                if held is not None: held.append(IQ[i, longs + shorts].copy())
                w = nw; held_l, held_s = longs, shorts; banned = set()
        cp = w * D.Rn[i]; coin[i] = cp
        lp[i] = cp[w > 0].sum(); sp[i] = cp[w < 0].sum(); fund[i] = -(w @ D.Fh[i])
        if Fh2 is not None: f2[i] = -(w @ Fh2[i])
        if hedge:
            hh = -hedge * (w @ D.B[i]); hpnl[i] = hh * D.rbn[i]; to[i] += abs(hh - hp)
            if IQ is not None: tinv[i] += abs(hh - hp) * IQ[i, ib]
            hp = hh
        if stops:
            act = w != 0; lc[act] += D.Rn[i, act]
            hit = act & (((w < 0) & (lc >= ln_up)) | ((w > 0) & (lc <= ln_dn)))
            if hit.any():
                a = np.abs(w[hit]); to[i] += a.sum()
                if IQ is not None: tinv[i] += a @ IQ[i, hit]
                sls[i] = np.abs(w[hit & (w < 0)]).sum(); sll[i] = np.abs(w[hit & (w > 0)]).sum()
                for s in np.flatnonzero(hit & (w < 0)):
                    banned.add(s); held_s = [z for z in held_s if z != s]
                w[hit] = 0.0; lc[hit] = 0.0
    net = lp + sp + hpnl + fund - to * cost
    df = pd.DataFrame({"net": net, "long": lp, "short": sp, "hedge": hpnl, "fund": fund, "to": to, "tinv": tinv,
                       "slip_s": sls, "slip_l": sll, "fund2": f2}, index=idx).resample("D").sum()
    cd = np.add.reduceat(coin, dayb, axis=0); del coin
    return df, cd
