# Full-body P0 solve on the grid-calibrated Ref_* cameras (docs/pipeline_v2.md step 4).
# Base pose = original P0 (Idle_Breath f1) + measured stance; ~47 channels on top of it (character axes, deg / cm):
#   root (t + r), spine, chest, neck, head, scapulae, right arm (elbow = hinge about local Z), feet (IK) + knee poles,
#   weapon rotation on the shoulder (+ tiny translation). The left arm rides the weapon (fixed separately later).
# Residuals: two-sided silhouette distance in 4 views + joint-limit excess (generic limits) + weak prior.
# Run in passes (state file keeps the solution):  ITERS = 3; exec(open(r".../fullbody_solve.py").read())
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")
import json
import math
import os

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

exec(open(ROOT + r"/tools/blender/anim_helpers.py").read())
STATE = globals().get("FB_STATE", ROOT + r"/work/idle/p0_fullbody.json")
FRAME = globals().get("FB_FRAME", 1)
LIMITS = json.load(open(ROOT + r"/work/idle/joint_limits.json"))
SILREF = np.load(ROOT + r"/work/idle/analysis/silref.npz")
PX_CM = 2.01

BODY = ["Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M", "Scapula_L", "Scapula_R", "Shoulder_R", "Elbow_R", "Wrist_R"]
CB = ["CTRL_weapon", "CTRL_hand_ik_L", "CTRL_elbow_pole_L", "H_Shoulder_L", "H_Elbow_L",
      "CTRL_foot_ik_L", "CTRL_foot_ik_R", "CTRL_knee_pole_L", "CTRL_knee_pole_R"]
CH = []        # (name, kind, target, axis, sigma)
for b in ("Root_M",):
    CH += [(f"{b}.t{a}", "move", b, a, 10.0) for a in "xyz"]
for b in ("Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M", "Scapula_L", "Scapula_R", "Shoulder_R", "Wrist_R"):
    CH += [(f"{b}.r{a}", "rot", b, a, 30.0) for a in "xyz"]
CH += [("Elbow_R.hinge", "hinge", "Elbow_R", 2, 30.0)]
for s in "LR":
    CH += [(f"foot_{s}.t{a}", "cmove", f"CTRL_foot_ik_{s}", a, 15.0) for a in "xy"]
    CH += [(f"foot_{s}.yaw", "crot", f"CTRL_foot_ik_{s}", "z", 30.0)]
    CH += [(f"knee_{s}.t{a}", "cmove", f"CTRL_knee_pole_{s}", a, 40.0) for a in "xy"]
CH += [(f"weapon.r{a}", "crot", "CTRL_weapon", a, 20.0) for a in "xyz"]
CH += [(f"weapon.t{a}", "cmove", "CTRL_weapon", a, 12.0) for a in "xyz"]   # where the prop rests is part of P0
NAMES = [c[0] for c in CH]
SIG = np.array([c[4] for c in CH])
AX = {"x": 0, "y": 1, "z": 2}


def setup_base():
    """Original P0 + measured stance, captured as the base of every evaluation."""
    global P0, CP0
    ARM.animation_data.action = bpy.data.actions["Idle_Breath"]; CTRL.animation_data.action = bpy.data.actions["Idle_Breath_CTRL"]
    bpy.context.scene.frame_set(1)
    ARM.animation_data.action = None; CTRL.animation_data.action = None
    for n in ("H_Shoulder_L", "H_Elbow_L"):
        CTRL.pose.bones[n].matrix_basis = Matrix()
    bpy.context.view_layer.update()
    st = globals().get("STANCE", dict(r=(0.0, 0.21), l=(-0.02, -0.36), l_yaw=35, r_yaw=-15))
    move_char(CTRL, "CTRL_foot_ik_R", (st["r"][0], st["r"][1], 0)); move_char(CTRL, "CTRL_knee_pole_R", (st["r"][0], st["r"][1], 0))
    move_char(CTRL, "CTRL_foot_ik_L", (st["l"][0], st["l"][1], 0)); move_char(CTRL, "CTRL_knee_pole_L", (st["l"][0], st["l"][1], 0))
    rotate_char(CTRL, "CTRL_foot_ik_R", (0, 0, st["r_yaw"])); rotate_char(CTRL, "CTRL_foot_ik_L", (0, 0, st["l_yaw"]))
    P0 = capture(ARM, BODY); CP0 = capture(CTRL, CB)


