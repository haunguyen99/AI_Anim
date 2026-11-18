import math
CT = [c for c in api.ls("Curve") if c.startswith("CTL_")]
A = ("tx", "ty", "tz", "rx", "ry", "rz")
def snap(f):
    api.set_frame(f); return {c: [api.get_attr(c + "." + a) for a in A] for c in CT}
S = [snap(f) for f in range(0, 31)]
seam = max(abs(S[0][c][i] - S[30][c][i]) for c in CT for i in range(6))
print("seam f0 vs f30 max diff:", round(seam, 6))
worst = []
for c in CT:
    for i in range(3, 6):
        d = max(abs(S[f + 1][c][i] - S[f][c][i]) for f in range(30)); r = max(S[f][c][i] for f in range(31)) - min(S[f][c][i] for f in range(31))
        worst.append((d, r, c, A[i]))
worst.sort(reverse=True)
print("largest per-frame rotation steps (deg/frame, total range):", [(round(d, 1), round(r, 1), c[4:], a) for d, r, c, a in worst[:6]])
def wp(j): m = api.world_matrix(j); return [m[12], m[13], m[14]]
for j in ("DEF_Wrist_R", "DEF_Root_M", "DEF_Head_M", "DEF_Muzzle_M", "DEF_Coin_L"):
    P = []
    for f in range(0, 31): api.set_frame(f); P.append(wp(j))
    print(j, "range x %.3f y %.3f z %.3f" % tuple(max(p[i] for p in P) - min(p[i] for p in P) for i in range(3)))
api.set_frame(0)
