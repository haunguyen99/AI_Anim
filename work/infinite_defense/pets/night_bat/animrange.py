import subprocess, os, tempfile, sys
from PIL import Image
PORT = os.environ.get("BATPORT", "9883")
poses = {
 "attack charge f8": "api.rotate('CTL_Wing1_L',0,-22,-34); api.rotate('CTL_Wing2_L',0,0,-9); api.rotate('CTL_Wing3_L',0,0,-9); api.rotate('CTL_Wing4_L',0,0,-14); api.rotate('CTL_Wing1_R',0,22,34); api.rotate('CTL_Wing2_R',0,0,9); api.rotate('CTL_Wing3_R',0,0,9); api.rotate('CTL_Wing4_R',0,0,14)",
 "attack fire f13": "api.rotate('CTL_Wing1_L',0,14,24); api.rotate('CTL_Wing2_L',0,0,6); api.rotate('CTL_Wing3_L',0,0,6); api.rotate('CTL_Wing4_L',0,0,8); api.rotate('CTL_Wing1_R',0,-14,-24); api.rotate('CTL_Wing2_R',0,0,-6); api.rotate('CTL_Wing3_R',0,0,-6); api.rotate('CTL_Wing4_R',0,0,-8)",
 "idle down": "api.rotate('CTL_Wing1_L',0,0,-27); api.rotate('CTL_Wing2_L',0,0,-7); api.rotate('CTL_Wing3_L',0,0,-8); api.rotate('CTL_Wing4_L',0,0,-13); api.rotate('CTL_Wing1_R',0,0,27); api.rotate('CTL_Wing2_R',0,0,7); api.rotate('CTL_Wing3_R',0,0,8); api.rotate('CTL_Wing4_R',0,0,13)",
}
ims = []
for k, (n, c) in enumerate(poses.items()):
    code = "for c in api.ls('Curve'):\n    if c.startswith('CTL_') and c!='CTL_Main': api.rotate(c,0,0,0); api.move(c,0,0,0)\n" + c + "\napi.set_frame(4); api.set_frame(0)\napi.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])\napi.look_through('front'); api.set_camera_ortho('front', True); api.set_attr('front.ow', 1.4); api.move('front', 0, 0.35, 100)\n"
    p = os.path.join(tempfile.gettempdir(), "_p.py"); open(p, "w").write(code)
    subprocess.run([sys.executable, "-I", "tools/frolvy_port.py", PORT, p], capture_output=True)
    png = os.path.join(tempfile.gettempdir(), "_p%d.png" % k); subprocess.run([sys.executable, "-I", "tools/frolvy_shot.py", PORT, png], capture_output=True)
    ims.append(Image.open(png).convert("RGB"))
w, h = ims[0].size; sh = Image.new("RGB", (w * 3, h))
for i, im in enumerate(ims): sh.paste(im, (i * w, 0))
sh.save(sys.argv[1]); print(sh.size)
