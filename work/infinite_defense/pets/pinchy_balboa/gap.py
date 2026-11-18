import math
M="Pet_Pinchy_Balboa"
def pts(md): Q=md['positions']; return [Q[i*3:i*3+3] for i in range(len(Q)//3)]
mdb=api.mesh_data(M); B=pts(mdb)
for f in (0,6,12,18,24,30,36,42):
    api.set_frame(1); api.set_frame(f); Pp=pts(api.mesh_data(M, posed=True))
    out=[]
    for sg in (1,-1):
        st=[i for i,p in enumerate(B) if sg*p[0]>0.26 and sg*p[0]<0.34 and 0.2<p[1]<0.4 and abs(p[2])<0.12]
        gl=[i for i,p in enumerate(B) if sg*p[0]>0.329 and 0.17<p[1]<0.42]
        # stalk verts near the glove in bind: pairs with bind dist < .02
        pr=[(i,j) for i in st for j in gl if math.dist(B[i],B[j])<0.02]
        gb=max((math.dist(B[i],B[j]) for i,j in pr),default=0); gp=max((math.dist(Pp[i],Pp[j]) for i,j in pr),default=0)
        out.append((len(pr),round(gb,3),round(gp,3)))
    print(f,out)
api.set_frame(1); api.set_frame(0)
