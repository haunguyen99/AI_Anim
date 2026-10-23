# Pattern search of the weapon placement (6 channels, bounded) on top of the accepted P0 stages: minimise the mean
# distance of weapon-mesh vertices outside the reference silhouette (4 grid cameras) + a pull to the start.
#   W_START = {"weapon.ty": 28}; W_BOUND = 12; exec(open(r".../weapon_search.py").read())  -> prints / sets W_BEST
import json

import bpy
import numpy as np

_S = json.load(open(r"E:/AI Animation/work/idle/p0_stages.json"))
_base = dict(_S["stage1_legs"]["TRIAL_CH"])
for _k, _st in _S.items():
    if _k != "stage1_legs":
        _base.update(_st.get("TRIAL_CH_add", {}))
STANCE = _S["stage1_legs"]["STANCE"]
_post = _S["stage1_legs"]["POST"]
for _k, _st in _S.items():
    if _k != "stage1_legs" and _st.get("POST_add"):
        _post += "; " + _st["POST_add"]
FB_NO_RUN = True
exec(open(r"E:/AI Animation/tools/blender/fullbody_solve.py").read())
setup_base()
_W = ["weapon.rx", "weapon.ry", "weapon.rz", "weapon.tx", "weapon.ty", "weapon.tz"]
_start = dict(globals().get("W_START", {}))
_bound = globals().get("W_BOUND", 12.0)
_dt = {v: SILREF[v + "_dt"][0].astype(np.float32) for v in _CAMS}


def _pose(wv):
    p = np.zeros(len(NAMES))
    for k, v in _base.items():
        p[NAMES.index(k)] = v
    for k, v in zip(_W, wv):
        p[NAMES.index(k)] = v
    apply(p)
    exec(_post, globals())


def _cost(wv):
    _pose(wv)
    dg = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects["EN_M11_Boss_Gaygor_VK"].evaluated_get(dg)
    a = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get("co", a); a = a.reshape(-1, 3)
    M = np.array(o.matrix_world); P = a @ M[:3, :3].T + M[:3, 3]
    sc_ = float(SILREF["scale"]); tot = []
    for v, (Mi, s, shx, shy) in _CAMS.items():
        q = P @ Mi[:3, :3].T + Mi[:3, 3]
        uv = np.c_[960 + q[:, 0] * s - shx, 540 - q[:, 1] * s + shy]; box = SILREF[v + "_box"]
        iu = np.clip(((uv[:, 0] - box[0]) * sc_).astype(int), 0, _dt[v].shape[1] - 1)
        iv = np.clip(((uv[:, 1] - box[1]) * sc_).astype(int), 0, _dt[v].shape[0] - 1)
        tot.append(np.minimum(_dt[v][iv, iu], 60.0))
    reg = sum(((wv[i] - _start.get(k, 0.0)) / 25.0) ** 2 for i, k in enumerate(_W))
    return float(np.mean(np.concatenate(tot))) + reg


x = np.array([_start.get(k, 0.0) for k in _W]); best = _cost(x); first = best
for step in (6.0, 3.0, 1.5):
    improved = True
    while improved:
        improved = False
        for i in range(6):
            for sgn in (1, -1):
                y = x.copy(); y[i] += sgn * step
                if abs(y[i] - _start.get(_W[i], 0.0)) > _bound:
                    continue
                c = _cost(y)
                if c < best - 1e-3:
                    x, best, improved = y, c, True
W_BEST = dict(zip(_W, map(float, x)))
print(f"weapon search {first:.2f} -> {best:.2f} px", {k: round(v, 1) for k, v in W_BEST.items()})
