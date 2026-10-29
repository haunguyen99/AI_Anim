"""File cảnh của Studio (.aas, "AI Anim Scene"): một nhân vật cùng mọi thứ cần để mở lại ở máy khác,
gói thành một file zip, giống .ma / .blend của các DCC khác.

Trong file:
  manifest.json            định dạng, nhân vật, ngày lưu, mục sổ work/clips.json (nhân vật, anim, dự án), dòng POSES của các anim
  files/<đường dẫn từ gốc>  file thật, chỉ trong work/:
    work/rig_lab/chars/<id>.json, chars/<id>/**      cấu hình + mesh gốc (cm) + texture
    work/rig_lab/<ref_dir>/**, <names_from>/**        mesh + xương tham chiếu
    work/rig_lab/pages/<id>/index.html                dữ liệu rig (Studio đọc qua /api/rigdata)
    work/store/<nhân vật>_{mesh_lab,rig_lab,studio}  mesh đã sửa, khớp, skin, physics, ghi chú
    work/store/<anim>_pose_lab, <anim>_studio         key, anim của từng phiên bản Pose
    work/pose_lab/models/<model>                      model glTF của từng phiên bản Pose
    work/<thư mục anim>/ (chỉ file chữ: md, json, txt) brief, ghi chú

Mở cảnh: chép file vào đúng chỗ (ghi đè), gộp sổ clips.json, thêm dòng POSES còn thiếu, build lại trang Pose / Review.
Không gói video ref, playblast, FBX gốc (nặng; chép tay nếu cần).

CLI:  .venv\\Scripts\\python.exe -I tools\\home\\scene_file.py save <nhân vật> [file.aas]
      .venv\\Scripts\\python.exe -I tools\\home\\scene_file.py open <file.aas> [--dry]
"""
import io, json, os, re, subprocess, sys, zipfile
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
WORK = os.path.join(ROOT, "work")
RIG = os.path.join(WORK, "rig_lab")
REG = os.path.join(WORK, "clips.json")
POSE_HTML = os.path.join(WORK, "pose_lab", "index.html")
FORMAT = "ai-anim-scene-v1"
TEXT_EXT = (".md", ".json", ".txt")
CHAR_NS = ("_mesh_lab", "_rig_lab", "_studio")


def slug(s):   # giống ST.slug / pose_data.slug: tên kho = slug(tên)
    return (re.sub(r"[^a-z0-9]+", "_", str(s or "page").lower()).strip("_")[:80]) or "page"


def _cid_ok(cid):
    if not re.match(r"^[A-Za-z0-9_\-]+$", cid or ""):
        raise ValueError("tên nhân vật không hợp lệ: " + str(cid))


def _char_info(cid):
    """(tên, [thư mục tham chiếu]) của nhân vật Studio."""
    if cid == "gaygor":
        return "Gaygor", ["ref_gaygor"]
    cf = os.path.join(RIG, "chars", cid + ".json")
    if not os.path.isfile(cf):
        raise ValueError("không có nhân vật " + cid)
    C = json.load(open(cf, encoding="utf8"))
    refs = [r for r in (C.get("ref_dir"), C.get("names_from")) if r]
    return C.get("name") or cid, refs


def _reg_names(d, cid, name):
    """Tên nhân vật trong sổ khớp với nhân vật Studio (giống /api/poses)."""
    out = []
    for n, c in (d.get("characters") or {}).items():
        if (c or {}).get("rig_page") == cid or n.lower() in (cid.lower(), name.lower()) or slug(n) == cid:
            out.append(n)
    return out


def _pose_entries():
    src = open(POSE_HTML, encoding="utf8").read()
    m = re.search(r"const POSES = \[\n(.*?)\n\];", src, re.S)
    return [e.rstrip().rstrip(",") for e in m.group(1).split("\n") if e.strip().startswith("{ clip:")] if m else []


