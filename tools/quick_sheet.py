"""One small contact sheet from a quick self-check render (rows = frames, columns = views), so a fix is checked
with ONE image read instead of one per frame and view (user 2026-10-22: gộp note + render nhanh, bớt token).
python tools/quick_sheet.py <dir with <view>_<frame>.png> [--cell 220] [--crop 0.08] [--out sheet.jpg] [--frames 19,23] [--views left,right]
--crop trims that fraction off every side (the character sits in the middle of the Ref_* frames)."""
import argparse
import os
import re

from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("dir")
ap.add_argument("--cell", type=int, default=220)
ap.add_argument("--crop", type=float, default=0.08)
ap.add_argument("--out", default="sheet.jpg")
ap.add_argument("--frames", default="", help="e.g. 19,21,23 (default: all)")
ap.add_argument("--views", default="", help="e.g. left,right (default: all)")
a = ap.parse_args()

cells = {}
for fn in os.listdir(a.dir):
    m = re.fullmatch(r"([a-z0-9]+)_(\d+)\.png", fn)
    if m:
        f, v = int(m.group(2)), m.group(1)
        if (a.frames and f not in {int(x) for x in a.frames.split(",")}) or (a.views and v not in a.views.split(",")):
            continue
        cells[(f, v)] = os.path.join(a.dir, fn)
frames = sorted({f for f, _ in cells})
order = ["right", "left", "front", "top", "game"]
views = sorted({v for _, v in cells}, key=lambda v: (order.index(v) if v in order else 99, v))
try:
    font = ImageFont.truetype("arial.ttf", 14)
except OSError:
    font = ImageFont.load_default()

C, LAB = a.cell, 18
sheet = Image.new("RGB", (C * len(views), LAB + C * len(frames)), (14, 15, 18))
d = ImageDraw.Draw(sheet)
for j, v in enumerate(views):
    d.text((j * C + 4, 2), v, fill=(200, 204, 210), font=font)
for i, f in enumerate(frames):
    for j, v in enumerate(views):
        if (f, v) not in cells:
            continue
        im = Image.open(cells[(f, v)]).convert("RGB")
        w, h = im.size
        cx, cy = int(w * a.crop), int(h * a.crop)
        im = im.crop((cx, cy, w - cx, h - cy))
        im.thumbnail((C, C))
        x, y = j * C + (C - im.width) // 2, LAB + i * C + (C - im.height) // 2
        sheet.paste(im, (x, y))
        d.text((j * C + 4, LAB + i * C + 2), f"F{f}", fill=(242, 177, 52), font=font)
out = os.path.join(a.dir, a.out)
sheet.save(out, quality=85)
print("SHEET", out, sheet.size, "frames", frames, "views", views)
