import json
d = json.load(open(r"C:\Users\Admin\AppData\Local\Temp\_lucky_w_now.json"))["Pet_lucky_neko"]
P = d["P"]; W = d["W"]
rows = [(p, w) for p, w in zip(P, W) if p[1] > 0.40 and p[0] >= -0.001 and p[2] > -0.2]
for p, w in sorted(rows, key=lambda t: -t[0][1]): print("%.3f %.3f %.3f  %s" % (p[0], p[1], p[2], {j[4:]: round(v, 2) for j, v in w}))
