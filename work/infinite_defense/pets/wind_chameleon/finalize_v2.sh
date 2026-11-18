#!/bin/bash
# raw_*.fbx (Frolvy, Linux) -> 3 FBX cho Unity. Chay tu goc repo.  raw trong work/.../wind_chameleon/fbx_tmp/
D="/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_16_Wind_Chameleon"; PY="python3 -I"; W=work/infinite_defense/pets/wind_chameleon; T=$W/fbx_tmp
$PY tools/fbx_ascii_keep.py $T/raw_Base.fbx $T/b1.fbx --root DEF_Root_M || exit 1
$PY tools/pet_fbx_finalize.py $T/b1.fbx $T/b2.fbx Base --meshes 1 || exit 1
$PY tools/fbx_unity_bind.py $T/b2.fbx $T/b3.fbx || exit 1
$PY tools/fbx_strip_anim.py $T/b3.fbx "$D/Pet_Wind_Chameleon.fbx" || exit 1
for N in Idle Attack; do
  $PY tools/fbx_ascii_keep.py $T/raw_$N.fbx $T/a1.fbx --root DEF_Root_M --no-meshes || exit 1
  $PY tools/pet_fbx_finalize.py $T/a1.fbx $T/a2.fbx $N --meshes 0 || exit 1
  $PY tools/fbx_add_sibling.py $T/a2.fbx "$D/Pet_Wind_Chameleon_$N.fbx" || exit 1
done
