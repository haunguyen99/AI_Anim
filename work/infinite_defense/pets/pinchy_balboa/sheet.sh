# usage: sheet.sh name "frames" cam   -> $P/shots/name.png
P=work/infinite_defense/pets/pinchy_balboa; mkdir -p $P/shots
for f in $2; do
 echo "api.look_through('$3'); api.set_camera_ortho('$3', True); api.set_attr('$3.ow', ${5:-1.6}); api.move('$3', $4); api.set_frame(1); api.set_frame($f)" > $P/_c.py
 .venv/Scripts/python.exe -I tools/frolvy_port.py 9885 $P/_c.py >/dev/null; .venv/Scripts/python.exe -I tools/frolvy_shot.py 9885 $P/shots/_$f.png >/dev/null
done
.venv/Scripts/python.exe -I - <<PY
from PIL import Image
fs="$2".split(); ims=[Image.open(r"$P/shots/_%s.png"%f).crop((100,0,700,337)) for f in fs]
cols=3; rows=(len(ims)+cols-1)//cols; W,H=ims[0].size
S=Image.new("RGB",(W*cols,H*rows))
for i,im in enumerate(ims): S.paste(im,((i%cols)*W,(i//cols)*H))
S.save(r"$P/shots/$1.png")
PY
