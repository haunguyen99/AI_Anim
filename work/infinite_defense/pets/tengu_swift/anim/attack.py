"""Tengu Swift Attack 30f: 0-5 lui nguoi, quat ra sau; 5-15 xoay 360 do (trai), 16 = CHEM/BAN (quat quet sang trai); 17-24 giat lai tat dan; 30 = Idle f0."""
import math
N = 30; FIRE = 12
KEYS = {}   # frame -> {ctl: (rx,ry,rz,tx,ty,tz)} overrides on top of idle(0)
def Z(): return [0, 0, 0, 0, 0, 0]
def kp(f, **d): KEYS[f] = d
kp(0)
kp(3,  Root_M=(10, -25, 0, 0, 0.09, -0.03), Spine1_M=(8, -15, 0), Head_M=(-6, 20, 0), Arm_R=(0, -40, 40), Hand_R=(0, 0, 10), Fan1_R=(60, 0, 0), Arm_L=(0, 10, -60), Hand_L=(0, 0, -15), Leg_L=(-25, 0, 0), Leg_R=(-25, 0, 0), Foot_L=(25, 0, 0), Foot_R=(25, 0, 0), Hair1_M=(-12, 0, 0), Hair2_M=(-12, 0, 0))
kp(6,  Root_M=(4, 190, 0, 0, 0.13, 0), Spine1_M=(0, 20, 0), Head_M=(0, -15, 0), Arm_R=(0, -10, 55), Fan1_R=(80, 0, 0), Arm_L=(0, 0, -70), Leg_L=(-15, 0, 0), Leg_R=(-15, 0, 0), Foot_L=(18, 0, 0), Foot_R=(18, 0, 0), Hair1_M=(-22, 0, 0), Hair2_M=(-25, 0, 0), Tuft1_L=(0, -30, 0), Tuft1_R=(0, 30, 0), Tuft2_L=(0, -25, 0), Tuft2_R=(0, 25, 0))
kp(9,  Root_M=(6, 340, 0, 0, 0.12, 0.02), Spine1_M=(0, 30, 0), Head_M=(0, -25, 0), Arm_R=(0, 40, 40), Fan1_R=(100, -50, 0), Arm_L=(0, 0, -50), Hair1_M=(-15, 0, 0), Hair2_M=(-20, 0, 0))
kp(FIRE, Root_M=(-4, 412, 4, 0.0, 0.12, 0.10), Spine1_M=(-4, 5, 0), Head_M=(0, 25, 0), Arm_R=(0, 100, 40), Hand_R=(0, 0, 0), Fan1_R=(120, -90, 0), Fan2_R=(0, 0, 10), Arm_L=(0, 20, -30), Hair1_M=(10, 0, 0), Hair2_M=(14, 0, 0))
kp(15, Root_M=(0, 398, 0, 0, 0.14, 0.05), Spine1_M=(0, 0, 0), Head_M=(0, 10, 0), Arm_R=(0, 85, 35), Fan1_R=(110, -80, -10), Fan2_R=(0, 0, -8), Arm_L=(0, 0, -35), Hair1_M=(-8, 0, 0), Hair2_M=(-10, 0, 0))
kp(21, Root_M=(0, 372, 0, 0, 0.12, 0.01), Arm_R=(0, 60, 22), Fan1_R=(30, 0, -15), Arm_L=(0, 0, -38), Hair1_M=(4, 0, 0), Hair2_M=(5, 0, 0))
kp(26, Root_M=(-0.5, 364, 1.5), Arm_R=(0, 36, 19), Fan1_R=(10, 0, -5), Arm_L=(0, -3, -38), Hair1_M=(-1, 0, 0), Hair2_M=(-1, 0, 0))
kp(30, Root_M=(-1.44, 360, 3.73))
def _cat(a, b, c, d, t):
    return 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
def build(api, idle_pose, CTLS, apply):
    base = idle_pose(0)
    ks = sorted(KEYS)
    def vals(f, ctl):
        d = KEYS[f]; n = ctl[4:]
        v = list(base[ctl])
        if n in d:
            o = list(d[n]) + [0] * (6 - len(d[n])); 
            for i in range(6):
                v[i] = o[i] + (base[ctl][i] if i >= 3 and i != 4 else 0) if False else o[i]
            if ctl == "CTL_Fan1_R": v[3:] = base[ctl][3:]
            if ctl != "CTL_Root_M" and len(d[n]) <= 3: v[3:] = base[ctl][3:]
            if ctl == "CTL_Root_M" and len(d[n]) < 6: v[3:] = base[ctl][3:]
        return v
    def pose(f):
        i = max(j for j in range(len(ks)) if ks[j] <= f)
        if i == len(ks) - 1: i -= 1
        k0, k1 = ks[i], ks[i + 1]; t = (f - k0) / (k1 - k0)
        ia = ks[max(i - 1, 0)]; ib = ks[min(i + 2, len(ks) - 1)]
        P = {}
        for c in CTLS:
            a0 = vals(ia, c); a = vals(k0, c); b = vals(k1, c); b1 = vals(ib, c)
            P[c] = [_cat(a0[m], a[m], b[m], b1[m], t) for m in range(6)]       # Catmull-Rom: van toc lien tuc qua cac key, khong dung lai o tung key
        return P
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); apply(api, pose(f)); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
