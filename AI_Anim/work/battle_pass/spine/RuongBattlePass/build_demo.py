"""Anim `rig_demo` của RuongBattlePass (viết riêng vì rig có 3 trạng thái cửa đổi bằng attachment + clipping, rig_demo.py chung không đổi được).
Chạy: .venv/Scripts/python.exe -I work/battle_pass/spine/RuongBattlePass/build_demo.py   (chỉ ghi anim, KHÔNG đụng lưới / weight)
Thứ tự (người xem thấy lần lượt từng bộ phận, mỗi đoạn có tên trong DEMO_STEPS):
  A cửa đóng: rương squash / nghiêng, cửa quay (scaleX quanh bản lề), mép cửa rung, núm xoay, vòng xoay đủ 1 vòng
  B cửa mở vừa: cửa quay, mép rung, núm lồi lắc, 3 chốt bật ra lần lượt
  C cửa mở hẳn: cửa quay, mép rung, 3 chốt bật ra
  D không cửa: 3 chồng xu + 4 xu cột + xu nghiêng trong rương (nhảy LÊN QUA MIỆNG rương để thấy clipping cắt đúng viền)
  E xu ngoài: từng chồng / xu nảy + xoay
  F cả rig cùng chuyển (về cửa đóng): rương squash, mọi xương lắc lệch pha, cuối trả setup đúng F0.
"""
import json, math, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "spine")); sys.path.insert(0, os.path.join(ROOT, "tools"))
import anim_kit as K
from key_reduce import reduce_keys
sys.stdout.reconfigure(encoding="utf-8")
JS = os.path.join(HERE, "ruong.json"); REL = "work/battle_pass/spine/RuongBattlePass/ruong.json"
FPS = 30
SK = json.load(open(JS, encoding="utf-8"))
BONES = [b["name"] for b in SK["bones"]]
SLOTS = [s["name"] for s in SK["slots"]]
SETUP_ATT = {s["name"]: s.get("attachment") for s in SK["slots"]}

STATE = {  # slot -> trạng thái cửa nào hiện
    "closed": ["door_c", "dial", "ring"],
    "half": ["door_h", "bolt_h1", "bolt_h2", "bolt_h3"],
    "open": ["door_o", "bolt_o1", "bolt_o2", "bolt_o3"],
    "none": [],
}
DOOR_SLOTS = sorted({s for v in STATE.values() for s in v})

# ----------------------------------------------------------------- kế hoạch đoạn (frame bắt đầu, độ dài)
STEPS = []   # (tên, trạng thái cửa, f0, n)
t = 0
def step(name, state, n):
    global t
    STEPS.append((name, state, t, n)); t += n
    return STEPS[-1]

A1 = step("A chest squash", "closed", 20); A2 = step("A door_c swing", "closed", 20); A3 = step("A door_c_tip", "closed", 16)
A4 = step("A dial", "closed", 16); A5 = step("A ring", "closed", 24)
B1 = step("B door_h swing", "half", 20); B2 = step("B door_h_tip + knob", "half", 20); B3 = step("B bolts_h", "half", 24)
C1 = step("C door_o swing", "open", 20); C2 = step("C door_o_tip", "open", 16); C3 = step("C bolts_o", "open", 24)
D1 = step("D stacks", "none", 24); D2 = step("D in_c1..c4", "none", 36); D3 = step("D in_tilt", "none", 16)
E1 = step("E fg stacks + tilt", "none", 36); E2 = step("E fg coins", "none", 36)
F1 = step("F all together", "closed", 40)
N = t

F = N + 1
rot = {b: [0.0] * F for b in BONES}; tx = {b: [0.0] * F for b in BONES}; ty = {b: [0.0] * F for b in BONES}
sx = {b: [1.0] * F for b in BONES}; sy = {b: [1.0] * F for b in BONES}


