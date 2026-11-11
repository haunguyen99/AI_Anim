"""Home: trang quản lý dự án chạy trên máy (một người dùng, dữ liệu nằm trên máy này).
Home → dự án (theo game) → animation → mở trang đang làm (Rig Lab / Pose Lab / Review Lab).
Đọc/ghi sổ work/clips.json (cùng sổ với tools/clip_registry.py), thêm khóa "projects".

Chạy:  .venv\\Scripts\\python.exe -I tools\\home\\server.py   rồi mở http://127.0.0.1:8780
"""
import base64, json, os, re, shutil, subprocess, sys, tempfile, time
from datetime import date
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, unquote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import store
import fbx_import
import rig_data
import studio_bridge
import pose_data
import scene_file
import keypose
import sessions

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REG = os.path.join(ROOT, "work", "clips.json")
REVIEW_HTML = os.path.join(ROOT, "work", "review_page", "index.html")
POSE_HTML = os.path.join(ROOT, "work", "pose_lab", "index.html")
STAGES = ["rig", "analysis", "p0", "blocking", "spline", "polish", "export"]
PORT = int(os.environ.get("HOME_PORT") or os.environ.get("PORT") or "8780")
SPINE_PORT = int(os.environ.get("SPINE_PORT") or "8781")   # Spine Live chạy riêng: tools/spine_live/server.py
LAB_DIRS = {"mesh": ("mesh_lab", "pages"), "pose": ("pose_lab", "pages"), "review": ("review_page", "pages"), "rig": ("rig_lab", "pages")}
LAB_STATIC = {".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8", ".css": "text/css; charset=utf-8",
              ".glb": "model/gltf-binary", ".gltf": "model/gltf+json", ".svg": "image/svg+xml", ".bin": "application/octet-stream", ".txt": "text/plain; charset=utf-8"}
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


def lab_dir(kind, id_):
    base, sub = LAB_DIRS[kind]
    return os.path.join(ROOT, "work", base, sub, re.sub(r"[^A-Za-z0-9_.\-]", "_", id_))


def rig_page_of(char, d, kind="rig"):
    """Tên thư mục trang Rig/Mesh Lab của nhân vật: khóa rig_page trong sổ, hoặc thư mục trùng tên (không phân biệt hoa thường)."""
    c = (d.get("characters") or {}).get(char) or {}
    if c.get("rig_page"):
        return c["rig_page"]
    base = os.path.join(ROOT, "work", LAB_DIRS[kind][0], "pages")
    if os.path.isdir(base):
        names = sorted(os.listdir(base))
        for n in names:
            if n.lower() == char.lower():
                return n
        for n in names:
            if n.lower().startswith(char.lower()):
                return n
    return ""


STUDIO = os.path.join(ROOT, "tools", "studio")
RIGLAB = os.path.join(ROOT, "work", "rig_lab")


def studio_chars():
    """Nhân vật mở được trong Studio: Gaygor (ref_gaygor) + mỗi work/rig_lab/chars/<id>.json có mesh_cm.json."""
    out = []
    if os.path.isfile(os.path.join(RIGLAB, "ref_gaygor", "ref_mesh.json")):
        out.append({"id": "gaygor", "name": "Gaygor"})
    cd = os.path.join(RIGLAB, "chars")
    if os.path.isdir(cd):
        for f in sorted(os.listdir(cd)):
            cid = f[:-5]
            if f.endswith(".json") and os.path.isfile(os.path.join(cd, cid, "mesh_cm.json")):
                try:
                    name = json.load(open(os.path.join(cd, f), encoding="utf8")).get("name") or cid
                except Exception:
                    name = cid
                out.append({"id": cid, "name": name})
    return out


def studio_skeleton(ref, sc):
    """Xương bind của nhân vật (work/rig_lab/<ref_dir>/ref_skeleton.json), cm. Xương thiếu bind (vd root) lấy vị trí cha / gốc."""
    f = os.path.join(RIGLAB, ref, "ref_skeleton.json") if ref else ""
    if not f or not os.path.isfile(f):
        return []
    sk = json.load(open(f, encoding="utf8"))
    pos = {s["name"]: s.get("bind_pos") for s in sk}
    out = []
    for s in sk:
        p, q = s.get("bind_pos"), s.get("parent")
        while p is None and q:
            p, q = pos.get(q), next((x.get("parent") for x in sk if x["name"] == q), None)
        out.append({"name": s["name"], "parent": s.get("parent"), "pos": [round(v * sc, 3) for v in (p or [0, 0, 0])]})
    return out


