"""Sua mesh bi Frolvy xuat sai khung toa do (vd Nova vu khi vk_Hero_NOVA1, 2026-11-18): Frolvy ghi dinh cua mot so object o
khung rieng (xoay hoan vi truc + dich) trong khi Model Lcl = 0, nen mesh nam sai cho trong Unity. Cong cu tu khop khung
tu du lieu that cua Frolvy (api.mesh_data(obj) -> json) roi ghi lai Vertices + Normals cua FBX ASCII ve dung vi tri the gioi.

  1) trong Frolvy:  json.dump(api.mesh_data("<object>"), open("/tmp/x.json","w"))
  2) python3 -I tools/fbx_fix_mesh_frame.py in.fbx out.fbx <ten Model mesh> /tmp/x.json

Khop: FBX_vertex[i] = sg * Frolvy_corner[perm] + t (perm = hoan vi truc, sg = dau, phai la phep xoay det>0). Bao loi neu sai so > 1e-3."""
import itertools, json, re, sys

src, dst, name, jpath = sys.argv[1:5]
t = open(src, encoding="utf-8").read()
d = json.load(open(jpath))
pos, fc = d["positions"], d["face_corners"]
P = [(pos[3 * i], pos[3 * i + 1], pos[3 * i + 2]) for i in fc]

mid = re.search(r'\tModel: (\d+), "Model::%s", "Mesh"' % re.escape(name), t)
assert mid, "khong thay Model mesh " + name
mid = mid.group(1)
gid = None
for a, b in re.findall(r'C: "OO",\s*(\d+),\s*(\d+)', t):
    if b == mid and re.search(r'\tGeometry: %s,' % a, t):
        gid = a
assert gid, "khong thay Geometry cua " + name
gm = re.search(r'\tGeometry: %s, [^\n]*\{.*?\n\t\}' % gid, t, flags=re.S)
g = gm.group(0)
vm = re.search(r'(Vertices: \*\d+ \{\s*a: )([^}]*)(\})', g)
v = [float(x) for x in vm.group(2).split(",")]
V = [(v[i], v[i + 1], v[i + 2]) for i in range(0, len(v), 3)]
assert len(V) == len(P), ("so dinh khac nhau", len(V), len(P))

best = None
for perm in itertools.permutations(range(3)):
    for sg in itertools.product((1, -1), repeat=3):
        tt = [V[0][k] - sg[k] * P[0][perm[k]] for k in range(3)]
        err = max(abs(V[i][k] - (sg[k] * P[i][perm[k]] + tt[k])) for i in range(len(V)) for k in range(3))
        if best is None or err < best[0]:
            best = (err, perm, sg, tt)
err, perm, sg, tt = best
det = 1
for a in range(3):
    for b in range(a + 1, 3):
        if perm.index(a) > perm.index(b):
            det = -det
for s in sg:
    det *= s
print("khop: perm", perm, "dau", sg, "dich", [round(x, 3) for x in tt], "sai so", err, "det", det)
assert err < 1e-3, "khong khop duoc khung"
assert det > 0, "phep khop la guong (det<0): can dao chieu mat"

def back(vec, shift):   # FBX -> Frolvy (the gioi)
    out = [0.0] * 3
    for k in range(3):
        out[perm[k]] = sg[k] * (vec[k] - (tt[k] if shift else 0.0))
    return out

nv = []
for p in V:
    nv += back(p, True)
g2 = g.replace(vm.group(0), vm.group(1) + ",".join("%.6f" % x for x in nv) + vm.group(3), 1)
nm = re.search(r'(Normals: \*\d+ \{\s*a: )([^}]*)(\})', g2)
if nm:
    n = [float(x) for x in nm.group(2).split(",")]
    out = []
    for i in range(0, len(n), 3):
        out += back(n[i:i + 3], False)
    g2 = g2.replace(nm.group(0), nm.group(1) + ",".join("%.6f" % x for x in out) + nm.group(3), 1)
t = t.replace(g, g2, 1)
open(dst, "w", encoding="utf-8", newline="\n").write(t)
print("da ghi", dst, "(", len(V), "dinh )")
