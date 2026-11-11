"""Kiểm và gộp KIẾN THỨC (skill, bộ nhớ Claude) giữa máy này và GitHub origin/main trước khi /push.

Vì sao: `push_source.py` ghi file trên máy đè lên cây origin/main. Máy khác đã đẩy bản mới của cùng file thì lần đẩy sau
sẽ xoá công việc đó. Công cụ này so 3 bản: gốc (lần đồng bộ cuối) / máy này / origin/main, rồi gộp từng file.

Dùng:  python tools/knowledge_merge.py            xem báo cáo (không ghi gì)
       python tools/knowledge_merge.py --apply    ghi vào thư mục làm việc (xung đột để dấu <<<<<<< may-nay ... >>>>>>> remote)
       python tools/knowledge_merge.py --mark     sau khi ĐẨY xong: ghi origin/main hiện tại làm gốc cho lần sau
       --base SHA  chỉ định gốc tay (chưa có dấu đồng bộ)
Gốc lưu ở `.git/knowledge_sync_base`. Phạm vi: .claude/skills (trừ Spine Live), .claude/memory_store, tools/claude_memory.py.
Quy tắc gộp: chỉ remote đổi → lấy remote; chỉ máy này đổi → giữ; cả hai → gộp 3 chiều (MEMORY.md gộp theo dòng).
Giữ kiểu xuống dòng (CRLF/LF) của file trên máy. Thoát mã 2 nếu còn xung đột."""
import os, pathlib, subprocess, sys, tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
R = pathlib.Path(__file__).resolve().parents[1]
THEIRS = "origin/main"
SCOPE = [".claude/skills", ".claude/memory_store", "tools/claude_memory.py"]
SKIP = (".claude/skills/spine2d/", ".claude/skills/spinelive/", ".claude/skills/exportspine/")
MARK = R / ".git" / "knowledge_sync_base"
ENV = {**os.environ, "MSYS_NO_PATHCONV": "1"}
norm = lambda b: b.replace(b"\r\n", b"\n")


def git(*a):
    return subprocess.run(["git", *a], cwd=R, capture_output=True, env=ENV)


def show(ref, f):
    p = git("show", f"{ref}:{f}")
    return p.stdout if p.returncode == 0 else None


def main():
    args = sys.argv[1:]
    git("fetch", "origin", "main")
    head = git("rev-parse", THEIRS).stdout.decode().strip()
    if "--mark" in args:
        MARK.write_text(head, encoding="utf-8"); print("Đã ghi gốc đồng bộ:", head[:8]); return 0
    base = args[args.index("--base") + 1] if "--base" in args else (MARK.read_text().strip() if MARK.exists() else None)
    if not base:
        print("Chưa có gốc đồng bộ: chạy với --base <sha> (commit origin/main lần đẩy / gộp cuối)."); return 1
    apply = "--apply" in args
    names = git("diff", "--name-only", base, THEIRS, "--", *SCOPE).stdout.decode().split("\n")
    rep, bad_files = [], []
    for f in (n for n in names if n and not n.startswith(SKIP)):
        b, t = show(base, f), show(THEIRS, f)
        path = R / f
        o = path.read_bytes() if path.exists() else None
        if t is None:
            rep.append(("remote xoá file: bỏ qua", f)); continue
        if b is not None and norm(b) == norm(t):
            continue
        crlf = o is not None and o.count(b"\r\n") > o.count(b"\n") / 2
        if o is None:
            new, how = t, "file mới từ remote"
        elif norm(o) == norm(t):
            continue
        elif b is None:
            new, how = o, "cả hai khác nhau, không có gốc: GIỮ bản máy này (xem tay)"
        elif norm(o) == norm(b):
            new, how = t, "chỉ remote đổi: lấy remote"
        elif f.endswith("MEMORY.md"):
            ol = norm(o).decode().split("\n"); have = set(ol)
            add = [l for l in norm(t).decode().split("\n") if l.strip() and l not in have]
            while ol and not ol[-1].strip():
                ol.pop()
            new, how = ("\n".join(ol + add) + "\n").encode(), f"gộp theo dòng (+{len(add)} dòng từ remote)"
        else:
            d = pathlib.Path(tempfile.mkdtemp())
            for n, x in (("o", o), ("b", b), ("t", t)):
                (d / n).write_bytes(norm(x))
            p = subprocess.run(["git", "merge-file", "-p", "-L", "may-nay", "-L", "goc", "-L", "remote",
                                str(d / "o"), str(d / "b"), str(d / "t")], capture_output=True)
            new, how = p.stdout, "gộp 3 chiều" + (f": {p.returncode} XUNG ĐỘT" if p.returncode else " sạch")
            if p.returncode:
                bad_files.append(f)
        if crlf:
            new = norm(new).replace(b"\n", b"\r\n")
        rep.append((how, f))
        if apply and new != o:
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(new)
    for how, f in rep:
        print(f"{how:48} {f}")
    print(f"Tổng {len(rep)} file cần gộp" + ("" if apply else " (xem trước, chưa ghi; thêm --apply)"))
    if apply and bad_files:
        print("CÒN XUNG ĐỘT, sửa tay các file này rồi mới đẩy:", *bad_files, sep="\n  "); return 2
    return 0


sys.exit(main())
