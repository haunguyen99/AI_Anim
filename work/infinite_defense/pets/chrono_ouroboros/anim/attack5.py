"""Chrono Ouroboros Attack v5 (RIG v3) = v4 + SỨC SỐNG khi quay (người dùng 2026-11-17: "quay đơ quá, không có anim").
40F, rồng quay 1 vòng quanh đồng hồ (đồng hồ bay lơ lửng như idle), f0 = f40 = idle f0 = pose người dùng, BẮN = frame 20.
Thêm vào v4 (mọi lớp nhân với env(f): 0 ở f0 và f40, mạnh nhất lúc quay nhanh):
 - Tốc độ quay giật theo đợt (2 lần dồn lực - xả), không đều.
 - Thân luồn lượn vào/ra khỏi mặt phẳng vòng (ry là hiệu của sóng tuyệt đối, sóng cố định trong không gian nên thân trượt qua các khúc lượn: không còn là bánh xe cứng).
 - Gợn độ cong (rx) cố định trong không gian, nhỏ.
 - Vòng co lại một chút lúc dồn lực (f4-8) rồi nở ra lúc quay nhanh (±3% độ cong).
 - (HYAW = 0: bỏ lắc yaw cả vòng vì Root của pose người dùng sát gimbal lock, Euler (15, -88, -180), yaw làm Euler lật nhánh)
 - Đầu chúi theo hướng quay, hàm há theo đợt, đuôi/vây trễ pha.
Đồng hồ cát không quay, không bị vòng kéo theo; nhấp nhô + lắc nhẹ như idle."""
import math
NA = 40; FIRE = 20; JAW_OPEN = 22.0; IDLE_AMT = 0.55; RING_AMT = 0.6
ns = {}; exec(open("/home/ngocvb/Desktop/DataHDD/AI_animation/work/infinite_defense/pets/chrono_ouroboros/anim/idle6.py", encoding="utf8").read(), ns)
CTLS = ns['CTLS']; CH6 = ns['CH6']
ease = lambda u: (1 - math.cos(math.pi * u)) / 2
def theta(f):
    if f <= 6: return -18.0 * ease(f / 6.0)
    if f <= 36:
        u = (f - 6) / 30.0
        return -18.0 + 386.0 * ease(u) + SURGE * math.sin(4 * math.pi * u) * math.sin(math.pi * u) ** 2
    return 368.0 - 8.0 * ease((f - 36) / 4.0)
def jaw(f):
    if f <= FIRE - 8: return 0.0
    if f <= FIRE: return JAW_OPEN * math.sin(math.pi / 2 * (f - (FIRE - 8)) / 8.0)
    if f <= FIRE + 8: return JAW_OPEN * (1 + math.cos(math.pi * (f - FIRE) / 8.0)) / 2
    return 0.0
