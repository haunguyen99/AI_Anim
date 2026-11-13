"""Them mot nut Null cung cap voi nhanh xuong vao FBX anim-only (ASCII). Unity coi nut goc DUY NHAT cua file la goc file,
nen 'Cannot find root motion transform DEF_Root_M' khi Copy From Other Avatar tu Base (Base co mesh cung cap voi xuong).
usage: py tools/fbx_add_sibling.py in.fbx out.fbx [ten]"""
import re, sys
t = open(sys.argv[1], encoding="utf-8").read(); name = sys.argv[3] if len(sys.argv) > 3 else "Dummy"
m = '\tModel: 1999001, "Model::%s", "Null" {\n\t\tVersion: 232\n\t\tProperties70:  {\n\t\t\tP: "Lcl Translation", "Lcl Translation", "", "A",0.000000,0.000000,0.000000\n\t\t\tP: "Lcl Rotation", "Lcl Rotation", "", "A",0.000000,0.000000,0.000000\n\t\t\tP: "Lcl Scaling", "Lcl Scaling", "", "A",1.000000,1.000000,1.000000\n\t\t}\n\t\tShading: T\n\t\tCulling: "CullingOff"\n\t}\n\tNodeAttribute: 1999002, "NodeAttribute::", "Null" {\n\t\tTypeFlags: "Null"\n\t}\n' % name
t = re.sub(r'(\nObjects:  \{\n)', lambda x: x.group(1) + m, t, count=1)
t = re.sub(r'(\nConnections:  \{\n)', lambda x: x.group(1) + '\tC: "OO",1999001,0\n\tC: "OO",1999002,1999001\n', t, count=1)
def bump(ty):
    global t
    t, n = re.subn(r'(ObjectType: "%s" \{\s*\n\t\tCount: )(\d+)' % ty, lambda x: x.group(1) + str(int(x.group(2)) + 1), t, count=1)
    assert n, ty
bump("Model"); bump("NodeAttribute")
d = re.search(r'Definitions:  \{\n\tVersion: 100\n\tCount: (\d+)', t)
t = t.replace(d.group(0), d.group(0).replace("Count: " + d.group(1), "Count: %d" % (int(d.group(1)) + 2)), 1)
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(t); print("added sibling", name)
