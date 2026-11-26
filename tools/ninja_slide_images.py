"""Bộ hình Ninja cho slide Rigging 3D (2026-11-26): joint thật (landmarks do người đặt trong Studio Rig) chồng lên mesh Ninja,
vẽ lưới dạng QUAD (ẩn đường chéo của tam giác ghép thành quad). Không cần Frolvy.

    python3 -I tools/ninja_slide_images.py <thư_mục_ra>

Ra: n_mesh, n_wire, n_wire_zoom, n_joints_front/side/top, n_leg, n_spine, n_arm, n_chain, n_beforeafter (.png)
Chỉ vẽ joint bên phải nhân vật + giữa. Mọi hình dùng vị trí ĐÃ CHỈNH như Windy (user 2026-11-26): Root hạ 3, Neck hạ 7, Head hạ 7, Hip hạ 3, Knee hạ 3, Spine hạ 5, Chest hạ 8 cm; Scapula hạ 3 và ra ngoài 6 cm; Shoulder ra ngoài 6 cm; Head End ở đỉnh đầu (185). (Windy: Chest 4, Scapula/Shoulder ra 6.) n_beforeafter: trái = landmarks gốc, phải = đã chỉnh.
Đơn vị cm; nhân vật nhìn +Z; bên phải nhân vật nằm bên trái ảnh.
"""
import json, sys, math, os
from PIL import Image, ImageDraw, ImageFont
OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
MESHP='work/rig_lab/chars/ninja/mesh_cm.json'; CHP='work/rig_lab/chars/ninja.json'
M=json.load(open(MESHP)); CH=json.load(open(CHP)); LM=CH['landmarks']
EX={e['name']:e['pos'] for e in CH['cfg']['extra']}
# ---- joint list (bên phải + giữa) với cha
order=[('Root','Root_M',-1),('Spine1','Spine1_M','Root'),('Chest','Chest_M','Spine1'),('Neck','Neck_M','Chest'),('Head','Head_M','Neck'),('HeadEnd','HeadEnd_M','Head'),
 ('Hip','Hip_R','Root'),('Knee','Knee_R','Hip'),('Ankle','Ankle_R','Knee'),('Toes','Toes_R','Ankle'),('ToesEnd','ToesEnd_R','Toes'),
 ('Scapula','Scapula_R','Chest'),('Shoulder','Shoulder_R','Scapula'),('Elbow','Elbow_R','Shoulder'),('Wrist','Wrist_R','Elbow'),('HandTip','HandTip_R','Wrist'),
 ('Middle1','MiddleFinger1_R','Wrist'),('Middle2','MiddleFinger2_R','Middle1'),('Thumb1','ThumbFinger1_R','Wrist'),('Thumb2','ThumbFinger2_R','Thumb1'),
 ('Scarf1','Scarf1_R','Chest'),('Scarf2','Scarf2_R','Scarf1'),('Scarf3','Scarf3_R','Scarf2'),('Scarf4','Scarf4_R','Scarf3'),('ScarfEnd','ScarfEnd_R','Scarf4')]
idx={n:i for i,(n,_,_) in enumerate(order)}
J=[{'name':n,'parent':(idx[p] if p!=-1 else -1)} for n,_,p in order]
P0=[list(LM.get(k) or EX[k]) for _,k,_ in order]
N=idx
import copy
Porig=copy.deepcopy(P0)   # landmarks gốc (chưa chỉnh)
P0[N['Root']][1]-=3.0; P0[N['Neck']][1]-=7.0; P0[N['Head']][1]-=7.0; P0[N['Hip']][1]-=3.0; P0[N['Knee']][1]-=3.0; P0[N['Spine1']][1]-=5.0; P0[N['Chest']][1]-=8.0; P0[N['Scapula']][1]-=3.0; P0[N['Scapula']][0]-=6.0; P0[N['Shoulder']][0]-=6.0; P0[N['HeadEnd']][1]=185.0
# ---- quad hoá: ghép tam giác thành quad, đường chéo bị ẩn
body=M[0]; v=body['verts']; V0=[(v[i],v[i+1],v[i+2]) for i in range(0,len(v),3)]; tt=body['tris']; T0=[tuple(tt[i:i+3]) for i in range(0,len(tt),3)]
def sub(a,b): return [a[k]-b[k] for k in range(3)]
def dot(a,b): return sum(a[k]*b[k] for k in range(3))
def nrm(a): l=math.sqrt(dot(a,a)) or 1; return [x/l for x in a]
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def cosang(p,q,r): return abs(dot(nrm(sub(q,p)),nrm(sub(r,p))))
em={}
for k,t in enumerate(T0):
    for a,b in ((t[0],t[1]),(t[1],t[2]),(t[2],t[0])): em.setdefault(tuple(sorted((a,b))),[]).append(k)
