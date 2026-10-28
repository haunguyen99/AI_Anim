"""Sổ đăng ký clip: điểm nối giữa Rig Lab, Pose Lab và Review Lab.
Mọi trang (artifact) của một clip nằm trong work/clips.json; split_pages.py của Review Lab và Pose Lab đọc sổ này,
skill /new_clip và /check_fb đọc/ghi qua script này. Chạy bằng .venv\\Scripts\\python.exe -I tools\\clip_registry.py <lệnh>.

  list                                    bảng trạng thái mọi clip (giai đoạn, trang nào đã có, link)
  urls                                    bảng link dạng markdown (skill /check_fb dùng)
  new <character> <clip> [--parts sdr06|sdr_attack|"A,B,C"] [--stage rig|analysis|p0|blocking|...]
                                          đăng ký clip mới (chưa tạo trang: trang tạo khi có version đầu tiên)
  stage <id> <giai đoạn>                  đổi giai đoạn của clip
  set-url <id|char:Tên> <rig|pose|review> <url>   ghi link artifact vừa đăng
  review-version <id> --version V --label L --src clips/x.webm --thumb clips/x.jpg --n N [--fps 30 --w 1200 --h 600 --views "..." --note "..."]
                                          thêm một version vào đầu CLIPS của work/review_page/index.html
  pose-version <id> --version V --label L --glb models/x.json --frames N [--fps 30 --keys 1,5 --mode keys --loop --seed-from V --note "..."]
                                          thêm một dòng vào đầu POSES của work/pose_lab/index.html
  build                                   chạy split_pages.py của Review Lab và Pose Lab
"""
import argparse, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REG = os.path.join(ROOT, "work", "clips.json")
STAGES = ["rig", "analysis", "p0", "blocking", "spline", "polish", "export"]


def load():
    return json.load(open(REG, encoding="utf8"))


