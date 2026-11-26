"""Bộ hình Windy cho slide Rigging 3D (2026-11-25): joint thật từ file fit .fvfit của Frolvy chồng lên mesh, không cần Frolvy.

    python3 -I tools/windy_slide_images.py <thư_mục_ra> [--fit …fvfit] [--mesh work/rig_lab/chars/windy/mesh_cm.json]

Ra: w_mesh, w_wire, w_wire_zoom, w_joints_front/side/top, w_leg, w_spine, w_arm, w_beforeafter (.png).
Chỉnh minh hoạ theo yêu cầu của user: Chest hạ 4 cm, HeadEnd về đỉnh đầu (185 cm), Scapula + Shoulder ra ngoài 6 cm.
Chuỗi áo choàng (Cape / Clo) chưa vẽ vì vị trí không đọc đúng được từ file. Đơn vị cm; nhân vật nhìn +Z; bên phải nhân vật nằm bên trái ảnh.
"""
import json, sys, math, os, argparse
from PIL import Image, ImageDraw, ImageFont
ap=argparse.ArgumentParser(); ap.add_argument('out')
ap.add_argument('--fit',default='/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Hero_Windy/Frolvy/Hero_Windy.fvfit')
ap.add_argument('--mesh',default='work/rig_lab/chars/windy/mesh_cm.json')
A=ap.parse_args(); os.makedirs(A.out,exist_ok=True)
J=json.load(open(A.fit))['joints']; M=json.load(open(A.mesh))
def mm(a,b): return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def rx(d): c,s=math.cos(math.radians(d)),math.sin(math.radians(d)); return [[1,0,0],[0,c,-s],[0,s,c]]
def ry(d): c,s=math.cos(math.radians(d)),math.sin(math.radians(d)); return [[c,0,s],[0,1,0],[-s,0,c]]
def rz(d): c,s=math.cos(math.radians(d)),math.sin(math.radians(d)); return [[c,-s,0],[s,c,0],[0,0,1]]
def quat(q):
    x,y,z,w=q
    return [[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
def mv(Mx,v): return [sum(Mx[i][k]*v[k] for k in range(3)) for i in range(3)]
P0=[None]*len(J); R=[None]*len(J)
for i,j in enumerate(J):
    ox,oy,oz=j['orient']; loc=mm(rz(oz) if False else mm(rz(oz),mm(ry(oy),rx(ox))),quat(j['rotate']))
    p=j['parent']; t=j['translate']
    if p<0: P0[i]=list(t); R[i]=loc
    else:
        dd=mv(R[p],t); P0[i]=[P0[p][k]+dd[k] for k in range(3)]; R[i]=mm(R[p],loc)
N={J[i]['name']:i for i in range(len(J))}
P1=[list(p) for p in P0]
P1[N['Chest']][1]-=4.0; P1[N['HeadEnd']][1]=185.0
P1[N['Scapula']][0]-=6.0; P1[N['Shoulder']][0]-=6.0
FB=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
FS=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',30)
INK=(22,34,58); GOLD=(240,177,59); RED=(194,73,46); GRN=(46,125,91)
def tr(o):
    v=o['verts']; V=[(v[i],v[i+1],v[i+2]) for i in range(0,len(v),3)]; t=o['tris']
    return V,[(t[i],t[i+1],t[i+2]) for i in range(0,len(t),3)]
VNMAP=[('HeadEnd','Đỉnh đầu'),('Spine1','Cột sống'),('Shoulder','Vai'),('Scapula','Bả vai'),('Elbow','Khuỷu'),('Wrist','Cổ tay'),('Ankle','Cổ chân'),('Toes','Ngón chân'),('Heel','Gót'),('Knee','Gối'),('Chest','Ngực'),('Neck','Cổ'),('Head','Đầu'),('Hip','Hông'),('Root','Gốc')]
def tvn(t):
    for a,b in VNMAP: t=t.replace(a,b)
    return t
def vn(x): return f'{x:.1f}'.replace('.',',')
def view(kind,size,scale,center,joints=None,names=None,P=P1,hl=(),wire=True,objs=(0,1),labeloff=None,fill=True,lw=None):
    W,H=size; im=Image.new('RGB',size,(246,243,238)); d=ImageDraw.Draw(im,'RGBA')
    u0,v0=center
    def pr(p):
        x,y,z=p
        u={'front':x,'side':z,'top':x}[kind]; v={'front':y,'side':y,'top':-z}[kind]
        return (W/2+(u-u0)*scale, H/2-(v-v0)*scale)
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
                d.line(pts+[pts[0]],fill=oc,width=(lw or ((2 if scale>=4 else 1) if oi==0 else 1)))
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
MAIN=[0,1,2,3,4,5,7,9,10,12,14,15,16,18,24,27,28,30,31,33,34,20,21,22]
# 1. mesh + kích thước
im,pr,d=view('front',(900,1000),4.2,(0,98),objs=(0,1),wire=False)
dim(d,pr((104,0,0)),pr((104,185,0)),'cao 185 cm',off=(-250,-14))
dim(d,pr((-87.8,-9,0)),pr((87.8,-9,0)),'sải tay 175,6 cm',off=(-130,-56))
vlabel(d,pr((-100,127,0)),'gậy (staff): mảnh riêng',col=(150,100,30),dx=0,dy=-90)
vlabel(d,pr((-38,34,0)),'thân + đầu + áo choàng',dx=0,dy=0)
vlabel(d,pr((-38,34,0)),'(mảnh body3)',dx=0,dy=40)
im.save(f'{A.out}/w_mesh.png')
# 2. lưới
im,_,d=view('front',(900,1000),4.6,(0,98),wire=True,objs=(0,)); im.save(f'{A.out}/w_wire.png')
im,_,d=view('front',(900,700),12,(-28,112),wire=True,objs=(0,)); im.save(f'{A.out}/w_wire_zoom.png')
# 3. joint ba góc
nm={1:'Spine1',0:'Root',2:'Hip',4:'Knee',9:'Ankle',14:'Toes',3:'Chest',5:'Neck',10:'Head',16:'HeadEnd',7:'Scapula',12:'Shoulder',18:'Elbow',24:'Wrist'}
lo={7:(34,56),12:(-110,70),24:(-60,-110),18:(-40,-70),2:(-90,-10),4:(-96,-10),9:(-96,-10),1:(16,-12)}
view('front',(900,1000),4.6,(0,98),MAIN,nm,labeloff=lo,hl=())[0].save(f'{A.out}/w_joints_front.png')
view('side',(900,1000),4.6,(0,98),MAIN,{k:v for k,v in nm.items() if k in(0,4,9,14,3,5,10,16,15)}|{15:'Heel'},labeloff={0:(14,-10)},objs=(0,1))[0].save(f'{A.out}/w_joints_side.png')
view('top',(900,900),4.2,(0,40),[0,3,5,10,7,12,18,24],{0:'Root',12:'Shoulder',18:'Elbow',24:'Wrist',10:'Head'},objs=(0,),labeloff={0:(14,-10),12:(-100,-50),18:(-60,-50),24:(-60,-50),10:(14,-40)})[0].save(f'{A.out}/w_joints_top.png')
# 4. chân
nl={2:f'Hip · cao {vn(P1[2][1])} cm',4:f'Knee · cao {vn(P1[4][1])} cm',9:f'Ankle · cao {vn(P1[9][1])} cm',14:f'Toes · {vn(P1[14][1])} cm',15:'Heel'}
a=view('front',(780,820),9.5,(-9,36),[2,4,9,14,15,20,21,22,0],nl,objs=(0,),labeloff={2:(16,-34),4:(16,-30),9:(16,-34),14:(16,6),15:(-70,6),0:(16,-14)})[0]
b=view('side',(780,820),9.5,(0,36),[2,4,9,14,15,20,0],nl,objs=(0,),labeloff={2:(16,-34),4:(16,-30),9:(16,-34),14:(16,6),15:(-70,6),0:(16,-14)})[0]
pair(a,b).save(f'{A.out}/w_leg.png')
# 5. thân + đầu
ns={0:f'Root · {vn(P1[0][1])}',1:f'Spine1 · {vn(P1[1][1])}',3:f'Chest · {vn(P1[3][1])}',5:f'Neck · {vn(P1[5][1])}',10:f'Head · {vn(P1[10][1])}',16:f'HeadEnd · {vn(P1[16][1])}'}
a=view('front',(780,900),6.2,(0,128),[0,1,3,5,10,16,7,12,2],ns,objs=(0,),labeloff={0:(16,-12),1:(16,-12),3:(16,-12),5:(16,-12),10:(16,-12),16:(16,-12),7:(10,18),12:(-40,18),2:(-60,-30)})[0]
b=view('side',(780,900),6.2,(0,128),[0,1,3,5,10,16],ns,objs=(0,),labeloff={k:(16,-12) for k in ns})[0]
pair(a,b).save(f'{A.out}/w_spine.png')
# 6. tay
na={7:'Scapula',12:'Shoulder',18:'Elbow',24:'Wrist',28:'Middle finger',27:'Thumb'}
im,pr,d=view('front',(1500,560),9.2,(-48,114),[5,3,7,12,18,24,27,28,30,31,33,34],na,objs=(0,1),labeloff={7:(36,58),12:(-90,60),18:(-30,-60),24:(10,-92),28:(-170,-64),27:(-50,26)})
dim(d,pr((P1[7][0],104,0)),pr((P1[12][0],104,0)),f'{vn(abs(P1[12][0]-P1[7][0]))} cm',off=(-30,6)); im.save(f'{A.out}/w_arm.png')
# 7. trước / sau chỉnh
def ba(P,hl,title):
    im,pr,d=view('front',(780,900),6.4,(-6,138),[0,1,3,5,10,16,7,12,2],({3:'Chest',16:'HeadEnd',5:'Neck',10:'Head'} if hl else {3:'Chest',16:'HeadEnd',7:'Scapula',12:'Shoulder',5:'Neck',10:'Head'}),P=P,objs=(0,),hl=hl,labeloff={3:(24,6),16:(16,-12),7:(40,40),12:(-150,46),5:(16,-12),10:(16,-12)})
    if hl:
        for i in hl:
            a=pr(P0[i]); b2=pr(P1[i]); d.ellipse([a[0]-12,a[1]-12,a[0]+12,a[1]+12],outline=RED+(255,),width=3)
            d.line([a,b2],fill=RED+(255,),width=4)
            import math as _m; ang=_m.atan2(b2[1]-a[1],b2[0]-a[0]); d.polygon([b2,(b2[0]-16*_m.cos(ang-0.45),b2[1]-16*_m.sin(ang-0.45)),(b2[0]-16*_m.cos(ang+0.45),b2[1]-16*_m.sin(ang+0.45))],fill=RED+(255,))
    if hl:
        for i,txt in {3:'Chest hạ 4 cm',16:'Head End về đỉnh đầu',7:'Scapula ra 6 cm',12:'Shoulder ra 6 cm'}.items():
            pt=pr(P1[i]); off={3:(30,40),16:(-330,-30),7:(26,-120),12:(-260,-66)}[i]
            vlabel(d,pt,txt,col=RED,dx=off[0],dy=off[1])
    vlabel(d,(20,20),title,col=RED if hl==() else GRN,dx=0,dy=0); return im
pair(ba(P0,(),'CHƯA ĐẠT: joint như trong file'),ba(P1,(3,16,7,12),'ĐẠT: đã chỉnh (vòng đỏ = chỗ cũ)')).save(f'{A.out}/w_beforeafter.png')
print('ok',sorted(os.listdir(A.out)))
