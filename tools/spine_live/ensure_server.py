"""Bật server Spine Live CHẠY RIÊNG (2026-11-10, rà soát: server chạy như tiến trình con của khung xem trước trong app
nên đóng khung là tắt luôn server).

  python -I tools/spine_live/ensure_server.py          server chưa chạy thì bật (tách hẳn), rồi thoát
  python -I tools/spine_live/ensure_server.py --hold   như trên rồi ngồi chờ (dùng cho .claude/launch.json: app giữ
                                                       tiến trình này; đóng khung chỉ tắt nó, server vẫn chạy)
  thêm --lan để bật server cho máy cùng mạng.
Log server: work/store/_sys/spine_live/server.log
"""
import os, subprocess, sys, time, urllib.request

try:   # cửa sổ lệnh Windows dùng bảng mã ANSI: in tiếng Việt không làm chết lệnh
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
PORT = int(os.environ.get("SPINE_PORT") or "8781")
URL = f"http://127.0.0.1:{PORT}/api/spine/ping"
LOG_DIR = os.path.join(ROOT, "work", "store", "_sys", "spine_live")


def alive(timeout=1.5):
    try:
        with urllib.request.urlopen(URL, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def start(lan=False):
    os.makedirs(LOG_DIR, exist_ok=True)
    out = open(os.path.join(LOG_DIR, "server_stdout.log"), "ab")
    args = [sys.executable, "-I", os.path.join(HERE, "server.py")] + (["--lan"] if lan else [])
    kw = {}
    if os.name == "nt":   # tách hẳn khỏi tiến trình cha, không có cửa sổ
        kw["creationflags"] = 0x00000008 | 0x00000200 | 0x08000000   # DETACHED_PROCESS | NEW_PROCESS_GROUP | NO_WINDOW
    else:
        kw["start_new_session"] = True
    subprocess.Popen(args, cwd=ROOT, stdout=out, stderr=out, stdin=subprocess.DEVNULL, close_fds=True, **kw)
    for _ in range(60):
        if alive():
            return True
        time.sleep(0.25)
    return False


def main():
    if alive():
        print(f"Spine Live đang chạy: http://127.0.0.1:{PORT}/spine")
    else:
        ok = start("--lan" in sys.argv)
        print(("đã bật" if ok else "KHÔNG bật được (xem server.log / server_stdout.log)") + f" Spine Live: http://127.0.0.1:{PORT}/spine")
        if not ok:
            sys.exit(1)
    if "--hold" in sys.argv:   # giữ cho khung xem trước của app; server chết thì bật lại
        while True:
            time.sleep(5)
            if not alive(3):
                start("--lan" in sys.argv)


if __name__ == "__main__":
    main()
