"""Build classes.js: the 職業／技能 tab.

Usage: python3 -I tools/build_classes.py <dir with wiki parse JSON> <reference map "Aincrad/Character Build" dir>
  - wiki: saominecraft.wiki.gg pages Classes, Guerrier, Assassin, Mage, Shaman, Archer, Martial Artist, fetched with
    api.php?action=parse&page=<page>&prop=wikitext|revid&format=json and saved as c_<Page_with_underscores>.json.
    Taken: role, difficulty, base-stat stars, specialisations, skill names / type / level. Descriptions are this
    site's own Chinese rewrite (ZH below), not copies.
  - reference map (DelayedCode SAO-MC-Interactive-Map, no licence: facts only, text-parsed, never executed):
    level 1 base stats, per-level gains (character-build-calculator.js) and the talent tree nodes
    (character-build-data.js), summarised per class.
  - equip.js (official catalogue): which weapon types each class can use ("Classe requise").
No images: the wiki's class / skill pictures are not used (they may come from the original SAO works, which the
server has no licence for).
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI, REF = sys.argv[1], sys.argv[2]

CLASSES = [  # id, wiki page, reference-map id, catalogue class key, Chinese name, emoji
    ("guerrier", "Guerrier", "guerrier", "guerrier", "戰士", "🛡️"),
    ("assassin", "Assassin", "assassin", "assassin", "刺客", "🗡️"),
    ("mage", "Mage", "mage", "mage", "法師", "🔮"),
    ("shaman", "Shaman", "shaman", "shaman", "薩滿", "🌿"),
    ("archer", "Archer", "archer", "archer", "弓箭手", "🏹"),
    ("martial", "Martial_Artist", None, None, "武鬥家", "👊"),
]
ZH = {  # this site's Chinese rewrite of the wiki descriptions
    "guerrier": "近戰職業，靠力量和耐打壓制對手。用重武器、穿重甲，在前線吸收傷害，同時打出高傷害，是隊友可以依靠的支柱。",
    "assassin": "速度快、出手致命，擅長爆擊和偷襲，在敵人反應前解決目標。用耐久換取爆發傷害和速度。",
    "mage": "精通奧術，從遠距離用法術控制戰場、造成大量傷害。近戰脆弱，靠魔力和範圍技能彌補。",
    "shaman": "隊伍的治療者，能回復隊友生命並給予增益、提高抗性。團體內容不可或缺。",
    "archer": "遠距離射手，從安全距離打出精準的穿透傷害。機動性好、輸出穩定。",
    "martial": "用拳套和肉體力量戰鬥的近戰職業，以快速連擊和重拳壓制敵人。",
    "Paladin": "神聖守護者，專注保護隊伍。", "Berserker": "犧牲防禦換取毀滅性的攻擊力。",
    "Samouraï": "太刀大師，兼具敏捷和力量，擅長正面連擊。", "Ninja": "暗影專家，無聲出手、造成持續傷害，擅長潛行和閃避。",
    "Archimage": "操控火、冰、雷等高階元素法術，從遠距離殲滅敵人。", "Nécromancien": "召喚生物、操縱靈魂，用黑魔法削弱並壓垮敵人。",
    "Druide": "專注自然治療和再生，用持續回復讓全隊撐下去。", "Oracle": "給予神聖預知和強力的攻擊增益。",
    "Sniper": "超遠距離的單發重擊，耐心和精準換來致命傷害。", "Ranger": "機動的快速射擊，擅長邊走邊打、持續輸出。",
    "Monk": "運用內在靈力，攻守平衡。", "Brawler": "靠蠻力和兇猛連擊，追求壓倒性的傷害。",
    # skills
    "Combinaison Brutale": "一連串重擊：大範圍突刺、再一次突刺、短衝刺穿刺、旋轉上挑把敵人打上空中，最後重重砸下。",
    "Instinct de Rempart": "受到攻擊時，獲得數秒的抗性 III。",
    "Le Saut du Berserker": "用劍掃過地面劃出裂地線，再躍起砸向瞄準的區域。",
    "Barrière de Bouclier": "召喚 4 面盾牌保護自己並擊退周圍目標；每面盾被打一次就碎，但會吸收那一下的全部傷害。同時嘲諷附近敵人。",
    "Tourbillon Implacable": "旋轉突刺一段時間，後撤再向前衝，打出長距離穿刺。",
    "Frappe Vicieuse": "站定蓄積氣場，從地面向上掃擊，向前放出一列造成重傷害的裂地衝擊。",
    "Frappe de Fureur": "紅色靈劍大幅伸長，向前砍 4 次後躍起砸向目標區域形成裂縫，再跳回原位；裂縫隨後爆炸，範圍內敵人暈眩。",
    "Lacération": "用匕首快速連斬前方敵人。", "Pas de l'Ombre": "穿過陰影衝刺，短暫隱形後出現在目標身後。",
    "Embuscade": "潛行中的第一擊爆擊傷害提高。", "Lame Empoisonnée": "刀刃塗毒，數秒內攻擊附帶持續傷害。",
    "Danse des Lames": "在周圍連續揮砍多次，最後一記強力突刺。",
    "Projectile Arcanique": "對目標發射奧術飛彈。", "Nova de Givre": "在身邊引發冰霜爆炸，緩速並傷害附近敵人。",
    "Bouclier Magique": "召喚吸收傷害的魔法屏障，持續數秒。", "Pluie de Météores": "在指定區域降下隕石雨，持續造成大範圍傷害。",
    "Cataclysme": "引導全部魔力，引發大範圍的毀滅性爆炸。",
    "Soin Naturel": "回復自己和附近隊友的生命。", "Totem de Protection": "放置圖騰，範圍內隊友受到的傷害降低。",
    "Bénédiction": "祝福隊友，一段時間內提升屬性和抗性。", "Chaîne de Vie": "和一名隊友連結，分享受到的治療，並替他承擔部分傷害。",
    "Renaissance": "大範圍大量治療所有隊友，並清除負面效果。",
    "Tir Précis": "精準射擊，距離越遠傷害越高。", "Pluie de Flèches": "向空中齊射，箭雨落在指定區域。",
    "Flèche Perforante": "強力箭矢，直線貫穿多名敵人。", "Roulade Tactique": "快速翻滾閃避，短暫無敵並調整位置。",
    "Tempête de Carreaux": "向前方扇形區域快速連射弩箭。",
    "Enchaînement": "三段拳連擊，一下比一下重。", "Coup de Paume": "掌擊放出衝擊波，擊退前方敵人。",
    "Aura de Combat": "連續命中會提高攻擊速度，最多疊 5 層。", "Uppercut Dévastateur": "強力上勾拳把目標打飛到空中。",
    "Poing du Dragon": "引導內在能量，打出向前推進的龍形拳。",
}
STARS_ZH = {"Health": "生命", "Strength": "力量", "Resistance": "抗性", "Speed": "速度", "Dexterity": "敏捷",
            "Magic": "魔法", "Mana": "魔力", "Stamina": "體力"}
REF_ZH = {"Health": "生命", "Damage": "傷害", "Mana": "魔力", "Attack Speed": "攻擊速度", "Critical Hit Chance": "暴擊率",
          "Critical Hit Damage": "暴擊傷害", "Movement Speed": "移動速度", "Evasion": "閃避", "Health Regeneration": "生命回復",
          "Mana Regeneration": "魔力回復", "Stamina Regeneration": "體力回復", "Skill Critical Hit Damage": "技能暴擊傷害",
          "Skill Critical Hit Chance": "技能暴擊率", "Projectile Damage": "投射物傷害", "Critical Power": "暴擊傷害",
          "Critical Chance": "暴擊率", "Defense": "防禦", "Lifesteal": "吸血", "Stamina": "體力", "Max Health": "最大生命",
          "Attack Damage": "攻擊傷害", "Physical Damage": "物理傷害", "Dodge": "閃避", "Damage Reduction": "傷害減免",
          "Magic Damage": "魔法傷害", "Max Mana": "最大魔力", "Spell Vampirism": "法術吸血", "Skill Critical Chance": "技能暴擊率",
          "Skill Critical Power": "技能暴擊傷害", "Bonus Heal": "治療加成"}


def wiki(page):
    d = json.load(open(os.path.join(WIKI, f"c_{page}.json"), encoding="utf-8"))["parse"]
    return d["wikitext"]["*"], d.get("revid")


def ref_block(text, start, end_pat=r"\n  \}\);"):
    i = text.index(start)
    return text[i:i + re.search(end_pat, text[i:]).start()]


calc = open(os.path.join(REF, "character-build-calculator.js"), encoding="utf-8").read()
data = open(os.path.join(REF, "character-build-data.js"), encoding="utf-8").read()


def ref_stats(block_name, cid):
    blk = ref_block(calc, f"const {block_name} = Object.freeze({{")
    m = re.search(rf"\n    {cid}: Object\.freeze\(\[(.*?)\]\)", blk, re.S)
    if not m:
        return []
    return [[REF_ZH.get(s, s), v] for s, v in re.findall(r'stat: "([^"]+)", value: "([^"]+)"', m.group(1))]


def talents(var):
    blk = data[data.index(f"const {var}_SKILLS"):]
    blk = blk[:blk.index("});")]
    c = collections.OrderedDict()
    for n, st, a, mode in re.findall(r'skill\d+: \{ name: "([^"]+)", stat: "([^"]+)", amount: ([\d.]+), statMode: "(\w+)"', blk):
        k = (n, REF_ZH.get(st, st), float(a), mode)
        c[k] = c.get(k, 0) + 1
    return [[n, st, a, "%" if mode == "percent" else "", cnt] for (n, st, a, mode), cnt in c.items()]


eq = open(os.path.join(ROOT, "equip.js"), encoding="utf-8").read()
EQ = json.loads(eq[eq.index("window.SAO_EQUIP") + len("window.SAO_EQUIP"):].lstrip(" =").rstrip().rstrip(";"))
weapons = collections.defaultdict(collections.Counter)
for r in EQ:
    v = (r[7] or {}).get("Classe requise")
    if v and r[2] != "armor":
        for c in str(v).lower().split(","):
            weapons[c.strip()][r[2]] += 1
TVAR = {"guerrier": "WARRIOR", "assassin": "ASSASSIN", "mage": "MAGE", "shaman": "SHAMAN", "archer": "ARCHER"}

out = []
for cid, page, rid, ckey, zh, emo in CLASSES:
    w, rev = wiki(page)
    role = re.search(r"'''Role''' \|\| (.*)", w).group(1).strip()
    diff = re.search(r"'''Difficulty''' \|\| (\S+)", w).group(1).count("⭐")
    stars = [[STARS_ZH[s], v.count("⭐")] for s, v in re.findall(r"\| (Health|Strength|Resistance|Speed|Dexterity|Magic|Mana|Stamina) \|\| (\S+)", w)]
    subs = [[n, ZH[n]] for n, _ in re.findall(r"\* '''\[\[([^\]]+)\]\]''' — (.*)", w)]
    rows = re.findall(r"\| \[\[File:([^|]+)\|32px\]\]\n\| '''(.*?)'''\n\| (\w+)\n\| (\d+)\n\| ", w)
    skills = [[n, "被動" if t == "Passive" else "主動", int(lv), ZH[n]] for f, n, t, lv in rows]
    placeholder = all("Placeholder" in f for f, *_ in rows)
    out.append({
        "id": cid, "name": page.replace("_", " "), "zh": zh, "ic": emo, "role": role, "diff": diff, "about": ZH[cid],
        "stars": stars, "subs": subs, "skills": skills, "skillsSure": not placeholder, "wikiRev": rev,
        "weapons": dict(weapons.get(ckey, {})) if ckey else {},
        "base": ref_stats("classBaseStats", rid) if rid else [], "perLv": ref_stats("classLevelBonuses", rid) if rid else [],
        "talents": talents(TVAR[cid]) if cid in TVAR else [],
    })

hdr = """/* Classes and skills (職業／技能 tab). Built by tools/build_classes.py; regenerate rather than edit by hand.
   wiki (saominecraft.wiki.gg): role, difficulty, stat stars, specialisations, skill names/levels; descriptions are
   this site's Chinese rewrite. skillsSure=false: every skill icon on the wiki page is a placeholder, so the list may
   be pre-release plans. Reference map (facts only): base stats, per-level gains, talent-tree nodes summarised as
   [name, stat, amount per point, unit, number of nodes]. weapons: official catalogue items per weapon type.
   No class or skill pictures on purpose (possible original SAO artwork the server has no licence for). */
window.SAO_CLASSES = """
open(os.path.join(ROOT, "classes.js"), "w", encoding="utf-8").write(hdr + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
print(len(out), "classes", [(c["id"], len(c["skills"]), c["skillsSure"], len(c["talents"]), sum(c["weapons"].values())) for c in out])
