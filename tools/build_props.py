"""Build props.js / props.png: every non-equipment item of the official catalogue.
usage: python3 build_props.py <repo>"""
import json,os,sys,glob
from PIL import Image
OUT=sys.argv[1]
src=open('build_equip.py').read()
ns={'Image':Image,'os':os,'CELL':48};exec(src[src.index('def clean'):src.index('cells=[]')],ns)   # clean, clean_insp, opaque_light, fit
clean,clean_insp,opaque_light,fit=ns['clean'],ns['clean_insp'],ns['opaque_light'],ns['fit']
CELL=48;COLS=16
A=json.load(open('catalog.json'));V=json.load(open('im_index.json'))['vanilla']
EQ={'sword','dagger','bow','crossbow','staff_mage','staff_shaman','shield','armor','gloves','ring','amulet','bracelet','artifact'}
P=[x for x in A if x['category'] not in EQ]
dirs=sorted(glob.glob('pshots_[0-9]'))
def shot(k):
    b=k.replace('/','__')
    for d in dirs:
        f=os.path.join(d,b)
        if os.path.exists(f+'.png'): return f
    return None
cells=[];cache={};rows=[];miss=0;okc={}
for x in sorted(P,key=lambda x:(x['category'],x['level'] or 0,x['name'])):
    e=dict((c,p) for c,p in V.get(x['mmo_material'] or '',{}).get('e',[]));k=e.get(x['mmo_cmd']) or ('id%d'%x['id'])
    f16='icons/%d.png'%x['id'];choice=None
    if os.path.exists(f16) and Image.open(f16).size==(16,16): choice=('i',f16)
    else:
        b=shot(k)
        if b:
            if b not in okc:
                n,lt=opaque_light(clean(Image.open(b+'.png')))
                if n>=400 and lt<=0.5: okc[b]=('s',b+'.png')
                elif os.path.exists(b+'.insp.png') and opaque_light(clean_insp(Image.open(b+'.insp.png')))[0]>=300: okc[b]=('n',b+'.insp.png')
                else: okc[b]=None
            choice=okc[b]
    ic=-1
    if choice:
        if choice[1] in cache: ic=cache[choice[1]]
        else:
            im=Image.open(choice[1]);im=clean(im) if choice[0]=='s' else clean_insp(im) if choice[0]=='n' else im
            c=fit(im)
            if c is not None: ic=len(cells);cells.append(c);cache[choice[1]]=ic
    if ic<0: miss+=1
    st={k2:v for k2,v in (x['identifications'] or {}).items() if not k2.startswith('Disable') and not k2.startswith('Hide')}
    rows.append([x['id'],x['name'],x['category'],x['rarity'],x['level'],(x['lore'] or '').replace('\n',' '),st,ic])
sheet=Image.new('RGBA',(COLS*CELL,max(1,(len(cells)+COLS-1)//COLS)*CELL),(0,0,0,0))
for i,c in enumerate(cells): sheet.paste(c,((i%COLS)*CELL,(i//COLS)*CELL))
sheet.save(os.path.join(OUT,'props.png'),optimize=True)
hdr='''/* Every non-equipment item of the official item catalogue (saominecraft.com/wiki, fetched 2026-10-31):
   materials, gathering items, consumables, potions, runes, keys, event items. Names and lore are the official (French) text.
   Row: [officialId, name, category, rarity, level, lore, stats, iconIndex]; props.png: 48 px cells, 16 per row.
   Built by tools/build_props.py; regenerate rather than edit by hand. */
'''
open(os.path.join(OUT,'props.js'),'w',encoding='utf-8').write(hdr+'window.SAO_PROPS='+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n')
print('items',len(rows),'icons',len(cells),'missing',miss,'png',os.path.getsize(os.path.join(OUT,'props.png'))//1024,'KB')
