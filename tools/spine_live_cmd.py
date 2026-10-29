"""Cho người dùng thấy Claude đang làm gì trên Spine Live (Home /spine, chế độ "Theo Claude").

  python tools/spine_live_cmd.py show <json> [--anim tap] [--frame 8 | --play] [--bones] [--mesh] [--weight wrist] [--ui Equipment|""] [--say "..."]
  python tools/spine_live_cmd.py say "Đang bẻ thử cổ tay ±25° để kiểm mesh"
  python tools/spine_live_cmd.py status          # trang Spine Live nào đang mở, có đang Theo Claude không
  python tools/spine_live_cmd.py clear           # xoá nhật ký bước
  python tools/spine_live_cmd.py notes [--all] [--json <rel>] [--bones]   # ghi chú + pose người dùng gửi từ chế độ Sửa
  python tools/spine_live_cmd.py note-done <id>... | --all                 # đánh dấu đã xử lý
  python tools/spine_live_cmd.py wait [--timeout s]   # chạy nền: thoát (in ghi chú) khi người dùng gửi ghi chú / bấm Gen tiếp

<json>: đường dẫn tính từ gốc dự án (work/<game>/spine/<anim>/x.json). Bản thử tạm: ghi vào work/<game>/spine/<anim>/_live/
(trang liệt kê thư mục này, ảnh lấy từ ../images). Mỗi lần ghi file JSON thì trang tự nạp lại, không cần gọi lệnh.
Không gửi gì tới trình duyệt: lệnh chỉ ghi work/store/_sys/spine_live/focus.json, trang hỏi server mỗi 0.5 s.
--bones / --mesh / --weight chỉ bật trên trang khi có cờ; không có cờ thì giữ nguyên lựa chọn của người dùng
(--no-bones / --no-mesh / --weight "" để tắt).
"""
import json, os, sys, time, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FOCUS = os.path.join(ROOT, "work", "store", "_sys", "spine_live", "focus.json")
BASE = f"http://127.0.0.1:{os.environ.get('HOME_PORT', '8780')}"
KEEP_LOG = 30
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load():
    try:
        return json.load(open(FOCUS, encoding="utf8"))
    except (OSError, ValueError):
        return {"seq": 0, "log": []}


def save(f):
    os.makedirs(os.path.dirname(FOCUS), exist_ok=True)
    tmp = FOCUS + ".tmp"
    with open(tmp, "w", encoding="utf8") as fh:
        json.dump(f, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, FOCUS)


def opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        v = args[i + 1] if i + 1 < len(args) else ""
        del args[i:i + 2]
        return v
    return default


def flag(args, name):
    if name in args:
        args.remove(name)
        return True
    return False


NOTES = os.path.join(ROOT, "work", "store", "_sys", "spine_live", "notes.json")


