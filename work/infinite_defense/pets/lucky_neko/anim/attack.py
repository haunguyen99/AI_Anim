"""Lucky Neko Attack, 30F, FIRE (coin flick, event) = frame 10, f30 = idle frame 0 (BASE pose).
Anticipation 0-7 (crouch, lean back, coin hand pulled in, right paw cocked up) -> snap 7-10 (lunge, left paw thrusts, coin flicked ahead and spinning) ->
follow-through 10-17 (overshoot, ears/tail/bell/tassels/jar/legs drag and swing) -> settle 17-30 back to the idle pose.
Run in Frolvy (port 9891) on a clean scene opened from lucky_neko_rig.fv. Primary motion = eased key poses; arms/coin = IK-style solves to world targets per frame; secondary = spring lag of the body motion."""
import json, math
N = 30; FIRE = 10
BASE = json.load(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\lucky_neko\anim\base_pose.json"))
CT = sorted(BASE)
def wp(j):
    m = api.world_matrix(j); return [m[12], m[13], m[14]]
# ---------- helpers
def sm(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def seg(t, ease):
    t = max(0.0, min(1.0, t))
    return {"io": t * t * (3 - 2 * t), "in": t * t, "out": 1 - (1 - t) ** 2, "lin": t}[ease]
def curve(f, keys):
    # keys: [(frame, value, ease of the segment arriving at this key)]
    if f <= keys[0][0]: return keys[0][1]
    for (f0, v0, _), (f1, v1, e) in zip(keys, keys[1:]):
        if f <= f1: return v0 + (v1 - v0) * seg((f - f0) / (f1 - f0), e)
    return keys[-1][1]
def spring(d, T, z):
    w = 2 * math.pi / T; x = d[0]; v = 0.0; out = []
    for dv in d:
        v += w * w * (dv - x) - 2 * z * w * v; x += v; out.append(x)
    return out
# ---------- primary key tracks (offsets from the idle pose)
# Action (user 2026-11-14): the coin hand lowers/pulls in, then SWEEPS UP and flicks the coin away (the coin leaves the hand at FIRE and flies off up/forward).
K = {
 "root_ty": [(0, 0, "io"), (5, -0.003, "io"), (7, -0.015, "io"), (10, 0.028, "in"), (13, 0.010, "out"), (17, -0.008, "io"), (22, 0.003, "io"), (30, 0, "io")],
 "root_tz": [(0, 0, "io"), (7, -0.020, "io"), (10, 0.040, "in"), (13, 0.030, "out"), (17, 0.008, "io"), (22, -0.002, "io"), (30, 0, "io")],
 "root_rx": [(0, 0, "io"), (7, -4, "io"), (10, 3, "in"), (13, 2, "out"), (17, -1, "io"), (30, 0, "io")],
 "spine_rx": [(0, 0, "io"), (7, -9, "io"), (10, 6, "in"), (13, 4, "out"), (17, -2, "io"), (22, 1, "io"), (30, 0, "io")],
 "head_rx": [(0, 0, "io"), (7, 5, "io"), (10, -8, "in"), (12, -14, "out"), (16, -6, "io"), (21, 1, "io"), (30, 0, "io")],      # head looks up after the coin
 "tail1_rx": [(0, 0, "io"), (7, 12, "io"), (10, -8, "in"), (13, 6, "out"), (17, -2, "io"), (30, 0, "io")],
 # left (coin) arm: LOW = tucked in and down a little (wrist ~-3.5 cm, the coin must not sink), HIGH = swept up (wrist ~+6 cm, +8 at the overshoot); offsets from the idle euler values
 "shL_rx": [(0, 0, "io"), (4, 5, "io"), (7, 15, "io"), (10, -30, "in"), (12, -36, "out"), (15, -15, "io"), (19, -4, "io"), (23, 2, "io"), (30, 0, "io")],
 "shL_ry": [(0, 0, "io"), (4, 4, "io"), (7, 12, "io"), (10, -24, "in"), (12, -24, "out"), (15, -12, "io"), (19, -3, "io"), (23, 1, "io"), (30, 0, "io")],
 "shL_rz": [(0, 0, "io"), (4, -5, "io"), (7, -12, "io"), (10, -30, "in"), (12, -36, "out"), (15, -15, "io"), (19, -4, "io"), (23, 2, "io"), (30, 0, "io")],
 "elL_ry": [(0, 0, "io"), (4, 4, "io"), (7, 12, "io"), (10, -30, "in"), (12, -30, "out"), (15, -12, "io"), (19, -3, "io"), (23, 1, "io"), (30, 0, "io")],
 "elL_rz": [(0, 0, "io"), (4, -4, "io"), (7, -12, "io"), (10, 30, "in"), (12, 30, "out"), (15, 12, "io"), (19, 3, "io"), (23, -1, "io"), (30, 0, "io")],
 "wrL_rz": [(0, 0, "io"), (7, -10, "io"), (9, -14, "io"), (11, 28, "in"), (14, 10, "out"), (19, -3, "io"), (30, 0, "io")],      # wrist snaps through the flick
 # right paw: lashes up on the wind-up and snaps back on the fire (counter-balance)
 "elR_rz": [(0, 0, "io"), (7, -12, "io"), (10, 14, "in"), (13, 6, "out"), (18, -2, "io"), (30, 0, "io")],
 "wrR_rz": [(0, 0, "io"), (7, -15, "io"), (10, 25, "in"), (13, 8, "out"), (18, -4, "io"), (30, 0, "io")],
}
# world-space offset tracks (dx, dy, dz) relative to the idle world position (+ the root offset of that frame)
W = {
 "wrist_L": [(0, (0, 0, 0), "io"), (4, (0, -.012, -.010), "io"), (7, (-.005, -.040, -.030), "io"), (10, (.005, .075, -.040), "in"), (12, (.010, .080, -.030), "out"), (14, (0, .050, -.020), "io"), (18, (0, .010, 0), "io"), (22, (0, -.003, 0), "io"), (30, (0, 0, 0), "io")],
 "wrist_R": [(0, (0, 0, 0), "io"), (7, (-.030, .060, -.040), "io"), (10, (-.020, -.030, .040), "in"), (13, (-.010, -.010, .020), "out"), (18, (0, .010, 0), "io"), (30, (0, 0, 0), "io")],
}
COIN_FLY = {}                                                     # user 2026-11-14 (after chot): the coin STAYS in the hand, it does not fly off (the projectile is VFX at the Muzzle on FIRE)
SPIN = [(0, 0, "io"), (30, 0, "io")]
COIN_S = BASE["CTL_Coin_L"][6]
SCALE = [(0, COIN_S, "io"), (30, COIN_S, "io")]
def vec(f, name):
    keys = W[name]
    return [curve(f, [(k[0], k[1][i], k[2]) for k in keys]) for i in range(3)]
def coin_vec(f):
    if f in COIN_FLY: return list(COIN_FLY[f])
    return vec(f, "wrist_L")
# ---------- secondary: lag/overshoot of the body motion (springs), faded out by f30
def sec_tracks():
    ty = [curve(f, K["root_ty"]) for f in range(N + 1)]; tz = [curve(f, K["root_tz"]) for f in range(N + 1)]; sp = [curve(f, K["spine_rx"]) for f in range(N + 1)]
    lag = lambda d, T, z: [a - b for a, b in zip(d, spring(d, T, z))]
    S = {}
    for i, T in enumerate((7.0, 9.0, 11.0), 1):
        S["yl%d" % i] = lag(ty, T, 0.28); S["zl%d" % i] = lag(tz, T, 0.28); S["pl%d" % i] = lag(sp, T, 0.28)
    return S
SEC = sec_tracks()
def fade(f): return 1.0 - sm((f - 21) / 9.0)           # secondary fully gone at f30
def wob(f, T, ph, tau):
    t = f - FIRE
    return fade(f) * math.exp(-t / tau) * math.sin(2 * math.pi * t / T - ph) if t >= 0 else 0.0
def pose(f):
    D = {c: [0.0] * 6 for c in CT}; s = lambda k: SEC[k][f] * fade(f)
    D["CTL_Root_M"][1] = curve(f, K["root_ty"]); D["CTL_Root_M"][2] = curve(f, K["root_tz"]); D["CTL_Root_M"][3] = curve(f, K["root_rx"])
    D["CTL_Spine1_M"][3] = curve(f, K["spine_rx"])
    D["CTL_Shoulder_L"][3] = curve(f, K["shL_rx"]); D["CTL_Shoulder_L"][4] = curve(f, K["shL_ry"]); D["CTL_Shoulder_L"][5] = curve(f, K["shL_rz"])
    D["CTL_Elbow_L"][4] = curve(f, K["elL_ry"]); D["CTL_Elbow_L"][5] = curve(f, K["elL_rz"]); D["CTL_Wrist_L"][5] = curve(f, K["wrL_rz"])
    D["CTL_Elbow_R"][5] = curve(f, K["elR_rz"]); D["CTL_Wrist_R"][5] = curve(f, K["wrR_rz"])
    D["CTL_Head_M"][3] = curve(f, K["head_rx"]) - 0.5 * s("pl1")
    D["CTL_Tail1_M"][3] = curve(f, K["tail1_rx"]) - 300 * s("yl1"); D["CTL_Tail2_M"][3] = -450 * s("yl2") + 6 * wob(f, 9, 0.5, 6); D["CTL_Tail3_M"][3] = -600 * s("yl3") + 10 * wob(f, 9, 1.0, 6)
    D["CTL_Tail1_M"][4] = 8 * wob(f, 12, 0.2, 7); D["CTL_Tail2_M"][4] = 12 * wob(f, 12, 0.9, 7); D["CTL_Tail3_M"][4] = 18 * wob(f, 12, 1.6, 7)
    D["CTL_Ear1_L"][3] = -300 * s("zl1"); D["CTL_Ear1_R"][3] = -300 * s("zl1"); D["CTL_Ear2_L"][3] = -500 * s("zl2"); D["CTL_Ear2_R"][3] = -500 * s("zl2")
    D["CTL_Ear1_L"][5] = 3 * wob(f, 10, 0.4, 6); D["CTL_Ear1_R"][5] = -3 * wob(f, 10, 0.9, 6)
    D["CTL_Bell_M"][3] = 350 * s("zl2") + 6 * wob(f, 8, 0.6, 5)
    for n, (g, k) in {"A1": (300, "zl1"), "A2": (400, "zl2"), "A3": (500, "zl3"), "B1": (300, "zl2"), "B2": (400, "zl3"), "B3": (500, "zl3")}.items():
        D["CTL_Tassel%s_M" % n][3] = g * s(k); D["CTL_Tassel%s_M" % n][5] = (1 if n[0] == "A" else -1) * 8 * wob(f, 9, 0.5 + 0.5 * int(n[1]), 6)
    D["CTL_Jar_M"][1] = -0.4 * s("yl3"); D["CTL_Jar_M"][2] = -0.3 * s("zl3")
    for sd, g in (("L", 1.0), ("R", 0.9)):
        D["CTL_Hip_%s" % sd][3] = 300 * g * s("zl1"); D["CTL_Ankle_%s" % sd][3] = 450 * g * s("zl2"); D["CTL_Toes_%s" % sd][3] = 250 * g * s("zl3")
    return D
# ---------- solvers (no frame changes: the curves already hold a key at every frame, so rotate/move stick)
def solve3(A, b):
    def det(M): return (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1]) - M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0]) + M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
    d = det(A)
    if abs(d) < 1e-14: return [0, 0, 0]
    out = []
    for k in range(3):
        M = [r[:] for r in A]
        for i in range(3): M[i][k] = b[i]
        out.append(det(M) / d)
    return out