def seg(s): return range(s[2], s[2] + s[3] + 1)
def u_of(s, f): return (f - s[2]) / s[3]
def bump(u): return math.sin(math.pi * u)          # 0 -> 1 -> 0
def wave(u, n=1, ph=0.0): return math.sin(2 * math.pi * (n * u - ph)) * math.sin(math.pi * u) ** 0.5   # đi + về, mượt hai đầu


# --- A: cửa đóng
for f in seg(A1):
    u = u_of(A1, f); w = wave(u)
    rot["chest"][f] = 3.5 * w; sy["chest"][f] = 1 - 0.07 * bump(u) * math.cos(2 * math.pi * u); sx["chest"][f] = 1 + 0.035 * bump(u) * math.cos(2 * math.pi * u)
for f in seg(A2):
    u = u_of(A2, f); sx["door_c"][f] = 1 - 0.7 * bump(u)       # bản lề trái, 100% -> 30% -> 100%
for f in seg(A3):
    u = u_of(A3, f); rot["door_c_tip"][f] = 12 * wave(u)
for f in seg(A4):
    u = u_of(A4, f); rot["dial"][f] = 40 * wave(u)
for f in seg(A5):
    u = u_of(A5, f); rot["ring"][f] = -360 * (u * u * (3 - 2 * u))
for f in range(A5[2] + A5[3] + 1, F): rot["ring"][f] = -360.0     # đủ 1 vòng = trùng setup; giữ -360 để khỏi quay ngược 1 frame
# --- B: cửa mở vừa
for f in seg(B1):
    u = u_of(B1, f); sx["door_h"][f] = 1 - 0.6 * bump(u)
for f in seg(B2):
    u = u_of(B2, f); rot["door_h_tip"][f] = 10 * wave(u); rot["knob_h"][f] = 22 * wave(u, 1, 0.1)
for f in seg(B3):
    u = u_of(B3, f)
    for i in range(3):
        v = min(1.0, max(0.0, (u - 0.2 * i) / 0.4)); tx[f"bolt_h{i + 1}"][f] = 16 * bump(v)
# --- C: cửa mở hẳn
for f in seg(C1):
    u = u_of(C1, f); sx["door_o"][f] = 1 - 0.6 * bump(u)
for f in seg(C2):
    u = u_of(C2, f); rot["door_o_tip"][f] = 10 * wave(u)
for f in seg(C3):
    u = u_of(C3, f)
    for i in range(3):
        v = min(1.0, max(0.0, (u - 0.2 * i) / 0.4)); tx[f"bolt_o{i + 1}"][f] = 16 * bump(v)     # cha door_o_tip hướng 180 -> x local dương = sang TRÁI thế giới (ra ngoài mép tự do)
# --- D: xu trong rương
for f in seg(D1):
    u = u_of(D1, f)
    for k, b in enumerate(("in_stack5", "in_stack4", "in_stack3")):
        v = min(1.0, max(0.0, (u - 0.2 * k) / 0.5)); rot[b][f] = 12 * wave(v); sx[b][f] = 1 + 0.08 * bump(v)    # sx = dọc (xương chỉ lên)
for f in seg(D2):
    u = u_of(D2, f)
    for i in range(4):
        b = f"in_c{i + 1}"; v = min(1.0, max(0.0, (u - 0.2 * i) / 0.4))
        rot[b][f] = 25 * wave(v); ty[b][f] = (60 + 45 * i) * bump(v)             # c4 (cao nhất) nhảy lên khỏi miệng rương
for f in seg(D3):
    u = u_of(D3, f); rot["in_tilt"][f] = -30 * wave(u); ty["in_tilt"][f] = 70 * bump(u)
# --- E: xu ngoài
for f in seg(E1):
    u = u_of(E1, f)
    for k, b in enumerate(("fg_stack3", "fg_tilt1", "fg_tilt3")):
        v = min(1.0, max(0.0, (u - 0.25 * k) / 0.5))
        if b == "fg_stack3": rot[b][f] = 10 * wave(v); sx[b][f] = 1 + 0.08 * bump(v)
        else: rot[b][f] = 25 * wave(v); ty[b][f] = 30 * bump(v)
