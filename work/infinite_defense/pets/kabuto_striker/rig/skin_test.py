import math
M="Pet_Kabuto_Striker"; CT=[c for c in api.ls("Curve") if c.startswith("CTL_") and c!="CTL_Main"]
def setpose(d):
    for c in CT: api.rotate(c,0,0,0); api.move(c,0,0,0)
    for c,v in d.items(): api.rotate(c,*v)
    api.set_frame(3); api.set_frame(0)
setpose({}); md=api.mesh_data(M); idx=list(md['vertices']); P=md['positions']; P0=[P[i*3:i*3+3] for i in range(len(idx))]
pos={v:i for i,v in enumerate(idx)}; E=set(); c=0
for s in md['face_sizes']:
    cs=[pos[q] for q in md['face_corners'][c:c+s]]; c+=s
    for k in range(s): E.add(tuple(sorted((cs[k],cs[(k+1)%s]))))
def rep(name,d):
    setpose(d); Q=api.mesh_data(M,True)['positions']; Q=[Q[i*3:i*3+3] for i in range(len(idx))]
    mv=max(math.dist(Q[i],P0[i]) for i in range(len(idx)))
    w=[]
    for a,b in E:
        l0=math.dist(P0[a],P0[b])
        if l0>1e-4: w.append((math.dist(Q[a],Q[b])/l0,[round(t,2) for t in P0[a]]))
    w.sort(reverse=True); print(name,"maxmove %.3f"%mv,"worst stretch",[(round(r,2),p) for r,p in w[:3]],"min",round(min(r for r,_ in w),2))
rep("head x25",{"CTL_Head_M":(25,0,0)}); rep("head y25",{"CTL_Head_M":(0,25,0)})
rep("chest x20",{"CTL_Chest_M":(20,0,0)}); rep("root x15",{"CTL_Root_M":(15,0,0)})
rep("horn1L z25",{"CTL_Horn1_L":(0,0,25)}); rep("horn2L z25",{"CTL_Horn2_L":(0,0,25)})
rep("sodeL z25",{"CTL_Sode_L":(0,0,25)}); rep("sodeL x25",{"CTL_Sode_L":(25,0,0)})
rep("skirtF x25",{"CTL_SkirtF_M":(25,0,0)}); rep("skirtB x25",{"CTL_SkirtB_M":(-25,0,0)}); rep("skirtS z25",{"CTL_SkirtS_L":(0,0,25)})
rep("ffoot x30",{"CTL_FFoot_L":(30,0,0)}); rep("rfoot x30",{"CTL_RFoot_R":(30,0,0)})
setpose({})
