"""Rock palette for the Earth spikes: copy of T_IceSpike_Palette.tga with the crystal UV patch (u 0.43-0.48, v 0.28-0.56)
repainted as hard strata bands, dark at the base to lighter at the tip (like layered rock).
The crystal meshes only sample v along their height inside that patch, so the texture works as a height ramp.
  python -I Docs/VFX/IceSpike/make_rock_palette.py
"""
from PIL import Image
import numpy as np

SRC = "Assets/VFX/IceSpike/Textures/T_IceSpike_Palette.tga"
OUT = "Assets/VFX/IceSpike/Textures/T_IceSpike_RockPalette.png"

# strata, bottom (dark, wet earth) -> top (pale, dry stone); hard steps, slight cool/warm alternation like sediment layers
BANDS = [(30, 23, 18), (50, 38, 29), (70, 56, 44), (62, 52, 44), (88, 72, 57), (108, 92, 76), (128, 112, 94)]   # dark soil brown -> dry grey-brown stone

# (u0, u1, v0, v1): UV patches of the meshes that sample the palette; v0..v1 = height range inside the patch
PATCHES = [
    (0.43, 0.48, 0.33, 0.51),   # SM_VFX_Big_/Small_Crystal_*, Debris_Crystal_* (u 0.455)
    (0.83, 0.88, 0.50, 0.65),   # SM_VFX_Bone (u 0.85, v 0.52-0.63), not used now
    (0.98, 1.00, 0.20, 0.32),   # SM_VFX_Small_Crystal_04 (u 0.995, v 0.21-0.31): was purple without it
]

im = np.asarray(Image.open(SRC).convert("RGB")).copy()
H, W, _ = im.shape
for u0, u1, v0, v1 in PATCHES:
    for y in range(H):
        v = 1 - (y + 0.5) / H
        t = np.clip((v - v0) / (v1 - v0), 0, 0.9999)
        c = BANDS[int(t * len(BANDS))]
        for x in range(int(u0 * W), int(u1 * W)):
            im[y, x] = c
Image.fromarray(im).save(OUT)
print("saved", OUT)
