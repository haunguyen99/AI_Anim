"""Đóng gói Spine Live thành thư mục PORTABLE cho Windows (chạy OFFLINE, bấm đúp là mở, không cài Python, không tự bật server).

Chạy (Linux / macOS / Windows, cần mạng MỘT LẦN để tải Python embed + wheel Windows):
    .venv/bin/python -I tools/spine_live/make_portable_win.py [--out dist/SpineLive_Windows] [--cache dist/_dl] [--sample work/<game>/spine/<anim>] [--no-zip]
Kết quả: <out>/ + <out>.zip.  Cấu trúc:
    SpineLive.vbs  (bấm đúp: bật phần xử lý ngầm + mở cửa sổ ứng dụng Edge / Chrome; đóng cửa sổ thì tự tắt sau ~3 phút)
    SpineLive_log.bat (xem log khi lỗi) · Mo_thu_muc_work.bat · HUONG_DAN.txt
    python/ (Python 3.12 embed) · site-packages/ (numpy, opencv, pillow bản Windows) · app/ (mã Spine Live + work/)
Phần xử lý (server) vẫn là tools/spine_live/server.py nhưng chạy ngầm trong máy người dùng, không cần mạng, không cần gõ lệnh.
Các lệnh dành cho Claude (spine_live_cmd.py, Theo Claude, Gen) KHÔNG đi kèm: chỉ có các chế độ sửa tay trên trang.
"""
import argparse, io, os, shutil, subprocess, sys, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PYVER = "3.12.10"
EMBED_URL = f"https://www.python.org/ftp/python/{PYVER}/python-{PYVER}-embed-amd64.zip"
WHEELS = ["numpy==2.2.6", "opencv-python==5.0.0.93", "pillow==12.3.0"]      # khớp requirements.txt; psd-tools / scipy chỉ cần cho script dựng rig
FILES = {   # nguồn (tính từ gốc dự án) -> đích trong app/
    "tools/spine_live": ["index.html", "*.js", "server.py", "vendor"],
    "tools/home": ["spine_live.py", "spine_edit.py", "spine_bridge.py"],
    "tools/spine": ["anim_params.py", "key_reduce.py", "anim_kit.py", "idle_engine.py", "active_engine.py", "rig_demo.py"],
}

VBS = r'''' Spine Live (portable): bat phan xu ly ngam + mo cua so ung dung. Bam dup file nay.
Option Explicit
Dim sh, fso, base, port, url, cmd, browser, rc
Function RegHas(k)
  Dim v
  On Error Resume Next
  v = sh.RegRead(k)
  RegHas = (Err.Number = 0)
  Err.Clear
End Function
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
base = fso.GetParentFolderName(WScript.ScriptFullName)
port = "8781"
url = "http://127.0.0.1:" & port & "/spine"
sh.CurrentDirectory = base & "\app"
sh.Environment("Process")("SPINE_PORT") = port
sh.Environment("Process")("SPINELIVE_IDLE_EXIT") = "180"
sh.Environment("Process")("PYTHONIOENCODING") = "utf-8"
' khoi dong server (an cua so). Neu cong da co server (mo lan 2) thi tien trinh moi tu thoat, trang van dung server cu.
cmd = """" & base & "\python\pythonw.exe"" -I ""tools\spine_live\server.py"""
sh.Run cmd, 0, False
WScript.Sleep 1800
browser = ""
If RegHas("HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe\") Then browser = "msedge"
If browser = "" Then
  If RegHas("HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe\") Or RegHas("HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe\") Then browser = "chrome"
End If
If browser <> "" Then
  sh.Run "cmd /c start """" " & browser & " --app=" & url & " --window-size=1500,900", 0, False
Else
  sh.Run url, 1, False
End If
'''

LOG_BAT = r'''@echo off
chcp 65001 >nul
cd /d "%~dp0app"
echo === Log Spine Live (work\store\_sys\spine_live\server.log) ===
if exist "work\store\_sys\spine_live\server.log" (type "work\store\_sys\spine_live\server.log") else (echo Chua co log.)
echo.
echo === Thu chay server o cua so nay (Ctrl+C de tat) ===
set SPINE_PORT=8781
"%~dp0python\python.exe" -I tools\spine_live\server.py
pause
'''

WORK_BAT = r'''@echo off
if not exist "%~dp0app\work" mkdir "%~dp0app\work"
start "" explorer "%~dp0app\work"
'''

