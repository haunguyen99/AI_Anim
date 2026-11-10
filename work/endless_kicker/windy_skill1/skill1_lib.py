"""Windy Skill1 blocking helpers - chay TRONG Frolvy (execute_code), khong can numpy.
Nap: exec(open(r'<duong dan file nay>').read())  (can bien `api` co san).
"""
import math, json, os

R = 'Windy_rig:'
C = R + 'CTL_'
IDLE = json.load(open(os.environ['TEMP'] + '/idle_f0.json'))   # gia tri CTL luc F0 (Idle)


def Wm(n):
    return api.world_matrix(R + n)


def pos(n):
    m = Wm(n)
    return [m[12], m[13], m[14]]


def rows(n):
    m = Wm(n)
    return [m[0:3], m[4:7], m[8:11]]


def sub(a, b): return [a[i] - b[i] for i in range(3)]
def add(a, b): return [a[i] + b[i] for i in range(3)]
def mul(a, s): return [x * s for x in a]
def dot(a, b): return sum(a[i] * b[i] for i in range(3))
def norm(a):
    l = math.sqrt(dot(a, a)) or 1e-9
    return [x / l for x in a]
def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def setv(ctrl, attr, v):
    api.set_attr(C + ctrl + '.' + attr, float(v))


def getv(ctrl, attr):
    return api.get_attr(C + ctrl + '.' + attr)


def staff():
    """tay (khop Weapon), huong trượng (duoi->dau)"""
    h = pos('DEF_Weapon_R')
    e = pos('DEF_WeaponEnd_R')
    return h, norm(sub(e, h))


# ---------- quay quanh truc the gioi ----------
def rot_axis(axis, deg):
    a = norm(axis); c = math.cos(math.radians(deg)); s = math.sin(math.radians(deg)); t = 1 - c
    x, y, z = a
    return [[t * x * x + c, t * x * y - s * z, t * x * z + s * y],
            [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
            [t * x * z - s * y, t * y * z + s * x, t * z * z + c]]


def apply_rot(M, v):
    return [dot(M[0], v), dot(M[1], v), dot(M[2], v)]


def swing(a, b):
    """quay ngan nhat a -> b (3x3, tac dong len vector cot)"""
    a = norm(a); b = norm(b)
    ax = cross(a, b); s = math.sqrt(dot(ax, ax)); c = dot(a, b)
    if s < 1e-9:
        return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    return rot_axis(ax, math.degrees(math.atan2(s, c)))


# ---------- giai he tuyen tinh (Gauss) ----------
def solve_lin(A, b):
    n = len(b)
    M = [A[i][:] + [b[i]] for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        d = M[i][i] or 1e-12
        for j in range(i, n + 1): M[i][j] /= d
        for r in range(n):
            if r != i:
                f = M[r][i]
                if f:
                    for j in range(i, n + 1): M[r][j] -= f * M[i][j]
    return [M[i][n] for i in range(n)]


def lm(vars_, resid, x0, iters=40, lam=1e-2, h=0.5, verbose=False):
    """vars_: [(ctrl,attr)], resid(): list residual (da set attr xong). Levenberg-Marquardt."""
    def setx(x):
        for (c, a), v in zip(vars_, x): setv(c, a, v)
    x = x0[:]
    setx(x); r = resid(); cost = sum(v * v for v in r)
    for it in range(iters):
        J = []
        for k in range(len(x)):
            xp = x[:]; xp[k] += h
            setx(xp); rp = resid()
            J.append([(rp[i] - r[i]) / h for i in range(len(r))])
        n = len(x)
        A = [[sum(J[i][m] * J[j][m] for m in range(len(r))) for j in range(n)] for i in range(n)]
        g = [sum(J[i][m] * r[m] for m in range(len(r))) for i in range(n)]
        improved = False
        for _ in range(8):
            Al = [[A[i][j] + (lam * (A[i][i] + 1e-9) if i == j else 0) for j in range(n)] for i in range(n)]
            dx = solve_lin(Al, [-v for v in g])
            xn = [x[i] + dx[i] for i in range(n)]
            setx(xn); rn = resid(); cn = sum(v * v for v in rn)
            if cn < cost:
                x, r, cost = xn, rn, cn; lam = max(lam / 3, 1e-6); improved = True; break
            lam *= 4
        if verbose: print(it, round(cost, 6))
        if not improved or cost < 1e-7: break
    setx(x)
    return x, cost


# ---------- giai tay phai: tay cam + huong trượng + xoay (swing tu Idle) ----------
RIGHT_VARS = [('Shoulder_R', 'rx'), ('Shoulder_R', 'ry'), ('Shoulder_R', 'rz'), ('Elbow_R', 'ry'),
              ('Wrist_R', 'rx'), ('Wrist_R', 'ry'), ('Wrist_R', 'rz')]


def solve_right(hand, rot_target, x0, ref=None, elbow_max_above=0.05, wrist_w=0.004, extra=None):
    """hand: vi tri khop Weapon (world). rot_target: 3x3 hang (X=huong trượng...) cua khop Weapon.
    extra: ham tra them residual."""
    ref = ref or x0
    def resid():
        h = pos('DEF_Weapon_R'); Rm = rows('DEF_Weapon_R')
        r = [(h[i] - hand[i]) * 12 for i in range(3)]
        for i in range(3):
            for j in range(3):
                r.append((Rm[i][j] - rot_target[i][j]) * 3)
        vals = [getv(c, a) for c, a in RIGHT_VARS]
        # on arm: khuyu chi gap ry trong [8,150]
        ey = vals[3]
        r.append(max(0, 8 - ey) * 0.05); r.append(max(0, ey - 150) * 0.05)
        # co tay lech <= ~35 do
        for v in vals[4:]:
            r.append(max(0, abs(v) - 35) * 0.05)
            r.append(v * wrist_w)
        # vai gan ref nhe (tranh nhay trục)
        for v, rv in zip(vals[:3], ref[:3]): r.append((v - rv) * 0.002)
        # khuyu khong qua cao so voi vai
        e = pos('DEF_Elbow_R'); s = pos('DEF_Shoulder_R')
        r.append(max(0, e[1] - s[1] - elbow_max_above) * 4)
        if extra: r += extra()
        return r
    return lm(RIGHT_VARS, resid, x0)


LEFT_VARS = [('Shoulder_L', 'rx'), ('Shoulder_L', 'ry'), ('Shoulder_L', 'rz'), ('Elbow_L', 'ry')]


def solve_left(wrist, x0, ref=None, elbow_below=0.03):
    ref = ref or x0
    def resid():
        w = pos('DEF_Wrist_L')
        r = [(w[i] - wrist[i]) * 12 for i in range(3)]
        vals = [getv(c, a) for c, a in LEFT_VARS]
        for v, rv in zip(vals[:3], ref[:3]): r.append((v - rv) * 0.004)
        r.append(max(0, 12 - vals[3]) * -0.0 + max(0, 12 - abs(vals[3])) * 0.05)
        e = pos('DEF_Elbow_L'); s = pos('DEF_Shoulder_L')
        r.append(max(0, e[1] - s[1] - elbow_below) * 4)
        return r
    return lm(LEFT_VARS, resid, x0)


def snapshot(names=('DEF_Head_M', 'DEF_Chest_M', 'DEF_Root_M', 'DEF_Shoulder_R', 'DEF_Elbow_R', 'DEF_Wrist_R',
                    'DEF_Weapon_R', 'DEF_WeaponEnd_R', 'DEF_Wrist_L', 'DEF_Elbow_L')):
    return {n: [round(v, 3) for v in pos(n)] for n in names}