def _entry_key(e):
    c = re.search(r'clip: "((?:[^"\\]|\\.)*)"', e)
    v = re.search(r'version: "((?:[^"\\]|\\.)*)"', e)
    return (c.group(1) if c else "", v.group(1) if v else "")


def _walk(rel_dir, only_text=False):
    full = os.path.join(ROOT, rel_dir)
    if not os.path.isdir(full):
        return []
    out = []
    for dp, _, fs in os.walk(full):
        for f in fs:
            if f.endswith(".tmp") or (only_text and os.path.splitext(f)[1].lower() not in TEXT_EXT):
                continue
            out.append(os.path.relpath(os.path.join(dp, f), ROOT).replace("\\", "/"))
    return out


def collect(cid):
    """Danh sách file + manifest của một nhân vật."""
    _cid_ok(cid)
    name, refs = _char_info(cid)
    d = json.load(open(REG, encoding="utf8"))
    names = _reg_names(d, cid, name)
    clips = [c for c in d.get("clips", []) if c.get("character") in names]
    projects = [p for p in d.get("projects", []) if set(p.get("characters") or []) & set(names)]
    files = []
    if cid != "gaygor":
        files.append("work/rig_lab/chars/%s.json" % cid)
        files += _walk("work/rig_lab/chars/" + cid)
    for r in refs:
        files += _walk("work/rig_lab/" + r)
    files += _walk("work/rig_lab/pages/" + cid)
    stores = [slug(name) + s for s in CHAR_NS]
    poses = {}
    entries = _pose_entries()
    for c in clips:
        p = c.get("pose") or {}
        if p.get("title"):
            stores.append(slug(p["title"]))
        stores.append(slug(c["id"]) + "_studio")
        mine = [e for e in entries if _entry_key(e)[0] == p.get("clip")] if p.get("clip") else []
        if mine:
            poses[c["id"]] = mine
        for e in mine:
            g = re.search(r'glb: "([^"]+)"', e)
            if g and not g.group(1).startswith(("http:", "https:", "/")):
                f = os.path.normpath(os.path.join("work", "pose_lab", g.group(1))).replace("\\", "/")
                if f.startswith("work/") and os.path.isfile(os.path.join(ROOT, f)):
                    files.append(f)
        cdir = c.get("dir") or ("work/" + c["id"])
        files += _walk(cdir, only_text=True)
    for ns in dict.fromkeys(stores):
        files += _walk("work/store/" + ns)
    files = [f for f in dict.fromkeys(files) if os.path.isfile(os.path.join(ROOT, f))]
    chars = {n: d["characters"][n] for n in names}
    man = {"format": FORMAT, "id": cid, "name": name, "saved": datetime.now().isoformat(timespec="seconds"),
           "registry": {"characters": chars, "clips": clips, "projects": projects}, "poses": poses, "files": files}
    return man


def save(cid):
    """Gói nhân vật thành bytes zip (.aas)."""
    man = collect(cid)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr("manifest.json", json.dumps(man, ensure_ascii=False, indent=1))
        for f in man["files"]:
            z.write(os.path.join(ROOT, f), "files/" + f)
    return buf.getvalue()


ALLOWED = ("work/rig_lab/chars/", "work/rig_lab/ref_", "work/rig_lab/pages/", "work/store/", "work/pose_lab/models/")


def _target(rel):
    """Đường dẫn đích an toàn trong work/ (chặn .., đường tuyệt đối, chỗ ngoài danh sách)."""
    rel = rel.replace("\\", "/")
    parts = rel.split("/")
    if rel.startswith("/") or ":" in rel or any(p in ("..", ".", "") for p in parts) or len(parts) < 3 or rel.startswith("work/store/_sys/"):
        raise ValueError("đường dẫn lạ trong file cảnh: " + rel)
    full = os.path.abspath(os.path.join(ROOT, rel))
    if not full.startswith(WORK + os.sep):
        raise ValueError("file nằm ngoài work/: " + rel)
    if not rel.startswith(ALLOWED) and os.path.splitext(rel)[1].lower() not in TEXT_EXT:
        raise ValueError("không nhận file này: " + rel)
    return full


