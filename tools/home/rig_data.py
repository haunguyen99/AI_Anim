"""Dữ liệu rig cho workspace Rig của Studio.
data(cid)   -> DATA của Rig Lab (mesh thân / quần áo / prop cm, landmark gợi ý, mẫu ngón, cấu hình, xương + skin khách),
               lấy đúng bản Rig Lab đang dùng: JSON nhúng trong work/rig_lab/pages/<id>/index.html (build_page.py / build_char.py).
build(cid)  -> nhân vật chưa có trang Rig (vd nhập FBX trong Studio): suy cấu hình từ xương khách rồi chạy build_char.py.
"""
import json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RIG = os.path.join(ROOT, "work", "rig_lab")
MARK = "(window.__meshApply || (d => d))("


def _ok(cid):
    if not re.match(r"^[A-Za-z0-9_\-]+$", cid or ""):
        raise ValueError("id nhân vật không hợp lệ")


def data(cid):
    _ok(cid)
    p = os.path.join(RIG, "pages", cid, "index.html")
    if not os.path.isfile(p):
        return None
    html = open(p, encoding="utf8").read()
    i = html.find(MARK)
    if i < 0:
        raise ValueError("trang Rig Lab của " + cid + " không có dữ liệu nhúng")
    d, _ = json.JSONDecoder().raw_decode(html, i + len(MARK))
    d["name"] = cid
    cf = os.path.join(RIG, "chars", cid + ".json")
    C = json.load(open(cf, encoding="utf8")) if os.path.isfile(cf) else {}
    d["title"] = C.get("name", cid) if C else ("Gaygor" if cid == "gaygor" else cid)
    # nhân vật nhập FBX đã rig (xương + skin của chính nó): build_char.py để trống vị trí xương khách và skin khách,
    # ở đây điền lại để dùng được "Đặt khớp theo xương khách" / "Dùng skin khách"
    if C and C.get("names_from") and C.get("names_from") == C.get("ref_dir") and not d.get("refW"):
        sc, ref = C.get("scale", 1), os.path.join(RIG, C["ref_dir"])
        try:
            sk = {s["name"]: s.get("bind_pos") for s in json.load(open(os.path.join(ref, "ref_skeleton.json")))}
            for b in d.get("ref", []):
                if b.get("pos") is None and sk.get(b["name"]):
                    b["pos"] = [round(v * sc, 3) for v in sk[b["name"]]]
            body = next((m for m in json.load(open(os.path.join(ref, "ref_mesh.json"))) if m["name"] == d["body"]["name"]), None)
            if body and len(body["verts"]) == len(d["body"]["verts"]) and body.get("weights"):
                d["refW"] = {k: [v[0], [round(x, 3) for x in v[1]]] for k, v in body["weights"].items()}
        except (OSError, ValueError, KeyError):
            pass
    return d


def _cfg_from_skeleton(names, body):
    """Cấu hình template Rig Lab theo tên xương khách (Advanced Skeleton: Root_M, Hip_R, MiddleFinger1_R…)."""
    n = set(names)
    fingers = [f for f in ["Middle", "Thumb", "Index", "Ring", "Pinky"] if f + "Finger1_R" in n]
    fseg = max([i for i in (1, 2, 3) if any(f + "Finger%d_R" % i in n for f in fingers)] or [1])
    return {"name": body, "fingers": fingers or ["Middle"], "fseg": fseg,
            "toes": "Toes_R" in n, "toesEnd": "ToesEnd_R" in n and "Toes_R" not in n, "fingerEnd": any(f + "FingerEnd_R" in n for f in fingers),
            "headEnd": "HeadEnd_M" in n, "dress": "DressFront_M" in n, "prop": "Prop_M" in n, "weapon": "Weapon" in n}


def _restore_ref(cid, C):
    """Thiếu work/rig_lab/ref_<id> (dữ liệu không có trong repo): mesh có skin weights thì dựng lại xương khách
    (skel_from_weights.py, khớp đặt theo vùng chuyển trọng số); không có weights thì chỉ chép mesh, rig như model tĩnh."""
    cf = os.path.join(RIG, "chars", cid + ".json")
    mp = os.path.join(RIG, "chars", cid, "mesh_cm.json")
    if not os.path.isfile(mp):
        raise ValueError("thiếu mesh của " + cid + " (work/rig_lab/chars/" + cid + "/mesh_cm.json): nhập lại FBX bằng Tệp → Nhập FBX")
    meshes = json.load(open(mp))
    body = next((m for m in meshes if m["name"] == C["body"]), None)
    C["ref_dir"] = C.get("ref_dir") or "ref_" + cid
    if body and body.get("weights"):
        r = subprocess.run([sys.executable, "-I", os.path.join(RIG, "skel_from_weights.py"), cid], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf8", errors="replace", timeout=300)
        if r.returncode:
            raise ValueError("dựng lại xương từ skin lỗi: " + (r.stderr.strip().splitlines() or ["?"])[-1])
        C["names_from"] = C["ref_dir"]; C["auto_from_ref"] = True
    else:
        ref = os.path.join(RIG, C["ref_dir"]); os.makedirs(ref, exist_ok=True)
        sc = C.get("scale", 1) or 1
        json.dump([dict(m, verts=[round(v / sc, 4) for v in m["verts"]]) for m in meshes], open(os.path.join(ref, "ref_mesh.json"), "w"), separators=(",", ":"))
        C["names_from"] = ""
    json.dump(C, open(cf, "w", encoding="utf8"), ensure_ascii=False, indent=1)


def build(cid):
    _ok(cid)
    cf = os.path.join(RIG, "chars", cid + ".json")
    if not os.path.isfile(cf):
        raise ValueError("chưa có work/rig_lab/chars/" + cid + ".json (nhập FBX bằng Tệp → Nhập FBX trước)")
    C = json.load(open(cf, encoding="utf8"))
    sk_path = os.path.join(RIG, C.get("names_from") or C["ref_dir"], "ref_skeleton.json")
    if not os.path.isfile(sk_path) or not os.path.isfile(os.path.join(RIG, C["ref_dir"], "ref_mesh.json")):
        _restore_ref(cid, C)   # máy không có FBX gốc: dựng lại xương khách từ skin weights (hoặc chỉ mesh nếu là model tĩnh)
        C = json.load(open(cf, encoding="utf8"))
        sk_path = os.path.join(RIG, C.get("names_from") or C["ref_dir"], "ref_skeleton.json")
    names = [s["name"] for s in json.load(open(sk_path))] if os.path.isfile(sk_path) else []
    if "fingers" not in C.get("cfg", {}):
        # có xương kiểu Advanced Skeleton thì theo tên xương; model tĩnh thì bàn tay mặc định 5 ngón × 3 đốt
        C["cfg"] = {**(_cfg_from_skeleton(names, C["body"]) if "Wrist_R" in names else
                       {"name": C["body"], "fingers": ["Middle", "Thumb", "Index", "Ring", "Pinky"], "fseg": 3, "toes": True, "toesEnd": False,
                        "fingerEnd": False, "headEnd": True, "dress": False, "prop": False, "weapon": False}), **C.get("cfg", {})}
        C.pop("note", None)
        json.dump(C, open(cf, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    r = subprocess.run([sys.executable, "-I", os.path.join(RIG, "build_char.py"), cid], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf8", errors="replace", timeout=300)
    if r.returncode:
        raise ValueError("build_char lỗi: " + (r.stderr.strip().splitlines() or ["?"])[-1])
    return {"id": cid, "cfg": C["cfg"]}
