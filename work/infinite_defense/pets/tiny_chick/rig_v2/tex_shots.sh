#!/bin/bash
OUT=$1
W=work/infinite_defense/pets/tiny_chick/rig_v2
S="/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_13_Tiny_Chick/v2_mesh_moi/shots"
for v in "front 0 0" "side 0 90" "back 0 180" "tq -18 35"; do set -- $v; printf "VIEW=($2,$3)\nexec(open('/home/ngocvb/Projects/AI_animation/$W/cam.py').read())\n" > /tmp/camx.py; python3 -I tools/frolvy_port.py 9883 /tmp/camx.py >/dev/null; python3 -I $W/shot.py 9883 /tmp/tx_$1.png >/dev/null; done
python3 -I - "$S/$OUT.png" <<'PY'
import sys
from PIL import Image
ims=[Image.open("/tmp/tx_%s.png"%n).crop((90,30,390,230)) for n in ("front","side","back","tq")]
w,h=ims[0].size; s=Image.new("RGB",(w*4,h))
for i,im in enumerate(ims): s.paste(im,(i*w,0))
s.resize((s.width*2,s.height*2)).save(sys.argv[1])
PY
