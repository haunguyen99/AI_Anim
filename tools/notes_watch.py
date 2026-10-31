"""Canh ghi chú vẽ Studio đã bấm "Gửi cho AI", yêu cầu thêm ảnh ở trang Key Pose (kind keypose_req → tools/keypose_gen.py <id>) và cổng duyệt Rig (nút Duyệt / Cần sửa ở mỗi bước Rig): chờ tới khi có mục mới
(đã gửi, chưa nhận), đánh dấu đã nhận, in danh sách rồi thoát. Mục cổng Rig có "kind": "rig_gate" (ns, char, step, status ok|fix, note).
Thêm (2026-10-29, user: "cho vào bộ canh luôn đi"): góp ý tab "Góp ý cho AI" của Pose (kind pose_adjust) ở
work/store/*_pose_lab/adjusts: nhận ngay khi bấm "Gửi tất cả cho AI" (rounds/<clip-ver> status sent), còn góp ý mới lưu mà
chưa gửi thì nhận khi người dùng ngừng thêm góp ý 3 s. Sửa xong: python tools/notes_watch.py --pose-done <ns> <clip> <ver> "ghi chú"
work/store/keypose/animreqs: "+ Anim mới" trong Image Key (kind anim_req). Cập nhật: python tools/notes_watch.py --anim-status <id> <trạng thái> "lời nhắn"
(đánh dấu các góp ý đó "AI đã áp", vòng = fixed).
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


def keypose_pending():
    """Key Pose (/keypose): work/store/keypose/requests/<id>.json gửi mà chưa nhận. Claude chạy tools/keypose_gen.py <id>."""
    out = []
    for f in glob.glob(os.path.join(STORE, "keypose", "requests", "*.json")):
        try:
            d = json.load(open(f, encoding="utf8"))
        except (OSError, ValueError):
            continue
        if d.get("sent") and not d.get("picked"):
            out.append((f, d))
    return out


def animreq_pending():
    """Image Key "+ Anim mới" (Studio, 2026-10-30): work/store/keypose/animreqs/<id>.json gửi mà chưa nhận.
    Claude làm: đăng ký anim, bản phân tích + bảng pha (cột Key pose) chờ duyệt, rồi ảnh key pose (gdd_stage0.md, mục Anim mới từ Studio)."""
    out = []
    for f in glob.glob(os.path.join(STORE, "keypose", "animreqs", "*.json")):
        try:
            d = json.load(open(f, encoding="utf8"))
        except (OSError, ValueError):
            continue
        if d.get("sent") and not d.get("picked"):
            out.append((f, d))
    return out


def anim_status(rid, status, reply=""):
    """--anim-status <id> <trạng thái> ["lời nhắn"]: cập nhật yêu cầu anim mới (trang Studio hiện ngay).
    Trạng thái: picked / analysis (đang phân tích) / review (chờ duyệt phân tích) / images (đang tạo ảnh) / done / error."""
    f = os.path.join(STORE, "keypose", "animreqs", rid + ".json")
    d = json.load(open(f, encoding="utf8"))
    d["status"] = status
    if reply:
        d["reply"] = reply
    if status == "done":
        d["done_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(d, open(f, "w", encoding="utf8"), ensure_ascii=False)
    print(json.dumps({"ok": True, "id": rid, "status": status}, ensure_ascii=False))
    return 0


POSE_QUIET = 3   # s: góp ý chưa gửi được nhận khi không có góp ý mới trong chừng này giây (user: "nhận luôn sau 3 giây")


def _load(f):
    try:
        raw = json.load(open(f, encoding="utf8"))
    except (OSError, ValueError):
        return None, None
    d = raw["data"] if isinstance(raw, dict) and isinstance(raw.get("data"), dict) else raw
    return raw, d


def _ts(iso):
    try:
        return time.mktime(time.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone if iso else 0
    except ValueError:
        return 0


def pose_pending():
    """Góp ý Pose: [(ns, clip, ver, [(file, raw, d)], round_file|None, round_raw, round_d)] cần nhận."""
    out = []
    for ns_dir in glob.glob(os.path.join(STORE, "*_pose_lab")):
        groups = {}
        for f in glob.glob(os.path.join(ns_dir, "adjusts", "*.json")):
            raw, d = _load(f)
            if not d or d.get("status") == "done" or d.get("picked"): continue
            groups.setdefault((d.get("clip"), d.get("version")), []).append((f, raw, d))
        for (clip, ver), items in groups.items():
            rf = os.path.join(ns_dir, "rounds", ("%s-%s" % (clip, ver)).replace(" ", "_") + ".json")
            rraw, rd = _load(rf) if os.path.exists(rf) else (None, None)
            sent = bool(rd and rd.get("status") == "sent")
            newest = max(_ts(d.get("createdAt")) for _, _, d in items)
            if sent or time.time() - newest > POSE_QUIET:
                out.append((os.path.basename(ns_dir), clip, ver, items, rf if rd else None, rraw, rd))
    return out


def pose_done(ns, clip, ver, note):
    n = 0; now = time.strftime("%Y-%m-%dT%H:%M:%S")
    for f in glob.glob(os.path.join(STORE, ns, "adjusts", "*.json")):
        raw, d = _load(f)
        if d and d.get("clip") == clip and d.get("version") == ver and d.get("status") != "done":
            d["status"] = "done"; d["doneAt"] = now; d["aiNote"] = note
            json.dump(raw, open(f, "w", encoding="utf8"), ensure_ascii=False); n += 1
    rf = os.path.join(STORE, ns, "rounds", ("%s-%s" % (clip, ver)).replace(" ", "_") + ".json")
    if os.path.exists(rf):
        raw, d = _load(rf)
        if d: d["status"] = "fixed"; d["aiNote"] = note; d["fixedAt"] = now; json.dump(raw, open(rf, "w", encoding="utf8"), ensure_ascii=False)
    print(json.dumps({"ok": True, "done": n}, ensure_ascii=False))


GATE_NAMES = {1: "Mesh", 2: "Khớp", 3: "Xương", 4: "Skin", 5: "Thử khớp", 6: "Vật lý"}


def gates_pending():
    """Cổng Rig: work/store/<id>_rig_lab/rig/gates.json, g[n] có sent mà chưa picked."""
    out = []
    for f in glob.glob(os.path.join(STORE, "*_rig_lab", "rig", "gates.json")):
        try:
            raw = json.load(open(f, encoding="utf8"))
        except (OSError, ValueError):
            continue
        d = raw["data"] if isinstance(raw, dict) and isinstance(raw.get("data"), dict) else raw
        for n, g in (d.get("g") or {}).items():
            if isinstance(g, dict) and g.get("sent") and not g.get("picked"):
                out.append((f, raw, d, n, g))
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--anim-status" in sys.argv:
        i = sys.argv.index("--anim-status"); a = sys.argv[i + 1:i + 4] + [""] * 3
        return anim_status(a[0], a[1], a[2])
    if "--pose-done" in sys.argv:
        i = sys.argv.index("--pose-done"); a = sys.argv[i + 1:i + 5] + [""] * 4
        pose_done(a[0], a[1], a[2], a[3]); return 0
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
        P, G, K, A, M = pending(), gates_pending(), keypose_pending(), pose_pending(), animreq_pending()
        if P or G or K or A or M:
            time.sleep(1.5)                      # người dùng có thể đang gửi nhiều ghi chú liền: gom một lượt
            P, G, K, A, M = pending(), gates_pending(), keypose_pending(), pose_pending(), animreq_pending()
            now = time.strftime("%Y-%m-%dT%H:%M:%S")
            for f, raw, d in P:
                d["picked"] = now                # trang hiện "AI đã nhận, đang sửa"
                json.dump(raw, open(f, "w", encoding="utf8"), ensure_ascii=False)
            for f, raw, d, n, g in G:
                g["picked"] = now
            for f in {x[0] for x in G}:
                raw = next(x[1] for x in G if x[0] == f)
                json.dump(raw, open(f, "w", encoding="utf8"), ensure_ascii=False)
            for f, d in K + M:
                d["picked"] = now; d["status"] = "picked"
                json.dump(d, open(f, "w", encoding="utf8"), ensure_ascii=False)
            for ns, clip, ver, items, rf, rraw, rd in A:
                for f, raw, d in items:
                    d["picked"] = now; json.dump(raw, open(f, "w", encoding="utf8"), ensure_ascii=False)
                if rd is not None:
                    rd["status"] = "working"; rd["aiNote"] = "AI đã nhận, đang sửa"; json.dump(rraw, open(rf, "w", encoding="utf8"), ensure_ascii=False)
            res = [{"kind": "note", "ns": os.path.basename(os.path.dirname(os.path.dirname(f))), "id": d["id"], "text": d.get("text"),
                    "focus": (d.get("ctx") or {}).get("focus"), "char": (d.get("ctx") or {}).get("char")} for f, _, d in P]
            res += [{"kind": "rig_gate", "ns": os.path.basename(os.path.dirname(os.path.dirname(f))), "char": g.get("char"), "step": int(n),
                     "step_name": GATE_NAMES.get(int(n)), "status": g.get("status"), "note": g.get("note")} for f, _, _, n, g in G]
            res += [{"kind": "keypose_req", "id": os.path.basename(f)[:-5], "job": d.get("job"), "key": d.get("key"), "base": d.get("base"),
                     "n": d.get("n"), "by": d.get("by"), "text": d.get("text")} for f, d in K]
            res += [{"kind": "anim_req", "id": os.path.basename(f)[:-5], "char": d.get("char"), "charName": d.get("charName"), "job": d.get("job"),
                     "name": d.get("name"), "desc": d.get("desc"), "loop": d.get("loop"), "frames": d.get("frames"), "fps": d.get("fps"),
                     "doc": d.get("doc"), "by": d.get("by")} for f, d in M]
            res += [{"kind": "pose_adjust", "ns": ns, "clip": clip, "version": ver, "sent": rd is not None,
                     "items": [{"id": os.path.basename(f)[:-5], "frame": d.get("frame"), "text": d.get("text"), "kind": d.get("kind"),
                                "bones": sorted((d.get("bones") or {}).keys()), "img": bool(d.get("img"))} for f, _, d in items]}
                    for ns, clip, ver, items, rf, rraw, rd in A]
            print(json.dumps(res, ensure_ascii=False))
            return 0
        if once or time.time() > end:
            print("[]"); return 0
        if not once: beat()
        time.sleep(2)


if __name__ == "__main__":
    sys.exit(main())
