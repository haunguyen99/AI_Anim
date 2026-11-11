"""Trang quản lý phiên Claude Code: /sessions (tools/home/sessions.html).

API (chỉ máy này, và POST chỉ từ chính trang Home):
  GET  /api/sessions/list            mọi phiên (`claude agents --json --all`) + thông tin phiên con (sổ subsession)
  GET  /api/sessions/detail?id=      báo cáo + log gần nhất của một phiên
  POST /api/sessions/start {name, brief, allow?}   giao việc phiên con mới
  POST /api/sessions/send  {id, message}           nhắn thêm cho phiên con
  POST /api/sessions/stop  {id}                    dừng phiên con
  POST /api/sessions/rm    {id}                    xoá phiên nền (và dòng trong sổ)
Phiên đang mở trong VS Code / app (kind interactive) chỉ xem, không điều khiển.
Việc thật do tools/subsession/subsession.py làm; module này chỉ gọi nó.
"""
import contextlib, importlib.util, io, json, os, re, shutil, subprocess, threading
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
_SS = os.path.join(ROOT, "tools", "subsession", "subsession.py")
_mod = None
_lock = threading.Lock()


def ss():
    global _mod
    if _mod is None:
        spec = importlib.util.spec_from_file_location("subsession_tool", _SS)
        _mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_mod)
    return _mod


def _local(h):
    return h.client_address[0] in ("127.0.0.1", "::1", "::ffff:127.0.0.1")


def _same_origin(h):
    o = h.headers.get("Origin")
    return not o or urlparse(o).netloc == h.headers.get("Host")


def _call(fn, *args, **kw):
    """chạy hàm của subsession (in ra stdout, thoát bằng SystemExit khi lỗi) -> (ok, text)"""
    buf = io.StringIO()
    try:
        with _lock, contextlib.redirect_stdout(buf):
            r = fn(*args, **kw)
        return True, (buf.getvalue().strip() or (r if isinstance(r, str) else ""))
    except SystemExit as e:
        return False, str(e.code if e.code not in (None, 0) else buf.getvalue()).strip()
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def _reg_by_cid(m):
    return {v["cid"][:8]: (k, v) for k, v in m.load().items() if v.get("cid")}


def listing():
    return ss().rows()


def detail(rid):
    return ss().detail(rid)


def _key(rid):
    m = ss()
    k = _reg_by_cid(m).get(rid[:8], (None,))[0]
    if not k:
        raise SystemExit("không phải phiên con do subsession giao (chỉ xem được)")
    return k


def handle_get(h, path, qs):
    if path in ("/sessions", "/sessions/"):
        h.send_bytes(open(os.path.join(HERE, "sessions.html"), "rb").read(), "text/html; charset=utf-8", True)
        return True
    if not path.startswith("/api/sessions/"):
        return False
    if not _local(h):
        h.send_json({"ok": False, "error": "chỉ máy này"}, 403)
        return True
    try:
        if path == "/api/sessions/list":
            h.send_json({"ok": True, "claude": bool(shutil.which("claude")), "rows": listing()})
        elif path == "/api/sessions/detail":
            h.send_json({"ok": True, **detail((qs.get("id") or [""])[0])})
        else:
            return False
    except Exception as e:
        h.send_json({"ok": False, "error": f"{type(e).__name__}: {e}"}, 500)
    return True


def handle_post(h, path, body):
    if not path.startswith("/api/sessions/"):
        return False
    if not _local(h) or not _same_origin(h):
        h.send_json({"ok": False, "error": "chỉ nhận từ trang Home trên máy này"}, 403)
        return True
    import argparse
    m = ss()
    op = path.rsplit("/", 1)[-1]
    try:
        if op == "start":
            name, brief = (body.get("name") or "").strip(), (body.get("brief") or "").strip()
            if not name or not brief or brief.startswith("@"):
                raise SystemExit("cần tên và nội dung việc")
            ok, txt = _call(m.cmd_start, argparse.Namespace(name=name, brief=brief, files=body.get("files"),
                                                             parent=None, max=m.MAX_RUNNING, allow=body.get("allow")))
        elif op == "send":
            k = _key(body.get("id", ""))
            ok, txt = _call(m.cmd_send, argparse.Namespace(id=k, message=body.get("message", "")))
        elif op == "stop":
            ok, txt = _call(m.cmd_stop, argparse.Namespace(id=_key(body.get("id", ""))))
        elif op == "rm":
            k = _key(body.get("id", ""))
            r = m.load()
            subprocess.run([m.CLAUDE, "rm", r[k]["cid"][:8]], capture_output=True, cwd=ROOT)
            r.pop(k, None)
            m.save(r)
            ok, txt = True, "đã xoá"
        else:
            return False
    except SystemExit as e:
        ok, txt = False, str(e.code)
    h.send_json({"ok": ok, "text" if ok else "error": txt}, 200 if ok else 400)
    return True
