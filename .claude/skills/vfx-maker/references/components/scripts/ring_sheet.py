"""Ring flipbook sheets for component 03 Ring (spec: ../03_Ring.md).

The ring grows INSIDE a fixed quad (8 frames, 4x2, cell 256 px), so the line thickness is
controlled per frame instead of scaling up with the particle.

  python -I ring_sheet.py <out_dir> [--thick 1.5] [--name T_RNG_Shock_4x2.png]

Style B (shockwave): sharp bright edge + soft fill fading inward behind the edge.
"""
import argparse
import os

import numpy as np
from PIL import Image

CELL, COLS, ROWS = 256, 4, 2


def frame(t, thick):
    n = CELL
    y, x = np.mgrid[0:n, 0:n]
    u = (x + 0.5) / n * 2 - 1
    v = (y + 0.5) / n * 2 - 1
    r = np.sqrt(u * u + v * v)
    px = 2.0 / n
    R = 0.12 + 0.80 * (1 - (1 - t) ** 2)            # ease-out growth, touches ~92 % of the cell at the end
    w = 0.085 * thick * (1 - 0.65 * t)               # edge gets thinner as it travels
    edge = np.clip(0.5 - (np.abs(r - R) - w / 2) / (1.5 * px), 0, 1)
    # wave body: a bright wall right behind the edge, fading inward (this is what reads as "shockwave")
    tail = R * (0.55 - 0.3 * t)                       # body length: thick at first, thinner as it travels
    k = np.clip((r - (R - tail)) / max(tail, 1e-4), 0, 1) * (r < R)
    inner = (k ** 1.3) * 0.9
    a = np.maximum(edge, inner)
    fade = 1.0 if t < 0.75 else 1 - (t - 0.75) / 0.25 * 0.8
    return np.clip(a * fade, 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--thick", type=float, default=1.0)
    ap.add_argument("--name", default="T_RNG_Shock_4x2.png")
    a = ap.parse_args()
    sheet = np.zeros((CELL * ROWS, CELL * COLS))
    for i in range(COLS * ROWS):
        f = frame(i / (COLS * ROWS - 1), a.thick)
        sheet[(i // COLS) * CELL:(i // COLS + 1) * CELL, (i % COLS) * CELL:(i % COLS + 1) * CELL] = f
    g = Image.fromarray((sheet * 255 + 0.5).astype(np.uint8), "L")
    os.makedirs(a.out_dir, exist_ok=True)
    out = os.path.join(a.out_dir, a.name)
    # RGB white + shape in alpha: Mobile/Particles/Additive multiplies rgb by alpha (Blend SrcAlpha One),
    # so storing the shape in both would square the brightness (a 0.45 fill would show as 0.2).
    w = Image.new("L", g.size, 255)
    Image.merge("RGBA", (w, w, w, g)).save(out)
    print(out, g.size)


if __name__ == "__main__":
    main()
