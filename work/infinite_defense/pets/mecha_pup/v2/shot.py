"""Chup viewport cua Frolvy theo cong (tu kiem). python tools/frolvy_shot.py <cong> <out.png>"""
import base64, json, os, subprocess, sys
EXE = os.path.expanduser("~/.local/share/frolvy/Frolvy-mcp")
port, out = sys.argv[1], sys.argv[2]
p = subprocess.Popen([EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                     env=dict(os.environ, DCC_MCP_PORT=port))
def send(m): p.stdin.write((json.dumps(m) + "\n").encode()); p.stdin.flush()
def recv(i):
    while True:
        m = json.loads(p.stdout.readline())
        if m.get("id") == i: return m
send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "shot", "version": "1"}}})
recv(1); send({"jsonrpc": "2.0", "method": "notifications/initialized"})
send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_viewport_screenshot", "arguments": {}}})
r = recv(2); p.kill()
for c in r["result"]["content"]:
    if c.get("type") == "image":
        open(out, "wb").write(base64.b64decode(c["data"])); print("ok", out); break
else: print(json.dumps(r)[:500])
