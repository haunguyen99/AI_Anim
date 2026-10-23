"""Eye-keying CLI: Claude looks at multi-view reference videos of the character
and keys the 3D model so it matches them.

  python tools/keyanim.py prep    --work W --view front=front.mp4 --view left=left.mp4 [...]
  python tools/keyanim.py ref     --work W --frames 1,40          (reference frames, all views, with pixel rulers)
  python tools/keyanim.py calib   --work W --view front --top 112 --ground 1010 --center 640
  python tools/keyanim.py inspect --work W MODEL                  (rig.json, mapping.json, controls.json)
  python tools/keyanim.py look    --work W --frames 1,40 [--views front,left]
                                  (builds anim.blend from keys.json, overlays the model on the reference)
  python tools/keyanim.py export  --work W --out W/result.fbx
  python tools/keyanim.py video   --work W                        (every frame, all views: compare.mp4)
  python tools/keyanim.py view    --work W                        (GLB + refs for the 3D web viewer, tools/viewer)

Views: front, back, left, right (camera looks at that side of the character).
Work folder: refs.json, sheets/, cameras.json, rig.json, mapping.json, controls.json,
keys.json (the animation, edited by Claude), anim.blend, look/.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BL = os.path.join(ROOT, "tools", "blender")
DEFAULT_BLENDER = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
VIEWS = ("front", "back", "left", "right")

SEGS = [("left_shoulder", "right_shoulder"), ("left_hip", "right_hip"),
        ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip")]
for _s in ("left", "right"):
    SEGS += [(f"{_s}_shoulder", f"{_s}_elbow"), (f"{_s}_elbow", f"{_s}_wrist"), (f"{_s}_wrist", f"{_s}_hand"),
             (f"{_s}_hip", f"{_s}_knee"), (f"{_s}_knee", f"{_s}_ankle"), (f"{_s}_ankle", f"{_s}_toe")]


# ---------------------------------------------------------------- helpers
def p(work, *names):
    return os.path.join(work, *names)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)


def blender_exe():
    exe = os.environ.get("BLENDER") or (DEFAULT_BLENDER if os.path.exists(DEFAULT_BLENDER) else shutil.which("blender"))
    if not exe:
        sys.exit("Blender not found: set the BLENDER environment variable.")
    return exe


def run_blender(script, *args):
    cmd = [blender_exe(), "-b", "--factory-startup", "-noaudio", "-P", os.path.join(BL, script), "--", *map(str, args)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    keep = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith(
        ("Blender ", "Read ", "Fra:", "Saved: ", "Time:", "FBX ", "  ", "(bpy", "Info:", "export ", "Import"))]
    if keep:
        print("\n".join(keep[-30:]))
    if r.returncode != 0 or "Traceback" in r.stdout or "Error:" in r.stdout:
        print(r.stdout[-3000:], r.stderr[-3000:], file=sys.stderr)
        sys.exit(f"Blender step '{script}' failed")


def read_frame(path, idx):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, img = cap.read()
    cap.release()
    return img if ok else None


def ruler(img, scale=1.0, box=(0, 0), step=None):
    """Pixel rulers on the left and top edges, labelled in ORIGINAL reference pixels.
    box = (x0, y0) of the crop the image was cut from."""
    h, w = img.shape[:2]
    ox, oy = box[0], box[1]
    if step is None:  # ~10-14 labelled ticks across the visible span
        span = h / scale
        step = next(s for s in (5, 10, 25, 50, 100, 200) if span / s <= 28)
    for y0 in range(int(oy // step * step), int(oy + h / scale) + 1, step):
        y = int((y0 - oy) * scale)
        if y < 0:
            continue
        big = y0 % (step * 2) == 0
        cv2.line(img, (0, y), (14 if big else 7, y), (0, 255, 255), 1)
        if big:
            cv2.putText(img, str(y0), (16, y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
    for x0 in range(int(ox // step * step), int(ox + w / scale) + 1, step):
        x = int((x0 - ox) * scale)
        if x < 30:
            continue
        big = x0 % (step * 2) == 0
        cv2.line(img, (x, 0), (x, 14 if big else 7), (0, 255, 255), 1)
        if big:
            cv2.putText(img, str(x0), (x - 10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
    return img


def crop_box(info, cal, crop):
    """Region of the reference to show: explicit --crop, else around the calibrated character."""
    W, H = info["width"], info["height"]
    if crop:
        x0, y0, x1, y1 = [int(float(v)) for v in crop.split(",")]
    elif cal:
        h = cal["ground_px"] - cal["top_px"]
        x0, x1 = cal["center_px"] - 0.85 * h, cal["center_px"] + 0.85 * h
        y0, y1 = cal["top_px"] - 0.45 * h, cal["ground_px"] + 0.12 * h
    else:
        return 0, 0, W, H
    return max(0, int(x0)), max(0, int(y0)), min(W, int(x1)), min(H, int(y1))


def label(img, text):
    cv2.putText(img, text, (8, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3)
    cv2.putText(img, text, (8, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    return img


def fit_h(img, h):
    s = h / img.shape[0]
    return cv2.resize(img, (int(img.shape[1] * s), h)), s


def grid_lines(img, cal, s, box=(0, 0)):
    """Ground, head-top and 10% height lines from the calibration."""
    if not cal:
        return img
    g, t = (cal["ground_px"] - box[1]) * s, (cal["top_px"] - box[1]) * s
    c = (cal["center_px"] - box[0]) * s
    for i in range(11):
        y = int(g + (t - g) * i / 10)
        cv2.line(img, (0, y), (img.shape[1], y), (90, 90, 255) if i in (0, 10) else (120, 120, 120), 1)
    cv2.line(img, (int(c), 0), (int(c), img.shape[0]), (120, 120, 120), 1)
    return img


# ---------------------------------------------------------------- commands
def cmd_prep(a):
    views = {}
    for spec in a.view:
        name, path = spec.split("=", 1)
        if name not in VIEWS:
            sys.exit(f"Unknown view '{name}', use one of {VIEWS}")
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            sys.exit(f"Cannot open {path}")
        views[name] = {"path": os.path.abspath(path), "fps": cap.get(cv2.CAP_PROP_FPS) or 30.0,
                       "frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                       "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}
        cap.release()
    counts = {v["frames"] for v in views.values()}
    fps = list(views.values())[0]["fps"]
    if len(counts) > 1:
        print(f"WARNING: views have different frame counts {sorted(counts)}; using the shortest")
    n = min(counts)

    # motion energy per frame (all views) -> key suggestions at pauses / turning points
    energy = np.zeros(n)
    sheets_dir = p(a.work, "sheets")
    os.makedirs(sheets_dir, exist_ok=True)
    for name, v in views.items():
        cap = cv2.VideoCapture(v["path"])
        prev, thumbs = None, []
        for k in range(n):
            ok, img = cap.read()
            if not ok:
                break
            small = cv2.cvtColor(cv2.resize(img, (160, int(160 * v["height"] / v["width"]))), cv2.COLOR_BGR2GRAY)
            if prev is not None:
                energy[k] += np.abs(small.astype(np.float32) - prev).mean()
            prev = small.astype(np.float32)
            if k % a.step == 0 or k == n - 1:
                t, _ = fit_h(img, 220)
                thumbs.append(label(t, f"{k + 1}"))
        cap.release()
        cols = 10
        while len(thumbs) % cols:
            thumbs.append(np.zeros_like(thumbs[0]))
        sheet = np.vstack([np.hstack(thumbs[i:i + cols]) for i in range(0, len(thumbs), cols)])
        if sheet.shape[1] > 2400:
            sheet = cv2.resize(sheet, (2400, int(sheet.shape[0] * 2400 / sheet.shape[1])))
        cv2.imwrite(p(sheets_dir, f"{name}.png"), sheet)
    energy[0] = energy[1] if n > 1 else 0
    k = np.ones(5) / 5
    sm = np.convolve(np.pad(energy, 2, mode="edge"), k, mode="valid")
    cand = [i for i in range(1, n - 1) if sm[i] <= sm[i - 1] and sm[i] <= sm[i + 1]]
    cand.sort(key=lambda i: sm[i])
    picks = [0, n - 1]
    for i in cand:
        if all(abs(i - j) >= a.min_gap for j in picks):
            picks.append(i)
    picks = sorted(picks)
    refs = {"fps": fps, "frame_count": n, "views": views,
            "key_suggestions": [i + 1 for i in picks],
            "motion": [round(float(x), 3) for x in sm]}
    save(p(a.work, "refs.json"), refs)
    print(f"{len(views)} views, {n} frames @ {fps:.2f} fps. Sheets in {sheets_dir}")
    print(f"Suggested keyframes (pauses / turning points): {refs['key_suggestions']}")


def cmd_ref(a):
    refs = load(p(a.work, "refs.json"))
    cams = load(p(a.work, "cameras.json")) if os.path.exists(p(a.work, "cameras.json")) else {}
    views = a.views.split(",") if a.views else list(refs["views"])
    out = p(a.work, "look")
    os.makedirs(out, exist_ok=True)
    for fr in [int(x) for x in a.frames.split(",")]:
        row = []
        for v in views:
            info = refs["views"][v]
            img = read_frame(info["path"], fr - 1)
            box = crop_box(info, cams.get(v), a.crop)
            img, s = fit_h(img[box[1]:box[3], box[0]:box[2]], a.height)
            grid_lines(img, cams.get(v), s, box)
            row.append(label(ruler(img, s, box), f"{v}  frame {fr}"))
        path = p(out, f"ref_{fr:05d}.png")
        cv2.imwrite(path, np.hstack(row))
        print(path)


def cmd_calib(a):
    path = p(a.work, "cameras.json")
    cams = load(path) if os.path.exists(path) else {}
    cams[a.view] = {"top_px": a.top, "ground_px": a.ground, "center_px": a.center}
    save(path, cams)
    print(f"{a.view}: head top y={a.top}, ground y={a.ground}, body centre x={a.center}")


def cmd_inspect(a):
    os.makedirs(a.work, exist_ok=True)
    save(p(a.work, "project.json"), {"model": os.path.abspath(a.model)})
    run_blender("inspect_rig.py", os.path.abspath(a.model), "--rig-out", p(a.work, "rig.json"),
                "--map-out", p(a.work, "mapping.auto.json"))
    if not os.path.exists(p(a.work, "mapping.json")) or a.force:
        shutil.copy(p(a.work, "mapping.auto.json"), p(a.work, "mapping.json"))
    run_blender("key_pose.py", "setup", os.path.abspath(a.model), "--work", a.work)
    keys = p(a.work, "keys.json")
    if not os.path.exists(keys):
        refs = load(p(a.work, "refs.json")) if os.path.exists(p(a.work, "refs.json")) else {"fps": 30, "frame_count": 1}
        save(keys, {"fps": refs["fps"], "frame_count": refs["frame_count"], "interpolation": "BEZIER",
                    "keys": {"1": {"bones": {}, "root": {"loc": [0, 0, 0]}}}})
        print(f"Created empty {keys}")


def build(a, export=None):
    model = load(p(a.work, "project.json"))["model"]
    args = ["key", model, "--work", a.work]
    if export:
        args += ["--export", os.path.abspath(export)]
    run_blender("key_pose.py", *args)


def overlay_tile(a, refs, cams, v, fr, h, scale):
    """[reference + model outline + skeleton | model rendered solid], same camera and crop."""
    info = refs["views"][v]
    ref = read_frame(info["path"], fr - 1)
    if ref is None:
        ref = np.zeros((info["height"], info["width"], 3), np.uint8)
    ren = cv2.imread(p(a.work, "look", f"render_{v}_{fr:05d}.png"), cv2.IMREAD_UNCHANGED)
    ren = cv2.resize(ren, (info["width"], info["height"]))
    alpha = ren[:, :, 3]
    solid = np.full_like(ref, 70)
    am = (alpha.astype(np.float32) / 255.0)[:, :, None]
    solid = (solid * (1 - am) + ren[:, :, :3] * am).astype(np.uint8)
    over = ref.copy()
    cnts, _ = cv2.findContours((alpha > 100).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(over, cnts, -1, (255, 255, 0), 2)
    joints = load(p(a.work, "look", f"joints_{v}_{fr:05d}.json"))
    pts = {k: (int(x * info["width"]), int(y * info["height"])) for k, (x, y) in joints.items()}
    for img in (over, solid):
        for s_, e in SEGS:
            if s_ in pts and e in pts:
                col = (255, 200, 0) if s_.startswith("left") else (255, 0, 255) if s_.startswith("right") else (255, 255, 255)
                cv2.line(img, pts[s_], pts[e], col, 2)
    box = crop_box(info, cams.get(v), getattr(a, "crop", None))
    over_s, s = fit_h(over[box[1]:box[3], box[0]:box[2]], h)
    solid_s, _ = fit_h(solid[box[1]:box[3], box[0]:box[2]], h)
    grid_lines(over_s, cams.get(v), s, box)
    grid_lines(solid_s, cams.get(v), s, box)
    return np.hstack([label(ruler(over_s, s, box), f"{v} ref+outline f{fr}"),
                      label(ruler(solid_s, s, box), f"{v} model f{fr}")])


def render(a, frames, views):
    run_blender("key_pose.py", "render", "--work", a.work, "--frames", ",".join(map(str, frames)),
                "--views", ",".join(views), "--scale", a.scale)


def cmd_look(a):
    refs = load(p(a.work, "refs.json"))
    cams = load(p(a.work, "cameras.json"))
    views = a.views.split(",") if a.views else [v for v in refs["views"] if v in cams]
    frames = [int(x) for x in a.frames.split(",")]
    build(a)
    render(a, frames, views)
    for fr in frames:
        rows = [overlay_tile(a, refs, cams, v, fr, a.height, a.scale) for v in views]
        wmax = max(r.shape[1] for r in rows)
        rows = [np.pad(r, ((0, 0), (0, wmax - r.shape[1]), (0, 0))) for r in rows]
        img = np.vstack(rows) if a.stack == "rows" else np.hstack(rows)
        path = p(a.work, "look", f"look_{fr:05d}.png")
        cv2.imwrite(path, img)
        print(path)


def cmd_export(a):
    build(a, export=a.out)


def cmd_view(a):
    """Export the animation for the 3D web viewer (tools/viewer) and register the job."""
    work = os.path.abspath(a.work)
    keys0 = load(p(work, "keys.json"))
    if a.fast and keys0.get("bake") and os.path.exists(p(work, "anim.glb")):
        # per-frame fit: write the animation straight into the existing GLB (no Blender)
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "fit", "glb_bake.py"), work,
                        "--basis", keys0["bake"], "--out", "anim.glb"], check=True)
    else:
        build(a, export=p(work, "anim.glb"))
    refs = load(p(work, "refs.json")) if os.path.exists(p(work, "refs.json")) else {"views": {}}
    keys = load(p(work, "keys.json"))
    web = p(work, "web")
    os.makedirs(web, exist_ok=True)
    ref_urls = {}
    for v, info in refs.get("views", {}).items():
        out = p(web, f"{v}.mp4")
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(info["path"]):
            if not shutil.which("ffmpeg"):
                print("ffmpeg not found: reference videos will not show in the viewer")
                break
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", info["path"], "-an", "-vf", "scale=-2:720",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-g", "1",
                            "-movflags", "+faststart", out], check=True)
        ref_urls[v] = f"web/{v}.mp4"
    # calibrated reference cameras for the viewer's overlay mode, in glTF axes (x, z, -y)
    cams_gl = {}
    if os.path.exists(p(work, "rig_np.json")):
        g = lambda v: [v[0], v[2], -v[1]]  # noqa: E731
        for v, c in load(p(work, "rig_np.json"))["cameras"].items():
            cams_gl[v] = {"pos": g(c["pos"]), "right": g(c["right"]), "up": g(c["up"]), "dir": g(c["dir"]),
                          "k": c["k"], "W": c["W"], "H": c["H"]}
    cals = load(p(work, "cameras.json")) if os.path.exists(p(work, "cameras.json")) else {}
    for v, c in cams_gl.items():
        if v in cals:
            c["box"] = crop_box(refs["views"][v], cals[v], None)
    name = os.path.basename(work.rstrip("/\\"))
    save(p(work, "viewer.json"), {
        "name": name, "fps": keys.get("fps", 30), "frame_count": keys.get("frame_count", 1),
        "glb": "anim.glb", "refs": ref_urls, "keys": sorted(int(f) for f in keys["keys"]),
        "model": os.path.basename(load(p(work, "project.json"))["model"]),
        "cameras": cams_gl,
        "loop": bool(keys0.get("loop", True)),
    })
    # job list for the viewer's dropdown (all work/* folders with a viewer.json)
    root = os.path.dirname(work)
    jobs = sorted(d for d in os.listdir(root) if os.path.exists(p(root, d, "viewer.json")))
    save(p(root, "index.json"), {"jobs": jobs})
    rel = os.path.relpath(work, ROOT).replace("\\", "/")
    print(f"Viewer ready: start the server (python -m http.server {a.port} in {ROOT}) and open")
    print(f"  http://localhost:{a.port}/tools/viewer/?job={rel}")


def cmd_video(a):
    refs = load(p(a.work, "refs.json"))
    cams = load(p(a.work, "cameras.json"))
    views = [v for v in refs["views"] if v in cams]
    n = refs["frame_count"]
    build(a)
    render(a, list(range(1, n + 1)), views)
    out = p(a.work, "compare.mp4")
    vw = None
    for fr in range(1, n + 1):
        img = np.hstack([overlay_tile(a, refs, cams, v, fr, a.height, a.scale) for v in views])
        if vw is None:
            vw = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*"mp4v"), refs["fps"], (img.shape[1], img.shape[0]))
        vw.write(img)
    vw.release()
    for f in os.listdir(p(a.work, "look")):
        if f.startswith(("render_", "joints_")):
            os.remove(p(a.work, "look", f))
    if shutil.which("ffmpeg"):
        tmp = out + ".h264.mp4"
        if subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-c:v", "libx264",
                           "-pix_fmt", "yuv420p", "-crf", "23", tmp]).returncode == 0:
            os.replace(tmp, out)
    print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("prep"); q.add_argument("--work", required=True)
    q.add_argument("--view", action="append", required=True, help="name=path, e.g. front=front.mp4")
    q.add_argument("--step", type=int, default=5, help="frames between timeline thumbnails")
    q.add_argument("--min-gap", type=int, default=6, help="min frames between suggested keys")

    q = sub.add_parser("ref"); q.add_argument("--work", required=True)
    q.add_argument("--frames", required=True); q.add_argument("--views", default=None)
    q.add_argument("--crop", default=None, help="x0,y0,x1,y1 in reference pixels (default: around the calibrated character)")
    q.add_argument("--height", type=int, default=520)

    q = sub.add_parser("calib"); q.add_argument("--work", required=True)
    q.add_argument("--view", required=True, choices=VIEWS)
    q.add_argument("--top", type=float, required=True, help="y pixel of the head top")
    q.add_argument("--ground", type=float, required=True, help="y pixel of the soles / ground")
    q.add_argument("--center", type=float, required=True, help="x pixel of the root (pelvis) centre")

    q = sub.add_parser("inspect"); q.add_argument("model"); q.add_argument("--work", required=True)
    q.add_argument("--force", action="store_true")

    for name in ("look", "video"):
        q = sub.add_parser(name); q.add_argument("--work", required=True)
        q.add_argument("--views", default=None)
        q.add_argument("--height", type=int, default=420)
        q.add_argument("--scale", type=float, default=0.5, help="render scale vs reference resolution")
        q.add_argument("--stack", choices=["rows", "cols"], default="rows")
        q.add_argument("--crop", default=None, help="x0,y0,x1,y1 in reference pixels")
        if name == "look":
            q.add_argument("--frames", required=True)

    q = sub.add_parser("export"); q.add_argument("--work", required=True); q.add_argument("--out", required=True)

    q = sub.add_parser("view"); q.add_argument("--work", required=True)
    q.add_argument("--fast", action="store_true", help="bake the fit straight into anim.glb without Blender")
    q.add_argument("--port", type=int, default=8765)

    a = ap.parse_args()
    {"prep": cmd_prep, "ref": cmd_ref, "calib": cmd_calib, "inspect": cmd_inspect, "look": cmd_look,
     "export": cmd_export, "video": cmd_video, "view": cmd_view}[a.cmd](a)


if __name__ == "__main__":
    main()
