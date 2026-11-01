"""Build recipes.js: floor 1 crafting / purchase recipes for the 配方 tab and the NPC panels.

Usage: python3 -I tools/build_recipes.py <reference-map clone>/Aincrad/eCompendium/ecompendium_current.js <catalog.json>
  - ecompendium_current.js: DelayedCode's SAO MC Interactive Map, Current Data (text-parsed, never executed).
    Only facts are taken: item name, level, where it is made, materials and amounts, Col cost.
  - catalog.json: the official item catalogue (saominecraft.com/wiki), used to link items to catalogue ids.
In-game screenshots from the owner (SHOTS below) win over the reference map for the same NPC + item.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF, CAT = sys.argv[1], sys.argv[2]

# owner's in-game screenshots (2026-11-01): npc -> [(catalogue id, name, seconds, mats, cost Col or "Free", rarity)]
SHOTS = {
    "Bandit Accessories": [
        (1455, "Bandit Coin", 30, [["Small Pouch", 24]], "Free", None),
        (2040, "Gloves of the Bandit", 15, [["Small Pouch", 16]], "Free", None),
        (1456, "Bandit Hood", 15, [["Small Pouch", 16]], "Free", None),
        (1292, "Stolen Amulet", 30, [["Small Pouch", 24]], "Free", None)],
    "Shark Accessories": [
        (None, "Shark Amulet", 15, [["Shark Shell", 8], ["Birch String", 1]], "30", "c"),
        (None, "Shark Fang", 30, [["Shark Shell", 12], ["Wolf Fangs", 8]], "33", "b"),
        (None, "Bracelet of the Shark", 30, [["Shark Shell", 12], ["Iron Ingot", 1]], "33", "b"),
        (None, "Ring of the Shark", 15, [["Shark Shell", 8]], "30", "c")],
}
SAME = {"Bandit's Gloves": "Gloves of the Bandit"}          # reference-map name -> in-game name
# material names used in game / by the reference map -> this site's ITEMS ids
MAT = {"Shark Carapace": "Shark Shell", "Soul of the Ruins": "Souls of the Ruins", "Sylve Shoot": "Sylvan Sprout",
       "Hard Glacial Hide": "Glacial Hardhide", "Essence of Gorbel": "Gorbel Essence", "Heart of Nymbrea": "Nymbréa's Heart",
       "Fragment of the Bear's Soul": "Bear Soul Fragment", "Small Purse": "Small Pouch"}
# item name -> official catalogue id (checked by hand: name keyword, level and set)
OID = {"Training Sword": 2596, "Training Bow": 1566, "Training Crossbow": 1727, "Training Scythe": 1761, "Katana Training": 1762,
       "Training Magic Staff": 2569, "Unbound Grimoire": 1626, "Training Lantern": 1627, "Wild Grimoire": 1628,
       "Beginner's Tunic": 1334, "Beginner Leggings": 1335, "Beginner's Boots": 1336,
       "Bracelet of the Stags": 1594, "Gloves of the Stags": 2043, "Slimy Ring": 2478, "Gelatinous Bracelet": 1592,
       "Gelatinous Amulet": 1291, "Gelatinous Cloak": 1453, "Spider Bracelet": 1595, "Iron Ring": 2482, "Iron Bracelet": 1593,
       "Iron Gloves": 2042, "Iron Coin": 1457, "Iron Amulet": 1297, "Copper Ring": 2477, "Copper Bracelet": 1591,
       "Copper Gloves": 2039, "Copper Coin": 1452, "Copper Amulet": 1290, "Bracelet of the Sylvan": 1589, "Ring of the Sylve": 2473,
       "Skeleton Skull": 1450, "Belt of the Stags": 1460, "Ring of the Wolf": 2480, "Albal's Necklace": 1296,
       "Stolen Cloak": 1454, "Sticky Ring": 2479, "Occult Skull": 1461}
CATS = {"weapon": "weapon", "armor": "armor", "accessory": "acc", "consumable": "potion", "dungeon": "key"}
EXTRA_POTION = {"Purification Elixir"}                      # listed under "material" by the reference map

t = open(REF, encoding="utf-8").read()
f1 = t[t.index("floor1: {"):t.index("floor2: {")]
secs = [(m.start(), m.group(1)) for m in re.finditer(r"\n    (\w+): \[", f1)]
npcs = {}
for k, (pos, sec) in enumerate(secs):
    body = f1[pos:secs[k + 1][0] if k + 1 < len(secs) else len(f1)]
    for m in re.finditer(r'\{\s*\n\s*name: "([^"]*)",(.*?)\n      \}', body, re.S):
        name, b = m.group(1), m.group(2)
        res = re.findall(r'\{\s*item: "([^"]*)",\s*amount: ([\d.]+)\s*\}', b)
        loc = re.search(r'craftingLocation: "([^"]*)"', b)
        cat = CATS.get(sec) or ("potion" if name in EXTRA_POTION else None)
        if not res or not loc or not cat:
            continue
        lv = re.search(r"level: (\d+)", b)
        npc = re.sub(r"^F1 - ", "", loc.group(1))
        mats = [[MAT.get(i, i), int(float(a))] for i, a in res if i != "Col"]
        col = next((str(int(float(a))) for i, a in res if i == "Col"), None)
        name = SAME.get(name, name)
        npcs.setdefault(npc, []).append([OID.get(name), name, None, mats, col, None, cat, int(lv[1]) if lv else None, "ref"])

for npc, rows in SHOTS.items():                              # screenshots replace the same item, keep the rest
    old = {r[1]: r for r in npcs.get(npc, [])}
    new = [[oid, n, sec, mats, cost, rar, "acc", (old.get(n) or [None] * 8)[7], "shot"] for oid, n, sec, mats, cost, rar in rows]
    names = {r[1] for r in new}
    npcs[npc] = new + [r for r in npcs.get(npc, []) if r[1] not in names]

cat_ids = {x["id"] for x in json.load(open(CAT, encoding="utf-8"))}
bad = [r[1] for rows in npcs.values() for r in rows if r[0] is not None and r[0] not in cat_ids]
assert not bad, bad

hdr = """/* Floor 1 recipes by NPC (key = NPC name; matches npcs.js where that NPC is mapped). Built by tools/build_recipes.py.
   Row: [catalogueId|null, name, seconds|null, [[material, qty]], cost Col ("Free"; null = unknown), rarity|null, category, level, source]
   category: weapon / armor / acc / potion / key. source: "shot" = owner's in-game screenshot (wins), "ref" = reference map.
   Weapons and armour here are only the starter gear sold by the Starting Merchant; smiths' recipes still need screenshots. */
window.SAO_RECIPES = """
out = {npc: {"floor": 1, "items": rows} for npc, rows in sorted(npcs.items())}
open(os.path.join(ROOT, "recipes.js"), "w", encoding="utf-8").write(hdr + json.dumps(out, ensure_ascii=False, indent=0) + ";\n")
n = sum(len(r) for r in npcs.values())
from collections import Counter
print(n, "recipes,", len(npcs), "NPCs", Counter(r[6] for rows in npcs.values() for r in rows), Counter(r[8] for rows in npcs.values() for r in rows))
