"""HorusChat bằng dòng lệnh cho phiên con (phiên nền không nạp MCP): nhận tin, đọc lịch sử, soạn NHÁP, gửi sau khi người dùng duyệt.

  python -I tools/horuschat_cli.py wait [--timeout 600]      # chờ tin mới (hộp thư của bộ canh nền), in mỗi tin một dòng JSON
  python -I tools/horuschat_cli.py rooms [lọc]               # phòng đã vào
  python -I tools/horuschat_cli.py history <phòng> [--limit 30] [--thread <event_id>]
  python -I tools/horuschat_cli.py draft --room <phòng> --text "..." [--thread <event_id>] [--mention @a:host,@b:host] [--why "..."]   # soạn nháp, KHÔNG gửi
  python -I tools/horuschat_cli.py draft --to @user:host --text "..." [--why "..."]                      # nháp tin nhắn riêng
  python -I tools/horuschat_cli.py drafts [--all]            # danh sách nháp (mặc định chỉ nháp đang chờ)
  python -I tools/horuschat_cli.py send <id nháp> --expect "<vài chữ đầu>"   # GỬI nháp (chỉ phiên chính chạy, sau khi người dùng đồng ý)
  python -I tools/horuschat_cli.py say --room <phòng> --text "..." [--thread ..] [--mention ..] [--why ..]   # trả lời NGAY, chỉ cho tin tán gẫu không liên quan công việc
  python -I tools/horuschat_cli.py who <tên>   # tìm user_id để --mention
  python -I tools/horuschat_cli.py download --room <phòng> --event <event_id> --out <thư mục> [--url mxc://..]   # tải file đính kèm
  python -I tools/horuschat_cli.py sendfile --room <phòng> --file <đường dẫn> [--text ..] [--thread ..] [--mention ..] [--max-mib N]   # gửi file (mặc định <=10 MiB), chỉ khi người dùng đã nói rõ
  python -I tools/horuschat_cli.py reject <id nháp> [lý do]  # bỏ nháp

Danh tính: theo tools/identity.py (--profile / AI_PROFILE / tools/.profile). Nháp: work/store/_sys/watch/horuschat_drafts[_<danh tính>].json
"""
import json, os, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import identity  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools", "horuschat_mcp"))
from horuschat_mcp.client import HCError, HorusChat, q, slim  # noqa: E402

DIR = os.path.join(ROOT, "work", "store", "_sys", "watch")
INBOX = identity.state_path(os.path.join(DIR, "horuschat_inbox.jsonl"))
CURSOR = identity.state_path(os.path.join(DIR, "horuschat_cli.json"))
DRAFTS = identity.state_path(os.path.join(DIR, "horuschat_drafts.json"))


def out(o):
    print(json.dumps(o, ensure_ascii=False))


def opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        v = args[i + 1] if i + 1 < len(args) else default
        del args[i:i + 2]
        return v
    return default


def jload(path, default):
    try:
        return json.load(open(path, encoding="utf8"))
    except (OSError, ValueError):
        return default


