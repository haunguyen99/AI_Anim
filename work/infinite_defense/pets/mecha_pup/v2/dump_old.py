# Chay trong Frolvy (rig cu dang mo): luu vi tri dinh + trong so skin cu ra JSON.
import json
n = "Pet_Mecha_Pup"
md = api.mesh_data(n)
V = list(md['vertices']); P = md['positions']
out = {"verts": V, "pos": [P[i*3:i*3+3] for i in range(len(V))], "w": {}}
for g in V:
    out["w"][str(g)] = api.vertex_weights(g)
json.dump(out, open("/tmp/mecha_old_weights.json", "w"))
print(len(V), sum(1 for g in V if out["w"][str(g)]))
