"""Dựng 3 anim cho Unlock vào unlock.json (giữ rig): rig_demo (demo rig từng bộ phận), idle (loop 90F), active (một lần 110F).
Chạy: .venv/Scripts/python.exe -I work/unlock/spine/Unlock/build_anims.py [rig_demo idle active]
Rig phải dựng trước (build_unlock.py). Mọi số người dùng hay sửa nằm ở đầu mỗi hàm."""
import json, math, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "spine")); sys.path.insert(0, os.path.join(ROOT, "tools"))
import anim_kit as K
from key_reduce import reduce_keys
sys.stdout.reconfigure(encoding="utf-8")
JS = os.path.join(HERE, "unlock.json"); REL = "work/unlock/spine/Unlock/unlock.json"
SK = json.load(open(JS, encoding="utf-8")); FPS = 30
BONES = [b["name"] for b in SK["bones"]]
CX, CY = 1166, 596                       # ốc kéo ở tư thế setup (canvas, y xuống)
CHAIN = {"L": ["ribL0", "ribL1", "ribL2", "ribL3"], "R": ["ribR0", "ribR1", "ribR2", "ribR3"]}


def sin2(u, ph=0.0, n=1): return math.sin(2 * math.pi * (n * u - ph))
def ss(a, b, x): return K.ss(a, b, x)


# ------------------------------------------------------------------ FK nhỏ (đo mép cắt, không dựng hình)
def fk(pose):
    W = {}
    for b in SK["bones"]:
        r, tx, ty = pose.get(b["name"], (0, 0, 0))
        x, y, rot = b.get("x", 0) + tx, b.get("y", 0) + ty, b.get("rotation", 0) + r
        if "parent" in b:
            px, py, pa = W[b["parent"]]; c, s = math.cos(math.radians(pa)), math.sin(math.radians(pa))
            W[b["name"]] = (px + x * c - y * s, py + x * s + y * c, pa + rot)
        else:
            W[b["name"]] = (x, y, rot)
    return W


LEN = {b["name"]: b.get("length", 0) for b in SK["bones"]}


def seam_end(W, side):
    x, y, a = W[CHAIN[side][3]]; L = LEN[CHAIN[side][3]]
    return x + L * math.cos(math.radians(a)), y + L * math.sin(math.radians(a))


# ------------------------------------------------------------------ bộ chứa kênh theo frame
class Anim:
    def __init__(self, n):
        self.n = n; F = n + 1
        self.rot = {b: [0.0] * F for b in BONES}; self.tx = {b: [0.0] * F for b in BONES}; self.ty = {b: [0.0] * F for b in BONES}
        self.sc = {b: [1.0] * F for b in BONES}; self.alpha = {}; self.order = []

    def pose(self, f): return {b: (self.rot[b][f], self.tx[b][f], self.ty[b][f]) for b in BONES}

    def emit(self, periodic):
        bones = {}
        for b in BONES:
            tl = {}
            if any(abs(v) > 1e-6 for v in self.rot[b]): tl["rotate"] = reduce_keys([self.rot[b]], ["value"], 0.12, periodic)
            if any(abs(v) > 1e-6 for v in self.tx[b] + self.ty[b]): tl["translate"] = reduce_keys([self.tx[b], self.ty[b]], ["x", "y"], 0.25, periodic)
            if any(abs(v - 1) > 1e-6 for v in self.sc[b]): tl["scale"] = reduce_keys([self.sc[b], self.sc[b]], ["x", "y"], 0.002, periodic)
            if tl: bones[b] = tl
        out = {"bones": bones}
        slots = {}
        for sl, keys in self.alpha.items():                    # keys: [(frame, alpha 0..1)]
            slots[sl] = {"rgba": [{**({"time": K.ktime(f / FPS, FPS)} if f else {}), "color": "ffffff%02x" % round(a * 255)} for f, a in keys]}
        if slots: out["slots"] = slots
        if self.order: out["drawOrder"] = [{"time": K.ktime(f / FPS, FPS), "offsets": o} for f, o in self.order]
        return out


def damped(f, f0, amp, hz, k):                                   # lò xo tắt dần bắt đầu ở f0 (frame)
    if f < f0: return 0.0
    t = (f - f0) / FPS; return amp * math.exp(-k * t) * math.sin(2 * math.pi * hz * t)


