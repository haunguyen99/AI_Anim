"""Spine Live: xem anim Spine 2D trong trình duyệt bằng spine-player 4.2, tự nạp lại khi file đổi.

Trang: /spine  (tools/spine_live/index.html)
API:
  GET /api/spine/list               các skeleton JSON trong work/<game>/spine/<anim>/ (và export/)
  GET /api/spine/stat?json=<rel>    dấu thời gian mới nhất của JSON + atlas + ảnh (trang hỏi mỗi 0.5 s)
  GET /api/spine/focus?seq=&follow=  "Claude đang xem gì" (tools/spine_live_cmd.py ghi work/store/_sys/spine_live/focus.json);
                                    trang hỏi mỗi 0.5 s, ở chế độ Theo Claude thì nhảy theo; server nhớ trang nào đang mở
  GET /api/spine/clients            các trang Spine Live đang mở (hỏi trong 3 s gần nhất)
  GET /spine-live/f/[v<số>/]<rel>   file JSON / atlas / PNG (không cache; v<số> chỉ để đổi URL mỗi lần nạp lại)
  GET /spine-live/f/<dir>/images/_auto.atlas   atlas tự sinh khi skeleton chỉ có ảnh rời (images/):
                                    mỗi PNG là một trang atlas, vùng = cả ảnh, tên vùng = đường dẫn bỏ đuôi
Sửa trực tiếp (chế độ Sửa trên trang):
  POST /api/spine/key   {json, anim, frame, bones:{tên:{rotate, x, y}} (giá trị local tuyệt đối), note?, curve?}
                        ghi key vào anim tại frame (tạo anim nếu chưa có), backup trước khi ghi, lưu một ghi chú
  POST /api/spine/note  {json, anim, frame, note, bones?}   chỉ ghi chú cho Claude, không sửa file
  POST /api/spine/undo  {json}   trả JSON về bản backup mới nhất (hoàn tác lần key cuối)
  GET  /api/spine/notes?json=&all=1   ghi chú (mặc định: chưa xử lý)
Ghi chú ở work/store/_sys/spine_live/notes.json; Claude đọc bằng tools/spine_live_cmd.py notes / note-done.
"""
import glob, json, os, shutil, struct, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
WORK = os.path.join(ROOT, "work")
PAGE = os.path.join(ROOT, "tools", "spine_live")
FOCUS = os.path.join(WORK, "store", "_sys", "spine_live", "focus.json")
SYS = os.path.dirname(FOCUS)
NOTES = os.path.join(SYS, "notes.json")
BACKUP = os.path.join(SYS, "backup")
KEEP_BACKUP = 40   # mỗi file JSON giữ chừng này bản backup
CLIENTS = {}   # id trang -> {t, follow, seq, json}
CT = {".json": "application/json; charset=utf-8", ".atlas": "text/plain; charset=utf-8", ".txt": "text/plain; charset=utf-8",
      ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".js": "text/javascript; charset=utf-8",
      ".css": "text/css; charset=utf-8"}


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def safe(r):
    """Đường dẫn tuyệt đối trong work/<game>/spine/, hoặc None."""
    full = os.path.abspath(os.path.join(ROOT, r.lstrip("/")))
    parts = os.path.relpath(full, WORK).replace("\\", "/").split("/")
    return full if full.startswith(WORK + os.sep) and len(parts) > 2 and parts[1] == "spine" else None


def is_skeleton(p):
    try:
        with open(p, encoding="utf8") as f:
            head = f.read(400)
        return '"skeleton"' in head and '"spine"' in head
    except OSError:
        return False


def atlas_for(js):
    """Atlas đi kèm skeleton: <tên>.atlas(.txt) cạnh JSON, nếu không có thì atlas tự sinh từ thư mục ảnh."""
    d, base = os.path.dirname(js), os.path.splitext(os.path.basename(js))[0]
    for ext in (".atlas.txt", ".atlas"):
        p = os.path.join(d, base + ext)
        if os.path.isfile(p):
            return p
    found = glob.glob(os.path.join(d, "*.atlas.txt")) + glob.glob(os.path.join(d, "*.atlas"))
    if found:
        return found[0]
    img = images_dir(js)
    return os.path.join(img, "_auto.atlas") if img else None


