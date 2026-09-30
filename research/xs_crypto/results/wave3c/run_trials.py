# wave3c trial runner. usage: python run_trials.py ID [ID ...]  (appends to results_raw.csv, saves daily df to OUT/<ID>.pkl)
import time, json
from lib3c import *
dfB, cB, perB = base()
T_ = len(D.idx); SQ3 = np.sqrt(3)

# ---------------- topic 1: execution policies ----------------
def ttype(w0, wt):
    if wt < 0 and w0 >= 0: return "SE"
    if w0 < 0 and wt > w0: return "SX"
    if wt > 0 and w0 <= 0: return "LE"
    if w0 > 0 and wt <= 0: return "LX"
    return "OT"
R_SE = {n: (lambda i0, j, c, n=n: float(rsum(j, c, n) <= 0)) for n in (1, 2, 3)}
def R_SX(i0, j, c, big=False):
    r3 = rsum(i0, c, 3); thr = -2 * SIGH[i0, c] * SQ3 if big else 0.0
    if not (r3 < thr): return 1.0
    return float(RS[j, c] >= 0)
R_LE = lambda i0, j, c: float(RS[j, c] >= 0)
def R_LX(i0, j, c):
    if not (rsum(i0, c, 3) > 0): return 1.0
    return float(RS[j, c] <= 0)
def policy(rules):
    def f(i0, j, c, w0, wt):
        r = rules.get(ttype(w0, wt)); return 1.0 if r is None else r(i0, j, c)
    return f
twap = lambda k: (lambda i0, j, c, w0, wt: (j - i0 + 1) / k)
EXEC = {
    "E01": (twap(2), 2), "E02": (twap(3), 3), "E03": (twap(4), 4),
    "E04": (lambda i0, j, c, w0, wt: 0.0, 1),
    "E05": (policy({"SE": R_SE[1]}), 4), "E06": (policy({"SE": R_SE[2]}), 4), "E07": (policy({"SE": R_SE[3]}), 6),
    "E08": (policy({"SX": R_SX}), 4), "E09": (policy({"SX": lambda i0, j, c: R_SX(i0, j, c, True)}), 4),
    "E10": (policy({"LE": R_LE}), 4), "E11": (policy({"LX": R_LX}), 4),
    "E12": (policy({"SX": R_SX, "LE": R_LE}), 4),
    "E13": (policy({"SE": R_SE[1], "SX": R_SX, "LE": R_LE, "LX": R_LX}), 4),
}
# ---------------- topic 3: entry filters (True = allowed to enter) ----------------
_F = {}
def feats():
    if _F: return _F
    z = np.load("/root/work/xs_hourly_2020_2025.npz", allow_pickle=True)
    Q = pd.DataFrame(z["quote_volume"], index=D.idx, columns=D.cols).astype(float); del z
    ratio = Q / Q.rolling(168, min_periods=100).mean().shift(1)
    _F["vmax8"] = ratio.rolling(8, min_periods=1).max().to_numpy(); del Q, ratio
    Z = np.abs(RS) / SIGH; Z[~np.isfinite(Z)] = 0
    _F["zmax8"] = pd.DataFrame(Z).rolling(8, min_periods=1).max().to_numpy()
    _F["Z"] = Z; return _F
def gaprev(k, ret=0.5):
    F_ = feats(); Z = F_["Z"]; blk = np.zeros_like(Z, bool)
    for L in range(1, 8):          # jump at row i-L, retrace measured over rows i-L+1..i
        J = np.roll(RS, L, 0); ZJ = np.roll(Z, L, 0); aft = CS - np.roll(CS, L, 0)
        c = (ZJ > k) & (-np.sign(J) * aft > ret * np.abs(J)); c[:L] = False; blk |= c
    return ~blk
def filt(tid):
    F_ = feats(); ok = lambda a, k: ~(np.nan_to_num(a, nan=0.0) > k)
    m = {"V01": ("both", ok(F_["vmax8"], 5)), "V02": ("short", ok(F_["vmax8"], 5)), "V03": ("long", ok(F_["vmax8"], 5)),
         "V04": ("both", ok(F_["vmax8"], 3)), "V05": ("both", ok(F_["vmax8"], 10)),
         "V06": ("both", ok(F_["zmax8"], 4)), "V07": ("short", ok(F_["zmax8"], 4)), "V08": ("long", ok(F_["zmax8"], 4)),
         "V09": ("both", ok(F_["zmax8"], 3)), "V10": ("both", ok(F_["zmax8"], 6))}
    side, mask = m[tid] if tid in m else ("both", gaprev(4))
    kw = {}
    if side in ("both", "short"): kw["entry_ok_s"] = mask
    if side in ("both", "long"): kw["entry_ok_l"] = mask
    frac = 1 - mask[D.M.to_numpy()].mean()
    return kw, frac

