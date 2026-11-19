"""AI Retopo for Frolvy - chọn mesh, bấm một nút: đo, retopo, bake texture, nhập lại bản mới.

Menu Plugins -> AI Retopo (panel: Role, Quad override, Check / Retopo).
Từ MCP (execute_code):
    exec(open(r'<repo>/tools/frolvy_plugins/ai_retopo/ai_retopo.py', encoding='utf-8').read())
    check(api)                          # chỉ đo, báo bằng lời (không đổi scene)
    retopo(api, role='hero')            # hero 6000 quad | npc 3000 | light 1200 | prop 1500 ; faces=N để tự chọn
Bản mới vào scene tên '<mesh>_retopo' (bản gốc ẩn, không xoá); texture bake: file *_albedo_vflip.png (đã lật V cho Frolvy).
Việc nặng (Blender nền, 20-60 giây) chạy ở tiến trình riêng; Frolvy không đứng, kết quả báo ở log.
Lõi: tools/retopo/ai_retopo.py + blender_retopo.py (chạy được ngoài Frolvy bằng dòng lệnh).
"""
import json, os, shutil, subprocess, sys, tempfile

_HERE = os.path.dirname(os.path.abspath(globals().get("__file__", "."))) if "__file__" in globals() else os.getcwd()
_REPO_CORE = "/media/haunv/\u1ed5 d/AI Animation/tools/retopo/ai_retopo.py"      # ban cai trong Documents/Frolvy/plugins khong nam trong repo
_REL_CORE = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "retopo", "ai_retopo.py")
CORE = os.environ.get("AI_RETOPO_CORE") or (_REL_CORE if os.path.exists(_REL_CORE) else _REPO_CORE)
ROLE_LIST = ("hero", "npc", "light", "prop")


def _workdir():
    """Thu muc lam viec: khong dung /tmp (uu tien thu muc Documents)."""
    root = os.path.join(os.path.expanduser("~"), "Documents", "AnimationDCC", "retopo_work")
    try:
        os.makedirs(root, exist_ok=True)
        return tempfile.mkdtemp(prefix="job_", dir=root)
    except Exception:                       # Frolvy chan script cua AI ghi ngoai /tmp: dung /tmp (Blender da duoc cap quyen /tmp)
        return tempfile.mkdtemp(prefix="ai_retopo_")


def _obj_path(d, name):
    return os.path.join(d, name + ".obj")


def _write_obj(api, node, path):
    md = api.mesh_data(node)
    flat, sizes, corners = md["positions"], md["face_sizes"], md["face_corners"]
    pos = [flat[i:i + 3] for i in range(0, len(flat), 3)]      # positions: x y z de moi dinh, noi tiep nhau
    with open(path, "w") as f:
        for p in pos:
            f.write("v %.6f %.6f %.6f\n" % tuple(p))
        k = 0
        for s in sizes:
            f.write("f " + " ".join(str(corners[k + i] + 1) for i in range(s)) + "\n")
            k += s
    return max(p[1] for p in pos) - min(p[1] for p in pos), len(sizes)


def _write_src(api, node, d):
    """Xuat nguon co UV: export_scene glb (ca scene), Blender chi lay mesh `node` (--pick). Tra ve (duong_dan, cao, so_mat)."""
    md = api.mesh_data(node)
    ys = md["positions"][1::3]
    p = os.path.join(d, node + ".glb")
    if not api.export_scene(p, "glb", True) or not os.path.exists(p):
        raise RuntimeError("export_scene glb that bai")
    return p, max(ys) - min(ys), len(md["face_sizes"])


def _python():
    for c in ("python3", "python"):
        p = shutil.which(c)
        if p:
            return p
    raise RuntimeError("không tìm thấy python để chạy Blender")


def _target(api, mesh):
    if mesh:
        return mesh
    sel = [n for n in api.selection()]
    for n in sel:
        try:
            if api.mesh_data(n)["face_sizes"]:
                return n
        except Exception:
            pass
    raise ValueError("chọn một mesh trước (Pick the mesh in the outliner)")


def _say(rep):
    b = rep["before"]
    out = ["%s: %d tam giác, %.0f%% quad, đối xứng lệch %.2f%% cao" % (rep["name"], b["tri_equiv"], b["quad_pct"], rep["symmetry_pct"])]
    out += ["- " + v for v in rep["verdict_before"]]
    return out


