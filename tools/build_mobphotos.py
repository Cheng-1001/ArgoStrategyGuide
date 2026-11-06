#!/usr/bin/env python3
"""官網新聞的怪物圖片 → img/mobs/ 和 mobphotos.js。

用法：python3 -I tools/build_mobphotos.py <news 資料夾>
  資料夾裡要有 news.json（官網新聞頁解析出來的 monsters 表：name、floor_en、local_img、changes_en、verdict_en）
  和 imgs/*.png（200×200 透明 PNG）。目前只有 2026-10-28 那篇新聞有怪物表。
做法：裁掉透明邊、補成正方形、縮成 128px，不翻轉；對照表 MAP 依官網名稱（法文）對到本站怪物，表上每一列都收。
"""
import json, os, re, sys
from PIL import Image

# 官網怪物表的名稱（法文）→ 本站怪物。全部依名稱對應（直譯或同名），一列都不丟：
#  - 同一隻有多列的（Gobelin de la Caverne 三列、Sentinelle Kobold＋召喚版）放在同一隻底下當「變體」，每列各自的圖和數值
#  - Chef de la Tribu（部族首領）：第 3 層沒有叫 Tribe Chief 的怪物；wiki 的 Orc Samurai Boss 掉 Tribe Essence（部族精華）＝WHY
#  - Nerius the Evil Treant、Jeune pousse：wiki 圖鑑表沒有，data23.js 照官網名稱新增
# 圖片不翻轉（使用者 2026-11-04 選 B、2026-11-06「首領不轉向」）。
MAP = {
 (1,"Bandit Archer"):"Bandit Archer",(1,"Bandit Assassin"):"Bandit Assassin",(1,"Bandit Robuste"):"Sturdy Bandit",
 (1,"Guerrier Kobold"):"Kobold Warrior",(1,"Petit Kobold"):"Small Kobold",(1,"Sentinelle Kobold"):"Kobold Sentinel",
 (1,"Kobold_sentinel_em_summoned"):"Kobold Sentinel",(1,"l’Archer Malicieux"):"The Mischievous Archer",
 (2,"Loup des Montagnes"):"Mountain Wolf",(2,"Loup des Savanes"):"Savanna Wolf",(2,"Taureau"):"Bull",
 (3,"Adoryll"):"Adoryll, the Caged Bird",(3,"Alpha des Bois"):"Woodland Alpha",
 (3,"Araignée Luminescente"):"Luminescent Spider",(3,"Araignée Noir"):"Black Spider",(3,"Araignée Spectrale"):"Shadow Spider",
 (3,"Araignée Volante"):"Flying Spider",(3,"Araignée d'Améthyste"):"Amethyst Spider",
 (3,"Bandit Archer"):"Bandit Archer",(3,"Bandit Assassin"):"Bandit Assassin",(3,"Bandit Robuste"):"Sturdy Bandit",
 (3,"Chef de la Tribu"):"Orc Samurai Boss",(3,"Chef des bandits"):"Bandit Chief",(3,"Gardien du Labyrinthe"):"Furacas, Guardian of the Labyrinth",
 (3,"Gobelin de la Caverne"):"Cave Goblin",(3,"Goblin_Shaman"):"Goblin Shaman",(3,"Jeune pousse"):"Jeune pousse",(3,"Loup Esclave"):"Slave Wolf",
 (3,"Muffet"):"Muffet, Mother of Black Spiders",(3,"Nerius the Evil Treant"):"Nerius the Evil Treant",
 (3,"Orc Samourai"):"Orc Samurai",(3,"Orc Shaman"):"Orc Shaman",(3,"Roi de la Caverne"):"Cave King",
 (3,"Sylnovar Archer Exilé"):"Sylnovar Archer",(3,"Sylnovar Garde Exilé"):"Sylnovar Guard",(3,"Sylnovar Mage Exilé"):"Sylnovar Mage",
 (3,"Sylvaer Archer Exilé"):"Sylvaer Archer",(3,"Sylvaer Garde Corrompu"):"Sylvaer Guard",(3,"Sylvaer Mage Exilé"):"Sylvaer Mage",
 (3,"Tréant Ancien du Labyrinthe"):"Ancient Labyrinth Treant",(3,"Tréant Juvenile"):"Juvenile Treant",(3,"Tréant Ravageur"):"Ravager Treant",(3,"Tréant du Labyrinthe"):"Labyrinth Treant",
}
WHY = {"Orc Samurai Boss":"官網寫 Chef de la Tribu（部族首領）。第 3 層沒有叫這個名字的怪物；wiki 的 Orc Samurai Boss 在獸人營地、掉 Tribe Essence（部族精華），所以放在這裡。"}

def main(src):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = json.load(open(os.path.join(src, "news.json"), encoding="utf-8"))
    os.makedirs(os.path.join(root, "img", "mobs"), exist_ok=True)
    by = {"1": {}, "2": {}, "3": {}}; unused = []
    for m in d["monsters"]:
        fl = int(m["floor_en"].split()[-1]); li = m.get("local_img")
        name = MAP.get((fl, m["name"]))
        if not name:
            unused.append((fl, m["name"])); continue
        row = {"fr": m["name"], "ch": [c["raw"] for c in m.get("changes_en", [])], "v": m.get("verdict_en", "")}
        if li:
            im = Image.open(os.path.join(src, li)).convert("RGBA"); im = im.crop(im.getchannel("A").getbbox())
            s = max(im.size); sq = Image.new("RGBA", (s + 8, s + 8), (0, 0, 0, 0)); sq.paste(im, ((s + 8 - im.width) // 2, (s + 8 - im.height) // 2))
            sq = sq.resize((128, 128), Image.LANCZOS)
            fn = "img/mobs/" + os.path.basename(li)          # the news' own file name (floor and variant number in it)
            sq.save(os.path.join(root, fn), optimize=True); row["f"] = fn
        e = by[str(fl)].setdefault(name, {"rows": []})
        e["rows"].append(row)
        if "f" in row and "f" not in e: e["f"] = row["f"]   # the first picture is the monster's face
        if name in WHY: e["why"] = WHY[name]
    if unused: raise SystemExit("not mapped: %r" % unused)
    meta = {"src": {"title": d["title_en"], "title_fr": d["title"], "url": d["url_en"], "date": "2026-10-28"}, "by": by}
    open(os.path.join(root, "mobphotos.js"), "w", encoding="utf-8").write(
        "/* 官網新聞〈" + d["title_en"] + "〉（2026-10-28）的怪物表：圖片（200×200 透明 PNG → 裁邊、縮成 128px）和平衡調整數值。\n"
        "   tools/build_mobphotos.py 產生，不要手改。使用者 2026-11-06 選 A（全用）；圖片不翻轉。rows＝官網表的每一列（同名多列＝變體），why＝官網名稱和本站名稱不同時的對應依據。 */\n"
        "window.SAO_MOBPHOTO=" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("monsters:", sum(len(v) for v in by.values()), "rows:", sum(len(e["rows"]) for v in by.values() for e in v.values()))

if __name__ == "__main__":
    main(sys.argv[1])
