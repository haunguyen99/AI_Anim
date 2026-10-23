# Refine the head channels of solved keys against the head silhouette in the side/back views.
# Run after solve_keys.py (same namespace):  HEADF = [37, 45]; exec(open(r".../head_refine.py").read())
import numpy as np

HSUB = ["head_yaw", "head_pitch", "head_roll", "twist"]
HSIG = {"head_yaw": 25.0, "head_pitch": 20.0, "head_roll": 10.0, "twist": 6.0}
HIDX = [PARAMS.index(k) for k in HSUB]  # noqa: F821
for _f in HEADF:  # noqa: F821
    pt = np.array(SOL[_f], float)  # noqa: F821
    apply(pt)  # noqa: F821
    c0, rois = head_sil(_f)  # noqa: F821
    rois = {v: (r[0] - 40, r[1] - 40, r[2] + 40, r[3] + 40) for v, r in rois.items()}

    def cost(p):
        apply(p)  # noqa: F821
        c, _ = head_sil(_f, roi=rois)  # noqa: F821
        return c + 0.5 * sum(((p[i] - pt[i]) / HSIG[k]) ** 2 for k, i in zip(HSUB, HIDX))

    p = pt.copy(); best = cost(p); start = best
    for step in (8.0, 4.0, 2.0, 1.0):
        improved = True
        while improved:
            improved = False
            for i in HIDX:
                for sgn in (1, -1):
                    q = p.copy(); q[i] += sgn * step
                    c = cost(q)
                    if c < best - 1e-3:
                        p, best, improved = q, c, True
                        break
    SOL[_f] = p  # noqa: F821
    print(f"f{_f:3d} head sil {start:.2f} -> {best:.2f}  " + " ".join(f"{k}={pt[i]:+.0f}->{p[i]:+.0f}" for k, i in zip(HSUB, HIDX)))