def images_dir(js):
    d = os.path.dirname(js)
    try:
        sk = json.load(open(js, encoding="utf8")).get("skeleton", {})
    except Exception:
        sk = {}
    for cand in (sk.get("images"), "images", "../images"):
        if cand:
            p = os.path.abspath(os.path.join(d, cand))
            if os.path.isdir(p) and p.startswith(WORK + os.sep):
                return p
    return None


def skeletons():
    out = []
    for anim in sorted(glob.glob(os.path.join(WORK, "*", "spine", "*"))):
        if not os.path.isdir(anim):
            continue
        game = os.path.basename(os.path.dirname(os.path.dirname(anim)))
        name = os.path.basename(anim)
        files = (sorted(glob.glob(os.path.join(anim, "*.json"))) + sorted(glob.glob(os.path.join(anim, "_live", "*.json")))
                 + sorted(glob.glob(os.path.join(anim, "export", "*.json"))))
        uis = ui_layouts(anim)
        for js in files:
            if not is_skeleton(js):
                continue
            at = atlas_for(js)
            if not at:
                continue
            tag = {"export": "export", "_live": "live"}.get(os.path.basename(os.path.dirname(js)), "build")
            out.append({"game": game, "anim": name, "kind": tag, "json": rel(js), "atlas": rel(at), "ui": uis,
                        "label": f"{game} / {name} / {os.path.basename(js)}" + {"export": " (export)", "live": " (Claude thử)"}.get(tag, "")})
    return out


def ui_layouts(anim_dir):
    """Nền UI game để ghép: <anim>/ui/<tên>.json {name, image, at:[x,y] px ảnh (y xuống) = gốc skeleton, scale: px ảnh / đơn vị Spine}."""
    out = []
    for p in sorted(glob.glob(os.path.join(anim_dir, "ui", "*.json"))):
        try:
            u = json.load(open(p, encoding="utf8"))
            img = os.path.join(os.path.dirname(p), u["image"])
            w, h = png_size(img)
            out.append({"name": u.get("name") or os.path.splitext(os.path.basename(p))[0], "image": rel(img),
                        "at": u["at"], "scale": float(u.get("scale", 1)), "w": w, "h": h})
        except (OSError, ValueError, KeyError):
            pass
    return out


def png_size(p):
    with open(p, "rb") as f:
        h = f.read(24)
    return struct.unpack(">II", h[16:24]) if h[:8] == b"\x89PNG\r\n\x1a\n" else (0, 0)


def auto_atlas(img_dir):
    pages = []
    for p in sorted(glob.glob(os.path.join(img_dir, "**", "*.png"), recursive=True)):
        w, h = png_size(p)
        if not w:
            continue
        r = os.path.relpath(p, img_dir).replace("\\", "/")
        pages.append(f"{r}\nsize:{w},{h}\nfilter:Linear,Linear\n{os.path.splitext(r)[0]}\nbounds:0,0,{w},{h}\n")
    return "\n".join(pages)


def stamp(js_rel):
    js = safe(js_rel)
    if not js or not os.path.isfile(js):
        return None
    paths = [js]
    at = atlas_for(js)
    if at:
        if os.path.basename(at) == "_auto.atlas":
            paths += glob.glob(os.path.join(os.path.dirname(at), "**", "*.png"), recursive=True)
        else:
            paths.append(at)
            paths += glob.glob(os.path.join(os.path.dirname(at), "*.png"))
    t = 0
    for p in paths:
        try:
            t = max(t, os.stat(p).st_mtime_ns)
        except OSError:
            pass
    return t


# ---------------- sửa trực tiếp: key pose, ghi chú, hoàn tác ----------------
def _load_notes():
    try:
        return json.load(open(NOTES, encoding="utf8"))
    except (OSError, ValueError):
        return []


