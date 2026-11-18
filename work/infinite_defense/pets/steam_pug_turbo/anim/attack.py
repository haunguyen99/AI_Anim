"""Steam-Pug Turbo Attack 30f (ban 2026-11-13: bo giat than/chan/dau, CHI rung lac ong nuoc = Valve + Pipe_L + Pipe_R).
0-11 rung tang dan (gom hoi), 12 = BAN (gắn event), 12-20 rung manh deu, 20-27 tat dan, 30 = dung tu the Idle f0.
Than chay theo Idle (tron ve Idle f0 tu f16 -> f30), ong rung chong len, key moi frame. Can idle_pose trong globals."""
import math
N = 30; FIRE = 12
def _ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def _sm(t): return t * t * (3 - 2 * t)
def pose(f):
    # than van tho/bong benh nhu Idle (khong dung im), tron ve dung Idle f0 tu f16 -> f30 de noi lien clip
    A0 = idle_pose(f); B0 = idle_pose(0); k = 1 - _sm(_ramp(f, 16, 30))
    P = {c: [k * A0[c][i] + (1 - k) * B0[c][i] for i in range(6)] for c in A0}
    # bien do: gom hoi 0.3 -> 0.5 (f3-11), bung len 1.0 tai f12-18, tat dan het o f28
    amp = (0.12 + 0.2 * _ramp(f, 6, 11)) * _sm(_ramp(f, 2, 5)) * (1 - _sm(_ramp(f, 11, 12))) \
        + 1.0 * _sm(_ramp(f, 11.5, 12.5)) * (1 - _sm(_ramp(f, 18, 28)))
    w = 2 * math.pi * f / 2.4; s = math.sin
    # tung ong mot pha / tan so lech nhau, rung quanh goc ong (rx truoc-sau, rz trai-phai)
    P["CTL_Valve_M"][0] += 12 * amp * s(w); P["CTL_Valve_M"][2] += 9 * amp * s(w + 1.3)
    P["CTL_Pipe_L"][0] += 12 * amp * s(w + 0.9); P["CTL_Pipe_L"][2] += 9 * amp * s(w + 2.2)
    P["CTL_Pipe_R"][0] += 12 * amp * s(w + 2.1); P["CTL_Pipe_R"][2] -= 9 * amp * s(w + 0.4)
    # CA NGUOI rung theo khi xi khoi (f12 bung, giu den ~f19, tat dan het o f27 roi hoi ve nhu Idle); gom hoi (f6-11) run nhe
    bamp = 0.2 * (0.18 * _sm(_ramp(f, 5, 8)) * (1 - _sm(_ramp(f, 11, 12))) + 1.0 * _sm(_ramp(f, 11.5, 12.5)) * (1 - _sm(_ramp(f, 19, 27))))
    v = 2 * math.pi * f / 3.0; u = 2 * math.pi * f / 2.2
    P["CTL_Root_M"][3] += 0.008 * bamp * s(v + 0.3); P["CTL_Root_M"][4] += 0.008 * bamp * s(u + 1.1); P["CTL_Root_M"][5] += 0.006 * bamp * s(v + 2.0)
    P["CTL_Root_M"][0] += 1.5 * bamp * s(u); P["CTL_Root_M"][2] += 2.0 * bamp * s(v + 0.9)
    P["CTL_Spine1_M"][0] += 1.0 * bamp * s(u - 0.5); P["CTL_Spine1_M"][2] += 1.2 * bamp * s(v + 0.4)
    P["CTL_Head_M"][0] += 1.5 * bamp * s(u - 1.0); P["CTL_Head_M"][2] += 1.2 * bamp * s(v - 0.6)
    P["CTL_Goggles_M"][0] += 2.0 * bamp * s(u - 1.6)
    for sd in "LR":
        for c, amp_, ph in (("FLeg1", 2.5, 0.8), ("FLeg2", 2.5, 1.4), ("FPaw", 2.0, 2.0), ("BLeg1", 3.0, 1.0), ("BLeg2", 3.0, 1.6), ("BPaw", 2.0, 2.2)):
            P["CTL_%s_%s" % (c, sd)][0] += amp_ * bamp * s(u - ph)
        P["CTL_Tank_" + sd][0] += 2.0 * bamp * s(u - 0.7)
    P["CTL_Tail1_M"][1] += 6 * bamp * s(v - 0.5); P["CTL_Tail2_M"][1] += 8 * bamp * s(v - 1.1)
    return P
def build(api):
    CT = list(idle_pose(0))
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); api.select(CT); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); P = pose(f)
        for c, v in P.items(): api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
        api.select(CT); api.set_key()
    api.set_frame(1); api.set_frame(0)
