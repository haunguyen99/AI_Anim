"""Overlay the projected vertices of chosen body parts (attack_pose.part_points JSON) on the reference frame, every view.
Coarse-to-fine reviewing: check the main masses (pelvis, legs, torso, head) first, then limbs, then hands/prop.
python tools/part_overlay.py WORK FRAME POINTS.json --parts pelvis,legs [--out file.png] [--h 380]
Each part gets its own colour; the reference keeps its shading so the matching part can be read under the dots."""
import argparse, json, os
import cv2, numpy as np

COL = {"pelvis": (0, 200, 255), "legs": (0, 255, 0), "leg_L": (0, 255, 0), "leg_R": (255, 160, 0), "torso": (255, 0, 255),
       "head": (0, 0, 255), "upperarm_L": (0, 255, 255), "forearm_L": (0, 160, 255), "hand_L": (0, 90, 255),
       "upperarm_R": (255, 255, 0), "forearm_R": (255, 160, 80), "hand_R": (255, 90, 160), "weapon": (200, 200, 200)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work"); ap.add_argument("frame", type=int); ap.add_argument("points")
    ap.add_argument("--parts", required=True); ap.add_argument("--out"); ap.add_argument("--h", type=int, default=380)
    ap.add_argument("--views", default="front,back,left,right,top")
    a = ap.parse_args()
    V = json.load(open(os.path.join(a.work, "refs.json")))["views"]
    P = json.load(open(a.points))
    parts = a.parts.split(",")
    tiles = []
    for v in a.views.split(","):
        c = cv2.VideoCapture(V[v]["path"]); c.set(1, a.frame - 1); ref = c.read()[1]
        m = ref.max(2) > 110
        img = (ref * 0.85).astype(np.uint8)
        allp = []
        for p in parts:
            for x, y in P[p][v]:
                xi, yi = int(x), int(y)
                if 0 <= xi < 1920 and 0 <= yi < 1080:
                    cv2.circle(img, (xi, yi), 2, COL.get(p, (255, 255, 255)), -1)
                    allp.append((xi, yi))
        ys, xs = np.nonzero(m)
        pts = np.array(allp) if allp else np.zeros((0, 2), int)
        x0 = min(xs.min(), pts[:, 0].min() if len(pts) else 1e9) - 30; x1 = max(xs.max(), pts[:, 0].max() if len(pts) else 0) + 30
        y0 = min(ys.min(), pts[:, 1].min() if len(pts) else 1e9) - 30; y1 = max(ys.max(), pts[:, 1].max() if len(pts) else 0) + 30
        x0, y0 = int(max(0, x0)), int(max(0, y0)); x1, y1 = int(min(1920, x1)), int(min(1080, y1))
        t = img[y0:y1, x0:x1]
        t = cv2.resize(t, (int(t.shape[1] * a.h / t.shape[0]), a.h))
        cv2.putText(t, f"{v}: {','.join(parts)}", (6, 22), 0, 0.6, (255, 255, 255), 2)
        tiles.append(t)
    out = a.out or os.path.join(os.path.dirname(a.points), f"parts_f{a.frame}_{'_'.join(parts)}.png")
    rows = [np.hstack(tiles[:3]), np.hstack(tiles[3:])] if len(tiles) > 3 else [np.hstack(tiles)]
    w = max(r.shape[1] for r in rows)
    cv2.imwrite(out, np.vstack([np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows]))
    print(out)


if __name__ == "__main__":
    main()
