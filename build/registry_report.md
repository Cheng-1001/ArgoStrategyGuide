# 引用檢查報告（R0.5 階段 1）

由 `python3 tools/check_refs.py` 產生，內容是建置當下的結果；Apps Script 之後收錄的回報（W11）要等下一次建置才反映。

## 結果

| 代號 | 數量 | 在例外清單上 | 不在例外清單上 |
| --- | --- | --- | --- |
| E1 | 87 | 87 | 0 |
| E2 | 28 | 28 | 0 |
| E3 | 1 | 1 | 0 |
| E6 | 0 | 0 | 0 |
| E7 | 0 | 0 | 0 |
| E9 | 0 | 0 | 0 |

建置判定：**通過**

## 來源覆蓋（G1，和例外分開統計）

欄位簽名 561 個：掃描 62、排除 499、沒有登記 0（E9）。

| 欄位 | 結論 | 列數 |
| --- | --- | --- |
| `NPC_NOTE{key}` | resolved | 17 |
| `SAO.BOSS_SPAWNS[][0]` | resolved | 23 |
| `SAO.ITEMS{}.fr` | ambiguous | 1 |
| `SAO.ITEMS{}.fr` | excluded-row | 55 |
| `SAO.ITEMS{}.fr` | no-catalogue | 2 |
| `SAO.ITEMS{}.fr` | resolved | 68 |
| `SAO.M[].drops[][0]` | resolved | 109 |
| `SAO.M[].zone` | resolved | 67 |
| `SAO.QUESTS[].bonus` | excluded-row | 49 |
| `SAO.QUESTS[].bonus` | resolved | 2 |
| `SAO.QUESTS[].kill[0][]` | resolved | 16 |
| `SAO.QUESTS[].need[][0]` | resolved | 70 |
| `SAO.QUESTS[].npc` | quest-npc | 51 |
| `SAO.QUESTS[].town` | resolved | 51 |
| `SAO.SPOTS[].dg.loot[][0]` | resolved | 27 |
| `SAO.SPOTS[].dg.loot[][0]` | unresolved | 2 |
| `SAO.SPOTS[].dg.loot[][1]` | excluded-row | 22 |
| `SAO.SPOTS[].dg.loot[][1]` | resolved | 7 |
| `SAO.SPOTS[].items[]` | resolved | 10 |
| `SAO.SPOTS[].mons[]` | resolved | 60 |
| `SAO23.extra{key}` | resolved | 49 |
| `SAO23.floors{}.BOSS_SPAWNS[][0]` | resolved | 15 |
| `SAO23.floors{}.M[].drops[][0]` | resolved | 258 |
| `SAO23.floors{}.M[].zone` | resolved | 137 |
| `SAO23.floors{}.spots[].dg.loot[][0]` | resolved | 5 |
| `SAO23.floors{}.spots[].dg.loot[][1]` | excluded-row | 5 |
| `SAO23.floors{}.spots[].mons[]` | resolved | 108 |
| `SAO23.floors{}.spots[].zone` | resolved | 22 |
| `SAO23.floors{}.spots[].zone[]` | resolved | 2 |
| `SAO23_ITEMS{}[0]` | excluded-row | 18 |
| `SAO23_ITEMS{}[0]` | no-catalogue | 1 |
| `SAO23_ITEMS{}[0]` | resolved | 117 |
| `SAO_BOSSES.world[].roulette0[][0]` | resolved | 3 |
| `SAO_BOSSES.world[].roulette0[][0]` | unresolved | 4 |
| `SAO_BOSSES.world[].roulette0[][1]` | excluded-row | 7 |
| `SAO_BOSSES.world[].roulette[][0]` | resolved | 3 |
| `SAO_BOSSES.world[].roulette[][0]` | unresolved | 7 |
| `SAO_BOSSES.world[].roulette[][1]` | excluded-row | 10 |
| `SAO_BUYBACK.items{key}` | resolved | 13 |
| `SAO_BUYBACK.items{key}` | unresolved | 1 |
| `SAO_BUYBACK.items{}[][0]` | resolved | 60 |
| `SAO_BUYBACK.shops{key}` | resolved | 13 |
| `SAO_BUYBACK.shops{key}` | unresolved | 1 |
| `SAO_CODEX{}{key}` | resolved | 33 |
| `SAO_EVENTS.dungeons[].dg.loot[][0]` | resolved | 4 |
| `SAO_EVENTS.dungeons[].dg.loot[][0]` | unresolved | 3 |
| `SAO_EVENTS.dungeons[].dg.loot[][1]` | excluded-row | 3 |
| `SAO_EVENTS.dungeons[].dg.loot[][1]` | resolved | 4 |
| `SAO_EVENTS.eqPatch.items{key}` | resolved | 6 |
| `SAO_EVENTS.eqPatch.items{}.en` | resolved | 6 |
| `SAO_GACHA.banners[].items[].en` | resolved | 7 |
| `SAO_GACHA.banners[].items[].en` | unresolved | 19 |
| `SAO_GACHA.banners[].items[].id` | resolved | 2 |
| `SAO_GAMEICONS{key}` | resolved | 96 |
| `SAO_GAMEICONS{key}` | unresolved | 6 |
| `SAO_GAMEINFO.items[].obt[]` | ambiguous | 15 |
| `SAO_GAMEINFO.items[].obt[]` | excluded-row | 113 |
| `SAO_GAMEINFO.items[].obt[]` | resolved | 188 |
| `SAO_GAMEINFO.items[].obt[]` | term | 19 |
| `SAO_GAMEINFO.items[].obt[]` | unresolved | 28 |
| `SAO_GAMEINFO.items[].oid[]` | resolved | 199 |
| `SAO_GAMEINFO.items[].site` | excluded-row | 239 |
| `SAO_GAMEINFO.items[].site` | resolved | 19 |
| `SAO_GAMESTATS.items{key}` | resolved | 115 |
| `SAO_HINTS{}{key}` | resolved | 49 |
| `SAO_MAINQ{}[].npc` | excluded-row | 43 |
| `SAO_MAINQ{}[].npc` | quest-npc | 34 |
| `SAO_MOBPHOTO.by{}{key}` | resolved | 133 |
| `SAO_MOBRENDER.by{}{key}` | resolved | 55 |
| `SAO_NPC_CALC{key}` | resolved | 41 |
| `SAO_RECICONS{key}` | resolved | 19 |
| `SAO_RECIPES{key}` | ambiguous | 1 |
| `SAO_RECIPES{key}` | resolved | 74 |
| `SAO_RECIPES{}.items[][0]` | excluded-row | 69 |
| `SAO_RECIPES{}.items[][0]` | resolved | 182 |
| `SAO_RECIPES{}.items[][1]` | excluded-row | 182 |
| `SAO_RECIPES{}.items[][1]` | resolved | 65 |
| `SAO_RECIPES{}.items[][1]` | unresolved | 4 |
| `SAO_RECIPES{}.items[][3][][0]` | ambiguous | 2 |
| `SAO_RECIPES{}.items[][3][][0]` | resolved | 392 |
| `SAO_RECIPES{}.items[][3][][0]` | unresolved | 3 |
| `SAO_SETS.potions[].name` | resolved | 58 |
| `SAO_SETS.potions[].name` | unresolved | 5 |
| `SAO_SETS.sets[].members[]` | ambiguous | 1 |
| `SAO_SETS.sets[].members[]` | resolved | 129 |
| `SAO_SETS.sets[].members[]` | unresolved | 3 |
| `SAO_ZHNAMES.items[].ids[]` | excluded-row | 40 |
| `SAO_ZHNAMES.items[].ids[]` | resolved | 560 |
| `SAO_ZHNAMES.items[].ids[]` | unresolved | 1 |
| `SAO_ZHNAMES.mobsByName{key}` | resolved | 74 |
| `SAO_ZHNAMES.mobs{key}` | resolved | 46 |
| `SAO_ZHNAMES.npcEn{key}` | ambiguous | 1 |
| `SAO_ZHNAMES.npcEn{key}` | resolved | 24 |
| `SAO_ZHNAMES.npcs{key}` | ambiguous | 5 |
| `SAO_ZHNAMES.npcs{key}` | quest-npc | 20 |
| `SAO_ZHNAMES.npcs{key}` | resolved | 48 |
| `SAO_ZHNAMES.places{key}` | ambiguous | 2 |
| `SAO_ZHNAMES.places{key}` | resolved | 36 |
| `SAO_ZHNAMES.places{key}` | unresolved | 1 |
| `SAO_ZHNAMES.quests{key}` | resolved | 40 |
| `SAO_ZHNAMES.sets{key}` | resolved | 18 |

