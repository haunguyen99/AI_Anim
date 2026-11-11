"""Đẩy MÃ NGUỒN lên GitHub (origin/main): skill, tool, quy trình, tài liệu, mã các Lab. Không đẩy dữ liệu (model, video, FBX, trang đã build, kho `work/store`).

Cách làm (không đụng nhánh đang làm, không đổi index thật, không force):
  1. fetch origin; dựng cây mới = cây origin/main + các file nguồn trong danh sách cho phép (đọc từ thư mục làm việc) - các file nguồn đã bị xoá ở máy
     thì bị xoá khỏi cây;
  2. commit lên origin/main (fast-forward) bằng chỉ mục tạm `.git/index_push`, gán nhánh cục bộ `source`, `git push origin source:main`.
Dùng: python tools/push_source.py [--dry-run] [-m "lời nhắn"] [--yes] [--only PATH…] [--committed] [--branch TÊN]
  --dry-run   chỉ liệt kê thay đổi sẽ đẩy
  --yes       đẩy luôn (bắt buộc để đẩy thật; thiếu thì chỉ liệt kê)
  --only      chỉ đẩy các file / thư mục này (vd đẩy một việc khi phiên khác đang sửa dở file khác); không xoá gì
  --branch    đẩy lên nhánh GitHub khác main, cây dựng trên nhánh đó (chưa có thì trên main); vẫn chỉ fast-forward (từ 2026-11-11 chỉ dùng main)
  --committed lấy nội dung đã commit (HEAD) thay vì thư mục làm việc: bỏ qua thay đổi chưa commit; không xoá gì
Giữ nguyên bản trên GitHub của `.claude/launch.json` và `.mcp.json` (bản trên máy có cấu hình riêng).
"""
import argparse, os, re, subprocess, sys

if hasattr(sys.stdout, "reconfigure"):   # Windows: tiếng Việt trong console
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.chdir(ROOT)

# Cho phép (glob, so khớp đường dẫn kiểu /). Mọi thứ khác không bao giờ được đẩy.
# .claude/memory_store = bản sao bộ nhớ Claude (tools/claude_memory.py), user 2026-11-04: đẩy lên để tài khoản khác dùng được;
# .claude/mcp_store KHÔNG đẩy (có khoá MCP).
ALLOW = [
    "README.md", "MAP.md", "CLAUDE.md", "requirements.txt", ".gitignore", ".vscode/extensions.json",
    ".claude/settings.json", ".claude/output-styles/**",
    ".claude/skills/**", ".claude/agents/**", ".claude/memory_store/**", "docs/**", "tools/**",
    "work/clips.json", "work/patch_localdb.py",
    "work/pose_lab/index.html", "work/pose_lab/*.py", "work/pose_lab/fbx/*.py", "work/pose_lab/fbx/*.js", "work/pose_lab/fbx/test.html",
    "work/review_page/index.html", "work/review_page/*.py",
    "work/rig_lab/template.html", "work/rig_lab/*.py", "work/rig_lab/*.json", "work/rig_lab/chars/*.json",
    "work/rig_lab/chars/*/landmarks_auto.json", "work/rig_lab/chars/*/mesh_cm.json",
    "work/mesh_lab/template.html", "work/mesh_lab/*.py",
]
# Không bao giờ đẩy / không đụng tới (giữ bản trên GitHub)
DENY = ["**/.env", "**/__pycache__/**", "**/*.pyc", "**/.venv/**", "tools/spine_mcp/.venv/**", "**/node_modules/**", "work/*/pages/**",
        "work/store/**", "work/pose_lab/models/**", "work/review_page/clips/**"]
KEEP_REMOTE = {".claude/launch.json", ".mcp.json"}
# Nhánh spine-live đã bỏ (người dùng 2026-11-11): Spine Live đi chung main như mọi file khác.
SPINE_LIVE = []
MAX_BYTES = 5 * 1024 * 1024


def git(*args, env=None, inp=None, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, env=env, input=inp)
    if check and r.returncode:
        sys.exit("git " + " ".join(args) + " lỗi: " + r.stderr.decode("utf8", "replace").strip())
    return r.stdout.decode("utf8", "replace")


def _blob(h):
    return subprocess.run(["git", "cat-file", "blob", h], cwd=ROOT, capture_output=True).stdout


def keep_eol(p, h, rh, write):
    """Giữ kiểu xuống dòng của bản trên GitHub. Repo lưu nhiều file dạng CRLF, còn hash-object
    (autocrlf) băm thành LF: không giữ thì file chỉ khác CRLF/LF cũng bị viết lại cả file,
    và lần kéo sau xung đột toàn file."""
    remote_b = _blob(rh)
    if b"\r\n" not in remote_b:
        return h
    raw = open(os.path.join(ROOT, p), "rb").read()
    if raw.replace(b"\r\n", b"\n") == remote_b.replace(b"\r\n", b"\n"):
        return rh                                  # chỉ khác kiểu xuống dòng: giữ bản trên GitHub
    crlf = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return git("hash-object", "--stdin", *(["-w"] if write else []), inp=crlf).strip()


