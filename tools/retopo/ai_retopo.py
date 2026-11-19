"""AI Retopo - một lệnh: đo mesh, retopo tự động, bake texture, xuất FBX, báo cáo bằng lời.

    python3 tools/retopo/ai_retopo.py check <file> [--out thư_mục]
    python3 tools/retopo/ai_retopo.py run <file> [--role hero|npc|light|prop | --faces N] [--tex ảnh] [--out thư_mục] [--name tên]
<file>: obj / fbx / glb. Cần Blender (lệnh `blender` hoặc flatpak org.blender.Blender); chạy nền, không mở giao diện.
Plugin Frolvy "AI Retopo" gọi chính file này. Kết quả: <out>/<tên>_retopo.fbx, _albedo.png (+ _albedo_vflip.png cho Frolvy), _retopo_report.json
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "blender_retopo.py")


def blender_cmd():
    if os.environ.get("BLENDER"):
        return [os.environ["BLENDER"]]
    if shutil.which("blender"):
        return ["blender"]
    if shutil.which("blender.exe"):
        return ["blender.exe"]
    if shutil.which("flatpak"):
        return ["flatpak", "run", "--user", "--filesystem=/tmp", "org.blender.Blender"]
    raise SystemExit("Chưa có Blender. Cài Blender (hoặc đặt biến BLENDER=đường dẫn) rồi chạy lại.")


def run_blender(args):
    cmd = blender_cmd() + ["-b", "--python", SCRIPT, "--"] + args
    p = subprocess.run(cmd, capture_output=True, text=True)
    rep = None
    for line in p.stdout.splitlines():
        if line.startswith("AI_RETOPO_REPORT "):
            rep = json.loads(line[len("AI_RETOPO_REPORT "):])
    if rep is None:
        raise SystemExit("Blender lỗi, không ra báo cáo:\n" + (p.stdout[-1500:] + p.stderr[-1500:]))
    return rep


def say(rep):
    b = rep["before"]
    L = ["%s: %d tam giác, %.0f%% quad, đối xứng lệch %.2f%% cao" % (rep["name"], b["tri_equiv"], b["quad_pct"], rep["symmetry_pct"])]
    L += ["- " + v for v in rep["verdict_before"]]
    if "after" in rep:
        a = rep["after"]
        L += ["Sau retopo: %d tam giác (%d quad, %.0f%% quad), đối xứng %s" % (a["tri_equiv"], a["quads"], a["quad_pct"], "có" if rep["symmetry_used"] else "không"),
              "Độ lệch so với bản gốc: TB %.2f%%, tệ nhất 1%% đỉnh %.2f%% chiều cao" % (rep["deviation_mean_pct"], rep["deviation_p99_pct"])]
        L += ["- " + v for v in rep["verdict_after"]]
        L += ["FBX: " + rep["fbx"], "Texture: " + (rep["bake"] if isinstance(rep["bake"], str) else rep["bake"]["albedo_vflip_for_frolvy"] + " (đã lật V cho Frolvy)"),
              "Lưu ý: " + rep["note"]]
    return "\n".join(L)


def main(argv):
    if len(argv) < 2 or argv[0] not in ("check", "run"):
        print(__doc__); return 2
    cmd, src, rest = argv[0], os.path.abspath(argv[1]), argv[2:]
    if "--out" not in rest:
        rest += ["--out", os.path.join(os.path.dirname(src), "retopo")]
    args = ["--in", src] + rest + (["--check-only"] if cmd == "check" else [])
    rep = run_blender(args)
    print(say(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
