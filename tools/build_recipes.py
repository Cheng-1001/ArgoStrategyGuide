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
    # 2026-11-12 (in24 11/8 18:13): Secret Leviathan Ring window — LEGENDARY, 5 min, materials same as the reference map
    'Ring of the Leviathan': [('Ring of the Leviathan', 's', 300, [['Shark Carapace', 24], ['Heart of Nymbrea', 3], ['Iron Ingot', 1]], '55', 'acc')],
    # 2026-11-05 evening batch (in12): Skeleton Accessories' full list, and the Skeleton Skull secret smith (window title "Secret Skeleton Skull")
    # 2026-11-07 batch (in14): new smith in the Boar Zone, window title "Corrupted Boar Accessories" (not in the reference map)
    'Corrupted Boar Accessories': [
        ('Ring of the Boar', 'c', 15, [['Boar Hide', 8], ['Corrupted Crystal', 8]], '25', 'acc'),
        ('Gloves of the Boar', 'c', 15, [['Boar Hide', 8], ['Corrupted Crystal', 8]], '25', 'acc'),
        ('Bracelet of the Boar', 'b', 30, [['Boar Hide', 16], ['Corrupted Crystal', 8]], '28', 'acc'),
        ('Belt of the Boar', 'b', 30, [['Boar Hide', 16], ['Corrupted Crystal', 8]], '28', 'acc'),
    ],
    'Wolf Accessories': [   # 2026-11-07 03:45 (in15): same as the reference map, plus rarity / time
        ('Ring of the Wolf', 'b', 30, [['Wolf Fur', 16], ['Oak Log', 8]], '33', 'acc'),
        ("Albal's Necklace", 'b', 30, [['Birch String', 1], ['Fangs of Albal', 4]], '33', 'acc'),
    ],
    'Skeleton Accessories': [
        ('Skeletal Ring', 'c', 15, [['Skeleton Bone', 8], ['Soul of the Ruins', 8]], '25', 'acc'),
        ('Bony Gloves', 'b', 30, [['Skeleton Bone', 12], ['Reinforced Skeleton Bone', 8]], '28', 'acc'),
        ('Skeletal Amulet', 'c', 15, [['Skeleton Bone', 4], ['Soul of the Ruins', 4], ['Oak String', 1]], '25', 'acc'),
    ],
    "Xal'Zirith Dungeon Guard - Candelia": [
        ("Key of Xal'Zirith", 'b', 60, [['Spider Cloth', 16], ['Spider Thread', 16]], '15', 'key'),
    ],
    'Skeleton Skull': [
        ('Skeleton Skull', 'a', 60, [['Reinforced Skeleton Bone', 20]], '35', 'acc'),
    ],
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
    # 2026-11-08 站長截圖：隱藏野狼手套（狼之谷冰窖 X 2493 Y 70 Z 3702）、隱藏雄鹿腰帶（雪原土洞 X 3653 Y 132 Z 1328），都只有一個配方
    'Secret Accessory Blacksmith': [
        ('Gloves of the Wolves', 'a', 60, [['Wolf Fur', 32], ['Wolf Fangs', 16]], '40', 'acc'),
    ],
    'Secret Deer Belt Merchant': [
        ('Belt of the Stags', 'a', 60, [['Mountain Stag Hide', 20]], '40', 'acc'),
    ],
    # 2026-11-07 站長截圖（中文介面工坊，NPC 中文名「隱藏黏液戒指」）：黏液之戒 EPIC 1m 35
    'Secret Sticky Ring Merchant': [
        ('Sticky Ring', 'a', 60, [['Slime Jelly', 12], ['Essence of Gorbel', 3], ['Slime Core', 8]], '35', 'acc'),
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
    # 2026-11-03 22:38-23:18 batch (Starting Town shops, Tolbana dungeon guard)
    'Starting Merchant': [                                     # Buy tab, 4 pages, all sold for Col (Potion I is bought here, not crafted)
        ('Teleportation Crystal', 's', None, [], '301.49', 'other'),    # a teleport item, not a potion (2026-11-07 audit)
        ('Boar Meat', 'c', None, [], '1.00', 'other'),
        ('Health Potion I', 'c', None, [], '5.02', 'potion'),
        ('Mana Potion I', 'c', None, [], '5.02', 'potion'),
        ('Stamina Potion I', 'c', None, [], '5.02', 'potion'),
        ("Beginner's Tunic", 'c', None, [], '50.25', 'armor'),
        ("Beginner's Leggings", 'c', None, [], '50.25', 'armor'),
        ("Beginner's Boots", 'c', None, [], '50.25', 'armor'),
        ('Training Sword', 'c', None, [], '1.00', 'weapon'),
        ('Training Bow', 'c', None, [], '1.00', 'weapon'),
        ('Training Crossbow', 'c', None, [], '1.00', 'weapon'),
        ('Training Dagger', 'c', None, [], '1.00', 'weapon'),
        ('Training Scythe', 'c', None, [], '1.00', 'weapon'),
        ('Training Katana', 'c', None, [], '1.00', 'weapon'),
        ('Training Magic Staff', 'c', None, [], '1.00', 'weapon'),
        ('Training Scepter', 'c', None, [], '1.00', 'weapon'),
        ('Unbound Grimoire', 'c', None, [], '1.00', 'weapon'),
        ('Training Lantern', 'c', None, [], '1.00', 'weapon'),
        ('Wild Grimoire', 'c', None, [], '1.00', 'weapon'),
        ('Training Quiver', 'c', None, [], '1.00', 'weapon'),
        ('Training Pavise', 'c', None, [], '1.00', 'weapon'),
        ('Training Buckler', 'c', None, [], '1.00', 'weapon'),
        # page 4 also lists a second "Training Dagger" (訓練用短劍: thin blade, assassin, 爆擊率 +0.5%; in16 15:02:51, in3 22:39:23) and a second
        # "Training Lantern" (the shaman one; page 3 is the mage one, in16 15:02:47 vs 15:02:39). Same English names in the game: "(2)" on the site.
        ('Training Dagger (2)', 'c', None, [], '1.00', 'weapon'),
        ('Training Lantern (2)', 'c', None, [], '1.00', 'weapon'),
    ],
    # Occult Merchants (owner's screenshots 2026-11-07 02:09-03:18): Buy tab, LEGENDARY, 5 024.91 Col (the item's Obtainable line says 5000 Cols)
    'Occult Merchant - Amulet': [('Occult Amulet', 's', None, [], '5024.91', 'acc')],
    'Occult Merchant - Bracelet': [('Occult Bracelet', 's', None, [], '5024.91', 'acc')],
    'Occult Merchant - Ring': [('Occult Ring', 's', None, [], '5024.91', 'acc')],
    'Occult Merchant - Gloves': [('Occult Gloves', 's', None, [], '5024.91', 'acc')],
    'Occult Merchant - Artifacts': [('Occult Skull', 's', None, [], '5024.91', 'acc'), ('Occult Robe', 's', None, [], '5024.91', 'acc'), ('Occult Hood', 's', None, [], '5024.91', 'acc')],
    'Starting Town - Tools': [                                 # in game "F1 - Starting City - Tools", Buy tab
        ('Chipped Axe', 'c', None, [], '50.25', 'other'),
        ('Cracked Pickaxe', 'c', None, [], '50.25', 'other'),
        ('Twisted Hoe', 'c', None, [], '50.25', 'other'),
        ('Wooden Fishing Rod', 'c', None, [], '50.25', 'other'),
    ],
    'Alchemist': [                                             # "F1 Alchemist - Starting City", Recipes tab 2 pages: only the Quality potions (each makes ×3)
        ('Quality Health Potion I', 'b', 5, [['Sylve Sprout', 8], ['Allium Flower', 8]], '5', 'potion'),
        ('Quality Health Potion II', 'b', 5, [['Sylve Sprout', 8], ['Bone Dust', 8], ['Allium Flower', 12]], '7', 'potion'),
        ('Quality Health Potion III', 'b', 5, [['Sylve Sprout', 8], ['Bone Dust', 8], ['Ancestral Root', 1], ['Allium Flower', 16]], '10', 'potion'),
        ('Quality Mana Potion I', 'b', 5, [['Soul of the Ruins', 8], ['Allium Flower', 8]], '5', 'potion'),
        ('Quality Mana Potion II', 'b', 5, [['Soul of the Ruins', 8], ['Bone Dust', 8], ['Allium Flower', 12]], '7', 'potion'),
        ('Quality Mana Potion III', 'b', 5, [['Soul of the Ruins', 8], ['Bone Dust', 8], ['Ancestral Root', 1], ['Allium Flower', 16]], '10', 'potion'),
        ('Quality Stamina Potion I', 'b', 5, [['Wheat', 8], ['Allium Flower', 8]], '5', 'potion'),
        ('Quality Stamina Potion II', 'b', 5, [['Wheat', 8], ['Bone Dust', 8], ['Allium Flower', 12]], '7', 'potion'),
        ('Quality Stamina Potion III', 'b', 5, [['Wheat', 8], ['Bone Dust', 8], ['Ancestral Root', 1], ['Allium Flower', 16]], '10', 'potion'),

        # Buy tab (owner's screenshot 2026-11-04, 2 pages): Potion I-III sold for Col, same prices as the loot buyers
        ('Health Potion I', 'c', None, [], '5.02', 'potion'),
        ('Health Potion II', 'c', None, [], '10.05', 'potion'),
        ('Health Potion III', 'c', None, [], '15.07', 'potion'),
        ('Mana Potion I', 'c', None, [], '5.02', 'potion'),
        ('Mana Potion II', 'c', None, [], '10.05', 'potion'),
        ('Mana Potion III', 'c', None, [], '15.07', 'potion'),
        ('Stamina Potion I', 'c', None, [], '5.02', 'potion'),
        ('Stamina Potion II', 'c', None, [], '10.05', 'potion'),
        ('Stamina Potion III', 'c', None, [], '15.07', 'potion'),
    ],
    'The Assistant': [                                         # "F1 The Assistant - Starting City"
        ('Quality Vitality Fortifier I', 'b', 10, [['Magic Wood Shard', 16], ['Wood Heart', 2], ['Slime Core', 2]], '10', 'potion'),
        ('Quality Ferocity Fortifier I', 'b', 10, [['Wolf Fangs', 16], ['Wheat Flower', 2], ['Fangs of Albal', 1]], '10', 'potion'),
        ('Quality Knowledge Fortifier I', 'b', 10, [['Allium Flower', 16], ['Lavender', 2], ['Refined Allium', 1]], '10', 'potion'),
        ('Quality Endurance Fortifier I', 'b', 10, [['Wheat', 16], ['Wheat Leaves', 2], ['Refined Wheat', 1]], '10', 'potion'),
        ('Quality Resistance Fortifier I', 'b', 10, [['Hard Glacial Hide', 16], ['Wisteria', 2], ['Ancestral Root', 2]], '10', 'potion'),
        ('Quality Patience Fortifier I', 'b', 10, [['Soul of the Ruins', 16], ['Glacial Magic Shard', 8], ["Fragment of the Bear's Soul", 1]], '10', 'potion'),
    ],
    'Crystallographer': [
        ('Healing Crystal', 'a', 300, [['Ancestral Root', 16], ['Magic Mycelium', 4], ['Essence of Gorbel', 1], ['Frost Dust', 32]], '50', 'potion'),
        ('Mana Crystal', 'a', 300, [['Ancestral Root', 16], ['Magic Mycelium', 4], ['Essence of Gorbel', 1], ['Glacial Magic Shard', 32]], '50', 'potion'),
        ('Stamina Crystal', 'a', 300, [['Ancestral Root', 16], ['Magic Mycelium', 4], ['Essence of Gorbel', 1], ['Hard Glacial Hide', 32]], '50', 'potion'),
    ],
    'PvP Purification Alchemist': [
        ('Purification Elixir', 'a', 15, [['Ancestral Root', 1], ['Frost Dust', 1], ['Bone Dust', 1], ['Slime Core', 1]], 'Free', 'potion'),
    ],
    'Copper Accessories': [(n, 'c', 15, [['Copper Ingot', 1]] + ([['Copper String', 1]] if 'Amulet' in n else []), '25', 'acc')
                           for n in ('Copper Ring', 'Copper Bracelet', 'Copper Gloves', 'Copper Coin', 'Copper Amulet')],
    'Iron Accessories': [(n, 'b', 15, [['Iron Ingot', 1]] + ([['Iron String', 1]] if 'Amulet' in n else []), '30', 'acc')
                         for n in ('Iron Ring', 'Iron Bracelet', 'Iron Gloves', 'Iron Coin', 'Iron Amulet')],
    'Fallen Labyrinth Dungeon Guard - Tolbana': [
        ('Key of the Fallen', 'b', 60, [['Leaf Fragments', 8], ['Cursed Cloth', 8]], '20', 'key'),
    ],
}
# the screenshot showed the NPC's whole list: drop reference-map rows the game no longer has
FULL = {'Secret Accessory Blacksmith', 'Secret Deer Belt Merchant', 'Secret Sticky Ring Merchant', 'Occult Merchant - Amulet', 'Occult Merchant - Bracelet', 'Occult Merchant - Ring', 'Occult Merchant - Gloves', 'Occult Merchant - Artifacts', 'Wolf Accessories', 'Corrupted Boar Accessories', "Xal'Zirith Dungeon Guard - Candelia", 'Skeleton Accessories', 'Skeleton Skull', 'Starting Merchant', 'Starting Town - Tools', 'Alchemist', 'The Assistant', 'Crystallographer', 'Copper Accessories', 'Iron Accessories'}
SAME = {"Katana Training": "Training Katana", "Beginner Leggings": "Beginner's Leggings", "Bandit's Gloves": "Gloves of the Bandit", "Bracelet of the Sylvan": "Bracelet of the Sylve", "Amulet of the Sylvan": "Amulet of the Sylve"}          # reference-map name -> in-game name
# material names used in game / by the reference map -> this site's ITEMS ids
MAT = {"Sylve Shoot": "Sylve Sprout", "Sylvan Sprout": "Sylve Sprout", "Essence Slime": "Slime Essence", "Tear Slime": "Slime Tear"}   # reference-map name -> in-game name. 2026-11-07 merchant audit: the other
# entries used to turn the game's names into old wiki item names (Shark Carapace -> Shark Shell, Small Purse -> Small Pouch, Leaf Fragments ->
# Leaf Fragment…); the site's items now use the game names (old names resolve through ITEM_OLD), so materials keep the game spelling.
# item name -> official catalogue id (checked by hand: name keyword, level and set)
OID = {"Ring of the Boar": 2475, "Gloves of the Boar": 2038, "Bracelet of the Boar": 1590, "Belt of the Boar": 1451,   # 2026-11-07: Anneau/Gants/Bracelet/Ceinture de Sanglier (name, level-3 set; game level 1)
       "Occult Hood": 1463, "Occult Robe": 1462, "Amulet of the Sylvan": 1288, "Amulet of the Sylve": 1288, "Gloves of the Bandit": 2040, "Bandit Hood": 1456, "Stolen Amulet": 1292, "Bandit Coin": 1455, "Bracelet of the Sylve": 1589, "Health Potion II": 2458, "Health Potion III": 2459, "Stamina Potion II": 2472, "Ring of the Leviathan": 2485, "Necklace of Aragorn": 1458, "Bracelet of Ice": 1596, "Gloves of the Wolves": 2044, "Occult Amulet": 1298, "Occult Ring": 2486, "Occult Bracelet": 1597, "Occult Gloves": 2045,   # 2026-11-02: official names matched by hand (Anneau de Léviathan, Collier de Aragorn, Capuche/Robe Occulte…; level may differ, the site shows the official one)
       "Training Sword": 2596, "Training Bow": 1566, "Training Crossbow": 1727, "Training Scythe": 1761, "Training Katana": 1762, "Training Dagger": 1760, "Training Pavise": 2534, "Training Buckler": 2533,
       "Boar Meat": 1957, "Chipped Axe": 2703, "Cracked Pickaxe": 2691, "Wooden Fishing Rod": 2709,
       "Training Magic Staff": 2569, "Unbound Grimoire": 1626, "Training Lantern": 1627, "Training Lantern (2)": 1627, "Wild Grimoire": 1628,
       "Beginner's Tunic": 1334, "Beginner's Leggings": 1335, "Beginner's Boots": 1336,
       "Bracelet of the Stags": 1594, "Gloves of the Stags": 2043, "Slimy Ring": 2478, "Gelatinous Bracelet": 1592,
       "Gelatinous Amulet": 1291, "Gelatinous Cloak": 1453, "Spider Bracelet": 1595, "Iron Ring": 2482, "Iron Bracelet": 1593,
       "Iron Gloves": 2042, "Iron Coin": 1457, "Iron Amulet": 1297, "Copper Ring": 2477, "Copper Bracelet": 1591,
       "Copper Gloves": 2039, "Copper Coin": 1452, "Copper Amulet": 1290, "Bracelet of the Sylvan": 1589, "Ring of the Sylve": 2473,
       "Skeleton Skull": 1450, "Skeletal Ring": 2474, "Bony Gloves": 2037, "Skeletal Amulet": 1289, "Belt of the Stags": 1460, "Ring of the Wolf": 2480, "Albal's Necklace": 1296,
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

# levels from the game tooltips (2026-11-07 merchant audit: Potion II/III cards had no level)
LV = {"Health Potion II": 3, "Health Potion III": 5, "Mana Potion II": 5, "Mana Potion III": 8, "Stamina Potion II": 5, "Stamina Potion III": 8,
      "Boar Meat": 1, "Training Scepter": 1, "Training Quiver": 1, "Training Dagger (2)": 1, "Training Lantern (2)": 1}
# output per craft (game window "×3"): npc|item -> quantity
QTY = {"Alchemist|Quality %s Potion %s" % (k, n): 3 for k in ("Health", "Mana", "Stamina") for n in ("I", "II", "III")}
for npc, rows in SHOTS.items():                              # screenshots replace the same item, keep the rest
    old = {r[1]: r for r in npcs.get(npc, [])}
    new = [[OID.get(n), n, sec, [[MAT.get(m, m), q] for m, q in mats], cost, rar, cat, LV.get(n) or (old.get(n) or [None] * 8)[7], "shot"] for n, rar, sec, mats, cost, cat in rows]
    names = {r[1] for r in new}
    npcs[npc] = new + ([] if npc in FULL else [r for r in npcs.get(npc, []) if r[1] not in names])


# 2026-11-12 batch (in24, owner's Chinese screenshots 11/8～11/12): other floors. Key = (floor, npcs.js name of that floor);
# recipes.js writes them as "3|Alchemist" (floor 3 also has an "Alchemist"). Window titles are in the comments.
# Materials use the site's item key when the game's Chinese name matches one (data23.js / zhnames.js), otherwise the
# game's Chinese name as shown (no English name seen for those).
FORT3 = [("Endurance", [["Wheat", 14], ["Wheat Leaves", 4], ["Wheat Flower", 2], ["Yellow Spider Carcass", 16]]),
         ("Knowledge", [["Allium Flower", 14], ["Lavender", 4], ["Wisteria", 5], ["Purple Spider Eyes", 8]]),
         ("Ferocity", [["琥珀萼片", 14], ["琥珀種子", 4], ["Flarevae", 16], ["Orc Blood", 8]]),
         ("Vitality", [["奧拉西爾之刺", 16], ["Sylvaerian Jewel", 8], ["Sylvaer Essence", 1]]),
         ("Patience", [["Sylnovarian Leaves", 12], ["Sylnovarian Jewel", 8], ["Sylnovar Essence", 1]]),
         ("Resistance", [["White Spider Powder", 12], ["Juvenile Bark", 6], ["Ravager Bark", 6], ["Orc Heart", 1]])]
P3_II = [["Allium Flower", 6], ["Sylve Sprout", 4], ["Magic Wood Shard", 3]]
P3_III = [["Allium Flower", 9], ["Sylve Sprout", 6], ["Magic Wood Shard", 5], ["Ancestral Root", 1]]
SHOTS23 = {
    # P3 - Assistant Alchimiste du Palier 3 (zh window「P3 - 樓層鍊金術師助手 3」), 11/12 01:47～01:48
    (3, "Assistant to the Alchemist"): [("Quality %s Fortifier III" % k, "b", 60, m, "55", "potion") for k, m in FORT3],
    # P3 - Alchimiste du Palier 3, 11/12 01:48～01:49: 13 recipes, 15 Col, 5 s, ×3 each (no tier I, no Mana/Stamina IV)
    (3, "Alchemist"): [("Quality %s Potion II" % k, "b", 5, P3_II, "15", "potion") for k in ("Health", "Mana", "Stamina")]
                      + [("Quality %s Potion III" % k, "b", 5, P3_III, "15", "potion") for k in ("Health", "Mana", "Stamina")]
                      + [("Quality Health Potion IV", "b", 5, [["Allium Flower", 10], ["Flaming Feather", 10], ["Marrow Powder", 3]], "15", "potion"),
                         ("Quality Health Potion V", "b", 5, [["Allium Flower", 12], ["Orc Blood", 6]], "15", "potion"),
                         ("Quality Health Potion VI", "b", 5, [["Allium Flower", 12], ["Orc Blood", 10], ["Orc Eye", 8]], "15", "potion"),
                         ("Quality Mana Potion V", "b", 5, [["Allium Flower", 12], ["Sylnovarian Leaves", 6]], "15", "potion"),
                         ("Quality Mana Potion VI", "b", 5, [["Allium Flower", 12], ["Sylnovarian Leaves", 10], ["Sylnovarian Jewel", 8]], "15", "potion"),
                         ("Quality Stamina Potion V", "b", 5, [["Allium Flower", 12], ["Yellow Spider Carcass", 12]], "15", "potion"),
                         ("Quality Stamina Potion VI", "b", 5, [["Allium Flower", 12], ["Yellow Spider Carcass", 16], ["Wheat Flower", 4]], "15", "potion")],
    # P3 - Marchand d'Outils (zh「P3 - 工具商人」), Buy tab 01:51:27
    (3, "Reinforced Tools Merchant"): [(n, "c", None, [], "753.74", "other") for n in ("Pioche Renforcée", "Hache Renforcée", "Houe Renforcée")],
    # P3 - Marchand de Consommables (zh「P3 - 消耗品商人」), Buy tab 01:51:58 / 01:52:34 / 01:52:47
    (3, "Consumables Merchant"): [("%s Potion %s" % (k, t), "c", None, [], c, "potion") for t, c in (("I", "30.15"), ("II", "65.32"), ("III", "100.50")) for k in ("Health", "Mana", "Stamina")]
                                 + [("Parchemin de Réallocation", "b", None, [], "753.74", "other"), ("Parchemin de Maîtrise", "b", None, [], "753.74", "other")],
    # P3 - Artisan de Runes (zh「P3 - 符文工匠」), first one ≈911,598: 4 RARE runes 01:53
    (3, "Basic Rune Craftsman"): [("Rune des Bois", "b", 60, [["橙色赤鐵礦", 8], ["蜂蜜琥珀", 16], ["Woodland Tail", 16]], "15", "other"),
                                  ("Rune Gobeline", "b", 60, [["孔雀石", 6], ["Goblin Essence", 1]], "15", "other"),
                                  ("Rune Orcienne", "b", 60, [["石榴石", 2], ["鋁土礦錠", 4], ["Orc Blood", 16]], "15", "other"),
                                  ("Rune de la Toile", "b", 60, [["赤鐵礦", 4], ["Iron Ingot", 4], ["Scrap Metal Piece", 8]], "15", "other")],
    # second Artisan de Runes ≈855,536: 5 EPIC runes 02:00
    (3, "Complex Rune Craftsman"): [("Rune Sylnovarienne", "a", 60, [["藍銅礦", 6], ["藍寶石", 2], ["Sylnovar Essence", 1]], "15", "other"),
                                    ("Rune Sylvaerienne", "a", 60, [["孔雀石", 6], ["綠松石", 2], ["Sylvaer Essence", 1]], "15", "other"),
                                    ("Rune Brumeuse", "a", 60, [["黃鐵礦", 6], ["Anthracite", 4], ["Misty Tail", 32]], "15", "other"),
                                    ("Rune Luminiscente", "a", 60, [["金黃鐵礦", 4], ["蜂蜜琥珀", 16], ["Luminescent Spider Venom", 1]], "15", "other"),
                                    ("Rune Spectrale", "a", 60, [["紅柱石", 6], ["Jet", 4], ["Spectral Essence", 1]], "15", "other")],
    # P3 - Craft Artefact de Sylnovar (nameplate 神器鐵匠, ≈918,598; reference map "Sylnovar Accessories Blacksmith" 918,579): 14 EPIC, 10 min, 30 Col
    (3, "Sylnovar Accessories Blacksmith"): [(n, "a", 600, m, "30", "acc") for n, m in (
        ("Bottes des Crocs des Bois", [["Bottes des Bois", 1], ["Woodland Tail", 32], ["Sylnovarian Cloth", 64]]),
        ("Bottes au Crocs Brumeux", [["Bottes Brumeuses", 1], ["Misty Tail", 32], ["Sylvaerian Cloth", 64]]),
        ("Bottes Orciennes", [["Bottes Goblines", 1], ["Ravager Bark", 32], ["Ravager Heart", 16]]),
        ("Bottes des Bois Sombres", [["Bottes Sylvestres", 1], ["Sylvaerian Jewel", 32], ["Juvenile Bark", 32], ["Sylvaer Essence", 16]]),
        ("Bottes de la Toile", [["Bottes en Toile d'Araignée", 1], ["Black Silk", 32], ["White Spider Silk", 32], ["Egg Cocoon", 16]]),
        ("Bottes Luminescentes", [["Yellow Spider Silk", 64], ["Luminescent Spider Venom", 16], ["Misty Fur", 64]]),
        ("Bottes Spectrales", [["White Spider Silk", 64], ["Spectral Essence", 16], ["Misty Fur", 64]]),
        ("Couteau à la Griffe des Bois", [["Woodland Claw", 128], ["Juvenile Seed", 16]]),
        ("Couteau à la Griffe de la Brume", [["Misty Claw", 128], ["Juvenile Seed", 16]]),
        ("Hache de la Tribu", [["Orc Eye", 64], ["Orc Essence", 16]]),
        ("Grimoire des Bois Sombres", [["Orc Heart", 16], ["Ravager Heart", 16]]),
        ("Masque de la Toile", [["強化蛛絲", 16], ["White Spider Silk", 64]]),
        ("Ceinture Luminescente", [["Yellow Spider Carcass", 128], ["Yellow Spider Silk", 64]]),
        ("Plume Spectrale", [["Spectral Essence", 16], ["White Spider Silk", 64]]))],
    # no nameplate; window titles P3 - Craft Couteau en Dent de Loup / Craft Gants Féroce / Forgeron Grimoire Corrompu (02:59～03:26)
    (3, "P3 - Craft Couteau en Dent de Loup"): [("Couteau en Dent de Loup", "s", 600, [["Wolf Fangs", 64], ["Fangs of Albal", 8], ["Woodland Claw", 96]], "55", "acc")],
    (3, "P3 - Craft Gants Féroce"): [("Gants Féroce", "s", 600, [["Wolf Fur", 64], ["狼皮（第 2 種，名稱相同）", 64], ["Woodland Fur", 96], ["Woodland Tail", 32]], "55", "acc")],
    # the three rows are three different Corrupted Fragments (green / blue / purple tooltip, 03:26:09～15)
    (3, "P3 - Forgeron Grimoire Corrompu"): [("Grimoire Faible Corruption", "splus", 600, [["Corrupted Fragment", 32], ["Corrupted Fragment (2)", 16], ["Corrupted Fragment (3)", 8]], "55", "acc")],
    # floor 2, Khesûn sanctuary (window title "2 -", 11/10 04:08): Runic Necklace EPIC 1 min, 55 Col; the three materials are all ×64
    (2, "Manufacturer of the Runic Necklace"): [("Collier Runique", "a", 60, [["Bone Dust", 64], ["Spectral Chain", 64], ["Runestone", 64]], "55", "acc")],
}
OID23 = {"Quality Endurance Fortifier III": 1999, "Quality Knowledge Fortifier III": 1998, "Quality Ferocity Fortifier III": 1997,
         "Quality Patience Fortifier III": 2001, "Quality Resistance Fortifier III": 2000, "Quality Vitality Fortifier III": 1996,
         "Quality Health Potion IV": 2466, "Quality Health Potion V": 2467, "Quality Health Potion VI": 2468, "Mana Potion III": 2470,
         "Pioche Renforcée": 2695, "Hache Renforcée": 2707, "Houe Renforcée": 2701, "Parchemin de Réallocation": 1708, "Parchemin de Maîtrise": 1707,
         "Rune des Bois": 2021, "Rune Gobeline": 2020, "Rune Orcienne": 2019, "Rune de la Toile": 2022, "Rune Sylnovarienne": 2023,
         "Rune Sylvaerienne": 2024, "Rune Brumeuse": 2025, "Rune Luminiscente": 2026, "Rune Spectrale": 2027,
         "Bottes des Crocs des Bois": 1517, "Bottes au Crocs Brumeux": 1519, "Bottes Orciennes": 1514, "Bottes des Bois Sombres": 1521,
         "Bottes de la Toile": 1526, "Bottes Luminescentes": 1523, "Bottes Spectrales": 1345, "Couteau à la Griffe des Bois": 1538,
         "Couteau à la Griffe de la Brume": 1540, "Hache de la Tribu": 1542, "Grimoire des Bois Sombres": 1545, "Masque de la Toile": 1547,
         "Ceinture Luminescente": 1549, "Plume Spectrale": 1551, "Couteau en Dent de Loup": 1564, "Gants Féroce": 2074,
         "Grimoire Faible Corruption": 1565, "Collier Runique": 1309}
LV23 = {"Quality Health Potion II": 5, "Quality Mana Potion II": 5, "Quality Stamina Potion II": 5, "Quality Health Potion III": 8,
        "Quality Mana Potion III": 8, "Quality Stamina Potion III": 8, "Quality Health Potion IV": 12, "Quality Health Potion V": 15,
        "Quality Health Potion VI": 18, "Quality Mana Potion V": 15, "Quality Mana Potion VI": 18, "Quality Stamina Potion V": 15,
        "Quality Stamina Potion VI": 18, "Health Potion I": 1, "Mana Potion I": 1, "Stamina Potion I": 1, "Health Potion II": 3,
        "Health Potion III": 5, "Mana Potion II": 5, "Mana Potion III": 8, "Stamina Potion II": 5, "Stamina Potion III": 8,
        "Pioche Renforcée": 15, "Hache Renforcée": 15, "Houe Renforcée": 15}
out23 = {}
for (fl, npc), rows in SHOTS23.items():
    key = "%d|%s" % (fl, npc)
    out23[key] = {"floor": fl, "items": [[OID23.get(n, OID.get(n)), n, sec, [m[:] for m in mats], cost, rar, cat, LV23.get(n), "shot"] for n, rar, sec, mats, cost, cat in rows]}
    if npc == "Alchemist":
        QTY.update({key + "|" + r[1]: 3 for r in out23[key]["items"]})
cat_ids = {x["id"] for x in json.load(open(CAT, encoding="utf-8"))}
bad = [r[1] for rows in list(npcs.values()) + [v["items"] for v in out23.values()] for r in rows if r[0] is not None and r[0] not in cat_ids]
assert not bad, bad

hdr = """/* Recipes by NPC (key = floor-1 NPC name, or "3|name" for another floor; matches npcs.js where that NPC is mapped). Built by tools/build_recipes.py.
   Row: [catalogueId|null, name, seconds|null, [[material, qty]], cost Col ("Free"; null = unknown), rarity|null, category, level, source]
   category: weapon / armor / acc / potion / key. source: "shot" = owner's in-game screenshot (wins), "ref" = reference map.
   Weapons and armour here are only the starter gear sold by the Starting Merchant; smiths' recipes still need screenshots. */
window.SAO_RECIPES = """
out = {npc: {"floor": 1, "items": rows} for npc, rows in sorted(npcs.items())}
out.update(out23)
open(os.path.join(ROOT, "recipes.js"), "w", encoding="utf-8").write(hdr + json.dumps(out, ensure_ascii=False, indent=0) + ";\nwindow.SAO_RECIPE_QTY = " + json.dumps(QTY, ensure_ascii=False) + ";\n")
n = sum(len(r) for r in npcs.values())
from collections import Counter
print(n, "recipes,", len(npcs), "NPCs", Counter(r[6] for rows in npcs.values() for r in rows), Counter(r[8] for rows in npcs.values() for r in rows))
