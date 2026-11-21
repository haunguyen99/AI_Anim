"""Nhắc và tự đẩy KIẾN THỨC (skill, bộ nhớ Claude) lên GitHub main. Người dùng 2026-11-11.

  python tools/knowledge_sync.py check       in tình trạng: kiến thức chưa commit / chưa đẩy / GitHub có bản mới
  python tools/knowledge_sync.py hook        hook Claude Code (SessionStart + UserPromptSubmit): có việc thì nhắc Claude, im nếu không
  python tools/knowledge_sync.py autopush    chạy theo lịch Windows (tools/knowledge_sync_install.ps1): lưu + gộp + đẩy, không cần Claude

autopush chỉ đụng kiến thức (`.claude/skills`, `.claude/memory_store`, `tools/claude_memory.py`):
  1. `git fetch`; sao lưu bộ nhớ (`claude_memory.py backup`); commit file kiến thức đang sửa dở (chỉ đúng các file đó);
  2. gộp với GitHub bằng knowledge_merge: chỉ làm khi mọi file gộp được SẠCH (chỉ remote đổi, thêm mới, gộp 3 chiều sạch);
     có xung đột / không có gốc chung / nhị phân thì DỪNG, ghi "cần gộp tay" để phiên Claude sau báo người dùng;
  3. đẩy các file khác GitHub bằng push_source `--only … --committed` (không xoá gì trên GitHub, không kéo file làm dở).
Trạng thái + nhật ký: work/store/_sys/watch/knowledge_sync.json, knowledge_autopush.log. Không bao giờ chặn lượt chat (hook thoát 0)."""
import json, os, pathlib, subprocess, sys, time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import push_source as ps   # noqa: E402  (danh sách cho phép dùng chung; đổi thư mục chạy về gốc repo)
import knowledge_merge as km   # noqa: E402

R = pathlib.Path(ps.ROOT)
SCOPE = [".claude/skills", ".claude/memory_store", "tools/claude_memory.py",
         ".claude/usage"]   # số lần gọi công cụ: tự đẩy theo lịch, nhưng không nhắc (đổi sau mỗi lệnh)
USAGE = ".claude/usage/"
STATE = R / "work" / "store" / "_sys" / "watch" / "knowledge_sync.json"
LOG = STATE.with_name("knowledge_autopush.log")
PY = R / ".venv" / "Scripts" / "python.exe"
CHECK_EVERY, FETCH_EVERY, SHOW_EVERY = 20 * 60, 60 * 60, 60 * 60   # giây
norm = km.norm


def git(*a, timeout=60):
    return subprocess.run(["git", *a], cwd=R, capture_output=True, timeout=timeout, env=km.ENV)


def load():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")


def uncommitted():
    out = git("status", "--porcelain", "-z", "--untracked-files=all", "--", *SCOPE).stdout.decode("utf-8", "replace")
    files = []
    for e in out.split("\0"):
        if len(e) > 3 and ps.allowed(e[3:]):
            files.append(e[3:])
    return files


def tree(ref):
    o = git("ls-tree", "-r", ref, "--", *SCOPE).stdout.decode("utf-8", "replace")
    return {ln.split("\t", 1)[1]: ln.split("\t", 1)[0].split()[2] for ln in o.splitlines() if "\t" in ln}


def unpushed():
    """File kiến thức đã commit mà nội dung (bỏ qua CRLF/LF) khác bản trên origin/main."""
    head, rem = tree("HEAD"), tree("origin/main")
    out = []
    for f, h in head.items():
        if not ps.allowed(f) or rem.get(f) == h:
            continue
        if f in rem:
            a, b = km.show("HEAD", f), km.show("origin/main", f)
            if a is not None and b is not None and norm(a) == norm(b):
                continue
        out.append(f)
    return out


def remote_changed(state):
    """GitHub có commit mới đụng tới kiến thức kể từ lần cuối ta thấy / đẩy."""
    head = git("rev-parse", "origin/main").stdout.decode().strip()
    seen = state.get("last_seen_remote")
    if not seen or seen == head:
        return [], head
    names = git("diff", "--name-only", seen, head, "--", *SCOPE).stdout.decode("utf-8", "replace").split("\n")
    return [n for n in names if n and ps.allowed(n)], head


def report(state, fetch=False):
    if fetch:
        try:
            git("fetch", "origin", "main", timeout=15)
            state["last_fetch"] = time.time()
        except Exception:
            pass
    unc, unp = uncommitted(), unpushed()
    rem, head = remote_changed(state)
    if not state.get("last_seen_remote"):
        state["last_seen_remote"] = head          # lần đầu: lấy mốc hiện tại, không nhắc oan
    return unc, unp, rem


def message(state, unc, unp, rem):
    # File đếm lần gọi công cụ đổi sau mỗi lệnh: lịch tự đẩy lo, không nhắc người dùng vì nó.
    unc, unp, rem = ([f for f in fs if not f.startswith(USAGE)] for fs in (unc, unp, rem))
    parts = []
    if unc or unp:
        parts.append(f"có kiến thức mới chưa đẩy lên GitHub ({len(unc)} file chưa commit, {len(unp)} file khác bản GitHub)")
    if rem:
        parts.append(f"GitHub có bản kiến thức mới từ máy khác ({len(rem)} file) chưa gộp về máy này")
    nm = state.get("needs_merge")
    if nm:
        parts.append("lần tự đẩy theo lịch đã dừng vì cần gộp tay: " + ", ".join(nm[:4]) + (" …" if len(nm) > 4 else ""))
    if not parts:
        return ""
    return ("Kiến thức: " + "; ".join(parts) + ". Cuối lượt trả lời này, nhắc người dùng MỘT dòng và hỏi có đẩy luôn không; "
            "đồng ý thì làm theo skill push (Bước A gộp bằng tools/knowledge_merge.py, rồi đẩy riêng kiến thức bằng "
            "push_source.py --only .claude/skills .claude/memory_store tools/claude_memory.py --committed). "
            "Không đẩy khi chưa được đồng ý.")


