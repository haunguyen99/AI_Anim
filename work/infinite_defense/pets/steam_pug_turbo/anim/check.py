# chay trong Frolvy: python tools/frolvy_port.py 9888 check.py  (MODEFR = "0-48" gan truoc)  -> in so do + ghi %TEMP%/pug_anim.json
import math, json, os
O = api.ls("Object")[0]
lo, hi = FR
api.set_frame(1); api.set_frame(0)
def P(f):
    api.set_frame(f); md = api.mesh_data(O, True); p = md['positions']; return [p[i*3:i*3+3] for i in range(len(p)//3)]
api.set_attr  # noqa
md = api.mesh_data(O); idx = list(md['vertices']); pos = {v: i for i, v in enumerate(idx)}; E = set(); c = 0
for s in md['face_sizes']:
    cs = [pos.get(q, q) for q in md['face_corners'][c:c+s]]; c += s
    for k in range(s): E.add(tuple(sorted((cs[k], cs[(k+1) % s]))))
bind = [md['positions'][i*3:i*3+3] for i in range(len(idx))]
frames = {}; worst = (1, 0, 0); minY = 9; maxJump = (0, 0)
prev = None
for f in range(lo, hi + 1):
    q = P(f); frames[f] = q
    minY = min(minY, min(v[1] for v in q))
    for a, b in E:
        l0 = math.dist(bind[a], bind[b])
        if l0 < 1e-3: continue
        r = math.dist(q[a], q[b]) / l0
        if r > worst[0]: worst = (r, f, a)
    if prev: 
        j = max(math.dist(q[i], prev[i]) for i in range(len(q))); 
        if j > maxJump[0]: maxJump = (j, f)
    prev = q
print("frames", lo, hi, "min mesh y %.3f" % minY, "max edge stretch x%.2f @f%d" % (worst[0], worst[1]), "max vertex move/frame %.3f @f%d" % maxJump)
if lo == 0 and hi == 48:
    print("loop f48 vs f0 max diff", round(max(math.dist(frames[0][i], frames[48][i]) for i in range(len(idx))), 5))
json.dump({str(f): [round(c, 3) for v in q for c in v] for f, q in frames.items()}, open(os.path.join(os.environ["TEMP"], "pug_anim.json"), "w"))
api.set_frame(1); api.set_frame(0)
