# UI-INV R0.1｜B. 風險清單

- 基準：`Cheng-1001/ArgoStrategyGuide` main `14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d`（2026-11-19 重新 fetch 確認 origin/main 仍是此 SHA）
- 版本：**v2**（2026-11-19，依 GPT 第 1 輪複審 M01～M05 修訂；v1 檔案保留不動）
- 性質：唯讀盤點＋規劃建議，**不是已核准決策**；component_key 都是提案，網站沒有實作。
- 標記：VERIFIED＝本機 Playwright 實測（1280／390 寬）；CODE＝只讀程式碼；NOT RUN＝沒有測；UNKNOWN＝不確定。行號都指 `src/index.html`，除非另外寫檔名。
- 分工來源：A＝全站外殼／路由／共用面板／測試涵蓋，B＝圖鑑五分頁，C＝地圖／任務／配方／地下城／職業／世界王，D＝協作區／關於本站／更新紀錄＋R0.6 依賴表。

## 1. 總表（依嚴重程度排序）

| # | ID | 嚴重 | 位置 | 問題（摘要） | 需要改程式 |
|---|---|---|---|---|---|
| 1 | A-R3 | 高 | :1212–1231、:1422–1423、:1458–1470 | 三套各自的連結綁定，涵蓋的屬性不同 | 是 |
| 2 | B-R1 | 高 | src/index.html:1009、1074-1075、1742、2093-2096、2296-2302；data.js:121；data23.js:13、16；1668-1674 | 五個分頁的卡片和面板連結大量使用**流水號**：怪物 `m<i>`、遊戲才有的裝備 `x<N>`、官網沒有的道具 `g<N>`、NPC `n<f>_<i>`、配方 `r\|<N>`。 | 是 |
| 3 | C-R9 | 高 | data.js:121、489；src/index.html:937、1074、1590、1742、2002 | 配方 r\|N、NPC n<f>_N、主線 mq<f>_N、支線 q<N>／f<f>q<N>、怪物 m<N> 都是陣列索引；資料順序一變，同一個 id 打開別的東西（和 B-R1、D-R12-2 同一件事） | R0.6（資料 ID）；測試清單可以先補 |
| 4 | A-R1 | 中 | :3639–3641、:713–717 | 重複 HTML ID（執行時） | 是 |
| 5 | A-R11 | 中 | :3612、:3746、:3720、:3135、:3596 等（見 2.2 節） | 拆分 src/index.html 時必須相容的識別：同名 function show（:3612／:3746）、導覽的 const esc 遮蔽 HTML escaper、宣告順序（COLLAB_PAUSE :3135 在 setFloor 使用）、window 介面、id、data 屬性、class、body 狀態、localStorage | 否（拆分時的相容清單） |
| 6 | A-R11a | 中 | :3721–3729 | 導覽依賴 9 個 selector | 否（測試補強） |
| 7 | A-R13 | 中 | :3593–3599、:3614 | #32 規則「切換樓層關閉面板」不成立（桌面裝備面板） | 是（一處：`setFloor`／`show()` 在桌面、換樓層、目前面板是裝備面板時 `closeP()`，不影響其他 |
| 8 | A-R14 | 中 | :1176–1179、:1233、:3671 | 瀏覽器「上一頁」和面板狀態脫鉤；面板不帶樓層 | 視站長決定 |
| 9 | A-R5 | 中 | :1475、:2962 | Esc 順序 | 是 |
| 10 | A-R6 | 中 | :3601–3605、:3644–3657、:3624–3637、:1183 等 | 桌面／手機判斷混用 4 種寫法 | 是 |
| 11 | A-R7 | 中 | :1188、:1226、:3614、:1197 | 面板狀態和 DOM | 是（小） |
| 12 | A-R8 | 中 | 見下表 | 切樓層或分頁時被重建的 DOM | 是（拆分時） |
| 13 | B-R2 | 中 | src/index.html:1701、1703-1704 | `recGoBtns` 和 `recipeTable` 用 `ALLREC.findIndex(npc 和 en 相同)` 找配方序號，**沒有比樓層**；`recRow` 產生的列沒有 `.i`，所以 NPC 面板一定走 findIndex。 | 是 |
| 14 | B-R3 | 中 | src/index.html:1681、1554、1715、1667、2094、2112、2397、1513-1515 | 用名稱當鍵的查找在名稱重複時取第一個或最後一個，沒有警告。 | 是（遷移時） |
| 15 | B-R4 | 中 | src/index.html:713-717、3639-3641 | `syncVTabs` 用 innerHTML 把 `#codexTabs a` 整段複製到 5 個分頁的 `.vtabs`，連同 `<span id="nMon">` 等 5 個 id。 | 是 |
| 16 | B-R5 | 中 | src/index.html:1242-1265、1291-1306、2263-2276、2405-2416、1980-1992 | 面板的區塊（掉落物、取得方式、用途、可以拿去製作、製作方式、回收物品…）只有 `h3.sec` 的文字，沒有任何識別屬性；同一面板裡相同的 `data-go` 也會重複。 | 是 |
| 17 | C-R1 | 中 | src/index.html:3482（townRow `data-tp`）、3496（首領列 `data-tp`）、3500（NPC 列 `data-tp`）、3541（filterMap 用 `data-tp` 篩列） | 右側清單的城鎮、首領、NPC 列用 `data-tp` 存「英文名稱＋類別」字串來比對搜尋，裡面沒有官方中文名（`pN(t)`、`mN(m)`、`npcN(n.n)`）。地圖標記用的 `townHit`／`npcHit`／`monHit` 有比對中文名，所以兩邊結果不一致。 | 是 |
| 18 | C-R14 | 中 | src/index.html:2434 | 樓層首領「看圖鑑」的連結用 `m.name.startsWith(Fx.boss)` 找怪物。第 2 層的 `boss` 是 "Asterius"，第 2 層怪物資料裡沒有名稱以 "Asterius" 開頭的怪物（Boss 類有 8 隻：Winnie, Man's Best Friend／Melisara, Sovereign of th | 是（資料或程式） |
| 19 | D-R12-1 | 中（遷移工作量與基準失效，不是線上故障） | src/index.html:1668–1675、1742、3204；reports.js；tests/baseline/fixtures/reports.js | 配方 id 是 `r\|<ALLREC 索引>`，而 ALLREC 是在**配方回報併入之後**才建：L1671–1675 對既有 NPC 是 `Rn.items.push(row)`（同 NPC 同名物品才原地取代），新 NPC 則在 `RECIPES` 物件尾端加鍵。所以 Apps Script 核准一筆「既有 NPC 的新配方」回報 | R0.6 時要 |
| 20 | D-R12-2 | 中（遷移工作量與基準失效，不是線上故障） | data.js:121、data23.js:13、src/index.html:1074、1590、2094、2299 | 怪物 `m<i>`／`f2m<i>`、NPC `n<f>_<i>`、主線 `mq<f>_<i>`、遊戲才有的裝備 `e\|x<k>`、遊戲才有的消耗品 `p\|g<k>`（L2299）都依陣列或物件鍵順序；在資料檔中間插入一筆，後面全部位移。EQX 的 k 依 `ITEMS` 合併順序（data.js 鍵 → data23.js 鍵 →  | R0.6 時要 |
| 21 | D-R12-3 | 中 | src/index.html:986–1030、970–981 | 玩家回報用**名稱**對資料：怪物用 name／aka／圖鑑編號／「舊名：X」，地點用 `n`／`old`，NPC 用名稱，任務用標題／aka，掉落和材料用 `ikey` 後的 ITEMS 名稱。而且 `renameMon` 會在**執行時**依回報改怪物名稱、把舊名塞進 aka，建置時的 check_refs 看不到這一步（只在 W11 | R0.6 時要 |
| 22 | D-R12-4 | 中 | src/index.html:1237–1239、1422–1423、1464–1470、1480 | `data-go`、`data-key` 是兩段 `<t>\|<id>`，`data-goview` 是三段 `<view>\|<t>\|<id>`；三者的**實體身份部分**（`<t>\|<id>`）必須一致：`markSel` 用 `[data-key="${t}\|${CSS.escape(id)}"]` 標選取、`goView`  | R0.6 時要 |
| 23 | D-R12-5 | 中 | src/index.html:1019–1022、922、2688、967 | 程式內寫死的名稱表：`ITEM_OLD`、`REP_MAT`、`DG_DIM`、`NPC_ZH`（回報 NPC 類別中文→npcs.js 類別鍵）；check_refs.py 只讀 NPC_NOTE 這一張（:756–778） | 是（工具） |
| 24 | D-R3 | 中 | src/index.html:3202–3204 | 已收錄清單的「看怪物資料／看配方／看任務」連結是在 render 時用**名稱**或**陣列索引**找：`FLOORS[f].M.find(x=>x.name===r.name\|\|aka)`、`ALLREC.findIndex(x=>x.rep===r.id)`、`MQ(f).findIndex(x=>(x.reps\|\|[]).i | R0.6 時要 |
| 25 | D-R5 | 中（v2 由低提高：會把第 2、3 層的玩家切回第 1 層，並讓回報表單預填樓層變成 1） | src/index.html:1939 | 關於本站「協作區」連結寫死 `href="#report"`，不經 `hashFor`；在第 2、3 層點了會到 `#report`＝**第 1 層**的協作區（show 依 hash 設樓層） | 是（小） |
| 26 | D-R8 | 中 | src/index.html:2688–2691；tools/jm_merge.py `DUNGEONS`；`tiles/dg/<id>/`；jmmeta.js `SAO_JM.dg` | 地下城地圖以 SPOTS 的手寫 id（xal、geldorakd、fallen、kobold）當資料夾名與 jmmeta 鍵；`dgName` 用 `FLOORS[1].spots.find(id)` | R0.6 時才需要 |
| 27 | A-R12 | 低 | :3612–3613 | hash 容錯不改寫網址 | 可選 |
| 28 | A-R1b | 低 | :2585、:3195 | `doneC`／`doneL` 靜態重複 | 否（現況正確），整理時可順手處理 |
| 29 | A-R2a | 低 | :695–703、:1420 | `data-v` 兩種意義 | 否 |
| 30 | A-R2b | 低 | :881–882 | `.rwin` 兩個視窗共用 | 否 |
| 31 | A-R2c | 低 | :3666–3668 | document 委派依賴 `.filters,.topf,.rsel` 三個 class | 否，拆分時寫進相容清單 |
| 32 | A-R9 | 低 | :3684–3686 | `goRep` 用輪詢等 `#doneL li[data-rid]` | 可選 |
| 33 | B-R6 | 低 | src/index.html:1420、3644-3665、2173-2184、1519、2322、2320 | 動態按鈕的定位方式：①已篩選列 `.af[data-i]`、`.afm[data-p]` 只有序號；②效果清單的清除鈕和選項共用 `data-eff`（清除是空字串）；③素材分類、道具分類和細分的 `data-v` 是中文顯示名；④`chipsInto` 寫 `data-v` 沒有 esc。 | 是（小） |
| 34 | B-R7 | 低 | src/index.html:3566、3638、1479、1702、1971、1545、1578、1258、1299、1529、2031、2084 | 名稱不一致但功能相同（或同名不同功能）：`CODEX` 和 `CODEX_V` 是同一份清單；`#codexTabs` 和 `.vtabs` 兩套導覽；`data-goview` 第一段沒人讀、`goView` 是死碼（它的重設會點 `data-v="all"`，會把取得樓層從預設「這一層＋還不知道」改成「全部樓層」）；`.npcgh`  | 是（小） |
| 35 | B-R8 | 低 | src/index.html:2254、2334、1543 | 裝備、道具只畫前 240 件，素材前 600 件；其餘不在 DOM。 | 否 |
| 36 | B-R9 | 低 | src/index.html:1498、2251、2332-2333、1535 | 「名稱」排序用內部名稱（怪物英文、裝備／道具法文、素材英文 key），畫面標題是中文。 | 視決定 |
| 37 | C-R10 | 低 | src/index.html:979–981 | 玩家回報的任務用標題或 NPC 名稱對到網站的任務。 | R0.6 |
| 38 | C-R11 | 低 | src/index.html:1329–1333（`dgKeys`） | 地下城鑰匙用兩種方式推斷，都不是 ID：① 地點 `note` 裡用正則抓 `Clé …` 法文名，再比對官網道具名；② 找入口 150 格內 NPC 做的鑰匙配方。 | R0.6 |
| 39 | C-R12 | 低 | src/index.html:1801（`isTowerSp`） | 用 `zh` 是否含「樓層首領」來判斷地點是不是樓層首領塔。 | R0.6 |
| 40 | C-R13 | 低 | src/index.html:1888（cwin 卡片 `data-key="e\|oid"`）、1237（`markSel` 掃整份 document） | `#cwin` 的卡片和裝備分頁的卡片用同一個 `data-key`。 | 可選 |
| 41 | C-R2 | 低 | src/index.html:3512–3527、803 | `showRoute` 沒有呼叫者，所以 `ROUTE` 永遠是 null、`#routeBar` 永遠不會出現；`drawRoute()` 雖然每次 renderMap 都呼叫（3445），但一定立刻 return。主線說明 `#qNoteMain` 還寫「按『在地圖上看路線』會在地圖上畫出步驟順序」，但頁面上沒有這顆按鈕。 | 是（文字） |
| 42 | C-R3 | 低 | src/index.html:731、3313 | `#dgSel` 永遠隱藏，但事件還在。 | 可選 |
| 43 | C-R4 | 低 | src/index.html:3479 | `.zsec` 的 `data-k` 和 `ZOPEN` 用分組的顯示標題文字當 key。 | 可選 |
| 44 | C-R5 | 低 | renderMap NPC 迴圈、`markSel`（1237） | 地圖上的 NPC 標記沒有 `data-key`。 | 可選 |
| 45 | C-R6 | 低 | src/index.html:3340（`underCrop` 的 `URL.createObjectURL`） | 每展開一次地下圖就產生一個 blob URL，從來沒有 revoke。 | 可選 |
| 46 | C-R7 | 低 | src/index.html:1057（SPAWNS） | 首領重生點用怪物名稱連到怪物（`monByName[n]`，`.filter(p=>p.m)`）。 | R0.6 |
| 47 | C-R8 | 低 | src/index.html:2002 | `mqCard` 的 id 用目前樓層 `FL` 組成（`"mq"+FL+"_"+i`），不是任務本身的樓層。 | 可選 |
| 48 | D-R1 | 低 | src/index.html:2585、3195、2601 | auto_checks 說 `#doneL`／`#doneC` 出現兩次：一次在舊版 `buildReport`（GitHub issue 流程，L2585），一次在 `buildFormReport`（L3195）。兩者都寫進 `#rWrap.innerHTML`，**互斥，不會同時存在**；而且 `FORM_PREFILL` 有字面值 | 否（現況）；清理是選擇 |
| 49 | D-R12-6 | 低 | src/index.html:3612、1049–1082 | 深層連結：網址只帶樓層＋分頁，不帶資料 id；localStorage 也不存資料 id | 否 |
| 50 | D-R12-7 | 低 | src/index.html:1001、1006、976 | 回報新增的怪物 `rep-<回報 id>`、地點 `rp-<回報 id>` 已經是穩定 id；回報新增的 NPC 卻是 `n<f>_<i>`（push 到尾端） | R0.6 時要 |
| 51 | D-R2 | 低 | src/index.html:3684–3686 | `goRep` 用 `setInterval` 50ms×40 次找 `#doneL li.replist[data-rid]`，找不到就靜默放棄 | 可選 |
| 52 | D-R4 | 低 | src/index.html:3133、3141 | `#fbL` 讀 GitHub API 失敗時寫「讀不到」，但沒有區分「0 則」和 API 限流（未登入每小時 60 次） | 否 |
| 53 | D-R6 | 低 | src/index.html:1910、1959、3165、3186 | 說明文字互相矛盾或過時：`ABOUT_SRC` 寫 JourneyMap 只有「第 1 層探索地圖」、資料來源 note 寫「第 2、3 層是開放前的 wiki 資料」（CLAUDE.md：11/11 已改成新聞＋參考地圖＋JourneyMap）；回報表單說明寫「目前只合併第 1 層」，打包說明 `.jmscope` 寫第 2、3 層地面 | 否（文字） |
| 54 | D-R7 | 低 | src/index.html:3125 | 下載檔名固定 `探索地圖-第1層-…zip`，但更新打包可同時含第 2、3 層方格、全地圖打包也含第 2、3 層地面 | 可選 |

