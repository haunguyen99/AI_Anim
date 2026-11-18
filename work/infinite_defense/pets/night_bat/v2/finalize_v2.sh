#!/bin/bash
# raw_*.fbx (Frolvy, /tmp/nb/exp) -> 3 FBX cho Unity vao thu muc Pet. Chay tu goc repo (Linux).
D="/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_15_Night_Bat"; R=/tmp/nb/exp; T=/tmp/nb/exp/_t; PY="python3 -I"; mkdir -p $T
set -e
W=work/infinite_defense/pets/night_bat
$PY $W/ghost_rename.py $R/raw_Base.fbx $T/g.fbx
$PY tools/fbx_ascii_keep.py $T/g.fbx $T/b1.fbx --root DEF_Root_M
$PY tools/pet_fbx_finalize.py $T/b1.fbx $T/b2.fbx Base --meshes 1
$PY tools/fbx_unity_bind.py $T/b2.fbx $T/b3.fbx
$PY tools/fbx_strip_anim.py $T/b3.fbx "$D/Pet_Night_Bat.fbx"
for N in Idle Attack; do
  $PY $W/ghost_rename.py $R/raw_$N.fbx $T/g.fbx
  $PY tools/fbx_ascii_keep.py $T/g.fbx $T/a1.fbx --root DEF_Root_M --no-meshes
  $PY tools/pet_fbx_finalize.py $T/a1.fbx $T/a2.fbx $N --meshes 0
  $PY tools/fbx_add_sibling.py $T/a2.fbx "$D/Pet_Night_Bat_$N.fbx"
done
