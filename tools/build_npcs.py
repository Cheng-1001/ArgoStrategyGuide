import re,json,math
D='ext/SAO-MC-Interactive-Map/Aincrad/Map/'
CATS=['alchemist','lumberjack','lootBuyers','weaponSellers','travelingMerchants','equipmentMerchants','toolMerchants','accessoriesMerchants','occultMerchants','consumablesMerchants','weaponsmith','armorBlacksmith','ingotBlacksmith','keyBlacksmith','materialsBlacksmith','accessoriesBlacksmith','equipmentBlacksmith','secretAccessoryBlacksmith']
def load(f,cur):
    t=open(D+f,encoding='utf-8').read();out=[]
    for m in re.finditer(r'"([\w-]+)":\s*\{(.*?)\n  \}',t,re.S):
        b=m.group(2);g=lambda k:(re.search(k+r':\s*"([^"]*)"',b) or [None,None])[1]
        c=re.search(r'coords:\s*\{\s*x:\s*(-?\d+),\s*z:\s*(-?\d+)',b);cat=g('category')
        if g('floor')!='floor1' or cat not in CATS or not c: continue
        if cur and g('dataset')!='current': continue
        x,z=int(c[1]),int(c[2])
        if not(70<=x<=5050 and 70<=z<=5050): continue
        out.append(dict(c=cat,n=re.sub(r'^F1 - ','',g('title')).strip(),x=x,z=z,u='underground: true' in b,src='ref' if cur else 'beta'))
    return out
cur=load('maps_current.js',True); beta=load('maps_floor1.js',False)
res=list(cur)
curcats={r['c'] for r in cur}
for b in beta:
    if b['c'] in curcats: continue          # Current Data already covers this role; Beta positions are likely outdated
    res.append(b)
res.sort(key=lambda r:(CATS.index(r['c']),r['n']))
from collections import Counter
print(len(res),Counter(r['c'] for r in res)); print(Counter(r['src'] for r in res))
rows=',\n'.join(' '+json.dumps([r['c'],r['n'],r['x'],r['z'],r['src']]+([1] if r['u'] else []),ensure_ascii=False) for r in res)
hdr='''/* Floor 1 NPCs by role, from DelayedCode's SAO MC Interactive Map (titles, roles and X / Z only).
   Row: [category, name, x, z, src, underground?]; src "ref" = Current Data, "beta" = only in the reference
   map's Beta-test data (may have moved since). Beta rows are used only for roles that Current Data does not list at all. */
window.SAO_NPCS={1:[
'''
open('/home/user/ArgoStrategyGuide/npcs.js','w',encoding='utf-8').write(hdr+rows+'\n]};\n')
