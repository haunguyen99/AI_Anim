import re, sys
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_23_Kitsune_Nine_Mist"
names = {}
for n in ("", "_Idle", "_Attack"):
    p = D + r"\Pet_Kitsune_Nine_Mist%s.fbx" % n; b = open(p, "rb").read(); print(n or "Base", len(b), b[:20])
    t = b.decode("latin1")
    c = lambda pat: len(re.findall(pat, t))
    limbs = re.findall(r'Model: \d+, "Model::([^"]+)", "LimbNode"', t); names[n] = set(limbs)
    print("  mesh", c(r'"Model::[^"]+", "Mesh"'), "geometry", c(r'\nGeometry: '), "skin", c(r'"Deformer::[^"]*", "Skin"'), "cluster", c(r'"SubDeformer::[^"]*", "Cluster"'), "bindpose", c(r'\nPose: .*"BindPose"'),
          "stack", c(r'\nAnimationStack: '), "limbs", len(limbs), "dummy", c(r'Model::Dummy'), "unit", re.findall(r'"UnitScaleFactor", "double", "Number", "",([\d.]+)', t)[:1], "take", re.findall(r'AnimationStack: \d+, "AnimStack::([^"]+)"', t))
    print("  muzzles", sorted(x for x in limbs if "Muzzle" in x))
print("same names Base/Idle/Attack:", names[""] == names["_Idle"] == names["_Attack"], len(names[""]))
t = open(D + r"\Pet_Kitsune_Nine_Mist.fbx", "rb").read().decode("latin1")
for nm in ("DEF_Root_M", "DEF_Head_M", "DEF_Tail3_2_L"):
    i = t.index('Model::%s", "LimbNode"' % nm); seg = t[i:i + 1500]
    print(nm, re.findall(r'P: "Lcl (Translation|Rotation)", "Lcl [^"]+", "", "A[+]?",([-\d.e, ]+)', seg))
