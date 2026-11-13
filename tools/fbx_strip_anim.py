"""Bo toan bo animation (AnimationStack/Layer/CurveNode/Curve + Takes) khoi FBX ASCII: dung cho file Base (bind pose, khong clip).
usage: py tools/fbx_strip_anim.py in.fbx out.fbx"""
import re, sys, collections
sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0] + "/tools") if False else None
import importlib.util, os
spec = importlib.util.spec_from_file_location("k", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fbx_ascii_keep.py")); k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
ANIM = ("AnimationStack", "AnimationLayer", "AnimationCurveNode", "AnimationCurve")
t = open(sys.argv[1], encoding="utf-8").read()
lines, objs, conns = k.parse(t)
drop = {o["id"] for o in objs if o["type"] in ANIM}
cut = set()
for o in objs:
    if o["id"] in drop: cut.update(range(o["span"][0], o["span"][1] + 1))
for i, kind, a, b in conns:
    if a in drop or b in drop:
        cut.add(i)
        if i > 0 and lines[i - 1].lstrip().startswith(";"): cut.add(i - 1)
text = "\n".join(l for i, l in enumerate(lines) if i not in cut)
for ty in ANIM:
    text = re.sub(r'\tObjectType: "%s" \{\s*\n\t\tCount: \d+\n(?:\t\t[^\n]*\n)*?\t\}\n' % ty, "", text)
n = sum(int(c) for c in re.findall(r'ObjectType: "\w+" \{\s*\n\s*Count: (\d+)', re.search(r'Definitions:  \{.*?\n\}', text, flags=re.S).group(0)))
text = re.sub(r'(Definitions:  \{.*?\n\tCount: )\d+', lambda m: m.group(1) + str(n), text, count=1, flags=re.S)
text = re.sub(r'\nTakes:  \{.*?\n\}\n', "\n", text, flags=re.S)
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(text)
print("dropped", len(drop), "anim objects; definitions count", n)
