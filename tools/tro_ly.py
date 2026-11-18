"""Trợ lý cá nhân của Hậu: bật / tắt / trạng thái, kênh trao đổi với chủ qua phòng "You (yourself)" trên HorusChat, sổ việc cá nhân.

Trợ lý là một phiên Paseo tên `tro-ly`, chạy bằng danh tính `haunv` (tài khoản của chủ), đọc brief tools/subsession/briefs/tro_ly_ca_nhan.md.
Mọi lệnh ở đây luôn dùng danh tính haunv (không phụ thuộc tools/.profile).

  python -I tools/assistant.py on [--no-daemons] [--quiet]   # bật: xoá cờ tắt, bật bộ canh nền haunv, tạo / đánh thức phiên trợ lý, báo vào You
  python -I tools/assistant.py off [--daemons] [--quiet]     # tắt: đặt cờ tắt, dừng phiên trợ lý (--daemons: dừng luôn 2 bộ canh nền haunv)
  python -I tools/assistant.py status                        # đang bật / tắt, phiên, bộ canh, phòng You, thiếu khoá nào

  python -I tools/assistant.py room [--set <room_id>]        # phòng You (tự tìm + kiểm chỉ có một mình chủ; --set để chỉ tay)
  python -I tools/assistant.py wait [--timeout 60]           # chờ tin MỚI của chủ trong You, in mỗi tin một dòng JSON (tin có 🤖 đầu dòng là của trợ lý, bỏ qua)
  python -I tools/assistant.py say --text "..." [--thread <event_id>]   # trợ lý nhắn chủ trong You (tự thêm 🤖 đầu tin, tối đa 12 tin / 10 phút)
  python -I tools/assistant.py history [--limit 20]          # đọc lại You

  python -I tools/assistant.py todo add "<việc>" [--due YYYY-MM-DD] [--src "<nguồn: chat / workai / chủ>"] [--ref "<event_id / mission / thẻ jobs>"]
  python -I tools/assistant.py todo ls [--all]               # việc đang mở (xếp theo hạn)
  python -I tools/assistant.py todo done|drop <id>
  python -I tools/assistant.py todo note <id> "<ghi chú>"

Cờ tắt: work/store/_sys/watch/tro_ly_off (có file = tắt; ensure / systemd cũng tôn trọng). Mốc + phòng: tro_ly.json cùng thư mục. Sổ việc: work/assistant/todo.json.
"""
import json, os, signal, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _owner():
    """Danh tính của chủ trợ lý: biến TRO_LY_OWNER > file tools/.tro_ly_owner (riêng từng máy, git-ignored) > haunv."""
    v = os.environ.get("TRO_LY_OWNER", "").strip()
    if not v:
        try:
            v = open(os.path.join(ROOT, "tools", ".tro_ly_owner"), encoding="utf8").read().strip()
        except OSError:
            pass
    return (v or "haunv").lower()


OWNER = _owner()
OWNER_NAME = "Hậu" if OWNER == "haunv" else OWNER  # tên gọi chủ trong brief / tin nhắn
os.environ["AI_PROFILE"] = OWNER  # trước khi nạp identity / client
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "horuschat_mcp"))
import identity  # noqa: E402,F401
from horuschat_mcp.client import HCError, HorusChat, q, slim, ENV_FILE  # noqa: E402

DIR = os.path.join(ROOT, "work", "store", "_sys", "watch")
OFF = os.path.join(DIR, "tro_ly_off")
STATE = os.path.join(DIR, "tro_ly.json")
TODO = os.path.join(ROOT, "work", "assistant", "todo.json")
NAME = "tro-ly"
MARK = "🤖"
BRIEF = os.path.join(ROOT, "tools", "subsession", "briefs", "tro_ly_ca_nhan.md")
WORKAI_ENV = os.path.join(ROOT, "tools", "workai", ".env." + OWNER)
DAEMONS = {  # haunv giữ tên file gốc, danh tính khác có hậu tố _<tên> (identity.state_path)
    "horuschat": ("horuschat_daemon.py", identity.state_path(os.path.join(DIR, "horuschat_daemon.lock"))),
    "workai": ("workai_daemon.py", identity.state_path(os.path.join(DIR, "workai_daemon.lock"))),
}
NUDGE = ("Phiên vừa được bật lại. Tiếp tục vai trợ lý cá nhân: chạy tro_ly.py todo ls, rồi vòng lặp tro_ly.py wait kèm "
         "kiểm hộp thư " + OWNER + " như brief. Không trả lời lại tin cũ đã xử lý.")


def out(o):
    print(json.dumps(o, ensure_ascii=False))


def opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        v = args[i + 1] if i + 1 < len(args) else default
        del args[i:i + 2]
        return v
    return default


def flag(args, name):
    if name in args:
        args.remove(name)
        return True
    return False


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


def pid_alive(pid):
    if os.name == "nt":
        o = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
        return str(pid) in o
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except OSError:
        return True


def daemon_pid(lock):
    try:
        pid = int(open(lock).read().strip())
        return pid if pid_alive(pid) else None
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------- phòng You
def verify_room(hc, rid, me_id):
    """Phòng You hợp lệ = chỉ một mình chủ, không mã hoá. Trả (ok, lý do)."""
    info = hc.get(f"/v1/developer/rooms/{q(rid)}")
    if info.get("encrypted"):
        return False, "phòng mã hoá, API không đọc được"
    mem = hc.get(f"/v1/developer/rooms/{q(rid)}/members", limit=50).get("members", [])
    ids = {m.get("user_id") or m.get("id") for m in mem}
    ids.discard(None)
    if ids and ids != {me_id}:
        return False, f"phòng có người khác: {len(ids)} thành viên"
    if not ids and info.get("member_count", 1) != 1:
        return False, "phòng không phải chỉ mình chủ"
    return True, ""


def self_room(hc, set_to=None):
    me = hc.me().get("user_id")
    st = jload(STATE, {})
    if set_to:
        ok, why = verify_room(hc, hc.room_id(set_to), me)
        if not ok:
            sys.exit(f"Không dùng được phòng này: {why}")
        st["room_id"] = hc.room_id(set_to)
        jsave(STATE, st)
        return st["room_id"], me
    rid = st.get("room_id")
    if rid:
        ok, why = verify_room(hc, rid, me)  # kiểm lại mỗi lần: nếu có người được mời vào thì dừng ngay
        if not ok:
            sys.exit(f"Phòng You không an toàn nữa ({why}): trợ lý dừng đọc / nhắn ở đó.")
        return rid, me
    names = ("you", "you (yourself)", "yourself", "bạn", "bạn (chính bạn)")
    cands = [r for r in hc.rooms(refresh=True) if (r.get("name") or "").strip().lower() in names]
    for r in cands:
        ok, _ = verify_room(hc, r["room_id"], me)
        if ok:
            st["room_id"] = r["room_id"]
            jsave(STATE, st)
            return r["room_id"], me
    sys.exit("Chưa tìm thấy phòng You (phòng chỉ có mình bạn). Mở HorusChat tạo / nhắn vào \"You (yourself)\" một tin, "
             "hoặc chỉ tay: tro_ly.py room --set <room_id>  (xem phòng: horuschat_cli.py --profile <chủ> rooms)")


def owner_msgs(hc, rid, limit=50):
    r = hc.get(f"/v1/developer/rooms/{q(rid)}/history", limit=limit)
    evs = [slim(e) for e in (r.get("events") or r.get("messages") or [])]
    evs.reverse()  # cũ → mới
    return [e for e in evs if e.get("text") is not None]


def cmd_room(args):
    hc = HorusChat()
    rid, me = self_room(hc, opt(args, "--set"))
    out({"room_id": rid, "chủ": me})


def cmd_wait(args):
    timeout = float(opt(args, "--timeout", 60))
    hc = HorusChat()
    rid, _ = self_room(hc)
    st = jload(STATE, {})
    t0 = time.time()
    while True:
        evs = owner_msgs(hc, rid)
        seen = st.get("seen")
        if seen is None:  # lần đầu: coi mọi tin có sẵn là đã xử lý
            st["seen"] = [e["event_id"] for e in evs][-200:]
            jsave(STATE, st)
            seen = st["seen"]
        new = [e for e in evs if e["event_id"] not in seen]
        if new:
            st["seen"] = (seen + [e["event_id"] for e in new])[-200:]
            jsave(STATE, st)
            mine = [e for e in new if not (e.get("text") or "").lstrip().startswith(MARK)]
            for e in mine:
                row = {"time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime((e.get("ts") or 0) / 1000)),
                       "event_id": e["event_id"], "text": e.get("text")}
                for k in ("thread", "reply", "attachments"):
                    if e.get(k):
                        row[k] = e[k]
                out(row)
            if mine:
                return
        if time.time() - t0 >= timeout:
            print("(không có tin mới)")
            return
        time.sleep(4)


def cmd_history(args):
    limit = int(opt(args, "--limit", 20))
    hc = HorusChat()
    rid, _ = self_room(hc)
    for e in owner_msgs(hc, rid, max(1, min(limit, 100)))[-limit:]:
        t = (e.get("text") or "")
        out({"event_id": e["event_id"], "của": "trợ lý" if t.lstrip().startswith(MARK) else "chủ",
             "text": t[:400]})