共 54 項。完整的「影響、建議修法、證據」在下面第 2 節（依分工原文）。

## 2. 詳細內容

### 2.1 分工 A、C 各區的風險（條列）

#### A｜1. 頁首和全站導航

- **A-R1｜中｜:3639–3641、:713–717｜重複 HTML ID（執行時）**：`syncVTabs` 把 `#codexTabs a` 的 innerHTML 原樣複製到 5 個圖鑑分頁的 `.vtabs`，裡面的 `<span id="nMon">` 等 5 個 id 一起被複製，所以頁面上 `nMon`、`nEquip`、`nProp`、`nItem`、`nNpc` 各有 6 個（VERIFIED：report、feedback、classes 頁都量到 6）。**實際影響**：`$("nMon")` 只拿到 DOM 順序第一個（`#codexTabs` 裡的那個，因為它在各分頁之前），數字靠下一次 `syncVTabs` 再複製才會同步；Playwright 嚴格模式用 `#nMon` 會因為多個元素而失敗；螢幕閱讀器、`aria` 參照會混淆。**建議**：`.vtabs` 從 `CODEX` 陣列產生，不複製 innerHTML；或複製後移除 id。**需要程式修改**：是。**證據**：check2 `dups`；auto_checks 只看原始碼字面，抓不到這種執行時重複。
- **A-R1b｜低｜:2585、:3195｜`doneC`／`doneL` 靜態重複**：auto_checks 找到兩處字面定義。:2585 在 `buildReport()`（舊的 GitHub issue 回報表單），:3195 在 `buildFormReport()`；`renderReport`（:3200–3201）依 `FORM_PREFILL` 二選一，而且 `rBuilt` 只建一次，兩者都寫 `#rWrap.innerHTML`（互相取代）。`FORM_PREFILL` 有寫死的備用網址（:2601），永遠是真值，所以 `buildReport` 在目前程式裡**不會執行**（死碼）。**實際影響**：沒有（VERIFIED：#report、#feedback 都只有 1 個 `#doneC`／`#doneL`）。**建議**：拆分時刪掉 `buildReport` 或抽成同一個共用片段。**需要程式修改**：否（現況正確），整理時可順手處理。
- **A-R2a｜低｜:695–703、:1420｜`data-v` 兩種意義**：上方選單、`#codexTabs`、`.vtabs` 的 `data-v` 是 view 名，篩選膠囊 `.chip[data-v]`（`chipsInto`）是篩選值（例如 `all`、`here`）。目前每個 selector 都有範圍（`nav.tabs a`、`.vtabs a`、`.chip[data-v=...]`），沒有誤抓。**建議**：拆分時保留範圍，新程式不要寫裸的 `[data-v]`。**需要程式修改**：否。
- **A-R11a｜中｜:3721–3729｜導覽依賴 9 個 selector**：見上表。改 id 不會報錯，只會框錯或不框。**建議**：拆分後加一個測試逐步檢查 `target(s)` 都找得到元素。**需要程式修改**：否（測試補強）。
- 檢查過、沒有問題：主題切換（不存在，已寫明）；`#updBar`（只建立一次，`shown` 防重複）；樓層格子（只產生一次，VERIFIED 換樓層沒有重建）。


