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
        (2,'Manufacturer of the Runic Necklace'):(1,196,'2026-11-10','遊戲視窗標題只寫「2 -」，會做符文項鍊；參考互動地圖寫 X -38 Z 199，差約 39 格，依名稱推測是同一位'),
        # 2026-11-17 (in27, owner's 11/15～11/18 screenshots with F3: player X/Z + targeted block; scratchpad in27/TRIAGE.md 1-C). Only these points
        # are moved; the reference map is not shifted as a whole
        (3,'Occult Rings Merchant'):(979,1015,'2026-11-15','Y 68；遊戲視窗「P3 - 神秘 - 戒指」，羅盤「霧之避難所」；參考互動地圖寫 X 985 Z 1017'),
        (3,'Accessories Bandit Blacksmith'):(1191,750,'2026-11-15','Y 62；遊戲視窗「P3 - 製作飾品 強盜」（取得途徑寫 P3 - Craft Accessoires Bandit）；參考互動地圖寫 X 1192 Z 741，差約 9 格'),
        (3,'Bandit Loot Repreneur'):(1186,742,'2026-11-15','Y 62；遊戲視窗「P3 - Repreneur - Bandits」；參考互動地圖寫 X 1185 Z 732，差約 10 格'),
        (3,'Amethyst Armor Blacksmith'):(626,1388,'2026-11-15','Y 74；遊戲名牌「[NPC] 防具鐵匠」、視窗「P3 - Craft Armure d\'紫水晶」；參考互動地圖寫 X 627 Z 1370，差約 18 格'),
        (3,'Occult Artifact Merchant'):(953,519,'2026-11-17','Y 14，木屋室內；遊戲視窗「P3 - 神秘 - 神器」；參考互動地圖寫 X 939 Z 510，差約 17 格'),
        (3,'Occult Runes Merchant'):(723,166,'2026-11-15','Y 93；符文視窗的截圖沒有拍到名牌，NPC 和神祕商人同款（紅色火把），推測是同一位；參考互動地圖寫 X 723 Z 151，差約 15 格'),
        (3,'Loot Buyer Treant'):(501,1401,'2026-11-18','Y 69；遊戲名牌「[NPC] 戰利品收購商」、視窗「P3 - 收購商 - 樹人」；參考互動地圖寫 X 499 Z 1390，差約 11 格'),
        # 2026-11-18 (in28, owner's 11/13～11/14 screenshots with F3: player X/Z + targeted block, about ±2 blocks; scratchpad in28/TRIAGE.md 1-C).
        # Only these points are moved; the reference map is not shifted as a whole
        (3,'Ringman'):(526,1387,'2026-11-13','Y 73；遊戲名牌「[NPC] 戒指商人」、視窗「P3 - 戒指商人」；參考互動地圖寫 X 537 Z 1382，差約 12 格'),
        (3,'Glove Merchant'):(505,1414,'2026-11-13','Y 69；遊戲名牌「[NPC] 手套商人」、視窗「P3 - 手套商人」；參考互動地圖寫 X 505 Z 1408，差約 6 格'),
        (3,'Ring Blacksmith'):(561,1412,'2026-11-13','Y 74；遊戲視窗「P3 - 製作飾品 de Sylnovar」（取得途徑寫 P3 - Craft Accessoires de Sylnovar）；參考互動地圖寫 X 562 Z 1409，差約 3 格'),
        (3,'Glove Blacksmith'):(568,1414,'2026-11-13','Y 79，和戒指鐵匠同一棟；遊戲視窗「P3 - Craft 手套 de Sylnovar」；參考互動地圖寫 X 567 Z 1411，差約 3 格'),
        (3,'Simple Accessories Merchant'):(570,1383,'2026-11-13','Y 79；遊戲名牌「[NPC] 飾品商人」、視窗「P3 - 飾品商人」；參考互動地圖寫 X 570 Z 1378，差約 5 格'),
        (3,'Bracelet Blacksmith'):(561,1363,'2026-11-13','Y 84；遊戲視窗「P3 - Craft Bracelets de Sylnovar」；參考互動地圖寫 X 561 Z 1361，差約 2 格'),
        (3,'Amulet Blacksmith'):(559,1370,'2026-11-13','Y 79；遊戲名牌「[NPC] 護符鐵匠」；參考互動地圖寫 X 559 Z 1367，差約 3 格'),
        (3,'Amulet Merchant'):(581,1343,'2026-11-13','Y 77；遊戲名牌「[NPC] 護符商人」、視窗「P3 - 護符商人」；參考互動地圖寫 X 581 Z 1338，差約 5 格'),
        (3,'Artifact Merchant'):(561,1344,'2026-11-13','Y 77；遊戲名牌「[NPC] 神器商人」、視窗「P3 - 神器商人」；參考互動地圖寫 X 561 Z 1338，差約 6 格'),
        (3,'Bracelet Merchant'):(536,1356,'2026-11-13','Y 78～80；遊戲名牌「[NPC] 手環商人」、視窗「P3 - 手環商人」；參考互動地圖寫 X 537 Z 1352，差約 4 格'),
        (3,'Loot Buyer Sylvaer'):(610,1384,'2026-11-13','Y 74；遊戲名牌「[SYLVAER] 戰利品收購商」；參考互動地圖寫 X 609 Z 1373，差約 11 格'),
        (3,'Spider Loot Repreneur'):(533,869,'2026-11-14','Y 67；遊戲名牌「[NPC] 戰利品收購商」、視窗「P3 - Repreneur - Araignées」；參考互動地圖寫 X 532 Z 860，差約 9 格'),
        (3,'Tribe Belt Blacksmith'):(236,1221,'2026-11-13','Y 79；遊戲視窗「P3 - Craft Artefact Ceinture Orc」；參考互動地圖寫 X 235 Z 1200，差約 21 格'),
        (3,'Ancient Wood Armor Blacksmith'):(779,274,'2026-11-14','Y 88，羅盤「迷宮區」；遊戲視窗「P3 - Craft Armure des Bois Anciens」；參考互動地圖寫 X 780 Z 253，差約 21 格'),
        (2,'Manufacturer of the Fierce Talisman'):(98,-55,'2026-11-14','Y 70；名牌「???」、視窗「第 2 層 - 飾品鍛造：凶猛護符」；參考互動地圖寫 X 78 Z -71，差約 25 格（第 2 層參考地圖的座標系統和遊戲一致，這個點本身沒對過）'),
        # 2026-11-19 owner decision (in29 TRIAGE B-4～B-6): use the positions worked out from the 11/18 screenshots (F3 player X/Z + targeted
        # block, about ±2 blocks). The window titles mean the same as these reference-map names; only these points are moved
        (2,'Scrap Accessories Blacksmith'):(238,323,'2026-11-18','Y 74，薩布勒莫礦脈附近；名牌看不到，遊戲視窗「第 2 層 - 廢鐵飾品」（取得途徑寫「第2層-廢鐵飾品」）。參考互動地圖的 Scrap Accessories Blacksmith 在 X -777 Z 17，差 1000 格以上；視窗標題意思相同、只看到這一位，網站當成同一位、改用截圖推算的位置（站長 2026-11-19）'),
        (2,'Manufacturer of the Ring of the Flaming Harpy'):(-613,276,'2026-11-18','Y -10，烈焰巢穴地下；名牌「???」，遊戲視窗「第 2 層 - 飾品鍛造：赤鳥身女妖戒指」。參考互動地圖寫 X -694 Z 205，差約 107 格，改用截圖推算的位置（站長 2026-11-19）'),
        (2,'Manufacturer of the Ring of the Drowned Harpy'):(-802,211,'2026-11-18','Y 43，洞穴裡；名牌「???」。遊戲視窗和取得途徑都寫「第 2 層 - 飾品鍛造：綠鳥身女妖戒指」，和做被碾碎之戒的那一位標題完全相同；這一位做藍色的溺水的鳥身女妖之戒，網站為了區分改叫「第 2 層 - 飾品鍛造：藍鳥身女妖戒指」（站長 2026-11-19 指定）。參考互動地圖寫 X -818 Z 98，差約 113 格，改用截圖推算的位置'),
        (2,'Manufacturer of the Crushed Harpy Ring'):(-580,532,'2026-11-18','Y 129；名牌「???」，遊戲視窗「第 2 層 - 飾品鍛造：綠鳥身女妖戒指」（另一位做溺水之戒的工坊標題相同，網站把那一位改叫藍鳥身女妖戒指）。參考互動地圖寫 X -618 Z 529，差約 38 格，改用截圖推算的位置（站長 2026-11-19）')}
