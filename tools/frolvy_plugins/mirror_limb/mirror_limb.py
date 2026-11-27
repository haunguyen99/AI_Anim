"""Mirror Limb - copy one arm's animation to the other by CURVES (user 2026-11-26, Hero Blade/Staff run).

Rule (user): when symmetry is needed, the two arms get the SAME CURVES and the SAME WORLD PATH of the hand,
same frames (no time offset). Chosen over "mirror relative to the chest": the chest twists while running, so a
chest-space mirror made the other hand 20+ cm higher/lower in the world and the curves differed.

Inside Frolvy (execute_code), or from Linux:
    echo "exec(open(r'<repo>/tools/frolvy_plugins/mirror_limb/mirror_limb.py', encoding='utf-8').read()); mirror_arm(api, 'L')" \
        | python3 -I tools/frolvy_call.py <port> -
    mirror_arm(api, 'L')   # left -> right  ('R' = right -> left)
    mirror_arm(api, 'L', dry=True)   # only check + report, write nothing

What it does:
  1. reads the source arm switch (CTL_ArmSwitch_<side>.fkIk): IK (>0.5) -> copies CTL_IKWrist + CTL_PoleArm (+ Scapula);
     FK -> copies CTL_Scapula, Shoulder, Elbow, Wrist. The other side's switch is set to the same mode (no autoSnap,
     its old keys on fkIk are removed, `space` copied);
  2. channel rule: tx x -1, ty / tz same, rx same, ry / rz x -1 (rigs from the Rig Builder: left and right control
     frames are mirrors). It first CHECKS that rule on the rig (offsets of every pair of controls must be mirrors of
     each other); a rig that fails is refused, nothing is written;
  3. same frames as the source keys (default 0..last key), keys on every frame (pass 1 creates the keys, because
     set_attr on a channel without keys does not stick - found 2026-11-26);
  4. prints the check: worst curve difference, world difference of the wrists (x mirror, height, forward) and the
     elbow bend difference. A big elbow difference = the torso twist makes the shoulders asymmetric; that is the
     price of "same hand path" (tell the user, offer to lower the pole).
Not touched: fingers, the weapon, the torso, the other limbs. Legs are not done yet (same idea, IKAnkle / PoleLeg).
"""
import math

SGN = {"tx": -1, "ty": 1, "tz": 1, "rx": 1, "ry": -1, "rz": -1}
CH6 = ("tx", "ty", "tz", "rx", "ry", "rz")
CH3 = ("rx", "ry", "rz")


def _M(m):
    return [[m[0], m[4], m[8]], [m[1], m[5], m[9]], [m[2], m[6], m[10]]]


def _mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _T(a):
    return [[a[j][i] for j in range(3)] for i in range(3)]


_S = [[-1, 0, 0], [0, 1, 0], [0, 0, 1]]


def _P(api, n):
    m = api.world_matrix(n)
    return [m[12], m[13], m[14]]


def _mirror_check(api, chain_src, chain_dst, parent0="CTL_Chest_M"):
    """Offsets of each control (to its parent) must be mirrors of the other side's, else the sign rule is wrong.
    The scapula group hangs under CTL_Chest_M_follow (it follows the DEF chest), which can differ from CTL_Chest_M by ~1 deg
    when the spine is posed, so that follow group is the reference when it exists."""
    if parent0 == "CTL_Chest_M" and "CTL_Chest_M_follow" in set(api.ls()):
        parent0 = "CTL_Chest_M_follow"
    api.set_frame(0)
    bad = []
    pl, pr = parent0, parent0
    for a, b in zip(chain_src, chain_dst):
        ol = _mul(_T(_M(api.world_matrix(pl))), _M(api.world_matrix(a + "_grp")))
        orr = _mul(_T(_M(api.world_matrix(pr))), _M(api.world_matrix(b + "_grp")))
        want = _mul(_mul(_S, ol), _S)
        d = max(abs(want[i][j] - orr[i][j]) for i in range(3) for j in range(3))
        if d > 1e-3:
            bad.append((a, round(d, 4)))
        pl, pr = a, b
    return bad


def _ik_check(api, L, R):
    api.set_frame(0)
    bad = []
    for a, b in zip(L, R):
        gl, gr = _M(api.world_matrix(a + "_grp")), _M(api.world_matrix(b + "_grp"))
        want = _mul(_mul(_S, gl), _S)
        d = max(abs(want[i][j] - gr[i][j]) for i in range(3) for j in range(3))
        if d > 1e-3:
            bad.append((a, round(d, 4)))
    return bad


def _ang(a, b, c):
    u = [a[i] - b[i] for i in range(3)]
    v = [c[i] - b[i] for i in range(3)]
    return math.degrees(math.acos(max(-1, min(1, sum(x * y for x, y in zip(u, v)) / (math.dist(a, b) * math.dist(c, b))))))


