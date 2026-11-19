"""Xuất bản giao Spine theo đúng setting Export của người dùng (skill /exportspine).

Chạy (từ gốc dự án):
  .venv/Scripts/python.exe -I tools/spine/export_spine.py <skeleton.json> --name <TenAsset> [--anims idle,active,mix]
        [--scale 1.18] [--out <thư mục>] [--dry]

Làm gì:
  1. Đọc setting Export JSON mới nhất của người dùng trong Spine (C:/Users/<user>/Spine/settings/editor-2.json, khoá
     export.json; file dạng JSON libgdx không ngoặc kép) -> <thư mục>/export_settings.json ("class": "export-json").
     Không dùng mặc định của CLI (2026-10-26: atlas .atlas + PMA mặc định bị lỗi trong game).
  2. Bản giao <ten>_final.json: chỉ giữ các anim cần giao (mặc định: mọi anim trừ setup / rig_test / test_* / tên bắt đầu _).
  3. Import -> <TenAsset>_final.spine (project mới, không đè project làm việc), export -> <thư mục>/export/.
  4. Kiểm bản export: đủ anim, độ dài từng anim khớp bản nguồn (cleanUp xoá key giữ cuối -> anim ngắn lại: tự thêm
     event `loop_end` ở cuối rồi xuất lại), atlas đúng đuôi, không PMA, liệt kê PNG + scale.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
SPINE_EXE = os.environ.get("SPINE_EXE") or (r"C:\Program Files\Spine\Spine.com" if os.name == "nt"
                                            else os.path.expanduser("~/.local/opt/Spine/Spine.sh"))   # Linux 2026-11-18
SPINE_VER = os.environ.get("SPINE_VERSION", "4.2.43")
SKIP = re.compile(r"^(setup|rig_test|test_.*|_.*)$")


# ---------------- setting của người dùng (JSON libgdx: khoá / chuỗi không ngoặc kép) ----------------
def parse_gdx(s):
    i = 0

    def ws():
        nonlocal i
        while i < len(s) and s[i] in " \t\r\n":
            i += 1

    def val():
        nonlocal i
        ws()
        c = s[i]
        if c == "{":
            i += 1; o = {}
            while True:
                ws()
                if s[i] == "}":
                    i += 1; return o
                k = tok(":")
                i += 1
                o[k] = val()
                ws()
                if s[i] == ",":
                    i += 1
        if c == "[":
            i += 1; a = []
            while True:
                ws()
                if s[i] == "]":
                    i += 1; return a
                a.append(val())
                ws()
                if s[i] == ",":
                    i += 1
        t = tok(",}]")
        return conv(t)

    def tok(stops):
        nonlocal i
        ws()
        if s[i] == '"':
            j = i + 1
            while s[j] != '"':
                j += 2 if s[j] == "\\" else 1
            r = json.loads(s[i:j + 1]); i = j + 1
            return r
        j = i
        while j < len(s) and s[j] not in stops:
            j += 1
        r = s[i:j].strip(); i = j
        return r

    def conv(t):
        if not isinstance(t, str):
            return t
        if t in ("true", "false"):
            return t == "true"
        if t == "null":
            return None
        try:
            return int(t)
        except ValueError:
            pass
        try:
            return float(t)
        except ValueError:
            return t

    return val()


def user_settings():
    home = os.path.expanduser("~")
    p = os.path.join(home, "Spine", "settings", "editor-2.json")
    if not os.path.exists(p):
        cands = glob.glob(r"C:/Users/*/Spine/settings/editor-2.json") + glob.glob(os.path.join(home, ".spine", "settings", "editor-*.json"))
        p = max(cands, key=os.path.getmtime) if cands else None
    if p:
        d = parse_gdx(open(p, encoding="utf-8").read())
        ej = (d.get("export") or {}).get("json")
        if ej:
            return p, ej
    # 2026-11-18 máy Linux: Spine chưa từng xuất (export:{}) -> setting người dùng ở lần giao gần nhất (export_settings.json
    # trong work/, do script này ghi từ editor-2.json trên máy Windows)
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    cands = [f for f in glob.glob(os.path.join(root, "work", "**", "export_settings.json"), recursive=True)
             if json.load(open(f, encoding="utf-8")).get("class") == "export-json"]
    if not cands:
        raise SystemExit("Không tìm thấy setting Spine (editor-2.json) hay export_settings.json cũ")
    p = max(cands, key=os.path.getmtime)
    return p, json.load(open(p, encoding="utf-8"))


def cli_settings(ej, out_dir, scale=None):
    pa = {k: v for k, v in ej["packAtlas"].items() if k not in ("id", "autoScale", "webp")}
    if scale is not None:
        pa["scale"] = [scale]
    keep = ("extension", "format", "prettyPrint", "nonessential", "cleanUp", "packTarget", "packSource", "warnings")
    st = {"class": "export-json", **{k: ej[k] for k in keep if k in ej}, "output": out_dir.replace("\\", "/"),
          "packAtlas": pa}
    return st


# ---------------- Spine CLI ----------------
def run(args):
    cmd = [SPINE_EXE, "-u", SPINE_VER] + [str(a) for a in args]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode != 0 or "error" in out.lower() and "0 error" not in out.lower():
        print(out[-3000:])
    if p.returncode != 0:
        raise SystemExit(f"Spine CLI lỗi ({p.returncode}): {subprocess.list2cmdline(cmd)}")
    return out


def anim_len(a):
    t = 0.0
    def walk(o):
        nonlocal t
        if isinstance(o, dict):
            if "time" in o and isinstance(o["time"], (int, float)):
                t = max(t, o["time"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(a)
    return round(t, 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--name", required=True, help="tên asset giao (vd MascotBackToSchool) -> tên file export")
    ap.add_argument("--anims", help="danh sách anim giao, cách bằng dấu phẩy (mặc định: mọi anim trừ setup / rig_test / test_*)")
    ap.add_argument("--rename", help="đổi tên anim khi giao: cũ:mới,cũ:mới (vd active_fast:active); anim không giao thì khỏi đụng tên")
    ap.add_argument("--scale", type=float, help="ghi đè scale atlas (mặc định: scale trong setting Spine của người dùng)")
    ap.add_argument("--out", help="thư mục export (mặc định <thư mục json>/export)")
    ap.add_argument("--dry", action="store_true", help="chỉ in setting + danh sách anim, không xuất")
    a = ap.parse_args()

    src = os.path.abspath(a.json)
    folder = os.path.dirname(src)
    out_dir = os.path.abspath(a.out or os.path.join(folder, "export"))
    skel = json.load(open(src, encoding="utf-8"))
    all_anims = list(skel.get("animations", {}))
    anims = [x.strip() for x in a.anims.split(",")] if a.anims else [x for x in all_anims if not SKIP.match(x)]
    miss = [x for x in anims if x not in all_anims]
    if miss:
        raise SystemExit(f"Không có anim: {miss} (file có: {all_anims})")
    ren = dict(p.strip().split(":", 1) for p in a.rename.split(",")) if a.rename else {}
    bad = [x for x in ren if x not in anims]
    if bad:
        raise SystemExit(f"--rename: anim {bad} không nằm trong danh sách giao {anims}")
    new = lambda x: ren.get(x, x)
    sp, ej = user_settings()
    st = cli_settings(ej, out_dir, a.scale)
    pa = st["packAtlas"]
    print(f"setting người dùng: {sp}")
    print(f"  atlas {pa.get('atlasExtension')} · scale {pa.get('scale')} · PMA {pa.get('premultiplyAlpha')} · "
          f"pot {pa.get('pot')} square {pa.get('square')} · max {pa.get('maxWidth')}x{pa.get('maxHeight')} · "
          f"cleanUp {st.get('cleanUp')} · nonessential {st.get('nonessential')} · {st.get('packTarget')}")
    src_len = {x: anim_len(skel["animations"][x]) for x in anims}
    print("anim giao:", ", ".join(f"{x}{' -> ' + new(x) if new(x) != x else ''} {src_len[x]:.3f}s ({round(src_len[x] * 30)}F)" for x in anims))
    print("bỏ:", ", ".join(x for x in all_anims if x not in anims) or "-")
    if a.dry:
        return
    if pa.get("premultiplyAlpha"):
        print("CẢNH BÁO: setting người dùng đang bật premultiplyAlpha")

    set_path = os.path.join(folder, "export_settings.json")
    json.dump(st, open(set_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    base = a.name
    final_json = os.path.join(folder, f"{base.lower()}_final.json")
    final_spine = os.path.join(folder, f"{base}_final.spine")

    def build_final(end_events):
        fin = json.loads(json.dumps(skel))
        fin["animations"] = {new(x): skel["animations"][x] for x in anims}
        if end_events:
            fin.setdefault("events", {}).setdefault("loop_end", {})
            for x in end_events:
                an = fin["animations"][new(x)] = json.loads(json.dumps(fin["animations"][new(x)]))
                ev = [e for e in an.get("events", []) if e.get("name") != "loop_end"]
                ev.append({"time": src_len[x], "name": "loop_end"})
                an["events"] = ev
        fin["skeleton"]["images"] = "./images/"
        json.dump(fin, open(final_json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    def export():
        if os.path.exists(final_spine):
            os.remove(final_spine)
        if os.path.isdir(out_dir):
            old = out_dir + "_old"
            shutil.rmtree(old, ignore_errors=True)
            shutil.move(out_dir, old)
        os.makedirs(out_dir, exist_ok=True)
        run(["-i", final_json, "-o", final_spine, "-r", base])
        run(["-i", final_spine, "-o", out_dir, "-e", set_path])

    build_final([])
    export()
    exp = glob.glob(os.path.join(out_dir, "*.json"))
    if not exp:
        raise SystemExit("Export không ra file JSON")
    ex = json.load(open(exp[0], encoding="utf-8"))
    short = [x for x in anims if anim_len(ex["animations"].get(new(x), {})) < src_len[x] - 1e-3]
    if short:
        print(f"cleanUp làm ngắn {short}: thêm event loop_end ở cuối rồi xuất lại")
        build_final(short)
        export()
        exp = glob.glob(os.path.join(out_dir, "*.json"))
        ex = json.load(open(exp[0], encoding="utf-8"))

    # ---- kiểm bản export ----
    ok = True
    print(f"\nbản giao: {final_spine}\nexport: {out_dir}")
    for x in anims:
        if new(x) not in ex.get("animations", {}):
            print(f"  THIẾU anim {new(x)}"); ok = False; continue
        L = anim_len(ex["animations"][new(x)])
        flag = "OK" if abs(L - src_len[x]) < 1e-3 else "LỆCH"
        ok &= flag == "OK"
        print(f"  {new(x)}: {L:.3f}s ({round(L * 30)}F) / nguồn {src_len[x]:.3f}s  {flag}")
    extra = [x for x in ex.get("animations", {}) if x not in {new(y) for y in anims}]
    if extra:
        print("  anim thừa:", extra); ok = False
    atl = [f for f in os.listdir(out_dir) if f.endswith(pa.get("atlasExtension", ".atlas"))]
    pngs = sorted(f for f in os.listdir(out_dir) if f.endswith(".png"))
    if not atl:
        print(f"  THIẾU atlas {pa.get('atlasExtension')}"); ok = False
    else:
        txt = open(os.path.join(out_dir, atl[0]), encoding="utf-8").read()
        pma = re.search(r"pma\s*:\s*true", txt) is not None
        sizes = re.findall(r"size\s*:\s*(\d+)\s*,\s*(\d+)", txt)
        print(f"  atlas {atl[0]} · PMA {'CÓ (sai)' if pma else 'không'} · trang {', '.join('x'.join(s) for s in sizes)}")
        ok &= not pma
    print(f"  PNG: {', '.join(pngs)}")
    print(f"  file: {', '.join(sorted(os.listdir(out_dir)))}")
    print("KẾT QUẢ:", "đạt" if ok else "CÓ LỖI")


if __name__ == "__main__":
    main()
