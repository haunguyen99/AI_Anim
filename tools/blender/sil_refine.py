# Refine only the torso twist / lean and the weapon pivot of solved keys against the reference silhouettes.
# Run after solve_keys.py in the same exec namespace (needs apply, sil_residual, PARAMS, SOL, PX_CM):
#   REFINE = [85, 95]; exec(open(ROOT + r"/tools/blender/sil_refine.py").read())
# Pattern search on a few channels, everything else stays at the tracking solution; a soft pull back
# to the tracking value (SIGMA deg) keeps the head turn, breath and arm drag the tracking measured.
import numpy as np

SUB = globals().get("SUB", ["lean", "twist", "wpn_x", "wpn_y", "wpn_z"])
SIGMA = {"lean": 4.0, "twist": 8.0, "wpn_x": 6.0, "wpn_y": 6.0, "wpn_z": 6.0, "scap_L": 6.0, "scap_R": 6.0,
         "head_yaw": 8.0, "head_pitch": 8.0, "armR_x": 8.0, "armR_z": 8.0, "elbowR": 8.0, "root_z": 3.0, "root_y": 3.0,
         "wpn_tx": 15.0, "wpn_ty": 15.0, "wpn_tz": 15.0,
         "grip_slide": 15.0, "grip_roll": 40.0, "pole_swing": 60.0, "neck_side": 10.0,
         "protract": 10.0, "root_yaw": 15.0, "root_pitch": 12.0, "twist": 8.0}
WPN_W = globals().get("WPN_W", 1.0)
ARM_W = globals().get("ARM_W", 0.0)   # weight on left-arm vertices outside the reference silhouette
IDX = [PARAMS.index(k) for k in SUB]  # noqa: F821


def sil_cost(p, p_track, f):
    apply(p)  # noqa: F821
    c = float(np.mean(sil_residual(f) * PX_CM)) + WPN_W * weapon_out(f)  # noqa: F821
    if ARM_W:
        c += ARM_W * part_out(f, "armL", ("Shoulder_L", "Elbow_L", "Wrist_L", "*_L"))  # noqa: F821
    c += sum(((p[i] - p_track[i]) / SIGMA[k]) ** 2 for k, i in zip(SUB, IDX)) * 0.5
    return c


SIL_LOG = {}
for _f in REFINE:  # noqa: F821
    pt = np.array(SOL[_f], float)  # noqa: F821
    p = pt.copy()
    best = sil_cost(p, pt, _f)
    start = best
    for step in globals().get("STEPS", (4.0, 2.0, 1.0)):
        improved = True
        while improved:
            improved = False
            for i in IDX:
                for sgn in (1, -1):
                    q = p.copy(); q[i] += sgn * step
                    c = sil_cost(q, pt, _f)
                    if c < best - 1e-3:
                        p, best, improved = q, c, True
                        break
    SOL[_f] = p  # noqa: F821
    SIL_LOG[_f] = (start, best)
    apply(p)  # noqa: F821
    print(f"f{_f:3d} weapon out {weapon_out(_f):.1f}px  sil cost {start:.2f} -> {best:.2f}  " + " ".join(f"{k}={p[i]:+.1f}" for k, i in zip(SUB, IDX)))
