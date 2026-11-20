"""Tileable noise textures for shader-only VFX (vfx-shader skill). Needs numpy + Pillow.

Each PNG packs two noises: R = main, G = a second, finer/other noise, B = R (for quick viewing), no alpha.
Import in Unity as linear data (no sRGB), Repeat wrap. Shaders read .r and .g.

  python -I make_noise.py smooth  -o T_Noise_Smooth.png      # R: soft blobs, G: finer soft noise
  python -I make_noise.py cells   -o T_Noise_Cells.png       # R: Worley cells (big/medium/small), G: cell edges
  python -I make_noise.py streaks -o T_Noise_Streaks.png     # R: stretched along +Y, G: stretched along +X
  python -I make_noise.py all     -o <folder>                # all three into a folder
Options: --size 256 --seed 7
"""
import argparse
import os

import numpy as np
from PIL import Image


def normalize(a):
    a = a - a.min()
    return a / (a.max() + 1e-9)


def fft_noise(n, sx, sy, rng):
    """Periodic noise: white noise low-passed in frequency space (sx, sy = feature size in px)."""
    f = np.fft.fft2(rng.standard_normal((n, n)))
    ky = np.fft.fftfreq(n)[:, None]
    kx = np.fft.fftfreq(n)[None, :]
    g = np.exp(-((kx * sx) ** 2 + (ky * sy) ** 2) * 2.0)
    return normalize(np.real(np.fft.ifft2(f * g)))


def worley(n, count, rng):
    """Tileable Worley F1 with mixed cell sizes; returns (distance-ish value, edge)."""
    pts = rng.random((count, 2)) * n
    w = rng.choice([1.0, 0.6, 0.35], size=count, p=[0.2, 0.35, 0.45])  # big / medium / small
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    f1 = np.full((n, n), 1e9, np.float32)
    f2 = np.full((n, n), 1e9, np.float32)
    for (px, py), wi in zip(pts, w):
        dx = np.abs(xx - px); dx = np.minimum(dx, n - dx)
        dy = np.abs(yy - py); dy = np.minimum(dy, n - dy)
        d = np.sqrt(dx * dx + dy * dy) / wi
        f2 = np.where(d < f1, f1, np.minimum(f2, d))
        f1 = np.minimum(f1, d)
    return normalize(-f1), normalize(f2 - f1)


def make(kind, n, seed):
    rng = np.random.default_rng(seed)
    if kind == "smooth":
        r = fft_noise(n, n / 6, n / 6, rng)
        g = fft_noise(n, n / 16, n / 16, rng)
    elif kind == "cells":
        r, g = worley(n, 18, rng)
    elif kind == "streaks":
        r = fft_noise(n, n / 24, n / 3, rng)   # long along Y
        g = fft_noise(n, n / 3, n / 24, rng)   # long along X
    else:
        raise SystemExit("unknown kind: " + kind)
    rgb = np.stack([r, g, r], -1)
    return Image.fromarray((rgb * 255 + 0.5).astype(np.uint8), "RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["smooth", "cells", "streaks", "all"])
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--size", type=int, default=256)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    if a.kind == "all":
        os.makedirs(a.out, exist_ok=True)
        for k, name in [("smooth", "T_Noise_Smooth"), ("cells", "T_Noise_Cells"), ("streaks", "T_Noise_Streaks")]:
            make(k, a.size, a.seed).save(os.path.join(a.out, name + ".png"))
            print("wrote", os.path.join(a.out, name + ".png"))
    else:
        make(a.kind, a.size, a.seed).save(a.out)
        print("wrote", a.out)


if __name__ == "__main__":
    main()
