"""Dust texture for component 05 Dust, style A Toon puff (spec: ../05_Dust.md).

  python -I dust_sheet.py <src_puff_4x4.png> <out.png>

Source: Assets/VFX/SmokeStylized/Textures/T_SmokeStylized3D_Puff_4x4.png (baked toon smoke, lavender-grey tones).
Component standard: textures are white-grey, colour comes from the colour slot. So the RGB tones are turned
neutral and lifted (shadow ~0.45, light 1.0) to keep the 2-tone look; alpha (shape + dissolve) is kept as is.
Alpha Blend rule: RGB = tones, A = shape.
"""
import sys

import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert("RGBA"), np.float32) / 255
lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
lo, hi = np.percentile(lum[a[..., 3] > 0.5], [2, 99.5])
t = np.clip((lum - lo) / max(hi - lo, 1e-4), 0, 1)
tone = 0.45 + 0.55 * t
rgba = np.dstack([tone, tone, tone, a[..., 3]])
Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), "RGBA").save(out)
print(out, f"tone range {lo:.2f}..{hi:.2f} -> 0.45..1.0")
