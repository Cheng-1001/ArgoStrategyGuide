"""Post-process equip.png (2026-11-07, user: 圖示去背不完全、圖示錯誤，全部都要檢查).
equip.png cells were partly 3D renders of the official item cards with the background keyed out; flat items
(rings, necklaces, bracelets, gloves, armour) came out with the hollow parts filled white and some with the
UV atlas instead of the item. For every equipment row whose official item model is flat
(item-models/m/<path>.json "flat":1, one texture) the cell is redrawn from pixel art:
  1. the catalogue image (image_url) when it is a 16x16 / 32x32 sprite (or a vertical animation strip of those):
     it is the official picture and has real transparency;
  2. otherwise the model's own texture (item-models/t/<hash>.png) — e.g. Amulette d'Améthyste, whose image_url is
     a dragon-mask atlas.
3D models (weapons, shields, some armour) are drawn from the same official model with tools/model_render.py
(orthographic, the model's own gui rotation; 192 px, then scaled down) instead of the old card screenshots, which
had leftover background and several wrong pictures (Bottes Tactiques showed a ring, Dague Médiocre a texture atlas…).
Items without a model keep their old cell.
Pixel art is scaled by a whole number (16 px -> 48 px) with nearest neighbour.
usage: python3 -I tools/equip_flat.py <work dir> <repo>
<work dir>: equip_old.png/equip_old.js (copies of the current files), off/catalog.json, off/im_index.json,
off/mj/<path>.json (item models), off/icons/<id>.png (catalogue images), im/t/<texture>."""
import json,sys,os,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import model_render
from PIL import Image
S=sys.argv[1];R=sys.argv[2];CELL=48;COLS=16
s=open(S+'/equip_old.js',encoding='utf-8').read();i=s.index('window.SAO_EQUIP=')+len('window.SAO_EQUIP=')
head=s[:i];rows=json.loads(s[i:s.rindex(';')])
A={x['id']:x for x in json.load(open(S+'/off/catalog.json'))}
V=json.load(open(S+'/off/im_index.json'))['vanilla']
SKIP={1734}   # Arbalète Hurlante: catalogue sprite is a broken fragment, no model
def model(x):
    e=dict((c,p) for c,p in V.get(x['mmo_material'],{}).get('e',[]));p=e.get(x['mmo_cmd'])
    f=S+'/off/mj/'+p.replace('/','__')+'.json' if p else None
    return json.load(open(f)) if f and os.path.exists(f) else None
def fitpx(im):
    im=im.convert('RGBA');w,h=im.size
    if h>w and h%w==0: im=im.crop((0,0,w,w))
    bb=im.getbbox()
    if not bb: return None
    im=im.crop(bb);w,h=im.size;k=CELL/max(w,h)
    im=im.resize((w*int(k),h*int(k)),Image.NEAREST) if k>=1 else im.resize((max(1,round(w*k)),max(1,round(h*k))),Image.LANCZOS)
    c=Image.new('RGBA',(CELL,CELL),(0,0,0,0));c.paste(im,((CELL-im.size[0])//2,(CELL-im.size[1])//2),im);return c
old=Image.open(S+'/equip_old.png').convert('RGBA')
cells=[];seen={};changed=0
def add(c):
    h=hashlib.md5(c.tobytes()).hexdigest()
    if h not in seen: seen[h]=len(cells);cells.append(c)
    return seen[h]
for r in rows:
    c=None;x=A.get(r[0]);m=model(x) if x else None
    if r[0] not in SKIP and m and m.get('flat') and len(m.get('tex',[]))==1:
        p=S+'/off/icons/%d.png'%r[0];src=None
        if os.path.exists(p):
            w,h=Image.open(p).size
            if w in (16,32) and (h==w or (h>w and h%w==0)): src=p
        src=src or S+'/im/t/'+m['tex'][0]
        if os.path.exists(src): c=fitpx(Image.open(src))
    elif r[0] not in SKIP and m and m.get('el') and all(os.path.exists(S+'/im/t/'+t) for t in m.get('tex',[])):
        im=model_render.render(m,S+'/im/t',N=192)
        bb=im.getbbox()
        if bb:
            im=im.crop(bb);w,h=im.size;k=(CELL-2)/max(w,h);im=im.resize((max(1,round(w*k)),max(1,round(h*k))),Image.LANCZOS)
            c=Image.new('RGBA',(CELL,CELL),(0,0,0,0));c.paste(im,((CELL-im.size[0])//2,(CELL-im.size[1])//2),im)
    if c is not None: changed+=1
    elif r[8] is not None and r[8]>=0: c=old.crop(((r[8]%COLS)*CELL,(r[8]//COLS)*CELL,(r[8]%COLS)*CELL+CELL,(r[8]//COLS)*CELL+CELL))
    r[8]=add(c) if c is not None else -1
sheet=Image.new('RGBA',(COLS*CELL,((len(cells)+COLS-1)//COLS)*CELL),(0,0,0,0))
for k,c in enumerate(cells): sheet.paste(c,((k%COLS)*CELL,(k//COLS)*CELL))
sheet.save(R+'/equip.png',optimize=True)
open(R+'/equip.js','w',encoding='utf-8').write(head+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n')
print('changed',changed,'cells',len(cells))