WEAVE = 10.0; RIPPLE = 1.0; SQ_IN = 0.02; SQ_OUT = 0.07;   # độ cong x(1 + SQ_IN) lúc dồn lực (vòng co), x(1 - SQ_OUT) lúc quay nhanh (vòng nở ra ~7% để lỗ vòng rộng hơn đồng hồ cát: lỗ chỉ hơn đồng hồ cát ~2 cm)
HYAW = 0.0; SURGE = 14.0; LEAD = 0.18
LMAX = 0.30   # khi quay, đầu/đuôi (có gai) đi xuống đáy vòng nên cả vòng bay cao thêm LMAX m (mượt, đỉnh giữa clip) để gai không chạm đất; về 0 ở f40
LIFT = [(LMAX * math.sin(math.pi * (f - 4) / 32.0) ** 2 if 4 <= f <= 36 else 0.0) + 0.07 * math.exp(-((f - 20) / 2.2) ** 2) for f in range(41)]   # + nảy thêm ở f20 (gai đầu/đuôi quét qua đáy lúc quay nhanh nhất, cũng là frame BẮN)
SARC = {}
for k in range(1, 9): SARC["Spine%d" % k] = 0.1775 * k
SARC.update({"Neck1": 1.55, "Neck2": 1.67, "Head": 1.78})
for k in range(1, 8): SARC["Tail%d" % k] = -0.1708 * k
env = lambda f: (math.sin(math.pi * min(max((f - 3.0) / 32.0, 0.0), 1.0)) ** 2)
J0 = [0.0, 0.3, -0.5]; REST = [0.0, 0.0, 0.5]; RCEN = 0.54      # khớp Root lúc bind, vị trí khớp Hourglass so với Root, bán kính vòng (v3/ring.py)
def make_pose(base):
    idle = ns['make_poses'](base)
    Rb = ns['from_euler'](base["CTL_Root_M"][0:3]); tb = base["CTL_Root_M"][3:6]
    B0 = ns['from_euler'](base["CTL_Hourglass_M"][0:3]); W0 = ns['mm'](Rb, B0)
    chord = 0.5 * (0.1775 + 0.17); s_off = RCEN - math.sqrt(RCEN ** 2 - chord ** 2)
    cl = [0.013, -0.464, 0.044]                                        # tâm vòng trong khung Root: ĐO bằng fit đường tròn lên mesh pose người dùng (công thức lý tưởng cho [0, -0,511, 0] lệch 5 cm làm vòng lắc lư khi quay)
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
        th = theta(f); ef = env(f)
        v = theta(f + 0.5) - theta(f - 0.5)                            # tốc độ quay (độ/frame)
        # --- sức sống ---
        sqz = SQ_IN * (math.sin(math.pi * (f - 2) / 8.0) ** 2 if 2 <= f <= 10 else 0.0) - SQ_OUT * (math.sin(math.pi * (f - 12) / 22.0) ** 2 if 12 <= f <= 34 else 0.0)
        CHAINS = (["Spine%d" % k for k in range(1, 9)] + ["Neck1", "Neck2"], ["Tail%d" % k for k in range(1, 7)])
        for chain in CHAINS:
            prev = 0.0
            for n in chain:
                c = "CTL_%s_M" % n
                P[c][0] *= (1 + sqz)                                         # co lại dồn lực / nở ra khi quay nhanh
                al = SARC[n] / RCEN + math.radians(th)                                 # vị trí góc của khớp trên vòng (quay theo vòng)
                P[c][0] += ef * RIPPLE * math.sin(3 * al + 0.5)                       # gợn độ cong cố định trong không gian
                a_abs = ef * WEAVE * math.sin(2 * al + 1.0)                           # độ nghiêng tuyệt đối ra khỏi mặt phẳng
                P[c][1] += a_abs - prev; prev = a_abs                                 # ry = hiệu => thân luồn lượn vào/ra
        for n, k in (("Head", 1.0), ("Neck2", 0.6), ("Neck1", 0.4)): P["CTL_%s_M" % n][0] += LEAD * k * v      # đầu chúi theo hướng quay
        for j in range(3, 8):
            nm = "CTL_Tail%d_M" % j
            if j < 7: P[nm][0] += -0.07 * v * (j / 7.0)                                # đuôi/vây trễ phía sau
            else: P["CTL_Tail7_M"][0] += -0.10 * v
        p = 2 * math.pi * f / NA; s = math.sin; m = lambda ph, k=1: s(k * p + ph) - s(ph)
        e = list(base["CTL_Root_M"][0:3]); e[0] += th                  # quay quanh trục pháp tuyến vòng (rx cục bộ)
        R = ns['from_euler'](e)
        dyaw = HYAW * ef * math.sin(2 * math.pi * (f - 4) / 16.0 + 0.3) # cả vòng lắc nghiêng quanh trục đứng thế giới
        R = ns['mm'](ns['Ry'](dyaw), R); e = ns['to_euler'](R)
        bob = RING_AMT * (ns['HB'] * (1 - math.cos(p)) + 0.006 * m(1.2, 2)) + LIFT[int(round(f))] if f == int(f) else 0.0
        Rootpos = add(C0, [0, bob, 0]); Rootpos = sub(Rootpos, mvv(R, cl))
        P["CTL_Root_M"][0:3] = e; P["CTL_Root_M"][3:6] = sub(Rootpos, J0)
        own = 0.6 * (ns['HGB'] * m(-1.3) + 0.008 * m(0.4, 2)); tilt = ns['HGS'] * m(-0.5)
        wc = math.sin(math.pi * min(max((f - 1.0) / 38.0, 0.0), 1.0)) ** 2        # khi vòng quay, đồng hồ cát trôi vào đúng TÂM vòng (ngang) để không bị mép vòng quét qua; về lại chỗ cũ ở f0/f40
        Phg = add(Phg0, [wc * (C0[0] - Phg0[0]), bob + own, wc * (C0[2] - Phg0[2])])
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
