"""Blender side of the eye-keying workflow (run headless by tools/keyanim.py).

  setup  MODEL --work W                 -> W/controls.json (bones, rest aims, character axes)
  key    MODEL --work W                 -> W/anim.blend (action built from W/keys.json)
  render --work W --frames 1,10 --views front,left --scale 0.5
                                        -> W/look/render_<view>_<frame>.png + joints json

Pose spec (keys.json), all directions/angles in CHARACTER space:
  x = character's RIGHT, y = character's forward, z = up (right-handed).
  rot signs (right-hand rule): +z turns the bone toward the character's left,
  +x tips a forward-pointing bone up (an upright bone leans back), +y leans an
  upright bone toward the character's right.
  "rot":  [x, y, z] degrees, Euler XYZ about the character axes, applied on top
          of the parent (FK). [0,0,0] = rest pose relative to the parent.
  "aim":  [x, y, z] absolute direction the bone should point (its chain to the
          next joint), plus optional "twist" degrees about that direction.
  root:   {"loc": [x, y, z]} metres offset of the root bone from rest.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bl_common as C  # noqa: E402
import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Euler, Matrix, Quaternion, Vector  # noqa: E402

VIEWS = ("front", "back", "left", "right")


# ---------------------------------------------------------------- rig helpers
class Rig:
    def __init__(self, arm, mapping):
        self.arm = arm
        self.mapping = mapping
        self.order = C.bones_in_order(arm)
        rest = C.resolve_rest_points(arm, mapping)
        side, up, fwd = C.rig_axes(rest)
        # level the character frame: "up" is the world's up, not the hip->shoulder line
        # (a hunched rig would otherwise tilt every camera and every aim by its hunch)
        up = (arm.matrix_world.to_3x3().inverted() @ Vector((0, 0, 1))).normalized()
        side = (side - up * side.dot(up)).normalized()
        fwd = side.cross(up).normalized()
        # character frame in armature space: columns = (right, forward, up), right-handed
        self.Cm = Matrix((-side, fwd, up)).transposed()
        self.rest_pts = rest
        self.root = (mapping.get("root") or {}).get("bone")
        self.dirs = {}
        for b in self.order:
            self.dirs[b.name] = self._dir(b)
        mw = arm.matrix_world
        self.world_to_arm = mw.inverted().to_3x3()
        # character axes in world space (for cameras)
        r3 = mw.to_3x3().normalized()
        self.w_side = (r3 @ side).normalized()
        self.w_fwd = (r3 @ fwd).normalized()
        self.w_up = (r3 @ up).normalized()

    def _dir(self, b):
        # prefer the mapping's joint chain (e.g. Shoulder_L: shoulder -> elbow)
        for e in self.mapping.get("bones", []):
            if e["bone"] == b.name:
                p, q = e["dir"]
                if p in self.rest_pts and q in self.rest_pts:
                    v = self.rest_pts[q] - self.rest_pts[p]
                    if v.length > 1e-6:
                        return v.normalized()
        kids = list(b.children)
        if kids:
            far = kids[0] if len(kids) == 1 else max(kids, key=lambda c: (c.head_local - b.head_local).length)
            v = far.head_local - b.head_local
            if v.length > 1e-6:
                return v.normalized()
        return (b.tail_local - b.head_local).normalized()

    def char_to_arm(self, v):
        """Character-space metres [right, forward, up] -> armature-space vector."""
        v = Vector(v)
        return self.world_to_arm @ (-self.w_side * v.x + self.w_fwd * v.y + self.w_up * v.z)

    def to_char(self, v):
        return self.Cm.transposed() @ v

    def from_char(self, v):
        return self.Cm @ Vector(v)

    def solve(self, pose):
        """pose: {"bones": {name: spec}, "root": {"loc": [...]}} -> {name: basis Matrix}"""
        specs = pose.get("bones", {})
        D, P, basis = {}, {}, {}
        loc = Vector((pose.get("root") or {}).get("loc", (0, 0, 0)))
        offset = self.char_to_arm(loc)
        for b in self.order:
            R = b.matrix_local
            pD = D[b.parent.name] if b.parent else Quaternion()
            M0 = P[b.parent.name] @ (b.parent.matrix_local.inverted() @ R) if b.parent else R.copy()
            s = specs.get(b.name)
            d = pD.copy()
            if s:
                if "aim" in s:
                    cur = pD @ self.dirs[b.name]
                    tgt = self.from_char(s["aim"]).normalized()
                    d = cur.rotation_difference(tgt) @ pD
                    if s.get("twist"):
                        d = Quaternion(tgt, math.radians(s["twist"])) @ d
                if "rot" in s:
                    e = Euler([math.radians(a) for a in s["rot"]], "XYZ").to_matrix()
                    q = (self.Cm @ e @ self.Cm.transposed()).to_quaternion()
                    d = d @ q if "aim" in s else pD @ q
            D[b.name] = d
            M = Matrix.Translation(M0.translation) @ (d @ R.to_quaternion()).to_matrix().to_4x4()
            if b.name == self.root and offset.length:
                M = Matrix.Translation(offset) @ M
            if s and "loc" in s:
                M = Matrix.Translation(self.char_to_arm(s["loc"])) @ M
            P[b.name] = M
            basis[b.name] = M0.inverted() @ M
        self.last_P = P
        return basis

    def char_dir_of(self, name):
        return [round(x, 3) for x in self.to_char(self.dirs[name])]


def body_heights(arm, rig):
    """Rest heights (along up) of mesh vertices skinned to the character's body
    chain (root bone, its ancestors and descendants) -- ignores separate props."""
    rb = arm.data.bones.get(rig.root) if rig.root else None
    body = {b.name for b in arm.data.bones}
    if rb:
        body = {rb.name} | {p.name for p in rb.parent_recursive} | {c.name for c in rb.children_recursive}
    zs = []
    for o in arm.children_recursive:
        if o.type != "MESH":
            continue
        names = {g.index: g.name for g in o.vertex_groups}
        for v in o.data.vertices:
            if v.groups:
                g = max(v.groups, key=lambda g: g.weight)
                if names.get(g.group) not in body:
                    continue
            zs.append((o.matrix_world @ v.co).dot(rig.w_up))
    return zs or [0.0, 1.0]


def resolve_keys(keys):
    """Carry bone specs forward: a bone missing from a key keeps its previous spec."""
    frames = sorted(int(f) for f in keys["keys"])
    cur_b, cur_root, out = {}, {}, []
    for f in frames:
        k = keys["keys"][str(f)]
        for name, spec in k.get("bones", {}).items():
            cur_b[name] = spec
        if "root" in k:
            cur_root = k["root"]
        out.append((f, {"bones": dict(cur_b), "root": dict(cur_root)}))
    return out


# ---------------------------------------------------------------- commands
def cmd_setup(a):
    C.load_model(a.model)
    mapping = C.load_json(os.path.join(a.work, "mapping.json"))
    arm = C.find_armature(mapping.get("armature"))
    rig = Rig(arm, mapping)
    roles = {e["bone"]: e for e in mapping.get("bones", [])}
    zs = body_heights(arm, rig)
    controls = {
        "armature": arm.name,
        "root_bone": rig.root,
        "axes_note": "character space: x = character's right, y = forward, z = up (right-handed). rot +z = turn left, +x = lean back (upright bone), +y = lean right",
        "character_height_m": round(max(zs) - min(zs), 4),
        "ground_m": round(min(zs), 4),
        "bones": [
            {
                "name": b.name,
                "parent": b.parent.name if b.parent else None,
                "mapped": b.name in roles,
                "rest_aim": rig.char_dir_of(b.name),
            }
            for b in rig.order if b.name in roles or b.name == rig.root
        ],
        "other_bones": [b.name for b in rig.order if b.name not in roles and b.name != rig.root],
    }
    C.save_json(os.path.join(a.work, "controls.json"), controls)
    print(f"controls.json: {len(controls['bones'])} key bones, height {controls['character_height_m']} m")


def build_action(arm, rig, keys):
    scene = bpy.context.scene
    scene.render.fps = max(1, round(keys.get("fps", 30)))
    scene.render.fps_base = scene.render.fps / keys.get("fps", 30)
    scene.frame_start = 1
    scene.frame_end = int(keys.get("frame_count", 1))
    arm.animation_data_create()
    old = arm.animation_data.action
    action = bpy.data.actions.new(keys.get("action", f"{arm.name}_keyed"))
    arm.animation_data.action = action
    if old and old.users == 0:
        bpy.data.actions.remove(old)
    names = set()
    for _, pose in resolve_keys(keys):
        names |= set(pose["bones"])
    if rig.root:
        names.add(rig.root)
    pbs = arm.pose.bones
    for pb in pbs:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
    grips = {n for _, pose in resolve_keys(keys) for n, sp in pose["bones"].items() if "grip" in sp}
    prev = {}
    keyed = [b for b in rig.order if b.name in names and b.name not in grips]
    for f, pose in resolve_keys(keys):
        basis = rig.solve(pose)
        for b in keyed:
            m = basis[b.name]
            q = m.to_quaternion().normalized()
            if b.name in prev and q.dot(prev[b.name]) < 0:
                q.negate()
            prev[b.name] = q
            pb = pbs[b.name]
            pb.rotation_quaternion = q
            pb.keyframe_insert("rotation_quaternion", frame=f, group=b.name)
            if b.name == rig.root:
                pb.location = m.to_translation()
                pb.keyframe_insert("location", frame=f, group=b.name)
    interp = keys.get("interpolation", "BEZIER")
    for fc in getattr(action, "fcurves", []):
        for kp in fc.keyframe_points:
            kp.interpolation = interp
    if keys.get("bake"):
        bake_frames(arm, keys)
    if keys.get("layers"):
        bake_layers(arm, rig, keys)
    if keys.get("foot_lock"):
        lock_feet(arm, keys["foot_lock"], int(keys.get("foot_lock_frame", 1)), keys.get("foot_lock_ranges"))
    if keys.get("props"):
        bake_props(arm, rig, keys["props"])
    if keys.get("arm_ik"):
        bake_arm_ik(arm, keys["arm_ik"])
        grips = set()  # hands now follow the props, not the other way round
    for name in grips:  # last, so props follow the hands including layer motion
        bake_grip(arm, rig, keys, name)
    return action


def _key_pb(pb, f):
    pb.keyframe_insert("rotation_quaternion", frame=f, group=pb.name)
    pb.keyframe_insert("location", frame=f, group=pb.name)


def _set_world(arm, pb, M_world):
    pb.matrix = arm.matrix_world.inverted() @ M_world
    bpy.context.view_layer.update()


def bake_props(arm, rig, props):
    """Held props as child-of constraints. Each prop is placed once (frame 1), in WORLD terms
    measured from the reference views (tools/tri.py), then rides on its parent bone every frame:
      {"bone": "Weapon", "parent": "Chest_M", "at": -0.3, "pos": [x,y,z],   # point `at` (bone
       "aim": [x,y,z], "twist": 0}                                            # fraction) -> pos
    aim is in character space (x right, y forward, z up); pos is world metres."""
    scene = bpy.context.scene
    pbs = arm.pose.bones
    mw = arm.matrix_world
    for p in props:
        pb, par = pbs[p["bone"]], pbs[p["parent"]]
        scene.frame_set(1)
        Mcur = mw @ pb.matrix
        y_now = (Mcur.to_3x3() @ Vector((0, 1, 0))).normalized()
        aim_w = (mw.to_3x3() @ rig.char_to_arm(p["aim"])).normalized()
        q = y_now.rotation_difference(aim_w)
        R = q.to_matrix() @ Mcur.to_3x3()
        if p.get("twist"):
            R = Quaternion(aim_w, math.radians(p["twist"])).to_matrix() @ R
        length_w = (R @ Vector((0, pb.bone.length, 0)))        # world vector head->tail (scaled)
        head = Vector(p["pos"]) - length_w * float(p.get("at", 0.0))
        M1 = Matrix.Translation(head) @ R.to_4x4()
        rel = (mw @ par.matrix).inverted() @ M1
        for f in range(scene.frame_start, scene.frame_end + 1):
            scene.frame_set(f)
            _set_world(arm, pb, (mw @ par.matrix) @ rel)
            _key_pb(pb, f)
        print(f"Prop {p['bone']} carried by {p['parent']}")


def bake_arm_ik(arm, specs):
    """Two-bone IK for hands holding props. Target and pole are world points measured at frame 1
    (tools/tri.py); both ride on `follow` (the prop) every frame. The end bone keeps the orientation
    relative to the prop it has at frame 1, so the grip never slides.
      {"chain": ["Shoulder_L","Elbow_L","Wrist_L"], "follow": "Weapon", "target": [x,y,z], "pole": [x,y,z]}"""
    scene = bpy.context.scene
    pbs = arm.pose.bones
    mw = arm.matrix_world
    for s in specs:
        up, lo, end = (pbs[n] for n in s["chain"])
        fol = pbs[s["follow"]]
        scene.frame_set(1)
        F1inv = (mw @ fol.matrix).inverted()
        tgt_rel = F1inv @ Vector(s["target"])
        pole_rel = F1inv @ Vector(s["pole"])
        end_rel = None
        for f in range(scene.frame_start, scene.frame_end + 1):
            scene.frame_set(f)
            Fw = mw @ fol.matrix
            if end_rel is None:   # frame 1, before IK: the hand's keyed (FK/aim) orientation vs the prop
                end_rel = Fw.to_3x3().inverted() @ (mw @ end.matrix).to_3x3()
            T, Pp = Fw @ tgt_rel, Fw @ pole_rel
            S = mw @ up.head
            E = mw @ lo.head
            W = mw @ end.head
            a, b = (E - S).length, (W - E).length
            d = min((T - S).length, (a + b) * 0.999)
            dirST = (T - S).normalized()
            pole_dir = (Pp - S) - dirST * (Pp - S).dot(dirST)
            pole_dir = pole_dir.normalized() if pole_dir.length > 1e-6 else (E - S).normalized()
            cosA = max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d)))
            elbow = S + dirST * (a * cosA) + pole_dir * (a * math.sqrt(max(0.0, 1 - cosA * cosA)))
            Mup = mw @ up.matrix
            q = (E - S).rotation_difference(elbow - S)
            _set_world(arm, up, Matrix.Translation(S) @ (q.to_matrix() @ Mup.to_3x3()).to_4x4())
            E2, W2 = mw @ lo.head, mw @ end.head
            Mlo = mw @ lo.matrix
            q = (W2 - E2).rotation_difference(S + dirST * d - E2)
            _set_world(arm, lo, Matrix.Translation(E2) @ (q.to_matrix() @ Mlo.to_3x3()).to_4x4())
            Wh = mw @ end.head
            _set_world(arm, end, Matrix.Translation(Wh) @ (Fw.to_3x3() @ end_rel).to_4x4())
            for pb in (up, lo, end):
                _key_pb(pb, f)
        print(f"Arm IK {s['chain']} following {s['follow']}")


def lock_feet(arm, chains, ref_frame=1, ranges=None):
    """Planted feet: analytic two-bone IK per frame so each ankle keeps the position and
    orientation it has at `ref_frame`; the knee bends in its current plane.
    chains: [["Hip_L", "Knee_L", "Ankle_L"], ...] (thigh, shin, foot bones)."""
    scene = bpy.context.scene
    pbs = arm.pose.bones
    scene.frame_set(ref_frame)
    targets = {c[2]: pbs[c[2]].matrix.copy() for c in chains}
    for f in range(scene.frame_start, scene.frame_end + 1):
        if ranges and not any(a <= f <= b for a, b in ranges):
            continue  # feet free (in the air / sliding): keep the keyed leg aims
        scene.frame_set(f)
        for hip, knee, ankle in chains:
            ph, pk, pa = pbs[hip], pbs[knee], pbs[ankle]
            H, K, A = ph.head.copy(), pk.head.copy(), pa.head.copy()
            T = targets[ankle].to_translation()
            a, b = (K - H).length, (A - K).length
            d = min((T - H).length, (a + b) * 0.9999)
            n = (K - H).cross(T - H)
            if n.length < 1e-9:
                continue
            n.normalize()
            dir_ht = (T - H).normalized()
            alpha = math.acos(max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d))))
            # two mirror solutions in the knee plane: keep the one on the current knee's side
            cands = [H + (Quaternion(n, s * alpha) @ dir_ht) * a for s in (1, -1)]
            knee_new = min(cands, key=lambda p: (p - K).length)
            q1 = (K - H).rotation_difference(knee_new - H)
            ph.matrix = Matrix.Translation(H) @ (q1.to_matrix() @ ph.matrix.to_3x3()).to_4x4()
            bpy.context.view_layer.update()
            K2, A2 = pk.head.copy(), pa.head.copy()
            q2 = (A2 - K2).rotation_difference(T - K2)
            pk.matrix = Matrix.Translation(K2) @ (q2.to_matrix() @ pk.matrix.to_3x3()).to_4x4()
            bpy.context.view_layer.update()
            pa.matrix = Matrix.Translation(pa.head.copy()) @ targets[ankle].to_3x3().to_4x4()
            bpy.context.view_layer.update()
            for pb in (ph, pk, pa):
                pb.keyframe_insert("rotation_quaternion", frame=f, group=pb.name)
                pb.keyframe_insert("location", frame=f, group=pb.name)
    print(f"Feet locked to frame {ref_frame}: {[c[2] for c in chains]}")


def layer_value(track, f, n_frames, cyclic):
    """Catmull-Rom through {frame: [x, y, z]} keys. Cyclic tracks wrap over the clip length
    (first frame == last frame), so extremes ease and the loop has no seam."""
    pts = sorted((int(k), Vector(v)) for k, v in track.items())
    if len(pts) == 1:
        return pts[0][1].copy()
    span = n_frames - 1
    if cyclic:
        if pts[-1][0] - pts[0][0] == span:   # drop the duplicated end key for wrapping
            pts = pts[:-1]
        ext = [(fr - span, v) for fr, v in pts] + pts + [(fr + span, v) for fr, v in pts]
    else:
        ext = [(pts[0][0] - 1, pts[0][1])] + pts + [(pts[-1][0] + 1, pts[-1][1])]
    for i in range(1, len(ext) - 2):
        (f1, p1), (f2, p2) = ext[i], ext[i + 1]
        if f1 <= f <= f2:
            f0, p0 = ext[i - 1]
            f3, p3 = ext[i + 2]
            t = (f - f1) / max(1e-9, f2 - f1)
            m1 = (p2 - p0) / max(1e-9, f2 - f0) * (f2 - f1)
            m2 = (p3 - p1) / max(1e-9, f3 - f1) * (f2 - f1)
            t2, t3 = t * t, t * t * t
            return (2 * t3 - 3 * t2 + 1) * p1 + (t3 - 2 * t2 + t) * m1 + (-2 * t3 + 3 * t2) * p2 + (t3 - t2) * m2
    return (pts[0][1] if f < pts[0][0] else pts[-1][1]).copy()


def bake_layers(arm, rig, keys):
    """Additive animation layers (like Maya/Blender anim layers), keyed per bone and per channel:

      "layers": [{"name": "breath", "cyclic": true,
                  "bones": {"Chest_M": {"rot": {"1": [0,0,0], "18": [-3,0,0], "31": [0,0,0]}},
                            "Root_M":  {"loc": {"1": [0,0,0], "16": [0,0,-0.04], "31": [0,0,0]}}}}]

    rot = degrees about the character axes (x right, y forward, z up), applied in the bone's
    rest frame on top of the base pose (FK: children inherit). loc = metres along the character
    axes. Each bone has its own key frames, so offsets / overlap are just shifted keys."""
    scene = bpy.context.scene
    n = scene.frame_end
    pbs = arm.pose.bones
    names = sorted({b for L in keys["layers"] for b in L.get("bones", {})})
    names = [b for b in names if b in pbs]
    # pass 1: sample the base pose before any layer key is written
    base = {}
    for f in range(1, n + 1):
        scene.frame_set(f)
        base[f] = {b: pbs[b].matrix_basis.copy() for b in names}
    # pass 2: add the layers and key every frame for the layered bones
    prev = {}
    for f in range(1, n + 1):
        scene.frame_set(f)
        for b in names:
            bone = arm.data.bones[b]
            Rrest = bone.matrix_local.to_3x3()
            rot = Vector((0, 0, 0))
            loc = Vector((0, 0, 0))
            for L in keys["layers"]:
                spec = L.get("bones", {}).get(b)
                if not spec:
                    continue
                cyc = L.get("cyclic", False)
                ff, nn = f, n
                if L.get("period"):   # repeat the track (authored over keys 1..span) every `period` frames
                    span = L.get("span", 31)
                    ph = ((f - 1) % L["period"]) / L["period"]
                    ff, nn = 1 + ph * (span - 1), span
                if "rot" in spec:
                    rot += layer_value(spec["rot"], ff, nn, cyc)
                if "loc" in spec:
                    loc += layer_value(spec["loc"], ff, nn, cyc)
            B = base[f][b].copy()
            if rot.length > 1e-9:
                E = Euler([math.radians(a) for a in rot], "XYZ").to_matrix()
                Q = rig.Cm @ E @ rig.Cm.transposed()           # armature-space rotation
                local = (Rrest.inverted() @ Q @ Rrest).to_4x4()
                B = B @ local
            if loc.length > 1e-9:
                if bone.parent:
                    M0 = pbs[bone.parent.name].matrix @ (bone.parent.matrix_local.inverted() @ bone.matrix_local)
                else:
                    M0 = bone.matrix_local
                t = M0.to_3x3().inverted() @ rig.char_to_arm(loc)
                B = Matrix.Translation(B.to_translation() + t) @ B.to_3x3().to_4x4()
            pb = pbs[b]
            q = B.to_quaternion().normalized()
            if b in prev and q.dot(prev[b]) < 0:
                q.negate()
            prev[b] = q
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = q
            pb.location = B.to_translation()
            pb.keyframe_insert("rotation_quaternion", frame=f, group=b)
            pb.keyframe_insert("location", frame=f, group=b)
    print(f"Layers baked: {len(names)} bones x {n} frames ({', '.join(L.get('name', '?') for L in keys['layers'])})")


def bake_frames(arm, keys):
    """Per-frame poses from the silhouette fitter (keys.json "bake": "fit_smooth.npy"):
    one key on every frame for every bone the fit moved."""
    import numpy as np
    work = os.path.dirname(os.path.abspath(keys["_path"]))
    B = np.load(os.path.join(work, keys["bake"]))
    names = C.load_json(os.path.join(work, "rig_np.json"))["bones"]
    pbs = arm.pose.bones
    moved = [i for i in range(len(names))
             if np.abs(B[:, i] - np.eye(4)).max() > 1e-5 and names[i] in pbs]
    prev = {}
    for f in range(B.shape[0]):
        for i in moved:
            pb = pbs[names[i]]
            m = Matrix(B[f, i].tolist())
            q = m.to_quaternion().normalized()
            if i in prev and q.dot(prev[i]) < 0:
                q.negate()
            prev[i] = q
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = q
            pb.location = m.to_translation()
            pb.keyframe_insert("rotation_quaternion", frame=f + 1, group=pb.name)
            pb.keyframe_insert("location", frame=f + 1, group=pb.name)
    action = arm.animation_data.action
    for fc in getattr(action, "fcurves", []):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    print(f"Baked {B.shape[0]} frames x {len(moved)} bones from {keys['bake']}")


def bake_grip(arm, rig, keys, name):
    """Key a held prop on every frame: orientation interpolated between its keys,
    position pinned so the point `at` (0 = bone head, 1 = tail) sits at the grip bone."""
    scene = bpy.context.scene
    b = arm.data.bones[name]
    R = b.matrix_local
    ks = []
    for f, pose in resolve_keys(keys):
        sp = pose["bones"].get(name)
        if not sp or "grip" not in sp:
            continue
        rig.solve(pose)
        g = sp["grip"]
        ks.append((f, rig.last_P[name].to_quaternion(), g["bone"], float(g.get("at", 0.0)),
                   rig.char_to_arm(g.get("offset", (0, 0, 0)))))
    if not ks:
        return
    pb = arm.pose.bones[name]
    prev = None
    for f in range(scene.frame_start, scene.frame_end + 1):
        i = max([j for j, k in enumerate(ks) if k[0] <= f] or [0])
        k0 = ks[i]
        k1 = ks[min(i + 1, len(ks) - 1)]
        t = 0.0 if k1[0] == k0[0] else min(1.0, max(0.0, (f - k0[0]) / (k1[0] - k0[0])))
        t = t * t * (3 - 2 * t)  # ease like the bezier keys
        q = k0[1].slerp(k1[1], t)
        at = k0[3] + (k1[3] - k0[3]) * t
        off = k0[4].lerp(k1[4], t)
        scene.frame_set(f)
        hand = arm.pose.bones[k0[2]].head.copy()
        axis = q @ Vector((0, 1, 0))
        head = hand + off - axis * (at * b.length)
        M = Matrix.Translation(head) @ q.to_matrix().to_4x4()
        if b.parent:
            pm = arm.pose.bones[b.parent.name].matrix
            M0 = pm @ (b.parent.matrix_local.inverted() @ R)
        else:
            M0 = R
        basis = M0.inverted() @ M
        qb = basis.to_quaternion().normalized()
        if prev is not None and qb.dot(prev) < 0:
            qb.negate()
        prev = qb
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = qb
        pb.location = basis.to_translation()
        pb.keyframe_insert("rotation_quaternion", frame=f, group=name)
        pb.keyframe_insert("location", frame=f, group=name)


def cmd_key(a):
    C.load_model(a.model)
    mapping = C.load_json(os.path.join(a.work, "mapping.json"))
    keys = C.load_json(os.path.join(a.work, "keys.json"))
    keys["_path"] = os.path.join(a.work, "keys.json")
    arm = C.find_armature(mapping.get("armature"))
    rig = Rig(arm, mapping)
    action = build_action(arm, rig, keys)
    bpy.context.scene.frame_set(1)
    bpy.context.preferences.filepaths.save_version = 0
    out = os.path.abspath(os.path.join(a.work, "anim.blend"))
    bpy.ops.wm.save_as_mainfile(filepath=out, copy=True)
    print(f"Keyed {len(keys['keys'])} keys into '{action.name}' -> {out}")
    if a.export:
        bpy.ops.object.select_all(action="DESELECT")
        arm.select_set(True)
        for o in arm.children_recursive:
            o.select_set(True)
        bpy.context.view_layer.objects.active = arm
        path = os.path.abspath(a.export)
        if path.lower().endswith(".fbx"):
            bpy.ops.export_scene.fbx(filepath=path, use_selection=True, bake_anim=True, add_leaf_bones=False)
        else:
            bpy.ops.export_scene.gltf(filepath=path, use_selection=True, export_animations=True,
                                      export_animation_mode="ACTIVE_ACTIONS", export_force_sampling=True,
                                      export_image_format="AUTO")
        print(f"Exported {path}")


def camera_params(rig, view, cal, ref_w, ref_h, ground_m, height_m):
    """Ortho camera of a calibrated reference view. A world point p lands on reference pixel
    u = W/2 + (p - pos).right / k,  v = H/2 - (p - pos).up / k."""
    d = {"front": -rig.w_fwd, "back": rig.w_fwd, "left": -rig.w_side, "right": rig.w_side}[view]
    up = rig.w_up
    right = d.cross(up).normalized()
    # metres per reference pixel, from the character's height in the reference
    k = height_m / max(1.0, cal["ground_px"] - cal["top_px"])
    root_w = rig.arm.matrix_world @ rig.arm.data.bones[rig.root].head_local if rig.root else Vector()
    along_r = root_w.dot(right) - (cal["center_px"] - ref_w / 2) * k
    along_u = ground_m + (cal["ground_px"] - ref_h / 2) * k
    pos = right * along_r + up * along_u + d * (root_w.dot(d) - height_m * 10)
    return d, up, right, k, pos


def make_camera(rig, view, cal, ref_w, ref_h, scale, ground_m, height_m):
    """Ortho camera matching a calibrated reference view."""
    d, up, right, k, pos = camera_params(rig, view, cal, ref_w, ref_h, ground_m, height_m)
    cam_data = bpy.data.cameras.new(f"Cam_{view}")
    cam_data.type = "ORTHO"
    cam_data.sensor_fit = "VERTICAL"
    cam_data.ortho_scale = ref_h * k
    cam_data.clip_end = height_m * 40
    cam = bpy.data.objects.new(f"Cam_{view}", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.matrix_world = Matrix((
        (right.x, up.x, -d.x, pos.x),
        (right.y, up.y, -d.y, pos.y),
        (right.z, up.z, -d.z, pos.z),
        (0, 0, 0, 1),
    ))
    return cam


def cmd_render(a):
    work = a.work
    C.load_model(os.path.join(work, "anim.blend"))
    mapping = C.load_json(os.path.join(work, "mapping.json"))
    controls = C.load_json(os.path.join(work, "controls.json"))
    refs = C.load_json(os.path.join(work, "refs.json"))
    cams = C.load_json(os.path.join(work, "cameras.json"))
    arm = C.find_armature(mapping.get("armature"))
    rig = Rig(arm, mapping)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "TEXTURE" if a.textured else "SINGLE"
    scene.display.shading.single_color = (0.95, 0.55, 0.2)
    scene.render.film_transparent = not a.textured
    if a.textured:  # flat grey background like the references, for optical-flow comparisons
        scene.world = scene.world or bpy.data.worlds.new("W")
        scene.world.color = (0.105, 0.105, 0.105)
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    outdir = os.path.join(work, "look")
    os.makedirs(outdir, exist_ok=True)
    frames = [int(x) for x in a.frames.split(",") if x.strip()]
    views = [v for v in a.views.split(",") if v.strip()] if a.views else list(cams.keys())
    joints = {k: v for k, v in mapping["joints"].items() if "bone" in v}
    for view in views:
        if view not in cams:
            raise SystemExit(f"View '{view}' is not calibrated (cameras.json)")
        rv = refs["views"][view]
        cam = make_camera(rig, view, cams[view], rv["width"], rv["height"], a.scale,
                          controls["ground_m"], controls["character_height_m"])
        scene.camera = cam
        scene.render.resolution_x = int(rv["width"] * a.scale)
        scene.render.resolution_y = int(rv["height"] * a.scale)
        scene.render.resolution_percentage = 100
        for fr in frames:
            scene.frame_set(fr)
            lms = {}
            for name, spec in joints.items():
                pb = arm.pose.bones[spec["bone"]]
                p = arm.matrix_world @ (pb.tail if spec.get("end") == "tail" else pb.head)
                c = world_to_camera_view(scene, cam, p)
                lms[name] = [c.x, 1 - c.y]
            C.save_json(os.path.join(outdir, f"joints_{view}_{fr:05d}.json"), lms)
            scene.render.filepath = os.path.abspath(os.path.join(outdir, f"render_{view}_{fr:05d}.png"))
            bpy.ops.render.render(write_still=True)
    print(f"Rendered {len(frames)} frames x {len(views)} views")


def cmd_dump(a):
    """Everything the numpy fitter needs: rest mesh, skin weights, bones, cameras, current pose."""
    import numpy as np
    work = a.work
    C.load_model(os.path.join(work, "anim.blend"))
    mapping = C.load_json(os.path.join(work, "mapping.json"))
    controls = C.load_json(os.path.join(work, "controls.json"))
    refs = C.load_json(os.path.join(work, "refs.json"))
    cams = C.load_json(os.path.join(work, "cameras.json"))
    arm = C.find_armature(mapping.get("armature"))
    rig = Rig(arm, mapping)
    order = rig.order
    bidx = {b.name: i for i, b in enumerate(order)}
    arm_inv = arm.matrix_world.inverted()
    V, F, WI, WW, PART, COL = [], [], [], [], [], []
    for o in arm.children_recursive:
        if o.type != "MESH":
            continue
        me = o.data
        me.calc_loop_triangles()
        base = len(V)
        names = {g.index: g.name for g in o.vertex_groups}
        to_arm = arm_inv @ o.matrix_world
        # per-vertex colour from the base colour texture (for part masks)
        img = None
        for slot in o.material_slots:
            if slot.material and slot.material.use_nodes:
                for n in slot.material.node_tree.nodes:
                    if n.type == "TEX_IMAGE" and n.image:
                        n.image.pixels[0]  # force-load the pixels
                        if n.image.size[0] > 0:
                            img = n.image
        vcol = np.zeros((len(me.vertices), 3))
        if img is not None and me.uv_layers.active:
            w, h = img.size
            px = np.array(img.pixels[:]).reshape(h, w, 4)
            uv = me.uv_layers.active.data
            cnt = np.zeros(len(me.vertices))
            for li, loop in enumerate(me.loops):
                x, y = uv[li].uv
                c = px[min(h - 1, max(0, int(y * h))), min(w - 1, max(0, int(x * w))), :3]
                vcol[loop.vertex_index] += c
                cnt[loop.vertex_index] += 1
            vcol /= np.maximum(cnt, 1)[:, None]
        for v in me.vertices:
            V.append(list(to_arm @ v.co))
            gs = sorted(((names.get(g.group), g.weight) for g in v.groups if names.get(g.group) in bidx),
                        key=lambda t: -t[1])[:4]
            tot = sum(wt for _, wt in gs) or 1.0
            gs += [(order[0].name, 0.0)] * (4 - len(gs))
            WI.append([bidx[n] for n, _ in gs])
            WW.append([wt / tot for _, wt in gs])
            PART.append(1 if gs[0][0] in ("Weapon",) else 0)
        COL.extend(vcol.tolist())
        for t in me.loop_triangles:
            F.append([base + i for i in t.vertices])
    rest = np.array([np.array(b.matrix_local) for b in order])
    parent = np.array([bidx[b.parent.name] if b.parent else -1 for b in order])
    # current animation, local basis per bone per frame
    scene = bpy.context.scene
    n = scene.frame_end
    basis = np.zeros((n, len(order), 4, 4))
    for f in range(1, n + 1):
        scene.frame_set(f)
        for i, b in enumerate(order):
            basis[f - 1, i] = np.array(arm.pose.bones[b.name].matrix_basis)
    cam = {}
    for v, cal in cams.items():
        rv = refs["views"][v]
        d, up, right, k, pos = camera_params(rig, v, cal, rv["width"], rv["height"],
                                             controls["ground_m"], controls["character_height_m"])
        cam[v] = {"right": list(right), "up": list(up), "dir": list(d), "k": k, "pos": list(pos),
                  "W": rv["width"], "H": rv["height"]}
    np.savez_compressed(os.path.join(work, "rig_np.npz"), verts=np.array(V), faces=np.array(F),
                        wi=np.array(WI), ww=np.array(WW), part=np.array(PART), vcol=np.array(COL),
                        rest=rest, parent=parent, basis=basis, arm_mw=np.array(arm.matrix_world))
    C.save_json(os.path.join(work, "rig_np.json"), {
        "bones": [b.name for b in order], "cameras": cam,
        "char_axes_world": {"right": list(-rig.w_side), "forward": list(rig.w_fwd), "up": list(rig.w_up)}})
    # reference skinned positions from Blender for frame 1 (to validate numpy skinning)
    scene.frame_set(1)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = []
    for o in arm.children_recursive:
        if o.type == "MESH":
            eo = o.evaluated_get(dg)
            m = eo.to_mesh()
            ev.extend([list(arm_inv @ (eo.matrix_world @ v.co)) for v in m.vertices])
            eo.to_mesh_clear()
    np.save(os.path.join(work, "check_f1.npy"), np.array(ev))
    print(f"dump: {len(V)} verts, {len(F)} tris, {len(order)} bones, {n} frames, views {list(cam)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["setup", "key", "render", "dump"])
    ap.add_argument("model", nargs="?")
    ap.add_argument("--work", required=True)
    ap.add_argument("--export", default=None)
    ap.add_argument("--frames", default="1")
    ap.add_argument("--views", default=None)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--textured", action="store_true")
    a = ap.parse_args(C.script_args())
    {"setup": cmd_setup, "key": cmd_key, "render": cmd_render, "dump": cmd_dump}[a.cmd](a)


if __name__ == "__main__":
    main()
