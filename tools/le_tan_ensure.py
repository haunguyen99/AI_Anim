"""Bảo đảm phiên lễ tân HorusChat (Paseo, tên 'le-tan') đang chạy. Gọi lúc đăng nhập (systemd user service), chạy tay cũng được.

  python3 -I tools/le_tan_ensure.py            # chờ Paseo sẵn sàng (tối đa 10 phút), rồi: đang chạy thì thôi; idle thì nhắn tiếp tục; mất / đóng thì tạo lại
  python3 -I tools/le_tan_ensure.py --check    # chỉ báo trạng thái

Tắt lễ tân tự bật: tạo file work/store/_sys/watch/le_tan_off (xóa file để bật lại).
Phiên lễ tân đọc brief tools/subsession/briefs/horuschat_intake.md (bản Linux: python3 thay .venv/Scripts/python.exe).
"""
import json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OFF = os.path.join(ROOT, "work", "store", "_sys", "watch", "le_tan_off")
NAME = "le-tan"
NUDGE = ("Máy vừa khởi động lại / phiên vừa được bật lại. Tiếp tục vai lễ tân: chạy jobs.py ls, rồi vòng lặp "
         "horuschat_cli.py wait --timeout 60 (workai_watch.py --once chỉ khi wait hết hạn) như brief. Không trả lời lại tin cũ đã xử lý (xem work/store/_sys/watch/horuschat_jobs_ai.md).")


def agents():
    p = subprocess.run(["paseo", "ls", "--json"], capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        return None
    d = json.loads(p.stdout or "[]")
    return d if isinstance(d, list) else d.get("agents", [])


def main():
    if os.path.exists(OFF):
        print("lễ tân tắt (có file le_tan_off)")
        return 0
    ag = None
    started = False
    for _ in range(60):  # chờ daemon Paseo lên (10 phút)
        try:
            ag = agents()
        except (OSError, ValueError, subprocess.SubprocessError):
            ag = None
        if ag is not None:
            break
        if not started:  # daemon Paseo chưa chạy: thử bật (app Paseo không cần mở)
            started = True
            subprocess.run(["paseo", "start"], capture_output=True, text=True, timeout=60)
        time.sleep(10)
    if ag is None:
        print("Paseo chưa chạy")
        return 1
    mine = [a for a in ag if a.get("name") == NAME]
    live = [a for a in mine if a.get("status") in ("running", "idle")]
    if "--check" in sys.argv:
        print(json.dumps([{k: a.get(k) for k in ("shortId", "status")} for a in mine]))
        return 0
    if any(a["status"] == "running" for a in live):
        print("lễ tân đang chạy")
        return 0
    if live:
        sid = live[0]["shortId"]
        subprocess.run(["paseo", "send", "--no-wait", sid, NUDGE], capture_output=True, text=True, timeout=60)
        print("đã nhắn lễ tân tiếp tục:", sid)
        return 0
    body = open(os.path.join(ROOT, "tools", "subsession", "briefs", "horuschat_intake.md"), encoding="utf-8").read()
    body = f"> Máy Linux: thay mọi `.venv/Scripts/python.exe` bằng `python3` (vẫn có -I). Dự án: {ROOT}.\n\n" + body.replace(".venv/Scripts/python.exe", "python3")
    tmp = os.path.join(ROOT, "work", "_subsessions", "le-tan-body.md")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    open(tmp, "w", encoding="utf-8").write(body)
    p = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "paseo_cmd.py"), "run", NAME, "@" + tmp],
                       capture_output=True, text=True, timeout=120)
    print((p.stdout + p.stderr).strip())
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
