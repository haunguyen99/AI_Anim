"""Hero RPG2 (Char_Main_T2) skin rules, 2026-11-04. Run inside Frolvy after Build Rig:
    import sys; sys.path.insert(0, r"D:\\Project\\AI_Anim\\.claude\\skills\\frolvy_auto_rig\\scripts")
    sys.path.insert(0, r"D:\\Project\\AI_Anim\\work\\rpg2_hero\\rig")
    import importlib, auto_rig as A, skin_hero as S; importlib.reload(A); importlib.reload(S)
    S.run(api, A)
Every vertex is written from rules, piece (shell) by piece. Heights in metres, bind pose.
Body shells (A.survey): 0 torso+head+upper arms, 1/2 hands, 3 pants, 4/5 boots, 6 sash, 7 skirt,
8 belt, 9/10 + 14/15 forearm guards, 11/13 shoulder pads, 12 chest piece, 16 front flap,
17/18 hand bands, 19-24 upper-arm straps, 25/26/28 belt buckles, 27 chest buckle.
"""
import math

ROOT, SP1, CH, NECK, HEAD = "DEF_Root_M", "DEF_Spine1_M", "DEF_Chest_M", "DEF_Neck_M", "DEF_Head_M"
SMOOTH = (2, 0.35)    # joint smoothing: iterations, strength ("a little")
ELBOW_PLUG = (0.49, 0.515, 0.5)   # Elbow share: 0 -> 0.5 over |x| 0.49-0.515 (one ring), 100% only for the tip inside the forearm guard (>= 0.515)
CROTCH_Y = 0.71     # the pants split into two legs below this (measured: centre seam ends at 0.70-0.72)


