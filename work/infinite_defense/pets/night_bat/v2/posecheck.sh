#!/bin/bash
# posecheck.sh out.png cams "pose python"  : dat pose (control) roi chup 1 frame (khong key). Reset ve 0 truoc.
R="for c in api.ls('Curve'):\n    if c.startswith('CTL_') and c != 'CTL_Main': api.rotate(c,0,0,0); api.move(c,0,0,0)\n"
printf "$R%s\n" "$3" > /tmp/nb/_pose.py
python3 -I /home/ngocvb/Projects/AI_animation/tools/frolvy_port.py 9884 /tmp/nb/_pose.py
python3 -I /home/ngocvb/Projects/AI_animation/work/infinite_defense/pets/night_bat/shot_v2.py "$1" 0 "$2" 0.95 0.33
