"""Nhập FBX cho Studio (không Blender): đọc bằng work/rig_lab/extract_fbx.py (fbxread), đổi về cm + trục Y lên.
parse(bytes)            -> mesh (cm, Y lên) + số xương, để Studio thêm / thay mesh trong cảnh
new_char(bytes, name)   -> tạo nhân vật mới: work/rig_lab/ref_<id>/ (mesh + skeleton + skin), chars/<id>.json, chars/<id>/mesh_cm.json
"""
import json, os, re, shutil, subprocess, sys, tempfile
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RIG = os.path.join(ROOT, "work", "rig_lab")
sys.path.insert(0, os.path.join(ROOT, "work", "pose_lab", "fbx"))


def _axes(path):
    """GlobalSettings: đơn vị (cm / đơn vị file) và trục. Mặc định như Maya: cm, Y lên."""
    import fbxread
    _, top = fbxread.read(path)
    T = {n[0]: n for n in top}
    g = {"UpAxis": 1, "UpAxisSign": 1, "FrontAxis": 2, "FrontAxisSign": 1, "CoordAxis": 0, "CoordAxisSign": 1, "UnitScaleFactor": 1.0}
    gs = T.get("GlobalSettings")
    if gs:
        p70 = next((k for k in gs[2] if k[0] == "Properties70"), None)
        for p in (p70[2] if p70 else []):
            if p[1][0] in g and len(p[1]) > 4:
                g[p[1][0]] = p[1][4]
    return g


def _extract(data):
    """Chạy extract_fbx.py vào thư mục tạm, trả (meshes, skeleton, axes)."""
    tmp = tempfile.mkdtemp(prefix="fbx_")
    try:
        f = os.path.join(tmp, "in.fbx")
        open(f, "wb").write(data)
        if data[:18] != b"Kaydara FBX Binary":
            raise ValueError("chỉ đọc được FBX dạng binary (không đọc FBX ASCII)")
        r = subprocess.run([sys.executable, "-I", os.path.join(RIG, "extract_fbx.py"), f, os.path.join(tmp, "out")],
                           capture_output=True, text=True, encoding="utf8", errors="replace", timeout=120)
        if r.returncode:
            raise ValueError("không đọc được FBX: " + (r.stderr.strip().splitlines() or ["?"])[-1])
        meshes = json.load(open(os.path.join(tmp, "out", "ref_mesh.json")))
        skel = json.load(open(os.path.join(tmp, "out", "ref_skeleton.json")))
        return meshes, skel, _axes(f)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _converter(ax, meshes):
    """Hàm đổi điểm file → cm, Y lên, mặt trước +Z, phải −X như các Lab. Đơn vị: UnitScaleFactor (cm / đơn vị);
    nếu ra chiều cao vô lý (< 10 cm hoặc > 5 000 cm) thì đoán lại (file mét → ×100)."""
    c, u, fr = int(ax["CoordAxis"]), int(ax["UpAxis"]), int(ax["FrontAxis"])
    cs, us, fs = float(ax["CoordAxisSign"]), float(ax["UpAxisSign"]), float(ax["FrontAxisSign"])
    k = float(ax["UnitScaleFactor"] or 1.0)
    ys = [v[u] * us for m in meshes for v in zip(*[iter(m["verts"])] * 3)]
    h = (max(ys) - min(ys)) * k if ys else 0
    note = ""
    if h and h < 10:
        note = "file cao %.2f cm: coi là mét, ×100" % h; k *= 100
    elif h > 5000:
        note = "file cao %.0f cm: chia 100" % h; k /= 100
    return (lambda p: [round(p[c] * cs * k, 4), round(p[u] * us * k, 4), round(p[fr] * fs * k, 4)]), k, note


def _convert(data):
    meshes, skel, ax = _extract(data)
    conv, k, note = _converter(ax, meshes)
    out = []
    for m in meshes:
        V = [conv(p) for p in zip(*[iter(m["verts"])] * 3)]
        out.append({"name": m["name"], "verts": [x for p in V for x in p], "tris": m["tris"], "weights": m.get("weights") or {}})
    for s in skel:
        if s.get("bind_pos"):
            s["bind_pos"] = conv(s["bind_pos"])
    up = "XYZ"[int(ax["UpAxis"])]
    return out, skel, {"unit_cm": k, "up": up, "note": note}


def _bbox(verts):
    xs, ys, zs = verts[0::3], verts[1::3], verts[2::3]
    return [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]


def parse(data):
    meshes, skel, info = _convert(data)
    res = []
    for m in meshes:
        mn, mx = _bbox(m["verts"]) if m["verts"] else ([0] * 3, [0] * 3)
        res.append({"name": m["name"], "verts": m["verts"], "tris": m["tris"], "bones": len(m["weights"]),
                    "min": [round(v, 1) for v in mn], "max": [round(v, 1) for v in mx]})
    return {"meshes": res, "bones": len(skel), **info}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]


def new_char(data, name, filename=""):
    name = (name or "").strip()
    cid = slug(name)
    if not cid:
        raise ValueError("cần tên nhân vật (chữ không dấu / số)")
    if cid == "gaygor" or os.path.exists(os.path.join(RIG, "chars", cid + ".json")):
        raise ValueError("đã có nhân vật '" + cid + "', chọn tên khác")
    meshes, skel, info = _convert(data)
    if not meshes:
        raise ValueError("FBX không có mesh")
    ref = os.path.join(RIG, "ref_" + cid)
    os.makedirs(ref, exist_ok=True)
    json.dump(meshes, open(os.path.join(ref, "ref_mesh.json"), "w"), separators=(",", ":"))
    json.dump(skel, open(os.path.join(ref, "ref_skeleton.json"), "w"), separators=(",", ":"))
    body = max(meshes, key=lambda m: len(m["tris"]))["name"]
    cfg = {"id": cid, "name": name, "ref_dir": "ref_" + cid, "scale": 1, "body": body, "clothes": [],
           "extra": [m["name"] for m in meshes if m["name"] != body], "names_from": "ref_" + cid if skel else "",
           "cfg": {"name": body}, "source": "Studio Nhập FBX %s: %s" % (date.today().isoformat(), filename or "?"),
           "note": "Rig chưa dựng: đặt clothes / cfg trước khi chạy build_char.py"}
    os.makedirs(os.path.join(RIG, "chars", cid), exist_ok=True)
    json.dump(cfg, open(os.path.join(RIG, "chars", cid + ".json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    json.dump([{"name": m["name"], "verts": m["verts"], "tris": m["tris"]} for m in meshes],
              open(os.path.join(RIG, "chars", cid, "mesh_cm.json"), "w"), separators=(",", ":"))
    return {"id": cid, "name": name, "meshes": len(meshes), "bones": len(skel), **info}
