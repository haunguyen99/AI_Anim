"""Like fbx_add_bindpose.py + fbx_unity_bind.py, but for rigs whose bones have joint ORIENT (Lcl Rotation != 0 at bind), e.g.
Mecha Pup (Build Rig aims bones along X). The two tools assert 'no rotation' and refuse.
 - BindPose: world matrix of every bone = parent world x (T R S) of its Lcl values (FBX XYZ euler, R = Rz Ry Rx); mesh = identity.
 - Cluster Transform = inverse(TransformLink)   (Unity reads Transform as the bind pose; Frolvy writes identity there).
 - Check: computed world of every skinned bone must equal its TransformLink (printed as max error).
usage: py tools/fbx_unity_bind_rot.py in.fbx out.fbx"""
import re, sys, os, math, importlib.util
spec = importlib.util.spec_from_file_location("k", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fbx_ascii_keep.py"))
k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
t = open(sys.argv[1], encoding="utf-8").read()
lines, objs, conns = k.parse(t)
models = {o["id"]: o for o in objs if o["type"] == "Model"}
parent = {a: b for _, kind, a, b in conns if kind == "OO" and a in models and b in models}

def mul(A, B):   # 4x4, column-major arrays (A*B)
    return [sum(A[r + 4 * i] * B[i + 4 * c] for i in range(4)) for c in range(4) for r in range(4)]
def local(o):
    blk = "\n".join(lines[o["span"][0]:o["span"][1] + 1])
    g = lambda n: [float(x) for x in re.search(r'P: "%s"[^\n]*"A",([^\n]*)' % n, blk).group(1).split(",")]
    tr, rot, sc = g("Lcl Translation"), g("Lcl Rotation"), g("Lcl Scaling")
    assert all(abs(x - 1) < 1e-6 for x in sc), ("scale not 1", o["name"])
    ax, ay, az = [math.radians(x) for x in rot]
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    Rx = [1, 0, 0, 0, 0, cx, sx, 0, 0, -sx, cx, 0, 0, 0, 0, 1]
    Ry = [cy, 0, -sy, 0, 0, 1, 0, 0, sy, 0, cy, 0, 0, 0, 0, 1]
    Rz = [cz, sz, 0, 0, -sz, cz, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    R = mul(Rz, mul(Ry, Rx)); R[12], R[13], R[14] = tr
    return R
cache = {}
def world(i):
    if i not in cache:
        L = local(models[i]); j = parent.get(i); cache[i] = L if j is None else mul(world(j), L)
    return cache[i]
def inv_rigid(M):
    R = [[M[r + 4 * c] for c in range(3)] for r in range(3)]; tt = M[12:15]
    out = [0.0] * 16
    for r in range(3):
        for c in range(3): out[r + 4 * c] = R[c][r]
        out[12 + r] = -sum(R[c][r] * tt[c] for c in range(3))
    out[15] = 1.0; return out
fmt = lambda M: ",".join("%.6f" % (0.0 if abs(x) < 5e-7 else x) for x in M)

# clusters: Transform = inverse(TransformLink); check against the computed world
name2id = {o["name"].replace("Model::", ""): i for i, o in models.items()}
err = [0.0]
def fix(m):
    b = m.group(0)
    link = [float(x) for x in re.search(r'TransformLink: \*16 \{\s*a: ([^\n]*)', b).group(1).split(",")]
    nm = re.search(r'"SubDeformer::Cluster ([^"]*)"', b).group(1)
    if nm in name2id: err[0] = max(err[0], max(abs(a - c) for a, c in zip(link, world(name2id[nm]))))
    return re.sub(r'(\n\t\tTransform: \*16 \{\s*a: )[^\n]*', lambda mm: mm.group(1) + fmt(inv_rigid(link)), b, count=1)
t, ncl = re.subn(r'\tDeformer: \d+, "SubDeformer::[^"]*", "Cluster" \{.*?\n\t\}', fix, t, flags=re.S)
ident = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
nodes = []
for i, o in models.items():
    M = ident if o["sub"] == "Mesh" else world(i)
    nodes.append("\t\tPoseNode:  {\n\t\t\tNode: %d\n\t\t\tMatrix: *16 {\n\t\t\t\ta: %s\n\t\t\t}\n\t\t}\n" % (i, fmt(M)))
pose = '\tPose: 1999999, "Pose::BIND_POSES", "BindPose" {\n\t\tType: "BindPose"\n\t\tVersion: 100\n\t\tNbPoseNodes: %d\n%s\t}\n' % (len(nodes), "".join(nodes))
t = re.sub(r'(\nObjects:  \{\n)', lambda m: m.group(1) + pose, t, count=1)
t = re.sub(r'(\tObjectType: "GlobalSettings" \{\s*\n\t\tCount: 1\n\t\})', lambda m: m.group(1) + '\n\tObjectType: "Pose" {\n\t\tCount: 1\n\t}', t, count=1)
m = re.search(r'Definitions:  \{\n\tVersion: 100\n\tCount: (\d+)', t)
t = t.replace(m.group(0), m.group(0).replace("Count: " + m.group(1), "Count: %d" % (int(m.group(1)) + 1)), 1)
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(t)
print("clusters %d, pose nodes %d, max |computed world - TransformLink| = %.2e" % (ncl, len(nodes), err[0]))