#### A｜2. 路由

- **A-R3｜高｜:1212–1231、:1422–1423、:1458–1470｜三套各自的連結綁定，涵蓋的屬性不同**：同樣的 `detailHTML` 被放進 3 個容器，各自綁定不同的屬性：

  | 屬性 | `#pBody`（renderP） | `.gvbody`（gvRender） | `#cwBody`（bindGo） | 清單（bindGo） |
  |---|---|---|---|---|
  | data-go | ✓（push／內嵌另算） | ✓（gvLink） | ✓（openP new，**取代職業面板**） | ✓ |
  | data-goview | ✓ | ✓ | ✓ | ✓ |
  | data-rep | ✓ | ✓（只有單點） | ✗（VERIFIED 點了沒反應） | ✗ |
  | data-route | ✓ | ✓ | ✗ | — |
  | data-imap | ✓ | ✓ | ✗ | — |
  | data-spot | ✓ | ✓ | ✗ | — |
  | data-town | ✓ | **✗（VERIFIED 點了沒反應）** | ✗ | — |
  | data-eqcls | ✓ | ✓ | ✗ | — |
  | data-repgo | document 委派 | 委派＋關閉全部 | 委派 | 委派 |
  | data-imgzoom／dgmap／under | document 委派 | document 委派 | document 委派 | — |

  **實際影響**：在彈出視窗裡打開城鎮後「在地圖上查看」沒反應；在職業裝備視窗裡點裝備的座標沒反應；職業裝備視窗裡點裝備面板的連結（例如製作 NPC）會把右側職業頁換成一般面板（VERIFIED：crumb 從「戰士」變「Corrupted Boar Accessories」、`cls-inline` 消失），和 :1893 註解「右側面板（職業）保持不變」矛盾。**建議修法**：拆分時做一個共用的 `bindDetail(root, ctx)`，所有屬性一次處理，依 ctx（panel／popup／cwin）決定開哪裡。**需要程式修改**：是。**證據**：check2 `gvTownClick`、check3 `cwRep`、`cwGo`。
- **A-R12｜低｜:3612–3613｜hash 容錯不改寫網址**：`#f9-equip` 顯示第 1 層但網址留 `#f9-equip`；`#bogus` 顯示地圖但網址不變；正則接受 3 位數樓層（TOTAL 是 100）。選單 `href` 會改成正確的第 1 層。**影響**：分享出去的網址和畫面不一致；不會壞。**建議**：不合法時 `history.replaceState` 成正規形式。**需要程式修改**：可選。**證據**：check4。
- **A-R9｜低｜:3684–3686｜`goRep` 用輪詢等 `#doneL li[data-rid]`**：40×50 ms 內找不到就靜默放棄（例如 reports.js 還沒載入）。**建議**：改成 `renderReport` 完成後的 callback。**需要程式修改**：可選。
- **A-R14｜中｜:1176–1179、:1233、:3671｜瀏覽器「上一頁」和面板狀態脫鉤；面板不帶樓層**：面板、彈出視窗、視窗的堆疊只在 JS 變數裡，沒有 `pushState`／`popstate`（grep 0 筆），瀏覽器上一頁只換分頁／樓層，不會退回上一筆資料；`openP` 也不改 `FL`，從面板跳到別層的資料時，頁面其他部分仍是原樓層。**影響**：手機使用者習慣按返回鍵，會直接離開分頁而不是關面板。**建議**：拆分時決定是否把面板開關放進歷史。**需要程式修改**：視站長決定。**證據**：CODE。
- 檢查過、沒有問題：`go()` 只改 hash，所有畫面變化都集中在 `show()`；`.csub a`（協作區子分頁）沒有 click 處理，是普通連結，靠 hashchange 進 `show()`，正常。


#### A｜3. 共用面板和視窗

- **A-R5｜中｜:1475、:2962｜Esc 順序**：（a）看圖視窗的監聽器在打開時才註冊，排在彈出視窗（:1475，載入時註冊）之後；兩者都在 capture 階段而且彈出視窗那個會 `stopImmediatePropagation`，所以**在彈出視窗裡打開任務圖片，按 Esc 先關掉下面的彈出視窗**，圖片還浮在畫面上，要再按一次（VERIFIED：check2 第一次 Esc 後 `gv:0, img:true`，第二次才 `img:false`）。（b）bubble 階段 5～10 都不停止傳遞，**一次 Esc 會同時關掉面板、路線視窗、職業裝備視窗**（VERIFIED：任務面板＋路線視窗，一次 Esc 兩個都關；職業裝備視窗同理，CODE）。smoke 只測了「看圖視窗在面板上」和「彈出視窗在面板上」兩種組合。**建議修法**：一個 Esc 管理器，維護「打開順序」的堆疊，每次只關最上層。**需要程式修改**：是。
- **A-R7｜中｜:1188、:1226、:3614、:1197｜面板狀態和 DOM**：面板的真正狀態是 JS 變數 `stack`（不是 DOM），這點是好的；但有兩處反過來讀 DOM：（1）`data-rep` 用 `#pCrumb` 的文字最後一段當浮動地圖標題（:1226），名稱顯示改了就跟著變；（2）關閉時 `#pCrumb` 不清（VERIFIED），目前沒有地方讀關閉後的文字，但拆分後若有人拿它判斷就會錯。另外「是不是內嵌頁」離開分頁時看 `stack[0]`、`fitClsPanel` 看 `stack[last]`。**建議**：標題由 `stack` 算；`closeP` 清空 crumb；內嵌判斷統一。**需要程式修改**：是（小）。
- **A-R2b｜低｜:881–882｜`.rwin` 兩個視窗共用**：`#cwin` 和 `#rwin` 都是 `class="rwin"`，`.rwhead` 也共用。JS 都用 id，CSS 共用是刻意的。拆分時新程式不要用 `.rwin` 找「路線視窗」。**需要程式修改**：否。
- 檢查過、沒有問題：彈出視窗、面板、裝備視窗同時打開同一筆資料時，detail HTML 裡沒有固定 id（只有 `miniTiles` 的 `mt<流水號>` 遮罩 id，每次呼叫都新編號，全站 279 個沒有重複）——VERIFIED check2 `detailIds`；所以同一筆資料放進 3 個容器不會造成重複 id。


#### A｜4. 列表頁共用機制

- **A-R6｜中｜:3601–3605、:3644–3657、:3624–3637、:1183 等｜桌面／手機判斷混用 4 種寫法**：`matchMedia("(max-width:820px)").matches`（10 處：:1183、:1187、:1209、:1220、:1447、:3285、:3323、:3523、:3614、:3707）、`innerWidth>820`（4 處：:1198、:1813、:1841、:3614）、`topMQ`＝`matchMedia("(min-width:821px)")`（:3625）、`innerWidth>=1180`（:3675）；CSS 另有 18 個 `max-width:820px`、12 個 `min-width:821px`、3 個 `min-width:1180px`、2 個 `max-width:1600px`。:3614 同一行裡兩種寫法都用，判斷條件分散在各處，日後改斷點時要改 4 種地方。另外 `fbarSync` 和 `actControls` 對「預設值」的判斷不同（前者寫死 `all`，後者看 `data-def`），已實測出錯（見 global.list.fbar）。**實際影響**：裝備分頁的「更多篩選」一打開就顯示「已調整 1 項」（VERIFIED）；道具分頁 `#fPrFl` 也是 `data-def="here"`、選項含 `all`（`FL_CHIPS` :2140），推定同樣（CODE，未實測）。**建議**：一個 `isPhone()`／`isWide()` 共用函式；`fbarSync` 用 `data-def`。**需要程式修改**：是。**證據**：check3。
- **A-R8｜中｜見下表｜切樓層或分頁時被重建的 DOM**（VERIFIED，check3：在節點上掛 JS 屬性，看操作後是不是同一個節點）：

  | 節點 | 打一個字（`#q`） | 切分頁再回來 | 換樓層（同分頁） | 點篩選膠囊 |
  |---|---|---|---|---|
  | `#lEq .card`（清單卡片） | 重建 | 重建 | 重建 | 重建 |
  | `.vtabs a` | 重建 | 重建 | 重建 | 保留 |
  | `#floorInfo>*` | 保留 | 保留 | **重建** | 保留 |
  | `#zlist>*`（地圖右側清單） | 保留 | 保留 | **重建** | 保留 |
  | `#pBody>*`（面板內容） | 保留 | 保留 | **保留（不重畫，內容停在舊樓層）** | 保留 |
  | `.flcell`、`#flGrid`、`#codexTabs a` | 保留 | 保留 | 保留 | 保留 |
  | `#fEqPart .chip`、`.topf`、`.rsel`、`.actf` 外殼 | 保留 | 保留 | 保留 | 保留 |

  **實際影響**：任何掛在卡片、`.vtabs`、`#floorInfo` 上的直接事件綁定（`onclick`）每次都要重綁，目前都有重綁；外部程式（測試、未來元件）不能拿著舊節點參照。`.topf`／`.rsel` 是「搬移」不是重建，靠 `g.__home` 這個 DOM 節點上的 JS 屬性記原位，拆分成模組時若重新產生 `.fgroup`，`__home` 就斷了。**建議**：清單用委派事件（掛在不重建的 `#l<X>` 上）；`.topf`／`.rsel` 改成 CSS 版面（同一個節點，用 grid area 放位置），不再搬 DOM。**需要程式修改**：是（拆分時）。
