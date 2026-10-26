"""Dump an armature's bone hierarchy and guess a bone mapping.

blender -b -P legacy/blender/inspect_rig.py -- MODEL --rig-out rig.json --map-out mapping.json [--armature NAME]

rig.json     : every bone (parent, head/tail in armature space, length, depth)
mapping.json : a first-guess mapping from MediaPipe landmarks to this rig. Claude
               must review it (bone names in custom rigs are ambiguous).
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bl_common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

# role -> regexes tried against a bone name with its side token removed (lowercase).
ROLE_PATTERNS = [
    ("toe", [r"toe", r"ball"]),
    ("foot", [r"foot", r"ankle"]),
    ("thigh", [r"thigh", r"upleg", r"upper_?leg", r"femur", r"leg\W*_?(up|upper|1)\b"]),
    ("shin", [r"shin", r"calf", r"lower_?leg", r"knee", r"crus", r"leg\W*_?(low|lower|2)\b", r"^leg$", r"leg"]),
    ("hand", [r"hand", r"wrist", r"palm"]),
    ("forearm", [r"forearm", r"fore_?arm", r"lower_?arm", r"lowarm", r"elbow", r"ulna",
                 r"arm\W*_?(low|lower|2)\b"]),
    ("upperarm", [r"upper_?arm", r"uparm", r"humerus", r"^arm$", r"arm"]),
    ("clavicle", [r"clavicle", r"collar", r"shoulder", r"scapula"]),
    ("neck", [r"neck"]),
    ("head", [r"^head$", r"head(?!.*(end|top|tip))"]),
    ("hips", [r"hips?$", r"pelvis", r"^hip", r"cog"]),
    ("spine", [r"spine", r"chest", r"torso", r"abdomen", r"belly", r"back", r"waist"]),
]
FINGER = re.compile(r"thumb|index|middle|ring|pinky|little|finger|digit|metacarp")
SIDE_TOKENS = [
    (r"(^|[._\-\s:])(l|left)($|[._\-\s:0-9])", "L"),
    (r"(^|[._\-\s:])(r|right)($|[._\-\s:0-9])", "R"),
    (r"^left", "L"), (r"^right", "R"), (r"left", "L"), (r"right", "R"),
]


def clean(name):
    n = name.lower()
    n = re.sub(r"^(mixamorig\d*:|def[-_]|org[-_]|mch[-_]|bip\d*\s?|cc_base_|j_bip_[clr]_|bone_?)", "", n)
    return n


def split_side(name):
    n = clean(name)
    m = re.search(r"[._\-](m|c|mid|center|middle)$", n)  # AdvancedSkeleton-style centre suffix
    if m:
        return None, n[:m.start()]
    for pat, side in SIDE_TOKENS:
        m = re.search(pat, n)
        if m:
            return side, (n[:m.start()] + " " + n[m.end():]).strip(" ._-:")
    return None, n


def guess_roles(arm, order):
    roles = {}  # (role, side) -> [bone names]
    for b in order:
        side, base = split_side(b.name)
        if FINGER.search(base) or re.search(r"(end|tip|top|twist|ik|pole|target|roll)", base):
            continue
        for role, pats in ROLE_PATTERNS:
            if any(re.search(p, base) for p in pats):
                if role in ("hips", "spine", "neck", "head"):
                    side = None
                elif side is None:
                    side = "L" if b.head_local.x > 0 else "R"
                roles.setdefault((role, side), []).append(b.name)
                break
    depth = {b.name: len(b.parent_recursive) for b in order}
    for names in roles.values():
        names.sort(key=lambda n: depth[n])
    bones = arm.data.bones

    for s in ("L", "R"):
        # "Hip_L" is a thigh, not the pelvis
        sided = [n for n in roles.get(("hips", None), []) if split_side(n)[0] == s]
        for n in sided:
            roles[("hips", None)].remove(n)
            roles.setdefault(("thigh", s), []).insert(0, n)
        # Scapula_L -> Shoulder_L -> Elbow_L: the deeper "shoulder" is the upper arm
        clav = roles.get(("clavicle", s), [])
        if not roles.get(("upperarm", s)):
            fore = roles.get(("forearm", s), [])
            for n in reversed(clav):
                if len(clav) > 1 or (fore and bones[fore[0]].parent and bones[fore[0]].parent.name == n):
                    roles[("upperarm", s)] = [n]
                    clav.remove(n)
                    break
    if not roles.get(("hips", None)) or not roles[("hips", None)]:
        # pelvis = the bone both thighs hang from
        tl, tr = roles.get(("thigh", "L")), roles.get(("thigh", "R"))
        if tl and tr and bones[tl[0]].parent and bones[tr[0]].parent and                 bones[tl[0]].parent == bones[tr[0]].parent:
            roles[("hips", None)] = [bones[tl[0]].parent.name]
    hips = (roles.get(("hips", None)) or [None])[0]
    if hips and ("spine", None) in roles:
        roles[("spine", None)] = [n for n in roles[("spine", None)] if n != hips]
    # real spine bones lie on the chain between pelvis and neck (drops e.g. "DressBack")
    top = (roles.get(("neck", None)) or roles.get(("upperarm", "L")) or [None])[0]
    if top and ("spine", None) in roles:
        chain = {p.name for p in bones[top].parent_recursive}
        roles[("spine", None)] = [n for n in roles[("spine", None)] if n in chain]

    picked = {}
    for (role, side), names in roles.items():
        if names:
            picked[(role, side)] = names if role == "spine" else names[0]
    return picked


def tip_joint(bone, prefer=None):
    """Joint spec for the far end of a bone. FBX/Maya rigs often have tails that
    don't point down the chain, so use a child's head when there is one."""
    kids = list(bone.children)
    if prefer:
        for c in kids:
            if re.search(prefer, c.name.lower()):
                return {"bone": c.name, "end": "head"}
    if len(kids) == 1:
        return {"bone": kids[0].name, "end": "head"}
    if kids:
        far = max(kids, key=lambda c: (c.head_local - bone.head_local).length)
        return {"bone": far.name, "end": "head"}
    return {"bone": bone.name, "end": "tail"}


def build_mapping(arm, picked):
    bones = arm.data.bones
    g = lambda role, side=None: picked.get((role, side))  # noqa: E731
    joints, entries, missing = {}, [], []

    def joint(lm, role, side, end="head"):
        b = g(role, side)
        if b:
            joints[lm] = {"bone": b, "end": end}
        else:
            missing.append(f"{role}.{side}")

    for s, lr in (("L", "left"), ("R", "right")):
        joint(f"{lr}_hip", "thigh", s)
        joint(f"{lr}_knee", "shin", s)
        joint(f"{lr}_ankle", "foot", s)
        if g("toe", s):
            joints[f"{lr}_toe"] = tip_joint(bones[g("toe", s)])
        elif g("foot", s):
            joints[f"{lr}_toe"] = tip_joint(bones[g("foot", s)])
        joint(f"{lr}_shoulder", "upperarm", s)
        joint(f"{lr}_elbow", "forearm", s)
        joint(f"{lr}_wrist", "hand", s)
        if g("hand", s):
            joints[f"{lr}_hand"] = tip_joint(bones[g("hand", s)], prefer=r"middle|mid|finger.*[23]|index")

    if not all(k in joints for k in ("left_hip", "right_hip", "left_shoulder", "right_shoulder")):
        return {"joints": joints, "bones": [], "missing": missing}

    rest = C.resolve_rest_points(arm, {"joints": joints})
    side, up, fwd = C.rig_axes(rest)
    head = g("head") or g("neck")
    if head:
        hb = bones[head]
        h = max(hb.length, (rest["mid_shoulder"] - rest["mid_hip"]).length * 0.25)
        ear = hb.head_local + up * h * 0.5
        joints["mid_ear"] = {"pos": C.vec(ear)}
        joints["left_ear"] = {"pos": C.vec(ear + side * h * 0.3)}
        joints["right_ear"] = {"pos": C.vec(ear - side * h * 0.3)}
        joints["nose"] = {"pos": C.vec(ear + fwd * h * 0.35 - up * h * 0.12)}

    hips = g("hips")
    torso_twist = [["right_hip", "left_hip", 1.0]]
    if hips:
        entries.append({"bone": hips, "mode": "frame", "dir": ["mid_hip", "mid_shoulder"], "twist": torso_twist})
    spine = g("spine") or []
    for i, b in enumerate(spine):
        w = (i + 1) / len(spine)
        entries.append({"bone": b, "mode": "frame", "dir": ["mid_hip", "mid_shoulder"],
                        "twist": [["right_hip", "left_hip", round(1 - w, 3)],
                                  ["right_shoulder", "left_shoulder", round(w, 3)]]})
    if g("neck"):
        entries.append({"bone": g("neck"), "mode": "swing", "dir": ["mid_shoulder", "mid_ear"]})
    if g("head"):
        entries.append({"bone": g("head"), "mode": "frame", "dir": ["mid_ear", "nose"], "twist": [["right_ear", "left_ear", 1.0]]})
    for s, lr in (("L", "left"), ("R", "right")):
        if g("upperarm", s):
            entries.append({"bone": g("upperarm", s), "mode": "limb", "dir": [f"{lr}_shoulder", f"{lr}_elbow"],
                            "pole": [f"{lr}_elbow", f"{lr}_wrist"], "pole_rest": C.vec(fwd)})
        if g("forearm", s):
            entries.append({"bone": g("forearm", s), "mode": "swing", "dir": [f"{lr}_elbow", f"{lr}_wrist"]})
        if g("hand", s):
            entries.append({"bone": g("hand", s), "mode": "swing", "dir": [f"{lr}_wrist", f"{lr}_hand"]})
        if g("thigh", s):
            entries.append({"bone": g("thigh", s), "mode": "limb", "dir": [f"{lr}_hip", f"{lr}_knee"],
                            "pole": [f"{lr}_knee", f"{lr}_ankle"], "pole_rest": C.vec(-fwd)})
        if g("shin", s):
            entries.append({"bone": g("shin", s), "mode": "swing", "dir": [f"{lr}_knee", f"{lr}_ankle"]})
        if g("foot", s):
            entries.append({"bone": g("foot", s), "mode": "swing", "dir": [f"{lr}_ankle", f"{lr}_toe"]})

    return {
        "armature": arm.name,
        "root": {"bone": hips or (spine[0] if spine else None)},
        "joints": joints,
        "bones": entries,
        "missing": missing,
        "rig_axes": {"side_left": C.vec(side), "up": C.vec(up), "forward": C.vec(fwd)},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--rig-out", required=True)
    ap.add_argument("--map-out", required=True)
    ap.add_argument("--armature", default=None)
    a = ap.parse_args(C.script_args())

    C.load_model(a.model)
    arm = C.find_armature(a.armature)
    order = C.bones_in_order(arm)
    meshes = [o.name for o in arm.children_recursive if o.type == "MESH"]
    rig = {
        "model": os.path.abspath(a.model),
        "armature": arm.name,
        "armatures_in_file": [o.name for o in C.bpy.data.objects if o.type == "ARMATURE"],
        "matrix_world": [C.vec(r) for r in arm.matrix_world],
        "meshes": meshes,
        "bone_count": len(order),
        "bones": [
            {
                "name": b.name,
                "parent": b.parent.name if b.parent else None,
                "depth": len(b.parent_recursive),
                "head": C.vec(b.head_local),
                "tail": C.vec(b.tail_local),
                "length": round(b.length, 5),
                "connected": b.use_connect,
                "deform": b.use_deform,
            }
            for b in order
        ],
    }
    C.save_json(a.rig_out, rig)
    mapping = build_mapping(arm, guess_roles(arm, order))
    C.save_json(a.map_out, mapping)
    print(f"Armature '{arm.name}': {len(order)} bones, meshes={meshes}")
    print(f"Mapped {len(mapping['bones'])} bones; missing roles: {mapping['missing']}")


main()
