/* Floor 1 recipes by NPC (key = NPC name; matches npcs.js where that NPC is mapped). Built by tools/build_recipes.py.
   Row: [catalogueId|null, name, seconds|null, [[material, qty]], cost Col ("Free"; null = unknown), rarity|null, category, level, source]
   category: weapon / armor / acc / potion / key. source: "shot" = owner's in-game screenshot (wins), "ref" = reference map.
   Weapons and armour here are only the starter gear sold by the Starting Merchant; smiths' recipes still need screenshots. */
window.SAO_RECIPES = {
"Alchemist": {
"floor": 1,
"items": [
[
2463,
"Quality Health Potion I",
5,
[
[
"Sylvan Sprout",
8
],
[
"Allium",
8
]
],
"5",
"b",
"potion",
1,
"shot"
],
[
2464,
"Quality Health Potion II",
5,
[
[
"Sylvan Sprout",
8
],
[
"Bone Dust",
8
],
[
"Allium",
12
]
],
"7",
"b",
"potion",
5,
"shot"
],
[
2465,
"Quality Health Potion III",
5,
[
[
"Sylvan Sprout",
8
],
[
"Bone Dust",
8
],
[
"Ancestral Root",
1
],
[
"Allium",
16
]
],
"10",
"b",
"potion",
8,
"shot"
],
[
null,
"Quality Mana Potion I",
5,
[
[
"Souls of the Ruins",
8
],
[
"Allium",
8
]
],
"5",
"b",
"potion",
1,
"shot"
],
[
null,
"Quality Mana Potion II",
5,
[
[
"Souls of the Ruins",
8
],
[
"Bone Dust",
8
],
[
"Allium",
12
]
],
"7",
"b",
"potion",
5,
"shot"
],
[
null,
"Quality Mana Potion III",
5,
[
[
"Souls of the Ruins",
8
],
[
"Bone Dust",
8
],
[
"Ancestral Root",
1
],
[
"Allium",
16
]
],
"10",
"b",
"potion",
8,
"shot"
],
[
null,
"Quality Stamina Potion I",
5,
[
[
"Wheat",
8
],
[
"Allium",
8
]
],
"5",
"b",
"potion",
1,
"shot"
],
[
null,
"Quality Stamina Potion II",
5,
[
[
"Wheat",
8
],
[
"Bone Dust",
8
],
[
"Allium",
12
]
],
"7",
"b",
"potion",
5,
"shot"
],
[
null,
"Quality Stamina Potion III",
5,
[
[
"Wheat",
8
],
[
"Bone Dust",
8
],
[
"Ancestral Root",
1
],
[
"Allium",
16
]
],
"10",
"b",
"potion",
8,
"shot"
],
[
2457,
"Health Potion I",
null,
[],
"5.02",
"c",
"potion",
1,
"shot"
],
[
2458,
"Health Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
2459,
"Health Potion III",
null,
[],
"15.07",
"c",
"potion",
null,
"shot"
],
[
null,
"Mana Potion I",
null,
[],
"5.02",
"c",
"potion",
1,
"shot"
],
[
null,
"Mana Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
null,
"Mana Potion III",
null,
[],
"15.07",
"c",
"potion",
null,
"shot"
],
[
2471,
"Stamina Potion I",
null,
[],
"5.02",
"c",
"potion",
1,
"shot"
],
[
2472,
"Stamina Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
null,
"Stamina Potion III",
null,
[],
"15.07",
"c",
"potion",
null,
"shot"
]
]
},
"Bandit Accessories": {
"floor": 1,
"items": [
[
2040,
"Gloves of the Bandit",
15,
[
[
"Small Pouch",
16
]
],
"Free",
"c",
"acc",
5,
"shot"
],
[
1456,
"Bandit Hood",
15,
[
[
"Small Pouch",
16
]
],
"Free",
"c",
"acc",
5,
"shot"
],
[
1292,
"Stolen Amulet",
30,
[
[
"Small Pouch",
24
]
],
"Free",
"b",
"acc",
5,
"shot"
],
[
1454,
"Stolen Cloak",
30,
[
[
"Small Pouch",
24
]
],
"Free",
"b",
"acc",
5,
"shot"
],
[
1455,
"Bandit Coin",
30,
[
[
"Small Pouch",
24
]
],
"Free",
"b",
"acc",
5,
"shot"
]
]
},
"Bracelet of Ice": {
"floor": 1,
"items": [
[
1596,
"Bracelet of Ice",
null,
[
[
"Bear Soul Fragment",
3
],
[
"Glacial Hardhide",
24
]
],
"45",
null,
"acc",
8,
"ref"
]
]
},
"Candelia": {
"floor": 1,
"items": [
[
2459,
"Health Potion III",
null,
[],
"15.07",
"c",
"potion",
null,
"shot"
],
[
null,
"Mana Potion III",
null,
[],
"15.07",
"c",
"potion",
null,
"shot"
],
[
null,
"Stamina Potion III",
null,
[],
"15.07",
"c",
"potion",
null,
"shot"
]
]
},
"Copper Accessories": {
"floor": 1,
"items": [
[
2477,
"Copper Ring",
15,
[
[
"Copper Ingot",
1
]
],
"25",
"c",
"acc",
3,
"shot"
],
[
1591,
"Copper Bracelet",
15,
[
[
"Copper Ingot",
1
]
],
"25",
"c",
"acc",
3,
"shot"
],
[
2039,
"Copper Gloves",
15,
[
[
"Copper Ingot",
1
]
],
"25",
"c",
"acc",
3,
"shot"
],
[
1452,
"Copper Coin",
15,
[
[
"Copper Ingot",
1
]
],
"25",
"c",
"acc",
3,
"shot"
],
[
1290,
"Copper Amulet",
15,
[
[
"Copper Ingot",
1
],
[
"Copper String",
1
]
],
"25",
"c",
"acc",
3,
"shot"
]
]
},
"Corrupted Boar Accessories": {
"floor": 1,
"items": [
[
2475,
"Ring of the Boar",
15,
[
[
"Boar Hide",
8
],
[
"Corrupted Crystal",
8
]
],
"25",
"c",
"acc",
null,
"shot"
],
[
2038,
"Gloves of the Boar",
15,
[
[
"Boar Hide",
8
],
[
"Corrupted Crystal",
8
]
],
"25",
"c",
"acc",
null,
"shot"
],
[
1590,
"Bracelet of the Boar",
30,
[
[
"Boar Hide",
16
],
[
"Corrupted Crystal",
8
]
],
"28",
"b",
"acc",
null,
"shot"
],
[
1451,
"Belt of the Boar",
30,
[
[
"Boar Hide",
16
],
[
"Corrupted Crystal",
8
]
],
"28",
"b",
"acc",
null,
"shot"
]
]
},
"Crystallographer": {
"floor": 1,
"items": [
[
1747,
"Healing Crystal",
300,
[
[
"Ancestral Root",
16
],
[
"Magic Mycelium",
4
],
[
"Gorbel Essence",
1
],
[
"Frost Dust",
32
]
],
"50",
"a",
"potion",
10,
"shot"
],
[
1749,
"Mana Crystal",
300,
[
[
"Ancestral Root",
16
],
[
"Magic Mycelium",
4
],
[
"Gorbel Essence",
1
],
[
"Glacial Magic Shard",
32
]
],
"50",
"a",
"potion",
10,
"shot"
],
[
1750,
"Stamina Crystal",
300,
[
[
"Ancestral Root",
16
],
[
"Magic Mycelium",
4
],
[
"Gorbel Essence",
1
],
[
"Glacial Hardhide",
32
]
],
"50",
"a",
"potion",
10,
"shot"
]
]
},
"Cursed Ruins - Loot Buyer": {
"floor": 1,
"items": [
[
2458,
"Health Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
null,
"Mana Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
2472,
"Stamina Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
]
]
},
"Cursed Ruins - Loot Buyer (2)": {
"floor": 1,
"items": [
[
2458,
"Health Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
null,
"Mana Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
2472,
"Stamina Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
]
]
},
"Deer Accessories": {
"floor": 1,
"items": [
[
1594,
"Bracelet of the Stags",
30,
[
[
"Mountain Stag Hide",
12
]
],
"33",
"b",
"acc",
7,
"shot"
],
[
2043,
"Gloves of the Stags",
30,
[
[
"Mountain Stag Hide",
12
]
],
"33",
"b",
"acc",
7,
"shot"
]
]
},
"Elite Treant Accessories": {
"floor": 1,
"items": [
[
null,
"Elite Gloves",
15,
[
[
"Wolf Fur",
8
]
],
"25",
"c",
"acc",
3,
"shot"
],
[
null,
"Elite Amulet",
15,
[
[
"Oak String",
1
],
[
"Sylvan Bark",
8
]
],
"25",
"c",
"acc",
3,
"shot"
],
[
null,
"Elite Bracelet",
30,
[
[
"Oak Log",
4
],
[
"Titan Bark",
4
],
[
"Sylvan Bark",
8
]
],
"28",
"b",
"acc",
3,
"shot"
],
[
null,
"Elite Carapace",
30,
[
[
"Titan Bark",
8
],
[
"Sylvan Bark",
8
],
[
"Sylvan Sprout",
8
]
],
"28",
"b",
"acc",
3,
"shot"
]
]
},
"Fallen Labyrinth Dungeon Guard - Tolbana": {
"floor": 1,
"items": [
[
1823,
"Key of the Fallen",
60,
[
[
"Leaf Fragment",
8
],
[
"Cursed Cloth",
8
]
],
"20",
"b",
"key",
null,
"shot"
]
]
},
"Geldorak Dungeon Guard - Starting Town": {
"floor": 1,
"items": [
[
1821,
"Forest Key",
60,
[
[
"Sylvan Bark",
8
],
[
"Wood Heart",
4
],
[
"Magic Mycelium",
1
]
],
"10",
"c",
"key",
null,
"shot"
]
]
},
"Hanaka - Loot Buyer": {
"floor": 1,
"items": [
[
2457,
"Health Potion I",
null,
[],
"5.02",
"c",
"potion",
null,
"shot"
],
[
null,
"Mana Potion I",
null,
[],
"5.02",
"c",
"potion",
null,
"shot"
],
[
2471,
"Stamina Potion I",
null,
[],
"5.02",
"c",
"potion",
null,
"shot"
]
]
},
"Ice Golem Accessories": {
"floor": 1,
"items": [
[
null,
"Frozen Ring",
30,
[
[
"Glacial Hardhide",
12
],
[
"Frost Dust",
8
]
],
"33",
"b",
"acc",
7,
"shot"
],
[
null,
"Frozen Bracelet",
30,
[
[
"Glacial Hardhide",
16
]
],
"33",
"b",
"acc",
7,
"shot"
],
[
null,
"Frozen Gloves",
15,
[
[
"Glacial Hardhide",
12
]
],
"30",
"c",
"acc",
7,
"shot"
],
[
null,
"Frozen Amulet",
15,
[
[
"Glacial Hardhide",
8
],
[
"Birch String",
1
]
],
"30",
"c",
"acc",
7,
"shot"
]
]
},
"Ice Spirit Accessories": {
"floor": 1,
"items": [
[
null,
"Glacial Ring",
30,
[
[
"Glacial Magic Shard",
12
],
[
"Frost Dust",
8
]
],
"33",
"b",
"acc",
7,
"shot"
],
[
null,
"Glacial Antenna",
30,
[
[
"Glacial Magic Shard",
16
]
],
"33",
"b",
"acc",
7,
"shot"
],
[
null,
"Glacial Essence",
60,
[
[
"Frost Dust",
32
]
],
"40",
"a",
"acc",
7,
"shot"
],
[
null,
"Glacial Amulet",
30,
[
[
"Glacial Magic Shard",
12
],
[
"Birch String",
1
]
],
"33",
"b",
"acc",
7,
"shot"
]
]
},
"Iron Accessories": {
"floor": 1,
"items": [
[
2482,
"Iron Ring",
15,
[
[
"Iron Ingot",
1
]
],
"30",
"b",
"acc",
5,
"shot"
],
[
1593,
"Iron Bracelet",
15,
[
[
"Iron Ingot",
1
]
],
"30",
"b",
"acc",
5,
"shot"
],
[
2042,
"Iron Gloves",
15,
[
[
"Iron Ingot",
1
]
],
"30",
"b",
"acc",
5,
"shot"
],
[
1457,
"Iron Coin",
15,
[
[
"Iron Ingot",
1
]
],
"30",
"b",
"acc",
5,
"shot"
],
[
1297,
"Iron Amulet",
15,
[
[
"Iron Ingot",
1
],
[
"Iron String",
1
]
],
"30",
"b",
"acc",
5,
"shot"
]
]
},
"Key Blacksmith": {
"floor": 1,
"items": [
[
null,
"Kobold Key",
null,
[],
"5000",
null,
"key",
null,
"ref"
]
]
},
"Magical & Icy Loot Buyer": {
"floor": 1,
"items": [
[
2459,
"Health Potion III",
null,
[],
"15.07",
"c",
"potion",
null,
"shot"
],
[
null,
"Mana Potion III",
null,
[],
"15.07",
"c",
"potion",
null,
"shot"
],
[
null,
"Stamina Potion III",
null,
[],
"15.07",
"c",
"potion",
null,
"shot"
]
]
},
"Mizunari Loot Buyer": {
"floor": 1,
"items": [
[
2458,
"Health Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
null,
"Mana Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
2472,
"Stamina Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
]
]
},
"Necklace of Aragorn": {
"floor": 1,
"items": [
[
1458,
"Necklace of Aragorn",
null,
[
[
"Spider Venom",
3
],
[
"Oak String",
1
],
[
"Spider Thread",
20
]
],
"50",
null,
"acc",
8,
"ref"
]
]
},
"Nepenthes Accessories": {
"floor": 1,
"items": [
[
null,
"Ring of the Nepenthes",
15,
[
[
"Leaf Fragment",
8
],
[
"Corrupted Spore",
8
]
],
"25",
"c",
"acc",
5,
"shot"
],
[
null,
"Bracelet of the Nepenthes",
30,
[
[
"Leaf Fragment",
12
]
],
"28",
"b",
"acc",
5,
"shot"
],
[
null,
"Amulet of the Nepenthes",
15,
[
[
"Leaf Fragment",
4
],
[
"Corrupted Spore",
4
],
[
"Oak String",
1
]
],
"25",
"c",
"acc",
5,
"shot"
]
]
},
"Occult Merchant - Amulet": {
"floor": 1,
"items": [
[
1298,
"Occult Amulet",
null,
[],
"5000",
null,
"acc",
10,
"ref"
]
]
},
"Occult Merchant - Artifacts": {
"floor": 1,
"items": [
[
1461,
"Occult Skull",
null,
[],
"5000",
null,
"acc",
10,
"ref"
],
[
1462,
"Occult Robe",
null,
[],
"5000",
null,
"acc",
10,
"ref"
],
[
1463,
"Occult Hood",
null,
[],
"5000",
null,
"acc",
10,
"ref"
]
]
},
"Occult Merchant - Bracelet": {
"floor": 1,
"items": [
[
1597,
"Occult Bracelet",
null,
[],
"5000",
null,
"acc",
10,
"ref"
]
]
},
"Occult Merchant - Gloves": {
"floor": 1,
"items": [
[
2045,
"Occult Gloves",
null,
[],
"5000",
null,
"acc",
10,
"ref"
]
]
},
"Occult Merchant - Ring": {
"floor": 1,
"items": [
[
2486,
"Occult Ring",
null,
[],
"5000",
null,
"acc",
10,
"ref"
]
]
},
"PvP Purification Alchemist": {
"floor": 1,
"items": [
[
null,
"Purification Elixir",
15,
[
[
"Ancestral Root",
1
],
[
"Frost Dust",
1
],
[
"Bone Dust",
1
],
[
"Slime Core",
1
]
],
"Free",
"a",
"potion",
null,
"shot"
]
]
},
"Ring of the Leviathan": {
"floor": 1,
"items": [
[
2485,
"Ring of the Leviathan",
null,
[
[
"Shark Shell",
24
],
[
"Nymbréa's Heart",
3
],
[
"Iron Ingot",
1
]
],
"55",
null,
"acc",
7,
"ref"
]
]
},
"Secret Accessory Blacksmith": {
"floor": 1,
"items": [
[
2044,
"Gloves of the Wolves",
null,
[
[
"Wolf Fur",
32
],
[
"Wolf Fangs",
16
]
],
"40",
null,
"acc",
5,
"ref"
]
]
},
"Secret Deer Belt Merchant": {
"floor": 1,
"items": [
[
1460,
"Belt of the Stags",
null,
[
[
"Mountain Stag Hide",
20
]
],
"40",
null,
"acc",
7,
"ref"
]
]
},
"Secret Gelatinous Cloak": {
"floor": 1,
"items": [
[
1453,
"Gelatinous Cloak",
null,
[
[
"Stolen Cloak",
1
],
[
"Essence Slime",
1
],
[
"Tear Slime",
1
]
],
null,
null,
"acc",
7,
"ref"
]
]
},
"Secret Sticky Ring Merchant": {
"floor": 1,
"items": [
[
2479,
"Sticky Ring",
null,
[
[
"Slime Jelly",
12
],
[
"Gorbel Essence",
3
],
[
"Slime Core",
8
]
],
"35",
null,
"acc",
5,
"ref"
]
]
},
"Sewer Reshaper": {
"floor": 1,
"items": [
[
null,
"Slime Essence",
60,
[
[
"Slime Jelly",
16
],
[
"Gorbel Essence",
1
]
],
"20",
"a",
"other",
null,
"shot"
],
[
null,
"Slime Tear",
240,
[
[
"Slime Core",
16
]
],
"25",
"s",
"other",
null,
"shot"
]
]
},
"Shark Accessories": {
"floor": 1,
"items": [
[
null,
"Ring of the Shark",
15,
[
[
"Shark Shell",
8
]
],
"30",
"c",
"acc",
7,
"shot"
],
[
null,
"Shark Amulet",
15,
[
[
"Shark Shell",
8
],
[
"Birch String",
1
]
],
"30",
"c",
"acc",
7,
"shot"
],
[
null,
"Shark Fang",
30,
[
[
"Shark Shell",
12
],
[
"Wolf Fangs",
8
]
],
"33",
"b",
"acc",
7,
"shot"
],
[
null,
"Bracelet of the Shark",
30,
[
[
"Shark Shell",
12
],
[
"Iron Ingot",
1
]
],
"33",
"b",
"acc",
7,
"shot"
]
]
},
"Skeleton Accessories": {
"floor": 1,
"items": [
[
2474,
"Skeletal Ring",
15,
[
[
"Skeleton Bone",
8
],
[
"Souls of the Ruins",
8
]
],
"25",
"c",
"acc",
null,
"shot"
],
[
2037,
"Bony Gloves",
30,
[
[
"Skeleton Bone",
12
],
[
"Reinforced Skeleton Bone",
8
]
],
"28",
"b",
"acc",
null,
"shot"
],
[
1289,
"Skeletal Amulet",
15,
[
[
"Skeleton Bone",
4
],
[
"Souls of the Ruins",
4
],
[
"Oak String",
1
]
],
"25",
"c",
"acc",
null,
"shot"
]
]
},
"Skeleton Skull": {
"floor": 1,
"items": [
[
1450,
"Skeleton Skull",
60,
[
[
"Reinforced Skeleton Bone",
20
]
],
"35",
"a",
"acc",
8,
"shot"
]
]
},
"Slime Accessories": {
"floor": 1,
"items": [
[
2478,
"Slimy Ring",
15,
[
[
"Slime Jelly",
8
]
],
"25",
"c",
"acc",
4,
"shot"
],
[
1592,
"Gelatinous Bracelet",
30,
[
[
"Slime Jelly",
12
],
[
"Slime Core",
4
]
],
"28",
"b",
"acc",
4,
"shot"
],
[
1291,
"Gelatinous Amulet",
15,
[
[
"Oak String",
1
],
[
"Slime Jelly",
8
]
],
"25",
"c",
"acc",
4,
"shot"
]
]
},
"Spider Accessories": {
"floor": 1,
"items": [
[
null,
"Spider Ring",
15,
[
[
"Spider Cloth",
8
],
[
"Coal Ore",
8
]
],
"30",
"c",
"acc",
6,
"shot"
],
[
1595,
"Spider Bracelet",
15,
[
[
"Spider Cloth",
8
],
[
"Corrupted Spore",
8
]
],
"30",
"c",
"acc",
6,
"shot"
],
[
null,
"Spider Gloves",
15,
[
[
"Spider Cloth",
8
],
[
"Spider Thread",
8
]
],
"30",
"c",
"acc",
6,
"shot"
],
[
null,
"Spider Cloak",
30,
[
[
"Spider Cloth",
12
],
[
"Spider Thread",
8
]
],
"33",
"b",
"acc",
6,
"shot"
]
]
},
"Starting Merchant": {
"floor": 1,
"items": [
[
null,
"Teleportation Crystal",
null,
[],
"301.49",
"s",
"potion",
null,
"shot"
],
[
1957,
"Boar Meat",
null,
[],
"1.00",
"c",
"other",
null,
"shot"
],
[
2457,
"Health Potion I",
null,
[],
"5.02",
"c",
"potion",
1,
"shot"
],
[
null,
"Mana Potion I",
null,
[],
"5.02",
"c",
"potion",
1,
"shot"
],
[
2471,
"Stamina Potion I",
null,
[],
"5.02",
"c",
"potion",
1,
"shot"
],
[
1334,
"Beginner's Tunic",
null,
[],
"50.25",
"c",
"armor",
1,
"shot"
],
[
1335,
"Beginner's Leggings",
null,
[],
"50.25",
"c",
"armor",
1,
"shot"
],
[
1336,
"Beginner's Boots",
null,
[],
"50.25",
"c",
"armor",
1,
"shot"
],
[
2596,
"Training Sword",
null,
[],
"1.00",
"c",
"weapon",
1,
"shot"
],
[
1566,
"Training Bow",
null,
[],
"1.00",
"c",
"weapon",
1,
"shot"
],
[
1727,
"Training Crossbow",
null,
[],
"1.00",
"c",
"weapon",
1,
"shot"
],
[
1760,
"Training Dagger",
null,
[],
"1.00",
"c",
"weapon",
null,
"shot"
],
[
1761,
"Training Scythe",
null,
[],
"1.00",
"c",
"weapon",
1,
"shot"
],
[
1762,
"Training Katana",
null,
[],
"1.00",
"c",
"weapon",
1,
"shot"
],
[
2569,
"Training Magic Staff",
null,
[],
"1.00",
"c",
"weapon",
1,
"shot"
],
[
null,
"Training Scepter",
null,
[],
"1.00",
"c",
"weapon",
null,
"shot"
],
[
1626,
"Unbound Grimoire",
null,
[],
"1.00",
"c",
"weapon",
1,
"shot"
],
[
1627,
"Training Lantern",
null,
[],
"1.00",
"c",
"weapon",
1,
"shot"
],
[
1628,
"Wild Grimoire",
null,
[],
"1.00",
"c",
"weapon",
1,
"shot"
],
[
null,
"Training Quiver",
null,
[],
"1.00",
"c",
"weapon",
1,
"shot"
],
[
2534,
"Training Pavise",
null,
[],
"1.00",
"c",
"weapon",
null,
"shot"
],
[
2533,
"Training Buckler",
null,
[],
"1.00",
"c",
"weapon",
null,
"shot"
]
]
},
"Starting Town - Tools": {
"floor": 1,
"items": [
[
2703,
"Chipped Axe",
null,
[],
"50.25",
"c",
"other",
null,
"shot"
],
[
2691,
"Cracked Pickaxe",
null,
[],
"50.25",
"c",
"other",
null,
"shot"
],
[
null,
"Twisted Hoe",
null,
[],
"50.25",
"c",
"other",
null,
"shot"
],
[
2709,
"Wooden Fishing Rod",
null,
[],
"50.25",
"c",
"other",
null,
"shot"
]
]
},
"Sylve Accessories": {
"floor": 1,
"items": [
[
1589,
"Bracelet of the Sylve",
15,
[
[
"Oak Log",
8
],
[
"Magic Wood Shard",
8
]
],
"25",
"c",
"acc",
3,
"shot"
],
[
1288,
"Amulet of the Sylve",
15,
[
[
"Magic Wood Shard",
8
],
[
"Oak String",
1
]
],
"25",
"c",
"acc",
3,
"shot"
],
[
2473,
"Ring of the Sylve",
30,
[
[
"Magic Wood Shard",
8
],
[
"Allium",
8
],
[
"Oak Log",
4
],
[
"Wood Heart",
1
]
],
"28",
"b",
"acc",
3,
"shot"
]
]
},
"The Assistant": {
"floor": 1,
"items": [
[
1969,
"Quality Vitality Fortifier I",
10,
[
[
"Magic Wood Shard",
16
],
[
"Wood Heart",
2
],
[
"Slime Core",
2
]
],
"10",
"b",
"potion",
8,
"shot"
],
[
1970,
"Quality Ferocity Fortifier I",
10,
[
[
"Wolf Fangs",
16
],
[
"Wheat Flower",
2
],
[
"Albal's Fangs",
1
]
],
"10",
"b",
"potion",
8,
"shot"
],
[
1971,
"Quality Knowledge Fortifier I",
10,
[
[
"Allium",
16
],
[
"Lavender",
2
],
[
"Refined Allium",
1
]
],
"10",
"b",
"potion",
8,
"shot"
],
[
1972,
"Quality Endurance Fortifier I",
10,
[
[
"Wheat",
16
],
[
"Wheat Leaves",
2
],
[
"Refined Wheat",
1
]
],
"10",
"b",
"potion",
8,
"shot"
],
[
1973,
"Quality Resistance Fortifier I",
10,
[
[
"Glacial Hardhide",
16
],
[
"Wisteria",
2
],
[
"Ancestral Root",
2
]
],
"10",
"b",
"potion",
8,
"shot"
],
[
1974,
"Quality Patience Fortifier I",
10,
[
[
"Souls of the Ruins",
16
],
[
"Glacial Magic Shard",
8
],
[
"Bear Soul Fragment",
1
]
],
"10",
"b",
"potion",
8,
"shot"
]
]
},
"Vallhat - Loot Buyer": {
"floor": 1,
"items": [
[
2457,
"Health Potion I",
null,
[],
"5.02",
"c",
"potion",
null,
"shot"
],
[
null,
"Mana Potion I",
null,
[],
"5.02",
"c",
"potion",
null,
"shot"
],
[
2471,
"Stamina Potion I",
null,
[],
"5.02",
"c",
"potion",
null,
"shot"
]
]
},
"Virelune - Loot Buyer": {
"floor": 1,
"items": [
[
2458,
"Health Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
null,
"Mana Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
],
[
2472,
"Stamina Potion II",
null,
[],
"10.05",
"c",
"potion",
null,
"shot"
]
]
},
"Wolf Accessories": {
"floor": 1,
"items": [
[
2480,
"Ring of the Wolf",
null,
[
[
"Wolf Fur",
16
],
[
"Oak Log",
8
]
],
"33",
null,
"acc",
3,
"ref"
],
[
1296,
"Albal's Necklace",
null,
[
[
"Birch String",
1
],
[
"Albal's Fangs",
4
]
],
"33",
null,
"acc",
3,
"ref"
]
]
},
"Xal'Zirith Dungeon Guard - Candelia": {
"floor": 1,
"items": [
[
1824,
"Key of Xal'Zirith",
60,
[
[
"Spider Cloth",
16
],
[
"Spider Thread",
16
]
],
"15",
"b",
"key",
null,
"shot"
]
]
}
};
