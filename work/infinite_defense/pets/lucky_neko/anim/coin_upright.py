# Make the coin stand upright facing front: world x axis -> (1,0,0), world y axis -> (0,1,0) (face normal = +Z). Only CTL_Coin_L rotation changes; the coin centre and the user's arm pose stay.
import math
def axes():
    m = api.world_matrix("DEF_Coin_L")
    def n(v):
        l = math.sqrt(sum(c * c for c in v)); return [c / l for c in v]
    return n(m[0:3]) + n(m[4:7])
TARGET = [1, 0, 0, 0, 1, 0]
def res(): a = axes(); return [TARGET[i] - a[i] for i in range(6)]
def solve3(A, b):
    def det(M): return (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1]) - M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0]) + M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
    d = det(A); out = []
    for k in range(3):
        M = [r[:] for r in A]
        for i in range(3): M[i][k] = b[i]
        out.append(det(M) / d)
    return out
pos0 = [api.world_matrix("DEF_Coin_L")[12 + i] for i in range(3)]
r = [api.get_attr("CTL_Coin_L." + a) for a in ("rx", "ry", "rz")]
print("before", [round(x, 1) for x in r], "err", round(sum(x * x for x in res()), 4))
for it in range(25):
    api.rotate("CTL_Coin_L", *r); e = res()
    if sum(x * x for x in e) < 1e-8: break
    J = []
    for k in range(3):
        r2 = r[:]; r2[k] += 1.0; api.rotate("CTL_Coin_L", *r2); e2 = res(); J.append([(e[i] - e2[i]) / 1.0 for i in range(6)])   # d(axes)/d angle
    A = [[sum(J[a][i] * J[b][i] for i in range(6)) + (1e-6 if a == b else 0) for b in range(3)] for a in range(3)]
    g = [sum(J[a][i] * e[i] for i in range(6)) for a in range(3)]
    dx = solve3(A, g)
    for k in range(3): r[k] += max(-60, min(60, dx[k]))
api.rotate("CTL_Coin_L", *r)
a = axes(); m = api.world_matrix("DEF_Coin_L")
print("after", [round(x, 1) for x in r], "axes", [round(x, 3) for x in a], "err", round(sum(x * x for x in res()), 6), "centre moved", [round(m[12 + i] - pos0[i], 4) for i in range(3)])