def _run(args, done, log, api):
    proc = subprocess.Popen([_python(), "-I", CORE] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def poll():
        if proc.poll() is None:
            api.call_later(2.0, poll)
            return
        out = proc.stdout.read()
        done(proc.returncode, out)
    api.call_later(2.0, poll)


def check(api, mesh=None, log=None):
    log = log or api.log
    node = _target(api, mesh)
    d = _workdir()
    objp = _write_src(api, node, d)[0]
    log("AI Retopo: đang đo %s ..." % node)
    _run(["check", objp, "--out", d, "--name", node, "--pick", node], lambda rc, out: log(out.strip() or "(không có kết quả)"), log, api)


def retopo(api, mesh=None, role="hero", faces=0, tex="", log=None):
    log = log or api.log
    node = _target(api, mesh)
    d = _workdir()
    objp, height, nfaces = _write_src(api, node, d)
    args = ["run", objp, "--out", d, "--name", node, "--pick", node, "--role", role]
    if faces:
        args += ["--faces", str(int(faces))]
    tex = tex or os.environ.get("AI_RETOPO_TEX", "")
    if tex:
        args += ["--tex", tex]
    log("AI Retopo: %s (%d mặt, cao %.2f) -> %s, Blender chạy nền 20-60 giây ..." % (node, nfaces, height, role if not faces else "%d quad" % faces))
    before = set(api.ls())

    def done(rc, out):
        if rc != 0:
            log("AI Retopo lỗi:\n" + out[-1200:])
            return
        log(out.strip())
        fbx = os.path.join(d, node + "_retopo.fbx")
        if not os.path.exists(fbx):
            log("AI Retopo: không thấy file FBX kết quả")
            return
        api.import_file(fbx, "add")
        new = [n for n in api.ls() if n not in before]
        meshes = []
        for n in new:
            try:
                if api.mesh_data(n)["face_sizes"]:
                    meshes.append(n)
            except Exception:
                pass
        if not meshes:
            log("AI Retopo: đã nhập FBX nhưng không thấy mesh mới")
            return
        nm = meshes[0]
        md = api.mesh_data(nm)
        ys = md["positions"][1::3]
        h2 = max(ys) - min(ys)
        ratio = h2 / height if height else 1.0
        if abs(ratio - 1.0) > 0.05:      # FBX đơn vị lệch (cm / m): chỉnh về đúng cỡ bản gốc
            log("AI Retopo: bản mới lệch cỡ x%.3f so với bản gốc, đã chỉnh scale" % ratio)
            api.set_transform(nm, (0, 0, 0), (0, 0, 0), (1 / ratio,) * 3)
        try:
            api.select([node])
            api.hide(True)
        except Exception:
            log("AI Retopo: hãy tự ẩn bản gốc '%s'." % node)
        flip = os.path.join(d, node + "_albedo_vflip.png")
        if os.path.exists(flip):
            try:
                mat = api.create_material(nm + "_Mat")
                api.set_texture(mat, flip)
                api.assign_material(mat, [nm])
                log("AI Retopo: texture bake %s" % api.texture_state(mat))
            except Exception as e:
                log("AI Retopo: chưa gắn được texture (%s), gắn tay file bên dưới" % e)
        log("AI Retopo xong: '%s'. Texture mới (đã lật V): %s" % (nm, flip if os.path.exists(flip) else "(không bake)"))
        log("Thư mục kết quả: " + d)

    _run(args, done, log, api)


def register(api):
    p = api.panel("AI Retopo")
    p.heading("AI Retopo")
    p.text("hint", "Chon mesh, chon Role, bam Retopo. Ra mesh moi '<ten>_retopo' + texture bake; ban goc bi an, khong xoa. Can Blender.", tone="muted")
    p.int_field("role", "Role (0 hero 6000q, 1 npc 3000q, 2 light 1200q, 3 prop 1500q)", 0, 0, 3)
    p.int_field("faces", "Quad (0 = theo role)", 0, 0, 100000)
    p.button("check", "Check (chi do)", lambda: check(api))
    p.button("go", "Retopo", lambda: retopo(api, role=ROLE_LIST[p.get("role")], faces=p.get("faces")))
    api.command("AI Retopo", p.open)
