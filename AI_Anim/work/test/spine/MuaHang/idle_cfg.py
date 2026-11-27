"""Idle mascot mua hàng (mô tả 2026-11-27): nhấp NHẸ NHÀNG lên xuống, tay / tai / miệng của mèo overlap theo thân. Loop 60F (2 s), 1 nhịp nhấp / loop.
Chạy: .venv/Scripts/python.exe -I work/test/spine/MuaHang/idle_cfg.py   (skill /skillidle, bộ máy tools/spine/idle_engine.py)

- ctrl_cart: cả xe nhấp lên xuống ~5 px (sin 1 nhịp); hàng hoá (coins_*, item_bst*) nhấp trễ pha sau xe; bánh xe nhún scale đồng nhịp (xe xuống thì bánh bẹt).
- mascot: nhấp trễ pha sau xe thêm ~3 px + nhún dọc nhẹ; face / glow theo.
- Overlap theo thân: tai, tay (2 đốt), râu xoay theo ĐỘ TRỄ chuyển động dọc của thân (vị trí thân - vị trí thân trễ k frame): thân đi lên thì đầu xương
  rũ xuống, đi xuống thì hất lên; đốt 2 trễ hơn đốt 1. Miệng scale dọc theo nhịp, trễ pha sau thân.
- Khói dưới xe đứng yên, chỉ co giãn ngang; sao nhấp nháy; glow thở.
Trục local: con của root xoay 90° (ctrl_cart, khói, sao, bánh mờ): X = DỌC (lên), Y = -X thế giới; con của ctrl_cart / mascot: local = thế giới."""
import math, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "tools", "spine"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import anim_kit as K
from anim_kit import FPS
from anim_params import Params

FOLDER = os.path.join(ROOT, "work", "test", "spine", "MuaHang")
PATH = os.environ.get("ANIM_KIT_PATH") or os.path.join(FOLDER, "muahang.json")
ANIM = "idle"

P = Params(os.path.dirname(PATH), "idle", "Idle", anim="idle", run=["idle_cfg.py"])
END = P.num("end", 60, 30, 120, 6, "Độ dài loop (frame, 60 = 2 s một nhịp nhấp)")
A_BOB = P.num("bob", 1.0, 0, 3, 0.1, "Xe nhấp lên xuống (x, 1 = 5 px)")
A_ITEM = P.num("items", 1.0, 0, 3, 0.1, "Hàng hoá nhấp trễ sau xe (x)")
A_CAT = P.num("cat", 1.0, 0, 3, 0.1, "Mèo nhấp thêm + nhún dọc (x, 1 = 3 px + 1,8%)")
A_OVL = P.num("overlap", 1.0, 0, 3, 0.1, "Tai + tay + râu overlap theo thân (x)")
LAG = P.num("lag", 4, 1, 12, 1, "Overlap: độ trễ đốt 1 (frame; đốt 2 trễ thêm 3F)")
A_MOUTH = P.num("mouth", 1.0, 0, 3, 0.1, "Miệng scale lên / xuống (x, 1 = 10%)")
A_WHEEL = P.num("wheel_squash", 0.03, 0, 0.2, 0.01, "Bánh xe nhún theo nhịp xe: scale dọc (0,03 = 3%)")
A_STREAK = P.num("streak", 1.0, 0, 5, 0.1, "Khói dưới xe: co giãn trái / phải (x, 1 = 3%)")
if not os.environ.get("ANIM_KIT_PATH"):
    P.save()

T = END / FPS
TAU = 2 * math.pi
sn = lambda k, ph=0.0: (lambda t: math.sin(TAU * k * t / T + ph))        # k nhịp nguyên mỗi loop -> khép loop

# ---- chuyển động dọc (px, +y = lên)
CART_Y = lambda t: A_BOB * 5.0 * sn(1, 0.0)(t)
MAS_Y = lambda t: A_CAT * 3.0 * sn(1, -0.55)(t)                          # mèo trễ pha sau xe (thân mềm)
MAS_S = lambda t: A_CAT * 0.018 * sn(1, -0.55 + math.pi / 2)(t)         # nhún: dọc giãn khi đi lên, ngang co lại
BODY_Y = lambda t: CART_Y(t) + MAS_Y(t)

# chiều dài từng đốt ở setup
_skel = K.load(PATH)
_rig = K.Rig(_skel)
LEN = {b: _rig.B[b]["length"] for b in ("ear_L", "ear_L2", "ear_R", "ear_R2", "paw_L", "paw_L2", "paw_R", "paw_R2", "whisker_L", "whisker_R") if b in _rig.B}


def ovl(b, nf, gain, sgn):
    """xoay theo độ trễ chuyển động dọc của thân: d = vị trí thân - vị trí thân trễ nf frame (> 0 khi thân đang đi lên).
    sgn = chiều RŨ XUỐNG khi thân đi lên: tai trái / tai phải / tay trái / râu trái = +1 (ccw), tay phải / râu phải = -1."""
    ln = LEN[b]
    return lambda t: A_OVL * gain * sgn * math.degrees((BODY_Y(t) - BODY_Y(t - nf / FPS)) / ln)


