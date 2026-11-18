# Xoay thu tung control (30 do moi truc; scale cho Cheek/Mouth) -> do gian canh mesh. Chay trong Frolvy 9885.
import math
M = "Pet_Wind_Chameleon"
md = api.mesh_data(M); P0 = md['positions']; fs = md['face_sizes']; fc = md['face_corners']
E = set(); c = 0
for s in fs:
    cs = fc[c:c+s]; c += s
    for a in range(s):
        E.add(tuple(sorted((cs[a], cs[(a+1) % s]))))
E = list(E)
def L(P, a, b): return math.sqrt(sum((P[a*3+k]-P[b*3+k])**2 for k in range(3)))
L0 = [L(P0, a, b) for a, b in E]
def test(ctl, attr, val):
    api.set_attr(ctl + "." + attr, val)
    P = api.mesh_data(M, True)['positions']
    api.set_attr(ctl + "." + attr, 0 if attr[0] != 's' else 1)
    r = [(L(P, a, b) / max(l, 1e-6), i) for i, ((a, b), l) in enumerate(zip(E, L0)) if l > 0.004]
    hi = max(r); lo = min(r)
    # lech lon nhat cua dinh (cm)
    mv = max(math.sqrt(sum((P[i*3+k]-P0[i*3+k])**2 for k in range(3))) for i in range(len(P)//3))
    return hi, lo, mv
rows = []
CT = [c for c in api.ls("Curve") if c.startswith("CTL_") and c != "CTL_Main"]
for c in CT:
    short = c[4:]
    tests = []
    if short.startswith(("Cheek", "Mouth")): tests = [("sx", 1.5), ("sy", 1.5), ("sy", 0.2), ("sz", 1.5)]
    else: tests = [("rx", 30), ("ry", 30), ("rz", 30)] + ([("rx", -30)] if short.startswith(("Jaw", "Tail", "Neck", "Head", "Tongue")) else [])
    for at, v in tests:
        hi, lo, mv = test(c, at, v)
        rows.append((hi[0], lo[0], mv, c, at, v, E[hi[1]], E[lo[1]]))
rows.sort(key=lambda t: -t[0])
print("top gian canh (ti le), dinh lech max m:")
for r in rows[:14]: print("%.2f  min%.2f  mv%.2f  %s %s %s  canh %s" % (r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
rows.sort(key=lambda t: t[1])
print("top nen canh:")
for r in rows[:8]: print("%.2f  max%.2f  mv%.2f  %s %s %s  canh %s" % (r[1], r[0], r[2], r[3], r[4], r[5], r[7]))
