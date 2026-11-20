"""layers.json + images/*.png -> PeaceGirl_layers.psd (mỗi layer một lớp, đúng vị trí ảnh gốc, z thấp ở dưới)."""
import json, sys
from PIL import Image
from psd_tools import PSDImage
D = sys.argv[1]
L = json.load(open(f"{D}/layers.json", encoding="utf-8"))
W, H = L["canvas"]
psd = PSDImage.new("RGB", (W, H))
for m in sorted(L["layers"], key=lambda m: m["z"]):
    im = Image.open(f"{D}/{m['file']}").convert("RGBA")
    layer = psd.create_pixel_layer(im, name=m["name"], top=m["y"], left=m["x"])
psd.save(f"{D}/PeaceGirl_layers.psd")
print("ghi", f"{D}/PeaceGirl_layers.psd", len(psd), "layer")