for f in seg(E2):
    u = u_of(E2, f)
    for k, b in enumerate(("fg_c1", "fg_c2", "fg_c3", "fg_tilt2")):
        v = min(1.0, max(0.0, (u - 0.2 * k) / 0.4)); rot[b][f] = 25 * wave(v); ty[b][f] = 28 * bump(v)
# --- F: tất cả
for f in seg(F1):
    u = u_of(F1, f); e = bump(u)
    sy["chest"][f] = 1 - 0.06 * e * math.cos(4 * math.pi * u); sx["chest"][f] = 1 + 0.03 * e * math.cos(4 * math.pi * u); rot["chest"][f] = 3 * e * math.sin(4 * math.pi * u)
    for i, b in enumerate(BONES):
        if b in ("root", "chest", "ring") or b.startswith(("door_h", "door_o", "knob_h", "bolt_")): continue
        if b in ("in_stack5", "in_stack4", "in_stack3", "fg_stack3"): rot[b][f] += 7 * e * math.sin(2 * math.pi * (2 * u - 0.07 * i))
        else: rot[b][f] += 12 * e * math.sin(2 * math.pi * (2 * u - 0.07 * i))
    sx["door_c"][f] = 1 - 0.25 * e * (0.5 - 0.5 * math.cos(4 * math.pi * u))
for b in rot:   # F0 == F cuối (loop): mọi kênh bằng setup ở hai đầu (ring: -360 = 0)
    z = lambda v: abs(v) < 1e-9
    assert z(rot[b][0]) and (z(rot[b][-1]) or (b == "ring" and z(rot[b][-1] + 360))) and z(tx[b][-1]) and z(ty[b][-1]) and z(sx[b][-1] - 1) and z(sy[b][-1] - 1), b

def build():
    bones = {}
    for b in BONES:
        tl = {}
        if any(abs(v) > 1e-6 for v in rot[b]): tl["rotate"] = reduce_keys([rot[b]], ["value"], 0.12, True)
        if any(abs(v) > 1e-6 for v in tx[b] + ty[b]): tl["translate"] = reduce_keys([tx[b], ty[b]], ["x", "y"], 0.25, True)
        if any(abs(v - 1) > 1e-6 for v in sx[b] + sy[b]): tl["scale"] = reduce_keys([sx[b], sy[b]], ["x", "y"], 0.002, True)
        if tl: bones[b] = tl
    slots = {}
    for s in DOOR_SLOTS:        # đổi trạng thái cửa theo STEPS; bước F quay về cửa đóng, F0 = setup (cửa đóng)
        keys = []; prev = None
        for name, state, f0, n in STEPS:
            cur = s if s in STATE[state] else None
            if cur != prev:
                keys.append({"time": K.ktime(f0 / FPS, FPS), **({"name": cur} if cur else {})}); prev = cur
        if keys and keys[0]["time"] != 0 and SETUP_ATT[s]:  # đầu anim phải = setup
            keys.insert(0, {"time": 0, "name": SETUP_ATT[s]})
        slots[s] = {"attachment": keys}
    return {"bones": bones, "slots": slots}


if __name__ == "__main__":
    anim = build()
    K.write_anim(JS, "rig_demo", anim, "Claude gen rig_demo (RuongBattlePass)", skel=SK)
    try:
        urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8781/api/spine/anim", json.dumps({"json": REL, "op": "meta", "name": "rig_demo", "loop": True}).encode(),
                               {"Content-Type": "application/json"}), timeout=3).read()
    except Exception:
        pass
    print("rig_demo:", N, "F =", round(N / FPS, 2), "s |", len(anim["bones"]), "xương có key")
    for name, state, f0, n in STEPS: print(f"  F{f0:3d}-{f0 + n:3d}  {name:22s} cửa: {state}")
