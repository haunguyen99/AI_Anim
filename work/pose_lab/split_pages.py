"""One Pose Lab page per animation from the master work/pose_lab/index.html (all POSES = every version of every clip),
like work/review_page/split_pages.py (user 2026-10-22: "lưu chung với cả nhân vật của map 2 ... hoạt động như bên review
bằng video, nó cũng lưu lại các phiên bản"). Each page = its own artifact and db; models/... paths stay relative.
python work/pose_lab/split_pages.py  -> work/pose_lab/pages/<key>/index.html"""
import os, re
ROOT = os.path.dirname(os.path.abspath(__file__))
import json
REG = json.load(open(os.path.join(ROOT, "..", "clips.json"), encoding="utf8"))   # sổ clip: tools/clip_registry.py
PAGES = {c["pose"]["key"]: (c["pose"]["clip"], c["pose"]["title"]) for c in REG["clips"] if c.get("pose")}   # key: (clip, page title)
src = open(os.path.join(ROOT, "index.html"), encoding="utf8").read()
m = re.search(r"const POSES = \[\n(.*?)\n\];", src, re.S)
entries = [e for e in m.group(1).split("\n") if e.strip().startswith("{ clip:")]
for key, (clip, title) in PAGES.items():
    mine = [e.rstrip(",") for e in entries if e.strip().startswith(f'{{ clip: "{clip}"')]
    if not mine:
        print(key, "chưa có version nào: bỏ qua"); continue
    s = src[:m.start(1)] + ",\n".join(mine) + "," + src[m.end(1):]
    s = s.replace("<title>Pose Lab 3D</title>", f"<title>{title}</title>", 1)
    out = os.path.join(ROOT, "pages", key); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w", encoding="utf8").write(s)
    print(key, "versions:", [re.search(r'version: "(.*?)"', e).group(1) for e in mine],
          "models:", [re.search(r'glb: "(.*?)"', e).group(1) for e in mine])