def solve_rot(ctl, joint, target, r, free, iters=25, lam=1e-4, mu=0.004, lim=45.0):
    # Gauss-Newton on the euler angles (deg); positions in cm so the normal equations are well scaled
    r = list(r); n = len(free); prior = BASE[ctl][3:6]       # pull towards the idle euler values: stops the solver spinning the limb around its own axis / hopping branches
    for _ in range(iters):
        api.rotate(ctl, *r); p = wp(joint); e = [100 * (target[i] - p[i]) for i in range(3)]
        if sum(x * x for x in e) < 1e-4: break
        J = []
        for k in free:
            r2 = r[:]; r2[k] += 2.0; api.rotate(ctl, *r2); q = wp(joint); J.append([100 * (q[i] - p[i]) / 2.0 for i in range(3)])
        A = [[(sum(J[a][i] * J[b][i] for i in range(3)) + ((lam + mu) if a == b else 0)) if (a < n and b < n) else (1.0 if a == b else 0.0) for b in range(3)] for a in range(3)]
        g = [sum(J[a][i] * e[i] for i in range(3)) + mu * (prior[free[a]] - r[free[a]]) if a < n else 0.0 for a in range(3)]
        dx = solve3(A, g)
        for a, k in enumerate(free): r[k] = max(prior[k] - lim, min(prior[k] + lim, r[k] + max(-25, min(25, dx[a]))))      # stay within +-lim of the idle value (no hyper-bent elbows)
    api.rotate(ctl, *r); return r
