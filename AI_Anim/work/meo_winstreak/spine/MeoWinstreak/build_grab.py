"""Anim `grab` (162F, 30fps, LOOP: frame cuối = frame 0) cho MeoWinstreak: mèo idle -> máy gắp từ trên cao hạ xuống, càng khép -> nhấc mèo lên cao, mèo giãy, máy mở càng thả mèo rơi tự do xuống đất.
Chạy: .venv/Scripts/python.exe -I work/meo_winstreak/spine/MeoWinstreak/build_grab.py [meo.json]
Chỉ ghi anim `grab` (giữ rig + anim khác). Đầu lượt chạy `spine_live_cmd.py gen-start`; đọc `anim_kit.user_edits` trước khi chạy lại.

Mốc (frame): 0-46 idle (thở, chớp F20, ngẩng đầu / vểnh tai F26-40) trong khi máy hạ xuống (F6 bắt đầu, F46 chạm);
  F40-52 càng khép (ép thêm 3° rồi nới), mặt nam -> keo F52, mèo bị ép (squash F54);
  F56-110 nhấc lên H px (hơi nhún xuống trước), mèo bám máy (cat = chuyển động cứng quanh đỉnh cán + D), bị kéo giãn;
  F58-150 mèo giãy (đầu / thân / hông ngoáy ngược pha, chân + bàn chân + cục nhô vẫy, tai phẩy, miệng mở / đóng), cả máy đu đưa.
Trục: root xoay 90° -> con của root (cat, hang): dời thế giới (dx, dy) = local (tx, ty) = (dy, -dx). Xoay dương = ngược chiều kim đồng hồ.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "spine")); sys.path.insert(0, os.path.join(ROOT, "tools"))
import anim_kit as K
from key_reduce import reduce_keys
sys.stdout.reconfigure(encoding="utf-8")

FPS = 30
T0 = 26                   # frame máy chạm mèo (càng khép lại quanh đó)
R = 110                   # frame máy mở càng thả mèo (R - T0 = 3 chu kỳ đu đưa 28F: cán đang ở giữa nhịp, mèo không lệch ngang)
TF = 13                   # mèo rơi tự do R -> LAND (13F, ~2000 px, gia tốc đều, chạm đất ~300 px/F)
LAND = R + TF
K_BODY = 0.2              # hệ số biên độ lắc THÂN / ĐẦU khi giãy (2026-11-27: người dùng "giảm biên độ lắc của mèo sao cho không bị lộ hoặc cắt"; bản #14 = 1.0).
                          # Mép cắt giữa cat_head và thân máy là bản sao mép kẹp ở tư thế gốc: lắc lệch quá vài px thì lộ bậc.
K_STRETCH = 0.15           # hệ số độ kéo giãn dọc khi bị nhấc / giãy (bản #14 = 1.0)
HOP1 = 85.0               # độ cao nảy lần 1 (px). Người dùng chọn bản #14 (85 px, dẹt 0.74 / 1.24, nảy 7F) hơn các bản sau (2026-11-27)
EYE_OPEN = 138              # frame mèo bắt đầu mở mắt lại (đổi mặt keo -> nam, mở hẳn ở EYE_OPEN + 2)
N = LAND + 34
H = 2000.0                # độ cao nhấc (px)
D0 = 3200.0               # máy bắt đầu cao hơn vị trí gắp (px)
ARM_OPEN = 28.0           # độ mở càng (độ)
L_CAT = 4320.0            # từ đỉnh cán (gốc hang) tới gốc xương cat (px, thế giới)
ss = K.ss

# ------------------------------------------------------------------ hàm thời gian (frame)
# loop (2026-11-27): sau khi thả mèo, máy bay lên lại D0 (F LAND+6 -> N-4) để F cuối = F0 (máy trên cao, càng mở, mèo idle mặt nam)
# rơi: F8 -> T0 (18F, nhanh dần như rơi tự do); nhấc: T0+9 -> T0+38 (~30F); giữ + giãy tới R; R: càng bật mở, máy giật nhẹ lên, mèo rơi
D = K.spl([(0, D0), (8, D0), (13, 0.88 * D0), (17, 0.60 * D0), (21, 0.27 * D0), (T0, 0), (T0 + 4, -20), (T0 + 9, -6),
           (T0 + 16, 0.15 * H), (T0 + 24, 0.67 * H), (T0 + 32, 0.97 * H), (T0 + 38, H), (R, H), (LAND + 6, H), (N - 4, D0), (N, D0)])
W_GRIP = lambda f: ss(T0 + 6, T0 + 14, f) if f <= R else 0.0                      # mèo bám máy (hết ở R: rơi tự do)
_base = lambda f: ss(T0 + 12, T0 + 26, f) * (1 - 0.35 * ss(T0 + 60, R, f))
STRUG = lambda f: _base(f) if f <= R else _base(R) * (1 - ss(LAND - 2, LAND + 3, f))   # giãy của mèo: tiếp tục (hoảng) lúc rơi, tắt khi chạm đất
STRUG_M = lambda f: _base(f) if f <= R else _base(R) * (1 - ss(R, R + 3, f))           # lắc của máy: tắt hẳn ngay sau khi thả (máy đứng yên)
LIFT = lambda f: ss(T0 + 14, T0 + 34, f) * (1 - 0.45 * ss(T0 + 64, T0 + 94, f)) * (1 - ss(R, R + 4, f))   # độ căng khi bị nhấc (hết khi thả)
sw = lambda f, per, ph=0.0: math.sin(2 * math.pi * (f - (T0 + 12) - ph) / per)    # sóng giãy
u1 = lambda f: 0.75 * sw(f, 8.0) + 0.25 * sw(f, 12.0, 1.5)               # nhịp ngoáy chính (hơi lệch)
THETA = lambda f: (0.7 * ss(T0 - 12, T0, f) * (1 - ss(T0 + 2, T0 + 20, f)) + 1.0 * STRUG_M(f)) * math.sin(2 * math.pi * (f - T0) / 28.0)   # đu đưa cán (độ)

arm_R = K.spl([(0, ARM_OPEN), (T0 - 8, ARM_OPEN), (T0 - 4, ARM_OPEN + 3), (T0 + 6, -3), (T0 + 12, -1), (T0 + 18, -1.5), (R - 4, -1.5),
               (R + 4, ARM_OPEN), (N, ARM_OPEN)])
ripple = lambda f, ph: 1.5 * STRUG_M(f) * sw(f, 7.0, ph) * (1 - ss(R - 4, R, f))
# cat scale: ép khi bị gắp, kéo dài khi rơi, dẹt khi chạm đất, nảy 2 lần rồi yên
squash = K.spl([(0, 1.0), (T0, 1.0), (T0 + 8, 0.92), (T0 + 16, 1.02), (T0 + 24, 1.0), (R, 1.0), (R + 5, 1.08), (LAND - 1, 1.14),
                (LAND + 2, 0.74), (LAND + 5, 0.78), (LAND + 8, 1.24), (LAND + 13, 0.82), (LAND + 17, 1.04), (LAND + 23, 1.0), (N, 1.0)])
squash_h = K.spl([(0, 1.0), (T0, 1.0), (T0 + 8, 1.06), (T0 + 16, 0.99), (T0 + 24, 1.0), (R, 1.0), (R + 5, 0.95), (LAND - 1, 0.92),
                  (LAND + 2, 1.24), (LAND + 5, 1.20), (LAND + 8, 0.84), (LAND + 13, 1.16), (LAND + 17, 0.98), (LAND + 23, 1.0), (N, 1.0)])
perk = K.spl([(0, 0), (T0 - 20, 0), (T0 - 14, 7), (T0 - 6, 5), (T0 + 6, -6), (T0 + 14, 0), (N, 0)])    # tai vểnh rồi cụp khi bị gắp
look = lambda f: 3.0 * ss(T0 - 22, T0 - 12, f) * (1 - ss(T0 - 4, T0 + 6, f))                         # ngẩng đầu nhìn kẹp
breath = lambda f: math.sin(2 * math.pi * f / 36.0) * (1 - ss(T0 - 8, T0 + 6, f))
blink_k = K.spl([(0, 1), (9, 1), (11, 0.08), (12, 0.08), (14, 1), (N, 1)])


def samples(fn, n=N):
    return [fn(f) for f in range(n + 1)]


def hop(f):
    """nảy sau khi chạm đất (khớp bản #14 người dùng chọn): lần 1 cao HOP1 px trong 7F (LAND+5 -> +12), lần 2 cao 10 px trong 5F (+12 -> +17)"""
    if LAND + 5 <= f <= LAND + 12:
        u = (f - LAND - 5) / 7.0; return HOP1 * 4 * u * (1 - u)
    if LAND + 12 < f <= LAND + 17:
        u = (f - LAND - 12) / 5.0; return 10 * 4 * u * (1 - u)
    return 0.0


HANG_FILE = None        # key `hang` (xoay / dời) người dùng đã sửa trong file (Graph: xoá key, Sửa curve): nếu có thì GIỮ NGUYÊN và mèo bám theo chính các key đó
_hang_cache = {}


def th_deg(f):
    """góc đu đưa THỰC của xương hang tại frame f (độ): từ file nếu người dùng đã sửa, không thì THETA của script"""
    if HANG_FILE is None:
        return THETA(f)
    g = _hang_cache.setdefault("r", K.spine_curve(HANG_FILE["rotate"], "value"))
    return g(f)


def d_px(f):
    """độ dời THỰC của xương hang (px, local x = dời lên thế giới)"""
    if HANG_FILE is None:
        return D(f)
    g = _hang_cache.setdefault("t", K.spine_curve(HANG_FILE["translate"], "x"))
    return g(f)


def cat_xy(f):
    """dời THẾ GIỚI của xương cat: tới R bám máy (cứng quanh đỉnh cán + D), sau R rơi tự do về 0 (dy = dy0 (1 - u^2)), rồi nảy"""
    if f <= R:
        th = math.radians(th_deg(f)); w = W_GRIP(f)
        return L_CAT * math.sin(th) * w, (L_CAT * (1 - math.cos(th)) + d_px(f)) * w
    th = math.radians(th_deg(R)); dx0 = L_CAT * math.sin(th); dy0 = L_CAT * (1 - math.cos(th)) + d_px(R)
    u = min(1.0, (f - R) / float(TF))
    return dx0 * (1 - ss(R, LAND, f)), dy0 * (1 - u * u) + hop(f)


def cat_rot(f):
    if f <= R:
        return W_GRIP(f) * th_deg(f) + 4.0 * K_BODY * STRUG(f) * u1(f - 1)
    u = min(1.0, (f - R) / float(TF))
    return 9.0 * math.sin(math.pi * u) + 4.0 * K_BODY * STRUG(f) * u1(f - 1)       # xoay nhẹ khi rơi


def build(path=None):
    global HANG_FILE
    HANG_FILE = None; _hang_cache.clear()
    if path and os.path.isfile(path):          # người dùng đã sửa key hang trên Spine Live? -> giữ nguyên + mèo bám theo
        hf = (K.load(path).get("animations", {}).get("grab", {}).get("bones", {}) or {}).get("hang")
        if hf and hf.get("rotate") and hf.get("translate"):
            gr, gt = K.spine_curve(hf["rotate"], "value"), K.spine_curve(hf["translate"], "x")
            dr = max(abs(gr(f) - THETA(f)) for f in range(N + 1)); dt = max(abs(gt(f) - D(f)) for f in range(N + 1))
            if dr > 0.05 or dt > 0.5:
                HANG_FILE = {"rotate": hf["rotate"], "translate": hf["translate"]}
                print("hang đã được người dùng sửa (lệch xoay %.2f°, dời %.0f px so với script): GIỮ NGUYÊN, mèo bám theo key của file" % (dr, dt))
    B = {}
    def rot(b, fn, tol=0.15):
        B.setdefault(b, {})["rotate"] = reduce_keys([samples(fn)], ["value"], tol, False)
    def scl(b, fx, fy, tol=0.003):
        B.setdefault(b, {})["scale"] = reduce_keys([samples(fx), samples(fy)], ["x", "y"], tol, False)
    def trn(b, fx, fy, tol=0.3):
        B.setdefault(b, {})["translate"] = reduce_keys([samples(fx), samples(fy)], ["x", "y"], tol, False)

    # máy gắp: hang dời (D) + đu đưa; càng khép / mở
    if HANG_FILE is None:
        trn("hang", lambda f: D(f), lambda f: 0.0)                    # local tx = dy (world lên)
        rot("hang", THETA, 0.05)
    else:
        import copy
        B["hang"] = {"rotate": copy.deepcopy(HANG_FILE["rotate"]), "translate": copy.deepcopy(HANG_FILE["translate"])}
    rot("arm_R", lambda f: arm_R(f) + ripple(f, 0.0), 0.12)
    rot("arm_L", lambda f: -arm_R(f) - ripple(f, 3.5), 0.12)
    # mèo bám máy (cứng quanh đỉnh cán) + squash khi bị ép
    trn("cat", lambda f: cat_xy(f)[1], lambda f: -cat_xy(f)[0])
    rot("cat", cat_rot, 0.05)
    scl("cat", squash, squash_h)
    # thở + ngẩng đầu + giãy
    scl("spine", lambda f: 1 + 0.010 * breath(f) + 0.07 * K_STRETCH * LIFT(f) + 0.04 * K_STRETCH * STRUG(f) * sw(f, 7.0, -1.75),
        lambda f: 1 - 0.035 * K_STRETCH * LIFT(f) - 0.025 * K_STRETCH * STRUG(f) * sw(f, 7.0, -1.75))
    scl("hip", lambda f: 1 + 0.006 * breath(f) + 0.03 * K_STRETCH * LIFT(f), lambda f: 1 - 0.015 * K_STRETCH * LIFT(f))
    rot("head", lambda f: look(f) + 11.0 * K_BODY * STRUG(f) * u1(f))
    rot("spine", lambda f: -6.0 * K_BODY * STRUG(f) * u1(f - 2))
    rot("hip", lambda f: 4.0 * K_BODY * STRUG(f) * u1(f - 4))
    # hai chân trước (foot_L, paw_F) quẫy NHẸ (2026-11-27: biên độ lớn làm lộ mesh cắt); cục nhô bên phải vẫn vẫy
    rot("foot_L", lambda f: 5 * STRUG(f) * sw(f, 6.0, 2.0))
    rot("paw_F", lambda f: 7 * STRUG(f) * sw(f, 6.0, 5.0))
    rot("bump_R", lambda f: 28 * STRUG(f) * sw(f, 5.0, -1.0))
    # tai: vểnh khi thấy kẹp, cụp khi bị gắp, phẩy khi giãy (đốt sau trễ cùng nhịp)
    ear = lambda f, s, ph: perk(f) * s + 10 * STRUG(f) * sw(f, 7.0, ph)
    rot("ear_L1", lambda f: ear(f, 1, 0.5)); rot("ear_L2", lambda f: 0.5 * ear(f - 2, 1, 0.5) * 1.3)
    rot("ear_R1", lambda f: ear(f, -1, 4.0)); rot("ear_R2", lambda f: 0.5 * ear(f - 2, -1, 4.0) * 1.3)
    # mặt: chớp (scaleX = dọc mắt), mắt / miệng nhún khi giãy
    # mở mắt lại (2026-11-27: "từ F138 hồi về 140 cho mèo mở mắt"): keo (nheo > <) giữ tới F137 (scale stepped), F138 đổi sang nam với mắt gần nhắm 0.15,
    # F139 0.55, F140 mở hẳn 1.0
    for e in ("eye_L", "eye_R"):
        keys = reduce_keys([samples(lambda f: blink_k(f) * (1 + 0.08 * STRUG(f) * sw(f, 7.0, 1.0)), EYE_OPEN - 1),
                            samples(lambda f: 1.0, EYE_OPEN - 1)], ["x", "y"], 0.003, False)
        keys[-1]["curve"] = "stepped"
        keys += [{"time": K.ktime(EYE_OPEN / FPS, FPS), "x": 0.15, "y": 1.0},
                 {"time": K.ktime((EYE_OPEN + 1) / FPS, FPS), "x": 0.55, "y": 1.0},
                 {"time": K.ktime((EYE_OPEN + 2) / FPS, FPS), "x": 1.0, "y": 1.0},
                 {"time": K.ktime(N / FPS, FPS), "x": 1.0, "y": 1.0}]
        B.setdefault(e, {})["scale"] = keys
    scl("mouth", lambda f: 1 + 0.30 * STRUG(f) * (0.5 + 0.5 * sw(f, 7.0, 0.5)), lambda f: 1 - 0.10 * STRUG(f) * (0.5 + 0.5 * sw(f, 7.0, 0.5)))
    # đổi mặt: nam (mở mắt, idle) -> keo (nheo > < khi bị gắp) -> nam (F138, mở mắt lại sau khi rơi xuống)
    T = K.tfloor
    slots = {s: {"attachment": [{"time": 0, "name": s + "_nam"}, {"time": T(T0 + 6), "name": s + "_keo"},
                                        {"time": T(EYE_OPEN), "name": s + "_nam"}]}
             for s in ("eye_L", "eye_R", "mouth")}
    slots = {("mouth" if s == "mouth" else s): v for s, v in slots.items()}
    return {"bones": B, "slots": slots}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "meo.json")
    ed = K.user_edits(path, "grab")
    print("sổ sửa tay:", ed.get("keyposes"), "| người dùng sửa sau Claude:", ed.get("user_since_claude"))
    sk = K.load(path)
    anim = build(path)
    K.write_anim(path, "grab", anim, "Claude gen grab (mèo bị gắp)", skel=sk)
    import urllib.request
    rel = os.path.relpath(os.path.abspath(path), ROOT).replace(os.sep, "/")
    try:
        urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8781/api/spine/anim", json.dumps(
            {"json": rel, "op": "meta", "name": "grab", "loop": True, "desc": "LOOP: mèo idle -> máy gắp hạ xuống, khép càng, nhấc lên, mèo giãy, càng mở thả mèo rơi, máy bay lên cao (F cuối = F0)"}).encode(),
            {"Content-Type": "application/json"}), timeout=3).read()
    except Exception as e:
        print("(không đặt được cờ loop=true:", e, ")")
    nk = sum(len(v) for b in anim["bones"].values() for v in b.values())
    print("grab: %dF một lần, %d xương, %d key" % (N, len(anim["bones"]), nk))


if __name__ == "__main__":
    main()