排除的欄位（理由、處理階段、欄位數）：

- NPC 的遊戲商店名／英法文名（名字索引的一部分，被引用的一方）；—；2 個：`SAO_BUYBACK.shops{}`、`SAO_ZHNAMES.npcEn{}`
- NPC 紀錄本身（被引用的一方）；—；1 個：`SAO_NPCS{}[][1]`
- 不是引用（數值、座標、說明文字、日期、旗標）；—；168 個：`SAO.BOSS_SPAWNS[][1]`、`SAO.BOSS_SPAWNS[][2]`、`SAO.BOSS_SPAWNS[][3]`、`SAO.ITEMS{}.cat`、`SAO.ITEMS{}.dmg`、`SAO.ITEMS{}.ic`、`SAO.ITEMS{}.icsrc`、`SAO.ITEMS{}.id`、`SAO.ITEMS{}.locked`、`SAO.ITEMS{}.lore`、`SAO.ITEMS{}.lv`、`SAO.ITEMS{}.note`、`SAO.ITEMS{}.r`、`SAO.ITEMS{}.set.tiers[][0]`、`SAO.ITEMS{}.set.tiers[][1]`、`SAO.ITEMS{}.src`、`SAO.ITEMS{}.st`、`SAO.ITEMS{}.st{key}`、`SAO.ITEMS{}.st{}`、`SAO.ITEMS{}.use[]`、`SAO.ITEMS{}.vanilla`、`SAO.MAP`、`SAO.M[].beh`、`SAO.M[].diff`、`SAO.M[].drops[][1]`、`SAO.M[].icon`、`SAO.M[].id`、`SAO.M[].lvShot`、`SAO.M[].note`、`SAO.M[].type`、`SAO.PHOTO{}`、`SAO.QUESTS[].id`、`SAO.QUESTS[].kill[1]`、`SAO.QUESTS[].money`、`SAO.QUESTS[].need[][1]`、`SAO.QUESTS[].need[][2]`、`SAO.QUESTS[].src`、`SAO.QUESTS[].x`、`SAO.QUESTS[].xp`、`SAO.QUESTS[].z`、`SAO.STATUS.est.c`、`SAO.STATUS.est.d`、`SAO.STATUS.est.t`、`SAO.STATUS.label.c`、`SAO.STATUS.label.d`、`SAO.STATUS.label.t`、`SAO.STATUS.npc.c`、`SAO.STATUS.npc.d`、`SAO.STATUS.npc.t`、`SAO.STATUS.player.c`、`SAO.STATUS.player.d`、`SAO.STATUS.player.t`、`SAO.STATUS.ref.c`、`SAO.STATUS.ref.d`、`SAO.STATUS.ref.t`、`SAO.STATUS.unk.c`、`SAO.STATUS.unk.d`、`SAO.STATUS.unk.t`、`SAO.STATUS.user.c`、`SAO.STATUS.user.d`、`SAO.STATUS.user.t`、`SAO.ZONES{}.fr`、`SAO.ZONES{}.n`、`SAO.ZONES{}.note`、`SAO.ZONES{}.old`、`SAO.ZONES{}.zh`、`SAO.ZONES{}.zl`、`SAO23.extra{}.note`、`SAO23.extra{}.slot`、`SAO23.extra{}.src`、`SAO23.extra{}.use[]`、`SAO23.floors{}.BOSS_SPAWNS[][1]`、`SAO23.floors{}.BOSS_SPAWNS[][2]`、`SAO23.floors{}.BOSS_SPAWNS[][3]`、`SAO23.floors{}.M[].beh`、`SAO23.floors{}.M[].diff`、`SAO23.floors{}.M[].drops[][1]`、`SAO23.floors{}.M[].drops[][2]`、`SAO23.floors{}.M[].gameDrop`、`SAO23.floors{}.M[].icon`、`SAO23.floors{}.M[].id`、`SAO23.floors{}.M[].lvShot`、`SAO23.floors{}.M[].news`、`SAO23.floors{}.M[].note`、`SAO23.floors{}.M[].num`、`SAO23.floors{}.M[].type`、`SAO23.floors{}.boss`、`SAO23.floors{}.lv`、`SAO23.floors{}.map.blank`、`SAO23.floors{}.map.clip.c`、`SAO23.floors{}.map.clip.r`、`SAO23.floors{}.map.img`、`SAO23.floors{}.map.lo`、`SAO23.floors{}.map.note`、`SAO23.floors{}.map.size`、`SAO23.floors{}.map.x0`、`SAO23.floors{}.map.z0`、`SAO23.floors{}.name`、`SAO23.floors{}.opened`、`SAO23.floors{}.quests[].date`、`SAO23.floors{}.quests[].money`、`SAO23.floors{}.quests[].src`、`SAO23.floors{}.quests[].xp`、`SAO23.floors{}.status`、`SAO23.floors{}.zones{}.n`、`SAO23.floors{}.zones{}.news`、`SAO23.floors{}.zones{}.note`、`SAO23.floors{}.zones{}.zh`、`SAO23.floors{}.zones{}.zhKeep`、`SAO23.unknown{}.note`、`SAO23_ITEMS{}[1]`、`SAO23_ITEMS{}[2]`、`SAO23_ITEMS{}[3]`、`SAO23_ITEMS{}[4]`、`SAO23_ITEMS{}[5]`、`SAO23_ITEMS{}[6]`、`SAO23_ITEMS{}[6]{key}`、`SAO23_ITEMS{}[6]{}`、`SAO23_ITEMS{}[7]`、`SAO_BUYBACK.items{}[][1]`、`SAO_BUYBACK.items{}[][2]`、`SAO_GACHA.banners[].n`、`SAO_GACHA.banners[].note`、`SAO_GACHA.src.date`、`SAO_GACHA.src.title`、`SAO_GACHA.src.url`、`SAO_GAMEINFO.date`、`SAO_GAMEINFO.items[].date`、`SAO_GAMEINFO.items[].desc`、`SAO_GAMEINFO.items[].lvl`、`SAO_GAMEINFO.items[].note`、`SAO_GAMESTATS.date`、`SAO_GAMESTATS.items{}.auc`、`SAO_GAMESTATS.items{}.date`、`SAO_GAMESTATS.items{}.dmg`、`SAO_GAMESTATS.items{}.lvl`、`SAO_GAMESTATS.items{}.r`、`SAO_GAMESTATS.items{}.st`、`SAO_GAMESTATS.items{}.st[][0]`、`SAO_GAMESTATS.items{}.st[][1]`、`SAO_HINTS{}{}[0]`、`SAO_HINTS{}{}[1]`、`SAO_HINTS{}{}[2]`、`SAO_MOBRENDER.src`、`SAO_NPCS{}[][0]`、`SAO_NPCS{}[][2]`、`SAO_NPCS{}[][3]`、`SAO_NPCS{}[][4]`、`SAO_NPCS{}[][5]`、`SAO_NPC_CALC{}.d`、`SAO_NPC_CALC{}.k`、`SAO_NPC_CALC{}.m`、`SAO_NPC_CALC{}.t`、`SAO_RECIPES{}.floor`、`SAO_RECIPES{}.items[][2]`、`SAO_RECIPES{}.items[][3][][1]`、`SAO_RECIPES{}.items[][4]`、`SAO_RECIPES{}.items[][5]`、`SAO_RECIPES{}.items[][6]`、`SAO_RECIPES{}.items[][7]`、`SAO_RECIPES{}.items[][8]`、`SAO_RECIPE_MISS{}`、`SAO_RECIPE_QTY{}`、`SAO_SETS.date`、`SAO_SETS.potions[].effects[]`、`SAO_SETS.sets[].tiers[][0]`、`SAO_SETS.sets[].tiers[][1]`、`SAO_SETS.sets[].zh`
- 世界首領資料（說明、時間、攻擊招式；物品只有輪盤欄位掃描）；階段 2；48 個：`SAO_BOSSES.uniqueRules[]`、`SAO_BOSSES.uniqueWiki[][0]`、`SAO_BOSSES.uniqueWiki[][1]`、`SAO_BOSSES.uniqueWiki[][2]`、`SAO_BOSSES.uniqueWiki[][3]`、`SAO_BOSSES.uniqueWiki[][4]`、`SAO_BOSSES.unique[].attacks[][0]`、`SAO_BOSSES.unique[].attacks[][1]`、`SAO_BOSSES.unique[].available`、`SAO_BOSSES.unique[].floor`、`SAO_BOSSES.unique[].fr`、`SAO_BOSSES.unique[].id`、`SAO_BOSSES.unique[].img`、`SAO_BOSSES.unique[].imgFront`、`SAO_BOSSES.unique[].level`、`SAO_BOSSES.unique[].levelSrc`、`SAO_BOSSES.unique[].name`、`SAO_BOSSES.unique[].note`、`SAO_BOSSES.unique[].phases`、`SAO_BOSSES.unique[].unit`、`SAO_BOSSES.unique[].zh`、`SAO_BOSSES.wikiWorld[][0]`、`SAO_BOSSES.wikiWorld[][1]`、`SAO_BOSSES.wikiWorld[][2]`、`SAO_BOSSES.world[].access`、`SAO_BOSSES.world[].attacks[][0]`、`SAO_BOSSES.world[].attacks[][1]`、`SAO_BOSSES.world[].desc`、`SAO_BOSSES.world[].fr`、`SAO_BOSSES.world[].guaranteed`、`SAO_BOSSES.world[].id`、`SAO_BOSSES.world[].img`、`SAO_BOSSES.world[].imgFront`、`SAO_BOSSES.world[].level`、`SAO_BOSSES.world[].maxPlayers`、`SAO_BOSSES.world[].name`、`SAO_BOSSES.world[].price`、`SAO_BOSSES.world[].queue`、`SAO_BOSSES.world[].rolls`、`SAO_BOSSES.world[].roulette0[][2]`、`SAO_BOSSES.world[].rouletteSrc`、`SAO_BOSSES.world[].roulette[][2]`、`SAO_BOSSES.world[].schedule[].day`、`SAO_BOSSES.world[].schedule[].minutes`、`SAO_BOSSES.world[].schedule[].time`、`SAO_BOSSES.world[].schedule[].zone`、`SAO_BOSSES.world[].weakness`、`SAO_BOSSES.world[].zh`
- 主線標題（被引用的一方）；—；1 個：`SAO_MAINQ{}[].t`
- 主線步驟文字、座標、圖片；階段 4；14 個：`SAO_MAINQ{key}`、`SAO_MAINQ{}[].d`、`SAO_MAINQ{}[].en{key}`、`SAO_MAINQ{}[].en{}`、`SAO_MAINQ{}[].img{key}`、`SAO_MAINQ{}[].img{}[][0]`、`SAO_MAINQ{}[].img{}[][1]`、`SAO_MAINQ{}[].lv`、`SAO_MAINQ{}[].n`、`SAO_MAINQ{}[].s[][0]`、`SAO_MAINQ{}[].s[][1]`、`SAO_MAINQ{}[].s[][2]`、`SAO_MAINQ{}[].s[][3]`、`SAO_MAINQ{}[].tip`
- 主線獎勵（自由文字）；階段 4；1 個：`SAO_MAINQ{}[].rw`
- 主線舊標題（名字索引的一部分）；—；1 個：`SAO_MAINQ{}[].aka`
- 任務原文；階段 4；4 個：`SAO.QUESTS[].raw`、`SAO23.floors{}.quests[].d`、`SAO23.floors{}.quests[].en{key}`、`SAO23.floors{}.quests[].en{}`
- 任務原文裡對不到物品的名稱（已知未知，說明在 note）；階段 4；1 個：`SAO23.unknown{key}`
- 區域 id 本身（被引用的一方）；—；2 個：`SAO.ZONES{key}`、`SAO23.floors{}.zones{key}`
- 區域排序，值是 ZONES 的鍵（網站內部 id）；階段 3；1 個：`SAO.ZONE_ORDER[]`
- 區域排序，值是 zones 的鍵（網站內部 id）；階段 3；1 個：`SAO23.floors{}.order[]`
- 名稱文字（首領、活動怪物、官網新聞的法文名、區域標籤），不在 v5 階段 1 涵蓋表；之後依種類搬家時處理；階段 3／4；19 個：`SAO.SPOTS[].dg.boss`、`SAO.SPOTS[].dg.bossZh`、`SAO.SPOTS[].dg.title`、`SAO23.floors{}.spots[].dg.boss`、`SAO23.floors{}.spots[].dg.bossZh`、`SAO23.floors{}.spots[].dg.title`、`SAO_CODEX{}{}.reg`、`SAO_EVENTS.dungeons[].bosses[][0]`、`SAO_EVENTS.dungeons[].dg.boss`、`SAO_EVENTS.dungeons[].forge.npc`、`SAO_EVENTS.dungeons[].key.npc`、`SAO_EVENTS.dungeons[].zones[].frag`、`SAO_EVENTS.dungeons[].zones[].leader`、`SAO_EVENTS.dungeons[].zones[].mobs[]`、`SAO_MOBPHOTO.by{}{}.old[].fr`、`SAO_MOBPHOTO.by{}{}.rows[].fr`、`SAO_MOBPHOTO.by{}{}.rows[].tw`、`SAO_MOBPHOTO.by{}{}.z[]`、`SAO_ZHNAMES.quests{}.reg`
- 圖示檔路徑；—；2 個：`SAO_MOBRENDER.by{}{}`、`SAO_RECICONS{}`
- 圖示檔路徑（E7 釘選另外檢查）；—；1 個：`SAO_GAMEICONS{}`
- 地點紀錄本身（被引用的一方）或說明文字；—；40 個：`SAO.SPOTS[].area[][0]`、`SAO.SPOTS[].area[][1]`、`SAO.SPOTS[].csrc`、`SAO.SPOTS[].dg.date`、`SAO.SPOTS[].dg.easy[][0]`、`SAO.SPOTS[].dg.easy[][1]`、`SAO.SPOTS[].dg.loot[][2]`、`SAO.SPOTS[].dg.modes[]`、`SAO.SPOTS[].game`、`SAO.SPOTS[].gt`、`SAO.SPOTS[].id`、`SAO.SPOTS[].kind`、`SAO.SPOTS[].n`、`SAO.SPOTS[].note`、`SAO.SPOTS[].nsrc`、`SAO.SPOTS[].old`、`SAO.SPOTS[].src`、`SAO.SPOTS[].tp`、`SAO.SPOTS[].x`、`SAO.SPOTS[].z`、`SAO.SPOTS[].zh`、`SAO23.floors{}.spots[].area[][0]`、`SAO23.floors{}.spots[].area[][1]`、`SAO23.floors{}.spots[].dg.date`、`SAO23.floors{}.spots[].dg.easy[][0]`、`SAO23.floors{}.spots[].dg.easy[][1]`、`SAO23.floors{}.spots[].dg.lootNote`、`SAO23.floors{}.spots[].dg.loot[][2]`、`SAO23.floors{}.spots[].dg.modes[]`、`SAO23.floors{}.spots[].id`、`SAO23.floors{}.spots[].kind`、`SAO23.floors{}.spots[].n`、`SAO23.floors{}.spots[].note`、`SAO23.floors{}.spots[].old`、`SAO23.floors{}.spots[].src`、`SAO23.floors{}.spots[].tp`、`SAO23.floors{}.spots[].u`、`SAO23.floors{}.spots[].x`、`SAO23.floors{}.spots[].z`、`SAO23.floors{}.spots[].zh`
- 城鎮紀錄本身（被引用的一方）；—；17 個：`SAO.TOWNS[].csrc`、`SAO.TOWNS[].id`、`SAO.TOWNS[].n`、`SAO.TOWNS[].note`、`SAO.TOWNS[].old`、`SAO.TOWNS[].tp`、`SAO.TOWNS[].x`、`SAO.TOWNS[].z`、`SAO.TOWNS[].zh`、`SAO23.floors{}.towns[].id`、`SAO23.floors{}.towns[].n`、`SAO23.floors{}.towns[].note`、`SAO23.floors{}.towns[].old`、`SAO23.floors{}.towns[].src`、`SAO23.floors{}.towns[].x`、`SAO23.floors{}.towns[].z`、`SAO23.floors{}.towns[].zh`
- 套裝名稱本身（被引用的一方）；—；1 個：`SAO_SETS.sets[].name`
- 套裝顯示名稱（說明文字）；階段 2；1 個：`SAO.ITEMS{}.set.name`
- 官方中文名本身（名字索引的一部分）；—；5 個：`SAO_ZHNAMES.items[].en`、`SAO_ZHNAMES.items[].fr`、`SAO_ZHNAMES.items[].inf`、`SAO_ZHNAMES.items[].src`、`SAO_ZHNAMES.items[].zh`
- 官方中文名本身（顯示文字）；—；11 個：`SAO_ZHNAMES.date`、`SAO_ZHNAMES.mobsByName{}`、`SAO_ZHNAMES.mobs{}`、`SAO_ZHNAMES.npcs{}`、`SAO_ZHNAMES.places{}`、`SAO_ZHNAMES.quests{}.d`、`SAO_ZHNAMES.quests{}.obj{key}`、`SAO_ZHNAMES.quests{}.obj{}`、`SAO_ZHNAMES.quests{}.zh`、`SAO_ZHNAMES.sets{}`、`SAO_ZHNAMES.terms{}`
- 官網圖鑑匯入的紀錄本身；—；20 個：`SAO_EQUIP[][0]`、`SAO_EQUIP[][1]`、`SAO_EQUIP[][2]`、`SAO_EQUIP[][3]`、`SAO_EQUIP[][4]`、`SAO_EQUIP[][5]`、`SAO_EQUIP[][6]`、`SAO_EQUIP[][7]{key}`、`SAO_EQUIP[][7]{}`、`SAO_EQUIP[][8]`、`SAO_EQUIP[][9]`、`SAO_PROPS[][0]`、`SAO_PROPS[][1]`、`SAO_PROPS[][2]`、`SAO_PROPS[][3]`、`SAO_PROPS[][4]`、`SAO_PROPS[][5]`、`SAO_PROPS[][6]{key}`、`SAO_PROPS[][6]{}`、`SAO_PROPS[][7]`
- 官網新聞的原文、圖片路徑和數值；—；14 個：`SAO_MOBPHOTO.by{}{}.f`、`SAO_MOBPHOTO.by{}{}.lv`、`SAO_MOBPHOTO.by{}{}.old[].ch[]`、`SAO_MOBPHOTO.by{}{}.old[].f`、`SAO_MOBPHOTO.by{}{}.old[].v`、`SAO_MOBPHOTO.by{}{}.rows[].ch[]`、`SAO_MOBPHOTO.by{}{}.rows[].f`、`SAO_MOBPHOTO.by{}{}.rows[].v`、`SAO_MOBPHOTO.srcs{key}`、`SAO_MOBPHOTO.srcs{}.date`、`SAO_MOBPHOTO.srcs{}.title`、`SAO_MOBPHOTO.srcs{}.title_fr`、`SAO_MOBPHOTO.srcs{}.title_tw`、`SAO_MOBPHOTO.srcs{}.url`
- 怪物圖片的鍵（只有 3 張舊圖，網站內部用）；階段 4；1 個：`SAO.PHOTO{key}`
- 怪物紀錄本身（被引用的一方）；—；2 個：`SAO.M[].name`、`SAO23.floors{}.M[].name`
- 怪物舊名（名字索引的一部分）；—；1 個：`SAO.M[].aka[]`
- 支線標題（被引用的一方）；—；2 個：`SAO.QUESTS[].title`、`SAO23.floors{}.quests[].title`
- 數值圖示（鍵是數值名，不是物品）；—；2 個：`SAO_STATICONS{key}`、`SAO_STATICONS{}`
- 更新紀錄文字；—；4 個：`SAO_CHANGELOG[][0]`、`SAO_CHANGELOG[][1][]`、`SAO_CHANGELOG_SUM{key}`、`SAO_CHANGELOG_SUM{}[]`
- 本站物品紀錄本身（被引用的一方）；—；2 個：`SAO.ITEMS{key}`、`SAO23_ITEMS{key}`
- 樓層號碼；—；6 個：`SAO23.floors{key}`、`SAO_CODEX{key}`、`SAO_HINTS{key}`、`SAO_MOBPHOTO.by{key}`、`SAO_MOBRENDER.by{key}`、`SAO_NPCS{key}`
- 活動公告文字、兌換表的數值和職業、碎片表（物品名欄位見 R44，首領／怪物名見 RN）；階段 2；37 個：`SAO_EVENTS.dungeons[].bosses[][1]`、`SAO_EVENTS.dungeons[].chest[]`、`SAO_EVENTS.dungeons[].dg.bossZh`、`SAO_EVENTS.dungeons[].dg.date`、`SAO_EVENTS.dungeons[].dg.easy[][0]`、`SAO_EVENTS.dungeons[].dg.easy[][1]`、`SAO_EVENTS.dungeons[].dg.loot[][2]`、`SAO_EVENTS.dungeons[].dg.modes[]`、`SAO_EVENTS.dungeons[].ev`、`SAO_EVENTS.dungeons[].forge.extra`、`SAO_EVENTS.dungeons[].forge.lvNote`、`SAO_EVENTS.dungeons[].forge.rows[][1]`、`SAO_EVENTS.dungeons[].forge.rows[][2]`、`SAO_EVENTS.dungeons[].forge.rows[][3]`、`SAO_EVENTS.dungeons[].fragRate`、`SAO_EVENTS.dungeons[].id`、`SAO_EVENTS.dungeons[].key.mats[][1]`、`SAO_EVENTS.dungeons[].key.n`、`SAO_EVENTS.dungeons[].key.note`、`SAO_EVENTS.dungeons[].key.where`、`SAO_EVENTS.dungeons[].loop[]`、`SAO_EVENTS.dungeons[].n`、`SAO_EVENTS.dungeons[].notes[]`、`SAO_EVENTS.dungeons[].players`、`SAO_EVENTS.dungeons[].soon[]`、`SAO_EVENTS.dungeons[].src.date`、`SAO_EVENTS.dungeons[].src.title`、`SAO_EVENTS.dungeons[].src.url`、`SAO_EVENTS.dungeons[].zh`、`SAO_EVENTS.dungeons[].zones[].n`、`SAO_EVENTS.eqPatch.items{}.note`、`SAO_EVENTS.eqPatch.items{}.set{key}`、`SAO_EVENTS.eqPatch.items{}.set{}`、`SAO_EVENTS.eqPatch.src.date`、`SAO_EVENTS.eqPatch.src.title`、`SAO_EVENTS.eqPatch.src.url`、`SAO_EVENTS.eqPatch.unmatched`
- 結構化的物品名欄位（地下城鑰匙名、活動兌換材料、兌換武器）：v5 階段 1 涵蓋表沒有列，階段 1 不掃描（P1 初審 S4，交站長決定要不要改成掃描）；階段 2；5 個：`SAO.SPOTS[].dg.key`、`SAO23.floors{}.spots[].dg.key`、`SAO_EVENTS.dungeons[].dg.key`、`SAO_EVENTS.dungeons[].forge.rows[][0]`、`SAO_EVENTS.dungeons[].key.mats[][0]`
- 職業資料（wiki 文字、屬性、技能）；—；33 個：`SAO_CLASSES[].about`、`SAO_CLASSES[].base[][0]`、`SAO_CLASSES[].base[][1]`、`SAO_CLASSES[].diff`、`SAO_CLASSES[].ic`、`SAO_CLASSES[].id`、`SAO_CLASSES[].name`、`SAO_CLASSES[].perLv[][0]`、`SAO_CLASSES[].perLv[][1]`、`SAO_CLASSES[].role`、`SAO_CLASSES[].skillsSure`、`SAO_CLASSES[].skills[][0]`、`SAO_CLASSES[].skills[][1]`、`SAO_CLASSES[].skills[][2]`、`SAO_CLASSES[].skills[][3]`、`SAO_CLASSES[].stars[][0]`、`SAO_CLASSES[].stars[][1]`、`SAO_CLASSES[].subs[][0]`、`SAO_CLASSES[].subs[][1]`、`SAO_CLASSES[].talents[][0]`、`SAO_CLASSES[].talents[][1]`、`SAO_CLASSES[].talents[][2]`、`SAO_CLASSES[].talents[][3]`、`SAO_CLASSES[].talents[][4]`、`SAO_CLASSES[].weapons.bow`、`SAO_CLASSES[].weapons.crossbow`、`SAO_CLASSES[].weapons.dagger`、`SAO_CLASSES[].weapons.shield`、`SAO_CLASSES[].weapons.staff_mage`、`SAO_CLASSES[].weapons.staff_shaman`、`SAO_CLASSES[].weapons.sword`、`SAO_CLASSES[].wikiRev`、`SAO_CLASSES[].zh`
- 說明文字；階段 4；2 個：`SAO.QUESTS[].tnote`、`SAO23.floors{}.quests[].steps[]`
- 遊戲取得途徑的商店名（顯示用對照）；階段 3；1 個：`SAO_ZHNAMES.terms{key}`
- 遊戲圖鑑原文；—；2 個：`SAO_CODEX{}{}.desc`、`SAO_CODEX{}{}.n`
- 遊戲圖鑑編號（E3 另外檢查）；—；1 個：`SAO.M[].num`
- 遊戲技能文字和圖示路徑；—；18 個：`SAO_GAMESKILLS{key}`、`SAO_GAMESKILLS{}.date`、`SAO_GAMESKILLS{}.icons{key}`、`SAO_GAMESKILLS{}.icons{}`、`SAO_GAMESKILLS{}.list[].base`、`SAO_GAMESKILLS{}.list[].d`、`SAO_GAMESKILLS{}.list[].dOff`、`SAO_GAMESKILLS{}.list[].data[]`、`SAO_GAMESKILLS{}.list[].dz[]`、`SAO_GAMESKILLS{}.list[].en`、`SAO_GAMESKILLS{}.list[].fr`、`SAO_GAMESKILLS{}.list[].g`、`SAO_GAMESKILLS{}.list[].lore`、`SAO_GAMESKILLS{}.list[].max`、`SAO_GAMESKILLS{}.list[].slot`、`SAO_GAMESKILLS{}.list[].t`、`SAO_GAMESKILLS{}.list[].zh`、`SAO_GAMESKILLS{}.lv`
- 遊戲英文名（名字索引的一部分）；—；1 個：`SAO_GAMEINFO.items[].en`
- 遊戲英文名（小寫，W7 跨檔線索用）；—；1 個：`SAO_GAMESTATS.items{}.en`
- 配方產量的鍵（NPC|產出，網站內部組合鍵）；階段 2；2 個：`SAO_RECIPE_MISS{key}`、`SAO_RECIPE_QTY{key}`

