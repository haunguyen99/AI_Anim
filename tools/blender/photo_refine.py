# Refine head channels of solved keys by comparing renders with the reference image itself (the reference is a
# render of this very model): gradient correlation inside the head region, in the front and side views.
# Run after solve_keys.py (same namespace):  PHOTOF = [1, 45]; exec(open(r".../photo_refine.py").read())
import os
ROOT = (globals().get("ROOT") or os.environ.get("AI_ANIM_ROOT") or os.getcwd()).replace("\\", "/").rstrip("/")   # project folder: set ROOT = r"<folder>" before exec(), or env AI_ANIM_ROOT, or run from the project folder
if not os.path.exists(ROOT + "/MAP.md"):
    raise RuntimeError("Project folder not found: set ROOT = r'<project folder>' or env AI_ANIM_ROOT")
import os

import bpy
import numpy as np

REFG = np.load(ROOT + r"/work/idle/analysis/refgray.npz")
PSUB = globals().get("PSUB", ["neck_side", "head_yaw", "head_pitch", "head_roll"])
PSIG = {"neck_side": 15.0, "head_yaw": 30.0, "head_pitch": 20.0, "head_roll": 12.0, "twist": 6.0, "lean": 4.0}
PVIEWS = globals().get("PVIEWS", ["front", "left", "right"])
PIDX = [PARAMS.index(k) for k in PSUB]  # noqa: F821
_TMP = os.path.join(os.environ.get("TEMP", "C:/Temp"), "photo_refine.png")
_sc = bpy.context.scene
_save = dict(engine=_sc.render.engine, cam=_sc.camera, path=_sc.render.filepath, transp=_sc.render.film_transparent,
             pct=_sc.render.resolution_percentage, border=_sc.render.use_border, crop=_sc.render.use_crop_to_border,
             ctype=_sc.display.shading.color_type, fmt=_sc.render.image_settings.file_format,
             mode=_sc.render.image_settings.color_mode,
             b=(_sc.render.border_min_x, _sc.render.border_max_x, _sc.render.border_min_y, _sc.render.border_max_y))
_sc.render.engine = "BLENDER_WORKBENCH"; _sc.display.shading.color_type = "TEXTURE"
_sc.render.film_transparent = True; _sc.render.resolution_percentage = 50
_sc.render.image_settings.file_format = "PNG"; _sc.render.image_settings.color_mode = "RGBA"
_sc.render.use_border = True; _sc.render.use_crop_to_border = False
_ctrl_hide = bpy.data.objects["CTRL"].hide_render
bpy.data.objects["CTRL"].hide_render = True


def head_roi(view, pad=28):
    dg = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects[_MESHES[0]].evaluated_get(dg)  # noqa: F821
    a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
    M = np.array(o.matrix_world); H = (a @ M[:3, :3].T + M[:3, 3])[head_vertex_index()]  # noqa: F821
    Mi, s = _CAMS[view]  # noqa: F821
    q = H @ Mi[:3, :3].T + Mi[:3, 3]
    uv = np.c_[960 + q[:, 0] * s, 540 - q[:, 1] * s] / 2          # half-res pixels
    x0, y0 = np.floor(uv.min(0) - pad).astype(int); x1, y1 = np.ceil(uv.max(0) + pad).astype(int)
    return max(0, x0), max(0, y0), min(959, x1), min(539, y1)


def render_gray(view, roi):
    x0, y0, x1, y1 = roi
    _sc.camera = bpy.data.objects["Ref_" + view]
    _sc.render.border_min_x, _sc.render.border_max_x = x0 / 960, (x1 + 1) / 960
    _sc.render.border_min_y, _sc.render.border_max_y = 1 - (y1 + 1) / 540, 1 - y0 / 540
    _sc.render.filepath = _TMP
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(_TMP, check_existing=False)
    px = np.array(img.pixels[:], np.float32).reshape(img.size[1], img.size[0], 4)[::-1]
    bpy.data.images.remove(img)
    g = (0.114 * px[..., 2] + 0.587 * px[..., 1] + 0.299 * px[..., 0]) * 255
    g = g * px[..., 3] + 91.0 * (1 - px[..., 3])
    return g[y0:y1 + 1, x0:x1 + 1]


def grad(g):
    gy, gx = np.gradient(g.astype(np.float32))
    v = np.concatenate([gx.ravel(), gy.ravel()])
    v -= v.mean()
    return v / (np.linalg.norm(v) + 1e-6)


def photo_cost(f, rois):
    c = 0.0
    for v in PVIEWS:
        x0, y0, x1, y1 = rois[v]
        ref = REFG[f"{v}_{f}"][y0:y1 + 1, x0:x1 + 1]
        c += 1.0 - float(grad(render_gray(v, rois[v])) @ grad(ref))
    return c / len(PVIEWS)


PHOTO_LOG = {}
try:
    for _f in PHOTOF:  # noqa: F821
        pt = np.array(SOL[_f], float)  # noqa: F821
        apply(pt)  # noqa: F821
        rois = {v: head_roi(v, 40) for v in PVIEWS}

        def cost(p):
            apply(p)  # noqa: F821
            return photo_cost(_f, rois) + 0.002 * sum(((p[i] - pt[i]) / PSIG[k]) ** 2 for k, i in zip(PSUB, PIDX))

        p = pt.copy(); best = cost(p); start = best
        for step in (8.0, 4.0, 2.0):
            improved = True
            while improved:
                improved = False
                for i in PIDX:
                    for sgn in (1, -1):
                        q = p.copy(); q[i] += sgn * step
                        cq = cost(q)
                        if cq < best - 1e-4:
                            p, best, improved = q, cq, True
                            break
        SOL[_f] = p  # noqa: F821
        PHOTO_LOG[_f] = (start, best)
        print(f"f{_f:3d} photo {start:.3f} -> {best:.3f}  " + " ".join(f"{k}={pt[i]:+.0f}->{p[i]:+.0f}" for k, i in zip(PSUB, PIDX)))
finally:
    _sc.render.engine = _save["engine"]; _sc.camera = _save["cam"]; _sc.render.filepath = _save["path"]
    _sc.render.film_transparent = _save["transp"]; _sc.render.resolution_percentage = _save["pct"]
    _sc.render.use_border = _save["border"]; _sc.render.use_crop_to_border = _save["crop"]
    _sc.display.shading.color_type = _save["ctype"]; _sc.render.image_settings.file_format = _save["fmt"]
    _sc.render.image_settings.color_mode = _save["mode"]
    (_sc.render.border_min_x, _sc.render.border_max_x, _sc.render.border_min_y, _sc.render.border_max_y) = _save["b"]
    bpy.data.objects["CTRL"].hide_render = _ctrl_hide
