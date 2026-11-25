D='/home/ngocvb/Projects/AI_animation/docs/slides/img/rig/'
F="font-family=\"Be Vietnam Pro, Arial, sans-serif\""
BAD='#C2492E';GOOD='#2E7D5B';INK='#16223A';MUT='#4C5568';GOLD='#F0B13B';BG='#FFFFFF'
def w(name,body,W,H):
    open(D+name,'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {F}><rect width="{W}" height="{H}" fill="{BG}"/>{body}</svg>')
def t(x,y,s,size=22,fill=INK,anchor='start',weight=500):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>'

# 1 cổ chân
b=''
b+='<path d="M300 40 L380 40 L385 330 L300 330 Z" fill="#D8DEE8" stroke="#8793A8" stroke-width="3"/>'          # cẳng chân
b+='<path d="M290 330 L395 330 L430 410 L560 420 Q600 430 595 460 L240 460 Q215 440 250 400 Z" fill="#E6D9C2" stroke="#8793A8" stroke-width="3"/>' # bàn chân
b+='<line x1="120" y1="460" x2="640" y2="460" stroke="#8793A8" stroke-width="3"/>'
b+=t(120,490,'sàn (0)',20,MUT)
# thước
for v,y in ((0,460),(0.065,420),(0.115,380),(0.2,300)):
    b+=f'<line x1="150" y1="{y}" x2="170" y2="{y}" stroke="{MUT}" stroke-width="2"/>'+t(142,y+7,f'{v:.3f}'.replace('.',','),18,MUT,'end')
b+=f'<line x1="170" y1="300" x2="170" y2="460" stroke="{MUT}" stroke-width="2"/>'
# joint AI
b+=f'<circle cx="342" cy="380" r="16" fill="{BAD}"/>'+f'<line x1="358" y1="380" x2="640" y2="380" stroke="{BAD}" stroke-width="3" stroke-dasharray="8 6"/>'
b+=t(650,372,'AI đặt: 0,115',24,BAD,'start',700)+t(650,398,'chỗ thắt nhỏ nhất của cẳng chân',19,BAD)
b+=f'<circle cx="342" cy="420" r="16" fill="{GOOD}"/>'+f'<line x1="358" y1="420" x2="640" y2="420" stroke="{GOOD}" stroke-width="3" stroke-dasharray="8 6"/>'
b+=t(650,430,'Đúng: 0,065',24,GOOD,'start',700)+t(650,455,'chỗ chân gặp bàn chân, trên gót',19,GOOD)
b+=f'<line x1="470" y1="380" x2="470" y2="420" stroke="{INK}" stroke-width="3"/><path d="M460 380 L480 380 M460 420 L480 420" stroke="{INK}" stroke-width="3"/>'+t(488,407,'5 cm',24,INK,'start',700)
b+='<defs><marker id="a" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#16223A"/></marker></defs>'
b+=t(20,34,'MeoTom (cao 1 m): vị trí joint cổ chân, nhìn bên · sơ đồ minh hoạ theo số đo',20,MUT)
w('d_ankle.svg',b,980,510)

# 2 hướng bàn chân nhìn từ trên
import math
b=t(20,34,'MeoTom: hướng bàn chân nhìn từ trên · sơ đồ minh hoạ theo số đo',20,MUT)
hx,hy=300,420
def line(ang,col,lab,ly):
    L=300; x=hx+L*math.sin(math.radians(ang)); y=hy-L*math.cos(math.radians(ang))
    return f'<line x1="{hx}" y1="{hy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{col}" stroke-width="5"/>'+f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{col}"/>'+t(x+(16 if col==GOOD else -16),y+(6 if col==GOOD else -14),lab,22,col,'start' if col==GOOD else 'end',700)
b+='<ellipse cx="320" cy="270" rx="110" ry="170" fill="#E6D9C2" stroke="#8793A8" stroke-width="3" transform="rotate(30 320 270)"/>'
for ox,oy in ((470,140),(430,100),(500,200)): b+=f'<circle cx="{ox}" cy="{oy}" r="30" fill="#E6D9C2" stroke="#8793A8" stroke-width="3"/>'
b+=f'<line x1="{hx}" y1="{hy}" x2="{hx}" y2="80" stroke="{MUT}" stroke-width="2" stroke-dasharray="6 6"/>'+t(hx-8,72,'thẳng phía trước',18,MUT,'end')
b+=line(8,BAD,'AI: 5–9°',160)+line(39,GOOD,'Đúng: khoảng 39° xoè ngoài',100)
b+=f'<circle cx="{hx}" cy="{hy}" r="12" fill="{INK}"/>'+t(hx-20,hy+34,'gót',20,INK,'end',700)
b+=t(20,500,'AI đo bằng PCA / hộp nhỏ nhất của đáy bàn chân. Bàn chân là cục tròn có 3 múi ngón xoè nên số đo sai.',18,MUT)
w('d_foot_dir.svg',b,1000,520)

