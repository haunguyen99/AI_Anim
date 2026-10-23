"""Shared helpers for the Blender-side scripts (run inside Blender's Python)."""
import json
import os
import sys

import bpy
from mathutils import Matrix, Vector

# Landmarks that are not in MediaPipe's 33 but are derived from them.
VIRTUAL = {
    "mid_hip": ["left_hip", "right_hip"],
    "mid_shoulder": ["left_shoulder", "right_shoulder"],
    "mid_ear": ["left_ear", "right_ear"],
    "left_hand": ["left_index", "left_pinky"],
    "right_hand": ["right_index", "right_pinky"],
    "left_toe": ["left_foot_index"],
    "right_toe": ["right_foot_index"],
}


def script_args():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


def load_model(path):
    """Open .blend, or import .fbx/.glb/.gltf/.bvh into an empty scene."""
    path = os.path.abspath(path)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".blend":
        bpy.ops.wm.open_mainfile(filepath=path)
        return
    bpy.ops.wm.read_homefile(use_empty=True)
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False)
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".bvh":
        bpy.ops.import_anim.bvh(filepath=path)
    else:
        raise SystemExit(f"Unsupported model format: {ext}")
    relink_images(os.path.dirname(path))


def relink_images(model_dir):
    """FBX files often point at textures on another machine/folder. Look for each
    missing image by file name in the model's asset folder (up to two levels up)."""
    roots = [model_dir, os.path.dirname(model_dir), os.path.dirname(os.path.dirname(model_dir))]
    for img in bpy.data.images:
        if img.source != "FILE" or (img.filepath and os.path.exists(bpy.path.abspath(img.filepath))):
            continue
        name = os.path.basename(img.filepath.replace("\\", "/"))
        if not name:
            continue
        for root in roots:
            hit = None
            for dirpath, _, files in os.walk(root):
                low = {f.lower(): f for f in files}
                if name.lower() in low:
                    hit = os.path.join(dirpath, low[name.lower()])
                    break
            if hit:
                img.filepath = hit
                img.reload()
                print(f"Relinked texture {name} -> {hit}")
                break


def find_armature(name=None):
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if name:
        for o in arms:
            if o.name == name:
                return o
        raise SystemExit(f"Armature '{name}' not found. Available: {[o.name for o in arms]}")
    if not arms:
        raise SystemExit("No armature found in the model.")
    return max(arms, key=lambda o: len(o.data.bones))


def bones_in_order(arm):
    """Bones parents-first (depth-first from each root)."""
    out = []

    def visit(b):
        out.append(b)
        for c in b.children:
            visit(c)

    for b in arm.data.bones:
        if b.parent is None:
            visit(b)
    return out


def vec(v):
    return [round(float(x), 5) for x in v]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=1)


def resolve_rest_points(arm, mapping):
    """Armature-space rest position for every joint named in mapping['joints'],
    plus virtual landmarks that can be derived from them."""
    bones = arm.data.bones
    pts = {}
    for name, spec in mapping.get("joints", {}).items():
        if "pos" in spec:
            pts[name] = Vector(spec["pos"])
        else:
            b = bones.get(spec["bone"])
            if b is None:
                raise SystemExit(f"Joint '{name}': bone '{spec['bone']}' not in armature")
            pts[name] = (b.tail_local if spec.get("end", "head") == "tail" else b.head_local).copy()
    for name, parts in VIRTUAL.items():
        if name not in pts and all(p in pts for p in parts):
            pts[name] = sum((pts[p] for p in parts), Vector()) / len(parts)
    return pts


def rig_axes(rest):
    """(side, up, forward) unit vectors of the rig in armature space.
    side points to the character's left, forward to where it faces."""
    side = (rest["left_hip"] - rest["right_hip"]).normalized()
    up = rest["mid_shoulder"] - rest["mid_hip"]
    up = (up - side * up.dot(side)).normalized()
    forward = side.cross(up).normalized()
    return side, up, forward
