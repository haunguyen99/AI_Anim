"""Fire -> smoke mass from a 3D mesh + noise dissolve (TOTK bomb reference, video gQ_1K61VTvo 4.5-6.0 s). Alpha + Light.

Observed in the reference:
  4.7-5.2 s  billowy mass (lobes melted together), flat orange with blobby yellow hot patches, red-dark underside
  5.3-5.6 s  cools to dark; the yellow stays only in the creases between lobes (not veins over the surface)
  5.6-6.0 s  holes open and the mass tears into ragged dark shreds, hot edges on the tears while still warm, then grey
One 3D noise stuck on the surface drives everything:
  heat  = global temperature(t) + noise  -> hard toon steps of the fire ramp (blobby patches, then crease fire)
  alpha = noise > threshold(t)           -> dissolve holes; the band just above the threshold = burning edge
The mass comes from Blender, headless (metaballs, skill codefx/mesh/blender_passes.py -> passes/passes.npz = normal + noise + alpha).
"""
import json
import math
import os

import numpy as np

import codefx as cf
from smoke import blur

HERE = os.path.dirname(os.path.abspath(__file__))
FIRE = ["#2E1A16", "#6A2A1A", "#A82A14", "#E8561A", "#FF8F1F", "#FFC93C", "#FFF1A8"]
SMOKE = ["#4A3F44", "#7B6E6E"]                     # shadow / lit: 2 big smooth tones (art lead 2026-11-03: mid frames read as rock)

META = dict(
    name="CFX_SmokeMesh", size=(176, 128), origin=(88, 112), duration=1.2, loop=False, fps=30, blend="alpha",
    space=dict(context="ground", plane="billboard", camera="3/4 40", width_m=4.4, anchor="world point (ground)", background="mixed"),
    options=dict(passes=os.path.join(HERE, "passes", "passes.npz"), palette=None, smoke=None,
                 hot_end=0.8, dis_start=0.3, contrast=2.6,
                 soft=0.12, dis_blur=0.035, crease_end=0.85, seed=3, edge_px=4.0,   # art lead 2026-11-03: smoother eaten edge (1.6 px read too sharp)
                 region_contrast=2.8, region_w=0.5),
)

_cache = {}


def _passes(path):
    if path not in _cache:
        z = np.load(path)
        info = json.load(open(os.path.join(os.path.dirname(path), "passes.json")))
        info["B"] = z["B"].astype(np.float32) if "B" in z.files else None       # ball centres / radii in pass px
        _cache[path] = (z["P"].astype(np.float32), info)
    return _cache[path]


