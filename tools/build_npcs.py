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
      dict(c='accessoriesBlacksmith',n='Corrupted Boar Accessories',x=1778,z=3530,u=False,src='site2'),   # Boar Zone smith ([NPC] Accessory Blacksmith), owner's screenshots 2026-11-07 02:20 (player X 1778 Z 3527-3533)
      # owner's screenshots 2026-11-03 22:40-23:00 (player position next to the NPC)
      dict(c='other',n='Weapon Recycling',x=1776,z=4132,u=False,src='site2'),
      dict(c='other',n='Accessory Recycling',x=1766,z=4123,u=False,src='site2'),
      dict(c='other',n='Auction House',x=1825,z=4086,u=False,src='site2'),
      dict(c='other',n='Vault',x=1825,z=4091,u=False,src='site2'),
      dict(c='other',n='Labyrinth Archaeologist',x=2389,z=2412,u=False,src='site2'),
      dict(c='other',n='Web Archaeologist',x=1019,z=1178,u=False,src='site2')]   # Arakh'Nol, next to the Xal'Zirith guard; owner's screenshot 2026-11-06 01:58 (minimap x 1019 z 1178 y 116); its window is "Aragorn's Lair - Loot Info" (sell tab)   # Geldorak Mine entrance, owner's screenshot 2026-11-03 22:10   # Tolbana, owner's gameplay video 2026-10-30 (player position next to the NPC)
res+=SITE
# reference-map rows that are the same NPC as another one (owner's screenshots 2026-11-08 13:44 / 13:51: at X 1790 Z 4181 the only tags are
# [NPC] 新手商人 and [NPC] 工具商人 — the Starting Merchant also buys back loot; at X 1021 Z 1178 only [NPC] 蛛網考古學家 (Web Archaeologist,
# sell-only window "Aragorn's Lair - Loot Info") and the Xal'Zirith guard)
DROP={'Boar and Wolf loot buyer',"Aragorn's Lair - Loot Buyer"}
res=[r for r in res if r['n'] not in DROP]
# NPC positions computed from the owner's screenshots (2026-11-11, scratchpad npcpos/: compass bearing + where the NPC is on screen;
# the minimap X/Z is the PLAYER's position, ~3 blocks off). 'tri' = sight lines from several screenshots taken from different directions
# meet (lines within 0.4 block of the point), 'one' = one screenshot, distance from the NPC's on-screen face/body size x1.17 (about ±1 block).
# Block coordinate = floor of the computed point (HUD X/Z taken as the block the player stands in).
CALC={'Accessory Recycling':(1766,4126,'tri',5,'2026-11-03、11-08'),
      'Weapon Recycling':(1773,4132,'tri',4,'2026-11-03、11-08'),
      'Iron Accessories':(1763,4144,'tri',5,'2026-11-03、11-08'),
      'Copper Accessories':(1773,4135,'tri',4,'2026-11-03、11-08'),   # reference map has 1771,4131 (4 blocks off; 4 lines meet within 0.04)
      'Labyrinth Archaeologist':(2389,2408,'one',1,'2026-11-03'),
      'Auction House':(1831,4079,'one',1,'2026-11-07')}   # a row of 4 clerks at X 1831-1832, Z 4072 / 4077 / 4079 / 4085 (NPC_NOTE)
for r in res:
    if r['n'] in CALC: x,z,m,k,d=CALC[r['n']]; r.update(x=x,z=z,src='calc')
# underground hideouts the owner reached (2026-11-08): Secret Wolf Gloves = ice room at the bottom of a shaft in Wolf Valley (Y 70)
for r in res:
    if r['n'] in ('Secret Accessory Blacksmith',): r['u']=True
# owner 2026-11-07: every Occult Merchant (Amulet / Artifacts / Bracelet / Gloves / Ring) is in a basement -> u = 2 ("地下室")
for r in res:
    if r['n'].startswith('Occult Merchant'): r['u']=2
