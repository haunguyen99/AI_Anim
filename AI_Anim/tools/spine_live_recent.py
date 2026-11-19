"""File Spine Live gần nhất (skill /spinelive).

  python tools/spine_live_recent.py            # file skeleton sửa gần nhất -> in JSON {json, label, sửa lúc, url}
  python tools/spine_live_recent.py bonemaw    # lọc theo từ khoá (tên game / anim / file, không phân biệt hoa thường)
  python tools/spine_live_recent.py --list 8   # 8 file gần nhất (để chọn)

Danh sách lấy từ server Spine Live (GET /api/spine/list, server Spine Live tools/spine_live/server.py phải đang chạy). "Gần nhất" = thời điểm sửa file JSON gần
nhất (Claude gen, người dùng Key / sửa lưới / weight trên Spine Live đều ghi file). Bản export xếp sau bản build cùng lúc.
"""
import json, os, sys, time, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE = "http://127.0.0.1:" + __import__("os").environ.get("SPINE_PORT", "8781")   # server Spine Live riêng (tools/spine_live/server.py)


def entries():
    with urllib.request.urlopen(BASE + "/api/spine/list", timeout=5) as r:
        items = json.load(r)
    out = []
    for e in items:
        p = os.path.join(ROOT, e["json"])
        if os.path.isfile(p):
            out.append(dict(e, mtime=os.path.getmtime(p)))
    # mới sửa trước; cùng mtime thì bản build trước bản export
    out.sort(key=lambda e: (-e["mtime"], e.get("kind") == "export"))
    return out


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        items = entries()
    except Exception as ex:
        print(json.dumps({"error": f"không gọi được server Spine Live ({BASE}): {ex}"}, ensure_ascii=False))
        return 2
    n_list = None
    if "--list" in argv:
        i = argv.index("--list")
        n_list = int(argv[i + 1]) if i + 1 < len(argv) and argv[i + 1].isdigit() else 10
        argv = argv[:i] + argv[i + 2 if n_list is not None and i + 1 < len(argv) and argv[i + 1].isdigit() else i + 1:]
    q = " ".join(argv).strip().lower()
    if q:
        items = [e for e in items if q in (e["label"] + " " + e["json"]).lower()]
    if not items:
        print(json.dumps({"error": f"không có file Spine nào khớp '{q}'"}, ensure_ascii=False))
        return 1
    row = lambda e: {"json": e["json"], "label": e["label"], "kind": e.get("kind"),
                     "sửa lúc": time.strftime("%Y-%m-%d %H:%M", time.localtime(e["mtime"])),
                     "url": f"{BASE}/spine?json={e['json']}"}
    if n_list:
        for e in items[:n_list]:
            print(json.dumps(row(e), ensure_ascii=False))
    else:
        print(json.dumps(row(items[0]), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