def studio_char(cid):
    """Mesh gốc (cm, +Y lên) của nhân vật, cùng nguồn với work/mesh_lab/build_mesh.py."""
    if not re.match(r"^[A-Za-z0-9_\-]+$", cid):
        return None
    if cid == "gaygor":
        p, name, ref, sc = os.path.join(RIGLAB, "ref_gaygor", "ref_mesh.json"), "Gaygor", "ref_gaygor", 1
    else:
        cf = os.path.join(RIGLAB, "chars", cid + ".json")
        if not os.path.isfile(cf):
            return None
        C = json.load(open(cf, encoding="utf8"))
        p, name, ref, sc = os.path.join(RIGLAB, "chars", cid, "mesh_cm.json"), C.get("name") or cid, C.get("ref_dir", ""), C.get("scale", 1)
    if not os.path.isfile(p):
        return None
    meshes = json.load(open(p, encoding="utf8"))
    tp = os.path.join(RIGLAB, "chars", cid, "texture.png")   # Tệp → Gắn texture… (fbx_import.set_texture)
    tex = "/work/rig_lab/chars/%s/texture.png?v=%d" % (cid, int(os.path.getmtime(tp))) if os.path.isfile(tp) else None
    return {"id": cid, "name": name, "unit": "cm", "skeleton": studio_skeleton(ref, sc), "texture": tex,
            "meshes": [dict({"name": m["name"], "verts": [round(v, 3) for v in m["verts"]], "tris": m["tris"]},
                            **({"weights": m["weights"]} if m.get("weights") else {}),   # skin FBX: {xương: [[đỉnh], [w]]}
                            **({"uvc": [round(v, 4) for v in m["uvc"]]} if m.get("uvc") else {}),   # UV theo góc tam giác
                            **({"tex": m["tex"]} if m.get("tex") else {})) for m in meshes]}


