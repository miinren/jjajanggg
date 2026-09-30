import sys, time, pickle, numpy as np
sys.path.insert(0, "/root/work"); sys.path.insert(0, "/root/work/results/active")
from common import *
import ext_active as ea
BK = dict(short_frac=0.55, stop=0.2, N=12, NS=20)
t = time.time(); a = ext.book(D, S0, **BK); t1 = time.time() - t
t = time.time(); b = ea.book(D, S0, **BK); t2 = time.time() - t
print("times", t1, t2)
print("B df identical:", np.array_equal(a[0].to_numpy(), b[0].to_numpy()), "coin identical:", np.array_equal(a[1], b[1]))
print("max abs diff", np.abs(a[0].to_numpy() - b[0].to_numpy()).max())
print(stats(a[0]))
l0 = ext.book(D, S0); l1 = ea.book(D, S0)
print("LIVE identical:", np.array_equal(l0[0].to_numpy(), l1[0].to_numpy()), np.array_equal(l0[1], l1[1]))
# stop features on but thresholds that never bind -> should be identical too
c = ea.book(D, S0, **BK, trail=100.0, half_at=100.0, time_stop=10**6)
print("non-binding active opts identical:", np.array_equal(a[0].to_numpy(), c[0].to_numpy()))
pickle.dump(dict(B=b[0], LIVE=l0[0]), open("base.pkl", "wb"))