def run(api, A):
    ramp = A.ramp

    def side(x):
        return "_R" if x < 0 else "_L"

    def spine(y):
        sp = ramp(y, 0.93, 1.06); ch = ramp(y, 1.06, 1.17)   # from the belt's bottom, so torso and belt meet
        return {ROOT: 1 - sp, SP1: sp * (1 - ch), CH: sp * ch}

    def belt(y):
        # the Spine1 joint (0.956) sits inside the belt (0.93-1.05): Root at the bottom edge, mostly
        # Spine1 at the top. User 2026-11-04: "skin phần đai khi xoay spine1 cứng quá" - with Root
        # + 15% Spine1 the belt moved 3 mm while the torso above moved 9 cm on a 30 deg twist.
        f = 0.15 + 0.6 * ramp(y, 0.93, 1.05)
        return {ROOT: 1 - f, SP1: f}

    def mix(a, fa, b):
        out = {}
        for d, f in ((a, fa), (b, 1 - fa)):
            for j, w in d.items():
                out[j] = out.get(j, 0) + w * f
        return out

    def scale(d, f):
        return {j: w * f for j, w in d.items()}

    def torso(p):
        x, y, z = p; ax = abs(x); s = side(x)
        rad = math.hypot(x, z - 0.05)                  # distance from the neck axis
        if y > 1.40 and ax < 0.2:
            return {HEAD: 1.0}
        if y > 1.37 and rad > 0.115 and ax < 0.2:      # chin / jaw
            return {HEAD: 1.0}
        if y > 1.315 and rad <= 0.115:                 # neck column (r 0.08-0.11, y 1.32-1.38): graded
            c = 1 - ramp(y, 1.315, 1.345); h = ramp(y, 1.36, 1.395)
            return {CH: c, NECK: (1 - c) * (1 - h), HEAD: (1 - c) * h}
        # the collar (r >= 0.13 below 1.33) falls through to the torso: 100% spine, never Head/Neck
        sh = 0.0
        if ax > 0.17 and 1.13 < y < 1.38:                    # shoulder and upper arm
            sh = ramp(ax, 0.19, 0.30) * (1 - (1 - ramp(y, 1.13, 1.20)) * (1 - ramp(ax, 0.30, 0.34)))
        sc = (1 - sh) * scap(p)
        # the upper arm's end sits INSIDE the forearm guard tube (guard starts at |x| 0.515, rigid on Elbow):
        # it must ride the Elbow fully there, else a bent elbow pulls it out of the open tube (user
        # 2026-11-04: "xoay khuỷu tay bị hở mesh"; it had 35-50% Elbow)
        # only the tip inside the tube is rigid (user: "chỉ gắn cứng phần mesh ở đầu thôi" - a long band
        # 0.38-0.515 put the whole upper arm on Elbow and it dented when rotating); before the tip, at most
        # ELBOW_PLUG[2] Elbow over one ring of vertices, as before
        el = 1.0 if ax >= ELBOW_PLUG[1] else ELBOW_PLUG[2] * ramp(ax, ELBOW_PLUG[0], ELBOW_PLUG[1])
        out = scale(spine(y), 1 - sh - sc)
        if sh > 0:
            out["DEF_Shoulder" + s] = sh * (1 - el); out["DEF_Elbow" + s] = sh * el
        if sc > 0:
            out["DEF_Scapula" + s] = sc
        return out

    def scap(p):
        """Shoulder-blade share. User 2026-11-04, twice: rotating the Scapula control the shoulder
        blade must follow more strongly, then "the mesh lying on the scapula follows the scapula
        fully". 100% over the scapula bone (|x| 0.11 -> shoulder joint, y 1.22-1.37), short blends:
        to the spine by |x| 0.06, below the armpit by y 1.12, to the head at 1.37-1.40; the Shoulder
        share (arm) is taken first by the caller. The collar ring at |x| < 0.06 keeps the chest."""
        x, y, z = p; ax = abs(x)
        if y < 1.10 or y > 1.40:
            return 0.0
        across = ramp(ax, 0.06, 0.11)
        height = ramp(y, 1.12, 1.22) * (1 - ramp(y, 1.37, 1.40))
        return across * height

    def hand(p):
        s = side(p[0]); f = lambda n: "DEF_%s%s" % (n, s)  # noqa: E731
        bones = [(f("Wrist"), f("MiddleFinger1"), f("Elbow")),
                 (f("MiddleFinger1"), f("MiddleFinger2"), f("Wrist")),
                 (f("MiddleFinger2"), f("MiddleFinger3"), f("MiddleFinger1")),
                 (f("MiddleFinger3"), f("MiddleFinger4"), f("MiddleFinger2"))]
        # only the thumb itself (it sticks out in front, z > 0.105) follows the thumb bones:
        # palm vertices that were nearer the thumb bone tore x4.8 on a 40 deg thumb curl
        if p[2] > 0.11 and p[1] < 1.26 and abs(p[0]) < 0.875:   # thumb: y 1.19-1.256, x 0.77-0.87
            bones = [(f("Wrist"), f("ThumbFinger1"), f("Elbow")),
                     (f("ThumbFinger1"), f("ThumbFinger2"), f("Wrist")),
                     (f("ThumbFinger2"), f("ThumbFinger3"), f("ThumbFinger1")),
                     (f("ThumbFinger3"), f("ThumbFinger4"), f("ThumbFinger2"))]
        return A.bone_w(api, p, bones)

    def leg(p):
        """Pants and boots by BONE OWNERSHIP, like the arms (user 2026-11-04: "why do the arms not dent
        but the legs do - many leg vertices are on the wrong joint"). Height bands not tied to the
        joints had put the boot shaft (shin) on Ankle (ankle joint is at y 0.10) and the outer thigh
        above y 0.77 on Root (hip joint is at 0.80): 74 of 545 leg vertices. Now: owner = joint of the
        nearest leg bone, 50% at each joint (bone_w); Root only for the pelvis ABOVE the hip joint,
        less on the outer hip; the inner thigh below the crotch (y 0.70) is leg only."""
        x, y, z = p; ax = abs(x); s = side(x)
        f = lambda n: "DEF_%s%s" % (n, s)  # noqa: E731
        hy = A._jp(api, f("Hip"))[1]
        if ax < 0.004:                       # centre seam (any height): both legs, pelvis above the crotch
            r = 0.3 + 0.7 * ramp(y, CROTCH_Y - 0.03, hy + 0.10)
            return {ROOT: r, "DEF_Hip_L": (1 - r) / 2, "DEF_Hip_R": (1 - r) / 2}
        w = A.bone_w(api, p, [(f("Hip"), f("Knee"), None), (f("Knee"), f("Ankle"), f("Hip")),
                              (f("Ankle"), f("Toes"), f("Knee")), (f("Toes"), f("ToesEnd"), f("Ankle"))],
                     blend=0.15)
        # pelvis band from a bit below the hip joint: the pants rows are 9 cm apart there, a short band
        # left one row 100% Hip next to one 70% Root (groin fold x0.13)
        r = ramp(y, hy - 0.10, hy + 0.12) * (1 - 0.7 * ramp(ax, 0.15, 0.24))
        if y > CROTCH_Y - 0.05 and ax < 0.06:   # around the crotch, where the two legs meet
            r = max(r, 0.3 * (1 - ramp(ax, 0.0, 0.06)) + 0.3 * ramp(y, CROTCH_Y, CROTCH_Y + 0.04) * (1 - ramp(ax, 0.0, 0.06)))
        out = scale(w, 1 - r)
        if r > 0:
            out[ROOT] = out.get(ROOT, 0) + r
        return out

    pants = boot = leg

    def chain(name, sfx, n):
        return ["DEF_%s%d%s" % (name, k, sfx) for k in range(1, n + 1)] + ["DEF_%sEnd%s" % (name, sfx)]

    def skirt(p):
        x, y, z = p
        ang = abs(math.degrees(math.atan2(x, z - 0.07)))
        back = A.chain_w(api, p, chain("SkirtBack", "_M", 3), ROOT, top=0.3)
        sidew = A.chain_w(api, p, chain("SkirtSide", side(x), 3), ROOT, top=0.3)
        return mix(back, ramp(ang, 145, 160), sidew)

    rules = {0: torso, 1: hand, 2: hand, 3: pants, 4: boot, 5: boot,
             6: lambda p: {ROOT: 1.0},
             7: skirt,
             8: lambda p: belt(p[1]),
             12: lambda p: dict(scale(spine(p[1]), 1 - scap(p)), **{"DEF_Scapula" + side(p[0]): scap(p)}),
             16: lambda p: A.chain_w(api, p, chain("SkirtFront", "_M", 3), ROOT, top=0.3),
             27: lambda p: {CH: 1.0}}
    for k in (9, 10, 14, 15):
        rules[k] = lambda p: {"DEF_Elbow" + side(p[0]): 1.0}
    for k in (11, 13, 19, 20, 21, 22, 23, 24):
        rules[k] = lambda p: {"DEF_Shoulder" + side(p[0]): 1.0}
    for k in (17, 18):
        rules[k] = lambda p: {"DEF_Wrist" + side(p[0]): 1.0}
    for k in (25, 26, 28):                           # buckles: rigid, riding the belt where they sit
        rules[k] = lambda p, k=k: belt(buckle_y[k])

    def hood(p):
        c = 1 - ramp(p[1], 1.30, 1.40)                # drape over the shoulders stays with the chest
        sc = c * ramp(abs(p[0]), 0.06, 0.11)          # ... the part lying on the scapula rides it fully
        out = {CH: c - sc, HEAD: 1 - c}
        if sc > 0:
            out["DEF_Scapula" + side(p[0])] = sc
        return out

    body = A.R.Mesh(api, A._obj(api, "body"))
    buckle_y = {k: sum(body.p(i)[1] for i in body.shells[k]) / len(body.shells[k]) for k in (25, 26, 28)}
    out = {}
    out["body"] = A.write_skin(api, "body", lambda i, p, sh: rules.get(sh, torso)(p))
    out["hood"] = A.write_skin(api, "hood", lambda i, p, sh: hood(p))
    out["scarf_1"] = A.write_skin(api, "scarf_1", lambda i, p, sh: A.chain_w(api, p, chain("ScarfA", "_R", 4), "DEF_Scapula_R", top=0.3))  # its top lies on the right shoulder blade
    out["scarf_2"] = A.write_skin(api, "scarf_2", lambda i, p, sh: A.chain_w(api, p, chain("ScarfB", "_R", 3), ROOT, top=0.3))
    # a little smoothing at the limb joints (user 2026-11-04: "skin tay chân ổn, smooth 1 chút ở các
    # khớp"): only the split between the two joints of each joint moves; rigid pieces and the crotch
    # seam are left as they are
    pairs = []
    for s in ("_L", "_R"):
        j = lambda n: "DEF_%s%s" % (n, s)  # noqa: E731
        pairs += [(ROOT, j("Hip"), lambda i, p: abs(p[0]) < 0.06),          # crotch keeps its split
                  (j("Hip"), j("Knee"), lambda i, p: p[2] < 0.06 and abs(p[1] - 0.44) < 0.1),  # back of knee stays tight
                  (j("Knee"), j("Ankle")), (j("Ankle"), j("Toes")),
                  (j("Scapula"), j("Shoulder")),
                  (j("Shoulder"), j("Elbow"), lambda i, p: abs(p[0]) >= ELBOW_PLUG[1]),  # plug stays 100% Elbow
                  (j("Wrist"), j("MiddleFinger1")), (j("MiddleFinger1"), j("MiddleFinger2")),
                  (j("MiddleFinger2"), j("MiddleFinger3")), (j("Wrist"), j("ThumbFinger1")),
                  (j("ThumbFinger1"), j("ThumbFinger2")), (j("ThumbFinger2"), j("ThumbFinger3"))]
    rigid = (9, 10, 11, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28)
    out["smoothed"] = A.smooth_pairs(api, "body", pairs, iters=SMOOTH[0], k=SMOOTH[1], skip_shells=rigid,
                                     skip=lambda i, p: abs(p[0]) < 0.004)
    print("weights written:", out)
    return out
