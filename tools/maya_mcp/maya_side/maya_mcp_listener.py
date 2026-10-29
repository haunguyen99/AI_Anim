"""Listener chạy BÊN TRONG Maya 2024 để MCP server (tools/maya_mcp) gửi lệnh Python sang.

Bật trong Maya (Script Editor, tab Python):
    import sys; sys.path.insert(0, r"E:/AI Animation/tools/maya_mcp/maya_side")
    import maya_mcp_listener; maya_mcp_listener.start()

Tắt:  maya_mcp_listener.stop()

Giao thức: mỗi yêu cầu là một dòng JSON {"code": "...", "mode": "exec"|"eval"},
trả về một dòng JSON {"ok", "result", "stdout", "error"}.
Chỉ nghe trên 127.0.0.1 (máy này), cổng mặc định 7022.
Code chạy ở luồng chính của Maya (executeInMainThreadWithResult), chung namespace __main__
nên biến giữ lại giữa các lần gọi. Trong code exec, gán biến `result` để trả giá trị về.
"""
from __future__ import annotations

import io
import json
import socket
import threading
import traceback
from contextlib import redirect_stdout

import maya.utils

HOST = "127.0.0.1"
PORT = 7022

_server: socket.socket | None = None
_thread: threading.Thread | None = None
_running = False
_direct = False  # True in mayapy/batch: run on the calling thread (no GUI event loop)


def _jsonable(v):
    try:
        json.dumps(v)
        return v
    except TypeError:
        if isinstance(v, (list, tuple, set)):
            return [_jsonable(x) for x in v]
        if isinstance(v, dict):
            return {str(k): _jsonable(x) for k, x in v.items()}
        return repr(v)


def _run(code: str, mode: str) -> dict:
    import __main__
    ns = __main__.__dict__
    buf = io.StringIO()
    out = {"ok": True, "result": None, "stdout": "", "error": None}
    try:
        with redirect_stdout(buf):
            if mode == "eval":
                out["result"] = _jsonable(eval(code, ns))
            else:
                ns.pop("result", None)
                exec(compile(code, "<maya_mcp>", "exec"), ns)
                out["result"] = _jsonable(ns.get("result"))
    except Exception:
        out["ok"] = False
        out["error"] = traceback.format_exc()
    out["stdout"] = buf.getvalue()[-20000:]
    return out


def _handle(conn: socket.socket) -> None:
    with conn:
        f = conn.makefile("rwb")
        for line in f:
            if not line.strip():
                continue
            try:
                req = json.loads(line.decode("utf-8"))
                args = (req.get("code", ""), req.get("mode", "exec"))
                res = _run(*args) if _direct else                     maya.utils.executeInMainThreadWithResult(_run, *args)
            except Exception:
                res = {"ok": False, "result": None, "stdout": "",
                       "error": traceback.format_exc()}
            f.write((json.dumps(res) + "\n").encode("utf-8"))
            f.flush()


def _loop() -> None:
    while _running and _server is not None:
        try:
            conn, _ = _server.accept()
        except OSError:
            break
        threading.Thread(target=_handle, args=(conn,), daemon=True).start()


def start(port: int = PORT, block: bool = False) -> None:
    """block=True for mayapy/batch: serve on this thread, one client at a time, until stop()."""
    global _server, _thread, _running, _direct
    if _running:
        print(f"[maya_mcp] already running on {HOST}:{port}")
        return
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, port))
    s.listen(4)
    _server, _running = s, True
    if block:
        _direct = True
        print(f"[maya_mcp] listener on {HOST}:{port} (blocking)")
        while _running:
            try:
                conn, _ = s.accept()
            except OSError:
                break
            _handle(conn)
        return
    _thread = threading.Thread(target=_loop, daemon=True)
    _thread.start()
    print(f"[maya_mcp] listener on {HOST}:{port}")


def stop() -> None:
    global _server, _running
    _running = False
    if _server is not None:
        try:
            _server.close()
        finally:
            _server = None
    print("[maya_mcp] listener stopped")