## 錯誤清單

### E1（87）

| 檔案 | 鍵 | 行 | 原因 | 例外 |
| --- | --- | --- | --- | --- |
| bosses.js | `boss:galiath/roulette0:1,000 Cols purse` | 26 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| bosses.js | `boss:galiath/roulette0:500 Triggiums` | 30 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| bosses.js | `boss:galiath/roulette0:Colossus Fragments` | 25 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| bosses.js | `boss:galiath/roulette0:Galiath's Core` | 27 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| bosses.js | `boss:galiath/roulette:1,000 Cols purse` | 26 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| bosses.js | `boss:galiath/roulette:500 Triggiums` | 30 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| bosses.js | `boss:galiath/roulette:Colossus Fragments` | 25 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| bosses.js | `boss:galiath/roulette:Colossus Helmet` | 28 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| bosses.js | `boss:galiath/roulette:Colossus Left Blade` | 31 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| bosses.js | `boss:galiath/roulette:Colossus Right Blade` | 32 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| bosses.js | `boss:galiath/roulette:Galiath's Core` | 27 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| buyback.js | `buyback-npc:Local Farmer` | 6 | 解析不到：沒有對得上的 NPC | 有 |
| data.js | `F1/spot:fallen/loot:500 Cols Pouch` | 391 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| data.js | `F1/spot:geldorakd/loot:250 Cols Pouch` | 389 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| events.js | `event:dg/loot:回響鬼火` | 46 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| events.js | `event:dg/loot:幽靈水晶` | 18 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| events.js | `event:dg/loot:萬聖節禮物` | 18 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:Aincrad 轉蛋/Greater Healing Crystal` | 11 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:Aincrad 轉蛋/Greater Mana Crystal` | 11 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:Aincrad 轉蛋/Greater Stamina Crystal` | 11 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:Aincrad 轉蛋/Superior Power Crystal` | 11 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Dark Gift Pumpkin` | 17 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Echo Will-o'-the-Wisp` | 17 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Halloween Gift` | 18 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Scroll: Gate of Souls (Earth)` | 16 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Scroll: Gate of Souls (Lightning)` | 16 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Scroll: Headless Ride` | 15 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Scroll: Hunter's Moon` | 15 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Scroll: Lights Out` | 15 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Scroll: Mutant Pumpkin` | 18 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Scroll: Pumpkin Knight` | 18 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Scroll: Witch's Broom` | 18 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Scroll: Witch's Cauldron` | 15 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Title: Pumpkin King` | 17 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Title: Soul Reaper` | 17 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gacha.js | `gacha:萬聖節轉蛋/Witch's Grimoire` | 16 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gameicons.js | `gameicons:Boar of Gluttony Candy` | 63 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gameicons.js | `gameicons:Halloween Candy Corn` | 64 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gameicons.js | `gameicons:Lion of Pride Candy` | 65 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gameicons.js | `gameicons:Pumpkin Caramel` | 66 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gameicons.js | `gameicons:Slime Tear` | 81 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gameicons.js | `gameicons:Training Dagger (2)` | 88 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| gameinfo.js | `gameinfo:Allium Flower/bought-back-by:F1 Local Farmer - Near the Starting City` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Bottes de l'Explorateur/crafted-at:P3 - Craft Bottes de l'Explorateur` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Ceinture de la Tribu/crafted-at:P3 - Craft Artefact Ceinture Orc` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Chipped Axe/sold-by:F1 - Starting City - Tools` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Clé de Melliona/sold-by:戰利品資訊-蜜蜂地下城` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Corrupted Fragment/loot:Gobelin Archer` | 4 | 解析不到：沒有對得上的怪物 | 有 |
| gameinfo.js | `gameinfo:Corrupted Fragment/loot:Gobelin Shaman` | 4 | 解析不到：沒有對得上的怪物 | 有 |
| gameinfo.js | `gameinfo:Corrupted Fragment/loot:Spectral Spider` | 4 | 解析不到：沒有對得上的怪物 | 有 |
| gameinfo.js | `gameinfo:Cracked Pickaxe/sold-by:F1 - Starting City - Tools` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Forest Key/crafted-at:F1 - Geldorack Dungeon Guard - Starting City` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Key of Xal'Zirith/crafted-at:F1 - Xal'Zirith Dungeon Guard - Candélia` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Key of the Fallen/crafted-at:F1 - Labyrinth of the Fallen Dungeon Guard - Tolbana` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Nodachi/crafted-at:Nodachi Altar` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Occult Amulet/sold-by:Secret Occult Amulet` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Occult Bracelet/sold-by:Secret Occult Bracelet` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Occult Gloves/sold-by:Secret Occult Gloves` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Occult Hood/sold-by:Secret Occult Artifacts` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Occult Ring/sold-by:Secret Occult Ring` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Occult Robe/sold-by:Secret Occult Artifacts` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Occult Skull/sold-by:Secret Occult Artifacts` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Resurrection Crystal/loot:NICOLASBOSS` | 4 | 解析不到：沒有對得上的怪物 | 有 |
| gameinfo.js | `gameinfo:Sang de Bête Corrompu/crafted-at:P3 - Refaçonneur Matériaux` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Scroll of Mastery/sold-by:P3 - Marchand de Consommables` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Scroll of Reallocation/sold-by:P3 - Marchand de Consommables` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Wheat/bought-back-by:F1 Local Farmer - Near the Starting City` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:Wooden Fishing Rod/sold-by:F1 - Starting City - Tools` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:獵人紫水晶護腿/crafted-at:P3 - Craft Armure d'Améthyste` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| gameinfo.js | `gameinfo:獵人紫水晶靴/crafted-at:P3 - Craft Armure d'Améthyste` | 4 | 解析不到：沒有對得上的 NPC | 有 |
| recipes.js | `recipe:3\|Adventurer's Shoemaker/Bottes de l'Aventurier/mat:磨損皮革` | 4237 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| recipes.js | `recipe:3\|Refaiter/out:冷杉細繩` | 4148 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| recipes.js | `recipe:3\|Refaiter/out:金合歡細繩` | 4208 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| recipes.js | `recipe:Iron Accessories/Iron Amulet/mat:Iron String` | 1262 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| recipes.js | `recipe:Secret Gelatinous Cloak/Gelatinous Cloak/mat:Slime Tear` | 1687 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| recipes.js | `recipe:Sewer Reshaper/out:Slime Tear` | 1687 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| recipes.js | `recipe:Starting Merchant/out:Training Dagger (2)` | 2333 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| sets.js | `potion:Boar of Gluttony Candy` | 110 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| sets.js | `potion:Effective Repair Kit` | 114 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| sets.js | `potion:Halloween Candy Corn` | 107 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| sets.js | `potion:Lion of Pride Candy` | 111 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| sets.js | `potion:Pumpkin Caramel` | 106 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| sets.js | `set:Stealthy Herald Set/member:Boots of the Herald` | 46 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| sets.js | `set:Stealthy Herald Set/member:Tunic of the Herald` | 46 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| sets.js | `set:Tenacious Necromancer Set/member:Helmet of the Tenacious Necromancer` | 50 | 解析不到：沒有任何物品紀錄、官網名或遊戲名對得上 | 有 |
| zhnames.js | `zhnames.places:Lair of Asterius` | 25 | 解析不到：沒有對得上的地點 | 有 |
| zhnames.js | `zhnames:蜘蛛毒液/i\|Spider Venom` | 293 | 解析不到：「i\|」指到的本站物品表（ITEMS）鍵不存在 | 有 |

