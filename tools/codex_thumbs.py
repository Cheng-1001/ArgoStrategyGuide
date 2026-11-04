"""Cut out 128 px monster thumbnails (transparent PNG) from in-game codex screenshots (2560x1440, Monstres page).
Usage: python3 -I tools/codex_thumbs.py <folder of codex_###_*.png> <out folder>
The codex panel is semi-transparent, so the game world shows through it and the background is uneven (user 2026-11-04):
the model is cut out instead of cropped with its background.
 1. find the centre panel on row 455; work in the model band (y 440-780) inside it
 2. estimate the (smoothly varying) background: inpaint the likely-model pixels, then blur heavily
 3. pixels that differ from that background = model, except the codex's soft glow behind it (neutral, bright, no texture); keep the model's connected parts (TOP_ONLY: upper copy only)
 4. fill holes inside the model only where they look like model (gaps that show background/glow stay empty), shrink the edge 1 px and feather it (no background halo)
 5. square crop around the model, 128 px RGBA PNG
Writes mob_###.png and sheet.png (on a checkerboard and on a dark colour, to check by eye).
The screenshots stay local; only the thumbnails go to icons/mobs/."""
import sys,glob,os,re
import numpy as np
from PIL import Image,ImageDraw
import cv2
src,out=sys.argv[1],sys.argv[2];os.makedirs(out,exist_ok=True)
# the codex draws these models twice (whole monster on top, loose parts underneath; a server-side glitch): keep the top
TOP_ONLY={'041','042','043'}
tiles=[]
def panel_x(im):
    row=im[455];light=(row.min(1)>175)&(row.max(1)-row.min(1)<30)
    runs=[];s=None
    for x,v in enumerate(light):
        if v and s is None:s=x
        if not v and s is not None:runs.append((s,x));s=None
    if s is not None:runs.append((s,len(light)))
    runs=[r for r in runs if 450<r[1]-r[0]<800 and 600<r[0]<1200]
    return max(runs,key=lambda r:r[1]-r[0]) if runs else (744,1440)
for f in sorted(glob.glob(src+'/*.png')):
    num=re.search(r'codex_(\d{3})',f).group(1)
    rgb=np.array(Image.open(f).convert('RGB'))
    x0,x1=panel_x(rgb.astype(int))
    X0,X1,Y0,Y1=x0+12,x1-12,440,780
    reg=rgb[Y0:Y1,X0:X1].copy();H,W=reg.shape[:2]
    # 2-3: background estimate and model mask (two rounds)
    fg=np.zeros((H,W),np.uint8)
    g=reg.astype(np.float32);gray=g.mean(2)
    sd=np.sqrt(np.maximum(cv2.blur(gray*gray,(5,5))-cv2.blur(gray,(5,5))**2,0))
    glow=((g.max(2)-g.min(2))<16)&(g.min(2)>165)&(sd<3.5)
    for it in range(3):
        hole=cv2.dilate(fg,np.ones((15,15),np.uint8)) if it else fg
        bg=cv2.inpaint(reg,hole*255,9,cv2.INPAINT_TELEA) if it else reg
        bg=cv2.GaussianBlur(bg,(0,0),25 if it else 40)
        d=np.abs(reg.astype(int)-bg.astype(int)).sum(2)
        fg=(d>(36 if it else 60)).astype(np.uint8)
        # the codex draws a soft light glow behind the model: neutral, bright and smooth (no pixel texture) -> not model
        fg[glow]=0
        fg=cv2.morphologyEx(fg,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        n,lab,st,_=cv2.connectedComponentsWithStats(fg)
        keep=[i for i in range(1,n) if st[i,4]>300 and st[i,0]>2 and st[i,0]+st[i,2]<W-2 and st[i,1]+st[i,3]<H-1]
        if not keep: break
        big=max(keep,key=lambda i:st[i,4])
        if num in TOP_ONLY: big=min([i for i in keep if st[i,4]>=0.2*st[big,4]],key=lambda i:st[i,1])
        b0,b1=st[big,1],st[big,1]+st[big,3]
        sel=[i for i in keep if st[i,4]>=0.02*st[big,4] and (num not in TOP_ONLY or (st[i,1]<b1 and st[i,1]+st[i,3]>b0))]
        fg=np.isin(lab,sel).astype(np.uint8)
    if not fg.any(): print(num,'nothing');continue
    # 4: fill holes inside the model (translucent slimes, faces close to the panel colour); no GrabCut: it grew halos
    m=fg.copy();inv=(1-m).astype(np.uint8);n,lab,st,_=cv2.connectedComponentsWithStats(inv)
    # only holes that look like model: a gap between legs / bow and body shows the background or the glow -> stays empty
    bgl=(d<=36)|glow
    for i in range(1,n):
        if st[i,0]>0 and st[i,1]>0 and st[i,0]+st[i,2]<W and st[i,1]+st[i,3]<H:
            h=lab==i
            if st[i,4]<=12 or bgl[h].mean()<0.5: m[h]=1
    alpha=cv2.GaussianBlur(cv2.erode(m*255,np.ones((2,2),np.uint8)).astype(np.float32),(0,0),0.8)
    rgba=np.dstack([reg,np.clip(alpha,0,255).astype(np.uint8)])
    # 5: square crop
    ys,xs=np.nonzero(m);bx0,bx1,by0,by1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    side=int(max(bx1-bx0,by1-by0)*1.08);cx,cy=(bx0+bx1)//2,(by0+by1)//2
    sq=Image.new('RGBA',(side,side),(0,0,0,0));tile=Image.fromarray(rgba,'RGBA')
    sq.paste(tile.crop((cx-side//2,cy-side//2,cx-side//2+side,cy-side//2+side)),(0,0))
    th=sq.resize((128,128),Image.LANCZOS);th.save(f'{out}/mob_{num}.png',optimize=True)
    tiles.append((num,th));print(num,'panel',x0,x1,'model px',int(m.sum()))
# contact sheet: each thumbnail on a checkerboard and on the site's dark ring colour
T=128;sheet=Image.new('RGB',(8*(2*T+12)+8,((len(tiles)+7)//8)*(T+22)+8),(40,40,40));dr=ImageDraw.Draw(sheet)
chk=Image.new('RGB',(T,T));cd=ImageDraw.Draw(chk)
for yy in range(0,T,16):
    for xx in range(0,T,16): cd.rectangle([xx,yy,xx+15,yy+15],fill=(255,255,255) if (xx+yy)//16%2 else (205,205,205))
for k,(num,c) in enumerate(tiles):
    x=8+(k%8)*(2*T+12);y=8+(k//8)*(T+22)
    a=chk.copy();a.paste(c,(0,0),c);sheet.paste(a,(x,y))
    b=Image.new('RGB',(T,T),(22,30,40));b.paste(c,(0,0),c);sheet.paste(b,(x+T,y));dr.text((x,y+T+4),'#'+num,fill=(255,255,255))
sheet.save(out+'/sheet.png')
