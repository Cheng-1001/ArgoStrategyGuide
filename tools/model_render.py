"""usage: python3 -I model_render.py <model.json> <texture dir> <out.png>
Tiny orthographic renderer for the official item-model JSON (item-models/m/*.json) -> RGBA icon."""
import json,sys,math
import numpy as np
from PIL import Image
def rotm(ax,deg):
    a=math.radians(deg);c,s=math.cos(a),math.sin(a)
    if ax==0:return np.array([[1,0,0],[0,c,-s],[0,s,c]])
    if ax==1:return np.array([[c,0,s],[0,1,0],[-s,0,c]])
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])
SH={'u':1.0,'d':0.5,'n':0.8,'s':0.8,'e':0.6,'w':0.6}
def faces(a,b):
    x1,y1,z1=a;x2,y2,z2=b
    return {'n':[(x2,y2,z1),(x1,y2,z1),(x1,y1,z1),(x2,y1,z1)],'s':[(x1,y2,z2),(x2,y2,z2),(x2,y1,z2),(x1,y1,z2)],
            'e':[(x2,y2,z2),(x2,y2,z1),(x2,y1,z1),(x2,y1,z2)],'w':[(x1,y2,z1),(x1,y2,z2),(x1,y1,z2),(x1,y1,z1)],
            'u':[(x1,y2,z1),(x2,y2,z1),(x2,y2,z2),(x1,y2,z2)],'d':[(x1,y1,z2),(x2,y1,z2),(x2,y1,z1),(x1,y1,z1)]}
def render(model,texdir,N=256,view=None,flip=False):
    tex=[np.asarray(Image.open(texdir+'/'+t).convert('RGBA')).astype(float) for t in model['tex']]
    g=(model.get('d') or {}).get('gui') or {}
    R=np.eye(3)
    rr=view if view is not None else g.get('r',[0,0,0])
    for ax in (0,1,2): R=rotm(ax,rr[ax])@R if False else R
    R=rotm(0,rr[0])@rotm(1,rr[1])@rotm(2,rr[2])
    sc=np.array(g.get('s',[1,1,1]),float);tr=np.array(g.get('t',[0,0,0]),float)
    tris=[]
    for el in model['el']:
        a=np.array(el['a'],float);b=np.array(el['b'],float)
        er=el.get('r')
        ER=None
        if er:
            o=np.array(er[:3]);ang=er[3:6];ER=(o,rotm(2,ang[2])@rotm(1,ang[1])@rotm(0,ang[0]))
        for k,vs in faces(a,b).items():
            f=el['f'].get(k)
            if not f:continue
            u1,v1,u2,v2=f[:4];ti=f[4] if len(f)>4 else 0;rot=f[5] if len(f)>5 else 0
            uvc=[(u1,v1),(u2,v1),(u2,v2),(u1,v2)];sh=int(rot//90)%4
            uvs=[uvc[(i+sh)%4] for i in range(4)]
            P=[]
            for v in vs:
                p=np.array(v,float)
                if ER:p=ER[1]@(p-ER[0])+ER[0]
                p=R@((p-8)*sc)+tr
                if flip:p=p*np.array([-1,1,-1])
                P.append(p)
            for (i,j,l) in ((0,1,2),(0,2,3)):tris.append((P[i],P[j],P[l],uvs[i],uvs[j],uvs[l],ti,SH[k]))
    img=np.zeros((N,N,4));zb=np.full((N,N),-1e9)
    allp=np.array([q for t in tris for q in t[:3]]) if tris else np.zeros((1,3))
    lo=allp.min(0);hi=allp.max(0);ctr=(lo+hi)/2;S=N*0.92/max(hi[0]-lo[0],hi[1]-lo[1],1e-6)
    def scr(p):return np.array([N/2+(p[0]-ctr[0])*S,N/2-(p[1]-ctr[1])*S,p[2]])
    for p0,p1,p2,t0,t1,t2,ti,sh in tris:
        A,B,C=scr(p0),scr(p1),scr(p2)
        den=(B[1]-C[1])*(A[0]-C[0])+(C[0]-B[0])*(A[1]-C[1])
        if abs(den)<1e-9:continue
        xs=[A[0],B[0],C[0]];ys=[A[1],B[1],C[1]]
        x0,x1=max(0,int(min(xs))),min(N-1,int(max(xs))+1);y0,y1=max(0,int(min(ys))),min(N-1,int(max(ys))+1)
        if x0>x1 or y0>y1:continue
        X,Y=np.meshgrid(np.arange(x0,x1+1)+0.5,np.arange(y0,y1+1)+0.5)
        w0=((B[1]-C[1])*(X-C[0])+(C[0]-B[0])*(Y-C[1]))/den
        w1=((C[1]-A[1])*(X-C[0])+(A[0]-C[0])*(Y-C[1]))/den
        w2=1-w0-w1
        m=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6)
        if not m.any():continue
        z=w0*A[2]+w1*B[2]+w2*C[2]
        T=tex[ti];th,tw=T.shape[:2]
        u=(w0*t0[0]+w1*t1[0]+w2*t2[0])/16*tw;v=(w0*t0[1]+w1*t1[1]+w2*t2[1])/16*tw
        ui=np.clip(u.astype(int),0,tw-1);vi=np.clip(v.astype(int),0,th-1)
        col=T[vi,ui]
        sub_zb=zb[y0:y1+1,x0:x1+1];m=m&(z>sub_zb)&(col[...,3]>8)
        sub_img=img[y0:y1+1,x0:x1+1]
        c=col.copy();c[...,:3]*=sh
        sub_img[m]=c[m];sub_zb[m]=z[m]
    return Image.fromarray(np.clip(img,0,255).astype('uint8'),'RGBA')
if __name__=='__main__':
    m=json.load(open(sys.argv[1]));im=render(m,sys.argv[2],flip=len(sys.argv)>4 and sys.argv[4]=='flip');im.save(sys.argv[3])