OWN = {
    "ear_L": ovl("ear_L", LAG, 1.0, +1), "ear_L2": ovl("ear_L2", LAG + 3, 1.2, +1),
    "ear_R": ovl("ear_R", LAG, 1.0, +1), "ear_R2": ovl("ear_R2", LAG + 3, 1.2, +1),
    "paw_L": ovl("paw_L", LAG, 0.9, +1), "paw_L2": ovl("paw_L2", LAG + 3, 1.1, +1),
    "paw_R": ovl("paw_R", LAG, 0.9, -1), "paw_R2": ovl("paw_R2", LAG + 3, 1.1, -1),
    "whisker_L": ovl("whisker_L", LAG + 2, 0.8, +1), "whisker_R": ovl("whisker_R", LAG + 2, 0.8, -1),
    # hàng hoá nghiêng nhẹ quanh đáy, lệch pha giữa các món
    "item_bst2": lambda t: A_ITEM * 0.9 * sn(1, 0.6)(t),
    "item_bst3": lambda t: A_ITEM * 0.8 * sn(1, 1.2)(t),
    "item_bst4": lambda t: A_ITEM * 0.6 * sn(1, 1.8)(t),
    "star_1": lambda t: 12 * sn(1, 0.0)(t), "star_2": lambda t: 12 * sn(1, 1.3)(t), "star_3": lambda t: 12 * sn(1, 2.1)(t),
    "star_4": lambda t: 12 * sn(1, 3.0)(t), "star_5": lambda t: 12 * sn(1, 4.2)(t),
}
INERTIA = {}
TRANSLATE = {
    "ctrl_cart": lambda t: (CART_Y(t), 0.0),                              # cha = root xoay 90°: local x = lên
    "mascot": lambda t: (0.0, MAS_Y(t)),
    "face": lambda t: (0.0, -0.25 * A_OVL * (BODY_Y(t) - BODY_Y(t - (LAG + 2) / FPS))),   # mặt trễ nhẹ sau thân
    "coins_L": lambda t: (0.0, A_ITEM * 1.5 * sn(1, -0.35)(t)),
    "coins_R": lambda t: (0.0, A_ITEM * 1.5 * sn(1, -0.55)(t)),
    "item_bst2": lambda t: (0.0, A_ITEM * 2.0 * sn(1, -0.45)(t)),
    "item_bst3": lambda t: (0.0, A_ITEM * 2.0 * sn(1, -0.70)(t)),
    "item_bst4": lambda t: (0.0, A_ITEM * 1.5 * sn(1, -0.90)(t)),
}
MOUTH_S = lambda t: A_MOUTH * 0.10 * sn(1, -1.2)(t)                       # miệng trễ pha sau thân
SCALE = {
    "mascot": lambda t: (1 - 0.7 * MAS_S(t), 1 + MAS_S(t)),
    "mouth": lambda t: (1 - 0.4 * MOUTH_S(t), 1 + MOUTH_S(t)),             # mở / khép: dọc giãn ra phía dưới gốc xương
    "glow": lambda t: (1 + 0.03 * sn(1, 0.0)(t), 1 + 0.03 * sn(1, 0.0)(t)),
    "streak_1": lambda t: (1 + 0.03 * A_STREAK * sn(1, 0.0)(t), 1.0),     # khói đứng yên, chỉ co giãn trái / phải
    "streak_2": lambda t: (1 + 0.03 * A_STREAK * sn(1, 1.6)(t), 1.0),
    "streak_3": lambda t: (1 + 0.03 * A_STREAK * sn(1, 3.1)(t), 1.0),
    "streak_4": lambda t: (1 + 0.03 * A_STREAK * sn(1, 4.6)(t), 1.0),
}
for _i, _s in enumerate((0.0, 1.3, 2.1, 3.0, 4.2), 1):
    SCALE[f"star_{_i}"] = (lambda ph: (lambda t: (lambda v: (v, v))(1 + 0.2 * sn(2, ph)(t))))(_s)
for _i, _b in enumerate(("wheel_1", "wheel_2", "wheel_3", "wheel_4", "ghost_wheel_1", "ghost_wheel_2")):
    # xe xuống -> bánh bẹt (dọc co, ngang giãn), xe lên -> bánh dài ra; lệch pha nhẹ giữa các bánh
    SCALE[_b] = (lambda ph: (lambda t: (1 - 0.5 * A_WHEEL * sn(1, ph)(t), 1 + A_WHEEL * sn(1, ph)(t))))(-0.15 * _i)
N_KEYS = 20
CHAINS = []
BLINK = None


if __name__ == "__main__":
    from idle_engine import build_idle
    anim = build_idle(sys.modules[__name__], write=False)
    K.write_anim(PATH, ANIM, anim, "Claude gen idle")
    print(f"{ANIM}: {END} frame, {len(anim['bones'])} xương có key -> {PATH}")
