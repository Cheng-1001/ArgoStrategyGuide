"""Post-process props.png (2026-11-05, user: 道具圖示有疊影).
Official items whose item model is flat (item-models/m/<path>.json has "flat":1 and one texture) were captured as
3D renders, which shows the extruded back face as a double image. This swaps those cells for the flat texture
(item-models/t/<hash>.png), and the 3D keys whose catalogue image is only a UV atlas for a render made by
tools/model_render.py. usage: python3 -I props_flat.py <work dir> <repo>
<work dir> holds props_old.png/props_old.js (copies of the current files), im/flat.json {officialId: texture},
im/t/<texture>, im/rk/<rendered key>.png."""
import json,sys,io,hashlib
from PIL import Image
S=sys.argv[1];R=sys.argv[2]
CELL=48;COLS=16
s=open(S+'/props_old.js').read();i=s.index('window.SAO_PROPS=')+17
head=s[:i];rows=json.loads(s[i:s.rindex(';')])
flat=json.load(open(S+'/im/flat.json'))
extra={1824:S+'/im/rk/elitecreatures_knight_assortment_key.png',1823:S+'/im/rk/rpg_essentials_1_rpg_essentials_1_model_key_shadow.png',2116:S+'/im/rk/treasure_tier_pack_keys_gold_key.png',2118:S+'/im/rk/treasure_tier_pack_keys_wood_key.png'}
OUTLINE=set()   # user 2026-11-05: no outline on the keys
old=Image.open(S+'/props_old.png').convert('RGBA')
def fitpx(im):
    im=im.convert('RGBA');w,h=im.size
    if h>w: im=im.crop((0,0,w,w))   # animated strip: first frame
    bb=im.getbbox()
    if not bb: return None
    im=im.crop(bb);w,h=im.size;s=min((CELL-4)/w,(CELL-4)/h)
    if s>=2: s=int(s);im=im.resize((w*s,h*s),Image.NEAREST)
    elif s>=1: im=im.resize((round(w*s),round(h*s)),Image.NEAREST)
    else: im=im.resize((max(1,round(w*s)),max(1,round(h*s))),Image.LANCZOS)
    c=Image.new('RGBA',(CELL,CELL),(0,0,0,0));c.paste(im,((CELL-im.size[0])//2,(CELL-im.size[1])//2),im);return c
cells=[];seen={};changed=0
def add(c):
    h=hashlib.md5(c.tobytes()).hexdigest()
    if h not in seen: seen[h]=len(cells);cells.append(c)
    return seen[h]
for r in rows:
    src=extra.get(r[0]) or (S+'/im/t/'+flat[str(r[0])] if str(r[0]) in flat else None)
    c=None
    if src: c=fitpx(Image.open(src))
    if c is not None and r[0] in OUTLINE:
        from PIL import ImageFilter
        a=c.split()[3].point(lambda v:255 if v>40 else 0).filter(ImageFilter.MaxFilter(3))
        ol=Image.new('RGBA',c.size,(214,206,232,0));ol.putalpha(a.point(lambda v:150 if v else 0));ol.alpha_composite(c);c=ol
    if c is not None: changed+=1
    elif r[7]>=0: c=old.crop(((r[7]%COLS)*CELL,(r[7]//COLS)*CELL,(r[7]%COLS)*CELL+CELL,(r[7]//COLS)*CELL+CELL))
    r[7]=add(c) if c is not None else -1
sheet=Image.new('RGBA',(COLS*CELL,((len(cells)+COLS-1)//COLS)*CELL),(0,0,0,0))
for k,c in enumerate(cells): sheet.paste(c,((k%COLS)*CELL,(k//COLS)*CELL))
sheet.save(R+'/props.png',optimize=True)
open(R+'/props.js','w',encoding='utf-8').write(head+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n')
print('changed',changed,'cells',len(cells),'missing',sum(r[7]<0 for r in rows))
