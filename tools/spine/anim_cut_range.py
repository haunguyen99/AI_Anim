"""Cắt bỏ một đoạn frame khỏi một anim Spine 4.2, giữ nguyên mọi key khác (kể cả key người dùng sửa tay).

  python -I tools/spine/anim_cut_range.py <skeleton.json> <anim> <f0> <f1> [--fps 30] [--keep-start]

- Key trong (f0, f1) bị xoá; key từ f1 trở đi lùi (f1 - f0) frame (cả tay cầm curve, event).
- Kênh có key ở cả f0 và f1: mặc định giữ key f1 (tư thế đi tiếp, curve ra của nó giữ nguyên), tay cầm curve đi vào
  của đoạn trước được dời theo độ chênh giá trị để giữ dáng curve. `--keep-start`: giữ key f0.
- Đoạn nối qua chỗ cắt mà key kế bị xoá: curve dựng lại ease in-out (tiếp tuyến phẳng).
- Ghi qua claude_backup (Hoàn tác được trên Spine Live). Không đổi anim khác.
"""
import argparse, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EPS = 1e-4

FIELDS = {"rotate": (["value"], [0.0]), "translate": (["x", "y"], [0.0, 0.0]), "scale": (["x", "y"], [1.0, 1.0]),
          "shear": (["x", "y"], [0.0, 0.0]), "translatex": (["value"], [0.0]), "translatey": (["value"], [0.0]),
          "scalex": (["value"], [1.0]), "scaley": (["value"], [1.0]), "shearx": (["value"], [0.0]),
          "sheary": (["value"], [0.0]), "alpha": (["value"], [1.0])}


def vals(k, kind):
    fl, df = FIELDS[kind]
    return [float(k.get(f, d)) for f, d in zip(fl, df)]


def cut_keys(keys, kind, t0, t1, keep_start):
    dt = t1 - t0
    curved = kind in FIELDS
    out, orig_next = [], []
    for i, k in enumerate(keys):
        t = k.get("time", 0.0)
        if t <= t0 + EPS:
            out.append(dict(k)); orig_next.append(i)
        elif t < t1 - EPS:
            continue
        else:
            n = dict(k)
            n["time"] = round(t - dt, 5)
            if isinstance(n.get("curve"), list):
                c = list(n["curve"])
                for j in range(0, len(c), 4):
                    c[j] = round(c[j] - dt, 6); c[j + 2] = round(c[j + 2] - dt, 6)
                n["curve"] = c
            out.append(n); orig_next.append(i)
    # gộp hai key trùng f0
    res, src = [], []
    for k, i in zip(out, orig_next):
        if res and abs(res[-1].get("time", 0.0) - k.get("time", 0.0)) < EPS:
            old = res[-1]
            if keep_start:
                continue
            if curved and len(res) >= 2 and isinstance(res[-2].get("curve"), list):
                dv = [a - b for a, b in zip(vals(k, kind), vals(old, kind))]
                c = list(res[-2]["curve"])
                for ch, d in enumerate(dv):
                    c[ch * 4 + 3] = round(c[ch * 4 + 3] + d, 4)
                res[-2]["curve"] = c
            res[-1], src[-1] = k, i
            continue
        res.append(k); src.append(i)
    # đoạn nối qua chỗ cắt mà key kế cũ đã bị xoá: dựng lại curve
    for j in range(len(res) - 1):
        if src[j + 1] != src[j] + 1 and res[j].get("time", 0.0) <= t0 + EPS and curved \
                and res[j].get("curve") != "stepped":
            ta, tb = res[j].get("time", 0.0), res[j + 1]["time"]
            h = (tb - ta) / 3
            c = []
            for va, vb in zip(vals(res[j], kind), vals(res[j + 1], kind)):
                c += [round(ta + h, 6), round(va, 4), round(tb - h, 6), round(vb, 4)]
            res[j]["curve"] = c
    if res and "time" in res[0] and res[0]["time"] < EPS:
        res[0].pop("time")
    if res and "curve" in res[-1]:
        res[-1].pop("curve")
    return res


def cut_anim(anim, f0, f1, fps=30, keep_start=False):
    t0, t1 = f0 / fps, f1 / fps
    for grp in ("bones", "slots"):
        for tl in anim.get(grp, {}).values():
            for kind in list(tl):
                tl[kind] = cut_keys(tl[kind], kind, t0, t1, keep_start)
    ev = []
    for e in anim.get("events", []):
        t = e.get("time", 0.0)
        if t <= t0 + EPS:
            ev.append(e)
        elif t >= t1 - EPS:
            e = dict(e); e["time"] = round(t - (t1 - t0), 5); ev.append(e)
    if "events" in anim:
        anim["events"] = ev
    return anim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json"); ap.add_argument("anim"); ap.add_argument("f0", type=float); ap.add_argument("f1", type=float)
    ap.add_argument("--fps", type=float, default=30); ap.add_argument("--keep-start", action="store_true")
    a = ap.parse_args()
    d = json.load(open(a.json, encoding="utf-8"))
    cut_anim(d["animations"][a.anim], a.f0, a.f1, a.fps, a.keep_start)
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    try:
        import spine_live_cmd
        spine_live_cmd.claude_backup(os.path.abspath(a.json), f"Claude cắt F{a.f0:g}-{a.f1:g} khỏi {a.anim}")
    except Exception as e:
        print("(không backup Spine Live:", e, ")")
    json.dump(d, open(a.json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"đã cắt F{a.f0:g}-{a.f1:g} khỏi {a.anim}")


if __name__ == "__main__":
    main()
