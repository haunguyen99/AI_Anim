"""GroundBlast smoke sphere textures (Beyond-FX "Zelda explosion" smoke technique, art lead reference 2026-11-04).

  python -I smoke_sphere_textures.py <textures_dir> [preview_png]

Writes:
  T_GroundBlast_SmokeErode.png  erosion mask (grey, linear data): dark swirl in the centre -> bright rim.
                                Read through view-space UVs on a sphere, so the centre always faces the camera.
                                Equalised inside the disc: a threshold sweeping 0 -> 1 eats an even area per step.
  T_GroundBlast_SmokeRamp.png   heat ramp, u = heat: 0 dark red -> orange -> yellow -> 1 white-hot.
Optional preview: the mask thresholded at 8 steps, to check the erosion order.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

N = 256


def smooth_noise(n, cells, seed):
    """Value noise: random grid upscaled with bicubic (cheap fBm octave)."""
    rng = np.random.default_rng(seed)
    g = rng.random((cells, cells)).astype(np.float32)
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255


def erode_mask():
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    u, v = (x + 0.5) / N * 2 - 1, (y + 0.5) / N * 2 - 1
    r = np.sqrt(u * u + v * v)
    th = np.arctan2(v, u)
    swirl = th + 3.4 * (1 - np.clip(r, 0, 1)) ** 1.2    # arms twist toward the centre
    arms = 0.5 + 0.5 * np.cos(3 * swirl)                   # three arms: big painted swirl
    fbm = 0.55 * smooth_noise(N, 6, 3) + 0.3 * smooth_noise(N, 12, 4) + 0.15 * smooth_noise(N, 24, 5)
    # v2: arms weigh as much as the centre->rim slope, so erosion runs along the swirl and breaks the mass into
    # pieces (v1 = one round hole growing from the centre -> hollow ring, the look the art lead rejected)
    m = 0.42 * np.clip(r, 0, 1) ** 0.8 + 0.40 * arms * (0.25 + 0.75 * np.clip(r, 0, 1)) + 0.18 * fbm
    m = np.asarray(Image.fromarray(np.clip(m * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2)), np.float32) / 255
    inside = r < 1.0
    flat = m[inside]
    ranks = np.argsort(np.argsort(flat))                   # equalise: even area per threshold step
    m[inside] = (ranks + 0.5) / len(flat) * 0.97
    m[~inside] = 1.0                                       # beyond the silhouette: never eaten early
    return np.clip(m, 0, 1)


def ramp():
    # v2 (reference compare 2026-11-04): hottest = yellow-orange, never white; mostly saturated orange
    stops = [(0.0, (0x6A, 0x14, 0x08)), (0.25, (0xD2, 0x3A, 0x10)), (0.55, (0xFF, 0x8A, 0x1E)),
             (0.85, (0xFF, 0xC2, 0x4A)), (1.0, (0xFF, 0xE0, 0x80))]
    row = np.zeros((N, 3), np.float32)
    for i in range(N):
        t = i / (N - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                k = (t - t0) / (t1 - t0)
                row[i] = [c0[j] + (c1[j] - c0[j]) * k for j in range(3)]
    return np.repeat(row[None], 8, axis=0).astype(np.uint8)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    m = erode_mask()
    Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(out, "T_GroundBlast_SmokeErode.png"))
    Image.fromarray(ramp(), "RGB").save(os.path.join(out, "T_GroundBlast_SmokeRamp.png"))
    print(os.path.join(out, "T_GroundBlast_SmokeErode.png"))
    print(os.path.join(out, "T_GroundBlast_SmokeRamp.png"))
    if len(sys.argv) > 2:                                   # erosion order preview
        W = 128
        sheet = Image.new("RGB", (W * 9 + 10 * 10, W + 30), (24, 24, 28))
        d = ImageDraw.Draw(sheet)
        mask = Image.fromarray((m * 255).astype(np.uint8)).resize((W, W))
        sheet.paste(mask.convert("RGB"), (10, 22)); d.text((10, 4), "mask", fill=(220, 220, 220))
        for i, thr in enumerate(np.linspace(0.0, 0.9, 8)):
            a = (np.asarray(mask, np.float32) / 255 > thr).astype(np.uint8) * 200
            sheet.paste(Image.fromarray(a).convert("RGB"), (10 + (i + 1) * (W + 10), 22))
            d.text((10 + (i + 1) * (W + 10), 4), f"thr {thr:.2f}", fill=(220, 220, 220))
        sheet.save(sys.argv[2])
        print(sys.argv[2])


if __name__ == "__main__":
    main()