def say_text(hc, rid, text, thread=None):
    st = jload(STATE, {})
    now = time.time()
    sent = [t for t in st.get("sent", []) if now - t < 600]
    if len(sent) >= 12:
        raise SystemExit("Từ chối: đã nhắn 12 tin trong 10 phút, gộp lại thành một tin hoặc chờ.")
    body = MARK + " " + text.strip()
    if len(body) > 3500:
        body = body[:3480] + "\n…(cắt bớt)"
    b = {"body": body, "msgtype": "m.text", "format": "markdown"}
    if thread:
        b["thread_root_event_id"] = thread
    r = hc.call("POST", f"/v1/developer/rooms/{q(rid)}/messages", body=b, idempotent=True)
    st["sent"] = sent + [now]
    st["seen"] = (st.get("seen") or [])[-200:] + ([r.get("event_id")] if r.get("event_id") else [])
    jsave(STATE, st)
    return (r or {}).get("event_id")


def cmd_say(args):
    text, thread = opt(args, "--text"), opt(args, "--thread")
    if not text:
        sys.exit("Cần --text")
    hc = HorusChat()
    rid, _ = self_room(hc)
    out({"đã nhắn": say_text(hc, rid, text, thread)})


# ---------------------------------------------------------------- bật / tắt
def agents():
    import paseo_cmd
    rc, o = paseo_cmd.run_paseo(["ls", "--json"])
    if rc != 0:
        return None
    try:
        d = json.loads(o or "[]")
    except ValueError:
        return None
    return d if isinstance(d, list) else d.get("agents", [])


def mine(ag):
    return [a for a in (ag or []) if a.get("name") == NAME and a.get("status") in ("running", "idle")]


def keys_missing():
    miss = []
    try:
        from horuschat_mcp.client import load_env
        if not load_env().get("HORUSCHAT_API_KEY"):
            miss.append(f"HorusChat (điền HORUSCHAT_API_KEY vào tools/horuschat_mcp/.env.{OWNER})")
    except Exception:
        miss.append("HorusChat")
    ok = False
    try:
        for line in open(WORKAI_ENV, encoding="utf8"):
            if line.strip().startswith("WORKAI_TOKEN=") and line.split("=", 1)[1].strip().strip("\"'"):
                ok = True
    except OSError:
        pass
    if not ok:
        miss.append(f"WorkAI (điền WORKAI_TOKEN vào tools/workai/.env.{OWNER})")
    return miss


def start_daemons():
    started = []
    for key, (script, lock) in DAEMONS.items():
        if daemon_pid(lock):
            continue
        cmd = [sys.executable, "-I", os.path.join(ROOT, "tools", script), "--profile", OWNER]
        kw = {"creationflags": 0x08000000} if os.name == "nt" else {"start_new_session": True}
        subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)
        started.append(key)
    return started


def stop_daemons():
    stopped = []
    for key, (_, lock) in DAEMONS.items():
        pid = daemon_pid(lock)
        if pid:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
            stopped.append(key)
    return stopped


def ensure_session():
    import paseo_cmd
    ag = agents()
    if ag is None:
        return "Paseo chưa chạy (mở app Paseo hoặc `paseo start`)"
    live = mine(ag)
    if any(a["status"] == "running" for a in live):
        return "đang chạy: " + live[0]["shortId"]
    if live:
        paseo_cmd.run_paseo(["send", "--no-wait", live[0]["shortId"], NUDGE])
        return "đã đánh thức: " + live[0]["shortId"]
    body = open(BRIEF, encoding="utf-8").read().replace("assistant.py", "tro_ly.py")
    body = body.replace("haunv", OWNER).replace("Hậu", OWNER_NAME)
    if os.name != "nt":
        body = ("> Máy Linux: thay mọi `.venv/Scripts/python.exe` bằng `python3` (vẫn có -I). Dự án: %s.\n\n" % ROOT
                + body.replace(".venv/Scripts/python.exe", "python3"))
    tmp = os.path.join(ROOT, "work", "_subsessions", "tro-ly-body.md")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    open(tmp, "w", encoding="utf-8").write(body)
    p = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "paseo_cmd.py"), "run", NAME, "@" + tmp],
                       capture_output=True, text=True, timeout=120)
    return "đã tạo phiên mới: " + (p.stdout + p.stderr).strip()[-200:]


