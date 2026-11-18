# Fit joints of Mecha Pup (Y up, +Z front, right = -X). rows: (name, parent, world xyz, side, label, radius)
# Only centre + right side are drawn; Build Rig mirrors the right side.
def _r(n, p, w, side, lab, r=0.02): return (n, p, w, side, lab, r)
ROWS = [
    _r("Root_M",   None,      (0.0, 0.34, -0.10), "centre", "root"),
    _r("Spine1_M", "Root_M",  (0.0, 0.36,  0.05), "centre", "spine"),
    _r("Chest_M",  "Spine1_M",(0.0, 0.37,  0.20), "centre", "chest"),
    _r("Neck_M",   "Chest_M", (0.0, 0.43,  0.30), "centre", "neck"),
    _r("Head_M",   "Neck_M",  (0.0, 0.50,  0.31), "centre", "head"),
    _r("HeadEnd_M","Head_M",  (0.0, 0.98,  0.31), "centre", ""),
    # ears (right side, x<0)
    _r("Ear1_R",   "Head_M",  (-0.27, 0.82, 0.30), "right", "prop"),
    _r("Ear2_R",   "Ear1_R",  (-0.30, 0.93, 0.30), "right", "prop"),
    _r("EarEnd_R", "Ear2_R",  (-0.31, 1.02, 0.30), "right", ""),
    # backpack + antenna (centre chain, antenna bends toward -x)
    _r("Backpack_M","Spine1_M",(0.0, 0.50, -0.22), "centre", "prop"),
    _r("Ant1_M",   "Backpack_M",(0.011, 0.68, -0.31), "centre", "prop"),
    _r("Ant2_M",   "Ant1_M",  (-0.013, 0.78, -0.37), "centre", "prop"),
    _r("Dish_M",   "Ant2_M",  (-0.11, 0.86, -0.53), "centre", "prop"),
    _r("Muzzle_M", "Dish_M",  (-0.13, 0.98, -0.60), "centre", ""),
    # tail
    _r("Tail1_M",  "Root_M",  (0.0, 0.40, -0.36), "centre", "prop"),
    _r("Tail2_M",  "Tail1_M", (0.0, 0.42, -0.45), "centre", "prop"),
    _r("TailEnd_M","Tail2_M", (0.0, 0.43, -0.52), "centre", ""),
    # front leg (arm-type chain)
    _r("Shoulder_R","Chest_M",(-0.17, 0.30, 0.20), "right", "shoulder"),
    _r("Elbow_R",  "Shoulder_R",(-0.17, 0.17, 0.20), "right", "elbow"),
    _r("Wrist_R",  "Elbow_R", (-0.15, 0.07, 0.19), "right", "wrist"),
    _r("FToes_R",  "Wrist_R", (-0.14, 0.03, 0.29), "right", "prop"),
    _r("FToesEnd_R","FToes_R",(-0.13, 0.01, 0.34), "right", ""),
    # rear leg (leg-type chain)
    _r("Hip_R",    "Root_M",  (-0.24, 0.32, -0.28), "right", "thigh"),
    _r("Knee_R",   "Hip_R",   (-0.26, 0.19, -0.25), "right", "knee"),
    _r("Ankle_R",  "Knee_R",  (-0.24, 0.08, -0.29), "right", "ankle"),
    _r("Toes_R",   "Ankle_R", (-0.22, 0.03, -0.40), "right", "toe"),
    _r("ToesEnd_R","Toes_R",  (-0.22, 0.01, -0.48), "right", ""),
]
