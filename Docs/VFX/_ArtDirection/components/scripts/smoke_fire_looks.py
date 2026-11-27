"""Compare the codefx smoke puff in 3 colour looks: smoke / fire / fire -> smoke (same shape + motion).

  python -I smoke_fire_looks.py <out_png>
"""
import sys

import numpy as np
from PIL import Image, ImageDraw

CFX = "D:/Game_prj/VFX_LIb/Docs/VFX/_ArtDirection/_archive/vfx-maker_2.2.0_before_codefx_removal_2026-11-03/codefx"
sys.path.insert(0, CFX)
import codefx as cf  # noqa: E402
import render as rd  # noqa: E402

mod = rd.load(CFX + "/fx/smoke/puff_burst.py")
TIMES = [0.03, 0.12, 0.25, 0.45, 0.65, 0.85]
W, H = 264, 192


def main():
    rows = [("smoke", "smoke"), ("fire", "fire"), ("fire -> smoke", "fire2smoke")]
    pad, lw = 22, 120
    sheet = Image.new("RGB", (lw + W * len(TIMES), pad + H * len(rows)), (18, 18, 18))
    dr = ImageDraw.Draw(sheet)
    for j, t in enumerate(TIMES):
        dr.text((lw + j * W + 6, 5), f"{t:.2f}s", fill=(220, 220, 220))
    for i, (lab, look) in enumerate(rows):
        dr.text((6, pad + i * H + H // 2), lab, fill=(255, 210, 120))
        for j, cv in enumerate(cf.render(mod, {"look": look}, TIMES, 1.5)):
            im = Image.fromarray((cf.composite(cv) * 255).astype(np.uint8)).resize((W, H))
            sheet.paste(im, (lw + j * W, pad + i * H))
    sheet.save(sys.argv[1])
    print(sys.argv[1], sheet.size)


if __name__ == "__main__":
    main()