NEW23=[(3,'other','Vault',815,675,'2026-11-12'),(3,'other','Auction House',826,675,'2026-11-12'),
       (3,'accessoriesBlacksmith','P3 - Craft Couteau en Dent de Loup',707,855,'2026-11-12'),
       (3,'accessoriesBlacksmith','P3 - Craft Gants Féroce',706,833,'2026-11-12'),
       (3,'accessoriesBlacksmith','P3 - Forgeron Grimoire Corrompu',642,600,'2026-11-12'),
       # 2026-11-13 (in26): listed without a position (user 2026-11-13: in the NPC list, no coordinates). Estimates kept here only:
       # Draconique ~X 1157 Z 1043 Y 77 (02.10.24/25 F3 player position + targeted block); Pionnier ~X 1068 Z 917 Y 172 (04.48.13, guessed: nameplate not seen)
       (3,'accessoriesBlacksmith','P3 - Craft Anneau Draconique Corrompu',None,None,'2026-11-13','遊戲視窗標題「P3 - Craft 戒指 Draconique 腐化」，在第 3 層尊弗特東邊的森林'),
       (3,'accessoriesBlacksmith','P3 - Craft Bottes du Pionnier',None,None,'2026-11-13','遊戲視窗標題「P3 - Craft 靴子 du Pionnier」，在室內'),
       # 2026-11-17 (in27, F3 player position + targeted block, about ±2 blocks; names = the obtain line / window title; TRIAGE 1-C)
       (3,'accessoriesBlacksmith','P3 - Craft Artefact Manteau Crocs Bois',956,999,'2026-11-15','洞穴裡，Y 63；房間有告示牌「SI AUCUN NPC PREVENEZ LA MODERATION」'),
       (3,'other','P3 - Craft Clée des Bois Ancien',1203,746,'2026-11-15','Y 62'),
       (3,'other','P3 - Craft Jeton Occulte',1175,745,'2026-11-15','Y 62'),
       (3,'other','P3 - Craft Clée des Bandits',1172,739,'2026-11-15','Y 62'),
       (3,'accessoriesBlacksmith','P3 - Craft Artefact Masque Voleur',1186,803,'2026-11-15','Y 90'),
       (3,'accessoriesBlacksmith',"P3 - Craft Artefact Boucles d'Oreilles Bois Sombres",689,1428,'2026-11-15','樹上，Y 118'),
       (3,'accessoriesBlacksmith','P3 - Craft Bracelet Goblin',978,1079,'2026-11-15','泰瑞亞莉絲之井，Y 67'),
       (3,'accessoriesBlacksmith','P3 - Craft Orbe Goblinne',957,1140,'2026-11-15','泰瑞亞莉絲之井的石室，Y 60；這張沒有開 F3，依小地圖座標和面向推算'),
       (3,'accessoriesBlacksmith','P3 - Craft Anneau des Cieux',None,None,'2026-11-15','獸人營地；21.43.04 從約 X 256 Z 1169 Y 116 往下看到 NPC 的頭頂（沒有 F3），推測在這附近、比玩家低'),
       (3,'other','P3 - Craft Outils des Bois Anciens',254,312,'2026-11-16','羅盤「迷宮區」，Y 85'),
       (2,'other',"考古學家 de l'Antre",-157,721,'2026-11-15','阿斯特里歐斯的巢穴入口告示板左邊，Y 83；遊戲名牌「[NPC] 考古學家 de l\'Antre」，視窗「L\'Antre d\'Astérius - 戰利品資訊」'),
       # 2026-11-18 (in28, F3 player position + targeted block; TRIAGE 1-C 16～19)
       (3,'accessoriesBlacksmith',"P3 - Craft Bottes de l'Explorateur",427,740,'2026-11-13','沒有名牌；視窗「P3 - Craft 靴子 de l\'Explorateur」，Y 87'),
       (3,'accessoriesBlacksmith','P3 - Craft Artefact Manteau Crocs Brumeux',727,801,'2026-11-13','洞穴裡，Y 53；房間有告示牌「SI AUCUN NPC PREVENEZ LA MODERATION」'),
       (3,'accessoriesBlacksmith','P3 - Forgeron Gants Corrompus',923,490,'2026-11-13','Y 99；遊戲視窗「P3 - 鐵匠 手套 Corrompus」'),
       # 03.30.50: the NPC fills the frame ~2-3 blocks in front of the player (520.6, -709.1, facing north); the targeted block (520, -717) is behind it
       (2,'other','蜂巢考古學家',520,-712,'2026-11-14','梅莉歐娜蜂巢入口旁，Y 74；遊戲名牌「[NPC] 蜂巢考古學家」、視窗「蜜蜂地下城 - 戰利品資訊」。位置是推測：NPC 在玩家正前方約 2～3 格（依畫面大小估距離），準星打到它後面的方塊 X 520 Z -717'),
       # 2026-11-19 (in29 00.32.40～42, F3 player 597.1 / 69 / -721.6, targeted block 598, 70, -723): name = the window title (nameplate is ???)
       (2,'accessoriesBlacksmith','第 2 層 - 飾品鍛造：維尼戒指',597,-722,'2026-11-19','甜蜜森林，Y 69；名牌「???」；只做維尼之戒。參考互動地圖附近沒有這位（只有 Honeyed Loot Buyer、Bees Weapon Blacksmith）；它的熊飾品鐵匠 Bull & Bear Accessories Blacksmith 在 -602,-285，差約 1200 格、是多品項鐵匠，判斷不是同一位'),
       # 2026-11-19 owner decision (in29 TRIAGE B-7): 19.37.28 / 19.37.30 F3 player 890.6 / 59 / 398.4 facing north, targeted block 890, 59, 396.
       # Added like the glove / grimoire smiths of the same series; the reference map's Low Corruption Bracelet Blacksmith (439, 474, underground) is kept
       (3,'accessoriesBlacksmith','P3 - Forgeron Bracelet Corrompu',890,397,'2026-11-18','Y 59，紫水晶礦坑'),
       # 2026-11-19 owner decision (in29 B-26 option B): listed without a position like the Anneau des Cieux smith; 00.44.28～35 show no coordinates.
       # The reference map's Manufacturer of Corrupt Mask (-713, -109) is kept and not linked (this batch's floor-2 smiths are 38～1000+ blocks off it)
       (2,'accessoriesBlacksmith','第 2 層 - 飾品鍛造：腐化面具',None,None,'2026-11-19','遊戲視窗「第 2 層 - 飾品鍛造：腐化面具」（取得途徑寫「第2層-飾品鍛造：腐化面具」）；截圖讀不到座標。參考互動地圖有一位 Manufacturer of Corrupt Mask（X -713 Z -109），名稱意思相同但位置沒對過，沒有合併')]
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
