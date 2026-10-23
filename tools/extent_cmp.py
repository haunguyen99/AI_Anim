"""Per-row / per-column silhouette extents, reference vs a render (tools/blender/eye_views.py), in metres on the grid.
python tools/extent_cmp.py WORK FRAME TAG [--dir work/attack/look_v4]
Side view Ref_left (+X camera): per column Y -> z range; top: per row Y -> X range; front: per row z -> X range.
Calibration from WORK/analysis.json "calibration". Tells WHERE a part is off (the IoU only tells how much)."""
import argparse, json, os
import cv2, numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work"); ap.add_argument("frame", type=int); ap.add_argument("tag"); ap.add_argument("--dir")
    a = ap.parse_args()
    d = a.dir or os.path.join(a.work, "look_v4")
    V = json.load(open(os.path.join(a.work, "refs.json")))["views"]
    cal = json.load(open(os.path.join(a.work, "analysis.json"), encoding="utf-8"))["calibration"]
    K, G = cal["px_per_m"], cal["ground_y"]
    ox = {"front": 1056.5, "left": 953.5, "top": 1056.5}
    def ref(v):
        c = cv2.VideoCapture(V[v]["path"]); c.set(1, a.frame - 1)
        return cv2.morphologyEx((c.read()[1].max(2) > 110).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0
    def anim(v): return cv2.imread(os.path.join(d, f"{a.tag}_{v}.png"), cv2.IMREAD_UNCHANGED)[:, :, 3] > 127
    def rng(arr, f):
        i = np.nonzero(arr)[0]
        return "%5.2f..%5.2f" % (f(i.min()), f(i.max())) if len(i) else "     -      "
    R, A = ref("left"), anim("left")
    print("Ref_left (+X cam): column Y -> z   ref | anim")
    for x in range(560, 1560, 50):
        f = lambda i: (G - i) / K
        print(" Y=%5.2f  %s | %s" % ((x - ox["left"]) / K, rng(R[::-1, x], lambda i: (i - (R.shape[0] - 1 - G)) / K),
                                     rng(A[::-1, x], lambda i: (i - (A.shape[0] - 1 - G)) / K)))
    R, A = ref("top"), anim("top")
    print("top: row Y -> X   ref | anim")
    for y in range(0, 620, 40):
        f = lambda i: (i - ox["top"]) / K
        print(" Y=%5.2f  %s | %s" % ((545.5 - y) / K, rng(R[y], f), rng(A[y], f)))
    R, A = ref("front"), anim("front")
    print("front: row z -> X   ref | anim")
    for z in np.arange(2.5, 0.1, -0.2):
        y = int(G - z * K); f = lambda i: (i - ox["front"]) / K
        print(" z=%4.1f  %s | %s" % (z, rng(R[y], f), rng(A[y], f)))


if __name__ == "__main__":
    main()
