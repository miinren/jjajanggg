"""ext_active.py: copy of /root/work/ext.py (book) plus ACTIVE intra-period position-management extensions.
All new features default to off; with defaults this reproduces ext.book exactly (verified in verify.py).

Timing conventions (identical to ext.book / cloud_harness):
  weights set in loop i earn Rn[i] = R1[i+2]. Price-level stops (lc) are checked after Rn[i] is accrued, exactly like the
  existing live stop (a resting stop order). Signal-based exits (rank, squeeze) are evaluated at the TOP of loop i on
  non-rebalance hours using only data rows <= i (like a rebalance decision), so they earn nothing from Rn[i] onward.

New options (None/False = off):
  resid_hyb  : raw short stop fires only if the BTC-residual cum return since entry is also >= resid_hyb
  vz         : residual z-stop for shorts: exit if resid cum >= vz * idio336_i * sqrt(hours held); vz_raw keeps the raw stop too
  half_at    : partial de-risk: halve a short once at raw cum >= half_at; the rest at `stop`
  trail      : short trailing stop: exit if price rose >= trail from its lowest level since entry (fixed stop kept)
  rank_exit_s/rank_exit_l : hourly exit if a held short (long) drops to rank >= k of the jumpy (calm) eligible order
  time_stop  : exit a position held >= time_stop days that is still under water (both legs)
  sqz        : (z, vm): exit a short if its 4h residual sum > z*idio*sqrt(4) AND 4h quote volume > vm x its 168h avg 4h volume
  redeploy   : 'next' = replace a stopped short immediately with the next-ranked short; 'scale' = scale the remaining shorts up
  lc_reset   : stop measured from the last rebalance instead of from entry
  brake      : if short-leg P&L since the last rebalance <= -brake, halve the whole book until the next rebalance
  confirm    : raw short stop requires the condition on `confirm` consecutive hourly checks
  offset     : rebalance clock shift in hours (robustness only; 0 = live clock)
  ban        : False = a stopped short is NOT excluded at the next rebalance (live: banned until the next rebalance)
  reb_dw     : at a rebalance, halve the weight of kept shorts already >= reb_dw adverse since entry (short leg renormalised)
  rec_pos    : list; appends (i, new_shorts, new_longs, shorts, longs) at each rebalance (diagnostics)
  rec        : list; appends (i, coin, side, hours_held, lc) the first time each position episode is >= adv adverse (raw)
"""
import numpy as np, pandas as pd, sys
sys.path.insert(0, "/root/work")
import cloud_harness as h

_Q = {}
def qvol(D):
    if "q" not in _Q:
        z = np.load(D._path, allow_pickle=True); Q = pd.DataFrame(z["quote_volume"], index=D.idx, columns=D.cols).astype(float)
        q4 = Q.rolling(4, min_periods=4).sum(); base = Q.rolling(168, min_periods=100).mean() * 4
        _Q["q"] = (q4 / base).to_numpy(np.float32)
        del Q, z
    return _Q["q"]