def _save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def add_note(b, keyed=False):
    notes = _load_notes()
    n = {"id": "n%d" % (time.time() * 1000), "t": time.strftime("%Y-%m-%d %H:%M:%S"), "json": b.get("json", ""),
         "anim": b.get("anim", ""), "frame": b.get("frame"), "note": (b.get("note") or "").strip(),
         "bones": b.get("pose") or b.get("bones") or {}, "keyed": keyed, "request": b.get("request") or "",
         "status": "open"}
    notes.append(n)
    _save_json(NOTES, notes)
    return n["id"]


def _backup_name(js_rel):
    return js_rel.replace("/", "__")


def backup(js):
    os.makedirs(BACKUP, exist_ok=True)
    base = _backup_name(rel(js))
    shutil.copy2(js, os.path.join(BACKUP, f"{base}__{time.time_ns()}.json"))
    olds = sorted(glob.glob(os.path.join(BACKUP, glob.escape(base) + "__*.json")))
    for p in olds[:-KEEP_BACKUP]:
        os.remove(p)


def _ease(t1, v1, t2, v2):
    d = t2 - t1
    return [round(t1 + d / 3, 4), round(v1, 4), round(t1 + 2 * d / 3, 4), round(v2, 4)]


def _set_key(keys, t, vals, fields, kind):
    """chèn / thay key ở thời điểm t; curve của key trước và key này đặt lại theo kind (ease / linear / stepped)."""
    tm = lambda k: k.get("time", 0)
    i = next((j for j, k in enumerate(keys) if abs(tm(k) - t) < 1e-4), None)
    if i is None:
        i = sum(1 for k in keys if tm(k) < t)
        keys.insert(i, {"time": round(t, 4)})
    keys[i].update({f: round(v, 4) for f, v in zip(fields, vals)})
    for j in (i - 1, i):
        if j < 0 or j + 1 >= len(keys):
            if 0 <= j < len(keys) and j + 1 >= len(keys):
                keys[j].pop("curve", None)
            continue
        a, b = keys[j], keys[j + 1]
        if kind == "stepped":
            a["curve"] = "stepped"
        elif kind == "linear":
            a.pop("curve", None)
        else:
            a["curve"] = sum((_ease(tm(a), a.get(f, 0), tm(b), b.get(f, 0)) for f in fields), [])


def key_pose(b):
    js = safe(b.get("json", ""))
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file " + str(b.get("json")))
    anim, frame, bones = (b.get("anim") or "").strip(), b.get("frame"), b.get("bones") or {}
    if not anim or frame is None or not bones:
        raise ValueError("thiếu anim / frame / xương")
    data = json.load(open(js, encoding="utf8"))
    fps = (data.get("skeleton") or {}).get("fps") or 30
    t = float(frame) / fps
    setup = {x["name"]: x for x in data.get("bones", [])}
    an = data.setdefault("animations", {}).setdefault(anim, {})
    bt = an.setdefault("bones", {})
    kind = b.get("curve") or "ease"
    n = 0
    for name, v in bones.items():
        if name not in setup:
            continue
        s = setup[name]
        tl = bt.get(name, {})
        if "rotate" in v:
            r = float(v["rotate"]) - s.get("rotation", 0)
            r = (r + 180) % 360 - 180
            ks = tl.get("rotate")
            if ks:   # chọn góc tương đương gần key trước nhất, tránh xoay vòng 360
                prev = [k for k in ks if k.get("time", 0) <= t + 1e-4] or ks
                p = prev[-1].get("value", 0)
                r += 360 * round((p - r) / 360)
            if ks or abs(r) > 1e-3:
                _set_key(tl.setdefault("rotate", []), t, [r], ["value"], kind)
                n += 1
        if "x" in v or "y" in v:
            dx = float(v.get("x", s.get("x", 0))) - s.get("x", 0)
            dy = float(v.get("y", s.get("y", 0))) - s.get("y", 0)
            if tl.get("translate") or abs(dx) > 1e-3 or abs(dy) > 1e-3:
                _set_key(tl.setdefault("translate", []), t, [dx, dy], ["x", "y"], kind)
                n += 1
        if tl:
            bt[name] = tl
    if not n:
        raise ValueError("pose trùng setup, không có gì để key")
    backup(js)
    _save_json(js, data)
    if (b.get("note") or "").strip() or b.get("request"):   # key không ghi chú: chỉ sửa file, không tạo ghi chú
        add_note(b, keyed=True)
    return {"keys": n, "anim": anim, "frame": frame}


