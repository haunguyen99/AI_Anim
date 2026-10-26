# Build Idle_Front end to end (review rounds v9..v11): shared breath curve + overlap lags, spine/neck/head bend with the
# breath, right arm IK hand lift, loop seams. Re-run after any parameter change; measure with idle_front_measure().
#   exec(open(ROOT + r"/legacy/blender/idle_front_build.py").read()); idle_front_build(); print(idle_front_measure())
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")
import math

import bpy
from mathutils import Matrix, Quaternion, Vector

IDLE_FRONT = dict(
    ease="sine",                       # v10: smootherstep stalled the hips ~8 F before the peak
    lags={"Root_M": 0, "Spine1_M": 2, "Chest_M": 4, "Scapula_L": 6, "Scapula_R": 6, "Neck_M": 6, "Head_M": 12,
          "Shoulder_R": 7, "Elbow_R": 9, "Wrist_R": 11, "CTRL_weapon": 9},       # v9 overlap: driver -> driven
    # (deg at trough, deg at peak) about world X: + = extension (chest up/back), - = flexion (bend forward)
    bend={"Spine1_M": (2, -1.0, 2.0), "Chest_M": (4, -2.0, 3.5), "Neck_M": (6, -0.5, 1.0), "Head_M": (3, 3.0, -4.0)},
    hand=dict(lift_cm=4, fwd_cm=1.5, lag=5, base_cm=3, base_fwd_cm=1, smooth=0),
    # v11: the grip is near one end, so the heavy spiked end drags: extra rotation about the shoulder contact,
    # angle = K * (s(t - D) - s(t)), s = the mace's breath; + lifts the heavy end (follow-through after the peak)
    mace_drag=None,
    # v11 (final): the heavy end replays its own height path D frames late (and AMP x bigger), by rotating the mace
    # about the shoulder fulcrum - its height is driven by the scapula/chest, so key lags alone did not move its peak
    mace_delay=dict(D=12, amp=1.3),
    # v12: secondary motion on the loincloth flaps - damped pendulum driven by the hips' vertical acceleration and the
    # spine bend; (deg amplitude, period F, damping ratio, sign: + swings the tip forward)
    # v13: "more, like flapping in the wind" -> bigger swing + wind gusts (loop-safe sines) + sideways sway
    flaps={"DressFront_M": (12.0, 20, 0.2, +1, dict(gust=7.0, side=6.0, lean=4.0, seed=3)),
           "DressBack_M": (10.0, 24, 0.2, -1, dict(gust=6.0, side=5.0, lean=-3.0, seed=7))},
)


