bl_info = {
    "name": "AI Retopo",
    "author": "AI Animation",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar (N) > AI Retopo",
    "description": "Chọn mesh, bấm Retopo: đo, dựng lưới quad theo role, bake texture, nhập bản mới '<tên>_retopo'",
    "category": "Mesh",
}
import bpy, os, json, subprocess, tempfile

REPO_SCRIPT = "/media/haunv/ổ d/AI Animation/tools/retopo/blender_retopo.py"
ROLES = [("hero", "Hero (6000 quad)", ""), ("npc", "NPC (3000 quad)", ""), ("light", "Light (1200 quad)", ""), ("prop", "Prop (1500 quad)", "")]


class AIR_Prefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    script: bpy.props.StringProperty(name="blender_retopo.py", subtype='FILE_PATH', default=REPO_SCRIPT)

    def draw(self, ctx):
        self.layout.prop(self, "script")


def _script():
    try:
        p = bpy.context.preferences.addons[__name__].preferences.script
    except Exception:
        p = ""
    for c in (p, os.path.join(os.path.dirname(__file__), "blender_retopo.py"), REPO_SCRIPT):
        if c and os.path.exists(c):
            return c
    raise RuntimeError("không thấy blender_retopo.py (đặt đường dẫn trong Preferences > Add-ons > AI Retopo)")


def build_cmd(obj_path, out, name, role, faces, tex, check):
    cmd = [bpy.app.binary_path, "-b", "--python", _script(), "--", "--in", obj_path, "--out", out, "--name", name, "--role", role]
    if faces: cmd += ["--faces", str(faces)]
    if tex: cmd += ["--tex", bpy.path.abspath(tex)]
    if check: cmd += ["--check-only"]
    return cmd


def parse(stdout):
    for line in stdout.splitlines():
        if line.startswith("AI_RETOPO_REPORT "):
            return json.loads(line[len("AI_RETOPO_REPORT "):])
    return None


def export_obj(obj, path):
    for o in bpy.context.view_layer.objects: o.select_set(False)
    obj.select_set(True); bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.obj_export(filepath=path, export_selected_objects=True, forward_axis='NEGATIVE_Z', up_axis='Y', export_materials=False, apply_modifiers=True)


def import_result(rep, src):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=rep["obj"], forward_axis='NEGATIVE_Z', up_axis='Y')
    new = [o for o in bpy.data.objects if o not in before]
    if not new: return None
    o = new[0]; o.name = src.name + "_retopo"
    for x in bpy.context.view_layer.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)    # importer để lại xoay 90°: nướng vào mesh
    flip = (rep.get("bake") or {})
    albedo = flip.get("albedo") if isinstance(flip, dict) else None
    if albedo and os.path.exists(albedo):               # bản không lật V: Blender dùng đúng ảnh này
        m = bpy.data.materials.new(o.name); m.use_nodes = True
        t = m.node_tree.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(albedo)
        m.node_tree.links.new(t.outputs[0], m.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
        o.data.materials.append(m)
    src.hide_set(True)
    return o


def summary(rep):
    b = rep["before"]; L = ["%d tam giác, %.0f%% quad" % (b["tri_equiv"], b["quad_pct"])] + rep["verdict_before"]
    if "after" in rep:
        a = rep["after"]; L += ["-> %d tam giác (%d quad)" % (a["tri_equiv"], a["quads"]),
                                "lệch %.2f%% (tệ nhất %.2f%%)" % (rep["deviation_mean_pct"], rep["deviation_p99_pct"])] + rep["verdict_after"]
    return L


class AIR_OT_run(bpy.types.Operator):
    bl_idname = "mesh.ai_retopo"
    bl_label = "AI Retopo"
    check_only: bpy.props.BoolProperty(default=False)
    _proc = None; _timer = None; _src = None; _dir = None

    def execute(self, ctx):
        src = ctx.active_object
        if not src or src.type != 'MESH':
            self.report({'ERROR'}, "Chọn một mesh trước"); return {'CANCELLED'}
        s = ctx.scene.ai_retopo
        self._src = src; self._dir = tempfile.mkdtemp(prefix="ai_retopo_")
        op = os.path.join(self._dir, src.name + ".obj"); export_obj(src, op)
        cmd = build_cmd(op, self._dir, src.name, s.role, s.faces, s.tex, self.check_only)
        self._proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.report({'INFO'}, "AI Retopo: Blender nền đang chạy (20-60 giây)...")
        self._timer = ctx.window_manager.event_timer_add(1.0, window=ctx.window)
        ctx.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, ctx, event):
        if event.type != 'TIMER' or self._proc.poll() is None:
            return {'PASS_THROUGH'}
        ctx.window_manager.event_timer_remove(self._timer)
        rep = parse(self._proc.stdout.read())
        if not rep:
            self.report({'ERROR'}, "AI Retopo lỗi (xem Window > Toggle System Console)"); return {'CANCELLED'}
        if not self.check_only:
            import_result(rep, self._src)
        ctx.scene.ai_retopo.last = " | ".join(summary(rep))
        for l in summary(rep): self.report({'INFO'}, l)
        return {'FINISHED'}


class AIR_Settings(bpy.types.PropertyGroup):
    role: bpy.props.EnumProperty(name="Role", items=ROLES, default="hero")
    faces: bpy.props.IntProperty(name="Quad (0 = theo role)", default=0, min=0, max=100000)
    tex: bpy.props.StringProperty(name="Texture albedo", subtype='FILE_PATH', description="Ảnh albedo của mesh gốc (bỏ trống nếu không bake)")
    last: bpy.props.StringProperty()


class AIR_PT_panel(bpy.types.Panel):
    bl_label = "AI Retopo"; bl_idname = "AIR_PT_panel"; bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = "AI Retopo"

    def draw(self, ctx):
        s = ctx.scene.ai_retopo; l = self.layout
        l.prop(s, "role"); l.prop(s, "faces"); l.prop(s, "tex")
        r = l.row(); r.operator("mesh.ai_retopo", text="Check (chỉ đo)").check_only = True
        r.operator("mesh.ai_retopo", text="Retopo").check_only = False
        for part in s.last.split(" | ") if s.last else []:
            l.label(text=part)


CLASSES = (AIR_Prefs, AIR_Settings, AIR_OT_run, AIR_PT_panel)

def register():
    for c in CLASSES: bpy.utils.register_class(c)
    bpy.types.Scene.ai_retopo = bpy.props.PointerProperty(type=AIR_Settings)

def unregister():
    del bpy.types.Scene.ai_retopo
    for c in reversed(CLASSES): bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
