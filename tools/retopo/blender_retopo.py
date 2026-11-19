"""AI Retopo - phần chạy trong Blender nền (không mở giao diện).

Gọi qua tools/retopo/ai_retopo.py (đừng gọi tay). Tham số đứng sau "--":
  --in <file>   obj / fbx / glb / gltf         --out <thư mục>      --name <tên>
  --role hero|npc|light|prop | --faces <số quad>   --tex <ảnh albedo> (tuỳ chọn)
  --res 1024  --smooth 25  --symmetry auto|on|off  --gs 0.01  --normal 0|1  --check-only
Các bước: đọc + đo (tam giác, quad, lỗ, đối xứng) → voxel remesh → làm mịn Taubin →
Quadriflow (có đối xứng X nếu mesh đối xứng) → UV mới → bake albedo → xuất FBX → báo cáo JSON.
Trục: Y lên, mặt +Z (giống Frolvy); chia cỡ theo chiều cao nên không phụ thuộc đơn vị.
"""
import bpy, bmesh, os, sys, json, math, time, argparse
import numpy as np
from mathutils import Vector, kdtree, bvhtree

ROLES = {"hero": 6000, "npc": 3000, "light": 1200, "prop": 1500}   # số quad (x2 = tam giác), theo docs/retopology_cho_rig.md mục 4

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="src", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--name", default="")
ap.add_argument("--role", default="hero")
ap.add_argument("--faces", type=int, default=0)
ap.add_argument("--pick", default="", help="chỉ lấy mesh có tên này (file từ scene nhiều mesh)")
ap.add_argument("--tex", default="")
ap.add_argument("--res", type=int, default=1024)
ap.add_argument("--smooth", type=int, default=25)
ap.add_argument("--vox", type=float, default=0.0, help="cạnh voxel theo tỉ lệ chiều cao (0 = tự chọn)")
ap.add_argument("--symmetry", default="auto")
ap.add_argument("--gs", type=float, default=0.01)
ap.add_argument("--normal", type=int, default=0)
ap.add_argument("--check-only", action="store_true")
A = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
t0 = time.time()
def log(*a): print("[%.0fs]" % (time.time() - t0), *a, flush=True)
os.makedirs(A.out, exist_ok=True)
NAME = A.name or os.path.splitext(os.path.basename(A.src))[0]

# ── đọc file ────────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
ext = os.path.splitext(A.src)[1].lower()
if ext == ".obj":
    bpy.ops.wm.obj_import(filepath=A.src, forward_axis='NEGATIVE_Z', up_axis='Y')
elif ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=A.src)
elif ext in (".glb", ".gltf"):
    bpy.ops.import_scene.gltf(filepath=A.src)
else:
    raise SystemExit("định dạng chưa hỗ trợ: " + ext)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
if A.pick:
    sel = [o for o in meshes if o.name == A.pick or o.name.startswith(A.pick)] or [o for o in meshes if A.pick in o.name]
    meshes = sel or meshes
if not meshes:
    raise SystemExit("file không có mesh")
for o in bpy.data.objects: o.select_set(o in meshes)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()                      # nhiều mảnh -> một khối để remesh
hi = bpy.context.view_layer.objects.active
hi.name = "hi"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = hi.data
# Blender dùng Z lên nội bộ (importer đã đổi); chiều cao = bề rộng theo Z
ys = [v.co.z for v in me.vertices]; H = max(ys) - min(ys)
H = H if H > 0 else max(hi.dimensions)

# ── đo ─────────────────────────────────────────────────────────────────
def measure(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6 * max(obj.dimensions))   # glTF / UV tách đỉnh ở đường cắt UV: hàn lại để đo đúng
    nq = sum(1 for f in bm.faces if len(f.verts) == 4)
    nt = sum(1 for f in bm.faces if len(f.verts) == 3)
    ng = sum(1 for f in bm.faces if len(f.verts) > 4)
    tri_eq = sum(len(f.verts) - 2 for f in bm.faces)
    holes = sum(1 for e in bm.edges if len(e.link_faces) == 1)
    nonman = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    poles = sum(1 for v in bm.verts if len(v.link_edges) in (3, 5) and not v.is_boundary)
    big = sum(1 for v in bm.verts if len(v.link_edges) > 5 and not v.is_boundary)
    lens = [e.calc_length() for e in bm.edges]
    mean = sum(lens) / max(1, len(lens))
    cv = (sum((l - mean) ** 2 for l in lens) / max(1, len(lens))) ** 0.5 / mean if mean else 0
    nv = len(bm.verts); bm.free()
    return {"faces": nq + nt + ng, "quads": nq, "tris": nt, "ngons": ng, "tri_equiv": tri_eq,
            "quad_pct": round(100.0 * nq / max(1, nq + nt + ng), 1), "open_edges": holes, "nonmanifold_edges": nonman,
            "poles_3_5": poles, "poles_6plus": big, "edge_len_cv": round(cv, 3), "verts": nv}

