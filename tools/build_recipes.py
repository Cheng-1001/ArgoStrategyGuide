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

# owner's in-game screenshots (2026-11-01, 2026-11-03 evening batch): npc -> [(name, rarity, seconds, mats, cost Col or "Free", category)]
# loot buyers' Buy tab = potions sold for Col (no materials). Catalogue id comes from OID.
SHOTS = {
    'Shark Accessories': [
        ('Ring of the Shark', 'c', 15, [['Shark Carapace', 8]], '30', 'acc'),
        ('Shark Amulet', 'c', 15, [['Shark Carapace', 8], ['Birch String', 1]], '30', 'acc'),
        ('Shark Fang', 'b', 30, [['Shark Carapace', 12], ['Wolf Fangs', 8]], '33', 'acc'),
        ('Bracelet of the Shark', 'b', 30, [['Shark Carapace', 12], ['Iron Ingot', 1]], '33', 'acc'),
    ],
    'Spider Accessories': [
        ('Spider Ring', 'c', 15, [['Spider Cloth', 8], ['Coal Ore', 8]], '30', 'acc'),
        ('Spider Bracelet', 'c', 15, [['Spider Cloth', 8], ['Corrupted Spore', 8]], '30', 'acc'),
        ('Spider Gloves', 'c', 15, [['Spider Cloth', 8], ['Spider Thread', 8]], '30', 'acc'),
        ('Spider Cloak', 'b', 30, [['Spider Cloth', 12], ['Spider Thread', 8]], '33', 'acc'),
    ],
    'Ice Golem Accessories': [
        ('Frozen Ring', 'b', 30, [['Hard Glacial Hide', 12], ['Frost Dust', 8]], '33', 'acc'),
        ('Frozen Bracelet', 'b', 30, [['Hard Glacial Hide', 16]], '33', 'acc'),
        ('Frozen Gloves', 'c', 15, [['Hard Glacial Hide', 12]], '30', 'acc'),
        ('Frozen Amulet', 'c', 15, [['Hard Glacial Hide', 8], ['Birch String', 1]], '30', 'acc'),
    ],
    'Deer Accessories': [
        ('Bracelet of the Stags', 'b', 30, [['Mountain Stag Hide', 12]], '33', 'acc'),
        ('Gloves of the Stags', 'b', 30, [['Mountain Stag Hide', 12]], '33', 'acc'),
    ],
    'Ice Spirit Accessories': [
        ('Glacial Ring', 'b', 30, [['Glacial Magic Shard', 12], ['Frost Dust', 8]], '33', 'acc'),
        ('Glacial Antenna', 'b', 30, [['Glacial Magic Shard', 16]], '33', 'acc'),
        ('Glacial Essence', 'a', 60, [['Frost Dust', 32]], '40', 'acc'),
        ('Glacial Amulet', 'b', 30, [['Glacial Magic Shard', 12], ['Birch String', 1]], '33', 'acc'),
    ],
    'Slime Accessories': [
        ('Slimy Ring', 'c', 15, [['Slime Jelly', 8]], '25', 'acc'),
        ('Gelatinous Bracelet', 'b', 30, [['Slime Jelly', 12], ['Slime Core', 4]], '28', 'acc'),
        ('Gelatinous Amulet', 'c', 15, [['Oak String', 1], ['Slime Jelly', 8]], '25', 'acc'),
    ],
    'Elite Treant Accessories': [
        ('Elite Gloves', 'c', 15, [['Wolf Fur', 8]], '25', 'acc'),
        ('Elite Amulet', 'c', 15, [['Oak String', 1], ['Sylvan Bark', 8]], '25', 'acc'),
        ('Elite Bracelet', 'b', 30, [['Oak Log', 4], ['Titan Bark', 4], ['Sylvan Bark', 8]], '28', 'acc'),
        ('Elite Carapace', 'b', 30, [['Titan Bark', 8], ['Sylvan Bark', 8], ['Sylve Sprout', 8]], '28', 'acc'),
    ],
    'Sylve Accessories': [
        ('Bracelet of the Sylve', 'c', 15, [['Oak Log', 8], ['Magic Wood Shard', 8]], '25', 'acc'),
        ('Amulet of the Sylve', 'c', 15, [['Magic Wood Shard', 8], ['Oak String', 1]], '25', 'acc'),
        ('Ring of the Sylve', 'b', 30, [['Magic Wood Shard', 8], ['Allium Flower', 8], ['Oak Log', 4], ['Wood Heart', 1]], '28', 'acc'),
    ],
    'Nepenthes Accessories': [
        ('Ring of the Nepenthes', 'c', 15, [['Leaf Fragments', 8], ['Corrupted Spore', 8]], '25', 'acc'),
        ('Bracelet of the Nepenthes', 'b', 30, [['Leaf Fragments', 12]], '28', 'acc'),
        ('Amulet of the Nepenthes', 'c', 15, [['Leaf Fragments', 4], ['Corrupted Spore', 4], ['Oak String', 1]], '25', 'acc'),
    ],
    'Bandit Accessories': [
        ('Gloves of the Bandit', 'c', 15, [['Small Purse', 16]], 'Free', 'acc'),
        ('Bandit Hood', 'c', 15, [['Small Purse', 16]], 'Free', 'acc'),
        ('Stolen Amulet', 'b', 30, [['Small Purse', 24]], 'Free', 'acc'),
        ('Stolen Cloak', 'b', 30, [['Small Purse', 24]], 'Free', 'acc'),
        ('Bandit Coin', 'b', 30, [['Small Purse', 24]], 'Free', 'acc'),
    ],
    'Geldorak Dungeon Guard - Starting Town': [
        ('Forest Key', 'c', 60, [['Sylvan Bark', 8], ['Wood Heart', 4], ['Magic Mycelium', 1]], '10', 'key'),
    ],
    'Sewer Reshaper': [
        ('Slime Essence', 'a', 60, [['Slime Jelly', 16], ['Essence of Gorbel', 1]], '20', 'other'),
        ('Slime Tear', 's', 240, [['Slime Core', 16]], '25', 'other'),
    ],
    'Vallhat - Loot Buyer': [
        ('Health Potion I', 'c', None, [], '5.02', 'potion'),
        ('Mana Potion I', 'c', None, [], '5.02', 'potion'),
        ('Stamina Potion I', 'c', None, [], '5.02', 'potion'),
    ],
    'Hanaka - Loot Buyer': [
        ('Health Potion I', 'c', None, [], '5.02', 'potion'),
        ('Mana Potion I', 'c', None, [], '5.02', 'potion'),
        ('Stamina Potion I', 'c', None, [], '5.02', 'potion'),
    ],
    'Virelune - Loot Buyer': [
        ('Health Potion II', 'c', None, [], '10.05', 'potion'),
        ('Mana Potion II', 'c', None, [], '10.05', 'potion'),
        ('Stamina Potion II', 'c', None, [], '10.05', 'potion'),
    ],
    'Mizunari Loot Buyer': [
        ('Health Potion II', 'c', None, [], '10.05', 'potion'),
        ('Mana Potion II', 'c', None, [], '10.05', 'potion'),
        ('Stamina Potion II', 'c', None, [], '10.05', 'potion'),
    ],
    'Cursed Ruins - Loot Buyer': [
        ('Health Potion II', 'c', None, [], '10.05', 'potion'),
        ('Mana Potion II', 'c', None, [], '10.05', 'potion'),
        ('Stamina Potion II', 'c', None, [], '10.05', 'potion'),
    ],
    'Cursed Ruins - Loot Buyer (2)': [
        ('Health Potion II', 'c', None, [], '10.05', 'potion'),
        ('Mana Potion II', 'c', None, [], '10.05', 'potion'),
        ('Stamina Potion II', 'c', None, [], '10.05', 'potion'),
    ],
    'Candelia': [
        ('Health Potion III', 'c', None, [], '15.07', 'potion'),
        ('Mana Potion III', 'c', None, [], '15.07', 'potion'),
        ('Stamina Potion III', 'c', None, [], '15.07', 'potion'),
    ],
    'Magical & Icy Loot Buyer': [
        ('Health Potion III', 'c', None, [], '15.07', 'potion'),
        ('Mana Potion III', 'c', None, [], '15.07', 'potion'),
        ('Stamina Potion III', 'c', None, [], '15.07', 'potion'),
    ],
}
SAME = {"Bandit's Gloves": "Gloves of the Bandit", "Bracelet of the Sylvan": "Bracelet of the Sylve", "Amulet of the Sylvan": "Amulet of the Sylve"}          # reference-map name -> in-game name
# material names used in game / by the reference map -> this site's ITEMS ids
MAT = {"Shark Carapace": "Shark Shell", "Soul of the Ruins": "Souls of the Ruins", "Sylve Shoot": "Sylvan Sprout",
       "Hard Glacial Hide": "Glacial Hardhide", "Essence of Gorbel": "Gorbel Essence", "Heart of Nymbrea": "Nymbréa's Heart",
       "Fragment of the Bear's Soul": "Bear Soul Fragment", "Small Purse": "Small Pouch", "Leaf Fragments": "Leaf Fragment", "Allium Flower": "Allium", "Sylve Sprout": "Sylvan Sprout"}
