"""Mecha Pup fit table (from joints placed in scene + hind foot fix). Run outside Frolvy:
.venv/Scripts/python.exe -I make_fit.py out.fvfit"""
import json, pathlib, sys
here = pathlib.Path(__file__).parent
rows = json.load(open(here / "joints_dump.json"))
def base(n): return n[:-2] if n[-2:] in ("_M", "_R") else n
pos = {base(r[0]): tuple(r[2]) for r in rows}
J = []
for n, p, w, label, side in rows:
    r = 0.04 if label == "root" else 0.03 if label in ("spine","chest","head") else 0.02
    J.append((base(n), base(p) if p else None, tuple(round(v, 4) for v in w), label, side, r))
J += [("Heel", "Ankle", (-0.24, 0.0, -0.46), "heel", "right", 0.012),
      ("FootSideOuter", "Toes", (-0.34, 0.0, -0.28), "foot_outer", "right", 0.01),
      ("FootSideInner", "Toes", (-0.10, 0.0, -0.28), "foot_inner", "right", 0.01)]
def doc(name):
    order = [j[0] for j in J]; where = {}; out = []
    for n, p, at, label, side, r in J:
        where[n] = at; above = where[p] if p else (0.0, 0.0, 0.0)
        out.append({"name": n, "parent": -1 if p is None else order.index(p),
            "translate": [round(at[i]-above[i], 6) for i in range(3)], "rotate": [0.0,0.0,0.0,1.0], "scale": [1.0,1.0,1.0],
            "radius": r, "orient": [0.0,0.0,0.0], "rotation_order": 0, "side": side, "label": label,
            "draw_style": "bone", "draw_label": False, "scale_compensate": False})
    return {"format": "AnimationDCC fit skeleton", "version": 1, "name": name, "joints": out}
if __name__ == "__main__":
    p = pathlib.Path(sys.argv[1]); p.write_text(json.dumps(doc(p.stem), indent=1)); print("wrote", p, len(J))
