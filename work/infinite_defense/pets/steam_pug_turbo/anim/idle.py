"""Steam-Pug Turbo Idle 48f loop (f0==f48), sua 2026-11-14 theo y nguoi dung:
nhip tho GIONG CAC CON KHAC (cham, em, 2 nhip/vong, ca nguoi bong benh nhe, KHONG rung ca nguoi); CHI co cac ONG XA phia sau run len nhu dang phun hoi.
- Luot long 12 cm, bong benh 2 nhip/vong; nguc/dau nhun theo nhip tho; chan, duoi tha tre.
- Cau co: dau cui nhe + ngoay nhin xeo cham.
- ONG XA (Valve giua + Pipe_L/R, 3 ong dung sau lung): rung lien tuc, xoay nga 7/5 do (rx truoc-sau, rz trai-phai), tan so 16/18/14 chu ky/vong lech pha.
  Cuc xa tron (DEF_Exhaust_M = Muzzle) rung tinh tien nhe. Xoay quanh truc khong thay (mesh tron) nen dung tinh tien.
- Kim dong ho do nhap nhay = VFX, khong co trong anim.
+rx = chui mui / chan ve sau, -rx = ngua. ry duoi = ve ben."""
import math
N = 48
CTLS = ["CTL_%s" % n for n in ("Root_M","Spine1_M","Head_M","Goggles_M","Gauge_M","Tail1_M","Tail2_M","Valve_M","Exhaust_M","Pipe_L","Pipe_R","Tank_L","Tank_R",
        "FLeg1_L","FLeg2_L","FPaw_L","FLeg1_R","FLeg2_R","FPaw_R","BLeg1_L","BLeg2_L","BPaw_L","BLeg1_R","BLeg2_R","BPaw_R")]
HOVER = 0.12
def pose(f):
    p = 2 * math.pi * f / N; s = math.sin; b = 2 * p      # b: nhip tho 2/vong
    P = {k: [0, 0, 0, 0, 0, 0] for k in CTLS}             # rx ry rz tx ty tz
    P["CTL_Root_M"][4] = HOVER + 0.025 * s(b - 0.3)
    P["CTL_Root_M"][5] = 0.010 * s(p + 0.8)
    P["CTL_Root_M"][:3] = [1.5 * s(b - 0.9), 2 * s(p), 1.5 * s(p + 0.5)]
    P["CTL_Spine1_M"][:3] = [-2.0 + 2.0 * s(b - 0.5), 1.0 * s(p - 0.4), 0]
    P["CTL_Head_M"][:3] = [3.5 + 1.5 * s(b - 1.0), 6 * s(p - 0.7), 2 * s(p - 0.3)]     # cui cau co + ngoay nhin xeo cham
    P["CTL_Goggles_M"][0] = 1.5 * s(b - 1.6)                                           # nay nhe theo dau
    for side, k, ph in (("L", 1, 0.0), ("R", -1, 0.35)):
        P["CTL_Pipe_" + side][0] = 2.5 * s(b - 1.3 + ph)                                # ong/binh lac nhe tre theo nhip tho (nen cho phan rung nhanh)
        P["CTL_Pipe_" + side][2] = k * 1.5 * s(p - 1.0 + ph)
        P["CTL_Tank_" + side][0] = 1.5 * s(b - 0.9 + ph)
        # chan tha buong (bay lo lung): tu the nghi gan thang, chi dua nhe NGUOC chieu than (lag), L/R cung nhip, khop sau tre hon khop truoc 0.6 rad
        q = 0.12 * ph / 0.35 if ph else 0.0                                              # L/R lech 0.12 rad (chan sau lech them 0.2)
        P["CTL_FLeg1_" + side][0] = 3 + 2.5 * s(b - 1.2 + q)
        P["CTL_FLeg2_" + side][0] = -1 + 2.5 * s(b - 1.8 + q)
        P["CTL_FPaw_" + side][0] = 1 + 2.0 * s(b - 2.4 + q)
        P["CTL_BLeg1_" + side][0] = 4 + 3 * s(b - 1.4 + q)
        P["CTL_BLeg2_" + side][0] = -2 + 3 * s(b - 2.0 + q)
        P["CTL_BPaw_" + side][0] = 1 + 2.0 * s(b - 2.6 + q)
    P["CTL_Tail1_M"][:3] = [-3 + 2 * s(b - 1.0), 14 * s(2 * p), 0]
    P["CTL_Tail2_M"][:3] = [2 * s(b - 1.6), 20 * s(2 * p - 0.9), 0]
    # ONG XA run len nhu phun hoi (chi phan nay rung nhanh)
    amp = 0.8 + 0.2 * s(b)
    P["CTL_Exhaust_M"][3:] = [0.009 * amp * s(16 * p + 0.4) + 0.004 * s(20 * p),
                              0.009 * amp * s(20 * p + 1.3) + 0.004 * s(16 * p + 2.0),
                              0.012 * amp * s(16 * p + 2.4) - 0.006 * s(20 * p + 0.5)]
    P["CTL_Exhaust_M"][0] = -2.5 + 1.5 * s(16 * p + 0.9)
    return P
def apply(api, P):
    for c, v in P.items():
        api.rotate(c, v[0], v[1], v[2]); api.move(c, v[3], v[4], v[5])
def build(api):
    # curve phai co key moi frame truoc khi rotate an (curve rong/thua bo qua rotate): key 0 truoc, roi ghi gia tri
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
