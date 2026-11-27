"""Bake crescent textures for Slash360 (used with the Coloso shaders, rpg-game convention: grey shape + colour from ramp / particle).
Texture space = (l, v): x = l (0 head .. 1 tail tip), y = v across the band (0.5 = sharp outer rim).
Bakes what SH_VFX_SlashSweep did in the shader: head pinch, tail fade, toon colour bands, heat.
Run: python -I Docs/VFX/Slash360/bake_slash_textures.py
"""
import numpy as np
from PIL import Image
import os
ROOT = "Assets/VFX/Slash360/Textures/"
NOISE = "Assets/VFX/_Shared/Textures/Noise/"

def sstep(a, b, x):
    t = np.clip((x - a) / max(b - a, 1e-6), 0, 1)
    return t * t * (3 - 2 * t)

def load_mask(path, w, h):
    im = Image.open(path).convert("RGB").resize((w, h), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32)[..., 0] / 255.0       # R channel, row 0 = top (v = 1)

def sample(mask, l, v):
    h, w = mask.shape
    x = np.clip(l, 0, 1) * (w - 1)
    y = (1 - np.clip(v, 0, 1)) * (h - 1)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    x1 = np.minimum(x0 + 1, w - 1); y1 = np.minimum(y0 + 1, h - 1)
    fx = x - x0; fy = y - y0
    top = mask[y0, x0] * (1 - fx) + mask[y0, x1] * fx
    bot = mask[y1, x0] * (1 - fx) + mask[y1, x1] * fx
    out = top * (1 - fy) + bot * fy
    return out * ((v >= 0) & (v <= 1))

def crescent(src, out, core, mid, outer, band1, band2, head_point, tail_soft, head_heat=0.45,
             band_soft=0.04, w=512, h=256):
    mask = load_mask(src, 1024, 512)
    xs = (np.arange(w) + 0.5) / w
    vs = 1 - (np.arange(h) + 0.5) / h
    l, v = np.meshgrid(xs, vs)
    pinch = 0.08 + (1 - 0.08) * sstep(0, head_point, l)
    vv = 0.5 + (v - 0.5) / pinch
    m = sample(mask, l, vv)
    m *= sstep(0, 0.03, l) * (1 - sstep(1 - tail_soft, 1, l))
    lat = 1 - np.abs(v * 2 - 1)
    heat = np.clip(m * (0.5 + 0.5 * lat) + (1 - l) * head_heat * m * 0.6, 0, 1)
    g = np.clip(0.35 + 0.65 * heat, 0, 1)            # grey: brighter in the middle and near the head
    rgba = np.dstack([g, g, g, m])
    Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA").save(out)

def ramp(out, core, mid, outer, band1, band2, band_soft=0.12, w=256, h=4):
    """Colour ramp across the band (x = v): outer at the edges, core on the sharp outer rim (v = 0.5).
    Used as _ColorTex of the Additive Coloso shader with Color90degreeUVFlip."""
    v = (np.arange(w) + 0.5) / w
    t_ = 1 - np.abs(v * 2 - 1)
    col = np.zeros((w, 3), np.float32) + np.array(outer, np.float32)
    for thr, c in ((band1, mid), (band2, core)):
        k = sstep(thr - band_soft, thr + band_soft, t_)[:, None]
        col = col * (1 - k) + np.array(c, np.float32) * k
    img = np.repeat(col[None, :, :], h, axis=0)
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB").save(out)

def detail(noise_file, out, lo, hi, amount, w=256, h=256):
    n = np.asarray(Image.open(NOISE + noise_file).convert("RGB").resize((w, h), Image.BILINEAR), np.float32)[..., 0] / 255.0
    d = (1 - amount) + amount * sstep(lo, hi, n)
    Image.fromarray((np.clip(d, 0, 1) * 255).astype(np.uint8), "L").convert("RGB").save(out)

ELEMENTS = {
    # name: (body src, core, mid, outer, band1, band2, noise, lo, hi, amount)
    "Fire":      ("Body_Fire",      (1, .93, .68), (1, .5, .08),   (.8, .12, .03), .3, .88, "T_Noise_Streaks.png", .25, .75, .55),
    "Ice":       ("Body_Ice",       (.92, 1, 1),   (.4, .8, 1),    (.12, .4, .95), .3, .88, "T_Noise_Cells.png",   .36, .42, .6),
    "Lightning": ("Body_Lightning", (1, 1, 1),     (1, .9, .3),    (.55, .3, 1),   .3, .88, "T_Noise_Streaks.png", .55, .6, .75),
    "Poison":    ("Body_Poison",    (.85, 1, .3),  (.32, .82, .18), (.2, .1, .3),  .3, .88, "T_Noise_Smooth.png",  .3, .6, .5),
    "Earth":     ("Body_Earth",     (.95, .8, .5), (.6, .4, .22),  (.28, .17, .1), .3, .88, "T_Noise_Cells.png",   .5, .55, .7),
}

if __name__ == "__main__":
    for name, (src, core, mid, outer, b1, b2, noise, lo, hi, amt) in ELEMENTS.items():
        crescent(ROOT + f"T_Slash360_{src}.png", ROOT + f"T_Slash360_Crescent_{name}.png", core, mid, outer, b1, b2, 0.28, 0.25)
        # hot leading edge: white core fading to the element colour; shorter and sharper
        edge_mid = tuple(0.6 * 1 + 0.4 * c for c in mid)
        crescent(ROOT + "T_Slash360_Edge.png", ROOT + f"T_Slash360_EdgeCrescent_{name}.png", (1, 1, 1), edge_mid, core, .25, .65, 0.2, 0.5, band_soft=0.08)
        detail(noise, ROOT + f"T_Slash360_Detail_{name}.png", lo, hi, amt)
        ramp(ROOT + f"T_Slash360_Ramp_{name}.png", core, mid, outer, b1, 0.85)
    detail("T_Noise_Streaks.png", ROOT + "T_Slash360_Detail_Trail.png", 0.2, 0.95, 0.6)
    print("baked")
