"""Even ring of spikes lying on the ground for IMP_Hit_Ground "Flat" (replaces T_IMP_GroundRing).

  python -I ground_burst.py <out.png>

Why (art lead 2026-11-03): the old Impact09 ring was lopsided (gap bottom-left, longer spikes right). Seen flat from the
3/4 camera its side spikes are not squashed, so it read as a directional hit inside a ground mix. This one is
radially even: 16 spikes alternating long / short with small jitter, hollow centre. Additive: RGB white, shape in alpha.
"""
import math
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, "D:/Game_prj/VFX_LIb/Docs/VFX/_ArtDirection/_archive/vfx-maker_2.2.0_before_codefx_removal_2026-11-03/codefx")
import codefx as cf  # noqa: E402

N, R = 16, 120.0
rng = cf.Rng(11)
cv = cf.Canvas((256, 256), (128, 128), res=2.0)
lengths = [R * (0.95 if i % 2 == 0 else 0.72) * rng.range(0.94, 1.04) for i in range(N)]
cv.star(0, 0, lengths, R * 0.5, rot=rng.range(0, cf.TAU / N), c=(1.0, 1.0, 1.0), a=1.0)
# hollow centre with a soft inner edge (the flash and splash fill it)
a = cv.alpha.copy()
h, w = a.shape
yy, xx = np.mgrid[0:h, 0:w]
r = np.hypot((xx + 0.5) / cv.res - 128, (yy + 0.5) / cv.res - 128)
a *= np.clip((r - R * 0.36) / (R * 0.12), 0, 1)
img = np.dstack([np.ones_like(a), np.ones_like(a), np.ones_like(a), a])
Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGBA").save(sys.argv[1])
print(sys.argv[1], img.shape)
