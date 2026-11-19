# UI-INV R0.1｜D.《UI-INV × R0.6 資料依賴對照表》

- 基準：`Cheng-1001/ArgoStrategyGuide` main `14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d`（2026-11-19 重新 fetch 確認 origin/main 仍是此 SHA）
- 版本：**v2**（2026-11-19，依 GPT 第 1 輪複審 M01～M05 修訂；v1 檔案保留不動）
- 性質：唯讀盤點＋規劃建議，**不是已核准決策**；component_key 都是提案，網站沒有實作。
- 標記：VERIFIED＝本機 Playwright 實測（1280／390 寬）；CODE＝只讀程式碼；NOT RUN＝沒有測；UNKNOWN＝不確定。行號都指 `src/index.html`，除非另外寫檔名。
- 分工來源：A＝全站外殼／路由／共用面板／測試涵蓋，B＝圖鑑五分頁，C＝地圖／任務／配方／地下城／職業／世界王，D＝協作區／關於本站／更新紀錄＋R0.6 依賴表。


## 先講清楚：網站目前的資料身份有四種

| 身份類型 | 用在哪裡 | 產生位置 | 穩不穩定 |
|---|---|---|---|
| **外部 oid**（官網圖鑑 id） | 裝備 `e\|<oid>`、道具 `p\|<oid>`、配方列的 `r.oid`、gamestats／gameinfo／zhnames 的 `e\|`／`p\|` | equip.js、props.js | 官網重抓不變就穩定 |
| **名稱鍵** | 素材 `i\|<ITEMS key>`（英文名，部分中文名）、`monByName`、NPC 的 `n.n`（配方 key、收購、NPC_NOTE、SAO_NPC_CALC、zhnames npcs）、套裝成員、gameinfo `en`、mobphotos／hints 的鍵、回報 `reports.js` | data.js、data23.js 等 | 改名就斷，靠 `ITEM_OLD`／`aka`／`old` 補 |
| **陣列順序流水號**（依資料檔順序產生） | 怪物 `m<i>`（L data.js:121）、`f2m<i>`／`f3m<i>`（data23.js:13，新聞怪物接在後面）、NPC `n<f>_<i>`（L1074）、主線任務 `mq<f>_<i>`（L1590）、配方 `r\|<ALLREC 索引>`（L1742）、遊戲才有的裝備 `e\|x<k>`（L2094，依 ITEMS 鍵順序）、遊戲才有的消耗品 `p\|g<k>`（L2299，依 sets.js potions 順序）、wiki 支線 `f<f>q<i>`（L935，沒寫 id 的才用） | index.html 執行時 | **最不穩定**：前面插一筆，後面全部位移 |
| **手寫 slug／回報 id** | 地點 `s\|<id>`（tob、xal、geldorakd…）、城鎮 `t\|<id>`、支線有寫 id 的、職業 `c\|<id>`、活動地下城 `d\|<id>`、回報新增 `rep-R00NN`（怪物）／`rp-R00NN`（地點） | 資料檔、L1006、L976 | 穩定 |

**URL hash 不帶資料 id**（VERIFIED：開裝備面板後 `location.hash` 仍是 `#equip`；路由正則 L3612 只認 `f{N}-{分頁}`）。資料 id 只存在於 DOM 的 `data-go`／`data-key`／`data-goview`／`data-spot`／`data-town`／`data-route`／`data-imap`、記憶體（`stack`、`lastCls`、`lastDg`、`GVW` 視窗堆疊），以及測試基準檔（`tests/fixed_links.json`、`tests/baseline/*.json`）。localStorage 只存篩選、底圖、更新紀錄模式、導覽、`?edit` 的區域位置（`sao-f<N>-zone-pos`，鍵是 ZONES 的 slug），**沒有存資料 id**（CODE：L1049–1082、1917–1931、3309–3311、3748）。

## 對照表

> **v2 說明（M01）**：下表第一欄是**依賴項目名稱**（描述「哪一種資料查找或連結」的名稱），**不是 UI 元件的 component_key**，所以不受 C 命名規則約束（例如 `global.data-key（卡片身份）` 含中文說明、`tests.*`／`tools.*` 不是 UI scope）。和清冊 component_key 指向同一個元件或屬性的，對應如下；沒列出的是跨元件的查找邏輯（例如 `global.ikey-old-names`、`global.zh-names`），沒有單一對應的元件。
>
> | 依賴項目名稱 | 清冊 component_key |
> |---|---|
> | `global.route.hash` | `global.route.hash` |
> | `panel.open` | `panel.root`（及 `panel.*` 各區塊） |
> | `global.data-go` | `global.link.data-go` |
> | `global.data-key（卡片身份）` | `global.selection.data-key` |
> | `popup.goview` | `global.link.data-goview` |
> | `popup.gv-menu` | `popup.menu-rule` |
> | `panel.inline（職業／地下城）` | `panel.inline` |
> | `global.report-ref` | `global.link.data-repgo` |
> | `map.show-points` | `floatmap.window`、`global.link.data-rep` |
> | `items.list.card`／`equip.list.card`／`props.list.card`／`recipes.list.card`／`monsters.list.card`／`npcs.list.card` | 同名 |
> | `map.spots／dungeons.card` | `map.marker.spot`、`dungeons.list.card` |
> | `map.towns` | `map.marker.town` |
> | `quests.card（主線）`／`quests.card（支線）` | `quests.list.main-card`／`quests.list.side-card` |
> | `classes.card` | `classes.list.card` |
> | `bosses.view` | `bosses.view.section`、`bosses.card.floor-boss-link` |
> | `report.done.links` | `report.done.card` |

