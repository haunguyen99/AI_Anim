# Bind + weight cho model moi. Chay SAU rig_build_v2.py. Moi control = 0 luc bind.
import math
for _c in api.ls("Curve"):
    if _c.startswith("CTL_") and _c != "CTL_Main": api.rotate(_c, 0, 0, 0); api.move(_c, 0, 0, 0)
api.set_frame(3); api.set_frame(0)
JP = {r["name"]: tuple(r["world"]) for r in api.joint_info()}
DEF = [j for j in JP if j.startswith("DEF_") and "Muzzle" not in j]
BODY = "Pet_chrono_ouroboros"; HG = "hourglass"
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t * t * (3 - 2 * t)
def bind(m):
    api.select([m])
    try: api.unbind_skin()
    except Exception: pass
    api.select([m]); api.bind_skin(DEF)
# dong ho cat: 100% Hourglass
md = api.mesh_data(HG); hidx = list(md["vertices"]); bind(HG); api.select([HG]); api.set_skin_weights(hidx, [[("DEF_Hourglass_M", 1.0)] for _ in hidx])
md = api.mesh_data(BODY); idx = list(md["vertices"]); P = md["positions"]; P = [P[i * 3:i * 3 + 3] for i in range(len(idx))]
bind(BODY)
CH = [(n, JP[n]) for n in ["DEF_Tail5_M", "DEF_Tail4_M", "DEF_Tail3_M", "DEF_Tail2_M", "DEF_Tail1_M", "DEF_Root_M", "DEF_Spine1_M", "DEF_Spine2_M", "DEF_Spine3_M", "DEF_Spine4_M", "DEF_Neck1_M", "DEF_Neck2_M", "DEF_Head_M"]]
def trunk(p):
    best = None
    for k in range(len(CH) - 1):
        (a, A), (b, B) = CH[k], CH[k + 1]
        AB = [B[i] - A[i] for i in range(3)]; L2 = sum(v * v for v in AB)
        t = max(0.0, min(1.0, sum((p[i] - A[i]) * AB[i] for i in range(3)) / L2))
        d = math.dist(p, [A[i] + t * AB[i] for i in range(3)])
        if best is None or d < best[0] - 1e-9: best = (d, k, t)
    _, k, t = best; t = sm(t)
    return {CH[k][0]: 1 - t, CH[k + 1][0]: t}
jy = JP["DEF_Jaw_M"][1]; jz = JP["DEF_Jaw_M"][2]
def row(i):
    x, y, z = P[i]; w = trunk(P[i])
    # ham duoi: phan mom thap (y < Jaw) o phia truoc khop ham
    jw = sm(ramp(jy + 0.06 - y, 0, 0.10)) * ramp(z, jz - 0.10, jz - 0.02)
    if jw > 0 and "DEF_Head_M" in w:
        h = w.pop("DEF_Head_M"); w["DEF_Head_M"] = h * (1 - jw); w["DEF_Jaw_M"] = h * jw
    # dau (z > 1.3, ke ca bom/sung): chi Head
    hw = sm(ramp(z, 1.28, 1.34))
    if hw > 0:
        a = {k: v * (1 - hw) for k, v in w.items()}; a["DEF_Head_M"] = a.get("DEF_Head_M", 0) + hw * (1 - jw); a["DEF_Jaw_M"] = a.get("DEF_Jaw_M", 0) + hw * jw; w = a
    return w
def fin(w):
    r = [(j, v) for j, v in w.items() if v > 0.01]; r.sort(key=lambda t: -t[1]); r = r[:4]; t = sum(v for _, v in r); return [(j, v / t) for j, v in r]
api.select([BODY]); api.set_skin_weights(idx, [fin(row(i)) for i in range(len(idx))])
print("skinned", len(idx), "hourglass", len(hidx))