def book(D, score, N=20, NS=None, every=8, L=336, keepx=0.5, guard=-5e-4, stop=0.40, long_stop=0.40, stops=True,
         hedge=1.0, gross=None, leg_weights=None, elig=None, short_frac=0.5, cost=h.COST, tp_short=None, tp_long=None,
         resid_hyb=None, vz=None, vz_raw=False, half_at=None, trail=None, rank_exit_s=None, rank_exit_l=None, time_stop=None,
         sqz=None, redeploy=None, lc_reset=False, brake=None, confirm=None, rec=None, adv=0.20, offset=0, rec_pos=None, ban=True, reb_dw=None):
    NS = N if NS is None else NS
    idx = D.idx; T, K = len(idx), len(D.cols)
    SC = np.asarray(score, dtype=float)
    E = np.array((D.M if elig is None else elig) & D.idio(L).notna() & D.bB.notna(), dtype=bool); E[:, D.ib] = False
    reb = ((idx.hour + 1 - offset) % every == 0) if every > 1 else np.ones(T, bool)
    G = np.ones(T) if gross is None else np.asarray(gross, float)
    w = np.zeros(K); held_l, held_s, banned = [], [], set(); lc = np.zeros(K); hp = 0.0
    lp, sp, hpnl, fund, to = (np.zeros(T) for _ in range(5)); coin = np.zeros((T, K), np.float32)
    ln_up = np.log(1 + stop); ln_dn = np.log(1 - long_stop) if long_stop is not None and long_stop < 1 else -np.inf
    gcur = 1.0
    # --- active-management state ---
    need_rc = resid_hyb is not None or vz is not None
    IV = D.idio(336).to_numpy() if (vz is not None or sqz is not None) else None
    RSn = (D.Rn - D.B * D.rbn[:, None]) if need_rc else None           # residual of the return actually earned (beta row i)
    RSr = np.nan_to_num(D.resid.to_numpy()) if sqz is not None else None
    QR = qvol(D) if sqz is not None else None
    rc = np.zeros(K); lmin = np.zeros(K); t0 = np.zeros(K, int); halved = np.zeros(K, bool); cnt = np.zeros(K, int)
    hitf = np.zeros(K, bool); ln_adv = np.log(1 + adv); ln_adv_l = np.log(1 - adv)
    ln_half = np.log(1 + half_at) if half_at is not None else np.inf
    ln_tr = np.log(1 + trail) if trail is not None else np.inf
    sp_since = 0.0; braked = False
    st = {"held_l": held_l, "held_s": held_s}

    def reset(mask):
        lc[mask] = 0.0; rc[mask] = 0.0; lmin[mask] = 0.0; halved[mask] = False; cnt[mask] = 0; hitf[mask] = False

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
                    nw[longs] = (1 - short_frac) / len(longs)
                    if len(shorts): nw[shorts] = -short_frac / len(shorts)   # guard: only reachable when every short candidate is banned
                else:
                    wl, ws = leg_weights(i, longs, shorts); nw[longs] = wl; nw[shorts] = -ws
                if reb_dw is not None and len(shorts):
                    dm = (nw < 0) & (w < 0) & (lc >= np.log(1 + reb_dw))     # kept shorts already >= reb_dw adverse since entry
                    if dm.any() and not dm[nw < 0].all():
                        nw[dm] *= 0.5; nw[nw < 0] *= short_frac / np.abs(nw[nw < 0]).sum()
                nw *= gcur
                new = (np.sign(nw) != np.sign(w)) & (nw != 0)
                reset(new | (nw == 0)); t0[new] = i
                if lc_reset: reset(nw != 0)
                if rec_pos is not None: rec_pos.append((i, np.flatnonzero(new & (nw < 0)), np.flatnonzero(new & (nw > 0)), list(shorts), list(longs)))
                to[i] += np.abs(nw - w).sum(); w = nw; held_l, held_s = longs, shorts; banned = set()
                sp_since = 0.0; braked = False
        elif rank_exit_s is not None or rank_exit_l is not None or sqz is not None:
            # signal-based hourly exits, data rows <= i only
            m = np.zeros(K, bool)
            if rank_exit_s is not None or rank_exit_l is not None:
                el = np.flatnonzero(E[i] & np.isfinite(SC[i]))
                if len(el) >= 6:
                    o = el[np.argsort(SC[i, el], kind="stable")]
                    r = np.full(K, 10 ** 6); r[o] = np.arange(len(o))            # calm rank (0 = calmest)
                    rj = np.full(K, 10 ** 6); rj[o[::-1]] = np.arange(len(o))    # jumpy rank (0 = jumpiest)
                    if rank_exit_s is not None: m |= (w < 0) & (rj >= rank_exit_s)
                    if rank_exit_l is not None: m |= (w > 0) & (r >= rank_exit_l)
            if sqz is not None:
                zz, vm = sqz; lo = max(0, i - 3)
                s4 = RSr[lo:i + 1].sum(0)
                m |= (w < 0) & (s4 > zz * np.nan_to_num(IV[i], nan=1.0) * 2.0) & (np.nan_to_num(QR[i]) > vm)
            if m.any():
                to[i] += np.abs(w[m]).sum()
                for s in np.flatnonzero(m):
                    if w[s] < 0: banned.add(s); held_s = [z for z in held_s if z != s]
                    else: held_l = [z for z in held_l if z != s]
                w[m] = 0.0; reset(m)
        cp = w * D.Rn[i]; coin[i] = cp
        lp[i] = cp[w > 0].sum(); sp[i] = cp[w < 0].sum(); fund[i] = -(w @ D.Fh[i])
        if hedge:
            hh = -hedge * (w @ D.B[i]); hpnl[i] = hh * D.rbn[i]; to[i] += abs(hh - hp); hp = hh
        if stops:
            act = w != 0; lc[act] += D.Rn[i, act]
            if need_rc: rc[act] += RSn[i, act]
            if rec is not None:
                nh = act & ~hitf & (((w < 0) & (lc >= ln_adv)) | ((w > 0) & (lc <= ln_adv_l)))
                for s in np.flatnonzero(nh): rec.append((i, s, int(np.sign(w[s])), i - t0[s], lc[s]))
                hitf |= nh
            lmin[act] = np.minimum(lmin[act], lc[act])
            sh = act & (w < 0)
            raw_s = sh & (lc >= ln_up)
            if resid_hyb is not None: raw_s &= rc >= np.log(1 + resid_hyb)
            if confirm is not None:
                cnt[raw_s] += 1; cnt[sh & ~raw_s] = 0; raw_s = raw_s & (cnt >= confirm)
            if vz is not None:
                hrs = np.maximum(i - t0 + 1, 24)   # floor 24h so the first hours are not hair-trigger
                zs = sh & (rc >= vz * np.nan_to_num(IV[i], nan=1.0) * np.sqrt(hrs))
                raw_s = (raw_s | zs) if vz_raw else zs
            hit = raw_s | (act & (w > 0) & (lc <= ln_dn))
            if trail is not None: hit |= sh & (lc - lmin >= ln_tr)
            if tp_short is not None: hit |= act & (w < 0) & (lc <= np.log(1 - tp_short))
            if tp_long is not None: hit |= act & (w > 0) & (lc >= np.log(1 + tp_long))
            if time_stop is not None:
                old = act & (i - t0 >= time_stop * 24)
                hit |= old & (((w < 0) & (lc > 0)) | ((w > 0) & (lc < 0)))
            if half_at is not None:
                hv = sh & ~halved & ~hit & (lc >= ln_half)
                if hv.any():
                    to[i] += np.abs(w[hv]).sum() / 2; w[hv] *= 0.5; halved[hv] = True
            if hit.any():
                hs = np.flatnonzero(hit & (w < 0)); freed = np.abs(w[hs]).sum()
                to[i] += np.abs(w[hit]).sum()
                for s in hs:
                    if ban: banned.add(s)
                    held_s = [z for z in held_s if z != s]
                w[hit] = 0.0; reset(hit)
                if redeploy is not None and len(hs):
                    if redeploy == "scale":
                        rem = w < 0
                        if rem.any():
                            g = np.abs(w[rem]).sum(); f = (g + freed) / g
                            to[i] += g * (f - 1); w[rem] *= f
                    elif redeploy == "next":
                        el = np.flatnonzero(E[i] & np.isfinite(SC[i]))
                        jumpy = el[np.argsort(-SC[i, el], kind="stable")]
                        hl = set(held_l); per = freed / len(hs); nadd = len(hs)
                        for s in jumpy:
                            if nadd == 0: break
                            if w[s] != 0 or s in banned or s in hl or D.FND[i, s] < guard: continue
                            w[s] = -per; to[i] += per; one = np.zeros(K, bool); one[s] = True; reset(one); t0[s] = i
                            held_s = held_s + [s]; nadd -= 1
        if brake is not None and not braked:
            sp_since += sp[i]
            if sp_since <= -brake:
                to[i] += np.abs(w).sum() * 0.5; w = w * 0.5; braked = True
    net = lp + sp + hpnl + fund - to * cost
    df = pd.DataFrame({"net": net, "long": lp, "short": sp, "hedge": hpnl, "fund": fund, "to": to}, index=idx).resample("D").sum()
    return df, coin
