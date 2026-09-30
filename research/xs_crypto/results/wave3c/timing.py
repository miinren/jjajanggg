import sys,time; sys.path.insert(0,"/root/work"); sys.path.insert(0,"/root/work/results/wave2")
t=time.time()
from common import D,S0
print("load",time.time()-t); import ext3, resource
t=time.time(); d,c=ext3.book(D,S0,short_frac=0.55,stop=0.2,N=12,NS=20); print("book",time.time()-t)
print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6,"GB")
