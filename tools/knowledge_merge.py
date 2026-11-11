"""Kiểm và gộp file nguồn giữa máy này và GitHub origin/main TRƯỚC khi /push (kiến thức + tool + tài liệu + mã Lab).

Vì sao: `push_source.py` ghi file trên máy ĐÈ lên cây origin/main, và coi file máy khác vừa thêm là "XOÁ".
Máy khác đã sửa / thêm file thì lần đẩy sau xoá công việc đó. Công cụ này gộp từng file theo 3 bản: máy này / origin/main /
GỐC CHUNG. Gốc chung của từng file tự tìm, không cần dấu đồng bộ: bản mới nhất trong lịch sử origin/main của file
mà nội dung trùng một bản nào đó trong lịch sử `master` (hoặc bản đang có trên máy). Phạm vi = đúng danh sách cho phép
của push_source (trừ file Spine Live, đi nhánh spine-live).

Dùng:  python tools/knowledge_merge.py [--scope knowledge|code|all]   xem báo cáo (không ghi gì)
       ... --apply   ghi vào thư mục làm việc (xung đột để dấu <<<<<<< may-nay ... >>>>>>> remote)
  knowledge = .claude/skills, .claude/memory_store, tools/claude_memory.py;  code = mọi file cho phép còn lại.
Quy tắc cho từng file khác nhau giữa máy này và origin/main:
  - bản remote = gốc chung  → máy này đã có hoặc mới hơn: giữ;     - bản máy này = gốc chung → lấy remote;
  - cả hai khác gốc → gộp 3 chiều (MEMORY.md gộp theo dòng; nhị phân thì giữ máy này, báo xem tay);
  - không tìm được gốc chung → GIỮ máy này, báo xem tay (mã thoát 2);
  - file remote có mà máy này chưa từng có → thêm về; file máy này đã xoá (từng có trong master) → giữ xoá, báo.
Chạy lại nhiều lần an toàn. Giữ kiểu xuống dòng (CRLF/LF) của file trên máy. Mã thoát 2 nếu còn việc xem tay."""
import hashlib, os, pathlib, subprocess, sys, tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import push_source as ps   # danh sách cho phép / loại trừ dùng chung với /push (import này đổi thư mục chạy về gốc repo)

R = pathlib.Path(ps.ROOT)
THEIRS = "origin/main"
ENV = {**os.environ, "MSYS_NO_PATHCONV": "1"}
norm = lambda b: b.replace(b"\r\n", b"\n")
H = lambda b: hashlib.sha1(norm(b)).hexdigest()


def git(*a):
    return subprocess.run(["git", *a], cwd=R, capture_output=True, env=ENV)


def show(ref, f):
    p = git("show", f"{ref}:{f}")
    return p.stdout if p.returncode == 0 else None


def group(f):
    k = f.startswith((".claude/skills/", ".claude/memory_store/")) or f == "tools/claude_memory.py"
    return "knowledge" if k else "code"


def in_scope(f):
    return bool(f) and ps.allowed(f) and not any(f == o or f.startswith(o + "/") for o in ps.SPINE_LIVE)


def history(ref, f):
    """Các bản của file trong lịch sử `ref`, mới → cũ: [(commit, bytes)]."""
    out = []
    for c in git("log", "--format=%H", ref, "--", f).stdout.decode().split():
        b = show(c, f)
        if b is not None:
            out.append((c, b))
    return out


def common_base(f, ours):
    """Bản gốc chung (bytes) của máy này và remote, hoặc None."""
    mine = {H(b) for _, b in history("HEAD", f)}
    if ours is not None:
        mine.add(H(ours))
    for _, b in history(THEIRS, f):
        if H(b) in mine:
            return b
    return None


def already_merged(o, b, t):
    """Mọi dòng remote thêm / sửa (so với gốc) đã có trong bản máy này, và mọi dòng remote xoá đã không còn."""
    S = lambda x: set(norm(x).decode("utf-8", "replace").splitlines())
    so, sb, st = S(o), S(b), S(t)
    return (st - sb) <= so and not ((sb - st) & so)


