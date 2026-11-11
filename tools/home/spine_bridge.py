"""Cầu nối Claude <-> Spine Live (2026-10-31): Claude gửi lệnh có tên, trang Spine Live đang mở chạy bằng runtime Spine thật
rồi trả kết quả. Cùng kiểu với studio_bridge.py.

Trang (tools/spine_live/bridge.js) long-poll   GET  /api/spine/br/poll?cid=…&vis=1
                          trả kết quả          POST /api/spine/br/result {id, ok, result | error}
Claude (tools/spine_live_cmd.py pose | measure | snap) gửi lệnh, chờ   POST /api/spine/br/cmd {op, args, timeout?}
Trang đang nối                                 GET  /api/spine/br/clients
An toàn: trang chỉ làm các lệnh có tên trong bridge.js (không eval); /cmd và /result chỉ nhận JSON từ chính máy này.
Lý do (tự đánh giá Spine Live 2026-10-31): mỗi lần kiểm anim Claude phải tự viết đoạn JS dài nạp skeleton + atlas
qua công cụ trình duyệt; render_spine.py không hiểu inherit / IK nên ảnh xem trước sai.
"""
import itertools
import threading
import time

POLL_WAIT = 25
ALIVE = POLL_WAIT + 10

_lock = threading.Condition()
_clients = {}       # cid -> {seen, vis, waiting, cmd}
_results = {}
_ids = itertools.count(1)


def _alive():
    now = time.time()
    for cid in [c for c, v in _clients.items() if now - v["seen"] > ALIVE]:
        del _clients[cid]
    return _clients


def clients():
    with _lock:
        return [{"cid": c, "visible": v["vis"], "idle_s": round(time.time() - v["seen"], 1)}
                for c, v in sorted(_alive().items(), key=lambda kv: (not kv[1]["vis"], -kv[1]["seen"]))]


def poll(cid, vis):
    end = time.time() + POLL_WAIT
    with _lock:
        c = _clients.setdefault(cid, {"cmd": None})
        c.update(seen=time.time(), vis=vis, waiting=True)
        _lock.notify_all()
        while c.get("cmd") is None and time.time() < end:
            _lock.wait(end - time.time())
        c["waiting"] = False
        c["seen"] = time.time()
        cmd, c["cmd"] = c.get("cmd"), None
        return cmd


def result(body):
    with _lock:
        _results[body.get("id")] = body
        _lock.notify_all()


def send(op, args=None, timeout=30.0):
    t0 = time.time()
    with _lock:
        while True:
            live = _alive()
            cands = sorted(live.items(), key=lambda kv: (not kv[1]["vis"], not kv[1].get("waiting"), -kv[1]["seen"]))
            pick = cands[0][0] if cands else None
            if pick and live[pick].get("waiting") and live[pick].get("cmd") is None:
                break
            if time.time() - t0 > 3:
                return {"ok": False, "error": "Không có trang Spine Live nào đang mở (mở http://127.0.0.1:8780/spine)"
                        if not live else "Trang Spine Live bận hoặc không phản hồi"}
            _lock.wait(0.1)
        i = next(_ids)
        live[pick]["cmd"] = {"id": i, "op": op, "args": args or {}}
        _lock.notify_all()
        end = t0 + timeout
        while i not in _results and time.time() < end:
            _lock.wait(end - time.time())
        r = _results.pop(i, None)
    if r is None:
        return {"ok": False, "error": f"Hết {timeout:g} s mà trang chưa trả lời", "cid": pick}
    r = {k: v for k, v in r.items() if k != "id"}
    r.update(cid=pick, ms=round((time.time() - t0) * 1000, 1))
    return r


LOCAL_ORIGINS = ("http://127.0.0.1", "http://localhost")


def local_json(h):
    if not (h.headers.get("Content-Type") or "").startswith("application/json"):
        return False
    o = h.headers.get("Origin")
    return o is None or any(o == b or o.startswith(b + ":") for b in LOCAL_ORIGINS)


def handle_get(h, path, q):
    g = lambda k, d="": (q.get(k) or [d])[0]
    if path == "/api/spine/br/poll":
        h.send_json(poll(g("cid"), g("vis") == "1") or {"op": None})
        return True
    if path == "/api/spine/br/bye":
        with _lock:
            _clients.pop(g("cid"), None)
            _lock.notify_all()
        h.send_json({"ok": True})
        return True
    if path == "/api/spine/br/clients":
        h.send_json(clients())
        return True
    return False


def handle_post(h, path, body):
    if path == "/api/spine/br/result":
        if not local_json(h):
            h.send_json({"ok": False}, 403)
            return True
        result(body)
        h.send_json({"ok": True})
        return True
    if path == "/api/spine/br/cmd":
        if not local_json(h):
            h.send_json({"ok": False, "error": "Chỉ nhận lệnh JSON từ chính máy này"}, 403)
            return True
        h.send_json(send(body.get("op"), body.get("args"), float(body.get("timeout") or 30)))
        return True
    return False
