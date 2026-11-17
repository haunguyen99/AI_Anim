"""py posed_shot.py out.png cam ow cx cy cz 'Ctl=rx,ry,rz;Ctl=...'"""
import subprocess, sys, os, tempfile
out, cam, ow, cx, cy, cz, pose = sys.argv[1:8]
pos = {"side": "100, %s, %s", "top": "%s, 100, %s", "front": "%s, %s, 100"}[cam]
a = {"side": (cy, cz), "top": (cx, cz), "front": (cx, cy)}[cam]
code = "ES = r'''%s'''\nd={}\nfor it in ES.split(';'):\n    if it.strip():\n        k,v=it.split('='); d[k.strip()]=tuple(float(x) for x in v.split(','))\n" % pose
code += open(r"work/infinite_defense/pets/chrono_ouroboros/v2/skin_check_v2.py", encoding="utf8").read().split("POSES =")[0].replace("setpose({})\nmd =", "md =", 1)
code += "setpose(d)\napi.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\n"
code += "api.look_through('%s'); api.set_camera_ortho('%s', True); api.set_attr('%s.ow', %s)\napi.move('%s', %s)\n" % (cam, cam, cam, ow, cam, pos % a)
p = os.path.join(tempfile.gettempdir(), "_ps.py"); open(p, "w").write(code)
r = subprocess.run([sys.executable, "-I", "tools/frolvy_port.py", "9890", p], capture_output=True, text=True); print(r.stdout[-300:], r.stderr[-300:])
subprocess.run([sys.executable, "-I", "tools/frolvy_shot.py", "9890", out])
