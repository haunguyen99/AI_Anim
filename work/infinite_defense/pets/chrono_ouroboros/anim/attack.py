"""Chrono Ouroboros Attack v1 (base = Idle v4). 40f, BẮN = frame 16 (gắn event). f0 và f40 = đúng tư thế Idle frame 0.
0-9 cuộn người (cổ rút về sau, hạ thân), 9-16 lao đầu tới + há miệng, 16 = bắn (hàm mở tối đa, thân vươn), 16-22 giật lại, 22-40 dao động tắt dần về idle f0.
Sóng trườn của idle vẫn chạy (1 vòng/attack) nên kết thúc đúng idle f0. (Bánh răng: mesh không có -> chưa làm.)"""
import math
NA = 40; FIRE = 16
ns = {}; exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\chrono_ouroboros\anim\idle2.py", encoding="utf8").read(), ns)
CTLS = ns['CTLS']; TIMES = [0, 9, 16, 22, 30, 40]
def spline(vals, t):
    """Catmull-Rom qua các key (tiếp tuyến 0 ở hai đầu)"""
    for i in range(len(TIMES) - 1):
        if TIMES[i] <= t <= TIMES[i + 1]: break
    t0, t1 = TIMES[i], TIMES[i + 1]; u = (t - t0) / (t1 - t0)
    p1, p2 = vals[i], vals[i + 1]
    m1 = 0.0 if i == 0 else (vals[i + 1] - vals[i - 1]) / (TIMES[i + 1] - TIMES[i - 1]) * (t1 - t0)
    m2 = 0.0 if i + 2 >= len(vals) else (vals[i + 2] - vals[i]) / (TIMES[i + 2] - TIMES[i]) * (t1 - t0)
    u2, u3 = u * u, u * u * u
    return (2 * u3 - 3 * u2 + 1) * p1 + (u3 - 2 * u2 + u) * m1 + (-2 * u3 + 3 * u2) * p2 + (u3 - u2) * m2
# offset keys theo TIMES: control -> {kênh: [6 giá trị]}  (rx độ, ty mét). rx dương = chúi/đưa về trước, âm = ngả/ngóc
OFF = {
 "CTL_Root_M": {"rx": [0, 6, -8, -2, 1, 0], "ty": [0, -0.07, 0.06, 0.02, -0.01, 0]},
 "CTL_Spine1_M": {"rx": [0, 4, -5, -2, 0, 0]}, "CTL_Spine2_M": {"rx": [0, 4, -5, -2, 0, 0]},
 "CTL_Spine3_M": {"rx": [0, 6, -6, -2, 1, 0]}, "CTL_Spine4_M": {"rx": [0, 8, -8, -3, 1, 0]},
 "CTL_Neck1_M": {"rx": [0, -28, 48, 8, -2, 0]}, "CTL_Neck2_M": {"rx": [0, -20, 28, 5, -2, 0]}, "CTL_Head_M": {"rx": [0, 30, -32, -6, 2, 0]},
 "CTL_Jaw_M": {"rx": [0, 0, 38, 36, 8, 0]},
}
for i in range(1, 6):
    k = 0.6 + 0.2 * i
    OFF["CTL_Tail%d_M" % i] = {"rx": [0, 8 * k, -10 * k, 14 * k, -6 * k, 0]}
for l in ns['LEG']:
    sgn = 1.0 if l.startswith("Fore") else 0.7
    OFF["CTL_" + l] = {"rx": [0, -8 * sgn, 12 * sgn, 4 * sgn, -2 * sgn, 0]}
def make_pose(S, W):
    idle = ns['make_pose'](S, W)
    def pose(f):
        P = idle(f * ns['N'] / NA)                 # sóng idle chạy 1 vòng trong attack -> f40 = idle f0
        for c, ch in OFF.items():
            for k, vals in ch.items():
                v = spline(vals, f); idx = {"rx": 0, "ry": 1, "rz": 2, "tx": 3, "ty": 4, "tz": 5}[k]
                P[c][idx] += v
        return P
    return pose
def build(api):
    S, W = ns['arc'](api); pose = make_pose(S, W)
    api.set_frame_range(0, NA)
    for c in CTLS:                                   # chỉ bỏ key quá NA (không làm rỗng curve)
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            for k in list(api.list_keys(c + "." + a)):
                if k > NA: api.delete_key(c + "." + a, int(round(k)))
    for f in range(0, NA + 1):
        api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, NA + 1):
        api.set_frame(f); ns['apply'](api, pose(f)); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
