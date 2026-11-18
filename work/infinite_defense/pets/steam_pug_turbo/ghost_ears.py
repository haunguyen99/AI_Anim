"""Tai da xoa nhung Frolvy van xuat ra (DEF_Ear1/2_L/R, joint ma): cat lien ket Model->cha de fbx_ascii_keep --root DEF_Root_M bo ra khoi cay.
usage: ghost_ears.py in.fbx out.fbx"""
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
ids = [int(i) for i in re.findall(r'\tModel: (\d+), "Model::DEF_Ear[12]_[LR]", "LimbNode"', t)]
n = 0
for i in ids:
    t, k = re.subn(r'(;Model::DEF_[^\n]*\n)?\tC: "OO",%d,\d+\n' % i, "", t); n += k
print("ghost ear joints", len(ids), "links cut", n)
open(sys.argv[2], "w", encoding="utf-8", newline="").write(t)
