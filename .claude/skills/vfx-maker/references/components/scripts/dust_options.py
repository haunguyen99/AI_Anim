"""Options preview for component 05 Dust (spec: ../05_Dust.md). 2D mock, not Unity.

  python -I dust_options.py <project_root> <out_png>

Rows = texture styles A/B/C, columns = texture + Ground (3 times) + Air + Dir, camera 3/4 (40 deg down).
Alpha blend; tint = Dust slot (light #CDBBA6, shadow from the texture tones).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

LIB = "Docs/VFX/_ArtDirection/tools/shape_library/smoke/"
CELL = 300
M_PER_PX = 5.0 / CELL
TINT = np.array([205, 187, 166]) / 255


def load_cells(path, cols, rows, mode):
    im = Image.open(path)
    if im.mode == "RGBA":
        a = np.asarray(im, np.float32) / 255
        rgb, al = a[..., :3], a[..., 3]
    else:
        l = np.asarray(im.convert("L"), np.float32) / 255
        if mode == "toon":       # white body + grey shadow: shape = anything above black, tone = L
            al = np.clip(l * 4, 0, 1)
            rgb = np.repeat(np.clip(l / np.maximum(al, 1e-3), 0, 1)[..., None], 3, 2)
        else:                    # soft: shape in L, almost white colour
            al = np.clip(l * 1.3, 0, 1)
            rgb = np.repeat((0.8 + 0.2 * l)[..., None], 3, 2)
    h, w = al.shape
    ch, cw = h // rows, w // cols
    out = []
    for r in range(rows):
        for c in range(cols):
            out.append(np.dstack([rgb[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw], al[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw]]))
    return out


def project(p):
    c, s = math.cos(math.radians(40)), math.sin(math.radians(40))
    return p[0], p[1] * c + p[2] * s, p[2] * c - p[1] * s   # x, screen-up, depth


def puffs(ctx, t, rng):
    n = {"ground": 12, "air": 9, "dir": 9}[ctx]
    out = []
    for i in range(n):
        if ctx == "ground":
            ph = rng.uniform(0, 2 * math.pi)
            d = np.array([math.cos(ph), rng.uniform(0.05, 0.25), math.sin(ph)]); spd = rng.uniform(2.5, 4.5); up = 0.35
            p0 = np.array([math.cos(ph) * 0.3, 0.15, math.sin(ph) * 0.3])
        elif ctx == "air":
            d = rng.normal(size=3); d /= np.linalg.norm(d); spd = rng.uniform(1.2, 2.5); up = 0.4
            p0 = d * 0.2
        else:
            th = math.radians(rng.uniform(0, 35)); ph = rng.uniform(0, 2 * math.pi)
            d = np.array([math.cos(th), math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph)]); spd = rng.uniform(2.5, 4.5); up = 0.3
            p0 = np.array([0.2, 0, 0])
        life = rng.uniform(0.8, 1.2)
        delay = rng.uniform(0, 0.08)
        tt = t - delay
        if tt <= 0 or tt >= life:
            continue
        drag = 3.0
        p = p0 + d * spd * (1 - math.exp(-drag * tt)) / drag + np.array([0, up * tt, 0])
        out.append((p, tt / life, rng.uniform(0, 360), rng.uniform(0.7, 1.1), rng.integers(0, 1 << 30)))
    return out


def render(style, cells, ctx, t, seed=3):
    rng = np.random.default_rng(seed)
    img = np.zeros((CELL, CELL, 3), np.float32) + 0.075
    ox, oy = CELL * (0.35 if ctx == "dir" else 0.5), CELL * (0.68 if ctx == "ground" else 0.55)
    if ctx == "ground":
        img[int(oy):int(oy) + 1] = 0.2
    ps = puffs(ctx, t, rng)
    ps.sort(key=lambda q: -project(q[0])[2])            # far first
    for p, k, rot, sz, pick in ps:
        if style == "A":
            cell = cells[min(int(k * len(cells)), len(cells) - 1)]; grow = 1.0   # sequence: growth + dissolve in the sheet
            fade = 1.0
        elif style == "B":
            cell = cells[pick % len(cells)]; grow = 0.5 + 0.9 * (1 - (1 - k) ** 2)
            fade = 1 - max(0, (k - 0.3) / 0.7)
        else:
            cell = cells[pick % len(cells)]; grow = (0.55 + 0.6 * min(k / 0.25, 1)) * (1 if k < 0.6 else 1 - (k - 0.6) / 0.4)
            fade = 1.0
        size_m = 1.5 * sz * grow
        px = max(int(size_m / M_PER_PX), 2)
        im = Image.fromarray((cell * 255).astype(np.uint8), "RGBA").resize((px, px), Image.BILINEAR).rotate(rot, Image.BILINEAR)
        a = np.asarray(im, np.float32) / 255
        sx, sy, _ = project(p)
        cx, cy = int(ox + sx / M_PER_PX - px / 2), int(oy - sy / M_PER_PX - px / 2)
        xs, ys, xe, ye = max(cx, 0), max(cy, 0), min(cx + px, CELL), min(cy + px, CELL)
        if xe <= xs or ye <= ys:
            continue
        sub = a[ys - cy:ye - cy, xs - cx:xe - cx]
        al = sub[..., 3:4] * fade * 0.9
        img[ys:ye, xs:xe] = img[ys:ye, xs:xe] * (1 - al) + sub[..., :3] * TINT * al
    img[int(oy) - 2:int(oy) + 3, int(ox) - 2:int(ox) + 3] = [0.8, 0.1, 0.1]
    return np.clip(img, 0, 1)


def main():
    root, out = sys.argv[1], sys.argv[2]
    styles = [
        ("A Toon puff (sheet 4x4)", "A", load_cells(os.path.join(root, "Assets/VFX/SmokeStylized/Textures/T_SmokeStylized3D_Puff_4x4.png"), 4, 4, "rgba")),
        ("B Soft (smoke_smoke_0x)", "B", [load_cells(os.path.join(root, LIB + "smoke_smoke_%02d.png" % i), 1, 1, "soft")[0] for i in (1, 2, 4, 5, 6, 7)]),
        ("C Toon khoi phang 2x2", "C", load_cells(os.path.join(root, LIB + "smoke_cloud_hardshadow.png"), 2, 2, "toon")),
    ]
    cols = [("texture", None, 0), ("Ground 0.15s", "ground", 0.15), ("Ground 0.45s", "ground", 0.45),
            ("Ground 0.85s", "ground", 0.85), ("Air 0.45s", "air", 0.45), ("Dir 0.45s", "dir", 0.45)]
    pad, lw = 24, 150
    sheet = Image.new("RGB", (lw + CELL * len(cols), pad + CELL * len(styles)), (18, 18, 18))
    dr = ImageDraw.Draw(sheet)
    for j, (lab, _, _) in enumerate(cols):
        dr.text((lw + j * CELL + 8, 6), lab, fill=(220, 220, 220))
    for i, (lab, st, cells) in enumerate(styles):
        dr.text((6, pad + i * CELL + CELL // 2), lab, fill=(255, 210, 120))
        for j, (_, ctx, t) in enumerate(cols):
            if ctx is None:
                n = len(cells); g = math.ceil(math.sqrt(n)); c = CELL // g
                tile = Image.new("RGB", (CELL, CELL), (55, 55, 62))
                for k, cell in enumerate(cells):
                    im = Image.fromarray((cell * 255).astype(np.uint8), "RGBA").resize((c, c))
                    bg = Image.new("RGBA", (c, c), (55, 55, 62, 255)); bg.alpha_composite(im)
                    tile.paste(bg.convert("RGB"), ((k % g) * c, (k // g) * c))
            else:
                tile = Image.fromarray((render(st, cells, ctx, t) * 255).astype(np.uint8), "RGB")
            sheet.paste(tile, (lw + j * CELL, pad + i * CELL))
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
