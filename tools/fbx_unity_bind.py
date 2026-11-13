"""Frolvy ASCII FBX -> Unity bind pose. Unity (2022.3) doc ma tran 'Transform' cua Cluster nhu bindpose truc tiep va khong dung
TransformLink cua Frolvy -> mesh skin bi doi cho 1 doan = vi tri xuong (Pebble Turtle 2026-11-12). Dat Transform = nghich dao
TransformLink (xuong khong xoay: tinh tien doi dau) cho moi cluster; them BindPose (xem fbx_add_bindpose.py).
usage: py tools/fbx_unity_bind.py in.fbx out.fbx"""
import re, sys, subprocess, os
here = os.path.dirname(os.path.abspath(__file__))
tmp = sys.argv[2] + ".tmp"
subprocess.check_call([sys.executable, "-I", os.path.join(here, "fbx_add_bindpose.py"), sys.argv[1], tmp])
t = open(tmp, encoding="utf-8").read(); os.remove(tmp)
def fix(m):
    b = m.group(0)
    link = re.search(r'TransformLink: \*16 \{\s*a: ([^\n]*)', b).group(1)
    v = [float(x) for x in link.split(",")]
    assert all(abs(v[i] - (1.0 if i in (0, 5, 10, 15) else 0.0)) < 1e-5 for i in (0, 1, 2, 4, 5, 6, 8, 9, 10, 15)), "bone has rotation"
    inv = "1,0,0,0,0,1,0,0,0,0,1,0,%.6f,%.6f,%.6f,1" % (-v[12], -v[13], -v[14])
    return re.sub(r'(\n\t\tTransform: \*16 \{\s*a: )[^\n]*', lambda mm: mm.group(1) + inv, b, count=1)
t, n = re.subn(r'\tDeformer: \d+, "SubDeformer::[^"]*", "Cluster" \{.*?\n\t\}', fix, t, flags=re.S)
t = t.replace("-0.000000", "0.000000")
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(t); print("clusters fixed", n)