def cmd_check():
    s = load()
    unc, unp, rem = report(s, fetch=True)
    save(s)
    for title, files in (("Chưa commit", unc), ("Khác bản GitHub (đã commit)", unp), ("GitHub có mới từ máy khác", rem)):
        print(f"{title}: {len(files)}")
        for f in files[:10]:
            print("  ", f)
    if s.get("needs_merge"):
        print("Cần gộp tay (tự đẩy theo lịch dừng):", *s["needs_merge"], sep="\n  ")
    if s.get("last_autopush"):
        print("Tự đẩy gần nhất:", json.dumps(s["last_autopush"], ensure_ascii=False))
    return 0


def cmd_hook():
    try:
        ev = json.load(sys.stdin).get("hook_event_name") or "UserPromptSubmit"
    except Exception:
        ev = "UserPromptSubmit"
    s, now = load(), time.time()
    if now - s.get("last_check", 0) > CHECK_EVERY:
        unc, unp, rem = report(s, fetch=now - s.get("last_fetch", 0) > FETCH_EVERY)
        s["msg"], s["last_check"] = message(s, unc, unp, rem), now
        save(s)
    msg = s.get("msg", "")
    if not msg or (now - s.get("last_shown", 0) < SHOW_EVERY and msg == s.get("shown_msg")):
        return 0
    s["last_shown"], s["shown_msg"] = now, msg
    save(s)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": ev, "additionalContext": msg}}, ensure_ascii=False))
    return 0


def log(line):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + line + "\n")


SAFE = ("chỉ remote đổi", "remote có, máy này chưa từng có", "gộp 3 chiều sạch", "gộp theo dòng", "gộp theo mục")


def cmd_autopush():
    s = load()
    s["last_autopush"] = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "result": "bắt đầu"}

    def done(result, **kw):
        s["last_autopush"] = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "result": result, **kw}
        s["last_check"] = 0                       # để hook tính lại thông điệp
        save(s); log(result + (" " + json.dumps(kw, ensure_ascii=False) if kw else ""))
        return 0

    if (R / ".git" / "index.lock").exists():
        return done("bỏ qua: git đang bận (index.lock)")
    try:
        if git("fetch", "origin", "main", timeout=90).returncode:
            return done("bỏ qua: không kết nối được GitHub")
    except Exception:
        return done("bỏ qua: không kết nối được GitHub")
    subprocess.run([str(PY), "-I", "tools/claude_memory.py", "backup"], cwd=R, capture_output=True, timeout=120)
    unc = uncommitted()
    if unc:
        git("add", "--", *unc)
        r = git("commit", "-q", "-o", "-m", f"knowledge: tự lưu theo lịch ({len(unc)} file)\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>", "--", *unc)
        if r.returncode:
            return done("dừng: commit kiến thức lỗi", error=r.stderr.decode("utf-8", "replace")[:200])
    rep, manual = km.merge(["knowledge"], apply=False)
    todo = [(h, f) for h, f in rep if not h.startswith("máy này đã xoá")]
    bad = [f for h, f in todo if not h.startswith(SAFE)]
    if bad:
        s["needs_merge"] = bad
        return done("dừng: cần gộp tay (xung đột / không có gốc chung)", files=bad)
    s["needs_merge"] = []
    if todo:
        km.merge(["knowledge"], apply=True)
        files = [f for _, f in todo]
        git("add", "--", *files)
        git("commit", "-q", "-o", "-m", f"merge: gộp kiến thức từ GitHub main (tự động theo lịch, {len(files)} file)\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>", "--", *files)
        if any(f.startswith(".claude/memory_store/") for f in files):
            subprocess.run([str(PY), "-I", "tools/claude_memory.py", "restore"], cwd=R, capture_output=True, timeout=120)
    git("fetch", "origin", "main")
    unp = unpushed()
    if not unp:
        s["last_seen_remote"] = git("rev-parse", "origin/main").stdout.decode().strip()
        return done("không có gì mới để đẩy", merged=len(todo))
    r = subprocess.run([str(PY), "-I", "tools/push_source.py", "--only", *unp, "--committed", "--yes", "-m",
                        f"knowledge: scheduled auto push ({len(unp)} files)"], cwd=R, capture_output=True, timeout=300)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    if r.returncode:
        return done("đẩy thất bại (chạy lại lần sau)", error=out[-300:])
    commit = out.strip().split()[-1] if "Đã đẩy commit" in out else ""
    s["last_seen_remote"] = git("rev-parse", "origin/main").stdout.decode().strip()
    return done("đã đẩy kiến thức", files=len(unp), commit=commit, merged=len(todo))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    try:
        rc = {"check": cmd_check, "hook": cmd_hook, "autopush": cmd_autopush}[cmd]()
    except Exception as e:                      # hook / lịch không được làm hỏng gì
        if cmd == "check":
            raise
        try:
            log(f"{cmd} lỗi: {e!r}")
        except Exception:
            pass
        rc = 0
    sys.exit(rc)