- **A-R2c｜低｜:3666–3668｜document 委派依賴 `.filters,.topf,.rsel` 三個 class**：任何控制項只要在這三個容器裡，click／change／input 都會觸發一次 `setTimeout(actSync)`；`.fbar` 也在 `.filters` 裡。新增的元件要放在這三個容器內才會同步「已篩選」列。**需要程式修改**：否，拆分時寫進相容清單。


#### C｜1. 地圖 `#view-map`

- **C-R1｜中｜src/index.html:3482（townRow `data-tp`）、3496（首領列 `data-tp`）、3500（NPC 列 `data-tp`）、3541（filterMap 用 `data-tp` 篩列）**
  - 問題：右側清單的城鎮、首領、NPC 列用 `data-tp` 存「英文名稱＋類別」字串來比對搜尋，裡面沒有官方中文名（`pN(t)`、`mN(m)`、`npcN(n.n)`）。地圖標記用的 `townHit`／`npcHit`／`monHit` 有比對中文名，所以兩邊結果不一致。
  - 實際影響：用官方中文名搜尋時，地圖上有標記，右側清單卻全部藏起來。實測：搜「煉金術士」時地圖顯示 2 個 NPC、清單 0 列；搜「起始之鎮」時地圖顯示城鎮、清單 0 列。搜英文「Alchemist」「Starting」時清單有列。smoke.py:184 只測英文「hanaka」，所以沒抓到。
  - 建議修法：城鎮、首領、NPC 列改成和地點列一樣，用身份屬性（`data-t`、`data-key`、`data-n`）配合 `townHit`／`monHit`／`npcHit` 比對；或者把 `pN`／`mN`／`npcN` 加進 `data-tp`。
  - 需要改程式：是。
  - 證據：VERIFIED（c_probe.py 的 `desk_srch_煉金術士`、`mob_srch_起始之鎮`：`rowsVisible: []`）。
- **C-R2｜低｜src/index.html:3512–3527、803**
  - 問題：`showRoute` 沒有呼叫者，所以 `ROUTE` 永遠是 null、`#routeBar` 永遠不會出現；`drawRoute()` 雖然每次 renderMap 都呼叫（3445），但一定立刻 return。主線說明 `#qNoteMain` 還寫「按『在地圖上看路線』會在地圖上畫出步驟順序」，但頁面上沒有這顆按鈕。
  - 實際影響：說明文字誤導玩家。
  - 建議修法：改說明文字，指向面板的「放大查看路線」；刪掉死碼，或補回按鈕。
  - 需要改程式：是（文字）。
  - 證據：CODE（`grep -n 'showRoute\b'` 只有定義 3523；`ROUTE=` 只有 3512、3513、3523）。
- **C-R3｜低｜src/index.html:731、3313**
  - 問題：`#dgSel` 永遠隱藏，但事件還在。
  - 實際影響：沒有使用者影響；只是盤點時的雜訊。
  - 建議修法：刪除，或在 R0.6 清理時移除。
  - 需要改程式：可選。
  - 證據：CODE。
- **C-R4｜低｜src/index.html:3479**
  - 問題：`.zsec` 的 `data-k` 和 `ZOPEN` 用分組的顯示標題文字當 key。
  - 實際影響：改文字或改圖示時，手機上已展開的分組狀態會失效（只在同一次瀏覽有效，影響很小）。
  - 建議修法：改用固定代碼（tp-town、tp-spot、land、gather…）。
  - 需要改程式：可選。
  - 證據：CODE。
- **C-R5｜低｜renderMap NPC 迴圈、`markSel`（1237）**
  - 問題：地圖上的 NPC 標記沒有 `data-key`。
  - 實際影響：NPC 面板開著時，地圖標記不會亮（怪物縮圖會亮）。這是功能缺口，不是錯誤。
  - 建議修法：加 `data-key="n|<id>"`。
  - 需要改程式：可選。
  - 證據：CODE。
- **C-R6｜低｜src/index.html:3340（`underCrop` 的 `URL.createObjectURL`）**
  - 問題：每展開一次地下圖就產生一個 blob URL，從來沒有 revoke。
  - 實際影響：長時間反覆展開時有少量記憶體累積。
  - 建議修法：收起或移除 figure 時 revoke。
  - 需要改程式：可選。
  - 證據：CODE。
- **C-R7｜低｜src/index.html:1057（SPAWNS）**
  - 問題：首領重生點用怪物名稱連到怪物（`monByName[n]`，`.filter(p=>p.m)`）。
  - 實際影響：怪物改名時如果沒有同步改 aka，重生點會**靜默消失**，不會報錯。
  - 建議修法：R0.6 改成用怪物 ID；過渡期在 check_refs 的掃描範圍裡加上 `BOSS_SPAWNS`。
  - 需要改程式：R0.6。
  - 證據：CODE。
- **已檢查但沒發現問題的項目**：
  - 手機寬度（390）地圖分頁沒有左右捲動（VERIFIED）。
  - 篩選面板：桌面固定展開、手機隱藏，和 CLAUDE.md 一致（VERIFIED）。
  - 游標座標只在桌面顯示（VERIFIED）。
  - 地圖分頁沒有 console 錯誤（VERIFIED，`desk_errs`／`mob_errs` 都是空的）。


#### C｜2. 任務 `#view-quests`

- **C-R8｜低｜src/index.html:2002**
  - 問題：`mqCard` 的 id 用目前樓層 `FL` 組成（`"mq"+FL+"_"+i`），不是任務本身的樓層。
  - 實際影響：目前清單只列目前樓層，結果正確；但這是隱含假設，日後如果做跨樓層清單或搜尋，會組出錯的 id。
  - 建議修法：改成傳樓層參數。
  - 需要改程式：可選。
  - 證據：CODE 2002、2005。
- **C-R10｜低｜src/index.html:979–981**
  - 問題：玩家回報的任務用標題或 NPC 名稱對到網站的任務。
  - 實際影響：網站任務標題改名後，舊回報就對不上（回報只會留在協作區清單，不會報錯）。
  - 建議修法：R0.6 改用任務 ID，或保留標題別名（`aka` 已有部分支援）。
  - 需要改程式：R0.6。
  - 證據：CODE。
- **已檢查但沒發現問題的項目**：
  - 主線、支線切換，城鎮 chip，依村鎮排序的分組標題（VERIFIED）。
  - 手機寬度沒有左右捲動（VERIFIED）。
  - 路線視窗會在換分頁時關閉（CODE 3614；smoke.py:134）。


#### C｜3. 配方 `#view-recipes`

- **C-R11｜低｜src/index.html:1329–1333（`dgKeys`）**
  - 問題：地下城鑰匙用兩種方式推斷，都不是 ID：① 地點 `note` 裡用正則抓 `Clé …` 法文名，再比對官網道具名；② 找入口 150 格內 NPC 做的鑰匙配方。
  - 實際影響：改 note 文字或搬 NPC 都會讓鑰匙改變或消失，不會報錯。地下城卡片圖示、面板「需要的鑰匙」、配方面板「用途」都依賴它。
  - 建議修法：R0.6 在地點資料加明確的 `key` 欄位（配方或道具 ID）。
  - 需要改程式：R0.6。
  - 證據：CODE。
- **已檢查但沒發現問題的項目**：
  - 配方分頁只列有材料的配方：87 筆，和 CLAUDE.md 一致（VERIFIED）。
  - NPC 下拉選單：桌面搬到標題旁，手機留在原位（VERIFIED `rselMoved` true／false）。


#### C｜4. 地下城 `#view-dungeons`

- **C-R11**：見第 3 節。
- **C-R12｜低｜src/index.html:1801（`isTowerSp`）**
  - 問題：用 `zh` 是否含「樓層首領」來判斷地點是不是樓層首領塔。
  - 實際影響：改中文說明就會影響排序和「樓層首領塔」標籤。
  - 建議修法：加資料欄位。
  - 需要改程式：R0.6。
  - 證據：CODE。
- **已檢查但沒發現問題的項目**：
  - 活動地下城只在第 1 層列出（CODE 1804）。
  - 換樓層時，清單裡沒有目前面板的東西就換成第一個，清單是空的就關掉面板（CODE 1812–1814）。
  - 手機不自動開面板（VERIFIED）。


#### C｜5. 職業 `#view-classes`

- **C-R13｜低｜src/index.html:1888（cwin 卡片 `data-key="e|oid"`）、1237（`markSel` 掃整份 document）**
  - 問題：`#cwin` 的卡片和裝備分頁的卡片用同一個 `data-key`。
  - 實際影響：右側面板開著某件裝備時，`#cwin` 裡同一件卡片也會被標成 `.sel`。目前看不出問題，但兩處用同一個識別。實測：開 `#cwin` 後 `.card.sel`＝1。
  - 建議修法：`#cwin` 卡片改用 `data-cwe` 就好，或者讓 `markSel` 限定範圍。
  - 需要改程式：可選。
  - 證據：VERIFIED `selMarked:1`；CODE。
- **已檢查但沒發現問題的項目**：
  - 官網配裝連結的參數和 class id 相同（VERIFIED）。
  - 手機不自動開面板（VERIFIED）。


#### C｜6. 世界王 `#view-bosses`

