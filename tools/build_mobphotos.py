#!/usr/bin/env python3
"""官網新聞的怪物表 → img/mobs/、mobphotos.js，以及 data23.js 裡「只有官網新聞有」的怪物。

用法：python3 -I tools/build_mobphotos.py <10/28 新聞資料夾> <11/9 新聞資料夾>
  10/28：news.json（monsters：name、floor_en、local_img、changes_en、verdict_en）＋ imgs/*.png
  11/9 ：news_monsters.json（name、sub "Floor N"、zone、twzone、tw、changes、v、img 網址）＋ news1109_imgs/<網址檔名>
做法：圖片裁掉透明邊、補成正方形、縮成 128px，不翻轉。名稱依官網原文（法文）對到本站怪物（MAP／MAP2，直譯或同名）。
  - 11/9 是最新的調整（rows），10/28 是之前的調整（old）；臉的圖片用 11/9 的。
  - 11/9 表上本站沒有的怪物（使用者 2026-11-11 選 A：照新聞名稱全部新增，標「只有官網公告」）寫進 data23.js 的
    BEGIN/END build_mobphotos 區塊（名稱照官網原文；腐化版沿用本體的類型、行為、區域；其他類型、行為未知）。
  - 區域：新聞的區域名對到本站區域（同一區的已對照怪物都在本站同一個區域才算），對不上的放「還不知道在哪個區域」，
    新聞的區域名另外顯示在怪物資料；本站完全沒有的新聞區域（Chêne noir 等）新增成區域。
"""
import json, os, re, sys
from PIL import Image