def nscore(tid):
    if tid.startswith("N02"):
        z = np.load("/root/work/xs_hourly_2020_2025.npz", allow_pickle=True)
        Q = pd.DataFrame(z["quote_volume"], index=D.idx, columns=D.cols).astype(float); del z
        qr = (Q / Q.rolling(168, min_periods=100).mean().shift(1)).replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy(); del Q
        X = pd.DataFrame(RS * qr, index=D.idx, columns=D.cols).rolling(72, min_periods=1).sum()
    else:
        X = D.idio(336) ** 2 / D.R1.rolling(336, min_periods=200).var()
    p = X.where(D.M).rank(1, pct=True).fillna(0.5)
    w = float(tid.split("w")[1]) if "w" in tid else 0.15
    return (1 - w) * S0 + w * p

def evaluate(tid, df, cm, per, extra=None):
    s = stats(df); r = h.partition_test(D, (df, cm), (dfB, cB), verbose=False)
    clk = {o: round(srx(cut(d.net)), 3) for o, d in per.items()} if per else {}
    wins = sum(clk[o] > srx(cut(perB[o].net)) for o in clk) if clk else None
    row = dict(id=tid, SR=s["SR"], SR8=sr_at(df, 8), SR12=sr_at(df, 12), bp=s["bp"], to=cut(df.to).mean(), t=r["tNW"],
               years=r["years_won"], groups=r["coin_groups_won"], reg=f"{r['regime_btc_up_bp']:.2f}/{r['regime_btc_down_bp']:.2f}",
               padopt=r["adopt"], adopt=bool(r["adopt"] and r["tNW"] >= 2.0), mdd2=s["mdd_at2pct"], minYr=s["minYrSR"],
               clocks_won=wins, clk=json.dumps(clk), ydiff=json.dumps(r["year_diffs_bp"]), **(extra or {}))
    pd.DataFrame([row]).to_csv("results_raw.csv", mode="a", header=not os.path.exists("results_raw.csv"), index=False)
    pickle.dump(dict(df=df, per=per), open(f"{OUT}/{tid}.pkl", "wb"))
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items() if k not in ("clk", "ydiff")}, flush=True)
    return row

def run(tid):
    t0 = time.time(); per = {}
    if tid in EXEC:
        f, H = EXEC[tid]; df, cm = avg8(per_offset=per, execf=f, H=H); extra = None
    elif tid.startswith("V"):
        kw, frac = filt(tid); df, cm = avg8(per_offset=per, **kw); extra = dict(blocked_frac_M=round(float(frac), 4))
    elif tid == "N02s":         # flow72 sleeve blended into B-MV at matched vol (rw 0.25; 0.15/0.35 sensitivity)
        sc = nscore("N02w1.0"); sdf = scm = None; sper = {}
        for off in range(8):
            d, c = ext4.book(D, sc, offset=off, N=20, NS=20, short_frac=0.5, stop=0.2); sper[off] = d
            sdf = d / 8 if sdf is None else sdf + d / 8; scm = c / np.float32(8) if scm is None else scm + c / np.float32(8)
        k = cut(dfB.net).std() / cut(sdf.net).std(); ss = stats(sdf)
        print("sleeve alone SR %.2f corr w/ B-MV %.2f" % (ss["SR"], cut(sdf.net).corr(cut(dfB.net))), flush=True)
        for rw in (0.25, 0.15, 0.35):
            df = dfB * (1 - rw) + sdf * (rw * k); cm = cB * np.float32(1 - rw) + scm * np.float32(rw * k)
            per = {o: perB[o] * (1 - rw) + sper[o] * (rw * k) for o in range(8)}
            evaluate(tid if rw == 0.25 else f"N02s_rw{rw}", df, cm, per, dict(sleeve_SR=round(ss["SR"], 3), rw=rw))
        return
    elif tid.startswith("N"):
        sc = nscore(tid); df = cm = None
        for off in range(8):
            d, c = ext4.book(D, sc, offset=off, leg_weights=minvar_floor, **BK); per[off] = d
            df = d / 8 if df is None else df + d / 8; cm = c / np.float32(8) if cm is None else cm + c / np.float32(8)
        extra = None
    elif tid.startswith("F"):      # single-clock book vs the 8-clock-averaged base
        off = int(tid.split("_o")[1]); df, cm = ext4.book(D, S0, offset=off, leg_weights=minvar_floor, **BK); per = None
        extra = dict(offset=off)
    evaluate(tid, df, cm, per, extra); print(tid, "%.0fs" % (time.time() - t0), flush=True)

if __name__ == "__main__":
    for tid in sys.argv[1:]: run(tid)
