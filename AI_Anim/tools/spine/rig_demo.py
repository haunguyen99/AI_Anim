"""Anim `rig_demo`: demo rig trực quan, tự dựng từ BẤT KỲ skeleton JSON (luật 2026-11-19, người dùng: "sau mỗi lệnh rig hãy auto làm
1 anim setup demo rig để demo rig trực quan"). Mỗi xương (trừ root) lần lượt lắc ±biên độ rồi về setup, theo thứ tự cây xương;
xương không có chiều dài / tên ctrl|dir|root* thì dời + phồng thay vì xoay; cuối anim có đoạn "tất cả cùng lắc" để thấy mesh / weight.
Chạy:  .venv/Scripts/python.exe -I tools/spine/rig_demo.py <skeleton.json> [--name rig_demo] [--seg 12] [--amp 18] [--only a,b]
Rig có cấu trúc đặc biệt (kéo mở / khép, chuỗi dải, IK) thì viết demo riêng của nhân vật (mẫu: work/unlock/spine/Unlock/build_anims.py,
hàm build_demo) và vẫn đặt tên anim `rig_demo`. Sau khi ghi: `spine_live_cmd.py show <json> --anim rig_demo` để trang Theo Claude chạy ngay."""
import argparse, json, math, os, sys, urllib.request
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "spine")); sys.path.insert(0, os.path.join(ROOT, "tools"))
import anim_kit as K
from key_reduce import reduce_keys
sys.stdout.reconfigure(encoding="utf-8")
FPS = 30


def build(sk, seg=12, amp=18.0, only=None):
    bones = [b for b in sk["bones"] if b["name"] != "root" and (not only or b["name"] in only)]
    kids = {}
    for b in sk["bones"]:
        kids.setdefault(b.get("parent"), []).append(b["name"])
    N = seg * len(bones) + 2 * seg
    rot = {b["name"]: [0.0] * (N + 1) for b in bones}; trn = {b["name"]: ([0.0] * (N + 1), [0.0] * (N + 1)) for b in bones}
    scl = {b["name"]: [1.0] * (N + 1) for b in bones}
    moveish = lambda b: b.get("length", 0) < 1 or b["name"].lower().startswith(("ctrl", "dir", "root", "main", "global"))
    for i, b in enumerate(bones):
        a, z = i * seg, (i + 1) * seg
        for f in range(a, min(z, N) + 1):
            u = (f - a) / seg
            if moveish(b):
                trn[b["name"]][1][f] = 30 * math.sin(math.pi * u); scl[b["name"]] = [1 + 0.05 * math.sin(math.pi * (g - a) / seg) if a <= g <= z else v for g, v in enumerate(scl[b["name"]])]
            else:
                rot[b["name"]][f] = amp * math.sin(2 * math.pi * u) * (0.6 if kids.get(b["name"]) else 1.0)
    a = seg * len(bones)                                       # đoạn cuối: cả rig cùng lắc (so khớp, weight)
    for i, b in enumerate(bones):
        if moveish(b): continue
        for f in range(a, N + 1):
            u = (f - a) / (2 * seg); rot[b["name"]][f] += 0.5 * amp * math.sin(2 * math.pi * (2 * u - 0.08 * i)) * math.sin(math.pi * u)
    anim = {"bones": {}}
    for b in bones:
        n = b["name"]; tl = {}
        if any(abs(v) > 1e-6 for v in rot[n]): tl["rotate"] = reduce_keys([rot[n]], ["value"], 0.12, True)
        if any(abs(v) > 1e-6 for v in trn[n][1]): tl["translate"] = reduce_keys([trn[n][0], trn[n][1]], ["x", "y"], 0.25, True)
        if any(abs(v - 1) > 1e-6 for v in scl[n]): tl["scale"] = reduce_keys([scl[n], scl[n]], ["x", "y"], 0.002, True)
        if tl: anim["bones"][n] = tl
    return anim, N


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json"); ap.add_argument("--name", default="rig_demo"); ap.add_argument("--seg", type=int, default=12)
    ap.add_argument("--amp", type=float, default=18.0); ap.add_argument("--only", default="")
    a = ap.parse_args()
    sk = K.load(a.json); anim, N = build(sk, a.seg, a.amp, set(filter(None, a.only.split(","))) or None)
    K.write_anim(a.json, a.name, anim, "Claude gen %s (demo rig)" % a.name, skel=sk)
    rel = os.path.relpath(os.path.abspath(a.json), ROOT).replace(os.sep, "/")
    try:
        urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8781/api/spine/anim", json.dumps({"json": rel, "op": "meta", "name": a.name, "loop": True}).encode(),
                               {"Content-Type": "application/json"}), timeout=3).read()
    except Exception:
        pass
    print("%s: %dF loop, %d xương lần lượt (%d F mỗi xương) -> %s" % (a.name, N, len(anim["bones"]), a.seg, a.json))