GUIDE = '''SPINE LIVE (bản portable cho Windows, chạy offline)

1. Giải nén cả thư mục SpineLive_Windows ở đâu cũng được (đừng để trong thư mục có dấu / ký tự lạ nếu gặp lỗi; tốt nhất C:\\SpineLive).
2. Bấm đúp  SpineLive.vbs  -> mở cửa sổ ứng dụng Spine Live (dùng Microsoft Edge hoặc Chrome có sẵn trên máy). Không cần cài Python, không cần mạng.
   Đóng cửa sổ là xong; phần xử lý ngầm tự tắt sau khoảng 3 phút.
3. Đưa file Spine vào:  Mo_thu_muc_work.bat  mở thư mục  app\\work\\ .  Mỗi anim một thư mục theo mẫu:
       app\\work\\<ten_game>\\spine\\<ten_anim>\\<ten>.json   (kèm thư mục images\\ chứa PNG, và atlas nếu có)
   Mở lại Spine Live, chọn file ở ô chọn file đầu trang.
4. Sửa tay trên trang: chọn xương (bấm / cây xương phím T), C xoay · V dời · X scale · Z shear; tab Animate để key, Auto key,
   Graph ▾ (chỉnh curve), Công cụ ▾ (Mesh / Bind, Weight, Physics, Tham số anim), Ctrl+Z hoàn tác, tab History / cột Phiên bản.
   Mọi chỉnh sửa ghi thẳng vào file JSON; lịch sử hoàn tác nằm ở app\\work\\store\\_sys\\spine_live\\ (xoá được nếu muốn dọn).

KHÔNG có trong bản này: các nút làm việc cùng Claude (Gen, Gửi ghi chú, chế độ Theo Claude) và lệnh spine_live_cmd.py.
Muốn đưa sang Spine editor: import file .json vào Spine.

Gặp lỗi:
 - Cửa sổ trắng / không mở: chạy  SpineLive_log.bat  xem log (thiếu MSVCP140.dll thì cài "Microsoft Visual C++ Redistributable 2015-2022 x64").
 - Cổng 8781 bận: đóng chương trình đang dùng cổng đó, hoặc sửa số 8781 trong SpineLive.vbs.
 - Antivirus chặn pythonw.exe: cho phép thư mục này (đây là Python chính thức, không có mã lạ).
'''


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1_000_000:
        return dest
    print("tải", url)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r, open(dest + ".part", "wb") as f:
        shutil.copyfileobj(r, f)
    os.replace(dest + ".part", dest)
    return dest


def copy_app(app):
    import glob
    for src_dir, pats in FILES.items():
        dst_dir = os.path.join(app, src_dir)
        os.makedirs(dst_dir, exist_ok=True)
        for pat in pats:
            for p in glob.glob(os.path.join(ROOT, src_dir, pat)):
                d = os.path.join(dst_dir, os.path.basename(p))
                if os.path.isdir(p):
                    shutil.copytree(p, d, ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)
                else:
                    shutil.copy2(p, d)
    os.makedirs(os.path.join(app, "work"), exist_ok=True)
    open(os.path.join(app, "work", "README.txt"), "w", encoding="utf-8").write(
        "Chép thư mục Spine vào đây: work\\<ten_game>\\spine\\<ten_anim>\\<ten>.json (+ images\\, atlas)\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "SpineLive_Windows"))
    ap.add_argument("--cache", default=os.path.join(ROOT, "dist", "_dl"))
    ap.add_argument("--sample", help="thư mục anim Spine (JSON + images) chép sẵn vào work/ làm mẫu")
    ap.add_argument("--no-zip", action="store_true")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    # Python embed
    emb = fetch(EMBED_URL, os.path.join(a.cache, os.path.basename(EMBED_URL)))
    py = os.path.join(out, "python")
    with zipfile.ZipFile(emb) as z:
        z.extractall(py)
    pth = [f for f in os.listdir(py) if f.endswith("._pth")][0]
    stem = pth[:-5]
    open(os.path.join(py, pth), "w", encoding="utf-8").write(
        f"{stem}.zip\n.\n..\\site-packages\n..\\app\\tools\\home\n..\\app\\tools\\spine\n..\\app\\tools\\spine_live\nimport site\n")
    # wheel Windows (cp312, win_amd64)
    wh = os.path.join(a.cache, "wheels")
    os.makedirs(wh, exist_ok=True)
    subprocess.check_call([sys.executable, "-m", "pip", "download", "--no-deps", "--only-binary=:all:", "--platform", "win_amd64",
                           "--python-version", "3.12", "--implementation", "cp", "-d", wh] + WHEELS)
    sp = os.path.join(out, "site-packages")
    os.makedirs(sp)
    for f in sorted(os.listdir(wh)):
        if f.endswith(".whl") and any(f.lower().startswith(w.split("==")[0].replace("-", "_").lower()) for w in WHEELS):
            with zipfile.ZipFile(os.path.join(wh, f)) as z:
                z.extractall(sp)
    # mã Spine Live
    app = os.path.join(out, "app")
    copy_app(app)
    if a.sample:
        name = os.path.basename(os.path.normpath(a.sample))
        dst = os.path.join(app, "work", "sample", "spine", name)
        shutil.copytree(a.sample, dst, ignore=shutil.ignore_patterns("__pycache__", "_live", "src", "*.psd", "*.pyc"))
    # launcher + hướng dẫn (CRLF cho Windows)
    for name, text in (("SpineLive.vbs", VBS), ("SpineLive_log.bat", LOG_BAT), ("Mo_thu_muc_work.bat", WORK_BAT), ("HUONG_DAN.txt", GUIDE)):
        open(os.path.join(out, name), "w", encoding="utf-8-sig" if name.endswith(".txt") else "ascii" if name.endswith(".vbs") else "utf-8",
             newline="\r\n").write(text if not name.endswith(".vbs") else text.encode("ascii", "replace").decode("ascii"))
    if not a.no_zip:
        zp = shutil.make_archive(out, "zip", os.path.dirname(out), os.path.basename(out))
        print("zip:", zp, "%.0f MB" % (os.path.getsize(zp) / 1e6))
    print("xong:", out)


if __name__ == "__main__":
    main()