欄位：元件識別名稱｜所屬樓層／分頁｜實際資料來源｜使用的查找函式（行號）｜以名稱作為資料鍵？｜使用外部編號（官網 oid）？｜已有本站資料 ID？｜依陣列順序的流水號？｜對應 R0.6 遷移階段（規劃對應，不是決定）｜需要的回歸測試｜程式碼位置｜狀態

### A. 共用路由、面板、跳轉

| 元件識別名稱 | 樓層／分頁 | 資料來源 | 查找函式（行號） | 名稱鍵 | 官網 oid | 本站 ID | 流水號 | R0.6 階段 | 回歸測試 | 程式碼位置 | 狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| global.route.hash | 全樓層／全分頁 | 無（只有樓層＋分頁） | `show()` L3612、`hashFor` L3567 | 否 | 否 | N/A | 否 | N/A | fixed_links `route:*` 37 筆 | L3564–3640 | 目前已確認依賴（不受影響） |
| panel.open | 全樓層／全分頁 | 依 type 分派 `detailHTML0` | `openP(t,id)` L1176（`i` 先 `redirI`、`p` 先 `redirP`）、`nameOf` L1188、`detailHTML0` L1190 | `i` 是名稱 | `e`／`p` 是 | `s`／`t`／`c`／`d` 是 | `m`／`n`／`r`／`q(mq)`／`e\|x` 是 | 2 物品＋後續 NPC・地點・怪物・任務 | fixed_links `entity:*` 933 筆；tests/site_audit.js | L1176–1190 | 未來預計遷移 |
| global.data-go | 全樓層／全分頁 | `data-go="<t>\|<id>"` 約 44 處產生 | `bindGo` L1422（每個面板 render 後綁 onclick）；彈出視窗 L1464–1470 | 同上 | 同上 | 同上 | 同上 | 2 物品＋後續 | fixed_links entity；smoke.py:110、123（寫死 `q\|mq1_33`、`q\|mq1_15`） | 產生處：L1243、1251、1258、1294–1297、1349–1414、1500、1545、1548、1568、1579、1706、1712、1789、1809–1810、1835、1969–1977、1992、2003–2022、2255、2335、2403、2434、3204 | 未來預計遷移 |
| global.data-key（卡片身份） | 全樓層／列表分頁 | 卡片 `data-key="<t>\|<id>"` | `markSel` L1237–1239（面板開著時標選取）、`goView` 找卡片 L1480 | 同上 | 同上 | 同上 | 同上 | 2 物品＋後續 | fixed_links `goview:*` 538 筆 | L1500、1545、1548、1579、1789、1809–1810、1835、1888、2003、2012、2255、2335 | 未來預計遷移（**實體身份部分** `<t>\|<id>` 必須和 data-go 相同；data-goview 是三段 `<view>\|<t>\|<id>`，見 C 命名規則 §5.1） |
| popup.goview | 全樓層／面板「查看配方／查看圖鑑」 | `data-goview="<分頁>\|<t>\|<id>"` | `bindGo` L1423→`gvOpen` L1472；`goView` L1479 | `i` | `e`／`p` | — | `r\|<索引>` 是 | 2 物品（配方索引另議） | fixed_links goview（r 293、e 188、p 57）；smoke.py:557–565 | L1702、1971 | 未來預計遷移 |
| popup.gv-menu | 全樓層 | 依 type 決定哪個「選單」 | `gvMenu` L1433、`gvNew` L1438、`GVW` 堆疊 | — | — | — | 堆疊存 `{t,i}` | 後續 | smoke.py pop-up 那幾項 | L1433–1475 | 目前已確認依賴（存 id，不存名稱） |
| panel.inline（職業／地下城） | 全樓層／classes、dungeons | `lastCls`、`lastDg`（記憶體） | `INL`、`fitClsPanel`、`openP` L1176 | 否 | 否 | 是（職業 id、地點 slug、活動 id） | 否 | 後續：地點 | smoke 職業／地下城 | L1175–1176、1841 | 目前已確認依賴 |
| global.redir-item | 全樓層／素材↔裝備↔道具 | ITEMS（名稱）→ 官網 EQ／PR（法文名） | `redirI` L1511、`redirP` L1512、`offOf` L1514（**用法文名 `fr` 對官網 `e.name`**）、`FR2ID` L2100、`EQX_BY` L2092 | 是（ITEMS key、法文名） | 是 | 否 | `e\|x<k>` 是 | 2 物品引用遷移 | four-tab codex（smoke）；fixed_links entity `i\|` 194 筆 | L1509–1516 | 未來預計遷移 |
| global.report-ref | 全樓層 | reports.js 回報 id | `repLink` L1271、`repRef` L1272、`goRep` L3684 | 否 | 否 | 是（R000N） | 否 | N/A | report_types_test.py:102–105 | L1271–1272、3684–3687 | 目前已確認依賴（不受影響） |
| map.show-points | 全樓層 | 座標 `data-rep="f\|x\|z"`、`data-spot`、`data-town`、`data-route`、`data-imap` | `showPoints` L1183；L1216–1231、L1464–1470 綁定；`spotById` L1110、`townById` L1010、`questById` L1590、`itemMap` | `data-imap`＝ITEMS key（名稱） | 否 | `spot`／`town` 是 slug | `data-route` 的主線是 `mq<f>_<i>` | 後續＋2 物品（imap） | 浮動地圖相關 smoke | L1216–1231、1464–1470 | 未來預計遷移（imap、route） |

