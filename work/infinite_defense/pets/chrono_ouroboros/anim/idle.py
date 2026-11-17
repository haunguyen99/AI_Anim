"""Chrono Ouroboros Idle 90f loop (f0==f90). Hover 12 cm, song bò uốn: sóng ngang 1 vòng/loop chạy từ đầu về đuôi + sóng dọc 2 vòng/loop => đầu vẽ số 8 (vô cực).
Chân buông lơ lửng, trễ theo thân. (Bánh răng: mesh không có -> chưa làm.)"""
import math
N = 90
SP = ["Spine1", "Spine2", "Spine3", "Spine4"]; NK = ["Neck1", "Neck2", "Head"]; TL = ["Tail1", "Tail2", "Tail3", "Tail4", "Tail5"]
LEG = ["%s%s_%s" % (a, b, s) for a in ("Fore", "Hind") for b in ("Leg1", "Leg2", "Foot") for s in "LR"]
CTLS = ["CTL_%s_M" % n for n in ["Root"] + SP + NK + ["Jaw"] + TL] + ["CTL_" + l for l in LEG]
HOVER = 0.12
# khoảng cách tới đầu (độ trễ pha): đầu dẫn, thân/đuôi theo
DELAY = {"Head": 0.0, "Neck2": 0.25, "Neck1": 0.5, "Spine4": 0.8, "Spine3": 1.1, "Spine2": 1.4, "Spine1": 1.7, "Root": 2.0,
         "Tail1": 2.35, "Tail2": 2.7, "Tail3": 3.05, "Tail4": 3.4, "Tail5": 3.75}
YAW = {"Head": 14, "Neck2": 10, "Neck1": 8, "Spine4": 7, "Spine3": 7, "Spine2": 7, "Spine1": 7, "Tail1": 9, "Tail2": 12, "Tail3": 15, "Tail4": 18, "Tail5": 21}
PIT = {"Head": 8, "Neck2": 7, "Neck1": 6, "Spine4": 4, "Spine3": 4, "Spine2": 4, "Spine1": 4, "Tail1": 5, "Tail2": 7, "Tail3": 9, "Tail4": 11, "Tail5": 13}
def pose(f):
    p = 2 * math.pi * f / N; s = math.sin
    P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}          # rx ry rz tx ty tz
    P["CTL_Root_M"][4] = HOVER + 0.02 * s(2 * p - 0.4)
    P["CTL_Root_M"][3] = 0.025 * s(p - 1.0)
    P["CTL_Root_M"][:3] = [-1.0 * s(2 * p - 0.9), 2.0 * s(p - 0.7), 2.0 * s(p - 0.3)]
    for n in SP + NK + TL:
        d = DELAY[n]
        ry = YAW[n] * s(p - d)                          # sóng ngang (ngược chiều số 8: ry dương = quay trái)
        rx = -PIT[n] * s(2 * p - 2 * d + 0.5)           # sóng dọc gấp đôi tần số, X âm = ngóc lên
        rz = 1.5 * s(p - d - 0.8) if n in ("Head", "Neck2", "Neck1") else 0.0
        P["CTL_%s_M" % n][:3] = [rx, ry, rz]
    P["CTL_Jaw_M"][0] = 2.0 + 1.5 * s(2 * p - 1.2)
    # chân buông lơ lửng: đung đưa trước/sau trễ theo thân, hai bên lệch pha
    for l in LEG:
        side = l[-1]; k = 1 if side == "L" else -1; part = l[:-2]
        fore = l.startswith("Fore"); base = 0.4 if fore else 2.0
        lag = {"Leg1": 0.0, "Leg2": 0.5, "Foot": 1.0}[part[4:] if part.startswith(("Fore", "Hind")) and part[4:] in ("Leg1", "Leg2", "Foot") else "Leg1"]
        amp = {"Leg1": 5, "Leg2": 7, "Foot": 9}[part[4:]]
        ph = p - base - lag + (0.6 if side == "R" else 0.0)
        P["CTL_" + l][0] = amp * s(2 * p - 2 * base - 2 * lag + (0.8 if side == "R" else 0.0)) + (4 if part[4:] != "Leg1" else 0)   # chân hơi co về sau khi buông
        P["CTL_" + l][2] = k * 0.6 * amp * s(ph)
    return P

def apply(api, P):
    for c, v in P.items():
        api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])

def build(api):
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); apply(api, pose(f)); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
