"""Chạy code Python trong Frolvy trên Linux qua Frolvy-mcp (nằm trong AppImage đang mount).
Dùng: python3 -I fv_call.py <cổng> <file.py|-> [--tool execute_code|get_scene_info|get_viewport_screenshot --out x.png]"""
import base64, glob, json, os, subprocess, sys
port = sys.argv[1]; src = sys.argv[2]
tool = "execute_code"; out = None
if "--tool" in sys.argv: tool = sys.argv[sys.argv.index("--tool") + 1]
if "--out" in sys.argv: out = sys.argv[sys.argv.index("--out") + 1]
exe = sorted(glob.glob("/tmp/.mount_Frolvy*/usr/bin/Frolvy-mcp"))[0]
args = {}
if "--args" in sys.argv: args = json.loads(sys.argv[sys.argv.index("--args") + 1])
elif tool == "execute_code":
    args = {"code": sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()}
p = subprocess.Popen([exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=dict(os.environ, DCC_MCP_PORT=port))
def send(m): p.stdin.write((json.dumps(m) + "\n").encode()); p.stdin.flush()
def recv(i):
    while True:
        l = p.stdout.readline()
        if not l: raise SystemExit("Frolvy-mcp closed")
        m = json.loads(l)
        if m.get("id") == i: return m
send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "fvcall", "version": "1"}}})
recv(1); send({"jsonrpc": "2.0", "method": "notifications/initialized"})
send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": tool, "arguments": args}})
r = recv(2); p.kill()
res = r.get("result") or r.get("error")
for c in (res.get("content") if isinstance(res, dict) else None) or []:
    if c.get("type") == "image" and out:
        open(out, "wb").write(base64.b64decode(c["data"])); print("ok", out)
    elif c.get("type") == "text": print(c["text"])
else:
    if not isinstance(res, dict) or "content" not in res: print(json.dumps(res)[:800])
