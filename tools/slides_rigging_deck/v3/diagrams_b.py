import math
D='/home/ngocvb/Projects/AI_animation/docs/slides/img/rig/'
F="font-family=\"Be Vietnam Pro, Arial, sans-serif\""
BAD='#C2492E';GOOD='#2E7D5B';INK='#16223A';MUT='#4C5568';GOLD='#F0B13B';BLUE='#3B6FB6';CARD='#EDE6D8'
def w(name,body,W,H,bg='#FFFFFF'):
    open(D+name,'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {F}><rect width="{W}" height="{H}" fill="{bg}"/>{body}</svg>')
def t(x,y,s,size=24,fill=INK,anchor='start',weight=500): return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>'
def box(x,y,wd,h,fill=CARD,st='#8793A8',r=14): return f'<rect x="{x}" y="{y}" width="{wd}" height="{h}" rx="{r}" fill="{fill}" stroke="{st}" stroke-width="3"/>'
def arrow(x1,y1,x2,y2,col=INK): 
    a=math.atan2(y2-y1,x2-x1); h=14
    return f'<line x1="{x1}" y1="{y1}" x2="{x2-10*math.cos(a)}" y2="{y2-10*math.sin(a)}" stroke="{col}" stroke-width="4"/><path d="M{x2} {y2} L{x2-h*math.cos(a-0.45)} {y2-h*math.sin(a-0.45)} L{x2-h*math.cos(a+0.45)} {y2-h*math.sin(a+0.45)} Z" fill="{col}"/>'
def dot(x,y,r=11,c=GOLD): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="{INK}" stroke-width="3"/>'
# 1 IK / FK
b=t(20,38,'IK và FK: hai cách điều khiển cùng một cái tay',24,MUT)
# FK
b+=box(20,60,470,420)+t(255,100,'FK: xoay từng khớp',28,INK,'middle',700)
pts=[(90,300),(200,230),(310,290)]
b+=f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{INK}" stroke-width="8"/>'
for (x,y),n in zip(pts,('Vai','Khuỷu','Cổ tay')): b+=dot(x,y,13)+t(x,y+44,n,22,INK,'middle',600)
b+=f'<path d="M110 270 A 40 40 0 0 1 150 265" fill="none" stroke="{BAD}" stroke-width="4"/>'+t(100,246,'① xoay',20,BAD,'start',700)
b+=f'<path d="M215 255 A 40 40 0 0 1 245 285" fill="none" stroke="{BAD}" stroke-width="4"/>'+t(250,262,'② xoay',20,BAD,'start',700)
b+=t(255,400,'Muốn đặt bàn tay ở đâu thì xoay vai,',22,MUT,'middle')+t(255,430,'rồi khuỷu, rồi cổ tay, từng bước.',22,MUT,'middle')
b+=t(255,462,'Hợp: vung tay, đánh nhịp',22,GOOD,'middle',700)
# IK
b+=box(520,60,470,420)+t(755,100,'IK: kéo bàn tay',28,INK,'middle',700)
pts2=[(590,300),(690,215),(800,285)]
b+=f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts2)}" fill="none" stroke="{INK}" stroke-width="8"/>'
for (x,y),n in zip(pts2,('Vai','Khuỷu','Cổ tay')): b+=dot(x,y,13)+t(x,y+44,n,22,INK,'middle',600)
b+=f'<circle cx="880" cy="250" r="26" fill="none" stroke="{BAD}" stroke-width="5"/>'+t(880,205,'control',20,BAD,'middle',700)
b+=arrow(810,282,850,262,BAD)
b+=t(755,400,'Kéo control ở bàn tay, vai và khuỷu',22,MUT,'middle')+t(755,430,'tự gập theo cho vừa.',22,MUT,'middle')
b+=t(755,462,'Hợp: chống tay, chạm vật, chân bám sàn',22,GOOD,'middle',700)
w('d_ikfk.svg',b,1010,500)
# 2 pipeline
b=t(20,38,'Rigging nằm ở đâu trong quy trình làm game',24,MUT)
items=[('Model','vỏ nhân vật','(chưa cử động được)'),('Rig','xương + dây kéo','(việc của slide này)'),('Anim','animator kéo control','tạo chuyển động'),('Unity','file FBX trong game','')]
for i,(a,b1,c) in enumerate(items):
    x=30+i*270; hl=(i==1)
    b+=box(x,80,220,200,fill=('#FFF3D6' if hl else CARD),st=(GOLD if hl else '#8793A8'))+t(x+110,135,a,36,INK,'middle',800)+t(x+110,185,b1,19,INK,'middle')+t(x+110,220,c,19,(BAD if hl else MUT),'middle',(700 if hl else 500))
    if i<3: b+=arrow(x+225,180,x+265,180)
