#!/bin/bash
# raw_*.fbx (Frolvy) -> 3 FBX cho Unity. Chay tu goc repo. Rig dung 1 lan trong scene sach nen khong co joint ma (khong can ghost_rename).
D="/c/Users/Admin/Documents/Ngoc/EndlessKicker/New_PET/Pet_14_Lucky_Neko"; PY=".venv/Scripts/python.exe -I"; T=$D/_tmp; mkdir -p $T
# Base: bind pose, mesh + skin, 0 anim
$PY tools/fbx_ascii_keep.py $D/raw_Base.fbx $T/b1.fbx --root DEF_Root_M
$PY tools/pet_fbx_finalize.py $T/b1.fbx $T/b2.fbx Base --meshes 3
$PY tools/fbx_unity_bind.py $T/b2.fbx $T/b3.fbx
$PY tools/fbx_strip_anim.py $T/b3.fbx $D/Pet_Lucky_Neko.fbx
# anim-only
for N in Idle Attack; do
  $PY tools/fbx_ascii_keep.py $D/raw_$N.fbx $T/a1.fbx --root DEF_Root_M --no-meshes
  $PY tools/pet_fbx_finalize.py $T/a1.fbx $T/a2.fbx $N --meshes 0
  $PY tools/fbx_add_sibling.py $T/a2.fbx $D/Pet_Lucky_Neko_$N.fbx
done
