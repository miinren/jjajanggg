"""ext2.book = ext.book (identical defaults) + drawdown-research hooks:
  short_ok : bool (T,K) extra eligibility mask applied to the SHORT candidate list only (squeeze filters)
  ban_h    : hours a stopped-out short stays banned (None = live rule: ban cleared at the next rebalance)
  resid_stop: short stop measured on cumulative BTC-residual return (R - beta*R_btc) instead of raw return
  half_at  : stop ladder - halve a short once when its raw (or resid) cum return >= half_at; full stop at `stop`
  adj      : partial rebalance - trade fraction adj toward targets (|w|<0.01 snapped to 0)
  HB       : (T,K) custom BTC hedge betas (replaces D.B for the hedge only)
  offset   : shift of the rebalance clock (hours); short_pick(i, ok_short)->filtered list; stop_fn(i, shorts)->per-name short stop
  HE, ren  : (T,K) ETH hedge betas and (T,) ETH next-returns (same i+2 alignment) for a two-factor hedge
"""
import numpy as np, pandas as pd, sys
sys.path.insert(0, "/root/work")
import cloud_harness as h

def book(D, score, N=20, NS=None, every=8, L=336, keepx=0.5, guard=-5e-4, stop=0.40, long_stop=0.40, stops=True,
         hedge=1.0, gross=None, leg_weights=None, elig=None, short_frac=0.5, cost=h.COST, tp_short=None, tp_long=None,
         short_ok=None, ban_h=None, resid_stop=False, half_at=None, adj=None, HB=None, HE=None, ren=None, offset=0, short_pick=None, stop_fn=None):
    NS = N if NS is None else NS
    idx = D.idx; T, K = len(idx), len(D.cols)
    SC = np.asarray(score, dtype=float)
    E = np.array((D.M if elig is None else elig) & D.idio(L).notna() & D.bB.notna(), dtype=bool); E[:, D.ib] = False
    reb = ((idx.hour + 1 + offset) % every == 0) if every > 1 else np.ones(T, bool)
    G = np.ones(T) if gross is None else np.asarray(gross, float)
    HBa = D.B if HB is None else HB
    w = np.zeros(K); held_l, held_s, banned = [], [], set(); lc = np.zeros(K); hp = 0.0; hpe = 0.0
    ban_until = np.full(K, -1); halved = np.zeros(K, bool)
    lp, sp, hpnl, fund, to = (np.zeros(T) for _ in range(5)); coin = np.zeros((T, K), np.float32)
    ln_up = np.log(1 + stop); ln_dn = np.log(1 - long_stop) if long_stop is not None and long_stop < 1 else -np.inf
    ln_half = np.log(1 + half_at) if half_at is not None else np.inf
    gcur = 1.0; slv = np.full(K, ln_up)
    for i in range(T):
        if reb[i]:
            el = np.flatnonzero(E[i] & np.isfinite(SC[i]))
            if len(el) >= 6:
                if ban_h is not None: banned = set(np.flatnonzero(ban_until > i).tolist())
                nl = N if len(el) >= 2 * N else max(1, min(N, len(el) // 3)); kl = nl + max(4, int(keepx * nl))
                ns = NS if len(el) >= 2 * NS else max(1, min(NS, len(el) // 3)); ks = ns + max(4, int(keepx * ns))
                order = el[np.argsort(SC[i, el], kind="stable")]
                calm = list(order); jumpy = calm[::-1]
                ok_short = [s for s in jumpy if D.FND[i, s] >= guard and s not in banned and (short_ok is None or short_ok[i, s])]
                if short_pick is not None: ok_short = short_pick(i, ok_short)
                rk = {s: j for j, s in enumerate(calm)}; rs = {s: j for j, s in enumerate(ok_short)}
                longs = sorted([s for s in held_l if s in set(calm[:kl])], key=lambda z: rk[z])[:nl]
                for s in calm:
                    if len(longs) >= nl: break
                    if s not in longs: longs.append(s)
                ls = set(longs)
                shorts = sorted([s for s in held_s if s in set(ok_short[:ks]) and s not in ls], key=lambda z: rs[z])[:ns]
                for s in ok_short:
                    if len(shorts) >= ns: break
                    if s not in shorts and s not in ls: shorts.append(s)
                gcur = G[i]
                nw = np.zeros(K)
                if leg_weights is None:
                    nw[longs] = (1 - short_frac) / len(longs)
                    if len(shorts): nw[shorts] = -short_frac / len(shorts)
                else:
                    wl, ws = leg_weights(i, longs, shorts); nw[longs] = wl; nw[shorts] = -ws
                nw *= gcur
                if stop_fn is not None: slv[:] = ln_up; slv[shorts] = np.log(1 + stop_fn(i, shorts))
                if adj is not None:
                    nw = w + adj * (nw - w); nw[np.abs(nw) < 0.01] = 0.0
                new = (np.sign(nw) != np.sign(w)) & (nw != 0); lc[new] = 0.0; lc[nw == 0] = 0.0
                halved[new | (nw == 0)] = False
                to[i] += np.abs(nw - w).sum(); w = nw; held_l, held_s = longs, shorts
                if ban_h is None: banned = set()
        cp = w * D.Rn[i]; coin[i] = cp
        lp[i] = cp[w > 0].sum(); sp[i] = cp[w < 0].sum(); fund[i] = -(w @ D.Fh[i])
        if hedge:
            hh = -hedge * (w @ HBa[i]); hpnl[i] = hh * D.rbn[i]; to[i] += abs(hh - hp); hp = hh
            if HE is not None:
                he = -hedge * (w @ HE[i]); hpnl[i] += he * ren[i]; to[i] += abs(he - hpe); hpe = he
        if stops:
            act = w != 0
            if resid_stop:
                inc = D.Rn[i] - D.B[i] * D.rbn[i]
                lc[act & (w < 0)] += inc[act & (w < 0)]; lc[act & (w > 0)] += D.Rn[i, act & (w > 0)]
            else:
                lc[act] += D.Rn[i, act]
            hit = act & (((w < 0) & (lc >= slv)) | ((w > 0) & (lc <= ln_dn)))
            if tp_short is not None: hit |= act & (w < 0) & (lc <= np.log(1 - tp_short))
            if tp_long is not None: hit |= act & (w > 0) & (lc >= np.log(1 + tp_long))
            if half_at is not None:
                hv = act & (w < 0) & ~hit & ~halved & (lc >= ln_half)
                if hv.any():
                    to[i] += np.abs(w[hv]).sum() * 0.5; w[hv] *= 0.5; halved[hv] = True
            if hit.any():
                to[i] += np.abs(w[hit]).sum()
                for s in np.flatnonzero(hit & (w < 0)):
                    banned.add(s); held_s = [z for z in held_s if z != s]
                    if ban_h is not None: ban_until[s] = i + ban_h
                w[hit] = 0.0; lc[hit] = 0.0; halved[hit] = False
    net = lp + sp + hpnl + fund - to * cost
    df = pd.DataFrame({"net": net, "long": lp, "short": sp, "hedge": hpnl, "fund": fund, "to": to}, index=idx).resample("D").sum()
    return df, coin