res.sort(key=lambda r:((CATS+['beggar','other']).index(r['c']),r['n']))
from collections import Counter
print(len(res),Counter(r['c'] for r in res)); print(Counter(r['src'] for r in res))
rows=',\n'.join(' '+json.dumps([r['c'],r['n'],r['x'],r['z'],r['src']]+([2 if r['u']==2 else 1] if r['u'] else []),ensure_ascii=False) for r in res)
hdr='''/* Floor 1 NPCs by role, from DelayedCode's SAO MC Interactive Map (titles, roles and X / Z only).
   Row: [category, name, x, z, src, underground?] (1 = underground, 2 = in a basement, owner-confirmed); src "ref" = Current Data, "beta" = only in the reference
   map's Beta-test data (may have moved since). Beta rows are used only for roles that Current Data does not list at all.
   "site" = located in game by the site owner (SITE list in tools/build_npcs.py); "site2" = the owner's position when taking the screenshot;
   "calc" = computed from the owner's screenshots (CALC in tools/build_npcs.py; SAO_NPC_CALC: m tri = several directions, one = one screenshot).
   Floors 2 / 3: src "ref23" = the reference map's floor-2/3 rows, in its own "map-local" coordinates (not yet checked against the game). */
window.SAO_NPCS={1:[
'''
# Floors 2 and 3 (2026-11-11, user: fill floors 2/3 from the old reference map): every NPC row of maps_floor2.js / maps_floor3.js.
# The reference map marks these floors "map-local" (its own coordinates, not yet checked against the game) -> src "ref23".
# 'refaire' (Refaiter / Refauncher) has no site category -> other; 'runeCraftsmen' gets its own type.
def load23(f,fl):
    t=open(D+f,encoding='utf-8').read();out=[]
    for m in re.finditer(r'\n  "?([\w-]+)"?:\s*\{(.*?)\n  \}',t,re.S):   # some keys are unquoted
        b=m.group(2);g=lambda k:(re.search(k+r':\s*"([^"]*)"',b) or [None,None])[1]
        c=re.search(r'coords:\s*\{\s*x:\s*(-?[\d.]+),\s*z:\s*(-?[\d.]+)',b);cat=g('category')
        if g('floor')!=fl or g('type')!='NPC' or not c: continue
        cat=cat if cat in CATS+['runeCraftsmen'] else 'other'
        out.append(dict(c=cat,n=g('title').strip(),x=round(float(c[1])),z=round(float(c[2])),u='underground: true' in b,src='ref23'))
    out.sort(key=lambda r:((CATS+['runeCraftsmen','beggar','other']).index(r['c']),r['n']))
    return out
F23={2:load23('maps_floor2.js','floor2'),3:load23('maps_floor3.js','floor3')}
# 2026-11-12 (in24, owner's floor-2/3 screenshots, user "3A"): positions worked out from one screenshot each — floor 3 has the
# F3 debug screen (player X/Z, facing, the block the crosshair hits behind the NPC), so the NPC lies between the player and that block;
# no second direction, about ±2 blocks. Key (floor, name) -> (x, z, date, note). NEW23 = NPCs the reference map does not have.
CALC23={(3,'Assistant to the Alchemist'):(828,656,'2026-11-12',''),(3,'Alchemist'):(830,659,'2026-11-12',''),
        (3,'Loot Buyer Sylnovar'):(824,663,'2026-11-12',''),(3,'Reinforced Tools Merchant'):(938,594,'2026-11-12',''),
        (3,'Basic Rune Craftsman'):(912,598,'2026-11-12',''),(3,'Complex Rune Craftsman'):(856,536,'2026-11-12',''),
        (3,'Sylnovar Accessories Blacksmith'):(919,598,'2026-11-12','遊戲名牌「神器鐵匠」、視窗「P3 - Craft Artefact de Sylnovar」；參考互動地圖的 Sylnovar Accessories Blacksmith 在 X 918 Z 579，差約 19 格，推測是同一位'),
        # 2026-11-13 (in26, F3 player position + targeted block): 05.11.41 / 05.12.18. The reference map has both ~14-15 blocks further north (-Z);
        # Sylnovar's smith above is +19: the reference points are not shifted as a whole (too few points)
        (3,'Refaiter'):(345,597,'2026-11-13','遊戲名牌「[重塑師] 材料」、視窗「P3 - Refaçonneur 材料」；參考互動地圖寫 X 345 Z 583，差約 14 格'),
        (3,"Adventurer's Shoemaker"):(359,587,'2026-11-13','沒有名牌；視窗「P3 - Craft 靴子 de l\'Aventurier」會做冒險者之靴。參考互動地圖的 Adventurer\'s Shoemaker 在 X 358 Z 572，差約 15 格，推測是同一位'),
        (2,'Manufacturer of the Runic Necklace'):(1,196,'2026-11-10','遊戲視窗標題只寫「2 -」，會做符文項鍊；參考互動地圖寫 X -38 Z 199，差約 39 格，依名稱推測是同一位')}
