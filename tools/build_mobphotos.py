#!/usr/bin/env python3
"""官網新聞的怪物圖片 → img/mobs/ 和 mobphotos.js。

用法：python3 -I tools/build_mobphotos.py <news 資料夾>
  資料夾裡要有 news.json（官網新聞頁解析出來的 monsters 表：name、floor_en、local_img、changes_en、verdict_en）
  和 imgs/*.png（200×200 透明 PNG）。目前只有 2026-10-28 那篇新聞有怪物表。
做法：裁掉透明邊、補成正方形、縮成 128px；首領（BOSS）左右翻轉成臉朝右（使用者 2026-11-06：「首領圖片改都不朝左」）；
對照表 MAP 把官網名稱（法文）對到本站怪物名稱，GUESS 是依外觀對應的（官網三張都叫 Gobelin de la Caverne 等）。
"""
import json, os, re, sys
from PIL import Image

MAP = {
 (1,"bandit-archer-palier-1"):"Bandit Archer",(1,"bandit-assassin-palier-1"):"Bandit Assassin",(1,"bandit-robuste-palier-1"):"Sturdy Bandit",
 (1,"guerrier-kobold-palier-1"):"Kobold Warrior",(1,"petit-kobold-palier-1"):"Small Kobold",(1,"sentinelle-kobold-palier-1"):"Kobold Sentinel",
 (1,"larcher-malicieux-palier-1"):"The Mischievous Archer",
 (2,"loup-des-montagnes-palier-2"):"Mountain Wolf",(2,"loup-des-savanes-palier-2"):"Savanna Wolf",(2,"taureau-palier-2"):"Bull",
 (3,"adoryll-palier-3"):"Adoryll, the Caged Bird",(3,"alpha-des-bois-palier-3"):"Woodland Alpha",
 (3,"araignee-luminescente-palier-3"):"Luminescent Spider",(3,"araignee-noir-palier-3"):"Black Spider",(3,"araignee-spectrale-palier-3"):"Shadow Spider",
 (3,"araignee-volante-palier-3"):"Flying Spider",(3,"araignee-d-amethyste-palier-3"):"Amethyst Spider",
 (3,"bandit-archer-palier-3"):"Bandit Archer",(3,"bandit-assassin-palier-3"):"Bandit Assassin",(3,"bandit-robuste-palier-3"):"Sturdy Bandit",
 (3,"chef-de-la-tribu-palier-3"):"Orc Samurai Boss",(3,"chef-des-bandits-palier-3"):"Bandit Chief",(3,"gardien-du-labyrinthe-palier-3"):"Furacas, Guardian of the Labyrinth",
 (3,"gobelin-de-la-caverne-palier-3"):"Goblin Soldier",(3,"gobelin-de-la-caverne-palier-3-2"):"Cave Goblin",(3,"gobelin-de-la-caverne-palier-3-3"):"Goblin Archer",
 (3,"goblin-shaman-palier-3"):"Goblin Shaman",(3,"loup-esclave-palier-3"):"Slave Wolf",(3,"muffet-palier-3"):"Muffet, Mother of Black Spiders",
 (3,"orc-samourai-palier-3"):"Orc Samurai",(3,"orc-shaman-palier-3"):"Orc Shaman",(3,"roi-de-la-caverne-palier-3"):"Cave King",
 (3,"sylnovar-archer-exile-palier-3"):"Sylnovar Archer",(3,"sylnovar-garde-exile-palier-3"):"Sylnovar Guard",(3,"sylnovar-mage-exile-palier-3"):"Sylnovar Mage",
 (3,"sylvaer-archer-exile-palier-3"):"Sylvaer Archer",(3,"sylvaer-garde-corrompu-palier-3"):"Sylvaer Guard",(3,"sylvaer-mage-exile-palier-3"):"Sylvaer Mage",
 (3,"treant-ancien-du-labyrinthe-palier-3"):"Ancient Labyrinth Treant",(3,"treant-juvenile-palier-3"):"Juvenile Treant",(3,"treant-ravageur-palier-3"):"Ravager Treant",(3,"treant-du-labyrinthe-palier-3"):"Labyrinth Treant",
}
GUESS = {"Goblin Soldier","Cave Goblin","Goblin Archer","Orc Samurai Boss","Bull"}
BOSS = {"Adoryll, the Caged Bird","Woodland Alpha","Orc Samurai Boss","Bandit Chief","Furacas, Guardian of the Labyrinth","Muffet, Mother of Black Spiders","Cave King"}
# not used: Kobold_sentinel_em_summoned (same model as the sentinel; its numbers are added to Kobold Sentinel),
# Jeune pousse (no image), Nerius the Evil Treant (not on the site)

def main(src):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = json.load(open(os.path.join(src, "news.json"), encoding="utf-8"))
    os.makedirs(os.path.join(root, "img", "mobs"), exist_ok=True)
    by = {"1": {}, "2": {}, "3": {}}; unused = []
    for m in d["monsters"]:
        fl = int(m["floor_en"].split()[-1]); li = m.get("local_img")
        key = (fl, os.path.basename(li)[:-4]) if li else None
        if not li or key not in MAP:
            unused.append((fl, m["name"], li)); continue
        name = MAP[key]
        im = Image.open(os.path.join(src, li)).convert("RGBA"); im = im.crop(im.getchannel("A").getbbox())
        s = max(im.size); sq = Image.new("RGBA", (s + 8, s + 8), (0, 0, 0, 0)); sq.paste(im, ((s + 8 - im.width) // 2, (s + 8 - im.height) // 2))
        sq = sq.resize((128, 128), Image.LANCZOS)
        flip = name in BOSS
        if flip: sq = sq.transpose(Image.FLIP_LEFT_RIGHT)
        fn = "img/mobs/f%d_%s.png" % (fl, re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_"))
        sq.save(os.path.join(root, fn), optimize=True)
        e = {"f": fn, "fr": m["name"], "ch": [c["raw"] for c in m.get("changes_en", [])], "v": m.get("verdict_en", "")}
        if flip: e["flip"] = 1
        if name in GUESS: e["guess"] = 1
        by[str(fl)][name] = e
    for m in d["monsters"]:
        if m["name"].startswith("Kobold_sentinel"):
            by["1"]["Kobold Sentinel"]["ch"] += ["（Kobold_sentinel_em_summoned）" + c["raw"] for c in m["changes_en"]]
    meta = {"src": {"title": d["title_en"], "title_fr": d["title"], "url": d["url_en"], "date": "2026-10-28"}, "by": by}
    open(os.path.join(root, "mobphotos.js"), "w", encoding="utf-8").write(
        "/* 官網新聞〈" + d["title_en"] + "〉（2026-10-28）的怪物圖片（200×200 透明 PNG → 裁邊、縮成 128px，首領左右翻轉成臉朝右）和平衡調整數值。\n"
        "   tools/build_mobphotos.py 產生，不要手改。使用者 2026-11-06 選 A（全用）、「首領圖片改都不朝左」。guess=1：官網名稱和本站不同，依外觀對應。 */\n"
        "window.SAO_MOBPHOTO=" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("images:", sum(len(v) for v in by.values()), "unused:", unused)

if __name__ == "__main__":
    main(sys.argv[1])
