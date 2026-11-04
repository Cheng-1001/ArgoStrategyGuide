"""Crop 128 px monster thumbnails from in-game codex screenshots (2560x1440, Monstres page).
Usage: python3 -I tools/codex_thumbs.py <folder of codex_###_*.png> <out folder>
Finds the centre panel on row 455, masks pixels that differ from the panel colour in the model band (y 445-775),
keeps the model's connected parts, crops a square around them and pads with the panel colour (never the header or name text).
Writes mob_###.jpg and sheet.jpg (contact sheet to check by eye). The screenshots stay local; only the thumbnails go to icons/mobs/."""
import sys,glob,os,re
import numpy as np
from PIL import Image
import cv2
src,out=sys.argv[1],sys.argv[2];os.makedirs(out,exist_ok=True)
tiles=[]
for f in sorted(glob.glob(src+'/*.png')):
    num=re.search(r'codex_(\d{3})',f).group(1)
    im=np.array(Image.open(f).convert('RGB')).astype(int)
    # find centre panel: on row y=560 the panel is a long light run around x 750..1440 (shifts right sometimes)
    row=im[455]; light=(row.min(1)>175)&(row.max(1)-row.min(1)<30)
    runs=[];s=None
    for x,v in enumerate(light):
        if v and s is None:s=x
        if not v and s is not None:runs.append((s,x));s=None
    if s is not None:runs.append((s,len(light)))
    runs=[r for r in runs if 450<r[1]-r[0]<800 and 600<r[0]<1200]
    x0,x1=max(runs,key=lambda r:r[1]-r[0]) if runs else (744,1440)
    y0,y1=445,775
    reg=im[y0:y1,x0+10:x1-10]
    bg=np.median(np.concatenate([reg[:6].reshape(-1,3),reg[-6:].reshape(-1,3)]),0)
    d=np.abs(reg-bg).sum(2); mask=(d>60).astype(np.uint8)
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(mask)
    W_=reg.shape[1];keep=[i for i in range(1,n) if st[i,4]>400 and st[i,0]>2 and st[i,0]+st[i,2]<W_-2 and st[i,1]+st[i,3]<reg.shape[0]-1]
    if not keep: print(num,'nothing');continue
    big=max(keep,key=lambda i:st[i,4])
    # union of components that are reasonably big (detached parts of the model) and near the main one
    xs=[];ys=[]
    for i in keep:
        if st[i,4]>=0.03*st[big,4]:
            xs+= [st[i,0],st[i,0]+st[i,2]]; ys+=[st[i,1],st[i,1]+st[i,3]]
    bx0,bx1,by0,by1=min(xs),max(xs),min(ys),max(ys)
    cx,cy=(bx0+bx1)/2,(by0+by1)/2; side=max(bx1-bx0,by1-by0)*1.12
    X0=int(x0+10+cx-side/2);Y0=int(y0+cy-side/2);S=int(side)
    full=Image.open(f).convert('RGB')
    # never reach into the header line above or the name text below: take what lies inside the model band, pad the rest with the panel colour
    band=(max(X0,x0+10),max(Y0,y0-8),min(X0+S,x1-10),min(Y0+S,y1+8))
    sq=Image.new('RGB',(S,S),tuple(int(v) for v in bg))
    sq.paste(full.crop(band),(band[0]-X0,band[1]-Y0))
    crop=sq.resize((128,128),Image.LANCZOS)
    crop.save(f'{out}/mob_{num}.jpg',quality=88)
    tiles.append((num,crop)); print(num,'panel',x0,x1,'box',S)
W=8;sheet=Image.new('RGB',(W*136,((len(tiles)+W-1)//W)*150),(40,40,40))
from PIL import ImageDraw
dr=ImageDraw.Draw(sheet)
for k,(num,c) in enumerate(tiles):
    x=(k%W)*136+4;y=(k//W)*150+4;sheet.paste(c,(x,y));dr.text((x,y+130),'#'+num,fill=(255,255,255))
sheet.save(out+'/sheet.jpg',quality=88)
