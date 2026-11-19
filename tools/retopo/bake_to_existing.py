"""Bake màu từ mesh gốc (hi) + texture sang một mesh retopo CÓ SẴN (vd bản từ Tripo / artist), giữ UV của nó.
Tự tìm góc xoay quanh trục đứng (0/90/180/270) cho khớp mesh gốc, căn tâm + chân, đo độ lệch, xuất FBX cho Frolvy.
  blender -b --python bake_to_existing.py -- --hi <fbx/glb> --lo <fbx/glb> --tex <albedo> --out <thư mục> --name <tên> [--res 1024] [--gs 0.01]
"""
import bpy, os, sys, math, json, argparse
from mathutils import Matrix, Vector, bvhtree
ap = argparse.ArgumentParser()
for k in ("hi", "lo", "tex", "out", "name"): ap.add_argument("--" + k, required=True)
ap.add_argument("--res", type=int, default=1024); ap.add_argument("--gs", type=float, default=0.01)
A = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
os.makedirs(A.out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def load(p):
    before = set(bpy.data.objects)
    (bpy.ops.import_scene.gltf if p.lower().endswith((".glb", ".gltf")) else bpy.ops.import_scene.fbx)(filepath=p)
    ms = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    for o in bpy.data.objects: o.select_set(o in ms)
    bpy.context.view_layer.objects.active = ms[0]
    if len(ms) > 1: bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o
hi = load(A.hi); hi.name = "hi"
lo = load(A.lo); lo.name = "lo"
H = max(hi.dimensions)
cen = lambda o: Vector((sum(v.co.x for v in o.data.vertices) / len(o.data.vertices), sum(v.co.y for v in o.data.vertices) / len(o.data.vertices), min(v.co.z for v in o.data.vertices)))
CH = cen(hi)
dg = bpy.context.evaluated_depsgraph_get(); tree = bvhtree.BVHTree.FromObject(hi, dg)
base = [v.co.copy() for v in lo.data.vertices]
def place(ang):
    R = Matrix.Rotation(math.radians(ang), 3, 'Z')
    pts = [R @ c for c in base]
    c = Vector((sum(p.x for p in pts) / len(pts), sum(p.y for p in pts) / len(pts), min(p.z for p in pts)))
    return [p - c + CH for p in pts]
best = None
for ang in (0, 90, 180, 270):
    pts = place(ang)
    d = sorted(tree.find_nearest(p)[3] for p in pts[::3])
    m = sum(d) / len(d)
    print("DBG angle", ang, "mean %.3f%%" % (100 * m / H))
    if best is None or m < best[0]: best = (m, ang)
ang = best[1]
for v, p in zip(lo.data.vertices, place(ang)): v.co = p
lo.data.update()
d = sorted(tree.find_nearest(v.co)[3] for v in lo.data.vertices)
dev = {"angle": ang, "mean_pct": round(100 * sum(d) / len(d) / H, 3), "p99_pct": round(100 * d[int(len(d) * .99)] / H, 3), "max_pct": round(100 * d[-1] / H, 3)}
print("DBG chosen", dev)
# vật liệu hi (albedo gốc) + bake sang UV của lo
mh = bpy.data.materials.new("hi_mat"); mh.use_nodes = True; nt = mh.node_tree
for n in list(nt.nodes):
    if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
bs = nt.nodes.new("ShaderNodeBsdfPrincipled"); nt.links.new(bs.outputs[0], out.inputs[0])
tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = bpy.data.images.load(A.tex); nt.links.new(tn.outputs[0], bs.inputs['Base Color'])
hi.data.materials.clear(); hi.data.materials.append(mh)
ml = bpy.data.materials.new("lo_mat"); ml.use_nodes = True; lt = ml.node_tree
node = lt.nodes.new("ShaderNodeTexImage"); lo.data.materials.clear(); lo.data.materials.append(ml)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24
b = sc.render.bake; b.use_selected_to_active = True; b.cage_extrusion = 0.03 * H; b.max_ray_distance = 0.08 * H
b.margin = 10; b.margin_type = 'EXTEND'; b.use_pass_direct = False; b.use_pass_indirect = False; b.use_pass_color = True
for o in bpy.data.objects: o.select_set(False)
hi.select_set(True); lo.select_set(True); bpy.context.view_layer.objects.active = lo
im = bpy.data.images.new(A.name + "_albedo", A.res, A.res, alpha=False); im.colorspace_settings.name = "sRGB"
node.image = im; lt.nodes.active = node
bpy.ops.object.bake(type='DIFFUSE')
png = os.path.join(A.out, A.name + "_albedo.png"); im.filepath_raw = png; im.file_format = 'PNG'; im.save()
import numpy as np
w, h = im.size; px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1].copy()
im2 = bpy.data.images.new(A.name + "_vf", w, h, alpha=False); im2.pixels.foreach_set(px.ravel()); im2.update()
flip = os.path.join(A.out, A.name + "_albedo_vflip.png"); im2.filepath_raw = flip; im2.file_format = 'PNG'; im2.save()
for o in bpy.data.objects: o.select_set(False)
lo.name = A.name; lo.select_set(True); bpy.context.view_layer.objects.active = lo
fbx = os.path.join(A.out, A.name + ".fbx")
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, axis_forward='-Z', axis_up='Y', apply_unit_scale=False, global_scale=A.gs,
                         bake_space_transform=True, mesh_smooth_type='FACE', add_leaf_bones=False, object_types={'MESH'}, path_mode='STRIP')
print("DBG DONE", json.dumps({"fbx": fbx, "albedo": png, "albedo_vflip": flip, "deviation": dev}))
