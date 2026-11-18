md = api.mesh_data("Pet_Night_Bat"); P = md['positions']; P=[P[i*3:i*3+3] for i in range(len(P)//3)]
def rng(name, sel):
    v=[p for p in P if sel(p)]
    if not v: print(name,"none"); return
    print(name, len(v), "x %.3f %.3f y %.3f %.3f z %.3f %.3f"%(min(p[0] for p in v),max(p[0] for p in v),min(p[1] for p in v),max(p[1] for p in v),min(p[2] for p in v),max(p[2] for p in v)))
rng("wing |x|>.3", lambda p: abs(p[0])>0.3)
rng("wing .2-.3", lambda p: 0.2<abs(p[0])<0.3 and p[1]<0.4)
rng("ear y>.5", lambda p: p[1]>0.5)
rng("ear y>.45 & |x|>.1", lambda p: p[1]>0.45 and abs(p[0])>0.1)
rng("head |x|<.15 y .22-.5 z>.1", lambda p: abs(p[0])<0.15 and 0.22<p[1]<0.5 and p[2]>0.1)
rng("body y<.17 |x|<.15", lambda p: p[1]<0.17 and abs(p[0])<0.15)
rng("z>.25", lambda p: p[2]>0.25)
