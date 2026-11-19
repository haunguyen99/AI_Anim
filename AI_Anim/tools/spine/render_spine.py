"""Small preview renderer for simple Spine 4.2 JSON skeletons.
Supports bone translate/rotate/scale timelines, slot alpha, region and
(weighted or unweighted) mesh attachments.

usage: render_spine.py skel.json images_dir anim out_prefix
         [--bg img.png | --bgcolor 1c3a5c] [--at X Y] [--scale S] [--size W H]
         [--loops N] [--frames 0,4,8] [--cross] [--ss 2] [--png_dir dir]
"""
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument("skel"); ap.add_argument("images"); ap.add_argument("anim"); ap.add_argument("out")
ap.add_argument("--bg"); ap.add_argument("--bgcolor", default="1c3a5c")
ap.add_argument("--at", nargs=2, type=float); ap.add_argument("--scale", type=float, default=1.0)
ap.add_argument("--size", nargs=2, type=int, default=[320, 320])
ap.add_argument("--loops", type=int, default=1); ap.add_argument("--frames", default="0,4,8,10,13,16,19,25")
ap.add_argument("--cross", action="store_true"); ap.add_argument("--ss", type=int, default=2)
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--skin", help="tên skin (gộp với skin default); mặc định: skin đầu tiên")
ap.add_argument("--png_dir", help="also save every frame as PNG (f_0001.png...) for a playblast video")
A = ap.parse_args()

data = json.loads(Path(A.skel).read_text(encoding="utf-8"))
anim = data["animations"][A.anim]
bones = data["bones"]
bidx = {b["name"]: i for i, b in enumerate(bones)}
if A.skin:   # skin default + skin được chọn (skin chọn đè)
    skin = {}
    for sk in data["skins"]:
        if sk["name"] in ("default", A.skin):
            for sl, atts in sk.get("attachments", {}).items():
                skin.setdefault(sl, {}).update(atts)
    assert any(sk["name"] == A.skin for sk in data["skins"]), "không có skin " + A.skin
else:
    skin = data["skins"][0]["attachments"]
if A.bg:
    BG = Image.open(A.bg).convert("RGBA")
else:
    BG = Image.new("RGBA", tuple(A.size), "#" + A.bgcolor)
OX, OY = A.at if A.at else (BG.width / 2, BG.height / 2)
SS = A.ss


def bez_y(t1, v1, c, t2, v2, t):
    cx1, cy1, cx2, cy2 = c
    lo, hi = 0.0, 1.0
    for _ in range(40):
        s = (lo + hi) / 2
        x = (1-s)**3*t1 + 3*(1-s)**2*s*cx1 + 3*(1-s)*s**2*cx2 + s**3*t2
        lo, hi = (s, hi) if x < t else (lo, s)
    s = (lo + hi) / 2
    return (1-s)**3*v1 + 3*(1-s)**2*s*cy1 + 3*(1-s)*s**2*cy2 + s**3*v2


def sample(keys, t, fields, defaults):
    if not keys:
        return list(defaults)
    vals = lambda k: [k.get(fl, d) for fl, d in zip(fields, defaults)]
    if t <= keys[0].get("time", 0):
        return vals(keys[0])
    for a, b in zip(keys, keys[1:]):
        ta, tb = a.get("time", 0), b.get("time", 0)
        if ta <= t < tb:
            va, vb, c = vals(a), vals(b), a.get("curve")
            if c == "stepped":
                return va
            return [bez_y(ta, va[i], c[i*4:i*4+4], tb, vb[i], t) if isinstance(c, list)
                    else va[i] + (vb[i]-va[i]) * (t-ta)/(tb-ta) for i in range(len(fields))]
    return vals(keys[-1])


def local_mat(x, y, rot, sx, sy):
    r = math.radians(rot)
    return (math.cos(r)*sx, -math.sin(r)*sy, math.sin(r)*sx, math.cos(r)*sy, x, y)


def mul(p, l):
    a, b, c, d, x, y = p; la, lb, lc, ld, lx, ly = l
    return (a*la + b*lc, a*lb + b*ld, c*la + d*lc, c*lb + d*ld, a*lx + b*ly + x, c*lx + d*ly + y)


def apply(m, px, py):
    a, b, c, d, x, y = m
    return (a*px + b*py + x, c*px + d*py + y)