NEW23=[(3,'other','Vault',815,675,'2026-11-12'),(3,'other','Auction House',826,675,'2026-11-12'),
       (3,'accessoriesBlacksmith','P3 - Craft Couteau en Dent de Loup',707,855,'2026-11-12'),
       (3,'accessoriesBlacksmith','P3 - Craft Gants Féroce',706,833,'2026-11-12'),
       (3,'accessoriesBlacksmith','P3 - Forgeron Grimoire Corrompu',642,600,'2026-11-12'),
       # 2026-11-13 (in26): listed without a position (user 2026-11-13: in the NPC list, no coordinates). Estimates kept here only:
       # Draconique ~X 1157 Z 1043 Y 77 (02.10.24/25 F3 player position + targeted block); Pionnier ~X 1068 Z 917 Y 172 (04.48.13, guessed: nameplate not seen)
       (3,'accessoriesBlacksmith','P3 - Craft Anneau Draconique Corrompu',None,None,'2026-11-13','遊戲視窗標題「P3 - Craft 戒指 Draconique 腐化」，在第 3 層尊弗特東邊的森林'),
       (3,'accessoriesBlacksmith','P3 - Craft Bottes du Pionnier',None,None,'2026-11-13','遊戲視窗標題「P3 - Craft 靴子 du Pionnier」，在室內')]
for fl,rs in F23.items():
    for r in rs:
        if (fl,r['n']) in CALC23: x,z,d,nt=CALC23[(fl,r['n'])]; r.update(x=x,z=z,src='calc')
for fl,c,n,x,z,d,*nt in NEW23:
    F23[fl].append(dict(c=c,n=n,x=x,z=z,u=False,src='calc' if x is not None else 'nopos')); CALC23[(fl,n)]=(x,z,d,nt[0] if nt else '')
miss=[k for k in CALC23 if not any(r['n']==k[1] for r in F23[k[0]])]; assert not miss, miss
print({k:len(v) for k,v in F23.items()})
rows23=''.join(',\n'+str(k)+':[\n'+',\n'.join(' '+json.dumps([r['c'],r['n'],r['x'],r['z'],r['src']]+([1] if r['u'] else []),ensure_ascii=False) for r in v)+'\n]' for k,v in F23.items())
C={n:{'m':m,'k':k,'d':d} for n,(x,z,m,k,d) in CALC.items()}
C.update({'%d|%s'%(f,n):{'m':'f3' if x is not None else 'nopos','k':1,'d':d,**({'t':nt} if nt else {})} for (f,n),(x,z,d,nt) in CALC23.items()})
calc='window.SAO_NPC_CALC='+json.dumps(C,ensure_ascii=False)+';\n'
open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'npcs.js'),'w',encoding='utf-8').write(hdr+rows+'\n]'+rows23+'};\n'+calc)