def cloth_flaps(flaps, step=2):
    """Simulate each flap as a damped pendulum, cyclic over the loop (run 5 loops, keep the last), driven by
    -hip vertical acceleration + spine flex velocity; key its swing about the world X axis at the bone head."""
    A = bpy.data.objects["Armature"]; sc = bpy.context.scene; mw = A.matrix_world; P = A.pose.bones
    act = A.animation_data.action; N = sc.frame_end - sc.frame_start
    z, pit = [], []
    for f in range(1, N + 1):
        sc.frame_set(f); z.append((mw @ P["Root_M"].head).z * 100)
        v = (mw @ P["Chest_M"].matrix).to_3x3().normalized().col[0]; pit.append(math.degrees(math.asin(max(-1, min(1, v.z)))))
    acc = [z[(i + 1) % N] - 2 * z[i] + z[i - 1] for i in range(N)]
    dpit = [(pit[(i + 1) % N] - pit[i - 1]) / 2 for i in range(N)]
    drive = [-a * 40.0 + d * 1.0 for a, d in zip(acc, dpit)]
    for bone, spec in flaps.items():
        amp, period, zeta, sign = spec[:4]; wind = spec[4] if len(spec) > 4 else None
        if bone not in P:
            continue
        w = 2 * math.pi / period; th = om = 0.0; sub = 8; out = [0.0] * N
        for loop in range(5):
            for i in range(N):
                for _ in range(sub):
                    acc_ = drive[i] - 2 * zeta * w * om - w * w * th
                    om += acc_ / sub; th += om / sub
                if loop == 4:
                    out[i] = th
        m = sum(out) / N; pk = max(abs(x - m) for x in out) or 1.0
        ang = [sign * amp * (x - m) / pk for x in out]
        side = [0.0] * N
        if wind:
            # wind (review v13: "flap like in the wind"): gusts = a few sines whose periods divide the loop (N/2, N/3,
            # N/5, N/7 -> the seam stays clean), random phases per flap; plus a sideways sway and a steady lean
            import random
            rnd = random.Random(wind.get("seed", 1))
            def waves(total):
                ks = (2, 3, 5, 7); ws = (1.0, 0.7, 0.45, 0.3); ph = [rnd.uniform(0, 2 * math.pi) for _ in ks]
                s = [sum(wk * math.sin(2 * math.pi * k * i / N + p) for k, wk, p in zip(ks, ws, ph)) for i in range(N)]
                pk2 = max(abs(x) for x in s) or 1.0
                return [total * x / pk2 for x in s]
            g = waves(wind.get("gust", 0.0))
            ang = [a + sign * (gi_ + wind.get("lean", 0.0)) for a, gi_ in zip(ang, g)]
            side = waves(wind.get("side", 0.0))
        pb = P[bone]; pb.rotation_mode = "QUATERNION"
        for fc in [fc for fc in act.fcurves if fc.data_path.startswith(f'pose.bones["{bone}"]')]:
            act.fcurves.remove(fc)
        # pivot = where the cloth hangs from the belt: the top of the vertices this bone deforms (the bone's own head
        # sits mid-flap, so swinging about it moved the upper half against the lower half)
        body = next(o for o in bpy.data.objects if o.type == "MESH" and bone in o.vertex_groups)
        gi = body.vertex_groups[bone].index; sc.frame_set(1)
        top = max((body.matrix_world @ v.co).z for v in body.data.vertices
                  for ge in v.groups if ge.group == gi and ge.weight > 0.3)
        frames = sorted(set(range(1, N + 1, step)) | {N + 1})
        for f in frames:
            sc.frame_set(f); i = (f - 1) % N
            pb.matrix_basis = Matrix.Identity(4); bpy.context.view_layer.update()
            M = mw @ pb.matrix; hd = M.to_translation()
            piv = Vector((hd.x, hd.y, top + ((mw @ P["Root_M"].head).z - z[0] / 100)))   # belt rides with the hips
            R = Matrix.Rotation(math.radians(side[i]), 4, "Y") @ Matrix.Rotation(math.radians(-ang[i]), 4, "X")
            pb.matrix = mw.inverted() @ (Matrix.Translation(piv) @ R @ Matrix.Translation(-piv) @ M)
            bpy.context.view_layer.update()
            pb.keyframe_insert("rotation_quaternion", frame=f); pb.keyframe_insert("location", frame=f)
        print(bone, "swing %.1f deg, period %d F, extremes f%d / f%d" % (
            max(ang) - min(ang), period, max(range(N), key=lambda i: ang[i]) + 1, min(range(N), key=lambda i: ang[i]) + 1))