def solve_move(ctl, joint, target, t, iters=5):
    t = list(t)
    for _ in range(iters):
        api.move(ctl, *t); p = wp(joint); e = [target[i] - p[i] for i in range(3)]
        if sum(x * x for x in e) < 1e-10: break
        J = []
        for k in range(3):
            t2 = t[:]; t2[k] += 0.01; api.move(ctl, *t2); q = wp(joint); J.append([(q[i] - p[i]) / 0.01 for i in range(3)])
        dt = solve3([[J[k][i] for k in range(3)] for i in range(3)], e)
        for k in range(3): t[k] += dt[k]
    api.move(ctl, *t); return t
def coin_axes():
    m = api.world_matrix("DEF_Coin_L")
    def n(v):
        l = math.sqrt(sum(c * c for c in v)); return [c / l for c in v]
    return n(m[0:3]) + n(m[4:7])
def solve_coin_rot(r, phi, iters=14):
    a = math.radians(phi); T = [math.cos(a), 0, -math.sin(a), 0, 1, 0]
    res = lambda: [T[i] - coin_axes()[i] for i in range(6)]
    r = list(r)
    for _ in range(iters):
        api.rotate("CTL_Coin_L", *r); e = res()
        if sum(x * x for x in e) < 1e-8: break
        J = []
        for k in range(3):
            r2 = r[:]; r2[k] += 1.0; api.rotate("CTL_Coin_L", *r2); e2 = res(); J.append([(e[i] - e2[i]) for i in range(6)])
        A = [[sum(J[a][i] * J[b][i] for i in range(6)) + (1e-6 if a == b else 0) for b in range(3)] for a in range(3)]
        g = [sum(J[a][i] * e[i] for i in range(6)) for a in range(3)]
        dx = solve3(A, g)
        for k in range(3): r[k] += max(-60, min(60, dx[k]))
    api.rotate("CTL_Coin_L", *r); return r
