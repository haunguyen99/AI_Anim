# Bind + weight rig v3. Chạy SAU rig_build_v3.py. Mọi control = 0 lúc bind. Thân/đuôi: nhân (kernel) theo độ dài cung dọc chuỗi, mỗi điểm ăn ~3 khớp để uốn vòng tròn mượt.
import math
for _c in api.ls("Curve"):
    if _c.startswith("CTL_") and _c != "CTL_Main": api.rotate(_c, 0, 0, 0); api.move(_c, 0, 0, 0)
api.set_frame(3); api.set_frame(0)
JP = {r["name"]: tuple(r["world"]) for r in api.joint_info()}
DEF = [j for j in JP if j.startswith("DEF_") and "Muzzle" not in j]
BODY = "Pet_chrono_ouroboros"; HG = "hourglass"
KW = 1.6   # bề rộng kernel tính theo bước khớp
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t * t * (3 - 2 * t)
def bind(m):
    api.select([m])
    try: api.unbind_skin()
    except Exception: pass
    api.select([m]); api.bind_skin(DEF)
md = api.mesh_data(HG); hidx = list(md["vertices"]); bind(HG); api.select([HG]); api.set_skin_weights(hidx, [[("DEF_Hourglass_M", 1.0)] for _ in hidx])
md = api.mesh_data(BODY); idx = list(md["vertices"]); P = md["positions"]; P = [P[i * 3:i * 3 + 3] for i in range(len(idx))]
bind(BODY)
order = ["DEF_Tail%d_M" % k for k in range(7, 0, -1)] + ["DEF_Root_M"] + ["DEF_Spine%d_M" % k for k in range(1, 9)] + ["DEF_Neck1_M", "DEF_Neck2_M", "DEF_Head_M"]
CH = [(n, JP[n]) for n in order]
S = [0.0]
for (a, A), (b, B) in zip(CH, CH[1:]): S.append(S[-1] + math.dist(A, B))
def trunk(p):
    best = None
    for k in range(len(CH) - 1):
        A, B = CH[k][1], CH[k + 1][1]
        AB = [B[i] - A[i] for i in range(3)]; L2 = sum(v * v for v in AB)
        t = max(0.0, min(1.0, sum((p[i] - A[i]) * AB[i] for i in range(3)) / L2))
        d = math.dist(p, [A[i] + t * AB[i] for i in range(3)])
        if best is None or d < best[0] - 1e-9: best = (d, k, t)
    _, k, t = best; s = S[k] + t * (S[k + 1] - S[k]); w = {}
    for i, (n, _) in enumerate(CH):
        step = (S[min(i + 1, len(S) - 1)] - S[max(i - 1, 0)]) / (2 if 0 < i < len(S) - 1 else 1)
        h = KW * step; x = 1 - abs(s - S[i]) / h
        if x > 0: w[n] = x * x
    tot = sum(w.values()); return {n: v / tot for n, v in w.items()}
jy = JP["DEF_Jaw_M"][1]; jz = JP["DEF_Jaw_M"][2]
def row(i):
    x, y, z = P[i]; w = trunk(P[i])
    jw = sm(ramp(jy + 0.06 - y, 0, 0.10)) * ramp(z, jz - 0.10, jz - 0.02)
    if jw > 0 and "DEF_Head_M" in w:
        h = w.pop("DEF_Head_M"); w["DEF_Head_M"] = h * (1 - jw); w["DEF_Jaw_M"] = h * jw
    hw = sm(ramp(z, 1.28, 1.34))
    if hw > 0:
        a = {k: v * (1 - hw) for k, v in w.items()}; a["DEF_Head_M"] = a.get("DEF_Head_M", 0) + hw * (1 - jw); a["DEF_Jaw_M"] = a.get("DEF_Jaw_M", 0) + hw * jw; w = a
    return w
def fin(w):
    r = [(j, v) for j, v in w.items() if v > 0.01]; r.sort(key=lambda t: -t[1]); r = r[:4]; t = sum(v for _, v in r); return [(j, v / t) for j, v in r]
api.select([BODY]); api.set_skin_weights(idx, [fin(row(i)) for i in range(len(idx))])
print("skinned", len(idx), "hourglass", len(hidx))
