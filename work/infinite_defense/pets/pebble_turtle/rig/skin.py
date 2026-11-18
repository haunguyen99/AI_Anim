# Bind + ghi weight theo luat (chay trong Frolvy 9881 sau build_rig.py)
MESH = dict(shell="tripo_node_20d58e65", head="tripo_node_20d58e65.001", front="tripo_node_20d58e65.002", back="tripo_node_20d58e65.003")
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_")]
for m in MESH.values():
    try: api.unbind_skin([m]) if False else None
    except Exception: pass
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def pts(o):
    v = api.mesh_data(o)['positions']
    return v if isinstance(v[0], (list, tuple)) else [v[i*3:i*3+3] for i in range(len(v)//3)]
for m in MESH.values():
    api.select([m])
    try: api.unbind_skin()
    except Exception: pass
    api.select([m]); api.bind_skin(DEF)
def norm(row):
    row = [(j, w) for j, w in row if w > 0.01]
    s = sum(w for _, w in row); return [(j, w/s) for j, w in row]
def write(m, rule):
    api.select([m]); P = pts(m); idx = list(api.mesh_data(m)['vertices']); rows = [norm(rule(p)) for p in P]
    api.set_skin_weights(idx, rows)
# shell: Root, tail ramps
def shell(p):
    x, y, z = p
    t2 = ramp(z, -0.36, -0.47) * ramp(0.30, y, 0.20)
    t1 = ramp(z, -0.22, -0.34) * ramp(0.30, y, 0.20) - t2
    t1 = max(0.0, t1)
    return [("DEF_Tail2_M", t2), ("DEF_Tail1_M", t1), ("DEF_Root_M", max(0.0, 1 - t1 - t2))]
write(MESH["shell"], shell)
write(MESH["head"], lambda p: [("DEF_Head_M", 1.0)])
def leg(pre):
    def f(p):
        x, y, z = p; s = "L" if x > 0 else "R"
        hip = 1 - ramp(y, 0.11, 0.19)
        hipw = ramp(y, 0.11, 0.19)
        toe = ramp(0.05, y, 0.0)  # 0 above y .05, 1 at y 0
        ank = (1 - hipw) * (1 - toe)
        return [("DEF_%sHip_%s" % (pre, s), hipw), ("DEF_%sAnkle_%s" % (pre, s), ank), ("DEF_%sToe_%s" % (pre, s), (1 - hipw) * toe)]
    return f
write(MESH["front"], leg("Front")); write(MESH["back"], leg("Back"))
api.select([])
for k, m in MESH.items():
    P = pts(m)
    api.select([m]); print(k, len(P), api.vertex_weights(api.mesh_data(m)['vertices'][0]))