def symmetry_score(obj):
    """% chiều cao: khoảng cách TB từ đỉnh lật qua X tới đỉnh gần nhất (nhỏ = đối xứng). Cũng cho biết tâm X."""
    vs = [v.co for v in obj.data.vertices]
    step = max(1, len(vs) // 4000)
    kd = kdtree.KDTree(len(vs))
    for i, c in enumerate(vs): kd.insert(c, i)
    kd.balance()
    cx = (max(c.x for c in vs) + min(c.x for c in vs)) / 2
    tot = n = 0
    for c in vs[::step]:
        m = Vector((2 * cx - c.x, c.y, c.z)); tot += kd.find(m)[2]; n += 1
    return 100.0 * (tot / max(1, n)) / H, cx

before = measure(hi)
sym_pct, cx = symmetry_score(hi)
log("đo:", before, "đối xứng lệch %.2f%% cao, tâm X %.4f" % (sym_pct, cx))
verdict = []
if before["quad_pct"] < 80: verdict.append("lưới tam giác lộn xộn (%.0f%% quad): cần retopo" % before["quad_pct"])
if before["tri_equiv"] > 40000: verdict.append("%d tam giác: nặng cho game mobile" % before["tri_equiv"])
if before["open_edges"]: verdict.append("%d cạnh hở (lỗ / mảnh rời)" % before["open_edges"])
if before["nonmanifold_edges"]: verdict.append("%d cạnh non-manifold" % before["nonmanifold_edges"])
if before["poles_6plus"]: verdict.append("%d đỉnh ≥6 cạnh" % before["poles_6plus"])
report = {"name": NAME, "source": A.src, "height": H, "before": before, "symmetry_pct": round(sym_pct, 3),
          "center_x": cx, "verdict_before": verdict or ["đạt, không cần retopo"]}
if A.check_only:
    json.dump(report, open(os.path.join(A.out, NAME + "_check.json"), "w"), ensure_ascii=False, indent=1)
    print("AI_RETOPO_REPORT " + json.dumps(report, ensure_ascii=False)); sys.exit(0)

# ── retopo ─────────────────────────────────────────────────────────────
target = A.faces or ROLES.get(A.role, ROLES["hero"])
vox = (A.vox or 1.0 / 220.0) * H
def make_lo(vox, fallback=False):
    """Bản thấp: voxel remesh -> Taubin -> sửa đỉnh kẹp -> Quadriflow. Trả về (đối tượng, dùng_đối_xứng) hoặc None nếu Quadriflow từ chối."""
    for o in list(bpy.data.objects):
        if o.name.startswith("lo"): bpy.data.objects.remove(o, do_unlink=True)
    lo = hi.copy(); lo.data = hi.data.copy(); lo.name = "lo"
    bpy.context.collection.objects.link(lo)
    while lo.data.uv_layers: lo.data.uv_layers.remove(lo.data.uv_layers[0])
    for o in bpy.data.objects: o.select_set(o is lo)
    bpy.context.view_layer.objects.active = lo
    lo.data.remesh_voxel_size = vox
    bpy.ops.object.voxel_remesh()
    log("voxel remesh (cạnh %.4f):" % vox, len(lo.data.polygons))
    m2 = lo.data; n = len(m2.vertices)
    co = np.empty(n * 3); m2.vertices.foreach_get("co", co); co = co.reshape(n, 3)
    ed = np.empty(len(m2.edges) * 2, dtype=np.int64); m2.edges.foreach_get("vertices", ed); ed = ed.reshape(-1, 2)
    deg = np.bincount(ed.ravel(), minlength=n).astype(float); deg[deg == 0] = 1
    def lap(c):
        acc = np.zeros_like(c); np.add.at(acc, ed[:, 0], c[ed[:, 1]]); np.add.at(acc, ed[:, 1], c[ed[:, 0]])
        return acc / deg[:, None] - c
    for _ in range(A.smooth):                      # Taubin: bỏ nhiễu lông, không co thể tích
        co = co + 0.5 * lap(co); co = co - 0.53 * lap(co)
    m2.vertices.foreach_set("co", co.ravel()); m2.update()
    # Quadriflow đòi manifold + pháp tuyến nhất quán: sửa đỉnh kẹp (pinch) nếu có
    bm = bmesh.new(); bm.from_mesh(m2)
    bad = [v for v in bm.verts if not v.is_manifold]
    if bad:
        log("đỉnh kẹp / non-manifold:", len(bad), "-> xoá và vá lỗ")
        bmesh.ops.delete(bm, geom=bad, context='VERTS')
        edges = [e for e in bm.edges if len(e.link_faces) == 1]
        if edges: bmesh.ops.holes_fill(bm, edges=edges, sides=8)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(m2); bm.free(); m2.update()
    sym = A.symmetry == "on" or (A.symmetry == "auto" and sym_pct < 0.6 and abs(cx) < 0.01 * H)
    if sym:                                         # Quadriflow đối xứng theo X của vật: đưa tâm về x = 0 tạm thời
        lo.location.x -= cx; bpy.ops.object.transform_apply(location=True)
    n0 = len(lo.data.polygons)
    if fallback:
        return lo, False
    bpy.ops.object.quadriflow_remesh(mode='FACES', target_faces=target, use_mesh_symmetry=sym,
                                     use_preserve_sharp=False, use_preserve_boundary=False, smooth_normals=True, seed=1)
    if sym:
        lo.location.x += cx; bpy.ops.object.transform_apply(location=True)
    ok = len(lo.data.polygons) < 3 * target and len(lo.data.polygons) != n0
    return (lo, sym) if ok else None

res = None
for mult in (1.0, 0.85, 1.25, 0.7):                 # Quadriflow hay từ chối ở một cỡ voxel nhất định: thử vài cỡ
    res = make_lo(vox * mult)
    if res: break
    log("Quadriflow không chạy ở cỡ voxel x%.2f, thử cỡ khác" % mult)
fallback_used = False
if not res:                                         # Quadriflow từ chối: voxel remesh thẳng ở cỡ ra đúng số quad (toàn quad, không theo dòng chảy)
    bmx = bmesh.new(); bmx.from_mesh(hi.data); area = sum(f.calc_area() for f in bmx.faces); bmx.free()
    vox_fb = (area / target) ** 0.5
    log("Quadriflow từ chối mọi cỡ: dùng voxel quad dự phòng, cạnh %.4f" % vox_fb)
    lo, _ = make_lo(vox_fb, fallback=True)
    sh = lo.modifiers.new("snap", 'SHRINKWRAP'); sh.target = hi; sh.wrap_method = 'NEAREST_SURFACEPOINT'
    bpy.ops.object.modifier_apply(modifier=sh.name)
    res = (lo, False); fallback_used = True
lo, use_sym = res
after = measure(lo)
log("quadriflow: ", after, "đối xứng:", use_sym)

# độ lệch lo so với hi (% chiều cao): đỉnh lo -> điểm gần nhất trên hi
dg = bpy.context.evaluated_depsgraph_get()
tree = bvhtree.BVHTree.FromObject(hi, dg)
dev = []
for v in lo.data.vertices:
    loc, nrm, idx, d = tree.find_nearest(v.co)
    if d is not None: dev.append(d)
dev.sort()
dev_mean = 100.0 * sum(dev) / max(1, len(dev)) / H
dev_p99 = 100.0 * dev[int(len(dev) * 0.99)] / H if dev else 0
report.update({"fallback_voxel_quad": fallback_used, "after": after, "target_quads": target, "symmetry_used": use_sym,
               "deviation_mean_pct": round(dev_mean, 3), "deviation_p99_pct": round(dev_p99, 3)})

# ── UV + bake ──────────────────────────────────────────────────────────
for o in bpy.data.objects: o.select_set(False)
bpy.context.view_layer.objects.active = lo; lo.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004, area_weight=0.6, correct_aspect=True, scale_to_bounds=False)
bpy.ops.uv.pack_islands(margin=0.004)
bpy.ops.object.mode_set(mode='OBJECT')

