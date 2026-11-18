# Trong Frolvy: dac tinh mesh theo frame (muzzle z, mui luoi, diem thap nhat, gian canh). Chay tren scene dang mo (cu hoac moi).
import math
MS = [m for m in api.ls("Object")]
ms0 = {m: api.mesh_data(m) for m in MS}
E = []
off = 0; Pall0 = []
for m in MS:
    md = ms0[m]; fs = md['face_sizes']; fc = md['face_corners']; c = 0; es = set()
    for s in fs:
        cs = fc[c:c+s]; c += s
        for a in range(s): es.add(tuple(sorted((cs[a], cs[(a+1) % s]))))
    E.append((m, list(es)))
def L(P, a, b): return math.sqrt(sum((P[a*3+k]-P[b*3+k])**2 for k in range(3)))
L0 = {m: [L(ms0[m]['positions'], a, b) for a, b in es] for m, es in E}
f0, f1 = api.frame_range()
print("frame muzzleZ tipZ(mesh max z) low(y) maxStretch minShrink")
for f in range(int(f0), int(f1) + 1):
    api.set_frame(f)
    mz = api.world_matrix("DEF_Muzzle_M")[14]
    tip = -9; low = 9; hi = 0; lo = 9
    for m, es in E:
        P = api.mesh_data(m, True)['positions']
        zs = P[2::3]; ys = P[1::3]; tip = max(tip, max(zs)); low = min(low, min(ys))
        for (a, b), l in zip(es, L0[m]):
            if l > 0.004:
                r = L(P, a, b) / l; hi = max(hi, r); lo = min(lo, r)
    print("%d %.3f %.3f %.3f %.2f %.2f" % (f, mz, tip, low, hi, lo))
api.set_frame(int(f0))
