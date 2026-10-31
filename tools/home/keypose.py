"""Key Pose: duyệt ảnh key pose (Codex, giai đoạn 0) và gửi yêu cầu tạo thêm ảnh.

Trang: /keypose  (tools/keypose/index.html)
Ảnh:   work/<dự án>/<job>/keys/*.png, nhóm theo key: k2_fire.png, k2_fire_v2.png, k2_fire_m5.png, k2_fire_r1.png → nhóm k2_fire
       prompt của ảnh: keys/prompts/<tên ảnh>.txt (nếu có). Ref cho ảnh mới: keys/keypose.json {"refs": [...]} hoặc model_ref/.
API:
  GET /api/keypose/jobs           các job có thư mục keys/ + Claude có đang canh không
  GET /api/keypose/job?id=<p/job> nhóm key, ảnh (url, prompt, thời gian), ref
  GET /api/keypose/clip?id=<anim> key pose của một anim (Studio, panel Key Pose) + các key khác của job
  POST /api/keypose/assign        {clip, key, on} gắn / bỏ key vào anim (keys/keypose.json "clips")
  POST /api/keypose/views         {clip, use, main} các góc nhìn dùng cho nhân vật (keys/keypose.json "views")
  POST /api/keypose/phase         {clip, i, f?, key?} sửa frame / key của một pha (i = -1 thêm pha)
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
# góc nhìn (Image Key nhiều góc, user 2026-10-30 "lõi ... đầy đủ các góc cơ bản ... nhân vật nào cần những góc nào người dùng sẽ lựa chọn"):
# tên ảnh <key>[__<góc>][_vN|_mN|_rN]; không có __<góc> = góc chính của nhân vật (keys/keypose.json "views": {"main", "use"})
VIEWS = ["right", "left", "front", "back", "top", "q34"]
VIEW_RE = re.compile(r"__(" + "|".join(VIEWS) + r")$")
VIEW_EN = {"right": "from the character's right side (pure side view, facing screen right)", "left": "from the character's left side (pure side view, facing screen left)",
           "front": "from the front (camera in front of the character, looking at its face)", "back": "from behind (camera behind the character)",
           "top": "from directly above (top-down, camera looking straight down)", "q34": "from a 3/4 front view (camera 45 degrees between front and side, slightly above)"}
# mọi góc là camera TRỰC GIAO (orthographic) chiếu vuông góc, như cam front / side / top của Maya (user 2026-10-30)
ORTHO = (" ORTHOGRAPHIC projection like a Maya orthographic camera: no perspective, no foreshortening, no vanishing point;"
         " parallel projection, camera axis exactly perpendicular to the view plane.")
CAMERA = {"right": "orthographic pure SIDE view, the character faces SCREEN RIGHT. Full body, feet visible." + ORTHO,
          "left": "orthographic pure SIDE view, the character faces SCREEN LEFT. Full body, feet visible." + ORTHO,
          "front": "orthographic FRONT view, the character faces the camera. Full body, feet visible." + ORTHO,
          "back": "orthographic BACK view, camera behind the character. Full body, feet visible." + ORTHO,
          "top": "orthographic TOP view, camera straight above looking down. Whole character and prop visible." + ORTHO,
          "q34": "orthographic 3/4 view, camera rotated 45 degrees between front and the character's right side, slightly above. Full body, feet visible." + ORTHO}
# ảnh khung camera: chỉ ảnh render trực giao (tools/render_fbx_tex.py → model_ref/char_<góc>, hoặc keys/camref_<góc>), không dùng ảnh phối cảnh
CAMREF = {"right": ["char_side_r"], "left": ["char_side_l"], "front": ["char_front"], "back": ["char_back"], "top": ["char_top"], "q34": ["char_q34"]}
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


def parse(stem):
    """tên ảnh → (key, góc | None = góc chính)"""
    b = VARIANT.sub("", stem)
    m = VIEW_RE.search(b)
    return (b[:m.start()], m.group(1)) if m else (b, None)


def key_of(stem):
    return parse(stem)[0]


def views_cfg(jd):
    v = _cfg(jd).get("views") or {}
    main = v.get("main") if v.get("main") in VIEWS else "right"
    use = [x for x in VIEWS if x in (v.get("use") or [main])] or [main]
    if main not in use:
        use = [main] + use
    return {"main": main, "use": use, "all": VIEWS}


def camref(jd, view):
    for d in (os.path.join(jd, "keys"), os.path.join(jd, "model_ref")):
        for n in ["camref_" + view] + CAMREF.get(view, []):
            for ext in IMG:
                f = os.path.join(d, n + ext)
                if os.path.isfile(f):
                    return f
    return None


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
            if r:   # keypose.json chỉ có "clips" (gắn key vào anim) thì vẫn lấy ref từ model_ref/
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
        kk, vv = parse(stem)
        groups.setdefault(kk, []).append({
            "name": stem, "view": vv, "url": "/" + rel(p) + "?t=%d" % os.path.getmtime(p), "mtime": os.path.getmtime(p),
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
        if path == "/api/keypose/clip":
            h.send_json(clip((qs.get("id") or [""])[0]))
            return True
    except ValueError as e:
        h.send_json({"error": str(e)}, 400)
        return True
    return False


# ---- theo anim (Studio, panel Key Pose): mỗi anim (id trong work/clips.json) có danh sách key pose riêng
#   job của anim: job nào có keys/keypose.json "clips" nhắc tới anim → "dir" của anim trong clips.json → job có tên là
#   tiền tố của id anim (sdr03_shoot → work/*/sdr03). Key của anim: keypose.json "clips": {"<anim>": ["k1_ready", ...]};
#   chưa ghi thì đoán theo tên: phần sau tiền tố (shoot) là một chữ trong tên key (k2_shoot_f05).
REG = os.path.join(WORK, "clips.json")


def _cfg(jd):
    f = os.path.join(jd, "keys", "keypose.json")
    try:
        return json.load(open(f, encoding="utf8")) if os.path.isfile(f) else {}
    except ValueError:
        return {}


def _job_dirs():
    return [os.path.dirname(k) for k in sorted(glob.glob(os.path.join(WORK, "*", "*", "keys")))
            if os.path.basename(os.path.dirname(os.path.dirname(k))) not in ("store", "_trash")]


def clip_job(cid):
    jds = _job_dirs()
    for jd in jds:
        if cid in (_cfg(jd).get("clips") or {}):
            return jd
    try:
        c = next((c for c in json.load(open(REG, encoding="utf8")).get("clips", []) if c.get("id") == cid), None)
    except (OSError, ValueError):
        c = None
    if c and c.get("dir"):
        d = os.path.join(ROOT, c["dir"])
        if os.path.isdir(os.path.join(d, "keys")):
            return d
    best = None
    for jd in jds:
        b = os.path.basename(jd).lower()
        if cid.lower().startswith(b + "_") and (not best or len(b) > len(os.path.basename(best))):
            best = jd
    return best


def _entry(cfg, cid):
    """Mục của anim trong keypose.json "clips": danh sách key (cũ) hoặc {frames, fps, phases[], keys[]} (có pha)."""
    e = (cfg.get("clips") or {}).get(cid)
    if isinstance(e, list):
        return {"keys": list(e)}
    return e if isinstance(e, dict) else None


def clip(cid):
    """Key pose của một anim. Có pha (bảng pha của bản phân tích, cột Key pose): phases = [{f, name, desc, key|None}]
    theo frame; key None = pha chuyển tiếp (breakdown), không có ảnh riêng. Trình chạy ảnh trong Studio giữ ảnh của
    pha có key từ frame của nó tới pha có key kế tiếp (bậc thang, như blocking)."""
    if not re.match(r"^[A-Za-z0-9_\-]+$", cid or ""):
        raise ValueError("anim không hợp lệ: " + str(cid))
    jd = clip_job(cid)
    if not jd:
        return {"clip": cid, "job": None, "keys": [], "other": [], "phases": [], "watching": watching()}
    jid = rel(jd)[len("work/"):]
    d = job(jid)
    e = _entry(_cfg(jd), cid)
    phases = []
    if e is not None:
        phases = sorted((dict(p, i=n) for n, p in enumerate(e.get("phases") or [])),
                        key=lambda p: (p.get("f") is None, p.get("f") or 0, p["i"]))
        want, guessed = [p["key"] for p in phases if p.get("key")] + list(e.get("keys") or []), False
    else:
        word = cid[len(os.path.basename(jd)) + 1:].lower() if cid.lower().startswith(os.path.basename(jd).lower() + "_") else cid.lower()
        want, guessed = [k["key"] for k in d["keys"] if word and word in k["key"].lower().split("_")], True
    mine = [k for k in d["keys"] if k["key"] in want]
    other = [{"key": k["key"], "count": len(k["images"]), "url": k["images"][-1]["url"]} for k in d["keys"] if k["key"] not in want]
    return {"clip": cid, "job": jid, "keys": mine, "other": other, "guessed": guessed, "refs": d["refs"], "watching": d["watching"],
            "phases": phases, "frames": (e or {}).get("frames"), "fps": (e or {}).get("fps"),
            "views": dict(views_cfg(jd), camref={v: "/" + rel(camref(jd, v)) for v in VIEWS if camref(jd, v)}),
            "extra": [k for k in (e or {}).get("keys") or [] if k not in [p.get("key") for p in phases]]}


def _save(jd, cfg):
    with open(os.path.join(jd, "keys", "keypose.json"), "w", encoding="utf8", newline="\n") as fh:
        json.dump(cfg, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def _edit(cid):
    jd = clip_job(cid)
    if not jd:
        raise ValueError("anim %s chưa có thư mục keys/" % cid)
    cfg = _cfg(jd)
    e = _entry(cfg, cid)
    if e is None:
        e = {"keys": [k["key"] for k in clip(cid)["keys"]]}   # lần đầu ghi: giữ các key đang đoán được
    cfg.setdefault("clips", {})[cid] = e
    return jd, cfg, e


def assign(b):
    """POST /api/keypose/assign {clip, key, on}: gắn / bỏ một key vào anim. Có pha: bỏ = pha đó thành chuyển tiếp (key None)."""
    cid, key, on = b.get("clip") or "", b.get("key") or "", bool(b.get("on", True))
    jd, cfg, e = _edit(cid)
    L = [k for k in e.get("keys") or [] if k != key]
    if on and key not in [p.get("key") for p in e.get("phases") or []]:
        L.append(key)
    if not on:
        for p in e.get("phases") or []:
            if p.get("key") == key:
                p["key"] = None
    e["keys"] = sorted(L, key=nat)
    _save(jd, cfg)
    return cid


def phase_set(b):
    """POST /api/keypose/phase {clip, i, f?, key?, name?}: sửa pha i (frame / key / tên). i = -1: thêm pha mới."""
    cid = b.get("clip") or ""
    jd, cfg, e = _edit(cid)
    P = e.setdefault("phases", [])
    i = int(b.get("i", -1))
    if i < 0:
        P.append({"f": None, "name": b.get("name") or b.get("key") or "", "desc": "", "key": b.get("key") or None})
        i = len(P) - 1
        e["keys"] = [k for k in e.get("keys") or [] if k != P[i]["key"]]
    p = P[i]
    if "f" in b:
        p["f"] = int(b["f"]) if b["f"] not in (None, "") else None
    if "key" in b:
        p["key"] = b["key"] or None
    if "name" in b and b["name"]:
        p["name"] = b["name"]
    _save(jd, cfg)
    return cid


def views_set(b):
    """POST /api/keypose/views {clip, use: [...], main}: chọn các góc dùng cho nhân vật (cả job, mọi anim của nhân vật)."""
    cid = b.get("clip") or ""
    jd = clip_job(cid)
    if not jd:
        raise ValueError("anim %s chưa có thư mục keys/" % cid)
    cfg = _cfg(jd)
    cur = views_cfg(jd)
    main = b.get("main") if b.get("main") in VIEWS else cur["main"]
    use = [x for x in VIEWS if x in (b.get("use") or cur["use"])]
    cfg["views"] = {"main": main, "use": use if main in use else [main] + use}
    _save(jd, cfg)
    return cid
