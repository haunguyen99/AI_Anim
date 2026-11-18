md = api.mesh_data("Pet_Pinchy_Balboa"); Q = md['positions']; P=[Q[i*3:i*3+3] for i in range(len(Q)//3)]
sel=[p for p in P if p[1]<0.2 and abs(p[0])<0.35]
import collections
# cluster by grid
cl=collections.defaultdict(list)
for p in sel: cl[(round(p[0]/0.08),round(p[2]/0.08))].append(p)
for k,v in sorted(cl.items()):
    print(k,len(v),"y %.3f..%.3f"%(min(p[1] for p in v),max(p[1] for p in v)), "x %.3f z %.3f"%(sum(p[0] for p in v)/len(v),sum(p[2] for p in v)/len(v)))
# arm stalk: verts in body with |x|>0.2
st=[p for p in P if abs(p[0])>0.2 and abs(p[0])<0.35 and p[0]>0]
print("stalk",len(st),min(p[0] for p in st),max(p[0] for p in st),min(p[1] for p in st),max(p[1] for p in st),min(p[2] for p in st),max(p[2] for p in st))