### B. 物品（素材、裝備、道具、配方）

| 元件識別名稱 | 樓層／分頁 | 資料來源 | 查找函式（行號） | 名稱鍵 | 官網 oid | 本站 ID | 流水號 | R0.6 階段 | 回歸測試 | 程式碼位置 | 狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| items.list.card | 全樓層／items | `ITEMS`（data.js `SAO.ITEMS`＋data23.js `SAO23_ITEMS`＋`S23.unknown`，L1015–1017 依物件鍵順序合併）；官網材料 PR | `matPool`；卡片 `data-key="i\|<ITEMS key>"` 或 `p\|<oid>`（L1545、1548）；`redirP` | 是 | 官網材料是 | 否 | 否 | 2 物品引用遷移 | fixed_links entity `i\|` 194；smoke four-tab | L1541–1550 | 未來預計遷移 |
| equip.list.card | 全樓層／equip | `EQ`＝equip.js（官網）＋EQX（ITEMS 裡沒有 `fr` 的裝備類，L2092–2096） | 卡片 `data-key="e\|<oid>"`（L2255）；`eqById` L2097 | EQX 的 `name`＝ITEMS key | 是 | 否 | **EQX `oid:"x"+(++k)`，依 ITEMS 鍵順序** | 2 物品引用遷移 | fixed_links entity `e\|` 233（含 `e\|x10`…） | L2092–2097、2251–2256 | 未來預計遷移 |
| props.list.card | 全樓層／props | `PR`＝props.js＋sets.js `potions[]` 裡官網沒有的消耗品（L2297–2301：`id="g"+(++k)`，依 sets.js potions 順序，跳過官網已有的）＋催化器併入 EQ | 卡片 `data-key="p\|<oid>"`（L2335）、`prById` L2279 | 消耗品假條目依名稱 | 是 | 否 | **是：`p\|g<k>`** | 2 物品引用遷移 | fixed_links entity `p\|` 109 | L2279、2296–2301、2327–2336 | 未來預計遷移 |
| recipes.list.card | 全樓層／recipes | recipes.js `SAO_RECIPES`（key＝NPC 名或「f\|NPC 名」）＋配方回報（L1671–1675，在 ALLREC 之前併入） | `rKey`／`rSplit`／`RCP` L1667；`recRow` L1678；`ALLREC` L1742（`r.i=i`）；卡片 `data-key="r\|<索引>"`（L1789） | NPC 名 | 列的 `oid` | 否 | **是：`r\|<ALLREC 索引>`** | 2 物品（配方身份另外要定） | fixed_links entity `r\|` 69、goview `r\|` 293；tests/baseline/operations.json | L1665–1755、1784–1790 | 未來預計遷移（風險高，見 D-R12-1） |
| recipes.material | 全樓層／配方面板、地下城寶箱、回收清單 | 材料名稱（遊戲英文或中文） | `matRef` L1694：`ikey`→ITEMS → `en2go()` L1688（zhnames en／zh、配方 oid、「N Cols Pouch」規則）→ `enGo` L2397（EQ／PR 的 `gen`、gameinfo en）→ 只有名字；`GICON[m]` 圖示 | 是 | 間接 | 否 | 否 | 2 物品＋過渡查找清理 | tests/site_audit.js（「本站還沒有這個物品的資料」）；`window.__iconFor` L2192 | L1688–1698、1354–1367、1710–1712、1977 | 未來預計遷移 |
| recipes.by-eq | 全樓層／裝備、道具面板「製作方式」 | `RECIPE_BY_EQ[oid]`、`RECIPE_BY_MAT[材料名]` L1679–1680；EQX 依英文名補（L2096） | `recGoBtns` L1701；裝備面板 L2273–2275、2301、2414–2415 | `RECIPE_BY_MAT` 是名稱、EQX 依 `norm(r.en)===norm(id)` | `RECIPE_BY_EQ` 是 | 否 | 產生 `recipes\|r\|<索引>` | 2 物品 | goview `r\|` 293 | L1679–1680、1701–1702、2096 | 未來預計遷移 |
| global.ikey-old-names | 全樓層／搜尋、回報、配方材料、收購 | `ITEM_OLD`（index.html L1019，程式內表）、`REP_MAT` L922；`ITEMS[n].aka` 由 ITEM_OLD 補（L1021） | `ikey` L1020（11 處）；L1022 回報 drops／mats 先過 ikey | 是（舊名→新名） | 否 | 否 | 否 | 過渡查找清理 | fixed_links `search:*` 13 筆（Shark Shell、Leaf Fragment、Pumba's Ring…） | L922、1019–1022 | 目前已確認依賴；**check_refs.py 不檢查 ITEM_OLD／REP_MAT**（只讀程式內的 NPC_NOTE，tools/check_refs.py:756–778） |
| global.zh-names | 全樓層／標題、副標、搜尋 | zhnames.js：`items[].ids`（`e\|`／`p\|`／`i\|`／`g\|`）、`mobs`（圖鑑編號）、`mobsByName`、`places`、`npcs`、`npcEn`、`quests`、`sets`、`search`、`terms` | `ZH_ID`／`ZH_EN`／`ZH_FR` L2081–2082、`zhE` L2084、`zhI` L2085、`zhGo` L2396、`zhS` L2083、`mN` L1094、`pN` L1095、`npcN` L1100、`npcEn` L1099、`qZ`／`qT` L1103–1104、`zhHTML`／`__zhDict` L2202、2219 | `i\|`、`g\|`、mobsByName、places、npcs、quests 是 | `e\|`／`p\|` 是 | 第 1 層怪物用圖鑑編號 | 否 | 2 物品＋後續 | `node tests/zh_gap.js`；smoke 中文標題 | L1093–1104、2081–2085、2196–2240 | 目前已確認依賴；zhnames 已在 check_refs COVERAGE |
| global.gameinfo | 全樓層／物品、裝備、道具、配方面板 | gameinfo.js `items[]{oid[],site,en,obt}` | `GI_OID`／`GI_SITE`／`GI_EN` L2043–2047；`loreHTML` L2089；`objFloors` L2134（**用「Loot: 怪物名」對 `monByName`**）；`GI_LOOT_OK` L1024 | `site`、`en`、「Loot: 怪物名」是 | `oid[]` 是 | 否 | 否 | 2 物品 | site_audit；`window.__objFl` L2139 | L1024、2043–2047、2089、2134、1979 | 目前已確認依賴 |
| global.sets-potions | 全樓層／裝備、道具、配方、素材面板；效果篩選 | sets.js `sets[].members`（英文名或法文名）、`potions[].name` | `SET_BY`／`POT_BY` L2393–2394、`setPotHTML` L2400、`eqSetOf` L2152、`eqSetN` L2191、`enGo` 連成員 L2403 | 是 | 否 | 否 | 否 | 2 物品 | smoke 套裝；`__effPick` | L2152、2191、2393–2403、1964、2408 | 目前已確認依賴 |
| global.icons | 全樓層 | gameicons.js（鍵＝英文名或法文名）、recicons.js（鍵＝配方英文名）、`OID_RECIC` L1779 | `slot()`／`eslot()`／`pslot()`、`recIcon`、`GICON[...]`（20 處）、`RECIC[...]`（24 處） | 是 | `OID_RECIC` 是 | 否 | 否 | 2 物品 | `__iconFor`；圖示比對腳本（scratchpad） | L1156–1158、1770–1780、2112、2312 | 目前已確認依賴；E7 釘選只有 2380 |
| global.reward-go | 全樓層／任務面板獎勵 | 任務 `bonus` 文字 | `rewardGo` L1409（`norm` 比 ITEMS key 或 `fr`、EQ／PR 的法文 `name`） | 是（含法文名） | 是 | 否 | 否 | 2 物品 | 任務面板 smoke | L1409–1414 | 目前已確認依賴 |
| global.buyback | 第 1 層（`shops` 只接第 1 層 NPC）／NPC 面板、NPC 分頁搜尋 | buyback.js `items[NPC 名]=[[英文物品名,價,來源]]` | `BB.items[n.n]` L1567、1570、1578；`bbGo` L1563（`ikey`→ITEMS，否則 `enGo`） | 是（NPC 名、物品名） | 間接 | 否 | 否 | 2 物品＋後續 NPC | smoke 收購 | L1554–1578 | 目前已確認依賴 |
| global.gamestats-patch | 全樓層／裝備數值 | gamestats.js `items{oid}`、events.js `eqPatch` | EQ 建好後覆蓋 lv／dmg／st（`gstNote`） | eqPatch `en` 是 | 是 | 否 | 否 | 2 物品 | 裝備面板 smoke | L2100–2130 附近 | 目前已確認依賴（行號範圍是 CODE 粗定位） |
| global.gacha | 全樓層／裝備、道具、配方面板 | gacha.js `banners[].rewards`（英文名、部分 `id:"p\|1696"`） | `gachaHTML(...keys)` | 是 | 部分 | 否 | 否 | 2 物品 | 面板文字 | L1979 呼叫處 | 尚未確認（未逐行讀 gachaHTML） |