def drop(f, f0, tgt, hz, zeta):                                  # rơi về góc tgt có nảy (hệ lò xo bậc 2, bắt đầu nghỉ)
    if f <= f0: return 0.0
    t = (f - f0) / FPS; w = 2 * math.pi * hz; wd = w * math.sqrt(1 - zeta * zeta)
    return tgt * (1 - math.exp(-zeta * w * t) * (math.cos(wd * t) + zeta / math.sqrt(1 - zeta * zeta) * math.sin(wd * t)))


def px2sp(px, py): return px - CX, -(py - CY)                      # vị trí ốc (canvas) -> dời sc_root


# ------------------------------------------------------------------ IDLE (loop 90F = 3 s): bập bùng nhẹ
def idle_fields(N=90):
    """trả về hàm f -> {kênh} để idle và active dùng chung (active mở đầu đúng idle F0)"""
    P = dict(ctrl_ty=3.0, ctrl_sc=0.004, bow_rot=2.2, bow_sc=0.012, bowM_rot=1.5, bowM_sc=0.015, tail=5.0, rib=[0.35, 0.45, 0.5, 0.4])
    def at(f):
        u = f / N; d = {}
        d["ctrl"] = dict(ty=P["ctrl_ty"] * sin2(u), sc=1 + P["ctrl_sc"] * sin2(u, 0.25))
        d["bowL"] = dict(rot=P["bow_rot"] * sin2(u, 0.10), sc=1 + P["bow_sc"] * sin2(u, 0.20))
        d["bowR"] = dict(rot=-P["bow_rot"] * sin2(u, 0.35), sc=1 + P["bow_sc"] * sin2(u, 0.45))
        d["bowM"] = dict(rot=P["bowM_rot"] * sin2(u, 0.50), sc=1 + P["bowM_sc"] * sin2(u, 0.70))
        for nm, sg, ph in (("bowL_t", 1, 0.00), ("bowR_t", -1, 0.15), ("bowM_t", 1, 0.30)):
            d[nm] = dict(rot=sg * (P["tail"] * sin2(u, 0.18 + ph) + 1.5 * sin2(u, 0.10 + ph, 2)))
        for side, sg, ph in (("L", -1, 0.00), ("R", 1, 0.06)):
            for k, b in enumerate(CHAIN[side]): d[b] = dict(rot=sg * P["rib"][k] * sin2(u, 0.05 + ph + 0.07 * k))
        return d
    return at


def apply_idle(A, at, w=lambda f, b: 1.0):
    """w(f, bone) = trọng số idle theo thời gian (active giảm dần phần dải / nơ giữa)"""
    for f in range(A.n + 1):
        d = at(f)
        for b, v in d.items():
            wt = w(f, b)
            if "rot" in v: A.rot[b][f] += v["rot"] * wt
            if "ty" in v: A.ty[b][f] += v["ty"] * wt
            if "sc" in v: A.sc[b][f] = 1 + (v["sc"] - 1) * wt
        # nơ giữa cưỡi theo mép cắt (trung bình hai nửa) để không hở / lệch
        pose = {b: (A.rot[b][f], A.tx[b][f], A.ty[b][f]) for b in BONES}
        W0 = fk({}); W1 = fk(pose)
        dl = [(seam_end(W1, s)[i] - seam_end(W0, s)[i]) for s in "LR" for i in (0, 1)]
        A.tx["bowM"][f] += (dl[0] + dl[2]) / 2 - (A.tx["ctrl"][f]); A.ty["bowM"][f] += ((dl[1] + dl[3]) / 2 - A.ty["ctrl"][f]) * w(f, "bowM")


def build_idle():
    N = 90; A = Anim(N); at = idle_fields(N)
    for f in range(N + 1):
        pass
    apply_idle(A, at)
    # bù nơ giữa: apply_idle đã trừ phần ctrl (nơ là con ctrl nên đi theo ctrl); chuỗi nằm dưới ctrl nên cộng thêm ctrl vào sai số -> đo lại bên dưới
    A.alpha = {"scissor_A": [(0, 0.0)], "scissor_B": [(0, 0.0)]}
    return A, True


