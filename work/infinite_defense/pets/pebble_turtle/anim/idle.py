# Idle 48f (0..48, f48 = f0) tren Base. Chay trong Frolvy 9881 voi scene PebbleTurtle_rig.fv
import math
api.open_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_12_Pebble_Turtle\PebbleTurtle_rig.fv")
api.select([]); api.reset_transforms(all_controls=True)
api.set_frame_range(0, 48)
N = 48
def S(t, ph=0): return math.sin(2*math.pi*t/N + math.radians(ph))
def lerp_keys(pts, t):  # pts [(f,v)] smoothstep
    for (f0, v0), (f1, v1) in zip(pts, pts[1:]):
        if f0 <= t <= f1:
            u = (t - f0)/(f1 - f0) if f1 > f0 else 1; u = u*u*(3-2*u); return v0 + (v1-v0)*u
    return pts[-1][1]
RET = [(0,0),(24,0),(30,1),(34,1),(44,0),(48,0)]   # nhip rut dau nhe 0..1
def pose(t):
    r = lerp_keys(RET, t)
    P = {}
    P["CTL_Root_M"] = dict(rz=4*S(t), rx=1.2*S(t, 90) - 1.2*S(0, 90), ty=-0.009*(1-math.cos(4*math.pi*t/N)))
    P["CTL_Tail1_M"] = dict(ry=10*S(t-6))
    P["CTL_Tail2_M"] = dict(ry=14*S(t-12))
    P["CTL_Neck_M"] = dict(rx=2*S(2*t, 0) + 9*r, rz=-1.5*S(t))
    P["CTL_Head_M"] = dict(tz=-0.10*r, rx=-3*r, rz=-1.5*S(t))
    for pre in ("Front", "Back"):
        for s in "LR":
            P["CTL_%sHip_%s" % (pre, s)] = dict(rz=-3.6*S(t), rx=-1.0*(S(t, 90) - 1), ty=0.009*(1-math.cos(4*math.pi*t/N)))
    return P
keyed = set()
for t in range(0, N + 1, 3):
    tt = 0 if t == N else t
    api.set_frame(t)
    P = pose(t)
    for node, ch in P.items():
        for c, v in ch.items(): api.set_attr(node + "." + c, v)
        api.select([node]); api.set_key(); keyed.add(node)
api.select([])
api.set_frame(0)
exec(open(r"C:\Users\Admin\Documents\AI_animation\tools\frolvy_plugins\loop_seam\loop_seam.py", encoding="utf-8").read())
print(smooth(api))
print(sorted(keyed))
