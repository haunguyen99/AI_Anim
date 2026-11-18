#!/bin/bash
# usage: sheet.sh <port> <name> <rx> <ry> f1 f2 ...   (clip dang mo; dung camera 3/4, an control) -> shots/<name>.png
P=$1; N=$2; RX=$3; RY=$4; shift 4
W=work/infinite_defense/pets/tiny_chick/rig_v2
S="/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_13_Tiny_Chick/v2_mesh_moi/shots"
printf "VIEW=($RX,$RY)\nexec(open('/home/ngocvb/Projects/AI_animation/$W/cam.py').read())\n" > /tmp/camx.py
python3 -I tools/frolvy_port.py $P /tmp/camx.py >/dev/null 2>&1
FILES=()
for f in "$@"; do echo "api.set_frame($f)" > /tmp/fr.py; python3 -I tools/frolvy_port.py $P /tmp/fr.py >/dev/null 2>&1; python3 -I $W/shot.py $P /tmp/sh_$f.png >/dev/null; FILES+=(/tmp/sh_$f.png); done
python3 -I - "$S/$N.png" "${FILES[@]}" <<'PY'
import sys
from PIL import Image, ImageDraw
out, fs = sys.argv[1], sys.argv[2:]
ims = [Image.open(f).crop((90, 30, 390, 230)) for f in fs]
w, h = ims[0].size; cols = min(4, len(ims)); rows = (len(ims)+cols-1)//cols
sh = Image.new("RGB", (w*cols, h*rows))
for i, im in enumerate(ims):
    d = ImageDraw.Draw(im); d.text((4, 4), "f" + fs[i].split("_")[-1][:-4], fill=(255, 255, 0))
    sh.paste(im, ((i % cols)*w, (i//cols)*h))
sh = sh.resize((sh.width*2//1, sh.height*2//1)) if sh.width < 1300 else sh
sh.save(out)
PY
