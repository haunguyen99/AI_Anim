"""Compare body-part motion of the keyed animation with the reference (optical flow per region).

Renders the model (textured) through the calibrated cameras, measures the median flow of each
region relative to the first frame - exactly as for the reference - and prints/plots both curves.
It compares timing and amplitude of parts (chest, head, hips, weapon...), not pixels.

python tools/motion_compare.py WORK --frames 1-31 --regions regions.json [--views front,left]
"""
import argparse, json, os, subprocess, sys
import cv2, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from keyanim import run_blender, load, read_frame  # noqa: E402


def flows(imgs, box, px_per_cm):
    x0, y0, x1, y1 = box
    g0 = imgs[0][y0 - 40:y1 + 40, x0 - 40:x1 + 40]
    dx, dy = [], []
    for im in imgs:
        fl = cv2.calcOpticalFlowFarneback(g0, im[y0 - 40:y1 + 40, x0 - 40:x1 + 40], None, 0.5, 3, 21, 3, 5, 1.1, 0)
        fl = fl[40:-40, 40:-40]
        dx.append(np.median(fl[..., 0]) / px_per_cm)
        dy.append(np.median(fl[..., 1]) / px_per_cm)
    return np.array(dx), np.array(dy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work"); ap.add_argument("--frames", default="1-31")
    ap.add_argument("--regions", required=True); ap.add_argument("--views", default=None)
    ap.add_argument("--ref-offset", type=int, default=0, help="reference frame = clip frame + offset")
    a = ap.parse_args()
    s, e = [int(x) for x in a.frames.split("-")]
    frames = list(range(s, e + 1))
    regions = load(a.regions)
    views = a.views.split(",") if a.views else list(regions)
    refs = load(os.path.join(a.work, "refs.json"))
    model = load(os.path.join(a.work, "project.json"))["model"]
    run_blender("key_pose.py", "key", model, "--work", a.work)
    run_blender("key_pose.py", "render", "--work", a.work, "--frames", ",".join(map(str, frames)),
                "--views", ",".join(views), "--scale", "1.0", "--textured")
    cams = load(os.path.join(a.work, "cameras.json"))
    report = {}
    plot_rows = []
    for v in views:
        info = refs["views"][v]
        k_px = (cams[v]["ground_px"] - cams[v]["top_px"]) / load(os.path.join(a.work, "controls.json"))["character_height_m"] / 100
        ref = [cv2.cvtColor(read_frame(info["path"], f - 1 + a.ref_offset), cv2.COLOR_BGR2GRAY) for f in frames]
        mod = [cv2.cvtColor(cv2.imread(os.path.join(a.work, "look", f"render_{v}_{f:05d}.png")), cv2.COLOR_BGR2GRAY) for f in frames]
        mod = [cv2.resize(m, (info["width"], info["height"])) for m in mod]
        for name, box in regions[v].items():
            rx, ry = flows(ref, box, k_px)
            mx, my = flows(mod, box, k_px)
            report[f"{v}/{name}"] = {"ref_dy": ry.round(2).tolist(), "mod_dy": my.round(2).tolist(),
                                     "ref_dx": rx.round(2).tolist(), "mod_dx": mx.round(2).tolist()}
            def pk(arr):
                i = int(np.argmax(np.abs(arr)))
                return f"{arr[i]:+5.1f}cm@f{frames[i]}"
            print(f"{v:5s} {name:8s}  up/down: ref {pk(-ry)}  model {pk(-my)}   fwd/back: ref {pk(rx)}  model {pk(mx)}"
                  f"   rms diff {np.sqrt(np.mean((ry - my) ** 2 + (rx - mx) ** 2)):.1f}cm")
            # small plot: ref (white) vs model (orange), vertical motion
            W, H = 300, 90
            img = np.full((H, W, 3), 30, np.uint8)
            sc = H / 2 / max(2.0, np.abs(np.r_[ry, my]).max())
            for arr, col in ((ry, (255, 255, 255)), (my, (0, 160, 255))):
                pts = [(int(i * (W - 1) / (len(arr) - 1)), int(H / 2 + arr[i] * sc)) for i in range(len(arr))]
                cv2.polylines(img, [np.array(pts)], False, col, 2)
            cv2.putText(img, f"{v} {name} (down +)", (4, 12), 0, 0.4, (200, 200, 200), 1)
            plot_rows.append(img)
    json.dump(report, open(os.path.join(a.work, "motion_compare.json"), "w"))
    cols = 2
    while len(plot_rows) % cols:
        plot_rows.append(np.zeros_like(plot_rows[0]))
    sheet = np.vstack([np.hstack(plot_rows[i:i + cols]) for i in range(0, len(plot_rows), cols)])
    cv2.imwrite(os.path.join(a.work, "look", "motion_compare.png"), sheet)


if __name__ == "__main__":
    main()