# ------------------------------------------------------------------ ACTIVE (một lần 110F)
def build_active():
    N = 66; A = Anim(N); at = idle_fields(90)
    CUT = 35                                                   # frame kéo khép lại = cắt
    FADE0, FADE1 = 50, 62                                      # ruy băng + nơ mờ hẳn
    # idle chạy tiếp ở hai nơ góc + đuôi; dải / nơ giữa / ctrl tắt dần trước khi kéo tới
    def w(f, b):
        if b.startswith("rib") or b in ("bowM", "bowM_t", "ctrl"): return 1 - ss(6, 28, f)
        return 1.0
    apply_idle(A, at, w)
    # kéo: đường bay ốc (canvas), xoay root, mở / khép lưỡi
    # đường bay kéo = cung cong: lấy đà (giữ 1F cho căng) -> lao nhanh qua điểm cắt -> lướt tiếp lên-trái, cong dần lên trên
    # F0-29: bay vào + lấy đà (spl). F29-45: MỘT CUNG TRÒN qua 3 điểm: điểm lấy đà W (F29) -> điểm cắt C (F35, đúng dưới nơ giữa) -> điểm thoát E (F45);
    # tốc độ trên cung theo spl của góc (tăng tốc tới điểm cắt rồi lướt), lưỡi quay theo tiếp tuyến cung
    X0 = K.spl([(0, 1150), (3, 1150), (17, 1290), (28, 1560), (29, 1560)]); Y0 = K.spl([(0, 1080), (3, 1080), (17, 700), (28, 860), (29, 860)])
    R0 = K.spl([(0, 0), (3, 0), (17, -8), (28, 16), (29, 16)])
    Wp, Cp, Ep = (1560, 860), (948, 624), (380, -100)
    ax, ay, bx, by = Cp[0] - Wp[0], Cp[1] - Wp[1], Ep[0] - Wp[0], Ep[1] - Wp[1]
    dd = 2 * (ax * by - ay * bx)
    ox = Wp[0] + (by * (ax * ax + ay * ay) - ay * (bx * bx + by * by)) / dd; oy = Wp[1] + (ax * (bx * bx + by * by) - bx * (ax * ax + ay * ay)) / dd
    rad = math.hypot(Wp[0] - ox, Wp[1] - oy)
    wrap = lambda a: (a + math.pi) % (2 * math.pi) - math.pi
    tw, tc, te = [math.atan2(q[1] - oy, q[0] - ox) for q in (Wp, Cp, Ep)]
    d1, d2 = wrap(tc - tw), wrap(te - tc); sgn = 1 if d1 + d2 > 0 else -1
    sC = d1 / (d1 + d2); G = K.spl([(29, 0.0), (CUT, sC), (45, 1.0), (50, 1.15)])
    def arc(f):
        th = tw + G(f) * (d1 + d2)
        return ox + rad * math.cos(th), oy + rad * math.sin(th), th
    X = lambda f: X0(f) if f <= 29 else arc(f)[0]
    Y = lambda f: Y0(f) if f <= 29 else arc(f)[1]
    def R(f):
        if f <= 29: return R0(f)
        th = arc(f)[2]; hx, hy = -math.sin(th) * sgn, math.cos(th) * sgn           # tiếp tuyến (canvas, y xuống)
        h = math.degrees(math.atan2(-hy, hx)); T = 0.8 * ((h - 148 + 180) % 360 - 180)
        b = ss(29, 36, f); return 16 * (1 - b) + T * b
    BA = K.spl([(0, 0), (17, 0), (20, -6), (26, 16), (31, 16), (CUT, -26), (CUT + 2, -23), (50, -23)])
    for f in range(N + 1):
        A.tx["sc_root"][f], A.ty["sc_root"][f] = px2sp(X(f), Y(f)); A.rot["sc_root"][f] = R(f)
        A.rot["sc_A"][f] = BA(f); A.rot["sc_B"][f] = -BA(f); A.sc["sc_root"][f] = 1 - 0.2 * ss(40, 46, f)   # xa dần
    A.alpha["scissor_A"] = A.alpha["scissor_B"] = [(0, 0.0), (3, 0.0), (6, 1.0), (40, 1.0), (46, 0.0)]
    A.order = [(26, [{"slot": "scissor_B", "offset": -3}, {"slot": "scissor_A", "offset": -3}])]   # kéo chui ra sau nơ giữa trước khi chém
    # dải ruy băng rơi sau cú cắt
    tgtL, tgtR = [-52, -9, -7, -6], [49, 9, 7, 6]
    for k in range(4):
        for f in range(N + 1):
            A.rot[CHAIN["L"][k]][f] += drop(f, CUT + 2 * k, tgtL[k], 1.0, 0.30)
            A.rot[CHAIN["R"][k]][f] += drop(f, CUT + 1 + 2 * k, tgtR[k], 1.05, 0.28)
    for f in range(N + 1):
        # nơ góc giật theo, đuôi nơ vung
        A.rot["bowL"][f] += damped(f, CUT, 7, 1.6, 3.0); A.rot["bowR"][f] += damped(f, CUT, -7, 1.6, 3.0)
        A.rot["bowL_t"][f] += damped(f, CUT + 1, 14, 1.5, 2.5); A.rot["bowR_t"][f] += damped(f, CUT + 1, -14, 1.5, 2.5)
        A.ty["ctrl"][f] += damped(f, CUT, -6, 1.8, 4.0)
        # nơ giữa: nhấc nhẹ rồi rơi (trọng lực), xoay + trôi, mờ dần
        t = min(max(0, f - CUT) / FPS, 0.75)
        pop = 14 * math.sin(math.pi * min(t / 0.18, 1.0)) if 0 < t < 0.18 else 0.0
        fall = 1500 * max(0.0, t - 0.1) ** 2
        if f >= CUT:
            A.ty["bowM"][f] = pop - fall; A.tx["bowM"][f] = -18 * ss(0.05, 0.7, t)
            A.rot["bowM"][f] = -28 * ss(0.05, 0.7, t); A.rot["bowM_t"][f] = damped(f, CUT, 20, 1.8, 1.5)
    for sl in ("ribbon_L", "ribbon_R", "bow_L", "bow_R", "bow_M"):   # cả ruy băng biến mất cùng nhau sau cú cắt
        A.alpha[sl] = [(0, 1.0), (FADE0, 1.0), (FADE1, 0.0)]
    return A, False


