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
  POST /api/spine/key   {json, anim, frame, bones:{tên:{rotate, x, y, sx?, sy?}} (giá trị local tuyệt đối), note?, curve?}
                        ghi key vào anim tại frame (tạo anim nếu chưa có), backup trước khi ghi, lưu một ghi chú
  POST /api/spine/note  {json, anim, frame, note, bones?}   chỉ ghi chú cho Claude, không sửa file
  POST /api/spine/undo  {json}   lùi đúng một lần ghi file (bản hiện tại cất sang ngăn Làm lại)
  POST /api/spine/redo  {json}   làm lại lần vừa hoàn tác
  POST /api/spine/anim  {json, op: create | delete | meta, name, frames?, loop?, desc?}   mục Anim: tạo anim mới (dài N
       frame), xoá anim, lưu mô tả anim cho Claude gen (work/store/_sys/spine_live/anims.json)
  GET  /api/spine/anims?json=    mô tả các anim của file: {anim: {desc, loop, frames, t}}
  POST /api/spine/timelines {json, anim, items: [{bone, channel, keys}], what}   ghi nhiều kênh một lần (tool Physics)
  POST /api/spine/reduce {json, anim, bones?, tol?}   Graph > Giảm key: dựng lại ít key nhất, giữ chuyển động (chỉ anim này)
  GET  /api/spine/versions?json=  phiên bản của file (cột trái Spine Live): [{id, t, who, what, from, thumb}], head = bản đang là file
       (server tự chụp mỗi khi file đổi: trang hỏi /stat mỗi 0.5 s -> ensure_version so mtime / hash)
  POST /api/spine/version/restore {json, id}   tiếp từ bản id: file = nội dung bản đó, thành bản MỚI NHẤT (không xoá bản giữa)
  POST /api/spine/version/publish {json, what?}   nút Update: đưa bản hiện tại (sửa tay) vào Phiên bản. Từ 2026-11-04 phiên bản
       chỉ tự chụp khi AI ghi file / file đổi ngoài Spine Live; sửa tay chỉ vào lịch sử (tab History)
  POST /api/spine/history/goto {json, undo: n | redo: n}   tab History: nhảy tới một bước (undo / redo n lần)
  GET  /api/spine/rigbase?json=   tư thế setup xương của "rig gốc" (nút Về rig gốc): bản gần nhất Claude dựng rig (nhãn
       "Claude dựng rig ..."), không có thì bản cũ nhất còn lưu -> {id, t, what, bones: {tên: {rotation, x, y, scaleX, scaleY}}}
  GET  /api/spine/version/thumb?json=&id=      ảnh nhỏ của bản;  POST /api/spine/version/thumb {json, id, data: dataURL jpeg}
  GET  /api/spine/history?json=  {undo: [{what, who, t}...] (mới nhất trước), redo: [...]}
  Mọi lần ghi (người dùng key / sửa curve / lưới / setup / weight; Claude gen qua backup(..., who="claude"))
  đều cất bản trước đó + nhãn vào backup/<file>.log.json; ghi mới thì xoá ngăn Làm lại.
  GET  /api/spine/keyed?json=      frame đã Key pose trên Spine Live theo anim (timeline tô nổi, Gen từ nhiều keypose)
  POST /api/spine/keyed/clear {json, anim?, frames?}   xoá đánh dấu keypose (không sửa file anim)
  POST /api/spine/keyed/delete {json, anim, frame}     xoá keypose: xoá key thật của các xương đã key ở frame đó (Hoàn tác được)
  Keypose đã dùng để gen: spine_live_cmd.py note-done đặt used=true (trang ẩn đi); Hoàn tác bản gen đó thì hiện lại.
  GET  /api/spine/notes?json=&all=1   ghi chú (mặc định: chưa xử lý)