- **C-R14｜中｜src/index.html:2434**
  - 問題：樓層首領「看圖鑑」的連結用 `m.name.startsWith(Fx.boss)` 找怪物。第 2 層的 `boss` 是 "Asterius"，第 2 層怪物資料裡沒有名稱以 "Asterius" 開頭的怪物（Boss 類有 8 隻：Winnie, Man's Best Friend／Melisara, Sovereign of the Hive／Sanctuary Guardian／Magnus, Colossus of the Veins／Velindra the Weaver／Morverth the Soul Flayer／Rugibœuf, The Guardian／Taurus）。另外 `Fx.status==="soon"` 的判斷已經沒有樓層會用到（第 2、3 層是 `new`）。
  - 實際影響：第 2 層顯示「（圖鑑還沒有收錄）」。實測：頁面上只有第 1、3 層的連結。Asterius 對應哪一隻（或還沒有收錄）要由站長確認，本盤點不判斷。
  - 建議修法：floors 資料加樓層首領的怪物 id；或者先確認 Asterius 和 Taurus 的關係。
  - 需要改程式：是（資料或程式）。
  - 證據：VERIFIED（`desk_boss.go`）；`node` 讀 data23：第 2 層 boss "Asterius"，Boss 類怪物清單裡沒有 Asterius。
- **已檢查但沒發現問題的項目**：
  - 手機寬度沒有左右捲動（VERIFIED）。
  - 3/4／正面切換按鈕存在（VERIFIED）。


### 2.2 分工 A：風險檢查第 1、2、5、6、7、8、11 項彙整


| 項 | 風險 ID | 結論 |
|---|---|---|
| 1 重複 HTML ID | A-R1、A-R1b | `doneC`／`doneL`：**不會同時存在**（:2585 在 `buildReport`，目前是死碼；:3195 在 `buildFormReport`；兩者都寫 `#rWrap.innerHTML`，VERIFIED 只有 1 個）。**新發現**：執行時 `nMon`／`nEquip`／`nProp`／`nItem`／`nNpc` 各 6 個（`.vtabs` 複製），auto_checks 的字面掃描抓不到。detail HTML 放進 3 個容器不會產生重複 id（VERIFIED）。 |
| 2 不同元件共用 selector | A-R2a、A-R2b、A-R2c | `data-v`（選單 view 名／膠囊值）、`.rwin`（兩個視窗）、`.subtabs`（`#codexTabs` 和協作區 `.csub`，:86）、`.rhead`（列表標題和協作區 `collabHead` :2607；`actSync`／`placeTopFilters` 限定 `.view.browse`，不會誤抓）、`.card[data-key]`（清單卡片和 `#cwBody` 卡片都會被 `markSel` 加 `.sel`，屬預期）。目前都有範圍限定，沒有實際誤抓。 |
| 5 事件委派是否依賴不穩定 DOM | A-R3、A-R8、A-R9 | document 層委派 25 個（auto_checks），其中 `.vtabs a`、`[data-repgo]`、`a[data-imgzoom]`、`[data-dgmap]`、`[data-under]` 是穩定的（委派在 document，不怕重建）。**不穩定的是直接綁定**：`bindGo`／`renderP`／`gvRender` 在每次重畫後對新節點逐一 `onclick`，三套涵蓋的屬性不同（A-R3 表）。`goRep` 用輪詢等節點出現。 |
| 6 桌面／手機邏輯識別衝突 | A-R6 | 4 種斷點寫法混用；`fbarSync` 與 `actControls` 的預設值判斷不同（VERIFIED 錯誤）；`.topf`／`.rsel` 依斷點搬移節點。縮窗時內嵌面板會變成一般面板（VERIFIED，行為合理）。 |
| 7 面板狀態是否依賴 DOM 存在 | A-R7 | 面板狀態在 JS（`stack`、`GVW[].hist`、`RW`、`CW`），不依賴 DOM；例外是 `data-rep` 讀 `#pCrumb` 文字當標題；`#panel.hidden` 被當成「面板是否開著」的唯一旗標（`show()`、`markSel`、`renderDungeons` 都讀它）。 |
| 8 切樓層或分頁時哪些 DOM 被重建 | A-R8 | 見第 4 節表格（VERIFIED）。 |
| 11 拆分 src/index.html 時必須相容的識別 | A-R11 | 見下面清單。 |

**A-R11｜中｜拆分相容清單**（CODE，grep `tests/`、`tools/`、`src/index.html`）：

- **重名／遮蔽**：`function show(` 有兩個（:3612 路由、:3746 導覽 IIFE 內）；`const esc` 在導覽 IIFE（:3720）遮蔽 HTML escaper `esc`（jm 放大圖的註解 :2968 也提到同樣問題）。合併成同一個模組時會衝突。
- **宣告順序**：`COLLAB_PAUSE`、`SITE_PAUSE_MSG`、`PAUSE_MSG`（:3135）在 `setFloor`（:3596）、`feedbackHTML` 裡使用；`EDIT_MODE`（:1052）在導覽（:3752）使用；`RW`／`rwSvg`（:1636）在 `showPoints`（:1183）使用。拆檔後載入順序要保持。
- **window 介面**（tests／tools 會用）：`__detail`、`__auditIds`、`__gv`、`__updCheck`、`__effPick`、`__effIc`、`__zhText`、`__zhGap`、`__dgMode`、`__underNear`、`__centerOn`、`__jm`、`__jmFull`、`__jmPv`、`__JMP`、`saoTour`；另有頁面自己用的 `__effToggle`（已篩選列的 ⇄，:3654）、頁面讀的 `__COLLAB_PAUSE`。注意：測試設定的 `__COLLAB_OPEN`（`jm_pack_test.py`、`report_types_test.py`）在目前程式裡**已經沒有作用**（`COLLAB_PAUSE` 預設就是關），不影響結果。
- **id**：`#q`、`#panel`、`#pBody`、`#pCrumb`、`#pClose`、`#pBack`、`#gvLayer`、`#rwin`／`#rwSvg`／`#rwTitle`、`#cwin`／`#cwBody`、`#flTrig`、`#flGrid`、`#codexTabs`、`#collabBtn`、`#aboutBtn`、`#aboutMenu`、`#tourBtn`、`#legalBtn`、`#updBar`、`#floorInfo`、`#view-*`（14 個，靠字串拼接 `"view-"+v`）、`#l<X>`（清單）、`TOPF` 列的 7 個篩選 id、`#doneL li[data-rid]`。
- **屬性**：`data-go`、`data-goview`、`data-key`、`data-repgo`、`data-rid`、`data-rep`、`data-route`、`data-imap`、`data-spot`、`data-town`、`data-eqcls`、`data-imgzoom`、`data-dgmap`、`data-under`／`data-ux`／`data-uz`、`data-v`、`data-f`、`data-def`、`data-sub`、`data-cwe`、`data-cwp`、`data-t`（fbar）、`data-a`（導覽）。
- **class（被 JS 或測試當 selector）**：`.card`、`.qcard`、`.sel`、`.selm`、`.gvback`／`.gvbox`／`.gvbody`／`.gvx`、`.imgzoom`、`.vtabs`、`.topf`、`.rsel`、`.actf`、`.fbar`、`.filters`、`.fgroup`、`.chip`、`.chips`、`.note.srcn`、`.srcend`、`.srcfold`、`.view.browse`、`.results>.rhead`、`.count`。
- **body 狀態**：class `panel-open`、`panel-wide`、`panel-xwide`、`pdeep`、`cls-inline`、`cls-one`、`amenu-open`；`body[data-view]`；CSS 變數 `--head-h`、`--clsw`、`--clsl`、`--clst`。
- **localStorage**：`sao-tour-v1`、`sao-map-filter-v5`、`sao-map-base`、`sao-cl-mode`、`sao-f1-zone-pos`（`sao-f` 前綴）；`meta[name=sao-build]`（build.py 寫、`updCheck` 讀）。
- **hash 正則和 `VIEWS`**：正則多一個 `feedback`（沒有容器），`VIEWS` 和正則要同步維護。
- **DOM 節點上的 JS 屬性**：`g.__home`（`placeTopFilters`）、`el.__dragged`（彈出視窗拖曳）。

---


### 2.3 分工 B 風險表