### C. 怪物

| 元件識別名稱 | 樓層／分頁 | 資料來源 | 查找函式（行號） | 名稱鍵 | 官網 oid | 本站 ID | 流水號 | R0.6 階段 | 回歸測試 | 程式碼位置 | 狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| monsters.list.card | 全樓層／monsters、地圖縮圖、重生點 | data.js `SAO.M`（`id:"m"+i`）、data23.js `mk(pre,rows)`（`f2m`/`f3m`+i，新聞怪物 `addNews` 接後面） | `monById` L1009；卡片 `data-key="m\|<id>"` L1500；地圖 `openP("m",m.id)` L3374、3441、3498 | 否 | 否 | 否 | **是** | 後續：怪物 | fixed_links entity `m\|` 180（例：`m\|f2m0`）；tests/baseline/panels.json 鍵 `m\|m0`… | data.js:121、data23.js:13、L1009、1496–1500 | 未來預計遷移 |
| global.mon-by-name | 全樓層 | `F.monByName`（名稱＋aka，L938） | 15 處：`SPOTS[].mons` L1055、1373、3345、3423、3488、3531；`BOSS_SPAWNS` `SPAWNS` L1057；任務 kill L1043、1404、1600；gameinfo Loot L2134；`renameMon` L992 | 是 | 否 | 否 | 否 | 後續：怪物 | site_audit 全怪物面板 | L938、992、1043、1055–1057、1373、1404、1600、2134、3345、3423、3488 | 目前已確認依賴 |
| global.mon-aux-tables | 全樓層／怪物面板 | mobphotos.js `by[樓層][名稱]`、data.js `PHOTO[名稱]`、hints.js `SAO_HINTS[樓層][名稱]`、codex.js `SAO_CODEX[樓層][圖鑑編號]`、mobrenders／mobcodex | `photoOf` L1137、`face` L1141、L1259（hints，含 aka）、L1260（codex 用 `m.num`） | 是（除 codex） | 否 | codex 用圖鑑編號 | 否 | 後續：怪物 | smoke「Albal shows codex description」smoke.py:89 | L1137–1151、1259–1260 | 目前已確認依賴 |
| global.mon-report-match | 全樓層 | reports.js（`type:"monster"` 的 `name`、`codexNo`、審核備註「舊名：X」） | `findMon` L990、`renameMon` L991（**執行時改名**）、L994–1001；新增怪物 `id:"rep-"+r.id` L1006；掉落取代 L1026（`r.drops.every(d=>ITEMS[d[0]])`） | 是 | 否 | 回報新增的是 `rep-R00NN` | 否 | 後續：怪物＋過渡查找清理 | tests/report_rules_test.py、report_types_test.py | L986–1030 | 目前已確認依賴（見 D-R12-3） |

