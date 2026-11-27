"""PSD mascot mua hàng (xe đẩy) -> images/<layer>.png + layers.json + muahang.json (chỉ xương root, mỗi layer một slot, chưa rig).
Chạy: .venv/Scripts/python.exe -I work/test/spine/MuaHang/build_muahang.py work/test/spine/MuaHang
Layer ẩn bị bỏ; độ mờ layer được nướng vào PNG; Multiply -> blend multiply của slot. Gốc root = giữa đáy canvas (y lên)."""
import json, os, re, sys
from psd_tools import PSDImage

D = sys.argv[1]
psd = PSDImage.open(f"{D}/src/mascot_muahang_anim.psd")
W, H = psd.size
OX, OY = W / 2.0, float(H)
os.makedirs(f"{D}/images", exist_ok=True)
for f in os.listdir(f"{D}/images"):
    if f.endswith(".png"):
        os.remove(f"{D}/images/{f}")

used, rows, skipped = {}, [], []


def uname(base):
    base = re.sub(r"[^0-9A-Za-z_]+", "_", base).strip("_") or "layer"
    n = used.get(base, 0) + 1
    used[base] = n
    return base if n == 1 else f"{base}_{n}"


def walk(layers, prefix=""):
    for l in layers:
        if l.is_group():
            walk(l, prefix + (l.name + "_" if l.name != "2_anim" else ""))
            continue
        if not l.is_visible():
            skipped.append(l.name)
            continue
        im = l.composite()
        if im is None:
            skipped.append(l.name)
            continue
        name = uname(prefix + l.name)
        im.convert("RGBA").save(f"{D}/images/{name}.png")
        x0, y0, x1, y1 = l.bbox
        rows.append({"name": name, "src": l.name, "x": x0, "y": y0, "w": im.width, "h": im.height,
                     "blend": "multiply" if "MULTIPLY" in str(l.blend_mode) else "normal", "opacity": l.opacity,
                     "smart": l.kind == "smartobject"})


walk(psd)
slots, atts = [], {}
for r in rows:
    cx, cy = r["x"] + r["w"] / 2.0, r["y"] + r["h"] / 2.0
    s = {"name": r["name"], "bone": "root", "attachment": r["name"]}
    if r["blend"] != "normal":
        s["blend"] = r["blend"]
    slots.append(s)
    atts[r["name"]] = {r["name"]: {"x": round(cx - OX, 2), "y": round(OY - cy, 2), "width": r["w"], "height": r["h"]}}
sk = {"skeleton": {"spine": "4.2.43", "fps": 30, "x": -W / 2, "y": 0, "width": W, "height": H, "images": "./images/"},
      "bones": [{"name": "root"}], "slots": slots, "skins": [{"name": "default", "attachments": atts}],
      "animations": {"setup": {"bones": {"root": {"translate": [{"x": 0, "y": 0}]}}}}}
json.dump(sk, open(f"{D}/muahang.json", "w", encoding="utf-8"), indent=1)
json.dump({"canvas": [W, H], "layers": rows, "skipped": skipped}, open(f"{D}/layers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"canvas {W}x{H}: {len(rows)} slot (dưới -> trên), bỏ {len(skipped)} layer ẩn: {skipped}")
