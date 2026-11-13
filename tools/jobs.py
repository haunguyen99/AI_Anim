"""Sổ thẻ việc cho order nhận qua HorusChat (quy trình: docs/quy_trinh_nhan_viec_horuschat.md).

Mỗi order một thẻ trong work/jobs/index.json (+ nhật ký work/jobs/<id>.md). Trạng thái: nhan -> ke-hoach -> lam -> demo -> phan-hoi -> giao -> dong (huy).

  python -I tools/jobs.py new <id> --title "..." --from @user:host --room <phòng> --thread <event_id gốc> [--event <event_id tin order>] [--file tên] [--project <tên dự án WorkAI>] [--note "..."]
  python -I tools/jobs.py ls [--all]                  # việc đang mở (hoặc tất cả)
  python -I tools/jobs.py get <id>
  python -I tools/jobs.py find --thread <event_id>     # tìm việc theo thread / tin: in id + phiên Paseo
  python -I tools/jobs.py set <id> <trạng thái> [--session <id Paseo>] [--note "..."]
  python -I tools/jobs.py log <id> "<ghi chú>"
  python -I tools/jobs.py start <id>                   # dựng brief từ mẫu + tạo phiên Paseo cho việc, ghi id phiên vào thẻ
  python -I tools/jobs.py access [--project <tên>]      # dự án WorkAI mà tài khoản AI đang thuộc (có --project: báo CÓ / CHƯA)
  python -I tools/jobs.py ask-add <id>                  # AI chưa thuộc dự án của order: nhắn người order / PM trong thread xin add (chỉ hỏi một lần)
  python -I tools/jobs.py say <id> --text "..." [--file <đường dẫn>] [--tag-hau]   # gửi vào ĐÚNG thread của order (tag người order; --tag-hau tag thêm Hậu)

`say` chỉ gửi được vào thread / phòng ghi trong thẻ (phiên làm việc không gửi lung tung được). Danh tính HorusChat theo tools/identity.py.
"""
import json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import identity  # noqa: E402
JOBS = os.path.join(ROOT, "work", "jobs")
INDEX = os.path.join(JOBS, "index.json")
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
STATUSES = ("nhan", "ke-hoach", "lam", "demo", "phan-hoi", "giao", "dong", "huy")
OPEN = ("nhan", "ke-hoach", "lam", "demo", "phan-hoi", "giao")
HAU = "@haunv:localhost"


