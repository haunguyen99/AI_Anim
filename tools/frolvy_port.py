"""Run Python inside a SECOND Frolvy instance on another MCP port, so two Claude sessions can use Frolvy in parallel
(user 2026-11-03: "Sao không chạy song song"). Frolvy reads env DCC_MCP_PORT (app and Frolvy-mcp.exe); the
session's own `frolvy` MCP server stays on 9877.

Start a second Frolvy (PowerShell):
    $env:DCC_MCP_PORT="9878"; Start-Process "C:\\Program Files\\Frolvy\\Frolvy.exe"; Remove-Item Env:DCC_MCP_PORT
Run code there:
    python tools/frolvy_port.py 9878 script.py        (or "-" to read code from stdin)
Prints the tool result (output / value / traceback). Timeout per call: --timeout seconds (default 900).
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


if __name__ == "__main__":
    port, src = sys.argv[1], sys.argv[2]
    code = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    print(call(port, code))
