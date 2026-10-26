# Gợi ý khớp biped chỉ từ mesh (không đọc xương khách): tỉ lệ template + tâm mặt cắt.
# python propose.py <ref_mesh.json> <out landmarks.json> [ref_skeleton.json để chấm sai lệch]
import sys, json
import numpy as np
mesh = json.load(open(sys.argv[1]))
# island: mesh có nhiều đỉnh nhất = thân; còn lại = prop
mesh.sort(key=lambda m: -len(m["verts"]))
body = np.array(mesh[0]["verts"]).reshape(-1, 3)
props = [np.array(m["verts"]).reshape(-1, 3) for m in mesh[1:]]
H = body[:, 1].max(); L = body[:, 0].max()  # chiều cao, nửa sải tay
cx = (body[:, 0].min() + body[:, 0].max()) / 2

def med(sel):
    return np.median(sel, axis=0) if len(sel) else np.zeros(3)

def slice_c(y, hw=5, xr=None, side=0):
    s = body[np.abs(body[:, 1] - y) < hw]
    if xr: s = s[(s[:, 0] * (side or 1) >= xr[0]) & (s[:, 0] * (side or 1) <= xr[1])]
    return s

P = {}
# thân giữa: y theo tỉ lệ, z theo trung vị lát cắt giữa
for n, f in dict(Root_M=.40, Spine1_M=.495, Chest_M=.60, Neck_M=.76, Head_M=.85, HeadEnd_M=.955).items():
    y = f * H; s = slice_c(y, 6, (-0.15 * L, 0.15 * L), 1)
    s = slice_c(y, 6, (-0.15 * L, 0.15 * L), 1); P[n] = [cx, y, float((s[:, 2].min() + s[:, 2].max()) / 2) if len(s) else 0]
# chân R (x âm): hip/knee/ankle theo chiều cao, x,z theo trung vị lát cắt bên chân
for n, f in dict(Hip=.39, Knee=.23, Ankle=.08).items():
    y = f * H; s = slice_c(y, 6, (0.04 * L, 0.26 * L), -1)
    P[n + "_R"] = [float(np.median(s[:, 0])) if n != "Hip" else float(-0.103 * L), y, float(np.median(s[:, 2]))]
foot = body[(body[:, 1] < 0.035 * H) & (body[:, 0] < 0)]
P["ToesEnd_R"] = [float(np.median(foot[:, 0])), 0.0, float(foot[:, 2].max())]
P["Toes_R"] = [P["ToesEnd_R"][0] * .95, 0.036 * H, P["Ankle_R"][2] + 0.55 * (P["ToesEnd_R"][2] - P["Ankle_R"][2])]
# tay R: dọc trục X; y,z = tâm lát cắt theo x
for n, f in dict(Scapula=.058, Shoulder=.256, Elbow=.51, Wrist=.74, HandTip=1.0).items():
    x = -f * L if n != "HandTip" else -L * .995
    s = body[(np.abs(body[:, 0] - x) < 6) & (body[:, 1] > .5 * H) & (body[:, 1] < .9 * H)]
    P[n + "_R"] = [x, float((s[:, 1].min() + s[:, 1].max()) / 2), float((s[:, 2].min() + s[:, 2].max()) / 2)]
P["Scapula_R"] = [P["Scapula_R"][0], .71 * H, P["Chest_M"][2]]
# phụ: váy, prop
sk = body[(body[:, 1] > .30 * H) & (body[:, 1] < .38 * H) & (np.abs(body[:, 0]) < .25 * L)]
P["DressFront_M"] = [cx, .32 * H, float(sk[:, 2].max() * .7)]
P["DressBack_M"] = [cx, .36 * H, float(sk[:, 2].min() * .7)]
P["Prop_M"] = [cx, P["Chest_M"][1] * 1.16, float(body[:, 2].max() * .6)]
for i, pv in enumerate(props):
    P["Weapon"] = [float((pv[:, 0].min() + pv[:, 0].max()) / 2), float(.265 * (pv[:, 1].max() - pv[:, 1].min())), float((pv[:, 2].min() + pv[:, 2].max()) / 2)]
# L = gương R
for k in [k for k in P if k.endswith("_R")]:
    p = P[k]; P[k[:-1] + "L"] = [-p[0] + 2 * cx, p[1], p[2]]
json.dump(dict(H=float(H), L=float(L), landmarks={k: [round(float(v), 2) for v in p] for k, p in P.items()}), open(sys.argv[2], "w"), indent=1)
if len(sys.argv) > 3:
    ref = {s["name"]: s["bind_pos"] for s in json.load(open(sys.argv[3]))}
    ref["HandTip_R"] = ref["MiddleFinger3_R"]; ref["HandTip_L"] = ref["MiddleFinger3_L"]
    print("%-14s %28s %28s  err(cm)" % ("joint", "auto", "ref"))
    for k, p in P.items():
        if k in ref and ref[k]:
            e = np.linalg.norm(np.array(p) - ref[k]); print("%-14s %28s %28s  %5.1f" % (k, np.round(p, 0).tolist(), np.round(ref[k], 0).tolist(), e))