b+=t(560,330,'Không có rig thì animator không có gì để kéo; rig sai thì anim đẹp mấy cũng méo.',24,INK,'middle',600)
w('d_pipeline.svg',b,1100,370)
# 3 roles
b=t(20,38,'Ai làm gì trong việc rig bằng AI',24,MUT)
cols=[('BẠN',GOLD,['Giao việc: nhân vật, file','Duyệt ở các cổng','Góp ý: khoanh trên hình','Nói "chốt" mới xuất file']),
      ('AI',GOOD,['Làm từng bước theo thứ tự','Báo bằng số + hình','Tự kiểm trước khi gửi bạn','Ghi cái chưa kiểm']),
      ('FROLVY',BLUE,['Phần mềm làm rig','Nơi dựng xương, dây, da','AI điều khiển qua cầu nối','Bạn mở ra xem trực tiếp'])]
for i,(n,c,ls) in enumerate(cols):
    x=30+i*350
    b+=box(x,70,320,360,fill='#fff',st=c)+f'<rect x="{x}" y="70" width="320" height="56" rx="14" fill="{c}"/>'+t(x+160,108,n,30,'#fff','middle',800)
    for k,l in enumerate(ls): b+=t(x+20,175+k*64,'• '+l,21,INK)
b+=arrow(352,250,378,250,MUT)+arrow(702,250,728,250,MUT)
w('d_roles.svg',b,1100,470)
# 4 UV flip
b=t(20,38,'Bẫy texture: Frolvy hiển thị ảnh lật dọc',24,MUT)
def sq(x,lab,lab2,flip,col):
    s=box(x,80,200,200,fill='#fff',st=col)+f'<g transform="translate({x+100},{180}) scale(1,{-1 if flip else 1})"><text x="0" y="48" font-size="130" fill="{INK}" text-anchor="middle" font-weight="800">F</text></g>'
    return s+t(x+100,318,lab,21,col,'middle',700)+t(x+100,346,lab2,19,MUT,'middle')
b+=sq(30,'Ảnh gốc','(Unity dùng ảnh này)',False,GOOD)+arrow(245,180,300,180)+sq(310,'Nạp thẳng vào Frolvy','hiện bị lật dọc',True,BAD)+arrow(525,180,580,180)+sq(590,'Lật ảnh trước rồi nạp','hiện đúng (chỉ để xem)',False,MUT)
b+=t(30,400,'FBX và Unity vẫn dùng ảnh gốc, không dùng ảnh đã lật.',21,INK)
w('d_uvflip.svg',b,820,430)
# 5 staff control Windy
b=t(20,38,'Windy: gậy có hai dây điều khiển',24,MUT)
b+=box(30,70,420,260,fill='#fff',st=GOOD)+t(240,112,'Chế độ A: gậy theo tay',26,GOOD,'middle',700)
b+=dot(100,220,14)+t(100,262,'Cổ tay phải',20,INK,'middle')+arrow(120,215,210,190,MUT)+f'<rect x="215" y="165" width="190" height="16" rx="8" fill="#B9955C" stroke="{INK}" stroke-width="3"/>'+t(310,152,'gậy',20,INK,'middle',600)
b+=t(240,300,'Dây ở tay phải: gậy đi theo tay',20,MUT,'middle')
b+=box(480,70,420,260,fill='#fff',st=BAD)+t(690,112,'Chế độ B: gậy bay tự do',26,BAD,'middle',700)
b+=f'<circle cx="560" cy="230" r="22" fill="none" stroke="{BAD}" stroke-width="5"/>'+t(560,274,'dây đích',19,BAD,'middle',700)+f'<rect x="640" y="170" width="190" height="16" rx="8" fill="#B9955C" stroke="{INK}" stroke-width="3" transform="rotate(-20 735 178)"/>'+arrow(585,222,650,195,BAD)
b+=t(690,312,'gậy bay theo dây này',20,MUT,'middle')
b+=t(30,380,'Hai chế độ: A gậy theo tay. B (chiêu cuối) gậy bay theo dây đích.',21,BAD,'start',700)+t(30,410,'AI sẽ chuyển chế độ khi cần, bạn không phải làm.',21,INK)
w('d_staffctl.svg',b,930,440)
# 6 skin rule
b=t(20,38,'Mức bám: mỗi điểm trên da nghe lời xương nào, bao nhiêu phần',24,MUT)
b+=box(30,70,880,230,fill='#fff',st='#8793A8')+t(60,112,'Điểm ở giữa khuỷu: bám cả xương Vai và xương Khuỷu',26,INK,'start',700)
cols=[(0,'Gần vai'),(1,''),(2,'Ở khớp'),(3,''),(4,'Gần khuỷu')]
for i,(k,l) in enumerate(cols):
    x=70+i*170; v=1-i/4
    b+=f'<rect x="{x}" y="150" width="130" height="34" fill="{GOLD}"/><rect x="{x+130*v}" y="150" width="{130*(1-v)}" height="34" fill="{BLUE}"/>'
    b+=t(x+65,214,f'{int(v*100)}% / {int((1-v)*100)}%',20,INK,'middle',700)+(t(x+65,246,l,20,MUT,'middle') if l else '')
