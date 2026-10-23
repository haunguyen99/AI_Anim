# Anatomical arm limits INSIDE the solver (user 2026-10-22: "tạo giới hạn cho các joint để tránh các lỗi bẻ pose quá
# đà sai Anatomy. AI cũng tránh phải thử quá nhiều lần").
# The angles are measured from world joint positions + the palm, not from bone-local Eulers, so they mean the same on
# every rig (Advanced Skeleton bone names) and have an anatomical zero:
#   elbow_flex   angle upper arm -> forearm (0 = straight)
#   humeral_rot  upper-arm rotation: forearm swung off the "neutral" direction (forearm forward when the arm hangs,
#                carried to the current upper-arm direction by the shortest swing); + = internal (forearm toward belly)
#   pronation    palm turned about the forearm from the neutral "thumb up" palm (palm facing the hinge side); + = palm down
#   wrist_flex   hand bent toward the palm (+) / back of the hand (-)
#   wrist_dev    hand bent sideways about the palm normal (+ = toward the little finger)
#   elevation    upper arm raised from hanging (0) to overhead (180)
# Use (namespace that already has wpos, palm_of, hand_on from p0_shoot/blocking):
#   ARM_LIMITS = r".../work/sdr06/joint_limits.json"; exec(open(r".../tools/blender/arm_limits.py").read(), NS)
#   NS["arm_angles"]("L"), NS["arm_violations"]("L"), NS["hand_on_limited"](side, grip, hw, pw, pole_w)
import json

import bpy
import math

from mathutils import Matrix, Quaternion, Vector

ARM_LIM = json.load(open(globals().get("ARM_LIMITS", r"E:/AI Animation/work/sdr06/joint_limits.json"), encoding="utf-8"))


def _chest():
    """Chest frame columns (right, forward, up) in world: from the shoulders and the chest bone."""
    r = (wpos("Shoulder_R") - wpos("Shoulder_L")).normalized()
    up = (wpos("Neck_M") - wpos("Chest_M")).normalized()
    fw = up.cross(r).normalized()       # character forward
    return r, fw, up


def arm_angles(side):
    S, E, W = wpos(f"Shoulder_{side}"), wpos(f"Elbow_{side}"), wpos(f"Wrist_{side}")
    H = wpos(f"MiddleFinger1_{side}")
    r, fw, up = _chest()
    out_dir = -r if side == "L" else r                 # away from the body on this side
    u, f, h = (E - S).normalized(), (W - E).normalized(), (H - W).normalized()
    a = {"elbow_flex": math.degrees(u.angle(f)), "elevation": math.degrees(u.angle(-up))}
    # humeral rotation: neutral forearm = forward when the arm hangs, swung with the upper arm (shortest rotation)
    q = (-up).rotation_difference(u)
    ref = q @ fw
    fp = f - u * f.dot(u)
    if fp.length > 0.15 and a["elbow_flex"] > 12:      # undefined for a straight arm
        fp.normalize()
        ref = (ref - u * ref.dot(u)).normalized()
        a["humeral_rot"] = math.degrees(math.atan2(ref.cross(fp).dot(u) * (1 if side == "L" else -1), ref.dot(fp)))
    # forearm pronation: palm about the forearm vs the neutral (thumb up) palm = facing the body side of the hinge
    p = palm_of(side)
    pp = (p - f * p.dot(f))
    # neutral palm = the elbow hinge axis (thumb up, palm to the body with the arm hanging); for a near-straight arm
    # the hinge the elbow WOULD have at neutral humeral rotation (rest T-pose palm down = 0)
    hinge = u.cross(f) if a["elbow_flex"] > 12 else u.cross(ref)
    if pp.length > 0.1 and hinge.length > 1e-3:
        pp.normalize()
        n0 = hinge.normalized() * (1 if side == "L" else -1)
        n0 = (n0 - f * n0.dot(f)).normalized()
        a["pronation"] = math.degrees(math.atan2(n0.cross(pp).dot(f) * (1 if side == "L" else -1), n0.dot(pp)))
        s = f.cross(pp)
        a["wrist_flex"] = math.degrees(math.atan2(h.dot(pp), h.dot(f)))
        a["wrist_dev"] = math.degrees(math.atan2(h.dot(s) * (1 if side == "L" else -1), h.dot(f)))
    return {k: round(v, 1) for k, v in a.items()}


