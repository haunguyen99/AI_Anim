"""Canh ghi chú vẽ Studio đã bấm "Gửi cho AI": chờ tới khi có ghi chú mới (đã gửi, chưa xong, chưa nhận), đánh dấu đã nhận, in danh sách rồi thoát.
Claude chạy file này nền (run_in_background) trong phiên chat: thoát = Claude được gọi dậy để sửa, xong thì chạy lại để canh tiếp.
Không tốn lượt AI khi chờ (chỉ đọc thư mục work/store/*_studio/notes mỗi 2 giây).

  python tools/notes_watch.py              # chờ (mặc định tối đa 8 giờ)
  python tools/notes_watch.py --once       # chỉ kiểm một lần, in và thoát
  python tools/notes_watch.py --status     # có bộ canh nào đang chạy không (nhịp tim < 10 s)

Nhịp tim: work/store/_sys/watch/notes.json (beat = giây epoch). Trang Studio đọc file này để hiện
"Claude đang canh"; hook tools/notes_watch_hook.py đọc để nhắc Claude bật bộ canh khi Studio đang mở.
"""
import glob, json, os, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
STORE = os.path.join(ROOT, "work", "store")
BEAT = os.path.join(STORE, "_sys", "watch", "notes.json")
FRESH = 10


def beat(on=True):
    try:
        os.makedirs(os.path.dirname(BEAT), exist_ok=True)
        tmp = BEAT + ".tmp"
        with open(tmp, "w", encoding="utf8") as fh:
            json.dump({"id": "notes", "pid": os.getpid(), "beat": time.time() if on else 0,
                       "at": time.strftime("%Y-%m-%dT%H:%M:%S")}, fh)
        os.replace(tmp, BEAT)
    except OSError:
        pass


def alive():
    try:
        return time.time() - json.load(open(BEAT, encoding="utf8")).get("beat", 0) < FRESH
    except (OSError, ValueError):
        return False


def pending():
    out = []
    for f in glob.glob(os.path.join(STORE, "*_studio", "notes", "*.json")) + glob.glob(os.path.join(STORE, "*_notes", "notes", "*.json")):   # *_notes: trang thử ?ns=
        try:
            raw = json.load(open(f, encoding="utf8"))
        except (OSError, ValueError):
            continue
        d = raw["data"] if isinstance(raw, dict) and isinstance(raw.get("data"), dict) else raw
        if d.get("sent") and d.get("status") != "done" and not d.get("picked"):
            out.append((f, raw, d))
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--status" in sys.argv:
        print("running" if alive() else "stopped"); return 0
    once = "--once" in sys.argv
    if not once and alive():
        print("[] # bộ canh khác đang chạy"); return 0
    try:
        return loop(once)
    finally:
        if not once: beat(False)


def loop(once):
    end = time.time() + 8 * 3600
    while True:
        P = pending()
        if P:
            time.sleep(1.5)                      # người dùng có thể đang gửi nhiều ghi chú liền: gom một lượt
            P = pending()
            now = time.strftime("%Y-%m-%dT%H:%M:%S")
            for f, raw, d in P:
                d["picked"] = now                # trang hiện "AI đã nhận, đang sửa"
                json.dump(raw, open(f, "w", encoding="utf8"), ensure_ascii=False)
            print(json.dumps([{"ns": os.path.basename(os.path.dirname(os.path.dirname(f))), "id": d["id"], "text": d.get("text"),
                               "focus": (d.get("ctx") or {}).get("focus"), "char": (d.get("ctx") or {}).get("char")} for f, _, d in P], ensure_ascii=False))
            return 0
        if once or time.time() > end:
            print("[]"); return 0
        if not once: beat()
        time.sleep(2)


if __name__ == "__main__":
    sys.exit(main())
