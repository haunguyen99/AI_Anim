"""py closeup.py out.png frame cam x y z ow"""
import subprocess, sys, os, tempfile
from PIL import Image
out, f, cam, x, y, z, ow = sys.argv[1:8]
pos = {"front": "%s,%s,100" % (x, y), "side": "100,%s,%s" % (y, z), "top": "%s,100,%s" % (x, z)}[cam]
code = "api.set_frame(1); api.set_frame(%s)\napi.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', %s)\napi.move('%s', %s)\n" % (f, cam, cam, cam, ow, cam, pos)
p = os.path.join(tempfile.gettempdir(), "_cu.py"); open(p, "w").write(code)
subprocess.run([sys.executable, "-I", "tools/frolvy_port.py", "9886", p], capture_output=True)
subprocess.run([sys.executable, "-I", "tools/frolvy_shot.py", "9886", out], capture_output=True); print(out)
