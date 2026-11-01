/* Floor 1 recipes by NPC (key = NPC name; matches npcs.js where that NPC is mapped). Built by tools/build_recipes.py.
   Row: [catalogueId|null, name, seconds|null, [[material, qty]], cost Col ("Free"; null = unknown), rarity|null, category, level, source]
   category: weapon / armor / acc / potion / key. source: "shot" = owner's in-game screenshot (wins), "ref" = reference map.
   Weapons and armour here are only the starter gear sold by the Starting Merchant; smiths' recipes still need screenshots. */
window.SAO_RECIPES = {
"Alchemist": {
"floor": 1,
"items": [
[
null,
"Quality Health Potion I",
null,
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
null,
"potion",
1,
"ref"
],
[
null,
"Quality Health Potion II",
null,
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
null,
"potion",
5,
"ref"
],
[
null,
"Quality Health Potion III",
null,
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
null,
"potion",
8,
"ref"
],
[
null,
"Quality Mana Potion I",
null,
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
null,
"potion",
1,
"ref"
],
[
null,
"Quality Mana Potion II",
null,
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
null,
"potion",
5,
"ref"
],
[
null,
"Quality Mana Potion III",
null,
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
null,
"potion",
8,
"ref"
],
[
null,
"Quality Stamina Potion I",
null,
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
null,
"potion",
1,
"ref"
],
[
null,
"Quality Stamina Potion II",
null,
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
null,
"potion",
5,
"ref"
],
[
null,
"Quality Stamina Potion III",
null,
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
null,
"potion",
8,
"ref"
]
]
},
"Bandit Accessories": {
"floor": 1,
"items": [
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
null,
"acc",
5,
"shot"
],
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
null,
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
null,
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
null,
"acc",
5,
"shot"
],
[
1454,
"Stolen Cloak",
null,
[
[
"Small Pouch",
24
]
],
null,
null,
"acc",
5,
"ref"
]
]
},
"Bracelet of Ice": {
"floor": 1,
"items": [
[
null,
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
"Copper Accessories": {
"floor": 1,
"items": [
[
2477,
"Copper Ring",
null,
[
[
"Copper Ingot",
1
]
],
"25",
null,
"acc",
3,
"ref"
],
[
1591,
"Copper Bracelet",
null,
[
[
"Copper Ingot",
1
]
],
"25",
null,
"acc",
3,
"ref"
],
[
2039,
"Copper Gloves",
null,
[
[
"Copper Ingot",
1
]
],
"25",
null,
"acc",
3,
"ref"
],
[
1452,
"Copper Coin",
null,
[
[
"Copper Ingot",
1
]
],
"25",
null,
"acc",
3,
"ref"
],
[
1290,
"Copper Amulet",
null,
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
null,
"acc",
3,
"ref"
]
]
},
"Crystallographer": {
"floor": 1,
"items": [
[
null,
"Healing Crystal",
null,
[
[
"Ancestral Root",
16
],
[
"Frost Dust",
32
],
[
"Magic Mycelium",
4
],
[
"Gorbel Essence",
1
]
],
"50",
null,
"potion",
10,
"ref"
],
[
null,
"Mana Crystal",
null,
[
[
"Ancestral Root",
16
],
[
"Glacial Magic Shard",
32
],
[
"Magic Mycelium",
4
],
[
"Gorbel Essence",
1
]
],
"50",
null,
"potion",
10,
"ref"
],
[
null,
"Stamina Crystal",
null,
[
[
"Ancestral Root",
16
],
[
"Glacial Hardhide",
32
],
[
"Magic Mycelium",
4
],
[
"Gorbel Essence",
1
]
],
"50",
null,
"potion",
10,
"ref"
]
]
},
"Deer Accessories": {
"floor": 1,
"items": [
[
1594,
"Bracelet of the Stags",
null,
[
[
"Mountain Stag Hide",
12
]
],
"33",
null,
"acc",
7,
"ref"
],
[
2043,
"Gloves of the Stags",
null,
[
[
"Mountain Stag Hide",
12
]
],
"33",
null,
"acc",
7,
"ref"
]
]
},
"Elite Treant Accessories": {
"floor": 1,
"items": [
[
null,
"Elite Gloves",
null,
[
[
"Wolf Fur",
8
]
],
"25",
null,
"acc",
3,
"ref"
],
[
null,
"Elite Amulet",
null,
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
null,
"acc",
3,
"ref"
],
[
null,
"Elite Bracelet",
null,
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
null,
"acc",
3,
"ref"
],
[
null,
"Elite Carapace",
null,
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
null,
"acc",
3,
"ref"
]
]
},
"Fallen Labyrinth Dungeon Guard - Tolbana": {
"floor": 1,
"items": [
[
null,
"Key of the Fallen",
null,
[
[
"Cursed Cloth",
8
],
[
"Leaf Fragment",
8
]
],
"20",
null,
"key",
null,
"ref"
]
]
},
"Geldorak Dungeon Guard - Starting Town": {
"floor": 1,
"items": [
[
null,
"Forest Key",
null,
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
null,
"key",
null,
"ref"
]
]
},
"Ice Golem Accessories": {
"floor": 1,
"items": [
[
null,
"Frozen Ring",
null,
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
null,
"acc",
7,
"ref"
],
[
null,
"Frozen Bracelet",
null,
[
[
"Glacial Hardhide",
16
]
],
"33",
null,
"acc",
7,
"ref"
],
[
null,
"Frozen Gloves",
null,
[
[
"Glacial Hardhide",
12
]
],
"30",
null,
"acc",
7,
"ref"
],
[
null,
"Frozen Amulet",
null,
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
null,
"acc",
7,
"ref"
]
]
},
"Ice Spirit Accessories": {
"floor": 1,
"items": [
[
null,
"Glacial Ring",
null,
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
null,
"acc",
7,
"ref"
],
[
null,
"Glacial Antenna",
null,
[
[
"Glacial Magic Shard",
16
]
],
"33",
null,
"acc",
7,
"ref"
],
[
null,
"Glacial Essence",
null,
[
[
"Frost Dust",
32
]
],
"40",
null,
"acc",
7,
"ref"
],
[
null,
"Glacial Amulet",
null,
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
null,
"acc",
7,
"ref"
]
]
},
"Iron Accessories": {
"floor": 1,
"items": [
[
2482,
"Iron Ring",
null,
[
[
"Iron Ingot",
1
]
],
"30",
null,
"acc",
5,
"ref"
],
[
1593,
"Iron Bracelet",
null,
[
[
"Iron Ingot",
1
]
],
"30",
null,
"acc",
5,
"ref"
],
[
2042,
"Iron Gloves",
null,
[
[
"Iron Ingot",
1
]
],
"30",
null,
"acc",
5,
"ref"
],
[
1457,
"Iron Coin",
null,
[
[
"Iron Ingot",
1
]
],
"30",
null,
"acc",
5,
"ref"
],
[
1297,
"Iron Amulet",
null,
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
null,
"acc",
5,
"ref"
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
"Necklace of Aragorn": {
"floor": 1,
"items": [
[
null,
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
null,
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
null,
"acc",
5,
"ref"
],
[
null,
"Bracelet of the Nepenthes",
null,
[
[
"Leaf Fragment",
12
]
],
"28",
null,
"acc",
5,
"ref"
],
[
null,
"Amulet of the Nepenthes",
null,
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
null,
"acc",
5,
"ref"
]
]
},
"Occult Merchant - Amulet": {
"floor": 1,
"items": [
[
null,
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
null,
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
null,
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
null,
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
null,
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
null,
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
null,
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
null,
null,
"potion",
null,
"ref"
]
]
},
"Ring of the Leviathan": {
"floor": 1,
"items": [
[
null,
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
null,
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
"Shark Accessories": {
"floor": 1,
"items": [
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
],
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
]
]
},
"Skeleton Skull": {
"floor": 1,
"items": [
[
1450,
"Skeleton Skull",
null,
[
[
"Reinforced Skeleton Bone",
20
]
],
"35",
null,
"acc",
8,
"ref"
]
]
},
"Slime Accessories": {
"floor": 1,
"items": [
[
2478,
"Slimy Ring",
null,
[
[
"Slime Jelly",
8
]
],
"25",
null,
"acc",
4,
"ref"
],
[
1592,
"Gelatinous Bracelet",
null,
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
null,
"acc",
4,
"ref"
],
[
1291,
"Gelatinous Amulet",
null,
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
null,
"acc",
4,
"ref"
]
]
},
"Spider Accessories": {
"floor": 1,
"items": [
[
null,
"Spider Ring",
null,
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
null,
"acc",
6,
"ref"
],
[
1595,
"Spider Bracelet",
null,
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
null,
"acc",
6,
"ref"
],
[
null,
"Spider Gloves",
null,
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
null,
"acc",
6,
"ref"
],
[
null,
"Spider Cloak",
null,
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
null,
"acc",
6,
"ref"
]
]
},
"Starting Merchant": {
"floor": 1,
"items": [
[
2596,
"Training Sword",
null,
[],
"1",
null,
"weapon",
1,
"ref"
],
[
1566,
"Training Bow",
null,
[],
"1",
null,
"weapon",
1,
"ref"
],
[
1727,
"Training Crossbow",
null,
[],
"1",
null,
"weapon",
1,
"ref"
],
[
1761,
"Training Scythe",
null,
[],
"1",
null,
"weapon",
1,
"ref"
],
[
1762,
"Katana Training",
null,
[],
"1",
null,
"weapon",
1,
"ref"
],
[
2569,
"Training Magic Staff",
null,
[],
"1",
null,
"weapon",
1,
"ref"
],
[
1626,
"Unbound Grimoire",
null,
[],
"1",
null,
"weapon",
1,
"ref"
],
[
1627,
"Training Lantern",
null,
[],
"1",
null,
"weapon",
1,
"ref"
],
[
1628,
"Wild Grimoire",
null,
[],
"1",
null,
"weapon",
1,
"ref"
],
[
null,
"Training Quiver",
null,
[],
"1",
null,
"weapon",
1,
"ref"
],
[
1334,
"Beginner's Tunic",
null,
[],
"50",
null,
"armor",
1,
"ref"
],
[
1335,
"Beginner Leggings",
null,
[],
"50",
null,
"armor",
1,
"ref"
],
[
1336,
"Beginner's Boots",
null,
[],
"50",
null,
"armor",
1,
"ref"
],
[
null,
"Teleportation Crystal",
null,
[],
"301",
null,
"potion",
null,
"ref"
]
]
},
"Starting Merchant / Alchemist": {
"floor": 1,
"items": [
[
null,
"Health Potion I",
null,
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
null,
"potion",
1,
"ref"
],
[
null,
"Mana Potion I",
null,
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
null,
"potion",
1,
"ref"
],
[
null,
"Stamina Potion I",
null,
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
null,
"potion",
1,
"ref"
]
]
},
"Sylve Accessories": {
"floor": 1,
"items": [
[
1589,
"Bracelet of the Sylvan",
null,
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
null,
null,
"acc",
3,
"ref"
],
[
null,
"Amulet of the Sylvan",
null,
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
null,
null,
"acc",
3,
"ref"
],
[
2473,
"Ring of the Sylve",
null,
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
null,
null,
"acc",
3,
"ref"
]
]
},
"The Assistant": {
"floor": 1,
"items": [
[
null,
"Quality Vitality Fortifier I",
null,
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
null,
"potion",
8,
"ref"
],
[
null,
"Quality Ferocity Fortifier I",
null,
[
[
"Wolf Fangs",
16
],
[
"Wheat",
2
],
[
"Albal's Fangs",
1
]
],
"10",
null,
"potion",
8,
"ref"
],
[
null,
"Quality Knowledge Fortifier I",
null,
[
[
"Allium",
17
],
[
"Wheat",
2
]
],
"10",
null,
"potion",
8,
"ref"
],
[
null,
"Quality Endurance Fortifier I",
null,
[
[
"Wheat",
19
]
],
"10",
null,
"potion",
8,
"ref"
],
[
null,
"Quality Resistance Fortifier I",
null,
[
[
"Glacial Hardhide",
16
],
[
"Allium",
2
],
[
"Ancestral Root",
2
]
],
"10",
null,
"potion",
8,
"ref"
],
[
null,
"Quality Patience Fortifier I",
null,
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
null,
"potion",
8,
"ref"
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
null,
"Key of Xal'Zirith",
null,
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
null,
"key",
null,
"ref"
]
]
}
};
