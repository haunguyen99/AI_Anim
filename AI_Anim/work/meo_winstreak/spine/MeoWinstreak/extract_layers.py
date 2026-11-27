"""Tách PSD meo_winstreak_anim.psd -> images/*.png (mỗi layer một PNG đúng tên attachment) + layers.json (bbox PSD).
Chạy: .venv/Scripts/python.exe -I work/meo_winstreak/spine/MeoWinstreak/extract_layers.py
Luật: bỏ nhóm ẩn 'bỏ' và smart object ẩn 'may gap' (ảnh tham chiếu cả máy gắp). Layer có lớp clip -> nướng bằng layer.composite(force=True)
(cắt theo bbox của layer gốc). Thứ tự duyệt của psd-tools = DƯỚI -> TRÊN (đã kiểm bằng cách ghép lại so với p.composite()).
"""
import warnings, json, os, sys
warnings.filterwarnings("ignore")
import numpy as np
from psd_tools import PSDImage
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PSD = os.path.join(HERE, "src", "meo_winstreak_anim.psd")
IMG = os.path.join(HERE, "images")
os.makedirs(IMG, exist_ok=True)

# (đường dẫn trong PSD) -> tên attachment
NAMES = {
    "Layer 1547": "claw_arm_L",
    "Brightness/Contrast 1": "claw_knob_L",
    "meo nam/Layer 12": "cat_foot_L",
    "meo nam/Layer 0": "cat_body",
    "meo nam/Layer 15": "cat_belly",
    "meo nam/Layer 18": "eye_L_nam",
    "meo nam/Layer 17": "eye_R_nam",
    "meo nam/Layer 19": "mouth_nam",
    "meo nam/Layer 3": "cat_ear_R",
    "meo keo/Shape 1 copy": "eye_L_keo",
    "meo keo/Shape 1": "eye_R_keo",
    "meo keo/Shape 2": "mouth_keo",
    "Layer 1559": "claw_arm_R",
    "Brightness/Contrast 1 copy": "claw_knob_R",
    "Layer 1548": "claw_body",
}

def bake(l):
    # layer có lớp clip HOẶC layer mask (claw_body có mask khoét chỗ tai mèo) -> composite(force) giữ đúng bbox + áp mask
    if l.has_clip_layers() or l.has_mask():
        im = l.composite(viewport=l.bbox, force=True)
    else:
        im = l.topil()
    return im.convert("RGBA")

def main():
    p = PSDImage.open(PSD)
    order = []   # dưới -> trên
    def walk(g, path=""):
        for l in g:
            n = path + l.name.strip()
            if l.is_group():
                if not l.visible: continue
                walk(l, n + "/"); continue
            if not l.visible or l.clipping_layer or l.bbox == (0, 0, 0, 0): continue
            order.append((n, l))
    walk(p)
    info = {}
    for n, l in order:
        if n not in NAMES:
            print("BỎ (không đặt tên):", n); continue
        im = bake(l)
        nm = NAMES[n]
        im.save(os.path.join(IMG, nm + ".png"))
        info[nm] = {"psd": n, "bbox": list(l.bbox), "blend": l.blend_mode.name, "opacity": round(l.opacity / 255, 4), "size": list(im.size)}
        print(f"{nm:18s} {str(l.bbox):28s} {l.blend_mode.name:9s} {l.opacity/255:.2f}  <- {n}")
    json.dump({"canvas": list(p.size), "layers": info, "order_bottom_to_top": [NAMES.get(n, n) for n, _ in order]},
              open(os.path.join(HERE, "layers.json"), "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