def undo(b):
    js = safe(b.get("json", ""))
    if not js:
        raise ValueError("không thấy file")
    olds = sorted(glob.glob(os.path.join(BACKUP, glob.escape(_backup_name(rel(js))) + "__*.json")))
    if not olds:
        raise ValueError("không còn bản backup để hoàn tác")
    shutil.copy2(olds[-1], js)
    os.utime(js)   # đổi mtime để trang nạp lại
    os.remove(olds[-1])
    return {"left": len(olds) - 1}


def handle_post(h, path, body):
    fn = {"/api/spine/key": key_pose, "/api/spine/note": lambda b: {"id": add_note(b)}, "/api/spine/undo": undo}.get(path)
    if not fn:
        return False
    try:
        h.send_json(dict(fn(body), ok=True))
    except ValueError as e:
        h.send_json({"ok": False, "error": str(e)}, 400)
    except Exception as e:
        h.send_json({"ok": False, "error": f"{type(e).__name__}: {e}"}, 500)
    return True


def handle_get(h, path, qs):
    """True nếu đã trả lời. h: handler của server.py (send_json, send_bytes)."""
    if path in ("/spine", "/spine/"):
        h.send_bytes(open(os.path.join(PAGE, "index.html"), "rb").read(), "text/html; charset=utf-8", True)
        return True
    if path.startswith("/spine/vendor/"):
        full = os.path.abspath(os.path.join(PAGE, path[len("/spine/"):]))
        ext = os.path.splitext(full)[1].lower()
        if full.startswith(PAGE + os.sep) and os.path.isfile(full) and ext in CT:
            h.send_bytes(open(full, "rb").read(), CT[ext])
            return True
        h.send_error(404)
        return True
    if path == "/api/spine/list":
        h.send_json(skeletons())
        return True
    if path == "/api/spine/focus":
        q = lambda k: (qs.get(k) or [""])[0]
        if q("id"):
            CLIENTS[q("id")] = {"t": time.time(), "follow": q("follow") == "1", "seq": q("seq"), "json": q("json"), "anim": q("anim")}
        try:
            f = json.load(open(FOCUS, encoding="utf8"))
        except (OSError, ValueError):
            f = {"seq": 0}
        h.send_json(f)
        return True
    if path == "/api/spine/notes":
        js, everything = (qs.get("json") or [""])[0], (qs.get("all") or [""])[0] == "1"
        h.send_json([n for n in _load_notes() if (everything or n.get("status") == "open") and (not js or n.get("json") == js)])
        return True
    if path == "/api/spine/clients":
        now = time.time()
        h.send_json([dict(v, id=k, ago=round(now - v["t"], 1)) for k, v in CLIENTS.items() if now - v["t"] < 3])
        return True
    if path == "/api/spine/stat":
        t = stamp((qs.get("json") or [""])[0])
        h.send_json({"t": t} if t is not None else {"error": "không thấy file"}, 200 if t is not None else 404)
        return True
    if path.startswith("/spine-live/f/"):
        r = path[len("/spine-live/f/"):]
        if r.startswith("v") and "/" in r and r[1:r.index("/")].isdigit():   # /spine-live/f/v<số>/work/...: số đổi mỗi lần nạp lại
            r = r[r.index("/") + 1:]
        full = safe(r)
        if full and os.path.basename(full) == "_auto.atlas" and os.path.isdir(os.path.dirname(full)):
            h.send_bytes(auto_atlas(os.path.dirname(full)).encode("utf8"), CT[".atlas"], True)
            return True
        ext = os.path.splitext(full or "")[1].lower()
        if full and os.path.isfile(full) and ext in CT:
            h.send_bytes(open(full, "rb").read(), CT[ext], True)
            return True
        h.send_error(404)
        return True
    return False
