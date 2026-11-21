"""MushroomBlast: one mushroom-cloud mesh made from metaballs (Blender 4.3, run inside Blender / via MCP).

Art lead 2026-11-04: "dùng mcp blender tạo 1 mesh hình nấm thay vì dùng nhiều khối sphere".
Stem (stacked balls) + cap (puffy ring, rolled-down rim, top dome) + ground skirt; metaballs merge into one billowy surface.
-> mesh, small cloud-noise lumps, decimate to ~3000 tris, smooth, pivot at the ground centre,
   cylindrical UV (u = angle around the up axis x2, v = height) so the erosion mask leaves vertical strands.
Export: Assets/VFX/MushroomBlast/Mesh/SM_MushroomBlast_Cloud.fbx (Y up, baked transform, metres).
"""
import bpy, bmesh, math, random, os

OUT = r"D:\Game_prj\VFX_LIb\Assets\VFX\MushroomBlast\Mesh\SM_MushroomBlast_Cloud.fbx"
random.seed(7)

coll = bpy.data.collections.get("MushroomBlast") or bpy.data.collections.new("MushroomBlast")
if coll.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(coll)
mb = bpy.data.metaballs.get("MB_Mushroom") or bpy.data.metaballs.new("MB_Mushroom")
mb.resolution = mb.render_resolution = 0.06
mb.threshold = 0.6
mb.elements.clear()
src = bpy.data.objects.get("MB_Mushroom") or bpy.data.objects.new("MB_Mushroom", mb)
if src.name not in coll.objects:
    coll.objects.link(src)


def ball(x, y, z, r):
    e = mb.elements.new()
    e.co = (x, y, z)
    e.radius = r


for i in range(7):                                   # stem
    z = 0.3 + i * 0.27
    r = 0.72 - i * 0.03
    a = random.uniform(0, 6.28)
    ball(0.08 * math.cos(a), 0.08 * math.sin(a), z, r)
    for k in range(3):
        a2 = a + k * 2.09
        ball(0.32 * math.cos(a2), 0.32 * math.sin(a2), z + random.uniform(-0.1, 0.1), r * 0.72)
for k in range(10):                                  # cap ring + rolled rim
    a = k / 10 * 6.283 + random.uniform(-0.15, 0.15)
    rr = random.uniform(0.95, 1.15)
    ball(rr * math.cos(a), rr * math.sin(a), 2.3 + random.uniform(-0.1, 0.15), random.uniform(0.62, 0.78))
    ball(1.25 * math.cos(a + 0.3), 1.25 * math.sin(a + 0.3), 2.0 + random.uniform(-0.05, 0.05), random.uniform(0.42, 0.52))
for k in range(5):                                   # cap dome
    a = k / 5 * 6.283 + 0.4
    ball(0.5 * math.cos(a), 0.5 * math.sin(a), 2.75 + random.uniform(0, 0.15), random.uniform(0.65, 0.8))
ball(0, 0, 2.95, 0.8)
for k in range(16):                                  # ground skirt
    a = k / 16 * 6.283 + random.uniform(-0.08, 0.08)
    rr = random.uniform(0.95, 1.2)
    ball(rr * math.cos(a), rr * math.sin(a), 0.15, random.uniform(0.5, 0.62))
for k in range(8):
    a = k / 8 * 6.283 + 0.2
    ball(0.6 * math.cos(a), 0.6 * math.sin(a), 0.2, 0.55)

dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(src.evaluated_get(dg))
old = bpy.data.objects.get("SM_MushroomBlast_Cloud")
if old:
    bpy.data.objects.remove(old, do_unlink=True)
ob = bpy.data.objects.new("SM_MushroomBlast_Cloud", me)
coll.objects.link(ob)
src.hide_set(True)

tex = bpy.data.textures.get("MB_Lumps") or bpy.data.textures.new("MB_Lumps", "CLOUDS")
tex.noise_scale = 0.35
tex.noise_depth = 1
d = ob.modifiers.new("Lumps", "DISPLACE")
d.texture = tex
d.strength = 0.12
d.mid_level = 0.5
tris = sum(len(p.vertices) - 2 for p in me.polygons)
dec = ob.modifiers.new("Decimate", "DECIMATE")
dec.ratio = min(1.0, 3000 / tris)
for o in bpy.context.selected_objects:
    o.select_set(False)
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.ops.object.modifier_apply(modifier="Lumps")
bpy.ops.object.modifier_apply(modifier="Decimate")
bpy.ops.object.shade_smooth()

me = ob.data
bm = bmesh.new()
bm.from_mesh(me)
zmin = min(v.co.z for v in bm.verts)
for v in bm.verts:
    v.co.z -= zmin + 0.05                            # base just under the ground, pivot at the ground centre
H = max(v.co.z for v in bm.verts)
uvl = bm.loops.layers.uv.verify()
for f in bm.faces:
    us = [(math.atan2(l.vert.co.y, l.vert.co.x) / (2 * math.pi) + 0.5) * 2.0 for l in f.loops]
    if max(us) - min(us) > 1.0:                      # face across the seam
        us = [u + 2.0 if u < 1.0 else u for u in us]
    for l, u in zip(f.loops, us):
        l[uvl].uv = (u, l.vert.co.z / H)
bm.to_mesh(me)
bm.free()
me.update()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={'MESH'}, apply_scale_options='FBX_SCALE_ALL',
                         axis_forward='-Z', axis_up='Y', bake_space_transform=True, mesh_smooth_type='FACE',
                         use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False)
print(OUT, "tris", sum(len(p.vertices) - 2 for p in me.polygons), "height", round(H, 2))