# ---------- build
def apply_base():
    for c in CT:
        b = BASE[c]; api.rotate(c, b[3], b[4], b[5]); api.scale(c, b[6], b[7], b[8])
        if c != "CTL_Main": api.move(c, b[0], b[1], b[2])
def build():
    api.set_frame_range(0, N); api.set_frame(0); apply_base()
    api.select(CT); api.set_key(); api.select([])
    for f in range(0, N + 1):                                    # key the idle pose on every frame first (rotate only sticks on keyed curves)
        api.set_frame(f); api.select(CT); api.set_key()
    api.set_frame(0); apply_base()
    ref = {"wrist_L": wp("DEF_Wrist_L"), "elbow_L": wp("DEF_Elbow_L"), "coin": wp("DEF_Coin_L"), "wrist_R": wp("DEF_Wrist_R"), "elbow_R": wp("DEF_Elbow_R")}
    seed = {c: BASE[c][3:6] for c in ("CTL_Shoulder_L", "CTL_Elbow_L", "CTL_Shoulder_R", "CTL_Elbow_R", "CTL_Coin_L")}
    cmove = BASE["CTL_Coin_L"][0:3]; log = []; P10 = [0, 0, 0]
    for f in range(0, N + 1):
        api.set_frame(f)
        D = pose(f)
        for c in CT:
            b = BASE[c]; d = D[c]
            api.rotate(c, b[3] + d[3], b[4] + d[4], b[5] + d[5])
            if c != "CTL_Main": api.move(c, b[0] + d[0], b[1] + d[1], b[2] + d[2])
            api.scale(c, b[6], b[7], b[8])
        ro = [D["CTL_Root_M"][0], D["CTL_Root_M"][1], D["CTL_Root_M"][2]]
        add = lambda p, o: [p[i] + ro[i] + o[i] for i in range(3)]
        wcur = wp("DEF_Wrist_L")                                  # the coin rides the REAL hand until it is flicked off at FIRE
        hand_coin = [wcur[i] + ref["coin"][i] - ref["wrist_L"][i] for i in range(3)]
        if f == FIRE: P10[:] = hand_coin
        if f in COIN_FLY: ctarget = [P10[i] + COIN_FLY[f][i] for i in range(3)]
        else: ctarget = hand_coin
        cmove = solve_move("CTL_Coin_L", "DEF_Coin_L", ctarget, cmove)
        cs = curve(f, SCALE); api.scale("CTL_Coin_L", cs, cs, cs)
        phi = curve(f, SPIN)
        rc = solve_coin_rot(seed["CTL_Coin_L"], phi % 360)
        seed["CTL_Coin_L"] = rc
        if f in (0, N):
            api.rotate("CTL_Coin_L", *BASE["CTL_Coin_L"][3:6]); api.move("CTL_Coin_L", *BASE["CTL_Coin_L"][0:3])
        api.select(CT); api.set_key(); api.select([])
        log.append((f, [round(x, 3) for x in wp("DEF_Wrist_L")], [round(x, 3) for x in wp("DEF_Coin_L")]))
    # unwrap the euler angles so no key jumps by more than 180 deg between frames (the coin spin flips the decomposition)
    for c in CT:
        vals = []
        for f in range(0, N + 1): api.set_frame(f); vals.append([api.get_attr(c + "." + a) for a in ("rx", "ry", "rz")])
        fixed = False
        for f in range(1, N + 1):
            for i in range(3):
                while vals[f][i] - vals[f - 1][i] > 180: vals[f][i] -= 360; fixed = True
                while vals[f][i] - vals[f - 1][i] < -180: vals[f][i] += 360; fixed = True
        if fixed:
            for f in range(0, N + 1):
                api.set_frame(f); api.rotate(c, *vals[f]); api.select([c]); api.set_key()
    api.select([]); api.set_frame(1); api.set_frame(0)
    return log
LOG = build()
print("L wrist, coin:", [LOG[i] for i in (0, 4, 7, 9, 10, 12, 16, 20, 30)])
