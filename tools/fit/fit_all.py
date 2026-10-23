"""Fit every frame in parallel: split the clip into chunks, run fitpose.py on each chunk in
its own process (warm-started inside the chunk), then merge into fit_basis.npy.

python tools/fit/fit_all.py work/idle [--jobs 12] [--views front,back,left,right]
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--views", default="front,back,left,right")
    ap.add_argument("--scale", type=float, default=0.25)
    ap.add_argument("--out", default="fit_basis.npy")
    ap.add_argument("--extra", default="", help="extra args passed to fitpose.py")
    a = ap.parse_args()

    n = np.load(os.path.join(a.work, "rig_np.npz"))["basis"].shape[0]
    bounds = np.linspace(0, n, a.jobs + 1).astype(int)
    procs, outs = [], []
    t0 = time.time()
    os.makedirs(os.path.join(a.work, "fit_chunks"), exist_ok=True)
    for j in range(a.jobs):
        s, e = bounds[j] + 1, bounds[j + 1]
        if s > e:
            continue
        out = f"fit_chunks/c{j:02d}.npy"
        for f in (out, out.replace(".npy", "_x.npy")):
            if os.path.exists(os.path.join(a.work, f)):
                os.remove(os.path.join(a.work, f))
        log = open(os.path.join(a.work, "fit_chunks", f"c{j:02d}.log"), "w")
        procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, "fitpose.py"), a.work, "--frames", f"{s}-{e}",
                                       "--views", a.views, "--scale", str(a.scale), "--out", out,
                                       "--log", f"fit_chunks/c{j:02d}.json", *a.extra.split()],
                                      stdout=log, stderr=subprocess.STDOUT))
        outs.append((s, e, out))
    for p in procs:
        p.wait()
    result = None
    logs = []
    for s, e, out in outs:
        r = np.load(os.path.join(a.work, out))
        if result is None:
            result = r.copy()
        result[s - 1:e] = r[s - 1:e]
        logs += json.load(open(os.path.join(a.work, out.replace(".npy", ".json").replace("fit_chunks/c", "fit_chunks/c"))))["log"]
    np.save(os.path.join(a.work, a.out), result)
    logs.sort(key=lambda r: r["frame"])
    b = np.mean([r["iou_before"] for r in logs])
    f = np.mean([r["iou_after"] for r in logs])
    json.dump({"log": logs}, open(os.path.join(a.work, "fit_log.json"), "w"), indent=1)
    print(f"{len(logs)} frames in {time.time() - t0:.0f}s: mean silhouette IoU {b:.3f} -> {f:.3f}")


if __name__ == "__main__":
    main()
