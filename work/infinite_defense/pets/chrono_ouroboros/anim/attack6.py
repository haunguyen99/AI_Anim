"""Chrono Ouroboros Attack v6 (RIG v3) = v4 (người dùng chọn lại v4, bỏ v5) + ĐOẠN VỀ f32 -> f40 MỀM HƠN: v4 vọt 368 độ ở f36 rồi giật về 360 trong 4 frame; v6 kéo dài đợt quay tới f40, giảm tốc liên tục (ease-in-out 6 -> 40) và chỉ vọt nhẹ 4 độ (đỉnh ~f33) rồi trôi về 360 với vận tốc 0 ở f40.
Mô tả v4:
Chrono Ouroboros Attack v4 (RIG v3). Người dùng 2026-11-17: 'attack chỉ làm rồng quay 1 vòng quanh đồng hồ, đồng hồ vẫn bay lơ lửng như idle'.
40F. Cả vòng rồng QUAY 1 VÒNG (360 độ) trong mặt phẳng vòng quanh TÂM VÒNG (đầu đi theo hướng mõm chỉ): rụt nhẹ ngược chiều (-18 độ, f6) rồi quay nhanh dần, nhanh nhất giữa clip,
vọt nhẹ 368 độ (f36) rồi về đúng 360 = pose idle f0 (f40 = f0). BẮN = frame 20 (lúc quay nhanh nhất): hàm mở 22 độ để gắn event (nếu không cần há miệng thì đặt JAW_OPEN = 0).
Đồng hồ cát giữ NGUYÊN chỗ trong không gian (không bị vòng kéo quay theo), vẫn nhấp nhô lơ lửng + lắc nhẹ như idle, không xoay. Thân/đuôi giữ chuyển động idle 55% (trôi, vây vẫy trễ) cho vòng quay mềm.
Root quay quanh trục pháp tuyến vòng (rx cục bộ) nên chỉ cộng góc vào rx; Root tịnh tiến để tâm vòng đứng yên."""
import math
OVER = 4.0
NA = 40; FIRE = 20; JAW_OPEN = 22.0; IDLE_AMT = 0.55; RING_AMT = 0.6
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/anim/idle6.py", encoding="utf8").read(), ns)
CTLS = ns['CTLS']; CH6 = ns['CH6']
ease = lambda u: (1 - math.cos(math.pi * u)) / 2
def theta(f):
    if f <= 6: return -18.0 * ease(f / 6.0)
    th = -18.0 + 378.0 * ease((f - 6) / 34.0)                           # ease-in-out kéo dài tới f40, vận tốc 0 ở f40
    if 26 <= f <= 40: th += OVER * math.sin(math.pi * (f - 26) / 14.0) ** 2   # vọt nhẹ (đỉnh ~f33) rồi trôi về 360, đầu/cuối vận tốc 0
    return th
def jaw(f):
    if f <= FIRE - 8: return 0.0
    if f <= FIRE: return JAW_OPEN * math.sin(math.pi / 2 * (f - (FIRE - 8)) / 8.0)
    if f <= FIRE + 8: return JAW_OPEN * (1 + math.cos(math.pi * (f - FIRE) / 8.0)) / 2
    return 0.0
LMAX = 0.22   # khi quay, đầu/đuôi (có gai) đi xuống đáy vòng nên cả vòng bay cao thêm LMAX m (mượt, đỉnh giữa clip) để gai không chạm đất; về 0 ở f40
LIFT = [(LMAX * math.sin(math.pi * (f - 4) / 32.0) ** 2 if 4 <= f <= 36 else 0.0) + 0.05 * math.exp(-((f - 22) / 2.0) ** 2) for f in range(41)]   # + nảy nhẹ ở f22: gai đầu/đuôi quét qua đáy lúc quay nhanh (v6 lệch nhịp so với v4)
J0 = [0.0, 0.3, -0.5]; REST = [0.0, 0.0, 0.5]; RCEN = 0.54      # khớp Root lúc bind, vị trí khớp Hourglass so với Root, bán kính vòng (v3/ring.py)
def make_pose(base):
    idle = ns['make_poses'](base)
    Rb = ns['from_euler'](base["CTL_Root_M"][0:3]); tb = base["CTL_Root_M"][3:6]
    B0 = ns['from_euler'](base["CTL_Hourglass_M"][0:3]); W0 = ns['mm'](Rb, B0)
    chord = 0.5 * (0.1775 + 0.17); s_off = RCEN - math.sqrt(RCEN ** 2 - chord ** 2)
    cl = [0.0, -(RCEN - s_off), 0.0]                                   # tâm vòng trong khung cục bộ của Root
    add = lambda a, b: [a[i] + b[i] for i in range(3)]; sub = lambda a, b: [a[i] - b[i] for i in range(3)]
    mvv = ns['mv']
    C0 = add(add(J0, tb), mvv(Rb, cl))                                 # tâm vòng trong thế giới (đứng yên)
    hgt = base["CTL_Hourglass_M"][3:6]
    Phg0 = add(add(J0, tb), mvv(Rb, add(REST, hgt)))                   # vị trí thế giới của đồng hồ cát ở pose gốc
    def pose(f):
        f = float(f)
        I = idle(f * ns['N'] / NA)
        P = {c: [base[c][i] + IDLE_AMT * (I[c][i] - base[c][i]) for i in range(6)] for c in base}
        p = 2 * math.pi * f / NA; s = math.sin; m = lambda ph, k=1: s(k * p + ph) - s(ph)
        P["CTL_Jaw_M"][0] = base["CTL_Jaw_M"][0] + jaw(f)
        th = theta(f)
        e = list(base["CTL_Root_M"][0:3]); e[0] += th                  # quay quanh trục pháp tuyến vòng (rx cục bộ)
        R = ns['from_euler'](e)
        bob = RING_AMT * (ns['HB'] * (1 - math.cos(p)) + 0.006 * m(1.2, 2)) + LIFT[int(round(f))] if f == int(f) else 0.0
        Rootpos = add(C0, [0, bob, 0]); Rootpos = sub(Rootpos, mvv(R, cl))
        P["CTL_Root_M"][0:3] = e; P["CTL_Root_M"][3:6] = sub(Rootpos, J0)
        own = ns['HGB'] * m(-1.3) + 0.008 * m(0.4, 2); tilt = ns['HGS'] * m(-0.5)
        Phg = add(Phg0, [0, bob + own, 0])
        Wf = ns['mm'](ns['Rz'](tilt), W0)
        P["CTL_Hourglass_M"][0:3] = ns['to_euler'](ns['mm'](ns['tr'](R), Wf))
        P["CTL_Hourglass_M"][3:6] = sub(mvv(ns['tr'](R), sub(Phg, Rootpos)), REST)
        return P
    return pose
def build(api, base):
    pose = make_pose(base); frames = [pose(f) for f in range(NA + 1)]
    for c in ("CTL_Root_M", "CTL_Hourglass_M"):
        u = ns['unwrap']([fr[c][0:3] for fr in frames])
        for fr, e in zip(frames, u): fr[c][0:3] = e
    api.set_frame_range(0, NA); api.set_frame(1)
    for f in range(0, NA + 1): api.set_frame(f); api.select(CTLS); api.set_key()
    for f in range(0, NA + 1): api.set_frame(f); ns['apply'](api, frames[f]); api.select(CTLS); api.set_key()
    api.set_frame(1); api.set_frame(0)
    for c in CTLS:
        for a in CH6:
            try: api.set_infinity(c + "." + a, "constant", "constant")
            except Exception: pass
    return frames