def clips_merge(o, b, t):
    """work/clips.json (sổ clip) gộp theo MỤC, không theo dòng: `characters` (theo tên), `clips` và `projects` (theo id).
    Mục chỉ một bên có → giữ (hợp hai bên); cả hai sửa khác nhau → giữ bản máy này, trừ khi bên kia là bản gốc."""
    import json
    O, B, T = (json.loads(norm(x).decode("utf-8")) for x in (o, b, t))
    kept = []

    def pick(k, ov, bv, tv):
        if ov == tv or tv == bv:
            return ov
        if ov == bv:
            return tv
        kept.append(str(k)); return ov            # cả hai sửa khác nhau: giữ máy này, báo

    ch = dict(O.get("characters", {}))
    for k, tv in T.get("characters", {}).items():
        ch[k] = tv if k not in ch else pick(k, ch[k], B.get("characters", {}).get(k), tv)
    O["characters"] = ch
    for key in ("clips", "projects"):
        ol, bm, tl = O.get(key, []), {x["id"]: x for x in B.get(key, [])}, T.get(key, [])
        idx = {x["id"]: i for i, x in enumerate(ol)}
        for x in tl:
            if x["id"] in idx:
                ol[idx[x["id"]]] = pick(f"{key}:{x['id']}", ol[idx[x["id"]]], bm.get(x["id"]), x)
            else:
                ol.append(x)
        O[key] = ol
    s = json.dumps(O, indent=1, ensure_ascii=False) + "\n"
    s = s.replace("\n", "\r\n") if o.count(b"\r\n") > o.count(b"\n") / 2 else s
    return s.encode("utf-8"), "gộp theo mục (clips.json)" + (f"; cả hai sửa, giữ máy này: {', '.join(kept)}" if kept else "")


def main():
    args = sys.argv[1:]
    git("fetch", "origin", "main")
    scope = args[args.index("--scope") + 1] if "--scope" in args else "all"
    groups = ["knowledge", "code"] if scope == "all" else [scope]
    apply = "--apply" in args
    rep, manual = [], []
    tree = [n for n in git("ls-tree", "-r", "--name-only", THEIRS).stdout.decode().split("\n")
            if in_scope(n) and group(n) in groups]
    for f in tree:
        t = show(THEIRS, f)
        path = R / f
        o = path.read_bytes() if path.exists() else None
        if o is None:
            if git("log", "-1", "--format=%h", "HEAD", "--", f).stdout.strip():
                rep.append(("máy này đã xoá (từng có): GIỮ xoá, /push sẽ xoá trên GitHub", f)); continue
            new, how = t, "remote có, máy này chưa từng có: thêm về"
        elif norm(o) == norm(t):
            continue
        else:
            b = common_base(f, o)
            if b is None:
                rep.append(("KHÔNG có gốc chung: GIỮ bản máy này (xem tay)", f)); manual.append(f); continue
            if norm(b) == norm(t):
                continue                        # remote không có gì mới hơn máy này
            crlf = o.count(b"\r\n") > o.count(b"\n") / 2
            if norm(o) == norm(b):
                new, how = t, "chỉ remote đổi: lấy remote"
            elif b"\0" in o or b"\0" in t:
                rep.append(("nhị phân cả hai đổi: GIỮ bản máy này (xem tay)", f)); manual.append(f); continue
            elif f.endswith("MEMORY.md"):
                ol = norm(o).decode().split("\n"); have = set(ol)
                add = [l for l in norm(t).decode().split("\n") if l.strip() and l not in have]
                while ol and not ol[-1].strip():
                    ol.pop()
                new, how = ("\n".join(ol + add) + "\n").encode(), f"gộp theo dòng (+{len(add)} dòng từ remote)"
                if not add:
                    continue
            elif f == "work/clips.json":
                new, how = clips_merge(o, b, t)
                if new == o:
                    continue
            elif already_merged(o, b, t):
                continue                        # lần gộp trước đã đưa thay đổi của remote vào file này
            else:
                d = pathlib.Path(tempfile.mkdtemp())
                for n, x in (("o", o), ("b", b), ("t", t)):
                    (d / n).write_bytes(norm(x))
                p = subprocess.run(["git", "merge-file", "-p", "-L", "may-nay", "-L", "goc", "-L", "remote",
                                    str(d / "o"), str(d / "b"), str(d / "t")], capture_output=True)
                new, how = p.stdout, "gộp 3 chiều" + (f": {p.returncode} XUNG ĐỘT" if p.returncode else " sạch")
                if p.returncode:
                    manual.append(f)
            if crlf and b"\0" not in new:
                new = norm(new).replace(b"\n", b"\r\n")
        rep.append((how, f))
        if apply and new != o:
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(new)
    for how, f in rep:
        print(f"{how:50} {f}")
    print(f"Tổng {len(rep)} file cần gộp / xem" + ("" if apply else " (xem trước, chưa ghi; thêm --apply)"))
    if apply and manual:
        print("CẦN XEM TAY (xung đột / không có gốc), xong mới đẩy:", *manual, sep="\n  "); return 2
    return 0


sys.exit(main())
