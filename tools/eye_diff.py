"""Two-colour difference overlay of a render (eye_views.py RGBA) vs the reference: white = both, red = ref only
(anim is missing something there), cyan = anim only (anim has something extra). Shows WHERE the silhouette is off.
python tools/eye_diff.py WORK FRAME TAG [--dir work/boss_gaygor/attack/look_v4] [--h 360]"""
import argparse, json, os
import cv2, numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work"); ap.add_argument("frame", type=int); ap.add_argument("tag")
    ap.add_argument("--dir"); ap.add_argument("--h", type=int, default=360)
    a = ap.parse_args()
    d = a.dir or os.path.join(a.work, "look_v4")
    V = json.load(open(os.path.join(a.work, "refs.json")))["views"]
    tiles = []
    for v in ("front", "back", "left", "right", "top"):
        c = cv2.VideoCapture(V[v]["path"]); c.set(1, a.frame - 1)
        r = cv2.morphologyEx((c.read()[1].max(2) > 110).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0
        m = cv2.imread(os.path.join(d, f"{a.tag}_{v}.png"), cv2.IMREAD_UNCHANGED)[:, :, 3] > 127
        ov = np.zeros(r.shape + (3,), np.uint8)
        ov[r & m] = 255; ov[r & ~m] = (0, 0, 255); ov[m & ~r] = (255, 255, 0)
        ys, xs = np.nonzero(r | m)
        y0, y1, x0, x1 = max(ys.min() - 20, 0), ys.max() + 20, max(xs.min() - 20, 0), xs.max() + 20
        t = ov[y0:y1, x0:x1]
        t = cv2.resize(t, (int(t.shape[1] * a.h / t.shape[0]), a.h))
        cv2.putText(t, f"{v} red=ref only cyan=anim only", (5, 22), 0, 0.55, (0, 255, 0), 2)
        tiles.append(t)
    out = os.path.join(d, f"diff_f{a.frame}_{a.tag}.png")
    cv2.imwrite(out, np.hstack(tiles))
    print(out)


if __name__ == "__main__":
    main()
