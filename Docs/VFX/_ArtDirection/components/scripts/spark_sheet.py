"""Spark textures + options preview for component 04 Sparks (spec: ../04_Sparks.md).

  python -I spark_sheet.py <out_dir>            # writes T_SPK_Streak/Toon/Ember.png
  python -I spark_sheet.py <out_dir> --options <png>   # also writes the A/B/C comparison sheet

Stretched Billboard rule (verified 2026-10-31): travel direction = texture LEFT edge.
So the bright HEAD is drawn at the left (u = 0) and the tail runs to the right.
RGB white + shape in alpha (Additive squares the brightness otherwise).
"""
import argparse
import math
import os

import numpy as np
from PIL import Image

W, H = 256, 64          # stretch textures: 4:1, horizontal


def streak():
    """A: soft comet. Round bright head at the left, tail tapers to a point on the right."""
    y, x = np.mgrid[0:H, 0:W]
    s = (x + 0.5) / W                     # 0 head .. 1 tail end
    v = np.abs((y + 0.5) / H * 2 - 1)     # 0 axis .. 1 edge
    half = 0.85 * (1 - s) ** 0.8 * np.clip(s / 0.06, 0, 1) ** 0.5
    body = np.clip(1 - v / np.maximum(half, 1e-4), 0, 1) ** 0.7
    body *= (1 - s) ** 0.6                # tail dimmer than head
    return np.clip(body, 0, 1)


def toon():
    """B: hard-edged needle/diamond. Widest at 18 % from the head, sharp points both ends."""
    y, x = np.mgrid[0:H, 0:W]
    s = (x + 0.5) / W
    v = np.abs((y + 0.5) / H * 2 - 1)
    p = 0.18
    half = np.where(s < p, s / p, ((1 - s) / (1 - p)) ** 1.15) * 0.8
    px = 2.0 / H
    a = np.clip(0.5 - (v - half) / (1.5 * px), 0, 1)        # crisp edge, 1.5 px AA
    core = np.clip(0.5 - (v - half * 0.35) / (1.5 * px), 0, 1)
    return np.clip(a * 0.75 + core * 0.25, 0, 1)


def ember(n=64):
    """C: round ember dot (Billboard, not stretched). Bright core + short soft falloff."""
    y, x = np.mgrid[0:n, 0:n]
    r = np.hypot((x + 0.5) / n * 2 - 1, (y + 0.5) / n * 2 - 1)
    return np.clip(np.maximum(np.clip(1 - r / 0.35, 0, 1), 0.6 * np.clip(1 - r, 0, 1) ** 2.2), 0, 1)


def save_rgba(a, path):
    g = Image.fromarray((a * 255 + 0.5).astype(np.uint8), "L")
    w = Image.new("L", g.size, 255)
    Image.merge("RGBA", (w, w, w, g)).save(path)
    print(path, g.size)


# ---------------------------------------------------------------- options preview (mock, not Unity)
CORE, MID, OUTER = np.array([255, 243, 196]) / 255, np.array([255, 154, 60]) / 255, np.array([200, 40, 30]) / 255
CELL = 300
M_PER_PX = 4.0 / CELL      # cell shows 4 m


def col_at(k):              # Core -> Mid -> Outer over life
    return CORE + (MID - CORE) * min(k / 0.4, 1) if k < 0.4 else MID + (OUTER - MID) * min((k - 0.4) / 0.6, 1)


def project(p):             # 3/4 camera, 40 deg down, looking +Z
    c, s = math.cos(math.radians(40)), math.sin(math.radians(40))
    return p[0], p[1] * c + p[2] * s


def stamp(acc, tex, cx, cy, length_px, width_px, ang, color, alpha):
    length_px, width_px = max(int(length_px), 2), max(int(width_px), 2)
    im = Image.fromarray((tex * 255).astype(np.uint8), "L").resize((length_px, width_px), Image.BILINEAR)
    # texture head is at the LEFT; rotate so the left edge points along travel (ang = travel angle on screen)
    im = im.rotate(math.degrees(ang) + 180, resample=Image.BILINEAR, expand=True)
    a = np.asarray(im, dtype=np.float32) / 255 * alpha
    h, w = a.shape
    # the head (left edge before rotation) must sit on the particle: shift centre back along travel
    hx = cx - math.cos(ang) * length_px / 2
    hy = cy + math.sin(ang) * length_px / 2
    x0, y0 = int(hx - w / 2), int(hy - h / 2)
    xs, ys = max(x0, 0), max(y0, 0)
    xe, ye = min(x0 + w, acc.shape[1]), min(y0 + h, acc.shape[0])
    if xe <= xs or ye <= ys:
        return
    acc[ys:ye, xs:xe] += a[ys - y0:ye - y0, xs - x0:xe - x0, None] * color


