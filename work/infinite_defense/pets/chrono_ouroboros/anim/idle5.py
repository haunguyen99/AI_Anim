"""Chrono Ouroboros Idle v12 (RIG v3, lơ lửng). 72F lặp liền (f72 == f0), 30 fps. Frame 0 = POSE v11 đã duyệt (v3/ring.py), mọi chuyển động là offset triệt tiêu ở f0.
Thành phần (tất cả chu kỳ nguyên 1 hoặc 2 lần/vòng):
 - Lơ lửng: Root lên/xuống ±HB cm (1 nhịp) + ngả nhẹ.
 - SỐ 8 vô cực: đầu và đuôi đổi trước/sau (ry thân và đuôi đảo pha) 1 nhịp, cả vòng xoay nhẹ trong mặt phẳng (Root rx) 2 nhịp => đầu vẽ số 8.
 - Thân trôi quanh vòng: sóng độ cong chạy dọc thân + đuôi (±WV độ mỗi khớp).
 - Đầu gật nhẹ trễ pha so với thân (overlap), hàm thở; vây đuôi (Tail5-7) vẫy trễ dần.
 - Đồng hồ cát xoay NGƯỢC chiều kim đồng hồ (nhìn từ trên xuống) 1 vòng/72F (5 độ/frame) quanh trục đứng thế giới + lơ lửng nhẹ."""
import math
N = 72
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/v3/ring.py", encoding="utf8").read(), ns)
CTLS = ns['CTLS']; SPN = ns['SPN']; TL = ns['TL']
HB = 0.028; WV = 1.2; YM = 0.15; RR = 1.2
def Rx(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a); return [[1, 0, 0], [0, c, -s], [0, s, c]]
def Ry(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a); return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def euler_zyx(R):   # R = Rz Ry Rx (kiểu Frolvy / Maya xyz)
    b = -math.asin(max(-1, min(1, R[2][0]))); a = math.atan2(R[2][1], R[2][2]); c = math.atan2(R[1][0], R[0][0])
    return [math.degrees(a), math.degrees(b), math.degrees(c)]
def make_poses(W, cfg=None):
    c = dict(ns['CFG']); c.update(cfg or {})
    base = ns['ring_pose'](W, c)
    phi = c['PHI']
    def pose(f):
        p = 2 * math.pi * f / N; s = math.sin
        m = lambda ph, k=1: s(k * p + ph) - s(ph)          # offset = 0 tại f0
        P = {k: list(v) for k, v in base.items()}
        # lơ lửng
        P["CTL_Root_M"][4] += HB * m(0.0) + 0.006 * m(1.2, 2)
        P["CTL_Root_M"][0] += RR * m(0.9, 2)                  # cả vòng xoay nhẹ trong mặt phẳng, 2 nhịp => số 8
        P["CTL_Root_M"][2] += 1.2 * m(0.3)                    # ngả nhẹ sang bên
        # đảo pha trước/sau (ry): đầu tiến thì đuôi lùi
        ys = 1 + YM * m(0.0); yt = 1 + YM * m(math.pi)
        for k, n in enumerate(SPN, 1): P["CTL_%s_M" % n][1] = c['YAW_SPINE'] * (k / 8.0) ** 2 * ys
        for k, n in enumerate(TL, 1): P["CTL_%s_M" % n][1] = c['YAW_TAIL'] * (k / 7.0) ** 2 * yt
        # sóng độ cong trôi quanh vòng
        for k, n in enumerate(SPN + ["Neck1", "Neck2"]):
            P["CTL_%s_M" % n][0] += WV * (1 - 0.85 * k / 9.0) * (s(2 * math.pi * k / 11.0 - p) - s(2 * math.pi * k / 11.0))
        for k, n in enumerate(TL[:-1]):
            P["CTL_%s_M" % n][0] += -WV * (s(2 * math.pi * (k + 6) / 11.0 - p) - s(2 * math.pi * (k + 6) / 11.0))
        # đầu gật trễ, hàm thở
        P["CTL_Head_M"][0] += 2.5 * m(-1.0)
        P["CTL_Jaw_M"][0] += 1.0 + 1.6 * (s(p - 0.8) + s(0.8))
        P["CTL_Jaw_M"][0] -= 1.0
        # vây đuôi vẫy trễ dần
        for i, n in enumerate(["Tail5", "Tail6", "Tail7"]):
            lag = 0.7 * (i + 1)
            P["CTL_%s_M" % n][0] += (2.0 + 1.5 * i) * m(-lag, 1)
            P["CTL_%s_M" % n][1] += (3.0 + 2.5 * i) * m(-lag - 1.2, 1)
        # đồng hồ cát: xoay ngược chiều kim đồng hồ quanh trục đứng thế giới, bù xoay Root (phi) và dao động nhẹ
        th = 360.0 * f / N
        Cm = mm(Rx(-phi), Ry(th)); P["CTL_Hourglass_M"][0:3] = euler_zyx(Cm)
        P["CTL_Hourglass_M"][4] += 0.010 * m(-1.3)
        return P
    return pose
def unwrap(seq):
    """seq: list of 3-góc; trải góc để liên tục giữa các frame"""
    out = [list(seq[0])]
    for v in seq[1:]:
        u = []
        for i in range(3):
            d = v[i] - out[-1][i]
            while d > 180: d -= 360
            while d < -180: d += 360
            u.append(out[-1][i] + d)
        out.append(u)
    return out
def apply(api, P):
    for c, v in P.items(): api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
def build(api, W, root_ty_fix=0.0, cfg=None):
    pose = make_poses(W, cfg)
    frames = [pose(f) for f in range(N + 1)]
    hg = unwrap([fr["CTL_Hourglass_M"][0:3] for fr in frames])
    for fr, h in zip(frames, hg): fr["CTL_Hourglass_M"][0:3] = h
    for fr in frames: fr["CTL_Root_M"][4] += root_ty_fix
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1): api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, N + 1): api.set_frame(f); apply(api, frames[f]); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
    return frames
