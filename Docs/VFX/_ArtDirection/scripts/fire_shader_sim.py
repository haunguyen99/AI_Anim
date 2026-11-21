"""CPU mirror of SH_VFX_FireStylized.shader for fast look-dev (numpy). Keep in sync with the shader.
  python fire_shader_sim.py NOISE_PNG OUT_DIR [key=value ...]
"""
import sys, os, math
import numpy as np
from PIL import Image

P = dict(nax=1.1, nay=0.9, nbx=2.2, nby=1.8, spa=0.5, spb=1.0, dist=0.16, width=0.34, taper=0.85, sway=0.07,
         sways=math.pi, erode=0.6, b1=0.12, b2=0.32, b3=0.55, soft=0.015, y0=0.0, y1=1.0, loop=2.0,
         co=(0.85, 0.12, 0.05), cm=(1.0, 0.45, 0.08), cc=(1.0, 0.86, 0.42))


def sample(tex, u, v):
    h, w = tex.shape
    x = (u * w - 0.5) % w; y = ((1 - v) * h - 0.5) % h          # v up, image rows down
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    x1 = (x0 + 1) % w; y1 = (y0 + 1) % h
    return (tex[y0, x0] * (1 - fx) * (1 - fy) + tex[y0, x1] * fx * (1 - fy) + tex[y1, x0] * (1 - fx) * fy + tex[y1, x1] * fx * fy)


def smooth(a, b, x):
    t = np.clip((x - a) / np.maximum(b - a, 1e-6), 0, 1)
    return t * t * (3 - 2 * t)


def frame(tex, t, p, n=256):
    v, u = np.mgrid[0:n, 0:n].astype(float)
    u = (u + 0.5) / n; v = 1 - (v + 0.5) / n
    nA = sample(tex, u * p["nax"], v * p["nay"] - t * p["spa"])
    nB = sample(tex, u * p["nbx"] + 0.37, v * p["nby"] - t * p["spb"])
    nn = nA * 0.6 + nB * 0.4
    # flame space: y remapped so the flame sits between y0 and y1 of the cell
    y = (v - p["y0"]) / (p["y1"] - p["y0"])
    dx_ = u + (nA - 0.5) * p["dist"] * np.clip(y, 0, 1)
    dy = y + (nB - 0.5) * p["dist"] * np.clip(y, 0, 1)
    sway = np.sin(t * p["sways"] + dy * 3) * p["sway"] * dy
    dx = np.abs(dx_ - 0.5 - sway)
    width = p["width"] * np.power(np.clip(1 - dy, 0, 1), p["taper"]) * np.sqrt(np.clip(dy / 0.18, 0, 1))
    shape = np.clip(1 - dx / np.maximum(width, 1e-4), 0, 1) * smooth(0, 0.04, dy)
    f = shape - (1 - nn) * p["erode"] * (0.35 + 0.65 * np.clip(y, 0, 1))
    aa = 1.5 / n + p["soft"]
    a1 = smooth(p["b1"] - aa, p["b1"] + aa, f); a2 = smooth(p["b2"] - aa, p["b2"] + aa, f); a3 = smooth(p["b3"] - aa, p["b3"] + aa, f)
    co, cm, cc = (np.array(p[k]) for k in ("co", "cm", "cc"))
    col = co * (1 - a2[..., None]) + cm * a2[..., None]
    col = col * (1 - a3[..., None]) + cc * a3[..., None]
    return col, a1


def main():
    tex = np.asarray(Image.open(sys.argv[1]).convert("L"), float) / 255
    out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    p = dict(P)
    for kv in sys.argv[3:]:
        k, v = kv.split("="); p[k] = float(v)
    n = 256; bg = np.array([30, 30, 36]) / 255
    frames = []
    for i in range(16):
        col, a = frame(tex, p["loop"] * i / 16, p, n)
        rgb = col * a[..., None] + bg * (1 - a[..., None])
        frames.append(Image.fromarray((rgb * 255).astype(np.uint8)))
    sheet = Image.new("RGB", (n * 4, n * 4))
    for i, f in enumerate(frames):
        sheet.paste(f, ((i % 4) * n, (i // 4) * n))
    sheet.save(os.path.join(out, "sim_sheet.png"))
    frames[0].save(os.path.join(out, "sim_loop.gif"), save_all=True, append_images=frames[1:], duration=125, loop=0)
    print("ok")


if __name__ == "__main__":
    main()