alb_img = None
if A.tex and os.path.exists(A.tex) and hi.data.uv_layers:
    alb_img = bpy.data.images.load(A.tex)
else:
    for mat in hi.data.materials:
        if mat and mat.use_nodes:
            for nd in mat.node_tree.nodes:
                if nd.type == 'TEX_IMAGE' and nd.image: alb_img = nd.image; break
        if alb_img: break
baked = None
if alb_img and hi.data.uv_layers:
    log("bake texture", alb_img.name)
    if A.tex and os.path.exists(A.tex):          # vật liệu tạm cho hi
        mh = bpy.data.materials.new("hi_mat"); mh.use_nodes = True; nt = mh.node_tree
        for nd in list(nt.nodes):
            if nd.type != 'OUTPUT_MATERIAL': nt.nodes.remove(nd)
        out = [nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL'][0]
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); nt.links.new(bsdf.outputs[0], out.inputs[0])
        tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = alb_img; nt.links.new(tn.outputs[0], bsdf.inputs['Base Color'])
        hi.data.materials.clear(); hi.data.materials.append(mh)
    ml = bpy.data.materials.new("lo_mat"); ml.use_nodes = True; lt = ml.node_tree
    node = lt.nodes.new("ShaderNodeTexImage"); lo.data.materials.clear(); lo.data.materials.append(ml)
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24
    b = sc.render.bake; b.use_selected_to_active = True; b.cage_extrusion = 0.02 * H; b.max_ray_distance = 0.05 * H
    b.margin = 10; b.margin_type = 'EXTEND'; b.use_pass_direct = False; b.use_pass_indirect = False; b.use_pass_color = True
    for o in bpy.data.objects: o.select_set(False)
    hi.select_set(True); lo.select_set(True); bpy.context.view_layer.objects.active = lo
    im = bpy.data.images.new(NAME + "_albedo", A.res, A.res, alpha=False); im.colorspace_settings.name = "sRGB"
    node.image = im; lt.nodes.active = node
    bpy.ops.object.bake(type='DIFFUSE')
    p_png = os.path.join(A.out, NAME + "_albedo.png")
    im.filepath_raw = p_png; im.file_format = 'PNG'; im.save()
    # Frolvy lật V của UV: bản lật dọc dùng cho Frolvy, bản gốc cho Unity
    w, h = im.size; px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1].copy()
    im2 = bpy.data.images.new(NAME + "_albedo_vflip", w, h, alpha=False); im2.pixels.foreach_set(px.ravel()); im2.update()
    p_flip = os.path.join(A.out, NAME + "_albedo_vflip.png"); im2.filepath_raw = p_flip; im2.file_format = 'PNG'; im2.save()
    baked = {"albedo": p_png, "albedo_vflip_for_frolvy": p_flip}
