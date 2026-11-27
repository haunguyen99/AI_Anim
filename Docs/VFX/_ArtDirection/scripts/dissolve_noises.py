"""Three tileable dissolve noises (256, grayscale, linear data) for the shader -> sheet pipeline.
  A cells   : weighted Worley - round holes in Large / Medium / Small sizes, no two same-size cells adjacent
  B streaks : noise stretched along +Y (motion direction) - wispy tearing that follows the rise
  C chunks  : low-frequency, high-contrast blobs - breaks into a few big pieces
Holes open where the value is LOW (shader: alpha = value > cut).
  python dissolve_noises.py OUT_DIR
"""
import os
import sys
import numpy as np
from PIL import Image

N = 256
rng = np.random.default_rng(21)


def normalize(a):
    a = a - a.min()
    return a / (a.max() + 1e-9)


def filtered_noise(sx, sy, seed):
    """Periodic (tileable) noise: white noise low-passed in the frequency domain with an anisotropic Gaussian."""
    r = np.random.default_rng(seed)
    f = np.fft.fft2(r.standard_normal((N, N)))
    ky = np.fft.fftfreq(N)[:, None]
    kx = np.fft.fftfreq(N)[None, :]
    g = np.exp(-((kx * sx) ** 2 + (ky * sy) ** 2))
    return normalize(np.real(np.fft.ifft2(f * g)))


def cells():
    """Weighted Worley with L/M/S cells; neighbours of the same size class are re-rolled."""
    pts, size = [], []
    radii = {0: 1.0, 1: 0.62, 2: 0.36}            # L / M / S
    grid = 6
    for gy in range(grid):
        for gx in range(grid):
            for _ in range(2 if rng.random() < 0.5 else 1):
                pts.append(((gx + rng.random()) / grid, (gy + rng.random()) / grid))
                size.append(int(rng.choice([0, 1, 2], p=[0.2, 0.35, 0.45])))
    pts = np.array(pts)
    # L/M/S rule: re-roll a cell that touches a same-size neighbour (a few passes)
    for _ in range(6):
        for i in range(len(pts)):
            d = np.abs(pts - pts[i]); d = np.minimum(d, 1 - d); d = np.hypot(d[:, 0], d[:, 1])
            near = (d < 0.2) & (d > 0)
            if any(size[j] == size[i] for j in np.where(near)[0]):
                size[i] = int(rng.integers(0, 3))
    w = np.array([radii[s] for s in size])
    ys, xs = np.mgrid[0:N, 0:N] / N
    best = np.full((N, N), 9.0)
    for (px, py), wi in zip(pts, w):
        dx = np.abs(xs - px); dx = np.minimum(dx, 1 - dx)
        dy = np.abs(ys - py); dy = np.minimum(dy, 1 - dy)
        best = np.minimum(best, np.hypot(dx, dy) / wi)
    v = normalize(best)                             # 0 at cell centres -> holes open there first
    v = 0.85 * v + 0.15 * filtered_noise(25, 25, 3)  # break perfect circles a little
    return normalize(v)


def streaks():
    base = filtered_noise(14, 110, 5)               # smooth along Y (motion) -> long vertical streaks
    detail = filtered_noise(30, 60, 6)
    return normalize(base * 0.75 + detail * 0.25)


def chunks():
    v = filtered_noise(70, 70, 9) * 0.8 + filtered_noise(25, 25, 10) * 0.2
    v = normalize(v)
    return normalize(1 / (1 + np.exp(-(v - 0.5) * 7)))   # high contrast -> a few big pieces


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, fn in (("Cells", cells), ("Streaks", streaks), ("Chunks", chunks)):
        img = Image.fromarray((fn() * 255).astype(np.uint8), "L")
        img.save(os.path.join(out, f"T_Noise_Dissolve_{name}.png"))
        print(name, "ok")