def _rx(p):   # glob: ** qua nhiều thư mục, * không qua dấu /
    out, i = "", 0
    while i < len(p):
        if p.startswith("**/", i): out += "(?:.*/)?"; i += 3
        elif p.startswith("**", i): out += ".*"; i += 2
        elif p[i] == "*": out += "[^/]*"; i += 1
        elif p[i] == "?": out += "[^/]"; i += 1
        else: out += re.escape(p[i]); i += 1
    return re.compile("^" + out + "$")


_CACHE = {}


def match(path, pats):
    return any((_CACHE.get(p) or _CACHE.setdefault(p, _rx(p))).match(path) for p in pats)


def allowed(path):
    return match(path, ALLOW) and not match(path, DENY) and path not in KEEP_REMOTE


def local_files():
    out = set()
    for ln in git("ls-files", "-z", "--cached", "--others", "--exclude-standard").split("\0"):
        if ln and allowed(ln) and os.path.isfile(os.path.join(ROOT, ln)):
            out.add(ln)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-m", "--message", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--only", nargs="+", default=None)
    ap.add_argument("--committed", action="store_true")
    ap.add_argument("--branch", default="main", help="nhánh GitHub đích (mặc định main); nhánh chưa có thì dựng từ cây main")
    a = ap.parse_args()
    only = [o.replace("\\", "/").rstrip("/") for o in a.only] if a.only else None
    inside = lambda p: (only is None or any(p == o or p.startswith(o + "/") for o in only))
    head = {}
    if a.committed:   # blob đã commit của từng file nguồn
        for ln in git("ls-tree", "-r", "HEAD").splitlines():
            meta, path = ln.split("\t", 1)
            if allowed(path): head[path] = meta.split()[2]
    git("fetch", "origin", "-q")
    remote = {}
    br = a.branch.strip() or "main"
    base = "origin/" + br if git("rev-parse", "--verify", "-q", "origin/" + br, check=False).strip() else "origin/main"
    if br != "main": print(f"Nhánh đích: {br} (dựng trên {base})")
    for ln in git("ls-tree", "-r", base).splitlines():
        meta, path = ln.split("\t", 1)
        remote[path] = meta.split()[2]            # blob hash
    local = {p for p in (set(head) if a.committed else local_files()) if inside(p)}
    add, mod, rem, big = [], [], [], []
    new_hash = {}
    for p in sorted(local):
        if a.committed: h = head[p]
        else:
            if os.path.getsize(os.path.join(ROOT, p)) > MAX_BYTES:
                big.append(p); continue
            h = git("hash-object", *(["-w"] if a.yes and not a.dry_run else []), p).strip()
            if p in remote and remote[p] != h:
                h = keep_eol(p, h, remote[p], a.yes and not a.dry_run)
        new_hash[p] = h
        if p not in remote: add.append(p)
        elif remote[p] != h: mod.append(p)
    for p in sorted(remote):
        if allowed(p) and p not in local and only is None and not a.committed: rem.append(p)
    for p in big: print("BỎ QUA (quá 5 MB):", p)
    dirty = [] if a.committed else [ln[3:] for ln in git("status", "--short").splitlines() if ln[3:] in set(add + mod)]
    if not (add or mod or rem):
        print("Không có gì mới để đẩy: GitHub đã khớp với mã nguồn trên máy."); return
    for tag, lst in (("THÊM", add), ("SỬA", mod), ("XOÁ", rem)):
        for p in lst: print(f"{tag:5} {p}")
    print(f"Tổng: {len(add)} thêm, {len(mod)} sửa, {len(rem)} xoá.")
    if dirty:
        print("Lưu ý: các file sau có thay đổi CHƯA commit trên máy (vẫn được đẩy theo nội dung hiện tại):")
        for p in dirty: print("  ", p)
    if a.dry_run or not a.yes:
        print("(chưa đẩy: thêm --yes để đẩy thật)"); return
    env = dict(os.environ, GIT_INDEX_FILE=os.path.join(ROOT, ".git", "index_push"))
    try:
        git("read-tree", base, env=env)
        for p in add + mod:
            git("update-index", "--add", "--cacheinfo", f"100644,{new_hash[p]},{p}", env=env)
        if rem:
            git("update-index", "--force-remove", "--stdin", env=env, inp=("\n".join(rem) + "\n").encode("utf8"))
        tree = git("write-tree", env=env).strip()
        if tree == git("rev-parse", base + "^{tree}").strip():
            print("Cây không đổi, không đẩy."); return
        msg = a.message.strip() or f"Update source: {len(add)} added, {len(mod)} modified, {len(rem)} removed"
        msg += "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
        commit = git("commit-tree", tree, "-p", base, "-m", msg).strip()
    finally:
        try: os.remove(os.path.join(ROOT, ".git", "index_push"))
        except OSError: pass
    lb = "source" if br == "main" else "source-" + br
    git("branch", "-f", lb, commit)
    r = subprocess.run(["git", "push", "origin", f"{lb}:refs/heads/{br}"], cwd=ROOT, capture_output=True, text=True, encoding="utf8")
    print((r.stdout + r.stderr).strip())
    if r.returncode:
        sys.exit("Đẩy thất bại (có thể người khác vừa đẩy: chạy lại để lấy bản mới, không dùng --force).")
    print("Đã đẩy commit", commit[:7])


if __name__ == "__main__":
    main()
