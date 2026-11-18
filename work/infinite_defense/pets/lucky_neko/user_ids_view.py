import json
T = r"C:\Users\Admin\AppData\Local\Temp"
ids = json.load(open(T + r"\_lucky_user_ids.json")); d = json.load(open(T + r"\_lucky_w_user.json"))["Pet_lucky_neko"]
pos = {v: p for v, p in zip(d["ids"], d["P"])}; w = {v: x for v, x in zip(d["ids"], d["W"])}
for v in sorted(ids, key=lambda v: -pos[v][1]):
    print(v, [round(c, 3) for c in pos[v]], {j[4:]: round(x, 2) for j, x in w[v]})
