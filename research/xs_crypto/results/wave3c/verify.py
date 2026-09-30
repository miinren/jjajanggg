# ext4 with execf=None / no masks must reproduce ext3 (B-MV) exactly at every offset.
from lib3c import *
mx = 0.0
for off in range(8):
    a = ext3.book(D, S0, offset=off, leg_weights=minvar_floor, **BK); b = ext4.book(D, S0, offset=off, leg_weights=minvar_floor, **BK)
    m = max(float((a[0] - b[0]).abs().max().max()), float(np.abs(a[1] - b[1]).max())); mx = max(mx, m); print(off, m, flush=True)
# a no-op exec policy (always f=1) must also reproduce it
b = ext4.book(D, S0, offset=0, leg_weights=minvar_floor, execf=lambda *a: 1.0, H=4, **BK)
a = ext3.book(D, S0, offset=0, leg_weights=minvar_floor, **BK)
print("noop-exec diff", float((a[0] - b[0]).abs().max().max()), float(np.abs(a[1] - b[1]).max()))
print("max diff", mx)
df, cm, per = base(); s = stats(df)
print("B-MV 8clk SR %.3f @8 %.3f @12 %.3f mdd2 %.1f minYr %.2f" % (s["SR"], sr_at(df, 8), sr_at(df, 12), s["mdd_at2pct"], s["minYrSR"]))
print({o: round(srx(cut(d.net)), 2) for o, d in per.items()})