def arm_violations(side, ang=None):
    """{measure: degrees outside its range} (empty = anatomical)."""
    ang = ang or arm_angles(side)
    bad = {}
    for k, (lo, hi) in ARM_LIM["arm"].items():
        if k in ang and not lo <= ang[k] <= hi:
            bad[k] = round(ang[k] - (lo if ang[k] < lo else hi), 1)
    return bad


_hand_on = hand_on


def hand_on_limited(side, grip, hand_w, palm_w, pole_w, split=0.5, swivels=None, extra_cost=None):
    """hand_on with the limits in the loop: try the given pole first; if a limit breaks, swing the pole about the
    shoulder->grip axis; per swivel a wrist out of range is fixed by aiming the hand back into it (the palm stays on the
    grip). Stops at the first swivel that is anatomical with the hand as asked; otherwise keeps the least-bad one.
    A limit no swivel can satisfy (elbow_flex = reach) is returned in 'limit_fail' so the key spec gets fixed instead
    of the arm being forced; hand_clamped = how far (deg) the hand aim had to give."""
    S = wpos(f"Shoulder_{side}")
    ax = (Vector(grip) - S).normalized()
    pole0 = Vector(pole_w)
    # every try starts from the same basis: hand_on's arm_plane assumes an untwisted elbow, and the previous try
    # left its pronation twist on Elbow (first run: wrist 33 cm off the target after 10 tries)
    names = [f"{n}_{side}" for n in ("Shoulder", "Elbow", "Wrist", "MiddleFinger1")]
    B0 = {n: (P[n].location.copy(), P[n].rotation_quaternion.copy()) for n in names}

    def hand_on(*a):
        for n in names:
            P[n].location, P[n].rotation_quaternion = B0[n]
        upd()
        return _hand_on(*a)
    def attempt(sw):
        """one swivel: solve, and if the wrist is out, aim the hand back into range. Up to 5 rounds: the wrist target
        and the pronation move with the aim (F9 test: wrist_dev -97 -> -85 -> -79 -> -12 -> -10; 2 rounds left it -60)"""
        pole = Quaternion(ax, math.radians(sw)) @ pole0
        hw, r = Vector(hand_w), hand_on(side, grip, hand_w, palm_w, pole, split)
        bad = arm_violations(side)
        for _ in range(5):
            if not {"wrist_flex", "wrist_dev"} & set(bad):
                break
            hw = clamp_hand_dir(side)
            r = hand_on(side, grip, hw, palm_w, pole, split)
            bad = arm_violations(side)
        cl = math.degrees(Vector(hand_w).angle(hw))
        # limits first, then keep the hand as asked, then stay near the asked pole
        ex = extra_cost() if extra_cost else 0.0        # e.g. the shoulder skin crease (lhand.py)
        return sum(abs(v) for v in bad.values()) + 0.3 * cl + 0.05 * abs(sw) + ex, sw, bad, r, cl
    best, last = None, None
    for k, sw in enumerate(swivels or ARM_LIM.get("swivels", [0, 15, -15, 30, -30, 45, -45, 60, -60, 90, -90])):
        res, last = attempt(sw), sw
        if best is None or res[0] < best[0]:
            best = res
        if not res[2] and res[4] < 1:                  # anatomical with the hand exactly as asked: done
            break
    cost, sw, bad, r, cl = best
    if sw != last:                                     # the best try was not the last one: pose it again
        cost, sw, bad, r, cl = attempt(sw)
    r.update(swivel=sw, tries=k + 1, limit_fail=bad, angles=arm_angles(side), hand_clamped=round(cl, 1))
    return r


