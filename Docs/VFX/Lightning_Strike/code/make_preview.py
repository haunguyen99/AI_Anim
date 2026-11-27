"""Ghép Strike (đứng) + Impact (nằm đất, ép theo camera 3/4 40) thành Preview_sheet.png cho Review Lab."""
import numpy as np
from PIL import Image
T = "D:/Game_prj/VFX_LIb/Assets/VFX/Lightning_Strike/Textures/"
st = Image.open(T + "T_CFX_Lightning_Strike_4x4.png").convert("RGBA")
im = Image.open(T.replace("Lightning_Strike", "Lightning_Impact") + "T_CFX_Lightning_Impact_4x4.png").convert("RGBA")
bg = np.array([18, 20, 26], float)
out = Image.new("RGB", (16 * 256, 256))
for i in range(16):
    cx, cy = (i % 4), (i // 4)
    s = st.crop((cx * 320, cy * 512, cx * 320 + 320, cy * 512 + 512)).resize((160, 256), Image.LANCZOS)
    g = im.crop((cx * 256, cy * 256, cx * 256 + 256, cy * 256 + 256)).resize((160, 102), Image.LANCZOS)
    def lum(a):  # add blend: rgb * alpha
        a = np.array(a, float); return a[..., :3] * a[..., 3:] / 255
    cell = np.tile(bg, (256, 256, 1))
    cell[0:232, 48:208] += lum(s)[24:256]
    cell[190 - 51:190 + 51, 48:208] += lum(g)
    out.paste(Image.fromarray(np.clip(cell, 0, 255).astype("uint8")), (i * 256, 0))
out.save("D:/Game_prj/VFX_LIb/Docs/VFX/Lightning_Strike/Preview_sheet.png")