| ID | 嚴重 | 檔案行號 | 問題 | 實際影響 | 建議修法 | 要改程式 | 證據 |
|---|---|---|---|---|---|---|---|
| B-R1 | 高 | src/index.html:1009、1074-1075、1742、2093-2096、2296-2302；data.js:121；data23.js:13、16；1668-1674 | 五個分頁的卡片和面板連結大量使用**流水號**：怪物 `m<i>`、遊戲才有的裝備 `x<N>`、官網沒有的道具 `g<N>`、NPC `n<f>_<i>`、配方 `r\|<N>`。 | 觸發條件不是「重寫資料」而是例行工作：ITEMS 補一個 `fr` → x 移位；某個官網道具得到 `gen` → g 移位；`build_npcs.py` 重產 → n 移位；**Apps Script 自動收錄一則配方回報 → r 移位**（不經開發者 commit，測試用複本看不到）。移位後連結會**打開別的東西**，不是壞掉。`p\|g*` 在 `tests/fixed_links.json` 一條都沒有（panels.json 有 31 條）。`registry/exceptions.json`、`pins.json` 沒有用這些 id 當鍵（VERIFIED 計數 0），所以已核准的例外不會失效。 | R0.6 給這幾類永久 ID，`data-go`／`data-key`／`data-goview` 改用 ID；在那之前，fixed_links 補 `p\|g*`，並在建置檢查裡比對「流水號 → 名稱」對照，移位就報錯。 | 是 | grep 計數：fixed_links `e\|x` 53、`n\|n` 96、`r\|` 363、`m\|m` 67、`m\|f[23]m` 115、`p\|g` 0 |
| B-R2 | 中 | src/index.html:1701、1703-1704 | `recGoBtns` 和 `recipeTable` 用 `ALLREC.findIndex(npc 和 en 相同)` 找配方序號，**沒有比樓層**；`recRow` 產生的列沒有 `.i`，所以 NPC 面板一定走 findIndex。 | **已確認錯連**：第 3 層煉金術士（`n\|n3_0`）面板的品質魔力／耐力藥水 II、III 四列連到 `r\|4`、`r\|5`、`r\|7`、`r\|8`，打開是「F1・起始之鎮煉金術士」的配方。品質生命藥水 II／III 和同名道具面板的「查看配方」按鈕也有同樣風險（6 筆同名同 NPC 跨樓層）。 | findIndex 加 `y.f===x.f`，或 recRow 時帶入 ALLREC 的序號。 | 是 | VERIFIED（埠 8772，`c5.py`）：r\|4/5/7/8 標題列都是「F1 配方・藥水」、地點「起始之鎮」 |
| B-R3 | 中 | src/index.html:1681、1554、1715、1667、2094、2112、2397、1513-1515 | 用名稱當鍵的查找在名稱重複時取第一個或最後一個，沒有警告。 | 已發生：`Occult Amulet (2)`（x49）因為 `gen` 去掉「(N)」，借到第 1 層紅色神祕護身符的圖示（VERIFIED）；`enGo("Occult Amulet")`、`GI_EN`、`SET_BY` 也會落到同一件。潛在：重名 NPC（第 1 層 Traveling Merchant ×8 等）共用 `BB.items`／`NPC_NOTE`／`RCP`；EQ 法文名重複 4 組讓 `offOf` 取最後一件。怪物頭像只用目前名稱查，回報改名後會對不到。 | 遷移時這些表改用 ID；過渡期在建置檢查裡列出重名（E2 類）。 | 是（遷移時） | VERIFIED `check3.py`／`check4.py` 輸出 |
| B-R4 | 中 | src/index.html:713-717、3639-3641 | `syncVTabs` 用 innerHTML 把 `#codexTabs a` 整段複製到 5 個分頁的 `.vtabs`，連同 `<span id="nMon">` 等 5 個 id。 | 每個數量 id 在頁面上 **6 份**；`$("nMon")` 只更新第一份（手機的 `#codexTabs`），桌面看到的是複本，只在 renderCurrent 時重新複製。BRIEF 的自動掃描只看靜態 id，沒抓到。測試或之後的程式用 id 定位會拿到隱藏的那一份。 | 複製時刪掉內層 id（或改成 class），桌面直接讀 class。 | 是 | VERIFIED：1280／390 兩種寬度 `dupIds` nMon、nEquip、nProp、nItem、nNpc 各 6 |
| B-R5 | 中 | src/index.html:1242-1265、1291-1306、2263-2276、2405-2416、1980-1992 | 面板的區塊（掉落物、取得方式、用途、可以拿去製作、製作方式、回收物品…）只有 `h3.sec` 的文字，沒有任何識別屬性；同一面板裡相同的 `data-go` 也會重複。 | 測試或遷移工具要定位「某一區塊的某個連結」只能靠顯示文字或順序。重複連結的面板：怪物 4、裝備 1、道具 13、素材 13、NPC 1（VERIFIED）。 | 每個區塊加 `data-sec="<代碼>"`；重複的列另加區分屬性（例如 GAME_DROPS 的 `dup`）。 | 是 | VERIFIED `check2.py`（全部面板跑過，`secs` 統計） |
| B-R6 | 低 | src/index.html:1420、3644-3665、2173-2184、1519、2322、2320 | 動態按鈕的定位方式：①已篩選列 `.af[data-i]`、`.afm[data-p]` 只有序號；②效果清單的清除鈕和選項共用 `data-eff`（清除是空字串）；③素材分類、道具分類和細分的 `data-v` 是中文顯示名；④`chipsInto` 寫 `data-v` 沒有 esc。 | 序號隨條件變；中文名改字就換值。目前沒有值含引號，沒有實際錯誤。 | 已篩選列加 `data-ctl`；清除鈕改專屬屬性；分類值改代碼；`data-v` 加 esc。 | 是（小） | CODE；VERIFIED 每個 `.chips` 內 `data-v` 唯一 |
| B-R7 | 低 | src/index.html:3566、3638、1479、1702、1971、1545、1578、1258、1299、1529、2031、2084 | 名稱不一致但功能相同（或同名不同功能）：`CODEX` 和 `CODEX_V` 是同一份清單；`#codexTabs` 和 `.vtabs` 兩套導覽；`data-goview` 第一段沒人讀、`goView` 是死碼（它的重設會點 `data-v="all"`，會把取得樓層從預設「這一層＋還不知道」改成「全部樓層」）；`.npcgh` 同時是 NPC 區域標題（h3）和素材的怪物分組標題（div）；「相關任務」「用途」列的是任務、連結是 `t\|城鎮`；`#fItemAll` 勾了反而只看這一層；view `items` 顯示「素材」；催化器連結用 `e\|oid`、zhnames 鍵用 `p\|oid`、`prById` 沒有它；zhnames 的 `g\|<英文名>` 和道具 oid `g<N>` 同字首不同意思；`data-v` 同時是導覽目標和膠囊值。 | 目前功能正常；改寫或遷移時容易改錯其中一份，或把 `g\|` 和 `g<N>` 混淆。 | 合併 CODEX 常數；刪 goView 或改正重設；任務列連到任務；`.npcgh` 拆兩個 class；記錄 `e\|`／`p\|` 催化器規則。 | 是（小） | CODE；goView 在 index.html 只有定義（1479），tests/ grep 無結果 |
| B-R8 | 低 | src/index.html:2254、2334、1543 | 裝備、道具只畫前 240 件，素材前 600 件；其餘不在 DOM。 | 用 `data-key` 定位卡片要先篩選；`markSel` 標不到；`goView` 的找卡片退路也找不到。 | 不改畫面；測試和工具先篩選再找，或用 `window.__detail`。 | 否 | VERIFIED 裝備、道具各 240 張；tests/smoke.py:146 |
| B-R9 | 低 | src/index.html:1498、2251、2332-2333、1535 | 「名稱」排序用內部名稱（怪物英文、裝備／道具法文、素材英文 key），畫面標題是中文。 | 排序看起來亂。是功能問題，不影響識別。 | 交使用者決定要不要依顯示名排序。 | 視決定 | CODE |

**風險 3、4 在這五個分頁的結論**：風險 3（名稱不一致但功能相同）見 B-R7；風險 4（動態按鈕能不能唯一定位）：卡片可以用「清單容器 id＋`data-key`」唯一定位（VERIFIED，5 個清單都沒有重複）；膠囊可以用「容器 id＋`data-v`」唯一定位；面板裡的連結和區塊**不能**唯一定位（B-R5）；已篩選列只能用序號（B-R6）；數量 id 不唯一（B-R4）。

---


### 2.4 分工 C：風險檢查第 9 項


**前提**：網址（hash）只帶分頁（`#f{N}-<view>`，src/index.html:3612 的正則），**沒有任何資料項目可以用網址直接打開**。所以下面這些 id 只在同一次瀏覽、執行時重新計算，玩家不會拿到過期的網址。真正會「固定」這些 id 的地方是：`tests/fixed_links.json`（每條的 `expect` 是起點打開的面板開頭文字，`baseline_compare.js` 比對不同就報 E5）、`tests/baseline/panels.json`（以 `type|id` 當 key），以及將來 R0.6 要建的 registry。

| ID 格式 | 產生位置 | 身份來源 | 資料順序變動時會不會指到別的東西 | 會觸發變動的常見操作 | fixed_links.json 裡的數量 | baseline panels.json 裡的數量 | 風險 |
|---|---|---|---|---|---|---|---|
| `r\|<N>`（配方） | src/index.html:1742 `ALLREC.forEach((r,i)=>r.i=i)` | `Object.entries(RECIPES)` 的 NPC 插入順序 × 每個 NPC 的 items 順序 | **會**：前面任何一位 NPC 多或少一列，後面全部位移；核准的配方回報 `Rn.items.push(row)`（1675）會插在那位 NPC 的最後，後面所有 NPC 的索引都 +1 | `build_recipes.py` 重產、`SHOTS23` 新增、Apps Script 收錄配方回報（reports.js） | entity `r\|` 69 條＋goview `recipes\|r\|N` 293 條＝**362 條** | 315 | **高** |
| `n<f>_<N>`（NPC） | src/index.html:1074 | `npcs.js` 每層陣列索引 | **會**：`build_npcs.py` 的 `DROP`／`SITE`／`CALC23`／`NEW23` 增刪，或核准的 NPC 地點回報（`SAO_NPCS` 新列），都會位移 | 重產 npcs.js、地點回報 | **95 條**（例如 `n\|n1_0`） | 192 | **高** |
| `mq<f>_<N>`（主線） | src/index.html:1590、2002 | `mainq.js` 每層陣列索引 | **會**：插入新的主線（例如 CLAUDE.md 記載的第 2 層「前往梅莉歐娜途中」空殼），後面全部位移 | 手改 mainq.js | **0 條**（沒有面板連到任務，所以 baseline 沒收錄）；smoke.py:110、123 寫死 2 條 | 147（含支線） | **高**（fixed_links 沒保護） |
| `q<N>`（第 1 層支線） | data.js:489 `.map((q,i)=>({...q,id:"q"+i}))` | data.js QUESTS 陣列索引 | **會** | 改 data.js 的支線表 | 0 條 | 含在上面的 147 | 中 |
| `f<f>q<N>`（第 2、3 層支線） | src/index.html:937（`q.id\|\|("f"+f+"q"+i)`） | data23.js quests 陣列索引（第 2 層 7 筆都沒有 id） | **會**（2026-11-19 才在陣列後面加了 2 筆；插在中間就會位移） | 改 data23.js | 0 條 | 同上 | 中 |
| `m<N>`／`f<f>m<N>`（怪物；地圖縮圖、重生點、世界王頁都用） | data.js:121、data23.js（`addNews` 接在後面） | 陣列索引 | **會**（CLAUDE.md 寫新怪物「加在 M 最後面以免動到既有 id」，表示大家已經知道是靠索引） | 改 data.js／data23.js 的 M | **180 條**；baseline_capture.js:83 寫死 `m\|m0` | 208 | 高（主要屬 A／B 分工，地圖和世界王頁也依賴） |
| `s\|<spot.id>`（地點／地下城） | data.js／data23.js 寫死的字串；回報 `rp-<回報編號>`；校正 `u<f>-<zone>` | 字串 | **不會**（順序無關）；但第 3 層 id 像是工具從英文名截短產生的（`f3entrancetothel`、`f3dungeonthemyst`），重跑產生工具時可能改變 | 重新產生 data23.js 第 3 層區塊 | 45 條 | 76 | 低（第 3 層：低～中） |
| `t\|<town.id>`（城鎮） | 資料字串（`tob`、`hanaka`…；第 2 層 `f2west` 等暫稱） | 字串 | 不會 | N/A | 8 條 | 12 | 低 |
| `d\|<event.id>`（活動地下城） | events.js 字串（`souls`） | 字串 | 不會 | N/A | 0 條 | 0（`__auditIds` 沒有 `d`） | 低（但沒有測試保護） |
| `c\|<class.id>`（職業） | classes.js 字串 | 字串 | 不會 | N/A | 0 條 | 6 | 低 |
| `data-dgmap="<dg id>"` | jmmeta.js `dg` 的 key（JourneyMap 資料夾名） | 字串 | 不會 | jm_merge 的 `DUNGEONS` 對照 | 0 | N/A | 低 |
| `#fRcNpc` option value | NPC **名稱** | 名稱 | 改名就失效（只在當次瀏覽，不存） | NPC 改名 | 0 | N/A | 低 |
| `data-under`、`.zsec[data-k]`、`.zrow[data-tp]` | 顯示文字 | 名稱／文字 | 改字就失效（C-R1、C-R4） | 改顯示名 | 0 | N/A | 低～中 |

