"""Tự cập nhật trạng thái subtask Pet (GEK-2355..2369, việc cha GEK-2273) trên WorkAI theo tiến độ thật.
Quy tắc (người dùng 2026-11-13, "tự tích done và in progress khi tôi đang làm dự án"):
  To Do -> In Progress : có agent Paseo "Pet NN" đang chạy, hoặc file .fv của Pet đang mở trong một cửa sổ Frolvy (kể cả cửa sổ người dùng tự mở), hoặc thư mục New_PET\\Pet_NN_* đã có file .fv
  -> Done              : thư mục có file đánh dấu CHOT.txt (Claude tạo khi người dùng nói "chốt <Pet>") và đủ 3 FBX.
                         (Không dựa riêng vào FBX: phiên con có thể xuất FBX sớm trước khi người dùng chốt.)
  Không bao giờ lùi trạng thái (Done không bị kéo về In Progress).
usage: py -I tools/workai_pet_sync.py [--once | --loop SECONDS] [--dry]   (mặc định --loop 120, tối đa 8 giờ)"""
import sys, os, re, glob, json, time, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "workai"))
import workai
sys.stdout.reconfigure(encoding="utf-8")
NEWPET = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET"
PASEO = r"C:\Users\Admin\AppData\Local\Programs\Paseo\resources\bin\paseo.cmd"
PARENT_KEYS = ("GEK-2355", "GEK-2369")  # khoảng mã subtask Pet
dry = "--dry" in sys.argv

def running_pets():
    try:
        out = subprocess.run([PASEO, "ls", "--json"], capture_output=True, text=True, timeout=60).stdout
        d = json.loads(out); d = d.get("agents", d) if isinstance(d, dict) else d
        r = set()
        for a in d:
            m = re.match(r"Pet (\d+) ", a.get("name") or a.get("title") or "")
            if m and (a.get("status") or "").lower() == "running": r.add(m.group(1))
        return r
    except Exception:
        return set()

def open_in_frolvy():
    """Pet nào đang mở trong cửa sổ Frolvy (kể cả cửa sổ người dùng tự mở): theo tên file .fv trong tiêu đề."""
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Process Frolvy | ForEach-Object { $_.MainWindowTitle }"],
                             capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return set()
    r = set()
    for t in out.splitlines():
        if " - " not in t: continue
        name = t.split(" - ", 1)[1].split("[")[0].strip().rstrip("*").strip()
        if not name.lower().endswith(".fv"): continue
        for f in glob.glob(os.path.join(NEWPET, "Pet_*", name)):
            folder = os.path.basename(os.path.dirname(f)).split("_")
            if len(folder) > 1 and folder[1].isdigit(): r.add(folder[1])
    return r

def folder_state(pid):
    ds = glob.glob(os.path.join(NEWPET, "Pet_%s_*" % pid))
    if not ds: return False, False
    d = ds[0]; fbx = [os.path.basename(f) for f in glob.glob(os.path.join(d, "*.fbx"))]
    base = [f for f in fbx if not f.endswith(("_Idle.fbx", "_Attack.fbx")) and "_src" not in f]
    done = os.path.exists(os.path.join(d, "CHOT.txt")) and bool(base) and any(f.endswith("_Idle.fbx") for f in fbx) and any(f.endswith("_Attack.fbx") for f in fbx)
    started = bool(glob.glob(os.path.join(d, "*.fv")))
    return started, done

def transition(issue, want):
    c, o = workai.call("GET", "/api/issues/%d/transitions" % issue["id"])
    for t in (o.get("transitions") or []):
        if t["name"].lower() == want.lower():
            c2, _ = workai.call("POST", "/api/issues/%d/transition" % issue["id"], {"transition_id": t["id"]})
            return c2
    return None

def once():
    c, o = workai.call("GET", "/api/issues?assignee_id=%d&per_page=100" % workai.call("GET", "/api/auth/me")[1]["data"]["user"]["id"])
    run = running_pets() | open_in_frolvy(); changes = []
    for i in o["data"]:
        m = re.match(r"Pet (\d+) ", i["summary"])
        if not m or not (PARENT_KEYS[0] <= i["issue_key"] <= PARENT_KEYS[1]): continue
        pid = m.group(1); started, done = folder_state(pid); st = i["status"]
        want = None
        if done and st != "Done": want = "Done"
        elif st == "To Do" and (pid in run or started): want = "In Progress"
        if want:
            res = "dry" if dry else transition(i, want)
            changes.append("%s %s: %s -> %s (%s)" % (time.strftime("%H:%M"), i["issue_key"], st, want, res)); print(changes[-1], flush=True)
    return changes

if __name__ == "__main__":
    if "--once" in sys.argv or dry: once(); print("xong 1 lượt")
    else:
        step = int(sys.argv[sys.argv.index("--loop") + 1]) if "--loop" in sys.argv else 120
        end = time.time() + 8 * 3600
        while time.time() < end:
            try: once()
            except Exception as e: print("lỗi:", e, flush=True)
            time.sleep(step)