def pose_world(t):
    W = []
    for b in bones:
        tl = anim.get("bones", {}).get(b["name"], {})
        dx, dy = sample(tl.get("translate"), t, ["x", "y"], [0, 0])
        sx, sy = sample(tl.get("scale"), t, ["x", "y"], [1, 1])
        (r,) = sample(tl.get("rotate"), t, ["value"], [0])
        lm = local_mat(b.get("x", 0) + dx, b.get("y", 0) + dy, b.get("rotation", 0) + r,
                       b.get("scaleX", 1) * sx, b.get("scaleY", 1) * sy)
        W.append(mul(W[bidx[b["parent"]]], lm) if "parent" in b else lm)
    return W


textures = {}


def tex(name):
    if name not in textures:
        textures[name] = Image.open(Path(A.images) / f"{name}.png").convert("RGBA")
    return textures[name]


def geometry(att, slot_bone, W):
    """Return (uv list, world vertex list, triangle index list)."""
    if att.get("type", "region") == "region":
        w, h = att["width"], att["height"]
        sx, sy = att.get("scaleX", 1), att.get("scaleY", 1)
        r = math.radians(att.get("rotation", 0))
        loc = []
        for lx, ly in ((-w/2, h/2), (w/2, h/2), (w/2, -h/2), (-w/2, -h/2)):
            lx, ly = lx * sx, ly * sy
            loc.append((att.get("x", 0) + lx*math.cos(r) - ly*math.sin(r),
                        att.get("y", 0) + lx*math.sin(r) + ly*math.cos(r)))
        m = W[bidx[slot_bone]]
        return [(0, 0), (1, 0), (1, 1), (0, 1)], [apply(m, *p) for p in loc], [0, 1, 2, 0, 2, 3]
    uv = att["uvs"]; uvs = [(uv[i], uv[i+1]) for i in range(0, len(uv), 2)]
    v = att["vertices"]; out = []
    if len(v) == len(uv):   # unweighted
        m = W[bidx[slot_bone]]
        out = [apply(m, v[i], v[i+1]) for i in range(0, len(v), 2)]
    else:
        i = 0
        while i < len(v):
            n = int(v[i]); i += 1; wx = wy = 0.0
            for _ in range(n):
                bi, bx, by, w = int(v[i]), v[i+1], v[i+2], v[i+3]; i += 4
                px, py = apply(W[bi], bx, by); wx += px * w; wy += py * w
            out.append((wx, wy))
    return uvs, out, att["triangles"]


def affine_from(dst, src):
    """Coeffs mapping output (dst) pixel -> input (src) pixel for Image.transform."""
    (x0, y0), (x1, y1), (x2, y2) = dst
    (u0, v0), (u1, v1), (u2, v2) = src
    det = (x1-x0)*(y2-y0) - (x2-x0)*(y1-y0)
    if abs(det) < 1e-9:
        return None
    a = ((u1-u0)*(y2-y0) - (u2-u0)*(y1-y0)) / det
    b = ((u2-u0)*(x1-x0) - (u1-u0)*(x2-x0)) / det
    d = ((v1-v0)*(y2-y0) - (v2-v0)*(y1-y0)) / det
    e = ((v2-v0)*(x1-x0) - (v1-v0)*(x2-x0)) / det
    return a, b, u0 - a*x0 - b*y0, d, e, v0 - d*x0 - e*y0


tri_alpha_cache = {}


