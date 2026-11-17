"""Chrono Ouroboros Attack v2 (RIG v2, base = Idle v7). 40F, BẮN = frame 16 (gắn event). f0 = f40 = đúng tư thế Idle v7 frame 0.
0-9 cuộn người (cổ rút về sau, hạ đầu nhẹ, thân vẫn lơ lửng >= ~9 cm), 9-16 lao đầu tới + há miệng, 16 = bắn (hàm mở tối đa, thân vươn), 16-22 giật lại, 22-40 dao động tắt dần về idle f0.
Sóng trườn idle chạy 1 vòng trong attack. Hourglass xoay ngược chiều kim đồng hồ, nhanh dần tới frame bắn (thêm 520 độ, tốc độ tối đa ~32 độ/frame quanh f16), cuối trở lại nhịp idle (5 độ/frame)."""
import math
NA = 40; FIRE = 16
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/anim/idle4.py", encoding="utf8").read(), ns)
CTLS = ns['CTLS']; TIMES = [0, 9, 16, 22, 30, 40]
def spline(vals, t):
    for i in range(len(TIMES) - 1):
        if TIMES[i] <= t <= TIMES[i + 1]: break
    t0, t1 = TIMES[i], TIMES[i + 1]; u = (t - t0) / (t1 - t0)
    p1, p2 = vals[i], vals[i + 1]
    m1 = 0.0 if i == 0 else (vals[i + 1] - vals[i - 1]) / (TIMES[i + 1] - TIMES[i - 1]) * (t1 - t0)
    m2 = 0.0 if i + 2 >= len(vals) else (vals[i + 2] - vals[i]) / (TIMES[i + 2] - TIMES[i]) * (t1 - t0)
    u2, u3 = u * u, u * u * u
    return (2 * u3 - 3 * u2 + 1) * p1 + (u3 - 2 * u2 + u) * m1 + (-2 * u3 + 3 * u2) * p2 + (u3 - u2) * m2
OFF = {
 "CTL_Root_M": {"rx": [0, 3, -8, -2, 1, 0], "ty": [0, 0.0, 0.06, 0.02, -0.01, 0]},
 "CTL_Spine1_M": {"rx": [0, 4, -5, -2, 0, 0]}, "CTL_Spine2_M": {"rx": [0, 4, -5, -2, 0, 0]},
 "CTL_Spine3_M": {"rx": [0, 6, -6, -2, 1, 0]}, "CTL_Spine4_M": {"rx": [0, 5, -8, -3, 1, 0]},
 "CTL_Neck1_M": {"rx": [0, -28, 48, 8, -2, 0]}, "CTL_Neck2_M": {"rx": [0, -20, 28, 5, -2, 0]}, "CTL_Head_M": {"rx": [0, 8, -32, -6, 2, 0]},
 "CTL_Jaw_M": {"rx": [0, 0, 38, 36, 8, 0]},
 "CTL_Hourglass_M": {"ry": [0, 40, 230, 400, 500, 520]},
}
for i in range(1, 6):
    k = 0.6 + 0.2 * i
    OFF["CTL_Tail%d_M" % i] = {"rx": [0, 8 * k, -10 * k, 14 * k, -6 * k, 0]}
def make_pose(S, hover):
    idle = ns['make_pose'](S, hover)
    def pose(f):
        P = idle(f * ns['N'] / NA)
        P["CTL_Hourglass_M"][1] = 5.0 * f      # nhịp idle (360/72), cộng thêm nhịp tăng tốc ở OFF
        for c, ch in OFF.items():
            for k, vals in ch.items():
                P[c][{"rx": 0, "ry": 1, "rz": 2, "tx": 3, "ty": 4, "tz": 5}[k]] += spline(vals, f)
        return P
    return pose
def build(api, hover):
    S = ns['arc'](api); pose = make_pose(S, hover)
    api.set_frame_range(0, NA); api.set_frame(1)
    for f in range(0, NA + 1): api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, NA + 1): api.set_frame(f); ns['apply'](api, pose(f)); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "constant", "constant")
            except Exception: pass
