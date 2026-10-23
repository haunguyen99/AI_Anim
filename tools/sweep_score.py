"""Score sweep renders (attack_pose.sweep) against reference silhouettes: IoU per view and mean.
python tools/sweep_score.py WORK FRAME TAG N [--views front,back,left,right,top] [--band y0,y1]
"""
import argparse, json, os
import cv2, numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work"); ap.add_argument("frame", type=int); ap.add_argument("tag"); ap.add_argument("n", type=int)
    ap.add_argument("--views", default="front,back,left,right,top"); ap.add_argument("--band")
    a = ap.parse_args()
    V = json.load(open(os.path.join(a.work, "refs.json")))["views"]
    d = os.path.join(a.work, "look_v4", "sweep")
    refs = {}
    for v in a.views.split(","):
        c = cv2.VideoCapture(V[v]["path"]); c.set(1, a.frame - 1); f = c.read()[1]
        m = cv2.morphologyEx((f.max(2) > 110).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        refs[v] = m
    res = []
    for i in range(a.n):
        s = {}
        for v, m in refs.items():
            im = cv2.imread(os.path.join(d, f"{a.tag}_{i:03d}_{v}.png"), cv2.IMREAD_UNCHANGED)
            am = (im[:, :, 3] > 127).astype(np.uint8)
            rm = cv2.resize(m, (am.shape[1], am.shape[0]), interpolation=cv2.INTER_NEAREST)
            if a.band and v != "top":
                b0, b1 = [int(int(x) * am.shape[0] / 1080) for x in a.band.split(",")]
                am = am[b0:b1]; rm = rm[b0:b1]
            s[v] = float((am & rm).sum() / max((am | rm).sum(), 1))
        s["mean"] = float(np.mean(list(s.values())))
        res.append(s)
    order = sorted(range(a.n), key=lambda i: -res[i]["mean"])
    for i in order[:10]:
        print(i, " ".join(f"{k}:{v:.3f}" for k, v in res[i].items()))
    json.dump(res, open(os.path.join(d, f"{a.tag}_scores.json"), "w"))


if __name__ == "__main__":
    main()
