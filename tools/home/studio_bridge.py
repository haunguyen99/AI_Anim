"""Cầu nối Claude ↔ Studio: Claude gửi lệnh qua server Home, trang Studio đang mở (Chrome hay trình duyệt trong app) thực hiện rồi trả kết quả.

Trang Studio (tools/studio/modules/bridge.js) long-poll   GET  /api/studio/poll?cid=…&vis=1&char=…&ws=…
                                    trả kết quả           POST /api/studio/result {id, ok, result | error}
Claude (tools/studio_cmd.py) gửi lệnh, chờ kết quả        POST /api/studio/cmd    {op, args, cid?, timeout?}
Danh sách trang đang nối                                  GET  /api/studio/clients
Lệnh đi tới trang đang hiện (tab đang xem) poll gần nhất, hoặc trang có cid chỉ định. Chỉ nghe 127.0.0.1 như server Home.
An toàn: trang chỉ làm các lệnh có tên trong bridge.js (không có eval); /cmd và /result chỉ nhận JSON từ chính máy này (chặn trang web lạ).
"""
import itertools
import threading
import time

POLL_WAIT = 25      # giây trang chờ mỗi lượt long-poll
ALIVE = POLL_WAIT + 10

_lock = threading.Condition()
_clients = {}       # cid -> {seen, vis, char, ws, waiting, cmd}
_results = {}       # id lệnh -> kết quả
_ids = itertools.count(1)


def _alive():
    now = time.time()
    for cid in [c for c, v in _clients.items() if now - v["seen"] > ALIVE]:
        del _clients[cid]
    return _clients


def clients():
    with _lock:
        return [{"cid": c, "visible": v["vis"], "char": v["char"], "ws": v["ws"], "idle_s": round(time.time() - v["seen"], 1)}
                for c, v in sorted(_alive().items(), key=lambda kv: (not kv[1]["vis"], -kv[1]["seen"]))]


def poll(cid, vis, char, ws):
    """Trang chờ lệnh. Trả lệnh {id, op, args} hoặc None khi hết giờ."""
    end = time.time() + POLL_WAIT
    with _lock:
        c = _clients.setdefault(cid, {"cmd": None})
        c.update(seen=time.time(), vis=vis, char=char, ws=ws, waiting=True)
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


def send(op, args=None, cid=None, timeout=10.0):
    """Gửi một lệnh tới trang Studio và chờ kết quả (dict: ok, result | error, cid, ms)."""
    t0 = time.time()
    with _lock:
        # chờ tối đa 2 s cho trang quay lại long-poll (vừa xong lệnh trước)
        while True:
            live = _alive()
            pick = cid if cid in live else None
            if pick is None and not cid:
                cands = sorted(live.items(), key=lambda kv: (not kv[1]["vis"], not kv[1].get("char"), not kv[1].get("waiting"), -kv[1]["seen"]))
                pick = cands[0][0] if cands else None
            if pick and live[pick].get("waiting") and live[pick].get("cmd") is None:
                break
            if time.time() - t0 > 2:
                return {"ok": False, "error": "Không có trang Studio nào đang mở" if not live else "Trang Studio bận hoặc không phản hồi"}
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
    """Chặn trang web lạ gửi lệnh (CSRF): phải là JSON, và nếu có Origin thì là chính server Home trên máy này."""
    if not (h.headers.get("Content-Type") or "").startswith("application/json"):
        return False
    o = h.headers.get("Origin")
    return o is None or any(o == b or o.startswith(b + ":") for b in LOCAL_ORIGINS)


def handle_get(h, path, q):
    """Gọi từ server.do_GET. Trả True nếu đã xử lý."""
    if path == "/api/studio/poll":
        g = lambda k, d="": (q.get(k) or [d])[0]
        cmd = poll(g("cid"), g("vis") == "1", g("char"), g("ws"))
        h.send_json(cmd or {"op": None})
        return True
    if path == "/api/studio/hello":   # trang báo đổi nhân vật / workspace / tab đang xem
        g = lambda k, d="": (q.get(k) or [d])[0]
        with _lock:
            c = _clients.get(g("cid"))
            if c:
                c.update(vis=g("vis") == "1", char=g("char"), ws=g("ws"), seen=time.time())
        h.send_json({"ok": True})
        return True
    if path == "/api/studio/bye":     # đóng / rời trang: không gửi lệnh tới nó nữa
        with _lock:
            _clients.pop((q.get("cid") or [""])[0], None)
            _lock.notify_all()
        h.send_json({"ok": True})
        return True
    if path == "/api/studio/clients":
        h.send_json(clients())
        return True
    return False


def handle_post(h, path, body):
    if path == "/api/studio/result":
        if not local_json(h):
            h.send_json({"ok": False}, 403)
            return True
        result(body)
        h.send_json({"ok": True})
        return True
    if path == "/api/studio/cmd":
        if not local_json(h):
            h.send_json({"ok": False, "error": "Chỉ nhận lệnh JSON từ chính máy này"}, 403)
            return True
        h.send_json(send(body.get("op"), body.get("args"), body.get("cid"), float(body.get("timeout") or 10)))
        return True
    return False
