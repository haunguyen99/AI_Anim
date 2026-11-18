# Bind khi moi control = 0 roi ghi weight theo luat (cong 9885)
M = "Pet_Pinchy_Balboa"
for c in api.ls("Curve"):
    if c.startswith("CTL_"): api.rotate(c,0,0,0); api.move(c,0,0,0) if c=="CTL_Main" else None
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_")]
import math
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
api.select([M])
try: api.unbind_skin()
except Exception: pass
api.select([M]); api.bind_skin(DEF)
md = api.mesh_data(M); Q = md['positions']; P=[Q[i*3:i*3+3] for i in range(len(Q)//3)]
idx=list(md['vertices']); par=list(range(len(idx)))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
pos={v:i for i,v in enumerate(idx)}; c=0
for s in md['face_sizes']:
    cs=md['face_corners'][c:c+s]; c+=s
    for q in cs[1:]: par[f(pos.get(q,q))]=f(pos.get(cs[0],cs[0]))
comp={}
for i in range(len(idx)): comp.setdefault(f(i),[]).append(i)
cl=sorted(comp.values(), key=len, reverse=True)
kind={}
for vs in cl:
    xs=[P[i][0] for i in vs]; ys=[P[i][1] for i in vs]
    if len(vs)>300: k="body"
    elif len(vs)>100: k="gloveL" if sum(xs)>0 else "gloveR"
    else: k="bandB" if max(ys)>0.55 else "bandA"
    for i in vs: kind[i]=k
sm=lambda t: t*t*(3-2*t)
def armw(a,s,_):
    # along the arm axis: Arm1 (root bend) -> Arm2 over x .24-.31, Arm2 rigid over the stalk + cuff ring (.31-.35),
    # Arm2 -> Arm3 over the thin neck (.35-.385), Arm3 on the neck, ball 100% Glove from .40. Stalk and glove use the same blend where they touch.
    g=sm(ramp(a,0.37,0.40))
    t1=sm(ramp(a,0.235,0.325)); t2=sm(ramp(a,0.345,0.375))
    r={"DEF_Arm1_"+s:1-t1,"DEF_Arm2_"+s:t1*(1-t2),"DEF_Arm3_"+s:t1*t2}
    r={kk:vv*(1-g) for kk,vv in r.items()}; r["DEF_Glove_"+s]=g
    return r
rows=[]
for i,(x,y,z) in enumerate(P):
    k=kind[i]; a=abs(x); S="L" if x>0 else "R"; r={}
    if k.startswith("glove"):
        s=k[-1]; r=armw(a, s, 0.0)
    elif k=="bandA":
        t=ramp(-x,0.08,0.26); r={"DEF_BandA2_M":t,"DEF_BandA1_M":1-t}
    elif k=="bandB":
        t=ramp(-x,0.03,0.17); r={"DEF_BandB2_M":t,"DEF_BandB1_M":1-t}
    else:
        leg=max(ramp(y,0.22,0.12)*ramp(a,0.215,0.25), ramp(y,0.09,0.05)*ramp(a,0.17,0.20))
        gz={g:math.exp(-((z-zc)/0.05)**2) for g,zc in (("F",0.10),("M",-0.02),("B",-0.17))}; gs=sum(gz.values()); leg*=min(1.0,gs*1.4)   # smooth share between the 3 legs
        tip=ramp(y,0.10,0.04)
        arm=ramp(a,0.15,0.24)*ramp(y,0.15,0.22)*ramp(y,0.37,0.30)*ramp(abs(z),0.17,0.11)*(1-leg)
        ar=armw(a, S, 1.0)
        head=(lambda t: t*t*(3-2*t))(ramp(y,0.14,0.44))
        rest=1-leg-arm
        r={**{"DEF_Leg%s_%s"%(g,S):leg*gz[g]/gs*(1-tip) for g in gz},**{"DEF_Leg%sTip_%s"%(g,S):leg*gz[g]/gs*tip for g in gz},
           **{kk:arm*vv for kk,vv in ar.items()},
           "DEF_Head_M":rest*head,"DEF_Root_M":rest*(1-head)}
    row=sorted([(j,w) for j,w in r.items() if w>0.01],key=lambda t:-t[1])[:4]; s=sum(w for _,w in row)
    rows.append([(j,w/s) for j,w in row])
api.select([M]); api.set_skin_weights(idx, rows)
api.select([])
api.set_frame(3); api.set_frame(0)
print("skin ok", max(len(r) for r in rows))