def draw_attachment(layer, name, uvs, pts, tris, scale):
    src = tex(name); sw, sh = src.size
    S = [(u * sw, v * sh) for u, v in uvs]
    D = [((OX + x * scale) * SS, (OY - y * scale) * SS) for x, y in pts]
    for k in range(0, len(tris), 3):
        ia, ib, ic = tris[k:k+3]
        key = (name, ia, ib, ic)
        if key not in tri_alpha_cache:   # skip fully transparent triangles
            m = Image.new("L", src.size, 0)
            ImageDraw.Draw(m).polygon([S[ia], S[ib], S[ic]], fill=255, outline=255)
            covered = Image.composite(src.getchannel("A"), Image.new("L", src.size, 0), m)
            tri_alpha_cache[key] = covered.getbbox() is not None
        if not tri_alpha_cache[key]:
            continue
        d3 = [D[ia], D[ib], D[ic]]
        x0 = math.floor(min(p[0] for p in d3)) - 1; y0 = math.floor(min(p[1] for p in d3)) - 1
        x1 = math.ceil(max(p[0] for p in d3)) + 1; y1 = math.ceil(max(p[1] for p in d3)) + 1
        if x1 <= 0 or y1 <= 0 or x0 >= layer.width or y0 >= layer.height:
            continue
        loc = [(p[0] - x0, p[1] - y0) for p in d3]
        co = affine_from(loc, [S[ia], S[ib], S[ic]])
        if co is None:
            continue
        piece = src.transform((x1 - x0, y1 - y0), Image.AFFINE, co, resample=Image.BILINEAR)
        mask = Image.new("L", piece.size, 0)
        ImageDraw.Draw(mask).polygon(loc, fill=255, outline=255)
        piece.putalpha(Image.composite(piece.getchannel("A"), Image.new("L", piece.size, 0), mask))
        layer.paste(Image.alpha_composite(layer.crop((x0, y0, x1, y1)), piece), (x0, y0))


def frame(t):
    W = pose_world(t)
    canvas = BG.copy()
    for slot in data["slots"]:
        name = slot.get("attachment")
        if not name:
            continue
        alpha = int(slot.get("color", "ffffffff")[6:8], 16) / 255
        stl = anim.get("slots", {}).get(slot["name"], {})
        if "attachment" in stl:   # đổi / ẩn attachment theo thời gian (key cuối có time <= t)
            for k in stl["attachment"]:
                if k.get("time", 0) <= t + 1e-6:
                    name = k.get("name")
            if not name:
                continue
        if "alpha" in stl:
            (alpha,) = sample(stl["alpha"], t, ["value"], [1])
        if alpha <= 0.01:
            continue
        uvs, pts, tris = geometry(skin[slot["name"]][name], slot["bone"], W)
        layer = Image.new("RGBA", (canvas.width * SS, canvas.height * SS), (0, 0, 0, 0))
        draw_attachment(layer, skin[slot["name"]][name].get("path", name), uvs, pts, tris, A.scale)
        layer = layer.resize(canvas.size, Image.LANCZOS)
        if alpha < 1:
            layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
        canvas = Image.alpha_composite(canvas, layer)
    if A.cross:
        d = ImageDraw.Draw(canvas)
        d.line((OX-6, OY, OX+6, OY), fill=(255, 60, 60), width=2)
        d.line((OX, OY-6, OX, OY+6), fill=(255, 60, 60), width=2)
    return canvas


dur = max([k.get("time", 0) for tl in anim.get("bones", {}).values() for ks in tl.values() for k in ks]
          + [e.get("time", 0) for e in anim.get("events", [])] + [1.0])   # an end event holds the last pose
n = round(dur * A.fps)
frames = [frame(i / A.fps) for i in range(n)]
out = Path(A.out)
if A.png_dir:   # full-colour frames for a playblast video (ffmpeg -i f_%04d.png)
    Path(A.png_dir).mkdir(parents=True, exist_ok=True)
    for i, fr in enumerate(frames):
        fr.convert("RGB").save(Path(A.png_dir) / f"f_{i + 1:04d}.png")
allf = frames * A.loops
pal = [fr.convert("RGB").quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG) for fr in allf]
pal[0].save(out.with_suffix(".gif"), save_all=True, append_images=pal[1:], duration=round(1000 / A.fps), loop=0)

picks = [int(x) for x in A.frames.split(",") if x]
w, h = frames[0].size
cols = min(4, len(picks)); rows = math.ceil(len(picks) / cols)
sheet = Image.new("RGBA", (w * cols, (h + 22) * rows), (15, 15, 15, 255))
sd = ImageDraw.Draw(sheet)
for i, fr in enumerate(picks):
    x, y = (i % cols) * w, (i // cols) * (h + 22)
    sheet.paste(frames[fr], (x, y + 22))
    sd.text((x + 6, y + 5), f"frame {fr} ({fr / A.fps:.2f}s)", fill=(230, 230, 230))
sheet.save(out.with_name(out.stem + "_frames.png"))
print("rendered", n, "frames ->", out.with_suffix(".gif"))
