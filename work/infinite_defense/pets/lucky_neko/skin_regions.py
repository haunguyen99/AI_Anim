# Per joint: vertices it influences (w>0.05): count, bounds, mean; plus vertices whose dominant joint is far from the nearest-bone choice.
import math
J = [j for j in api.ls("Joint") if j.startswith("DEF_") and "Muzzle" not in j]
JP = {}
for j in J:
    m = api.rest_matrix(j) if hasattr(api, "rest_matrix") else None
    JP[j] = (m[12], m[13], m[14]) if m and len(m) >= 15 else None
print("rest_matrix ok" if JP[J[0]] else "no rest_matrix", JP[J[0]])
for o in api.ls("Object"):
    md = api.mesh_data(o); idx = list(md['vertices']); P = md['positions']
    reg = {}
    for k, v in enumerate(idx):
        p = P[3*k:3*k+3]
        for j, w in api.vertex_weights(v):
            if w > 0.05: reg.setdefault(j, []).append((p, w))
    print("==", o)
    for j in sorted(reg, key=lambda j: J.index(j) if j in J else 99):
        L = reg[j]; xs = [p[0] for p, _ in L]; ys = [p[1] for p, _ in L]; zs = [p[2] for p, _ in L]
        full = sum(1 for _, w in L if w > 0.95)
        print("%-16s n%3d full%3d x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f joint %s" % (j[4:], len(L), full, min(xs), max(xs), min(ys), max(ys), min(zs), max(zs), tuple(round(c, 3) for c in JP[j]) if JP.get(j) else "?"))
