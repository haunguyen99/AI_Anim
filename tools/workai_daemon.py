"""Bộ canh WorkAI chạy ngầm từ lúc mở máy (không cần phiên Claude).

Hỏi WorkAI mỗi 60 giây, dùng đúng bộ lọc của tools/workai_watch.py. Có việc mới liên quan thì:
  - hiện thông báo Windows (balloon ở khay hệ thống),
  - ghi thêm một dòng JSON vào work/store/_sys/watch/workai_inbox.jsonl (Claude đọc được khi mở phiên).
Mốc riêng: work/store/_sys/watch/workai_daemon.json (không đụng mốc của workai_watch.py).
Nhật ký: work/store/_sys/watch/workai_daemon.log.  Chỉ cho một bản chạy (khoá workai_daemon.lock).

  pythonw -I tools/workai_daemon.py            # chạy mãi
  python  -I tools/workai_daemon.py --once     # kiểm một lần rồi thoát
Cài tự chạy khi đăng nhập Windows: tools/workai_daemon_install.ps1 (-Remove để gỡ).
"""
import json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import identity  # noqa: E402
import workai_watch as W  # noqa: E402

D = os.path.join(ROOT, "work", "store", "_sys", "watch")
STATE = identity.state_path(os.path.join(D, "workai_daemon.json"))
INBOX = identity.state_path(os.path.join(D, "workai_inbox.jsonl"))
LOG = identity.state_path(os.path.join(D, "workai_daemon.log"))
LOCK = identity.state_path(os.path.join(D, "workai_daemon.lock"))


def log(msg):
    os.makedirs(D, exist_ok=True)
    with open(LOG, "a", encoding="utf8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")
    try:  # giữ nhật ký gọn
        if os.path.getsize(LOG) > 500_000:
            lines = open(LOG, encoding="utf8").read().splitlines()[-500:]
            open(LOG, "w", encoding="utf8").write("\n".join(lines) + "\n")
    except OSError:
        pass


def toast(title, body):
    ps = ("Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
          "$n=New-Object System.Windows.Forms.NotifyIcon;$n.Icon=[System.Drawing.SystemIcons]::Information;"
          "$n.Visible=$true;$n.BalloonTipTitle=$env:WA_T;$n.BalloonTipText=$env:WA_B;$n.ShowBalloonTip(10000);"
          "Start-Sleep -Seconds 12;$n.Dispose()")
    env = dict(os.environ, WA_T=title[:60], WA_B=body[:250])
    try:
        subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps], env=env,
                         creationflags=0x08000000)  # CREATE_NO_WINDOW
    except OSError as e:
        log(f"toast lỗi: {e}")


def lock():
    os.makedirs(D, exist_ok=True)
    try:
        old = int(open(LOCK).read().strip())
        out = subprocess.run(["tasklist", "/FI", f"PID eq {old}", "/NH"], capture_output=True, text=True).stdout
        if str(old) in out and old != os.getpid():
            return False
    except (OSError, ValueError):
        pass
    open(LOCK, "w").write(str(os.getpid()))
    return True


def load():
    try:
        return json.load(open(STATE, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def save(st):
    st["beat"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    for k in ("seen_notif", "seen_missions"):
        st[k] = st.get(k, [])[-3000:]
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def step(st):
    notifs, missions = W.fetch()
    out = []
    seen_n, seen_m = set(st["seen_notif"]), set(st["seen_missions"])
    for n in notifs:
        if n["id"] in seen_n:
            continue
        st["seen_notif"].append(n["id"])
        why = W.notif_reason(n)
        if why:
            out.append(W.notif_line(n, why))
    for m in missions:
        if m["id"] in seen_m:
            continue
        st["seen_missions"].append(m["id"])
        why = W.mission_reason(m)
        if why:
            out.append(W.mission_line(m, why))
    return out


def main():
    once = "--once" in sys.argv
    if not once and not lock():
        return
    st = load()
    if "seen_notif" not in st:  # lần đầu: đặt mốc từ bây giờ
        n, m = W.fetch()
        st["seen_notif"], st["seen_missions"] = [x["id"] for x in n], [x["id"] for x in m]
        save(st)
        log("đặt mốc ban đầu")
    log("bắt đầu canh")
    while True:
        try:
            out = step(st)
            save(st)
            for o in out:
                with open(INBOX, "a", encoding="utf8") as f:
                    f.write(json.dumps(o, ensure_ascii=False) + "\n")
                title = o.get("title") or o.get("summary") or "WorkAI"
                toast("WorkAI: " + title, (o.get("body") or o.get("epic") or "") + " " + o.get("url", ""))
                log("báo: " + title)
        except Exception as e:  # mạng / Cloudflare chập chờn: chờ rồi thử lại
            log(f"lỗi: {e}")
        if once:
            print("done")
            return
        time.sleep(W.WAIT)


if __name__ == "__main__":
    main()