# bar chart helper
def bars(name,title,rows,unit,W=980,rowh=64,maxv=None,note='',x0=300):
    H=70+len(rows)*rowh+(40 if note else 10)
    maxv=maxv or max(v for r in rows for v in r[1:3] if v is not None)
    b=t(20,34,title,20,MUT)
    span=W-x0-190
    for i,(lab,a,bv,la,lb) in enumerate(rows):
        y=60+i*rowh
        b+=t(20,y+30,lab,22,INK,'start',600)
        for k,(v,col,l) in enumerate(((a,BAD,la),(bv,GOOD,lb))):
            if v is None: continue
            yy=y+k*26; wd=max(4,span*v/maxv)
            b+=f'<rect x="{x0}" y="{yy}" width="{wd:.0f}" height="22" rx="4" fill="{col}"/>'+t(x0+wd+8,yy+18,l,19,col,'start',700)
    if note: b+=t(20,H-14,note,18,MUT)
    w(name,b,W,H)
bars('d_ctl_size.svg','MeoTom: cỡ control hai bên sau khi Build (m). Đỏ = bên phải, xanh = bên trái',
     [('Shoulder',0.84,0.15,'R 0,84 m','L 0,15 m'),('Hip',0.49,0.18,'R 0,49 m','L 0,18 m')],'m',note='HipSwinger còn lệch 33 cm khỏi hông. Sửa: soi gương bên có cỡ đúng sang bên kia.')
bars('d_stretch.svg','Hero: độ co giãn cạnh lưới (1,0 = không biến dạng; càng gần 1 càng tốt). Đỏ = trước, xanh = sau sửa',
     [('Sau gối (kéo IK 17 cm)',0.38,0.74,'×0,38','×0,74'),('Nếp bẹn trước',0.36,0.54,'×0,36','×0,54'),('Sau gối: làm mịn quá tay',0.45,0.29,'×0,45 trước','×0,29 sau làm mịn: TỆ HƠN')],'x',maxv=1.0,
     note='Dòng 3 là lỗi ngược: làm mịn 3 lượt mức 0,5 làm sau gối tệ hơn. Hạ 2 lượt × 0,35 và bỏ qua sau gối.')
bars('d_scapula.svg','Hero: số đỉnh bả vai chịu ảnh hưởng của Scapula (trên 79 đỉnh). Đỏ = trước, xanh = sau',
     [('Đỉnh có weight Scapula',20,53,'20 đỉnh (TB 4%)','53 đỉnh (TB 21%)')],'',maxv=79,note='Người dùng: "xoay Scapula thì mesh bả vai phải theo mạnh hơn".')
# root skin
rows=[('SDR06 Base (London)',277,None,'277 đỉnh',''),('EN_zom2_map6',133,None,'133 đỉnh',''),('EN_zom1 / zom2 map2',32,None,'32 đỉnh',''),('map1 (Rau1)',4,None,'4 đỉnh','')]
bars('d_root.svg','Joint root có skin: số đỉnh bị root kéo (quét Unity 2026-11-06). Ở London: 277 / 1199 đỉnh = 23% thân',rows,'',note='Root dời thì mọi đỉnh này bị kéo theo, thân méo. Luật: root không skin, hông là Root_M.')
bars('d_elbow_edges.svg','Hero: số cạnh móp ở khuỷu khi gập 57° (đo chỉ trên phần nhìn thấy, ít hơn = tốt)',
     [('Kéo cả bắp tay theo Elbow',71,None,'71 cạnh xấu',''),('Trước khi sửa',9,None,'9 cạnh xấu',''),('Chỉ phần đầu nằm trong ống',12,None,'12 cạnh xấu','')],'',x0=440,note='Sửa lần 1 (dải dài) làm móp tay; sửa đúng: chỉ phần nằm trong ống giáp = 100% joint của ống.')

