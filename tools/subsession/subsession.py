"""Phiên con cho Claude Code (VS Code / terminal / app): giao việc cho phiên nền `claude --bg`,
theo dõi, nhắn thêm, nhận báo cáo. Thiết kế: docs/vscode_subsessions_design.md

Chạy:  .venv/Scripts/python.exe -I tools/subsession/subsession.py <lệnh> ...
  start --name N (--brief "text" | --brief @file) [--files a,b] [--parent ID] [--max N]
  list [--all]            bảng phiên con
  tree                    cây cha → con + câu đầu báo cáo
  log ID [--lines 40]     đầu ra gần nhất (claude logs)
  send ID "tin nhắn"      việc thêm (resume nền); phiên đang chạy dở thì xếp hàng
  wait ID [--timeout 7200]  chạy nền: kết thúc khi có báo cáo / phiên thoát / hết giờ
  stop ID                 dừng (giữ hội thoại)
  done ID                 (phiên con gọi) đánh dấu xong, đọc report.md
ID = id đầy đủ hoặc tên (--name).
"""
import argparse, json, os, re, shutil, subprocess, sys, time, uuid
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
REG = Path(__file__).with_name("registry.json")
DIR = ROOT / "work" / "_subsessions"
MAX_RUNNING = 4
ISOLATION = '{"worktree":{"bgIsolation":"none"}}'  # ghi thẳng vào checkout chung (phạm vi theo brief)
# Phiên nền không hỏi quyền được: cho sẵn tool đọc/sửa file + lệnh báo cáo. Việc cần thêm: --allow "Bash(git status*);..."
BASE_TOOLS = ["Read", "Glob", "Grep", "Edit", "Write", "Bash(.venv/Scripts/python.exe -I tools/subsession/subsession.py done*)"]
CLAUDE = shutil.which("claude") or "claude"

RULES = """
---
LUẬT PHIÊN CON (bắt buộc)
- Chỉ sửa file trong phạm vi brief. Không commit, không đổi nhánh, không đẩy GitHub.
- Không ghi key/token vào file hay báo cáo. Trả lời tiếng Việt.
- Khi xong, hoặc bị chặn cần người dùng trả lời: ghi {report}
  dòng đầu `XONG: <một câu>` hoặc `CHẶN: <câu hỏi>`, các dòng sau là chi tiết (file đã sửa, cách kiểm).
  Rồi chạy: .venv/Scripts/python.exe -I tools/subsession/subsession.py done {id}
"""


def load():
    return json.loads(REG.read_text("utf-8")) if REG.exists() else {}


def save(r):
    REG.write_text(json.dumps(r, ensure_ascii=False, indent=1), "utf-8")


def find(r, key):
    if key in r:
        return key
    m = [k for k, v in r.items() if v["name"] == key or k.startswith(key)]
    if len(m) != 1:
        sys.exit(f"không tìm thấy / không rõ phiên '{key}'")
    return m[0]


def agents():
    p = subprocess.run([CLAUDE, "agents", "--json", "--all"], capture_output=True, text=True,
                       encoding="utf-8", cwd=ROOT)
    try:
        return {a["sessionId"]: a for a in json.loads(p.stdout)}
    except Exception:
        return {}


def status(r, sid, ag=None):
    """chạy / chờ / kẹt (chờ duyệt quyền) / xong / chặn / dừng / thoát"""
    v = r[sid]
    rep = DIR / sid / "report.md"
    if v.get("done") and rep.exists():
        return "chặn" if rep.read_text("utf-8").lstrip().startswith("CHẶN") else "xong"
    if v.get("stopped"):
        return "dừng"
    a = (ag if ag is not None else agents()).get(v.get("cid"))
    if a is None:
        return "thoát"
    st = a.get("state") or a.get("status")
    if st == "blocked":
        return "kẹt"  # đang chờ duyệt quyền/hộp thoại: cần `log` / `attach`
    return "chờ" if st in ("idle", "done", "exited") else "chạy"


