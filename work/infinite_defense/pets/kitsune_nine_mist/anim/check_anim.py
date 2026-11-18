# usage: set NF (last frame) before exec; chạy trong Frolvy. Kiểm F0==F_last, xoay/frame, kéo skin, đầu đuôi.
import math
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())
JN = list(api.ls("Joint"))
def state(f): api.set_frame(f); return {j: api.world_matrix(j) for j in JN}
S0 = state(0); SN = state(NF)
print("f0==f%d max joint diff cm:" % NF, round(max(max(abs(S0[j][i] - SN[j][i]) for i in (12, 13, 14)) for j in JN) * 100, 3))
E = [(i, n) for i in range(len(IDX)) for n in NB[i] if i < n and math.dist(V[i], V[n]) > 1e-4]
prev = S0; mr = (0, None, 0); ws = (0, 0); wd = (0, 0); mv = (0, 0)
for f in range(0, NF + 1):
    S = state(f)
    for j in JN:
        A, B = prev[j], S[j]; ang = 0
        for c in range(3):
            na = math.sqrt(sum(A[c * 4 + k] ** 2 for k in range(3))); nb = math.sqrt(sum(B[c * 4 + k] ** 2 for k in range(3)))
            d = sum(A[c * 4 + k] * B[c * 4 + k] for k in range(3)) / (na * nb); ang = max(ang, math.degrees(math.acos(max(-1, min(1, d)))))
        if ang > mr[0]: mr = (ang, j, f)
    md = api.mesh_data(MESH, True); Pf = md['positions']; Q = [Pf[i * 3:i * 3 + 3] for i in range(len(IDX))]
    w = max(math.dist(Q[a], Q[b]) / math.dist(V[a], V[b]) for a, b in E)
    if w > ws[0]: ws = (w, f)
    d = max(math.dist(Q[a], Q[b]) - math.dist(V[a], V[b]) for a, b in E)
    if d > wd[0]: wd = (d, f)
    if prev is not S0 or f > 0:
        m = max(math.dist(S[j][12:15], prev[j][12:15]) for j in JN)
        if m > mv[0]: mv = (m, f)
    prev = S
print("max rot/frame %.1f deg %s f%d" % mr); print("worst edge stretch x%.2f at f%d; worst absolute +%.1f cm at f%d" % (ws + (wd[0] * 100, wd[1]))); print("max joint move/frame %.1f cm at f%d" % (mv[0] * 100, mv[1]))
for f in (0, 8, 12):
    S = state(f); print("f%d Muzzle cm:" % f, {m[4:]: [round(S[m][12 + a] * 100) for a in range(3)] for m in JN if "Muzzle" in m})
print("root y cm f0/8/12/18/last:", [round(state(f)["DEF_Root_M"][13] * 100, 1) for f in (0, 8, 12, 18, NF)])
api.set_frame(0)