def load():
    try:
        return json.load(open(INDEX, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def save(d):
    os.makedirs(JOBS, exist_ok=True)
    tmp = INDEX + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    os.replace(tmp, INDEX)


def opt(a, name, default=None):
    if name in a:
        i = a.index(name)
        v = a[i + 1] if i + 1 < len(a) else default
        del a[i:i + 2]
        return v
    return default


def log(jid, text):
    os.makedirs(JOBS, exist_ok=True)
    with open(os.path.join(JOBS, jid + ".md"), "a", encoding="utf8") as f:
        f.write(f"- {time.strftime('%Y-%m-%d %H:%M')} {text}\n")


def need(d, jid):
    if jid not in d:
        sys.exit(f"Không có việc '{jid}'. Dùng: jobs.py ls --all")
    return d[jid]


def out(o):
    print(json.dumps(o, ensure_ascii=False))


def wa_projects():
    """Dự án WorkAI mà tài khoản đang dùng (theo tools/identity.py) thấy được: [{id, name}]."""
    p = subprocess.run([PY, "-I", os.path.join(ROOT, "tools", "workai", "workai.py"), "get", "api/projects?per_page=100"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
    txt = p.stdout or ""
    try:
        o = json.loads(txt[txt.index("{"):])
    except (ValueError, json.JSONDecodeError):
        return None
    rows = o.get("data") or []
    return [{"id": r.get("id"), "name": r.get("name") or r.get("title")} for r in rows if isinstance(r, dict)]


def has_project(rows, name):
    n = (name or "").strip().lower()
    return bool(n) and any(n in (r.get("name") or "").lower() or n == str(r.get("id")) for r in rows or [])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd, a = a[0], a[1:]
    d = load()
    if cmd == "new":
        if not a:
            sys.exit("new <id> ...")
        jid = a.pop(0)
        if jid in d:
            sys.exit(f"Việc '{jid}' đã có (không tạo trùng): trạng thái {d[jid]['status']}, phiên {d[jid].get('session')}")
        card = {"id": jid, "title": opt(a, "--title", jid), "from": opt(a, "--from"), "room": opt(a, "--room"),
                "thread": opt(a, "--thread"), "event": opt(a, "--event"), "file": opt(a, "--file"),
                "project": opt(a, "--project"), "status": "nhan", "session": None,
                "created": time.strftime("%Y-%m-%d %H:%M"), "workai_issue": None, "workai_asked": None}
        if not (card["from"] and card["room"] and card["thread"]):
            sys.exit("Cần --from --room --thread")
        d[jid] = card
        save(d)
        log(jid, f"Nhận việc từ {card['from']}: {card['title']}" + (f" ({opt(a, '--note')})" if "--note" in a else ""))
        out(card)
    elif cmd == "ls":
        for jid, c in d.items():
            if "--all" in a or c["status"] in OPEN:
                out({k: c.get(k) for k in ("id", "status", "title", "from", "session", "thread")})
    elif cmd == "get":
        out(need(d, a[0]))
    elif cmd == "find":
        t = opt(a, "--thread")
        for jid, c in d.items():
            if t and t in (c.get("thread"), c.get("event")) and c["status"] in OPEN + ("dong",):
                out({"id": jid, "status": c["status"], "session": c.get("session"), "from": c["from"]})
                return
        print("(không có việc khớp)")
    elif cmd == "set":
        jid, st = a[0], a[1]
        a = a[2:]
        c = need(d, jid)
        if st not in STATUSES:
            sys.exit(f"Trạng thái hợp lệ: {STATUSES}")
        c["status"] = st
        s = opt(a, "--session")
        if s:
            c["session"] = s
        save(d)
        log(jid, f"Trạng thái -> {st}" + (f": {opt(a, '--note')}" if "--note" in a else ""))
        out(c)
    elif cmd == "log":
        need(d, a[0])
        log(a[0], " ".join(a[1:]))
    elif cmd == "start":
        jid = a[0]
        c = need(d, jid)
        tpl = open(os.path.join(ROOT, "tools", "subsession", "briefs", "job_template.md"), encoding="utf8").read()
        body = tpl
        for k, v in (("{ID}", jid), ("{TITLE}", c["title"]), ("{FROM}", c["from"] or ""), ("{ROOM}", c["room"] or ""),
                     ("{THREAD}", c["thread"] or ""), ("{EVENT}", c.get("event") or ""), ("{FILE}", c.get("file") or "(không có)")):
            body = body.replace(k, v)
        os.makedirs(JOBS, exist_ok=True)
        bp = os.path.join(JOBS, jid + ".brief.md")
        open(bp, "w", encoding="utf8").write(body)
        p = subprocess.run([PY, "-I", os.path.join(ROOT, "tools", "paseo_cmd.py"), "run", jid, "@" + bp],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
        txt = (p.stdout or "") + (p.stderr or "")
        print(txt.strip())
        import re
        m = re.search(r"id ([0-9a-f]{7})", txt)
        if m:
            c["session"] = m.group(1)
            save(d)
            log(jid, f"Mở phiên Paseo {m.group(1)}")
        else:
            sys.exit(1)
    elif cmd == "access":
        proj = opt(a, "--project")
        rows = wa_projects()
        if rows is None:
            sys.exit("Không đọc được danh sách dự án WorkAI (kiểm token / danh tính).")
        if proj:
            print("CÓ" if has_project(rows, proj) else "CHƯA", "-", proj)
        out({"danh_tinh": identity.NAME, "so_du_an": len(rows), "du_an": rows[:30]})
    elif cmd == "ask-add":
        jid = a[0]
        c = need(d, jid)
        rows = wa_projects()
        if rows is None:
            sys.exit("Không đọc được danh sách dự án WorkAI.")
        proj = c.get("project")
        if proj and has_project(rows, proj):
            print("Đã có quyền trong dự án", proj)
            return
        if c.get("workai_asked"):
            print("Đã xin add lúc", c["workai_asked"], "- không hỏi lại")
            return
        where = f"dự án {proj}" if proj else "dự án của việc này"
        text = (f"Mình chưa thuộc {where} trên WorkAI nên chưa cập nhật tiến độ được. "
                f"Bạn hoặc PM của dự án add giúp tài khoản AI Animation (animationa@horusvn.com) vào dự án nhé, "
                f"và cho mình biết tên dự án nếu mình chưa ghi đúng.")
        args = [PY, "-I", os.path.join(ROOT, "tools", "horuschat_cli.py"), "say", "--room", c["room"], "--thread", c["thread"],
                "--mention", c["from"], "--text", text, "--why", f"việc {jid}: xin add vào dự án WorkAI"]
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
        print((p.stdout or "").strip() or (p.stderr or "").strip())
        if p.returncode == 0:
            c["workai_asked"] = time.strftime("%Y-%m-%d %H:%M")
            save(d)
            log(jid, "Đã xin PM add AI Animation vào dự án WorkAI")
        else:
            sys.exit(p.returncode)
    elif cmd == "say":
        jid = a.pop(0)
        c = need(d, jid)
        text, fp = opt(a, "--text", ""), opt(a, "--file")
        tag_hau = "--tag-hau" in a
        mentions = [m for m in (c.get("from"), HAU if tag_hau else None) if m]
        base = [PY, "-I", os.path.join(ROOT, "tools", "horuschat_cli.py")]
        if fp:
            args = base + ["sendfile", "--room", c["room"], "--thread", c["thread"], "--file", fp, "--mention", ",".join(mentions)]
            if text:
                args += ["--text", text]
        else:
            if not text:
                sys.exit("Cần --text hoặc --file")
            args = base + ["say", "--room", c["room"], "--thread", c["thread"], "--mention", ",".join(mentions),
                           "--text", text, "--why", f"việc {jid}"]
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
        print((p.stdout or "").strip() or (p.stderr or "").strip())
        if p.returncode == 0:
            log(jid, "Đã gửi vào thread" + (f" (file {os.path.basename(fp)})" if fp else "") + ": " + (text[:120] if text else ""))
        else:
            sys.exit(p.returncode)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
