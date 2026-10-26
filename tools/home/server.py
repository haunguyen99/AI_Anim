"""Home: trang quản lý dự án chạy trên máy (một người dùng, dữ liệu nằm trên máy này).
Home → dự án (theo game) → animation → mở trang đang làm (Rig Lab / Pose Lab / Review Lab).
Đọc/ghi sổ work/clips.json (cùng sổ với tools/clip_registry.py), thêm khóa "projects".

Chạy:  .venv\\Scripts\\python.exe -I tools\\home\\server.py   rồi mở http://127.0.0.1:8780
"""
import json, os, re, subprocess, sys, time
from datetime import date
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, unquote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REG = os.path.join(ROOT, "work", "clips.json")
REVIEW_HTML = os.path.join(ROOT, "work", "review_page", "index.html")
POSE_HTML = os.path.join(ROOT, "work", "pose_lab", "index.html")
STAGES = ["rig", "analysis", "p0", "blocking", "spline", "polish", "export"]
PORT = int(os.environ.get("HOME_PORT") or os.environ.get("PORT") or "8780")
MEDIA = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".webm": "video/webm", ".mp4": "video/mp4"}

# Dự án mặc định khi sổ chưa có khóa "projects" (theo game).
DEFAULT_PROJECTS = [
    {"id": "boss_gaygor", "name": "Boss Gaygor", "desc": "Boss M11 Gaygor: chùy + khiên", "characters": ["Gaygor"], "labels": {"Gaygor": "boss"}},
    {"id": "shoot_die_repeat", "name": "Shoot Die Repeat", "desc": "Game bắn súng, mỗi map một nhân vật",
     "characters": ["SDR", "SDR06"], "labels": {"SDR": "map2 · lính La Mã", "SDR06": "map06 · gangster + Thompson"}},
]


def slug(s):
    s = s.lower()
    for a, b in (("đ", "d"),):
        s = s.replace(a, b)
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def load():
    d = json.load(open(REG, encoding="utf8"))
    if "projects" not in d:
        d["projects"] = DEFAULT_PROJECTS
        save(d)
    return d


def save(d):
    tmp = REG + ".tmp"
    with open(tmp, "w", encoding="utf8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, REG)


def read(p):
    try:
        return open(p, encoding="utf8").read()
    except OSError:
        return ""


def entries(html, const):
    """Các mục { clip: ... } trong mảng `const X = [ ... ];` (mỗi mục có thể nhiều dòng)."""
    m = re.search(r"const " + const + r"\s*=\s*\[(.*?)\n\];", html, re.S)
    if not m:
        return []
    return [("clip:" + chunk) for chunk in re.split(r"\n\s*\{\s*clip:", "\n" + m.group(1))[1:]]


def field(e, k, num=False):
    m = re.search(r"\b" + k + (r":\s*(\d+)" if num else r':\s*"((?:[^"\\]|\\.)*)"'), e)
    return (int(m.group(1)) if num else m.group(1)) if m else (None if num else "")


def versions():
    """Bản mới nhất của mỗi clip trên Review Lab (CLIPS) và Pose Lab (POSES): mục đầu tiên là mới nhất."""
    rev, pose = {}, {}
    for e in entries(read(REVIEW_HTML), "CLIPS"):
        rev.setdefault(field(e, "clip"), []).append({"version": field(e, "version"), "label": field(e, "label"),
                                                    "thumb": field(e, "thumb"), "n": field(e, "n", True)})
    for e in entries(read(POSE_HTML), "POSES"):
        pose.setdefault(field(e, "clip"), []).append({"version": field(e, "version"), "label": field(e, "label"),
                                                     "date": field(e, "date"), "frames": field(e, "frames", True)})
    return rev, pose


def git_log(n=40):
    try:
        out = subprocess.run(["git", "log", f"-{n}", "--format=%h\x1f%ad\x1f%s", "--date=short"], cwd=ROOT,
                             capture_output=True, text=True, encoding="utf8", timeout=10).stdout
    except Exception:
        return []
    rows = []
    for line in out.splitlines():
        p = line.split("\x1f")
        if len(p) == 3:
            rows.append({"hash": p[0], "date": p[1], "msg": p[2]})
    return rows


def status_of(c):
    note = (c.get("note") or "").lower()
    if c.get("status"):
        return c["status"]
    if c.get("stage") == "export":
        return "done"
    if "tạm dừng" in note:
        return "paused"
    if "chờ" in note:
        return "waiting"
    return "working"


def enrich(d):
    rev, pose = versions()
    out = []
    for c in d["clips"]:
        r = c.get("review") or {}
        p = c.get("pose") or {}
        rv = (rev.get(r.get("clip")) or [None])[0]
        pv = (pose.get(p.get("clip")) or [None])[0]
        thumb = ""
        updated = c.get("updated", "")
        if rv and rv["thumb"]:
            thumb = "/work/review_page/" + rv["thumb"]
            tp = os.path.join(ROOT, "work", "review_page", rv["thumb"])
            if os.path.exists(tp):
                updated = max(updated, time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(tp))))
        if pv and pv["date"]:
            updated = max(updated, pv["date"])
        frames = c.get("frames") or (rv or {}).get("n") or (pv or {}).get("frames")
        rig = d["characters"].get(c["character"], {}).get("rig_url", "")
        # Tiếp tục: trang của giai đoạn hiện tại
        st = c.get("stage", "analysis")
        cont = None
        if st in ("rig",) and rig:
            cont = ("Rig Lab", rig)
        elif st in ("spline", "polish", "export") and r.get("url"):
            cont = ("Review Lab", r["url"])
        elif p.get("url"):
            cont = ("Pose Lab", p["url"])
        elif r.get("url"):
            cont = ("Review Lab", r["url"])
        elif rig:
            cont = ("Rig Lab", rig)
        out.append({**c, "status_manual": c.get("status", ""), "status": status_of(c), "thumb": thumb, "updated": updated, "frames": frames,
                    "rig_url": rig, "pose_url": p.get("url", ""), "review_url": r.get("url", ""),
                    "review_latest": rv, "pose_latest": pv, "continue": cont,
                    "name": c.get("title") or r.get("name") or (p.get("clip") or c["id"]).split("_", 1)[-1],
                    "base_name": r.get("name") or (p.get("clip") or c["id"]).split("_", 1)[-1]})
    return out