Ghi chú ở work/store/_sys/spine_live/notes.json; Claude đọc bằng tools/spine_live_cmd.py notes / note-done.
"""
import base64, glob, hashlib, json, math, os, re, shutil, struct, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
WORK = os.path.join(ROOT, "work")
PAGE = os.path.join(ROOT, "tools", "spine_live")
FOCUS = os.path.join(WORK, "store", "_sys", "spine_live", "focus.json")
SYS = os.path.dirname(FOCUS)
NOTES = os.path.join(SYS, "notes.json")
BACKUP = os.path.join(SYS, "backup")
KEYED = os.path.join(SYS, "keyed.json")   # frame người dùng đã Key pose: {json: {anim: [{frame, bones, t, bk}]}}
REDO = os.path.join(SYS, "redo")
VERS = os.path.join(SYS, "versions")      # phiên bản: versions/<file>/vNNNN.json + index.json (+ vNNNN.jpg ảnh nhỏ)
KEEP_VERS = 300
GEN_MERGE_S = 600                          # không có nhóm gen: các lần Claude ghi cách nhau < 10 phút (không ai xen) = 1 phiên bản
_VMT = {}                                 # json rel -> mtime đã xét
_HEAD = {}                                 # json rel -> bản vừa bấm về ở cột Phiên bản
PENDING = {}                              # json rel -> nhãn cho phiên bản kế tiếp (undo / redo / tiếp từ bản cũ)
ANIMS = os.path.join(SYS, "anims.json")   # mô tả anim: {json: {anim: {desc, loop, frames, t}}}
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
         "frames": b.get("frames") or [], "keyposes": b.get("keyposes") or [],   # gen nhiều keypose: tích chọn / mọi frame đã sửa
         "desc": (b.get("desc") or "").strip(),   # mô tả anim (mục Anim) gửi kèm yêu cầu gen
         "status": "open"}
    if b.get("sketch"):   # góp ý vẽ trên khung xem (sketch.js): nét theo toạ độ skeleton + xương gần nhất
        n["sketch"] = b["sketch"]
    img = b.get("image") or ""
    if img.startswith("data:image/jpeg;base64,"):   # ảnh khung xem kèm nét vẽ
        d = os.path.join(SYS, "notes")
        os.makedirs(d, exist_ok=True)
        f = os.path.join(d, n["id"] + ".jpg")
        with open(f, "wb") as fh:
            fh.write(base64.b64decode(img.split(",", 1)[1]))
        n["image"] = os.path.relpath(f, ROOT).replace("\\", "/")
    notes.append(n)
    _save_json(NOTES, notes)
    return n["id"]


def _backup_name(js_rel):
    return js_rel.replace("/", "__")


def _log_path(d, base):
    return os.path.join(d, base + ".log.json")


def _load_log(d, base):
    try:
        return json.load(open(_log_path(d, base), encoding="utf8"))
    except (OSError, ValueError):
        return []


def _snaps(d, base):
    return sorted(glob.glob(os.path.join(d, glob.escape(base) + "__*.json")))


def _push(d, js, meta):
    """cất bản hiện tại của js vào ngăn d (backup / redo) kèm nhãn; trả tên file."""
    os.makedirs(d, exist_ok=True)
    base = _backup_name(rel(js))
    name = f"{base}__{time.time_ns()}.json"
    shutil.copy2(js, os.path.join(d, name))
    log = [e for e in _load_log(d, base) if os.path.isfile(os.path.join(d, e["name"]))]
    log.append(dict(meta, name=name, t=meta.get("t") or time.strftime("%Y-%m-%d %H:%M:%S")))
    olds = _snaps(d, base)
    for p in olds[:-KEEP_BACKUP]:
        os.remove(p)
    keep = {os.path.basename(p) for p in olds[-KEEP_BACKUP:]}
    _save_json(_log_path(d, base), [e for e in log if e["name"] in keep])
    return name


def _pop(d, base):
    """lấy bản mới nhất của ngăn d: (đường dẫn, nhãn) hoặc (None, None)."""
    olds = _snaps(d, base)
    if not olds:
        return None, None
    name = os.path.basename(olds[-1])
    log = _load_log(d, base)
    meta = next((e for e in log if e["name"] == name), {"name": name, "what": "lần ghi file", "who": "?"})
    _save_json(_log_path(d, base), [e for e in log if e["name"] != name])
    return olds[-1], meta


def _clear_redo(base):
    for p in _snaps(REDO, base):
        os.remove(p)
    if os.path.isfile(_log_path(REDO, base)):
        os.remove(_log_path(REDO, base))


def backup(js, who="user", what="", keyed=None, extra=None):
    """gọi NGAY TRƯỚC khi ghi js: cất bản hiện tại để Hoàn tác lùi đúng lần ghi này. who: user / claude."""
    name = _push(BACKUP, js, dict({"who": who, "what": what or "sửa file", "keyed": keyed}, **(extra or {})))
    _clear_redo(_backup_name(rel(js)))
    return name


def history(js_rel):
    base = _backup_name(js_rel)
    pick = lambda d: [{k: e.get(k) for k in ("what", "who", "t")} for e in reversed(_load_log(d, base))
                      if os.path.isfile(os.path.join(d, e["name"]))]
    return {"undo": pick(BACKUP), "redo": pick(REDO)}


def _load_keyed():
    try:
        return json.load(open(KEYED, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def mark_keyed(js_rel, anim, frame, bones, bk):
    """ghi frame vừa Key pose (gộp xương nếu frame đã có); bk = bản backup tạo ra lần key này (để Hoàn tác gỡ đúng lần)."""
    d = _load_keyed()
    lst = d.setdefault(js_rel, {}).setdefault(anim, [])
    e = next((x for x in lst if x["frame"] == frame), None)
    if not e:
        e = {"frame": frame, "bones": [], "bk": []}
        lst.append(e)
    e["bones"] = sorted(set(e["bones"]) | set(bones))
    e["bk"].append(bk)
    e["t"] = time.strftime("%Y-%m-%d %H:%M:%S")
    lst.sort(key=lambda x: x["frame"])
    _save_json(KEYED, d)


def unmark_backup(js_rel, bk):
    d = _load_keyed()
    for anim, lst in (d.get(js_rel) or {}).items():
        for e in lst:
            if bk in e.get("bk", []):
                e["bk"].remove(bk)
        d[js_rel][anim] = [e for e in lst if e.get("bk")]
    _save_json(KEYED, d)


def set_used(js_rel, items, used):
    """items: [{anim, frame}] -> đặt cờ used của keypose (đã dùng để gen: trang ẩn; Hoàn tác bản gen: hiện lại)."""
    d = _load_keyed()
    for it in items or []:
        for e in (d.get(js_rel) or {}).get(it["anim"], []):
            if e["frame"] == it["frame"]:
                e["used"] = used
    _save_json(KEYED, d)


def _readd_keyed(js_rel, entry):
    d = _load_keyed()
    lst = d.setdefault(js_rel, {}).setdefault(entry["anim"], [])
    if not any(e["frame"] == entry["frame"] for e in lst):
        lst.append({k: v for k, v in entry.items() if k != "anim"})
        lst.sort(key=lambda x: x["frame"])
    _save_json(KEYED, d)


def _drop_keyed(js_rel, anim, frame):
    d = _load_keyed()
    if anim in (d.get(js_rel) or {}):
        d[js_rel][anim] = [e for e in d[js_rel][anim] if e["frame"] != frame]
    _save_json(KEYED, d)


def delete_keypose(b):
    """xoá keypose ở frame: xoá key (mọi kênh) của các xương đã key ở frame đó trong anim; Hoàn tác được."""
    js = safe(b.get("json", ""))
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file")
    anim, frame = b.get("anim"), int(b.get("frame"))
    ent = next((e for e in (_load_keyed().get(rel(js)) or {}).get(anim, []) if e["frame"] == frame), None)
    data = json.load(open(js, encoding="utf8"))
    fps = (data.get("skeleton") or {}).get("fps") or 30
    bt = ((data.get("animations") or {}).get(anim) or {}).get("bones") or {}
    names = (ent or {}).get("bones") or b.get("bones") or []
    n = 0
    for bn in names:
        for ch in list((bt.get(bn) or {}).keys()):
            ks = bt[bn][ch]
            keep = []
            for k in ks:
                if abs(k.get("time", 0) * fps - frame) <= 0.5:
                    n += 1
                    if keep and isinstance(keep[-1].get("curve"), list):
                        keep[-1].pop("curve")          # đoạn nối key trước -> key sau: thẳng (bezier cũ thuộc đoạn đã mất)
                else:
                    keep.append(k)
            if keep:
                keep[-1].pop("curve", None)
                bt[bn][ch] = keep
            else:
                del bt[bn][ch]
        if bn in bt and not bt[bn]:
            del bt[bn]
    if not n and not ent:
        raise ValueError("không có key ở F%d" % frame)
    backup(js, "user", f"Xoá keypose {anim} F{frame}", extra={"keyed_del": dict(ent, anim=anim) if ent else None})
    _save_json(js, data)
    _drop_keyed(rel(js), anim, frame)
    return {"removed": n}


def clear_keyed(b):
    js_rel = b.get("json", "")
    d = _load_keyed()
    an, frames = b.get("anim"), b.get("frames")
    for anim in list((d.get(js_rel) or {})):
        if an and anim != an:
            continue
        d[js_rel][anim] = [e for e in d[js_rel][anim] if frames is not None and e["frame"] not in frames]
    _save_json(KEYED, d)
    return {}


def _ease(t1, v1, t2, v2):
    d = t2 - t1
    return [round(t1 + d / 3, 4), round(v1, 4), round(t1 + 2 * d / 3, 4), round(v2, 4)]


def _asset_root(js):
    """thư mục asset của một file skeleton: bỏ các thư mục phụ (export/, export_old/, _live/, _v1.../) ở cuối."""
    d = os.path.dirname(js.replace("\\", "/"))
    while os.path.basename(d) in ("export", "export_old") or os.path.basename(d).startswith("_"):
        d = os.path.dirname(d)
    return d


def anims_for(js):
    """sổ anim của file js; anim chưa có cờ loop thì lấy cờ cùng tên anim ở file khác cùng asset (bản xuất, bản sao,
    bản _final ...), file sửa gần nhất trước (2026-11-10, rà soát: cờ gắn theo đường dẫn file nên bản xuất mất cờ)."""
    meta = _load_anims()
    own = {k: dict(v) for k, v in (meta.get(js) or {}).items()}
    root = _asset_root(js)
    others = sorted(((k, v) for k, v in meta.items() if k != js and _asset_root(k) == root),
                    key=lambda kv: max([x.get("t", "") for x in kv[1].values()] or [""]), reverse=True)
    for k, v in others:
        for a, m in v.items():
            if "loop" in m and "loop" not in own.get(a, {}):
                own.setdefault(a, {})["loop"] = m["loop"]
                own[a]["from"] = k
    return own


def ktime(t, fps=30):
    """thời gian key an toàn (2026-11-10, rà soát Spine Live): key nằm đúng frame -> ghi SỚM hơn mốc frame 0.00001 s,
    không bao giờ muộn (round(2/30, 4) = 0.0667 > 0.066667 làm key stepped / đổi ảnh hiện trễ 1 frame khi lấy mẫu f/fps;
    float32 của 0.1 cũng > 0.1). Key không nằm đúng frame: làm tròn 5 chữ số."""
    t = float(t)
    if t <= 0:
        return 0.0
    f = t * fps; r = round(f)
    if abs(f - r) < 0.02:
        return math.floor(r / fps * 1e5 - 0.5) / 1e5
    return round(t, 5)


def _set_key(keys, t, vals, fields, kind):
    """chèn / thay key ở thời điểm t; curve của key trước và key này đặt lại theo kind (ease / linear / stepped)."""
    tm = lambda k: k.get("time", 0)
    i = next((j for j, k in enumerate(keys) if abs(tm(k) - t) < 1e-4), None)
    if i is None:
        i = sum(1 for k in keys if tm(k) < t)
        keys.insert(i, {"time": ktime(t)})
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
        if "sx" in v or "sy" in v:   # scale timeline = hệ số nhân với scale setup
            bsx, bsy = s.get("scaleX", 1) or 1, s.get("scaleY", 1) or 1
            kx = float(v.get("sx", bsx)) / bsx
            ky = float(v.get("sy", bsy)) / bsy
            if tl.get("scale") or abs(kx - 1) > 1e-4 or abs(ky - 1) > 1e-4:
                _set_key(tl.setdefault("scale", []), t, [kx, ky], ["x", "y"], kind)
                n += 1
        if "shx" in v or "shy" in v:   # shear timeline = độ cộng thêm vào shear setup (công cụ Z, 2026-11-05)
            dx = float(v.get("shx", s.get("shearX", 0))) - s.get("shearX", 0)
            dy = float(v.get("shy", s.get("shearY", 0))) - s.get("shearY", 0)
            if tl.get("shear") or abs(dx) > 1e-3 or abs(dy) > 1e-3:
                _set_key(tl.setdefault("shear", []), t, [dx, dy], ["x", "y"], kind)
                n += 1
        if tl:
            bt[name] = tl
    if not n:
        raise ValueError("pose trùng setup, không có gì để key")
    fr = int(round(float(frame)))
    bk = backup(js, "user", f"Key pose {anim} F{fr}", {"anim": anim, "frame": fr, "bones": list(bones)})
    _save_json(js, data)
    mark_keyed(rel(js), anim, fr, list(bones), bk)
    if (b.get("note") or "").strip() or b.get("request"):   # key không ghi chú: chỉ sửa file, không tạo ghi chú
        add_note(b, keyed=True)
    return {"keys": n, "anim": anim, "frame": frame}


def undo(b):
    js = safe(b.get("json", ""))
    if not js:
        raise ValueError("không thấy file")
    base = _backup_name(rel(js))
    src, meta = _pop(BACKUP, base)
    if not src:
        raise ValueError("không còn lần ghi nào để hoàn tác")
    _push(REDO, js, meta)                    # bản hiện tại -> ngăn Làm lại (kèm nhãn của lần ghi đang lùi)
    shutil.copy2(src, js)
    os.utime(js)   # đổi mtime để trang nạp lại
    os.remove(src)
    unmark_backup(rel(js), os.path.basename(src))
    if meta.get("consumed"):          # hoàn tác bản gen: keypose đã dùng hiện lại
        set_used(rel(js), meta["consumed"], False)
    if meta.get("keyed_del"):         # hoàn tác xoá keypose: đưa lại vào sổ
        _readd_keyed(rel(js), meta["keyed_del"])
    h = history(rel(js))
    return {"left": len(h["undo"]), "undone": meta.get("what"), "who": meta.get("who"), "history": h}


def redo(b):
    js = safe(b.get("json", ""))
    if not js:
        raise ValueError("không thấy file")
    base = _backup_name(rel(js))
    src, meta = _pop(REDO, base)
    if not src:
        raise ValueError("không còn gì để làm lại")
    meta = {k: v for k, v in meta.items() if k not in ("name", "t")}
    bk = _push(BACKUP, js, meta)              # không xoá ngăn Làm lại: còn làm lại tiếp được
    shutil.copy2(src, js)
    os.utime(js)
    os.remove(src)
    k = meta.get("keyed")
    if k:
        mark_keyed(rel(js), k["anim"], k["frame"], k["bones"], bk)
    if meta.get("consumed"):
        set_used(rel(js), meta["consumed"], True)
    if meta.get("keyed_del"):
        _drop_keyed(rel(js), meta["keyed_del"]["anim"], meta["keyed_del"]["frame"])
    return {"redone": meta.get("what"), "who": meta.get("who"), "history": history(rel(js))}


def _load_anims():
    try:
        return json.load(open(ANIMS, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def anim_op(b):
    import re
    js = safe(b.get("json", ""))
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file " + str(b.get("json")))
    op, name = b.get("op"), (b.get("name") or "").strip()
    if not name:
        raise ValueError("thiếu tên anim")
    meta = _load_anims()
    m = meta.setdefault(rel(js), {})
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    if op == "meta":
        m.setdefault(name, {}).update({k: b[k] for k in ("desc", "loop", "frames") if k in b}, t=now)
        _save_json(ANIMS, meta)
        return {}
    data = json.load(open(js, encoding="utf8"))
    an = data.setdefault("animations", {})
    fps = (data.get("skeleton") or {}).get("fps") or 30
    if op == "create":
        if not re.fullmatch(r"[A-Za-z0-9_\-]+", name):
            raise ValueError("tên anim chỉ gồm chữ không dấu, số, _ và -")
        if name in an:
            raise ValueError("đã có anim " + name)
        frames = max(1, int(b.get("frames") or 30))
        # anim trống dài đúng N frame: key dời 0 của root ở F0 và F N (root không ảnh hưởng hình), rồi pose trực tiếp
        an[name] = {"bones": {"root": {"translate": [{"x": 0, "y": 0}, {"time": ktime(frames / fps, fps), "x": 0, "y": 0}]}}}
        backup(js, "user", f"Tạo anim {name} ({frames}F)")
        _save_json(js, data)
        m[name] = {"desc": (b.get("desc") or "").strip(), "loop": bool(b.get("loop", True)), "frames": frames, "t": now}
        _save_json(ANIMS, meta)
    elif op == "delete":
        if name not in an:
            raise ValueError("không có anim " + name)
        if len(an) == 1:
            raise ValueError("không xoá anim cuối cùng của file")
        backup(js, "user", f"Xoá anim {name}")
        del an[name]
        _save_json(js, data)
        clear_keyed({"json": rel(js), "anim": name})
    else:
        raise ValueError("op không hợp lệ")
    return {"anims": list(an)}


# ---------------- phiên bản (cột trái Spine Live) ----------------
def _vdir(js_rel):
    return os.path.join(VERS, _backup_name(js_rel))


def _vindex(js_rel):
    try:
        return json.load(open(os.path.join(_vdir(js_rel), "index.json"), encoding="utf8"))
    except (OSError, ValueError):
        return []


def ensure_version(js_rel):
    """file đổi (mtime + hash khác bản cuối) -> chụp thành phiên bản mới, nhãn lấy từ PENDING hoặc lần ghi gần nhất trong lịch sử."""
    js = safe(js_rel)
    if not js or not os.path.isfile(js):
        return None
    mt = os.path.getmtime(js)
    if _VMT.get(js_rel) == mt:
        return None
    _VMT[js_rel] = mt
    data = open(js, "rb").read()
    hsh = hashlib.sha1(data).hexdigest()
    idx = _vindex(js_rel)
    if any(e["hash"] == hsh for e in idx):   # trùng một bản đã có (vd bấm về bản cũ ở cột Phiên bản): không tạo bản mới
        PENDING.pop(js_rel, None)
        return None
    meta = PENDING.pop(js_rel, None)
    log = _load_log(BACKUP, _backup_name(js_rel))
    if not meta:
        last = log[-1] if log else None
        if not idx:
            meta = {"who": "", "what": "bản đầu (lúc mở)"}
        elif last and last.get("t", "") >= idx[-1]["t"]:
            meta = {"who": last.get("who"), "what": last.get("what"), "group": last.get("group")}
        else:
            meta = {"who": "", "what": "file đổi (ngoài Spine Live)"}
    # 2026-11-04 (người dùng: "1 prompt chỉ gen ra 1 phiên bản"): các lần Claude ghi file trong cùng một lượt gen gộp vào
    # MỘT phiên bản (ghi đè bản cuối). Cùng lượt = cùng nhóm gen (spine_live_cmd.py gen-start), hoặc khi không có nhóm:
    # bản cuối cũng do Claude ghi, cách < GEN_MERGE_S và người dùng không thao tác gì xen giữa.
    prev = idx[-1] if idx else None
    if prev and meta.get("who") == "claude" and prev.get("who") == "claude" and not prev.get("pub"):
        g, pg = meta.get("group"), prev.get("group")
        user_between = any(e.get("who") == "user" and e.get("t", "") > prev["t"] for e in log)
        try:
            age = time.time() - time.mktime(time.strptime(prev["t"], "%Y-%m-%d %H:%M:%S"))
        except (ValueError, KeyError):
            age = 1e9
        if not user_between and ((g and g == pg) or (not g and not pg and age < GEN_MERGE_S)):
            d = _vdir(js_rel)
            with open(os.path.join(d, f"v{prev['id']:04d}.json"), "wb") as fh:
                fh.write(data)
            try:
                os.remove(os.path.join(d, f"v{prev['id']:04d}.jpg"))   # ảnh nhỏ chụp lại theo nội dung mới
            except OSError:
                pass
            prev.update({"t": time.strftime("%Y-%m-%d %H:%M:%S"), "hash": hsh, "what": meta.get("what") or prev.get("what", ""),
                         "merged": prev.get("merged", 1) + 1})
            _save_json(os.path.join(d, "index.json"), idx)
            return prev["id"]
    # 2026-11-04 (người dùng: "phần phiên bản chỉ để những bản AI gen ra, chứ không ghi cả vào đấy những chỉnh sửa người thủ
    # công sửa"): sửa tay (who = user: key, curve, lưới, weight, hoàn tác...) không tạo phiên bản; chúng nằm ở tab History.
    # Người dùng muốn đưa bản sửa tay vào Phiên bản thì bấm Update (POST /api/spine/version/publish -> force).
    if idx and meta.get("who") == "user" and not meta.get("force"):
        return None
    vid = (idx[-1]["id"] + 1) if idx else 1
    d = _vdir(js_rel)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"v{vid:04d}.json"), "wb") as fh:
        fh.write(data)
    idx.append({"id": vid, "t": time.strftime("%Y-%m-%d %H:%M:%S"), "who": meta.get("who") or "", "what": meta.get("what") or "",
                "from": meta.get("from"), "hash": hsh, "pub": bool(meta.get("force")), "group": meta.get("group")})
    for e in idx[:-KEEP_VERS]:
        for ext in (".json", ".jpg"):
            try:
                os.remove(os.path.join(d, f"v{e['id']:04d}{ext}"))
            except OSError:
                pass
    _save_json(os.path.join(d, "index.json"), idx[-KEEP_VERS:])
    return vid


def versions(js_rel):
    ensure_version(js_rel)
    # cột Phiên bản: bản AI gen / file đổi ngoài Spine Live / bản đầu / bản Update; ẩn bản sửa tay cũ (trước 2026-11-04)
    idx = [e for e in _vindex(js_rel) if e.get("who") != "user" or e.get("pub")]
    d = _vdir(js_rel)
    js = safe(js_rel)
    cur = hashlib.sha1(open(js, "rb").read()).hexdigest() if js and os.path.isfile(js) else None
    want = _HEAD.get(js_rel)   # bản người dùng vừa bấm về (nhiều bản trùng nội dung thì sáng đúng bản đã bấm)
    head = want if any(e["id"] == want and e["hash"] == cur for e in idx) else next((e["id"] for e in reversed(idx) if e["hash"] == cur), None)
    return {"head": head, "versions": [dict({k: e.get(k) for k in ("id", "t", "who", "what", "from")},
                                            thumb=os.path.isfile(os.path.join(d, f"v{e['id']:04d}.jpg"))) for e in idx]}


def rigbase(js_rel):
    """rig gốc của asset: bản gần nhất Claude dựng rig (script rig ghi nhãn "Claude dựng rig ..."), không có thì bản cũ nhất."""
    ensure_version(js_rel)
    idx = _vindex(js_rel)
    if not idx:
        raise ValueError("chưa có phiên bản nào của file")
    rig = [e for e in idx if e.get("who") == "claude" and "rig" in (e.get("what") or "").lower()]
    e = rig[-1] if rig else idx[0]
    data = json.load(open(os.path.join(_vdir(js_rel), f"v{e['id']:04d}.json"), encoding="utf8"))
    bones = {x["name"]: {"rotation": x.get("rotation", 0), "x": x.get("x", 0), "y": x.get("y", 0),
                         "scaleX": x.get("scaleX", 1), "scaleY": x.get("scaleY", 1),
                         "shearX": x.get("shearX", 0), "shearY": x.get("shearY", 0)} for x in data.get("bones", [])}
    return {"id": e["id"], "t": e.get("t"), "what": e.get("what") or "", "bones": bones}


def publish_version(b):
    """nút Update (Properties): đưa bản hiện tại (người dùng sửa tay xong) vào cột Phiên bản."""
    js_rel = b.get("json", "")
    js = safe(js_rel)
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file")
    # 2026-11-04 (người dùng: "quay về bản cũ (từ 100 về 80) và nhấn update phiên bản tại properties thì lập tức xoá các
    # bản 81-100"): đang đứng ở bản cũ (bấm về ở cột Phiên bản) mà bấm Update -> xoá mọi bản sau nó trước khi ghi
    removed = []
    head = _HEAD.get(js_rel)
    idx = _vindex(js_rel)
    if head and idx and head != idx[-1]["id"] and any(e["id"] == head for e in idx):
        d = _vdir(js_rel)
        keep = [e for e in idx if e["id"] <= head]
        for e in idx:
            if e["id"] > head:
                removed.append(e["id"])
                for ext in (".json", ".jpg"):
                    try:
                        os.remove(os.path.join(d, f"v{e['id']:04d}{ext}"))
                    except OSError:
                        pass
        _save_json(os.path.join(d, "index.json"), keep)
    PENDING[js_rel] = {"who": "user", "what": b.get("what") or "Update (sửa tay)", "force": True}
    _VMT.pop(js_rel, None)
    vid = ensure_version(js_rel)
    if vid is None:   # nội dung trùng một bản đã có
        PENDING.pop(js_rel, None)
        hsh = hashlib.sha1(open(js, "rb").read()).hexdigest()
        same = next((e["id"] for e in _vindex(js_rel) if e["hash"] == hsh), None)
        return {"id": same, "same": True, "removed": removed}
    _HEAD[js_rel] = vid
    return {"id": vid, "same": False, "removed": removed}


def history_goto(b):
    """tab History (kiểu Photoshop): undo n bước hoặc redo n bước một lần (các bước sau vẫn giữ ở ngăn Làm lại)."""
    n_u, n_r = int(b.get("undo") or 0), int(b.get("redo") or 0)
    if n_u and n_r:
        raise ValueError("chỉ undo hoặc redo")
    r = None
    for _ in range(n_u):
        r = undo(b)
    for _ in range(n_r):
        r = redo(b)
    PENDING[b.get("json", "")] = {"who": "user", "what": f"Lịch sử: {'lùi' if n_u else 'tới'} {n_u or n_r} bước"}
    return {"history": history(b.get("json", "")), "steps": n_u or n_r}


def restore_version(b):
    js_rel = b.get("json", "")
    js = safe(js_rel)
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file")
    vid = int(b.get("id"))
    src = os.path.join(_vdir(js_rel), f"v{vid:04d}.json")
    if not os.path.isfile(src):
        raise ValueError(f"không còn bản #{vid}")
    ensure_version(js_rel)                       # chụp bản hiện tại trước (nếu chưa)
    # 2026-10-31 (người dùng: "đang ở bản 10 khi click về bản 9 thì lại nhảy thành bản 11 ... chỉ cần nhảy về ô ver 9"):
    # file = nội dung bản đó, đang ở bản đó; không tạo bản mới (sửa tiếp thì bản mới nối cuối danh sách như thường)
    backup(js, "user", f"Về bản #{vid}")
    _HEAD[js_rel] = vid
    shutil.copyfile(src, js)
    os.utime(js)
    ensure_version(js_rel)
    return {"id": vid}


def save_thumb(b):
    js_rel, vid, data = b.get("json", ""), int(b.get("id")), b.get("data", "")
    if not data.startswith("data:image/jpeg;base64,"):
        raise ValueError("ảnh không hợp lệ")
    raw = base64.b64decode(data.split(",", 1)[1])
    if len(raw) > 400_000:
        raise ValueError("ảnh quá lớn")
    d = _vdir(js_rel)
    if not os.path.isdir(d):
        raise ValueError("không có kho phiên bản")
    with open(os.path.join(d, f"v{vid:04d}.jpg"), "wb") as fh:
        fh.write(raw)
    return {}


def set_attachment(b):
    """Properties của layer ảnh (2026-10-31): ghi vị trí / góc / scale của ảnh thường, hoặc đỉnh của mesh (dời cả lưới),
    trong hệ xương cha (dữ liệu setup). Một bước Hoàn tác."""
    js_rel = b.get("json", "")
    js = safe(js_rel)
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file")
    data = json.load(open(js, encoding="utf8"))
    slot, name, want = b.get("slot"), b.get("attachment"), b.get("skin") or "default"
    skins = data.get("skins") or []
    if isinstance(skins, dict):   # định dạng cũ {tên: {slot: {...}}}
        skins = [{"name": k, "attachments": v} for k, v in skins.items()]
    found = None
    for sk in sorted(skins, key=lambda k: k.get("name") != want):
        a = ((sk.get("attachments") or {}).get(slot) or {}).get(name)
        if a is not None:
            found = a
            break
    if found is None:
        raise ValueError(f"không thấy ảnh {slot}/{name}")
    if b.get("fields"):
        if (found.get("type") or "region") != "region":
            raise ValueError("chỉ sửa x / y / xoay / scale cho ảnh thường")
        for k, d in (("x", 0), ("y", 0), ("rotation", 0), ("scaleX", 1), ("scaleY", 1)):
            v = round(float(b["fields"].get(k, found.get(k, d))), 3)
            if abs(v - d) < 1e-6:
                found.pop(k, None)
            else:
                found[k] = v
    elif b.get("vertices") is not None:
        if found.get("type") != "mesh":
            raise ValueError("ảnh này không phải mesh")
        if len(b["vertices"]) != len(found.get("vertices") or []):
            raise ValueError("số đỉnh không khớp (lưới đã đổi?): nạp lại trang")
        found["vertices"] = b["vertices"]
    else:
        raise ValueError("thiếu dữ liệu")
    label = f"{b.get('what') or 'Dời'} ảnh {slot}"
    backup(js, "user", label)
    PENDING[js_rel] = {"who": "user", "what": label}
    _save_json(js, data)
    return {}


def delete_file(b):
    """2026-10-31 (người dùng: "cho thêm chức năng có thể xoá trực tiếp file"): chuyển JSON skeleton vào work/_trash."""
    js_rel = b.get("json", "")
    js = safe(js_rel)
    if not js or not os.path.isfile(js) or not js.lower().endswith(".json"):
        raise ValueError("không thấy file " + str(js_rel))
    if not any(s["json"] == js_rel for s in skeletons()):
        raise ValueError("chỉ xoá được file skeleton trong danh sách Spine Live")
    dst = os.path.join(ROOT, "work", "_trash", "spine_" + time.strftime("%Y%m%d_%H%M%S"), js_rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(js, dst)
    return {"trash": os.path.relpath(dst, ROOT).replace("\\", "/")}


def _labeled(b, word, fn):
    r = fn(b)
    what = r.get("undone") or r.get("redone") or ""
    PENDING[b.get("json", "")] = {"who": "user", "what": f"{word}: {what}"}
    return r


def _params_path(js_rel):
    js = safe(js_rel or "")
    if not js:
        raise ValueError("không thấy file")
    return js, os.path.join(os.path.dirname(js), "params.json")


def get_params(js_rel):
    """mục "Tham số anim": tham số các script dựng anim khai báo (tools/spine/anim_params.py) trong <thư mục>/params.json."""
    try:
        _, pp = _params_path(js_rel)
        return json.load(open(pp, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def set_params(b):
    """ghi giá trị tham số của một nhóm rồi chạy lại các script của nhóm (một bước Hoàn tác "Tham số ...")."""
    import subprocess, sys as _sys
    js, pp = _params_path(b.get("json"))
    data = json.load(open(pp, encoding="utf8"))
    g = (data.get("groups") or {}).get(b.get("group") or "")
    if not g:
        raise ValueError("không có nhóm tham số " + str(b.get("group")))
    defs = {d["key"]: d for d in g.get("defs") or []}
    vals = dict(g.get("values") or {})
    if b.get("reset"):
        vals = {}
    for k, v in (b.get("values") or {}).items():
        d = defs.get(k)
        if d is None:
            continue
        v = min(d["max"], max(d["min"], float(v)))
        if v == d["default"]:
            vals.pop(k, None)
        else:
            vals[k] = v
    g["values"] = vals
    _save_json(pp, data)
    label = "Tham số " + g.get("label", b.get("group"))
    backup(js, "user", label)
    PENDING[b.get("json")] = {"who": "user", "what": label}
    log = []
    env = dict(os.environ, SPINE_LIVE_NO_BACKUP="1", PYTHONIOENCODING="utf-8")
    for rel_script in g.get("run") or []:
        sc = os.path.abspath(os.path.join(os.path.dirname(pp), rel_script))
        if not sc.startswith(os.path.dirname(pp) + os.sep) or not os.path.isfile(sc):
            raise ValueError("không thấy script " + rel_script)
        r = subprocess.run([_sys.executable, "-I", sc], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", timeout=180)
        out = (r.stdout or "").strip().splitlines()[-1:] + (r.stderr or "").strip().splitlines()[-3:]
        log.append(rel_script + ": " + " | ".join(out))
        if r.returncode:
            raise ValueError("script lỗi: " + log[-1])
    return {"log": log, "values": vals}


def handle_post(h, path, body):
    import spine_edit   # graph editor + sửa lưới mesh
    if path.startswith("/api/spine/br/"):   # cầu nối lệnh Claude <-> trang (spine_bridge.py)
        import spine_bridge
        return spine_bridge.handle_post(h, path, body)
    fn = {"/api/spine/key": key_pose, "/api/spine/params": set_params, "/api/spine/file/delete": delete_file, "/api/spine/attachment": set_attachment, "/api/spine/note": lambda b: {"id": add_note(b)}, "/api/spine/undo": lambda b: _labeled(b, "Hoàn tác", undo), "/api/spine/redo": lambda b: _labeled(b, "Làm lại", redo),
          "/api/spine/version/restore": restore_version, "/api/spine/version/thumb": save_thumb,
          "/api/spine/version/publish": publish_version, "/api/spine/history/goto": history_goto, "/api/spine/anim": anim_op,
          "/api/spine/keyed/clear": clear_keyed, "/api/spine/keyed/delete": delete_keypose,
          "/api/spine/timeline": lambda b, L="Sửa curve": spine_edit.set_timeline(b, safe, lambda js, L=L: backup(js, "user", L), _save_json),
          "/api/spine/mesh/trace": lambda b: spine_edit.trace(b, safe),
          "/api/spine/mesh/remesh": lambda b: spine_edit.remesh(b, safe),
          "/api/spine/mesh/tri": spine_edit.tri_preview,
          "/api/spine/timelines": lambda b: spine_edit.set_timelines(b, safe, lambda js, L: backup(js, "user", L), _save_json),
          "/api/spine/reduce": lambda b, L="Giảm key": spine_edit.reduce_anim(b, safe, lambda js, L=L: backup(js, "user", L), _save_json),
          "/api/spine/setup": lambda b, L="Lưu setup": spine_edit.set_setup(b, safe, lambda js, L=L: backup(js, "user", L), _save_json),
          "/api/spine/bind": lambda b, L="Bind weight": spine_edit.bind_auto(b, safe, lambda js, L=L: backup(js, "user", L), _save_json),
          "/api/spine/parent": lambda b, L="Đổi parent": spine_edit.set_parent(b, safe, lambda js, L=L: backup(js, "user", L), _save_json),
          "/api/spine/weights": lambda b, L="Lưu weight": spine_edit.set_weights(b, safe, lambda js, L=L: backup(js, "user", L), _save_json),
          "/api/spine/mesh/apply": lambda b, L="Áp dụng lưới": spine_edit.apply_mesh(b, safe, lambda js, L=L: backup(js, "user", L), _save_json)}.get(path)
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
    if path.startswith("/api/spine/br/"):   # cầu nối lệnh Claude <-> trang (spine_bridge.py)
        import spine_bridge
        return spine_bridge.handle_get(h, path, qs)
    if path in ("/spine", "/spine/"):
        html = open(os.path.join(PAGE, "index.html"), encoding="utf-8").read()

        def _ver(m):   # ?v=<mtime>: trình duyệt luôn nạp module mới khi file đổi (trước đây tab cũ giữ dock.js / meshbind.js cũ)
            f = os.path.join(PAGE, m.group(1))
            return '<script src="/spine/%s?v=%d"></script>' % (m.group(1), int(os.path.getmtime(f)) if os.path.isfile(f) else 0)
        html = re.sub(r'<script src="/spine/([\w.-]+\.js)"></script>', _ver, html)
        h.send_bytes(html.encode("utf-8"), "text/html; charset=utf-8", True)
        return True
    if path.startswith("/spine/vendor/") or (path.startswith("/spine/") and path.count("/") == 2 and path.endswith((".js", ".css"))):
        full = os.path.abspath(os.path.join(PAGE, path[len("/spine/"):]))
        ext = os.path.splitext(full)[1].lower()
        if full.startswith(PAGE + os.sep) and os.path.isfile(full) and ext in CT:
            # module của trang (không phải thư viện vendor): không cache, sửa tool là trang nạp bản mới ngay
            h.send_bytes(open(full, "rb").read(), CT[ext], not path.startswith("/spine/vendor/"))
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
    if path == "/api/spine/params":
        h.send_json(get_params((qs.get("json") or [""])[0]))
        return True
    if path == "/api/spine/anims":
        h.send_json(anims_for((qs.get("json") or [""])[0]))
        return True
    if path == "/api/spine/history":
        h.send_json(history((qs.get("json") or [""])[0]))
        return True
    if path == "/api/spine/keyed":
        h.send_json({a: [{k: e.get(k) for k in ("frame", "bones", "t", "used")} for e in lst]
                     for a, lst in (_load_keyed().get((qs.get("json") or [""])[0]) or {}).items()})
        return True
    if path == "/api/spine/clients":
        now = time.time()
        h.send_json([dict(v, id=k, ago=round(now - v["t"], 1)) for k, v in CLIENTS.items() if now - v["t"] < 3])
        return True
    if path == "/api/spine/versions":
        h.send_json(versions((qs.get("json") or [""])[0]))
        return True
    if path == "/api/spine/rigbase":
        try:
            h.send_json(rigbase((qs.get("json") or [""])[0]))
        except (ValueError, OSError) as e:
            h.send_json({"error": str(e)})
        return True
    if path == "/api/spine/version/thumb":
        js_rel, vid = (qs.get("json") or [""])[0], (qs.get("id") or ["0"])[0]
        f = os.path.join(_vdir(js_rel), f"v{int(vid):04d}.jpg") if vid.isdigit() else ""
        if f and os.path.isfile(f):
            h.send_bytes(open(f, "rb").read(), "image/jpeg")
        else:
            h.send_error(404)
        return True
    if path == "/api/spine/stat":
        try:
            ensure_version((qs.get("json") or [""])[0])   # file đổi -> phiên bản mới (mọi nguồn: key, Claude gen, Spine...)
        except Exception:
            pass
        t = stamp((qs.get("json") or [""])[0])
        code = 0   # dấu thời gian mã trang (html / js / css, không tính vendor): đổi -> trang tự tải lại
        try:
            for f in os.scandir(PAGE):
                if f.is_file() and f.name.endswith((".html", ".js", ".css")):
                    code = max(code, f.stat().st_mtime_ns)
        except OSError:
            pass
        h.send_json({"t": t, "code": code} if t is not None else {"error": "không thấy file"}, 200 if t is not None else 404)
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
