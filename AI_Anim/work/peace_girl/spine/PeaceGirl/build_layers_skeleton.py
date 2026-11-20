"""layers.json -> peacegirl.json: chỉ xương root + slot theo thứ tự z + region đặt đúng vị trí ảnh gốc (chưa rig).
Gốc root = giữa đáy ảnh (368, 1075)."""
import json, sys
D = sys.argv[1]
L = json.load(open(f"{D}/layers.json", encoding="utf-8"))
W, H = L["canvas"]
OX, OY = W / 2, H
slots, atts = [], {}
for m in sorted(L["layers"], key=lambda m: m["z"]):
    cx, cy = m["x"] + m["w"] / 2, m["y"] + m["h"] / 2
    slots.append({"name": m["name"], "bone": "root", "attachment": m["name"]})
    atts[m["name"]] = {m["name"]: {"x": round(cx - OX, 2), "y": round(OY - cy, 2), "width": m["w"], "height": m["h"]}}
sk = {"skeleton": {"spine": "4.2.43", "fps": 30, "x": -W / 2, "y": 0, "width": W, "height": H, "images": "./images/"},
      "bones": [{"name": "root"}], "slots": slots, "skins": [{"name": "default", "attachments": atts}], "animations": {"setup": {"bones": {"root": {"translate": [{"x": 0, "y": 0}]}}}}}
json.dump(sk, open(f"{D}/peacegirl.json", "w", encoding="utf-8"), indent=1)
print("slots:", len(slots))
