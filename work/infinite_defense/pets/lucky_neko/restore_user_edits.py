# Put back the weights the user hand-edited (ids from dry_compare, values from the dump taken before the rebuild). Ear region is skipped (ears were re-segmented on purpose).
import json
T = r"C:\Users\Admin\AppData\Local\Temp"
ids = json.load(open(T + r"\_lucky_user_ids.json")); d = json.load(open(T + r"\_lucky_w_user.json"))["Pet_lucky_neko"]
pos = {v: p for v, p in zip(d["ids"], d["P"])}; w = {v: x for v, x in zip(d["ids"], d["W"])}
keep = [v for v in ids if not any('Ear' in j and x > 0.001 for j, x in w[v])]   # ear edits are now built into rig_skin.py (EAR table)
J = set(api.ls("Joint"))
api.select(["Pet_lucky_neko"])
api.set_skin_weights(keep, [[(j, x) for j, x in w[v] if x > 0.0005 and j in J] for v in keep])
print("restored", len(keep), "of", len(ids))
