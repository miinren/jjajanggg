from common import *
import time; t=time.time()
b = ext.book(D, S0); ref = h.live_book(D, score=S0)
print("reproduce diff", float((b[0].net-ref[0].net).abs().max()), time.time()-t)
x = cut(b[0]); print(stats(b[0]))
print("mean bp/day", (x[["long","short","hedge","fund","to"]].mean()*1e4).round(2).to_dict())
print("std bp", (x[["long","short","hedge","fund"]].std()*1e4).round(1).to_dict())
print("corr\n", x[["long","short","hedge"]].corr().round(2))
worst = x.net.nsmallest(12); print((x.loc[worst.index, ["net","long","short","hedge","fund"]]*1e4).round(0))
cum=x.net.cumsum(); dd=cum-cum.cummax(); tr=dd.idxmin(); pk=cum[:tr].idxmax(); print("MDD", pk, tr, (x.loc[pk:tr,["long","short","hedge","fund"]].sum()*1e4).round(0).to_dict())
# top-5 drawdown episodes
import pickle; pickle.dump(b[0], open("base_ext.pkl","wb"))