def _read_zip(data):
    z = zipfile.ZipFile(io.BytesIO(data))
    try:
        man = json.loads(z.read("manifest.json"))
    except KeyError:
        raise ValueError("không phải file cảnh Studio (thiếu manifest.json)")
    if man.get("format") != FORMAT:
        raise ValueError("định dạng lạ: " + str(man.get("format")))
    _cid_ok(man.get("id"))
    return z, man


def _merge_registry(R):
    d = json.load(open(REG, encoding="utf8"))
    d.setdefault("characters", {})
    for n, c in (R.get("characters") or {}).items():
        d["characters"][n] = {**d["characters"].get(n, {}), **(c or {})}
    by = {c["id"]: i for i, c in enumerate(d.setdefault("clips", []))}
    for c in R.get("clips") or []:
        if c["id"] in by:
            d["clips"][by[c["id"]]] = c
        else:
            d["clips"].append(c)
    pj = {p["id"]: p for p in d.setdefault("projects", [])}
    for p in R.get("projects") or []:
        if p["id"] in pj:
            q = pj[p["id"]]
            for n in p.get("characters") or []:
                if n not in q.setdefault("characters", []):
                    q["characters"].append(n)
            q.setdefault("labels", {}).update({k: v for k, v in (p.get("labels") or {}).items() if k not in q.get("labels", {})})
        else:
            d["projects"].append(p)
    tmp = REG + ".tmp"
    with open(tmp, "w", encoding="utf8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, REG)


def _merge_poses(poses):
    have = {_entry_key(e) for e in _pose_entries()}
    new = [e for es in poses.values() for e in es if _entry_key(e) not in have]
    if not new:
        return 0
    src = open(POSE_HTML, encoding="utf8").read()
    mk = "const POSES = [\n"
    i = src.index(mk) + len(mk)
    open(POSE_HTML, "w", encoding="utf8").write(src[:i] + "".join("  " + e.strip() + ",\n" for e in new) + src[i:])
    return len(new)


def open_scene(data, dry=False):
    """Bung file cảnh. dry=True: chỉ đọc manifest, cho biết nhân vật đã có trên máy chưa (để hỏi trước khi ghi đè)."""
    z, man = _read_zip(data)
    cid = man["id"]
    exists = os.path.isfile(os.path.join(RIG, "chars", cid + ".json")) or (cid == "gaygor" and os.path.isdir(os.path.join(RIG, "ref_gaygor")))
    info = {"id": cid, "name": man.get("name") or cid, "saved": man.get("saved"), "exists": exists,
            "clips": [c["id"] for c in man["registry"].get("clips") or []], "files": len(man.get("files") or [])}
    if dry:
        return info
    names = [n[len("files/"):] for n in z.namelist() if n.startswith("files/") and not n.endswith("/")]
    targets = [(n, _target(n)) for n in names]   # kiểm hết trước khi ghi file nào
    for n, full in targets:
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(z.read("files/" + n))
    _merge_registry(man.get("registry") or {})
    info["poses_added"] = _merge_poses(man.get("poses") or {})
    if man.get("poses"):
        r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "clip_registry.py"), "build"], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf8", errors="replace", timeout=300)
        if r.returncode:
            info["warn"] = "build trang Pose/Review lỗi: " + (r.stderr.strip().splitlines() or ["?"])[-1]
    return info


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "save":
        out = a[2] if len(a) > 2 else a[1] + ".aas"
        b = save(a[1])
        open(out, "wb").write(b)
        print("Đã lưu", out, "(%.1f MB)" % (len(b) / 1048576))
    elif len(a) >= 2 and a[0] == "open":
        print(json.dumps(open_scene(open(a[1], "rb").read(), dry="--dry" in a), ensure_ascii=False, indent=1))
    else:
        print(__doc__)
