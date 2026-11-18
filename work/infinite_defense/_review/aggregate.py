"""Gộp số liệu 3 phiên Ninja Idle + Attack (Studio), sửa 4 lượt gen bất thường, gán giai đoạn. Ghi stats_all.json + timeline_all.md."""
import json, sys, re, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
T = "tmp/"
SESS = {"S1": ("131029d3-c74f-4ac6-8d8e-9114d976d6ea", range(1, 64)),
        "S2": ("6eacd60e-2606-48f9-b1f5-1390dd78fc40", range(1, 16)),
        "S3": ("e7f5846c", range(1, 44))}
# lượt gen bất thường: cắt tại khoảng im lặng > 60 phút (phút gen đúng)
FIX = {("S1", 31): 5.4 * 60, ("S1", 63): 13.5 * 60, ("S3", 8): 38.6 * 60}
def rng(a, b): return set(range(a, b + 1))
PH = {
 "S1": [("Rig", rng(1, 17)), ("Idle", rng(18, 21) | rng(24, 26) | rng(29, 43) | rng(51, 60)), ("Khác", rng(22, 23) | rng(27, 28) | rng(48, 50)),
        ("Skin", rng(44, 47)), ("Sự cố", rng(61, 63))],
 "S2": [("Khác", {1}), ("Idle", rng(2, 4) | rng(9, 14)), ("Skin", rng(5, 8)), ("Attack", {15})],
 "S3": [("Attack", rng(1, 8) | rng(10, 13) | rng(15, 37) | rng(39, 43)), ("Khác", {9, 14, 38})],
}
def phase(s, n):
    for p, ns in PH[s]:
        if n in ns: return p
rows = []
for s, (sid, ns) in SESS.items():
    d = json.load(open(T + sid + "/stats.json", encoding="utf-8"))
    for t in d["turns"]:
        if t["n"] in ns:
            g = FIX.get((s, t["n"]), t["gen_s"])
            rows.append(dict(s=s, n=t["n"], start=t["start"], gen=g, wait=t["wait_s"], human=t["human_after_s"], brk=t.get("break_after"),
                             phase=phase(s, t["n"]), prompt=t["prompt"], ai=t["ai_last"], images=t["images"]))
rows.sort(key=lambda r: r["start"])
def fmt(sec): sec = int(round(sec)); return "%d g %02d′" % (sec // 3600, sec % 3600 // 60) if sec >= 3600 else "%d′%02d″" % (sec // 60, sec % 60)
tot = collections.OrderedDict()
for r in rows:
    k = r["phase"]; a = tot.setdefault(k, dict(turns=0, gen=0, human=0, wait=0))
    a["turns"] += 1; a["gen"] += r["gen"]; a["human"] += r["human"]; a["wait"] += r["wait"]
T0 = dict(turns=len(rows), gen=sum(r["gen"] for r in rows), human=sum(r["human"] for r in rows), wait=sum(r["wait"] for r in rows))
json.dump(dict(total=T0, phases=tot, rows=rows), open("stats_all.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
out = ["# Số liệu gộp Ninja Idle + Attack (Studio)\n", "| giai đoạn | lượt | AI gen | người | chờ trả lời |", "|---|---|---|---|---|"]
for k, a in tot.items(): out.append(f"| {k} | {a['turns']} | {fmt(a['gen'])} | {fmt(a['human'])} | {fmt(a['wait'])} |")
out.append(f"| **Tổng** | {T0['turns']} | {fmt(T0['gen'])} | {fmt(T0['human'])} | {fmt(T0['wait'])} |\n")
for r in rows:
    out.append(f"{r['s']}#{r['n']} {r['start'][5:16]} [{r['phase']}] gen {fmt(r['gen'])} người {fmt(r['human'])} — {r['prompt'][:110]!r}")
open("timeline_all.md", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out[:12]))
