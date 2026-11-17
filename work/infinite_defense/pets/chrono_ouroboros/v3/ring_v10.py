"""Pose vòng tròn (ouroboros) cho rig v3. Thân + đuôi cuộn về phía BỤNG (vây lưng nằm ngoài vòng, đúng concept): thân rx dương, đuôi rx âm.
Vòng nằm trong mặt phẳng đứng (Y-Z) + xoắn nhẹ ra trước/sau (ry mỗi khớp) để đầu và đuôi bắt chéo nhau (điểm giao số 8). Tâm vòng dưới Root.
Root xoay rx = PHI để đặt khe hở (đầu - đuôi) ra phía trước (+Z). Đồng hồ cát về tâm vòng (hạ HG_DY), giữ thẳng đứng (bù PHI), chỉ xoay Y.
Đầu mesh bind đã cúi xuống ~70 độ nên phải ngửa đầu (Head/Neck2 rx âm) để mõm đi tiếp theo đường vòng, không cuộn ngược vào tâm."""
import math
SPN = ["Spine%d" % k for k in range(1, 9)]; NK = ["Neck1", "Neck2", "Head"]; TL = ["Tail%d" % k for k in range(1, 8)]
CTLS = ["CTL_%s_M" % n for n in ["Root"] + SPN + NK + ["Jaw"] + TL + ["Hourglass"]]
# v9 (sửa theo director 2026-11-17): R 0,52, PHI -150, ngửa đầu -75 (đầu bind đã cúi), xoắn ra trước (đầu +x) / sau (đuôi -x)
CFG = dict(R=0.52, PHI=-150.0, TAIL_EXTRA=-10.0, HEAD_EXTRA=-75.0, NECK2_EXTRA=-10.0, TAIL_TIP=-10.0, YAW_SPINE=4.0, YAW_TAIL=9.0, HG_DY=-0.02, HG_DZ=0.05, ROOT_YAW=0.0, HG_X=0.08)   # v10: đồng hồ cát dời +0,08 m về phía đầu (x), nâng 2 cm
def ring_pose(W, cfg=None, scale=1.0):
    c = dict(CFG); c.update(cfg or {}); R = c['R']
    P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}
    seg = lambda a, b: math.dist(W["DEF_%s_M" % a], W["DEF_%s_M" % b])
    cf = SPN + NK
    for i, n in enumerate(cf[:-1]):
        P["CTL_%s_M" % n][0] = math.degrees(seg(n, cf[i + 1]) / R) * scale
    P["CTL_Head_M"][0] = (math.degrees(0.10 / R) + c['HEAD_EXTRA']) * scale
    P["CTL_Neck2_M"][0] += c['NECK2_EXTRA'] * scale
    for i, n in enumerate(TL[:-1]): P["CTL_%s_M" % n][0] = -math.degrees(seg(n, TL[i + 1]) / R) * scale
    for n in TL[2:]: P["CTL_%s_M" % n][0] += c['TAIL_EXTRA'] * scale
    P["CTL_Tail7_M"][0] += c['TAIL_TIP'] * scale
    for n in SPN: P["CTL_%s_M" % n][1] = c['YAW_SPINE'] * scale
    for n in TL: P["CTL_%s_M" % n][1] = c['YAW_TAIL'] * scale
    P["CTL_Root_M"][0] = c['PHI'] * scale; P["CTL_Root_M"][1] = c['ROOT_YAW'] * scale
    # HG_DY / HG_DZ = dời đồng hồ cát so với tâm vòng THEO TRỤC THẾ GIỚI (Y lên, Z ra trước); đổi sang trục cục bộ của Root (đã xoay PHI)
    ph = math.radians(c['PHI']); wy, wz = c['HG_DY'], c['HG_DZ']
    ly = wy * math.cos(ph) + wz * math.sin(ph); lz = -wy * math.sin(ph) + wz * math.cos(ph)
    hg = P["CTL_Hourglass_M"]; hg[0] = -c['PHI'] * scale; hg[4] = (-R + ly) * scale; hg[5] = (-0.495 + lz) * scale; hg[3] = c['HG_X'] * scale
    return P
def apply(api, P):
    for c, v in P.items(): api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
