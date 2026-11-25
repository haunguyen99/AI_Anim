"""Dựng slide 'Rigging 3D bằng AI trong Frolvy' (hướng dẫn cho người mới, 38 trang) -> docs/slides/rigging_3d_cho_nguoi_moi.html
    python3 -I tools/slides_rigging_deck/build.py
Hình: docs/slides/img/rig (ảnh Pet + sơ đồ SVG từ diagrams_a/b.py) và docs/slides/img/windy (tools/windy_slide_images.py)."""
import os
H=os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
src=open('core.py').read().replace("/tmp/rigparts/a_head.html","a_head.html").replace("/tmp/rigparts/z_tail.html","z_tail.html")
exec(src)
for f in ('c1.py','c2.py','c3.py'): exec(open(f).read())
build(os.path.join(H,'..','..','docs','slides','rigging_3d_cho_nguoi_moi.html')); print(len(S),'trang')
