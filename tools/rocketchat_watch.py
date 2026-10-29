"""Canh kênh Rocket.Chat (ROCKETCHAT_WATCH trong tools/rocketchat_mcp/.env, vd AI_StudioSupport): chờ tới khi có tin
mới của người khác (bỏ qua tin trả lời của AI, bắt đầu bằng "🤖 AI:"), in ra rồi thoát; cũng bắt yêu cầu thêm ảnh ở trang Key Pose (/keypose). Claude chạy file này nền
(run_in_background): thoát = Claude được gọi dậy để đọc góp ý, xong thì chạy lại để canh tiếp.
Không tốn lượt AI khi chờ (chỉ gọi REST API mỗi 15 giây).

  python tools/rocketchat_watch.py              # chờ (mặc định tối đa 8 giờ)
  python tools/rocketchat_watch.py --once       # chỉ kiểm một lần
  python tools/rocketchat_watch.py --rooms A,B  # canh kênh khác

Mốc đã đọc: work/store/_sys/watch/rocketchat.json ({kênh: ts tin cuối đã báo}). Lần chạy đầu chỉ ghi mốc, không báo tin cũ.
"""
import json, os, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "rocketchat_mcp"))
from rocketchat_mcp.client import RCError, RocketChat, slim  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
from notes_watch import keypose_pending  # noqa: E402  (yêu cầu thêm ảnh ở trang Key Pose)

STATE = os.path.join(ROOT, "work", "store", "_sys", "watch", "rocketchat.json")
POLL = 15
AI_TAG = "🤖 AI:"


def load():
    try:
        return json.load(open(STATE, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def save(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    once = "--once" in args
    rc = RocketChat()
    rooms = rc.watch
    if "--rooms" in args:
        rooms = [r.strip().lstrip("#") for r in args[args.index("--rooms") + 1].split(",") if r.strip()]
    if not rooms:
        sys.exit("Chưa có kênh canh: đặt ROCKETCHAT_WATCH trong tools/rocketchat_mcp/.env")
    rc.get("me")   # kiểm token
    st = load()
    deadline = time.time() + 8 * 3600
    while True:
        found = []
        for room in rooms:
            try:
                msgs = rc.history(room, count=50, oldest=st.get(room))
            except RCError as e:
                print(f"[{room}] lỗi: {e}", file=sys.stderr)
                continue
            msgs = sorted(msgs, key=lambda m: m.get("ts", ""))
            if room not in st:          # lần đầu: chỉ đặt mốc
                st[room] = msgs[-1]["ts"] if msgs else time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
                continue
            new = [m for m in msgs if m.get("ts", "") > st[room]]
            if new:
                st[room] = new[-1]["ts"]
                others = [m for m in new if not (m.get("msg") or "").startswith(AI_TAG) and not m.get("t")]   # token = tài khoản người dùng: chỉ bỏ tin AI
                if others:
                    found.append((room, others))
        save(st)
        kp = keypose_pending()
        if kp:
            now = time.strftime("%Y-%m-%dT%H:%M:%S")
            for f, d in kp:
                d["picked"] = now; d["status"] = "picked"
                json.dump(d, open(f, "w", encoding="utf8"), ensure_ascii=False)
                print("=== Key Pose: yêu cầu mới ===")
                print(json.dumps({"kind": "keypose_req", "id": os.path.basename(f)[:-5], **{k: d.get(k) for k in ("job", "key", "base", "n", "by", "text")}}, ensure_ascii=False))
        if found:
            for room, msgs in found:
                print(f"=== #{room}: {len(msgs)} tin mới ===")
                for m in msgs:
                    print(json.dumps(slim(m), ensure_ascii=False))
            return
        if kp:
            return
        if once or time.time() > deadline:
            print("Không có tin mới.")
            return
        time.sleep(POLL)


if __name__ == "__main__":
    main()
