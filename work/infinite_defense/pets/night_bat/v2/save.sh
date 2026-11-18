#!/bin/bash
# Luu scene Frolvy cong 9884 vao v2_mesh_moi (save_scene khong ghi de, Frolvy chan os.remove => xoa o day). Dung: save.sh ten.fv
D="/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_15_Night_Bat/v2_mesh_moi"
rm -f "$D/$1"
echo "api.save_scene('$D/$1')" > /tmp/nb/_save.py
python3 -I /home/ngocvb/Projects/AI_animation/tools/frolvy_port.py 9884 - <<< "print(api.save_scene('$D/$1'))"
ls -la "$D/$1"
