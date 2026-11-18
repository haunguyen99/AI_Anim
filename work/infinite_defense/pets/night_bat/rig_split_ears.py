# Detach the two ear shells from the welded mesh (faces whose vertices are ALL ear-classified). Ear/wing/head are welded in the source model by long faces;
# a skin cannot separate welded surfaces without stretching, so the ears become their own shells (same positions = no visual change at bind).
M = "Pet_Night_Bat"
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t * t * (3 - 2 * t)
md = api.mesh_data(M); idx = list(md['vertices']); P = md['positions']; P = [P[i * 3:i * 3 + 3] for i in range(len(idx))]
def edom(i):
    x, y, z = P[i]; ax = abs(x)
    q = (((ax / 0.19) ** 2) + (((y - 0.345) / 0.175) ** 2) + (((z - 0.15) / 0.18) ** 2)) ** 0.5
    d = y - (0.345 - 0.1 * (ax - 0.14))
    ew = sm(ramp(d, 0.0, 0.035)) * sm(ramp(ax, 0.06, 0.11)) * sm(ramp(q, 1.0, 1.2))
    ww = sm(ramp(ax, 0.15, 0.20)) * (1 - sm(ramp(z, 0.07, 0.12))) * sm(ramp(q, 1.0, 1.2))
    return (ew >= ww and ew > 0.5) or (q > 1.12 and y > 0.40 and ax > 0.04)   # everything standing out of the head sphere above the wing line = ear
E = [edom(i) for i in range(len(idx))]
def wdom(i):
    x, y, z = P[i]; ax = abs(x)
    q = (((ax / 0.19) ** 2) + (((y - 0.345) / 0.175) ** 2) + (((z - 0.15) / 0.18) ** 2)) ** 0.5
    return (not E[i]) and sm(ramp(ax, 0.15, 0.20)) * (1 - sm(ramp(z, 0.07, 0.12))) * sm(ramp(q, 1.0, 1.2)) > 0.5
Wv = [wdom(i) for i in range(len(idx))]
pos = {v: i for i, v in enumerate(idx)}; faces = []; c = 0
for s in md['face_sizes']:
    faces.append([pos.get(q, q) for q in md['face_corners'][c:c + s]]); c += s
ef = [fi for fi, f in enumerate(faces) if all(E[v] for v in f) or (any(E[v] for v in f) and any(Wv[v] for v in f) and not any((not E[v]) and (not Wv[v]) for v in f))]   # all-ear faces + the web faces (ear+wing vertices only): the web stays with the ear, the wing sheet simply moves away from it   # ONLY faces whose vertices are all ear: the web between ear and wing stays in the body and rides with the wing (taking it with the ear left holes at the shoulder)
print("ear faces", len(ef), "of", len(faces))
api.select([M]); api.set_component_mode("face")
print(api.select_components("face", ef)); print(api.extract_faces()); api.set_component_mode("object"); api.select([])
_new = [o for o in api.ls("Object") if o.startswith("Pet_Night_Bat") and o != M]
if _new and _new[0] != "Pet_Night_Bat_Ears": print("rename", api.rename(_new[0], "Pet_Night_Bat_Ears"))
md2 = api.mesh_data(M); print("verts", len(md2['vertices']), "faces", len(md2['face_sizes']), "objects", api.ls("Object"))
