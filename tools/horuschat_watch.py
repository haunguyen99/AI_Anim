"""Canh HorusChat: báo khi có người tag (mention) chủ key, trả lời tin của chủ key, nhắn riêng (DM), mời vào phòng,
hoặc nhắn trong thread chủ key đã tham gia (đã nhắn / được tag trong thread đó; danh sách ở mốc, khoá "threads").
Claude chạy file này nền (run_in_background): có tin thì in ra rồi thoát = Claude được gọi dậy để báo người dùng,
xong thì chạy lại để canh tiếp. Không tốn lượt AI khi chờ (long-poll /v1/developer/events, mỗi lần chờ 30 giây).

  python tools/horuschat_watch.py            # chờ (mặc định tối đa 8 giờ)
  python tools/horuschat_watch.py --once     # chỉ kiểm một lần
  python tools/horuschat_watch.py --reset    # đặt lại mốc = bây giờ (bỏ tin cũ)
  python tools/horuschat_watch.py --stream   # chạy liên tục, mỗi tin một dòng, không thoát (chạy bằng Monitor)

Mốc: work/store/_sys/watch/horuschat.json ({"cursor": ..., "beat": giờ kiểm cuối}).
Lần chạy đầu chỉ đặt mốc từ bây giờ, không báo tin cũ.
"""
import json, os, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "horuschat_mcp"))
from horuschat_mcp.client import HCError, HorusChat, q, slim  # noqa: E402

STATE = os.path.join(ROOT, "work", "store", "_sys", "watch", "horuschat.json")
WAIT = 30


def load():
    try:
        return json.load(open(STATE, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def save(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    st["beat"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    for i in range(10):  # Windows: file may be briefly locked by another reader
        try:
            os.replace(tmp, STATE)
            return
        except PermissionError:
            if i == 9:
                return  # skip this beat, try again next loop
            time.sleep(0.3)


def reason(hc, me, ev, cache):
    """Why this event concerns the key owner, or None."""
    t = ev.get("type")
    room = ev.get("room") or {}
    if t == "invite":
        return "mời vào phòng"
    if t != "message":
        return None
    m = ev.get("message") or {}
    mt = m.get("mentions") or {}
    if me["user_id"] in (mt.get("user_ids") or []):
        return "tag bạn"
    if room.get("is_direct"):
        return "nhắn riêng"
    body = (m.get("body") or "").lower()
    local = me["user_id"].split(":")[0].lower()             # @haunv
    if local in body or (me.get("display_name") and me["display_name"].lower() in body):
        return "nhắc tên bạn"
    if mt.get("room"):
        return "tag cả phòng (@room)"
    rid = m.get("reply_to_event_id")
    if rid:
        key = (ev.get("room_id"), rid)
        if key not in cache:
            try:
                src = hc.get(f"/v1/developer/rooms/{q(ev['room_id'])}/events/{q(rid)}")
                cache[key] = (src.get("sender") or {}).get("user_id")
            except HCError:
                cache[key] = None
        if cache[key] == me["user_id"]:
            return "trả lời tin của bạn"
    return None


def thread_of(ev):
    """Thread root id of a message (or the message itself when it starts a thread)."""
    m = ev.get("message") or {}
    return m.get("thread_root_event_id") or None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    once = "--once" in args
    stream = "--stream" in args
    hc = HorusChat()
    for i in range(60):  # server hiccup at start (HTTP 5xx, DNS): retry up to ~30 min
        try:
            me = hc.me()
            break
        except HCError as e:
            print(f"lỗi: {e}", file=sys.stderr)
            time.sleep(30)
    else:
        raise SystemExit("HorusChat không phản hồi sau 30 phút.")
    st = {} if "--reset" in args else load()
    cache = {}
    if not st.get("cursor"):
        r = hc.get("/v1/developer/events", after="now", wait=0, limit=1)
        st["cursor"] = r.get("next_cursor")
        save(st)
        print(f"Đặt mốc canh cho {me.get('display_name')} ({me['user_id']}) từ bây giờ.")
        if once:
            return
    deadline = time.time() + 8 * 3600
    while True:
        try:
            r = hc.call("GET", "/v1/developer/events", params={
                "after": st["cursor"], "wait": 0 if once else WAIT, "limit": 200,
                "addressed_only": False, "include_own": True}, timeout=WAIT + 20)
        except HCError as e:
            if e.code == "cursor_expired" or e.status == 410:
                print("Mốc hết hạn (máy tắt lâu?), đặt lại từ bây giờ; tin trong khoảng trống chưa được kiểm.")
                st.pop("cursor", None)
                r = hc.get("/v1/developer/events", after="now", wait=0, limit=1)
                st["cursor"] = r.get("next_cursor")
                save(st)
                continue
            if e.status == 429:
                time.sleep(max(e.retry_after, 5))
                continue
            if e.status in (401, 403):
                sys.exit(f"Key bị từ chối: {e}")
            print(f"lỗi: {e}", file=sys.stderr)
            time.sleep(15)
            continue
        found = []
        threads = set(st.get("threads") or [])
        for ev in r.get("events") or []:
            troot = thread_of(ev)
            if (ev.get("sender") or {}).get("user_id") == me["user_id"]:
                if troot:
                    threads.add(troot)   # thread bạn đã nhắn -> theo dõi tiếp
                continue
            why = reason(hc, me, ev, cache)
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
        if found:
            if stream:  # không thoát: mỗi tin một dòng, dùng với Monitor để Claude được gọi dậy từng tin
                for why, ev in found:
                    print(json.dumps({"why": why, **slim(ev)}, ensure_ascii=False), flush=True)
                continue
            print(f"=== HorusChat: {len(found)} tin mới cho {me.get('display_name')} ===")
            for why, ev in found:
                print(json.dumps({"why": why, **slim(ev)}, ensure_ascii=False))
            if not r.get("has_more"):
                return
            continue
        if r.get("has_more"):
            continue
        if once or (time.time() > deadline and not stream):
            print("Không có tin mới.")
            return


if __name__ == "__main__":
    main()
