"""Rig Spine cho mascot mua hàng (muahang.json do build_muahang.py xuất): mỗi layer = region gắn một xương (chưa dùng mesh / weight).
Chạy: .venv/Scripts/python.exe -I work/test/spine/MuaHang/build_rig.py [out.json]   (dựng lại sẽ đè sửa tay trên Spine Live)
Cây xương: root > fx_shadow / streak_1-4 / ghost_wheel_1-2 / star_1-5 / ctrl_cart
  ctrl_cart (ctrl xe: thân xe + lưới trước + tay đẩy nằm trên chính nó) > wheel_1-4, coins_L / coins_R, item_bst2 / 3 / 4,
  mascot (thân mèo) > glow, face > eye_L / eye_R / mouth / nose / whisker_L / whisker_R, ear_L / ear_R, paw_L / paw_R, foot_L / foot_R.
Toạ độ ảnh (px, py; y xuống) -> Spine (px - W/2, H - py)."""
import json, math, os, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
L = json.load(open(f"{HERE}/layers.json", encoding="utf-8"))
W, H = L["canvas"]
OX, OY = W / 2.0, float(H)
LAY = {r["name"]: r for r in L["layers"]}
ORDER = [r["name"] for r in L["layers"]]
S = lambda px, py: (px - OX, OY - py)

BONES, BW = [], {}


def bone(name, parent, cx, cy, length=40, ang=0.0):
    wx, wy = S(cx, cy)
    if parent is None:
        x, y, rot = wx, wy, ang
    else:
        pwx, pwy, pa = BW[parent]
        x, y, rot = wx - pwx, wy - pwy, ang - pa          # mọi xương cùng hướng thế giới 0° nên local = hiệu vị trí
    BW[name] = (wx, wy, ang)
    b = {"name": name, "length": length, "x": round(x, 3), "y": round(y, 3), "rotation": round(rot, 3)}
    if parent: b["parent"] = parent
    BONES.append(b)


def center(n):
    r = LAY[n]; return r["x"] + r["w"] / 2.0, r["y"] + r["h"] / 2.0


def build():
    bone("root", None, 770, 1266, 30)
    bone("fx_shadow", "root", 650, 620, 0)                        # bóng multiply của mascot (đứng yên theo root)
    for i, n in enumerate(["bong", "bong_2", "bong_3", "bong_4"], 1):
        bone(f"streak_{i}", "root", *center(n), 60)                # vệt tốc độ
    for i, n in enumerate(["banhxe1", "banhxe2"], 1):
        bone(f"ghost_wheel_{i}", "root", *center(n), 40)           # bánh mờ bay phía sau
    for i, n in enumerate(["star", "star_2", "star_3", "star_4", "star_5"], 1):
        bone(f"star_{i}", "root", *center(n), 25)
    bone("ctrl_cart", "root", 640, 1000, 0)                       # ctrl xe: dời + phồng (nảy cả xe + mèo + hàng)
    for i, n in enumerate(["banhxe_Layer_1", "banhxe_Layer_2", "banhxe_Layer_3", "banhxe_Layer_4"], 1):
        bone(f"wheel_{i}", "ctrl_cart", *center(n), 40)            # bánh xe: xoay quanh tâm
    bone("coins_L", "ctrl_cart", 430, 880, 50)
    bone("coins_R", "ctrl_cart", 720, 790, 50)
    bone("item_bst2", "ctrl_cart", 629, 440, 70)                   # đồ trong xe: nghiêng quanh đáy
    bone("item_bst3", "ctrl_cart", 899, 580, 70)
    bone("item_bst4", "ctrl_cart", 798, 840, 70)
    bone("mascot", "ctrl_cart", 430, 790, 80)                      # thân mèo: nhún / nghiêng quanh đáy thân
    bone("glow", "mascot", 450, 526, 40)
    bone("face", "mascot", 340, 370, 40)
    bone("eye_L", "face", 271, 320, 20)
    bone("eye_R", "face", 401, 361, 20)
    bone("mouth", "face", 317, 380, 20)
    bone("nose", "face", 325, 365, 15)
    bone("whisker_L", "face", 225, 345, 40)
    bone("whisker_R", "face", 460, 415, 40)
    bone("ear_L", "mascot", 320, 290, 70)
    bone("ear_R", "mascot", 520, 340, 70)
    bone("paw_L", "mascot", 200, 470, 70)
    bone("paw_R", "mascot", 520, 455, 70)
    bone("foot_L", "mascot", 331, 705, 60)
    bone("foot_R", "mascot", 544, 710, 60)