def save(d):
    json.dump(d, open(REG, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    open(REG, "a", encoding="utf8").write("\n")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def find(d, cid):
    for c in d["clips"]:
        if c["id"] == cid:
            return c
    sys.exit(f"Không có clip '{cid}'. Dùng: list")


def cmd_list(a):
    d = load()
    print(f"{'id':<20}{'nhân vật':<10}{'giai đoạn':<10}{'pose':<6}{'review':<8}ghi chú")
    for c in d["clips"]:
        print(f"{c['id']:<20}{c['character']:<10}{c.get('stage', '-'):<10}{'có' if (c.get('pose') or {}).get('url') else '-':<6}"
              f"{'có' if (c.get('review') or {}).get('url') else '-':<8}{c.get('note', '')}")
    print("\nNhân vật / Rig Lab:", {k: ("có" if v.get("rig_url") else "-") for k, v in d["characters"].items()})


def cmd_urls(a):
    d = load()
    print("| nhân vật | clip | Rig Lab | Pose Lab | Review Lab |\n|---|---|---|---|---|")
    for c in d["clips"]:
        rig = d["characters"].get(c["character"], {}).get("rig_url", "")
        print(f"| {c['character']} | {c['id']} | {rig} | {(c.get('pose') or {}).get('url', '')} | {(c.get('review') or {}).get('url', '')} |")


def cmd_new(a):
    d = load()
    cid = slug(f"{a.character}_{a.clip}")
    if any(c["id"] == cid for c in d["clips"]):
        sys.exit(f"Clip '{cid}' đã có.")
    d["characters"].setdefault(a.character, {"rig_url": ""})
    parts = a.parts
    if parts and parts not in ("sdr06", "sdr_attack"):
        parts = [p.strip() for p in parts.split(",") if p.strip()]
    d["clips"].append({"id": cid, "character": a.character, "stage": a.stage, "note": a.note or "",
                       "review": {"key": cid, "clip": a.clip, "title": f"{a.character} {a.clip.replace('_', ' ')} Review Lab",
                                  "crumb": f"{a.character} · anim", "name": a.clip, "parts": parts or None, "url": ""},
                       "pose": {"key": cid, "clip": f"{a.character}_{a.clip}", "title": f"{a.character} {a.clip.replace('_', ' ')} Pose Lab", "url": ""}})
    save(d)
    print("Đã đăng ký", cid, "| giai đoạn", a.stage)
    if not d["characters"][a.character].get("rig_url"):
        print(f"Nhân vật {a.character} chưa có Rig Lab: chạy /rig (chế độ 3) trước khi làm P0.")
    print("Trang Pose Lab và Review Lab tạo khi có POSES / CLIPS đầu tiên: dùng pose-version / review-version, rồi build, rồi đăng artifact mới và set-url.")


def cmd_stage(a):
    d = load(); c = find(d, a.id)
    if a.stage not in STAGES:
        sys.exit("Giai đoạn hợp lệ: " + ", ".join(STAGES))
    c["stage"] = a.stage; save(d); print(a.id, "→", a.stage)


def cmd_set_url(a):
    d = load()
    if a.id.startswith("char:"):
        ch = a.id[5:]
        d["characters"].setdefault(ch, {})["rig_url"] = a.url
    else:
        c = find(d, a.id)
        if a.lab == "rig":
            d["characters"].setdefault(c["character"], {})["rig_url"] = a.url
        else:
            c.setdefault(a.lab, {})["url"] = a.url
    save(d); print("Đã ghi", a.id, a.lab, a.url)


def js(s):
    return json.dumps(s, ensure_ascii=False)


def prepend(path, marker, entry):
    src = open(path, encoding="utf8").read()
    i = src.index(marker) + len(marker)
    open(path, "w", encoding="utf8").write(src[:i] + entry + "\n" + src[i:])


def cmd_review_version(a):
    d = load(); c = find(d, a.id); r = c["review"]
    fields = [f"clip: {js(r['clip'])}", f"version: {js(a.version)}", f"label: {js(a.label)}", f"src: {js(a.src)}", f"thumb: {js(a.thumb)}",
              f"n: {a.n}", f"fps: {a.fps}"]
    if a.w: fields.append(f"w: {a.w}")
    if a.h: fields.append(f"h: {a.h}")
    if a.views: fields.append(f"views: {js(a.views)}")
    if a.note: fields.append(f"note: {js(a.note)}")
    prepend(os.path.join(ROOT, "work", "review_page", "index.html"), "const CLIPS = [\n", "  { " + ", ".join(fields) + " },")
    print("Đã thêm version", a.version, "vào Review Lab (clip", r["clip"] + ")")


def cmd_pose_version(a):
    d = load(); c = find(d, a.id); p = c["pose"]
    keys = "[" + ", ".join(x for x in (a.keys or "1").split(",")) + "]"
    fields = [f"clip: {js(p['clip'])}", f"project: {js(c['character'])}", f"version: {js(a.version)}", f"date: {js(a.date)}", f"frames: {a.frames}",
              f"fps: {a.fps}", f"keys: {keys}"]
    if a.mode: fields.append(f"mode: {js(a.mode)}")
    if a.loop: fields.append("loop: true")            # F cuối = F1
    if a.seed_from: fields.append(f"seedFrom: {js(a.seed_from)}")   # chép key của version này (db) làm điểm bắt đầu
    if a.main: fields.append("main: [" + ", ".join(x.strip() for x in a.main.split(",")) + "]")    # main keys (phase starts) for the Timing panel
    if a.phases: fields.append("phases: " + json.dumps([x.strip() for x in a.phases.split(",")], ensure_ascii=False))
    fields += [f"label: {js(a.label)}", f"note: {js(a.note or '')}", f"glb: {js(a.glb)}"]
    prepend(os.path.join(ROOT, "work", "pose_lab", "index.html"), "const POSES = [\n", "  { " + ", ".join(fields) + " },")
    print("Đã thêm version", a.version, "vào Pose Lab (clip", p["clip"] + ")")


def cmd_build(a):
    py = sys.executable
    for rel in ("work/review_page/split_pages.py", "work/pose_lab/split_pages.py"):
        print("→", rel); subprocess.run([py, "-I", "-X", "utf8", os.path.join(ROOT, rel)], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("list").set_defaults(f=cmd_list)
    sp.add_parser("urls").set_defaults(f=cmd_urls)
    sp.add_parser("build").set_defaults(f=cmd_build)
    n = sp.add_parser("new"); n.add_argument("character"); n.add_argument("clip"); n.add_argument("--parts"); n.add_argument("--stage", default="analysis"); n.add_argument("--note"); n.set_defaults(f=cmd_new)
    s = sp.add_parser("stage"); s.add_argument("id"); s.add_argument("stage"); s.set_defaults(f=cmd_stage)
    u = sp.add_parser("set-url"); u.add_argument("id"); u.add_argument("lab", choices=["rig", "pose", "review"]); u.add_argument("url"); u.set_defaults(f=cmd_set_url)
    r = sp.add_parser("review-version"); r.add_argument("id")
    for k in ("version", "label", "src", "thumb"): r.add_argument("--" + k, required=True)
    r.add_argument("--n", type=int, required=True); r.add_argument("--fps", type=int, default=30); r.add_argument("--w"); r.add_argument("--h"); r.add_argument("--views"); r.add_argument("--note")
    r.set_defaults(f=cmd_review_version)
    p = sp.add_parser("pose-version"); p.add_argument("id")
    for k in ("version", "label", "glb"): p.add_argument("--" + k, required=True)
    p.add_argument("--frames", type=int, required=True); p.add_argument("--fps", type=int, default=30); p.add_argument("--keys"); p.add_argument("--mode"); p.add_argument("--note"); p.add_argument("--main"); p.add_argument("--phases"); p.add_argument("--loop", action="store_true"); p.add_argument("--seed-from")
    p.add_argument("--date", default=__import__("datetime").date.today().isoformat()); p.set_defaults(f=cmd_pose_version)
    a = ap.parse_args(); a.f(a)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