def state():
    d = load()
    clips = enrich(d)
    log = git_log()
    projs = []
    for pr in d["projects"]:
        chars = pr.get("characters", [])
        mine = [c for c in clips if c["character"] in chars]
        act = [g for g in log if any(w and w.lower() in g["msg"].lower() for w in chars)]
        projs.append({**pr, "clips": [c["id"] for c in mine], "activity": act[:8],
                      "cover": next((c["thumb"] for c in mine if c["thumb"]), ""),
                      "updated": max([c["updated"] for c in mine] + [pr.get("created", "")] or [""])})
    return {"projects": projs, "characters": d["characters"], "clips": clips, "stages": STAGES, "activity": log[:10],
            "root": ROOT}


def new_project(b):
    d = load()
    name = (b.get("name") or "").strip()
    if not name:
        raise ValueError("Thiếu tên dự án")
    pid = slug(name)
    if any(p["id"] == pid for p in d["projects"]):
        raise ValueError(f"Dự án '{name}' đã có")
    chars = [c.strip() for c in b.get("characters", []) if c.strip()]
    for c in chars:
        d["characters"].setdefault(c, {"rig_url": ""})
    d["projects"].append({"id": pid, "name": name, "desc": b.get("desc", ""), "characters": chars,
                          "labels": {c: b.get("labels", {}).get(c, "") for c in chars}, "created": date.today().isoformat()})
    save(d)
    os.makedirs(os.path.join(ROOT, "work", pid), exist_ok=True)
    return pid


def add_character(b):
    d = load()
    pr = next((p for p in d["projects"] if p["id"] == b.get("project")), None)
    ch = (b.get("character") or "").strip()
    if not pr or not ch:
        raise ValueError("Thiếu dự án hoặc tên nhân vật")
    if ch not in pr["characters"]:
        pr["characters"].append(ch)
    pr.setdefault("labels", {})[ch] = b.get("label", "")
    d["characters"].setdefault(ch, {"rig_url": ""})
    save(d)