else:
    log("không có texture nguồn: bỏ bake")
report["bake"] = baked or "bỏ qua (không có texture nguồn)"

# ── xuất ───────────────────────────────────────────────────────────────
for o in bpy.data.objects: o.select_set(False)
lo.name = NAME; lo.select_set(True); bpy.context.view_layer.objects.active = lo
fbx = os.path.join(A.out, NAME + "_retopo.fbx")
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, axis_forward='-Z', axis_up='Y', apply_unit_scale=False,
                         global_scale=A.gs, bake_space_transform=True, mesh_smooth_type='FACE', add_leaf_bones=False,
                         object_types={'MESH'}, path_mode='STRIP')
report["fbx"] = fbx
obj_out = os.path.join(A.out, NAME + "_retopo.obj")          # cho add-on Blender: cùng đơn vị, không qua FBX
bpy.ops.wm.obj_export(filepath=obj_out, export_selected_objects=True, forward_axis='NEGATIVE_Z', up_axis='Y', export_materials=False)
report["obj"] = obj_out
v2 = []
if after["quad_pct"] < 95: v2.append("còn %.0f%% quad" % after["quad_pct"])
if dev_p99 > 1.5: v2.append("lệch hình tới %.1f%% chiều cao ở vài chỗ (ngón, tai, đuôi mỏng?)" % dev_p99)
if after["tri_equiv"] > 15000: v2.append("%d tam giác: còn nặng" % after["tri_equiv"])
if fallback_used: v2.append("Quadriflow từ chối mesh này: dùng voxel quad dự phòng (toàn quad nhưng cạnh kém đều hơn)")
report["verdict_after"] = v2 or ["đạt về số liệu"]
report["note"] = ("Quadriflow cho lưới quad đều, KHÔNG theo xương và không có vòng mắt / miệng: dùng tạm; "
                  "vùng khớp, mặt, bàn tay cần retopo tay nếu anim kỹ (docs/retopology_cho_rig.md).")
report["seconds"] = round(time.time() - t0, 1)
json.dump(report, open(os.path.join(A.out, NAME + "_retopo_report.json"), "w"), ensure_ascii=False, indent=1)
print("AI_RETOPO_REPORT " + json.dumps(report, ensure_ascii=False))