def mace_delay(D, amp=1.0):
    A = bpy.data.objects["Armature"]; C = bpy.data.objects["CTRL"]; sc = bpy.context.scene
    mw = A.matrix_world; cw = C.matrix_world; P = A.pose.bones; wb = C.pose.bones["CTRL_weapon"]
    act = C.animation_data.action; N = sc.frame_end - sc.frame_start
    h0 = {}
    for f in range(1, N + 1):
        sc.frame_set(f); h0[f] = (mw @ P["Weapon"].tail).z
    mean = sum(h0.values()) / N
    ks = sorted({int(round(k.co[0])) for fc in act.fcurves if fc.data_path.startswith('pose.bones["CTRL_weapon"]')
                 for k in fc.keyframe_points})
    new = {}
    for f in ks:
        sc.frame_set(f)
        want = mean + (h0[(f - 1 - D) % N + 1] - mean) * amp
        h, t = mw @ P["Weapon"].head, mw @ P["Weapon"].tail; d = (t - h).normalized()
        s = mw @ P["Shoulder_L"].head; pivot = h + d * (s - h).dot(d)
        axis = d.cross(Vector((0, 0, 1))).normalized()
        M0 = cw @ wb.matrix
        for _ in range(3):                                   # solve the tilt so the heavy end sits at `want`
            sc.frame_set(f); cur = (mw @ P["Weapon"].tail).z
            M = cw @ wb.matrix; R1 = Matrix.Rotation(math.radians(1.0), 4, axis)
            wb.matrix = cw.inverted() @ (Matrix.Translation(pivot) @ R1 @ Matrix.Translation(-pivot) @ M)
            bpy.context.view_layer.update(); dz = (mw @ P["Weapon"].tail).z - cur
            wb.matrix = cw.inverted() @ M; bpy.context.view_layer.update()
            if abs(dz) < 1e-6:
                break
            ang = (want - cur) / dz
            wb.matrix = cw.inverted() @ (Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(ang), 4, axis)
                                         @ Matrix.Translation(-pivot) @ M)
            bpy.context.view_layer.update()
        new[f] = (wb.location.copy(), wb.rotation_quaternion.copy())
        wb.matrix = cw.inverted() @ M0; bpy.context.view_layer.update()
    for fc in act.fcurves:
        if fc.data_path.startswith('pose.bones["CTRL_weapon"]'):
            src = 0 if fc.data_path.endswith("location") else 1
            for k in fc.keyframe_points:
                k.co[1] = new[int(round(k.co[0]))][src][fc.array_index]
            fc.update()


def mace_drag(K, D, lag):
    """Rotate CTRL_weapon keys about the handle point nearest the left shoulder (the fulcrum), in the vertical plane
    of the handle, so the heavy end lags the shoulder's rise and fall."""
    g = globals(); br = g["breath"]
    A = bpy.data.objects["Armature"]; C = bpy.data.objects["CTRL"]; sc = bpy.context.scene
    mw = A.matrix_world; cw = C.matrix_world; P = A.pose.bones; wb = C.pose.bones["CTRL_weapon"]
    act = C.animation_data.action
    ks = sorted({int(round(k.co[0])) for fc in act.fcurves if fc.data_path.startswith('pose.bones["CTRL_weapon"]')
                 for k in fc.keyframe_points})
    new = {}
    for f in ks:
        sc.frame_set(f)
        h, t = mw @ P["Weapon"].head, mw @ P["Weapon"].tail; d = (t - h).normalized()
        s = mw @ P["Shoulder_L"].head; pivot = h + d * (s - h).dot(d)             # fulcrum on the handle
        axis = d.cross(Vector((0, 0, 1))).normalized()                            # tilts the handle up/down
        ang = K * (br(f - 1 - lag - D) - br(f - 1 - lag))
        R = Matrix.Rotation(math.radians(ang), 4, axis)
        if (R.to_3x3() @ d).z < d.z and ang > 0:                                  # make + lift the heavy (tail) end
            R = Matrix.Rotation(math.radians(-ang), 4, axis)
        elif (R.to_3x3() @ d).z > d.z and ang < 0:
            R = Matrix.Rotation(math.radians(-ang), 4, axis)
        M = cw @ wb.matrix
        wb.matrix = cw.inverted() @ (Matrix.Translation(pivot) @ R @ Matrix.Translation(-pivot) @ M)
        bpy.context.view_layer.update()
        new[f] = (wb.location.copy(), wb.rotation_quaternion.copy())
    for fc in act.fcurves:
        if fc.data_path.startswith('pose.bones["CTRL_weapon"]'):
            src = 0 if fc.data_path.endswith("location") else 1
            for k in fc.keyframe_points:
                k.co[1] = new[int(round(k.co[0]))][src][fc.array_index]
            fc.update()


