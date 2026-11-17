"""Chrono Ouroboros Idle v12 (RIG v3, lơ lửng). Pose gốc = POSE NGƯỜI DÙNG ĐÃ SỬA (idle_v12_pose_user.fv, frame 0) đọc thẳng từ file; mọi chuyển động là offset triệt tiêu ở f0, nên f0 giữ nguyên pose đã duyệt.
72F lặp liền (f72 == f0), 30 fps. Thành phần (chu kỳ nguyên 1 hoặc 2 lần/vòng):
 - Lơ lửng: Root nhô lên 2*HB m rồi hạ về pose gốc (1 nhịp) + gợn nhỏ 2 nhịp; f0 là điểm thấp nhất nên không chạm đất.
 - SỐ 8: đầu và đuôi đảo pha trước/sau (ry thân và đuôi, 1 nhịp), đầu lên/xuống 2 nhịp (độ cong cuối thân) => đầu vẽ số 8.
 - Thân trôi quanh vòng: sóng độ cong chạy dọc thân + đuôi (±WV độ mỗi khớp, nhỏ dần về phía đầu để đầu không chạm đồng hồ cát).
 - Đầu gật nhẹ trễ pha, hàm thở, vây đuôi (Tail5-7) vẫy trễ dần.
 - (SPIN=False: đồng hồ cát KHÔNG quay, nhấp nhô riêng như đang bay: lên/xuống tối đa ~4 cm so với vòng + lắc ±2,5°, trễ pha so với vòng) Nếu SPIN=True: đồng hồ cát xoay NGƯỢC chiều kim đồng hồ (nhìn từ trên xuống) 1 vòng/72F quanh trục đứng thế giới, lơ lửng nhẹ so với vòng.
Root không xoay thêm (pose người dùng để Root gần gimbal lock: Euler (15, -88, -180))."""
import math
N = 72
CH6 = ("rx", "ry", "rz", "tx", "ty", "tz")
SPN = ["Spine%d" % k for k in range(1, 9)]; TL = ["Tail%d" % k for k in range(1, 8)]
CTLS = ["CTL_%s_M" % n for n in ["Root"] + SPN + ["Neck1", "Neck2", "Head", "Jaw"] + TL + ["Hourglass"]]
SPIN = False   # người dùng 2026-11-17: KHÔNG cho đồng hồ cát quay; đồng hồ cát đứng yên ở pose gốc
HGB = 0.022; HGS = 2.5   # đồng hồ cát nhấp nhô riêng (m) + lắc ngang trong mặt phẳng vòng (độ), trễ pha so với vòng
HB = 0.025; WV = 1.2; YM = 0.15; YS = 14.0; YT = 20.0
def Rx(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a); return [[1, 0, 0], [0, c, -s], [0, s, c]]
def Ry(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a); return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
def Rz(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a); return [[c, -s, 0], [s, c, 0], [0, 0, 1]]
def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def tr(A): return [list(r) for r in zip(*A)]
def mv(A, v): return [sum(A[i][k] * v[k] for k in range(3)) for i in range(3)]
def from_euler(e): return mm(Rz(e[2]), mm(Ry(e[1]), Rx(e[0])))        # Frolvy / Maya xyz: R = Rz Ry Rx
def to_euler(R):
    b = -math.asin(max(-1, min(1, R[2][0]))); a = math.atan2(R[2][1], R[2][2]); c = math.atan2(R[1][0], R[0][0])
    return [math.degrees(a), math.degrees(b), math.degrees(c)]
def read_base(api):
    api.set_frame(0)
    return {c: [api.get_attr("%s.%s" % (c, a)) for a in CH6] for c in CTLS}
