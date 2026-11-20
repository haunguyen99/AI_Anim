"""Một lần: thêm xương `pole` (cán cờ) vào flagchar.json ĐANG CÓ mà KHÔNG dựng lại rig (giữ lưới / weight người dùng đã sửa).
- chèn `pole` (con của grip, cùng gốc grip) ngay trước flag1, đổi cha của flag1 thành pole, slot `flag` -> bone pole;
- cộng 1 vào chỉ số xương >= chỗ chèn ở MỌI mesh có weight (weight lưu theo số thứ tự xương);
- weight mesh `flag` tính lại theo w_flag (pole / flag1 / flag2) từ vị trí đỉnh hiện có.
Chạy: .venv/Scripts/python.exe -I work/daily_reward/spine/FlagChar/patch_pole.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_flagchar as bf
sys.path.insert(0, os.path.join(bf.ROOT, "tools"))
J = os.path.join(bf.HERE, "flagchar.json")
sk = json.load(open(J, encoding="utf8"))
names = [b["name"] for b in sk["bones"]]
if "pole" in names:
    print("đã có pole"); sys.exit()
i = names.index("flag1")
sk["bones"].insert(i, {"name": "pole", "parent": "grip", "length": 40, "x": 0, "y": 0, "rotation": 0})
for b in sk["bones"]:
    if b["name"] == "flag1": b["parent"] = "pole"
for s_ in sk["slots"]:
    if s_["name"] == "flag": s_["bone"] = "pole"
# chỉ số xương >= i tăng 1 ở mọi mesh có weight
for skin in sk["skins"]:
    for slot, atts in skin["attachments"].items():
        for name, a in atts.items():
            if a.get("type") != "mesh" or len(a["vertices"]) == len(a["uvs"]): continue
            v, out, k = a["vertices"], [], 0
            while k < len(v):
                n = int(v[k]); out.append(n); k += 1
                for _ in range(n):
                    bi = int(v[k]); out += [bi + 1 if bi >= i else bi, v[k + 1], v[k + 2], v[k + 3]]; k += 4
            a["vertices"] = out
# weight mesh flag: tính lại theo w_flag
bf.build()
bf.BW["pole"] = bf.BW["grip"]
bf.BIDX = {b["name"]: j for j, b in enumerate(sk["bones"])}
a = sk["skins"][0]["attachments"]["flag"]["flag"]
px0, py0 = bf.PARTS["flag"]; w, h = a["width"], a["height"]
verts = []
for k in range(len(a["uvs"]) // 2):
    cx, cy = px0 + a["uvs"][2 * k] * w, py0 + a["uvs"][2 * k + 1] * h
    wx, wy = bf.S(cx, cy)
    ws = bf.w_flag(cx, cy)
    tot = sum(x for _, x in ws); ws = [(b, x / tot) for b, x in ws if x / tot > 0.01]
    tot = sum(x for _, x in ws); ws = [(b, x / tot) for b, x in ws]
    verts.append(len(ws))
    for b, x in ws:
        lx, ly = bf.to_local(b, wx, wy)
        verts += [bf.BIDX[b], round(lx, 3), round(ly, 3), round(x, 4)]
a["vertices"] = verts
try:
    import spine_live_cmd; spine_live_cmd.claude_backup(J, "Claude thêm xương pole (cán cờ)")
except Exception as e:
    print("(backup:", e, ")")
json.dump(sk, open(J, "w", encoding="utf8"), indent=1)
print("đã thêm pole trước flag1; mesh flag:", len(a["uvs"]) // 2, "đỉnh")
