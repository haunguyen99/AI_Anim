"""Chrono Ouroboros Attack v3 (RIG v3, vòng ouroboros). 40F, BẮN = frame 16 (gắn event). f0 = f40 = Idle v14 frame 0 = pose người dùng đã sửa.
0-9 rụt đầu/cổ về sau (ngửa ra), hạ vòng nhẹ; 9-16 đầu lao tới (cổ cuộn thêm) + há miệng; 16 = BẮN (hàm mở tối đa ~36 độ, vòng nảy lên); 16-22 giật lại;
22-40 dao động tắt dần về idle f0. Chuyển động idle (trôi, số 8, vây) chạy 1 vòng trong 40F ở biên độ 55% để f40 = f0. Đồng hồ cát không quay: nảy lên + lắc khi bắn (lóe sáng là VFX)."""
import math
NA = 40; FIRE = 16
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/anim/idle6.py", encoding="utf8").read(), ns)
CTLS = ns['CTLS']; TIMES = [0, 9, 16, 22, 30, 40]; IDLE_AMT = 0.55
def spline(vals, t):
    for i in range(len(TIMES) - 1):
        if TIMES[i] <= t <= TIMES[i + 1]: break
    t0, t1 = TIMES[i], TIMES[i + 1]; u = (t - t0) / (t1 - t0)
    p1, p2 = vals[i], vals[i + 1]
    m1 = 0.0 if i == 0 else (vals[i + 1] - vals[i - 1]) / (TIMES[i + 1] - TIMES[i - 1]) * (t1 - t0)
    m2 = 0.0 if i + 2 >= len(vals) else (vals[i + 2] - vals[i]) / (TIMES[i + 2] - TIMES[i]) * (t1 - t0)
    u2, u3 = u * u, u * u * u
    return (2 * u3 - 3 * u2 + 1) * p1 + (u3 - 2 * u2 + u) * m1 + (-2 * u3 + 3 * u2) * p2 + (u3 - u2) * m2
IX = {"rx": 0, "ry": 1, "rz": 2, "tx": 3, "ty": 4, "tz": 5}
# offset theo TIMES [0, 9, 16, 22, 30, 40]; rx dương = cuộn thêm về phía bụng (vào trong vòng), âm = duỗi/ngửa ra
OFF = {
 "CTL_Root_M": {"ty": [0, -0.03, 0.04, 0.015, -0.005, 0]},
 "CTL_Spine7_M": {"rx": [0, -3, 1, 0.5, -0.3, 0]}, "CTL_Spine8_M": {"rx": [0, -4, 1, 0.5, -0.3, 0]},
 "CTL_Neck1_M": {"rx": [0, -10, 3, 2, -1, 0]}, "CTL_Neck2_M": {"rx": [0, -8, 3, 2, -1, 0]}, "CTL_Head_M": {"rx": [0, -10, 2, 2, -1, 0]},
}
# lao ra khỏi mặt phẳng vòng (hướng camera): ry dương = đầu ra trước. Rụt về sau ở f9, lao tới ở f16
for k, n in enumerate(["Spine5", "Spine6", "Spine7", "Spine8"], 1):
    OFF["CTL_%s_M" % n] = dict(OFF.get("CTL_%s_M" % n, {}), ry=[0, -1.5 * k / 2, 2.5 * k / 2, 1 * k / 2, -0.5 * k / 2, 0])
for n, a_ in (("Neck1", 1.0), ("Neck2", 1.0), ("Head", 0.8)):
    OFF["CTL_%s_M" % n] = dict(OFF["CTL_%s_M" % n], ry=[0, -8 * a_, 14 * a_, 5 * a_, -2 * a_, 0])
for i, n in enumerate(["Tail3", "Tail4", "Tail5", "Tail6", "Tail7"], 1):
    k = 0.5 + 0.25 * i
    OFF["CTL_%s_M" % n] = {"rx": [0, 3 * k, -4 * k, 5 * k, -2 * k, 0], "ry": [0, 4 * k, -6 * k, 5 * k, -2 * k, 0]}
def jaw(f):
    """hàm: đóng tới f9, mở ra nhanh (ease-out) tới ĐỈNH ĐÚNG f16 = BẮN, khép lại ease-in-out tới f22 (còn 10 độ), thở ra tắt dần hết f32"""
    if f <= 9: return 0.0
    if f <= 16: return 37.0 * math.sin(math.pi / 2 * (f - 9) / 7)
    if f <= 22: u = (f - 16) / 6.0; return 10 + 27 * (1 + math.cos(math.pi * u)) / 2
    if f <= 32: u = (f - 22) / 10.0; return 10 * (1 + math.cos(math.pi * u)) / 2
    return 0.0
HG_UP = [0, -0.01, 0.03, 0.015, 0.003, 0]; HG_TILT = [0, 0, 4, -3, 1, 0]     # m (trục đứng thế giới), độ (lắc quanh trục nhìn)
def make_pose(base):
    idle = ns['make_poses'](base)
    R0 = ns['from_euler'](base["CTL_Root_M"][0:3]); B0 = ns['from_euler'](base["CTL_Hourglass_M"][0:3]); W0 = ns['mm'](R0, B0)
    def pose(f):
        I = idle(f * ns['N'] / NA)
        P = {c: [base[c][i] + IDLE_AMT * (I[c][i] - base[c][i]) for i in range(6)] for c in base}
        P["CTL_Jaw_M"][0] = base["CTL_Jaw_M"][0] + jaw(f)
        for c, ch in OFF.items():
            for k, vals in ch.items(): P[c][IX[k]] += spline(vals, f)
        # đồng hồ cát: dao động idle (đã nhân IDLE_AMT) + nảy lên + lắc khi bắn, tính lại từ hướng thế giới
        p = 2 * math.pi * (f * ns['N'] / NA) / ns['N']; s = math.sin; m = lambda ph, k=1: s(k * p + ph) - s(ph)
        up = IDLE_AMT * (ns['HGB'] * m(-1.3) + 0.008 * m(0.4, 2)) + spline(HG_UP, f)
        tilt = IDLE_AMT * ns['HGS'] * m(-0.5) + spline(HG_TILT, f)
        Cm = ns['mm'](ns['tr'](R0), ns['mm'](ns['Rz'](tilt), W0)); P["CTL_Hourglass_M"][0:3] = ns['to_euler'](Cm)
        dl = ns['mv'](ns['tr'](R0), [0, up, 0])
        for i in range(3): P["CTL_Hourglass_M"][3 + i] = base["CTL_Hourglass_M"][3 + i] + dl[i]
        return P
    return pose
def build(api, base):
    pose = make_pose(base); frames = [pose(f) for f in range(NA + 1)]
    api.set_frame_range(0, NA); api.set_frame(1)
    for f in range(0, NA + 1): api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, NA + 1): api.set_frame(f); ns['apply'](api, frames[f]); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in ns['CH6']:
            try: api.set_infinity(c + "." + a, "constant", "constant")
            except Exception: pass
    return frames