def make_poses(base):
    R0 = from_euler(base["CTL_Root_M"][0:3]); B0 = from_euler(base["CTL_Hourglass_M"][0:3])
    W0 = mm(R0, B0)                                   # hướng thế giới của đồng hồ cát ở pose gốc
    def pose(f):
        p = 2 * math.pi * f / N; s = math.sin
        m = lambda ph, k=1: s(k * p + ph) - s(ph)          # offset = 0 tại f0
        P = {k: list(v) for k, v in base.items()}
        P["CTL_Root_M"][4] += HB * (1 - math.cos(p)) + 0.006 * m(1.2, 2)      # nhô lên rồi hạ về đúng pose gốc: không bao giờ thấp hơn pose đã duyệt
        ys = YM * m(0.0); yt = YM * m(math.pi)
        for k, n in enumerate(SPN, 1): P["CTL_%s_M" % n][1] += YS * (k / 8.0) ** 2 * ys
        for k, n in enumerate(TL, 1): P["CTL_%s_M" % n][1] += YT * (k / 7.0) ** 2 * yt
        for k, n in enumerate(SPN + ["Neck1", "Neck2"]):      # sóng độ cong trôi quanh vòng, nhỏ dần về đầu
            P["CTL_%s_M" % n][0] += WV * (1 - 0.85 * k / 9.0) * (s(2 * math.pi * k / 11.0 - p) - s(2 * math.pi * k / 11.0))
        for k, n in enumerate(TL[:-1]):
            P["CTL_%s_M" % n][0] += -WV * (s(2 * math.pi * (k + 6) / 11.0 - p) - s(2 * math.pi * (k + 6) / 11.0))
        for n in ("Spine7", "Spine8", "Neck1"): P["CTL_%s_M" % n][0] += 0.9 * m(0.5, 2)   # đầu lên/xuống 2 nhịp => số 8
        P["CTL_Head_M"][0] += 2.5 * m(-1.0)
        P["CTL_Jaw_M"][0] += 1.6 * m(-0.8)
        for i, n in enumerate(["Tail5", "Tail6", "Tail7"]):
            lag = 0.7 * (i + 1)
            P["CTL_%s_M" % n][0] += (2.0 + 1.5 * i) * m(-lag, 1)
            P["CTL_%s_M" % n][1] += (3.0 + 2.5 * i) * m(-lag - 1.2, 1)
        if SPIN:
            th = 360.0 * f / N                                  # ngược chiều kim đồng hồ nhìn từ trên: +Y
            Cm = mm(tr(R0), mm(Ry(th), W0))                     # Root * C = Ry(th) * W0
            P["CTL_Hourglass_M"][0:3] = to_euler(Cm)
            dl = mv(tr(R0), [0, 0.010 * m(-1.3), 0])            # dao động dọc theo trục đứng thế giới, đổi sang trục cục bộ Root
            for i in range(3): P["CTL_Hourglass_M"][3 + i] += dl[i]
        if not SPIN:                                        # đồng hồ cát không quay nhưng nhấp nhô như đang bay: lên xuống riêng + lắc nhẹ, trễ pha so với vòng
            up = HGB * m(-1.3) + 0.008 * m(0.4, 2)
            dl = mv(tr(R0), [0, up, 0])
            for i in range(3): P["CTL_Hourglass_M"][3 + i] += dl[i]
            Cm = mm(tr(R0), mm(Rz(HGS * m(-0.5)), W0))      # lắc quanh trục nhìn (Z thế giới), không xoay quanh trục đứng
            P["CTL_Hourglass_M"][0:3] = to_euler(Cm)
        return P
    return pose
def unwrap(seq):
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
def build(api, base, root_ty_fix=0.0):
    pose = make_poses(base)
    frames = [pose(f) for f in range(N + 1)]
    h = unwrap([fr["CTL_Hourglass_M"][0:3] for fr in frames])
    for fr, e in zip(frames, h): fr["CTL_Hourglass_M"][0:3] = e
    for fr in frames: fr["CTL_Root_M"][4] += root_ty_fix
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1): api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, N + 1): api.set_frame(f); apply(api, frames[f]); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in CH6:
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
    return frames
