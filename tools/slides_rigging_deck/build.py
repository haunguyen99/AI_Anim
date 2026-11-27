"""Dựng slide 'Rigging 3D bằng AI trong Frolvy' (hướng dẫn cho người mới, 38 trang) -> docs/slides/rigging_3d_cho_nguoi_moi.html
    python3 -I tools/slides_rigging_deck/build.py
Hình: docs/slides/img/rig (ảnh Pet + sơ đồ SVG từ diagrams_a/b.py) và docs/slides/img/windy (tools/windy_slide_images.py)."""
import os
H=os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
src=open('core.py').read().replace("/tmp/rigparts/a_head.html","a_head.html").replace("/tmp/rigparts/z_tail.html","z_tail.html")
exec(src)
import sys
SHORT=len(sys.argv)>1 and sys.argv[1]=='short'   # python3 -I build.py short -> bản ngắn (bước 2 còn 2 trang)
if SHORT:
    TOTAL=8; STEPMAP={9:8}; GATES={1,2,6}   # bản ngắn: bỏ bước Rig test, Export FBX thành bước 8
for f in ('ccmd.py','c1n.py','c2n_short.py' if SHORT else 'c2n.py','c3n.py'): exec(open(f).read())
if SHORT: exec(open('short_edit.py').read())
NAME='rigging_3d_ngan.html' if SHORT else 'rigging_3d_cho_nguoi_moi.html'
build(os.path.join(H,'..','..','docs','slides',NAME)); import re,time
VER=str(int(time.time()))
out=os.path.join(H,'..','..','docs','slides',NAME)
t=open(out).read(); t=re.sub(r'src="(img/[^"?]+)"',lambda m:'src="%s?v=%s"'%(m.group(1),VER),t); open(out,'w').write(t)
print(len(S),'trang')
