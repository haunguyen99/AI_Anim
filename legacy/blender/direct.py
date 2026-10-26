# "Director" tools that edit curves instead of re-keying (docs/pipeline_v2.md step 5).
#   exec(open(ROOT + r"/legacy/blender/direct.py").read())
#   offset_bone(obj, "Chest_M", 2)          # delay a bone by 2 frames, cyclic over the loop (first key == last key)
#   scale_amp(obj, "Scapula_R", 1.2)        # scale the motion of a bone around its mean pose (loc + rot)
import bpy
import numpy as np


def _curves(obj, bone):
    act = obj.animation_data.action
    return [fc for fc in act.fcurves if fc.data_path.startswith(f'pose.bones["{bone}"].')]


def _loop_range(obj):
    xs = [k.co[0] for fc in obj.animation_data.action.fcurves for k in fc.keyframe_points]
    return int(min(xs)), int(max(xs))


def offset_bone(obj, bone, frames):
    """Shift every key of BONE by FRAMES (later if > 0), wrapping around the loop f0..f1 (value at f1 == f0).
    Keys keep their exact values; new boundary keys at f0/f1 are sampled from the shifted cyclic curve."""
    if not frames:
        return
    f0, f1 = _loop_range(obj); per = f1 - f0
    for fc in _curves(obj, bone):
        samples = {f: fc.evaluate(f) for f in range(f0, f1 + 1)}
        keys = [(k.co[0], k.co[1]) for k in fc.keyframe_points if k.co[0] < f1]          # drop the duplicate end key
        new = {}
        for x, y in keys:
            nx = (x - f0 + frames) % per + f0
            new[round(nx, 3)] = y
        src = (f0 - frames - f0) % per + f0                      # value now at f0 came from frame f0 - frames
        v0 = fc.evaluate(src) if src not in samples else samples[int(src)]
        new[f0] = v0; new[f1] = v0
        while fc.keyframe_points:
            fc.keyframe_points.remove(fc.keyframe_points[0])
        for x in sorted(new):
            kp = fc.keyframe_points.insert(x, new[x], options={"FAST"})
            kp.interpolation = "BEZIER"; kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        fc.update()


def scale_amp(obj, bone, k):
    for fc in _curves(obj, bone):
        ys = [kp.co[1] for kp in fc.keyframe_points]
        m = float(np.mean(ys))
        for kp in fc.keyframe_points:
            kp.co[1] = m + (kp.co[1] - m) * k
        fc.update()


def match_seam(obj):
    """Make every curve leave f0 with the slope it arrives at f1 (loop seam): aligned handles on the two end keys."""
    f0, f1 = _loop_range(obj); n = 0
    for fc in obj.animation_data.action.fcurves:
        kps = fc.keyframe_points
        if len(kps) < 3:
            continue
        a, b = kps[0], kps[-1]
        if abs(a.co[0] - f0) > 1e-3 or abs(b.co[0] - f1) > 1e-3:
            continue
        # slope from the neighbours across the seam (central difference on the cyclic curve)
        prev_y, next_y = kps[-2].co, kps[1].co
        dx = (f1 - prev_y[0]) + (next_y[0] - f0)
        slope = (next_y[1] - prev_y[1]) / dx if dx else 0.0
        for kp, side in ((a, "right"), (b, "left")):
            kp.handle_left_type = kp.handle_right_type = "ALIGNED"
        hl = (b.co[0] - prev_y[0]) / 3.0; hr = (next_y[0] - a.co[0]) / 3.0
        a.handle_right = (a.co[0] + hr, a.co[1] + slope * hr); a.handle_left = (a.co[0] - hl, a.co[1] - slope * hl)
        b.handle_left = (b.co[0] - hl, b.co[1] - slope * hl); b.handle_right = (b.co[0] + hr, b.co[1] + slope * hr)
        fc.update(); n += 1
    return n
