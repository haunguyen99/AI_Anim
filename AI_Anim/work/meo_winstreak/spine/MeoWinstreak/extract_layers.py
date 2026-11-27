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
    # NGOẠI LỆ Layer 1548 (thân máy gắp): mask của nó khoét theo hình đầu mèo (hoạ sĩ trick để mèo thò ra trước). Nướng mask thì thân máy bị
    # móp khi mèo cử động, KHÔNG nướng thì mèo bị mép kẹp cắt lẹm -> dùng pixel gốc không mask và đặt thân máy DƯỚI mèo (góp ý 2026-11-27)
    if l.name.strip() == "Layer 1548":
        im = l.topil()
    elif l.has_clip_layers() or l.has_mask():
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
    # cat_head (2026-11-27, người dùng đề xuất "tách mèo thành 2: đầu ở trên, thân ở dưới layer gắp"): cat_body giữ NGUYÊN (cả con mèo, nằm dưới thân máy
    # như PSD). cat_head = CÙNG ảnh, CÙNG kích thước, alpha = mèo TRỪ vùng PSD cho thân máy che mèo (thân máy gốc ∩ mèo ngoài chỗ khoét mask, = vai phải,
    # ~18k px; cắt SẮC theo đúng mép kẹp, nới 1-2 px, không làm mờ: mờ 24 px nhìn như vệt nhoè), đặt TRÊN thân máy: đầu + tai + vai trái không bao giờ bị
    # mép kẹp cắt. Mesh của cat_head = BẢN SAO mesh cat_body (cùng đỉnh / weight / uv) nên hai mảnh biến dạng giống hệt từng điểm. Nửa phải mờ dần ở đáy
    # (y 3955 -> 4015) để không đè càng / chốt phải (nằm trên mèo trong PSD). Vì mép cắt là bản sao mép kẹp ở tư thế gốc, mèo lắc lệch quá vài px so với
    # máy gắp thì thấy bậc: build_grab.py giảm biên độ lắc thân / đầu (K_BODY) cho khớp.
    import numpy as np, cv2
    cbb = info["cat_body"]["bbox"]; cb2 = info["claw_body"]["bbox"]
    Hh, Ww = p.size[1], p.size[0]
    mk = [x for x in p.descendants() if x.name.strip() == "Layer 1548"][0].mask
    mb = mk.bbox
    hole = np.zeros((Hh, Ww), np.float32)
    hole[mb[1]:mb[3], mb[0]:mb[2]] = 1.0 - np.asarray(mk.topil()).astype(np.float32) / 255.0      # 1 = thân máy bị ẩn = mèo lộ ra
    claw = np.zeros((Hh, Ww), np.float32)
    ca = np.asarray(Image.open(os.path.join(IMG, "claw_body.png")).convert("RGBA"))[..., 3].astype(np.float32) / 255.0
    claw[cb2[1]:cb2[1] + ca.shape[0], cb2[0]:cb2[0] + ca.shape[1]] = ca
    covered = (claw * (1.0 - hole) > 0.3).astype(np.uint8)          # vùng thân máy che mèo trong PSD
    covered = cv2.dilate(covered, np.ones((3, 3), np.uint8))
    covered = cv2.GaussianBlur(covered.astype(np.float32), (0, 0), 0.8)
    cat = np.asarray(Image.open(os.path.join(IMG, "cat_body.png")).convert("RGBA")).copy()
    hh, ww = cat.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32); gx, gy = xx + cbb[0], yy + cbb[1]
    ss_ = lambda t: t * t * (3 - 2 * t)
    fy = 1.0 - ss_(np.clip((gy - 3955.0) / 60.0, 0, 1)) * ss_(np.clip((gx - 700.0) / 250.0, 0, 1))
    # cắt thêm theo hình càng phải + chốt phải (nằm TRÊN mèo trong PSD): không cắt thì cat_head (trên thân máy) đè lên mép chốt thành vệt cam
    over = np.zeros((Hh, Ww), np.float32)
    for nm_ in ("claw_arm_R", "claw_knob_R"):
        bb_ = info[nm_]["bbox"]
        al_ = np.asarray(Image.open(os.path.join(IMG, nm_ + ".png")).convert("RGBA"))[..., 3].astype(np.float32) / 255.0
        over[bb_[1]:bb_[1] + al_.shape[0], bb_[0]:bb_[0] + al_.shape[1]] = np.maximum(over[bb_[1]:bb_[1] + al_.shape[0], bb_[0]:bb_[0] + al_.shape[1]], al_)
    over = cv2.GaussianBlur(cv2.dilate((over > 0.3).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=2).astype(np.float32), (0, 0), 0.8)
    keep = (1.0 - np.clip(covered[cbb[1]:cbb[1] + hh, cbb[0]:cbb[0] + ww], 0, 1)) * (1.0 - np.clip(over[cbb[1]:cbb[1] + hh, cbb[0]:cbb[0] + ww], 0, 1)) * fy
    cat[..., 3] = (cat[..., 3].astype(np.float32) * keep).astype(np.uint8)
    Image.fromarray(cat).save(os.path.join(IMG, "cat_head.png"))
    info["cat_head"] = dict(info["cat_body"], psd="meo nam/Layer 0 trừ vùng thân máy che (cùng kích thước cat_body)")
    print(f"{'cat_head':18s} {info['cat_head']['bbox']}  (mèo trừ vùng thân máy che, cắt sắc; đặt trên thân máy)  covered px={int((covered > 0.5).sum())}")
    json.dump({"canvas": list(p.size), "layers": info, "order_bottom_to_top": [NAMES.get(n, n) for n, _ in order]},
              open(os.path.join(HERE, "layers.json"), "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
