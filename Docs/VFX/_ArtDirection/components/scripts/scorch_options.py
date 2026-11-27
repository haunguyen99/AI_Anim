"""Options sheet for component 06 Scorch (spec: ../06_Scorch.md). Uses the codefx effect ../codefx/scorch.py.

  python -I scorch_options.py <out_png>

Rows = styles (burn / cracks / both); columns = times, top-down on a ground-coloured background,
plus the hot frame squashed to 0.64 (how the flat mark reads from the 3/4 40-degree game camera).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

CFX = "D:/Game_prj/VFX_LIb/Docs/VFX/_ArtDirection/_archive/vfx-maker_2.2.0_before_codefx_removal_2026-11-03/codefx"
sys.path.insert(0, CFX)
import codefx as cf  # noqa: E402
import render as rd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
mod = rd.load(os.path.join(HERE, "..", "codefx", "scorch.py"))
GROUND = (0.42, 0.39, 0.33)
TIMES = [0.03, 0.15, 0.4, 0.9, 1.5, 1.85]
CELL = 220


def tile(cv, squash=1.0):
    im = Image.fromarray((cf.composite(cv, GROUND) * 255).astype(np.uint8), "RGB")
    im = im.resize((CELL, CELL))
    if squash != 1.0:
        sq = im.resize((CELL, int(CELL * squash)))
        im = Image.new("RGB", (CELL, CELL), tuple(int(c * 255) for c in GROUND))
        im.paste(sq, (0, (CELL - sq.height) // 2))
    return im


def main():
    out = sys.argv[1]
    rows = [("A burn", "burn"), ("B cracks", "cracks"), ("C burn + cracks", "both")]
    cols = [f"{t:.2f}s" for t in TIMES] + ["3/4 cam 0.15s"]
    lw, pad = 150, 22
    sheet = Image.new("RGB", (lw + CELL * len(cols), pad + CELL * len(rows)), (18, 18, 18))
    dr = ImageDraw.Draw(sheet)
    for j, c in enumerate(cols):
        dr.text((lw + j * CELL + 6, 5), c, fill=(220, 220, 220))
    for i, (lab, st) in enumerate(rows):
        dr.text((6, pad + i * CELL + CELL // 2), lab, fill=(255, 210, 120))
        fr = cf.render(mod, {"style": st}, TIMES, 2.0)
        for j, cv in enumerate(fr):
            sheet.paste(tile(cv), (lw + j * CELL, pad + i * CELL))
        sheet.paste(tile(fr[1], 0.64), (lw + len(TIMES) * CELL, pad + i * CELL))
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