### D. NPC、地點、城鎮、任務、職業

| 元件識別名稱 | 樓層／分頁 | 資料來源 | 查找函式（行號） | 名稱鍵 | 官網 oid | 本站 ID | 流水號 | R0.6 階段 | 回歸測試 | 程式碼位置 | 狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| npcs.list.card | 全樓層／npcs、地圖 NPC 標記 | npcs.js `SAO_NPCS[f]=[[c,n,x,z,src,u,rep]]` | `NPCS(f)` L1074（`id:"n"+f+"_"+i`）、`npcById` L1075；卡片 `data-key="n\|<id>"` L1579；地圖 L3444、3502 | 否 | 否 | 否 | **是** | 後續：NPC | fixed_links entity `n\|` 95；baseline operations `n\|n1_0` | L1074–1075、1571–1580 | 未來預計遷移 |
| global.npc-by-name | 全樓層／配方「在哪裡做」、地下城鑰匙、NPC 面板 | NPC 名 `n.n`：recipes.js key、buyback.js、`NPC_NOTE`（程式內表 L1715）、`SAO_NPC_CALC`（key「名」或「f\|名」）、zhnames `npcs`／`npcEn` | `npcByName` L1681（6 處：1332、1703、1738、1781、1974）、`NPC_NOTE[n.n]` L1987、`npcCalcNote` L1073、`npcN`／`npcEn` L1099–1100、`npcHit` L1088 | 是 | 否 | 否 | 否 | 後續：NPC | site_audit NPC 84；smoke Alchemist | L1073、1088、1099–1100、1681、1715–1735、1987 | 目前已確認依賴；NPC_NOTE 已被 check_refs 讀（L756） |
| global.npc-report-add | 全樓層 | reports.js `type:"place"`、kind NPC | L970：直接 push 到 `SAO_NPCS[f]` 尾端（id 隨位置） | 是（比對 `nrm(n[1])`） | 否 | 否 | 是（排在尾端，不推移既有） | 後續：NPC | report_types_test.py | L966–971 | 目前已確認依賴 |
| map.spots／dungeons.card | 全樓層／地圖、地下城分頁、地點面板 | data.js `SPOTS[].id`、data23.js spots、回報新增 `rp-R00NN` L976 | `spotById` L1110；`data-spot` L1253、1370、1388；卡片 `data-key="s\|<id>"` L1810；地圖 L3428、3432、3487 | `mons`／`items` 欄位是名稱 | 否 | **是（手寫 slug）** | 否 | 後續：地點 | fixed_links entity `s\|` 45 | L1110、1372–1391、1808–1810 | 目前已確認依賴 |
| global.dungeon-keys | 第 1～3 層／地下城面板、鑰匙配方面板 | 地點 `note` 裡的「Clé …」法文名、配方 `cat:"key"`、入口 150 格內 NPC | `dgKeys` L1329（`prById` 法文名比對、`npcByName`＋距離） | 是（法文名、NPC 名） | 是 | 否 | 結果是 ALLREC 列 | 2 物品＋後續 | smoke 地下城鑰匙 | L1329–1333、1365–1368、1807、1976 | 目前已確認依賴 |
| global.dungeon-map-dim | 第 1 層／打包工具、地圖的地下城模式、地下城面板 | `DG_DIM`（L2688，資料夾名→SPOTS id）、jmmeta.js `SAO_JM.dg[SPOTS id]`、`tiles/dg/<SPOTS id>/`、tools/jm_merge.py `DUNGEONS` | `dgOf` L2689、`dgName` L2691、`data-dgmap` L3322 | 否 | 否 | 是（SPOTS slug） | 否 | 後續：地點 | jm_pack_test.py、jm_merge_test.py 4e | L2688–2691、3216–3221、3322 | 目前已確認依賴（見 D-R8） |
| map.towns | 全樓層／地圖、城鎮面板 | data.js `TOWNS[].id` | `townById` L1010；`data-town` L1395；`openP("t",…)` L3421、3484 | `TOWNS` 名稱給 `ZPL` | 否 | 是（slug） | 否 | 後續：地點 | fixed_links entity `t\|` 8 | L1010、1392–1395 | 目前已確認依賴 |
| quests.card（主線） | 全樓層／quests、任務面板、路線 | mainq.js `SAO_MAINQ[f]`（陣列） | `questById` L1590（`mq<f>_<i>`）；卡片 L2003；`data-route` L2001；回報對任務 L979–981（`nrm(x.t)===nrm(r.name)\|\|aka`） | 回報比對是名稱 | 否 | 否 | **是** | 後續：任務 | smoke.py:110、123（寫死 `q\|mq1_33`、`q\|mq1_15`）；fixed_links 沒有 `q\|` entity（UNKNOWN：為何沒收） | L1586–1592、2002–2006 | 未來預計遷移 |
| quests.card（支線） | 全樓層／quests | data.js `QUESTS`、data23.js quests；`id:q.id\|\|("f"+f+"q"+i)` L935 | `questById` L1591；`qRow` L2012；`qNpc`；`townById` | `npc`、`town` 欄位是名稱／slug | 否 | 有寫 id 的是 | 沒寫 id 的是 | 後續：任務 | site_audit 任務 106 | L935、1591、2012 | 尚未確認（多少支線沒寫 id） |
| classes.card | 全樓層／classes | classes.js `SAO_CLASSES[].id`、gameskills.js `[職業 id]` | 卡片 `data-key="c\|<id>"` L1835；`CLS_OFF` L1798 | 否 | 否 | 是 | 否 | N/A | smoke 職業 | L1798、1833–1841 | 目前已確認依賴 |
| bosses.view | 全樓層／bosses | bosses.js | `renderBosses` L2430；`data-go="m\|…"` L2434（世界王連到怪物） | 世界王→怪物用名稱 | 否 | 否 | 連結對象是怪物流水號 | 後續：怪物 | smoke 世界王 | L2430–2434 | 尚未確認（未逐行讀名稱比對） |
| report.done.links | 全樓層／協作區已收錄 | reports.js | L3202–3204（見第一部分 D-R3） | 是 | 否 | 回報 id | 產生 `r\|<索引>`、`q\|mq<f>_<索引>` | 後續＋2 物品 | report_types_test.py | L3201–3207 | 未來預計遷移 |

