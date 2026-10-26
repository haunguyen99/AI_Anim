"""Measure how closely the keyed rig follows the reference landmarks.

blender -b -P tools/blender/score_motion.py -- RESULT_BLEND POSE_JSON MAPPING_JSON --out score.json

For every mapped bone whose dir endpoints are real rig joints, compares the
world-space direction of the posed segment with the reference segment per frame
(angle in degrees). Reports mean / p95 / max per bone and the worst frames.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bl_common as C  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("blend")
    ap.add_argument("pose")
    ap.add_argument("mapping")
    ap.add_argument("--out", required=True)
    ap.add_argument("--armature", default=None)
    a = ap.parse_args(C.script_args())

    C.load_model(a.blend)
    mapping = C.load_json(a.mapping)
    pose = C.load_json(a.pose)
    arm = C.find_armature(a.armature or mapping.get("armature"))
    idx = {n: i for i, n in enumerate(pose["landmark_names"])}
    joints = {k: v for k, v in mapping["joints"].items() if "bone" in v}

    def lm(f, name):
        if name in idx:
            return Vector(f["world"][idx[name]])
        parts = C.VIRTUAL[name]
        return sum((lm(f, p) for p in parts), Vector()) / len(parts)

    def jp(name):
        if name in joints:
            spec = joints[name]
            pb = arm.pose.bones[spec["bone"]]
            return arm.matrix_world @ (pb.tail if spec.get("end") == "tail" else pb.head)
        parts = C.VIRTUAL.get(name)
        if parts and all(p in joints for p in parts):
            return sum((jp(p) for p in parts), Vector()) / len(parts)
        return None

    checks = [(e["bone"], e["dir"]) for e in mapping["bones"]]
    errs = {b: [] for b, _ in checks}
    frames = pose["frames"]
    step = max(1, len(frames) // 300)
    for k in range(0, len(frames), step):
        bpy.context.scene.frame_set(k + 1)
        f = frames[k]
        for bone, (p, q) in checks:
            A, B = jp(p), jp(q)
            if A is None or B is None:
                continue
            r = B - A
            t = lm(f, q) - lm(f, p)
            if r.length < 1e-6 or t.length < 1e-6:
                continue
            errs[bone].append((math.degrees(r.angle(t)), k + 1))

    report = {}
    for bone, vals in errs.items():
        if not vals:
            continue
        ang = sorted(v for v, _ in vals)
        worst = sorted(vals, reverse=True)[:3]
        report[bone] = {
            "mean": round(sum(ang) / len(ang), 2),
            "p95": round(ang[int(len(ang) * 0.95) - 1 if len(ang) > 1 else 0], 2),
            "max": round(ang[-1], 2),
            "worst_frames": [fr for _, fr in worst],
        }
    allv = [v["mean"] for v in report.values()]
    summary = {"mean_deg": round(sum(allv) / max(1, len(allv)), 2), "bones": report}
    C.save_json(a.out, summary)
    print(f"Mean direction error {summary['mean_deg']} deg over {len(report)} bones")
    for b, v in sorted(report.items(), key=lambda kv: -kv[1]["mean"])[:6]:
        print(f"  {b:24s} mean {v['mean']:6.2f}  p95 {v['p95']:6.2f}  max {v['max']:6.2f}  worst frames {v['worst_frames']}")


main()
