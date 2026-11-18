import math
M="Pet_Pinchy_Balboa"
md=api.mesh_data(M); Q=md['positions']; B=[Q[i*3:i*3+3] for i in range(len(Q)//3)]; idx=list(md['vertices'])
api.select([M])
for i,p in enumerate(B):
    if math.dist(p,(0.22,0.37,0.02))<0.035:
        w=api.vertex_weights(idx[i]); print(i,[round(v,2) for v in p],[(j[4:],round(x,2)) for j,x in w])