def new_clip(b):
    d = load()
    ch = (b.get("character") or "").strip()
    clip = re.sub(r"\s+", "_", (b.get("clip") or "").strip())
    if not ch or not clip:
        raise ValueError("Thiếu nhân vật hoặc tên anim")
    cid = slug(f"{ch}_{clip}")
    if any(c["id"] == cid for c in d["clips"]):
        raise ValueError(f"Anim '{cid}' đã có")
    d["characters"].setdefault(ch, {"rig_url": ""})
    pr = next((p for p in d["projects"] if p["id"] == b.get("project")), None)
    if pr and ch not in pr["characters"]:
        pr["characters"].append(ch)
    stage = "analysis" if d["characters"][ch].get("rig_url") else "rig"
    pretty = clip.replace("_", " ")
    entry = {"id": cid, "character": ch, "stage": stage, "note": "Mới tạo từ Home: chờ /new_clip " + cid,
             "frames": int(b["frames"]) if str(b.get("frames", "")).isdigit() else None,
             "fps": int(b["fps"]) if str(b.get("fps", "")).isdigit() else 30,
             "ref": b.get("ref", ""), "desc": b.get("desc", ""), "created": date.today().isoformat(),
             "updated": date.today().isoformat(),
             "review": {"key": cid, "clip": clip, "title": f"{ch} {pretty} Review Lab", "crumb": f"{ch} · anim",
                        "name": pretty, "parts": None, "url": ""},
             "pose": {"key": cid, "clip": f"{ch}_{clip}", "title": f"{ch} {pretty} Pose Lab", "url": ""}}
    d["clips"].append(entry)
    save(d)
    folder = os.path.join(ROOT, "work", cid)
    os.makedirs(folder, exist_ok=True)
    brief = os.path.join(folder, "brief.md")
    if not os.path.exists(brief):
        with open(brief, "w", encoding="utf8") as f:
            f.write(f"# {ch} {pretty}\n\n- Dự án: {pr['name'] if pr else '-'}\n- Frame: {entry['frames'] or '?'} @ {entry['fps']} fps\n"
                    f"- Ref: {entry['ref'] or '(chưa có)'}\n- Tạo: {entry['created']} (Home)\n\n## Mô tả\n\n{entry['desc'] or '(chưa có)'}\n")
    return cid


def update_clip(b):
    d = load()
    c = next((x for x in d["clips"] if x["id"] == b.get("id")), None)
    if not c:
        raise ValueError("Không có anim này")
    if b.get("stage") in STAGES:
        c["stage"] = b["stage"]
    if "note" in b:
        c["note"] = b["note"]
    if "title" in b:  # tên hiển thị trên Home; id, thư mục, trang Lab giữ nguyên
        t = (b["title"] or "").strip()
        if t:
            c["title"] = t
        else:
            c.pop("title", None)
    if b.get("status") in ("working", "waiting", "done", "paused", ""):
        if b["status"]:
            c["status"] = b["status"]
        else:
            c.pop("status", None)
    c["updated"] = date.today().isoformat()
    save(d)


def update_project(b):
    d = load()
    p = next((x for x in d["projects"] if x["id"] == b.get("id")), None)
    if not p:
        raise ValueError("Không có dự án này")
    if "name" in b and not (b["name"] or "").strip():
        raise ValueError("Tên dự án không được để trống")
    for k in ("name", "desc"):
        if k in b:
            p[k] = b[k].strip() if k == "name" else b[k]
    save(d)


ROUTES = {"/api/project": new_project, "/api/character": add_character, "/api/clip": new_clip,
          "/api/clip/update": update_clip, "/api/project/update": update_project}


class H(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, ctype):
        data = open(path, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store" if ctype.startswith("text/html") else "max-age=300")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path in ("/", "/index.html"):
            return self.send_file(os.path.join(HERE, "index.html"), "text/html; charset=utf-8")
        if path == "/api/state":
            try:
                return self.send_json(state())
            except Exception as e:
                return self.send_json({"error": str(e)}, 500)
        if path.startswith("/work/"):
            full = os.path.abspath(os.path.join(ROOT, path.lstrip("/")))
            ext = os.path.splitext(full)[1].lower()
            if full.startswith(os.path.join(ROOT, "work")) and ext in MEDIA and os.path.isfile(full):
                return self.send_file(full, MEDIA[ext])
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        fn = ROUTES.get(path)
        if not fn:
            return self.send_error(404)
        try:
            n = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(n) or b"{}")
            res = fn(body)
            self.send_json({"ok": True, "id": res})
        except ValueError as e:
            self.send_json({"ok": False, "error": str(e)}, 400)
        except Exception as e:
            self.send_json({"ok": False, "error": f"{type(e).__name__}: {e}"}, 500)


if __name__ == "__main__":
    load()
    print(f"Home: http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
