import pickle, numpy as np, pandas as pd, cloud_harness as h
from scipy.stats import norm, skew, kurtosis
S = pickle.load(open("sweeps.pkl","rb")); base = S["base"]; sw = S["sweeps"]
ST = "2020-03-15"; COST = 5.5e-4
def ser(df, c=COST):
    g = df.net + df.to*COST  # gross of costs
    x = g - df.to*c
    return x[(x.index >= ST) & (x.index < "2026-01-01")]
def sr(x): return x.mean()/x.std()*np.sqrt(365)
def bp(x): return x.mean()*1e4
out = []
P = lambda *a: out.append(" ".join(str(z) for z in a))
x0 = ser(base); n = len(x0)
# --- sweeps
def row(k):
    x = ser(sw[k]); return f"| {k[1]} | {sr(x):.2f} | {bp(x):.1f} | {sr(x[x.index<'2023']):.2f} | {sr(x[x.index>='2023']):.2f} | {sw[k].to[sw[k].index>=ST].mean():.2f} |"
P("## 2. Parameter stability\n")
for p in ["N","L","fw","every","stop","keepx"]:
    P(f"\n**{p}** (live marked *)\n\n| {p} | SR | bp/day | SR 20-22 | SR 23-25 | turnover/day |\n|---|---|---|---|---|---|")
    for k in [k for k in sw if k[0]==p]: P(row(k))
Ns = sorted({k[1] for k in sw if k[0]=="NxL"}); Ls = sorted({k[2] for k in sw if k[0]=="NxL"})
for lab, f in [("SR", sr), ("bp/day", bp)]:
    P(f"\n**N x L grid – {lab}**\n\n| N \\ L | " + " | ".join(map(str,Ls)) + " |\n" + "|---" * (len(Ls)+1) + "|")
    for N in Ns: P(f"| {N} | " + " | ".join(f"{f(ser(sw[('NxL',N,L)])):.2f}" if lab=="SR" else f"{f(ser(sw[('NxL',N,L)])):.1f}" for L in Ls) + " |")
grid = np.array([[sr(ser(sw[("NxL",N,L)])) for L in Ls] for N in Ns])
P(f"\nGrid SR: min {grid.min():.2f}, median {np.median(grid):.2f}, max {grid.max():.2f}; live (20,336) = {sr(x0):.2f}.")
# walk-forward over NxL family
fam = {k: (sw[k], None) for k in sw if k[0]=="NxL"}
wf = h.walk_forward(fam, (base, None)); P(f"\nWalk-forward over the N x L family (pick best SR on years < Y, trade year Y): picks {wf['picks']}, WF SR {wf['wf_SR']:.2f} vs live-config SR {wf['base_SR']:.2f} over 2021-25, t_NW(diff) {wf['tNW_vs_base']:.2f}.")
# all sweep SRs for DSR variance
allsr_d = np.array([ser(v).mean()/ser(v).std() for v in sw.values()])
# --- realistic expectation
P("\n## 3. Realistic expectation\n")
srd = x0.mean()/x0.std(); sk = skew(x0); ku = kurtosis(x0, fisher=False)
se_d = np.sqrt((1 - sk*srd + (ku-1)/4*srd**2)/(n-1))
P(f"Daily returns (1x gross, 5.5 bp): n={n}, mean {bp(x0):.1f} bp/day, SR {sr(x0):.2f}, skew {sk:.2f}, kurtosis {ku:.1f}, SE(SR ann.) {se_d*np.sqrt(365):.2f}.\n")
g = 0.5772156649; Ntr = 255
def dsr(vsr):
    emax = np.sqrt(vsr)*((1-g)*norm.ppf(1-1/Ntr) + g*norm.ppf(1-1/(Ntr*np.e)))
    return emax, norm.cdf((srd-emax)/se_d)
P("| Deflated Sharpe (N_trials=255) | SR* (expected max of 255 null trials, ann.) | DSR = P(true SR > SR*) |\n|---|---|---|")
for lab, v in [("V[SR] = sampling var of SR (pure-noise trials)", se_d**2), ("V[SR] = dispersion of today's sweep variants", allsr_d.var()), ("V[SR] = 2x sampling var (conservative)", 2*se_d**2)]:
    em, d = dsr(v); P(f"| {lab} | {em*np.sqrt(365):.2f} | {d:.4f} |")