**測試裡寫死的索引 id**（grep `tests/*.py tests/*.js` 的 `data-go`／`data-key` 字面值，不含 fixed_links.json）：
- `tests/smoke.py:110` `[data-go='q|mq1_33']`（期望標題「水晶之下」）、`tests/smoke.py:123` `[data-go='q|mq1_15']`：主線索引 id。mainq.js 第 1 層插入一段，smoke 就會失敗。這是主線 id 唯一的保護，而且只有 2 條。
- `tests/baseline_capture.js:83` `.card[data-key="m|m0"]`：用第 1 隻怪物的卡片當探測起點，data.js M 第 0 列換掉時 baseline 工具本身會受影響。
- 其他字面值是穩定字串：`c|guerrier`、`c|archer`（smoke.py:311、319）、`d|souls`（198）、`s|xal`（202）、`s|geldorakd`（jm_pack_test.py:470）、`p|2165`（290）、`i|Sylvan Bow`（410）、`e|1760`（baseline_capture.js:120）。
- 根目錄資料檔（changelog.js、reports.js、jmmeta.js）裡沒有找到 `r|數字`、`n數字_數字`、`mq數字_數字`、`m|m數字` 這類字面值（grep 0 筆）。

**名稱當身份的查找（非 id，但同樣會在改名時靜默失效）**：
- `BOSS_SPAWNS` 依怪物名稱（1057）。
- 配方的 `npcByName(r.f,r.npc)`（1681），以及 `RQTY`／`RMISS` 的 key（NPC 名＋英文物品名）。
- `recGoBtns` 用 npc＋en 找配方索引（1701）。
- `EQX_BY[r.en]`。
- 地下城寶箱 `sp.dg.loot` 的物品名和怪物名（1357–1360）。
- `dgKeys` 用 note 裡的法文鑰匙名和 150 格距離（1329）。
- 樓層首領用名稱前綴（2434，C-R14）。
- 任務回報用標題或 NPC 名稱（979–981）。
- 職業技能回報用職業名稱（1795）。

**結論**：
- **C-R9（高）**：`r|N`、`n<f>_N`、`mq<f>_N`、`q<N>`／`f<f>q<N>`、`m<N>` 都是陣列索引。
  - 會怎樣：資料順序一變，同一個 id 就打開別的東西。
  - 現在的保護：`baseline_compare.js` 的 E5 會發現 r／n／m 的位移，因為 fixed_links 裡有 362＋95＋180 條。專案目前的做法是新資料一律加在陣列最後面（CLAUDE.md：「放在最後，配方 id 不變」「加在 M 最後面以免動到既有 id」），這樣不會位移；但**插在中間的新增，或某位已有的 NPC 多一列配方**（`ALLREC` 是依 NPC 分組攤平的，例如核准一則已有 NPC 的配方回報），後面全部的索引都會位移，大量固定連結會一起報 E5。
  - 保護不足的部分：主線、支線任務 id 在 fixed_links 裡是 0 條；只有 smoke.py 寫死的 `q|mq1_33`、`q|mq1_15` 兩條，支線完全沒有。
  - 建議（v2）：`r`、`n` 等流水號身份列入「R0.6 影響與待決事項」，處理順序由 R0.6 決定，UI-INV 不主張調整 R0.6 的順序；任務 id 先在 fixed_links 加幾條代表性連結（例如 `q|mq1_20`、`q|mq1_32`、`q|q0`、`q|f2q0`），或在 check_refs 加「主線／支線順序沒變」的檢查。
  - 是否需要改程式：R0.6（資料 ID）；測試清單可以先補。
  - 證據：data.js:121、489；src/index.html:937、1074、1590、1742、2002；fixed_links 統計（`('goview','recipes'):293`、`('entity','r'):69`、`('entity','n'):95`、`('entity','m'):180`，沒有 `q`、`c`、`d`）。

---


### 2.5 分工 D 風險表（一般）


| ID | 嚴重程度 | 檔案行號 | 問題 | 實際影響 | 建議修法 | 需要程式修改 | 證據 |
|---|---|---|---|---|---|---|---|
| D-R1 | 低 | src/index.html:2585、3195、2601 | auto_checks 說 `#doneL`／`#doneC` 出現兩次：一次在舊版 `buildReport`（GitHub issue 流程，L2585），一次在 `buildFormReport`（L3195）。兩者都寫進 `#rWrap.innerHTML`，**互斥，不會同時存在**；而且 `FORM_PREFILL` 有字面值備援（L2601），`buildReport` 實際上永遠不會執行 | 現在沒有錯；只有在有人把 FORM_PREFILL 清空時才走舊流程。舊流程 `rBuilt` 共用，兩套不會混建 | 之後清理時可刪掉 `buildReport`、`loadPending` 與 `#rf_*` 整段（約 L2505–2597），或保留並註明是備援 | 否（現況）；清理是選擇 | VERIFIED：#report 時 `#doneL` 1 個、`#pendL` 0 個；CODE L3200 |
| D-R2 | 低 | src/index.html:3684–3686 | `goRep` 用 `setInterval` 50ms×40 次找 `#doneL li.replist[data-rid]`，找不到就靜默放棄 | 已收錄清單很長或手機慢時，2 秒內沒畫好就不捲動、沒有提示 | 改成等 renderReport 完成的回呼；或至少找不到時提示 | 可選 | CODE；report_types_test.py:102–105 只測得到的情況 |
| D-R3 | 中 | src/index.html:3202–3204 | 已收錄清單的「看怪物資料／看配方／看任務」連結是在 render 時用**名稱**或**陣列索引**找：`FLOORS[f].M.find(x=>x.name===r.name\|\|aka)`、`ALLREC.findIndex(x=>x.rep===r.id)`、`MQ(f).findIndex(x=>(x.reps\|\|[]).includes(r))` 產生 `r\|<索引>`、`q\|mq<f>_<索引>` | R0.6 把怪物、配方、任務改成永久 ID 時，這段要跟著改；而且回報用名稱，資料改名就會失去連結（目前靠 aka） | 遷移時讓回報對到的資料 ID 由 R0.6 的對照表提供，這裡只讀 ID | R0.6 時要 | CODE；VERIFIED `data-go` 有 `m\|m12`、`m\|rep-R0022` |
| D-R4 | 低 | src/index.html:3133、3141 | `#fbL` 讀 GitHub API 失敗時寫「讀不到」，但沒有區分「0 則」和 API 限流（未登入每小時 60 次） | 顯示「目前沒有處理中的問題或建議」也可能是 API 回應空陣列；實測無法分辨是否真的連上 | 不處理（影響小） | 否 | VERIFIED 文字；連線狀態 UNKNOWN |
| D-R5 | 中（v2 由低提高：會把第 2、3 層的玩家切回第 1 層，並讓回報表單預填樓層變成 1） | src/index.html:1939 | 關於本站「協作區」連結寫死 `href="#report"`，不經 `hashFor`；在第 2、3 層點了會到 `#report`＝**第 1 層**的協作區（show 依 hash 設樓層） | 樓層選擇被切回第 1 層；回報表單的預填樓層也變成 1 | 改用 `hashFor("report",FL)` 產生，或 data-v 交給 go() | 是（小） | CODE（L3612–3613：`want` 沒有 f 前綴就是 1）；VERIFIED href 是 `#report` |
| D-R6 | 低 | src/index.html:1910、1959、3165、3186 | 說明文字互相矛盾或過時：`ABOUT_SRC` 寫 JourneyMap 只有「第 1 層探索地圖」、資料來源 note 寫「第 2、3 層是開放前的 wiki 資料」（CLAUDE.md：11/11 已改成新聞＋參考地圖＋JourneyMap）；回報表單說明寫「目前只合併第 1 層」，打包說明 `.jmscope` 寫第 2、3 層地面也收 | 玩家看到的範圍說法不一致 | 交給站長決定文字；不屬於 R0.6 | 否（文字） | CODE；CLAUDE.md 檔案表 data23.js 列 |
| D-R7 | 低 | src/index.html:3125 | 下載檔名固定 `探索地圖-第1層-…zip`，但更新打包可同時含第 2、3 層方格、全地圖打包也含第 2、3 層地面 | 只影響檔名，合併由內容判斷 | 檔名改成依包含的樓層 | 可選 | CODE（L2865–2866、L3011：sel 含所有樓層） |
| D-R8 | 中 | src/index.html:2688–2691；tools/jm_merge.py `DUNGEONS`；`tiles/dg/<id>/`；jmmeta.js `SAO_JM.dg` | 地下城地圖以 SPOTS 的手寫 id（xal、geldorakd、fallen、kobold）當資料夾名與 jmmeta 鍵；`dgName` 用 `FLOORS[1].spots.find(id)` | R0.6 地點改 ID 時，如果 SPOTS id 換掉，打包工具、合併工具、已存的切片資料夾、jmmeta 都對不上；check_refs.py 目前不檢查 DG_DIM（只讀 NPC_NOTE 這一張程式內表，L756–778） | 遷移時把 SPOTS 現有 id 當永久 ID 保留，或在 registry 列 DG_DIM／DUNGEONS 為依賴 | R0.6 時才需要 | CODE |