# 10/28 新聞（官網名稱 → 本站怪物）
MAP = {
 (1,"Bandit Archer"):"Bandit Archer",(1,"Bandit Assassin"):"Bandit Assassin",(1,"Bandit Robuste"):"Sturdy Bandit",
 (1,"Guerrier Kobold"):"Kobold Warrior",(1,"Petit Kobold"):"Small Kobold",(1,"Sentinelle Kobold"):"Kobold Sentinel",
 (1,"Kobold_sentinel_em_summoned"):"Kobold Sentinel",(1,"l’Archer Malicieux"):"The Mischievous Archer",
 (2,"Loup des Montagnes"):"Mountain Wolf",(2,"Loup des Savanes"):"Savanna Wolf",(2,"Taureau"):"Bull",
 (3,"Adoryll"):"Adoryll, the Caged Bird",(3,"Alpha des Bois"):"Woodland Alpha",
 (3,"Araignée Luminescente"):"Luminescent Spider",(3,"Araignée Noir"):"Black Spider",(3,"Araignée Spectrale"):"Shadow Spider",
 (3,"Araignée Volante"):"Flying Spider",(3,"Araignée d'Améthyste"):"Amethyst Spider",
 (3,"Bandit Archer"):"Bandit Archer",(3,"Bandit Assassin"):"Bandit Assassin",(3,"Bandit Robuste"):"Sturdy Bandit",
 (3,"Chef des bandits"):"Bandit Chief",(3,"Gardien du Labyrinthe"):"Furacas, Guardian of the Labyrinth",
 (3,"Gobelin de la Caverne"):"Cave Goblin",(3,"Goblin_Shaman"):"Goblin Shaman",(3,"Jeune pousse"):"Jeune pousse",(3,"Loup Esclave"):"Slave Wolf",
 (3,"Muffet"):"Muffet, Mother of Black Spiders",(3,"Nerius the Evil Treant"):"Nerius the Evil Treant",
 (3,"Orc Samourai"):"Orc Samurai",(3,"Orc Shaman"):"Orc Shaman",(3,"Roi de la Caverne"):"Cave King",
 (3,"Sylnovar Archer Exilé"):"Sylnovar Archer",(3,"Sylnovar Garde Exilé"):"Sylnovar Guard",(3,"Sylnovar Mage Exilé"):"Sylnovar Mage",
 # 2026-11-11: the 11/9 table lists both "Sylvaer Garde Exilé" (the guard) and "Sylvaer Garde Corrompu" (its corrupted version)
 (3,"Sylvaer Archer Exilé"):"Sylvaer Archer",(3,"Sylvaer Garde Corrompu"):"Sylvaer Garde Corrompu",(3,"Sylvaer Mage Exilé"):"Sylvaer Mage",
 (3,"Tréant Ancien du Labyrinthe"):"Ancient Labyrinth Treant",(3,"Tréant Juvenile"):"Juvenile Treant",(3,"Tréant Ravageur"):"Ravager Treant",(3,"Tréant du Labyrinthe"):"Labyrinth Treant",
 # 使用者 2026-11-06 因位置不明先不放；11/9 新聞寫在 Village des orcs，使用者 2026-11-11 選 A（新聞的怪物全部新增）
 (3,"Chef de la Tribu"):"Chef de la Tribu",
}
# 11/9 新聞〈Floors 2 and 3 are open!〉：官網名稱 → 本站怪物（名稱直譯或同名；scratchpad f23/news1109_monster_table.md 的 A／B 級）
MAP2 = {
 (2,"Brute Morte-Vivante"):"Undead Brute",(2,"Dardroyal"):"Royal Stinger",(2,"Gardien"):"Guardian",
 (2,"Gardien du Sanctuaire"):"Sanctuary Guardian",(2,"Gargouille Morte-Vivante"):"Undead Gargoyle",(2,"Golem de Pierre"):"Stone Golem",
 (2,"Harpy de Feu"):"Fire Harpy",(2,"Harpy de Foudre"):"Lightning Harpy",(2,"Harpy de Terre"):"Earth Harpy",
 (2,"Loup des Montagnes"):"Mountain Wolf",(2,"Loup des Savanes"):"Savanna Wolf",(2,"Magnus, Colosse des Veines"):"Magnus, Colossus of the Veins",
 (2,"Melisara, Souveraine de la Ruche"):"Melisara, Sovereign of the Hive",(2,"Ours de la Forêt"):"Forest Bear",(2,"Ouvrière"):"Worker Bee",
 (2,"Poisson Fulgurant"):"Fulgurant Fish",(2,"Rugiboeuf, Le Gardien"):"Rugibœuf, The Guardian",
 (2,"Squelette Archer de Feu"):"Fire Skeleton Archer",(2,"Squelette Lancier de Feu"):"Fire Skeleton Lancer",
 (2,"Squelette Sorcier de Feu"):"Fire Skeleton Sorcerer",(2,"Squelette Tank de Feu"):"Fire Skeleton Tank",(2,"Squelette de Feu"):"Fire Skeleton",
 (2,"Squelette Épéiste de Feu"):"Fire Skeleton Swordsman",(2,"Taureau"):"Bull",(2,"Taureau Monstrueux"):"Monstrous Bull",
 (2,"Velindra la Tisseuse"):"Velindra the Weaver",(2,"Winnie"):"Winnie, Man's Best Friend",(2,"Âme Squelette"):"Skeleton Soul",
 # the site / wiki spell it Morverth (one more r); same title "the Soul Flayer"
 (2,"Morveth l’Écorcheur d’Âmes"):"Morverth the Soul Flayer",
 (3,"Adoryll"):"Adoryll, the Caged Bird",(3,"Alpha des Bois"):"Woodland Alpha",(3,"Araignée Luminescente"):"Luminescent Spider",
 (3,"Araignée Noire"):"Black Spider",(3,"Araignée Spectrale"):"Shadow Spider",(3,"Araignée Volante"):"Flying Spider",
 (3,"Araignée d'Améthyste"):"Amethyst Spider",(3,"Bandit Archer"):"Bandit Archer",(3,"Bandit Assassin"):"Bandit Assassin",
 (3,"Bandit Robuste"):"Sturdy Bandit",(3,"Chef des bandits"):"Bandit Chief",(3,"Gardien du Labyrinthe"):"Furacas, Guardian of the Labyrinth",
 (3,"Gobelin Shaman"):"Goblin Shaman",(3,"Gobelin de la Caverne"):"Cave Goblin",(3,"Jeune pousse"):"Jeune pousse",
 (3,"Loup Esclave"):"Slave Wolf",(3,"Loup brumeux"):"Misty Wolf",(3,"Loup des bois"):"Woodland Wolf",
 (3,"Muffet"):"Muffet, Mother of Black Spiders",(3,"Nerius, le Tréant Maléfique"):"Nerius the Evil Treant",
 (3,"Orc Guerrier"):"Orc Warrior",(3,"Orc Samourai"):"Orc Samurai",(3,"Orc Shaman"):"Orc Shaman",(3,"Roi de la Caverne"):"Cave King",
 (3,"Sylnovar Archer Exilé"):"Sylnovar Archer",(3,"Sylnovar Garde Exilé"):"Sylnovar Guard",(3,"Sylnovar Mage Exilé"):"Sylnovar Mage",
 (3,"Sylvaer Archer Exilé"):"Sylvaer Archer",(3,"Sylvaer Garde Exilé"):"Sylvaer Guard",(3,"Sylvaer Mage Exilé"):"Sylvaer Mage",
 (3,"Tréant Ancien du Labyrinthe"):"Ancient Labyrinth Treant",(3,"Tréant Juvenile"):"Juvenile Treant",(3,"Tréant Ravageur"):"Ravager Treant",
 (3,"Tréant du Labyrinthe"):"Labyrinth Treant",
}
# corrupted versions whose base name is not literally another row of the table
BASE = {(3,"Gobelin Archer"):"Goblin Archer",(3,"Tréant Ancien"):"Ancient Labyrinth Treant",(3,"Sylnovar Archer"):"Sylnovar Archer",
        (3,"Sylnovar Garde"):"Sylnovar Guard",(3,"Sylnovar Mage"):"Sylnovar Mage",(3,"Sylvaer Archer"):"Sylvaer Archer",
        (3,"Sylvaer Garde"):"Sylvaer Guard",(3,"Sylvaer Mage"):"Sylvaer Mage"}
