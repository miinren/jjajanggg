"""Extended copy of cloud_harness.live_book: identical rules, plus per-leg attribution, hourly gross scaling, hedge ratio,
separate long/short N. Validated to reproduce live_book when defaults are used."""
import numpy as np, pandas as pd, cloud_harness as h

def book(D, score, N=20, NS=None, every=8, L=336, keepx=0.5, guard=-5e-4, stop=0.40, long_stop=0.40, stops=True,
         hedge=1.0, gross=None, leg_weights=None, elig=None, short_frac=0.5, cost=h.COST, tp_short=None, tp_long=None):
    NS = N if NS is None else NS
    idx = D.idx; T, K = len(idx), len(D.cols)
    SC = np.asarray(score, dtype=float)
    E = np.array((D.M if elig is None else elig) & D.idio(L).notna() & D.bB.notna(), dtype=bool); E[:, D.ib] = False
    reb = ((idx.hour + 1) % every == 0) if every > 1 else np.ones(T, bool)
    G = np.ones(T) if gross is None else np.asarray(gross, float)
    w = np.zeros(K); held_l, held_s, banned = [], [], set(); lc = np.zeros(K); hp = 0.0
    lp, sp, hpnl, fund, to = (np.zeros(T) for _ in range(5)); coin = np.zeros((T, K), np.float32)
    ln_up = np.log(1 + stop); ln_dn = np.log(1 - long_stop) if long_stop is not None and long_stop < 1 else -np.inf
    gcur = 1.0
    for i in range(T):
        if reb[i]:
            el = np.flatnonzero(E[i] & np.isfinite(SC[i]))
            if len(el) >= 6:
                nl = N if len(el) >= 2 * N else max(1, min(N, len(el) // 3)); kl = nl + max(4, int(keepx * nl))
                ns = NS if len(el) >= 2 * NS else max(1, min(NS, len(el) // 3)); ks = ns + max(4, int(keepx * ns))
                order = el[np.argsort(SC[i, el], kind="stable")]
                calm = list(order); jumpy = calm[::-1]
                ok_short = [s for s in jumpy if D.FND[i, s] >= guard and s not in banned]
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
                    nw[longs] = (1 - short_frac) / len(longs); nw[shorts] = -short_frac / len(shorts)
                else:
                    wl, ws = leg_weights(i, longs, shorts); nw[longs] = wl; nw[shorts] = -ws
                nw *= gcur
                new = (np.sign(nw) != np.sign(w)) & (nw != 0); lc[new] = 0.0; lc[nw == 0] = 0.0
                to[i] += np.abs(nw - w).sum(); w = nw; held_l, held_s = longs, shorts; banned = set()
        cp = w * D.Rn[i]; coin[i] = cp
        lp[i] = cp[w > 0].sum(); sp[i] = cp[w < 0].sum(); fund[i] = -(w @ D.Fh[i])
        if hedge:
            hh = -hedge * (w @ D.B[i]); hpnl[i] = hh * D.rbn[i]; to[i] += abs(hh - hp); hp = hh
        if stops:
            act = w != 0; lc[act] += D.Rn[i, act]
            hit = act & (((w < 0) & (lc >= ln_up)) | ((w > 0) & (lc <= ln_dn)))
            if tp_short is not None: hit |= act & (w < 0) & (lc <= np.log(1 - tp_short))
            if tp_long is not None: hit |= act & (w > 0) & (lc >= np.log(1 + tp_long))
            if hit.any():
                to[i] += np.abs(w[hit]).sum()
                for s in np.flatnonzero(hit & (w < 0)):
                    banned.add(s); held_s = [z for z in held_s if z != s]
                w[hit] = 0.0; lc[hit] = 0.0
    net = lp + sp + hpnl + fund - to * cost
    df = pd.DataFrame({"net": net, "long": lp, "short": sp, "hedge": hpnl, "fund": fund, "to": to}, index=idx).resample("D").sum()
    return df, coin