# item name -> official catalogue id (checked by hand: name keyword, level and set)
OID = {"Occult Hood": 1463, "Occult Robe": 1462, "Amulet of the Sylvan": 1288, "Amulet of the Sylve": 1288, "Gloves of the Bandit": 2040, "Bandit Hood": 1456, "Stolen Amulet": 1292, "Bandit Coin": 1455, "Bracelet of the Sylve": 1589, "Health Potion II": 2458, "Health Potion III": 2459, "Stamina Potion II": 2472, "Ring of the Leviathan": 2485, "Necklace of Aragorn": 1458, "Bracelet of Ice": 1596, "Gloves of the Wolves": 2044, "Occult Amulet": 1298, "Occult Ring": 2486, "Occult Bracelet": 1597, "Occult Gloves": 2045,   # 2026-11-02: official names matched by hand (Anneau de Léviathan, Collier de Aragorn, Capuche/Robe Occulte…; level may differ, the site shows the official one)
       "Training Sword": 2596, "Training Bow": 1566, "Training Crossbow": 1727, "Training Scythe": 1761, "Katana Training": 1762,
       "Training Magic Staff": 2569, "Unbound Grimoire": 1626, "Training Lantern": 1627, "Wild Grimoire": 1628,
       "Beginner's Tunic": 1334, "Beginner Leggings": 1335, "Beginner's Boots": 1336,
       "Bracelet of the Stags": 1594, "Gloves of the Stags": 2043, "Slimy Ring": 2478, "Gelatinous Bracelet": 1592,
       "Gelatinous Amulet": 1291, "Gelatinous Cloak": 1453, "Spider Bracelet": 1595, "Iron Ring": 2482, "Iron Bracelet": 1593,
       "Iron Gloves": 2042, "Iron Coin": 1457, "Iron Amulet": 1297, "Copper Ring": 2477, "Copper Bracelet": 1591,
       "Copper Gloves": 2039, "Copper Coin": 1452, "Copper Amulet": 1290, "Bracelet of the Sylvan": 1589, "Ring of the Sylve": 2473,
       "Skeleton Skull": 1450, "Belt of the Stags": 1460, "Ring of the Wolf": 2480, "Albal's Necklace": 1296,
       "Stolen Cloak": 1454, "Sticky Ring": 2479, "Occult Skull": 1461,
       # potions, crystals, fortifiers, keys (official name and level both match; checked by hand 2026-11-01)
       "Quality Health Potion I": 2463, "Quality Health Potion II": 2464, "Quality Health Potion III": 2465,
       "Health Potion I": 2457, "Stamina Potion I": 2471,
       "Healing Crystal": 1747, "Mana Crystal": 1749, "Stamina Crystal": 1750,
       "Quality Vitality Fortifier I": 1969, "Quality Ferocity Fortifier I": 1970, "Quality Knowledge Fortifier I": 1971,
       "Quality Endurance Fortifier I": 1972, "Quality Resistance Fortifier I": 1973, "Quality Patience Fortifier I": 1974,
       "Forest Key": 1821, "Key of the Fallen": 1823, "Key of Xal'Zirith": 1824}
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
        # "Starting Merchant / Alchemist" = either NPC makes it (user 2026-11-03): list it under each
        npc_list = [re.sub(r"^F1 - ", "", x.strip()) for x in loc.group(1).split(" / ")]
        mats = [[MAT.get(i, i), int(float(a))] for i, a in res if i != "Col"]
        col = next((str(int(float(a))) for i, a in res if i == "Col"), None)
        name = SAME.get(name, name)
        for npc in npc_list:
            npcs.setdefault(npc, []).append([OID.get(name), name, None, [m[:] for m in mats], col, None, cat, int(lv[1]) if lv else None, "ref"])

for npc, rows in SHOTS.items():                              # screenshots replace the same item, keep the rest
    old = {r[1]: r for r in npcs.get(npc, [])}
    new = [[OID.get(n), n, sec, [[MAT.get(m, m), q] for m, q in mats], cost, rar, cat, (old.get(n) or [None] * 8)[7], "shot"] for n, rar, sec, mats, cost, cat in rows]
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
