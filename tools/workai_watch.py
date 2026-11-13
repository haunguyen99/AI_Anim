"""Canh WorkAI: báo khi có thông báo / mission / issue liên quan tới team Anim hoặc tới chủ token.
Claude chạy file này nền (run_in_background): có việc thì in ra rồi thoát = Claude được gọi dậy để báo người dùng,
xong thì chạy lại để canh tiếp. Không tốn lượt AI khi chờ (hỏi API mỗi 60 giây).

  python -I tools/workai_watch.py            # chờ (mặc định tối đa 8 giờ)
  python -I tools/workai_watch.py --once     # chỉ kiểm một lần
  python -I tools/workai_watch.py --scan     # liệt kê mission / issue liên quan hiện có (không đổi mốc)
  python -I tools/workai_watch.py --reset    # đặt lại mốc = bây giờ (bỏ việc cũ)
  python -I tools/workai_watch.py --stream   # chạy liên tục, mỗi việc một dòng, không thoát (chạy bằng Monitor)

Liên quan = giao cho bạn / nhắc tên bạn / cần bạn duyệt, hoặc nội dung có từ khoá anim (animation, rig, skin, FBX, Spine...).
Bỏ qua: tin lịch tự đặt của người khác, sprint bắt đầu / kết thúc, trừ khi có từ khoá anim.
Mốc: work/store/_sys/watch/workai.json ({"seen_notif": [...], "seen_missions": [...], "beat": ...}).
Lần chạy đầu chỉ đặt mốc từ bây giờ, không báo việc cũ.
"""
import json, os, re, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import identity  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools", "workai"))
import workai  # noqa: E402

STATE = identity.state_path(os.path.join(ROOT, "work", "store", "_sys", "watch", "workai.json"))
WAIT = 60
ME = None  # id người dùng của danh tính đang chạy, lấy từ api/auth/me (whoami)
KW = re.compile(r"\banim|animation|\brig\b|rigging|skin weight|\bfbx\b|spine|diễn hoạt|chuyển động|playblast|blocking", re.I)
NOISE = {"self_pinned_on_schedule", "self_rescheduled", "sprint_started", "sprint_completed"}
PERSONAL = re.compile(r"giao cho bạn|nhắc đến bạn|nhắc bạn|mention|duyệt|nghiệm thu|bình luận|comment|review|phê duyệt", re.I)


def load():
    try:
        return json.load(open(STATE, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def save(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    st["beat"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    for k in ("seen_notif", "seen_missions"):
        st[k] = st.get(k, [])[-3000:]
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def whoami():
    global ME
    if ME is None:
        c, o = workai.call("GET", "/api/auth/me")
        try:
            ME = o["data"]["user"]["id"]
        except (TypeError, KeyError):
            raise RuntimeError(f"api/auth/me: {c} {str(o)[:200]}")
    return ME


def get(path):
    whoami()
    c, o = workai.call("GET", path)
    if c != 200 or not isinstance(o, dict) or not o.get("success"):
        raise RuntimeError(f"{path}: {c} {str(o)[:200]}")
    return o


def notif_reason(n):
    d = n.get("data") or {}
    text = " ".join(str(d.get(k) or "") for k in ("title", "body"))
    action = (d.get("action") or "").lower()
    title = (d.get("title") or "")
    if (d.get("actor") or {}).get("id") == ME:
        return None  # own actions (AI acting with the user's token) are not news
    if PERSONAL.search(title) or "assign" in action or "mention" in action or "approv" in action:
        return "cho bạn"
    if KW.search(text):
        return "anim"
    if action in NOISE or "sprint" in (d.get("category") or ""):
        return None
    return None


def mission_reason(m):
    if (m.get("assignee") or {}).get("id") == ME and (m.get("created_by") or {}).get("id") != ME:
        return "giao cho bạn"
    text = " ".join(str(m.get(k) or "") for k in ("summary", "description"))
    if KW.search(text) or "Animation" in ((m.get("epic") or {}).get("name") or ""):
        if (m.get("created_by") or {}).get("id") != ME:
            return "anim"
    return None


def notif_line(n, why):
    d = n.get("data") or {}
    return {"why": why, "kind": "notification", "at": n.get("created_at"), "title": d.get("title"),
            "body": d.get("body"), "from": (d.get("actor") or {}).get("name"),
            "url": "https://workai.horusjsc.com" + (d.get("url") or "")}


def mission_line(m, why):
    return {"why": why, "kind": "mission", "id": m["id"], "project_id": m.get("project_id"),
            "epic": (m.get("epic") or {}).get("name"), "summary": m.get("summary"),
            "by": (m.get("created_by") or {}).get("display_name"),
            "assignee": (m.get("assignee") or {}).get("display_name"), "status": m.get("display_status"),
            "url": f"https://workai.horusjsc.com/missions/{m['id']}"}


def fetch():
    notifs = get("/api/notifications").get("data") or []
    missions = []
    for pg in (1, 2):
        missions += get(f"/api/missions?page={pg}").get("data") or []
    return notifs, missions


def scan():
    hits = []
    for pg in range(1, 40):
        o = get(f"/api/missions?page={pg}")
        for m in o.get("data") or []:
            why = mission_reason(m)
            if why:
                hits.append(mission_line(m, why))
        if pg >= (o.get("meta") or {}).get("last_page", 1):
            break
    o = get(f"/api/issues?assignee_id={ME}")
    for i in o.get("data") or []:
        hits.append({"kind": "issue giao cho bạn", "key": i.get("jira_issue_key"), "summary": i.get("summary"),
                     "status": i.get("status") or i.get("status_name"),
                     "url": f"https://workai.horusjsc.com/issues/{i.get('jira_issue_key')}"})
    print(f"=== WorkAI: {len(hits)} mục liên quan ===")
    for h in hits:
        print(json.dumps(h, ensure_ascii=False))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if "--scan" in args:
        return scan()
    stream = "--stream" in args
    st = load()
    if "--reset" in args or "seen_notif" not in st:
        n, m = fetch()
        st["seen_notif"] = [x["id"] for x in n]
        st["seen_missions"] = [x["id"] for x in m]
        save(st)
        print("Đặt mốc WorkAI từ bây giờ.")
        if "--reset" in args:
            return
    end = time.time() + 8 * 3600
    while True:
        try:
            notifs, missions = fetch()
        except Exception as e:  # network / Cloudflare hiccup: wait and retry
            print(f"lỗi: {e}", file=sys.stderr)
            notifs, missions = [], []
        out = []
        seen_n, seen_m = set(st["seen_notif"]), set(st["seen_missions"])
        for n in notifs:
            if n["id"] in seen_n:
                continue
            st["seen_notif"].append(n["id"])
            why = notif_reason(n)
            if why:
                out.append(notif_line(n, why))
        for m in missions:
            if m["id"] in seen_m:
                continue
            st["seen_missions"].append(m["id"])
            why = mission_reason(m)
            if why:
                out.append(mission_line(m, why))
        save(st)
        if out:
            if stream:  # không thoát: mỗi việc một dòng, dùng với Monitor
                for o in out:
                    print(json.dumps(o, ensure_ascii=False), flush=True)
                time.sleep(WAIT)
                continue
            print(f"=== WorkAI: {len(out)} việc mới liên quan ===")
            for o in out:
                print(json.dumps(o, ensure_ascii=False))
            return
        if "--once" in args:
            print("Không có việc mới.")
            return
        if time.time() > end and not stream:
            print("Hết giờ canh, không có việc mới.")
            return
        time.sleep(WAIT)


if __name__ == "__main__":
    main()
