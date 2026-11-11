"""Rig FBX của team (đủ xương: nỏ, tóc, root) + texture + các frame pose → model Pose Lab (glTF JSON, buffer nhúng), không Blender.
Khác rig Studio (`rig.useFbx` chỉ giữ 25 xương thân). Cách dựng như make_model.py của Gaygor: node "Armature" scale 0.01, xương
tính bằng cm, trục FBX Y lên giữ nguyên (không xoay root). Mesh tách đỉnh theo góc tam giác để mang UV; skin 4 xương mạnh nhất.
Animation: frame trang f (1-based) = thời điểm glTF f/30; mỗi xương có kênh translation + rotation.

    python -I poselab_model.py <ra.json> [--rig RIG.fbx] [--pose p0/p0_v1.json ...] [--tex texture.png]
Mặc định: rig gốc của team, 1 frame = P0 v1, texture chars/mc_map3/texture.png."""
import os, sys, json, base64, argparse
import numpy as np
from io import BytesIO
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")
import rigpose as RP

ROOT = os.path.abspath(os.path.join(HERE, ".."))
TEX_PNG = os.path.join(ROOT, "work", "rig_lab", "chars", "mc_map3", "texture.png")
FPS = 30


def quat(R):
    t = R[0, 0] + R[1, 1] + R[2, 2]
    if t > 0:
        s = np.sqrt(t + 1) * 2; q = [(R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s, s / 4]
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = np.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2]) * 2; q = [s / 4, (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s, (R[2, 1] - R[1, 2]) / s]
    elif R[1, 1] > R[2, 2]:
        s = np.sqrt(1 + R[1, 1] - R[0, 0] - R[2, 2]) * 2; q = [(R[0, 1] + R[1, 0]) / s, s / 4, (R[1, 2] + R[2, 1]) / s, (R[0, 2] - R[2, 0]) / s]
    else:
        s = np.sqrt(1 + R[2, 2] - R[0, 0] - R[1, 1]) * 2; q = [(R[0, 2] + R[2, 0]) / s, (R[1, 2] + R[2, 1]) / s, s / 4, (R[1, 0] - R[0, 1]) / s]
    q = np.array(q); return q / np.linalg.norm(q)


def trs(M):
    S = np.linalg.norm(M[:3, :3], axis=0); return M[:3, 3].copy(), quat(M[:3, :3] / S), S


def build(rig, frames, tex_png, out, anim_name="P0"):
    buf = bytearray(); views, acc = [], []
    def add(arr, typ, comp=5126, target=None, mm=False):
        arr = np.ascontiguousarray(arr, {5126: np.float32, 5123: np.uint16, 5125: np.uint32}[comp])
        off = (len(buf) + 3) // 4 * 4; buf.extend(b"\0" * (off - len(buf))); buf.extend(arr.tobytes())
        v = {"buffer": 0, "byteOffset": off, "byteLength": arr.nbytes}
        if target: v["target"] = target
        views.append(v)
        n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[typ]
        a = {"bufferView": len(views) - 1, "componentType": comp, "count": int(arr.size // n), "type": typ}
        if mm:
            r = arr.reshape(-1, n); a["min"] = r.min(0).astype(float).tolist(); a["max"] = r.max(0).astype(float).tolist()
        acc.append(a); return len(acc) - 1

    bones = rig.order; jidx = {b: i for i, b in enumerate(bones)}
    nodes = []
    for b in bones:
        T, Q, S = trs(frames[0][b] if frames else rig.rest_pose[b])
        nd = {"name": b, "translation": T.tolist(), "rotation": Q.tolist()}
        if np.abs(S - 1).max() > 1e-4: nd["scale"] = S.tolist()
        nodes.append(nd)
    for b in bones:
        if b in rig.parent: nodes[jidx[rig.parent[b]]].setdefault("children", []).append(jidx[b])
    roots = [jidx[b] for b in bones if b not in rig.parent]
    arm = len(nodes); nodes.append({"name": "Armature", "scale": [0.01, 0.01, 0.01], "children": roots})

    # mesh: mỗi góc tam giác một đỉnh (mang UV), skin 4 xương mạnh nhất
    meshes, mesh_nodes = [], []
    for m in rig.meshes:
        V = np.array(m["verts"], float).reshape(-1, 3); T = np.array(m["tris"], int).reshape(-1, 3)
        n = len(V); per = [[] for _ in range(n)]
        for b, (ix, wt) in m["weights"].items():
            if b not in jidx: continue
            for i, w in zip(ix, wt):
                if w > 1e-6: per[i].append((w, jidx[b]))
        J = np.zeros((n, 4), np.uint16); Wt = np.zeros((n, 4), np.float32)
        for i, l in enumerate(per):
            l = sorted(l, reverse=True)[:4]; s = sum(w for w, _ in l) or 1
            if not l: J[i, 0] = jidx[bones[0]]; Wt[i, 0] = 1; continue
            for k, (w, j) in enumerate(l): J[i, k] = j; Wt[i, k] = w / s
        c = T.reshape(-1)
        P = V[c] * 0.01; UV = np.array(m["uvc"], float).reshape(-1, 2).copy(); UV[:, 1] = 1 - UV[:, 1]; UV = np.clip(UV, 1 / 1024, 1 - 1 / 1024)   # glTF: v từ trên xuống; UV đúng mép (bảng màu) kéo vào trong nửa texel, khỏi lẫn hàng đối diện
        fn = np.cross(P[1::3] - P[0::3], P[2::3] - P[0::3]); fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12
        N = np.repeat(fn, 3, axis=0)
        idx = np.arange(len(c), dtype=np.uint32 if len(c) > 65535 else np.uint16)
        prim = {"attributes": {"POSITION": add(P, "VEC3", target=34962, mm=True), "NORMAL": add(N, "VEC3", target=34962),
                               "TEXCOORD_0": add(UV, "VEC2", target=34962), "JOINTS_0": add(J[c], "VEC4", 5123, 34962),
                               "WEIGHTS_0": add(Wt[c], "VEC4", target=34962)},
                "indices": add(idx, "SCALAR", 5125 if len(c) > 65535 else 5123, 34963), "material": 0, "mode": 4}
        meshes.append({"name": m["name"], "primitives": [prim]})
        mesh_nodes.append(len(nodes)); nodes.append({"name": m["name"], "mesh": len(meshes) - 1, "skin": 0})
    # Đỉnh mesh tính bằng MÉT, mesh ở gốc scene: Pose engine gỡ mesh khỏi Armature và bản ma (ghost, không skin) vẽ thẳng đỉnh.
    # Bản đầu ghi đỉnh cm → ghost to gấp 100 lần (user 2026-10-28, ảnh nhân vật khổng lồ mờ). Xương vẫn cm trong Armature 0.01.
    A = np.diag([0.01, 0.01, 0.01, 1.0])   # IBM = nghịch đảo world của xương KỂ CẢ scale Armature → skin ra mét
    ibm = np.stack([np.linalg.inv(A @ rig.bind[b]).T.reshape(-1) for b in bones]).astype(np.float32)   # glTF MAT4 theo cột
    skin = {"name": "Armature", "joints": list(range(len(bones))), "inverseBindMatrices": add(ibm, "MAT4"), "skeleton": roots[0]}

    # animation: mỗi frame pose
    ch, sm = [], []
    if frames:
        tin = add(np.arange(1, len(frames) + 1, dtype=float) / FPS, "SCALAR", mm=True)
        for b in bones:
            Ts, Qs = [], []
            for P in frames:
                t, q, _ = trs(P[b])
                if Qs and np.dot(q, Qs[-1]) < 0: q = -q
                Ts.append(t); Qs.append(q)
            for path, arr, typ in (("translation", Ts, "VEC3"), ("rotation", Qs, "VEC4")):
                sm.append({"input": tin, "interpolation": "LINEAR", "output": add(np.array(arr), typ)})
                ch.append({"sampler": len(sm) - 1, "target": {"node": jidx[b], "path": path}})

    png = BytesIO(); Image.open(tex_png).convert("RGB").save(png, "PNG")
    g = {"asset": {"version": "2.0", "generator": "sdr03/poselab_model.py (FBX team, không Blender)"}, "scene": 0,
         "scenes": [{"name": "Scene", "nodes": [arm] + mesh_nodes}], "nodes": nodes, "meshes": meshes, "skins": [skin],
         "materials": [{"name": "T_Color", "doubleSided": True, "pbrMetallicRoughness": {"baseColorTexture": {"index": 0},
                        "metallicFactor": 0, "roughnessFactor": 0.9}}],
         "textures": [{"sampler": 0, "source": 0}], "samplers": [{"magFilter": 9728, "minFilter": 9728, "wrapS": 33071, "wrapT": 33071}],
         "images": [{"mimeType": "image/png", "uri": "data:image/png;base64," + base64.b64encode(png.getvalue()).decode()}],
         "accessors": acc, "bufferViews": views,
         "buffers": [{"byteLength": len(buf), "uri": "data:application/octet-stream;base64," + base64.b64encode(bytes(buf)).decode()}]}
    if ch: g["animations"] = [{"name": anim_name, "channels": ch, "samplers": sm}]
    json.dump(g, open(out, "w"), separators=(",", ":"))
    print("xương", len(bones), "mesh", len(meshes), "frame", len(frames), "→", out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--rig", default=RP.RIG_FBX)
    ap.add_argument("--pose", nargs="*", default=[os.path.join(ROOT, "work", "shoot_die_repeat", "sdr03", "p0", "p0_v1.json")]); ap.add_argument("--tex", default=TEX_PNG)
    a = ap.parse_args()
    rig = RP.Rig(a.rig)
    frames = [{k: np.array(v) for k, v in json.load(open(p)).items()} for p in a.pose]
    build(rig, frames, a.tex, a.out)
