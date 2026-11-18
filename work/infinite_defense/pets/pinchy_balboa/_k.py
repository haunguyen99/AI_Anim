md=api.mesh_data("Pet_Pinchy_Balboa"); Q=md['positions']; B=[Q[i*3:i*3+3] for i in range(len(Q)//3)]
g=[p for p in B if p[0]>0.329 and 0.17<p[1]<0.42]
print(len(g), "glove a-range", min(p[0] for p in g))
top=[p for p in g if p[1]>0.34]; print("top knob", len(top), "x", round(min(p[0] for p in top),3), round(max(p[0] for p in top),3), "z", round(min(p[2] for p in top),3), round(max(p[2] for p in top),3))
for lo,hi in ((.329,.36),(.36,.38),(.38,.40),(.40,.42),(.42,.45)):
    s=[p for p in g if lo<=p[0]<hi]; print(lo,hi,len(s), "y %.2f-%.2f z %.2f-%.2f"%(min(p[1] for p in s),max(p[1] for p in s),min(p[2] for p in s),max(p[2] for p in s)) if s else "")
