"""Bộ canh HorusChat chạy ngầm từ lúc mở máy (không cần phiên Claude). Chỉ ĐỌC, không đăng gì lên HorusChat.

Dùng đúng bộ lọc của tools/horuschat_watch.py (tag, nhắn riêng, nhắc tên, trả lời tin của bạn, thread đã tham gia, lời mời).
Có tin mới liên quan thì: hiện thông báo Windows + ghi một dòng JSON vào work/store/_sys/watch/horuschat_inbox.jsonl.
Mốc riêng: horuschat_daemon.json (không đụng mốc của horuschat_watch.py); nhật ký horuschat_daemon.log; một bản chạy (khoá).

  pythonw -I tools/horuschat_daemon.py        # chạy mãi
  python  -I tools/horuschat_daemon.py --once # kiểm một lần rồi thoát
Cài tự chạy khi đăng nhập Windows: tools/horuschat_daemon_install.ps1 (-Remove để gỡ).
"""
import json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import identity  # noqa: E402
import horuschat_watch as W  # noqa: E402
import workai_daemon as D  # noqa: E402  (dùng lại toast)
from horuschat_watch import HCError, HorusChat, slim  # noqa: E402

DIR = os.path.join(ROOT, "work", "store", "_sys", "watch")
STATE = identity.state_path(os.path.join(DIR, "horuschat_daemon.json"))
INBOX = identity.state_path(os.path.join(DIR, "horuschat_inbox.jsonl"))
LOG = identity.state_path(os.path.join(DIR, "horuschat_daemon.log"))
LOCK = identity.state_path(os.path.join(DIR, "horuschat_daemon.lock"))


def log(msg):
    os.makedirs(DIR, exist_ok=True)
    with open(LOG, "a", encoding="utf8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")
    try:
        if os.path.getsize(LOG) > 500_000:
            lines = open(LOG, encoding="utf8").read().splitlines()[-500:]
            open(LOG, "w", encoding="utf8").write("\n".join(lines) + "\n")
    except OSError:
        pass


def lock():
    os.makedirs(DIR, exist_ok=True)
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
    os.makedirs(DIR, exist_ok=True)
    st["beat"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def new_cursor(hc, st):
    r = hc.get("/v1/developer/events", after="now", wait=0, limit=1)
    st["cursor"] = r.get("next_cursor")
    save(st)


def main():
    once = "--once" in sys.argv
    if not once and not lock():
        return
    hc, me = HorusChat(), None
    while me is None:  # server / mạng chập chờn lúc mở máy: thử lại
        try:
            me = hc.me()
        except Exception as e:
            log(f"chưa vào được HorusChat: {e}")
            if once:
                return
            time.sleep(30)
    st, cache = load(), {}
    if not st.get("cursor"):
        new_cursor(hc, st)
        log("đặt mốc ban đầu")
    log("bắt đầu canh " + me["user_id"])
    while True:
        try:
            r = hc.call("GET", "/v1/developer/events", params={
                "after": st["cursor"], "wait": 0 if once else W.WAIT, "limit": 200,
                "addressed_only": False, "include_own": True}, timeout=W.WAIT + 20)
            found, threads = [], set(st.get("threads") or [])
            for ev in r.get("events") or []:
                troot = W.thread_of(ev)
                if (ev.get("sender") or {}).get("user_id") == me["user_id"]:
                    if troot:
                        threads.add(troot)
                    continue
                why = W.reason(hc, me, ev, cache)
                if not why and troot and troot in threads:
                    why = "tin trong thread bạn tham gia"
                if why:
                    if troot:
                        threads.add(troot)
                    found.append((why, ev))
            st["threads"] = sorted(threads)[-500:]
            if r.get("next_cursor"):
                st["cursor"] = r["next_cursor"]
            save(st)
            for why, ev in found:
                o = {"why": why, **slim(ev)}
                with open(INBOX, "a", encoding="utf8") as f:
                    f.write(json.dumps(o, ensure_ascii=False) + "\n")
                D.toast(f"HorusChat: {why} · {o.get('from')}", (o.get("text") or "")[:200])
                log(f"báo: {why} từ {o.get('from')}")
            if r.get("has_more"):
                continue
        except HCError as e:
            if e.code == "cursor_expired" or e.status == 410:
                log("mốc hết hạn, đặt lại từ bây giờ")
                try:
                    new_cursor(hc, st)
                except Exception as e2:
                    log(f"lỗi đặt mốc: {e2}")
                continue
            if e.status == 429:
                time.sleep(max(e.retry_after, 5))
                continue
            if e.status in (401, 403):
                log(f"key bị từ chối: {e}")
                return
            log(f"lỗi: {e}")
            time.sleep(15)
        except Exception as e:
            log(f"lỗi: {e}")
            time.sleep(15)
        if once:
            print("done")
            return


if __name__ == "__main__":
    main()