# news region -> site zone by name (Hive of Melliona = Ruche de Melliona)
ZONE_BY_NAME = {(2,"Ruche de Melliona"):"hive"}
# region names too generic to be a zone of their own
GENERIC = {"Monde","Forêt","Harpies"}
# notes for new monsters that may be a site monster under another name (not merged: names differ)
MAYBE = {
 (2,"Le Roi Taurus"):"名稱和網站的 Taurus（wiki 樓層總表寫第 2 層首領是 Asterius）不同，可能是同一隻，還沒有遊戲畫面確認。",
 (2,"Squelette de Sable"):"網站（wiki）分成 Sand Skeleton Warrior、Sand Skeleton Archer 兩隻，官網新聞只有這一列（生命寫 3000–4500）。",
 (2,"Squelette du Sanctuaire"):"網站（wiki）分成 Sanctuary Skeleton - Archer／Shaman／Warrior 三隻，官網新聞只有這一列。",
 (3,"Alpha Spectral"):"名稱和網站的 Misty Wolf Alpha 不同，可能是同一隻（官網圖檔名 wolf-spectral-boss；Loup brumeux＝Misty Wolf 的圖檔是 wolf-spectral）。",
 (3,"Chef de la Tribu"):"站長 2026-11-06 因為位置不明先不放；官網 11/9 新聞寫在 Village des orcs（獸人村落）。",
}
NEWZ_ICON = "👾"

# 256-colour palette PNG (with alpha): about 1/3 the size, looks the same at map-marker size (2026-11-11, slow mobile loading)
def png8(im): return im.convert("RGBA").quantize(256, method=Image.Quantize.FASTOCTREE)

