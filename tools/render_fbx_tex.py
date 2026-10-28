"""Render tĩnh một FBX (bind pose) có texture bảng màu, không cần Blender/GPU: mỗi tam giác tô phẳng theo màu
lấy ở UV (trung bình các góc), đổ sáng lambert, z-buffer numpy. Dùng làm ảnh ref đúng màu cho Codex (giai đoạn 0).

    .venv/Scripts/python.exe -I tools/render_fbx_tex.py model.fbx texture.tga out_dir [--size 1024]
      [--views front,side_r,side_l,q34,back] [--only mesh1,mesh2] [--skip mesh3] [--name prefix]

Trục: FBX Y lên, nhân vật nhìn +Z. side_r = camera ở bên phải nhân vật (−X), nhân vật quay sang PHẢI màn hình.
"""
import argparse, os, sys
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fbx_replace_mesh as R

VIEWS = {  # (hướng nhìn của camera = từ camera tới nhân vật), trục lên
    "front": np.array([0, 0, -1.0]), "back": np.array([0, 0, 1.0]),
    "side_r": np.array([1.0, 0, 0]), "side_l": np.array([-1.0, 0, 0]),
    "q34": np.array([0.6, -0.15, -0.78]),
}


def load(path, tex, only=None, skip=()):
    f = R.Fbx(path)
    T = np.asarray(Image.open(tex).convert("RGB"), float) / 255.0
    H, W = T.shape[:2]
    tris, cols = [], []
    for i, (o, pr) in f.obj.items():
        if o[0] != "Model" or pr[2] != "Mesh": continue
        name = f.name(i)
        if (only and name not in only) or name in skip: continue
        d = R.geo_data(f, f.geometry(i))
        M = f.world(i)
        V = (np.c_[d["V"], np.ones(len(d["V"]))] @ M.T)[:, :3]
        UV = d["UV"].reshape(-1, 2)[d["UVI"]]
        poly, start = [], 0
        for k, idx in enumerate(d["P"]):
            poly.append(k)
            if idx < 0:
                vi = [d["P"][j] if d["P"][j] >= 0 else ~d["P"][j] for j in poly]
                uv = UV[poly]
                px = np.clip((uv[:, 0] * W).astype(int), 0, W - 1)
                py = np.clip(((1 - uv[:, 1]) * H).astype(int), 0, H - 1)
                c = T[py, px].mean(0)
                for t in range(1, len(vi) - 1):
                    tris.append(V[[vi[0], vi[t], vi[t + 1]]]); cols.append(c)
                poly = []
        print("  %-32s %5d tam giác" % (name, len(tris)))
    return np.array(tris), np.array(cols)


def render(tris, cols, view, size, pad=0.06, bg=(0.33, 0.35, 0.38)):
    fwd = VIEWS[view] / np.linalg.norm(VIEWS[view])
    up0 = np.array([0, 1.0, 0])
    right = np.cross(fwd, up0); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    X, Y, Z = tris @ right, tris @ up, tris @ fwd        # Z: xa camera thì lớn
    lo = np.array([X.min(), Y.min()]); hi = np.array([X.max(), Y.max()])
    s = (1 - 2 * pad) * size / (hi - lo).max()
    cx = (lo + hi) / 2
    px = (X - cx[0]) * s + size / 2
    py = size / 2 - (Y - cx[1]) * s
    img = np.ones((size, size, 3)) * bg
    zb = np.full((size, size), np.inf)
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    L = -fwd * 0.6 + up * 0.6 + right * 0.3; L /= np.linalg.norm(L)
    shade = 0.62 + 0.38 * np.abs(n @ L)                   # hai mặt (mesh game hay lật normal)
    for t in range(len(tris)):
        x, y, z = px[t], py[t], Z[t]
        x0, x1 = max(int(x.min()), 0), min(int(x.max()) + 1, size)
        y0, y1 = max(int(y.min()), 0), min(int(y.max()) + 1, size)
        if x0 >= x1 or y0 >= y1: continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(d) < 1e-9: continue
        a = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
        b = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
        c = 1 - a - b
        m = (a >= -1e-4) & (b >= -1e-4) & (c >= -1e-4)
        zz = a * z[0] + b * z[1] + c * z[2]
        sub = zb[y0:y1, x0:x1]
        w = m & (zz < sub)
        sub[w] = zz[w]
        img[y0:y1, x0:x1][w] = cols[t] * shade[t]
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fbx"); ap.add_argument("tex"); ap.add_argument("out")
    ap.add_argument("--size", type=int, default=1024)
    ap.add_argument("--views", default="front,side_r,q34")
    ap.add_argument("--only", default=""); ap.add_argument("--skip", default="")
    ap.add_argument("--name", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    only = set(x for x in a.only.split(",") if x); skip = set(x for x in a.skip.split(",") if x)
    tris, cols = load(a.fbx, a.tex, only, skip)
    for v in a.views.split(","):
        p = os.path.join(a.out, "%s%s.png" % (a.name, v))
        render(tris, cols, v, a.size).save(p); print(p)


if __name__ == "__main__":
    main()