def try_say(text):
    try:
        hc = HorusChat()
        rid, _ = self_room(hc)
        say_text(hc, rid, text)
        return True
    except (HCError, SystemExit):
        return False


def cmd_on(args):
    quiet, nod = flag(args, "--quiet"), flag(args, "--no-daemons")
    miss = keys_missing()
    if miss:
        sys.exit("Chưa bật được, thiếu khoá của tài khoản " + OWNER + ": " + "; ".join(miss) + ". (Không dán khoá vào chat, điền thẳng vào file.)")
    if os.path.exists(OFF):
        os.remove(OFF)
    d = [] if nod else start_daemons()
    s = ensure_session()
    if not quiet:
        try_say("Trợ lý đã bật. Nhắn mình ở đây (You); gõ \"tóm tắt\" để xem việc đang mở.")
    out({"bật": True, "bộ canh vừa chạy": d, "phiên": s})


def cmd_off(args):
    quiet, dae = flag(args, "--quiet"), flag(args, "--daemons")
    if not quiet:
        try_say("Trợ lý sắp tắt. Bật lại bằng /assistant_on.")
    os.makedirs(DIR, exist_ok=True)
    open(OFF, "w").write(time.strftime("%Y-%m-%d %H:%M:%S"))
    import paseo_cmd
    stopped = []
    for a in mine(agents()):
        paseo_cmd.run_paseo(["stop", a["shortId"]])
        stopped.append(a["shortId"])
    d = stop_daemons() if dae else []
    out({"tắt": True, "phiên đã dừng": stopped, "bộ canh đã dừng": d})


def cmd_status(args):
    ag = agents()
    live = mine(ag) if ag is not None else None
    r = {"cờ tắt": os.path.exists(OFF),
         "phiên": "Paseo chưa chạy" if live is None else ([f"{a['shortId']} {a['status']}" for a in live] or "chưa có"),
         "chủ": OWNER,
         "bộ canh nền": {k: bool(daemon_pid(l)) for k, (_, l) in DAEMONS.items()},
         "thiếu khoá": keys_missing() or "không"}
    try:
        rid, me = self_room(HorusChat())
        r["phòng You"] = rid
    except (HCError, SystemExit) as e:
        r["phòng You"] = "chưa dùng được: " + str(e)[:160]
    st = jload(STATE, {})
    r["việc mở"] = len([t for t in jload(TODO, []) if t.get("status") == "open"])
    out(r)


# ---------------------------------------------------------------- sổ việc
def cmd_todo(args):
    if not args:
        sys.exit(__doc__)
    sub, rest = args[0], args[1:]
    ts = jload(TODO, [])
    if sub == "add":
        due, src, ref = opt(rest, "--due"), opt(rest, "--src", ""), opt(rest, "--ref", "")
        if not rest:
            sys.exit('Cần tên việc: todo add "<việc>"')
        t = {"id": (max([x["id"] for x in ts]) + 1) if ts else 1, "title": rest[0], "due": due, "src": src, "ref": ref,
             "status": "open", "created": time.strftime("%Y-%m-%d %H:%M"), "notes": []}
        ts.append(t)
        jsave(TODO, ts)
        out(t)
    elif sub == "ls":
        show_all = flag(rest, "--all")
        rows = [t for t in ts if show_all or t.get("status") == "open"]
        rows.sort(key=lambda t: (t.get("due") or "9999", t["id"]))
        for t in rows:
            out({k: t.get(k) for k in ("id", "title", "due", "src", "ref", "status") if t.get(k)} | ({"ghi chú": t["notes"][-1]} if t.get("notes") else {}))
        if not rows:
            print("(không có việc mở)")
    elif sub in ("done", "drop", "note"):
        tid = int(rest[0])
        t = next((x for x in ts if x["id"] == tid), None)
        if not t:
            sys.exit(f"Không có việc #{tid}")
        if sub == "note":
            t.setdefault("notes", []).append(time.strftime("%m-%d %H:%M ") + " ".join(rest[1:]))
        else:
            t["status"] = "done" if sub == "done" else "dropped"
            t["closed"] = time.strftime("%Y-%m-%d %H:%M")
        jsave(TODO, ts)
        out({"id": tid, "trạng thái": t["status"]})
    else:
        sys.exit(__doc__)


CMDS = {"on": cmd_on, "off": cmd_off, "status": cmd_status, "room": cmd_room, "wait": cmd_wait, "say": cmd_say,
        "history": cmd_history, "todo": cmd_todo}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a or a[0] not in CMDS:
        sys.exit(__doc__)
    try:
        CMDS[a[0]](a[1:])
    except HCError as e:
        sys.exit(f"HorusChat lỗi: {e}")
