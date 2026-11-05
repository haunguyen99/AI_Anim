"""Hero RPG2 (Char_Main_T2) fit skeleton. usage: py make_fit.py <out.fvfit>
Measured 2026-11-04 from edge sections of char_main_t2_body / scarf meshes (metres, Y up, face +Z, right = -X)."""
import json, pathlib, sys
J = [
    ("Root",    None,     (0.0, 0.86, 0.07),  "root",  "centre", 0.045),
    ("Spine1",  "Root",   (0.0, 1.02, 0.05),  "spine", "centre", 0.035),
    ("Chest",   "Spine1", (0.0, 1.18, 0.04),  "chest", "centre", 0.04),
    ("Neck",    "Chest",  (0.0, 1.36, 0.035), "neck",  "centre", 0.022),
    ("Head",    "Neck",   (0.0, 1.41, 0.06),  "head",  "centre", 0.035),
    ("HeadEnd", "Head",   (0.0, 1.80, 0.08),  "",      "centre", 0.02),
    ("Scapula", "Chest",  (-0.05, 1.31, 0.03),  "clavicle", "right", 0.018),
    ("Shoulder","Scapula",(-0.24, 1.265, 0.03), "shoulder", "right", 0.028),
    ("Elbow",   "Shoulder",(-0.53, 1.27, 0.025),"elbow",    "right", 0.024),
    ("Wrist",   "Elbow",  (-0.725, 1.255, 0.045),"wrist",   "right", 0.02),
    ("ThumbFinger1","Wrist",(-0.775,1.235,0.10),"thumb","right",0.009),
    ("ThumbFinger2","ThumbFinger1",(-0.81,1.22,0.135),"thumb","right",0.008),
    ("ThumbFinger3","ThumbFinger2",(-0.845,1.205,0.15),"thumb","right",0.008),
    ("ThumbFinger4","ThumbFinger3",(-0.875,1.197,0.16),"","right",0.005),
    # mitten hand: one finger chain for the fused fingers
    ("MiddleFinger1","Wrist",(-0.865,1.258,0.045),"finger","right",0.009),
    ("MiddleFinger2","MiddleFinger1",(-0.905,1.256,0.045),"finger","right",0.009),
    ("MiddleFinger3","MiddleFinger2",(-0.935,1.252,0.045),"finger","right",0.009),
    ("MiddleFinger4","MiddleFinger3",(-0.965,1.245,0.045),"","right",0.005),
    # dual blades: one per hand, keep both sides after build
    ("Weapon",   "Wrist",  (-0.80, 1.245, 0.05), "prop", "right", 0.02),
    ("WeaponEnd","Weapon", (-0.80, 1.245, 0.45), "",     "right", 0.012),
    # red scarf tails (secondary motion, GDD): one-sided, delete _L after build
    ("ScarfA1", "Chest",  (-0.18, 1.30, -0.06), "prop", "right", 0.016),
    ("ScarfA2", "ScarfA1",(-0.18, 1.10, -0.105),"prop", "right", 0.015),
    ("ScarfA3", "ScarfA2",(-0.24, 0.90, -0.13), "prop", "right", 0.014),
    ("ScarfA4", "ScarfA3",(-0.33, 0.70, -0.21), "prop", "right", 0.013),
    ("ScarfAEnd","ScarfA4",(-0.41, 0.58, -0.25),"",     "right", 0.01),
    ("ScarfB1", "Root",   (-0.01, 0.92, -0.07), "prop", "right", 0.016),
    ("ScarfB2", "ScarfB1",(-0.12, 0.70, -0.117),"prop", "right", 0.015),
    ("ScarfB3", "ScarfB2",(-0.21, 0.50, -0.163),"prop", "right", 0.014),
    ("ScarfBEnd","ScarfB3",(-0.27, 0.36, -0.24),"",     "right", 0.01),
    ("Hip",   "Root",  (-0.12, 0.80, 0.07),   "thigh", "right", 0.03),
    ("Knee",  "Hip",   (-0.15, 0.44, 0.085),  "knee",  "right", 0.026),
    ("Ankle", "Knee",  (-0.167, 0.10, 0.04),  "ankle", "right", 0.022),
    ("Toes",  "Ankle", (-0.175, 0.04, 0.22),  "toe",   "right", 0.016),
    ("ToesEnd","Toes", (-0.175, 0.03, 0.337), "",      "right", 0.01),
    ("FootSideOuter","Toes",(-0.267, 0.0, 0.15),"foot_outer","right",0.01),
    ("FootSideInner","Toes",(-0.085, 0.0, 0.15),"foot_inner","right",0.01),
    ("Heel",  "Ankle", (-0.165, 0.0, -0.06),  "heel",  "right", 0.012),
]
def doc(name):
    order=[j[0] for j in J]; where={}; out=[]
    for n,p,at,label,side,r in J:
        where[n]=at; above=where[p] if p else (0.0,0.0,0.0)
        out.append({"name":n,"parent":-1 if p is None else order.index(p),
            "translate":[round(at[i]-above[i],6) for i in range(3)],
            "rotate":[0.0,0.0,0.0,1.0],"scale":[1.0,1.0,1.0],"radius":r,
            "orient":[0.0,0.0,0.0],"rotation_order":0,"side":side,"label":label,
            "draw_style":"bone","draw_label":False,"scale_compensate":False})
    return {"format":"AnimationDCC fit skeleton","version":1,"name":name,"joints":out}
if __name__=="__main__":
    path=pathlib.Path(sys.argv[1]); path.write_text(json.dumps(doc(path.stem),indent=2)+"\n",encoding="utf-8"); print(path)