def idle_front_build(**over):
    cfg = {**IDLE_FRONT, **over}
    g = globals()
    g.pop("BREATH_AMP", None)
    g["BREATH_EASE"] = cfg["ease"]; g["BREATH_LAGS"] = cfg["lags"]
    exec(open(ROOT + r"/work/blender/key_idle_breath_curve.py").read(), g)
    A = bpy.data.objects["Armature"]; C = bpy.data.objects["CTRL"]; sc = bpy.context.scene
    mw = A.matrix_world; P = A.pose.bones; act = A.animation_data.action
    br = g["breath"]

    def rot_keys(b, lag, lo, hi):
        pb = P[b]; new = {}
        ks = sorted({int(round(k.co[0])) for fc in act.fcurves if fc.data_path.startswith(f'pose.bones["{b}"]')
                     for k in fc.keyframe_points})
        for f in ks:
            sc.frame_set(f); M = mw @ pb.matrix; h = M.to_translation()
            ang = lo + (hi - lo) * br(f - 1 - lag)
            pb.matrix = mw.inverted() @ (Matrix.Translation(h) @ Matrix.Rotation(math.radians(ang), 4, "X")
                                         @ Matrix.Translation(-h) @ M)
            bpy.context.view_layer.update(); new[f] = pb.rotation_quaternion.copy()
        for fc in act.fcurves:
            if fc.data_path == f'pose.bones["{b}"].rotation_quaternion':
                for k in fc.keyframe_points:
                    k.co[1] = new[int(round(k.co[0]))][fc.array_index]
                fc.update()

    for b, (lag, lo, hi) in cfg["bend"].items():
        rot_keys(b, lag, lo, hi)
    if cfg.get("mace_drag"):
        mace_drag(**cfg["mace_drag"])
    if cfg.get("mace_delay"):
        mace_delay(**cfg["mace_delay"])
    if cfg.get("flaps"):
        cloth_flaps(cfg["flaps"])
    exec(open(ROOT + r"/legacy/blender/arm_ik_R.py").read(), g)
    g["ik_R_breath"](**cfg["hand"])
    hb = C.pose.bones["H_Elbow_R"]
    hb.rotation_quaternion = Quaternion(Vector((1, 0, 0)), math.radians(-0.5)) @ Quaternion(Vector((0, 1, 0)), math.radians(-3.0))
    for f in (1, 60):
        hb.keyframe_insert("rotation_quaternion", frame=f)
    exec(open(ROOT + r"/legacy/blender/direct.py").read(), g)
    g["match_seam"](A); g["match_seam"](C)


def idle_front_measure():
    """Per part: world pitch range + extreme frame (spine chain), z range (shoulders), hip speed profile, head yaw."""
    A = bpy.data.objects["Armature"]; sc = bpy.context.scene; mw = A.matrix_world; P = A.pose.bones; out = {}
    for b in ("Spine1_M", "Chest_M", "Neck_M", "Head_M"):
        r = []
        for f in range(1, 60):
            sc.frame_set(f); v = (mw @ P[b].matrix).to_3x3().normalized().col[0]
            r.append(math.degrees(math.asin(max(-1, min(1, v.z)))))
        out[b] = "pitch %.1f deg, extension at f%d" % (max(r) - min(r), min(range(59), key=lambda i: r[i]) + 1)
    for b in ("Root_M", "Shoulder_L", "Shoulder_R", "Wrist_R", "Wrist_L"):
        z = []
        for f in range(1, 60):
            sc.frame_set(f); z.append((mw @ P[b].head).z * 100)
        v = [z[(i + 1) % 59] - z[i] for i in range(59)]
        out[b] = "z %.1f cm, peak f%d, up %.2f down %.2f cm/F" % (max(z) - min(z), max(range(59), key=lambda i: z[i]) + 1,
                                                                 max(v), -min(v))
    z = []
    for f in range(1, 60):
        sc.frame_set(f); z.append((mw @ P["Weapon"].tail).z * 100)
    v = [z[(i + 1) % 59] - z[i] for i in range(59)]
    out["mace_heavy_end"] = "z %.1f cm, peak f%d, trough f%d, up %.2f down %.2f cm/F" % (
        max(z) - min(z), max(range(59), key=lambda i: z[i]) + 1, min(range(59), key=lambda i: z[i]) + 1, max(v), -min(v))
    ys = []
    for f in range(1, 60):
        sc.frame_set(f); v = (mw @ P["Head_M"].matrix).to_3x3().normalized().col[2]
        ys.append(math.degrees(math.atan2(v.x, -v.y)))
    out["head_yaw"] = "%.1f..%.1f" % (min(ys), max(ys))
    return out
