"""Bản thử rig / anim của Claude (2026-11-05, người dùng: "những file mà claude tạo ra để thử rig, anim hãy lưu lại kết quả
thử và tự động lập tức xóa file thử sau khi đã đạt được kết quả").

Một lần thử = bản sao skeleton + mọi file phụ sinh ra (ảnh snap / contact sheet, JSON tạm). Xong thì `done`: ghi kết quả vào
sổ `<thư mục skeleton>/trials.md` (+ work/store/_sys/trials/log.jsonl), rồi XOÁ NGAY bản sao, file phụ, và kho Hoàn tác /
Phiên bản của Spine Live sinh ra cho bản sao (work/store/_sys/spine_live/backup|versions). File gốc không bị đụng.

Dòng lệnh (từ gốc dự án, .venv/Scripts/python.exe -I tools/spine/trial.py ...):
  new  <json gốc> <tên> [--why "thử gì"]      -> in đường dẫn bản sao <thư mục>/_trial_<tên>.json (cùng thư mục: ảnh vẫn nạp)
  add  <tên> <file> [file ...]                 đăng ký file phụ (ảnh snap, JSON tạm) để xoá cùng lần thử
  done <tên> --result "kết quả" [--keep FILE]  ghi kết quả + xoá hết (--keep: giữ lại file phụ đó, vd ảnh gửi người dùng)
  list                                          lần thử đang mở
  sweep [--hours 6]                             lần thử bỏ dở quá N giờ: ghi "bỏ dở" + xoá
Trong Python:
  from trial import Trial
  with Trial(json_goc, "bindtest", why="Bind thêm hip giữ weight cũ") as t:
      ... dùng t.path, t.add(file_anh) ...
      t.result("52/85 điểm nhận hip, tỉ lệ cũ giữ nguyên")      # không gọi result -> ghi "không ghi kết quả"
  # ra khỏi with (kể cả lỗi) là ghi sổ + xoá
"""
import argparse, glob, json, os, shutil, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SYS = os.path.join(ROOT, "work", "store", "_sys")
ACTIVE = os.path.join(SYS, "trials", "active.json")
LOG = os.path.join(SYS, "trials", "log.jsonl")
SL_BACKUP = os.path.join(SYS, "spine_live", "backup")
SL_VERS = os.path.join(SYS, "spine_live", "versions")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def rel(p):
    return os.path.relpath(os.path.abspath(p), ROOT).replace("\\", "/")


def _load():
    try:
        return json.load(open(ACTIVE, encoding="utf-8"))
    except Exception:
        return {}


def _save(d):
    os.makedirs(os.path.dirname(ACTIVE), exist_ok=True)
    tmp = ACTIVE + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, ACTIVE)


def new(src, name, why=""):
    src = os.path.abspath(src)
    if not os.path.isfile(src):
        raise SystemExit("không thấy file gốc: " + src)
    d = _load()
    if name in d:
        raise SystemExit(f"lần thử '{name}' đang mở ({d[name]['path']}): done / sweep trước")
    dst = os.path.join(os.path.dirname(src), f"_trial_{name}.json")
    shutil.copyfile(src, dst)
    d[name] = {"path": rel(dst), "src": rel(src), "why": why, "t": time.strftime("%Y-%m-%d %H:%M:%S"), "files": []}
    _save(d)
    return dst


def add(name, *files):
    d = _load()
    if name not in d:
        raise SystemExit(f"không có lần thử '{name}'")
    for f in files:
        r = rel(f)
        if r not in d[name]["files"]:
            d[name]["files"].append(r)
    _save(d)


def _sl_purge(js_rel):
    """xoá kho Hoàn tác / Phiên bản Spine Live của một file thử (tên = đường dẫn, '/' -> '__')."""
    base = js_rel.replace("/", "__")
    n = 0
    for p in glob.glob(os.path.join(glob.escape(SL_BACKUP), glob.escape(base) + "*")):
        os.remove(p); n += 1
    v = os.path.join(SL_VERS, base)
    if os.path.isdir(v):
        shutil.rmtree(v); n += 1
    return n


