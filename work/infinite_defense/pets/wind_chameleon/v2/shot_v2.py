"""Chup viewport Frolvy (Linux, cong 9885) tu kiem mesh v2.
  python3 -I shot_v2.py <out.png> <cam: side|front|top|persp> [frame] [--joints] [ow] [cx,cy,cz]
Hien mesh, an control (tru khi --joints thi hien joint)."""
import base64, json, os, subprocess, sys
sys.path.insert(0, "/home/ngocvb/Projects/AI_animation/tools")
import frolvy_port as fp
PORT = 9885
out, cam = sys.argv[1], sys.argv[2]
rest = sys.argv[3:]
joints = "--joints" in rest; rest = [a for a in rest if a != "--joints"]
frame = int(rest[0]) if rest else 0
ow = float(rest[1]) if len(rest) > 1 else 1.7
ctr = [float(x) for x in rest[2].split(",")] if len(rest) > 2 else [0, .4, 0]
code = f'''
api.set_frame(1); api.set_frame({frame})
cur=list(api.ls('Curve')); jn=list(api.ls('Joint'))
api.select(cur); api.hide(True); api.select(jn); api.hide(not {joints}); api.select([])
api.look_through({cam!r})
'''
if cam != "persp":
    off = {"side": (100, 0, 0), "front": (0, 0, 100), "top": (0, 100, 0)}[cam]
    code += f"api.set_camera_ortho({cam!r}, True); api.set_attr({cam+'.ow'!r}, {ow})\napi.move({cam!r}, {ctr[0]+off[0]}, {ctr[1]+off[1]}, {ctr[2]+off[2]})\n"
fp.call(PORT, code)
r = fp.subprocess.Popen([fp.EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=dict(os.environ, DCC_MCP_PORT=str(PORT)))
def send(m): r.stdin.write((json.dumps(m) + "\n").encode()); r.stdin.flush()
def recv(i):
    while True:
        m = json.loads(r.stdout.readline())
        if m.get("id") == i: return m
send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "shot", "version": "1"}}})
recv(1); send({"jsonrpc": "2.0", "method": "notifications/initialized"})
send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_viewport_screenshot", "arguments": {}}})
m = recv(2); r.kill()
for c in m["result"]["content"]:
    if c.get("type") == "image":
        open(out, "wb").write(base64.b64decode(c["data"])); print("ok", out); break
else: print(json.dumps(m)[:300])
