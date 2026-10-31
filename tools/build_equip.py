import json,os,sys
from PIL import Image
OUT=sys.argv[1]
A=json.load(open('catalog.json'));V=json.load(open('im_index.json'))['vanilla']
need=json.load(open('models_need.json'));keys=list(need)
EQ=['sword','dagger','bow','crossbow','staff_mage','staff_shaman','shield','armor','gloves','ring','amulet','bracelet','artifact']
E=[x for x in A if x['category'] in EQ]
CELL=48;COLS=16
def clean(im):
    im=im.convert('RGBA');w,h=im.size;px=im.load()
    bg=px[2,2]
    # flood fill near-bg from borders
    from collections import deque
    seen=set();dq=deque([(x,y) for x in range(w) for y in (0,h-1)]+[(x,y) for y in range(h) for x in (0,w-1)])
    def near(c):return abs(c[0]-bg[0])+abs(c[1]-bg[1])+abs(c[2]-bg[2])<40
    while dq:
        x,y=dq.popleft()
        if (x,y) in seen or not(0<=x<w and 0<=y<h):continue
        seen.add((x,y))
        if px[x,y][3]==0 or near(px[x,y]):
            px[x,y]=(0,0,0,0);dq.extend([(x+1,y),(x-1,y),(x,y+1),(x,y-1)])
    return im
def clean_insp(im):
    im=im.convert('RGBA').crop((12,12,408,250));w,h=im.size;px=im.load();bg=px[w//2,4]
    from collections import deque
    seen=set();dq=deque([(x,y) for x in range(w) for y in (0,h-1)]+[(x,y) for y in range(h) for x in (0,w-1)])
    near=lambda c:abs(c[0]-bg[0])+abs(c[1]-bg[1])+abs(c[2]-bg[2])<18
    while dq:
        x,y=dq.popleft()
        if (x,y) in seen or not(0<=x<w and 0<=y<h):continue
        seen.add((x,y))
        if near(px[x,y]):px[x,y]=(0,0,0,0);dq.extend([(x+1,y),(x-1,y),(x,y+1),(x,y-1)])
    return im
def opaque_light(im):
    px=[p for p in im.get_flattened_data() if p[3]>0]
    return len(px),(sum(1 for p in px if p[0]>225 and p[1]>225 and p[2]>225)/len(px) if px else 1)
def fit(im):
    im=im.convert('RGBA');bb=im.getbbox()
    if not bb:return None
    im=im.crop(bb);w,h=im.size;s=min((CELL-4)/w,(CELL-4)/h)
    rs=Image.NEAREST if s>=1 else Image.LANCZOS
    im=im.resize((max(1,round(w*s)),max(1,round(h*s))),rs)
    c=Image.new('RGBA',(CELL,CELL),(0,0,0,0));c.paste(im,((CELL-im.size[0])//2,(CELL-im.size[1])//2),im);return c
cells=[];cache={};okshot={};rows=[];miss=0
for x in sorted(E,key=lambda x:(x['level'] or 0,x['name'])):
    src=None
    e=dict((c,p) for c,p in V.get(x['mmo_material'],{}).get('e',[]));k=e.get(x['mmo_cmd']) or ('nomodel:%s:%s'%(x['mmo_material'],x['mmo_cmd']))
    f16='icons/%d.png'%x['id']
    cands=[]
    if os.path.exists(f16) and Image.open(f16).size==(16,16):cands.append(('i',f16))
    cands.append(('s','shots2/id%d.png'%x['id']))
    if k in need:cands.append(('s','shots/%03d.png'%keys.index(k)))
    cands.append(('s','shots3/'+k.replace('/','__')+'.png'))
    cands.append(('s','shots3/id%d.png'%x['id']))
    for c in cands:
        if not os.path.exists(c[1]):continue
        if c[0]=='s':
            if c[1] not in okshot:
                n,lt=opaque_light(clean(Image.open(c[1])))
                okshot[c[1]]=n>=400 and lt<=0.5
            if not okshot[c[1]]:
                ins=c[1].replace('.png','.insp.png')
                if os.path.exists(ins):
                    if ins not in okshot:okshot[ins]=opaque_light(clean_insp(Image.open(ins)))[0]>=300
                    if okshot[ins]:src=('n',ins);break
                continue
        src=c;break
    ic=-1
    if src:
        if src[1] in cache:ic=cache[src[1]]
        else:
            im=Image.open(src[1]);im=clean(im) if src[0]=='s' else clean_insp(im) if src[0]=='n' else im
            c=fit(im)
            if c is not None:ic=len(cells);cells.append(c);cache[src[1]]=ic
    if ic<0:miss+=1
    st={k:v for k,v in (x['identifications'] or {}).items() if not k.startswith('Disable') and not k.startswith('Hide')}
    slot=''
    m=x['mmo_material'] or ''
    for a,b in (('helmet','head'),('chestplate','chest'),('leggings','legs'),('boots','feet')):
        if a in m:slot=b
    rows.append([x['id'],x['name'],x['category'],x['rarity'],x['level'],x['damage'],(x['lore'] or '').replace('\n',' '),st,ic,slot])
sheet=Image.new('RGBA',(COLS*CELL,((len(cells)+COLS-1)//COLS)*CELL),(0,0,0,0))
for i,c in enumerate(cells):sheet.paste(c,((i%COLS)*CELL,(i//COLS)*CELL))
sheet.save(OUT+'/equip.png',optimize=True)
hdr='''/* Equipment from the official item catalogue (saominecraft.com/wiki, fetched 2026-10-31): weapons, shields,
   armour and accessories. Names and lore are the official (French) text.
   Row: [officialId, name, category, rarity, level, damage, lore, stats, iconIndex, armourSlot]
   equip.png: 48 px cells, 16 per row; icons are the official 2D icon or a capture of the official 3D model render.
   Regenerate rather than edit by hand. */
'''
open(OUT+'/equip.js','w',encoding='utf-8').write(hdr+'window.SAO_EQUIP='+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n')
print('items',len(rows),'icons',len(cells),'missing',miss,'png',os.path.getsize(OUT+'/equip.png')//1024,'KB','js',os.path.getsize(OUT+'/equip.js')//1024,'KB')