### E2（28）

| 檔案 | 鍵 | 行 | 原因 | 例外 |
| --- | --- | --- | --- | --- |
| data.js | `Cursed Skeleton Shaman Staff/fr` | 170 | 對到 2 個不同的實體：2592 Spectre Maudit（裝備）、2717 Spectre Maudit（裝備） | 有 |
| gameinfo.js | `gameinfo:Bandit's Dagger/loot:Bandit Assassin` | 4 | 對到 2 個不同的實體：M1:m31、M3:f3m17 | 有 |
| gameinfo.js | `gameinfo:Bone Dust/bought-back-by:Shop - Cursed Ruins` | 4 | 對到 2 個不同的實體：N1:4:Cursed Ruins - Loot Buyer、N1:5:Cursed Ruins - Loot Buyer (2) | 有 |
| gameinfo.js | `gameinfo:Crossbow of the Bandits/loot:Bandit Archer` | 4 | 對到 2 個不同的實體：M1:m30、M3:f3m19 | 有 |
| gameinfo.js | `gameinfo:Cursed Cloth/bought-back-by:Shop - Cursed Ruins` | 4 | 對到 2 個不同的實體：N1:4:Cursed Ruins - Loot Buyer、N1:5:Cursed Ruins - Loot Buyer (2) | 有 |
| gameinfo.js | `gameinfo:Health Potion II/sold-by:Shop - Cursed Ruins` | 4 | 對到 2 個不同的實體：N1:4:Cursed Ruins - Loot Buyer、N1:5:Cursed Ruins - Loot Buyer (2) | 有 |
| gameinfo.js | `gameinfo:Metal Soul Piece/bought-back-by:F1 - Labyrinth of the Forgotten - Loot Buyer` | 4 | 對到 2 個不同的實體：N1:10:Labyrinth of the Fallen - Loot Buyer、N1:9:Labyrinth of the Fallen (2) - Loot Buyer | 有 |
| gameinfo.js | `gameinfo:Piece of Spectral Mane/bought-back-by:Shop - Cursed Ruins` | 4 | 對到 2 個不同的實體：N1:4:Cursed Ruins - Loot Buyer、N1:5:Cursed Ruins - Loot Buyer (2) | 有 |
| gameinfo.js | `gameinfo:Reinforced Skeleton Bone/bought-back-by:Shop - Cursed Ruins` | 4 | 對到 2 個不同的實體：N1:4:Cursed Ruins - Loot Buyer、N1:5:Cursed Ruins - Loot Buyer (2) | 有 |
| gameinfo.js | `gameinfo:Ring of Narax/bought-back-by:Shop - Cursed Ruins` | 4 | 對到 2 個不同的實體：N1:4:Cursed Ruins - Loot Buyer、N1:5:Cursed Ruins - Loot Buyer (2) | 有 |
| gameinfo.js | `gameinfo:Skeleton Bone/bought-back-by:Shop - Cursed Ruins` | 4 | 對到 2 個不同的實體：N1:4:Cursed Ruins - Loot Buyer、N1:5:Cursed Ruins - Loot Buyer (2) | 有 |
| gameinfo.js | `gameinfo:Soul of the Herald/bought-back-by:F1 - Labyrinth of the Forgotten - Loot Buyer` | 4 | 對到 2 個不同的實體：N1:10:Labyrinth of the Fallen - Loot Buyer、N1:9:Labyrinth of the Fallen (2) - Loot Buyer | 有 |
| gameinfo.js | `gameinfo:Soul of the Reaper/bought-back-by:F1 - Labyrinth of the Forgotten - Loot Buyer` | 4 | 對到 2 個不同的實體：N1:10:Labyrinth of the Fallen - Loot Buyer、N1:9:Labyrinth of the Fallen (2) - Loot Buyer | 有 |
| gameinfo.js | `gameinfo:Soul of the Ruins/bought-back-by:Shop - Cursed Ruins` | 4 | 對到 2 個不同的實體：N1:4:Cursed Ruins - Loot Buyer、N1:5:Cursed Ruins - Loot Buyer (2) | 有 |
| gameinfo.js | `gameinfo:Soul of the Warden/bought-back-by:F1 - Labyrinth of the Forgotten - Loot Buyer` | 4 | 對到 2 個不同的實體：N1:10:Labyrinth of the Fallen - Loot Buyer、N1:9:Labyrinth of the Fallen (2) - Loot Buyer | 有 |
| gameinfo.js | `gameinfo:Stamina Potion II/sold-by:Shop - Cursed Ruins` | 4 | 對到 2 個不同的實體：N1:4:Cursed Ruins - Loot Buyer、N1:5:Cursed Ruins - Loot Buyer (2) | 有 |
| recipes.js | `recipe-npc:3\|Consumables Merchant` | 3292 | 對到 2 個不同的實體：N3:25:Consumables Merchant、N3:26:Consumables Merchant | 有 |
| recipes.js | `recipe:3\|Adventurer's Shoemaker/Bottes de l'Aventurier/mat:狼皮（第 1 或第 2 層，看不出來）` | 4241 | 資料本身寫明看不出是哪一種（已知的多重可能，沒有指定實體） | 有 |
| recipes.js | `recipe:3\|P3 - Craft Anneau Draconique Corrompu/Anneau Draconique Corrompu/mat:腐化碎片（三種之一，看不出是哪一種）` | 4094 | 資料本身寫明看不出是哪一種（已知的多重可能，沒有指定實體） | 有 |
| sets.js | `set:Ika Set/member:Leggings of Ika` | 37 | 對到 2 個不同的實體：1341 Jambières d'Ika（裝備）、1348 Jambières d’Ika（裝備） | 有 |
| zhnames.js | `zhnames.npcEn:Assistant to the Alchemist` | 34 | 對到 2 個不同的實體：N2:1:Assistant to the Alchemist、N3:1:Assistant to the Alchemist | 有 |
| zhnames.js | `zhnames.npcs:Alchemist` | 32 | 對到 3 個不同的實體：N1:0:Alchemist、N2:0:Alchemist、N3:0:Alchemist | 有 |
| zhnames.js | `zhnames.npcs:Assistant to the Alchemist` | 34 | 對到 2 個不同的實體：N2:1:Assistant to the Alchemist、N3:1:Assistant to the Alchemist | 有 |
| zhnames.js | `zhnames.npcs:Auction House` | 37 | 對到 2 個不同的實體：N1:76:Auction House、N3:46:Auction House | 有 |
| zhnames.js | `zhnames.npcs:Consumables Merchant` | 37 | 對到 2 個不同的實體：N3:25:Consumables Merchant、N3:26:Consumables Merchant | 有 |
| zhnames.js | `zhnames.npcs:Vault` | 37 | 對到 2 個不同的實體：N1:79:Vault、N3:45:Vault | 有 |
| zhnames.js | `zhnames.places:Geldorack Mine` | 25 | 對到 2 個不同的實體：P1:spot:geldorak、P1:spot:geldorakd | 有 |
| zhnames.js | `zhnames.places:Virelune` | 25 | 對到 2 個不同的實體：P1:spot:virelune、P1:town:virelune | 有 |

