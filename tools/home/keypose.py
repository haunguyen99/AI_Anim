"""Key Pose: duyệt ảnh key pose (Codex, giai đoạn 0) và gửi yêu cầu tạo thêm ảnh.

Trang: /keypose  (tools/keypose/index.html)
Ảnh:   work/<dự án>/<job>/keys/*.png, nhóm theo key: k2_fire.png, k2_fire_v2.png, k2_fire_m5.png, k2_fire_r1.png → nhóm k2_fire
       prompt của ảnh: keys/prompts/<tên ảnh>.txt (nếu có). Ref cho ảnh mới: keys/keypose.json {"refs": [...]} hoặc model_ref/.
API:
  GET /api/keypose/jobs           các job có thư mục keys/ + Claude có đang canh không
  GET /api/keypose/job?id=<p/job> nhóm key, ảnh (url, prompt, thời gian), ref
  GET /api/keypose/clients        số trang Key Pose đang mở (hỏi trong 10 s gần nhất); hook notes_watch_hook.py dùng để nhắc bật bộ canh
Mỗi máy chạy Home riêng (tools/home/start.bat) nên trang đọc ảnh và lưu đánh dấu / yêu cầu trên chính máy đó.
Đánh dấu và yêu cầu ghi qua kho chung /api/store/keypose/...:
  marks/<p__job>.json      {"<tên ảnh>": {"mark": "star"|"reject"|"", "note": "...", "by": "..."}}
  requests/<id>.json       {job, key, base, text, n, by, sent, picked, status, progress, results[], error}
  tools/notes_watch.py bắt yêu cầu mới (kind keypose_req), Claude chạy tools/keypose_gen.py <id>.
"""
import getpass, glob, json, os, re, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
WORK = os.path.join(ROOT, "work")
PAGE = os.path.join(ROOT, "tools", "keypose")
BEAT = os.path.join(WORK, "store", "_sys", "watch", "notes.json")
VARIANT = re.compile(r"_(?:v|m|r)\d+$")
IMG = (".png", ".jpg", ".jpeg", ".webp")
SEEN = {"t": 0}   # lần cuối một trang Key Pose hỏi server


def user():
    try:
        return getpass.getuser()
    except Exception:
        return ""


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def job_dir(jid):
    if not re.match(r"^[A-Za-z0-9_\-]+/[A-Za-z0-9_\-]+$", jid or ""):
        raise ValueError("job không hợp lệ: " + str(jid))
    d = os.path.join(WORK, *jid.split("/"))
    if not os.path.isdir(os.path.join(d, "keys")):
        raise ValueError("không có thư mục keys/ trong work/" + jid)
    return d


def key_of(stem):
    return VARIANT.sub("", stem)


def nat(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def watching():
    try:
        return time.time() - json.load(open(BEAT, encoding="utf8")).get("beat", 0) < 10
    except (OSError, ValueError):
        return False


def jobs():
    out = []
    for kd in sorted(glob.glob(os.path.join(WORK, "*", "*", "keys"))):
        imgs = [f for f in os.listdir(kd) if f.lower().endswith(IMG)]
        if not imgs:
            continue
        jd = os.path.dirname(kd)
        out.append({"id": rel(jd)[len("work/"):], "count": len(imgs),
                    "keys": len({key_of(os.path.splitext(f)[0]) for f in imgs}),
                    "mtime": max(os.path.getmtime(os.path.join(kd, f)) for f in imgs)})
    out.sort(key=lambda j: -j["mtime"])
    return {"jobs": out, "watching": watching(), "user": user(), "root": ROOT}


def refs_for(jd):
    cfg = os.path.join(jd, "keys", "keypose.json")
    if os.path.isfile(cfg):
        try:
            r = json.load(open(cfg, encoding="utf8")).get("refs") or []
            return [p for p in (os.path.join(jd, x) for x in r) if os.path.isfile(p)]
        except ValueError:
            pass
    md = os.path.join(jd, "model_ref")
    if not os.path.isdir(md):
        return []
    cands = sorted(f for f in os.listdir(md) if f.lower().endswith(IMG))
    pick = [f for f in cands if re.search(r"(char|body).*(q34|side)", f)][:2] + \
           [f for f in cands if not f.startswith(("char", "body", "front", "side", "persp")) and "q34" in f][:1]
    return [os.path.join(md, f) for f in (pick or cands[:2])]


def job(jid):
    jd = job_dir(jid)
    kd = os.path.join(jd, "keys")
    groups = {}
    for f in os.listdir(kd):
        stem, ext = os.path.splitext(f)
        if ext.lower() not in IMG:
            continue
        p = os.path.join(kd, f)
        pr = os.path.join(kd, "prompts", stem + ".txt")
        groups.setdefault(key_of(stem), []).append({
            "name": stem, "url": "/" + rel(p) + "?t=%d" % os.path.getmtime(p), "mtime": os.path.getmtime(p),
            "prompt": open(pr, encoding="utf8").read() if os.path.isfile(pr) else ""})
    keys = []
    for k in sorted(groups, key=nat):
        imgs = sorted(groups[k], key=lambda i: i["mtime"])
        keys.append({"key": k, "images": imgs})
    return {"id": jid, "keys": keys, "refs": ["/" + rel(p) for p in refs_for(jd)], "watching": watching()}


def handle_get(h, path, qs):
    if path in ("/keypose", "/keypose/"):
        h.send_bytes(open(os.path.join(PAGE, "index.html"), "rb").read(), "text/html; charset=utf-8", True)
        return True
    if path == "/api/keypose/clients":
        h.send_json({"open": 1 if time.time() - SEEN["t"] < 10 else 0})
        return True
    SEEN["t"] = time.time()
    try:
        if path == "/api/keypose/jobs":
            h.send_json(jobs())
            return True
        if path == "/api/keypose/job":
            h.send_json(job((qs.get("id") or [""])[0]))
            return True
    except ValueError as e:
        h.send_json({"error": str(e)}, 400)
        return True
    return False
