md = api.mesh_data("Pet_lucky_neko"); P = md['positions']; n = len(P)//3
V = [(P[3*i], P[3*i+1], P[3*i+2]) for i in range(n)]
body = [v for v in V if v[1] < 0.262]
print("body-ish", len(body))
for y0 in [i*0.02 for i in range(0, 14)]:
    s = [v for v in V if y0 <= v[1] < y0+0.02]
    if not s: continue
    print("y %.2f n%3d x %.3f..%.3f z %.3f..%.3f" % (y0, len(s), min(v[0] for v in s), max(v[0] for v in s), min(v[2] for v in s), max(v[2] for v in s)))
# tail: z < -0.14
t = [v for v in V if v[2] < -0.15]; print("back z<-.15", len(t), [tuple(round(c,3) for c in v) for v in t[:6]])
# arms: |x|>0.14 and y<0.24
for sg in (1, -1):
    a = [v for v in V if sg*v[0] > 0.13 and v[1] < 0.26]; print("arm", sg, len(a), "x", min(sg*v[0] for v in a), max(sg*v[0] for v in a), "y", min(v[1] for v in a), max(v[1] for v in a), "z", min(v[2] for v in a), max(v[2] for v in a))
# bell
b = [v for v in V if v[1] > 0.23 and v[1] < 0.3 and v[2] > 0.07 and abs(v[0]) < 0.06]; print("bell-ish", len(b), min(v[1] for v in b), max(v[1] for v in b))