def first_line(sid):
    rep = DIR / sid / "report.md"
    return rep.read_text("utf-8").strip().splitlines()[0] if rep.exists() and rep.read_text("utf-8").strip() else ""


def running(r):
    ag = agents()
    return [k for k in r if status(r, k, ag) in ("chạy", "chờ", "kẹt") and not r[k].get("done")]


def cmd_start(a):
    r = load()
    brief = Path(a.brief[1:]).read_text("utf-8") if a.brief.startswith("@") else a.brief
    files = [f.strip() for f in (a.files or "").split(",") if f.strip()]
    act = running(r)
    if len(act) >= a.max:
        sys.exit(f"đã có {len(act)} phiên con đang chạy (tối đa {a.max}): {[r[k]['name'] for k in act]}")
    for k in act:
        dup = set(files) & set(r[k].get("files", []))
        if dup:
            print(f"CẢNH BÁO: file trùng với phiên '{r[k]['name']}': {sorted(dup)}", file=sys.stderr)
    sid = str(uuid.uuid4())
    d = DIR / sid
    d.mkdir(parents=True)
    rep = d / "report.md"
    (d / "brief.md").write_text(brief + RULES.format(report=rep.relative_to(ROOT).as_posix(), id=sid), "utf-8")
    tools = BASE_TOOLS + [t for t in (a.allow or "").split(";") if t.strip()]
    prompt = f"Bạn là phiên con. Đọc {(d / 'brief.md').relative_to(ROOT).as_posix()} rồi làm đúng theo đó."
    p = subprocess.run([CLAUDE, "--bg", "--name", a.name, prompt, "--strict-mcp-config", "--settings", ISOLATION, "--allowedTools", ",".join(tools)],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    m = re.search(r"backgrounded\W+([0-9a-f]{8})", p.stdout + p.stderr)
    if p.returncode or not m:
        sys.exit("claude --bg lỗi: " + p.stdout + p.stderr)
    full = next((k for k in agents() if k.startswith(m.group(1))), m.group(1))
    r[sid] = dict(cid=full, name=a.name, parent=a.parent, files=files, cwd=str(ROOT), started=time.time(), done=False)
    save(r)
    print("ID:", sid, "| claude:", full[:8])


def cmd_list(a):
    r = load()
    ag = agents()
    for k, v in r.items():
        s = status(r, k, ag)
        if a.all or s in ("chạy", "chờ", "chặn", "kẹt"):
            print(f"{k[:8]}  {s:6} {v['name']}  {first_line(k)}")


def cmd_tree(a):
    r = load()
    ag = agents()

    def show(pid, depth):
        for k, v in r.items():
            if (v.get("parent") or None) == pid:
                print("  " * depth + f"- {v['name']} [{k[:8]}] {status(r, k, ag)} {first_line(k)}")
                show(k, depth + 1)
    show(None, 0)


def cmd_log(a):
    sid = find(load(), a.id)
    p = subprocess.run([CLAUDE, "logs", load()[sid]["cid"][:8]], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    txt = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", p.stdout + p.stderr)
    print("\n".join([l.rstrip() for l in txt.splitlines() if l.strip()][-a.lines:]))


def resume_bg(r, sid, msg):
    """nhắn thêm: --resume --bg; nếu bản cũ còn mở thì claude tạo bản sao id mới -> theo bản sao, dừng bản cũ"""
    old = r[sid]["cid"]
    p = subprocess.run([CLAUDE, "--resume", old, "--bg", msg, "--strict-mcp-config", "--settings", ISOLATION,
                        "--allowedTools", ",".join(BASE_TOOLS)], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    m = re.search(r"backgrounded\W+([0-9a-f]{8})", p.stdout + p.stderr)
    if not m:
        sys.exit("resume lỗi: " + p.stdout + p.stderr)
    if not old.startswith(m.group(1)):
        r[sid]["cid"] = next((k for k in agents() if k.startswith(m.group(1))), m.group(1))
        subprocess.run([CLAUDE, "stop", old[:8]], capture_output=True, cwd=ROOT)
    save(r)
    return r[sid]["cid"][:8]


def cmd_send(a):
    r = load()
    sid = find(r, a.id)
    s = status(r, sid)
    r[sid]["done"] = False
    r[sid].pop("stopped", None)
    if s == "chạy":  # đang chạy dở: xếp hàng, gửi khi xong lượt (wait lo)
        r[sid].setdefault("queue", []).append(a.message)
        save(r)
        print("phiên đang chạy: đã xếp hàng, gửi khi xong lượt (chạy `wait`).")
        return
    rep = DIR / sid / "report.md"
    rep.unlink(missing_ok=True)
    msg = a.message + f"\n\n(Khi xong ghi lại {rep.relative_to(ROOT).as_posix()} và chạy `subsession.py done {sid}` như cũ.)"
    save(r)
    print("đã gửi, phiên claude:", resume_bg(r, sid, msg))


def cmd_wait(a):
    r = load()
    sid = find(r, a.id)
    t0 = time.time()
    while time.time() - t0 < a.timeout:
        r = load()
        s = status(r, sid)
        if s in ("xong", "chặn", "chờ") and r[sid].get("queue"):  # xong lượt: gửi tin xếp hàng, báo cáo cũ không còn đúng
            rep = DIR / sid / "report.md"
            msg = "\n\n".join(r[sid].pop("queue"))
            r[sid]["done"] = False
            rep.unlink(missing_ok=True)
            save(r)
            resume_bg(r, sid, msg + f"\n\n(Khi xong ghi lại {rep.relative_to(ROOT).as_posix()} và chạy `subsession.py done {sid}`.)")
        elif s in ("xong", "chặn"):
            print(f"[{s}] {r[sid]['name']}\n" + (DIR / sid / "report.md").read_text("utf-8"))
            return
        elif s == "kẹt":
            print("[kẹt] phiên chờ duyệt quyền. Log cuối:"); cmd_log(argparse.Namespace(id=sid, lines=30)); return
        elif s in ("thoát", "dừng"):
            print(f"[{s}] phiên thoát mà chưa có báo cáo. Log cuối:")
            cmd_log(argparse.Namespace(id=sid, lines=30))
            return
        time.sleep(10)
    print("[hết giờ] log cuối:")
    cmd_log(argparse.Namespace(id=sid, lines=30))


def cmd_stop(a):
    r = load()
    sid = find(r, a.id)
    subprocess.run([CLAUDE, "stop", r[sid]["cid"][:8]], cwd=ROOT)
    r[sid]["stopped"] = True
    save(r)


def cmd_done(a):
    r = load()
    sid = find(r, a.id)
    if not (DIR / sid / "report.md").exists():
        sys.exit("chưa có report.md: ghi báo cáo trước rồi mới `done`")
    r[sid]["done"] = True
    save(r)
    print("đã đánh dấu xong.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="c", required=True)
    s = sp.add_parser("start"); s.add_argument("--name", required=True); s.add_argument("--brief", required=True)
    s.add_argument("--files"); s.add_argument("--allow", help="thêm tool cho phép, ngăn bằng ;"); s.add_argument("--parent"); s.add_argument("--max", type=int, default=MAX_RUNNING)
    s.set_defaults(f=cmd_start)
    s = sp.add_parser("list"); s.add_argument("--all", action="store_true"); s.set_defaults(f=cmd_list)
    sp.add_parser("tree").set_defaults(f=cmd_tree)
    s = sp.add_parser("log"); s.add_argument("id"); s.add_argument("--lines", type=int, default=40); s.set_defaults(f=cmd_log)
    s = sp.add_parser("send"); s.add_argument("id"); s.add_argument("message"); s.set_defaults(f=cmd_send)
    s = sp.add_parser("wait"); s.add_argument("id"); s.add_argument("--timeout", type=int, default=7200); s.set_defaults(f=cmd_wait)
    s = sp.add_parser("stop"); s.add_argument("id"); s.set_defaults(f=cmd_stop)
    s = sp.add_parser("done"); s.add_argument("id"); s.set_defaults(f=cmd_done)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
