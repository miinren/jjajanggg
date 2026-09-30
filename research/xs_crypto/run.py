import time, pickle, numpy as np, pandas as pd, cloud_harness as h
from multiprocessing import Pool
D = h.Data()
e = D.resid; el = e.shift(1)
def ar1_idio(L, W=336):
    mp = min(200, int(L*0.6))
    phi = ((e*el).rolling(W, min_periods=200).mean() / (el*el).rolling(W, min_periods=200).mean()).clip(-0.5, 0.5)
    return (e - phi*el).rolling(L, min_periods=mp).std()
pF = D.F.where(D.M).rank(1, pct=True).fillna(0.5)
IDIO = {}
def live_score(L=336, fw=0.25):
    if L not in IDIO: IDIO[L] = ar1_idio(L).where(D.M).rank(1, pct=True)
    return (1-fw)*IDIO[L] + fw*pF if fw > 0 else IDIO[L]
# precompute scores for all L in parent so forked workers share them
Ls = [168, 240, 336, 504, 720]
for L in Ls: live_score(L)
S0 = live_score()
BASE = h.live_book(D, score=S0)
print(h.summary(BASE[0]), flush=True)

def run_cfg(kw):
    kw = dict(kw); L = kw.get("L", 336); fw = kw.pop("fw", 0.25)
    df, _ = h.live_book(D, score=live_score(L, fw), **kw)
    return df

def run_placebo(seed):
    rng = np.random.default_rng(1000+seed)
    f = pd.DataFrame(np.broadcast_to(rng.random(len(D.cols)), (len(D.idx), len(D.cols))), index=D.idx, columns=D.cols)
    pP = f.where(D.M).rank(1, pct=True)
    sc = 0.9*S0 + 0.1*pP
    c = h.live_book(D, score=sc)
    r = h.partition_test(D, c, BASE, verbose=False)
    r["SR"] = h.summary(c[0])["all"]["SR"]
    return r

if __name__ == "__main__":
    cfgs = {}
    for N in [12,15,18,20,22,25,30]: cfgs[("N",N)] = dict(N=N)
    for L in Ls: cfgs[("L",L)] = dict(L=L)
    for fw in [0,0.1,0.25,0.4,0.5]: cfgs[("fw",fw)] = dict(fw=fw)
    for ev in [4,6,8,12,24]: cfgs[("every",ev)] = dict(every=ev)
    for st in [0.2,0.3,0.4,0.6,1.0]: cfgs[("stop",st)] = dict(stop=st, long_stop=st)
    cfgs[("stop","off")] = dict(stops=False)
    for kx in [0.0,0.25,0.5,1.0]: cfgs[("keepx",kx)] = dict(keepx=kx)
    for N in [12,16,20,25,30]:
        for L in Ls: cfgs[("NxL",N,L)] = dict(N=N, L=L)
    keys = list(cfgs)
    t = time.time()
    with Pool(4) as p:
        out = p.map(run_cfg, [cfgs[k] for k in keys])
    res = dict(zip(keys, out)); print("sweeps", time.time()-t, flush=True)
    pickle.dump(dict(base=BASE[0], sweeps=res), open("sweeps.pkl","wb"))
    t = time.time()
    with Pool(4) as p:
        pl = p.map(run_placebo, range(200))
    print("placebo", time.time()-t, flush=True)
    pickle.dump(pl, open("placebo.pkl","wb"))
