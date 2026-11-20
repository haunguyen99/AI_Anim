"""Heal magic circle textures, drawn from scratch (no library shapes). White on black, tinted by the particle colour.

  python -I heal_circle_textures.py <out_dir>

Writes (512 px, supersampled 4x for clean thin lines):
  T_HealCircle_RuneOuter.png  outer band: double ring, 12 dots, 24 ticks, 6 small arcs (rotates one way)
  T_HealCircle_RuneInner.png  inner pattern: ring, 6 round leaf petals, small centre ring (rotates the other way)
  T_HealCircle_Beam.png       soft light column for a Stretched Billboard: bright at the RIGHT edge (ground),
                              fading to the LEFT edge (= flight direction, up), soft across its width
Healing reads as safe, so everything is round: circles, dots and leaf petals, no sharp spikes.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

N, SS = 512, 4
S = N * SS
C = S / 2


def ring(d, r, w, a=255):
    d.ellipse([C - r, C - r, C + r, C + r], outline=a, width=int(w))


def dot(d, x, y, r, a=255):
    d.ellipse([x - r, y - r, x + r, y + r], fill=a)


def polar(r, ang):
    return C + r * math.cos(ang), C + r * math.sin(ang)


def leaf(d, ang, r0, r1, half_w, a=255, steps=48):
    """Round-ended leaf (vesica) from radius r0 to r1 along angle ang."""
    pts = []
    L = r1 - r0
    for side in (1, -1):
        rng = range(steps + 1) if side == 1 else range(steps, -1, -1)
        for i in rng:
            t = i / steps
            w = half_w * math.sin(math.pi * t) ** 0.8 * side
            rr = r0 + L * t
            x, y = polar(rr, ang)
            nx, ny = -math.sin(ang), math.cos(ang)
            pts.append((x + nx * w, y + ny * w))
    d.polygon(pts, fill=a)


def finish(img, glow_r=10, glow_w=0.55):
    """Downsample + a faint soft halo so the lines read as light (stylized soft)."""
    small = img.resize((N, N), Image.LANCZOS)
    halo = small.filter(ImageFilter.GaussianBlur(glow_r)).point(lambda v: min(255, int(v * glow_w)))
    return ImageChops.lighter(small, halo)


def outer():
    img = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(img)
    R = S * 0.46
    ring(d, R, 7 * SS)                       # main outer ring (thick)
    ring(d, R - 16 * SS, 2 * SS, 200)        # thin companion ring
    ring(d, R * 0.80, 3 * SS, 220)           # inner edge of the band
    for i in range(24):                      # ticks inside the band
        a = i / 24 * math.tau
        x0, y0 = polar(R - 22 * SS, a)
        x1, y1 = polar(R * 0.80 + 8 * SS, a)
        if i % 2 == 0:
            continue
        d.line([x0, y0, x1, y1], fill=170, width=2 * SS)
    for i in range(12):                      # dots: big / small alternating rhythm
        a = i / 12 * math.tau
        x, y = polar((R - 16 * SS + R * 0.80) / 2, a)
        dot(d, x, y, (9 if i % 2 == 0 else 5) * SS)
    for i in range(6):                       # small arcs outside the main ring
        a0 = math.degrees(i / 6 * math.tau) + 10
        r = R + 10 * SS
        d.arc([C - r, C - r, C + r, C + r], a0, a0 + 40, fill=200, width=3 * SS)
    return finish(img)


def inner():
    img = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(img)
    R = S * 0.46
    ring(d, R, 4 * SS)
    for i in range(6):                       # six round leaf petals, like a flower
        a = i / 6 * math.tau - math.pi / 2
        leaf(d, a, R * 0.22, R * 0.92, R * 0.17, 255)
        leaf(d, a, R * 0.30, R * 0.84, R * 0.10, 0)      # hollow centre -> outline petal
        x, y = polar(R * 0.58, a)
        dot(d, x, y, 6 * SS, 230)                         # seed dot inside each petal
    for i in range(6):                       # tiny dots between petals
        a = (i + 0.5) / 6 * math.tau - math.pi / 2
        x, y = polar(R * 0.78, a)
        dot(d, x, y, 4 * SS, 200)
    ring(d, R * 0.20, 4 * SS)                # centre ring + core dot
    dot(d, C, C, 9 * SS, 230)
    return finish(img, 8, 0.6)


def beam():
    x = np.linspace(0, 1, N)[None, :]        # 0 = left (top of the column), 1 = right (ground)
    y = np.linspace(-1, 1, N)[:, None]
    along = np.clip(x, 0, 1) ** 1.6          # bright at the ground, fading upward
    along *= np.clip(1 - np.clip(x - 0.94, 0, 1) / 0.06, 0, 1)   # soft cut at the very bottom edge
    across = np.exp(-(y / 0.42) ** 2)        # soft width
    core = np.exp(-(y / 0.12) ** 2) * 0.6    # brighter thin core
    v = np.clip(along * (across * 0.7 + core), 0, 1)
    return Image.fromarray((v * 255).astype("uint8"))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for name, fn in (("T_HealCircle_RuneOuter", outer), ("T_HealCircle_RuneInner", inner), ("T_HealCircle_Beam", beam)):
        p = os.path.join(out, name + ".png")
        fn().convert("RGB").save(p)
        print(p)


if __name__ == "__main__":
    main()
