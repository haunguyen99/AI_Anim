"""Bắt đầu một anim Spine 2D mới (bước 0 của skill /spine2d).

Tạo thư mục work/<dự án>/spine/<Anim>/ đủ cấu trúc, brief.md ghi order của GD, export_settings.json theo setting
người dùng (mẫu HandTut), build_<anim>.py mẫu (root + dir + mỗi ảnh trong images/ một slot, anim rỗng), ghi clip vào
work/clips.json để hiện trên Home, rồi in link Spine Live.

  .venv/Scripts/python.exe -I tools/spine/new_spine_anim.py <dự án> <Nhân vật> <Anim> [--fps 30] [--frames 30]
      [--loop | --once] [--use "màn tut / UI / nhân vật"] [--src "ảnh/PSD nguồn"] [--size "kích thước hiển thị"]
      [--variants "trái,phải"] [--ui <ảnh UI game.png>] [--desc "mô tả order"] [--dry]

Dự án là id trong khóa projects của sổ (vd pirate_goldrush, test). Không ghi đè thư mục đã có.
"""
import argparse, json, os, re, shutil, sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REG = os.path.join(ROOT, "work", "clips.json")
EXPORT_TEMPLATE = os.path.join(ROOT, "work", "pirate_goldrush", "spine", "HandTut", "export_settings.json")
SUBDIRS = ["images", "export", "preview", "ui", "_live"]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


