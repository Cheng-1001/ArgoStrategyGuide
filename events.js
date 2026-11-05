/* Limited-time events shown on the site. Source: official news (saominecraft.com/news), facts only, text rewritten in Chinese.
   dungeons: event dungeons listed first in the 地下城 tab on every floor (no coordinates yet: the announcement has none).
   eqPatch: balance changes announced in the news before the official item catalogue is updated
            (only items whose name AND "before" values match the catalogue; user 2026-11-05: 公告有調整就先修，不用等圖鑑).
   Keep item / monster / NPC names in English as written in the announcement. */
window.SAO_EVENTS = {
 dungeons: [{
  id: "souls",
  n: "Sanctuary of Souls",
  zh: "萬聖節活動地下城",
  ev: "萬聖節活動（2026，10/31 開始）",
  src: { title: "Halloween: the Sanctuary of Souls opens its doors", url: "https://saominecraft.com/news/halloween-le-sanctuaire-des-ames-ouvre-ses-portes", date: "2026-11-04" },
  players: "1～4 人",
  bosses: [
   ["Cursed Valdor", "守在儀式法陣旁"],
   ["Skeleton Colossus", "等級 30，坐在王座上的最終首領，這次活動最強的敵人"]
  ],
  chest: ["每位玩家必得 Halloween Gift", "10% 機率得到 Spectral Crystal（萬聖節轉蛋的免費貨幣）"],
  zones: [
   { n: "1", mobs: ["Blind Jaw", "Varagor", "Stonehorn"], leader: "Svarg the Ash Eater", frag: "Soul Shard" },
   { n: "2", mobs: ["Hafu Demon", "Magic Demon", "Rogue Demon"], leader: "Warlock Imp", frag: "Ritual Ectoplasm" },
   { n: "3", mobs: ["Imp Minion", "Armored Imp", "Cursed Valdor"], leader: "the Archdemon", frag: "Eternal Shadow" }
  ],
  fragRate: "一般惡魔 3%、菁英 8%、首領（Svarg、Warlock Imp）必掉、the Archdemon 掉 1～2 個。每個惡魔區只掉自己那一種碎片，三區都要去。",
  key: { n: "Sanctuary of Souls Key", npc: "Halloween Exchanger", where: "地下城告示牌旁邊", mats: [["Soul Shard", 1], ["Ritual Ectoplasm", 1], ["Eternal Shadow", 1]], note: "進場時消耗" },
  loop: ["在三個惡魔區打出三種碎片", "到 Halloween Exchanger 換鑰匙，打通 Sanctuary of Souls", "寶箱有機率給 Spectral Crystal，3 個可以抽一次萬聖節轉蛋", "轉蛋抽到 Dark Gift Pumpkin，拿去 Halloween Forge 換武器"],
  banner: {
   cost: "200 Triggium 或 3 Spectral Crystal 抽一次",
   rows: [
    ["普通", "Halloween Gift", "72%"],
    ["史詩", "Witch Broom、Pumpkin Knight 坐騎卷軸，Pumpkin King、Soul Reaper 稱號", "18%（各 4.5%）"],
    ["傳說", "Dark Gift Pumpkin、Witch Grimoire、Mutant Pumpkin", "8%（4.5%／2%／1.5%）"],
    ["神話", "6 種萬聖節終極技能卷軸、Echo Will-o'-the-Wisp", "2%（各 0.25%／0.5%）"]
   ],
   pity: "保底：第 20 抽前必出史詩、第 80 抽前必出傳說、第 90 抽前必出神話。"
  },
  forge: {
   npc: "Halloween Blacksmith",
   rows: [
    ["Flayed Blade", "戰士、刺客", 5, null],
    ["Butcher Cleaver", "戰士", 5, 10],
    ["Gore Parasite Greatsword", "戰士", 5, 10],
    ["Infernal Crucible", "戰士", 5, null],
    ["Blunderbuss of the Outer Gods", "弓箭手", 5, 10],
    ["Twinflame Scepter", "法師", 5, null],
    ["Staff of Wandering Souls", "法師", 5, 10],
    ["Scepter of the Risen Dead", "薩滿", 5, 8]
   ],
   extra: "Grappling Hook、Grappling Anchor（限弓箭手）各 3 個 Dark Gift Pumpkin。",
   lvNote: "需求等級是同一篇公告的平衡調整（原本都是 13）；Blunderbuss of the Outer Gods 的第 3 招傷害 20 → 5。另外 Archdemon Blade 需求等級 13 → 10。空白＝公告沒寫。"
  },
  soon: ["現有武器升級成第 2 層版本：公告寫「明天晚上」開放（法國時間 11/5 晚上），要先通關第 2 層才能用，NPC 會一直在，不用急。",
         "舊的萬聖節武器換成新武器：同樣是「明天晚上」開放。"]
 }],
 eqPatch: {
  src: { title: "Halloween: the Sanctuary of Souls opens its doors", url: "https://saominecraft.com/news/halloween-le-sanctuaire-des-ames-ouvre-ses-portes", date: "2026-11-04" },
  items: {
   "1484": { en: "Corrupted Mask", set: { "Max Health": -20, "Skill Damage": 3, "Critical Strike Chance": 3, "Critical Strike Power": 3, "Skill Critical Strike Chance": 3, "Skill Critical Strike Power": 3, "Weapon Damage": 3 },
             note: "公告寫的調整前數值是 5（最大生命 −50 相同），官網圖鑑是 10；調整後的數值以公告為準。" },
   "1405": { en: "Necromancer's Mask", set: { "Max Health": 45, "Defense": 10 } },
   "1406": { en: "Lunar Dragon Mask", set: { "Max Health": 45, "Defense": 10, "Critical Strike Chance": 0, "Skill Critical Strike Power": 5 } },
   "1508": { en: "Simple Boots", set: { "Magic Damage": -15, "Physical Damage": -15, "Projectile Damage": -15 } },
   "1509": { en: "Superior Boots", set: { "Magic Damage": -20, "Physical Damage": -20, "Projectile Damage": -20 } },
   "1511": { en: "Explorer's Boots", set: { "Magic Damage": -25, "Physical Damage": -25, "Projectile Damage": -25 } }
  },
  unmatched: "Lostvayne、Rhitta、Wild Gloves、Amethyst Boots、Ancient Wood Catalyst、Ancient Wood Lantern 也有調整，但官網圖鑑找不到名稱和調整前數值都對得上的物品（可能是不同階段的版本），先不改。"
 }
};
