"""Tách PSD Ruong_battle_pass_anim.psd -> images/*.png (mỗi layer một PNG đúng tên attachment) + layers.json (bbox PSD).
Chạy: .venv/Scripts/python.exe -I work/battle_pass/spine/RuongBattlePass/extract_layers.py
PSD là bảng THAM CHIẾU 5 trạng thái xếp chồng (không cửa / cửa đóng / đóng + vòng / mở vừa / mở hẳn), thứ tự psd-tools = DƯỚI -> TRÊN.
Layer clip + multiply (bóng cam / tím) KHÔNG dùng blend multiply của runtime (PNG không PMA làm sáng vùng bóng, bài MeoWinstreak): nướng
multiply vào ảnh gốc (chỉ trong alpha của ảnh) = đúng công thức PSD  Cb*(1-a) + Cb*Cs*a.
  chest_body = Layer 6 + Layer 21 (clip)
  cavity     = Layer 9 + Layer 21 copy (clip) + bóng 17 / 16 (clip vào cavity) + bóng trong Layer 15 (multiply, không clip)
  in_*       = xu trong rương: ảnh gốc + bóng 17/16 (nếu có) + Layer 15
  fg_*       = xu ngoài rương: ảnh gốc + bóng clip riêng (18 / 19 / 20)
Toạ độ trong layers.json = canvas PSD (y xuống).
"""
import warnings, json, os, sys
warnings.filterwarnings("ignore")
import numpy as np
from psd_tools import PSDImage
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "images"); os.makedirs(IMG, exist_ok=True)
p = PSDImage.open(os.path.join(HERE, "src", "Ruong_battle_pass_anim.psd"))
W, H = p.size
RAW = {}
def walk(g, path=""):
    for l in g:
        n = path + l.name.strip()
        if l.is_group(): walk(l, n + "/"); continue
        RAW[n] = l
walk(p)

def canvas(l):
    """ảnh layer đặt vào canvas PSD đầy đủ, float 0..1 RGBA (straight alpha)"""
    im = l.topil().convert("RGBA"); c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); c.paste(im, (l.bbox[0], l.bbox[1]))
    return np.asarray(c, np.float32) / 255.0

def mult(base, shade, op):
    """multiply `shade` (canvas RGBA float, opacity op) lên base (canvas RGBA float), chỉ trong alpha của base"""
    a = shade[..., 3:4] * op
    out = base.copy()
    out[..., :3] = base[..., :3] * (1 - a) + base[..., :3] * shade[..., :3] * a
    return out

R = lambda n: RAW["rương/" + n]
def L(n): l = R(n); return canvas(l), l.opacity / 255.0

S21, o21 = L("Layer 21"); S21c, o21c = L("Layer 21 copy")
S17, o17 = L("Layer 17"); S16, o16 = L("Layer 16"); S15, o15 = L("Layer 15")
S18, o18 = L("Layer 18"); S19, o19 = L("Layer 19"); S20, o20 = L("Layer 20")

OUT = {}   # tên -> (canvas float RGBA, layer gốc)
def put(name, arr, l): OUT[name] = (arr, l)

body = canvas(R("Layer 6")); body = mult(body, S21, o21); put("chest_body", body, R("Layer 6"))
cav = canvas(R("Layer 9")); cav = mult(cav, S21c, o21c); cav = mult(cav, S17, o17); cav = mult(cav, S16, o16); cav = mult(cav, S15, o15)
put("cavity", cav, R("Layer 9"))
def interior(name, lname, *shades):
    a = canvas(R(lname))
    for s, o in shades: a = mult(a, s, o)
    put(name, a, R(lname))
interior("in_stack5", "Layer 13 copy 5", (S17, o17), (S15, o15))
interior("in_stack4", "Layer 13 copy 9", (S16, o16), (S15, o15))
for nm, ln in [("in_c1", "Layer 13"), ("in_c2", "Layer 13 copy"), ("in_c3", "Layer 13 copy 2"), ("in_c4", "Layer 13 copy 3"),
               ("in_tilt", "Layer 14"), ("in_stack3", "Layer 13 copy 8")]:
    interior(nm, ln, (S15, o15))
interior("fg_stack3", "Layer 13 copy 10", (S18, o18))
interior("fg_tilt1", "Layer 14 copy")
interior("fg_c1", "Layer 13 copy 4", (S19, o19))
interior("fg_c2", "Layer 13 copy 6")
interior("fg_c3", "Layer 13 copy 7", (S20, o20))
interior("fg_tilt2", "Layer 14 copy 3")
interior("fg_tilt3", "Layer 14 copy 2")
G = lambda g, n: RAW[g + "/" + n]
for nm, l in [("door_o", RAW["cửa mở hẳn/cửa mở hẳn"]), ("bolt_o1", RAW["cửa mở hẳn/Layer 22 copy 5"]), ("bolt_o2", RAW["cửa mở hẳn/Layer 22 copy 4"]),
              ("bolt_o3", RAW["cửa mở hẳn/Layer 22 copy 3"]), ("door_c", RAW["cửa đóng"]), ("dial", RAW["Layer 24"]),
              ("door_h", RAW["cửa mở vừa/Layer 23"]), ("bolt_h1", RAW["cửa mở vừa/Layer 22"]), ("bolt_h2", RAW["cửa mở vừa/Layer 22 copy"]),
              ("bolt_h3", RAW["cửa mở vừa/Layer 22 copy 2"]), ("ring", RAW["vong tron"])]:
    put(nm, canvas(l), l)

info = {}
for nm, (arr, l) in OUT.items():
    x0, y0, x1, y1 = l.bbox
    crop = arr[y0:y1, x0:x1]
    Image.fromarray(np.clip(crop * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA").save(os.path.join(IMG, nm + ".png"))
    info[nm] = {"psd": l.name.strip(), "bbox": [x0, y0, x1, y1], "size": [x1 - x0, y1 - y0]}
    print(f"{nm:10s} {str([x0, y0, x1, y1]):22s} <- {l.name.strip()}")
json.dump({"canvas": [W, H], "layers": info}, open(os.path.join(HERE, "layers.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
# kiểm: L15 có tràn ra ngoài alpha cavity không (phần đó bị mất khi nướng)
cav_a = canvas(R("Layer 9"))[..., 3] > 0.05
a15 = S15[..., 3] > 0.05
print("Layer 15 ngoài alpha cavity (px):", int((a15 & ~cav_a).sum()), "/", int(a15.sum()))
