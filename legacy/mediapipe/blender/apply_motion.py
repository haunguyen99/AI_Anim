"""Key a rig frame-by-frame so it reproduces the motion in pose.json.

blender -b -P tools/blender/apply_motion.py -- MODEL POSE_JSON MAPPING_JSON --out result.blend
        [--export result.fbx|.glb] [--root-motion xz|x|none] [--floor clamp|lock|none]
        [--step 1] [--action NAME]

Bone modes in mapping.json:
  swing : rotate the bone (from its parent-posed orientation) by the smallest
          rotation that aligns the rest segment dir[0]->dir[1] with the reference.
  frame : full orientation from two vectors: dir + weighted "twist" vectors.
  limb  : like frame, with the bend plane (dir, pole) driving the twist so elbows
          and knees hinge correctly; falls back to swing when the limb is straight.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bl_common as C  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Quaternion, Vector  # noqa: E402


def frame_matrix(d, s):
    """Orthonormal 3x3 from a primary and a secondary direction (None if degenerate)."""
    x = d.normalized()
    s = s - x * s.dot(x)
    if s.length < 1e-6:
        return None
    y = s.normalized()
    return Matrix((x, y, x.cross(y))).transposed()


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


class Retargeter:
    def __init__(self, arm, mapping, pose):
        self.arm = arm
        self.mapping = mapping
        self.order = C.bones_in_order(arm)
        self.rest = C.resolve_rest_points(arm, mapping)
        self.entries = {e["bone"]: e for e in mapping["bones"]}
        for name in self.entries:
            if name not in arm.data.bones:
                raise SystemExit(f"Mapped bone '{name}' not in armature '{arm.name}'")
        self.names = pose["landmark_names"]
        self.index = {n: i for i, n in enumerate(self.names)}
        # world (Blender convention) -> armature space, rotation only
        self.to_arm = arm.matrix_world.to_quaternion().inverted().to_matrix()
        self.root = (mapping.get("root") or {}).get("bone")
        self.prev_rot = {}
        self.aspect = pose["width"] / max(1, pose["height"])
        self.foot_joints = [j for j in ("left_ankle", "right_ankle", "left_toe", "right_toe")
                            if j in mapping["joints"] and "bone" in mapping["joints"][j]]

    # -- landmark access -------------------------------------------------
    def point(self, frame, name):
        if name in self.index:
            return self.to_arm @ Vector(frame["world"][self.index[name]])
        parts = C.VIRTUAL.get(name)
        if not parts:
            raise SystemExit(f"Unknown landmark '{name}'")
        return sum((self.point(frame, p) for p in parts), Vector()) / len(parts)

    def rest_point(self, name):
        if name not in self.rest:
            raise SystemExit(f"Landmark '{name}' has no rest position: add it to mapping.joints")
        return self.rest[name]

    def seg(self, frame, a, b):
        return self.point(frame, b) - self.point(frame, a)

    def rest_seg(self, a, b):
        return self.rest_point(b) - self.rest_point(a)

    def twist(self, frame, spec, rest):
        v = Vector()
        for a, b, w in spec:
            s = self.rest_seg(a, b) if rest else self.seg(frame, a, b)
            if s.length > 1e-8:
                v += s.normalized() * w
        return v

    # -- solving ---------------------------------------------------------
    def root_offset(self, frame, frame0, scale):
        """World-space root displacement from the 2D hip track."""
        mode = self.args.root_motion
        if mode == "none" or not self.root:
            return Vector()
        def hip2d(f):
            l, r = f["image"][self.index["left_hip"]], f["image"][self.index["right_hip"]]
            return (l[0] + r[0]) / 2, (l[1] + r[1]) / 2
        u, v = hip2d(frame)
        u0, v0 = hip2d(frame0)
        dx = (u - u0) * self.aspect
        dz = -(v - v0) if mode == "xz" else 0.0
        return Vector((dx, 0.0, dz)) * scale

    def solve(self, frame, offset):
        """Return {bone_name: posed armature-space Matrix} for one frame."""
        P = {}
        for b in self.order:
            R = b.matrix_local
            M0 = P[b.parent.name] @ (b.parent.matrix_local.inverted() @ R) if b.parent else R.copy()
            e = self.entries.get(b.name)
            if e is None:
                P[b.name] = M0
                continue
            M0rot = M0.to_quaternion()
            Rrot = R.to_quaternion()
            target = self.seg(frame, *e["dir"])
            rest = self.rest_seg(*e["dir"])
            # swing relative to the parent-posed orientation
            cur = (M0rot @ Rrot.inverted()) @ rest
            swing = cur.rotation_difference(target) @ M0rot
            rot = swing
            if e["mode"] == "frame":
                Ft = frame_matrix(target, self.twist(frame, e["twist"], False))
                Fr = frame_matrix(rest, self.twist(frame, e["twist"], True))
                if Ft is not None and Fr is not None:
                    rot = (Ft @ Fr.transposed()).to_quaternion() @ Rrot
            elif e["mode"] == "limb":
                pole = self.seg(frame, *e["pole"])
                Ft = frame_matrix(target, pole)
                Fr = frame_matrix(rest, Vector(e["pole_rest"]))
                # when the limb is nearly straight its twist is unobservable:
                # carry the previous frame's orientation forward instead
                prev = self.prev_rot.get(b.name)
                hold = swing if prev is None else \
                    (prev @ Rrot.inverted() @ rest).rotation_difference(target) @ prev
                if Ft is not None and Fr is not None:
                    bend = target.normalized().cross(pole.normalized()).length
                    w = smoothstep(0.08, 0.35, bend)
                    full = (Ft @ Fr.transposed()).to_quaternion() @ Rrot
                    if full.dot(hold) < 0:
                        full.negate()
                    # hold and full share the bone direction and differ only in twist;
                    # rate-limit that twist so depth flips in the reference don't pop
                    twist = math.degrees(hold.rotation_difference(full).angle)
                    if prev is not None and twist * w > self.args.max_twist:
                        w = self.args.max_twist / twist
                    rot = hold.slerp(full, w)
                else:
                    rot = hold
                self.prev_rot[b.name] = rot
            M = Matrix.Translation(M0.translation) @ rot.to_matrix().to_4x4()
            if b.name == self.root:
                M = Matrix.Translation(offset) @ M
            P[b.name] = M
        return P

    def joint_world_z(self, P):
        out = []
        for j in self.foot_joints:
            spec = self.mapping["joints"][j]
            b = self.arm.data.bones[spec["bone"]]
            M = P[b.name]
            p = M @ Vector((0, b.length, 0)) if spec.get("end") == "tail" else M.translation
            out.append((self.arm.matrix_world @ p).z)
        return min(out) if out else None

    def run(self, pose, args):
        self.args = args
        frames = pose["frames"]
        arm = self.arm
        scene = bpy.context.scene

        # metres-in-image -> armature units, from torso length
        def torso2d(f):
            g = lambda n: f["image"][self.index[n]]  # noqa: E731
            sx = (g("left_shoulder")[0] + g("right_shoulder")[0] - g("left_hip")[0] - g("right_hip")[0]) / 2
            sy = (g("left_shoulder")[1] + g("right_shoulder")[1] - g("left_hip")[1] - g("right_hip")[1]) / 2
            return math.hypot(sx * self.aspect, sy)
        lens = sorted(torso2d(f) for f in frames)
        rig_torso = (self.rest_point("mid_shoulder") - self.rest_point("mid_hip")).length
        rig_torso_world = (arm.matrix_world.to_3x3() @ self.rest_seg("mid_hip", "mid_shoulder")).length
        scale_world = rig_torso_world / max(1e-6, lens[len(lens) // 2])

        rest_P = {b.name: b.matrix_local.copy() for b in self.order}
        floor_z = self.joint_world_z(rest_P)
        world_to_arm = arm.matrix_world.inverted().to_3x3()

        # fps
        fps = pose["fps"]
        scene.render.fps = max(1, round(fps))
        scene.render.fps_base = scene.render.fps / fps
        scene.frame_start = 1
        scene.frame_end = len(frames)

        arm.animation_data_create()
        action = bpy.data.actions.new(args.action or f"{arm.name}_mocap")
        arm.animation_data.action = action
        pbones = arm.pose.bones
        for pb in pbones:
            pb.rotation_mode = "QUATERNION"
            pb.location = (0, 0, 0)
            pb.rotation_quaternion = (1, 0, 0, 0)

        prev_q = {}
        keyed = [b for b in self.order if b.name in self.entries]
        for k in range(0, len(frames), max(1, args.step)):
            f = frames[k]
            offset = world_to_arm @ self.root_offset(f, frames[0], scale_world)
            P = self.solve(f, offset)
            if args.floor != "none" and floor_z is not None:
                z = self.joint_world_z(P)
                dz = 0.0
                if args.floor == "lock" or (args.floor == "clamp" and z < floor_z):
                    dz = floor_z - z
                if abs(dz) > 1e-7:
                    offset = offset + world_to_arm @ Vector((0, 0, dz))
                    P = self.solve(f, offset)
            fr = k + 1
            for b in keyed:
                if b.parent:
                    M0 = P[b.parent.name] @ (b.parent.matrix_local.inverted() @ b.matrix_local)
                else:
                    M0 = b.matrix_local
                basis = M0.inverted() @ P[b.name]
                q = basis.to_quaternion().normalized()
                if b.name in prev_q and q.dot(prev_q[b.name]) < 0:
                    q.negate()
                prev_q[b.name] = q
                pb = pbones[b.name]
                pb.rotation_quaternion = q
                pb.keyframe_insert("rotation_quaternion", frame=fr, group=b.name)
                if b.name == self.root and (args.root_motion != "none" or args.floor != "none"):
                    pb.location = basis.to_translation()
                    pb.keyframe_insert("location", frame=fr, group=b.name)
        scene.frame_set(1)
        print(f"Keyed {len(keyed)} bones x {len(range(0, len(frames), max(1, args.step)))} frames "
              f"into action '{action.name}' (rig torso {rig_torso:.3f} units)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("pose")
    ap.add_argument("mapping")
    ap.add_argument("--out", required=True, help="result .blend")
    ap.add_argument("--export", default=None, help="also export .fbx/.glb")
    ap.add_argument("--armature", default=None)
    ap.add_argument("--root-motion", choices=["xz", "x", "none"], default="xz")
    ap.add_argument("--floor", choices=["clamp", "lock", "none"], default="clamp")
    ap.add_argument("--step", type=int, default=1, help="key every Nth frame")
    ap.add_argument("--action", default=None)
    ap.add_argument("--max-twist", type=float, default=12.0, help="max limb twist change per frame (deg)")
    a = ap.parse_args(C.script_args())

    C.load_model(a.model)
    mapping = C.load_json(a.mapping)
    pose = C.load_json(a.pose)
    arm = C.find_armature(a.armature or mapping.get("armature"))
    Retargeter(arm, mapping, pose).run(pose, a)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0  # no .blend1 backups
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.out), copy=True)
    print(f"Saved {a.out}")
    if a.export:
        ext = os.path.splitext(a.export)[1].lower()
        bpy.ops.object.select_all(action="DESELECT")
        arm.select_set(True)
        for o in arm.children_recursive:
            o.select_set(True)
        bpy.context.view_layer.objects.active = arm
        if ext == ".fbx":
            bpy.ops.export_scene.fbx(filepath=os.path.abspath(a.export), use_selection=True,
                                     bake_anim=True, add_leaf_bones=False)
        elif ext in (".glb", ".gltf"):
            bpy.ops.export_scene.gltf(filepath=os.path.abspath(a.export), use_selection=True,
                                      export_animations=True)
        else:
            raise SystemExit(f"Unsupported export format {ext}")
        print(f"Exported {a.export}")


main()
