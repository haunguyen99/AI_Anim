# Mẫu bảng fit skeleton (Boss Bastion, 2026-10-31)

Script đầy đủ đã dùng: chép từ đây, thay số đo theo model mới. Mét, Y lên, mặt nhìn +Z, phải = −X; chỉ vẽ giữa + phải.
Root ở hông (rig game). Sau khi nạp, người dùng thường chỉnh tay vài joint; lưu lại bằng `api.save_fit_skeleton`.

```python
"""usage: py make_fit.py <out.fvfit>"""
import json, pathlib, sys

def fingers(name, z, xs, ys):
    rows = []; parent = "Wrist"
    for i, (x, y) in enumerate(zip(xs, ys)):
        n = "%sFinger%d" % (name, i + 1)
        rows.append((n, parent, (x, y, z), "finger" if i < 3 else "", "right", 0.009 if i < 3 else 0.005))
        parent = n
    return rows

J = [
    # name, parent, world (x,y,z), label, side, radius
    ("Root",    None,     (0.0, 1.00, -0.01),  "root",  "centre", 0.05),   # hips (Root_M = hip joint)
    ("Spine1",  "Root",   (0.0, 1.18, 0.003),  "spine", "centre", 0.037),
    ("Chest",   "Spine1", (0.0, 1.38, 0.006),  "chest", "centre", 0.044),
    ("Neck",    "Chest",  (0.0, 1.60, -0.045), "neck",  "centre", 0.025),
    ("Head",    "Neck",   (0.0, 1.70, 0.025),  "head",  "centre", 0.039),  # chin height, on the helmet axis
    ("HeadEnd", "Head",   (0.0, 1.90, 0.03),   "",      "centre", 0.021),
    ("Scapula", "Chest",  (-0.082, 1.539, -0.014), "clavicle", "right", 0.021),
    ("Shoulder","Scapula",(-0.358, 1.518, -0.049), "shoulder", "right", 0.031),
    ("Elbow",   "Shoulder",(-0.597, 1.51, -0.07),  "elbow",    "right", 0.027),
    ("Wrist",   "Elbow",  (-0.86, 1.505, -0.05),   "wrist",    "right", 0.021),
    ("ThumbFinger1","Wrist",(-0.875,1.445,0.02),"thumb","right",0.009),   # thumb axes set afterwards (SKILL.md)
    ("ThumbFinger2","ThumbFinger1",(-0.935,1.425,0.042),"thumb","right",0.008),
    ("ThumbFinger3","ThumbFinger2",(-0.975,1.422,0.05),"thumb","right",0.008),
    ("ThumbFinger4","ThumbFinger3",(-1.012,1.42,0.056),"","right",0.005),
] + fingers("Index", 0.03, (-0.98,-1.02,-1.065,-1.115), (1.52,1.517,1.512,1.508)) \
  + fingers("Middle",-0.03, (-0.98,-1.025,-1.075,-1.13), (1.522,1.518,1.512,1.508)) \
  + fingers("Ring", -0.075, (-0.975,-1.015,-1.055,-1.095), (1.522,1.517,1.51,1.497)) \
  + fingers("Pinky", -0.14, (-0.965,-0.995,-1.03,-1.075), (1.52,1.517,1.51,1.502)) + [
    ("Weapon",   "Wrist",  (-0.86, 1.533, -0.0765), "prop", "right", 0.025),   # one-sided prop: delete _L after build
    ("WeaponEnd","Weapon", (-1.53, 1.533, -0.0765), "",     "right", 0.015),
    ("Arrow",    "Weapon", (-0.702, 1.585, -0.0765),"prop", "right", 0.018),   # pivot at the nock
    ("ArrowEnd", "Arrow",  (-1.76, 1.585, -0.0765), "",     "right", 0.010),
    ("ShoulderPad","Scapula",(-0.204,1.694,-0.065),"prop","right",0.02),
    ("ShoulderPadEnd","ShoulderPad",(-0.40,1.632,-0.065),"","right",0.012),
    ("HipPad1",  "Root",   (-0.21, 1.10, 0.0), "prop", "right", 0.018),
    ("HipPad2",  "HipPad1",(-0.26, 0.99, 0.0), "prop", "right", 0.016),
    ("HipPadEnd","HipPad2",(-0.33, 0.85, 0.0), "",     "right", 0.010),
    ("Hip",   "Root",  (-0.17, 0.94, 0.0),    "thigh", "right", 0.033),
    ("Knee",  "Hip",   (-0.178, 0.60, 0.025), "knee",  "right", 0.029),
    ("Ankle", "Knee",  (-0.19, 0.21, -0.045), "ankle", "right", 0.025),
    ("Toes",  "Ankle", (-0.195, 0.05, 0.17),  "toe",   "right", 0.017),
    ("ToesEnd","Toes", (-0.195, 0.04, 0.345), "",      "right", 0.012),
    ("FootSideOuter","Toes",(-0.33, 0.0, 0.12),"foot_outer","right",0.010),
    ("FootSideInner","Toes",(-0.06, 0.0, 0.12),"foot_inner","right",0.010),
    ("Heel",  "Ankle", (-0.195, 0.0, -0.19),  "heel",  "right", 0.012),
]

def doc(name):
    order = [j[0] for j in J]; where = {}; out = []
    for n, p, at, label, side, r in J:
        where[n] = at; above = where[p] if p else (0.0, 0.0, 0.0)
        out.append({"name": n, "parent": -1 if p is None else order.index(p),
                    "translate": [round(at[i] - above[i], 6) for i in range(3)],
                    "rotate": [0.0, 0.0, 0.0, 1.0], "scale": [1.0, 1.0, 1.0], "radius": r,
                    "orient": [0.0, 0.0, 0.0], "rotation_order": 0, "side": side, "label": label,
                    "draw_style": "bone", "draw_label": False, "scale_compensate": False})
    return {"format": "AnimationDCC fit skeleton", "version": 1, "name": name, "joints": out}

if __name__ == "__main__":
    path = pathlib.Path(sys.argv[1])
    path.write_text(json.dumps(doc(path.stem), indent=2) + "\n", encoding="utf-8")
```

Nạp: `api.load_fit_skeleton(path)` (bị từ chối khi scene đã có fit skeleton).
