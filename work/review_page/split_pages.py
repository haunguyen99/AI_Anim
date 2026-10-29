"""Build one review page per animation from the master work/review_page/index.html (all CLIPS).
python work/review_page/split_pages.py  -> work/review_page/pages/<key>/index.html (clips/... paths stay relative)"""
import os, re
ROOT = os.path.dirname(os.path.abspath(__file__))
import json
REG = json.load(open(os.path.join(ROOT, "..", "clips.json"), encoding="utf8"))   # sổ clip: tools/clip_registry.py
PAGES = {c["review"]["key"]: (c["review"]["clip"], c["review"]["title"], c["review"]["crumb"], c["review"]["name"])
         for c in REG["clips"] if c.get("review")}   # key: (clip, page title, crumb text, project name)
GAYGOR_PARTS = "<option>Vai</option><option>Tay phải · khiên</option><option>Tay trái</option><option>Chùy</option><option>Chân</option>"
SDR06_PARTS = ("<option>Thân · vai</option><option>Tay phải · cán súng</option>"
               "<option>Tay trái · ốp nòng</option><option>Súng</option><option>Trống đạn</option><option>Chân</option>")
PRESET_PARTS = {"sdr06": SDR06_PARTS, "sdr_attack": "<option>Vai</option><option>Tay phải · dao</option><option>Tay trái · ngắm</option>"
                "<option>Dao bay · cắm bia</option><option>Chân</option>"}
PARTS = {}   # key -> danh sách bộ phận của khung ghi note: tên preset (sdr06, sdr_attack) hoặc danh sách chuỗi trong clips.json; trống = bộ của Gaygor
for c in REG["clips"]:
    pt = (c.get("review") or {}).get("parts")
    if pt:
        PARTS[c["review"]["key"]] = PRESET_PARTS[pt] if isinstance(pt, str) else "".join(f"<option>{x}</option>" for x in pt)
src = open(os.path.join(ROOT, "index.html"), encoding="utf8").read()
m = re.search(r"const CLIPS = \[\n(.*?)\n\];", src, re.S)
entries = re.findall(r"  \{ clip: .*?\},?(?=\n  \{ clip:|\Z)", m.group(1), re.S)
for key, (clip, title, crumb, name) in PAGES.items():
    mine = [e.rstrip(",") for e in entries if e.startswith(f'  {{ clip: "{clip}"')]
    if not mine:
        print(key, "chưa có version nào: bỏ qua"); continue
    s = src[:m.start(1)] + ",\n".join(mine) + "," + src[m.end(1):]
    s = s.replace("<title>Review Lab</title>", f"<title>{title}</title>", 1)
    s = s.replace('<small>Boss Gaygor · project</small><select class="proj" id="proj" aria-label="Chọn project"></select>',
                  f'<small>{crumb}</small><select class="proj" id="proj" aria-label="Chọn project" hidden></select>'
                  f'<span class="proj">{name}</span>', 1)
    if key in PARTS:      # body-part list of the note composer follows the character/props of this animation
        s = s.replace(GAYGOR_PARTS, PARTS[key], 1)
    out = os.path.join(ROOT, "pages", key); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w", encoding="utf8").write(s)
    print(key, len(mine), "versions:", [re.search(r'version: "(.*?)"', e).group(1) for e in mine])