def notes_cmd(cmd, args):
    """notes [--all] [--json <rel>] [--bones]: ghi chú người dùng gửi từ chế độ Sửa (kèm pose đã key);
    note-done <id> [id...] | --all: đánh dấu đã xử lý."""
    try:
        notes = json.load(open(NOTES, encoding="utf8"))
    except (OSError, ValueError):
        notes = []
    if cmd == "note-done":
        ids = set(args)
        n = 0
        for x in notes:
            if x.get("status") == "open" and ("--all" in ids or x.get("id") in ids):
                x["status"] = "done"
                x["done_t"] = time.strftime("%Y-%m-%d %H:%M:%S")
                n += 1
        os.makedirs(os.path.dirname(NOTES), exist_ok=True)
        with open(NOTES + ".tmp", "w", encoding="utf8") as fh:
            json.dump(notes, fh, ensure_ascii=False, indent=1)
        os.replace(NOTES + ".tmp", NOTES)
        print(f"đã đánh dấu xong {n} ghi chú")
        return 0
    if cmd == "wait":   # chạy nền: thoát khi có ghi chú / yêu cầu gen chưa xử lý (Claude được báo ngay)
        timeout = float(opt(args, "--timeout", "0") or 0)
        t0 = time.time()
        while True:
            try:
                notes = json.load(open(NOTES, encoding="utf8"))
            except (OSError, ValueError):
                notes = []
            if any(x.get("status") == "open" for x in notes):
                return notes_cmd("notes", ["--bones"])
            if timeout and time.time() - t0 > timeout:
                print("hết giờ chờ, chưa có ghi chú mới")
                return 2
            time.sleep(1)
    show_all, bones = flag(args, "--all"), flag(args, "--bones")
    js = opt(args, "--json")
    sel = [x for x in notes if (show_all or x.get("status") == "open") and (not js or x.get("json") == js)]
    if not sel:
        print("Không có ghi chú mới từ Spine Live")
        return 0
    for x in sel:
        b = x.get("bones") or {}
        print(f"[{x['id']}] {x['t']} {x.get('status')}{' · YÊU CẦU GEN TIẾP' if x.get('request') == 'gen' else ''}"
              f" · {x['json']} · {x.get('anim')} @F{x.get('frame')}"
              f" · {'ĐÃ KEY vào file' if x.get('keyed') else 'chỉ ghi chú'} · {len(b)} xương")
        if x.get("note"):
            print("   ghi chú:", x["note"])
        if bones:
            for k, v in b.items():
                print(f"     {k}: xoay {v.get('rotate')} x {v.get('x')} y {v.get('y')}")
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd, args = argv[0], argv[1:]
    f = load()
    f.setdefault("log", [])
    if cmd == "status":
        try:
            cl = json.load(urllib.request.urlopen(BASE + "/api/spine/clients", timeout=3))
        except OSError as e:
            print("Không gọi được Home:", e)
            return 1
        if not cl:
            print("Không có trang Spine Live nào đang mở (" + BASE + "/spine)")
        for c in cl:
            print(f"trang {c['id']}: {'Theo Claude' if c['follow'] else 'KHÔNG theo Claude'} · {c['json']} · {c['anim']} · đã thấy bước {c['seq']}/{f.get('seq')}")
        return 0
    if cmd in ("notes", "note-done", "wait"):
        return notes_cmd(cmd, args)
    if cmd == "clear":
        f["log"] = []
    elif cmd == "say":
        f["say"] = " ".join(args)
    elif cmd == "show":
        if not args:
            print("thiếu <json>")
            return 1
        js = args.pop(0).replace("\\", "/")
        if os.path.isabs(js):
            js = os.path.relpath(js, ROOT).replace("\\", "/")
        if not os.path.isfile(os.path.join(ROOT, js)):
            print("không thấy", js)
            return 1
        f["json"] = js
        say = opt(args, "--say")
        anim = opt(args, "--anim")
        frame = opt(args, "--frame")
        weight = opt(args, "--weight")
        ui = opt(args, "--ui")   # tên nền UI trong <anim>/ui/*.json ("" = tắt)
        play = flag(args, "--play")
        view = {}
        for k, on, off in (("bones", "--bones", "--no-bones"), ("mesh", "--mesh", "--no-mesh")):
            if flag(args, on):
                view[k] = True
            elif flag(args, off):
                view[k] = False
        if weight is not None:
            view["weight"] = weight
        if ui is not None:
            view["ui"] = ui
        f["anim"] = anim
        f["frame"] = None if play or frame is None else float(frame)
        f["view"] = view
        f["say"] = say if say is not None else f.get("say", "")
        if args:
            print("bỏ qua:", " ".join(args))
    else:
        print("lệnh không biết:", cmd)
        return 1
    if cmd != "clear":
        f["seq"] = int(f.get("seq") or 0) + 1
        f["what"] = cmd   # "say": trang chỉ đổi chú thích, không nhảy file / frame
        f["t"] = time.strftime("%H:%M:%S")
        if f.get("say"):
            f["log"] = (f["log"] + [{"t": f["t"], "say": f["say"]}])[-KEEP_LOG:]
    save(f)
    print(f"bước {f.get('seq')}: {f.get('json', '')} {f.get('anim') or ''} {'' if f.get('frame') is None else 'F' + str(f['frame'])} {f.get('say', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