### E. 測試與工具端的身份依賴

| 元件識別名稱 | 樓層／分頁 | 資料來源 | 查找函式（行號） | 名稱鍵 | 官網 oid | 本站 ID | 流水號 | R0.6 階段 | 回歸測試 | 程式碼位置 | 狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tests.fixed-links | 全站 | tests/fixed_links.json（1521 筆：entity 933、goview 538、route 37、search 13） | tests/baseline_compare.js 比對 | entity `i\|` 194 筆是名稱 | `e\|`／`p\|` 是 | `s\|`、`t\|` | `m\|` 180、`n\|` 95、`r\|` 69＋goview `r\|` 293、`e\|x…` | 1.5 S15-B1（Registry／驗證工具）＋各遷移階段 | 本身就是回歸測試；**R0.6 改鍵時的處理**（v2，依 GPT 複審 M04）：route 37＋search 13 共 50 筆不依實體 ID，不會只因 ID 更新而失敗；階段 1.5 不切換網站、維持 G5 `IDENTICAL`；階段 2 起依已審查的 `key_map` 和舊連結對照核對舊新結果，沒有非預期差異才更新，不能先重產再用新版對新版 | tests/fixed_links.json | 目前已確認依賴 |
| tests.baseline | 全站（階段 1.5 不改網站和基準，G5 維持 `IDENTICAL`） | tests/baseline/panels.json（鍵 `m\|m0`…）、operations.json（`m\|m35`、`n\|n1_0`、`r\|103`…） | tests/baseline_capture.js、baseline_compare.js | 同上 | 同上 | 同上 | 是 | 1.5 S15-B1 | 同上 | tests/baseline/ | 目前已確認依賴 |
| tests.audit-hooks | 全站（階段 1.5 不改網站和基準） | `window.__auditIds`（L2192：e=EQ oid、p、i=ITEMS 鍵、r=ALLREC 索引、n、q=`mq…`＋ALLQ id、s、t、c）、`__detail` | tests/site_audit.js | 是（i） | 是 | 是 | 是 | 1.5 S15-B1 | site_audit.js | L2192 | 目前已確認依賴（id 改了，掛鉤自動跟著） |
| tools.check-refs | 建置 | tools/check_refs.py（資料檔 COVERAGE／SKIP、NPC_NOTE 程式內表）、registry/pins.json（只有 2380）、exceptions.json | `npc_note_keys` check_refs.py:756；W11 回報名稱 check_refs.py:1765–1778 | — | — | — | — | 1.5 S15-B1 | tests/check_refs_test.py | tools/check_refs.py | 目前已確認依賴；**沒有掃 index.html 的 ITEM_OLD、REP_MAT、DG_DIM、NPC_ZH 等程式內名稱表** |