# ------------------------------------------------------------------ RIG DEMO (180F loop): từng bộ phận lần lượt
def build_demo():
    N = 180; A = Anim(N)
    def seg(f, f0, f1):                                          # 0..1 trong đoạn, ngoài = None
        return (f - f0) / (f1 - f0) if f0 <= f <= f1 else None
    for f in range(N + 1):
        u = seg(f, 0, 16)                                       # ctrl: nhấc + phồng
        if u is not None: A.ty["ctrl"][f] += 40 * math.sin(math.pi * u); A.sc["ctrl"][f] = 1 + 0.05 * math.sin(math.pi * u)
        for (a, b), (bow, tail, sg) in (((16, 34), ("bowL", "bowL_t", 1)), ((34, 52), ("bowR", "bowR_t", -1)), ((52, 70), ("bowM", "bowM_t", 1))):
            u = seg(f, a, b)
            if u is not None:
                A.rot[bow][f] += 15 * sin2(u) * sg; A.rot[tail][f] += 24 * sin2(u, 0.15) * sg
                A.sc[bow][f] = 1 + 0.06 * math.sin(math.pi * u)
        for (a, side, sg) in ((70, "L", -1), (100, "R", 1)):     # dải: mỗi đốt một nhịp nối tiếp
            for k, bn in enumerate(CHAIN[side]):
                u = seg(f, a + k * 6, a + k * 6 + 12)
                if u is not None: A.rot[bn][f] += sg * 22 * math.sin(math.pi * u)
        u = seg(f, 130, 172)                                    # kéo: bay lên, mở khép, về chỗ cũ
        if u is not None:
            e = math.sin(math.pi * u)
            A.ty["sc_root"][f] += 70 * e; A.tx["sc_root"][f] -= 50 * e; A.rot["sc_root"][f] += 12 * e
            A.rot["sc_A"][f] += 14 * sin2(u, 0, 2) * (1 if u < 0.9 else 0) - 24 * ss(0.25, 0.45, u) * (1 - ss(0.55, 0.75, u)); A.rot["sc_B"][f] = -A.rot["sc_A"][f]
    return A, True


def post_meta(name, loop):
    try:
        req = urllib.request.Request("http://127.0.0.1:8781/api/spine/anim", json.dumps({"json": REL, "op": "meta", "name": name, "loop": loop}).encode(),
                                     {"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=3).read()
    except Exception as e:
        print("(không ghi được cờ loop:", e, ")")


if __name__ == "__main__":
    want = sys.argv[1:] or ["rig_demo", "idle", "active"]
    B = {"rig_demo": build_demo, "idle": build_idle, "active": build_active}
    for nm in want:
        A, loop = B[nm](); anim = A.emit(periodic=loop)
        K.write_anim(JS, nm, anim, "Claude gen %s (Unlock)" % nm)
        post_meta(nm, loop)
        nk = sum(len(v) for t in anim["bones"].values() for v in t.values())
        print("%s: %dF %s | %d xương, %d key" % (nm, A.n, "loop" if loop else "một lần", len(anim["bones"]), nk))
