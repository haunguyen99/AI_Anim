#!/bin/bash
# Linux: raw_*.fbx (Frolvy) -> 3 FBX cho Unity. Chay tu goc repo: finalize_v2.sh <thu muc raw> <thu muc dich>
R=${1:-/tmp/tg/raw}; D=${2:-/tmp/tg/out}; PY="python3 -I"; T=/tmp/tg/_tmp; mkdir -p $T $D
G=work/infinite_defense/pets/tengu_swift/ghost_rename.py
SNAP_DEG=0.3 $PY $G $R/raw_Base.fbx $T/g.fbx
$PY tools/fbx_ascii_keep.py $T/g.fbx $T/b1.fbx --root DEF_Root_M
$PY tools/pet_fbx_finalize.py $T/b1.fbx $T/b2.fbx Base --meshes 2
$PY tools/fbx_unity_bind.py $T/b2.fbx $T/b3.fbx
$PY tools/fbx_strip_anim.py $T/b3.fbx $D/Pet_Tengu_Swift.fbx
for N in Idle Attack; do
  $PY $G $R/raw_$N.fbx $T/g.fbx
  $PY tools/fbx_ascii_keep.py $T/g.fbx $T/a1.fbx --root DEF_Root_M --no-meshes
  $PY tools/pet_fbx_finalize.py $T/a1.fbx $T/a2.fbx $N --meshes 0
  $PY tools/fbx_add_sibling.py $T/a2.fbx $D/Pet_Tengu_Swift_$N.fbx
done
