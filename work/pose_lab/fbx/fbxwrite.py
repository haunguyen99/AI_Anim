"""Pose Lab model (glTF json) -> animation-only ASCII FBX 7.4 (Armature + skeleton, Lcl T/R(XYZ euler)/S curves), no meshes.
Spec for the JS port in work/pose_lab/fbx/fbxwrite.js (outputs must be byte-identical).
World rule (calibrated against Blender's own FBX of the same rig, all 60 bones):
FBX bone world = [R_gltf_world (unit scale) | 100 * t_gltf_world]."""
import math
import numpy as np
import gltfpose as g
from fbxbin import E, serialize

DT = 1539538600  # FBX ticks per frame at 30 fps
ARMATURE = True  # False: không bọc nút Armature, `root` là gốc (rig team Jungle/Western: avatar Humanoid không có Armature)
FPS = 30  # Jungle (24 fps): đặt fbxwrite.FPS = 24 và fbxwrite.DT = 46186158000 // 24 trước build()


def fmt(x):
    if x == 0:
        return "0"
    return "%.9g" % x


def euler_from(R, prev):
    ry = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    if abs(R[2, 0]) < 0.99999:
        rx = math.atan2(R[2, 1], R[2, 2])
        rz = math.atan2(R[1, 0], R[0, 0])
    else:
        rx = math.atan2(-R[1, 2], R[1, 1])
        rz = 0.0
    cands = []
    for (a, b, c) in ((rx, ry, rz), (rx + math.pi, math.pi - ry, rz + math.pi)):
        cands.append([math.degrees(a), math.degrees(b), math.degrees(c)])
    best = None
    for e in cands:
        e2 = list(e)
        if prev is not None:
            for i in range(3):
                while e2[i] - prev[i] > 180:
                    e2[i] -= 360
                while e2[i] - prev[i] < -180:
                    e2[i] += 360
        d = 0 if prev is None else sum(abs(e2[i] - prev[i]) for i in range(3))
        if best is None or d < best[0]:
            best = (d, e2)
    return best[1]


def skeleton(j):
    N = j["nodes"]
    names = [n["name"] for n in N]
    par = {}
    for i, n in enumerate(N):
        for c in n.get("children", []):
            par[c] = i
    root = names.index("root")
    order = []

    def walk(i):
        order.append(i)
        for c in N[i].get("children", []):
            walk(c)
    walk(root)
    return order, par


