import pickle, numpy as np, pandas as pd
from common import *
r3 = pickle.load(open("exp3.pkl", "rb")); base = pickle.load(open("base_ext.pkl", "rb"))
cands = {"LIVE (20/20, 50/50, stop .40)": base, "A: 8L/20S only": r3[("5050", 0.4, 8)][1],
         "B: sf.55 ss.20 12L/20S": r3[(0.55, 0.2, 12)][1], "C: sf.60 ss.20 12L/20S": r3[(0.6, 0.2, 12)][1]}
v0 = cut(base.net).std()
out = []
P = out.append
P("| Book | SR | SR 20-22 | SR 23-25 | worst yr SR | bp/day @1x | vol-matched gross (≙ live 1.5x) | ann. return at that gross | MDD at that gross | worst day | worst 20d | SR @8bp | SR @12bp | turnover/day |")
P("|" + "---|" * 14)
for n, df in cands.items():
    x = cut(df.net); g = 1.5 * v0 / x.std(); xs = g * x
    cum = xs.cumsum(); mdd = (cum - cum.cummax()).min()
    yr = x.groupby(x.index.year).apply(lambda y: y.mean()/y.std()*np.sqrt(365))
    s = lambda y: y.mean()/y.std()*np.sqrt(365)
    tcost = lambda c: cut(df.net + df.to*5.5e-4 - df.to*c*1e-4)
    P(f"| {n} | {s(x):.2f} | {s(x[x.index<'2023']):.2f} | {s(x[x.index>='2023']):.2f} | {yr.min():.2f} | {x.mean()*1e4:.1f} | {g:.2f}x | {xs.mean()*365*100:.0f}% | {mdd*100:.1f}% | {xs.min()*100:.1f}% | {xs.rolling(20).sum().min()*100:.1f}% | {s(tcost(8)):.2f} | {s(tcost(12)):.2f} | {cut(df.to).mean():.2f} |")
P("\nYearly SR:\n\n| Book | " + " | ".join(str(y) for y in range(2020, 2026)) + " |\n|" + "---|" * 7)
for n, df in cands.items():
    x = cut(df.net); yr = x.groupby(x.index.year).apply(lambda y: y.mean()/y.std()*np.sqrt(365)); P(f"| {n} | " + " | ".join(f"{v:.2f}" for v in yr) + " |")
C = cut(cands["C: sf.60 ss.20 12L/20S"]); B = cut(base)
P("\nLeg attribution bp/day (live → C): " + ", ".join(f"{k} {B[k].mean()*1e4:.1f}→{C[k].mean()*1e4:.1f}" for k in ["long", "short", "hedge", "fund"]))
P(f"Correlation of daily PnL live vs C: {B.net.corr(C.net):.2f}")
print("\n".join(out)); open("final.md", "w").write("\n".join(out))