def _cr(v, u):
    """Periodic Catmull-Rom sample of the list v (one value per frame of a loop; F_last == F_0 is NOT in v) at time u."""
    n = len(v)
    i = int(math.floor(u)); t = u - i
    p0, p1, p2, p3 = v[(i - 1) % n], v[i % n], v[(i + 1) % n], v[(i + 2) % n]
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def mirror_arm(api, src="L", dry=False, shift=0.0, log=print):
    s, d = src.upper(), ("R" if src.upper() == "L" else "L")
    sw_s, sw_d = "CTL_ArmSwitch_%s" % s, "CTL_ArmSwitch_%s" % d
    api.set_frame(0)
    ik = api.get_attr(sw_s + ".fkIk") > 0.5
    n = lambda k, side: "CTL_%s_%s" % (k, side)
    if ik:
        pairs = [(n("IKWrist", s), n("IKWrist", d), CH6), (n("PoleArm", s), n("PoleArm", d), CH6), (n("Scapula", s), n("Scapula", d), CH3)]
        bad = _ik_check(api, [p[0] for p in pairs[:2]], [p[1] for p in pairs[:2]]) + \
            _mirror_check(api, [n("Scapula", s)], [n("Scapula", d)])
    else:
        ks = ("Scapula", "Shoulder", "Elbow", "Wrist")
        pairs = [(n(k, s), n(k, d), CH3) for k in ks]
        bad = _mirror_check(api, [p[0] for p in pairs], [p[1] for p in pairs])
    log("mirror_arm %s -> %s, mode %s" % (s, d, "IK" if ik else "FK"))
    if bad:
        log("REFUSED: left/right frames are not mirrors, the sign rule would be wrong: %s" % bad)
        return False
    frames = sorted({int(f) for p in pairs for c in p[2] for f in api.list_keys(p[0] + "." + c)})
    if not frames:
        log("REFUSED: the source arm has no keys")
        return False
    log("frames %d..%d (%d keys per channel)" % (frames[0], frames[-1], len(frames)))
    if dry:
        log("dry run: nothing written")
        return True
    # switch of the destination side = same mode, no snap
    if ik:
        api.set_frame(frames[0])
        for f in api.list_keys(sw_d + ".fkIk"):
            api.delete_key(sw_d + ".fkIk", int(f))
        api.set_attr(sw_d + ".autoSnap", 0)
        api.set_attr(sw_d + ".fkIk", 1)
        for k in ("IKWrist", "PoleArm"):
            api.set_attr(n(k, d) + ".space", api.get_attr(n(k, s) + ".space"))
    vals = {}
    srcv = {}
    for f in frames:
        api.set_frame(f)
        for a, b, chs in pairs:
            srcv[(a, f)] = {c: api.get_attr(a + "." + c) for c in chs}
    if shift:
        # half-cycle (or any) offset: right at frame f = mirrored left at time f - shift, loop of N = last-first frames,
        # sampled with a periodic cubic (smooth between frames). The wrap is unwrapped on rotation channels first.
        N = frames[-1] - frames[0]
        f0 = frames[0]
        for a, b, chs in pairs:
            for c in chs:
                seq = [srcv[(a, f)][c] for f in frames[:-1]]
                if c.startswith("r"):                       # unwrap euler around the loop
                    for k in range(1, len(seq)):
                        seq[k] += 360 * round((seq[k - 1] - seq[k]) / 360.0)
                for f in frames:
                    u = (f - f0 - shift) % N
                    vals.setdefault((b, f), []).append((c, SGN[c] * _cr(seq, u)))
        log("offset %.1f frames of a %d-frame cycle (Catmull-Rom between frames)" % (shift, N))
    else:
        for f in frames:
            for a, b, chs in pairs:
                vals[(b, f)] = [(c, SGN[c] * srcv[(a, f)][c]) for c in chs]
    dst = [p[1] for p in pairs]
    for f in frames:                      # pass 1: make the keys (set_attr alone does not stick on a channel without keys)
        api.set_frame(f)
        api.select(dst)
        api.set_key()
    for f in frames:                      # pass 2: values
        api.set_frame(f)
        for a, b, chs in pairs:
            for c, v in vals[(b, f)]:
                api.set_attr(b + "." + c, v)
        api.select(dst)
        api.set_key()
    # check
    if shift:
        def rng(n, c):
            v = []
            for f in frames:
                api.set_frame(f); v.append(api.get_attr(n + "." + c))
            return v
        main = [p for p in pairs if "IKWrist" in p[0]] or [p for p in pairs if "Shoulder" in p[0]]
        for a, b, chs in main:
            for c in ("tz", "ty") if "IKWrist" in a else ("ry",):
                va, vb = rng(a, c), rng(b, c)
                log("%s: range src %.1f dst %.1f | peak frame src F%d dst F%d | trough src F%d dst F%d" % (c, max(va) - min(va), max(vb) - min(vb), frames[va.index(max(va))], frames[vb.index(max(vb))], frames[va.index(min(va))], frames[vb.index(min(vb))]))
        for f in frames:
            pass
        log("done (shifted copy; strict L/R curve equality does not apply)")
        return True
    worst = {}
    wx = wy = wz = 0.0
    elb = []
    for f in frames:
        api.set_frame(f)
        for a, b, chs in pairs:
            for c in chs:
                dd = abs(api.get_attr(b + "." + c) - SGN[c] * api.get_attr(a + "." + c))
                worst[a] = max(worst.get(a, 0), dd)
        ps, pd = _P(api, "DEF_Wrist_" + s), _P(api, "DEF_Wrist_" + d)
        wx, wy, wz = max(wx, abs(ps[0] + pd[0])), max(wy, abs(ps[1] - pd[1])), max(wz, abs(ps[2] - pd[2]))
        elb.append(_ang(_P(api, "DEF_Shoulder_" + d), _P(api, "DEF_Elbow_" + d), pd) - _ang(_P(api, "DEF_Shoulder_" + s), _P(api, "DEF_Elbow_" + s), ps))
    log("curve diff (0 = identical): %s" % {k: round(v, 4) for k, v in worst.items()})
    log("wrist in the world: mirror x err %.2f cm, height diff %.2f, forward diff %.2f" % (wx, wy, wz))
    me = max(abs(x) for x in elb)
    log("elbow bend difference, max %.0f deg%s" % (me, "  <- torso twist makes the shoulders asymmetric; tell the user, offer to lower the pole" if me > 15 else ""))
    return True


