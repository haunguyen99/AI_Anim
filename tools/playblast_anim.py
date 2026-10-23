"""Playblast of the animation alone (no reference), 2x2 views, looped - for clips that have no ref (variants, edits).

Blender side first: FRAMES = list(range(1, N+1)); VIEWS = [...]; exec(live_render.py) -> work/blender/look/r_<view>_<frame>.png
python tools/playblast_anim.py --frames 60 --out work/idle_front/review.webm [--label Idle_Front] [--loops 3]
    [--page-webm work/review_page/clips/idle_front_v6.webm]
Use .webm (VP9 via ffmpeg, ~10x lighter than mp4). The last frame of a loop equals the first, so each loop plays
f1..f(N-1) - playing fN too shows a 1-frame hitch.
"""
import argparse
import os
import shutil
import subprocess
import tempfile

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--views", default="front,left,back,top")
    ap.add_argument("--label", default="")
    ap.add_argument("--loops", type=int, default=3)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--height", type=int, default=360)
    ap.add_argument("--jpg-dir", default="", help="also write one JPEG per frame (f001.jpg..)")
    ap.add_argument("--page-webm", default="", help="also write one clean loop as WebM for the review page")
    a = ap.parse_args()
    look = os.path.join(ROOT, "work", "blender", "look"); views = a.views.split(","); n = a.frames
    imgs = {(v, f): cv2.imread(os.path.join(look, f"r_{v}_{f:04d}.png"), cv2.IMREAD_UNCHANGED)
            for v in views for f in range(1, n + 1)}
    box = {}
    for v in views:                                   # one crop per view: union of the character over the clip
        m = np.zeros(imgs[(v, 1)].shape[:2], bool)
        for f in range(1, n + 1):
            m |= imgs[(v, f)][:, :, 3] > 0
        ys, xs = np.where(m)
        box[v] = (max(0, ys.min() - 30), ys.max() + 30, max(0, xs.min() - 30), xs.max() + 30)

    def tile(v, f):
        y0, y1, x0, x1 = box[v]; im = imgs[(v, f)][y0:y1, x0:x1]; al = im[:, :, 3:] / 255.0
        o = (np.full(im.shape[:2] + (3,), 70) * (1 - al) + im[:, :, :3] * al).astype(np.uint8)
        s = a.height / o.shape[0]; o = cv2.resize(o, (int(o.shape[1] * s), a.height), interpolation=cv2.INTER_AREA)
        for yy in range(0, a.height, 24):             # faint guide lines to read vertical motion
            o[yy] = (o[yy] * 0.7 + 30).astype(np.uint8)
        cv2.putText(o, v, (8, 22), 0, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        return o

    w = max(tile(v, 1).shape[1] for v in views)
    grid = {}
    for f in range(1, n):
        ts = [tile(v, f) for v in views]
        ts = [np.pad(t, ((0, 0), (0, w - t.shape[1]), (0, 0)), constant_values=70) for t in ts]
        grid[f] = np.vstack([np.hstack(ts[i:i + 2]) for i in range(0, len(ts), 2)])
    if a.jpg_dir:                                     # clean frames (no text bar): the review page draws its own UI
        os.makedirs(a.jpg_dir, exist_ok=True)
        for f, fr in grid.items():
            cv2.imwrite(os.path.join(a.jpg_dir, f"f{f:03d}.jpg"), fr, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if a.page_webm:                                   # one clean loop for the review page (seekable: keyframe every 10 F)
        encode([grid[f] for f in range(1, n)], a.page_webm, a.fps, gop=10)
        print(a.page_webm, f"{os.path.getsize(a.page_webm) / 1e3:.0f} kB")
    seq = []
    for loop in range(a.loops):
        for f in range(1, n):
            bar = np.full((30, grid[f].shape[1], 3), 25, np.uint8)
            cv2.putText(bar, f"{a.label}  f{f:3d}/{n}  loop {loop + 1}/{a.loops}", (8, 21), 0, 0.6, (230, 230, 230), 1,
                        cv2.LINE_AA)
            seq.append(np.vstack([bar, grid[f]]))
    encode(seq, a.out, a.fps)
    print(a.out, f"{os.path.getsize(a.out) / 1e3:.0f} kB")


def encode(frames, out, fps, gop=60):
    """WebM (VP9 through ffmpeg) when OUT ends in .webm - about 10x lighter than mp4v; otherwise OpenCV mp4v."""
    if not out.lower().endswith(".webm"):
        wr = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (frames[0].shape[1], frames[0].shape[0]))
        for fr in frames:
            wr.write(fr)
        wr.release(); return
    ff = shutil.which("ffmpeg")
    if not ff:
        raise SystemExit("ffmpeg not found on PATH (winget install Gyan.FFmpeg)")
    with tempfile.TemporaryDirectory() as tmp:
        for i, fr in enumerate(frames):
            cv2.imwrite(os.path.join(tmp, f"{i:05d}.png"), fr)
        subprocess.run([ff, "-v", "error", "-y", "-framerate", str(fps), "-i", os.path.join(tmp, "%05d.png"),
                        "-c:v", "libvpx-vp9", "-crf", "34", "-b:v", "0", "-g", str(gop), "-row-mt", "1",
                        "-pix_fmt", "yuv420p", out], check=True)


if __name__ == "__main__":
    main()
