#!/bin/bash
# raw_*.fbx (Frolvy) -> 3 FBX cho Unity. Chay tu goc repo. (Khong can ghost_rename: rig nay khong dung lai trong cung scene.)
D="/c/Users/Admin/Documents/Ngoc/EndlessKicker/New_PET/Pet_23_Kitsune_Nine_Mist"; PY=".venv/Scripts/python.exe -I"; T=$D/_tmp; mkdir -p $T
$PY tools/fbx_ascii_keep.py $D/raw_Base.fbx $T/b1.fbx --root DEF_Root_M
$PY tools/pet_fbx_finalize.py $T/b1.fbx $T/b2.fbx Base --meshes 1
$PY tools/fbx_unity_bind.py $T/b2.fbx $T/b3.fbx
$PY tools/fbx_strip_anim.py $T/b3.fbx $D/Pet_Kitsune_Nine_Mist.fbx
for N in Idle Attack; do
  $PY tools/fbx_ascii_keep.py $D/raw_$N.fbx $T/a1.fbx --root DEF_Root_M --no-meshes
  $PY tools/pet_fbx_finalize.py $T/a1.fbx $T/a2.fbx $N --meshes 0
  $PY tools/fbx_add_sibling.py $T/a2.fbx $D/Pet_Kitsune_Nine_Mist_$N.fbx
done