b+=f'<rect x="70" y="262" width="26" height="18" fill="{GOLD}"/>'+t(104,278,'Xương Vai',19)+f'<rect x="250" y="262" width="26" height="18" fill="{BLUE}"/>'+t(284,278,'Xương Khuỷu',19)
b+=box(30,320,880,110,fill='#FFF3D6',st=GOLD)+t(60,362,'Windy: gậy là mảnh cứng, mỗi điểm bám 100% một xương (không chia).',24,INK,'start',700)+t(60,400,'Thân người: mỗi điểm chia cho tối đa 4 xương, tổng luôn 100%.',24,INK)
w('d_skinrule.svg',b,940,450)
# 7 Build
b=t(20,38,'Build Rig: từ bộ xương trần ra rig dùng được',24,MUT)
b+=box(30,80,260,210,fill='#fff',st='#8793A8')+t(160,125,'Trước Build',26,INK,'middle',700)+t(160,170,'chỉ có bộ xương',22,MUT,'middle')+t(160,205,'đã đặt đúng chỗ',22,MUT,'middle')+t(160,250,'không điều khiển được',21,BAD,'middle',600)
b+=arrow(300,185,400,185)+box(410,110,160,150,fill='#FFF3D6',st=GOLD)+t(490,180,'Build',30,INK,'middle',800)+t(490,215,'Rig',30,INK,'middle',800)
b+=arrow(580,185,680,185)
b+=box(690,80,330,210,fill='#fff',st=GOOD)+t(855,125,'Sau Build',26,INK,'middle',700)+t(855,165,'+ xương dùng cho game',21,INK,'middle')+t(855,200,'+ dây điều khiển (thứ bạn kéo)',21,INK,'middle')+t(855,235,'+ công tắc IK / FK',21,INK,'middle')
b+=t(30,345,'Trước khi bấm: bỏ xương phụ game không cần · xương gốc ở hông',22,BAD,'start',700)
w('d_build.svg',b,1050,380)
print('ok')
# 8 BindPose / Dummy
b=t(20,38,'Hai lỗi hay gặp khi FBX từ Frolvy vào Unity',24,MUT)
b+=box(30,70,440,330,fill='#fff',st=BAD)+t(250,110,'Thiếu thông tin tư thế gốc',28,BAD,'middle',700)
b+=f'<ellipse cx="250" cy="300" rx="90" ry="70" fill="#D8DEE8" stroke="#8793A8" stroke-width="3"/>'+f'<circle cx="360" cy="170" r="48" fill="#E6D9C2" stroke="#8793A8" stroke-width="3"/>'+arrow(300,250,330,205,BAD)
b+=t(250,390,'đầu bay khỏi thân',22,BAD,'middle',700)
b+=box(500,70,440,330,fill='#fff',st=GOOD)+t(720,110,'Đủ thông tin tư thế gốc',28,GOOD,'middle',700)
b+=f'<ellipse cx="720" cy="300" rx="90" ry="70" fill="#D8DEE8" stroke="#8793A8" stroke-width="3"/>'+f'<circle cx="720" cy="195" r="48" fill="#E6D9C2" stroke="#8793A8" stroke-width="3"/>'
b+=t(720,390,'đầu nằm đúng chỗ',22,GOOD,'middle',700)
b+=box(30,430,440,160,fill='#fff',st=BAD)+t(250,470,'File chuyển động: thiếu điểm phụ',24,BAD,'middle',700)+box(150,490,200,50,fill='#FDECE7',st=BAD)+t(250,522,'Điểm gốc',22,INK,'middle',600)+t(250,570,'→ game báo lỗi',19,BAD,'middle')
b+=box(500,430,440,160,fill='#fff',st=GOOD)+t(720,470,'Thêm một điểm phụ',24,GOOD,'middle',700)+box(520,490,180,50,fill='#E6F2EC',st=GOOD)+t(610,522,'Điểm phụ',22,INK,'middle',600)+box(740,490,180,50,fill='#E6F2EC',st=GOOD)+t(830,522,'Điểm gốc',22,INK,'middle',600)+t(720,570,'→ chạy được',19,GOOD,'middle')
w('d_bindpose.svg',b,970,610)
# 9 Bắt đầu từ đâu
b=t(20,38,'Bắt đầu từ đâu: 4 việc đầu tiên',24,MUT)
steps=[('1','Mở Frolvy','phần mềm làm rig;\nnhân vật hiện ra'),('2','Mở khung chat với AI','nơi bạn gõ yêu cầu\nvà xem AI trả lời'),('3','Đưa file + câu đầu','nói tên nhân vật,\nfile model, yêu cầu'),('4','Xem hình AI gửi','AI dừng ở mỗi cổng,\nbạn duyệt hoặc góp ý')]
for i,(n,a,c) in enumerate(steps):
    x=30+i*270
    b+=box(x,80,240,300,fill='#fff',st=GOLD)+f'<circle cx="{x+40}" cy="125" r="26" fill="{GOLD}"/>'+t(x+40,135,n,30,INK,'middle',800)+t(x+120,200,a,23,INK,'middle',700)
    for k,l in enumerate(c.split('\n')): b+=t(x+120,250+k*30,l,20,MUT,'middle')
    if i<3: b+=arrow(x+245,230,x+265,230)
