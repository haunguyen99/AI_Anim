#!/bin/bash
# raw_*.fbx (Frolvy, /tmp/pet12) -> 3 FBX cho Unity, ghi vao thu muc Pet. Chay tu goc repo. (Muzzle khong phai DEF_Muzzle_M: canh bao "missing DEF_Muzzle_M" la binh thuong.)
D="/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_12_Pebble_Turtle"; R=/tmp/pet12; PY="python3 -I"; T=$R/_tmp; mkdir -p $T
$PY tools/fbx_ascii_keep.py $R/raw_Base.fbx $T/b1.fbx --root DEF_Root_M
$PY tools/pet_fbx_finalize.py $T/b1.fbx $T/b2.fbx Base --meshes 1
$PY tools/fbx_unity_bind.py $T/b2.fbx $T/b3.fbx
$PY tools/fbx_strip_anim.py $T/b3.fbx "$D/Pet_Pebble_Turtle.fbx"
for N in Idle Attack; do
  $PY tools/fbx_ascii_keep.py $R/raw_$N.fbx $T/a1.fbx --root DEF_Root_M --no-meshes
  $PY tools/pet_fbx_finalize.py $T/a1.fbx $T/a2.fbx $N --meshes 0
  $PY tools/fbx_add_sibling.py $T/a2.fbx "$D/Pet_Pebble_Turtle_$N.fbx"
done
