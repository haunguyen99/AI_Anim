"""Run Python inside a SECOND Frolvy instance on another MCP port, so two Claude sessions can use Frolvy in parallel
(user 2026-11-03: "Sao không chạy song song"). Frolvy reads env DCC_MCP_PORT (app and Frolvy-mcp.exe); the
session's own `frolvy` MCP server stays on 9877.

Start a second Frolvy (PowerShell):
    $env:DCC_MCP_PORT="9878"; Start-Process "C:\\Program Files\\Frolvy\\Frolvy.exe"; Remove-Item Env:DCC_MCP_PORT
Run code there:
    python tools/frolvy_port.py 9878 script.py        (or "-" to read code from stdin)
Prints the tool result (output / value / traceback). Timeout per call: --timeout seconds (default 900).

One-command jobs (tools/frolvy_plugins/anim_ops), plain-text result, the port is optional (env DCC_MCP_PORT, else 9877):
    python tools/frolvy_port.py scene               open file (* = unsaved), frames, layers, ref clips, keyed nodes
    python tools/frolvy_port.py keys Scarf          key table of the nodes whose name contains Scarf
    python tools/frolvy_port.py clear Scarf         delete all their keys + controls back to the default pose
                                                    (--keep-pose: keys only, --dry: only count)
    python tools/frolvy_port.py reset Scarf         default pose, keys untouched
--json prints the raw tool result instead of the plain output.
"""
import json
import os
import subprocess
import sys

EXE = r"C:\Program Files\Frolvy\Frolvy-mcp.exe"


def call(port, code, timeout=900):
    env = dict(os.environ, DCC_MCP_PORT=str(port))
    p = subprocess.Popen([EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)

    def send(msg):
        p.stdin.write((json.dumps(msg) + "\n").encode("utf-8")); p.stdin.flush()

    def recv(want):
        while True:
            line = p.stdout.readline()
            if not line:
                raise RuntimeError("Frolvy-mcp closed")
            m = json.loads(line)
            if m.get("id") == want:
                return m

    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
              "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                         "clientInfo": {"name": "frolvy_port", "version": "1"}}})
        recv(1)
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
              "params": {"name": "execute_code", "arguments": {"code": code}}})
        r = recv(2)
        res = r.get("result") or r.get("error")
        if isinstance(res, dict) and "content" in res:
            return "\n".join(c.get("text", "") for c in res["content"])
        return json.dumps(res)
    finally:
        p.kill()


HERE = os.path.dirname(os.path.abspath(__file__))
OPS = ("scene", "keys", "clear", "reset")


def ops_code(cmd, args):
    path = os.path.join(HERE, "frolvy_plugins", "anim_ops", "anim_ops.py")
    return "exec(open(%r, encoding='utf-8').read())\ncli(api, %r, %r)\n" % (path, cmd, list(args))


def window_title(port):
    """Title of the Frolvy window that owns this MCP port: the open scene, `*` = unsaved changes."""
    import ctypes
    user32 = ctypes.windll.user32
    found = []

    def visit(hwnd, _):
        n = user32.GetWindowTextLengthW(hwnd)
        if n and user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            if buf.value.startswith("Frolvy") and "[MCP %s]" % port in buf.value:
                found.append(buf.value)
        return True

    user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(visit), 0)
    return found[0] if found else None


def show(res):
    """Print the tool result as plain text; return the exit code."""
    try:
        d = json.loads(res)
    except ValueError:
        print(res, file=sys.stderr)  # the bridge's own message, e.g. "Frolvy is not running..."
        return 1
    if not isinstance(d, dict) or not ("output" in d or "ok" in d):
        print(res)
        return 0
    if d.get("output"):
        print(d["output"].rstrip())
    if d.get("ok") is False:
        print(json.dumps({k: v for k, v in d.items() if k != "output"}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # python -I ignores PYTHONIOENCODING; Frolvy output is UTF-8
    argv = [a for a in sys.argv[1:] if a != "--json"]
    port = argv.pop(0) if argv and argv[0].isdigit() else os.environ.get("DCC_MCP_PORT", "9877")
    src, rest = argv[0], argv[1:]
    if src in OPS:
        code = ops_code(src, rest)
        if src == "scene":
            print("window:", window_title(port) or "no Frolvy window with [MCP %s]" % port)
    else:
        code = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    res = call(port, code)
    if "--json" in sys.argv[1:]:
        print(res)
        sys.exit(0)
    rc = show(res)
    tries = 1
    # clear_keys lists the keys again on every run, so a run that was cut short just continues where it stopped
    while rc and src == "clear" and "--dry" not in rest and tries < 4 and "not running" not in res:
        tries += 1
        print("retry %d: the run was cut, continuing" % tries, file=sys.stderr)
        res = call(port, code)
        rc = show(res)
    sys.exit(rc)
