"""Inventory of a rig for step 2 (analysis): which bones are body chains and which are secondary
(cloth, hair, tail, ears, cape, accessories), and which mesh pieces each one moves.

exec in Blender (MCP). Set ARM / MESHES before exec, or the first armature and its skinned meshes are used.
Prints:
  1. bone tree with a class per bone: body (spine/neck/head/arms/legs/fingers), extra (anything else), prop;
  2. extra chains: root bone, length in bones, world head/tail, vertex region they weigh (bbox, vertex count);
  3. mesh islands (loose parts): vertex count, bbox, top-weighted bones -> rigid accessory vs skinned part.
Reading guide: a chain of 2+ extra bones = something that needs overlap/follow-through (hair, tail, cape, ears);
a single extra bone with rigid weights = a flap or hanging accessory (one rotation per key, lag + gravity);
a mesh island weighted 100% to one body bone = rigid armour/ornament (check it does not intersect when that joint bends).
"""
import collections
import re

import bmesh
import bpy

BODY = re.compile(r"(root|Root|Spine|Chest|Neck|Head|Scapula|Shoulder|Elbow|Wrist|Finger|Hip|Knee|Ankle|Toes)", re.I)
PROP = re.compile(r"(weapon|prop|sword|shield|mace)", re.I)

arm = globals().get("ARM") or next(o for o in bpy.data.objects if o.type == "ARMATURE" and any(
    m.type == "ARMATURE" and m.object == o for ob in bpy.data.objects if ob.type == "MESH" for m in ob.modifiers))
meshes = globals().get("MESHES") or [o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" and m.object == arm for m in o.modifiers)]
mw = arm.matrix_world


def cls(b):
    if PROP.search(b.name):
        return "prop?"
    return "body" if BODY.search(b.name) else "EXTRA"


print(f"== armature {arm.name}: {len(arm.data.bones)} bones; meshes {[m.name for m in meshes]}")
extra_roots = []
for b in arm.data.bones:
    c = cls(b)
    if c != "body" and (b.parent is None or cls(b.parent) == "body"):
        extra_roots.append(b)


def chain(b):
    out = [b]
    while len(b.children) == 1:
        b = b.children[0]
        out.append(b)
    return out, len(b.children)


regions = collections.defaultdict(list)
for ob in meshes:
    me = ob.data
    names = {g.index: g.name for g in ob.vertex_groups}
    for v in me.vertices:
        for g in v.groups:
            if g.weight > 0.05:
                regions[names[g.group]].append((ob.matrix_world @ v.co, g.weight))

print("== extra / prop chains")
for r in extra_roots:
    ch, branches = chain(r)
    h, t = mw @ ch[0].head_local, mw @ ch[-1].tail_local
    pts = [p for b in ch for p in regions.get(b.name, [])]
    reg = ""
    if pts:
        xs, ys, zs = zip(*[(p.x, p.y, p.z) for p, _ in pts])
        rigid = sum(1 for _, w in pts if w > 0.95)
        reg = f"verts {len(pts)} (rigid {rigid}) x {min(xs):.2f}..{max(xs):.2f} y {min(ys):.2f}..{max(ys):.2f} z {min(zs):.2f}..{max(zs):.2f}"
    print(f"{cls(r):5s} {r.name} parent={r.parent.name if r.parent else None} bones={len(ch)}{'+branches' if branches else ''} "
          f"head=({h.x:.2f},{h.y:.2f},{h.z:.2f}) tail=({t.x:.2f},{t.y:.2f},{t.z:.2f}) {reg or 'no verts'}")

print("== mesh islands")
for ob in meshes:
    me = ob.data
    names = {g.index: g.name for g in ob.vertex_groups}
    bm = bmesh.new()
    bm.from_mesh(me)
    seen = set()
    for v in bm.verts:
        if v.index in seen:
            continue
        st, isl = [v], []
        seen.add(v.index)
        while st:
            x = st.pop()
            isl.append(x.index)
            for e in x.link_edges:
                o = e.other_vert(x)
                if o.index not in seen:
                    seen.add(o.index)
                    st.append(o)
        w = collections.Counter()
        for i in isl:
            for g in me.vertices[i].groups:
                w[names.get(g.group, "?")] += g.weight
        tot = sum(w.values()) or 1
        co = [ob.matrix_world @ me.vertices[i].co for i in isl]
        bb = " ".join(f"{a}:{min(getattr(c, a) for c in co):.2f}..{max(getattr(c, a) for c in co):.2f}" for a in "xyz")
        top = ", ".join(f"{k}:{n / tot:.2f}" for k, n in w.most_common(3))
        print(f"{ob.name} island {len(isl)} verts {bb} | {top}")
    bm.free()
