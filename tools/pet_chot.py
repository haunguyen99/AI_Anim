"""Chốt Pet: dọn thư mục làm việc + kiểm FBX đã chốt + đánh dấu CHOT.txt (để workai_pet_sync tích Done).
Chạy khi người dùng nói "chốt <Pet>" (quy tắc 2026-11-13). Việc xuất FBX do phiên Pet / finalize của con đó làm; công cụ này dọn và kiểm.
  py -I tools/pet_chot.py clean <ID> [--dry]   giữ file .fv MỚI NHẤT của mỗi clip (rig / idle / attack), xóa các bản cũ cùng clip,
                                               FBX: chỉ giữ 3 file chốt (Base, _Idle, _Attack), chuyển vào Thùng rác MỌI FBX khác (raw_*, _src, _orig,
                                               _old_fbx), kể cả bản sao mesh + fbx_backup bên work/infinite_defense/pets/<tên>/. Giữ report + script.
  py -I tools/pet_chot.py check <ID>           kiểm 3 FBX: Base có mesh + deformer + BindPose, 0 AnimationStack; _Idle/_Attack 0 mesh, có Dummy.
  py -I tools/pet_chot.py mark <ID>            ghi CHOT.txt (chỉ khi check đạt)
  py -I tools/pet_chot.py all <ID>             clean + check + mark"""
import sys, os, re, glob, shutil, time
sys.stdout.reconfigure(encoding="utf-8")
NEWPET = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET"

def folder(pid):
    ds = glob.glob(os.path.join(NEWPET, "Pet_%s_*" % pid))
    if not ds: sys.exit("không thấy thư mục Pet_%s_*" % pid)
    return ds[0]

def family(name):
    stem = name[:-3] if name.lower().endswith(".fv") else name
    return re.sub(r"(_new|_v\d+|_old|_final|_fix)+$", "", stem)

def clean(pid, dry):
    d = folder(pid); dele = []
    fvs = sorted(glob.glob(os.path.join(d, "*.fv")), key=os.path.getmtime)
    latest = {}
    for f in fvs: latest[family(os.path.basename(f))] = f
    keep = set(latest.values())
    dele += [f for f in fvs if f not in keep]
    dele += glob.glob(os.path.join(d, "*.tmp"))
    # FBX: chỉ giữ đúng 3 file chốt (Base, _Idle, _Attack) ở thư mục Pet; mọi FBX khác xóa (raw_*, _src, _orig, _old_fbx, bản sao...)
    final = set(finals(d))
    for f in glob.glob(os.path.join(d, "**", "*.fbx"), recursive=True):
        if f not in final: dele.append(f)
    for sub in ("_tmp", "_old_fbx", "_orig", "_old"):
        t = os.path.join(d, sub)
        if os.path.isdir(t): dele.append(t)
    # bên work/infinite_defense/pets/<tên>/: xóa bản sao mesh, fbx_backup, mọi *.fbx (script, rig, anim, shots, report giữ)
    wk = workdir(d)
    if wk and os.path.isdir(wk):
        dele += glob.glob(os.path.join(wk, "**", "*.fbx"), recursive=True)
        fb = os.path.join(wk, "fbx_backup")
        if os.path.isdir(fb): dele.append(fb)
    dele = sorted({x for x in dele if os.path.exists(x)}, key=lambda x: -len(x))   # file trước, thư mục sau
    for f in dele:
        print(("sẽ bỏ vào thùng rác: " if dry else "bỏ vào thùng rác: ") + os.path.relpath(f, d))
    if not dry and dele: recycle(dele)
    print("giữ .fv: " + ", ".join(os.path.basename(f) for f in sorted(keep)))
    return d

def recycle(paths):
    """Chuyển vào Thùng rác Windows (khôi phục được), không xóa hẳn."""
    import subprocess
    lines = ["Add-Type -AssemblyName Microsoft.VisualBasic"]
    for p in paths:
        q = p.replace("'", "''")
        if os.path.isdir(p):
            lines.append("[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory('%s','OnlyErrorDialogs','SendToRecycleBin')" % q)
        else:
            lines.append("[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile('%s','OnlyErrorDialogs','SendToRecycleBin')" % q)
    r = subprocess.run(["powershell", "-NoProfile", "-Command", "; ".join(lines)], capture_output=True, text=True, timeout=300)
    if r.returncode: print("LỖI thùng rác:", r.stderr[:300])

def finals(d):
    fb = glob.glob(os.path.join(d, "Pet_*.fbx"))
    idle = [f for f in fb if f.endswith("_Idle.fbx")]; att = [f for f in fb if f.endswith("_Attack.fbx")]
    base = [f for f in fb if not f.endswith(("_Idle.fbx", "_Attack.fbx", "_src.fbx")) and "original" not in f]
    return base + idle + att

def workdir(d):
    m = re.match(r"Pet_\d+_(.+)$", os.path.basename(d))
    return os.path.join(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets", m.group(1).lower()) if m else None

def count(text, pat): return len(re.findall(pat, text, re.M))

def check(pid):
    d = folder(pid); ok = True; msgs = []
    files = glob.glob(os.path.join(d, "Pet_*.fbx"))
    idle = [f for f in files if f.endswith("_Idle.fbx")]; att = [f for f in files if f.endswith("_Attack.fbx")]
    base = [f for f in files if not f.endswith(("_Idle.fbx", "_Attack.fbx")) and "_src" not in f]
    if len(base) != 1 or len(idle) != 1 or len(att) != 1:
        print("THIẾU file: Base=%d Idle=%d Attack=%d" % (len(base), len(idle), len(att))); return False
    def rd(f): return open(f, encoding="utf-8", errors="ignore").read()
    b = rd(base[0])
    r = {"mesh (Geometry)": count(b, r"^\s*Geometry: ") >= 1, "deformer": count(b, r"^\s*Deformer: ") >= 1,
         "BindPose": "BindPose" in b, "0 AnimationStack": count(b, r"^\s*AnimationStack: ") == 0}
    for k, v in r.items(): msgs.append(("Base %-18s %s" % (k, "ĐẠT" if v else "LỖI"))); ok &= v
    for f in (idle[0], att[0]):
        t = rd(f); n = os.path.basename(f)
        r = {"0 mesh": count(t, r"^\s*Geometry: ") == 0, "0 deformer": count(t, r"^\s*Deformer: ") == 0,
             "có clip": count(t, r"^\s*AnimationStack: ") >= 1, "Dummy cùng cấp": "Model::Dummy" in t}
        for k, v in r.items(): msgs.append(("%s %-14s %s" % (n, k, "ĐẠT" if v else "LỖI"))); ok &= v
    print("\n".join(msgs)); print("KẾT QUẢ: " + ("ĐẠT" if ok else "CHƯA ĐẠT")); return ok

def mark(pid):
    d = folder(pid)
    open(os.path.join(d, "CHOT.txt"), "w", encoding="utf-8").write("Chốt %s\n" % time.strftime("%Y-%m-%d %H:%M"))
    print("đã ghi CHOT.txt")

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2: sys.exit(__doc__)
    cmd, pid = a[0], a[1]; dry = "--dry" in a
    if cmd == "clean": clean(pid, dry)
    elif cmd == "check": sys.exit(0 if check(pid) else 1)
    elif cmd == "mark": mark(pid)
    elif cmd == "all":
        clean(pid, dry)
        if check(pid) and not dry: mark(pid)
    else: sys.exit(__doc__)