def rot_local(obj, name, axis_idx, deg):
    pb = obj.pose.bones[name]; mw = obj.matrix_world
    M = mw @ pb.matrix; ax = M.to_3x3().normalized().col[axis_idx].normalized(); h = M.to_translation()
    R = Matrix.Rotation(math.radians(deg), 4, ax)
    pb.matrix = mw.inverted() @ (Matrix.Translation(h) @ R @ Matrix.Translation(-h) @ M)
    bpy.context.view_layer.update()


def apply(p):
    restore(ARM, P0); restore(CTRL, CP0)
    v = dict(zip(NAMES, p))
    # feet + knee poles first (IK targets), then the body top-down, then the weapon
    for c in CH:
        n, kind, tgt, ax, _ = c
        if kind == "cmove" and not tgt.startswith("CTRL_weapon"):
            d = [0, 0, 0]; d[AX[ax]] = v[n] / 100; move_char(CTRL, tgt, tuple(d))
        elif kind == "crot" and tgt.startswith("CTRL_foot"):
            rotate_char(CTRL, tgt, (0, 0, v[n]))
    move_char(ARM, "Root_M", (v["Root_M.tx"] / 100, v["Root_M.ty"] / 100, v["Root_M.tz"] / 100))
    for b in ("Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M", "Scapula_L", "Scapula_R", "Shoulder_R"):
        rotate_char(ARM, b, (v[f"{b}.rx"], v[f"{b}.ry"], v[f"{b}.rz"]))
    rot_local(ARM, "Elbow_R", 2, v["Elbow_R.hinge"])
    rotate_char(ARM, "Wrist_R", (v["Wrist_R.rx"], v["Wrist_R.ry"], v["Wrist_R.rz"]))
    rotate_char(CTRL, "CTRL_weapon", (v["weapon.rx"], v["weapon.ry"], v["weapon.rz"]))
    move_char(CTRL, "CTRL_weapon", (v["weapon.tx"] / 100, v["weapon.ty"] / 100, v["weapon.tz"] / 100))


_MESHES = ["EN_M11_Boss_Gaygor", "EN_M11_Boss_Gaygor_VK"]
_EDGES = []
for _n in _MESHES:
    _me = bpy.data.objects[_n].data
    _e = np.empty(len(_me.edges) * 2, np.int32); _me.edges.foreach_get("vertices", _e); _EDGES.append(_e.reshape(-1, 2))
_CAMS = {}
for _v in ("front", "back", "left", "right"):
    _c = bpy.data.objects["Ref_" + _v]
    _CAMS[_v] = (np.array(_c.matrix_world.inverted()), 1920 / _c.data.ortho_scale, _c.data.shift_x * 1920, _c.data.shift_y * 1920)


def mesh_points():
    dg = bpy.context.evaluated_depsgraph_get(); out = []
    for n, E in zip(_MESHES, _EDGES):
        o = bpy.data.objects[n].evaluated_get(dg)
        a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
        a = np.vstack([a, (a[E[:, 0]] + a[E[:, 1]]) / 2]); M = np.array(o.matrix_world)
        out.append(a @ M[:3, :3].T + M[:3, 3])
    return np.vstack(out)


