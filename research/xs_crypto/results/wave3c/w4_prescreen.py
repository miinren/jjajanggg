# Wave-4 pre-screen for W01-W04 (rule in trials.csv). Swap effect = mean fwd return of names the rule ADDS minus names it DROPS
# (shorts: predicted < 0; longs: predicted > 0). Forward = residual rows i+2..i+9; long side net of funding received (-F/3).
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/root/work")
from common import D, S0, h
T = len(D.idx); RS = np.nan_to_num(D.resid.to_numpy()); CS = np.cumsum(RS, 0); M = D.M.to_numpy(); S = S0.to_numpy(); F = D.F.to_numpy()
z = np.load("/root/work/xs_hourly_2020_2025.npz", allow_pickle=True); Q = pd.DataFrame(z["quote_volume"]).astype(float)
C = pd.DataFrame(z["close"]).astype(float); del z
qr = (Q / Q.rolling(168, min_periods=100).mean().shift(1)).replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy(); del Q
FL = pd.DataFrame(RS * qr).rolling(72, min_periods=1).sum().to_numpy(); del qr
lc = np.log(C); NH = (lc - lc.rolling(720, min_periods=400).max()).to_numpy(); del C, lc
rows = np.flatnonzero((D.idx.hour % 8 == 7) & (np.arange(T) >= 800) & (np.arange(T) + 10 < T) & (D.idx >= "2020-03-15"))
res = {k: [] for k in ("W01", "W02", "W03L", "W03S", "W04")}; nveto = {"W01": [], "W04": []}; dts = []
for i in rows:
    m = np.flatnonzero(M[i] & np.isfinite(S[i]))
    if len(m) < 60: continue
    fwd = CS[i + 9] - CS[i + 1]; fwdL = fwd - np.nan_to_num(F[i]) / 3
    o = m[np.argsort(S[i, m])]; calm = o; jumpy = o[::-1]
    okS = [c for c in jumpy if not (F[i, c] < -5e-4)]; candS = np.array(okS[:28]); BS = candS[:20]
    candL = calm[:20]; BL = candL[:12]
    pflow = pd.Series(FL[i, m], index=m).rank(pct=True)
    def swap(add, drop, f): return (np.mean(f[list(add)]) if len(add) else np.nan) - (np.mean(f[list(drop)]) if len(drop) else np.nan) if len(add) and len(drop) else np.nan
    # W01: long veto F < -5e-4
    Lk = [c for c in candL if not (F[i, c] < -5e-4)][:12]; nveto["W01"].append(len(set(BL) - set(Lk)))
    res["W01"].append(swap(set(Lk) - set(BL), set(BL) - set(Lk), fwdL))
    # W02: from candS drop the 8 lowest flow
    keep = sorted(candS, key=lambda c: -pflow.get(c, 0.5))[:20]; keep = [c for c in candS if c in set(keep)]
    res["W02"].append(swap(set(keep) - set(BS), set(BS) - set(keep), fwd))
    # W03: near-high tie-break both legs
    nhL = sorted(candL, key=lambda c: -np.nan_to_num(NH[i, c], nan=-9))[:12]; res["W03L"].append(swap(set(nhL) - set(BL), set(BL) - set(nhL), fwdL))
    nhS = sorted(candS, key=lambda c: np.nan_to_num(NH[i, c], nan=0))[:20]; res["W03S"].append(swap(set(nhS) - set(BS), set(BS) - set(nhS), fwd))
    # W04: long veto pct(flow) < 0.10
    Lk4 = [c for c in candL if not (pflow.get(c, 0.5) < 0.10)][:12]; nveto["W04"].append(len(set(BL) - set(Lk4)))
    res["W04"].append(swap(set(Lk4) - set(BL), set(BL) - set(Lk4), fwdL))
    dts.append(D.idx[i])
pred = {"W01": 1, "W02": -1, "W03L": 1, "W03S": -1, "W04": 1}
out = []
for k, v in res.items():
    s = pd.Series(v, index=dts); r = {}
    for lab, sel in (("IS", s.index < "2023-01-01"), ("OOS", s.index >= "2023-01-01"), ("ALL", s.index >= "2000")):
        x = s[sel].dropna(); r[lab] = (x.mean() * 1e4, h.nw_t(x.to_numpy(), 6) if len(x) > 30 else np.nan, len(x))
    ok = all(np.sign(r[p][0]) == pred[k] for p in ("IS", "OOS")) and pred[k] * r["ALL"][1] >= 1.5
    out.append(dict(rule=k, pred=pred[k], IS_bp=r["IS"][0], IS_t=r["IS"][1], OOS_bp=r["OOS"][0], OOS_t=r["OOS"][1], ALL_t=r["ALL"][1],
                    n_active=r["ALL"][2], veto_per_reb=np.mean(nveto[k]) if k in nveto else np.nan, PASS=ok))
o = pd.DataFrame(out).round(3); o.to_csv("w4_prescreen.csv", index=False); print(o.to_string(index=False))