def sq128(path):
    im = Image.open(path).convert("RGBA"); bb = im.getchannel("A").getbbox()
    if bb: im = im.crop(bb)
    s = max(im.size); sq = Image.new("RGBA", (s + 8, s + 8), (0, 0, 0, 0)); sq.paste(im, ((s + 8 - im.width) // 2, (s + 8 - im.height) // 2))
    return sq.resize((128, 128), Image.LANCZOS)

def corrupted_base(fr):
    for suf in (" (Corrupted)", " Corrompue", " Corrompu"):
        if fr.endswith(suf): return fr[: -len(suf)]
    return None

def main(src1028, src1109):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(root, "img", "mobs"), exist_ok=True)
    # site monsters (name -> zone/type/beh/icon) from data23.js, without the generated block
    import subprocess
    site = json.loads(subprocess.run(["node", "-e", """
      global.window={};require(process.argv[1]);const o={};
      for(const f of [2,3]){for(const m of window.SAO23.floors[f].M) if(!m.news) o[f+'|'+m.name]={zone:m.zone,type:m.type,beh:m.beh,icon:m.icon};}
      console.log(JSON.stringify(o))""", os.path.join(root, "data23.js")], capture_output=True, text=True, check=True).stdout)
    by = {"1": {}, "2": {}, "3": {}}

    def put(fl, name, row, key):
        e = by[str(fl)].setdefault(name, {"rows": []})
        e.setdefault(key, []).append(row)

    # ---- 10/28 (older) ----
    d = json.load(open(os.path.join(src1028, "news.json"), encoding="utf-8"))
    for m in d["monsters"]:
        fl = int(m["floor_en"].split()[-1]); name = MAP.get((fl, m["name"]))
        if not name: raise SystemExit("10/28 not mapped: %r" % ((fl, m["name"]),))
        row = {"fr": m["name"], "ch": [c["raw"] for c in m.get("changes_en", [])], "v": m.get("verdict_en", "")}
        li = m.get("local_img")
        if li:
            fn = "img/mobs/" + os.path.basename(li); png8(sq128(os.path.join(src1028, li))).save(os.path.join(root, fn), optimize=True); row["f"] = fn
        put(fl, name, row, "old")
    # ---- 11/9 (latest) ----
    n9 = json.load(open(os.path.join(src1109, "news_monsters.json"), encoding="utf-8"))
    new = {"2": {}, "3": {}}           # new monster name -> info
    zmap = {}                          # (fl, news zone) -> set of site zones
    rows9 = []
    for m in n9:
        fl = int(m["sub"].split()[-1]); fr = m["name"] = re.sub(r"\s+", " ", m["name"]).strip()   # the table has "Loup des bois  (Corrupted)"
        name = MAP2.get((fl, fr))
        base = None
        if not name:
            b = corrupted_base(fr)
            if b: base = MAP2.get((fl, b)) or MAP2.get((fl, b + " Exilé")) or BASE.get((fl, b)) or b
            name = fr
            new[str(fl)][fr] = {"fr": fr, "zone9": m["zone"], "tw": m.get("tw"), "twzone": m.get("twzone"), "base": base}
        rows9.append((fl, name, m))
        if (fl, fr) in MAP2:
            (site[f"{fl}|{name}"]["zone"] != "none") and zmap.setdefault((fl, m["zone"]), set()).add(site[f"{fl}|{name}"]["zone"])
    # base of a new corrupted monster may itself be new (Chef de la Tribu, Alpha Spectral)
    for fl in ("2", "3"):
        for k, v in new[fl].items():
            b = v["base"]
            if b and f"{fl}|{b}" not in site and b not in new[fl]: raise SystemExit("base not found: %s -> %s" % (k, b))
            if b and f"{fl}|{b}" in site and site[f"{fl}|{b}"]["zone"] != "none": zmap.setdefault((int(fl), v["zone9"]), set()).add(site[f"{fl}|{b}"]["zone"])
    def site_zone(fl, z):
        if (fl, z) in ZONE_BY_NAME: return ZONE_BY_NAME[(fl, z)]
        s = zmap.get((fl, z))
        return next(iter(s)) if s and len(s) == 1 else None
    for fl, name, m in rows9:
        ch = [c.strip() for c in m["changes"].split(" ; ") if c.strip()]
        row = {"fr": m["name"], "ch": ch, "v": m.get("v", ""), "tw": m.get("tw", "")}
        li = m.get("img")
        if li:
            fn = "img/mobs/n1109-" + os.path.basename(li).replace("news-1794200000000-mob-", "")
            png8(sq128(os.path.join(src1109, "news1109_imgs", os.path.basename(li)))).save(os.path.join(root, fn), optimize=True); row["f"] = fn
        put(fl, name, row, "rows")
        e = by[str(fl)][name]
        lv = [re.search(r"→\s*(\d+)", c).group(1) for c in ch if c.startswith("Level")]
        if lv: e["lv"] = int(lv[0])
        e["z"] = [m["zone"], m.get("twzone", "")]
        sz = site_zone(fl, m["zone"]); e["zs"] = sz
    for v in by.values():
        for e in v.values():
            e["rows"] = e.get("rows", [])
            pics = [r["f"] for r in e["rows"] + e.get("old", []) if r.get("f")]
            if pics: e["f"] = pics[0]
            e.pop("zs", None)
    # ---- data23.js block: new zones + new monsters ----
    blocks = {}
    for fl in ("2", "3"):
        zones = {}; rows = []; done = {}
        order = sorted(new[fl].items(), key=lambda kv: 1 if kv[1]["base"] in new[fl] else 0)   # new bases first
        for fr, v in order:
            b = v["base"]; bi = site.get(f"{fl}|{b}") if b else None
            if b and b in done: bi = done[b]
            z9 = v["zone9"]; sz = site_zone(int(fl), z9)
            if bi: zone = bi["zone"]
            elif sz: zone = sz
            elif z9 in GENERIC: zone = "none"
            elif zmap.get((int(fl), z9)): zone = "none"             # region spread over several site zones
            else:
                key = "n_" + re.sub(r"[^a-z]", "", z9.lower().replace("é", "e").replace("ê", "e"))[:14]
                zones[key] = {"n": z9, "zh": v["twzone"], "news": 1}; zone = key
            note = "只有官網 2026-11-09 新聞的怪物表有這隻（還沒有遊戲圖鑑資料），名稱照官網原文。"
            if b: note += "腐化版（Corrupted）；本體是 %s。" % b
            if MAYBE.get((int(fl), fr)): note += MAYBE[(int(fl), fr)]
            # the news region itself is shown in the monster's location row (mobphotos.js z)
            typ = bi["type"] if bi else "Unknown"
            beh = bi["beh"] if bi else "U"
            icon = bi["icon"] if bi else NEWZ_ICON
            rows.append(["", fr, typ, beh, zone, 0, [], note, icon]); done[fr] = {"zone": zone, "type": typ, "beh": beh, "icon": icon}
        blocks[fl] = (zones, rows)
    path = os.path.join(root, "data23.js"); s = open(path, encoding="utf-8").read()
    body = "// BEGIN build_mobphotos (generated: monsters only in the 2026-11-09 official news table; do not edit by hand)\n"
    for fl in ("2", "3"):
        zones, rows = blocks[fl]
        body += "addNews(F%s,\"f%sm\",%s,[\n%s\n]);\n" % (fl, fl, json.dumps(zones, ensure_ascii=False), ",\n".join("  " + json.dumps(r, ensure_ascii=False) for r in rows))
    body += "// END build_mobphotos\n"
    s2 = re.sub(r"// BEGIN build_mobphotos.*?// END build_mobphotos\n", lambda _: body, s, flags=re.S)
    if s2 == s and "// BEGIN build_mobphotos" not in s: raise SystemExit("data23.js has no BEGIN/END build_mobphotos block")
    open(path, "w", encoding="utf-8").write(s2)
    meta = {"srcs": {"1109": {"title": "Floors 2 and 3 are open!", "title_tw": "第2層與第3層開放了！",
                              "url": "https://saominecraft.com/us/news/paliers-2-et-3-ouverts", "date": "2026-11-09"},
                     "1028": {"title": d["title_en"], "title_fr": d["title"], "url": d["url_en"], "date": "2026-10-28"}},
            "by": by}
    open(os.path.join(root, "mobphotos.js"), "w", encoding="utf-8").write(
        "/* 官網新聞的怪物表：圖片（透明 PNG → 裁邊、縮成 128px，不翻轉）和平衡調整數值。tools/build_mobphotos.py 產生，不要手改。\n"
        "   rows＝2026-11-09〈Floors 2 and 3 are open!〉（最新），old＝2026-10-28〈Floors 2 & 3 Postponed…〉（之前的調整）；\n"
        "   lv＝11/9 表的「Level : a → b」的 b，z＝11/9 表的區域［官網原文, 台灣版新聞的譯名］。 */\n"
        "window.SAO_MOBPHOTO=" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("monsters:", sum(len(v) for v in by.values()), "new:", {k: len(v[1]) for k, v in blocks.items()},
          "new zones:", {k: list(v[0]) for k, v in blocks.items()})
    print("zone map:", {f"{k[0]}|{k[1]}": sorted(v) for k, v in zmap.items()})

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
