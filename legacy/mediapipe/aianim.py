"""AI Animation CLI: reference video -> per-frame keyed animation on a 3D rig.

  python tools/aianim.py extract VIDEO  --work work/job1
  python tools/aianim.py inspect MODEL  --work work/job1
  python tools/aianim.py apply   MODEL  --work work/job1 [--export out.fbx] [--root-motion xz] [--floor clamp]
  python tools/aianim.py review         --work work/job1 [--count 6]
  python tools/aianim.py video          --work work/job1      (side-by-side compare.mp4, every frame)
  python tools/aianim.py run     VIDEO MODEL --work work/job1     (all four steps)

Work folder layout:
  pose.json           per-frame landmarks (extract)
  ref_preview/        reference frames with detected skeleton (extract)
  rig.json            bone hierarchy of the model (inspect)
  mapping.json        landmark -> bone mapping; edit this to fix the retarget (inspect)
  result.blend        model with the keyed action (apply)
  review/compare_*.png, review/sheet.png   reference vs result side by side (review)
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
TOOLS = os.path.join(ROOT, "tools")
BL = os.path.join(TOOLS, "blender")
DEFAULT_BLENDER = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"


def blender_exe():
    exe = os.environ.get("BLENDER") or (DEFAULT_BLENDER if os.path.exists(DEFAULT_BLENDER) else shutil.which("blender"))
    if not exe:
        sys.exit("Blender not found: set the BLENDER environment variable.")
    return exe


def run_blender(script, *args):
    cmd = [blender_exe(), "-b", "--factory-startup", "-noaudio", "-P", os.path.join(BL, script), "--", *map(str, args)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [l for l in p.stdout.splitlines() if not l.startswith(("Blender ", "Read ", "Fra:", "Saved: ", "Time:"))]
    useful = [l for l in lines if l.strip() and "Info:" not in l]
    print("\n".join(useful[-40:]))
    err = p.stderr.strip()
    if p.returncode != 0 or "Traceback" in p.stdout or "Error:" in p.stdout:
        if err:
            print(err[-3000:], file=sys.stderr)
        sys.exit(f"Blender step '{script}' failed")


def w(work, name):
    return os.path.join(work, name)


def cmd_extract(a):
    os.makedirs(a.work, exist_ok=True)
    preview = w(a.work, "ref_preview")
    shutil.rmtree(preview, ignore_errors=True)
    cmd = [sys.executable, os.path.join(TOOLS, "extract_pose.py"), a.video, "-o", w(a.work, "pose.json"),
           "--model", a.model, "--smooth", str(a.smooth), "--preview", preview, "--preview-count", "8",
           "--start", str(a.start)]
    if a.end is not None:
        cmd += ["--end", str(a.end)]
    if subprocess.run(cmd).returncode != 0:
        sys.exit("Pose extraction failed (see message above).")


def cmd_inspect(a):
    os.makedirs(a.work, exist_ok=True)
    auto = w(a.work, "mapping.auto.json")
    extra = ["--armature", a.armature] if a.armature else []
    run_blender("inspect_rig.py", os.path.abspath(a.model), "--rig-out", w(a.work, "rig.json"), "--map-out", auto, *extra)
    target = w(a.work, "mapping.json")
    if os.path.exists(target) and not a.force:
        print(f"Kept existing {target} (new guess in {auto}; use --force to overwrite)")
    else:
        shutil.copy(auto, target)
        print(f"Wrote {target}")


def cmd_apply(a):
    args = [os.path.abspath(a.model), w(a.work, "pose.json"), w(a.work, "mapping.json"),
            "--out", w(a.work, "result.blend"), "--root-motion", a.root_motion, "--floor", a.floor,
            "--step", a.step, "--max-twist", a.max_twist]
    if a.export:
        args += ["--export", os.path.abspath(a.export)]
    if a.armature:
        args += ["--armature", a.armature]
    run_blender("apply_motion.py", *args)
    cmd_score(a)


def cmd_score(a):
    extra = ["--armature", a.armature] if getattr(a, "armature", None) else []
    run_blender("score_motion.py", w(a.work, "result.blend"), w(a.work, "pose.json"), w(a.work, "mapping.json"),
                "--out", w(a.work, "score.json"), *extra)


def read_ref_frame(pose, k):
    cap = cv2.VideoCapture(pose["source"])
    cap.set(cv2.CAP_PROP_POS_FRAMES, pose["first_frame"] + k)
    ok, img = cap.read()
    cap.release()
    return img if ok else np.zeros((pose["height"], pose["width"], 3), np.uint8)


def fit(img, size):
    h, wd = img.shape[:2]
    s = size / max(h, wd)
    img = cv2.resize(img, (int(wd * s), int(h * s)))
    canvas = np.full((size, size, 3), 40, np.uint8)
    y, x = (size - img.shape[0]) // 2, (size - img.shape[1]) // 2
    canvas[y:y + img.shape[0], x:x + img.shape[1]] = img
    return canvas, s, x, y


# Same skeleton topology drawn on both sides of the review image.
REVIEW_SEGS = [("left_shoulder", "right_shoulder"), ("left_hip", "right_hip"),
               ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip")]
for _s in ("left", "right"):
    REVIEW_SEGS += [(f"{_s}_shoulder", f"{_s}_elbow"), (f"{_s}_elbow", f"{_s}_wrist"), (f"{_s}_wrist", f"{_s}_hand"),
                    (f"{_s}_hip", f"{_s}_knee"), (f"{_s}_knee", f"{_s}_ankle"), (f"{_s}_ankle", f"{_s}_toe")]
REF_VIRTUAL = {"left_hand": ["left_index", "left_pinky"], "right_hand": ["right_index", "right_pinky"],
               "left_toe": ["left_foot_index"], "right_toe": ["right_foot_index"]}


def draw_segments(img, pts, color):
    for p, q in REVIEW_SEGS:
        if p in pts and q in pts:
            color_ = color if "left" not in p else tuple(int(c * 0.6) for c in color)
            cv2.line(img, pts[p], pts[q], color_, 3)


def make_tile(pose, k, ref_img, outdir, size):
    """Reference frame (green skeleton) | rendered result (orange skeleton)."""
    fr = k + 1
    ref, s, ox, oy = fit(ref_img, size)
    lm = dict(zip(pose["landmark_names"], pose["frames"][k]["image"]))
    for v, parts in REF_VIRTUAL.items():
        lm[v] = np.mean([lm[p] for p in parts], axis=0)
    pts = {nm: (int(u * pose["width"] * s + ox), int(v * pose["height"] * s + oy)) for nm, (u, v) in lm.items()}
    draw_segments(ref, pts, (0, 255, 0))
    ren = cv2.imread(os.path.join(outdir, f"render_{fr:05d}.png"))
    with open(os.path.join(outdir, f"joints_{fr:05d}.json")) as f:
        jl = json.load(f)["landmarks"]
    draw_segments(ren, {nm: (int(u * size), int(v * size)) for nm, (u, v) in jl.items()}, (0, 160, 255))
    tile = np.hstack([ref, ren])
    cv2.putText(tile, f"frame {fr}  t={k / pose['fps']:.2f}s", (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return tile


def render_frames(a, ks, outdir):
    shutil.rmtree(outdir, ignore_errors=True)
    run_blender("render_review.py", w(a.work, "result.blend"), "--frames", ",".join(str(k + 1) for k in ks),
                "--outdir", outdir, "--size", a.size, "--mapping", w(a.work, "mapping.json"))


def cmd_review(a):
    with open(w(a.work, "pose.json")) as f:
        pose = json.load(f)
    n = pose["frame_count"]
    ks = sorted(set(np.linspace(0, n - 1, min(a.count, n)).astype(int).tolist()))
    outdir = w(a.work, "review")
    render_frames(a, ks, outdir)
    tiles = []
    for k in ks:
        tile = make_tile(pose, k, read_ref_frame(pose, k), outdir, a.size)
        cv2.imwrite(os.path.join(outdir, f"compare_{k + 1:05d}.png"), tile)
        tiles.append(tile)
    cols = 2
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    sheet = np.vstack(rows)
    if sheet.shape[1] > 2048:
        sc = 2048 / sheet.shape[1]
        sheet = cv2.resize(sheet, (2048, int(sheet.shape[0] * sc)))
    cv2.imwrite(os.path.join(outdir, "sheet.png"), sheet)
    print(f"Review sheet: {os.path.join(outdir, 'sheet.png')}  (left = reference, right = result)")


def cmd_video(a):
    """Side-by-side mp4 of every frame: reference | result."""
    with open(w(a.work, "pose.json")) as f:
        pose = json.load(f)
    ks = list(range(pose["frame_count"]))
    outdir = w(a.work, "review_video")
    render_frames(a, ks, outdir)
    cap = cv2.VideoCapture(pose["source"])
    cap.set(cv2.CAP_PROP_POS_FRAMES, pose["first_frame"])
    out_path = w(a.work, "compare.mp4")
    vw = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), pose["fps"], (a.size * 2, a.size))
    for k in ks:
        ok, img = cap.read()
        if not ok:
            img = np.zeros((pose["height"], pose["width"], 3), np.uint8)
        vw.write(make_tile(pose, k, img, outdir, a.size))
    vw.release()
    cap.release()
    shutil.rmtree(outdir, ignore_errors=True)
    if shutil.which("ffmpeg"):  # re-encode mp4v -> H.264 so any player opens it
        tmp = out_path + ".h264.mp4"
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out_path, "-c:v", "libx264",
                            "-pix_fmt", "yuv420p", "-crf", "22", tmp])
        if r.returncode == 0:
            os.replace(tmp, out_path)
    print(f"Comparison video: {out_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, model=False, video=False):
        if video:
            p.add_argument("video")
        if model:
            p.add_argument("model")
        p.add_argument("--work", required=True)
        p.add_argument("--armature", default=None)

    p = sub.add_parser("extract"); common(p, video=True)
    p.add_argument("--model", choices=["heavy", "full"], default="heavy")
    p.add_argument("--smooth", type=float, default=1.5)
    p.add_argument("--start", type=float, default=0.0)
    p.add_argument("--end", type=float, default=None)

    p = sub.add_parser("inspect"); common(p, model=True)
    p.add_argument("--force", action="store_true")

    for name in ("apply", "run"):
        p = sub.add_parser(name)
        common(p, model=True, video=(name == "run"))
        p.add_argument("--export", default=None)
        p.add_argument("--root-motion", choices=["xz", "x", "none"], default="xz")
        p.add_argument("--floor", choices=["clamp", "lock", "none"], default="clamp")
        p.add_argument("--step", type=int, default=1)
        p.add_argument("--max-twist", type=float, default=12.0)
        if name == "run":
            p.add_argument("--smooth", type=float, default=1.5)
            p.add_argument("--start", type=float, default=0.0)
            p.add_argument("--end", type=float, default=None)
            p.add_argument("--count", type=int, default=6)
            p.add_argument("--size", type=int, default=480)
            p.add_argument("--force", action="store_true")

    p = sub.add_parser("score"); p.add_argument("--work", required=True)
    p.add_argument("--armature", default=None)

    p = sub.add_parser("review"); p.add_argument("--work", required=True)
    p.add_argument("--count", type=int, default=6)
    p.add_argument("--size", type=int, default=480)

    p = sub.add_parser("video"); p.add_argument("--work", required=True)
    p.add_argument("--size", type=int, default=480)

    a = ap.parse_args()
    if a.cmd == "run":
        a.model_name = a.model
        model = a.model
        a.model = "heavy"
        cmd_extract(a)
        a.model = model
        cmd_inspect(a)
        cmd_apply(a)
        cmd_review(a)
    else:
        {"extract": cmd_extract, "inspect": cmd_inspect, "apply": cmd_apply, "score": cmd_score,
         "review": cmd_review, "video": cmd_video}[a.cmd](a)


if __name__ == "__main__":
    main()