### E3（1）

| 檔案 | 鍵 | 行 | 原因 | 例外 |
| --- | --- | --- | --- | --- |
| recipes.js | `id:1627` |  | 官網 1627 Lanterne d'Entraînement（道具） 掛在 2 筆本站紀錄：Training Lantern、Training Lantern (2) | 有 |

## 提醒（只寫報告）

### W2

- gameinfo 等級：41 件
- gamestats 稀有度：8 件
- gamestats 等級：45 件
- 配方等級：46 件

### W5（91）

- 第 1 層 NPC：Lumberjack ↔ Cabinetmaker（3.6 格）
- 第 1 層 NPC：Cursed Ruins - Loot Buyer ↔ Cursed Ruins - Loot Buyer (2)（223.4 格）
- 第 1 層 NPC：Geldorak Mine Dungeon - Loot Buyer ↔ Mine Archaeologist（4.0 格）
- 第 1 層 NPC：Labyrinth of the Fallen (2) - Loot Buyer ↔ Labyrinth of the Fallen - Loot Buyer（26.9 格）
- 第 1 層 NPC：Labyrinth of the Fallen (2) - Loot Buyer ↔ Labyrinth Archaeologist（0.0 格）
- 第 1 層 NPC：Local Miner ↔ Blacksmith of Copper & Iron Ingots（2.8 格）
- 第 1 層 NPC：Level 1 Weapon Buyer ↔ Level 5 Weapon Buyer（814.7 格）
- 第 1 層 NPC：Level 1 Weapon Buyer ↔ Starting Merchant（2.8 格）
- 第 1 層 NPC：Level 5 Weapon Buyer ↔ Elite Treant Accessories（2.2 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2040.2 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2403.7 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2659.5 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（3443.6 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2074.0 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（3574.2 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2806.3 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（969.5 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（1837.4 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2205.6 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（3102.8 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（3926.5 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2677.4 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（922.1 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（1255.0 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2722.6 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（3180.9 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（1880.5 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（848.8 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2222.2 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2318.5 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（1017.6 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（3019.6 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（2777.2 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（1604.2 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（1638.2 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（1556.2 格）
- 第 1 層 NPC：Traveling Merchant ↔ Traveling Merchant（1305.3 格）
- 第 1 層 NPC：Equipment Merchant ↔ Equipment Merchant（2518.1 格）
- 第 1 層 NPC：Accessories Merchant ↔ Accessories Merchant（3185.2 格）
- 第 1 層 NPC：Occult Merchant - Amulet ↔ Occult Merchant - Bracelet（41.8 格）
- 第 1 層 NPC：Tolbana Weaponsmith ↔ Ice Golem Accessories（2.8 格）
- 第 1 層 NPC：Tolbana Armor Blacksmith ↔ Deer Accessories（2.8 格）
- 第 1 層 NPC：Geldorak Dungeon Guard - Starting Town ↔ Mine Archaeologist（2.2 格）
- 第 1 層 NPC：Copper Accessories ↔ Weapon Recycling（3.0 格）
- 第 1 層 NPC：Deer Accessories ↔ Spider Accessories（1402.6 格）
- 第 1 層 NPC：Slime Accessories ↔ Spider Accessories（2780.8 格）
- 第 1 層 NPC：Slime Accessories ↔ Sylve Accessories（1226.1 格）
- 第 1 層 NPC：Mine Archaeologist ↔ Web Archaeologist（4242.0 格）
- 第 2 層 NPC：Necrotic Loot Repreneur ↔ Necrotic Weaponsmith（3.2 格）
- 第 2 層 NPC：Necrotic Tool Blacksmith ↔ Blacksmith of Necromancer Armor（4.0 格）
- 第 2 層 NPC：Occult Amulet Merchant ↔ Occult Bracelet Merchant（8.2 格）
- 第 2 層 NPC：Refauncher ↔ Refaiter（2.2 格）
- 第 2 層 NPC：Accessories Blacksmith ↔ Scrap Accessories Blacksmith（984.5 格）
- 第 2 層 NPC：Impure Onyx Accessories Blacksmith ↔ Pure Onyx Accessories Blacksmith（858.2 格）
- 第 2 層 NPC：Manufacturer of the Ring of the Drowned Harpy ↔ Manufacturer of the Ring of the Flaming Harpy（163.8 格）
- 第 3 層 NPC：Alchemist ↔ Assistant to the Alchemist（3.6 格）
- 第 3 層 NPC：Loot Buyer Sylnovar ↔ Loot Buyer Sylvaer（741.8 格）
- 第 3 層 NPC：Equipment Merchant ↔ Equipment Merchant（823.4 格）
- 第 3 層 NPC：Occult Rings Merchant ↔ Occult Runes Merchant（886.8 格）
- 第 3 層 NPC：Consumables Merchant ↔ Consumables Merchant（796.1 格）
- 第 3 層 NPC：P3 - Craft Clée des Bois Ancien ↔ P3 - Craft Outils des Bois Anciens（1043.5 格）
- 物品：Amulet of the Nepenthes ↔ Bracelet of the Nepenthes
- 物品：Bear Hide ↔ Boar Hide
- 物品：Blazing Feather ↔ Flaming Feather
- 物品：Cursed Skeleton Mage Staff ↔ Cursed Skeleton Shaman Staff
- 物品：Nodachi Bow ★★ ↔ Nodachi Bow ★★★
- 物品：Nodachi Bow ★★ ↔ Nodachi Bow ★★★★
- 物品：Nodachi Bow ★★ ↔ Nodachi Bow ★★★★★
- 物品：Nodachi Bow ★★★ ↔ Nodachi Bow ★★★★
- 物品：Nodachi Bow ★★★ ↔ Nodachi Bow ★★★★★
- 物品：Nodachi Bow ★★★★ ↔ Nodachi Bow ★★★★★
- 物品：Nodachi Bow ★★★★ ↔ Nodachi ★★★★
- 物品：Nodachi Bow ★★★★★ ↔ Nodachi ★★★★★
- 物品：Nodachi ★★ ↔ Nodachi ★★★
- 物品：Nodachi ★★ ↔ Nodachi ★★★★
- 物品：Nodachi ★★ ↔ Nodachi ★★★★★
- 物品：Nodachi ★★★ ↔ Nodachi ★★★★
- 物品：Nodachi ★★★ ↔ Nodachi ★★★★★
- 物品：Nodachi ★★★★ ↔ Nodachi ★★★★★
- 物品：Sylnovar Essence ↔ Sylvaer Essence
- 物品：Sylnovarian Cloth ↔ Sylvaerian Cloth
- 物品：Sylnovarian Jewel ↔ Sylvaerian Jewel
- 物品：Sylnovarian Leaves ↔ Sylvaerian Leaves
- zhnames 重複條目：g|Kobold Key → 狗頭人之鑰、狗頭人之鑰
- zhnames 重複條目：i|Ravager Branch → 毀滅樹枝、毀滅樹枝
- zhnames 重複條目：p|1835 → 麥葉、麥葉
- zhnames 重複條目：p|1836 → 麥花、麥花
- zhnames 重複條目：p|1837 → 精煉小麥、精煉小麥
- zhnames 重複條目：p|1839 → 薰衣草、薰衣草
- zhnames 重複條目：p|1840 → 紫藤、紫藤
- zhnames 重複條目：p|1841 → 精煉紫紅球花、精煉紫紅球花

