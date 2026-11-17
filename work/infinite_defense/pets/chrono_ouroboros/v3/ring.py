"""Pose vòng tròn ouroboros cho rig v3 - bản TRÒN THẬT (v11): giải hình học thay vì cộng độ cong đều.
Mọi khớp thân/cổ/đuôi nằm trên MỘT đường tròn bán kính R trong mặt phẳng đứng; Root nằm giữa dây cung phẳng Spine1-Tail1 (lệch tâm ~3 cm vào trong).
Mỗi đoạn xương là một dây cung của đường tròn => góc xoay khớp = (hướng dây cung) - (hướng xương lúc bind) - (góc khớp cha). Hướng xương bind đo từ joint thật nên đuôi bind cong lên vẫn đúng.
Vòng cuộn về phía BỤNG (vây lưng ngoài vòng). Root xoay rx = PHI để đặt khe hở đầu-đuôi. Đầu: tiếp tuyến + HEAD_DOWN độ (mõm đi tiếp đường vòng, cúi nhẹ).
Xoắn ra khỏi mặt phẳng: YAW_SPINE / YAW_TAIL (ry mỗi khớp) => đầu ra trước (+x), đuôi lùi sau (-x). Đồng hồ cát về tâm vòng (+HG_*), thẳng đứng (bù PHI)."""
import math
SPN = ["Spine%d" % k for k in range(1, 9)]; NK = ["Neck1", "Neck2", "Head"]; TL = ["Tail%d" % k for k in range(1, 8)]
CTLS = ["CTL_%s_M" % n for n in ["Root"] + SPN + NK + ["Jaw"] + TL + ["Hourglass"]]
CFG = dict(R=0.54, PHI=-165.0, HEAD_DOWN=12.0, TAIL_TIP=0.0, YAW_SPINE=14.0, YAW_TAIL=20.0, HG_DY=-0.02, HG_DZ=0.05, HG_X=0.08)
def _norm(a):
    while a > 180: a -= 360
    while a < -180: a += 360
    return a
def ring_pose(W, cfg=None, scale=1.0):
    c = dict(CFG); c.update(cfg or {}); R = c['R']
    J = lambda n: W["DEF_%s_M" % n]
    vec = lambda a, b: (J(b)[2] - J(a)[2], J(b)[1] - J(a)[1])       # (dz, dy) bind của đoạn a -> b
    ang = lambda v: math.degrees(math.atan2(-v[1], v[0]))             # góc so với +z, dương = chúi xuống (rx dương)
    L = lambda a, b: math.hypot(*vec(a, b))
    P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}
    chain_s = ["Spine1"] + SPN[1:] + NK         # Spine1 ... Head
    chain_t = TL
    # vị trí trên đường tròn: theta từ ĐỈNH, dương về phía +z (thân), âm về phía đuôi
    beta_s = math.asin(L("Root", "Spine1") / R); beta_t = math.asin(L("Root", "Tail1") / R)
    th = {"Spine1": beta_s, "Tail1": -beta_t}
    for a, b in zip(chain_s[:-1], chain_s[1:]): th[b] = th[a] + 2 * math.asin(L(a, b) / (2 * R))
    for a, b in zip(chain_t[:-1], chain_t[1:]): th[b] = th[a] - 2 * math.asin(L(a, b) / (2 * R))
    pt = lambda n: (R * math.sin(th[n]), R * math.cos(th[n]))        # (z, y)
    def chord_angle(a, b):
        pa, pb = pt(a), pt(b); return ang((pb[0] - pa[0], pb[1] - pa[1]))
    # Root: dây cung phẳng, hướng +z => orient 0
    orient = {"Root": 0.0}
    prev = "Root"
    for i, n in enumerate(chain_s[:-1]):
        nxt = chain_s[i + 1]
        o = _norm(chord_angle(n, nxt) - ang(vec(n, nxt)))
        orient[n] = o; P["CTL_%s_M" % n][0] = _norm(o - orient[prev]) * scale; prev = n
    # Head: tiếp tuyến đường tròn tại Head + HEAD_DOWN, hướng xương Head -> Jaw
    tang = math.degrees(th["Head"])                                        # hướng đi tới tại Head (rx của tiếp tuyến = theta)
    o = _norm(tang + c['HEAD_DOWN'] - ang(vec("Head", "Jaw")))
    P["CTL_Head_M"][0] = _norm(o - orient["Neck2"]) * scale
    prev = "Root"
    for i, n in enumerate(chain_t[:-1]):
        nxt = chain_t[i + 1]
        o = _norm(chord_angle(n, nxt) - ang(vec(n, nxt)))
        orient[n] = o; P["CTL_%s_M" % n][0] = _norm(o - orient[prev]) * scale; prev = n
    P["CTL_Tail7_M"][0] += c['TAIL_TIP'] * scale
    # Root -> Tail1 là dây cung phẳng: hướng xương bind Root->Tail1 là -z (+ chút y), orient Root = 0 nên Tail1 xoay bù độ lệch bind
    P["CTL_Tail1_M"][0] = _norm(chord_angle("Tail1", "Tail2") - ang(vec("Tail1", "Tail2"))) * scale
    # xoắn ra khỏi mặt phẳng chỉ dồn về hai đầu (bình phương theo vị trí) để phần thân giữa vẫn tròn phẳng
    for k, n in enumerate(SPN, 1): P["CTL_%s_M" % n][1] = c['YAW_SPINE'] * (k / 8.0) ** 2 * scale
    for k, n in enumerate(TL, 1): P["CTL_%s_M" % n][1] = c['YAW_TAIL'] * (k / 7.0) ** 2 * scale
    P["CTL_Root_M"][0] = c['PHI'] * scale
    # Root nằm trên dây cung, cách tâm vòng sqrt(R^2 - chord_half^2) ~ R - 0.03; tâm vòng ở (y = -(R - s)) trong khung Root
    s = R - math.sqrt(R * R - (0.5 * (L("Root", "Spine1") + L("Root", "Tail1"))) ** 2)
    ph = math.radians(c['PHI']); wy, wz = c['HG_DY'], c['HG_DZ']
    ly = wy * math.cos(ph) + wz * math.sin(ph); lz = -wy * math.sin(ph) + wz * math.cos(ph)
    hg = P["CTL_Hourglass_M"]; hg[0] = -c['PHI'] * scale; hg[4] = (-(R - s) + ly) * scale; hg[5] = (-0.5 + lz) * scale; hg[3] = c['HG_X'] * scale
    return P
def apply(api, P):
    for c, v in P.items(): api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
