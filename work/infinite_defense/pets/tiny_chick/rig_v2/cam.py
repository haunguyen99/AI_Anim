# Camera 3/4 + an control/joint de tu kiem (chay trong Frolvy 9883). Dat bien VIEW = (rx, ry) truoc neu muon doi.
import math
try: VIEW
except NameError: VIEW = (-18, 32)
CURVES = list(api.ls("Curve")); JOINTS = list(api.ls("Joint"))
cam = "camera1" if "camera1" in [n for n in api.ls("Camera")] else api.create_camera()
rx, ry = math.radians(VIEW[0]), math.radians(VIEW[1])
fwd = (-math.cos(rx)*math.sin(ry), math.sin(rx), -math.cos(rx)*math.cos(ry))
c = (0, 0.5, 0); D = 1.7*1.8
pos = [c[k]-fwd[k]*D for k in range(3)]
for j in JOINTS: api.set_joint_draw_style(j, 'none')
api.select(CURVES+JOINTS); api.hide(True); api.select([])
api.set_transform(cam, pos, [VIEW[0], VIEW[1], 0], [1,1,1]); api.look_through(cam)
print(cam)