def _resize(img, H, W):
    """Bilinear resize (H0, W0, C) -> (H, W, C)."""
    H0, W0 = img.shape[:2]
    if (H0, W0) == (H, W):
        return img
    y = (np.arange(H) + 0.5) * H0 / H - 0.5
    x = (np.arange(W) + 0.5) * W0 / W - 0.5
    y0 = np.clip(np.floor(y).astype(int), 0, H0 - 2)
    x0 = np.clip(np.floor(x).astype(int), 0, W0 - 2)
    fy = np.clip(y - y0, 0, 1)[:, None, None]
    fx = np.clip(x - x0, 0, 1)[None, :, None]
    a, b = img[y0][:, x0], img[y0][:, x0 + 1]
    c, d = img[y0 + 1][:, x0], img[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def _frame(P, info, t):
    # nearest frame: blending two frames ghosts the edges (a lobe popping in shows twice)
    return P[int(round(min(max(t * info["fps"], 0), P.shape[0] - 1)))]


def _sample(img, X, Y):
    """Bilinear sample img (H, W, C) at float pixel coords X, Y (outside = 0)."""
    H, W = img.shape[:2]
    x, y = X - 0.5, Y - 0.5
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = (x - x0)[..., None], (y - y0)[..., None]
    out = np.zeros(X.shape + img.shape[2:])
    for oy, wy in ((0, 1 - fy), (1, fy)):
        for ox, wx in ((0, 1 - fx), (1, fx)):
            xi, yi = x0 + ox, y0 + oy
            ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
            v = img[np.clip(yi, 0, H - 1), np.clip(xi, 0, W - 1)] * ok[..., None]
            out = out + v * wx * wy
    return out


def _field(p, cv, o):
    """Dissolve field from a (resized) pass frame. Fixed mapping, no per-frame statistics (frame coherence)."""
    a0 = np.clip(p[..., 3], 0, 1)
    n = (p[..., 2] - 0.5) * o["contrast"] + 0.5
    sg = 0.006 * cv.H
    detail = blur(n * a0, sg) / np.maximum(blur(a0, sg), 1e-3)        # inside-only blur (background would read as 0)
    # NOT clamped: clamping made flat plateaus; when the threshold reached a plateau the whole area turned half
    # transparent at once (a dark veil at the end)
    if p.shape[2] > 5:                                                 # inside blur too: raw values on the anti-aliased
        r = (p[..., 5] - 0.5) * o["region_contrast"] + 0.5             # rim are unreliable (left a ghost outline)
        region = blur(r * a0, sg) / np.maximum(blur(a0, sg), 1e-3)
    else:
        region = detail
    return region * o["region_w"] + detail * (1 - o["region_w"])


def _edge(field, thr):
    """field > thr with a 1 px anti-aliased edge, whatever the slope of the field."""
    gy, gx = np.gradient(field)
    return cf.clamp(0.5 + (field - thr) / (np.sqrt(gx * gx + gy * gy) + 1e-6))


def draw(cv, t, o):
    D = META["duration"]
    if t >= D:
        return
    P, info = _passes(o["passes"])
    fi = int(round(min(max(t * info["fps"], 0), P.shape[0] - 1)))
    p = _resize(P[fi], cv.H, cv.W)
    a0 = cf.clamp(p[..., 3])
    if a0.max() < 0.01:
        return
    nx, ny = p[..., 0] * 2 - 1, p[..., 1] * 2 - 1
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    n = cf.clamp((p[..., 2] - 0.5) * o["contrast"] + 0.5)          # stretch the noise to 0..1

    fire = cf.ramp(o["palette"] or FIRE)
    smoke = cf.ramp(o["smoke"] or SMOKE)
    # light from the top-left-front (camera space: x right, y up, z to the viewer)
    Ld = np.array([-0.45, 0.7, 0.55])
    Ld /= np.linalg.norm(Ld)
    lam = np.clip(nx * Ld[0] + ny * Ld[1] + nz * Ld[2], 0, 1)
    if p.shape[2] > 4:                                              # AO pass: creases between lobes go to shadow
        lam = lam * cf.clamp(p[..., 4]) ** 2

    # ---- temperature: white flash -> hot orange -> cool. Heat patches follow the noise, lit side a bit hotter
    # smooth (blurred) noise for everything big: heat patches, smoke tone border, holes. Fine noise = rock texture.
    nd = blur(n * a0, o["dis_blur"] * cv.H) / np.maximum(blur(a0, o["dis_blur"] * cv.H), 1e-3)   # inside-only blur
    nd = cf.clamp((nd - 0.5) * 1.6 + 0.5)
    T = 1.05 - 0.3 * float(cf.seg(0.0, 0.15, t)) ** 0.6 - 1.0 * float(cf.smooth(0.15, o["hot_end"], t))
    # fire retreats into the core (rim cools first): reads as fire inside smoke, not a crust of lava
    heat = T + (nd - 0.5) * 1.0 + (lam - 0.5) * 0.25 - (1 - nz) * 0.35 * float(cf.smooth(0.12, 0.4, t))
    # the whole mass is fire at first (no grey rim around a fire sticker), then smoke creeps in from the rim
    heat = np.maximum(heat, 0.3 * (1 - float(cf.smooth(0.08, 0.3, t))))
    # fire in the CREASES only (art lead 2026-11-03, reference 5.0-5.4 s: yellow shows in the gaps between lobes, not
    # as veins all over the surface). Crease mask = the AO pass, widened a little, broken up by the smooth noise.
    if p.shape[2] > 4:
        crease = cf.clamp((0.975 - p[..., 4]) / 0.07)                  # thin lines along the seams between lobes
        crease = blur(crease, 0.004 * cv.H)                            # just enough to keep the line smooth
        crease = crease * cf.smooth(0.3, 0.5, nd)                      # gaps in the glow: only some stretches burn
        crease_k = 1 - float(cf.smooth(0.35, o["crease_end"], t))
        heat = np.maximum(heat, crease * (0.35 + 0.6 * crease_k) * (crease_k > 0.02))

    # ---- dissolve, CONTROLLED BY NOISE (art lead 2026-11-03: the arc dissolve looked bad -> dropped; "control the
    # dissolving area with noise"). Two noises, both computed IN BLENDER on the surface and FIXED in time:
    #  - REGION noise (pass channel 5, very large): which areas go first and which hold on -> uneven rhythm
    #  - DETAIL noise (pass channel 2): the edge of the holes
    # FRAME COHERENCE (art lead 2026-11-03: "later frames do not match the earlier ones"): the threshold rises on ONE
    # fixed scale for the whole effect (no per-frame normalising / area quantile) and the noise never changes, so a
    # point that has dissolved never comes back.
    field = _field(p, cv, o)
    Bp = info.get("B")
    if Bp is not None:                                                 # ball centres: only used for the drift below
        k = cv.W / P.shape[2]
        bx, by, br = Bp[fi, :, 0] * k, Bp[fi, :, 1] * k, np.maximum(Bp[fi, :, 2] * k, 1.0)
    key = ("rng", cv.W, cv.H)
    if key not in info:                                                # field range at the start of the dissolve, once
        f0 = int(round(o["dis_start"] * info["fps"]))
        p0 = _resize(P[f0], cv.H, cv.W)
        fv = _field(p0, cv, o)[p0[..., 3] > 0.5]
        info[key] = np.sort(fv)
    # ONE fixed curve thr(prog) for the whole effect, built once from the reference frame so the area goes evenly
    # (a plain linear scale held the mass until ~0.8 s and then dropped it all at once)
    ref = info[key]
    prog = float(cf.seg(o["dis_start"], D * 0.97, t)) ** 1.2
    margin = (ref[-1] - ref[0]) * 0.06
    if prog <= 0:
        thr = ref[0] - margin * 2
    elif prog >= 1:
        thr = ref[-1] + margin * 2
    else:
        thr = float(np.interp(prog, np.linspace(0, 1, len(ref)), ref))
    # soft eaten edge of an EVEN width in pixels (art lead: not hard / sharp). A band in field units blurred wide
    # wherever the field is flat -> round blurry holes.
    gy, gx = np.gradient(field)
    g = np.sqrt(gx * gx + gy * gy) + 1e-6
    alive = cf.smooth(0.0, 1.0, 0.5 + (field - thr) / (g * o["edge_px"] * cv.res))
    # glow band along the eaten edge, a few px wide everywhere (a band in field units smeared into orange smudges)
    # ...and ONLY next to a hole that is really open: in flat noise just above the threshold it glowed in contour
    # rings before any hole existed (orange smudges)
    eaten = a0 * (1 - alive)
    bw = (o["edge_px"] * 0.6 + 1.5) * cv.res                          # burn band: thin (a wide one smeared orange fringes)
    near = cf.clamp(blur(eaten, bw * 0.6) * 5.0)
    burn = cf.clamp(1 - (field - thr) / (g * bw)) * (field > thr) * near
    burn_k = 1 - float(cf.smooth(0.3, o["hot_end"], t))                # burning edges only while there is fire

    # ---- colour: fire steps where hot, smoke tones (lit / mid / shadow) where cool
    nf = len(fire)
    fire_col = cf.at(fire, cf.clamp(heat))
    # 2 tones: big lit area, shadow on the underside and in the creases; border only gently wobbled
    lit = (lam + (nd - 0.5) * 0.15) > 0.33
    smoke_col = np.where(lit[..., None], smoke[-1], smoke[0])
    # skip the 2 darkest fire steps (hard dark ring); the bar rises so ALL fire is gone by hot_end (with a noise that
    # never changes, the hottest noise spots stayed as red "eyes" in the smoke until the end)
    cool = heat < 0.24 + 0.8 * float(cf.smooth(0.45, o["hot_end"], t))
    col = np.where(cool[..., None], smoke_col, fire_col)
    # warm eaten edge blends toward the fire colour (no hard dark rim)
    if burn_k > 0.05:
        col = cf.mix(col, fire[nf - 3], (burn * burn_k * 0.8)[..., None])

    A = a0 * alive

    # ---- light layer: glow on hot areas and burning edges
    hot_glow = cf.clamp((heat - 0.45) * 1.6) * A
    lt = cf.blend(fire, cf.clamp(heat)) * hot_glow[..., None] * 0.35
    if burn_k > 0.05:
        lt = lt + fire[nf - 3] * (burn * A * burn_k * 0.35)[..., None]

    # ---- drift while dissolving (reference 5.6-6.1 s): what is left spreads out, curls up at the sides and rises
    e = float(cf.smooth(o["dis_start"] + 0.15, D, t))
    if e > 0 and Bp is not None:
        cx, cy = bx[0], by[0]
        Rm = br[0] * 2.2
        yy, xx = np.mgrid[0:cv.H, 0:cv.W].astype(np.float64)
        dx, dy = xx - cx, yy - (cy - 0.03 * cv.H * e)
        r = np.hypot(dx, dy)
        side = np.tanh(dx / (0.35 * Rm))                               # smooth left/right (a hard sign() tore a seam down the middle)
        th = -0.4 * e * np.clip(r / Rm, 0, 1) * side                   # sides curl upward (screen y is down)
        s_ = 1 + 0.12 * e
        c_, sn = np.cos(-th), np.sin(-th)
        sx_ = cx + (dx * c_ - dy * sn) / s_
        sy_ = cy + (dx * sn + dy * c_) / s_
        col, A, lt = _sample(col, sx_, sy_), _sample(A[..., None], sx_, sy_)[..., 0], _sample(lt, sx_, sy_)

    cv.put((slice(0, cv.H), slice(0, cv.W)), 1.0, col, A)
    if t < 0.12:                                                        # flash
        k = 1 - t / 0.12
        cv.glow(0, -38, 52, fire[nf - 1], 0.8 * k)
    cv.light += lt