BUILD_TEMPLATE = '''"""Dựng skeleton JSON cho {anim} ({project}). Chạy: .venv/Scripts/python.exe -I {rel}/build_{low}.py [out.json]

Mẫu khởi tạo từ tools/spine/new_spine_anim.py: root + dir + mỗi PNG trong images/ một slot (thứ tự tên file = thứ tự
vẽ), anim "{low}" rỗng. Rig thật (mesh, weight, FK, điểm chạm) xem work/pirate_goldrush/spine/HandTut/build_handtut.py.
"""
import json, os, struct, sys

sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
FPS = {fps}
FRAMES = {frames}


def f(fr):                       # frame -> giây
    return round(fr / FPS, 4)


def ease(t1, v1, t2, v2, a=1 / 3, b=1 / 3, end_slope=0.0):
    """Curve Spine 4.2 một kênh: [cx1, cy1, cx2, cy2] = thời gian (giây) và giá trị tuyệt đối, đặt ở key đầu đoạn."""
    dt = t2 - t1
    return [round(t1 + dt * a, 4), round(v1, 4), round(t2 - dt * b, 4), round(v2 - (v2 - v1) * end_slope, 4)]


def ease2(t1, p1, t2, p2, **kw):  # translate / scale: 2 kênh = 8 số
    return ease(t1, p1[0], t2, p2[0], **kw) + ease(t1, p1[1], t2, p2[1], **kw)


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    return struct.unpack(">II", head[16:24])


def build():
    img_dir = os.path.join(HERE, "images")
    names = sorted(n[:-4] for n in os.listdir(img_dir) if n.lower().endswith(".png")) if os.path.isdir(img_dir) else []
    bones = [{{"name": "root"}}, {{"name": "dir", "parent": "root"}}]
    slots, atts = [], {{}}
    for n in names:
        w, h = png_size(os.path.join(img_dir, n + ".png"))
        slots.append({{"name": n, "bone": "dir", "attachment": n}})
        atts[n] = {{n: {{"width": w, "height": h}}}}
    anim = {{"bones": {{"dir": {{"rotate": [{{"time": 0, "value": 0}}, {{"time": f(FRAMES), "value": 0}}]}}}}}}
    return {{
        "skeleton": {{"spine": "4.2.43", "fps": FPS, "images": "./images/"}},
        "bones": bones, "slots": slots,
        "skins": [{{"name": "default", "attachments": atts}}],
        "animations": {{"{low}": anim}},
    }}


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "{low}.json")
    sk = build()
    json.dump(sk, open(out, "w", encoding="utf8"), indent=1)
    print("Đã ghi", out, "|", len(sk["bones"]), "xương,", len(sk["slots"]), "slot")
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project"); ap.add_argument("character"); ap.add_argument("anim")
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--frames", type=int, default=30)
    g = ap.add_mutually_exclusive_group(); g.add_argument("--loop", action="store_true"); g.add_argument("--once", action="store_true")
    for k in ("use", "src", "size", "variants", "ui", "desc"):
        ap.add_argument("--" + k, default="")
    ap.add_argument("--dry", action="store_true", help="chỉ in, không ghi gì")
    a = ap.parse_args()

    d = json.load(open(REG, encoding="utf8"))
    pr = next((p for p in d["projects"] if p["id"] == a.project), None)
    if not pr:
        sys.exit("Không có dự án '%s'. Dự án có: %s" % (a.project, ", ".join(p["id"] for p in d["projects"])))
    anim, low = a.anim, slug(a.anim)
    rel = "work/%s/spine/%s" % (a.project, anim)
    folder = os.path.join(ROOT, *rel.split("/"))
    cid = slug("%s_%s" % (a.character, anim))
    if os.path.exists(folder):
        sys.exit("Thư mục %s đã có: không ghi đè." % rel)
    if any(c["id"] == cid for c in d["clips"]):
        sys.exit("Clip '%s' đã có trong sổ." % cid)
    loop = "loop" if a.loop else ("một lần" if a.once else "chưa rõ")
    print("Dự án %s | clip %s | %s | %d F @ %d fps | %s" % (a.project, cid, rel, a.frames, a.fps, loop))
    if a.dry:
        return

    for s in SUBDIRS:
        os.makedirs(os.path.join(folder, s))
    today = date.today().isoformat()
    brief = [
        "# %s %s (Spine 2D)" % (a.character, anim), "",
        "Order nhận ngày %s. Ô nào còn \"chưa rõ\" thì hỏi gộp một lần trước khi thiết kế." % today, "",
        "| Mục | Giá trị |", "|---|---|",
        "| Dự án | %s |" % pr["name"],
        "| Dùng ở đâu | %s |" % (a.use or "chưa rõ"),
        "| Ảnh nguồn | %s |" % (a.src or "chưa rõ (bỏ PNG vào images/ hoặc đưa PSD)"),
        "| Kích thước hiển thị | %s |" % (a.size or "chưa rõ"),
        "| fps / độ dài | %d fps, %d F (%.2f s) |" % (a.fps, a.frames, a.frames / a.fps),
        "| Loop | %s |" % loop,
        "| Hướng / biến thể | %s |" % (a.variants or "chưa rõ"),
        "| Ảnh UI game | %s |" % (a.ui or "chưa có (bỏ vào ui/)"),
        "| Giao | JSON + .atlas.txt theo export_settings.json |", "",
        "## Mô tả", "", a.desc or "(chưa có)", "",
        "## Thiết kế (chờ duyệt)", "", "(viết từng pha theo frame ở bước 2)", "",
    ]
    open(os.path.join(folder, "brief.md"), "w", encoding="utf8").write("\n".join(brief))
    shutil.copyfile(EXPORT_TEMPLATE, os.path.join(folder, "export_settings.json"))
    open(os.path.join(folder, "build_%s.py" % low), "w", encoding="utf8").write(
        BUILD_TEMPLATE.format(anim=anim, project=pr["name"], rel=rel, low=low, fps=a.fps, frames=a.frames))
    if a.ui and os.path.isfile(a.ui):
        img = os.path.basename(a.ui)
        shutil.copyfile(a.ui, os.path.join(folder, "ui", img))
        json.dump({"name": os.path.splitext(img)[0], "image": img, "at": [0, 0], "scale": 1.0},
                  open(os.path.join(folder, "ui", os.path.splitext(img)[0] + ".json"), "w", encoding="utf8"), indent=1)

    d["characters"].setdefault(a.character, {"rig_url": ""})
    if a.character not in pr["characters"]:
        pr["characters"].append(a.character)
        pr.setdefault("labels", {}).setdefault(a.character, "Spine 2D")
    d["clips"].append({
        "id": cid, "character": a.character, "stage": "analysis", "kind": "spine",
        "note": "Spine 2D: chờ thiết kế", "dir": rel, "frames": a.frames, "fps": a.fps,
        "desc": a.desc, "created": today, "updated": today,
        "review": {"key": cid, "clip": anim, "title": "%s %s Review Lab" % (a.character, anim),
                   "crumb": "%s · Spine 2D" % pr["name"], "name": anim, "parts": None, "url": ""},
    })
    json.dump(d, open(REG, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    open(REG, "a", encoding="utf8").write("\n")

    print("Đã tạo", rel, "(", ", ".join(SUBDIRS), "+ brief.md, export_settings.json, build_%s.py )" % low)
    print("Đã ghi clip", cid, "vào sổ (giai đoạn analysis, hiện trên Home)")
    print("Spine Live: http://127.0.0.1:8780/spine?json=%s/%s.json  (có sau lần chạy build đầu tiên)" % (rel, low))
    print("Còn lại: thêm dòng vào MAP.md; bỏ ảnh vào images/; chỉnh ui/*.json (at, scale) nếu có ảnh UI.")


if __name__ == "__main__":
    main()
