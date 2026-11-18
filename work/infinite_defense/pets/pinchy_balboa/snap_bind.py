"""Base FBX: Frolvy writes the static Lcl of each joint from a half-evaluated constraint pose (up to 1 cm / 1.7 deg off). Snap every current DEF_ joint
(id >= last DEF_Root_M id) to the designed bind: rotation 0, translation = world(joint) - world(parent) from the J table of rig_build.py.
usage: snap_bind.py in.fbx out.fbx"""
import re, sys
src = open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\pinchy_balboa\rig_build.py", encoding="utf-8").read()
ns = {}; exec(src[src.index("J = ["):src.index("made = {}")], ns)
W = {n: (p, pos) for n, p, pos, _, _ in ns["J"]}
t = open(sys.argv[1], encoding="utf-8").read()
cut = max(int(x) for x in re.findall(r'\tModel: (\d+), "Model::DEF_Root_M", "LimbNode"', t))
cnt = 0
def f(m):
    global cnt
    mid, name, body = int(m.group(1)), m.group(2), m.group(0)
    if mid < cut or name not in W: return body
    par, pos = W[name]; pp = W[par][1] if par else (0, 0, 0)
    loc = [pos[i] - pp[i] for i in range(3)]
    body = re.sub(r'(P: "Lcl Translation", "Lcl Translation", "", "A",)[^\n]*', lambda k: k.group(1) + "%.6f,%.6f,%.6f" % tuple(loc), body, 1)
    body = re.sub(r'(P: "Lcl Rotation", "Lcl Rotation", "", "A",)[^\n]*', lambda k: k.group(1) + "0.000000,0.000000,0.000000", body, 1)
    cnt += 1; return body
t = re.sub(r'\tModel: (\d+), "Model::(DEF_[^"]*)", "LimbNode" \{.*?\n\t\}', f, t, flags=re.S)
open(sys.argv[2], "w", encoding="utf-8").write(t); print("snapped", cnt)