def lab_html(kind, id_):
    """Trang Lab đã build, thêm <base> để model/clip/ảnh ref tương đối tìm đúng chỗ khi mở trong vỏ ứng dụng."""
    p = os.path.join(lab_dir(kind, id_), "index.html")
    if not os.path.isfile(p):
        return None
    html = open(p, encoding="utf8").read()
    base = "/work/%s/" % LAB_DIRS[kind][0]
    if kind == "pose":
        html = html.replace('src="fbxexport.js"', 'src="fbx/fbxexport.js"')   # file nằm ở work/pose_lab/fbx/
    tag = '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><base href="%s">' % base
    tag += "<script>window.LOCALDB_API = location.origin;</script>"   # mở từ máy khác (--lan): lưu vào server này, không vào 127.0.0.1 của máy đó
    return (tag + html).encode("utf8")


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
        pid = (p.get("clip") or c["id"])
        rp = rig_page_of(c["character"], d)
        labs = {"pose": os.path.isfile(os.path.join(lab_dir("pose", c["id"]), "index.html")),
                "review": os.path.isfile(os.path.join(lab_dir("review", c["id"]), "index.html")),
                "rig": rp, "mesh": rig_page_of(c["character"], d, "mesh")}
        labs["studio"] = labs["mesh"] if any(x["id"] == labs["mesh"] for x in studio_chars()) else ""
        out.append({**c, "labs": labs, "status_manual": c.get("status", ""), "status": status_of(c), "thumb": thumb, "updated": updated, "frames": frames,
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
    # mỗi dự án một thư mục: work/<dự án>/<anim>
    pr = pr or next((p for p in d["projects"] if ch in p.get("characters", [])), None)
    rel_dir = "work/" + (pr["id"] + "/" if pr else "") + cid
    entry = {"id": cid, "character": ch, "stage": stage, "note": "Mới tạo từ Home: chờ /new_clip " + cid,
             "dir": rel_dir,
             "frames": int(b["frames"]) if str(b.get("frames", "")).isdigit() else None,
             "fps": int(b["fps"]) if str(b.get("fps", "")).isdigit() else 30,
             "ref": b.get("ref", ""), "desc": b.get("desc", ""), "created": date.today().isoformat(),
             "updated": date.today().isoformat(),
             "review": {"key": cid, "clip": clip, "title": f"{ch} {pretty} Review Lab", "crumb": f"{ch} · anim",
                        "name": pretty, "parts": None, "url": ""},
             "pose": {"key": cid, "clip": f"{ch}_{clip}", "title": f"{ch} {pretty} Pose Lab", "url": ""}}
    d["clips"].append(entry)
    save(d)
    folder = os.path.join(ROOT, *rel_dir.split("/"))
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


# ---------- nối dữ liệu giữa các Lab (vỏ ứng dụng gọi) ----------
REGISTRY = os.path.join(ROOT, "tools", "clip_registry.py")


def run_registry(*args):
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", REGISTRY, *args], cwd=ROOT, capture_output=True, text=True, encoding="utf8")
    if r.returncode:
        raise ValueError((r.stderr or r.stdout or "clip_registry lỗi").strip().splitlines()[-1])
    return r.stdout


def clip_of(d, id_):
    for c in d["clips"]:
        if c["id"] == id_:
            return c
    raise ValueError("không có anim " + str(id_))


def safe(s):
    return re.sub(r"[^A-Za-z0-9_.\-]", "_", s or "x")


def rig_to_pose(b):
    """Rig Lab → Pose Lab: ghi glTF của rig làm model base pose rồi đăng ký version Pose Lab (frames=1) và build lại trang."""
    d = load(); c = clip_of(d, b.get("clip")); p = c.get("pose") or {}
    if not p.get("clip"):
        raise ValueError("anim chưa đăng ký Pose Lab (gõ /new_clip " + c["id"] + ")")
    mdir = os.path.join(ROOT, "work", "pose_lab", "models"); os.makedirs(mdir, exist_ok=True)
    n = 1
    while os.path.exists(os.path.join(mdir, "%s_rig_v%d.json" % (safe(p["clip"]).lower(), n))):
        n += 1
    ver = "rig_v%d" % n; fn = "%s_%s.json" % (safe(p["clip"]).lower(), ver)
    with open(os.path.join(mdir, fn), "w", encoding="utf8") as f:
        json.dump(b["gltf"], f, separators=(",", ":"))
    run_registry("pose-version", c["id"], "--version", ver, "--label", "Base pose từ Rig Lab", "--glb", "models/" + fn, "--frames", "1", "--keys", "1",
                 "--mode", "keys", "--note", "Model xuất từ Rig Lab (skin + xương hiện tại), frame 1 = pose đứng của rig.")
    if c.get("stage") in ("rig", "analysis"):
        run_registry("stage", c["id"], "p0")
    run_registry("build")
    return ver


def studio_new_clip(b):
    """Studio Animate → Anim mới…: đăng ký anim cho nhân vật Studio (?char=<id>) như Home, rồi tạo phiên bản Pose đầu tiên
    (p0_v1, dạng key, frame 1 = pose đứng) từ rig hiện tại (glTF do trang dựng) để anim mở được ngay trong Studio."""
    d = load(); cid = (b.get("char") or "").strip()
    names = [n for n in (d.get("characters") or {}) if rig_page_of(n, d, "mesh") == cid or n.lower() == cid.lower()]
    used = {c["character"] for c in d["clips"]}
    ch = next((n for n in names if n in used), names[0] if names else (b.get("name") or cid))
    if not ch:
        raise ValueError("Thiếu nhân vật")
    if not b.get("gltf"):
        raise ValueError("Thiếu model của rig")
    nid = new_clip({"character": ch, "clip": b.get("clip"), "frames": b.get("frames"), "fps": b.get("fps"), "desc": b.get("desc", ""), "ref": ""})
    d = load(); c = clip_of(d, nid); p = c["pose"]
    c["note"] = "Tạo từ Studio (Animate → Anim mới): P0 từ rig hiện tại, chờ phân tích / blocking"; save(d)
    frames = int(b["frames"]) if str(b.get("frames", "")).isdigit() and int(b["frames"]) > 0 else 1
    mdir = os.path.join(ROOT, "work", "pose_lab", "models"); os.makedirs(mdir, exist_ok=True)
    fn = "%s_rig_v1.json" % safe(p["clip"]).lower()
    with open(os.path.join(mdir, fn), "w", encoding="utf8") as f:
        json.dump(b["gltf"], f, separators=(",", ":"))
    run_registry("pose-version", nid, "--version", "p0_v1", "--label", "P0 từ rig Studio", "--glb", "models/" + fn, "--frames", str(frames),
                 "--fps", str(c.get("fps") or 30), "--keys", "1", "--mode", "keys", "--note", "Tạo từ Studio (Animate → Anim mới): frame 1 = pose đứng của rig hiện tại.")
    run_registry("stage", nid, "p0")
    run_registry("build")
    return nid


def studio_delete_clip(b):
    """Studio → Xoá anim: không xoá hẳn mà chuyển mọi thứ của anim vào work/_trash/<anim>_<giờ>/ (khôi phục được):
    mục trong clips.json (clip.json), dòng phiên bản Pose / Review (lines.json), trang Pose / Review, model, video, kho key / ghi chú,
    thư mục work/<dự án>/<anim>. Thứ dùng chung với anim khác (tên clip Review trùng, model, thư mục chung) được giữ nguyên."""
    d = load(); c = clip_of(d, b.get("id")); others = [x for x in d["clips"] if x is not c]
    T = os.path.join(ROOT, "work", "_trash", "%s_%s" % (safe(c["id"]), time.strftime("%Y%m%d-%H%M%S")))
    os.makedirs(T, exist_ok=True); moved = []

    def move(rel):
        src = os.path.join(ROOT, *rel.split("/"))
        if os.path.exists(src):
            dst = os.path.join(T, "files", *rel.split("/")); os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst); moved.append(rel)

    lines = {}
    for lab, marker, kind in (("pose_lab", "const POSES = [", "pose"), ("review_page", "const CLIPS = [", "review")):
        name = (c.get(kind) or {}).get("clip")
        if not name or any((x.get(kind) or {}).get("clip") == name for x in others):
            continue   # tên clip dùng chung với anim khác: không đụng dòng phiên bản
        P = os.path.join(ROOT, "work", lab, "index.html"); src = open(P, "rb").read().decode("utf8")
        i = src.index(marker); j = src.index("\n];", i)
        tag = "{ clip: " + json.dumps(name, ensure_ascii=False) + ","
        body = src[i:j].split("\n"); mine = [l for l in body if l.strip().startswith(tag)]
        if not mine:
            continue
        lines[kind] = mine
        rest = src[:i] + "\n".join(l for l in body if not l.strip().startswith(tag)) + src[j:]
        open(P, "wb").write(rest.encode("utf8"))
        for l in mine:   # model / video / ảnh của các dòng này, nếu không dòng nào khác dùng
            for f in re.findall(r'(?:glb|src|thumb): "([^"]+)"', l):
                if '"' + f + '"' not in rest:
                    move("work/%s/%s" % (lab, f))
        key = (c.get(kind) or {}).get("key")
        if key:
            move("work/%s/pages/%s" % (lab, key))
    for kind in ("pose", "review"):   # kho key / ghi chú (<tiêu đề trang>_pose_lab, _review_lab)
        t = (c.get(kind) or {}).get("title")
        if t:
            move("work/store/" + pose_data.slug(t))
    dr = c.get("dir")
    if dr and dr.startswith("work/") and dr.count("/") >= 2 and not any(x.get("dir") == dr for x in others):
        move(dr)
    with open(os.path.join(T, "clip.json"), "w", encoding="utf8") as f:
        json.dump({"clip": c, "lines": lines, "moved": moved, "deleted": time.strftime("%Y-%m-%d %H:%M:%S")}, f, ensure_ascii=False, indent=1)
    d["clips"] = others; save(d)
    return {"trash": os.path.relpath(T, ROOT).replace("\\", "/"), "moved": moved, "lines": {k: len(v) for k, v in lines.items()}}


def _retime_playblast(ff, path, n, fps):
    """Tab Studio chạy nền ghi playblast theo thời gian thực (~1 s mỗi frame anim: SDR01 Shoot pb1 2026-10-29 ra 915 frame cho 30).
    Video có quá nhiều frame thì lấy frame giữa của mỗi đoạn, ghép lại đúng n frame @ fps."""
    fp = shutil.which("ffprobe")
    if not fp or n < 1:
        return
    try:
        q = subprocess.run([fp, "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                            "-of", "csv=p=0", path], capture_output=True, text=True, timeout=120)
        m = int(q.stdout.strip().split(",")[0])
    except Exception:
        return
    if m <= n * 1.5:
        return
    step = m / n
    sel = "+".join("eq(n\\,%d)" % int(step * i + step / 2) for i in range(n))
    tmp = path + ".retime.webm"
    q = subprocess.run([ff, "-y", "-v", "error", "-i", path, "-vf", "select='%s',setpts=N/%d/TB" % (sel, fps), "-r", str(fps), "-an",
                        "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "30", "-deadline", "good", "-cpu-used", "4", "-pix_fmt", "yuv420p", tmp],
                       capture_output=True, timeout=300)
    if q.returncode == 0 and os.path.getsize(tmp) > 0:
        os.replace(tmp, path)


def playblast_to_review(b):
    """Pose Lab → Review Lab: lưu video playblast, nén lại bằng ffmpeg (có thể tua), đăng ký version Review và build lại trang."""
    d = load(); c = clip_of(d, b.get("clip")); r = c.get("review") or {}
    if not r.get("clip"):
        raise ValueError("anim chưa đăng ký Review Lab (gõ /new_clip " + c["id"] + ")")
    cdir = os.path.join(ROOT, "work", "review_page", "clips"); os.makedirs(cdir, exist_ok=True)
    base = safe(c["id"]); n = 1
    while os.path.exists(os.path.join(cdir, "%s_pb%d.webm" % (base, n))):
        n += 1
    ver = "pb%d" % n; stem = "%s_%s" % (base, ver)
    raw = base64.b64decode(b["webm_b64"]); out = os.path.join(cdir, stem + ".webm")
    ff = shutil.which("ffmpeg"); ok = False
    if ff:
        tmp = os.path.join(tempfile.gettempdir(), stem + "_raw.webm")
        with open(tmp, "wb") as f:
            f.write(raw)
        try:
            q = subprocess.run([ff, "-y", "-v", "error", "-i", tmp, "-an", "-r", str(int(b.get("fps") or 30)), "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "30", "-deadline", "realtime", "-cpu-used", "8", "-pix_fmt", "yuv420p", out],
                               capture_output=True, timeout=180)
            ok = q.returncode == 0 and os.path.getsize(out) > 0
        except Exception:
            ok = False
        try:
            os.remove(tmp)
        except OSError:
            pass
    if not ok:
        with open(out, "wb") as f:
            f.write(raw)
    if ok:
        _retime_playblast(ff, out, int(b["n"]), int(b.get("fps") or 30))
    if b.get("thumb_b64"):
        with open(os.path.join(cdir, stem + ".jpg"), "wb") as f:
            f.write(base64.b64decode(b["thumb_b64"]))
    args = ["review-version", c["id"], "--version", ver, "--label", b.get("label") or ("%s · playblast từ Pose Lab (%s)" % (c.get("title") or c["id"], ver)),
            "--src", "clips/%s.webm" % stem, "--thumb", "clips/%s.jpg" % stem, "--n", str(int(b["n"])), "--fps", str(int(b.get("fps") or 30)),
            "--w", str(int(b["w"])), "--h", str(int(b["h"]))]
    if b.get("views"):
        args += ["--views", b["views"]]
    args += ["--note", b.get("note") or ("Quay trong Pose Lab" + ("" if ok else " (chưa nén lại, có thể không tua được)") + ".")]
    run_registry(*args)
    run_registry("build")
    return {"version": ver, "reencoded": ok}


def fbx_parse(b):
    """Studio → Tệp → Nhập FBX: đọc FBX (base64), trả mesh cm Y lên."""
    return fbx_import.parse(base64.b64decode(b.get("fbx_b64") or ""))


def rig_build(b):
    """Studio workspace Rig: dựng dữ liệu rig (landmark gợi ý, trang Rig Lab) cho nhân vật mới."""
    return rig_data.build(b.get("id", ""))


def fbx_new_char(b):
    """Studio: tạo nhân vật mới từ FBX (work/rig_lab/ref_<id>, chars/<id>)."""
    return fbx_import.new_char(base64.b64decode(b.get("fbx_b64") or ""), b.get("name", ""), b.get("filename", ""))


def char_texture(b):
    """Studio → Tệp → Gắn texture…: ảnh (base64, tga/png/jpg…) → work/rig_lab/chars/<id>/texture.png.
    Hoặc {"id", "path"}: đọc thẳng file trên máy (cho studio_cmd / Claude)."""
    if b.get("path"):
        p = b["path"]
        if os.path.splitext(p)[1].lower() not in (".tga", ".png", ".jpg", ".jpeg", ".bmp", ".psd", ".tif", ".tiff", ".webp"):
            raise ValueError("chỉ nhận file ảnh")
        if not os.path.isfile(p):
            raise ValueError("không thấy file " + p)
        return fbx_import.set_texture(b.get("id", ""), open(p, "rb").read(), os.path.basename(p))
    return fbx_import.set_texture(b.get("id", ""), base64.b64decode(b.get("img_b64") or ""), b.get("filename", ""))


def scene_open(b):
    """Studio → Tệp → Mở cảnh…: bung file .aas (base64); dry=True chỉ đọc manifest."""
    return scene_file.open_scene(base64.b64decode(b.get("zip_b64") or ""), dry=bool(b.get("dry")))


ROUTES = {"/api/scene/open": scene_open, "/api/char/texture": char_texture, "/api/rig/to-pose": rig_to_pose, "/api/fbx/parse": fbx_parse, "/api/rig/build": rig_build, "/api/fbx/new-char": fbx_new_char, "/api/playblast": playblast_to_review, "/api/project": new_project, "/api/character": add_character, "/api/clip": new_clip, "/api/clip/studio-new": studio_new_clip, "/api/clip/studio-delete": studio_delete_clip, "/api/keypose/assign": keypose.assign, "/api/keypose/phase": keypose.phase_set, "/api/keypose/views": keypose.views_set,
          "/api/clip/update": update_clip, "/api/project/update": update_project}


class H(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):   # Lab chạy ở cổng khác (Pose 8771, Rig 8772...) gọi API kho
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def store_call(self, method):
        parts = [unquote(x) for x in urlparse(self.path).path[len("/api/store"):].strip("/").split("/")]
        body = None
        if method in ("POST", "PUT", "PATCH"):
            n = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(n) or b"{}")
        try:
            code, obj = store.handle(method, parts, body)
        except ValueError as e:
            code, obj = 400, {"error": str(e)}
        except Exception as e:
            code, obj = 500, {"error": f"{type(e).__name__}: {e}"}
        self.send_json(obj, code)

    def do_PUT(self):
        if urlparse(self.path).path.startswith("/api/store"):
            return self.store_call("PUT")
        self.send_error(404)

    def do_PATCH(self):
        if urlparse(self.path).path.startswith("/api/store"):
            return self.store_call("PATCH")
        self.send_error(404)

    def do_DELETE(self):
        if urlparse(self.path).path.startswith("/api/store"):
            return self.store_call("DELETE")
        self.send_error(404)

    def send_bytes(self, data, ctype, nocache=False):
        total = len(data)
        rng = self.headers.get("Range")
        code, start, end = 200, 0, total - 1
        m = re.match(r"bytes=(\d*)-(\d*)", rng or "")
        if m and total:
            a, b = m.group(1), m.group(2)
            start = int(a) if a else max(0, total - int(b or 0))
            end = int(b) if (a and b) else total - 1
            end = min(end, total - 1)
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", "bytes */%d" % total)
                self.end_headers()
                return
            code = 206
        chunk = data[start:end + 1]
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        if code == 206:
            self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, total))
        self.send_header("Content-Length", str(len(chunk)))
        self.send_header("Cache-Control", "no-store" if nocache or ctype.startswith("text/html") else "max-age=60")
        self.end_headers()
        self.wfile.write(chunk)

    def send_file(self, path, ctype):
        with open(path, "rb") as f:
            self.send_bytes(f.read(), ctype)

    def spine_moved(self):
        """Spine Live chạy riêng (tools/spine_live/server.py, cổng SPINE_PORT): chuyển trang sang đó, giữ query."""
        u = urlparse(self.path)
        host = (self.headers.get("Host") or "127.0.0.1").rsplit(":", 1)[0]
        url = f"http://{host}:{SPINE_PORT}{u.path}" + ("?" + u.query if u.query else "")
        import socket
        try:
            socket.create_connection(("127.0.0.1", SPINE_PORT), timeout=0.3).close()
        except OSError:
            html = ("<meta charset=utf-8><body style='font:15px sans-serif;padding:24px'>Spine Live chưa chạy. "
                    "Bấm <b>tools/spine_live/start.bat</b> (hoặc chạy <code>.venv/Scripts/python.exe -I tools/spine_live/server.py</code>) "
                    f"rồi mở <a href='{url}'>{url}</a>.</body>").encode("utf8")
            return self.send_bytes(html, "text/html; charset=utf-8")
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path in ("/", "/index.html"):   # mở là vào thẳng Studio (viewport), nhân vật mở lần trước
            return self.send_file(os.path.join(STUDIO, "index.html"), "text/html; charset=utf-8")
        if path in ("/home", "/home/"):    # trang quản lý dự án (trước đây ở /)
            return self.send_file(os.path.join(HERE, "index.html"), "text/html; charset=utf-8")
        if path.startswith("/api/store"):
            return self.store_call("GET")
        if path.startswith("/api/studio/"):   # cầu nối Claude ↔ Studio (studio_bridge.py)
            from urllib.parse import parse_qs
            if studio_bridge.handle_get(self, path, parse_qs(urlparse(self.path).query)):
                return
        if path in ("/spine", "/spine/") or path.startswith(("/spine/", "/api/spine/", "/spine-live/")):   # Spine Live đã tách ra server riêng
            return self.spine_moved()
        if path in ("/keypose", "/keypose/") or path.startswith("/api/keypose/"):   # Key Pose: duyệt ảnh Codex + yêu cầu thêm ảnh (keypose.py)
            from urllib.parse import parse_qs
            if keypose.handle_get(self, path, parse_qs(urlparse(self.path).query)):
                return
        if path in ("/sessions", "/sessions/") or path.startswith("/api/sessions/"):   # quản lý phiên Claude Code (sessions.py)
            from urllib.parse import parse_qs
            if sessions.handle_get(self, path, parse_qs(urlparse(self.path).query)):
                return
        if path in ("/keypose", "/keypose/") or path.startswith("/api/keypose/"):   # Key Pose: duyệt ảnh Codex + yêu cầu thêm ảnh (keypose.py)
            from urllib.parse import parse_qs
            if keypose.handle_get(self, path, parse_qs(urlparse(self.path).query)):
                return
        if path == "/api/state":
            try:
                return self.send_json(state())
            except Exception as e:
                return self.send_json({"error": str(e)}, 500)
        if path == "/api/chars":
            return self.send_json(studio_chars())
        if path == "/api/joint-rules":   # luật giới hạn + liên động khớp cho Studio (?char=<id>): mặc định + chars/<id>/joint_rules.json
            from urllib.parse import parse_qs
            sys.path.insert(0, os.path.join(ROOT, "tools")); import joint_rules
            cid = re.sub(r"[^\w.-]", "", (parse_qs(urlparse(self.path).query).get("char") or [""])[0])
            return self.send_json(joint_rules.load(os.path.join(ROOT, "work", "rig_lab", "chars", cid, "joint_rules.json") if cid else None))
        if path == "/api/poses":   # anim có Pose của một nhân vật Studio (?char=<id>)
            from urllib.parse import parse_qs
            cid = (parse_qs(urlparse(self.path).query).get("char") or [""])[0]
            d = load()
            names = [n for n in (d.get("characters") or {}) if rig_page_of(n, d, "mesh") == cid or n.lower() == cid.lower()]
            return self.send_json(pose_data.clips_for(names if cid else None))
        m = re.match(r"^/api/poses/([^/]+)$", path)
        if m:
            r = pose_data.poses(m.group(1))
            return self.send_json(r) if r else self.send_json({"error": "anim chưa có phiên bản Pose"}, 404)
        m = re.match(r"^/api/rigdata/([^/]+)$", path)
        if m:
            try:
                d = rig_data.data(m.group(1))
            except ValueError as e:
                return self.send_json({"error": str(e)}, 400)
            return self.send_json(d) if d else self.send_json({"error": "chưa có dữ liệu rig", "build": True}, 404)
        m = re.match(r"^/api/scene/save/([^/]+)$", path)   # Tệp → Lưu cảnh…: tải file .aas của nhân vật (scene_file.py)
        if m:
            try:
                data = scene_file.save(m.group(1))
            except ValueError as e:
                return self.send_json({"error": str(e)}, 400)
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", 'attachment; filename="%s_%s.aas"' % (m.group(1), date.today().isoformat()))
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        m = re.match(r"^/api/char/([^/]+)$", path)
        if m:
            c = studio_char(m.group(1))
            return self.send_json(c) if c else self.send_json({"error": "không có nhân vật " + m.group(1)}, 404)
        if path == "/studio" or path.startswith("/studio/"):
            rel = path[len("/studio/"):] if path.startswith("/studio/") else ""
            full = os.path.abspath(os.path.join(STUDIO, rel))
            ext = os.path.splitext(full)[1].lower()
            if full.startswith(STUDIO + os.sep) and os.path.isfile(full) and ext in LAB_STATIC:
                return self.send_bytes(open(full, "rb").read(), LAB_STATIC[ext], True)
            if not ext:   # /studio, /studio/<nhân vật>: vỏ ứng dụng
                return self.send_file(os.path.join(STUDIO, "index.html"), "text/html; charset=utf-8")
            return self.send_error(404)
        m = re.match(r"^/lab/(mesh|pose|review|rig)/([^/]+)/?$", path)
        if m:
            body = lab_html(m.group(1), m.group(2))
            if body is None:
                return self.send_json({"error": "chưa có trang " + m.group(1) + " cho " + m.group(2)}, 404)
            return self.send_bytes(body, "text/html; charset=utf-8", True)
        if path.startswith("/work/"):
            full = os.path.abspath(os.path.join(ROOT, path.lstrip("/")))
            ext = os.path.splitext(full)[1].lower()
            work = os.path.join(ROOT, "work")
            if full.startswith(work + os.sep) and os.path.isfile(full):
                if ext in MEDIA:
                    return self.send_file(full, MEDIA[ext])
                top = os.path.relpath(full, work).replace("\\", "/").split("/")[0]
                if ext in LAB_STATIC and top in ("pose_lab", "review_page", "rig_lab", "mesh_lab"):
                    return self.send_file(full, LAB_STATIC[ext])
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path.startswith("/api/store"):
            return self.store_call("POST")
        if path.startswith("/api/studio/"):
            n = int(self.headers.get("Content-Length", "0"))
            if studio_bridge.handle_post(self, path, json.loads(self.rfile.read(n) or b"{}")):
                return
        if path.startswith("/api/sessions/"):   # quản lý phiên Claude Code (sessions.py)
            n = int(self.headers.get("Content-Length", "0"))
            if sessions.handle_post(self, path, json.loads(self.rfile.read(n) or b"{}")):
                return
        if path.startswith("/api/spine/"):   # Spine Live đã tách ra server riêng (tools/spine_live/server.py)
            return self.send_json({"ok": False, "error": f"Spine Live chạy riêng ở cổng {SPINE_PORT}"}, 410)
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
    lan = "--lan" in sys.argv   # --lan (tools/home/start_lan.bat): máy khác cùng mạng mở được; không có mật khẩu, chỉ dùng trong mạng tin cậy
    print(f"Home: http://127.0.0.1:{PORT}")
    if lan:
        import socket
        try:
            s_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s_.connect(("10.255.255.255", 1)); ip = s_.getsockname()[0]; s_.close()
        except OSError:
            ip = "<IP may nay>"
        print(f"May khac cung mang: http://{ip}:{PORT}  (ai trong mang cung mo va sua duoc: dong cua so nay khi xong)")
    ThreadingHTTPServer(("0.0.0.0" if lan else "127.0.0.1", PORT), H).serve_forever()
