# Chay trong Frolvy (scene rig/idle/attack CU dang mo, mesh cu da bind): thay mesh cu bang mesh moi
# (xoay 180 quanh Y + freeze), bind lai o bind pose, chuyen trong so cu theo dinh gan nhat.
import math
from collections import defaultdict
FBX = '/home/ngocvb/Projects/endless-kicker/Assets/Kho/Skin/mesh/Pet_new/mesh/Pet_Mecha_Pup.fbx'
OLD = 'Pet_Mecha_Pup'
md = api.mesh_data(OLD); V0 = md['vertices']; P0 = md['positions']
op = [P0[i*3:i*3+3] for i in range(len(V0))]
ow = [api.vertex_weights(g) for g in V0]
assert all(ow), 'mesh cu thieu trong so'
used_j = sorted({j for w in ow for j, _ in w})
cell = 0.02; grid = defaultdict(list)
for i, p in enumerate(op): grid[(int(p[0]//cell), int(p[1]//cell), int(p[2]//cell))].append(i)
def nn(q):
    c = (int(q[0]//cell), int(q[1]//cell), int(q[2]//cell)); best = (9, None)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for i in grid.get((c[0]+dx, c[1]+dy, c[2]+dz), []):
                    d = math.dist(q, op[i])
                    if d < best[0]: best = (d, i)
    return best
print('go_to_bind_pose', api.go_to_bind_pose())
before = set(api.ls())
print('import', api.import_file(FBX, 'add'))
new = [x for x in api.ls() if x not in before and api.node_type(x) == 'Object'][0]
api.select([new]); api.rotate(new, 0, 180, 0); api.freeze_transform()
nm = api.mesh_data(new); NV = nm['vertices']; NP = nm['positions']
ds = [nn(NP[i*3:i*3+3]) for i in range(len(NV))]
far = [d for d, _ in ds if d > 1e-4]
print('new verts', len(NV), 'old', len(V0), 'far', len(far))
assert not far
print('delete old', api.delete_node(OLD))
print('rename', api.rename(new, OLD))
api.select([OLD])
print('bind', api.bind_skin(used_j))
rows = []
for k in range(len(NV)):
    w = [(j, v) for j, v in ow[ds[k][1]] if v > 1e-6]; s = sum(v for _, v in w)
    rows.append([(j, v/s) for j, v in w])
print('weights', api.set_skin_weights(list(NV), rows))
api.set_frame(1); api.set_frame(0)