tau = 1.0; se_a = se_d*np.sqrt(365); k = tau**2/(tau**2+se_a**2)
P(f"\nBayesian shrinkage (prior SR ~ N(0, 1.0²)): posterior mean {k*sr(x0):.2f}, 90% interval [{k*sr(x0)-1.645*np.sqrt(k)*se_a:.2f}, {k*sr(x0)+1.645*np.sqrt(k)*se_a:.2f}] (shrink factor {k:.2f}).")
em, _ = dsr(se_d**2); hc = sr(x0) - em*np.sqrt(365)
P(f"Selection-bias haircut (SR − expected max-of-255-noise SR, same variance): {hc:.2f}.")
yr = x0.groupby(x0.index.year)
P("\n| Period | SR | bp/day | ann. return @1.5x | worst day @1x (bp) |\n|---|---|---|---|---|")
for y, xx in yr: P(f"| {y} | {sr(xx):.2f} | {bp(xx):.1f} | {1.5*xx.mean()*365*100:.0f}% | {xx.min()*1e4:.0f} |")
for lab, a, b in [("2020-22", ST, "2023"), ("2023-25", "2023", "2026"), ("all", ST, "2026")]:
    xx = x0[(x0.index >= a) & (x0.index < b)]; P(f"| {lab} | {sr(xx):.2f} | {bp(xx):.1f} | {1.5*xx.mean()*365*100:.0f}% | {xx.min()*1e4:.0f} |")
P(f"\nAnnualised arithmetic return at 1.5x gross, 5.5 bp: {1.5*x0.mean()*365*100:.0f}% (ann. vol {1.5*x0.std()*np.sqrt(365)*100:.0f}%).")
P("\nWorst rolling losses (sum of daily log-ish returns, per unit gross; bp and $ at 1.5x on $330):\n\n| Window | worst @1x (bp) | worst @1.5x | $ on $330 @1.5x |\n|---|---|---|---|")
for w in [1,5,20]:
    m = x0.rolling(w).sum().min(); P(f"| {w}d | {m*1e4:.0f} | {1.5*m*100:.1f}% | ${1.5*m*330:.0f} |")
cum = x0.cumsum(); mdd = (cum-cum.cummax()).min(); P(f"| max drawdown | {mdd*1e4:.0f} | {1.5*mdd*100:.1f}% | ${1.5*mdd*330:.0f} |")
# --- costs
P("\n## 4. Cost sensitivity (live config)\n\n| cost bp/unit | SR | bp/day | SR 20-22 | SR 23-25 | ann @1.5x |\n|---|---|---|---|---|---|")
for c in [4, 5.5, 8, 12]:
    xx = ser(base, c*1e-4); P(f"| {c} | {sr(xx):.2f} | {bp(xx):.1f} | {sr(xx[xx.index<'2023']):.2f} | {sr(xx[xx.index>='2023']):.2f} | {1.5*xx.mean()*365*100:.0f}% |")
P(f"\nMean turnover {base.to[base.index>=ST].mean():.2f} units/day → each +1 bp cost ≈ −{base.to[base.index>=ST].mean():.2f} bp/day.")
# --- placebo
try:
    pl = pickle.load(open("placebo.pkl","rb"))
    t = np.array([r["tNW"] for r in pl]); ad = np.array([r["adopt"] for r in pl]); s = np.array([r["SR"] for r in pl])
    P(f"\n## 1. Noise floor (placebo)\n\n200 random constant per-coin features, pct-ranked within M, blended at weight 0.10 into the live score; partition_test (risk-matched) vs live.\n")
    P(f"- paired t_NW: mean {t.mean():.2f}, sd {t.std():.2f}, 5/50/95/99th pct {np.percentile(t,5):.2f}/{np.median(t):.2f}/{np.percentile(t,95):.2f}/{np.percentile(t,99):.2f}, max {t.max():.2f}")
    P(f"- t_NW ≥ 1.5: {np.mean(t>=1.5)*100:.1f}%;  full adoption rule passes: {ad.sum()}/200 = {ad.mean()*100:.1f}%")
    P(f"- years≥5/6: {np.mean([int(r['years_won'][0])>=5 for r in pl])*100:.1f}%, groups≥4/5: {np.mean([int(r['coin_groups_won'][0])>=4 for r in pl])*100:.1f}%, both regimes: {np.mean([r['regime_btc_up_bp']>0 and r['regime_btc_down_bp']>0 for r in pl])*100:.1f}%")
    P(f"- placebo-book SR: mean {s.mean():.2f}, sd {s.std():.2f}, range {s.min():.2f}..{s.max():.2f} (live {sr(x0):.2f})")
except FileNotFoundError: P("placebo pending")
open("analysis.md","w").write("\n".join(out)); print("\n".join(out))