（檢查方法：讀 L2505–3214 全部協作區程式；以 Playwright 在 1280／390 寬度實測 id 數量、可見性、樓層切換時是否重建、changelog 切換是否重建、面板開啟後 hash；打包工具需真的 mp 資料夾，互動部分以 tests/jm_pack_test.py 的測試步驟為證據、未實跑。未發現 JS 例外（`errs: []`）。）


### 2.6 分工 D：風險檢查第 12 項


| ID | 嚴重程度 | 檔案行號 | 問題 | 實際影響 | 建議修法 | 需要程式修改 | 證據 |
|---|---|---|---|---|---|---|---|
| D-R12-1 | 中（遷移工作量與基準失效，不是線上故障） | src/index.html:1668–1675、1742、3204；reports.js；tests/baseline/fixtures/reports.js | 配方 id 是 `r\|<ALLREC 索引>`，而 ALLREC 是在**配方回報併入之後**才建：L1671–1675 對既有 NPC 是 `Rn.items.push(row)`（同 NPC 同名物品才原地取代），新 NPC 則在 `RECIPES` 物件尾端加鍵。所以 Apps Script 核准一筆「既有 NPC 的新配方」回報、只改 reports.js、不重新建置，就會讓 `Object.entries(RECIPES)` 中這個 NPC 之後所有配方的索引 +1 | 網站本身：每次載入重算、網址不帶 id，玩家看不到斷連結。測試基準：baseline_capture／compare 讀的是 `tests/baseline/fixtures/reports.js`（baseline_capture.js:11、35；目前和根目錄 reports.js 逐位元組相同），所以線上多一筆回報**不會**讓 baseline_compare 失敗；但下次更新 fixtures 時，69＋293 筆 `r\|` 固定連結的鍵會整批位移。R0.6：若遷移時用「當下的 ALLREC 索引」建對照表，之後任何配方回報都會讓對照表失準。現在 reports.js 沒有配方回報（23 筆：jmap 13、monster 6、item 3、place 1），尚未發生 | R0.6 給配方一個不依順序的 ID（例如 NPC 鍵＋產物 oid／英文名）；在那之前，回報新增的配方列可改成一律排到 ALLREC 最後 | R0.6 時要 | CODE：L1668–1675（全文已讀）、L1742；tests/baseline_capture.js:11、35；`cmp` 根目錄與 fixtures 的 reports.js 相同 |
| D-R12-2 | 中（遷移工作量與基準失效，不是線上故障） | data.js:121、data23.js:13、src/index.html:1074、1590、2094、2299 | 怪物 `m<i>`／`f2m<i>`、NPC `n<f>_<i>`、主線 `mq<f>_<i>`、遊戲才有的裝備 `e\|x<k>`、遊戲才有的消耗品 `p\|g<k>`（L2299）都依陣列或物件鍵順序；在資料檔中間插入一筆，後面全部位移。EQX 的 k 依 `ITEMS` 合併順序（data.js 鍵 → data23.js 鍵 → unknown，L1015–1017），在 data.js 中間加一件裝備就會推移所有 `x` 編號；**更常見的觸發是既有物品補上 `fr`（對到官網 id）**：L2093 `if(it.fr…)return` 讓它退出 EQX，後面的 `x` 編號全部往前一號 | 網站內連結當下仍正確（每次載入重算），但 fixed_links（m 180、n 95、e\|x…）、tests/baseline/panels.json、smoke.py:110／123 的 `q\|mq1_33`／`q\|mq1_15` 會失效；CLAUDE.md 也因此要求「配方 id 不變」「新增放在最後」，靠人工維持 | R0.6 給這幾類永久 ID。基準處理（v2，依 GPT 複審 M04）：階段 1.5 網站不切換，G5 維持 `IDENTICAL`；階段 2 起的預期身份遷移，依已審查的 `key_map`、舊連結對照和預期修正清單核對舊新結果，確認沒有非預期差異後才更新相關基準，不能先重產再用新版對新版 | R0.6 時要 | CODE；tests/fixed_links.json 統計；tests/baseline/operations.json:123–127 |
| D-R12-3 | 中 | src/index.html:986–1030、970–981 | 玩家回報用**名稱**對資料：怪物用 name／aka／圖鑑編號／「舊名：X」，地點用 `n`／`old`，NPC 用名稱，任務用標題／aka，掉落和材料用 `ikey` 後的 ITEMS 名稱。而且 `renameMon` 會在**執行時**依回報改怪物名稱、把舊名塞進 aka，建置時的 check_refs 看不到這一步（只在 W11 統計：resolved 3、unresolved 6，build/registry_report.md:472–474） | R0.6 若把名稱鍵改成 ID，reports.js 不會跟著改（Apps Script 寫入、CLAUDE.md 規定格式不能變）；必須保留一層「回報名稱 → ID」的過渡查找，否則已收錄的回報（怪物 6 筆、物品 3 筆、地點 1 筆）會失去對應，Albal 的圖鑑掉落取代也會失效（L1026 要求每個掉落名都在 ITEMS） | 遷移時保留名稱解析（含 aka、ITEM_OLD），只讓解析結果改成 ID；在 registry 把 reports.js 的名稱列入檢查（目前只計數） | R0.6 時要 | CODE；build/registry_report.md:472–474；reports.js 統計 |
| D-R12-4 | 中 | src/index.html:1237–1239、1422–1423、1464–1470、1480 | `data-go`、`data-key` 是兩段 `<t>\|<id>`，`data-goview` 是三段 `<view>\|<t>\|<id>`；三者的**實體身份部分**（`<t>\|<id>`）必須一致：`markSel` 用 `[data-key="${t}\|${CSS.escape(id)}"]` 標選取、`goView` 用同樣字串找卡片；`bindGo` 用 `split("\|")` 解構取前兩段／前三段（v2 依 GPT 複審 M02 改寫；完整格式見 C 命名規則 §5.1） | R0.6 的 ID 如果含 `\|`，`split` 會拆錯；只改其中一種屬性，選取標示和「查看圖鑑」找卡片會失效 | ID 字元集排除 `\|`，或改用 `indexOf` 只拆第一個；三種屬性一起改 | R0.6 時要 | CODE；smoke.py:557–562 |
| D-R12-5 | 中 | src/index.html:1019–1022、922、2688、967 | 程式內寫死的名稱表：`ITEM_OLD`、`REP_MAT`、`DG_DIM`、`NPC_ZH`（回報 NPC 類別中文→npcs.js 類別鍵）；check_refs.py 只讀 NPC_NOTE 這一張（:756–778） | R0.6 改資料鍵時這些表不會被 E1／E9 抓到，可能悄悄失效（例如 ITEM_OLD 指到不存在的新名，`ikey` 只會原樣回傳） | 1.5 S15-B1 階段把這些程式內表列進 registry 的檢查範圍，或搬成資料檔 | 是（工具） | CODE |
| D-R12-6 | 低 | src/index.html:3612、1049–1082 | 深層連結：網址只帶樓層＋分頁，不帶資料 id；localStorage 也不存資料 id | 遷移**不會**讓玩家收藏的網址或官方信件裡的連結失效（fixed_links 的 route 37 筆）；這是好消息，但也代表目前沒有「分享某一件物品」的網址 | 不處理；若之後要加 `#…/e/<id>`，請在 R0.6 ID 定案後再做 | 否 | VERIFIED：開面板後 hash 不變 |
| D-R12-7 | 低 | src/index.html:1001、1006、976 | 回報新增的怪物 `rep-<回報 id>`、地點 `rp-<回報 id>` 已經是穩定 id；回報新增的 NPC 卻是 `n<f>_<i>`（push 到尾端） | NPC 這一類尾端追加不推移既有，但 npcs.js 重產（build_npcs.py）時如果插在中間就會推移 | 與 D-R12-2 一起處理 | R0.6 時要 | CODE |

### 這一區檢查了什麼
- 用 grep 列出 src/index.html 所有 `data-*` 產生處（data-go 44 處、data-key 15 處等，auto_checks.txt 統計相同）並逐一對到所在函式（Python 腳本依行與欄位找最近的函式定義）。
- 讀了每種 id 的產生程式（data.js:121、data23.js:13、L935、L1074、L1590、L1742、L2093、L1006、L976）。
- 統計 tests/fixed_links.json 每種前綴的數量，grep tests/*.py、*.js、tests/baseline/ 裡寫死的流水號。
- 讀 tools/check_refs.py 的檔頭、MAPS／TUPLES、NPC_NOTE 讀取、W11，確認它檢查資料檔、不檢查 index.html 其他程式內表。

