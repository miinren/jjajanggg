# Wave 3 (pre-registered single trial): minvar short leg with a notional floor so every short is >= $5 at $330 x 1.4 gross.
# floor: x >= 0.4 * equal weight within the short leg (0.4 * 0.55/20 * 462 = $5.1). Judged vs B on the pre-registered wave-2 rule.
from lib import *
def minvar_floor(i, longs, shorts):
    a, b = minvar(i, longs, shorts); x = b / 0.55; e = 1 / len(shorts)
    for _ in range(10): x = np.clip(x, 0.4 * e, 2 * e); x /= x.sum()
    CV["minvar"].append(x.std() / x.mean()); return a, 0.55 * x
df, cm = avg8(leg_weights=minvar_floor)
s1 = pickle.load(open(f"{OUT}/s1.pkl", "rb")); B = s1["B"]["df"]; cB = np.load(f"{OUT}/coin_B.npy")
vref = cut(B.net).std(); rb_, rc = risk(B, vref), risk(df, vref)
r = h.partition_test(D, (df, cm), (B, cB), verbose=False); st = stats(df)
print("CV", np.mean(CV["minvar"]))
print("SR %.2f  @8 %.2f @12 %.2f  t %.2f yrs %s grp %s  mdd2 %.1f minYr %.2f" % (st["SR"], sr_at(df, 8), sr_at(df, 12), r["tNW"], r["years_won"], r["coin_groups_won"], st["mdd_at2pct"], st["minYrSR"]))
print("dCVaR %.1f dW20 %.0f  2022-06-13 %.0f (B %.0f)" % (rb_["cvar5"] - rc["cvar5"], rb_["w20"] - rc["w20"], rc["d20220613"], rb_["d20220613"]))
pickle.dump(dict(df=df, r=r), open(f"{OUT}/s3_floor.pkl", "wb"))
