"""Dữ liệu workspace Pose của Studio: các phiên bản (POSES) của một anim, lấy từ bản gốc work/pose_lab/index.html
(cùng cách split_pages.py tách trang), kèm tên kho (<tiêu đề trang>_pose_lab) để dùng chung kho với Pose Lab cũ."""
import json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MASTER = os.path.join(ROOT, "work", "pose_lab", "index.html")
REG = os.path.join(ROOT, "work", "clips.json")


def slug(s):   # giống LOCALDB của các Lab: tên kho = slug(tiêu đề trang)
    return (re.sub(r"[^a-z0-9]+", "_", str(s or "page").lower()).strip("_")[:80]) or "page"


def _entries():
    src = open(MASTER, encoding="utf8").read()
    m = re.search(r"const POSES = \[\n(.*?)\n\];", src, re.S)
    return [e.rstrip().rstrip(",") for e in m.group(1).split("\n") if e.strip().startswith("{ clip:")]


def clip_versions():
    out = {}
    for e in _entries():
        c = re.match(r'\s*\{ clip: "((?:[^"\\]|\\.)*)"', e).group(1)
        out.setdefault(c, []).append(e)
    return out


def poses(clip_id):
    reg = json.load(open(REG, encoding="utf8"))
    c = next((x for x in reg["clips"] if x["id"] == clip_id or (x.get("pose") or {}).get("key") == clip_id), None)
    if not c or not c.get("pose"):
        return None
    p = c["pose"]
    mine = clip_versions().get(p["clip"], [])
    if not mine:
        return None
    return {"id": c["id"], "character": c["character"], "name": c.get("title") or p["title"].replace(" Pose Lab", ""),
            "title": p["title"], "ns": slug(p["title"]), "stage": c.get("stage", ""), "js": "[\n" + ",\n".join(mine) + "\n]"}


def clips_for(char_names):
    """Anim có Pose Lab của các nhân vật (tên trong sổ, vd "Gaygor")."""
    reg = json.load(open(REG, encoding="utf8"))
    have = clip_versions()
    out = []
    for c in reg["clips"]:
        p = c.get("pose")
        if p and (char_names is None or c["character"] in char_names) and p.get("clip") in have:
            out.append({"id": c["id"], "character": c["character"], "name": c.get("title") or p["title"].replace(" Pose Lab", ""), "stage": c.get("stage", ""),
                        "versions": len(have[p["clip"]]), "updated": c.get("updated", "")})
    return out