---

## 附錄 1（分工 B）：圖鑑資料查找函式和連結值格式


這一節不是 UI 元件，是上面各表 `lookup_dependency` 用到的函式。「鍵的種類」：**名稱**＝會因改名而變；**外部編號**＝官網圖鑑 id，穩定；**流水號**＝依陣列順序產生，前面插入一筆就全部移位。

| 函式／值 | 位置 | 鍵的種類 | 怎麼產生 | 誰在用 | 什麼情況會移位或對錯 | 現有保護 |
|---|---|---|---|---|---|---|
| `m\|<id>`（`monById`） | src/index.html:1009；data.js:121；data23.js:13、16；回報 1004 | **流水號**（`m<i>`、`f<N>m<i>`），回報的 `rep-R<N>` 穩定 | `M` 陣列 map 的序號；新聞怪物 `addNews` 接在 wiki 怪物後 | 怪物卡片、素材「取得方式」、地下城、任務 | data.js／data23.js 的 M 陣列中間插入或刪除；`build_mobphotos.py` 重產 BEGIN/END 區塊時改順序 | fixed_links `m\|m*` 67、`m\|f[23]m*` 115；panels.json 67／137 |
| `e\|<官網 oid>` | eqById 2097；equip.js | 外部編號 | equip.js 第 0 欄；催化器來自 props.js（2031，`ps:1`） | 裝備卡片、所有裝備連結、gamestats、gameinfo、zhnames | 不會移位；催化器的 zhnames 鍵是 `p\|`（zhE 2084） | 穩定 |
| `e\|x<N>`（EQX） | 2092-2096 | **流水號** | `Object.keys(ITEMS)` 依序（data.js ITEMS → SAO23_ITEMS → S23.unknown，1015-1017），挑出 `fr` 空白且 `cat` 在 EQX_CATS 的 | 遊戲才有的裝備（61 件） | **前面任何一件 ITEMS 補上 `fr`（對到官網）或改 `cat`，後面的 x 全部往前移**；這是例行的對照工作就會發生 | fixed_links `e\|x*` 53、panels.json 61 |
| `p\|<官網 oid>` | prById 2279 | 外部編號 | props.js 第 0 欄（去掉 catalyst） | 道具卡片、素材的官網材料卡片 | 不會移位 | 穩定 |
| `p\|g<N>` | 2296-2302 | **流水號** | sets.js `potions` 依序，跳過 `have`（已有 `gen` 的 PR） | 官網沒有的消耗品（31 件） | **任何官網道具新得到 `gen`（gameinfo、zhnames 的 en、截圖配方 2287-2289）而和某個 potion 同名，就被跳過，後面的 g 全部前移**；sets.js 增刪也會 | **fixed_links 0 條**；panels.json 31 |
| `i\|<ITEMS key>` | ITEMS 1015；ikey 1020 | **名稱**（英文） | data.js／data23.js 的物件鍵 | 怪物掉落、素材卡片、`data-imap`、回收、配方材料、地下城寶箱 | 改名時要寫 ITEM_OLD（1019），`ikey` 只在部分路徑套用（搜尋、回報、配方材料、收購）；`data-go="i\|舊名"` 不會轉（CLAUDE.md 第 26 案） | fixed_links `i\|` 198 |
| `n\|n<f>_<i>`（npcById） | NPCS 1074；npcById 1075 | **流水號** | `SAO_NPCS[f]` 陣列序號；回報 NPC push 在後（964） | NPC 卡片、配方「在哪裡做」、裝備「製作方式」 | `build_npcs.py` 重產（SITE／CALC23／NEW23／DROP 變動） | fixed_links `n\|n*` 96 |
| `npcByName(f,name)` | 1681 | **名稱**，取第一個 | `NPCS(f).find(n.n===name)` | recipeTable、isShop、dgKeys | 重名 NPC（見第 5 節）只會找到第一個 | 無 |
| `r\|<N>`（ALLREC 序號） | ALLREC 1742；報告合併 1668-1674 | **流水號** | `Object.entries(RECIPES)` 依序展開；**核准的配方回報在建 ALLREC 之前插入 RECIPES**（同 NPC 同名就取代，否則 push；新 NPC 新增鍵） | 查看配方（`data-goview="recipes\|r\|N"`）、recipeTable 的配方連結、enGo 退路、配方分頁卡片 | recipes.js 重產；**Apps Script 自動寫 reports.js 的配方回報也會讓序號移位，不經開發者 commit**；測試用 `tests/baseline/fixtures/` 的複本，看不到這種移位 | fixed_links `r\|` 363 |
| `recGoBtns`／`recipeTable` 的 `findIndex` | 1701、1704 | 名稱（`npc`＋`en`） | `ALLREC.findIndex(y.npc===x.npc&&y.en===x.en)` | 裝備／道具「查看配方」、NPC 面板配方列 | **不比樓層**：第 1、3 層都有「Alchemist」和同名品質藥水 II／III 6 筆（VERIFIED） | 無 |
| `offOf(id)` | 1513-1515 | 名稱（法文） | ITEMS 的 `fr` 對 EQ／PR 的 `name`，後者覆蓋前者（`eb[e.name]=e`） | redirI、素材分類、zhI、圖示 | EQ 法文名重複 4 組（Bâton Magique du Magicien ×2、Bâton Magique d'Amour ×2、Orbe d'Avarice ×3、Spectre Maudit ×2，VERIFIED）→ 取最後一件 | 無 |
| `redirI(id)` | 1511 | 名稱 | `EQX_BY[id]` → `offOf(id)` | openP、gvNorm、goView、slot | 同 offOf | 無 |
| `redirP(oid)` | 1512 | 外部編號→名稱 | 材料類道具：`FR2ID[e.name]` 對到 ITEMS | openP("p")、gvNorm | 法文名重複時最後一筆贏 | ITEMS 法文名目前不重複（VERIFIED） |
| `FR2ID` | 2100 | 名稱（法文→英文 key） | ITEMS 依序，後者覆蓋 | objFloors、zhE、eqHit、propDetail（`en`） | 同上 | 同上 |
| `EQX_BY` | 2092-2096 | 名稱→流水號 | ITEMS key → `x<N>` | redirI、rcEq | 同 EQX | 同 EQX |
| `ikey(n)`／`ITEM_OLD` | 1019-1022 | 名稱（舊→新） | 手寫表 | 回報掉落和材料、配方材料、matRef、bbGo、搜尋 aka | 新改名沒寫進表，舊名的資料就對不到 | registry 檢查（R0.5 階段 1 E1） |
| `matRef(m)` | 1694-1697 | 名稱 | ITEMS key → `en2go()`（zhnames 的 en／zh、配方 oid、「N Cols Pouch」）→ `enGo` | 配方材料、地下城寶箱、回收表、dgSrcHTML、`__iconFor` | 名稱碰撞時取第一個 | 無 |
| `enGo(n)` | 2397-2399 | 名稱（英文） | EQ.gen → PR.gen → ITEMS key → **`r\|<序號>`** → 法文名 | 套裝成員、回收、matRef 退路 | `gen` 重複 4 組（Occult Amulet ×2、Christmas Mittens ×3、Leggings of Ika ×2、Boots of Ika ×2，VERIFIED）→ 取第一件 | 無 |
| `zhE(e)`／`zhI(id)`／`dn`／`dnSub` | 2084-2088 | `e\|oid`／`p\|oid`／`i\|key`／`g\|<英文名>`（注意：zhnames 的 `g\|` 是遊戲英文名，不是道具的 `g<N>`）／英文名／法文名 | ZH_ID、ZH_EN、ZH_FR（2082-2083） | 所有標題、搜尋 | 多重退路，名稱碰撞時取第一個 | 無 |
| `GI_OID`／`GI_EN`／`GI_SITE` | 2043-2047 | 外部編號／英文名／ITEMS key | gameinfo.js | 取得方式、gen、objFloors | `GI_EN` 依英文名，後者覆蓋 | 無 |
| `GICON[e.gen]`（圖示） | eslot 2112、pslot 2312 | 名稱 | gameicons.js | 圖示 | `gen` 去掉「(N)」（2094）：`Occult Amulet (2)`（x49）沒有自己的圖示鍵，借到 `Occult Amulet`（x53）的紅色圖示（VERIFIED 兩件都是 `icons/game/occult_amulet.png`；CLAUDE.md 說第 2 層的是深灰鏈子） | 無 |
| `SET_BY`／`POT_BY` | 2394 | 名稱（英文） | sets.js members／potions | 套裝效果、效果篩選、道具效果 | `gen` 重複時兩件都對到同一套 | 無 |
| `monByName`（`FLOORS[f].monByName`） | 938；renameMon 994 | 名稱（含 aka） | 每層 M | KILLQ、SPAWNS、objFloors、dgMonByName | 回報改名會更新 | 無 |
| 頭像 `renderOf`／`photoOf` | 1137-1140 | 名稱（樓層＋英文名） | mobcodex.js、mobphotos.js | face、photoNote | 回報改名後對不到（不查 aka） | 無 |
| `BB.items`、`NPC_NOTE`、`RCP`、`SAO_NPC_CALC` | 1554、1715、1667、1073 | 名稱（NPC key） | buyback.js、手寫、recipes.js、npcs.js | NPC 面板 | 重名 NPC 共用一份 | 無 |
| `data-goview="<view>\|<type>\|<id>"` | 1702、1971；處理 1213、1423、1461 | 第一段 view 名**沒有被使用** | — | 查看配方、查看圖鑑 | gvOpen 只取後兩段；`goView`（1479）是唯一會用 view 段的函式，但**沒有任何地方呼叫**（index.html 和 tests/ 都 grep 過） | smoke 用前綴選取（tests/smoke.py:557、562、565） |

---

