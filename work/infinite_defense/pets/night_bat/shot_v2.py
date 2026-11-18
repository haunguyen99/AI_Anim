"""Linux: chup viewport Frolvy cong 9884 (tu kiem Night Bat v2).
  python3 -I shot_v2.py out.png frames cam[,cam..] [ow] [cy] [rig] [port]   cam: front|side|top ; frames: 0,10,20
Ra mot anh ghep (hang = frame, cot = cam)."""
import base64, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "tools"))
import frolvy_port
from PIL import Image
out = sys.argv[1]; frames = [int(x) for x in sys.argv[2].split(",")]; cams = sys.argv[3].split(",")
ow = sys.argv[4] if len(sys.argv) > 4 else "0.9"; cy = sys.argv[5] if len(sys.argv) > 5 else "0.3"
rig = len(sys.argv) > 6 and sys.argv[6] == "rig"; port = sys.argv[7] if len(sys.argv) > 7 else "9884"
POS = {"side": "100, %s, 0", "front": "0, %s, 100", "top": "0, 100, -0.1"}
def shot(png):
    env = dict(os.environ, DCC_MCP_PORT=port)
    p = subprocess.Popen([frolvy_port.EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
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
        if c.get("type") == "image": open(png, "wb").write(base64.b64decode(c["data"])); return
    raise RuntimeError(json.dumps(r)[:300])
rows = []
for f in frames:
    row = []
    for cam in cams:
        code = "api.set_frame(1); api.set_frame(%d)\napi.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(%s); api.select([])\n" % (f, "False" if rig else "True")
        pos = POS[cam] % cy if "%s" in POS[cam] else POS[cam]
        code += "api.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', %s)\napi.move('%s', %s)\n" % (cam, cam, cam, ow, cam, pos)
        pth = os.path.join(tempfile.gettempdir(), "_nbs.py"); open(pth, "w").write(code)
        frolvy_port.call(port, code)
        png = os.path.join(tempfile.gettempdir(), "_nbs_%s_%d.png" % (cam, f)); shot(png); row.append(Image.open(png).convert("RGB"))
    rows.append(row)
w, h = rows[0][0].size
sheet = Image.new("RGB", (w * len(cams), h * len(frames)))
for r, row in enumerate(rows):
    for c, im in enumerate(row): sheet.paste(im, (c * w, r * h))
sheet.save(out); print("ok", out, sheet.size)
