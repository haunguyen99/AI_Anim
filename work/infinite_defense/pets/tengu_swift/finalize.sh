#!/bin/bash
# raw_*.fbx (Frolvy) -> 3 FBX cho Unity. Chay tu goc repo.
D="/c/Users/Admin/Documents/Ngoc/EndlessKicker/New_PET/Pet_18_Tengu_Swift"; PY=".venv/Scripts/python.exe -I"; T=$D/_tmp; mkdir -p $T
# Base: bind pose, mesh + skin, 0 anim
SNAP_DEG=0.3 $PY work/infinite_defense/pets/tengu_swift/ghost_rename.py $D/raw_Base.fbx $T/g.fbx
$PY tools/fbx_ascii_keep.py $T/g.fbx $T/b1.fbx --root DEF_Root_M
$PY tools/pet_fbx_finalize.py $T/b1.fbx $T/b2.fbx Base --meshes 2
$PY tools/fbx_unity_bind.py $T/b2.fbx $T/b3.fbx
$PY tools/fbx_strip_anim.py $T/b3.fbx $D/Pet_Tengu_Swift.fbx
# anim-only
for N in Idle Attack; do
  $PY work/infinite_defense/pets/tengu_swift/ghost_rename.py $D/raw_$N.fbx $T/g.fbx
  $PY tools/fbx_ascii_keep.py $T/g.fbx $T/a1.fbx --root DEF_Root_M --no-meshes
  $PY tools/pet_fbx_finalize.py $T/a1.fbx $T/a2.fbx $N --meshes 0
  $PY tools/fbx_add_sibling.py $T/a2.fbx $D/Pet_Tengu_Swift_$N.fbx
done
