"""Them BindPose (FbxPose) vao FBX ASCII xuat tu Frolvy. Frolvy khong ghi Pose -> Unity doc bindpose = 0 (mesh skin vo,
dau/chan bay khoi mai, Pebble Turtle 2026-11-12). Pose: ma tran the gioi cua moi xuong (tu Lcl Translation, xoay 0, scale 1)
va moi mesh (don vi). usage: py tools/fbx_add_bindpose.py in.fbx out.fbx"""
import re, sys, os, importlib.util
spec = importlib.util.spec_from_file_location("k", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fbx_ascii_keep.py"))
k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
t = open(sys.argv[1], encoding="utf-8").read()
lines, objs, conns = k.parse(t)
models = {o["id"]: o for o in objs if o["type"] == "Model"}
parent = {a: b for _, kind, a, b in conns if kind == "OO" and a in models and b in models}
def local(o):
    blk = "\n".join(lines[o["span"][0]:o["span"][1] + 1])
    tr = re.search(r'P: "Lcl Translation"[^\n]*"A",([^\n]*)', blk); rot = re.search(r'P: "Lcl Rotation"[^\n]*"A",([^\n]*)', blk)
    sc = re.search(r'P: "Lcl Scaling"[^\n]*"A",([^\n]*)', blk)
    r = [float(x) for x in rot.group(1).split(",")]; s = [float(x) for x in sc.group(1).split(",")]
    assert max(abs(x) for x in r) < 1e-4 and all(abs(x - 1) < 1e-6 for x in s), ("rot/scale not trivial", o["name"])
    return [float(x) for x in tr.group(1).split(",")]
def world(i):
    p = local(models[i]); j = parent.get(i)
    if j is None: return p
    w = world(j); return [p[n] + w[n] for n in range(3)]
nodes = []
for i, o in models.items():
    w = world(i) if o["sub"] != "Mesh" else [0, 0, 0]
    m = "1,0,0,0,0,1,0,0,0,0,1,0,%.6f,%.6f,%.6f,1" % tuple(w)
    nodes.append("\t\tPoseNode:  {\n\t\t\tNode: %d\n\t\t\tMatrix: *16 {\n\t\t\t\ta: %s\n\t\t\t}\n\t\t}\n" % (i, m))
pose = '\tPose: 1999999, "Pose::BIND_POSES", "BindPose" {\n\t\tType: "BindPose"\n\t\tVersion: 100\n\t\tNbPoseNodes: %d\n%s\t}\n' % (len(nodes), "".join(nodes))
text = "\n".join(lines)
text = re.sub(r'(\nObjects:  \{\n)', lambda m: m.group(1) + pose, text, count=1)
text = re.sub(r'(\tObjectType: "GlobalSettings" \{\s*\n\t\tCount: 1\n\t\})', lambda m: m.group(1) + '\n\tObjectType: "Pose" {\n\t\tCount: 1\n\t}', text, count=1)
m = re.search(r'Definitions:  \{\n\tVersion: 100\n\tCount: (\d+)', text)
text = text.replace(m.group(0), m.group(0).replace("Count: " + m.group(1), "Count: %d" % (int(m.group(1)) + 1)), 1)
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(text)
print("pose nodes", len(nodes))