# 7 khuỷu
b=t(20,34,'Hero: khuỷu hở khi gập · sơ đồ minh hoạ',20,MUT)
def arm(ox,bend,col):
    s=''
    s+=f'<g transform="translate({ox},200) rotate({bend})"><rect x="-30" y="-48" width="210" height="96" rx="16" fill="#C7D0DE" stroke="#8793A8" stroke-width="3"/></g>'
    s+=f'<rect x="{ox-270}" y="165" width="290" height="70" rx="30" fill="#E6D9C2" stroke="#8793A8" stroke-width="3"/>'
    s+=f'<circle cx="{ox}" cy="200" r="13" fill="{INK}"/>'
    return s
b+=arm(280,0,GOOD)+t(300,330,'duỗi: bắp tay lồng trong ống giáp',20,MUT,'middle')
b+=arm(740,57,BAD)+t(760,330,'gập 57°: đầu bắp tay trượt ra khỏi ống',20,BAD,'middle',700)
b+=f'<ellipse cx="752" cy="200" rx="62" ry="58" fill="none" stroke="{BAD}" stroke-width="4" stroke-dasharray="8 6"/>'+t(830,150,'hở 4,1 cm',24,BAD,'start',700)
b+=t(490,385,'Sửa: phần đầu nằm trong ống = 100% joint của ống (Elbow); trước miệng ống giữ như cũ.',20,INK,'middle',600)
w('d_elbow.svg',b,980,410)
print('ok')

# ---- picker
RED='#D9534F';BLUE='#3B6FB6';YEL='#E8B923';GRN='#4C9A6A';PUR='#8A5FB5'
b=t(20,34,'Picker Hero (57 nút): nhìn chính diện, bên phải nhân vật nằm bên TRÁI trang · sơ đồ bố cục',20,MUT)
b+='<rect x="190" y="50" width="300" height="470" rx="14" fill="#F6F3EE" stroke="#D9D0BE" stroke-width="3"/>'
def btn(x,y,w_,h,c,lab='',circ=False):
    s=f'<circle cx="{x+w_/2}" cy="{y+h/2}" r="{w_/2}" fill="{c}"/>' if circ else f'<rect x="{x}" y="{y}" width="{w_}" height="{h}" rx="4" fill="{c}"/>'
    return s+(t(x+w_/2,y+h/2+5,lab,13,'#fff','middle',700) if lab else '')
# thân giữa
for i,(n,wd) in enumerate((('Head',64),('Neck',64),('Chest',64),('Spine',64),('Hip',64),('Root',84))):
    b+=btn(340-wd/2,70+i*34,wd,22,YEL,n)
# tay (phải nhân vật = trái trang, đỏ)
for k,(n) in enumerate(('Clav','Sh','El','Wr')):
    b+=btn(205+k*0,105+k*28,44,20,RED,n)+btn(431,105+k*28,44,20,BLUE,n)
b+=btn(210,225,44,44,RED,'IK',True)+btn(426,225,44,44,BLUE,'IK',True)
# chân
b+=btn(250,300,50,50,RED,'IK Foot',True)+btn(380,300,50,50,BLUE,'IK Foot',True)
b+=btn(262,360,26,26,RED,'K',True)+btn(392,360,26,26,BLUE,'K',True)
b+=btn(250,400,50,20,RED,'Toes')+btn(380,400,50,20,BLUE,'Toes')
b+=btn(205,300,34,18,'#E7A9A7','Hip')+btn(441,300,34,18,'#A9C1E3','Hip')
# vải
for k in range(3): b+=btn(318,300+k*26,44,18,GRN,'Skirt')
b+=btn(320,470,40,22,'#9A9AA5','Main')
# chú thích
b+=t(560,110,'Đỏ = phải · Xanh dương = trái',24,INK,'start',700)
b+=t(560,150,'Vàng = thân (giữa) · Xanh lá = vải, đạo cụ',24,INK)
b+=t(560,200,'Thân: chỉ FK, nút nhỏ cùng cỡ, xếp dọc',22,MUT)+t(560,230,'giữa hai tay (Root rộng hơn một chút)',22,MUT)
b+=t(560,280,'Tay: Clav, Sh, El, Wr + IK tròn to + Pole',22,MUT)
b+=t(560,320,'Chân: ưu tiên IK tròn to; FK nhỏ, nhạt',22,MUT)
b+=t(560,380,'Không có: nút ngón, IK thân, HipSwinger',22,BAD,'start',600)
b+=t(560,430,'Kiểm: bấm từng nút = đúng control; không nút',22,GOOD,'start',600)+t(560,460,'đè nhau; nút All chứa mọi control',22,GOOD,'start',600)
w('d_picker.svg',b,1130,540)