def done(name, result="", keep=(), status="xong"):
    d = _load()
    tr = d.pop(name, None)
    if not tr:
        raise SystemExit(f"không có lần thử '{name}'")
    keep = {rel(k) for k in keep}
    gone = []
    for r in [tr["path"]] + tr["files"]:
        if r in keep:
            continue
        p = os.path.join(ROOT, r)
        if os.path.isfile(p):
            os.remove(p); gone.append(r)
        elif os.path.isdir(p):
            shutil.rmtree(p); gone.append(r + "/")
    purged = _sl_purge(tr["path"])
    for r in tr["files"]:
        if r.endswith(".json") and r not in keep:
            purged += _sl_purge(r)
    entry = {"t": time.strftime("%Y-%m-%d %H:%M:%S"), "start": tr["t"], "name": name, "src": tr["src"], "why": tr["why"],
             "status": status, "result": result or "(không ghi kết quả)", "deleted": gone, "kept": sorted(keep)}
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    book = os.path.join(ROOT, os.path.dirname(tr["src"]), "trials.md")
    first = not os.path.isfile(book)
    with open(book, "a", encoding="utf-8") as fh:
        if first:
            fh.write("# Sổ thử của Claude\n\nMỗi lần thử rig / anim trên bản sao: thử gì, kết quả. Bản sao + file phụ đã xoá ngay sau khi có kết quả (tools/spine/trial.py).\n\n")
        fh.write(f"## {entry['t']} · {name} ({status})\n- File gốc: `{tr['src']}`\n")
        if tr["why"]:
            fh.write(f"- Thử: {tr['why']}\n")
        fh.write(f"- Kết quả: {entry['result']}\n")
        if keep:
            fh.write(f"- Giữ lại: {', '.join(sorted(keep))}\n")
        fh.write("\n")
    if d:
        _save(d)
    elif os.path.isfile(ACTIVE):
        os.remove(ACTIVE)
    return {"deleted": gone, "store_purged": purged, "book": rel(book)}


def sweep(hours=6.0):
    d = _load(); out = []
    for name, tr in list(d.items()):
        age = (time.time() - time.mktime(time.strptime(tr["t"], "%Y-%m-%d %H:%M:%S"))) / 3600
        if age >= hours:
            done(name, "bỏ dở (không có kết quả, dọn tự động)", status="bỏ dở"); out.append(name)
    return out


class Trial:
    def __init__(self, src, name, why=""):
        self.name = name
        self.path = new(src, name, why)
        self._result = ""
        self.keep = []

    def add(self, *files):
        add(self.name, *files)

    def result(self, text, keep=()):
        self._result = text
        self.keep += list(keep)

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        if et is not None:
            done(self.name, f"lỗi {et.__name__}: {ev}" + (f" · {self._result}" if self._result else ""), self.keep, "lỗi")
        else:
            done(self.name, self._result, self.keep)
        return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("new"); a.add_argument("src"); a.add_argument("name"); a.add_argument("--why", default="")
    a = sp.add_parser("add"); a.add_argument("name"); a.add_argument("files", nargs="+")
    a = sp.add_parser("done"); a.add_argument("name"); a.add_argument("--result", default=""); a.add_argument("--keep", nargs="*", default=[])
    sp.add_parser("list")
    a = sp.add_parser("sweep"); a.add_argument("--hours", type=float, default=6.0)
    o = ap.parse_args()
    if o.cmd == "new":
        print(rel(new(o.src, o.name, o.why)))
    elif o.cmd == "add":
        add(o.name, *o.files); print("đã đăng ký", len(o.files), "file")
    elif o.cmd == "done":
        print(json.dumps(done(o.name, o.result, o.keep), ensure_ascii=False))
    elif o.cmd == "list":
        print(json.dumps(_load(), ensure_ascii=False, indent=1))
    elif o.cmd == "sweep":
        print("dọn:", sweep(o.hours))
