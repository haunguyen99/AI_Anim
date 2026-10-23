"""Write per-frame poses straight into a GLB's animation (no Blender).

Takes a GLB exported once from the rig (mesh, skin, textures) and replaces its
animation with one LINEAR sampler per joint per channel, one key per frame,
computed from local pose matrices (fit_smooth.npy, Blender bone convention).

Blender bone -> glTF joint (armature-node space): N_b = C @ M_b @ K_b @ C^-1, where C is the
Z-up -> Y-up axis change, M_b the posed armature-space bone matrix and K_b the exporter's
bone-axis correction (constant; recovered from the rest pose).

python tools/fit/glb_bake.py work/idle --basis fit_smooth.npy --glb anim.glb --out anim.glb [--check]
"""
import argparse
import json
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from silmodel import SilModel  # noqa: E402
from smooth import mat_to_quat, quat_to_mat  # noqa: E402


def read_glb(path):
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    off = 20 + n
    bn = struct.unpack("<I", b[off:off + 4])[0]
    return j, bytearray(b[off + 8:off + 8 + bn])


def write_glb(path, j, binary):
    while len(binary) % 4:
        binary += b"\0"
    js = json.dumps(j, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    total = 12 + 8 + len(js) + 8 + len(binary)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(binary), 0x004E4942) + binary)


def trs_matrix(nd):
    M = np.eye(4)
    if "matrix" in nd:
        return np.array(nd["matrix"]).reshape(4, 4).T
    t = nd.get("translation", [0, 0, 0])
    x, y, z, w = nd.get("rotation", [0, 0, 0, 1])
    s = nd.get("scale", [1, 1, 1])
    M[:3, :3] = quat_to_mat(np.array([w, x, y, z])) * np.array(s)
    M[:3, 3] = t
    return M


def accessor(j, data, idx):
    a = j["accessors"][idx]
    bv = j["bufferViews"][a["bufferView"]]
    comp = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[a["type"]]
    start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    return np.frombuffer(bytes(data[start:start + a["count"] * comp * 4]), np.float32).reshape(a["count"], comp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--basis", default="fit_smooth.npy")
    ap.add_argument("--glb", default="anim.glb")
    ap.add_argument("--out", default="anim.glb")
    ap.add_argument("--fps", type=float, default=None)
    ap.add_argument("--check", action="store_true", help="compare with the GLB's existing animation instead of writing")
    a = ap.parse_args()

    m = SilModel(a.work)
    B = np.load(os.path.join(a.work, a.basis)) if a.basis != "basis0" else m.basis0
    j, data = read_glb(os.path.join(a.work, a.glb))
    nodes = j["nodes"]
    joints = j["skins"][0]["joints"]
    name_to_node = {nodes[i]["name"]: i for i in joints}
    parent_of = {c: i for i, nd in enumerate(nodes) for c in nd.get("children", [])}
    fps = a.fps or json.load(open(os.path.join(a.work, "keys.json"))).get("fps", 30)

    # rest: joint node matrices relative to the armature node, vs Blender rest bone matrices
    def chain(i, stop):
        M = np.eye(4)
        while i is not None and i not in stop:
            M = trs_matrix(nodes[i]) @ M
            i = parent_of.get(i)
        return M
    arm_node = parent_of[name_to_node[m.bones[0]]]
    while arm_node in joints:
        arm_node = parent_of[arm_node]
    Cm = np.eye(4)
    Cm[:3, :3] = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]   # Blender (x, y, z) -> glTF (x, z, -y)
    Ci = np.linalg.inv(Cm)
    corr = {}
    for b, name in enumerate(m.bones):
        N = chain(name_to_node[name], {arm_node})
        corr[b] = np.linalg.inv(m.rest[b]) @ Ci @ N @ Cm
    c0 = corr[0]
    spread = max(np.abs(c - c0).max() for c in corr.values())
    print(f"rest correction constant across bones: max diff {spread:.2e}")

    # local TRS per joint per frame
    nF = B.shape[0]
    T = np.zeros((len(m.bones), nF, 3), np.float32)
    Q = np.zeros((len(m.bones), nF, 4), np.float32)
    for f in range(nF):
        M = m.fk(B[f])
        Nw = {b: Cm @ M[b] @ corr[b] @ Ci for b in range(len(m.bones))}
        for b, name in enumerate(m.bones):
            pn = parent_of.get(name_to_node[name])
            pb = m.bones.index(nodes[pn]["name"]) if pn in joints else None
            L = Nw[b] if pb is None else np.linalg.inv(Nw[pb]) @ Nw[b]
            T[b, f] = L[:3, 3]
            R = L[:3, :3] / np.linalg.norm(L[:3, :3], axis=0)
            w, x, y, z = mat_to_quat(R)
            q = np.array([x, y, z, w])
            if f and np.dot(q, Q[b, f - 1]) < 0:
                q = -q
            Q[b, f] = q

    if a.check:
        anim = j["animations"][0]
        errs_t, errs_r = [], []
        for ch in anim["channels"]:
            node = ch["target"]["node"]
            if node not in joints or ch["target"]["path"] not in ("translation", "rotation"):
                continue
            b = m.bones.index(nodes[node]["name"])
            s = anim["samplers"][ch["sampler"]]
            times = accessor(j, data, s["input"])[:, 0]
            vals = accessor(j, data, s["output"])
            for t, v in zip(times, vals):
                f = int(round(t * fps)) - 1 if len(times) == nF else int(round(t * fps)) - 1
                if not 0 <= f < nF:
                    continue
                if ch["target"]["path"] == "translation":
                    errs_t.append(np.abs(T[b, f] - v).max())
                else:
                    errs_r.append(min(np.abs(Q[b, f] - v).max(), np.abs(Q[b, f] + v).max()))
        print(f"vs existing GLB animation: max translation err {max(errs_t):.4f}, max quat err {max(errs_r):.4f} "
              f"({len(errs_t) + len(errs_r)} samples)")
        return

    # append the new animation data to the binary chunk
    def add(arr, typ):
        nonlocal data
        while len(data) % 4:
            data += b"\0"
        off = len(data)
        data += arr.astype(np.float32).tobytes()
        j["bufferViews"].append({"buffer": 0, "byteOffset": off, "byteLength": arr.nbytes})
        acc = {"bufferView": len(j["bufferViews"]) - 1, "componentType": 5126, "count": int(arr.shape[0]),
               "type": {1: "SCALAR", 3: "VEC3", 4: "VEC4"}[arr.shape[1] if arr.ndim > 1 else 1]}
        if acc["type"] == "SCALAR":
            acc["min"], acc["max"] = [float(arr.min())], [float(arr.max())]
        j["accessors"].append(acc)
        return len(j["accessors"]) - 1

    times = add(((np.arange(nF) + 1) / fps).reshape(-1, 1).astype(np.float32), 1)
    samplers, channels = [], []
    for b, name in enumerate(m.bones):
        node = name_to_node[name]
        for path, arr in (("translation", T[b]), ("rotation", Q[b])):
            samplers.append({"input": times, "output": add(arr, None), "interpolation": "LINEAR"})
            channels.append({"sampler": len(samplers) - 1, "target": {"node": node, "path": path}})
    j["animations"] = [{"name": "fit", "samplers": samplers, "channels": channels}]
    j["buffers"][0]["byteLength"] = len(data)
    write_glb(os.path.join(a.work, a.out), j, data)
    print(f"wrote {a.out}: {nF} frames x {len(m.bones)} joints")


if __name__ == "__main__":
    main()
