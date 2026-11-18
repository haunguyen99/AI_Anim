"""Lucky Neko Idle, 48F loop (f0 == f48). Hovering, right paw waves 4x per loop (beckoning), left paw holds the coin,
tail/ears/bell/tassels/jar/legs lag behind the bob. Every offset is 0 at f0 and f48 (off() = A*(sin(k*p+ph) - sin(ph))) so frame 0 = the approved idle pose.
Run in Frolvy (port 9891) on the scene holding the idle pose (lucky_neko_idle_pose.fv)."""
import json, math
N = 48
BASE = json.load(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\lucky_neko\anim\base_pose.json"))
CT = sorted(BASE)
def off(f, k, ph, A):
    p = 2 * math.pi * f / N
    return A * (math.sin(k * p + ph) - math.sin(ph))
def pose(f):
    D = {c: [0.0] * 6 for c in CT}          # tx ty tz rx ry rz
    o = lambda k, ph, A: off(f, k, ph, A)
    # --- body: hover bob 2x per loop, soft sway 1x, spine/head lag the bob
    D["CTL_Root_M"][1] = o(2, 0.0, 0.011); D["CTL_Root_M"][2] = o(1, 0.4, 0.004)
    D["CTL_Root_M"][5] = o(1, 0.9, 1.4); D["CTL_Root_M"][3] = o(2, -0.5, 1.0)
    D["CTL_Spine1_M"][3] = o(2, -0.9, 1.3); D["CTL_Spine1_M"][5] = o(1, 0.2, 1.2)
    D["CTL_Head_M"][3] = o(2, -1.4, 0.9); D["CTL_Head_M"][4] = o(1, -0.5, 1.0); D["CTL_Head_M"][5] = o(1, 0.8, 1.0) + o(4, 0.0, 0.3)
    # --- waving right arm: elbow sweeps, wrist follows through (lag), shoulder gives a small push
    D["CTL_Shoulder_R"][5] = o(4, 0.5, 3.0)
    D["CTL_Elbow_R"][5] = o(4, 0.0, 16.0) + o(8, 0.7, 2.0)
    D["CTL_Wrist_R"][5] = o(4, -1.0, 30.0) + o(8, -0.2, 3.0)
    # --- left arm holds the coin: small bob, coin rides with the hand
    D["CTL_Shoulder_L"][3] = o(2, -0.7, 1.5); D["CTL_Elbow_L"][4] = o(2, -1.0, 2.0); D["CTL_Wrist_L"][5] = o(2, -1.5, 2.0)
    # --- legs dangle and lag behind the bob
    D["CTL_Hip_L"][3] = o(2, -1.4, 1.5); D["CTL_Ankle_L"][3] = o(2, -2.2, 2.2)
    D["CTL_Hip_R"][3] = o(2, -1.7, 1.5); D["CTL_Ankle_R"][3] = o(2, -2.5, 2.2)
    # --- tail (question mark): sway 1x with a travelling lag, little bob 2x
    D["CTL_Tail1_M"][4] = o(1, -0.3, 6.0); D["CTL_Tail2_M"][4] = o(1, -0.9, 9.0); D["CTL_Tail3_M"][4] = o(1, -1.5, 12.0)
    D["CTL_Tail2_M"][3] = o(2, -1.2, 4.0); D["CTL_Tail3_M"][3] = o(2, -1.8, 6.0)
    # --- ears flick, out of step
    D["CTL_Ear1_L"][5] = o(2, -1.0, 2.5); D["CTL_Ear1_R"][5] = o(2, -1.4, -2.5)
    D["CTL_Ear2_L"][5] = o(2, -1.6, 3.0); D["CTL_Ear2_R"][5] = o(2, -2.0, -3.0)
    # --- bell swings on the bob (+ jiggle on the wave beat)
    D["CTL_Bell_M"][3] = o(2, -1.3, 9.0) + o(4, -0.4, 2.5); D["CTL_Bell_M"][5] = o(4, 0.3, 3.0)
    # --- jar on the back: translation only (its base rotation is a free Euler combo), tassels swing behind it
    D["CTL_Jar_M"][1] = o(2, -1.0, 0.006); D["CTL_Jar_M"][2] = o(1, -0.8, 0.004)
    for n, (ph, a) in {"A1": (-1.4, 7.0), "A2": (-2.0, 10.0), "A3": (-2.6, 12.0), "B1": (-1.7, -7.0), "B2": (-2.3, -10.0), "B3": (-2.9, -12.0)}.items():
        D["CTL_Tassel%s_M" % n][5] = o(2, ph, a); D["CTL_Tassel%s_M" % n][3] = o(1, ph, a * 0.4)
    return D
def apply(f):
    D = pose(f)
    for c in CT:
        b = BASE[c]; d = D[c]
        api.rotate(c, b[3] + d[3], b[4] + d[4], b[5] + d[5])
        if c != "CTL_Main": api.move(c, b[0] + d[0], b[1] + d[1], b[2] + d[2])
        api.scale(c, b[6], b[7], b[8])
def build():
    api.set_frame_range(0, N); api.set_frame(0)
    # rotate only sticks on curves that already hold a key at every frame: key the base pose on every frame first
    for c in CT: api.rotate(c, *BASE[c][3:6]); api.move(c, *BASE[c][0:3]) if c != "CTL_Main" else None
    for f in range(0, N + 1):
        api.set_frame(f); api.select(CT); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); apply(f); api.select(CT); api.set_key()
    api.select([]); api.set_frame(1); api.set_frame(0)
    for c in CT:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try: api.set_infinity(c + "." + a, "cycle", "cycle")
            except Exception: pass
if __name__ == "__main__" or True:
    build(); print("idle keyed", N)