cand=[]
for (u,w),ts in em.items():
    if len(ts)!=2: continue
    a=[x for x in T0[ts[0]] if x not in (u,w)]; b=[x for x in T0[ts[1]] if x not in (u,w)]
    if len(a)!=1 or len(b)!=1: continue
    a,b=a[0],b[0]; q=[V0[a],V0[u],V0[b],V0[w]]
    n1=nrm(cross(sub(V0[w],V0[u]),sub(V0[a],V0[u]))); n2=nrm(cross(sub(V0[b],V0[u]),sub(V0[w],V0[u])))
    sc=max(cosang(q[i],q[(i+1)%4],q[(i-1)%4]) for i in range(4))+(1-abs(dot(n1,n2)))*2
    cand.append((sc,(u,w),ts))
cand.sort(key=lambda x:x[0]); used=set(); DIAG=set()
for sc,e,ts in cand:
    if sc>0.55: break
    if ts[0] in used or ts[1] in used: continue
    used.update(ts); DIAG.add(e)
print('quad ghép:',len(DIAG),'/',len(T0)//2,'tam giác lẻ:',len(T0)-2*len(DIAG))
FB=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
FS=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',30)
INK=(22,34,58); GOLD=(240,177,59); RED=(194,73,46); GRN=(46,125,91)
def tr(o):
    v=o['verts']; V=[(v[i],v[i+1],v[i+2]) for i in range(0,len(v),3)]; t=o['tris']
    return V,[(t[i],t[i+1],t[i+2]) for i in range(0,len(t),3)]

def vn(x): return f'{x:.1f}'.replace('.',',')
def tvn(t): return t
def view(kind,size,scale,center,joints=None,names=None,P=None,hl=(),wire=True,objs=(0,),labeloff=None,fill=True,lw=None):
    P=P or P0
    W,H=size; im=Image.new('RGB',size,(246,243,238)); d=ImageDraw.Draw(im,'RGBA')
    u0,v0=center
    def pr(p):
        x,y,z=p
        u={'front':x,'side':z,'top':x}[kind]; v_={'front':y,'side':y,'top':-z}[kind]
        return (W/2+(u-u0)*scale, H/2-(v_-v0)*scale)
    for oi in objs:
        V,T=tr(M[oi])
        dep=lambda t:{'front':sum(V[i][2] for i in t)/3,'side':-sum(V[i][0] for i in t)/3,'top':sum(V[i][1] for i in t)/3}[kind]
        for t in sorted(T,key=dep):
            a=[V[i] for i in t]; pts=[pr(p) for p in a]
            ux,uy,uz=[a[1][k]-a[0][k] for k in range(3)]; vx,vy,vz=[a[2][k]-a[0][k] for k in range(3)]
            n=(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx); l=math.sqrt(sum(c*c for c in n)) or 1
            lit=0.55+0.45*abs({'front':n[2],'side':n[0],'top':n[1]}[kind]/l)
            base=(215,220,228) if oi==0 else (190,165,120)
            c=tuple(int(x*lit) for x in base)
            if wire:
                fc=(250,251,253,255) if oi==0 else (247,242,232,255); oc=(40,58,105,255) if oi==0 else (214,196,162,255)
                d.polygon(pts,fill=fc if fill else None)
                for pa,pb in ((0,1),(1,2),(2,0)):
                    if oi==0 and tuple(sorted((t[pa],t[pb]))) in DIAG: continue
                    d.line([pts[pa],pts[pb]],fill=oc,width=(lw or ((2 if scale>=4 else 1) if oi==0 else 1)))
            else: d.polygon(pts,fill=c+(235,))
    S=set(joints or [])
    for i in (joints or []):
        p=J[i]['parent']
        if p>=0 and p in S: d.line([pr(P[p]),pr(P[i])],fill=INK+(255,),width=4)
    for i in (joints or []):
        x,y=pr(P[i]); r=10 if i in hl else 7
        d.ellipse([x-r,y-r,x+r,y+r],fill=(RED if i in hl else GOLD)+(255,),outline=INK+(255,),width=2)
        if names and i in names:
            dx,dy=(labeloff or {}).get(i,(14,-12))
            txt=names[i]; w=d.textlength(txt,font=FS)
            if abs(dx)>22 or abs(dy)>22: d.line([(x,y),(x+dx+(w if dx<0 else 0),y+dy+17)],fill=INK+(255,),width=2)
            d.rectangle([x+dx-3,y+dy-2,x+dx+w+3,y+dy+38],fill=(246,243,238,215)); d.text((x+dx,y+dy),txt,fill=INK,font=FS)
    return im,pr,d
def dim(d,a,b,txt,off=(0,0),col=INK):
    d.line([a,b],fill=col+(255,),width=3)
    for p in (a,b):
        if abs(a[0]-b[0])<abs(a[1]-b[1]): d.line([(p[0]-10,p[1]),(p[0]+10,p[1])],fill=col+(255,),width=3)
        else: d.line([(p[0],p[1]-10),(p[0],p[1]+10)],fill=col+(255,),width=3)
    mx,my=(a[0]+b[0])/2+off[0],(a[1]+b[1])/2+off[1]
    w=d.textlength(txt,font=FB); d.rectangle([mx-4,my-3,mx+w+4,my+38],fill=(246,243,238,230)); d.text((mx,my),txt,fill=col,font=FB)
def pair(a,b,gap=20):
    S=Image.new('RGB',(a.width+b.width+gap,max(a.height,b.height)),(246,243,238)); S.paste(a,(0,0)); S.paste(b,(a.width+gap,0)); return S
def vlabel(d,pt,txt,col=INK,dx=14,dy=-12):
    w=d.textlength(txt,font=FB); d.rectangle([pt[0]+dx-3,pt[1]+dy-2,pt[0]+dx+w+3,pt[1]+dy+38],fill=(246,243,238,230)); d.text((pt[0]+dx,pt[1]+dy),txt,fill=col,font=FB)
MAIN=[N[k] for k in ('Root','Spine1','Chest','Neck','Head','HeadEnd','Hip','Knee','Ankle','Toes','ToesEnd','Scapula','Shoulder','Elbow','Wrist','HandTip','Middle1','Middle2','Thumb1','Thumb2')]
NM={'Root':'Root','Spine1':'Spine','Chest':'Chest','Neck':'Neck','Head':'Head','HeadEnd':'Head End','Hip':'Hip','Knee':'Knee','Ankle':'Ankle','Toes':'Toes','Scapula':'Scapula','Shoulder':'Shoulder','Elbow':'Elbow','Wrist':'Wrist'}
def names(keys,vals=False):
    out={}
    for k in keys:
        t=NM[k]
        if vals: t=f'{t} · {vn(P0[N[k]][1])}'
        out[N[k]]=t
    return out
# 1. mesh + kích thước
im,pr,d=view('front',(900,1000),4.2,(0,98),wire=False)
dim(d,pr((104,0,0)),pr((104,185,0)),'cao 185 cm',off=(-250,-14))
dim(d,pr((-87.8,-9,0)),pr((87.8,-9,0)),'sải tay 175,6 cm',off=(-130,-56))
vlabel(d,pr((-60,40,0)),'1 mảnh body (có khăn)',dx=0,dy=0)
im.save(f'{OUT}/n_mesh.png')
# 2. lưới quad
view('front',(900,1000),4.6,(0,98))[0].save(f'{OUT}/n_wire.png')
view('front',(900,700),12,(-26,116))[0].save(f'{OUT}/n_wire_zoom.png')
# 3. joint ba góc
lo={N['Scapula']:(34,56),N['Shoulder']:(-110,70),N['Wrist']:(-60,-110),N['Elbow']:(-40,-70),N['Hip']:(-90,-10),N['Knee']:(-96,-10),N['Ankle']:(-96,-10),N['Spine1']:(16,-12)}
view('front',(900,1000),4.6,(0,98),MAIN,names(NM.keys()),labeloff=lo)[0].save(f'{OUT}/n_joints_front.png')
view('side',(900,1000),4.6,(-60,98),MAIN,names(['Root','Chest','Neck','Head','HeadEnd','Hip','Knee','Ankle','Toes']),labeloff={N['Root']:(14,-10)})[0].save(f'{OUT}/n_joints_side.png')
view('top',(900,900),3.2,(0,-60),[N[k] for k in ('Root','Chest','Neck','Head','Scapula','Shoulder','Elbow','Wrist')],names(['Root','Head','Shoulder','Elbow','Wrist']),labeloff={N['Root']:(14,-10),N['Shoulder']:(-100,-50),N['Elbow']:(-60,-50),N['Wrist']:(-60,-50),N['Head']:(14,-40)})[0].save(f'{OUT}/n_joints_top.png')
# 4. chân
lg=[N[k] for k in ('Root','Hip','Knee','Ankle','Toes','ToesEnd')]
nl={N['Hip']:f'Hip · cao {vn(P0[N["Hip"]][1])} cm',N['Knee']:f'Knee · cao {vn(P0[N["Knee"]][1])} cm',N['Ankle']:f'Ankle · cao {vn(P0[N["Ankle"]][1])} cm',N['Toes']:f'Toes · {vn(P0[N["Toes"]][1])} cm'}
lo2={N['Hip']:(16,-34),N['Knee']:(16,-30),N['Ankle']:(16,-34),N['Toes']:(16,6),N['Root']:(16,-14)}
a=view('front',(780,820),9.5,(-9,40),lg,nl,labeloff=lo2)[0]
b=view('side',(780,820),9.5,(0,40),lg,nl,labeloff=lo2)[0]
pair(a,b).save(f'{OUT}/n_leg.png')
# 5. thân + đầu
sp=[N[k] for k in ('Root','Spine1','Chest','Neck','Head','HeadEnd','Scapula','Shoulder','Hip')]
ns={N['Root']:f'Root · {vn(P0[N["Root"]][1])}',N['Spine1']:f'Spine · {vn(P0[N["Spine1"]][1])}',N['Chest']:f'Chest · {vn(P0[N["Chest"]][1])}',N['Neck']:f'Neck · {vn(P0[N["Neck"]][1])}',N['Head']:f'Head · {vn(P0[N["Head"]][1])}',N['HeadEnd']:f'Head End · {vn(P0[N["HeadEnd"]][1])}'}
lo3={k:(16,-12) for k in ns}
a=view('front',(780,900),6.2,(0,128),sp,ns,labeloff=lo3)[0]
b=view('side',(780,900),6.2,(0,128),[N[k] for k in ('Root','Spine1','Chest','Neck','Head','HeadEnd')],ns,labeloff=lo3)[0]
pair(a,b).save(f'{OUT}/n_spine.png')
# 6. tay
na={N['Scapula']:'Scapula',N['Shoulder']:'Shoulder',N['Elbow']:'Elbow',N['Wrist']:'Wrist',N['Middle1']:'Middle finger',N['Thumb1']:'Thumb'}
arm=[N[k] for k in ('Neck','Chest','Scapula','Shoulder','Elbow','Wrist','HandTip','Middle1','Middle2','Thumb1','Thumb2')]
im,pr,d=view('front',(1500,560),9.2,(-48,116),arm,na,labeloff={N['Scapula']:(36,58),N['Shoulder']:(-90,60),N['Elbow']:(-30,-60),N['Wrist']:(10,-92),N['Middle1']:(-170,-64),N['Thumb1']:(-50,26)})
dim(d,pr((P0[N['Scapula']][0],104,0)),pr((P0[N['Shoulder']][0],104,0)),f'{vn(abs(P0[N["Shoulder"]][0]-P0[N["Scapula"]][0]))} cm',off=(-30,6)); im.save(f'{OUT}/n_arm.png')
# 7. chuỗi khăn (joint chain)
ch=[N[k] for k in ('Chest','Neck','Scarf1','Scarf2','Scarf3','Scarf4','ScarfEnd')]
view('side',(1500,620),5.2,(-62,112),ch,{N['Scarf1']:'Scarf 1',N['Scarf2']:'Scarf 2',N['Scarf3']:'Scarf 3',N['Scarf4']:'Scarf 4',N['ScarfEnd']:'Scarf End',N['Chest']:'Chest'},labeloff={N['Scarf1']:(0,-70),N['Scarf2']:(-30,-70),N['Scarf3']:(-30,-70),N['Scarf4']:(-30,-70),N['ScarfEnd']:(-30,-70),N['Chest']:(20,40)})[0].save(f'{OUT}/n_chain.png')
# 8. trước/sau: trái = GIẢ LẬP lỗi, phải = Ninja thật
Pbad=Porig
def ba(P,hl,title,col):
    j=[N[k] for k in ('Root','Spine1','Chest','Neck','Head','HeadEnd','Scapula','Shoulder','Hip')]
    nmx={N['Root']:'Root',N['Spine1']:'Spine',N['Chest']:'Chest',N['HeadEnd']:'Head End',N['Neck']:'Neck',N['Head']:'Head'}
    im,pr,d=view('front',(780,900),6.0,(-6,126),j,nmx,P=P,labeloff={N['Root']:(16,-12),N['Spine1']:(16,-12),N['Chest']:(16,-12),N['HeadEnd']:(16,-12),N['Neck']:(16,-12),N['Head']:(16,-12)})
    vlabel(d,(20,20),title,col=col,dx=0,dy=0); return im
pair(ba(Pbad,(),'CHƯA ĐẠT: joint như trong file',RED),ba(P0,(N['Root'],N['Spine1'],N['Chest'],N['Scapula'],N['Shoulder']),'ĐẠT: joint đã hạ xuống',GRN)).save(f'{OUT}/n_beforeafter.png')

# 9. control (hình minh hoạ: vòng/hộp quanh joint, xanh dương = phải, tím = trái, vàng = giữa)
def ctl_img():
    im,pr,d=view('front',(900,1060),4.4,(0,86),[],{})
    BLUE=(59,111,182); PUR=(138,95,181); YEL=(232,185,35)
    def ring(c,rx,ry,col,w=5):
        x,y=pr(c); d.ellipse([x-rx*4.6,y-ry*4.6,x+rx*4.6,y+ry*4.6],outline=col+(255,),width=w)
    def box(c,w_,h_,col,wd=5):
        x,y=pr(c); d.rectangle([x-w_*4.6/2,y-h_*4.6/2,x+w_*4.6/2,y+h_*4.6/2],outline=col+(255,),width=wd)
    def lab(c,txt,col,dx,dy):
        x,y=pr(c); vlabel(d,(x,y),txt,col=col,dx=dx,dy=dy)
    def L(k): p=P0[N[k]]; return p
    def Lm(k): p=P0[N[k]]; return [-p[0],p[1],p[2]]
    ring([0,0,0],34,8,YEL,6); lab([0,0,0],'Main (sàn)',(138,100,0),160,-20)
    ring(L('Root'),22,6,YEL,5); lab(L('Root'),'Root',(138,100,0),60,-14)
    ring(L('Chest'),19,5,YEL,5); lab(L('Chest'),'Chest',(138,100,0),58,-14)
    ring(L('Head'),16,5,YEL,5); lab(L('Head'),'Head',(138,100,0),60,-10)
    for side,fn,col in (('R',L,BLUE),('L',Lm,PUR)):
        ring(fn('Shoulder'),6,6,col,4)
        ring(fn('Elbow'),5,5,col,4)
        box(fn('Wrist'),9,9,col,5)
        box([fn('Ankle')[0],3,0],13,6,col,5)
        ring(fn('Knee'),7,7,col,4)
    lab(L('Wrist'),'Wrist (tay phải)',BLUE,-60,-70)
    lab(Lm('Wrist'),'Wrist (tay trái)',PUR,-100,-70)
    lab([L('Ankle')[0],3,0],'Ankle (phải)',BLUE,-250,-90)
    lab([-L('Ankle')[0],3,0],'Ankle (trái)',PUR,70,-90)
    vlabel(d,(20,20),'Xanh dương: phải · Tím: trái · Vàng: giữa',col=INK,dx=0,dy=0)
    im.save(f'{OUT}/n_controls.png')
ctl_img()

# 10. bản đồ ảnh hưởng skin (sơ đồ minh hoạ: mỗi điểm bám theo joint gần nhất, chỗ khớp pha màu)
def skinmap():
    # xương = đoạn từ joint tới joint con (bên phải + đối xứng sang trái)
    segs=[]  # (tên, a, b, màu)
    COL={'Root':(232,185,35),'Spine':(242,140,40),'Chest':(217,83,79),'Neck':(160,110,190),'Head':(236,120,170),
         'Shoulder':(59,111,182),'Elbow':(46,160,110),'Wrist':(138,95,181),'Hip':(59,111,182),'Knee':(46,160,110),'Ankle':(138,95,181)}
    def J(k,side=1):
        p=P0[N[k]]; return [p[0]*side,p[1],p[2]]
    def add(n,a,b,side=1): segs.append((n,J(a,side),J(b,side),COL[n]))
    add('Root','Root','Spine1'); add('Spine','Spine1','Chest'); add('Chest','Chest','Neck'); add('Neck','Neck','Head'); add('Head','Head','HeadEnd')
    for sd in (1,-1):
        add('Shoulder','Shoulder','Elbow',sd); add('Elbow','Elbow','Wrist',sd); add('Wrist','Wrist','HandTip',sd)
        add('Hip','Hip','Knee',sd); add('Knee','Knee','Ankle',sd); add('Ankle','Ankle','Toes',sd)
        # vai: bả vai nối ngực
        segs.append(('Shoulder',J('Scapula',sd),J('Shoulder',sd),COL['Shoulder']))
    def dseg(p,a,b):
        ab=[b[k]-a[k] for k in range(3)]; ap=[p[k]-a[k] for k in range(3)]
        t=max(0,min(1,sum(ap[k]*ab[k] for k in range(3))/(sum(x*x for x in ab) or 1)))
        q=[a[k]+ab[k]*t for k in range(3)]; return math.sqrt(sum((p[k]-q[k])**2 for k in range(3)))
    V,T=tr(M[0])
    cols=[]
    for p in V:
        ws=[]; 
        for n,a,b,c in segs:
            d_=dseg(p,a,b)+0.5; ws.append((1/d_**4,c))
        ws.sort(key=lambda x:-x[0]); ws=ws[:3]; tot=sum(w for w,_ in ws)
        cols.append(tuple(sum(w*c[k] for w,c in ws)/tot for k in range(3)))
    W,H=1500,1000; scale=4.6; u0,v0=0,98
    im=Image.new('RGB',(W,H),(246,243,238)); d=ImageDraw.Draw(im)
    pr=lambda p:(470+(p[0]-u0)*scale,H/2-(p[1]-v0)*scale)
    for t in sorted(T,key=lambda t:sum(V[i][2] for i in t)/3):
        c=tuple(int(sum(cols[i][k] for i in t)/3) for k in range(3))
        d.polygon([pr(V[i]) for i in t],fill=c,outline=c)
    for sd in (1,-1):
        pass
    # nhãn joint chính
    for k,txt,off in (('Chest','Chest',(40,-10)),('Shoulder','Shoulder',(-40,52)),('Elbow','Elbow',(-60,-80)),('Hip','Hip',(-130,-5)),('Knee','Knee',(-130,-5)),('Root','Root',(40,-10))):
        x,y=pr(P0[N[k]])
        d.ellipse([x-8,y-8,x+8,y+8],fill=(255,255,255),outline=INK,width=3)
        w=d.textlength(txt,font=FB); d.rectangle([x+off[0]-4,y+off[1]-3,x+off[0]+w+4,y+off[1]+38],fill=(246,243,238)); d.text((x+off[0],y+off[1]),txt,fill=INK,font=FB)
    # chú giải bên phải
    d.text((980,60),'Mỗi màu = một joint',fill=INK,font=FB)
    d.text((980,104),'điều khiển điểm đó',fill=INK,font=FB)
    items=[((232,185,35),'Root'),((242,140,40),'Spine'),((217,83,79),'Chest'),((236,120,170),'Head'),((59,111,182),'Shoulder, Hip'),((46,160,110),'Elbow, Knee'),((138,95,181),'Wrist, Ankle')]
    for i,(c,t) in enumerate(items):
        y=190+i*64; d.rectangle([980,y,1030,y+44],fill=c,outline=INK,width=2); d.text((1050,y+4),t,fill=INK,font=FB)
    d.text((980,680),'Chỗ pha màu = điểm bám',fill=INK,font=FS)
    d.text((980,722),'cả hai joint cạnh nhau.',fill=INK,font=FS)
    d.text((980,780),'Chuyển màu mượt',fill=(46,125,91),font=FB)
    d.text((980,824),'= chỗ gập đẹp.',fill=(46,125,91),font=FB)
    im.save(f'{OUT}/n_skinmap.png')
skinmap()

# 11. ví dụ lỗi control: shoulder phải to, trái bé (sơ đồ minh hoạ)
def ctl_bad():
    im,pr,d=view('front',(900,1000),4.6,(0,98),[],{})
    BLUE=(59,111,182); PUR=(138,95,181); RED_=(194,73,46)
    def ring(c,r,col,w=6):
        x,y=pr(c); d.ellipse([x-r*4.6,y-r*4.6,x+r*4.6,y+r*4.6],outline=col+(255,),width=w)
    R=P0[N['Shoulder']]; Lc=[-R[0],R[1],R[2]]
    ring(R,34,BLUE,7); ring(Lc,5,PUR,7)
    for k in ('Elbow','Wrist'):
        p_=P0[N[k]]; ring(p_,6,BLUE,4); ring([-p_[0],p_[1],p_[2]],6,PUR,4)
    for k in ('Hip','Knee'):
        p_=P0[N[k]]; ring(p_,6,BLUE,4); ring([-p_[0],p_[1],p_[2]],6,PUR,4)
    x,y=pr(R); vlabel(d,(x,y),'Shoulder phải: quá to',col=RED_,dx=-300,dy=-175)
    x,y=pr(Lc); vlabel(d,(x,y),'Shoulder trái: bé xíu',col=RED_,dx=-40,dy=-110)
    vlabel(d,(20,20),'Hai bên không giống nhau',col=INK,dx=0,dy=0)
    im.save(f'{OUT}/n_ctl_bad.png')
ctl_bad()
print('ok',sorted(os.listdir(OUT)))