b+=t(30,425,'Câu đầu tiên mẫu:',22,INK,'start',700)+t(30,455,'"Rig nhân vật Windy trong Frolvy. Dừng ở bước đặt xương, chụp 3 góc gửi mình duyệt."',21,INK,'start',600)
w('d_start.svg',b,1130,480)
# 10 Lưới đạt / chưa đạt (sơ đồ)
b=t(20,38,'Lưới quanh một khớp (ví dụ khuỷu tay): đạt và chưa đạt',24,MUT)
def mesh(x0,ok):
    s=box(x0,70,430,330,fill='#fff',st=(GOOD if ok else BAD))
    if ok:
        for i in range(6): s+=f'<line x1="{x0+30}" y1="{140+i*36}" x2="{x0+400}" y2="{140+i*36}" stroke="#8793A8" stroke-width="3"/>'
        for j in range(8): s+=f'<line x1="{x0+30+j*53}" y1="140" x2="{x0+30+j*53}" y2="320" stroke="#8793A8" stroke-width="3"/>'
        s+=t(x0+215,100,'ĐẠT',26,GOOD,'middle',800)+t(x0+215,375,'nhiều vòng ngang quanh khớp, ô vuông đều',20,INK,'middle')
    else:
        for (a,b2,c,d) in [(30,140,400,140),(30,320,400,320),(30,140,400,320),(30,320,400,140),(215,140,215,320),(30,230,400,230),(30,140,30,320),(400,140,400,320)]:
            s+=f'<line x1="{x0+a}" y1="{b2}" x2="{x0+c}" y2="{d}" stroke="#8793A8" stroke-width="3"/>'
        s+=t(x0+215,100,'CHƯA ĐẠT',26,BAD,'middle',800)+t(x0+215,375,'ít vòng, nhiều tam giác lộn xộn',20,INK,'middle')
    return s
b+=mesh(30,True)+mesh(500,False)
b+=t(30,440,'Lưới ít vòng quanh khớp thì chỗ gập sẽ bị góc cạnh hoặc móp, skin kiểu gì cũng xấu.',22,INK,'start',600)
w('d_meshokbad.svg',b,960,470)
# 11 Hai loại file
b=t(20,38,'Hai loại file khi xuất cho game',24,MUT)
b+=box(30,70,400,230,fill='#fff',st=GOLD)+t(230,115,'File nhân vật (Base)',26,INK,'middle',800)+t(230,165,'xương + vỏ',24,INK,'middle',600)+t(230,205,'dùng một lần cho mỗi nhân vật',20,MUT,'middle')+t(230,250,'không có chuyển động',20,MUT,'middle')
b+=box(480,70,400,230,fill='#fff',st=BLUE)+t(680,115,'File chuyển động (anim)',26,INK,'middle',800)+t(680,165,'chỉ xương + chuyển động',24,INK,'middle',600)+t(680,205,'mỗi chuyển động một file',20,MUT,'middle')+t(680,250,'không có vỏ',20,MUT,'middle')
b+=arrow(230,305,450,360,INK)+arrow(680,305,520,360,INK)+box(300,360,300,70,fill='#E6F2EC',st=GOOD)+t(450,404,'Unity (game)',26,INK,'middle',800)
b+=t(30,470,'Chỉ xuất file khi bạn nói "chốt". Vòng sửa và góp ý thì không xuất.',22,BAD,'start',700)
w('d_files.svg',b,920,500)
