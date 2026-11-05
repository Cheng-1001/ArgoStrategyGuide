"""Rebuild npcs.js from the reference map (DelayedCode/SAO-MC-Interactive-Map).
Usage: python3 -I tools/build_npcs.py <clone>/Aincrad/Map
"""
import re,json,math
import sys, os
D=(sys.argv[1] if len(sys.argv)>1 else 'ext/SAO-MC-Interactive-Map/Aincrad/Map').rstrip('/')+'/'   # reference map repo's Aincrad/Map folder; text-parsed, never executed
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
# the site groups these types by function for the map filter (NGRP in src/index.html); the type itself is kept
res=list(cur)
curcats={r['c'] for r in cur}
for b in beta:
    if b['c'] in curcats: continue          # Current Data already covers this role; Beta positions are likely outdated
    res.append(b)
# NPCs the site owner located in game (not in the reference map); src "site"
SITE=[dict(c='beggar',n='臭乞丐',x=3336,z=1760,u=False,src='site'),
      dict(c='other',n='Mine Archaeologist',x=4280,z=3891,u=False,src='site2'),   # Geldorak Mine entrance, owner's screenshot 2026-11-03 22:10
      # owner's screenshots 2026-11-03 22:40-23:00 (player position next to the NPC)
      dict(c='other',n='Weapon Recycling',x=1776,z=4132,u=False,src='site2'),
      dict(c='other',n='Accessory Recycling',x=1766,z=4123,u=False,src='site2'),
      dict(c='other',n='Auction House',x=1825,z=4086,u=False,src='site2'),
      dict(c='other',n='Vault',x=1825,z=4091,u=False,src='site2'),
      dict(c='other',n='Labyrinth Archaeologist',x=2389,z=2412,u=False,src='site2'),
      dict(c='other',n='Web Archaeologist',x=1019,z=1178,u=False,src='site2')]   # Arakh'Nol, next to the Xal'Zirith guard; owner's screenshot 2026-11-06 01:58 (minimap x 1019 z 1178 y 116); its window is "Aragorn's Lair - Loot Info" (sell tab)   # Geldorak Mine entrance, owner's screenshot 2026-11-03 22:10   # Tolbana, owner's gameplay video 2026-10-30 (player position next to the NPC)
res+=SITE
res.sort(key=lambda r:((CATS+['beggar','other']).index(r['c']),r['n']))
from collections import Counter
print(len(res),Counter(r['c'] for r in res)); print(Counter(r['src'] for r in res))
rows=',\n'.join(' '+json.dumps([r['c'],r['n'],r['x'],r['z'],r['src']]+([1] if r['u'] else []),ensure_ascii=False) for r in res)
hdr='''/* Floor 1 NPCs by role, from DelayedCode's SAO MC Interactive Map (titles, roles and X / Z only).
   Row: [category, name, x, z, src, underground?]; src "ref" = Current Data, "beta" = only in the reference
   map's Beta-test data (may have moved since). Beta rows are used only for roles that Current Data does not list at all.
   "site" = located in game by the site owner (SITE list in tools/build_npcs.py). */
window.SAO_NPCS={1:[
'''
open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'npcs.js'),'w',encoding='utf-8').write(hdr+rows+'\n]};\n')
