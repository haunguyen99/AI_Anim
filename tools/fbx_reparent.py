"""Đổi cha của một Model trong FBX ASCII xuất từ Frolvy. Frolvy chỉ xuất nhóm (Null) ở cấp scene dù trong scene nó là con của một joint
(vd. nhóm vk_Hero_NOVA1 nằm trong DEF_Weapon_R, Nova 2026-11-18): chạy trước fbx_ascii_keep để nhóm đi theo cây xương và không bị lọc mất.
Transform local giữ nguyên (nhóm đặt sẵn tại joint: T 0 R 0 trong Frolvy).
usage: python3 -I tools/fbx_reparent.py in.fbx out.fbx <child> <parent> [--child-type Null]"""
import argparse
import re

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("child"); ap.add_argument("parent")
ap.add_argument("--child-type", default=None, help="Null / Mesh / LimbNode, khi tên trùng nhau")
a = ap.parse_args()
t = open(a.src, encoding="utf-8").read()
ms = re.findall(r'\tModel: (\d+), "Model::([^"]*)", "(\w+)"', t)
kids = [m[0] for m in ms if m[1] == a.child and (a.child_type is None or m[2] == a.child_type)]
pars = [m[0] for m in ms if m[1] == a.parent]
if len(kids) != 1 or len(pars) != 1:
    raise SystemExit("can 1 child va 1 parent duy nhat, thay %d / %d (dung --child-type)" % (len(kids), len(pars)))
c, p = kids[0], pars[0]
pat = re.compile(r'(\tC: "OO",%s,)(\d+)(\n)' % c)
m = pat.search(t)
if not m:
    raise SystemExit("khong thay ket noi cha cua child")
t = pat.sub(lambda mm: mm.group(1) + p + mm.group(3), t, count=1)
open(a.dst, "w", encoding="utf-8", newline="\n").write(t)
print("da dat cha: %s(%s) -> %s (cha cu %s)" % (a.child, c, a.parent, m.group(2)))