def build(path, take, out):
    j, acc = g.load(path)
    N = j["nodes"]
    order, par = skeleton(j)
    nk = len(acc(j["animations"][0]["samplers"][0]["input"]))
    names = (["Armature"] if ARMATURE else []) + [N[i]["name"] for i in order]
    parent = {N[i]["name"]: (N[par[i]]["name"] if par[i] in order else "Armature") for i in order}
    parent["Armature"] = None
    if not ARMATURE:
        parent["root"] = None
    T = {n: [] for n in names}
    R = {n: [] for n in names}
    prev = {}
    for k in range(nk):
        GW, _ = g.world(j, g.local_mats(j, acc, k))
        FW = {}
        for i in order:
            w = GW[i]
            s = np.linalg.norm(w[:3, 0])
            m = np.eye(4)
            m[:3, :3] = w[:3, :3] / s
            m[:3, 3] = w[:3, 3] * 100.0
            FW[N[i]["name"]] = m
        FW["Armature"] = np.eye(4)
        for n in names:
            loc = np.eye(4) if n == "Armature" else (np.linalg.inv(FW[parent[n]]) @ FW[n] if parent[n] else FW[n])
            e = euler_from(loc[:3, :3], prev.get(n))
            prev[n] = e
            T[n].append(loc[:3, 3].tolist())
            R[n].append(e)
    ids, nid = {}, [1000]

    def new():
        nid[0] += 1
        return nid[0]
    for n in names:
        ids[n] = new()
    attr = {n: new() for n in names}
    stack, layer = new(), new()
    cnode = {(n, p): new() for n in names for p in "TRS"}
    curves = {(n, p, a): new() for n in names for p in "TRS" for a in range(3)}
    times = [(k + 1) * DT for k in range(nk)]
    nm = len(names)

    def P(name, typ, label, flags, *vals):
        return E("P", [("S", name), ("S", typ), ("S", label), ("S", flags)] + list(vals))
    t0, t1 = times[0], times[-1]
    top = []
    top.append(E("FBXHeaderExtension", [], [E("FBXHeaderVersion", [("I", 1003)]), E("FBXVersion", [("I", 7400)]),
                                             E("EncryptionType", [("I", 0)]), E("Creator", [("S", "Pose Lab")])]))
    top.append(E("FileId", [("R", bytes.fromhex("28b32aebb624ccc2bfc8b02aa92bfcf1"))]))  # phải khớp mã footer của fbxbin (Blender); 00..0f làm Unity báo "File is corrupted" (SDR06 Reload 2026-11-06)
    top.append(E("CreationTime", [("S", "1970-01-01 10:00:00:000")]))
    top.append(E("Creator", [("S", "Pose Lab FBX")]))
    gs = [P("UpAxis", "int", "Integer", "", ("I", 1)), P("UpAxisSign", "int", "Integer", "", ("I", 1)),
          P("FrontAxis", "int", "Integer", "", ("I", 2)), P("FrontAxisSign", "int", "Integer", "", ("I", 1)),
          P("CoordAxis", "int", "Integer", "", ("I", 0)), P("CoordAxisSign", "int", "Integer", "", ("I", 1)),
          P("OriginalUpAxis", "int", "Integer", "", ("I", -1)), P("OriginalUpAxisSign", "int", "Integer", "", ("I", 1)),
          P("UnitScaleFactor", "double", "Number", "", ("D", 1.0)), P("OriginalUnitScaleFactor", "double", "Number", "", ("D", 1.0)),
          P("TimeMode", "enum", "", "", ("I", 6 if FPS == 30 else 14)), P("TimeSpanStart", "KTime", "Time", "", ("L", t0)),
          P("TimeSpanStop", "KTime", "Time", "", ("L", t1)), P("CustomFrameRate", "double", "Number", "", ("D", float(FPS)))]
    top.append(E("GlobalSettings", [], [E("Version", [("I", 1000)]), E("Properties70", [], gs)]))
    top.append(E("Documents", [], [E("Count", [("I", 1)]), E("Document", [("L", 1), ("S", take), ("S", take)],
                [E("Properties70", [], [P("SourceObject", "object", "", ""), P("ActiveAnimStackName", "KString", "", "", ("S", take))]),
                 E("RootNode", [("L", 0)])])]))
    top.append(E("References"))
    defs = [E("Version", [("I", 100)]), E("Count", [("I", 1 + nm + nm + 1 + 1 + nm * 3 + nm * 9)])]
    for nme, cnt in (("GlobalSettings", 1), ("NodeAttribute", nm), ("Model", nm), ("AnimationStack", 1), ("AnimationLayer", 1),
                     ("AnimationCurveNode", nm * 3), ("AnimationCurve", nm * 9)):
        defs.append(E("ObjectType", [("S", nme)], [E("Count", [("I", cnt)])]))
    top.append(E("Definitions", [], defs))
    obj = []
    for n in names:
        kind = "Null" if n == "Armature" else "LimbNode"
        kids = [E("TypeFlags", [("S", "Null" if n == "Armature" else "Skeleton")])]
        if n != "Armature":
            kids.append(E("Properties70", [], [P("Size", "double", "Number", "", ("D", 3.3))]))
        obj.append(E("NodeAttribute", [("L", attr[n]), ("S", n + "\x00\x01NodeAttribute"), ("S", kind)], kids))
    for n in names:
        kind = "Null" if n == "Armature" else "LimbNode"
        pr = [P("Lcl Translation", "Lcl Translation", "", "A+", *[("D", float(v)) for v in T[n][0]]),
              P("Lcl Rotation", "Lcl Rotation", "", "A+", *[("D", float(v)) for v in R[n][0]]),
              P("Lcl Scaling", "Lcl Scaling", "", "A+", ("D", 1.0), ("D", 1.0), ("D", 1.0)),
              P("DefaultAttributeIndex", "int", "Integer", "", ("I", 0)), P("InheritType", "enum", "", "", ("I", 1))]
        obj.append(E("Model", [("L", ids[n]), ("S", n + "\x00\x01Model"), ("S", kind)],
                     [E("Version", [("I", 232)]), E("Properties70", [], pr), E("MultiLayer", [("I", 0)]), E("MultiTake", [("I", 0)]),
                      E("Shading", [("C", "T")]), E("Culling", [("S", "CullingOff")])]))
    obj.append(E("AnimationStack", [("L", stack), ("S", take + "\x00\x01AnimStack"), ("S", "")],
                 [E("Properties70", [], [P("LocalStart", "KTime", "Time", "", ("L", t0)), P("LocalStop", "KTime", "Time", "", ("L", t1)),
                                         P("ReferenceStart", "KTime", "Time", "", ("L", t0)), P("ReferenceStop", "KTime", "Time", "", ("L", t1))])]))
    obj.append(E("AnimationLayer", [("L", layer), ("S", take + "\x00\x01AnimLayer"), ("S", "")]))
    for n in names:
        for p in "TRS":
            d = {"T": T[n][0], "R": R[n][0], "S": [1.0, 1.0, 1.0]}[p]
            obj.append(E("AnimationCurveNode", [("L", cnode[(n, p)]), ("S", p + "\x00\x01AnimCurveNode"), ("S", "")],
                         [E("Properties70", [], [P("d|" + ax, "Number", "", "A", ("D", float(d[i]))) for i, ax in enumerate("XYZ")])]))
    for n in names:
        for p in "TRS":
            for a in range(3):
                vals = [({"T": T, "R": R}[p][n][k][a] if p != "S" else 1.0) for k in range(nk)]
                obj.append(E("AnimationCurve", [("L", curves[(n, p, a)]), ("S", "\x00\x01AnimCurve"), ("S", "")],
                             [E("Default", [("D", 0.0)]), E("KeyVer", [("I", 4008)]), E("KeyTime", [("l", times)]),
                              E("KeyValueFloat", [("f", [float(v) for v in vals])]), E("KeyAttrFlags", [("i", [24836])]),
                              E("KeyAttrDataFloat", [("f", [0.0, 0.0, 0.0, 0.0])]), E("KeyAttrRefCount", [("i", [nk])])]))
    top.append(E("Objects", [], obj))
    con = []

    def C(kind, a, b, prop=None):
        pr = [("S", kind), ("L", a), ("L", b)] + ([("S", prop)] if prop else [])
        con.append(E("C", pr))
    for n in names:
        C("OO", attr[n], ids[n])
        C("OO", ids[n], ids[parent[n]] if parent[n] else 0)
    C("OO", layer, stack)
    for n in names:
        for p, pn in (("T", "Lcl Translation"), ("R", "Lcl Rotation"), ("S", "Lcl Scaling")):
            C("OO", cnode[(n, p)], layer)
            C("OP", cnode[(n, p)], ids[n], pn)
            for a, ax in enumerate("XYZ"):
                C("OP", curves[(n, p, a)], cnode[(n, p)], "d|" + ax)
    top.append(E("Connections", [], con))
    top.append(E("Takes", [], [E("Current", [("S", take)]), E("Take", [("S", take)],
                [E("FileName", [("S", take + ".tak")]), E("LocalTime", [("L", t0), ("L", t1)]), E("ReferenceTime", [("L", t0), ("L", t1)])])]))
    open(out, "wb").write(serialize(top))
    return nk, nm


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1], sys.argv[2], sys.argv[3]))
