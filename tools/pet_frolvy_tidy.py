"""Dọn + mở Frolvy cho người dùng khi đang làm Pet (quy tắc người dùng 2026-11-13):
 - Pet đang làm = Pet có phiên Paseo "Pet NN" đang chạy, hoặc file .fv của Pet đang mở trong một cửa sổ Frolvy.
 - Với mỗi Pet đang làm: file .fv MỚI NHẤT trong New_PET\Pet_NN_*.
   * Đóng cửa sổ Frolvy đang mở file CŨ của Pet đó, nếu cửa sổ không có dấu * (không mất việc chưa lưu) và Pet đó không có phiên đang chạy ghi vào nó.
   * Nếu chưa cửa sổ nào đang mở file mới nhất: mở nó trong một Frolvy mới (cổng riêng từ 9900).
 Không bao giờ đóng cửa sổ có dấu * hoặc cửa sổ không phải file của Pet.
usage: py -I tools/pet_frolvy_tidy.py [--once | --loop SECONDS] [--dry]"""
import sys, os, glob, re, time, json, subprocess, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sync", os.path.join(HERE, "workai_pet_sync.py")); sync = importlib.util.module_from_spec(spec)
sys.argv_backup = sys.argv; sys.argv = sys.argv[:1]; spec.loader.exec_module(sync); sys.argv = sys.argv_backup
sys.stdout.reconfigure(encoding="utf-8")
FROLVY = r"C:\Program Files\Frolvy\Frolvy.exe"
dry = "--dry" in sys.argv

def windows():
    ps = "Get-Process Frolvy | ForEach-Object { '{0}|{1}' -f $_.Id, $_.MainWindowTitle }"
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=30).stdout
    r = []
    for l in out.splitlines():
        if "|" not in l: continue
        pid, t = l.split("|", 1)
        name = t.split(" - ", 1)[1] if " - " in t else ""
        port = name.split("[MCP")[1].strip(" ]") if "[MCP" in name else ""
        fname = name.split("[")[0].strip()
        saved = not fname.endswith("*")
        r.append({"pid": int(pid), "title": t, "file": fname.rstrip("*").strip(), "saved": saved, "port": port})
    return r

def pet_folder(pid):
    ds = glob.glob(os.path.join(sync.NEWPET, "Pet_%s_*" % pid)); return ds[0] if ds else None

STATE = os.path.join(HERE, "..", "work", "store", "_sys", "watch", "pet_tidy.json")

def load_state():
    try: return set(json.load(open(STATE, encoding="utf-8")))
    except Exception: return set()

def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True); json.dump(sorted(st)[-500:], open(STATE, "w", encoding="utf-8"))

def family(name):
    """pinchy_idle_new.fv / pinchy_idle_v2.fv -> pinchy_idle (các phiên bản của cùng một clip)."""
    stem = name[:-3] if name.lower().endswith(".fv") else name
    return re.sub(r"(_new|_v\d+|_old|_final|_fix)+$", "", stem)

def once():
    ws = windows(); st = load_state()
    running = sync.running_pets(); focus = running | sync.open_in_frolvy()
    used_ports = {int(w["port"]) for w in ws if w["port"].isdigit()}
    for pid in sorted(focus):
        d = pet_folder(pid)
        if not d: continue
        fvs = sorted(glob.glob(os.path.join(d, "*.fv")), key=os.path.getmtime)
        if not fvs: continue
        names = {os.path.basename(f) for f in fvs}
        latest_of = {}
        for f in fvs: latest_of[family(os.path.basename(f))] = f      # file mới nhất của từng clip
        mine = [w for w in ws if w["file"] in names]
        todo = []   # file cần có cửa sổ
        for w in mine:                                                  # clip người dùng đang mở -> phải là bản mới nhất
            lf = latest_of[family(w["file"])]
            if os.path.basename(lf) != w["file"] and lf not in todo: todo.append(lf)
        newest = fvs[-1]                                                # file vừa được sửa/lưu gần đây -> mở cho người dùng
        if time.time() - os.path.getmtime(newest) < 600 and newest not in todo: todo.append(newest)
        for f in todo:
            key = f + "|" + str(int(os.path.getmtime(f)))
            if any(w["file"] == os.path.basename(f) for w in ws) or key in st: continue
            port = next(p for p in range(9900, 9990) if p not in used_ports); used_ports.add(port); st.add(key)
            print("%s Pet %s: mở %s (cổng %d)" % (time.strftime("%H:%M"), pid, os.path.basename(f), port), flush=True)
            if not dry: subprocess.Popen([FROLVY, f], env=dict(os.environ, DCC_MCP_PORT=str(port)))
        for w in mine:                                                  # đóng bản cũ của cùng clip
            lf = latest_of[family(w["file"])]
            if os.path.basename(lf) != w["file"] and w["saved"] and pid not in running:
                print("%s Pet %s: đóng cửa sổ cũ %s" % (time.strftime("%H:%M"), pid, w["file"]), flush=True)
                if not dry:
                    subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-Process -Id %d).CloseMainWindow() | Out-Null" % w["pid"]], timeout=30)
    if not dry: save_state(st)

if __name__ == "__main__":
    if "--once" in sys.argv or dry: once(); print("xong 1 lượt")
    else:
        step = int(sys.argv[sys.argv.index("--loop") + 1]) if "--loop" in sys.argv else 60
        end = time.time() + 8 * 3600
        while time.time() < end:
            try: once()
            except Exception as e: print("lỗi:", e, flush=True)
            time.sleep(step)
