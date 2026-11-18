import json
T = r"C:\Users\Admin\AppData\Local\Temp"
d = json.load(open(T + r"\_lucky_w_user.json"))["Pet_lucky_neko"]
rows = [(p, w) for p, w in zip(d["P"], d["W"]) if p[0] > 0 and any("Ear" in j and x > 0.03 for j, x in w)]
print(len(rows))
for p, w in sorted(rows, key=lambda t: -t[0][1]): print([round(c, 3) for c in p], {j[4:]: round(x, 2) for j, x in w})