def sil_res(f):
    P = mesh_points(); sc_ = float(SILREF["scale"]); r = []
    for v, (Mi, s, shx, shy) in _CAMS.items():
        q = P @ Mi[:3, :3].T + Mi[:3, 3]
        uv = np.c_[960 + q[:, 0] * s - shx, 540 - q[:, 1] * s + shy]
        dt = SILREF[v + "_dt"][f - 1].astype(np.float32); box = SILREF[v + "_box"]
        iu = np.clip(((uv[:, 0] - box[0]) * sc_).astype(int), 0, dt.shape[1] - 1)
        iv = np.clip(((uv[:, 1] - box[1]) * sc_).astype(int), 0, dt.shape[0] - 1)
        r.append(np.minimum(dt[iv, iu], 30.0)[::3] * 0.5)
        img = np.full(dt.shape, 1, np.uint8); img[iv, iu] = 0
        # nearest model point for each reference contour sample (brute force on a subsample)
        ct = SILREF[v + "_ct"][f - 1]
        sub = uv[::3]
        d = np.sqrt(((ct[:, None, :] - sub[None, :, :]) ** 2).sum(2)).min(1)
        r.append(np.minimum(d, 30.0) * 2.0)
    return np.concatenate(r) / PX_CM


import fnmatch  # noqa: E402


def joint_angles(pb):
    D = ARM.data.bones; par = pb.parent
    q = (D[par.name].matrix_local.inverted() @ D[pb.name].matrix_local).to_quaternion().inverted() @ \
        (par.matrix.inverted() @ pb.matrix).to_quaternion()
    p = Vector((q.x, q.y, q.z)).project(Vector((1, 0, 0)))
    t = Quaternion((q.w, p.x, p.y, p.z)); t.normalize()
    tw = math.degrees(2 * math.atan2(t.x, t.w)); tw = (tw + 180) % 360 - 180
    e = (q @ t.inverted()).to_euler("YZX")
    return {"twist": tw, "bendY": math.degrees(e.y), "bendZ": math.degrees(e.z)}


LIM_BONES = ["Spine1_M", "Chest_M", "Neck_M", "Head_M", "Scapula_L", "Scapula_R", "Shoulder_R", "Elbow_R", "Wrist_R",
             "Hip_L", "Hip_R", "Knee_L", "Knee_R", "Ankle_L", "Ankle_R"]


def limit_res():
    r = []
    for n in LIM_BONES:
        lim = next((v for k, v in LIMITS["limits"].items() if fnmatch.fnmatch(n, k)), None)
        a = joint_angles(ARM.pose.bones[n])
        for k in ("twist", "bendY", "bendZ"):
            lo, hi = lim[k]
            r.append(max(0.0, lo - a[k], a[k] - hi) * globals().get("LIMIT_W", 0.5))
    return np.array(r)


def residual(p):
    apply(p)
    return np.concatenate([sil_res(FRAME), limit_res(), p / SIG])


def report(p):
    apply(p)
    s = sil_res(FRAME) * PX_CM; lim = limit_res() / globals().get("LIMIT_W", 0.5)
    return {"sil_px": round(float(np.mean(s)), 2), "limit_excess_deg": round(float(lim.sum()), 1)}


if "FB_NO_RUN" not in globals():
    setup_base()
    p = np.array([json.load(open(STATE))["p"].get(n, 0.0) for n in NAMES]) if os.path.exists(STATE) else np.zeros(len(NAMES))
    r = residual(p); lam = json.load(open(STATE)).get("lam", 3.0) if os.path.exists(STATE) else 3.0
    print("start", report(p), "cost", round(float(r @ r), 1))
    for _it in range(globals().get("ITERS", 3)):
        J = np.zeros((len(r), len(p)))
        for i in range(len(p)):
            d = np.zeros(len(p)); d[i] = 1.0
            J[:, i] = residual(p + d) - r
        g = J.T @ r; A = J.T @ J
        for _ in range(6):
            step = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-3), g)
            step = np.clip(step, -15, 15)
            rn = residual(p + step)
            if rn @ rn < r @ r:
                p, r, lam = p + step, rn, max(lam * 0.4, 1e-3)
                break
            lam *= 4
        print(f"iter {_it}: cost {float(r @ r):.1f} lam {lam:.3g}", report(p))
    json.dump({"p": dict(zip(NAMES, map(float, p))), "lam": lam}, open(STATE, "w"), indent=1)
    apply(p)