def register(api):
    api.command("Mirror Limb: Left arm -> Right", lambda: mirror_arm(api, "L", log=api.log))
    api.command("Mirror Limb: Right arm -> Left", lambda: mirror_arm(api, "R", log=api.log))


def _eul(R):
    ry = -math.asin(max(-1, min(1, R[2][0])))
    return [math.degrees(math.atan2(R[2][1], R[2][2])), math.degrees(ry), math.degrees(math.atan2(R[1][0], R[0][0]))]


def spread_arm(api, side="R", deg=6.5, log=print):
    """Open the IK arm `side` outward by `deg` degrees (user 2026-11-26: "tay phải lệch tầm 5-8 độ so với tay trái").
    The whole hand path + pole (+ hand orientation) is rotated about that shoulder, around the world Z (forward) axis,
    the same angle on every frame: rhythm, swing amplitude and reach stay as they are. Run it ONCE right after
    mirror_arm (it is applied on top of the current keys; to redo, run mirror_arm again first). IK arms only."""
    side = side.upper()
    if api.get_attr("CTL_ArmSwitch_%s.fkIk" % side) <= 0.5:
        log("spread_arm: the %s arm is FK, only IK arms are supported" % side)
        return False
    a = math.radians(-deg if side == "R" else deg)       # right arm: outward = -x
    c, s = math.cos(a), math.sin(a)
    Rz = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    ctrls = ("CTL_IKWrist_%s" % side, "CTL_PoleArm_%s" % side)
    frames = sorted({int(f) for f in api.list_keys(ctrls[0] + ".tx")})
    plan = {}
    for f in frames:
        api.set_frame(f)
        sh = _P(api, "DEF_Shoulder_" + side)
        for n in ctrls:
            w = api.world_matrix(n)
            g = api.world_matrix(n + "_grp")
            G = _M(g)
            d = [w[12] - sh[0], w[13] - sh[1], w[14] - sh[2]]
            nd = [sum(Rz[i][k] * d[k] for k in range(3)) for i in range(3)]
            pw = [sh[i] + nd[i] for i in range(3)]
            t = [sum(G[k][i] * (pw[k] - g[12 + k]) for k in range(3)) for i in range(3)]
            e = None
            if "IKWrist" in n:
                cur = [api.get_attr(n + "." + ch) for ch in CH3]
                e = _eul(_mul(_T(G), _mul(Rz, _M(w))))
                e = [x + 360 * round((o - x) / 360.0) for x, o in zip(e, cur)]
            plan[(n, f)] = (t, e)
    for f in frames:
        api.set_frame(f)
        for n in ctrls:
            t, e = plan[(n, f)]
            for ch, v in zip(("tx", "ty", "tz"), t):
                api.set_attr(n + "." + ch, v)
            if e:
                for ch, v in zip(CH3, e):
                    api.set_attr(n + "." + ch, v)
        api.select(list(ctrls))
        api.set_key()
    # check: angle between shoulder->wrist before (mirror) and now is deg by construction; report outward shift
    mx = 0
    for f in frames:
        api.set_frame(f)
        sh, wr = _P(api, "DEF_Shoulder_" + side), _P(api, "DEF_Wrist_" + side)
        mx = max(mx, abs(wr[0] - sh[0]))
    log("spread_arm %s: %.1f deg outward on %d frames (max hand-to-shoulder sideways %.1f cm)" % (side, deg, len(frames), mx))
    return True
