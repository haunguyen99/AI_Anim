"""Gộp số liệu Ninja trong Frolvy (3-4/11): rig/skin/picker, pose Idle, Skill 1 blocking + refine. Ghi stats_frolvy.json."""
import json, collections, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
T = "tmp/"
def rng(a, b): return set(range(a, b + 1))
S = {
 "F1": ("8da47427-9f72-493e-b481-ce53b4367a2a", [("Rig", rng(1, 2)), ("Pose Idle", rng(3, 5))]),
 "F2": ("3f0e1f05-d67e-4d33-be71-8c534443b74c", [("Khác", rng(1, 4) | rng(7, 12) | {15}), ("Pose Idle", rng(5, 6) | rng(17, 18)), ("Rig", {13, 14, 16})]),
 "F3": ("d3a5179a-e5ca-4fef-86a8-32c78dcab1bc", [("Pose Idle", rng(1, 4)), ("Skill 1 blocking", rng(5, 17) | {20}), ("Khác", {18, 19})]),
 "F4": ("798033c1-b992-4065-8219-7a643da3d52e", [("Skill 1 blocking", rng(2, 7)), ("Khác", {1} | rng(8, 11))]),
 "F5": ("2d4078de-b9dd-4e1c-af5a-9aeafccc64bd", [("Skill 1 blocking", rng(2, 9)), ("Skill 1 refine + xuất", {10}), ("Khác", {1, 11})]),
 "F6": ("f847746a-eaa3-4ec0-9afb-f943f876a3f4", [("Skill 1 refine + xuất", rng(1, 24))]),
}
rows = []
for s, (sid, ph) in S.items():
    d = json.load(open(T + sid + "/stats.json", encoding="utf-8"))
    for t in d["turns"]:
        p = next((k for k, ns in ph if t["n"] in ns), None)
        if p: rows.append(dict(s=s, n=t["n"], start=t["start"], gen=t["gen_s"], wait=t["wait_s"], human=t["human_after_s"], brk=t.get("break_after"), phase=p, prompt=t["prompt"], ai=t["ai_last"]))
rows.sort(key=lambda r: r["start"])
def fmt(x): x = int(round(x)); return "%d g %02d′" % (x // 3600, x % 3600 // 60) if x >= 3600 else "%d′%02d″" % (x // 60, x % 60)
tot = collections.OrderedDict()
for r in rows:
    a = tot.setdefault(r["phase"], dict(turns=0, gen=0, human=0, wait=0)); a["turns"] += 1; a["gen"] += r["gen"]; a["human"] += min(r["human"], 900); a["wait"] += r["wait"]
T0 = {k: sum(a[k] for a in tot.values()) for k in ("turns", "gen", "human", "wait")}
json.dump(dict(total=T0, phases=tot, rows=rows), open("stats_frolvy.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("| giai đoạn | lượt | AI gen | người | chờ |")
for k, a in tot.items(): print(f"| {k} | {a['turns']} | {fmt(a['gen'])} | {fmt(a['human'])} | {fmt(a['wait'])} |")
print(f"| Tổng | {T0['turns']} | {fmt(T0['gen'])} | {fmt(T0['human'])} | {fmt(T0['wait'])} |")