### W6（8）

- Daily Stamina Crystal、Stamina Shard
- Dragon of Wrath Candy、Witch's Dragée
- Health Potion I、Health Potion II、Health Potion III
- Mana Potion I、Mana Potion II、Mana Potion III
- Quality Health Potion I、Quality Health Potion II、Quality Health Potion III
- Quality Mana Potion I、Quality Mana Potion II、Quality Mana Potion III
- Quality Stamina Potion I、Quality Stamina Potion II、Quality Stamina Potion III
- Stamina Potion I、Stamina Potion II、Stamina Potion III

### W7（48 筆有候選）

- data.js ITEMS「Christmas Mittens (2)」→ 2048 Moufles de Noël（0.8，英→法字彙）
- data.js ITEMS「Christmas Mittens (3)」→ 2048 Moufles de Noël（0.8，英→法字彙）
- data.js ITEMS「Cursed Skeleton Shaman Staff」→ 2592 Spectre Maudit（1.0，法文相似度）；2717 Spectre Maudit（1.0，法文相似度）；2097 Sceptre Maudit（0.857，法文相似度）
- data.js ITEMS「Frozen Bracelet」→ 1596 Bracelet de Glace（0.8，英→法字彙）
- data.js ITEMS「Ika Armour Set」→ 1341 Jambières d'Ika（0.612，法文相似度）；1348 Jambières d’Ika（0.612，法文相似度）
- data.js ITEMS「Magic Staff of the Revenants」→ 2569 Bâton Magique d'Entraînement（0.667，英→法字彙）；2570 Bâton Magique Sylvestre（0.667，英→法字彙）；2571 Bâton Magique en Cuivre（0.667，英→法字彙）
- data.js ITEMS「Nodachi Bow ★★」→ 1573 Arc Nodachi（1.0，英→法字彙）
- data.js ITEMS「Nodachi Bow ★★★」→ 1573 Arc Nodachi（1.0，英→法字彙）
- data.js ITEMS「Nodachi Bow ★★★★」→ 1573 Arc Nodachi（1.0，英→法字彙）
- data.js ITEMS「Nodachi Bow ★★★★★」→ 1573 Arc Nodachi（1.0，英→法字彙）
- data.js ITEMS「Nodachi Staff」→ 2576 Bâton Magique Nodachi（0.8，英→法字彙）
- data.js ITEMS「Nodachi ★★」→ 2619 Nodachi（1.0，英→法字彙）
- data.js ITEMS「Nodachi ★★★」→ 2619 Nodachi（1.0，英→法字彙）
- data.js ITEMS「Nodachi ★★★★」→ 2619 Nodachi（1.0，英→法字彙）
- data.js ITEMS「Nodachi ★★★★★」→ 2619 Nodachi（1.0，英→法字彙）
- data.js ITEMS「Skull of a Wolf」→ 1469 Crâne de Loup（1.0，英→法字彙）
- data.js ITEMS「Wolf Fur」→ 2175 Fourrure de Loup（1.0，英→法字彙）
- data23.js SAO23_ITEMS「Adoryll's Talons」→ 2351 Serres d''Adoryll（0.97，法文相似度）；1790 Serpe d'Amour（0.69，法文相似度）；2595 Sceptre d'Amour（0.645，法文相似度）
- data23.js SAO23_ITEMS「Corrupted Fragment」→ 2380 Fragment Corrompu（0.8，英→法字彙）
- data23.js SAO23_ITEMS「Corrupted Fragment (2)」→ 2380 Fragment Corrompu（0.667，英→法字彙）
- data23.js SAO23_ITEMS「Occult Amulet」→ 1298 Amulette Occulte（1.0，英→法字彙）
- data23.js SAO23_ITEMS「Occult Amulet (2)」→ 1298 Amulette Occulte（0.8，英→法字彙）
- data23.js SAO23_ITEMS「Occult Ring」→ 1559 Bague Occulte（0.8，英→法字彙）；2486 Anneau Occulte（0.8，英→法字彙）
- gameinfo.js「Boots of the Hunter Necromancer」→ 1404 Bottes du Necromancien（0.8，英→法字彙）
- gameinfo.js「Daily Stamina Crystal」→ 1750 Cristal de Stamina（0.667，英→法字彙）
- gameinfo.js「Frozen Bracelet」→ 1596 Bracelet de Glace（0.8，英→法字彙）
- gameinfo.js「Hunter's Boots」→ 1438 Bottes des Bois Anciens Chasseur（0.667，英→法字彙）
- gameinfo.js「Nodachi Staff」→ 2576 Bâton Magique Nodachi（0.8，英→法字彙）
- gameinfo.js「Radiant Power Crystal」→ 1748 Cristal de Puissance（0.8，英→法字彙）
- recipes.js 產出（id 是 null）「Frozen Bracelet」→ 1596 Bracelet de Glace（0.8，英→法字彙）
- recipes.js 產出（id 是 null）「Mana Potion I」→ 2457 Potion de Vie I（0.667，英→法字彙）；2470 Potion de Mana III（0.667，英→法字彙）；2471 Potion de Stamina I（0.667，英→法字彙）
- recipes.js 產出（id 是 null）「Mana Potion II」→ 2458 Potion de Vie II（0.667，英→法字彙）；2470 Potion de Mana III（0.667，英→法字彙）；2472 Potion de Stamina II（0.667，英→法字彙）
- recipes.js 產出（id 是 null）「Mana Potion III」→ 2470 Potion de Mana III（1.0，英→法字彙）；2459 Potion de Vie III（0.667，英→法字彙）
- recipes.js 產出（id 是 null）「Occult Amulet」→ 1298 Amulette Occulte（1.0，英→法字彙）
- recipes.js 產出（id 是 null）「Occult Ring」→ 1559 Bague Occulte（0.8，英→法字彙）；2486 Anneau Occulte（0.8，英→法字彙）
- recipes.js 產出（id 是 null）「Quality Mana Potion I」→ 2463 Qualité Potion de Vie I（0.75，英→法字彙）
- recipes.js 產出（id 是 null）「Quality Mana Potion II」→ 2464 Qualité Potion de Vie II（0.75，英→法字彙）
- recipes.js 產出（id 是 null）「Quality Mana Potion III」→ 2470 Potion de Mana III（0.857，英→法字彙）；2465 Qualité Potion de Vie III（0.75，英→法字彙）
- recipes.js 產出（id 是 null）「Quality Mana Potion V」→ 2467 Qualité Potion de Vie V（0.75，英→法字彙）
- recipes.js 產出（id 是 null）「Quality Mana Potion VI」→ 2468 Qualité Potion de Vie VI（0.75，英→法字彙）
- recipes.js 產出（id 是 null）「Quality Stamina Potion I」→ 2471 Potion de Stamina I（0.75，英→法字彙）；1972 Qualité Fortifiant d'Endurance I（0.667，英→法字彙）；2463 Qualité Potion de Vie I（0.667，英→法字彙）
- recipes.js 產出（id 是 null）「Quality Stamina Potion II」→ 2472 Potion de Stamina II（0.75，英→法字彙）；1984 Qualité Fortifiant d'Endurance II（0.667，英→法字彙）；2464 Qualité Potion de Vie II（0.667，英→法字彙）
- recipes.js 產出（id 是 null）「Quality Stamina Potion III」→ 1999 Qualité Fortifiant d'Endurance III（0.667，英→法字彙）；2465 Qualité Potion de Vie III（0.667，英→法字彙）
- recipes.js 產出（id 是 null）「Quality Stamina Potion V」→ 2467 Qualité Potion de Vie V（0.667，英→法字彙）
- recipes.js 產出（id 是 null）「Quality Stamina Potion VI」→ 2468 Qualité Potion de Vie VI（0.667，英→法字彙）
- recipes.js 產出（id 是 null）「Slime Essence」→ 2369 Essence de Slime（1.0，英→法字彙）
- recipes.js 產出（id 是 null）「Slime Tear」→ 2370 Larme de Slime（1.0，英→法字彙）
- recipes.js 產出（id 是 null）「Training Dagger (2)」→ 1760 Dague d'Entraînement（0.8，英→法字彙）

### W10

- 數量：179

### W11

- 數量：{"resolved": 3, "unresolved": 6}

### W12

- 數量：{"ITEMS fr": 7, "SAO23 fr": 101, "gameinfo oid": 10, "zhnames ids": 95, "配方 id": 5}

### 未量測（4）

- W1（同順位來源矛盾：資料檔沒有同時保存 catalog 和 wiki 的值）
- W3（同一來源的不同觀察：資料檔每件物品只存一個值）
- W4（同一外部編號在新舊匯入之間改名：階段 1 沒有上一次匯入的快照）
- W8、W9 由瀏覽器測試 tests/zh_gap.js、tests/site_audit.js 產生（CI 的「site audit and untranslated names」步驟執行，輸出在 CI 的 registry_report 附件；只記錄、不擋建置）
