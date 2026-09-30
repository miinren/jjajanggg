"""wave3c: ext3.book (offset, leg_weights, short_ok/long_ok) + EXECUTION TIMING and ENTRY-ONLY FILTERS.

Target portfolio at every rebalance is computed exactly as ext3.book. What changes is WHEN each coin's weight moves from its
old value to the target, inside a window of `H` hours after the rebalance:
  execf(i0, j, c, w_old, w_tgt) -> fraction f in [0, 1] of the change to have executed by step j (non-decreasing in j),
        evaluated at step j >= i0 using data rows <= j only; forced to 1 at j = i0 + H. None = immediate (bit-identical to ext3).
Weight set at step j earns D.Rn[j] = R1[j+2] (same 1 h lag as the book). Turnover |dw| is charged when the weight actually
moves, so total turnover per rebalance is unchanged for monotone paths (TWAP, delay). Hedge follows the actual weights.
Stops act on actual (filled) weights. A coin stopped while pending has its pending change cancelled. Entry price (lc) resets
on the first fill of a new position.
entry_ok_s / entry_ok_l: bool (T,K) masks applied only to NEW names (not already held) at a rebalance: entry filters, no
extra trades. (ext3's short_ok/long_ok apply to held names too.)
"""
import numpy as np, pandas as pd, sys
sys.path.insert(0, "/root/work")
import cloud_harness as h


def book(D, score, N=20, NS=None, every=8, L=336, keepx=0.5, guard=-5e-4, stop=0.40, long_stop=0.40, stops=True,
         hedge=1.0, leg_weights=None, elig=None, short_frac=0.5, cost=h.COST, offset=0,
         execf=None, H=0, entry_ok_s=None, entry_ok_l=None, hedge_target=False, hedge_band=None):
    NS = N if NS is None else NS
    idx = D.idx; T, K = len(idx), len(D.cols)
    SC = np.asarray(score, dtype=float)
    E = np.array((D.M if elig is None else elig) & D.idio(L).notna() & D.bB.notna(), dtype=bool); E[:, D.ib] = False
    reb = ((idx.hour + 1 + offset) % every == 0) if every > 1 else np.ones(T, bool)
    w = np.zeros(K); held_l, held_s, banned = [], [], set(); lc = np.zeros(K); hp = 0.0
    lp, sp, hpnl, fund, to, toh = (np.zeros(T) for _ in range(6)); coin = np.zeros((T, K), np.float32)
    ln_up = np.log(1 + stop); ln_dn = np.log(1 - long_stop) if long_stop is not None and long_stop < 1 else -np.inf
    pend = np.zeros(K, bool); w0 = np.zeros(K); wt = np.zeros(K); i0 = -1; hforce = True
    for i in range(T):
        if reb[i]:
            el = np.flatnonzero(E[i] & np.isfinite(SC[i]))
            if len(el) >= 6:
                nl = N if len(el) >= 2 * N else max(1, min(N, len(el) // 3)); kl = nl + max(4, int(keepx * nl))
                ns = NS if len(el) >= 2 * NS else max(1, min(NS, len(el) // 3)); ks = ns + max(4, int(keepx * ns))
                order = el[np.argsort(SC[i, el], kind="stable")]
                calm = list(order); jumpy = calm[::-1]
                hs, hl = set(held_s), set(held_l)
                ok_short = [s for s in jumpy if D.FND[i, s] >= guard and s not in banned
                            and (entry_ok_s is None or s in hs or entry_ok_s[i, s])]
                calmL = calm if entry_ok_l is None else [s for s in calm if s in hl or entry_ok_l[i, s]]
                rk = {s: j for j, s in enumerate(calmL)}; rs = {s: j for j, s in enumerate(ok_short)}
                longs = sorted([s for s in held_l if s in set(calmL[:kl])], key=lambda z: rk[z])[:nl]
                for s in calmL:
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
                held_l, held_s = longs, shorts; banned = set()
                if execf is None:
                    new = (np.sign(nw) != np.sign(w)) & (nw != 0); lc[new] = 0.0; lc[nw == 0] = 0.0
                    to[i] += np.abs(nw - w).sum(); w = nw
                else:   # start a new execution window (any unfinished change from the last window is completed first)
                    if pend.any():
                        tgt = np.where(pend, wt, w); new = (np.sign(tgt) != np.sign(w)) & (tgt != 0); lc[new] = 0.0; lc[tgt == 0] = 0.0
                        to[i] += np.abs(tgt - w).sum(); w = tgt
                    pend = nw != w; w0 = w.copy(); wt = nw; i0 = i
        if execf is not None and pend.any():
            forced = i - i0 >= H
            for c in np.flatnonzero(pend):
                f = 1.0 if forced else min(1.0, max(0.0, execf(i0, i, c, w0[c], wt[c])))
                x = w0[c] + f * (wt[c] - w0[c])
                if x != w[c]:
                    if np.sign(x) != np.sign(w[c]) and x != 0: lc[c] = 0.0
                    if x == 0: lc[c] = 0.0
                    to[i] += abs(x - w[c]); w[c] = x
                if f >= 1.0: pend[c] = False
        cp = w * D.Rn[i]; coin[i] = cp
        lp[i] = cp[w > 0].sum(); sp[i] = cp[w < 0].sum(); fund[i] = -(w @ D.Fh[i])
        if hedge:
            wh = np.where(pend, wt, w) if (hedge_target and execf is not None) else w
            hh = -hedge * (wh @ D.B[i])
            if hedge_band is not None:      # W06: hold the hedge unless rebalance/stop or drift beyond the band
                if not (reb[i] or hforce or abs(hh - hp) > hedge_band): hh = hp
                hforce = False
            hpnl[i] = hh * D.rbn[i]; to[i] += abs(hh - hp); toh[i] = abs(hh - hp); hp = hh
        if stops:
            act = w != 0; lc[act] += D.Rn[i, act]
            hit = act & (((w < 0) & (lc >= ln_up)) | ((w > 0) & (lc <= ln_dn)))
            if hit.any():
                to[i] += np.abs(w[hit]).sum()
                for s in np.flatnonzero(hit & (w < 0)):
                    banned.add(s); held_s = [z for z in held_s if z != s]
                w[hit] = 0.0; lc[hit] = 0.0; pend[hit] = False; hforce = True
    net = lp + sp + hpnl + fund - to * cost
    df = pd.DataFrame({"net": net, "long": lp, "short": sp, "hedge": hpnl, "fund": fund, "to": to, "to_hedge": toh}, index=idx).resample("D").sum()
    return df, coin
