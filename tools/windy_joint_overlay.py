"""Vẽ joint thật của nhân vật Windy (file fit .fvfit của Frolvy) chồng lên mesh (mesh_cm.json), nhìn trước + nhìn bên.
Dùng làm hình minh hoạ cho slide Rigging 3D (không cần Frolvy). Chỉ dùng joint thân (chuỗi áo choàng / khăn chưa vẽ đúng được).

    python3 -I tools/windy_joint_overlay.py out.png [--fit Hero_Windy.fvfit] [--mesh work/rig_lab/chars/windy/mesh_cm.json]

Điều chỉnh minh hoạ do người dùng yêu cầu 2026-11-25: Chest hạ thấp 4 cm; HeadEnd về đỉnh đầu (đỉnh mesh y=185 cm); Scapula + Shoulder dịch ra ngoài 6 cm (dịch 2 lần: 3 rồi thêm 3).
Đơn vị cm, nhân vật nhìn +Z, bên phải nhân vật nằm bên trái ảnh.
"""
import json, sys, math, argparse
from PIL import Image, ImageDraw, ImageFont
ap=argparse.ArgumentParser(); ap.add_argument('out'); 
ap.add_argument('--fit',default='/home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Hero_Windy/Frolvy/Hero_Windy.fvfit')
ap.add_argument('--mesh',default='work/rig_lab/chars/windy/mesh_cm.json')
ap.add_argument('--scapula-out',type=float,default=6.0); ap.add_argument('--shoulder-out',type=float,default=6.0)
ap.add_argument('--chest-drop',type=float,default=4.0); ap.add_argument('--head-top',type=float,default=185.0)
A=ap.parse_args(); FIT=A.fit; MESH=A.mesh
f=json.load(open(FIT))
J=f['joints']
def mm(a,b): return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def rx(d):
    c,s=math.cos(math.radians(d)),math.sin(math.radians(d)); return [[1,0,0],[0,c,-s],[0,s,c]]
def ry(d):
    c,s=math.cos(math.radians(d)),math.sin(math.radians(d)); return [[c,0,s],[0,1,0],[-s,0,c]]
def rz(d):
    c,s=math.cos(math.radians(d)),math.sin(math.radians(d)); return [[c,-s,0],[s,c,0],[0,0,1]]
def quat(q):
    x,y,z,w=q
    return [[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
def mv(M,v): return [sum(M[i][k]*v[k] for k in range(3)) for i in range(3)]
P=[None]*len(J); R=[None]*len(J)
for i,j in enumerate(J):
    ox,oy,oz=j['orient']; JO=mm(rz(oz),mm(ry(oy),rx(ox)))
    Rr=quat(j['rotate']); loc=mm(JO,Rr) if False else mm(Rr,JO)   # world = parent * T * JO * R ; Maya: JO then R -> M=JO*R? see below
    loc=mm(JO,Rr)
    p=j['parent']; t=j['translate']
    if p<0: P[i]=list(t); R[i]=loc
    else:
        d=mv(R[p],t); P[i]=[P[p][k]+d[k] for k in range(3)]; R[i]=mm(R[p],loc)
M=json.load(open(MESH))
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
FONTS=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
def tris(o):
    v=o['verts']; V=[(v[i],v[i+1],v[i+2]) for i in range(0,len(v),3)]
    t=o['tris']; return V,[(t[i],t[i+1],t[i+2]) for i in range(0,len(t),3)]
def view(kind,size=(900,1000),scale=4.9,box=None,joints=None,bones=True,label=True,names=None,hl=None,meshcol=(215,220,228),cx=None,cy=None,objs=(0,1)):
    W,H=size
    im=Image.new('RGB',size,(246,243,238)); d=ImageDraw.Draw(im,'RGBA')
    # axes: front: u=-x? viewer sees character right (-x) on left: u=x. v=y
    def pr(p):
        x,y,z=p
        if kind=='front': u,dep=x,-z      # nhìn từ +z, vật gần = z lớn
        elif kind=='side': u,dep=-z,-x    # nhìn từ phải nhân vật (-x): mặt (+z) hướng sang trái? chọn mặt nhìn sang phải
        elif kind=='top': u,dep=x,-y
        if kind=='side': u=z
        v=y if kind!='top' else -z
        return (cx_+u*scale, cy_-v*scale)
    cx_=W/2 if cx is None else cx; cy_=H-60 if cy is None else cy
    for oi in objs:
        V,T=tris(M[oi])
        def depth(t):
            a=[V[i] for i in t]
            if kind=='front': return sum(p[2] for p in a)/3
            if kind=='side': return -sum(p[0] for p in a)/3
            return sum(p[1] for p in a)/3
        for t in sorted(T,key=depth):
            a=[V[i] for i in t]; pts=[pr(p) for p in a]
            # normal shading
            ux,uy,uz=[a[1][k]-a[0][k] for k in range(3)]; vx,vy,vz=[a[2][k]-a[0][k] for k in range(3)]
            n=(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx); l=math.sqrt(sum(c*c for c in n)) or 1
            n=[c/l for c in n]
            lit=0.55+0.45*abs({'front':n[2],'side':n[0],'top':n[1]}[kind])
            c=tuple(int(x*lit) for x in meshcol) if oi==0 else (int(190*lit),int(165*lit),int(120*lit))
            d.polygon(pts,fill=c+(235,))
    idx=joints if joints is not None else range(len(J))
    S=set(idx)
    if bones:
        for i in idx:
            p=J[i]['parent']
            if p>=0 and p in S: d.line([pr(P[p]),pr(P[i])],fill=(30,40,70,255),width=4)
    for i in idx:
        x,y=pr(P[i]); r=9 if (hl and i in hl) else 7
        col=(194,73,46,255) if (hl and i in hl) else (240,177,59,255)
        d.ellipse([x-r,y-r,x+r,y+r],fill=col,outline=(30,40,70,255),width=2)
        if label and names and i in names:
            dx,dy={7:(14,8),12:(-40,14)}.get(i,(12,-12)); d.text((x+dx,y+dy),names[i],fill=(30,40,70),font=FONTS)
    return im

# --- điều chỉnh minh hoạ
NAMES={J[i]['name']:i for i in range(len(J))}
P[NAMES['Chest']][1]-=A.chest_drop
P[NAMES['HeadEnd']][1]=A.head_top
for n,o in (('Scapula',A.scapula_out),('Shoulder',A.shoulder_out)):   # dịch ra ngoài (bên phải nhân vật = -x)
    P[NAMES[n]][0]-=o
main=[0,1,2,3,4,5,7,9,10,12,14,15,16,18,24,27,28,30,31,33,34,21,22,20]
a=view('front',size=(900,1000),joints=main,names={0:'Root',3:'Chest',5:'Neck',10:'Head',16:'HeadEnd',7:'Scapula',12:'Shoulder',18:'Elbow',24:'Wrist',2:'Hip',4:'Knee',9:'Ankle',14:'Toes'},scale=4.6)
b=view('side',size=(900,1000),joints=main,names={0:'Root',3:'Chest',5:'Neck',10:'Head',16:'HeadEnd',4:'Knee',9:'Ankle',14:'Toes',15:'Heel'},scale=4.6)
S=Image.new('RGB',(1800,1000)); S.paste(a,(0,0)); S.paste(b,(900,0)); S.save(A.out)