SLOT_BONE = {"bong": "streak_1", "bong_2": "streak_2", "bong_3": "streak_3", "bong_4": "streak_4",
             "banhxe_Layer_1": "wheel_1", "banhxe_Layer_2": "wheel_2", "banhxe_Layer_3": "wheel_3", "banhxe_Layer_4": "wheel_4",
             "xeday_bong2": "ctrl_cart", "xe_day1": "ctrl_cart", "xeday_bong1": "ctrl_cart", "xeday2": "ctrl_cart",
             "gold": "coins_R", "gold_2": "coins_R", "gold_3": "coins_R", "gold_4": "coins_R", "gold2": "coins_L", "gold1": "coins_L",
             "bst3": "item_bst3", "bst4": "item_bst4", "bst2": "item_bst2", "shadow_mascot": "fx_shadow", "glow_mascot": "glow",
             "banhxe1": "ghost_wheel_1", "banhxe2": "ghost_wheel_2",
             "star": "star_1", "star_2": "star_2", "star_3": "star_3", "star_4": "star_4", "star_5": "star_5",
             "tay2": "paw_L", "tay1": "paw_R", "chan1": "foot_R", "chan2": "foot_L", "tai1": "ear_L", "tai2": "ear_R",
             "body": "mascot", "mui": "nose", "mieng": "mouth", "mat1": "eye_L", "mat2": "eye_R", "rau2": "whisker_L", "rau1": "whisker_R"}


def region(name, b):
    cx, cy = center(name); wx, wy = S(cx, cy)
    bx, by, _ = BW[b]
    r = LAY[name]
    return {"type": "region", "x": round(wx - bx, 2), "y": round(wy - by, 2), "rotation": 0, "width": r["w"], "height": r["h"]}


def build_all():
    build()
    prev_slots = {s["name"]: s for s in json.load(open(f"{HERE}/muahang.json", encoding="utf-8"))["slots"]}
    slots, atts = [], {}
    for n in ORDER:
        b = SLOT_BONE[n]
        s = {"name": n, "bone": b, "attachment": n}
        if "blend" in prev_slots.get(n, {}): s["blend"] = prev_slots[n]["blend"]
        slots.append(s); atts[n] = {n: region(n, b)}
    sk = {"skeleton": {"spine": "4.2.43", "fps": 30, "x": -W / 2, "y": 0, "width": W, "height": H, "images": "./images/"},
          "bones": BONES, "slots": slots, "skins": [{"name": "default", "attachments": atts}], "animations": {}}
    return sk


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else f"{HERE}/muahang.json"
    prev = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else None
    sk = build_all()
    if prev and prev.get("animations"):
        sk["animations"] = {k: v for k, v in prev["animations"].items() if k != "setup"}
    try:
        import spine_live_cmd
        spine_live_cmd.claude_backup(out, "Claude dựng rig mascot mua hàng")
    except Exception as e:
        print("(không ghi được backup Spine Live:", e, ")")
    json.dump(sk, open(out, "w", encoding="utf-8"), indent=1)
    miss = [n for n in ORDER if n not in SLOT_BONE]
    print("Đã ghi", out, "|", len(sk["bones"]), "xương,", len(sk["slots"]), "slot | slot chưa gán xương:", miss)
    sys.path.insert(0, HERE)
    import patch_arms_ears
    patch_arms_ears.apply(out)                                   # 2 tay + 2 tai = chuỗi 2 xương + mesh weight