def clamp_hand_dir(side):
    """The current hand direction with wrist_flex / wrist_dev clamped into the limits (in the forearm-palm frame)."""
    E, W, H = wpos(f"Elbow_{side}"), wpos(f"Wrist_{side}"), wpos(f"MiddleFinger1_{side}")
    f, h, p = (W - E).normalized(), (H - W).normalized(), palm_of(side)
    pp = (p - f * p.dot(f)).normalized()
    s = f.cross(pp) * (1 if side == "L" else -1)
    lim = ARM_LIM["arm"]
    fl = max(lim["wrist_flex"][0], min(lim["wrist_flex"][1], math.degrees(math.atan2(h.dot(pp), h.dot(f)))))
    dv = max(lim["wrist_dev"][0], min(lim["wrist_dev"][1], math.degrees(math.atan2(h.dot(s), h.dot(f)))))
    v = f + pp * math.tan(math.radians(fl)) + s * math.tan(math.radians(dv))
    return v.normalized()


_COVER = {}


def elbow_covered(side, body=None):
    """(skin verts round the elbow hidden INSIDE the torso/coat seen from the outside, deepest cm). A ray from each
    elbow-skin vertex outward (away from the body) that hits torso skin = the elbow sank into the body (user
    2026-10-22: "Khuỷu tay đang bị chìm vào trong cơ thể"). Works on open low-poly shells (coat), unlike inside tests."""
    from mathutils.bvhtree import BVHTree
    ob = bpy.data.objects[body or BODY]
    if side not in _COVER:
        gi = {g.index: g.name for g in ob.vertex_groups}
        Wt = [{gi[g.group]: g.weight for g in v.groups} for v in ob.data.vertices]
        armw = lambda d: sum(d.get(f"{n}_{side}", 0) for n in ("Shoulder", "Elbow", "Wrist", "MiddleFinger1"))
        keep = set(i for i, d in enumerate(Wt) if armw(d) < 0.2)
        _COVER[side] = ([tuple(f.vertices) for f in ob.data.polygons if all(i in keep for i in f.vertices)],
                        [i for i, d in enumerate(Wt) if 0.25 < d.get(f"Elbow_{side}", 0) < 0.8])
    polys, elb = _COVER[side]
    r, fw, up = _chest()
    out = -r if side == "L" else r
    bo = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = bo.to_mesh()
    V = [bo.matrix_world @ v.co for v in me.vertices]
    bvh = BVHTree.FromPolygons(V, polys)
    hits = [h[3] for h in (bvh.ray_cast(V[i], out, 0.3) for i in elb) if h[0] is not None]
    bo.to_mesh_clear()
    return len(hits), round(max(hits or [0]) * 100, 1)


def elbow_gap(side, body=None, band_cm=6.0):
    """Sideways gap (cm) between the elbow skin and the torso/coat skin next to it (same height and depth band).
    b2q3: the elbow pressed 2 cm against the ribs and a bit back -> from the front the upper arm vanished behind the
    chest and the forearm grew out of the coat; P0 (approved) keeps 7 cm. 99 = nothing of the torso beside it."""
    ob = bpy.data.objects[body or BODY]
    if side not in _COVER:
        elbow_covered(side, body)
    polys, elb = _COVER[side]
    keepv = _COVER.setdefault(side + "_v", sorted(set(i for p in polys for i in p)))
    r, fw, up = _chest()
    out = -r if side == "L" else r
    C = wpos("Chest_M")
    bo = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = bo.to_mesh()
    M = bo.matrix_world
    rel = lambda co: (M @ co - C)
    ev = [rel(me.vertices[i].co) for i in elb]
    el_up = sum(v.dot(up) for v in ev) / len(ev)
    el_fw = sum(v.dot(fw) for v in ev) / len(ev)
    lat_e = min(v.dot(out) for v in ev)
    band = [v.dot(out) for v in (rel(me.vertices[i].co) for i in keepv)
            if abs(v.dot(up) - el_up) < band_cm / 100 and abs(v.dot(fw) - el_fw) < 0.08]
    bo.to_mesh_clear()
    return round((lat_e - max(band)) * 100, 1) if band else 99.0
