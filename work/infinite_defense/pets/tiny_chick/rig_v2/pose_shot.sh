#!/bin/bash
# usage: pose_shot.sh <port> <name> "CTL rx ry rz; ..."  -> shots/t_<name>.png (chay tu goc repo)
P=$1; N=$2; SPEC=$3; W=work/infinite_defense/pets/tiny_chick/rig_v2
S="/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_13_Tiny_Chick/v2_mesh_moi/shots"
python3 - "$N" "$SPEC" <<'PY'
import sys
n, spec = sys.argv[1], sys.argv[2]
code = "api.select([]); api.reset_transforms(all_controls=True)\n"
for part in spec.split(";"):
    p = part.split()
    if p: code += "api.rotate('%s',%s,%s,%s)\n" % (p[0], p[1], p[2], p[3])
code += "api.set_frame(1); api.set_frame(0)\n"
open("/tmp/pose_%s.py" % n, "w").write(code)
PY
python3 -I tools/frolvy_port.py $P /tmp/pose_$N.py >/dev/null 2>&1; python3 -I $W/shot.py $P "$S/t_$N.png" >/dev/null
