# Chay trong Frolvy: dat camera ba phan tu khung vao pet, an control/joint (chi de tu kiem).
import math
cams = [n for n in api.ls() if n == 'camera1']
cam = cams[0] if cams else api.create_camera()
f0, f1 = api.frame_range()
lo = [1e9]*3; hi = [-1e9]*3
for fr in range(f0, f1 + 1, max(1, (f1 - f0)//12)):
    api.set_frame(fr)
    p = api.mesh_data('Pet_Mecha_Pup', True)['positions']
    for i in range(0, len(p), 3):
        for k in range(3):
            lo[k] = min(lo[k], p[i+k]); hi[k] = max(hi[k], p[i+k])
api.set_frame(f0)
c = [(lo[k]+hi[k])/2 for k in range(3)]; dim = max(hi[k]-lo[k] for k in range(3))
rx, ry = math.radians(-18), math.radians(32)
fwd = (-math.cos(rx)*math.sin(ry), math.sin(rx), -math.cos(rx)*math.cos(ry))
D = dim*1.8; pos = [c[k]-fwd[k]*D for k in range(3)]
keep = {cam, 'Pet_Mecha_Pup'}
hide = [n for n in api.ls() if api.node_type(n) in ('Curve', 'Group', 'Joint') and n not in ('persp','top','front','side')]
for j in api.ls('Joint'): api.set_joint_draw_style(j, 'none')
api.select(hide); api.hide(True); api.select([])
api.set_transform(cam, pos, [-18, 32, 0], [1, 1, 1]); api.look_through(cam)
print('cam', cam, 'dim', round(dim, 2))