def simulate(kind, ctx, t, rng):
    """Return particles (pos, vel, age_k). ctx: air / dir / ground. Hit direction = +X in preview."""
    n = {"air": 22, "dir": 18, "ground": 20}[ctx]
    out = []
    for _ in range(n):
        if ctx == "air":
            d = rng.normal(size=3); d /= np.linalg.norm(d); spd = rng.uniform(4, 8); g = 1.0
        elif ctx == "dir":
            th = math.radians(rng.uniform(0, 28)); ph = rng.uniform(0, 2 * math.pi)
            d = np.array([math.cos(th), math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph)])
            spd = rng.uniform(7, 12); g = 1.0
        else:
            th = math.radians(rng.uniform(15, 75)); ph = rng.uniform(0, 2 * math.pi)
            d = np.array([math.cos(th) * math.cos(ph), math.sin(th), math.cos(th) * math.sin(ph)])
            spd = rng.uniform(4, 8); g = 9.8 * 1.2
        if kind == "C":
            spd *= 0.6; g *= 0.6
        life = rng.uniform(0.35, 0.6)
        drag = 1.6                           # Limit Velocity dampen-ish
        k = t / life
        if k >= 1:
            continue
        tt = (1 - math.exp(-drag * t)) / drag
        v = d * spd * math.exp(-drag * t) - np.array([0, g * t, 0])
        p = d * spd * tt - np.array([0, 0.5 * g * t * t, 0])
        if ctx == "ground" and p[1] < 0:
            p[1] = 0
        out.append((p, v, k))
    return out


def render(kind, ctx, t, tex, seed=7):
    rng = np.random.default_rng(seed)
    acc = np.zeros((CELL, CELL, 3), np.float32)
    ox, oy = CELL * (0.3 if ctx == "dir" else 0.5), CELL * (0.72 if ctx == "ground" else 0.5)
    for p, v, k in simulate(kind, ctx, t, rng):
        sx, sy = project(p)
        vx, vy = project(v)
        spd = math.hypot(vx, vy)
        ang = math.atan2(vy, vx)
        shrink = 1 - k
        if kind == "C":
            L = W_ = 0.22 * shrink / M_PER_PX
        else:
            L = (0.25 + spd * 0.045) * shrink / M_PER_PX   # Length Scale + Speed Scale
            W_ = (0.13 if kind == "A" else 0.15) * shrink / M_PER_PX
        stamp(acc, tex, ox + sx / M_PER_PX, oy - sy / M_PER_PX, L, W_, ang, col_at(k), 1.0)
    img = np.clip(acc, 0, 1)
    bg = np.full_like(img, 0.07)
    # ground line + hit marker
    gy = int(oy)
    if ctx == "ground":
        bg[gy:gy + 1, :, :] = 0.2
    bg[gy - 2:gy + 3, int(ox) - 2:int(ox) + 3] = [0.8, 0.1, 0.1]
    return np.clip(bg + img, 0, 1)


def options(out_png, texs):
    from PIL import ImageDraw
    cols = [("texture", None, None), ("Air 0.12s", "air", 0.12), ("Dir 0.10s", "dir", 0.10),
            ("Ground 0.12s", "ground", 0.12), ("Ground 0.28s", "ground", 0.28)]
    rows = [("A Streak", "A"), ("B Toon", "B"), ("C Ember", "C")]
    pad = 28
    sheet = Image.new("RGB", (CELL * len(cols) + 110, CELL * len(rows) + pad), (18, 18, 18))
    dr = ImageDraw.Draw(sheet)
    for j, (lab, _, _) in enumerate(cols):
        dr.text((110 + j * CELL + 8, 8), lab, fill=(220, 220, 220))
    for i, (lab, kind) in enumerate(rows):
        dr.text((8, pad + i * CELL + CELL // 2), lab, fill=(255, 210, 120))
        tex = texs[kind]
        for j, (_, ctx, t) in enumerate(cols):
            if ctx is None:
                a = Image.fromarray((tex * 255).astype(np.uint8), "L")
                a = a.resize((CELL - 40, int((CELL - 40) * tex.shape[0] / tex.shape[1])) if kind != "C" else (120, 120))
                cell = Image.new("RGB", (CELL, CELL), (40, 40, 40))
                cell.paste(Image.merge("RGB", (a, a, a)), ((CELL - a.width) // 2, (CELL - a.height) // 2))
                if kind != "C":
                    ImageDraw.Draw(cell).text((14, CELL // 2 + 40), "<- huong bay (mep TRAI)", fill=(255, 120, 120))
            else:
                cell = Image.fromarray((render(kind, ctx, t, tex) * 255).astype(np.uint8), "RGB")
            sheet.paste(cell, (110 + j * CELL, pad + i * CELL))
    sheet.save(out_png)
    print(out_png, sheet.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--options")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    texs = {"A": streak(), "B": toon(), "C": ember()}
    for k, name in (("A", "T_SPK_Streak"), ("B", "T_SPK_Toon"), ("C", "T_SPK_Ember")):
        save_rgba(texs[k], os.path.join(a.out_dir, name + ".png"))
    if a.options:
        options(a.options, texs)


if __name__ == "__main__":
    main()