# ---- kiểm rig ma trận
b=t(20,34,'Kiểm rig: thử cả 4 chi, cả IK và FK (kiểm cũ chỉ thử tay TRÁI) · sơ đồ',20,MUT)
cols=['Tay trái','Tay phải','Chân trái','Chân phải']; rowsn=['IK','FK']
for j,c in enumerate(cols): b+=t(250+j*170+60,80,c,22,INK,'middle',700)
for i,r in enumerate(rowsn):
    b+=t(60,140+i*70,r,24,INK,'start',700)
    for j in range(4):
        ok = (j==0)
        col=GOOD if ok else BAD
        b+=f'<rect x="{250+j*170}" y="{110+i*70}" width="120" height="50" rx="8" fill="{col}" opacity="0.18" stroke="{col}" stroke-width="3"/>'
        b+=t(250+j*170+60,144+i*70,'✓ thử' if ok else '✗ bỏ sót',22,col,'middle',700)
b+=t(60,290,'Lỗi 2026-11-02: group rìu constrain vào DEF cổ tay thì cổ tay DEF thôi chạy.',22,INK)
b+=t(60,324,'Kiểm rig vẫn báo sạch vì mặc định chỉ thử tay trái → luôn thử đủ 4 chi.',22,BAD,'start',700)
b+=t(60,378,'Kiểm thêm: đổi frame rồi pose gốc phải đứng yên;',21,MUT)+t(60,406,'DEF khớp fit ở FK (cả L và R); texture đúng trên viewport.',21,MUT)
w('d_check.svg',b,980,430)

# ---- thứ tự autoSnap
b=t(20,34,'Trả công tắc sau khi thử biến dạng: đúng thứ tự (autoSnap chép pose IK ↔ FK sang control) · sơ đồ',20,MUT)
steps=[('1','Tắt autoSnap'),('2','Trả fkIk'),('3','Trả control'),('4','Bật autoSnap')]
for i,(n,l) in enumerate(steps):
    x=40+i*235
    b+=f'<rect x="{x}" y="80" width="205" height="90" rx="12" fill="#EDE6D8" stroke="{GOOD}" stroke-width="3"/>'+t(x+102,118,n,26,GOOD,'middle',700)+t(x+102,150,l,22,INK,'middle',600)
    if i<3: b+=f'<path d="M{x+210} 125 L{x+230} 125" stroke="{INK}" stroke-width="3"/>'
b+=t(40,230,'Sai thứ tự (bật autoSnap trước khi trả fkIk):',22,BAD,'start',700)+t(40,260,'Frolvy snap control IK theo FK → mất pose IK.',22,BAD,'start',700)
b+=t(40,296,'Hero: tay IK trái về 0; từng làm IKAnkle_L lệch 7 mm, PoleLeg_L lệch 5,6 cm.',21,MUT)
w('d_autosnap.svg',b,980,330)

# ---- xuất FBX
b=t(20,34,'Từ Frolvy tới Unity: các bước xử lý FBX (Pebble Turtle 2026-11-12) · sơ đồ quy trình',20,MUT)
def box(x,y,wd,h,lab1,lab2='',c='#EDE6D8',st='#8793A8'):
    return f'<rect x="{x}" y="{y}" width="{wd}" height="{h}" rx="12" fill="{c}" stroke="{st}" stroke-width="3"/>'+t(x+wd/2,y+34,lab1,22,INK,'middle',700)+(t(x+wd/2,y+62,lab2,18,MUT,'middle') if lab2 else '')
b+=box(30,100,200,90,'FBX Frolvy','ghi cả scene, ASCII')
b+=box(290,100,200,90,'Lọc','giữ cây root + mesh')
b+=box(550,100,200,90,'Finalize','đơn vị ×100, tên take')
b+=box(810,100,200,90,'BindPose','thêm cho file Base',GOOD+'22',GOOD)
for x in (235,495,755): b+=f'<path d="M{x} 145 L{x+50} 145" stroke="{INK}" stroke-width="3"/>'
b+=f'<path d="M910 190 L910 240" stroke="{INK}" stroke-width="3"/>'
b+=box(100,240,380,90,'Base = xương + mesh','bỏ clip tĩnh (strip anim)')
b+=box(540,240,440,90,'File anim = xương + clip','thêm Null "Dummy" cùng cấp',BAD+'22',BAD)
b+=f'<path d="M910 190 L760 240 M910 190 L290 240" stroke="{INK}" stroke-width="2" stroke-dasharray="6 5"/>'
b+=box(100,380,880,80,'Kiểm bằng Unity chạy nền','bound mesh = bound ở bind pose · log import sạch · đường dẫn xương','#fff',GOOD)
w('d_export.svg',b,1020,490)
print('ok2')
