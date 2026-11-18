# Pose helpers (run inside Frolvy): world position of a joint, zero all controls, solve control rotation / translation so a joint reaches a world target.
def wp(j):
    m = api.world_matrix(j); return [m[12], m[13], m[14]]
def refresh(): api.set_frame(1); api.set_frame(0)
def zero_all():
    for c in api.ls("Curve"):
        if c.startswith("CTL_") and c != "CTL_Main": api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    refresh()
def _solve3(A, b):
    # solve A x = b (3x3) by Cramer
    def det(M): return (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1]) - M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0]) + M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
    d = det(A)
    if abs(d) < 1e-12: return [0, 0, 0]
    out = []
    for k in range(3):
        M = [row[:] for row in A]
        for i in range(3): M[i][k] = b[i]
        out.append(det(M) / d)
    return out
def solve_rot(ctl, joint, target, start=(0, 0, 0), free=(0, 1, 2), iters=14, lam=1e-4, base=None):
    # Gauss-Newton on the rotation of ctl (deg) so that joint reaches target (world). free = which of rx, ry, rz may change.
    r = list(start)
    def put(r): api.rotate(ctl, *r); refresh()
    for _ in range(iters):
        put(r); p = wp(joint); e = [target[i] - p[i] for i in range(3)]
        if sum(x * x for x in e) < 1e-8: break
        J = []
        for k in free:
            r2 = r[:]; r2[k] += 2.0; put(r2); q = wp(joint); J.append([(q[i] - p[i]) / 2.0 for i in range(3)])
        n = len(free)
        A = [[sum(J[a][i] * J[b][i] for i in range(3)) + (lam if a == b else 0) for b in range(3)] if a < n else [0, 0, 0] for a in range(3)]
        A = [[(sum(J[a][i] * J[b][i] for i in range(3)) + (lam if a == b else 0)) if (a < n and b < n) else (1.0 if a == b else 0.0) for b in range(3)] for a in range(3)]
        g = [sum(J[a][i] * e[i] for i in range(3)) if a < n else 0.0 for a in range(3)]
        dx = _solve3(A, g)
        for a, k in enumerate(free): r[k] += max(-40, min(40, dx[a]))
    put(r); return r, wp(joint)
def solve_move(ctl, joint, target, iters=6):
    t = [0.0, 0.0, 0.0]
    def put(t): api.move(ctl, *t); refresh()
    for _ in range(iters):
        put(t); p = wp(joint); e = [target[i] - p[i] for i in range(3)]
        if sum(x * x for x in e) < 1e-9: break
        J = []
        for k in range(3):
            t2 = t[:]; t2[k] += 0.01; put(t2); q = wp(joint); J.append([(q[i] - p[i]) / 0.01 for i in range(3)])
        # J[k][i] = d p_i / d t_k  -> solve sum_k J[k][i] dt_k = e_i
        A = [[J[k][i] for k in range(3)] for i in range(3)]
        dt = _solve3(A, e)
        for k in range(3): t[k] += dt[k]
    put(t); return t, wp(joint)