def jsave(path, o):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    json.dump(o, open(tmp, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def cmd_wait(args):
    timeout = float(opt(args, "--timeout", 600))
    cur = jload(CURSOR, {})
    t0 = time.time()
    while True:
        size = os.path.getsize(INBOX) if os.path.exists(INBOX) else 0
        pos = min(cur.get("pos", 0), size)
        if size > pos:
            with open(INBOX, "rb") as f:
                f.seek(pos)
                data = f.read()
            end = data.rfind(b"\n") + 1
            if end:
                for line in data[:end].decode("utf8").splitlines():
                    if line.strip():
                        print(line)
                jsave(CURSOR, {"pos": pos + end})
                return
        if time.time() - t0 >= timeout:
            print("(không có tin mới)")
            return
        time.sleep(3)


def cmd_rooms(args):
    f = (args[0] if args else "").lower()
    rows = HorusChat().rooms(refresh=True)
    for r in rows:
        if not f or f in (r.get("name") or "").lower() or f in (r.get("canonical_alias") or "").lower():
            out({k: r.get(k) for k in ("room_id", "name", "canonical_alias") if r.get(k)})


def cmd_history(args):
    limit = int(opt(args, "--limit", 30))
    thread = opt(args, "--thread")
    hc = HorusChat()
    rid = hc.room_id(args[0])
    r = hc.get(f"/v1/developer/rooms/{q(rid)}/history", limit=max(1, min(limit, 100)), thread_root_event_id=thread or None)
    evs = r.get("events") or r.get("messages") or []
    for e in reversed(evs):
        out(slim(e))


def cmd_draft(args):
    room, to = opt(args, "--room"), opt(args, "--to")
    text, thread, why = opt(args, "--text"), opt(args, "--thread"), opt(args, "--why", "")
    mentions = [m.strip() for m in (opt(args, "--mention", "") or "").split(",") if m.strip()]
    if not text or not (room or to):
        sys.exit("Cần --text và (--room hoặc --to)")
    ds = jload(DRAFTS, [])
    d = {"id": (max([x["id"] for x in ds]) + 1) if ds else 1, "time": time.strftime("%Y-%m-%d %H:%M:%S"),
         "status": "pending", "room": room, "to": to, "thread": thread, "text": text, "why": why, "mentions": mentions}
    ds.append(d)
    jsave(DRAFTS, ds)
    out({"nháp": d["id"], "trạng thái": "chờ duyệt"})
    try:
        import workai_daemon as D
        D.toast(f"Nháp #{d['id']} chờ duyệt ({identity.NAME})", (f"{room or to}: " + text)[:200])
    except Exception:
        pass


def cmd_drafts(args):
    show_all = "--all" in args
    for d in jload(DRAFTS, []):
        if show_all or d["status"] == "pending":
            out(d)


def _find(i):
    ds = jload(DRAFTS, [])
    for d in ds:
        if d["id"] == int(i):
            return ds, d
    sys.exit(f"Không có nháp #{i}")


def cmd_send(args):
    expect = opt(args, "--expect")
    ds, d = _find(args[0])
    if not expect or not d["text"].lstrip().startswith(expect):
        sys.exit(f"Từ chối gửi: cần --expect \"<vài chữ đầu của nháp>\" khớp nháp #{d['id']} (nháp này bắt đầu bằng: {d['text'][:50]!r}). Đọc `drafts` rồi gửi đúng số.")
    if d["status"] != "pending":
        sys.exit(f"Nháp #{d['id']} đã {d['status']}")
    hc = HorusChat()
    tags = ["@" + m.lstrip("@").split(":")[0] for m in d.get("mentions") or []]
    tags = [t for t in tags if t not in d["text"]]
    if tags:  # nhắc ai thì chữ @tên (không :localhost, Hậu 2026-11-13) có trong tin; id đầy đủ đi trong danh sách mentions để app báo
        d["text"] = " ".join(tags) + " " + d["text"]
    try:
        if d.get("to"):
            r = hc.call("POST", "/v1/developer/messages",
                        body={"user_id": d["to"], "body": d["text"], "msgtype": "m.text"}, idempotent=True)
        else:
            rid = hc.room_id(d["room"])
            b = {"body": d["text"], "msgtype": "m.text", "format": "markdown"}
            if d.get("thread"):
                b["thread_root_event_id"] = d["thread"]
            if d.get("mentions"):
                b["mentions"] = d["mentions"]
            r = hc.call("POST", f"/v1/developer/rooms/{q(rid)}/messages", body=b, idempotent=True)
    except HCError as e:
        sys.exit(f"Gửi lỗi: {e}")
    d["status"], d["sent_at"] = "sent", time.strftime("%Y-%m-%d %H:%M:%S")
    jsave(DRAFTS, ds)
    out({"đã gửi": d["id"], "event_id": (r or {}).get("event_id")})


def cmd_say(args):
    """Trả lời NGAY tin không liên quan công việc (người dùng cho phép 2026-11-13). Có ghi sổ + giới hạn tốc độ."""
    ds = jload(DRAFTS, [])
    recent = [d for d in ds if d.get("status") == "sent" and d.get("kind") == "chat"
              and time.time() - time.mktime(time.strptime(d["sent_at"], "%Y-%m-%d %H:%M:%S")) < 600]
    if len(recent) >= 6:
        sys.exit("Từ chối: đã tự trả lời 6 tin trong 10 phút, chờ bớt hoặc để người dùng xem.")
    room, text = opt(args, "--room"), opt(args, "--text")
    thread, why = opt(args, "--thread"), opt(args, "--why", "")
    mentions = [m.strip() for m in (opt(args, "--mention", "") or "").split(",") if m.strip()]
    if not room or not text:
        sys.exit("Cần --room và --text")
    d = {"id": (max([x["id"] for x in ds]) + 1) if ds else 1, "time": time.strftime("%Y-%m-%d %H:%M:%S"),
         "status": "pending", "kind": "chat", "room": room, "to": None, "thread": thread, "text": text,
         "why": why, "mentions": mentions}
    ds.append(d)
    jsave(DRAFTS, ds)
    cmd_send([str(d["id"]), "--expect", text.lstrip()[:20]])


def cmd_who(args):
    """Tìm user_id theo tên: who <tên> (tìm trong danh bạ HorusChat)"""
    name = " ".join(args)
    if not name:
        sys.exit("Cần tên: who <tên>")
    r = HorusChat().get("/v1/developer/users", q=name, limit=10)
    for u in r.get("users") or r.get("results") or []:
        out({k: u.get(k) for k in ("user_id", "display_name", "email") if u.get(k)})


def cmd_download(args):
    """Tải file đính kèm: download --room <phòng> --event <event_id> --out <thư mục> [--url mxc://... ] [--name tên]"""
    from pathlib import Path
    room, ev, outdir = opt(args, "--room"), opt(args, "--event"), opt(args, "--out")
    url, name = opt(args, "--url"), opt(args, "--name", "")
    if not (room and ev and outdir):
        sys.exit("Cần --room --event --out")
    hc = HorusChat()
    rid = hc.room_id(room)
    if not url:
        e = hc.get(f"/v1/developer/rooms/{q(rid)}/events/{q(ev)}")
        at = (slim(e).get("attachments") or [])
        if not at:
            sys.exit("Tin không có file đính kèm")
        url = at[0].get("media_id") or at[0].get("url") or at[0].get("mxc_url") or at[0].get("media_url") or ""
    if not url.startswith("mxc://"):
        sys.exit(f"Không thấy mxc:// của file (có: {url!r}); truyền --url")
    server, media = url[6:].split("/", 1)
    data, headers = hc.call("GET", f"/v1/developer/media/{q(server)}/{q(media)}",
                            params={"room_id": rid, "event_id": ev}, raw=True, timeout=180)
    cd = headers.get("Content-Disposition") or headers.get("content-disposition") or ""
    if not name and "filename=" in cd:
        name = cd.split("filename=", 1)[1].strip('"; ')
    o = Path(outdir)
    o.mkdir(parents=True, exist_ok=True)
    f = o / Path(name or media).name
    f.write_bytes(data)
    out({"path": str(f), "bytes": len(data)})


def cmd_sendfile(args):
    """Gửi file vào phòng (đúng một file, tối đa 10 MiB): sendfile --room <phòng> --file <đường dẫn> [--text chú thích] [--thread id] [--mention @a:host,..]
    CHỈ chạy khi người dùng đã nói rõ gửi file đó."""
    import mimetypes, uuid, urllib.request, urllib.error
    from pathlib import Path
    room, fp = opt(args, "--room"), opt(args, "--file")
    text, thread = opt(args, "--text", ""), opt(args, "--thread")
    mentions = [m.strip() for m in (opt(args, "--mention", "") or "").split(",") if m.strip()]
    if not room or not fp or not Path(fp).is_file():
        sys.exit("Cần --room và --file (file phải tồn tại)")
    f = Path(fp)
    cap = float(opt(args, "--max-mib", "10"))   # mặc định 10 MiB; chỉ nâng khi người dùng đã nói rõ gửi file lớn (máy chủ vẫn có thể từ chối)
    if f.stat().st_size > cap * 1024 * 1024:
        sys.exit("File quá %g MiB (nâng bằng --max-mib khi người dùng đồng ý)" % cap)
    hc = HorusChat()
    hc.check()
    rid = hc.room_id(room)
    tags = ["@" + m.lstrip("@").split(":")[0] for m in mentions]
    tags = [t for t in tags if t not in text]
    if tags and text:
        text = " ".join(tags) + " " + text
    fields = {"body": text}
    if thread:
        fields["thread_root_event_id"] = thread
    if mentions:
        fields["mentions"] = json.dumps(mentions)
    b = "----hc" + uuid.uuid4().hex
    CRLF = "\r\n"
    parts = []
    for k, v in fields.items():
        if v:
            parts.append(f'--{b}{CRLF}Content-Disposition: form-data; name="{k}"{CRLF}{CRLF}{v}{CRLF}'.encode("utf8"))
    ct = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
    parts.append(f'--{b}{CRLF}Content-Disposition: form-data; name="file"; filename="{f.name}"{CRLF}Content-Type: {ct}{CRLF}{CRLF}'.encode("utf8"))
    parts.append(f.read_bytes())
    parts.append(f"{CRLF}--{b}--{CRLF}".encode())
    req = urllib.request.Request(f"{hc.url}/v1/developer/rooms/{q(rid)}/messages", data=b"".join(parts), method="POST")
    req.add_header("Authorization", "Bearer " + hc.key)
    req.add_header("Content-Type", f"multipart/form-data; boundary={b}")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "AI-Animation-horuschat/1.0")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            o = json.loads(r.read().decode("utf8") or "{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"Gửi file lỗi {e.code}: {e.read().decode('utf8', 'ignore')[:300]}")
    out({"đã gửi file": f.name, "event_id": (o.get("event_id") or (o.get("data") or {}).get("event_id")), "raw": str(o)[:200]})


def cmd_reject(args):
    ds, d = _find(args[0])
    d["status"], d["reject_reason"] = "rejected", " ".join(args[1:])
    jsave(DRAFTS, ds)
    out({"đã bỏ": d["id"]})


CMDS = {"wait": cmd_wait, "rooms": cmd_rooms, "history": cmd_history, "draft": cmd_draft,
        "drafts": cmd_drafts, "send": cmd_send, "say": cmd_say, "who": cmd_who, "download": cmd_download, "sendfile": cmd_sendfile, "reject": cmd_reject}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a or a[0] not in CMDS:
        sys.exit(__doc__)
    try:
        CMDS[a[0]](a[1:])
    except HCError as e:
        sys.exit(f"HorusChat lỗi: {e}")
