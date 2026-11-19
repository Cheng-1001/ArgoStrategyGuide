# UI-INV R0.1｜A. 全站 UI 元件清冊

- 基準：`Cheng-1001/ArgoStrategyGuide` main `14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d`（2026-11-19 重新 fetch 確認 origin/main 仍是此 SHA）
- 版本：**v2**（2026-11-19，依 GPT 第 1 輪複審 M01～M05 修訂；v1 檔案保留不動）
- 性質：唯讀盤點＋規劃建議，**不是已核准決策**；component_key 都是提案，網站沒有實作。
- 標記：VERIFIED＝本機 Playwright 實測（1280／390 寬）；CODE＝只讀程式碼；NOT RUN＝沒有測；UNKNOWN＝不確定。行號都指 `src/index.html`，除非另外寫檔名。
- 分工來源：A＝全站外殼／路由／共用面板／測試涵蓋，B＝圖鑑五分頁，C＝地圖／任務／配方／地下城／職業／世界王，D＝協作區／關於本站／更新紀錄＋R0.6 依賴表。

## 0. 跨分工重複列的對照（同一個元素，分工各自取了不同的 key）

以下列在清冊裡保留原文，但**以「正式 key」為準**。這 15 列都是同一個實體元素，不另計入去重後元件數。（v2：v1 這裡另有 2 列「改名建議」`popup.jm-preview`／`popup.jm-zoom`，v2 已直接在清冊改成 `report.jmpack.preview`／`report.jmpack.zoom`，所以不再列在這裡；`map.legend.base-button` 也已直接改成 `map.legend.base-button@f1-2`。）

| 分工列的 key | 分工 | 種類 | 正式 key | 理由 |
|---|---|---|---|---|
| `global.codex-nav.subtabs` | B | 重複 | `global.codextabs` | 同一個 `#codexTabs`；A 管全站導航 |
| `global.codex-nav.vtabs` | B | 重複 | `global.codextabs.vtabs` | 同一組 `.filters>.vtabs` |
| `global.codex-nav.count` | B | 重複 | `global.codextabs.count` | 同一組 `#nMon` 等（A 標 P1、B 標 P2，以 P1 計） |
| `global.browse.fbar` | B | 重複 | `global.list.fbar` | 同一個 `.fbar` |
| `global.browse.topf` | B | 重複 | `global.list.topf` | 同一個 `.topf` |
| `global.browse.rsel` | B | 重複 | `global.list.rsel` | 同一個 `.rsel` |
| `global.browse.active-filters` | B | 重複 | `global.list.actf` | 同一個 `.actf` |
| `global.chips.factory` | B | 重複 | `global.list.filters.chips` | 同一組 `.chip[data-v]`（`chipsInto`） |
| `global.search.codex-behavior` | B | 重複 | `global.search` | 同一個 `#q`；B 的五列 `<view>.search` 是各分頁的比對規則（行為），元素仍是 `#q`，保留為子項 |
| `global.list.bindgo` | B | 重複 | `global.link.data-go`、`global.link.data-goview` | 同一組委派 |
| `floatmap.route-window` | C | 重複 | `floatmap.window` | 同一個 `#rwin`（物品取得地點、任務路線、座標都共用） |
| `cwin.class-equipment.window` | C | 重複 | `cwin.window` | 同一個 `#cwin` |
| `report.head.collab-btn` | D | 重複 | `global.collab-btn` | 同一個 `#collabBtn`，在頁首 |
| `about.menu` | D | 重複 | `global.about.button`、`global.about.menu` | 同一組 `#aboutBtn`／`#aboutMenu`，在頁首 |
| `global.report-ref.link` | D | 重複 | `global.link.data-repgo` | 同一個 `data-repgo` 連結種類 |

---

## 第 1 部分（分工 A）：頁首、路由、共用面板、列表共用機制

## 1. 頁首和全站導航

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global.header | 全樓層 | 全站 | `.app` | header | `header#top.top` | :684 | 靜態 | 共用；高度由 ResizeObserver 寫進 `--head-h` | 無 | CSS 變數 `--head-h` | N/A | N/A | N/A | N/A | 低 | P0 | 保留：`#top` 被 `setHead` 量高度（:3679–3680） | :684、:3679 |
| global.header.brand | 全樓層 | 全站 | `#top` | div | `#top .brand` | :685 | 靜態 | ≤820px `display:none`（:661；VERIFIED 390px 是 none） | 無 | 無 | N/A | N/A | N/A | N/A | 低 | P2 | 不處理：純展示 | check3 `disp390` |
| global.floor.trigger | 全樓層 | 全站 | `#floorPick` | button | `#flTrig`（文字 `#flNo`、`#flNm`） | :687、:3584–3585、:3593–3594 | 靜態；文字由 `setFloor` 改 | 共用 | click → `openPick(切換)` | `aria-expanded`、`data-ready`（`setFloor` 用來判斷第一次） | 樓層 | `FLOORS[f]` | N/A | N/A | 中：`data-ready` 被拿來當「已初始化」旗標（A-R11） | P0 | 保留：導覽 `saoTour` 第 2 步用 `#flTrig` 當 selector（:3727） | :3585、:3593；smoke 沒有點過（見第 7 節） |
| global.floor.popup | 全樓層 | 全站 | `#floorPick` | div[role=dialog] | `#flPop` | :688–693、:3584 | 靜態 | 共用（≤820px 位置不同，:387） | Esc、點外面關（:3586–3587） | `hidden` | N/A | N/A | N/A | N/A | 低 | P1 | 保留 | :3586–3587 |
| global.floor.jump-form | 全樓層 | 全站 | `#flPop` | form＋input[number] | `#flForm`、`#flJump`、`#flMsg` | :689–690、:3588–3592 | 靜態 | 共用 | submit → `pickFloor(parseInt)` → `go(view,f)` | `#flMsg` 錯誤訊息 | 樓層 | `flState(f)`（:3580） | N/A | N/A | 低 | P1 | 保留 | :3588–3592 |
| global.floor.cell | 全樓層 | 全站 | `#flGrid` | button | `#flGrid .flcell[data-f="<N>"]`（class `open/soon/lock/cur`） | :3581–3583 | 動態（載入時產生一次，之後只改 class `cur`，VERIFIED 換樓層後同一個節點） | 共用 | click → `pickFloor(+data-f)` → `go(view,f)`：**保留目前分頁，只換樓層** | `cur`、`aria-disabled`（lock） | 樓層 | `data-f`＝樓層數字 | N/A | N/A | 低 | P1 | 保留：`data-f` 已是穩定識別 | :3591；check3 `.flcell kept` |
| global.floor.legend | 全樓層 | 全站 | `#flPop` | div | `.fllegend` | :692 | 靜態 | 共用 | 無 | 無 | N/A | N/A | N/A | N/A | 低 | P2 | 不處理 | :692 |
| global.nav.tabs | 全樓層 | 全站 | `#top` | nav＞a | `nav.tabs a[data-v]`（`data-v` 值：map、codex、quests、recipes、dungeons、classes、bosses） | :695–703、:3569、:3616–3618 | 靜態；`href` 和 `aria-current` 每次 `show()` 重寫 | 共用；≤1600px 職業用短標籤 `.ts`（:79–81） | click → `preventDefault` → `go(data-v==="codex"?lastCodex:data-v)` | `aria-current="page"` | N/A | `data-v`＝view 名；**`codex` 是虛擬值**，實際去 `lastCodex` | N/A | N/A | 中：`data-v` 也是篩選膠囊 `.chip[data-v]` 的值屬性（A-R2） | P0 | 保留；記錄 `codex` 別名 | :3569、:3617 |
| global.nav.count | 全樓層 | 全站 | `nav.tabs` | span | `#nQuest`、`#nRec` | :698–699、:3597 | 動態（`setFloor` 填數字） | 共用 | 無 | 無 | 任務、配方 | `Fx.quests`、`MQ(f)`、`RCV` | N/A | N/A | 低 | P2 | 不處理 | :3597 |
| global.codextabs | 全樓層 | 圖鑑 5 個分頁 | `.app` | nav＞a | `#codexTabs a[data-v]`（monsters、equip、props、items、npcs） | :712–718、:3616 | 靜態；`hidden` 由 `show()` 依 `CODEX` 設定 | **手機顯示、桌面 `display:none`**（:42；VERIFIED 1280 none、390 flex） | click → `go(data-v)` | `hidden`、`aria-current` | N/A | `data-v` | N/A | N/A | 中：是 `.vtabs` 的複製來源（A-R1） | P0 | 保留 | :3569、:3616；check3 |
| global.codextabs.count | 全樓層 | 圖鑑 | `#codexTabs a` | span | `#nMon`、`#nEquip`、`#nProp`、`#nItem`、`#nNpc` | :713–717、:3597–3598 | 動態（`setFloor` 用 `$()` 寫第一個） | 共用 | 無 | 無 | 怪物、裝備、道具、素材、NPC | `F().M`、`EQ`、`PRV()`、`matPool`、`NPCS(f)` | N/A | N/A | **中：被 `.vtabs` 連 id 一起複製，頁面上同一個 id 有 6 個**（A-R1，VERIFIED） | P1 | 補識別：改用 class 或 `data-count="mon"`，`.vtabs` 複製時不帶 id | check2 `dups`：nMon/nEquip/nProp/nItem/nNpc 各 6 |
| global.codextabs.vtabs | 全樓層 | 圖鑑 5 個分頁 | `#view-<codex>>.filters` 最前面 | nav＞a | `.filters>.vtabs a[data-v]` | :3639–3642 | **重建**：每次 `renderCurrent`（含每打一個字的搜尋）經 rAF 整個 innerHTML 重寫（VERIFIED） | 桌面專用（≤820px `display:none`，:43–44；VERIFIED） | document click 委派 `.vtabs a` → `go(data-v)`（:3642） | `aria-current` | N/A | `data-v` | N/A | N/A | 中：靠複製 `#codexTabs` 的 innerHTML（A-R1、A-R8） | P1 | 改名／補識別：改成從資料產生，不複製 DOM | check3 `afterKey .vtabs a NEW` |
| global.search | 全樓層 | 全站（各分頁各自解讀） | `#top label.gsearch` | input[type=search] | `#q` | :706–709、:1166–1167、:3672 | 靜態 | 共用 | input → `renderCurrent()`（重畫目前分頁） | 值；**切分頁不會清空**（各分頁共用同一個搜尋字） | 怪物、物品、裝備、道具、NPC、地點、城鎮、任務、配方 | `norm()` 後比對名稱、中文名、法文名、`aka`、`ITEM_OLD`（`itemHit`／`monHit`／`questHit`／`eqHit`／`prHit`／`npcHit`…） | 名稱比對要改成「ID → 所有名稱（含舊名）」的索引；搜尋結果仍輸出 `data-key` | 2 物品引用遷移；後續：NPC／地點／怪物／任務遷移；過渡查找清理（舊名 aka） | 中：舊名只能靠搜尋找到（fixed_links 有 13 筆 search） | P0 | 保留 `#q`；比對來源改由 registry 提供 | :1166–1170；fixed_links search 13 筆；baseline_capture.js:23–26 |
| global.collab-btn | 全樓層 | 全站 | `#top .hbtns` | a | `#collabBtn[data-v="report"]` | :704、:3569 | 靜態 | 共用（手機縮小，:82、:98） | click → `go("report")` | `aria-current` | N/A | `data-v` | N/A | N/A | 低 | P0 | 保留：導覽第 7 步 selector | :3569、:3617；smoke 有測 |
| global.about.button | 全樓層 | 全站 | `#top .amenu-w` | button | `#aboutBtn` | :704、:3571–3573 | 靜態 | 共用（手機 86px，:102） | click → 開關 `#aboutMenu`；開啟時量每項寬度決定跑馬燈 | `aria-expanded`；about／changelog 頁時 `aria-current`（:3619）；`body.amenu-open` | N/A | N/A | N/A | N/A | 低 | P0 | 保留：導覽第 8 步 selector | :3571–3577、:3619；smoke 有測 |
| global.about.menu | 全樓層 | 全站 | `.amenu-w` | div[role=menu] | `#aboutMenu`（項目 `#aboutInfo`、`#logBtn`、`#tourBtn`，文字包 `.amq`） | :705、:3574–3577 | 靜態 | 共用；手機選單同寬、放不下時 `.marq` 跑馬燈 | `#aboutInfo` → `go("about")`、`#logBtn` → `go("changelog")`（已在那頁時捲到頂）、`#tourBtn` → `saoTour.start()`；點外面／Esc 關閉 | `hidden`、`aria-current`（項目） | N/A | N/A | N/A | N/A | 低 | P1 | 保留。註：auto_checks 把 `aboutInfo`、`logBtn` 列為「沒有被引用」是誤判，它們在 `[["aboutInfo","about"],["logBtn","changelog"]]` 字串陣列裡被 `$()` 用（:3574、:3618） | :3574、:3618 |
| global.theme | 全樓層 | 全站 | `:root` | N/A（沒有 UI） | `:root[data-theme]`（只有 CSS） | :20–24、:394 | N/A | 共用 | **沒有主題切換按鈕**；只跟隨系統 `prefers-color-scheme` | 無 | N/A | N/A | N/A | N/A | 低 | P2 | 不處理：程式和 build.py 都沒有設定 `data-theme`（grep `dataset.theme`、`setAttribute("data-theme"` 都是 0 筆），CSS 留著 `data-theme="light/dark"` 的掛鉤 | CODE grep |
| global.update-bar | 全樓層 | 全站 | `body`（動態 append） | div[role=status] | `#updBar`（`.ub-go`、`.ub-x`） | :3689–3702 | 動態（`updCheck` 發現線上 `sao-build` 不同時才建立） | 共用 | `.ub-go` → `location.replace(?u=新版號)`；`.ub-x` 移除 | 無（`shown` 變數記已提示的版號） | N/A | `meta[name=sao-build]` | N/A | N/A | 低 | P1 | 保留：smoke 用 `__updCheck` 和 `#updBar .ub-go` 測 | smoke.py:58–73 |
| global.pause-bar | 全樓層 | 全站 | `#floorInfo` | div[role=status] | `#floorInfo .pausebar#pauseBar` | :3596、:3135 | 重建（`setFloor` 每次換樓層重寫 `#floorInfo`；只在 `COLLAB_PAUSE` 為真時出現） | 共用；手機收成兩行，inline `onclick` 切換 `.open` | 點一下展開 | `.open`；目前預設不出現（`!!window.__COLLAB_PAUSE`） | N/A | `SITE_PAUSE_MSG` | N/A | N/A | 低 | P2 | 保留；拆分時注意 `COLLAB_PAUSE` 宣告在 :3135、使用在 :3596（A-R11） | :3135、:3596 |
| global.floorinfo | 全樓層（內容依目前樓層） | 全站 | `.app` | div | `#floorInfo`（`span`、`.soon`、`#legalBtn`） | :711、:3596 | **重建**（每次換樓層 innerHTML，VERIFIED） | ≤820px 整列 `display:none`（VERIFIED），即將開放提示例外（:393） | `#legalBtn` → `aboutJump="legal"` → `go("about")` 或直接 `renderAbout()` | 無 | 樓層（建議等級、首領、status） | `F()`＝`FLOORS[FL]` | N/A | N/A | 低 | P1 | 保留 | :3596；check3 `afterFloor #floorInfo>* NEW` |
| global.floorinfo.legal | 全樓層 | 全站 | `#floorInfo` | button | `#legalBtn` | :3596 | 重建；`onclick` 每次重設 | ≤820px 跟著整列隱藏 | 跳到說明頁 `#legal` | `aboutJump`（:1915） | N/A | N/A | N/A | N/A | 低 | P1 | 保留：smoke 有用 `legalBtn` | smoke.py（legalBtn 1 次） |
| global.tour | 全樓層 | 全站（自動只在地圖首頁） | `body`（動態 `#tour`） | div＋卡片 | `#tour .tour-hole`、`#tour .tour-card button[data-a]`（n／p／x）；另插 `style#tourCss` | :3705–3752 | 動態（`saoTour.start` 建立，`end` 移除） | 共用；手機卡片固定在下方 | 下一步／上一步／略過；步驟 `go(s.go)` 會切到地圖 | `localStorage sao-tour-v1` | N/A | 寫死的 selector：`#flTrig`、`nav.tabs`、`.gsearch`、`#filterBtn`、`#fpanel`、`#stage`、`#stage img.map`、`#collabBtn`、`#aboutBtn` | N/A | N/A | 中：拆檔或改 id 時這 9 個 selector 一斷，導覽就框錯位置（不會報錯）（A-R11） | P1 | 保留：列入拆分相容清單；`window.saoTour` 是對外介面 | :3721–3729；smoke「tour does not start」「略過」 |

### 這一區的風險

- **A-R1｜中｜:3639–3641、:713–717｜重複 HTML ID（執行時）**：`syncVTabs` 把 `#codexTabs a` 的 innerHTML 原樣複製到 5 個圖鑑分頁的 `.vtabs`，裡面的 `<span id="nMon">` 等 5 個 id 一起被複製，所以頁面上 `nMon`、`nEquip`、`nProp`、`nItem`、`nNpc` 各有 6 個（VERIFIED：report、feedback、classes 頁都量到 6）。**實際影響**：`$("nMon")` 只拿到 DOM 順序第一個（`#codexTabs` 裡的那個，因為它在各分頁之前），數字靠下一次 `syncVTabs` 再複製才會同步；Playwright 嚴格模式用 `#nMon` 會因為多個元素而失敗；螢幕閱讀器、`aria` 參照會混淆。**建議**：`.vtabs` 從 `CODEX` 陣列產生，不複製 innerHTML；或複製後移除 id。**需要程式修改**：是。**證據**：check2 `dups`；auto_checks 只看原始碼字面，抓不到這種執行時重複。
- **A-R1b｜低｜:2585、:3195｜`doneC`／`doneL` 靜態重複**：auto_checks 找到兩處字面定義。:2585 在 `buildReport()`（舊的 GitHub issue 回報表單），:3195 在 `buildFormReport()`；`renderReport`（:3200–3201）依 `FORM_PREFILL` 二選一，而且 `rBuilt` 只建一次，兩者都寫 `#rWrap.innerHTML`（互相取代）。`FORM_PREFILL` 有寫死的備用網址（:2601），永遠是真值，所以 `buildReport` 在目前程式裡**不會執行**（死碼）。**實際影響**：沒有（VERIFIED：#report、#feedback 都只有 1 個 `#doneC`／`#doneL`）。**建議**：拆分時刪掉 `buildReport` 或抽成同一個共用片段。**需要程式修改**：否（現況正確），整理時可順手處理。
- **A-R2a｜低｜:695–703、:1420｜`data-v` 兩種意義**：上方選單、`#codexTabs`、`.vtabs` 的 `data-v` 是 view 名，篩選膠囊 `.chip[data-v]`（`chipsInto`）是篩選值（例如 `all`、`here`）。目前每個 selector 都有範圍（`nav.tabs a`、`.vtabs a`、`.chip[data-v=...]`），沒有誤抓。**建議**：拆分時保留範圍，新程式不要寫裸的 `[data-v]`。**需要程式修改**：否。
- **A-R11a｜中｜:3721–3729｜導覽依賴 9 個 selector**：見上表。改 id 不會報錯，只會框錯或不框。**建議**：拆分後加一個測試逐步檢查 `target(s)` 都找得到元素。**需要程式修改**：否（測試補強）。
- 檢查過、沒有問題：主題切換（不存在，已寫明）；`#updBar`（只建立一次，`shown` 防重複）；樓層格子（只產生一次，VERIFIED 換樓層沒有重建）。

---

## 2. 路由

### 2.1 view 名 → 容器 → 畫面函式

| view（hash 用的名字） | 實際容器 | 畫面函式（`renderCurrent` :3670） | 清單容器 | 說明 |
|---|---|---|---|---|
| map | `#view-map` | `filterMap`（:3533；`renderMap` :3388 由 `setFloor` 呼叫） | `#zlist`（右側清單）、`#world` 標記 | 預設 view；hash 不合法時也回到這裡 |
| monsters | `#view-monsters` | `renderMon` :1496 | `#lMon` | CODEX |
| items（素材） | `#view-items` | `renderItems` :1528 | `#lItem` | CODEX；顯示名「素材」但 view 名是 items |
| npcs | `#view-npcs` | `renderNpcs` :1571 | `#lNpc` | CODEX |
| props（道具） | `#view-props` | `renderProps` :2327 | `#lPr` | CODEX |
| equip | `#view-equip` | `renderEquip` :2245 | `#lEq` | CODEX |
| recipes | `#view-recipes` | `renderRecipes` :1784 | `#lRc` | |
| dungeons | `#view-dungeons` | `renderDungeons` :1802 | `#lDg` | 桌面內嵌面板（INL） |
| quests | `#view-quests` | `renderQuests` :2015（`renderCurrent` 的最後 else） | `#lQ` | |
| classes | `#view-classes` | `renderClasses` :1833 | `#lCls` | 桌面內嵌面板（INL） |
| bosses | `#view-bosses` | `renderBosses` :2430 | `#bWrap` | 切進來會關面板 |
| report | `#view-report` | `renderReport` :3199 | `#rWrap`（`#doneL`、`#rData`、`#rFeedW`） | `rSub="data"` |
| feedback | **沒有 `#view-feedback`**：`show()` 把它改成 view `report`＋`rSub="feedback"`（:3613） | `renderReport`→`showCollab` | `#rFeedW` | 只在 hash 正則裡，不在 `VIEWS` |
| about | `#view-about` | `renderAbout` :1933 | `#aWrap` | |
| changelog | `#view-changelog` | `renderChangelog` :1928 | `#clWrap` | |

### 2.2 元件表

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global.route.hash | 全樓層 | 全站 | `window` | location.hash | `#f{樓層}-{view}`；第 1 層正規形式**沒有前綴**（`#equip`），`#f1-equip` 也接受 | :3567（`hashFor`）、:3612–3613（正則）、:3671（hashchange） | N/A | 共用 | `hashchange` → `show()` | 全域 `view`、`FL` | 樓層 | 正則 `^(?:f(\d{1,3})-)?(map\|…\|dungeons)$` | N/A：網址不含資料 id，不受 registry 影響 | N/A | 中：不存在的樓層（例如 `#f9-equip`）顯示第 1 層、**網址不改寫**（VERIFIED）；不認得的 hash（`#bogus`）回到地圖、網址也不改（VERIFIED）（A-R12） | P0 | 保留格式（fixed_links 有 37 筆 route，官方信件引用 `#f1-recipes`、`#f1-equip`） | check4 `f9`、`bogus`；fixed_links route 37 筆 |
| global.route.views | 全樓層 | 全站 | `.app` | section | `section.view#view-<view>`（14 個） | :721–877；`VIEWS` :3565；切換 :3614 | 靜態；`hidden` 由 `show()` 設定 | 共用；`body[data-view]` 給 CSS 用（:3614） | 只有目前 view 不 hidden | `body.dataset.view` | 見 2.1 | `VIEWS` 陣列 | N/A | N/A | 中：`feedback` 在正則有、`VIEWS` 沒有、也沒有容器（A-R12） | P0 | 保留 id：baseline 用 `[id^="view-"]` 判斷顯示哪一頁 | baseline_capture.js:135；auto_checks 把 `view-equip` 等列為「沒有被引用」是誤判：它們用 `$("view-"+v)` 字串拼接 |
| global.route.show | 全樓層 | 全站 | N/A | 函式 | `show()` | :3612–3621 | N/A | 共用但分支不同：手機切分頁關面板（`matchMedia(max-width:820px)`），桌面只在 INL 時用 `innerWidth>820` 判斷 | 解析 hash → `setFloor` → 切 view → 關閉／保留面板、彈出視窗、路線視窗、裝備視窗 → 更新選單 `href`／`aria-current` → `renderCurrent()` → 執行 `viewPending`／`pending` | `view`、`lastCodex`、`rSub`、`pending`、`viewPending` | 全部 | N/A | N/A | N/A | 中：同一個函式名 `show` 在導覽 IIFE 裡還有一個（:3746）（A-R11） | P0 | 保留；拆分時改名其一 | :3612、:3746 |
| global.route.go | 全樓層 | 全站 | N/A | 函式 | `go(v,f)` | :3568 | N/A | 共用 | 只改 `location.hash`（不直接畫面） | N/A | N/A | N/A | N/A | N/A | 低 | P0 | 保留：所有選單、樓層、跳轉都走它 | :3568 |
| global.route.goview | 全樓層 | 全站 | N/A | 函式（死碼） | `goView(v,t,i)` | :1479–1487 | N/A | 共用 | 切分頁後 `openP`、捲到卡片、必要時清搜尋和篩選 | `viewPending` | 物品、裝備、道具 | `redirI`／`redirP`／`MATG` | 若恢復使用：卡片定位 `[data-key="t\|id"]` 要用新 ID | 2 物品引用遷移 | 低：**沒有任何呼叫者**（grep 只有定義）；三處 `data-goview` 處理函式都丟掉 view 段、改開 `gvOpen`（CLAUDE.md 寫「保留給其他地方用」） | P1 | 不處理或刪除：拆分時確認沒有外部使用者再刪 | CODE grep `goView(` 只有 :1479 |
| global.route.floor-switch | 全樓層（內容依目前樓層） | 全站 | N/A | 函式 | `setFloor(f)`（樓層選擇 `pickFloor` → `go(view,f)` → `show()` → `setFloor`） | :3588–3599 | N/A | 共用 | 同樓層直接 return；換樓層：改樓層標籤、重建 `#floorInfo`、更新分頁數字、清路線、`fillNpcArea`／`fillZoneSelect`／`fillTownChips`、離開校正模式、`DGV=null`（非第 1 層）、`renderMap`、`renderZoneList` | `FL`、`fitted` | 樓層全部資料 | `FLOORS[f]` | N/A | N/A | 中：**不關面板、不碰 `stack`**（見第 5 節 #32）；`COLLAB_PAUSE`、`SITE_PAUSE_MSG` 是 :3135 的 `const`，`setFloor` 在它之後才第一次執行，拆檔順序改變會變成 TDZ 錯誤（A-R11） | P0 | 保留；拆分時把 `COLLAB_PAUSE` 等搬到共用設定 | :3593–3599 |
| global.link.data-go | 全樓層 | 全站（面板、彈出視窗、清單卡片、已收錄、裝備視窗） | 各容器 | 屬性 | `[data-go="<type>\|<id>"]`；type＝m 怪物、e 裝備（官網 oid 或 x…）、p 道具（oid 或 g…）、i 素材（ITEMS 英文 key）、r 配方（ALLREC 索引）、n NPC（`n<樓層>_<序號>`）、q 任務（`mq<樓層>_<序號>` 或支線 id）、s 地點、t 城鎮、c 職業、d 活動地下城 | 綁定：`bindGo` :1422（清單、`#cwBody`、`#bWrap`、`#doneL`）、`renderP` :1212–1214、`gvRender` :1463 | 動態（屬性寫在模板字串裡，綁定在每次重畫後） | 共用 | 清單卡片：`openP(t,i,"new")`；面板內：`openP(t,i,"push")`；內嵌頁：開彈出視窗或換頁；彈出視窗內：`gvLink`（同選單換內容、不同選單疊新視窗） | 面板 `stack`、彈出視窗 `hist` | 全部 | `i` 經 `redirI` 轉成 e／p（:1176）；`p` 經 `redirP` 轉成 i；`ikey()` 處理舊名；`r` 用陣列索引；`n`／`q` 用序號 | **主要受影響**：值從名稱／陣列索引／序號改成永久 ID；`i\|英文名`、`r\|索引`、`n\|n1_52`、`q\|mq1_33` 都不是穩定身份 | 2 物品引用遷移（i、e、p、r）；後續（m、n、s、t、q） | 高：同一個屬性有 3 種不同處理方式、三套綁定（A-R3） | P0 | 改名＋補識別：保留屬性名，值改 ID；三套綁定合成一個委派 | fixed_links entity 933 筆（e 233、i 194、m 180、p 109、n 95、r 69、s 45、t 8） |
| global.link.data-goview | 全樓層 | 面板、彈出視窗、清單卡片 | 各容器 | 屬性 | `[data-goview="<view>\|<type>\|<id>"]` | `bindGo` :1423、`renderP` :1215、`gvRender` :1462 | 動態 | 共用 | **一律開中央彈出視窗**，view 段被丟掉（`gvOpen(t,i)` 或 `gvLink`） | 同上 | 裝備、道具、配方 | 同 data-go | 同 data-go；view 段可以考慮拿掉 | 2 物品引用遷移 | 中：view 段沒用卻被 fixed_links 當成 key 的一部分（538 筆：recipes 293、equip 188、props 57） | P0 | 保留格式（fixed_links 依賴）；之後若拿掉 view 段要同時改 fixed_links | fixed_links goview 538 筆 |
| global.link.data-repgo | 全樓層 | 全站（資料來源的「回報 R000N」） | 各容器 | 屬性 | `[data-repgo="R000N"]` | document 委派 :3687；`goRep` :3684；彈出視窗內另外 `gvCloseAll`（:1466） | 動態 | 共用 | 切到 `#report`，每 50 ms 找 `#doneL li.replist[data-rid]`（最多 40 次），捲到中間並閃一下 | `.rflash` | 玩家回報 | `data-rid`＝回報編號 | N/A（回報編號本來就是穩定 id） | N/A | 中：靠輪詢等 DOM 出現（A-R9） | P0 | 保留 | :3684–3687；fixed_links 0 筆、smoke 0 筆（report_types_test.py 有測） |
| global.link.data-rep | 全樓層（內容依目前樓層） | 面板、彈出視窗、已收錄 | 各容器 | 屬性 | `[data-rep="<樓層>\|<x>\|<z>"]` | `renderP` :1216–1226、`gvRender` :1468、`#doneL` :3207 | 動態 | 共用但不同：手機的任務步驟只把小地圖上的點標紅（:1220），其他手機情況走 `goMapThen` 切地圖；桌面開浮動地圖 | 座標 → `showPoints` | 無 | 座標 | 座標字串 | N/A（座標不是身份） | N/A | 中：**`#cwBody` 裡的 `data-rep` 沒有綁定，點了沒反應**（VERIFIED）（A-R3） | P1 | 補綁定 | check3 `cwRep`：點了 rwin 沒開、hash 沒變 |
| global.link.data-route | 全樓層（內容依目前樓層） | 面板、彈出視窗 | 任務面板 | 屬性 | `[data-route="<任務 id>"]` | `renderP` :1229、`gvRender` :1465 | 動態 | 桌面；手機由 CSS `[data-route],[data-imap]{display:none!important}` 隱藏（:175，CODE） | `openRouteWin(任務路線)` | `RW` | 任務 | `questById(id)` | 任務 id 改永久 ID | 後續：任務遷移 | 低 | P1 | 保留 | smoke「enlarge opens the floating route window」 |
| global.link.data-imap | 全樓層（內容依目前樓層） | 面板、彈出視窗 | 物品／素材面板 | 屬性 | `[data-imap="<ITEMS key>"]` | `renderP` :1228、`gvRender` :1469 | 動態 | 桌面；手機由 CSS 隱藏（:175，CODE） | `openRouteWin(物品取得地點)` | `RW` | 物品 | `itemMap(ITEMS key)`、`zhI` | 值從英文 key 改永久 ID | 2 物品引用遷移 | 中：`#cwBody` 沒綁（目前裝備面板沒有這個按鈕，VERIFIED 0 個，潛在） | P1 | 改值＋統一綁定 | smoke `[data-imap]` |
| global.link.data-spot | 全樓層（內容依目前樓層） | 面板、彈出視窗 | 地點面板 | 屬性 | `[data-spot="<地點 id>"]` | `renderP` :1230、`gvRender` :1470 | 動態 | 共用（手機走 `goMapThen`） | `showPoints(地點)` | 無 | 地點 | `spotById` | 地點 id 改永久 ID | 後續：地點遷移 | 低 | P1 | 保留 | CODE |
| global.link.data-town | 全樓層（內容依目前樓層） | 面板 | 城鎮面板「在地圖上查看」 | 屬性 | `[data-town="<城鎮 id>"]` | `renderP` :1231；**`gvRender` 沒有綁** | 動態 | 共用 | `showPoints(城鎮)` | 無 | 城鎮 | `townById` | 城鎮 id 改永久 ID | 後續：地點遷移 | **中：在彈出視窗裡打開城鎮，「在地圖上查看」點了沒反應**（VERIFIED）（A-R3） | P1 | 補綁定 | check2 `gvTownClick`：rwin 沒開、hash 沒變 |
| global.link.data-eqcls | 全樓層 | 職業面板 | `#pBody`／`.gvbody` | 屬性 | `[data-eqcls="<職業 id>"]` | `renderP` :1227、`gvRender` :1464 | 動態 | 共用 | `openClassEquip(職業)` 開 `#cwin` | `CW` | 職業、裝備 | `CLS.find`、`eqClasses(e)` | 裝備清單卡片的 `data-cwe` 改 ID | 2 物品引用遷移 | 低 | P1 | 保留 | smoke「equipment window opens over the classes tab」 |
| global.link.data-imgzoom | 全樓層 | 面板、彈出視窗 | 任務步驟圖片 | 屬性 | `a[data-imgzoom][href]` | document click capture 委派 :2957 | 動態 | 共用 | 開 `.imgzoom` 看圖視窗；←／→ 切換同一組（`.mqs`、`#pBody`、`.gvbody`、`body` 最近的） | 無 | 任務圖片 | `href` | N/A | N/A | 中：Esc 順序問題（A-R5） | P1 | 保留 | smoke:116–119 |
| global.link.data-dgmap@f1 | 第 1 層（地下城地圖只有第 1 層） | 地下城面板 | `#pBody`、`.gvbody` | 屬性 | `[data-dgmap="<地下城 id>"]` | document click capture 委派 :3322 | 動態 | 共用；手機會關面板（:3323） | 切到地下城地圖 | `DGV` | 地下城 | 地下城 id（jmmeta `SAO_JM.dg` 的鍵） | 地下城 id 改永久 ID | 後續：地點遷移 | 低 | P1 | 保留（由 C／D 分工細查）；v2：由原本合併的一列拆出 | :3322 |
| global.link.data-under@f1 | 第 1 層（`data-under` 只在第 1 層出現） | 城鎮／地點面板 | `#pBody`、`.gvbody` | 屬性 | `[data-under][data-ux][data-uz]` | document click capture 委派 :3326 | 動態 | 共用 | 插入地下截圖 | N/A | 地點 | 座標 | N/A | 後續：地點遷移 | 低 | P1 | 保留（由 C／D 分工細查）；v2：由原本合併的一列拆出 | :3326 |
| global.selection.data-key | 全樓層 | 全站 | 清單卡片、地圖標記、`#cwBody` 卡片 | 屬性 | `[data-key="<type>\|<id>"]`（卡片同時有 `data-go`） | `markSel` :1237–1239 | 動態 | 共用 | 面板目前那一筆的卡片加 `.sel`、地圖縮圖加 `.selm` | `.sel`、`.selm` | 全部 | 同 data-go | 值改 ID，和 data-go 同步 | 2；後續 | 中：`goView`、baseline、smoke 都用它找卡片（`.card[data-key="m\|m0"]`） | P0 | 保留：是卡片定位的唯一穩定方式 | baseline_capture.js:83、:120、:150 |
| panel.back | 全樓層 | 面板 | `#panel .ptop` | button | `#pBack` | :884、:1206、:1233 | 靜態；`hidden` 由 `renderP` 依堆疊深度設定 | 共用（手機 `body.pdeep` 才顯示路徑） | `stack.pop()` → `renderP()` | `stack` | N/A | N/A | N/A | N/A | 低 | P0 | 保留；smoke 沒有測 | :1233 |
| global.route.cross-floor | 全樓層 | 全站 | N/A | 行為（沒有獨立元件） | 換樓層只有 3 條路：① 樓層選擇 `.flcell`／`#flForm` → `pickFloor` → `go(view,f)`（保留目前分頁）；② 直接改 hash（含選單 `href`，`show()` 每次把選單連結改成目前樓層）；③ `goMapThen(f,fn)` → `go("map",f)`（`showPoints`／座標連結指到別層時） | :3588–3592、:3617、:1187 | N/A | 共用（手機 `goMapThen` 先 `closeP`） | 換樓層一律經過 `show()`→`setFloor` | `FL` | 樓層 | `FLOORS[f]`；`data-rep` 的第一段是樓層 | N/A | N/A | 中：`openP`／`data-go` **不會換樓層**——從第 1 層面板點到第 2 層的怪物或 NPC，面板顯示它，但地圖、清單、`#floorInfo` 仍是第 1 層；面板也不會因換樓層關閉（A-R13、A-R14） | P1 | 保留；記錄「面板不帶樓層」的行為 | :1176–1179（`openP` 沒有碰 `FL`） |
| global.route.back-controls | 全樓層 | 全站 | 各視窗 | button | `#pBack`（面板堆疊）、`.gvprev`（彈出視窗 `hist`）、`#cwBack`（職業裝備視窗回清單）、`#dgBack`（地下城地圖回第 1 層地圖） | :884、:1233；:1441、:1443；:1894；:731、:3314、:3394 | `#pBack`、`#dgBack` 靜態；`.gvprev`、`#cwBack` 動態 | 共用（`#dgBack` 只在地圖分頁的地下城模式顯示） | 各自退回自己的堆疊 | `stack`、`GVW[].hist`、`CW`、`DGV` | N/A | N/A | N/A | N/A | 中：**瀏覽器的「上一頁」只走 hash 歷史**（分頁、樓層），面板、彈出視窗、視窗的狀態都不在歷史裡，按上一頁不會關面板或退回上一筆（CODE：沒有 `pushState`／`popstate`）（A-R14） | P1 | 保留；拆分時決定要不要把面板放進歷史 | CODE grep 無 `popstate` |

### 這一區的風險

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

---

## 3. 共用面板和視窗

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| panel.root | 全樓層 | 全站 | `body` | aside | `#panel` | :883、`openP` :1176、`closeP` :1235 | 靜態外殼 | **共用但版面不同**：桌面右側抽屜，`panel-wide`（任務）、`panel-xwide`（職業）；手機全螢幕（:659） | 開、關、Esc（非內嵌時，:1236） | `hidden`；JS 變數 `stack`；`body.panel-open/panel-wide/panel-xwide/pdeep` | 全部 | `openP` 先 `redirI`／`redirP` | 面板 `stack` 存 `{type,id}`，id 改永久 ID | 2；後續 | 高：狀態在 JS 變數，DOM 只是畫面；關閉時 `#pCrumb` 文字不清（VERIFIED 關閉後仍是舊名稱）（A-R7） | P0 | 保留 id；`stack` 改成存永久 ID | :1176–1179、:1235 |
| panel.crumb | 全樓層 | 面板 | `#panel .ptop` | span | `#pCrumb` | :884、:1206 | 動態（`renderP` 寫 `stack.map(nameOf)`） | 手機只在 `pdeep` 顯示 | 無 | 無 | 全部 | `nameOf`（:1188） | `nameOf` 依 type 查名稱，改 ID 後要改查表 | 2；後續 | 中：`data-rep` 處理用 `pCrumb` 的最後一段當浮動地圖標題（:1226），文字變成邏輯輸入（A-R7） | P1 | 補識別：標題從 `stack` 算，不讀 DOM 文字 | :1226 |
| panel.close | 全樓層 | 面板 | `#panel .ptop` | button | `#pClose` | :884、:1234 | 靜態 | 共用；**內嵌模式整個 `.ptop` 隱藏**（`body.cls-inline`，:197） | `closeP()` | 無 | N/A | N/A | N/A | N/A | 低 | P0 | 保留：smoke 用了 18 次 | smoke `pClose` 18 次 |
| panel.body | 全樓層 | 面板 | `#panel` | div | `#pBody` | :885、:1207 | **重建**：每次 `renderP` 整個 innerHTML（`detailHTML`＝`zhHTML(detailHTML0)`），**換樓層、換分頁都不重畫**（VERIFIED `#pBody>*` kept） | 共用；資料來源 `.note.srcn` 桌面合併成 `.srcend` 放最後，手機收進 `details.srcfold`（:1209–1210） | 子元素連結見 A-R3 | 無 | 依 type：c/r/n/q/m/i/e/p/s/d/t | `detailHTML0` 分派（:1190） | 每種 type 的 id 改永久 ID | 2；後續 | 中 | P0 | 保留 | :1207–1231 |
| panel.inline | 全樓層 | classes、dungeons | `#panel` | 模式（body class） | `body.cls-inline`、`body.cls-one`；CSS 變數 `--clsw/--clsl/--clst` | `INL` :1196、`fitClsPanel` :1197–1202；`renderDungeons` :1812–1815、`renderClasses` :1840–1841 | 動態 | **桌面專用**（`innerWidth>820`）；VERIFIED 1280→390 縮窗時變回一般全螢幕面板（有 ✕，Esc 可關） | 進分頁自動開上次看的（`lastCls`／`lastDg`）或第一個；裡面的連結開彈出視窗；Esc 不關 | `lastCls`、`lastDg` | 職業、地下城、活動地下城 | `CLS`、`spotsOf`、`EVT.dungeons` | 地下城 key `"s\|id"`／`"d\|id"` 改永久 ID | 後續：地點遷移 | 中：判斷「是不是內嵌」看 `stack[0]`（離開時，:3614）和 `stack[last]`（`fitClsPanel`），兩者不同時結果不同（A-R7） | P0 | 保留；統一用同一個判斷 | smoke「class is shown on the page (no ✕)」「Esc does not close the dungeon」 |
| popup.layer | 全樓層 | 全站 | `body` | div | `#gvLayer` | :880 | 靜態外殼 | 共用 | 放所有彈出視窗 | `GVW` 陣列 | N/A | N/A | N/A | N/A | 低 | P0 | 保留 | :1438（`gvNew` 把視窗 append 進來） |
| popup.window | 全樓層 | 全站 | `#gvLayer` | div[role=dialog][aria-modal] | `.gvback>.gvbox`（`.gvhead`、`.gvprev`、`.gvtitle`、`.gvx`、`.gvbody`） | `gvNew` :1438–1457、`gvRender` :1458–1470、`gvOpen` :1472、`gvClose` :1473 | 動態（可疊多個，`z-index 60+n`、`--gvn` 偏移） | 共用；手機不能拖（:1447） | `gvMenu`（:1434）決定同選單換內容或疊新視窗；← 上一個；✕／Esc／點背景只關最上面；換分頁全部關（:3614） | `GVW[].hist`；`__gv()` 掛鉤 | 全部 | `gvNorm`（`redirI`／`redirP`） | `hist` 存 `[type,id]`，改永久 ID | 2；後續 | 中：沒有 id，只能靠 class 定位；連結綁定缺 `data-town`（A-R3） | P0 | 補識別：外殼加 `data-gv-depth`；保留 `window.__gv` | smoke「pop-up」7 項；baseline goview 538 筆 |
| popup.menu-rule | 全樓層 | 全站 | N/A | 函式 | `gvMenu([t,i])` | :1433–1434 | N/A | 共用 | 回傳 codex／recipes／quests／classes／dungeons／bosses／map | N/A | 地點（kind） | `spotById(i).kind` | 地點身份改 ID 後 kind 查表不變 | 後續：地點遷移 | 低 | P1 | 保留 | :1433 |
| floatmap.window | 全樓層（內容依目前樓層） | 全站（地圖分頁以外） | `body` | div[role=dialog] | `#rwin`（`#rwHead`、`#rwTitle`、`#rwIn`、`#rwOut`、`#rwFit`、`#rwX`、`#rwBody`、`#rwSvg`） | :882、`openRouteWin` :1652、`showPoints` :1183–1186、`rwRender` :1641 | 靜態外殼；SVG 內容重建 | **桌面專用**：手機 `showPoints` 一律改走 `goMapThen` 切地圖（:1183）；任務放大按鈕手機隱藏 | 拖標題、滾輪縮放、拖曳平移、✕／Esc 關；換分頁時若 `RW.view` 不同就關（:3614） | JS `RW`（steps、f、vb、sel） | 地點、城鎮、任務步驟、物品取得點 | 座標 | N/A（只吃座標） | N/A | 低 | P0 | 保留；smoke 用 `#rwin`、`#rwSvg`、`#rwTitle` | smoke「route window zooms/closes」 |
| floatmap.gomap | 全樓層（內容依目前樓層） | 全站 | N/A | 函式 | `goMapThen(f,fn)` | :1187 | N/A | 手機先 `closeP()` 再切地圖並捲到 `#stage` | 存 `pending`，`show()` 切到地圖後執行（:3620） | `pending` | 座標 | N/A | N/A | N/A | 低 | P1 | 保留 | :1187、:3620 |
| cwin.window | 全樓層 | classes（從職業面板打開） | `body` | div[role=dialog] | `#cwin`（`#cwHead`、`#cwTitle`、`#cwX`、`#cwBody`；卡片 `[data-cwe]`、部位膠囊 `[data-cwp]`、返回 `#cwBack`） | :881、`openClassEquip` :1881–1891、`showCWItem` :1894–1895、`closeCW` :1896 | 靜態外殼；`#cwBody` 重建 | 共用（拖曳用指標事件） | 部位篩選、點裝備在視窗內顯示詳細；✕／Esc 關；換分頁（`CW.view` 不同）關 | JS `CW`（cid、part、scroll） | 職業、裝備 | `EQ`、`eqClasses`、`EQ_PART`；卡片 `data-key="e\|oid"`＋`data-cwe="oid"` | `data-cwe` 和 `data-key` 改永久 ID | 2 物品引用遷移 | 中：見 A-R3（座標沒綁、連結取代職業頁）；`.rwin` class 和 `#rwin` 共用（A-R2） | P1 | 補綁定 | smoke「equipment window opens」「item detail opens inside the window」 |
| imgzoom.viewer | 全樓層 | 任務面板、彈出視窗 | `body`（動態） | div[role=dialog] | `.imgzoom`（`.imx`、`.imnav.imp/.imn`、`img`） | :2957–2964 | 動態（每次點擊建立，關閉時移除並拿掉 keydown） | 共用 | ←／→ 切換、Esc／✕／點背景關 | 無 | 任務圖片 | `a[data-imgzoom]` 的 `href` | N/A | N/A | **中：從彈出視窗裡打開時，第一次 Esc 關掉的是彈出視窗、看圖視窗留著**（VERIFIED）（A-R5） | P1 | 補識別（加 id）；修 Esc 順序 | check2 `gvImg_after1`：gv 0、img 還在 |
| global.esc-order | 全樓層 | 全站 | `document`／`window` | 事件順序 | 見下表 | 見下表 | N/A | 共用 | 見下表 | N/A | N/A | N/A | N/A | N/A | 中（A-R5） | P1 | 拆分時改成單一 Esc 管理器（堆疊：最後打開的先關） | 下表 |

**Esc 的實際處理順序**（CODE＋VERIFIED）。同一個節點、同一個階段的監聽器依「註冊順序」執行：

| 順序 | 階段 | 註冊位置 | 條件 | 停止傳遞 |
|---|---|---|---|---|
| 1 | document capture | :1475（載入時） | 有彈出視窗 → 關最上面那個 | `stopImmediatePropagation`（後面全部不執行） |
| 2 | document capture | :2962（看圖視窗打開時才註冊） | 看圖視窗 → 關閉 | `stopImmediatePropagation` |
| 3 | document capture | :2968（jm 放大圖打開時才註冊） | 放大的探索地圖 → 關閉 | `stopPropagation`（同節點後面的仍執行） |
| 4 | target | :2180（`#fEqEff` 輸入框自己） | 效果清單開著 → 關 | `stopPropagation`＋`preventDefault` |
| 5 | document bubble | :1236 | 面板開著、不是內嵌 → `closeP` | 無 |
| 6 | document bubble | :1664 | 路線視窗開著 → 關 | 無 |
| 7 | document bubble | :1901 | 職業裝備視窗開著 → 關 | 無 |
| 8 | document bubble | :2991 | 打包工具的小視窗／預覽視窗 | 只有關預覽時 `stopPropagation`（擋不住同節點） |
| 9 | document bubble | :3577 | 關於本站選單 | 無 |
| 10 | document bubble | :3587 | 樓層選擇 | 無 |
| 11 | window bubble | :3720（導覽開著時） | 結束導覽 | 無 |

### 這一區的風險

- **A-R5｜中｜:1475、:2962｜Esc 順序**：（a）看圖視窗的監聽器在打開時才註冊，排在彈出視窗（:1475，載入時註冊）之後；兩者都在 capture 階段而且彈出視窗那個會 `stopImmediatePropagation`，所以**在彈出視窗裡打開任務圖片，按 Esc 先關掉下面的彈出視窗**，圖片還浮在畫面上，要再按一次（VERIFIED：check2 第一次 Esc 後 `gv:0, img:true`，第二次才 `img:false`）。（b）bubble 階段 5～10 都不停止傳遞，**一次 Esc 會同時關掉面板、路線視窗、職業裝備視窗**（VERIFIED：任務面板＋路線視窗，一次 Esc 兩個都關；職業裝備視窗同理，CODE）。smoke 只測了「看圖視窗在面板上」和「彈出視窗在面板上」兩種組合。**建議修法**：一個 Esc 管理器，維護「打開順序」的堆疊，每次只關最上層。**需要程式修改**：是。
- **A-R7｜中｜:1188、:1226、:3614、:1197｜面板狀態和 DOM**：面板的真正狀態是 JS 變數 `stack`（不是 DOM），這點是好的；但有兩處反過來讀 DOM：（1）`data-rep` 用 `#pCrumb` 的文字最後一段當浮動地圖標題（:1226），名稱顯示改了就跟著變；（2）關閉時 `#pCrumb` 不清（VERIFIED），目前沒有地方讀關閉後的文字，但拆分後若有人拿它判斷就會錯。另外「是不是內嵌頁」離開分頁時看 `stack[0]`、`fitClsPanel` 看 `stack[last]`。**建議**：標題由 `stack` 算；`closeP` 清空 crumb；內嵌判斷統一。**需要程式修改**：是（小）。
- **A-R2b｜低｜:881–882｜`.rwin` 兩個視窗共用**：`#cwin` 和 `#rwin` 都是 `class="rwin"`，`.rwhead` 也共用。JS 都用 id，CSS 共用是刻意的。拆分時新程式不要用 `.rwin` 找「路線視窗」。**需要程式修改**：否。
- 檢查過、沒有問題：彈出視窗、面板、裝備視窗同時打開同一筆資料時，detail HTML 裡沒有固定 id（只有 `miniTiles` 的 `mt<流水號>` 遮罩 id，每次呼叫都新編號，全站 279 個沒有重複）——VERIFIED check2 `detailIds`；所以同一筆資料放進 3 個容器不會造成重複 id。

---

## 4. 列表頁共用機制

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global.list.filters | 全樓層 | 所有 `.view.browse`（monsters、items、npcs、quests、equip、props、recipes、dungeons、classes） | `section.view.browse` | div | `#view-<v>>.filters` | :762、:773、:788、:798、:811、:828、:843、:856、:864 | 靜態 | 共用但版面不同：桌面左欄（職業分頁電腦版不顯示）；手機只顯示第一組，其他收在「更多篩選」 | 子元素各自事件；document 委派 click／change／input → `actSync`（:3666–3668） | 子控制項的值 | 依分頁 | N/A | N/A | N/A | 中：桌面的部分 `.fgroup` 會被搬到 `.topf`／`.rsel`（A-R8） | P1 | 保留 | :3666–3668 |
| global.list.filters.chips | 全樓層 | 同上 | `.fgroup` | div＞button | `.chips#<id>>.chip[data-v][aria-pressed]`；預設值 `data-def`（只有 `#fEqFl`、`#fPrFl` 是 `here`，其他是 `all`） | `chipsInto` :1420–1421 | 動態（`chipsInto` 建立時寫 innerHTML；VERIFIED 點膠囊、換樓層後 `#fEqPart .chip` 節點保留，只改 `aria-pressed`） | 共用 | 點選 → `set(v)` → 改 `aria-pressed` → `cb()` | `aria-pressed` | 依分頁 | `data-v`＝篩選值 | N/A | N/A | 中：見 A-R6（`fbarSync` 不看 `data-def`） | P1 | 保留 | :1420 |
| global.list.topf | 全樓層 | monsters、equip、items、props | `.results` | div | `.results>.topf`（裝 `TOPF` 列的 `.fgroup`） | `TOPF` :3624、`placeTopFilters` :3626–3630 | 動態（第一次建立，之後**搬移**原本的 `.fgroup`，用註解節點 `__home` 記住原位） | **桌面專用**（`topMQ` min-width:821px；手機搬回左欄、`.topf` hidden，VERIFIED） | 切換斷點時 `placeTopFilters()`＋`renderCurrent()`（:3636） | `g.__home`（DOM 節點上的 JS 屬性） | N/A | `TOPF` 寫死的 id：fMonType、fEqPart、fEqSub、fItemGroup、fPrGroup、fPrSub、fPrSub2 | N/A | N/A | 中：同一個 `.fgroup` 在桌面和手機位於不同父節點；靠 `closest(".fgroup")` 和 `__home` 註解節點（A-R6、A-R8） | P1 | 保留；拆分時 `TOPF` 列的 id 不能改 | check3 `disp390 .topf none(hidden)` |
| global.list.rsel | 全樓層 | 所有 `.view.browse` | `.results>.rhead` | div | `.rhead>.rsel`（含 `<select>` 或 `.torsel` 的 `.fgroup`） | `placeTopFilters` :3631–3635 | 動態（搬移） | 桌面專用（手機搬回，VERIFIED hidden） | 同上 | 同上 | N/A | 條件：有 `select` 或 `.torsel`、而且沒有 `.chips` | N/A | N/A | 中：判斷「要不要搬」看內容結構，新增 `.fgroup` 時可能被意外搬走（A-R8） | P1 | 補識別：用 `data-place="rsel"` 明確標記 | smoke `.rsel` 0 次 |
| global.list.actf | 全樓層 | 所有 `.view.browse` | `.results>.rhead` | div＞button | `.rhead>.actf`（`.af[data-i]`、`.afm[data-p]`、`.afgl`、`.afx`） | `actControls` :3644–3657、`actSync` :3658–3665 | **重建**（每次 `actSync` innerHTML；外殼第一次建立後保留，VERIFIED） | 共用 | ✕ 取消單一條件（呼叫控制項自己的 click／dispatchEvent）、⇄ 換且／或、全部清除 | 無（每次從控制項重新讀） | N/A | 讀 `.chips` 的 `aria-pressed`／`data-def`、`select.selectedIndex`（`id` 結尾 `Sort` 的排除）、checkbox、search、number；效果另讀 `EFF_SEL` | N/A | N/A | 中：靠控制項的 DOM 狀態和 id 命名慣例（`*Sort`）（A-R6） | P1 | 保留；排序排除改用 `data-sort` | smoke `.actf` 7 次 |
| global.list.fbar | 全樓層 | 所有 `.view.browse`（有 ≥2 組或有說明的） | `.filters` | div＞button | `.filters>.fbar .fbtn[data-t="fopen"]`、`[data-t="nopen"]`；狀態 class `.filters.fopen`／`.nopen` | 建立 :3606–3611、`fbarSync` :3601–3605 | 動態（載入時插入一次，插在第 2 組之前） | **手機專用**（桌面 `display:none`，:630；VERIFIED） | 開關「更多篩選」「ⓘ 說明」；數字顯示「已調整 N 項」 | `.fopen`、`.nopen`、`aria-expanded` | N/A | 讀 `.chip[data-v="all"]`（**寫死 all，不看 data-def**）、select、checkbox、number | N/A | N/A | **中：裝備分頁一打開就寫「更多篩選（已調整 1 項）」**（VERIFIED，390 和 1280 都是），因為「取得樓層」預設是 `here`（選項 here／only／all，`FL_CHIPS` :2140），`fbarSync` 只認 `all` 是預設；`.actf` 同時是 hidden（兩者不一致）（A-R6） | P1 | 修：`fbarSync` 改用 `c.dataset.def` | check3 `fbarLabel390`、`actf390` |
| global.list.grid | 全樓層 | 所有 `.view.browse` | `.results` | div | `.browse .grid`（`#lMon`、`#lItem`、`#lNpc`、`#lEq`、`#lPr`、`#lRc`、`#lDg`、`#lCls`；任務是 `#lQ`，不是 `.grid`） | :730 等；`fixCols` :3675–3676 | 靜態外殼；卡片每次重建 | ≥1180px 固定成「面板開著時」的欄數；`#lCls` 例外；手機不固定 | resize、面板開關、`renderCurrent` 時重算 | inline `grid-template-columns` | N/A | `innerWidth>=1180`、`body.panel-open` | N/A | N/A | 低 | P1 | 保留 | smoke「monster grid keeps its column count」 |
| global.list.card | 全樓層 | 所有清單 | `.grid`／`#lQ` | button | `#l<X> .card[data-key="<type>\|<id>"][data-go="<type>\|<id>"]`（任務 `.qcard`） | 各 render 函式；綁定 `bindGo` :1422 | **重建**（每次 render、每打一個字、換分頁、換樓層都整批重寫，VERIFIED） | 共用 | click → `openP(t,i,"new")` | `.sel`（`markSel`） | 依分頁 | `data-go`／`data-key` 值見第 2 節 | 值改永久 ID | 2；後續 | 中：每次重建要重新綁定（A-R8） | P2 | 保留 `data-key`（定位唯一依據）；不逐張列 | check3 `#lEq .card NEW` |

### 這一區的風險

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

---


---

## 第 2 部分（分工 B）：圖鑑五分頁

## 0. 五個圖鑑分頁共用的元件

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| global.codex-nav.subtabs | 全樓層 | 圖鑑（5 個分頁） | `body .app` | nav（5 個 a） | `#codexTabs`；項目 `#codexTabs a[data-v="<view>"]` | src/index.html:712-718；點擊 3569；顯示／隱藏 3615；href 3616 | 靜態（href 由 show() 重寫） | 手機專用（≥821px `display:none!important`，src/index.html:42） | 點了 `go(view)` 換 hash | `hidden`＝不在圖鑑分頁；`aria-current="page"` | N/A | `data-v`＝view 名 | N/A | N/A | B-R4（內含的數量 id 被複製） | P0 | 保留；它的 innerHTML 被 `.vtabs` 照抄（含 id），見 B-R4 | VERIFIED：390px `codexTabsVisible:true`，1280px `false`；tests/smoke.py:346 |
| global.codex-nav.vtabs | 全樓層 | 圖鑑（5 個分頁） | 每個 `#view-<v> .filters` 第一個子元素 | nav（`.vtabs`，5 個 a） | `#view-<v> .filters>.vtabs a[data-v="<view>"]` | 產生 syncVTabs src/index.html:3639-3641；點擊委派 3642 | 重建（每次 renderCurrent 用 innerHTML 從 `#codexTabs` 複製） | 桌面專用（手機隱藏） | 點了 `go(data-v)` | `aria-current="page"` 只標目前分頁 | N/A | `data-v` | N/A | N/A | B-R4、B-R7（和 `#codexTabs` 兩份同功能元件） | P0 | 補識別：複製時拿掉內層 `id`，或改成直接搬移 | VERIFIED：1280px 每個分頁 `vtabsVisible:true`；tests/smoke.py:346-349 |
| global.codex-nav.count | 全樓層 | 圖鑑 | `#codexTabs a`、`.vtabs a` | span | `#nMon` `#nEquip` `#nProp` `#nItem` `#nNpc` | src/index.html:713-717；寫入 setFloor 3596-3597 | 靜態＋被 `.vtabs` 複製成 5 份 | 共用（桌面看到的是複本） | 無 | 文字＝這層的件數 | 怪物／裝備／道具／素材／NPC | `F().M`、`EQ`、`PRV()`、`matPool(f,false)`、`NPCS(f)` | N/A | N/A | B-R4 | P2 | 補識別：只留一份 id，複本用 class | VERIFIED：每個 id 在頁面上 6 份（`dupIds` nMon…×6） |
| global.browse.fbar | 全樓層 | 所有 `.browse` 分頁（含本區 5 頁） | `.filters` | div＋button（`.fbtn[data-t="fopen"\|"nopen"]`） | `#view-<v> .filters>.fbar .fbtn[data-t="fopen"]` | 產生 src/index.html:3606-3610；同步 fbarSync 3601-3605 | 動態（載入時插入一次） | 手機專用（桌面 CSS 隱藏） | 切換 `.filters.fopen`／`.nopen` | `aria-expanded`；文字「已調整 N 項」 | N/A | 讀 `.chip[data-v="all"]`、select、checkbox、number | N/A | N/A | 無 | P1 | 保留 | VERIFIED：1280px `display:none`、390px `flex` |
| global.browse.topf | 全樓層 | 怪物、裝備、素材、道具（NPC 沒有） | `.results`，在 `.rhead` 後 | div（`.topf`），裝被搬移的 `.fgroup` | `#view-<v> .results>.topf` | TOPF 3624；placeTopFilters 3626-3628 | 動態（搬移原本的節點，不是複製） | 桌面專用；手機搬回左欄（註解節點 `__home`） | N/A | `hidden` 依寬度 | N/A | N/A | N/A | N/A | 無 | P1 | 保留；NPC 分頁的類型膠囊沒有搬上來（不在 TOPF），和其他頁不一致但不影響功能 | VERIFIED：1280px 裝備 topf＝`fEqPart,gEqSub,fEqSub`；390px `topf:[]`、hidden |
| global.browse.rsel | 全樓層 | 所有 `.browse` | `.rhead` 件數後 | div（`.rsel`） | `#view-<v> .rhead>.rsel` | placeTopFilters src/index.html:3630-3634 | 動態（搬移含 select 或 `.torsel` 的 `.fgroup`） | 桌面專用 | N/A | `hidden` | N/A | N/A | N/A | N/A | 無 | P1 | 保留 | VERIFIED：1280px 怪物 `fMonZone,fMonSort`、裝備 `fEqSort,fEqEff`、道具 `fPrSort`、素材 `fItemSort`、NPC `fNpcArea`；390px 全空 |
| global.browse.active-filters | 全樓層 | 所有 `.browse` | `.rhead` | div（`.actf`），chip `button.af[data-i]`、切換 `button.afm[data-p]`、`button.afx` | `#view-<v> .actf .af[data-i="<序號>"]` | actControls 3644-3657；actSync 3658-3665；委派 3666-3668 | 重建（每次點擊／變更後 innerHTML） | 共用 | 點 ✕ 取消那一項；⇄ 切且／或；全部清除 | 依目前篩選；chips 以 `data-def`（沒有就 `all`）為預設 | N/A | 讀 `.chips` 的 `aria-pressed`、select、checkbox、`input[type=search]`、number；效果用 `EFF_SEL` | N/A | N/A | B-R6（只能用序號定位） | P1 | 補識別：chip 加 `data-ctl="<控制項 id>"`＋值 | VERIFIED（smoke 間接）：tests/smoke.py:220-223、352-355 |
| global.search.codex-behavior | 全樓層 | 5 個圖鑑分頁 | `#q`（全站搜尋框，在 header） | input[type=search]（共用） | `#q` | 定義 src/index.html:708；`Sq()` 1167；監聽 3672 → renderCurrent 3670 | 靜態 | 共用 | 輸入即重畫目前分頁 | 值跨分頁保留 | 依分頁 | 怪物 monHit 1170、裝備 eqHit 2244、道具 prHit 2326、素材 itemHit 1169＋掉落怪物名、NPC npcCardHit 1570 | 搜尋比對英文 key／法文名／中文名，改永久 ID 不影響比對，但 `ITEMS[...].aka`（ITEM_OLD 舊名）要保留 | 過渡查找清理 | 無 | P1 | 保留（`#q` 本身由負責 header 的分工列） | CODE；tests/smoke.py:225、415 |
| global.chips.factory | 全樓層 | 本區所有膠囊篩選 | 各 `.chips` 容器 | button（`.chip[data-v]`） | `#<容器 id> .chip[data-v="<值>"]` | chipsInto src/index.html:1420-1421 | 重建（每次呼叫整組 innerHTML） | 共用 | 點了 set＋全組 `aria-pressed`＋callback | `aria-pressed="true"` | N/A | `data-v` 原樣寫入、**沒有 esc**（1420） | N/A | N/A | B-R6、B-R7 | P1 | 保留；`data-v` 改用代碼而不是中文顯示名（素材／道具分類現在是中文） | CODE；VERIFIED：每個 `.chips` 容器內 `data-v` 不重複 |
| global.list.bindgo | 全樓層 | 5 個清單 | `#lMon` `#lEq` `#lPr` `#lItem` `#lNpc` | 事件綁定 | `[data-go]`、`[data-goview]` | bindGo src/index.html:1422-1423 | 每次 render 後重新綁 | 共用 | `data-go` → `openP(t,i,"new")`；`data-goview` → `gvOpen(t,i)` | N/A | 全部 | `data-go="<type>\|<id>"` 用 `split("\|")` 拆，`id` 不能含 `\|`（目前 ITEMS 沒有，VERIFIED `pipeKeys:[]`） | 改永久 ID 時 `<id>` 換成 Registry ID；`split` 只取前兩段 | 2 物品引用遷移 | B-R1 | P0 | 保留；新 ID 不要用 `\|` | VERIFIED：pipeKeys 0 |
| panel.shared.router | 全樓層 | 右側面板／彈出視窗 | `#panel #pBody`、`.gvback .gvbody` | 函式 | `#pBody`（右側）、`#gvLayer .gvback:last-child .gvbody`（彈出） | openP 1176-1178；nameOf 1188；detailHTML／detailHTML0 1189-1190；renderP 1205-1232；markSel 1237-1239；gvNorm 1432、gvMenu 1433、gvOpen 1472 | 重建 | 共用；手機 `#panel` top 0 全螢幕 | `openP` 把 `i` 經 `redirI` 改成 `e`／`p`，`p` 經 `redirP` 改成 `i` | `stack`（只存在記憶體） | 全部 | type：`m e p i n r s t q c d` | 面板的 stack 用 `[type,id]`，改 ID 後 `nameOf`／`markSel` 跟著換 | 2 物品引用遷移 | B-R5 | P0 | 保留（面板本身由負責全站面板的分工列；這裡只記圖鑑的入口） | VERIFIED：390px `panelTop:0px`、1280px `66.7px` |

### 這一區的風險
- 見 B-R4（數量 id 重複）、B-R6（動態 chip 只能用序號）、B-R7（同功能兩套元件）。
- 檢查了：每個 `.chips` 容器內 `data-v` 是否重複、每個清單的 `data-key` 是否重複（VERIFIED：5 個清單 `dupCardKeys` 都是空的）、1280／390 兩種寬度的 topf／rsel 搬移（VERIFIED）、橫向捲動（VERIFIED：5 個分頁兩種寬度 `scrollX:false`）。

---

## 1. 怪物 `#view-monsters`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| monsters.view.container | 全樓層 | 怪物 | `body` | section.view.browse | `#view-monsters` | src/index.html:761 | 靜態 | 共用 | show() 設 `hidden`（3613） | `hidden` | 怪物 | 網址 `#f<N>-monsters` | N/A | N/A | 無 | P0 | 保留 | tests/fixed_links.json `route:#f1-monsters`；VERIFIED 開啟 |
| monsters.list.header | 全樓層 | 怪物 | `#view-monsters .results` | div.rhead＋h2＋span.count | `#view-monsters .rhead`、`#cMon` | src/index.html:768；件數 1499 | 靜態（件數動態） | 共用 | 無 | 「N / M 種・已知等級 K」 | 怪物 | `F().M`、`lvOf` | N/A | N/A | 無 | P2 | 保留 | VERIFIED：`67 / 67 種・已知等級 15` |
| monsters.filter.type | 全樓層 | 怪物 | `.filters`（桌面搬到 `.topf`） | chips | `#fMonType .chip[data-v="all"\|"Boss"\|"Mini-Boss"\|"Monster"\|"Minion"]` | HTML 763；chipsInto 1491 | 動態（載入一次） | 共用但版面不同（≥821px 在 `.topf`） | 設 `monType` → renderMon | `monType`（記憶體，不存 localStorage） | 怪物 | `m.type`（英文代碼） | N/A | N/A | 無 | P1 | 保留 | VERIFIED topf=`fMonType` |
| monsters.filter.zone | 全樓層 | 怪物 | `.filters`（桌面搬到 `.rsel`） | select（optgroup 野外／地下城） | `#fMonZone`；值 `all`／`@dg`／`@wild`／區域 key | HTML 764；fillZoneSelect 1494-1495（setFloor 3597 呼叫）；onchange 1492 | 重建（每次換樓層） | 共用但版面不同 | renderMon | select 值；換樓層時重建、選擇丟失 | 地點（ZONES） | `F().zones[key]`、`isDgZone`（依名稱正則 1493） | 區域 key 是 data.js／data23.js 的字串鍵，R0.6 做地點遷移時可能要換 | 後續：NPC／地點／怪物／任務遷移 | 無 | P1 | 保留 | tests/smoke.py:419-422 |
| monsters.sort | 全樓層 | 怪物 | `.rsel` | select | `#fMonSort`（num／diff／name／lv） | HTML 765-766；onchange 1492；排序 1498 | 靜態 | 共用但版面不同 | renderMon | select 值 | 怪物 | `name` 用英文 `m.name`，顯示是 `mN(m)` 中文 | N/A | N/A | B-R9 | P1 | 保留（名稱排序規則待使用者決定） | CODE src/index.html:1498 |
| monsters.search | 全樓層 | 怪物 | `#q` | 行為 | `#q` | monHit 1170；renderMon 1497 | N/A | 共用 | 比對 名稱＋中文名＋舊名 aka＋編號＋區域名＋掉落物（itemHit shallow） | N/A | 怪物、物品 | `m.aka`、`FLOORS[f].zones[m.zone]`、`itemHit(d[0])` | 掉落物 `d[0]` 是 ITEMS key（名稱），物品遷移後要改成查 ID 的顯示名 | 2 物品引用遷移 | 無 | P1 | 保留 | tests/smoke.py:415 |
| monsters.list.container | 全樓層 | 怪物 | `.results` | div.grid | `#lMon` | HTML 768；renderMon 1496-1505 | 重建（每次 innerHTML） | 共用（≥1180px fixCols 固定欄數 3675） | bindGo 1504、markSel | N/A | 怪物 | `F().M` | N/A | N/A | 無 | P1 | 保留 | VERIFIED：換篩選後第一張卡片是新節點（`rebuild:false` 於裝備分頁；怪物同一寫法，CODE） |
| monsters.list.card | 全樓層（卡片只列目前樓層） | 怪物 | `#lMon` | button.card | `#lMon .card[data-key="m\|<monster id>"]`（同值也在 `data-go`） | renderMon 1500-1503 | 重建 | 共用 | openP("m",id) | `.sel`（markSel） | 怪物、物品（掉落小圖示） | `monById[id]`（1009）；id＝`m<陣列序>`（data.js:121）／`f<N>m<序>`（data23.js:13、16）／`rep-R<N>`（回報新增，1004） | **id 是陣列序號**：data.js M 陣列插入、刪除或改順序，所有 id 往後移 | 後續：NPC／地點／怪物／任務遷移 | B-R1 | P2 | 補識別（永久 ID）：卡片定位方式不變，值改永久 ID | VERIFIED：67 張、無重複，樣本 `m\|m0`；tests/fixed_links.json `m\|m*` 67 條、`m\|f[23]m*` 115 條 |
| monsters.list.card.drops | 全樓層 | 怪物 | 卡片 | span.slot（`.minis`） | `#lMon .card .minis .slot` | renderMon 1503；slot 1157-1160 | 重建 | 共用 | 無（不可點） | N/A | 物品 | `slot(ITEMS key)`、`GICON[key]`、`redirI` 借裝備圖示 | 圖示表 `ITEMS[key].ic` 以名稱為鍵 | 2 物品引用遷移 | 無 | P2 | 不處理 | CODE |
| monsters.avatar | 全樓層 | 怪物卡片、面板、地圖、素材分組標題 | 各處 `.th` | img.face 或 emoji span | `.th img.face` | face 1141；renderOf 1140（`SAO_MOBCODEX.by[floor][name]`）；photoOf 1137（`SAO_MOBPHOTO.by[floor][name]`，第 1 層再退到 `S1.PHOTO[name]`）；thHTML 1155 | 動態 | 共用 | 無 | N/A | 怪物 | **名稱鍵**：`(floor, m.name)` | 回報改名（renameMon 994）後 `m.name` 變了，頭像就對不到（舊名不查） | 後續：NPC／地點／怪物／任務遷移 | B-R3 | P2 | 改名：圖片表改用怪物永久 ID 或也查 `aka` | CODE；tests/smoke.py:587 |
| panel.monster.header | 全樓層 | 怪物面板 | `#pBody` | div.phead | `#pBody .phead`（無專屬 hook） | monDetail 1242-1245 | 重建 | 共用 | 無 | N/A | 怪物 | `monById[id]`、`mN(m)`（1094：`ZMOB[m.num]` 只第 1 層，`ZMOBN[m.name]`） | 中文名依編號或英文名查 | 後續：NPC／地點／怪物／任務遷移 | B-R5 | P1 | 補識別：`data-sec="header"` | CODE |
| panel.monster.location | 全樓層 | 怪物面板 | `dl.facts` | dd＋linkbtn | `#pBody dl.facts button[data-go^="s\|"]` | monDetail 1249-1252 | 重建 | 共用 | 開地點面板（push） | N/A | 地點 | `monPos(m)` 1111：**用怪物名稱比對 `spot.mons`**（含 aka）；`data-go="s\|<spot id>"` | 地點遷移後 `s\|` 值和 `spot.mons` 的名稱都要換 | 後續：NPC／地點／怪物／任務遷移 | 無 | P1 | 保留 | VERIFIED：m1 面板 data-go 類型含 `s` |
| panel.monster.spawns | 全樓層 | 怪物面板 | `dl.facts` | button.linkbtn.mono（`.rnum` 編號） | `#pBody button[data-rep="<f>\|<x>\|<z>"]` | monDetail 1252；renderP 的 data-rep 處理 1216-1226 | 重建 | 共用；手機不開浮動地圖、改切到地圖分頁 | 浮動地圖（同一欄的所有座標一起編號） | N/A | 怪物重生點 | `SPAWN_OF[m.id]`（1058，由 `BOSS_SPAWNS` 依**名稱**建） | 重生點表用怪物名稱，遷移要換 | 後續：NPC／地點／怪物／任務遷移 | 無 | P1 | 保留 | VERIFIED：m1 面板有 `data-rep` |
| panel.monster.map-link | 全樓層 | 怪物面板 | `#pBody` | button.linkbtn | `#pBody button[data-spot="<spot id>"]` | monDetail 1254；renderP 1231 | 重建 | 共用 | showPoints／focusSpot | N/A | 地點 | `spotById` | 同上 | 後續：NPC／地點／怪物／任務遷移 | 無 | P1 | 保留 | VERIFIED：m1 面板有 `data-spot` |
| panel.monster.drops | 全樓層 | 怪物面板 | `#pBody` | ul.rows＋button.lrow | `#pBody ul.rows button.lrow[data-go="i\|<ITEMS key>"]` | monDetail 1243（drops）、1255-1258 | 重建 | 共用 | openP("i",key,"push") → redirI 轉成 `e`／`p`／留 `i`（跨分頁） | N/A | 物品、裝備、道具 | `m.drops[[ITEMS key, %, 標記]]`；`zhI(key)`、`slot(key)`；開啟時 `redirI`→`EQX_BY[key]` 或 `offOf(key)`（法文名） | **主要遷移點**：`i\|<名稱>` 改成物品永久 ID | 2 物品引用遷移 | B-R1、B-R5（同一面板可能出現兩次同一物品，GAME_DROPS `dup`） | P0 | 補識別：值改永久 ID；`dup` 列加區分屬性 | VERIFIED：全部怪物面板 data-go `i` 377 個；4 個面板同物品重複（f3m2、f3m3、f3m4、f3m33） |
| panel.monster.quests | 全樓層 | 怪物面板 | `#pBody` | button.lrow | `#pBody button.lrow[data-go="t\|<town id>"]`（在「相關任務」下） | monDetail 1258 | 重建 | 共用 | **開城鎮面板，不是任務面板** | N/A | 任務、城鎮 | `KILLQ[m.id]`（1043，任務 kill 名稱→`monByName`） | 任務遷移時要決定連到任務還是城鎮 | 後續：NPC／地點／怪物／任務遷移 | B-R7 | P1 | 改名或改連結：標題是任務、連結是城鎮，功能和文字不一致 | VERIFIED：怪物面板 data-go `t` 16 個 |
| panel.monster.hints | 全樓層 | 怪物面板 | `#pBody` | div.hint／div.hint.cdx／p.lore | `#pBody .hint`、`#pBody .hint.cdx` | monDetail 1259-1261 | 重建 | 共用；手機隱藏 `.hfr` 法文 | 無 | N/A | 怪物 | 出沒提示 `SAO_HINTS[floor][m.name 或 aka]`；圖鑑說明 `SAO_CODEX[floor][m.num]` | 名稱／編號鍵 | 後續：NPC／地點／怪物／任務遷移 | 無 | P2 | 不處理 | CODE |
| panel.monster.photo-note | 全樓層 | 怪物面板 | `#pBody` | div.hint.mph＋details.mphold | `#pBody .hint.mph` | photoNote 1151-1154 | 重建 | 共用 | 展開舊調整 | details open | 怪物 | `photoOf(m)`（名稱鍵） | 同 monsters.avatar | 後續：NPC／地點／怪物／任務遷移 | 無 | P2 | 不處理 | CODE |
| panel.monster.reports | 全樓層 | 怪物面板 | `#pBody` | h3＋figure.repfig＋linkbtn | `#pBody .repfig`、`button[data-rep]`、`a.replink[data-repgo="R000N"]` | repBlock 1278-1283；repsOf 1273（`r.monId` 或名稱／aka） | 重建 | 共用 | 截圖另開、地圖、`goRep` 跳協作區（document 委派 3687） | N/A | 回報 | 回報 id `R000N`（穩定） | N/A | N/A | 無 | P1 | 保留 | VERIFIED：6 個面板有「玩家回報」 |
| panel.monster.sources | 全樓層 | 怪物面板 | `#pBody` | div.note.srcn（renderP 合併後放最後） | `#pBody .srcn.srcend`（手機 `details.srcfold`） | monDetail 1265；srcMerge 1203；renderP 1208-1209 | 重建 | 共用但版面不同（≤820px 收合） | 展開（手機） | N/A | N/A | N/A | N/A | N/A | 無 | P2 | 保留 | CODE |

### 這一區的風險
- B-R1（怪物 id 是陣列序號）、B-R3（頭像和圖片用名稱查）、B-R5（面板區塊沒有識別、同物品重複）、B-R7（「相關任務」連到城鎮）、B-R9（名稱排序用英文）。
- 檢查了：卡片 `data-key` 唯一（VERIFIED）、手機寬度篩選搬回左欄（VERIFIED）、全部 208 個怪物面板能打開、沒有例外（VERIFIED，`bad:0`）。

---

## 2. 裝備 `#view-equip`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| equip.view.container | 全樓層 | 裝備 | `body` | section.view.browse | `#view-equip` | src/index.html:810 | 靜態 | 共用 | show() | `hidden` | 裝備 | `#f<N>-equip` | N/A | N/A | 無 | P0 | 保留 | tests/fixed_links.json `route:#f1-equip`（「官方信件裡的連結」） |
| equip.list.header | 全樓層 | 裝備 | `.results` | div.rhead＋`#cEq` | `#view-equip .rhead`、`#cEq` | HTML 823；件數 2253 | 靜態（件數動態） | 共用 | 無 | 「N / 751 件」 | 裝備 | `EQ.length` | N/A | N/A | 無 | P2 | 保留 | VERIFIED：`633 / 751 件`（預設「這一層＋還不知道」） |
| equip.filter.part | 全樓層 | 裝備 | `.topf`（手機在左欄） | chips | `#fEqPart .chip[data-v="all"\|"weapon"\|"off"\|"armor"\|"acc"]` | HTML 812；chipsInto 2126 | 動態（一次） | 共用但版面不同 | 設 `eqPart`＋fillEqSub → renderEquip | `eqPart` | 裝備 | `EQ_PART[e.cat]`（2101） | N/A | N/A | 無 | P1 | 保留 | VERIFIED topf；tests/smoke.py:355 |
| equip.filter.sub | 全樓層 | 裝備 | `.topf` | fgroup＋chips（含 `.cn` 件數） | `#gEqSub`、`#fEqSub .chip[data-v="<cat 或 slot>"]` | HTML 813；fillEqSub 2125；件數 2248 | 重建（每次換部位） | 共用但版面不同 | 設 `eqSubV` | `#gEqSub[hidden]`＝部位是「全部」 | 裝備 | `eqSub(e)`（2117）、`EQ_SUBS`（2118） | N/A | N/A | 無 | P1 | 保留 | tests/smoke.py:361 |
| equip.filter.class | 全樓層 | 裝備 | `.filters` | chips | `#fEqClass .chip[data-v="guerrier"\|"archer"\|…]` | HTML 814；chipsInto 2127 | 動態 | 共用 | 設 `eqClass` | `eqClass` | 裝備 | `eqClasses(e)`＝`st["Classe requise"]`（法文鍵）、`CLASS_ZH` | N/A | N/A | 無 | P1 | 保留 | CODE |
| equip.filter.floor | 全樓層 | 裝備 | `.filters` | chips（`data-def="here"`） | `#fEqFl .chip[data-v="here"\|"only"\|"all"]` | HTML 815；chipsInto 2142；flOk 2141；objFloors 2131-2138 | 動態 | 共用 | 設 `eqFl` | 預設 `here`；已篩選列認 `data-def`（3645） | 裝備、物品、配方、怪物、地點 | `objFloors`：`e.itemId\|\|FR2ID[e.name]`→`itemFloors`；`RECIPE_BY_EQ[e.oid]`；`GI_OID[e.oid]` 或 `GI_EN[e.gen]` 的「Loot: 名稱」→`monByName`；地下城寶箱名稱比對；名稱正則（Kazor／Fallen…） | 多種名稱比對，遷移後要改成依 ID 的反查表 | 2 物品引用遷移 | B-R7（goView 重設會選成「全部樓層」） | P1 | 保留 | tests/smoke.py（`__objFl` 2139） |
| equip.filter.rarity | 全樓層 | 裝備 | `.filters` | chips | `#fEqRar .chip[data-v="c"\|"b"\|"a"\|"s"\|"splus"]` | HTML 816；chipsInto 2143 | 動態 | 共用 | 設 `eqRar` | `eqRar` | 裝備 | `rarK(e.r)`（1122，三種神話合併） | N/A | N/A | 無 | P1 | 保留 | CODE |
| equip.filter.level | 全樓層 | 裝備 | `.filters` | input[type=number] ×2 | `#fEqMin`、`#fEqMax` | HTML 817；監聽 2144 | 靜態 | 共用 | input → renderEquip | 值 | 裝備 | `e.lv`（gamestats 蓋過圖鑑） | N/A | N/A | 無 | P1 | 保留 | CODE |
| equip.sort | 全樓層 | 裝備 | `.rsel` | select | `#fEqSort`（lv／lvd／rar／name） | HTML 818-819；排序 2251 | 靜態 | 共用但版面不同 | renderEquip | 值 | 裝備 | `name` 用**法文** `e.name`，顯示是 `dn(e)` | N/A | N/A | B-R9 | P1 | 保留（待決定） | CODE src/index.html:2251 |
| equip.filter.effect-input | 全樓層 | 裝備 | `.fgroup.torsel` → `.rsel` | input[type=search]＋`span.effwrap` | `#fEqEff` | HTML 820；邏輯區塊 2159-2190 | 靜態 | 共用但版面不同 | 點擊／focus 開清單；打字縮小清單；Esc 關閉（preventDefault） | 關閉時顯示「且：A、B｜或：C」；`aria-expanded` | 裝備、套裝 | `eqAllStats`＝`eqStats`＋`setStats(eqSetOf(e))`；`eqSetOf` 依 `e.gen`／`FR2ID[e.name]`／`e.name` 查 `SET_BY[norm(英文名)]` | 套裝成員是英文名，物品遷移後要改 ID | 2 物品引用遷移 | 無 | P1 | 保留 | tests/smoke.py:209-226 |
| equip.filter.effect-popup | 全樓層 | 裝備 | `span.effwrap` | span[role=listbox]（`.effhd`＋`button.effo`） | `#effPop`；模式 `#effPop [data-effm="and"\|"or"]`；選項 `#effPop .effo[data-eff="<中文效果名>"]`；清除 `#effPop .effo.clr[data-eff=""]` | draw 2173-2175；open／close 2176-2177；點擊 2181-2184；外部點擊關閉（document capture）2189 | 重建（每次 draw） | 共用 | 切換勾選（清單不關）；切新選的模式；清除 | `EFF_SEL`、`EFF_M`、`EFF_MODE`（記憶體） | 裝備數值名（STAT_ZH） | `data-eff` 是**顯示用中文名**（STAT_ZH／SET_LAB 翻譯後） | N/A（不是遊戲資料 ID），但翻譯表改字就改變值 | N/A | B-R6 | P1 | 補識別：清除鈕改用自己的屬性（現在和選項共用 `data-eff`，值空字串） | tests/smoke.py:209-212；`__effPick`／`__effToggle` 2186-2188 |
| equip.search | 全樓層 | 裝備 | `#q` | 行為 | `#q` | eqHit 2244 | N/A | 共用 | 比對法文名、`gen`、中文、搜尋別名 zhS、套裝名、英文類別、舊名 aka、`FR2ID[e.name]` | N/A | 裝備、套裝 | `zhE`、`zhS`（`ZH_SRCH[(ps?"p\|":"e\|")+oid]`）、`eqSetN` | zhnames 的鍵是 `e\|<oid>`，遷移要同步 | 2 物品引用遷移 | 無 | P1 | 保留 | tests/smoke.py:225 |
| equip.list.container | 全樓層 | 裝備 | `.results` | div.grid | `#lEq` | HTML 823；renderEquip 2245-2258 | 重建 | 共用 | bindGo 2257 | **只畫前 240 件**（2254） | 裝備 | `EQ` | N/A | N/A | B-R8 | P1 | 保留 | VERIFIED：240 張；換篩選後第一張是新節點 |
| equip.list.card | 全樓層 | 裝備 | `#lEq` | button.card | `#lEq .card[data-key="e\|<oid>"]` | renderEquip 2255-2257 | 重建 | 共用 | openP("e",oid) | `.sel` | 裝備 | `eqById[oid]`（2097）；oid＝官網數字編號（equip.js／props.js 催化器）或 `x<N>`（EQX，2093-2096） | `x<N>` 是**依 ITEMS key 順序產生的流水號**；官網 oid 穩定 | 2 物品引用遷移 | B-R1 | P2 | 補識別：`x<N>` 改永久 ID | VERIFIED：無重複；樣本 `e\|2475`；fixed_links `e\|x*` 53 條 |
| equip.list.card.stat | 全樓層 | 裝備 | 卡片 | div.estat | `#lEq .card .estat` | renderEquip 2257；eqKey 2122 | 重建 | 共用 | 無 | 有效果篩選時改顯示符合的效果 | 裝備 | `eqEffHit` | N/A | N/A | 無 | P2 | 不處理 | tests/smoke.py:214 |
| panel.equip.header | 全樓層 | 裝備面板 | `#pBody` | div.phead | `#pBody .phead` | equipDetail0 2264-2269 | 重建 | 共用 | 無 | N/A | 裝備 | `eslot(e)`（2112：`GICON[e.gen]`→`GICON[e.name]`→…）、`dn`／`dnSub`（2086-2088）、`zhE`（2084） | 圖示表和中文名都依 `gen`（英文名）或 `e\|oid` | 2 物品引用遷移 | B-R3（同 `gen` 共用圖示） | P1 | 補識別 `data-sec` | CODE |
| panel.equip.stats | 全樓層 | 裝備面板 | `#pBody` | dl.stats | `#pBody dl.stats` | equipDetail0 2265、2271 | 重建 | 共用 | 無 | N/A | 裝備 | `statVal`、`effIc`（STATIC 圖示） | N/A | N/A | 無 | P2 | 不處理 | CODE |
| panel.equip.patch-note | 全樓層 | 裝備面板 | `#pBody` | div.note.warn | `#pBody .note.warn`（無專屬 hook） | patchNote 2262；呼叫 2272 | 重建 | 共用 | 無 | `e.patch` 有值才出現 | 裝備 | `EVT.eqPatch.items[oid]`（官網 oid） | 官網 oid 穩定 | N/A | 無 | P2 | 不處理 | CODE |
| panel.equip.gst-note | 全樓層 | 裝備面板 | `#pBody` | div.note | `#pBody .note`（以文字「🎮」開頭辨認） | gstNote 2260-2261；呼叫 2272 | 重建 | 共用 | 無 | `e.gst`／`e.gstLv` | 裝備 | `GST.items[oid]`（gamestats.js，官網 oid） | `x<N>` 沒有 gamestats（EQX 數值寫在 data.js ITEMS） | N/A | 無 | P2 | 不處理 | CODE |
| panel.equip.set | 全樓層 | 裝備面板 | `#pBody` | h3＋table.settbl＋成員 linkbtn | `#pBody table.settbl`、成員 `#pBody button.linkbtn[data-go]` | setPotHTML 2400-2404；呼叫 2272 | 重建 | 共用 | 成員連到本站頁面（push） | N/A | 套裝、裝備 | `SET_BY[norm(英文成員名)]`；成員連結 `enGo(名稱)`（2397：`gen`→`PR.gen`→ITEMS key→**`r\|<配方序號>`**→法文名） | 成員是名稱，遷移時 sets.js 要改 ID；`enGo` 會回傳 `r\|N` | 2 物品引用遷移 | B-R3（同 `gen` 時 `enGo` 取第一件） | P1 | 補識別：成員改 ID | VERIFIED：1469 面板 h3「套裝效果・下級狼套裝」、2 個 `e\|` 連結 |
| panel.equip.obtain | 全樓層 | 裝備面板 | `#pBody` | 多段 h3＋ul.glist／ul.rows | `#pBody ul.glist`、`#pBody ul.rows button[data-go]` | equipDetail0 2273；itemObtainHTML 1291-1306；giHTML 2072 | 重建 | 共用 | 掉落怪物 `m\|`、採集點 `s\|`、任務 `t\|`（push） | N/A | 物品、怪物、地點、任務 | 有本站物品時 `en=e.itemId\|\|FR2ID[e.name]`；`GI_OID[e.oid]`／`GI_EN[norm(e.gen)]`／`GI_SITE[ITEMS key]` | gameinfo.js 用官網 oid＋英文名＋`site`（ITEMS key） | 2 物品引用遷移 | B-R5 | P1 | 補識別 `data-sec` | VERIFIED：全部裝備面板 data-go `m` 29、`s` 11、`i` 7 |
| panel.equip.dungeon-chest | 全樓層 | 裝備面板 | `#pBody` | h3＋ul.rows | `#pBody button.lrow[data-go^="s\|"]`（在「地下城寶箱」下） | dgSrcHTML 1354-1358 | 重建（DG_SRC 快取一次） | 共用 | 開地下城面板 | N/A | 地點 | 反查 `sp.dg.loot` 的**物品名稱**→`matRef`→`go` | 寶箱清單是名稱，遷移要改 ID | 2 物品引用遷移 | 無 | P1 | 保留 | VERIFIED：11 個裝備面板有「地下城寶箱」 |
| panel.equip.gacha | 全樓層 | 裝備面板 | `#pBody` | h3＋ul.glist | `#pBody ul.glist`（「轉蛋」下） | gachaHTML 2077-2080 | 重建 | 共用 | 無 | N/A | 道具、裝備 | `x.id`（`e\|oid`／`p\|oid`）或英文名 | gacha.js 用 `p\|1696` 這種鍵 | 2 物品引用遷移 | 無 | P2 | 不處理 | CODE |
| panel.equip.how | 全樓層 | 裝備面板 | `#pBody` | h3（`howTitle`：製作方式／NPC 販售／製作或購買）＋ul.rows.recipes＋div.gobtns | NPC 列 `#pBody ul.recipes button.lrow[data-go="n\|n<f>_<i>"]`；查看配方 `#pBody .gobtns button[data-goview="recipes\|r\|<N>"]` | equipDetail0 2274；recipeTable(rows,true) 1703-1707；recGoBtns 1701-1702 | 重建 | 共用；按鈕開中間彈出視窗（不換分頁） | NPC → push；查看配方 → `gvOpen("r",N)` | N/A | 配方、NPC | `RECIPE_BY_EQ[e.oid]`（1679，官網 oid 或 `x`／`g` 由 2096、2302 補）；NPC `npcByName(r.f,r.npc)`（1681，**名稱、取第一個**）；配方序號 `ALLREC.findIndex(npc 和 en 相同)`（**沒比樓層**） | `r\|N`、`n\|n<f>_<i>` 都是流水號 | 2 物品引用遷移（配方序號）／後續（NPC） | B-R1、B-R2、B-R3 | P0 | 補識別：配方和 NPC 改永久 ID；findIndex 加樓層 | VERIFIED：全部裝備面板 `n\|` 190 個；1627 面板 `n\|n1_29` 出現 2 次；tests/smoke.py:557-565 |
| panel.equip.sources | 全樓層 | 裝備面板 | `#pBody` | div.note.srcn | `#pBody .srcn.srcend` | equipDetail0 2276 | 重建 | 共用但版面不同 | 無 | N/A | N/A | 官網 oid 文字 | N/A | N/A | 無 | P2 | 保留 | CODE |

### 這一區的風險
- B-R1（`x<N>`、`r\|N`、`n\|…` 流水號）、B-R2（查看配方沒比樓層）、B-R3（同 `gen` 的裝備共用圖示和連結）、B-R6（效果清單的清除鈕）、B-R8（240 件上限）、B-R9（名稱排序用法文）。
- 檢查了：751 個裝備面板全部能打開（VERIFIED，`bad:0`）；效果清單由 smoke 測（tests/smoke.py:209-226）。

---

## 3. 道具 `#view-props`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| props.view.container | 全樓層 | 道具 | `body` | section.view.browse | `#view-props` | src/index.html:827 | 靜態 | 共用 | show() | `hidden` | 道具 | `#f<N>-props` | N/A | N/A | 無 | P0 | 保留 | tests/fixed_links.json `route:#f1-props` |
| props.list.header | 全樓層 | 道具 | `.results` | div.rhead＋`#cPr` | `#cPr` | HTML 837；件數 2334 | 靜態（件數動態） | 共用 | 無 | 「N / M 件」 | 道具 | `PRV()`（2308，PR 去掉材料和採集） | N/A | N/A | 無 | P2 | 保留 | VERIFIED：`256 / 304 件` |
| props.filter.group | 全樓層 | 道具 | `.topf` | chips | `#fPrGroup .chip[data-v="all"\|"消耗品"\|"符文・強化"\|"工具"\|"鑰匙"\|"活動"]` | HTML 829；chipsInto 2322 | 動態 | 共用但版面不同 | 設 `prGroup`＋fillPrSub | `prGroup` | 道具 | `PR_GROUP[e.cat]`（2310）；**值是中文顯示名** | N/A | N/A | B-R6 | P1 | 改名：值改代碼 | VERIFIED topf |
| props.filter.sub | 全樓層 | 道具 | `.topf` | fgroup＋chips（`.cn`） | `#gPrSub`、`#fPrSub .chip[data-v="<中文細分名>"]` | HTML 830；fillPrSub 2320-2321；件數 2329 | 重建（換分類時） | 共用但版面不同 | 設 `prSubV`＋fillPrSub2 | `#gPrSub[hidden]` 分類全部或只有 1 種時 | 道具 | `PR_SUBLAB(e.cat)`（2317）；值是中文（例如「聖誕節（2025）」） | N/A | N/A | B-R6 | P1 | 改名：值改代碼 | CODE |
| props.filter.sub2 | 全樓層 | 道具 | `.topf` | fgroup＋chips | `#gPrSub2`、`#fPrSub2 .chip[data-v="tool_pick"\|"tool_axe"\|"tool_hoe"]` | HTML 831；fillPrSub2 2318-2319；件數 2330 | 重建 | 共用但版面不同 | 設 `prSub2` | 細分不是「採集」時 hidden | 道具 | `e.cat`（依法文名正則改寫的類別，2303-2305） | N/A | N/A | 無 | P1 | 保留 | CODE |
| props.filter.floor | 全樓層 | 道具 | `.filters` | chips（`data-def="here"`） | `#fPrFl .chip[data-v="here"\|"only"\|"all"]` | HTML 832；chipsInto 2323；flOk 2141 | 動態 | 共用 | 設 `prFl` | 預設 `here` | 道具 | 同 equip.filter.floor（objFloors 用 `e.oid`） | 同上 | 2 物品引用遷移 | 無 | P1 | 保留 | CODE |
| props.filter.rarity | 全樓層 | 道具 | `.filters` | chips | `#fPrRar .chip[data-v="c"…"splus"]` | HTML 833；chipsInto 2324 | 動態 | 共用 | 設 `prRar` | `prRar` | 道具 | `rarK(e.r)` | N/A | N/A | 無 | P1 | 保留 | CODE |
| props.sort | 全樓層 | 道具 | `.rsel` | select | `#fPrSort`（name／rar／lv） | HTML 834-835；排序 2332-2333 | 靜態 | 共用但版面不同 | renderProps | 值 | 道具 | `name` 用法文 `e.name` | N/A | N/A | B-R9 | P1 | 保留（待決定） | CODE |
| props.search | 全樓層 | 道具 | `#q` | 行為 | `#q` | prHit 2326 | N/A | 共用 | 比對法文、`gen`、中文、zhS、舊名、`FR2ID`、類別、說明 | N/A | 道具 | `zhE(e)`、`zhS(e)` | 同裝備 | 2 物品引用遷移 | 無 | P1 | 保留 | CODE |
| props.list.container | 全樓層 | 道具 | `.results` | div.grid | `#lPr` | HTML 837；renderProps 2327-2339 | 重建 | 共用 | bindGo 2339 | 只畫前 240 件（2334） | 道具 | `PRV()` | N/A | N/A | B-R8 | P1 | 保留 | VERIFIED：240 張 |
| props.list.card | 全樓層 | 道具 | `#lPr` | button.card | `#lPr .card[data-key="p\|<oid>"]` | renderProps 2335-2337 | 重建 | 共用 | openP("p",oid)；材料類 `redirP` 轉成 `i` | `.sel` | 道具 | `prById[oid]`（2279）；oid＝官網數字或 `g<N>`（sets.js 消耗品，2296-2302） | `g<N>` 是**依 sets.js potions 順序、跳過已有 `gen` 的流水號** | 2 物品引用遷移 | B-R1 | P2 | 補識別：`g<N>` 改永久 ID | VERIFIED：無重複，樣本 `p\|2077`；fixed_links **沒有任何 `p\|g*`**（panels.json 有 31 個） |
| panel.prop.header | 全樓層 | 道具面板 | `#pBody` | div.phead | `#pBody .phead` | propDetail0 2411-2412 | 重建 | 共用 | 無 | N/A | 道具 | `pslot(e)`（2312：`OID_RECIC[oid]`→`GICON[e.gen]`→`FR2ID` 的 ITEMS 圖示）、`dn`、`dnSub`、`potZhE` | 圖示依 oid／英文名 | 2 物品引用遷移 | B-R5 | P1 | 補識別 `data-sec` | CODE |
| panel.prop.effects | 全樓層 | 道具面板 | `#pBody` | h3「遊戲寫的效果」＋ul.gieff | `#pBody ul.gieff` | setPotHTML 2400-2401；propDetail0 2413 | 重建 | 共用 | 無 | 有遊戲效果時隱藏官網數值（potGame 2408） | 道具 | `POT_BY[norm(e.gen 或 FR2ID 名)]`（英文名鍵） | 名稱鍵 | 2 物品引用遷移 | 無 | P2 | 不處理 | VERIFIED：63 個道具面板有這段 |
| panel.prop.obtain | 全樓層 | 道具面板 | `#pBody` | 同 panel.equip.obtain | `#pBody ul.rows button[data-go]` | propDetail0 2414；itemObtainHTML 1291 | 重建 | 共用 | push | N/A | 物品、怪物、地點、任務 | `en=FR2ID[e.name]`（**法文名→ITEMS key**）；`GI_OID`／`GI_EN` | 名稱橋接是主要過渡查找 | 2 物品引用遷移／過渡查找清理 | B-R5 | P1 | 補識別 | VERIFIED：道具面板 data-go `m` 316、`t` 65、`s` 17 |
| panel.prop.dungeon-chest | 全樓層 | 道具面板 | `#pBody` | 同裝備 | `#pBody button[data-go^="s\|"]` | dgSrcHTML 1354；propDetail0 2414 | 重建 | 共用 | 開地下城面板 | N/A | 地點 | 寶箱物品名稱 | 同裝備 | 2 物品引用遷移 | 無 | P1 | 保留 | VERIFIED：8 個面板 |
| panel.prop.gacha | 全樓層 | 道具面板 | `#pBody` | ul.glist | `#pBody ul.glist` | gachaHTML 2077；propDetail0 2414 | 重建 | 共用 | 無 | N/A | 道具 | `p\|oid`／英文名 | 同裝備 | 2 物品引用遷移 | 無 | P2 | 不處理 | VERIFIED：6 個面板 |
| panel.prop.how | 全樓層 | 道具面板 | `#pBody` | 同 panel.equip.how | `#pBody ul.recipes button[data-go="n\|…"]`、`#pBody .gobtns button[data-goview="recipes\|r\|<N>"]` | propDetail0 2415；recipeTable 1703；recGoBtns 1701 | 重建 | 共用 | 同上 | N/A | 配方、NPC | `RECIPE_BY_EQ[oid]` | 同上 | 2 物品引用遷移 | B-R1、B-R2 | P0 | 同 panel.equip.how | VERIFIED：1830 面板有 `n\|` 和 `GV:recipes` |
| panel.prop.sources | 全樓層 | 道具面板 | `#pBody` | div.note.srcn | `#pBody .srcn.srcend` | propDetail0 2416 | 重建 | 共用但版面不同 | 無 | N/A | N/A | N/A | N/A | N/A | 無 | P2 | 保留 | CODE |

### 這一區的風險
- B-R1（`g<N>`，而且固定連結清單沒有涵蓋）、B-R2、B-R6（分類值是中文）、B-R8、B-R9。
- 催化器（法師／薩滿副手）在 props.js 但放進裝備 `EQ`（2031，`ps:1`）：連結是 `e\|<oid>`，zhnames 的鍵卻是 `p\|<oid>`（zhE 2084 依 `ps` 切換），`prById` 沒有它們。見 B-R7。
- 檢查了：723 個道具面板全部能打開（VERIFIED）；13 個面板同一連結出現兩次（例如 1838 的 `t\|hanaka`、`p\|2464`）。

---

## 4. 素材 `#view-items`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| items.view.container | 全樓層 | 素材（view 名 `items`） | `body` | section.view.browse | `#view-items` | src/index.html:772 | 靜態 | 共用 | show() | `hidden` | 物品 | `#f<N>-items` | N/A | N/A | B-R7（view 名 `items` 但內容只有素材） | P0 | 保留（網址不改） | tests/fixed_links.json `route:#f1-items` |
| items.list.header | 全樓層 | 素材 | `.results` | div.rhead＋`#cItem` | `#cItem` | HTML 784；件數 1543 | 靜態（件數動態） | 共用 | 無 | 「N / M 件」 | 物品 | `matPool` | N/A | N/A | 無 | P2 | 保留 | VERIFIED：`430 / 430 件` |
| items.filter.group | 全樓層 | 素材 | `.topf` | chips | `#fItemGroup .chip[data-v="all"\|"怪物掉落物"\|"材料"\|"作物"\|"礦物"\|"木材"\|"漁獲"\|"官網未收錄"]` | HTML 774；GROUPS 1519；chipsInto 1522；沒東西的分類隱藏 1531 | 動態（`hidden` 每次 render 更新） | 共用但版面不同 | 設 `itemGroup` | `itemGroup`；空的分類 `hidden` | 物品、道具（材料） | `matGroup`（1520）：`SOURCES[id]` 有掉落＝怪物掉落物；`offOf(id).e.cat`；**值是中文顯示名** | N/A | N/A | B-R6 | P1 | 改名：值改代碼 | VERIFIED topf |
| items.filter.rarity | 全樓層 | 素材 | `.filters` | chips | `#fItemRar .chip[data-v="c"…"splus"]` | HTML 775；chipsInto 1523 | 動態 | 共用 | 設 `itemRar` | `itemRar` | 物品 | `rarK(ITEMS[id].r 或 e.r)` | N/A | N/A | 無 | P1 | 保留 | CODE |
| items.filter.quest | 全樓層 | 素材 | `.filters` | checkbox | `#fItemQuest` | HTML 777；onchange 1524 | 靜態 | 共用 | renderItems | checked | 任務 | `USES[id]` | N/A | N/A | 無 | P1 | 保留（BRIEF 沒列，程式有） | CODE |
| items.filter.drop | 全樓層 | 素材 | `.filters` | checkbox | `#fItemDrop` | HTML 778；onchange 1524 | 靜態 | 共用 | renderItems | checked | 怪物 | `SOURCES[id]` | N/A | N/A | 無 | P1 | 保留（BRIEF 沒列，程式有） | CODE |
| items.filter.floor-only | 全樓層 | 素材 | `.filters` | checkbox | `#fItemAll` | HTML 779；onchange 1524；`all=!checked` 1529 | 靜態 | 共用 | renderItems（`matPool(FL,true)`） | checked＝只看這一層 | 物品 | `itemFloors(id)`（1041） | N/A | N/A | B-R7（id 叫 All、勾了反而縮小） | P1 | 改名（id 和變數名相反；改 id 要同步 smoke） | CODE；CLAUDE.md 寫明「id 沒改」 |
| items.sort | 全樓層 | 素材 | `.rsel` | select | `#fItemSort`（name／rar／src／need） | HTML 780-781；排序 1535-1536；「怪物掉落物」時另依怪物分組 1537-1542 | 靜態 | 共用但版面不同 | renderItems | 值 | 物品、怪物 | `name` 用 ITEMS key（英文）或法文 `e.name`，顯示是中文 | N/A | N/A | B-R9 | P1 | 保留（待決定） | CODE |
| items.note | 全樓層 | 素材 | `.filters` | div.note | `#view-items .filters>.note` | HTML 782 | 靜態 | 共用但版面不同（手機收進「ⓘ 說明」） | 無 | N/A | N/A | N/A | N/A | N/A | 無 | P2 | 保留 | CODE |
| items.search | 全樓層 | 素材 | `#q` | 行為 | `#q` | itemHit 1169；renderItems 1534 | N/A | 共用 | 本站物品：key、中文、法文、aka、類別；再比對掉落怪物英文名。官網材料：法文＋gen＋中文 | N/A | 物品、怪物 | `zhI(id)`（2085）、`ITEMS[id].aka`（ITEM_OLD 1019-1022） | 舊名搜尋依 `aka` | 過渡查找清理 | 無 | P1 | 保留 | tests/smoke.py:415 |
| items.list.container | 全樓層 | 素材 | `.results` | div.grid | `#lItem` | HTML 784；renderItems 1528-1552 | 重建 | 共用 | bindGo 1551 | **只畫前 600 件**（1543） | 物品、道具 | `matPool(f,here)`（1526） | N/A | N/A | B-R8 | P1 | 保留 | VERIFIED：430 張（未達上限） |
| items.list.card | 全樓層 | 素材 | `#lItem` | button.card（兩種） | 本站：`#lItem .card[data-key="i\|<ITEMS key>"]`；官網材料：`#lItem .card[data-key="p\|<oid>"]` | renderItems 1545-1550 | 重建 | 共用 | openP；`p` 經 redirP 轉 `i`（如果有同法文名的本站物品） | `.sel` | 物品、道具 | **`i\|<英文名稱>`**（ITEMS key，會因改名變）；`p\|<官網 oid>`（穩定） | `i\|<名稱>` 改永久 ID | 2 物品引用遷移 | B-R1 | P2 | 補識別：值改 ID | VERIFIED：樣本 `i\|Acacia Log`；有撇號的 key 19 個（`data-key` 用 esc、markSel 用 CSS.escape，CODE 1239） |
| items.list.monster-heading | 全樓層 | 素材（分類「怪物掉落物」） | `#lItem` | div.npcgh（含 face） | `#lItem .npcgh` | renderItems 1545 | 重建 | 共用 | 無（不可點） | 只在 `itemGroup==="怪物掉落物"` | 怪物 | `SOURCES[id][0].m`（第一隻） | 無 data 屬性，無法知道是哪隻怪物 | 後續：NPC／地點／怪物／任務遷移 | B-R7（和 NPC 分頁區域標題同 class） | P2 | 補識別：加 `data-key="m\|<id>"` 或另一個 class | CODE |
| panel.item.header | 全樓層 | 素材面板 | `#pBody` | div.phead | `#pBody .phead` | itemDetail 1308-1311 | 重建 | 共用 | 無 | N/A | 物品 | `slot(id,64)`、`zhI(id)`、`itemFloors(id)` | 名稱鍵 | 2 物品引用遷移 | B-R5 | P1 | 補識別 | CODE |
| panel.item.stats | 全樓層 | 素材面板 | `#pBody` | dl.stats／table.settbl（各件數值、套裝） | `#pBody dl.stats`、`#pBody table.settbl` | itemDetail 1312-1321 | 重建 | 共用 | 無 | N/A | 物品、套裝 | `setPotHTML(id,...aka)` | 套裝名稱鍵 | 2 物品引用遷移 | 無 | P2 | 不處理 | VERIFIED：1 個面板有「各件數值」 |
| panel.item.obtain | 全樓層 | 素材面板（也被裝備、道具面板共用） | `#pBody` | h3「取得方式」＋ul.rows | 怪物 `#pBody button.lrow[data-go="m\|<id>"]`；採集點 `#pBody button.lrow[data-go="s\|<id>"]` | itemObtainHTML 1291-1306（掉落列 1295、採集 1296） | 重建 | 共用 | push | N/A | 怪物、地點 | `SOURCES[id]`（1036-1038，依**物品名稱**彙整 `m.drops`）、`GATHER[id]`（`sp.items` 名稱）、`GI_SITE[id]`／`GI_OID[offOf(id).e.oid]` | 掉落和採集點用物品名稱 | 2 物品引用遷移 | B-R5 | P1 | 補識別 | VERIFIED：素材面板 data-go `m` 377 |
| panel.item.obtain-map | 全樓層（有地圖的樓層） | 素材面板 | `#pBody` | svg.qmap（routeMini）＋button.btn | `#pBody .qmap`、`#pBody button[data-imap="<ITEMS key>"]` | itemMap 1286-1290；itemObtainHTML 1301；renderP 1229 | 重建 | 共用但版面不同（≤820px 按鈕隱藏、小地圖全寬） | 浮動路線視窗 | N/A | 怪物、地點 | `data-imap` 值是 **ITEMS key（名稱）** | 改 ID | 2 物品引用遷移 | 無 | P1 | 補識別：值改 ID | VERIFIED：Wolf Fur 面板有 `data-imap`、`data-xz` |
| panel.item.uses | 全樓層 | 素材面板 | `#pBody` | h3「用途」＋ul.rows | `#pBody button.lrow[data-go="t\|<town id>"]` | itemObtainHTML 1299、1302-1303 | 重建 | 共用 | **開城鎮面板**（列的是任務） | N/A | 任務、城鎮 | `USES[id]`（任務 need 的物品名稱） | 同 panel.monster.quests | 後續：NPC／地點／怪物／任務遷移 | B-R7 | P1 | 改連結：任務列連到任務 | VERIFIED：素材面板 `t` 70 個 |
| panel.item.crafts | 全樓層 | 素材面板 | `#pBody` | h3「可以拿去製作」＋ul.rows.recipes | `#pBody ul.recipes button.lrow[data-go="e\|…"\|"p\|…"\|"r\|<N>"]` | itemObtainHTML 1304；recipeTable(rows,false) 1703-1706 | 重建 | 共用 | 開裝備／道具面板，沒對到時開配方 `r\|N`（跨分頁） | N/A | 配方、裝備、道具 | `RECIPE_BY_MAT[ITEMS key]`（1679）；`eqById[r.oid]`／`prById[r.oid]`；`ALLREC.findIndex`（**沒比樓層**） | 材料鍵是名稱；配方序號是流水號 | 2 物品引用遷移 | B-R1、B-R2 | P0 | 補識別 | VERIFIED：素材面板 `e` 330、`p` 104、`r` 86 |
| panel.item.sources | 全樓層 | 素材面板 | `#pBody` | div.note.warn＋srcn | `#pBody .note.warn`（最後的配方提示） | itemDetail 1326 | 重建 | 共用 | 無 | N/A | N/A | N/A | N/A | N/A | 無 | P2 | 保留 | CODE |

### 這一區的風險
- B-R1（`i\|<名稱>`）、B-R2、B-R6（分類值是中文）、B-R7（`fItemAll` 名稱相反、`.npcgh` 兩種用途、用途列連到城鎮）、B-R8（600 件上限）、B-R9。
- 檢查了：263 個本站素材面板全部能打開（VERIFIED）；13 個面板有重複連結。ITEMS 的法文名沒有重複（VERIFIED `itemsFrDup:[]`），所以 `FR2ID`／`offOf` 目前沒有碰撞。

---

## 5. NPC `#view-npcs`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| npcs.view.container | 全樓層 | NPC | `body` | section.view.browse | `#view-npcs` | src/index.html:787 | 靜態 | 共用 | show() | `hidden` | NPC | `#f<N>-npcs` | N/A | N/A | 無 | P0 | 保留 | tests/fixed_links.json `route:#f1-npcs` |
| npcs.list.header | 全樓層 | NPC | `.results` | div.rhead＋`#cNpc` | `#cNpc` | HTML 793；件數 1575 | 靜態（件數動態） | 共用 | 無 | 「N / M 位」 | NPC | `NPCS(FL)` | N/A | N/A | 無 | P2 | 保留 | VERIFIED：`82 / 82 位` |
| npcs.filter.group | 全樓層 | NPC | `.filters`（**桌面也留在左欄**，不在 TOPF） | chips | `#fNpcGrp .chip[data-v="all"\|"potion"\|"loot"\|"key"\|"acc"\|"gear"\|"mat"\|"tool"\|"travel"\|"beggar"\|"other"]` | HTML 789；chipsInto 1561；空的組隱藏 1573 | 動態 | 共用 | 設 `npcGrpSel` | `npcGrpSel` | NPC | `npcGrp(n.c)`（1072，NGRP） | N/A | N/A | 無 | P1 | 保留 | VERIFIED：1280px NPC 分頁沒有 topf |
| npcs.filter.area | 全樓層 | NPC | `.rsel` | select | `#fNpcArea`；值＝最近城鎮／地點的**英文名 `b.n`**、`~wild`、`~nopos` | HTML 790；fillNpcArea 1558-1560（setFloor 3597 呼叫）；onchange 1562 | 重建（換樓層） | 共用但版面不同 | renderNpcs | 值；換樓層時找不到就回 `all` | NPC、城鎮、地點 | `npcRegion(n)`（1555：400 格內最近的城鎮或 tp／poi 地點，依距離） | 值是地點名稱，地點遷移時要換 | 後續：NPC／地點／怪物／任務遷移 | 無 | P1 | 補識別：值改地點 ID | tests/smoke.py:382-387 |
| npcs.search | 全樓層 | NPC | `#q` | 行為 | `#q` | npcCardHit 1570 | N/A | 共用 | 比對 key、中文 npcN、英文 npcEn、組名、區域名、回收物品英文和中文 | N/A | NPC、物品 | `BB.items[n.n]`（**NPC 名稱鍵**）、`bbGo` | 回收清單用 NPC 名稱和物品英文名 | 後續（NPC）＋2（物品） | 無 | P1 | 保留 | CODE |
| npcs.list.container | 全樓層 | NPC | `.results` | div.grid | `#lNpc` | HTML 793；renderNpcs 1571-1582 | 重建 | 共用 | bindGo 1581 | N/A | NPC | `NPCS(FL)` | N/A | N/A | 無 | P1 | 保留 | VERIFIED：82 張 |
| npcs.list.area-heading | 全樓層 | NPC | `#lNpc` | h3.npcgh | `#lNpc .npcgh` | renderNpcs 1578 | 重建 | 共用 | 無 | N/A | 地點 | `npcRegion` | 無 data 屬性 | 後續：NPC／地點／怪物／任務遷移 | B-R7 | P2 | 補識別：`data-area="<值>"` | tests/smoke.py:382 |
| npcs.list.card | 全樓層 | NPC | `#lNpc` | button.card | `#lNpc .card[data-key="n\|n<f>_<i>"]` | renderNpcs 1578-1580 | 重建 | 共用 | openP("n",id) | `.sel` | NPC、配方、回收 | `npcById(id)`（1075：從 id 取樓層，再 `NPCS(f).find`）；id＝`"n"+樓層+"_"+SAO_NPCS[f] 陣列序號`（1074）；回報新增的 NPC 接在最後（964） | **流水號**：`build_npcs.py` 重產 npcs.js、DROP 名單變動，id 就移位 | 後續：NPC／地點／怪物／任務遷移 | B-R1 | P2 | 補識別：改永久 ID | VERIFIED：樣本 `n\|n1_13`；fixed_links `n\|n*` 96 條 |
| panel.npc.header | 全樓層 | NPC 面板 | `#pBody` | div.phead | `#pBody .phead` | npcDetail 1980-1982 | 重建 | 共用 | 無 | N/A | NPC | `npcN`／`npcEn`（1099-1100，`ZNPC[名稱]`、`ZNPCEN[名稱]`） | 中文名用 NPC 名稱鍵 | 後續 | B-R5 | P1 | 補識別 | CODE |
| panel.npc.map-link | 全樓層 | NPC 面板 | `#pBody` | button.linkbtn | `#pBody button[data-rep="<f>\|<x>\|<z>"]` | npcDetail 1984 | 重建 | 共用；手機切到地圖分頁 | 浮動地圖 | 沒位置時改成說明 | NPC | 座標 | N/A | N/A | 無 | P1 | 保留 | VERIFIED：n1_0 面板有 `data-rep` |
| panel.npc.crafts | 全樓層 | NPC 面板 | `#pBody` | h3「可以製作」＋ul.rows.recipes | `#pBody ul.recipes button.lrow[data-go="e\|…"\|"p\|…"\|"r\|<N>"]` | npcDetail 1985；recipeTable(mk) 1703-1706 | 重建 | 共用 | 開裝備／道具／配方（跨分頁） | N/A | 配方、裝備、道具 | `RCP(n.floor,n.n)`（1667：鍵＝第 1 層 NPC 名稱或「樓層\|名稱」）；`recRow` 沒有 `.i`，所以 `ri=ALLREC.findIndex(npc、en 相同)`（1704，**沒比樓層**） | 配方鍵用 NPC 名稱；連結是流水號 | 2 物品引用遷移 | B-R1、B-R2、B-R3 | P0 | 補識別；findIndex 加樓層或改 `r.i` | **VERIFIED 錯連**：第 3 層煉金術士 `n\|n3_0` 的 `r\|4`、`r\|5`、`r\|7`、`r\|8` 打開是 F1 起始之鎮煉金術士的配方 |
| panel.npc.shop | 全樓層 | NPC 面板 | `#pBody` | h3「販售」＋ul.rows.recipes | 同上 | npcDetail 1985；isShop 1738 | 重建 | 共用 | 同上 | N/A | 配方 | `isShop`：`npcByName(r.f,r.npc)` 的類別在 SHOP_CATS | 同上 | 2 物品引用遷移 | B-R2、B-R3 | P1 | 同上 | VERIFIED：n1_0 面板有「販售 9」 |
| panel.npc.buyback | 全樓層（目前資料只有第 1 層） | NPC 面板 | `#pBody` | h3「回收物品」＋ul.rows.bbl | `#pBody ul.bbl button.lrow[data-go]`（沒對到的是 `div.lrow`） | buybackHTML 1567-1569；bbGo 1563；bbName 1564；bbIcon 1565-1566 | 重建 | 共用 | 開物品／裝備／道具（跨分頁） | N/A | 物品、裝備、道具 | `BB.items[n.n]`（**NPC 名稱鍵**）；物品 `bbGo(英文名)`＝`ikey`→`i\|<key>`，否則 `enGo`（可能回 `r\|N`） | NPC 名稱和物品英文名都要遷移 | 2 物品引用遷移＋後續（NPC） | B-R3 | P1 | 補識別 | VERIFIED：16 個 NPC 面板有「回收物品」；tests/smoke.py:388 |
| panel.npc.note | 第 1 層 | NPC 面板 | `#pBody` | h3＋div.note（回收表、位置、補貨） | `#pBody .note`；回收表 `#pBody ul.rows button.lrow[data-go]` | NPC_NOTE 1715-1735；recyTable 1708-1711；npcDetail 1990（`n.floor===1&&NPC_NOTE[n.n]`） | 重建（getter 每次產生） | 共用 | 回收表物品連結 | N/A | NPC、物品 | **NPC 名稱鍵**；物品 `matRef(英文名)`（1694） | 同上 | 後續（NPC）＋2（物品） | B-R3 | P2 | 保留 | VERIFIED：位置 13、補貨 5、回收 2 個面板 |
| panel.npc.sources | 全樓層 | NPC 面板 | `#pBody` | div.note.srcn | `#pBody .srcn.srcend` | npcDetail 1992；npcCalcNote 1073（`SAO_NPC_CALC` 鍵：第 1 層名稱、其他「樓層\|名稱」） | 重建 | 共用但版面不同 | 回報連結 `data-repgo` | N/A | NPC | 名稱鍵 | 同上 | 後續 | 無 | P2 | 保留 | CODE |

### 這一區的風險
- B-R1（`n<f>_<i>`）、B-R2（**已確認錯連**）、B-R3（NPC 名稱重複）、B-R7（`.npcgh`）。
- 檢查了：192 個 NPC 面板全部能打開（VERIFIED）；第 1 層有重名 NPC：Traveling Merchant ×8、Equipment Merchant ×2、Accessories Merchant ×2；第 3 層 Equipment Merchant ×2、Consumables Merchant ×2（VERIFIED）。`npcByName` 回傳第一個，`BB.items`／`NPC_NOTE`／`RCP`／`SAO_NPC_CALC` 以名稱共用一份。目前這幾類 NPC 沒有配方和回收資料，所以還沒有看得到的錯誤。

---


---

## 第 3 部分（分工 C）：地圖、任務、配方、地下城、職業、世界王

## 1. 地圖 `#view-map`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| map.view.section | 全樓層 | map | `main` | section | `#view-map` | src/index.html:721 | 靜態（`show()` 切 hidden） | 共用 | 路由 `#f{N}-map` 顯示 | hidden | N/A | `location.hash` 正則（src/index.html:3612） | N/A | N/A | 低 | P0 | 保留：路由入口，固定連結有 `route:#f1-map`、`#f2-map`、`#f3-map` | tests/fixed_links.json `route:#f1-map`；VERIFIED |
| map.view.stage | 全樓層 | map | `#view-map` | div（拖曳／滾輪／捏合） | `#stage` | src/index.html:722；事件 3290–3305 | 靜態；class `dgmode`／`dragging`／`edit` 動態 | 共用（手機用 `goMapThen` 捲到 stage） | 拖曳平移、滾輪縮放（`wheelF` 每畫格一次）、雙指縮放、校正模式點擊放置 | `sc`/`tx`/`ty`/`fitted`（3216） | N/A | `MP()`（3219）＝地下城模式時換成 jmmeta dg 框架 | N/A | N/A | 低 | P0 | 保留：主要容器 | CODE 3216–3305 |
| map.view.world | 全樓層 | map | `#stage` | div（transform 容器） | `#world` | src/index.html:723；`apply` 3278 | 靜態容器；子元素每次 `renderMap` 重建 | 共用（CSS 變數 `--inv`/`--tk`/`--areaw` 依縮放） | 承載所有標記 | `--inv` 等只在縮放變 12% 以上或停 120 ms 更新（`applyVars` 3281） | N/A | N/A | N/A | N/A | 低 | P0 | 保留；CLAUDE.md 規定不能加 `will-change:transform` | CODE 3278–3281 |
| map.base.image | 全樓層 | map | `#world` | img ×2 | `#mapImg`、`#mapLo` | src/index.html:723；renderMap 3388 起 | 動態（src、visibility、mask 由 renderMap 設） | 共用 | 先顯示 512px 預覽 `#mapLo`，主圖載完後藏 | `mapImg.dataset.f`＝樓層 | 樓層地圖 | `FLOORS[f].map.img/lo/jm` | N/A | N/A | 低 | P1 | 保留 | CODE renderMap（`mapImg.src.endsWith(want)` 那段） |
| map.overlay.no-map | 全樓層（目前沒有樓層用到：第 1～3 層都有 map） | map | `#stage` | div | `#noMap` | src/index.html:724；renderMap 3389 | 靜態，hidden 由 renderMap 設（`!!m`） | 共用 | 沒有地圖的樓層顯示說明，同時藏 world、縮放、HUD、圖例 | hidden | 樓層地圖 | `MP()` | N/A | N/A | 低 | P2 | 保留 | CODE renderMap 第 2 行 |
| map.base.tiles | 全樓層（第 3 層一律、第 1、2 層探索地圖時、地下城模式） | map | `#world` | div＋img 切片 | `#tiles`（`data-base`、`data-f`），子 img class `l0`/`l1`/`mid`/`hi` | src/index.html:723；`updateTiles` 3251 | 動態（`TL` Map 快取、GC 700 ms） | 共用 | 依縮放選 L0～L3，L1 整層常駐，畫面外一圈低優先預讀 | `tilesEl.dataset.base` 換底圖時清空 | 探索地圖切片 | `useTiles()`/`jmOn()`（3227–3228）、`JMV(f)`、jmmeta `layers`/`dg` | N/A | N/A | 低 | P1 | 保留 | CODE 3251–3276 |
| map.legend.base-button@f1-2 | 第 1、2 層（第 3 層 `jmAlways` 隱藏） | map | `.legend` | button | `#baseBtn` | src/index.html:730；click 3311 | 靜態；文字和 hidden 由 renderMap 設 | 共用 | 切換 wiki／探索地圖，存 localStorage `sao-map-base` | `BASE` | N/A | N/A | N/A | N/A | 低 | P1 | 保留 | VERIFIED（1280／390 都看得到） |
| map.legend.filter-button | 全樓層 | map | `.legend` | button | `#filterBtn`（`aria-controls=fpanel`） | src/index.html:729；click 3365；文字 3347 | 靜態；文字動態（「已隱藏 N 類」） | 手機專用（≥821px CSS 隱藏，src/index.html:329） | 開關 `#fpanel` | `aria-expanded` | N/A | N/A | N/A | N/A | 低 | P1 | 保留 | VERIFIED（桌面不可見、手機可見） |
| map.legend.dungeon-select@f1 | 第 1 層 | map | `.legend` | select | `#dgSel` | src/index.html:731；change 3313 | 靜態；renderMap 一律 `hidden=true` | 共用（永遠隱藏） | 原本切換地下城地圖 | N/A | 地下城地圖 | jmmeta dg id | N/A | 過渡查找清理 | 低 | P2 | 不處理或刪除：2026-11-08 起不再使用（「不用放地下城」），只剩事件 | CODE renderMap `$("dgSel").hidden=true` |
| map.legend.dungeon-back@f1 | 第 1 層（地下城模式） | map | `.legend` | button | `#dgBack` | src/index.html:731；click 3314；文字 renderMap | 靜態；hidden/文字動態 | 共用 | 離開地下城模式 `DGV=null` 並 `fit` | `DGV` | 地下城地圖 | `dgName(m.dg)` | N/A | N/A | 低 | P1 | 保留 | CODE；CLAUDE.md 說 jm_pack_test.py 有測（NOT RUN） |
| map.legend.layer-select@f1 | 第 1 層（只在地下城模式） | map | `.legend` | select | `#layerSel` | src/index.html:732；change 3312；選項 renderMap | 靜態；options 每次重建 | 共用 | 切換地下城高度 `DJL[DGV]` | `DJL` | 地下城地圖 | jmmeta `dg[id].layers` 的 key（`day`、`c<n>`） | N/A | N/A | 低 | P1 | 保留；CLAUDE.md 寫「高度選單 `#layerSel`（JML，localStorage `sao-map-layer`）」是舊說法，程式現在只在地下城模式出現、`JML` 只在 3235 宣告為 `day`、全檔沒有 `sao-map-layer` | CODE grep `JML=`（只有 3235）、`sao-map-layer`（0 筆）；renderMap `$("layerSel").hidden=true`；VERIFIED 一般模式隱藏 |
| map.filter.panel | 全樓層 | map | `#stage` | div[role=dialog] | `#fpanel`、`#fpCats`、`#fpAll`、`#fpX` | src/index.html:734–740；`renderFilter` 3346；`syncFilter` 3367 | `#fpCats` 每次重建（`data-k` chips） | 共用但版面不同：≥821px 一直展開在左側；≤820px 用 `#filterBtn` 開關 | 點 chip 切換 `FILT[k]`，存 `sao-map-filter-v5` | `FILT`（1081），預設 `FILT_DEF`（1080） | N/A | `MAPGRP`（1065）分類 key：tp/land/gather/npc/wboss/dungeon/area/boss/mini/mobs | N/A | N/A | 低 | P1 | 保留：chip 用 `data-k` 分類 key，不是資料名稱 | VERIFIED（桌面可見、手機隱藏） |
| map.filter.npc-groups | 全樓層 | map | `#fpanel` 或 `#fpFly` | details＋chips | `#fpNpcWrap`、`#fpNpcBody`、`#fpNpc [data-k="npc:<組>"]`、`#fpNpcAll`、`#fpNpcNone` | src/index.html:737；renderFilter 3351–3352；setNpcAll 3362 | 重建 | 共用但版面不同：桌面 `#fpNpcBody` 搬到 `#fpFly`（`syncNpcFly` 3356）；手機留在 `#fpNpcWrap` | 切換 NPC 功能組 | `FILT["npc:<組>"]` | NPC | `NGRP`／`npcGrp(n.c)`（npcs.js 類別 key） | N/A | N/A | 低 | P1 | 保留 | CODE；smoke.py:494 |
| map.filter.npc-flyout | 全樓層 | map | `#stage` | div[role=group] | `#fpFly` | src/index.html:741；`syncNpcFly` 3356 | 動態搬移 DOM | 桌面專用（NPC 篩選開著時） | 顯示 NPC 組 | hidden | NPC | 同上 | N/A | N/A | 低 | P2 | 保留 | VERIFIED（預設 NPC 關閉時隱藏） |
| map.overlay.note | 全樓層 | map | `#stage` | div | `#mapNote` | src/index.html:725；renderMap | 動態文字 | 共用但版面不同（≤820px 一行、點了展開，src/index.html:520–521） | 說明目前底圖／地下城 | hidden | 探索地圖 meta | jmmeta `"<f>"` 的 date/pct/log | N/A | N/A | 低 | P2 | 保留 | CODE renderMap |
| map.overlay.credit | 全樓層（有探索地圖時） | map | `#stage` | div | `#jmCredit`（`.r`、`.r.f`、`.r.o`） | src/index.html:726；renderMap；`jmCredits` 2647 | 重建 | 共用但版面不同（≤820px 收成一行，src/index.html:516–519；≥821px 左移到 220px，523） | 列貢獻比例 | hidden | 探索地圖 log | jmmeta `log[].by` → reports.js 暱稱 → `JM_OWNER`（2646） | N/A | N/A | 低 | P2 | 保留 | VERIFIED（wiki 底圖時隱藏） |
| map.overlay.search-hint | 全樓層 | map | `#stage` | div[role=status]＋button | `#srchHint`、`#srchTxt`、`#srchClr` | src/index.html:727；filterMap 3533 起；3547 | 動態 | 共用 | 搜尋時顯示符合數量、清除搜尋 | hidden | 城鎮／地點／怪物／NPC | `townHit`/`spotHit`/`monHit`/`npcHit` | N/A | N/A | 低 | P1 | 保留 | VERIFIED（「正在搜尋…」文字） |
| map.hud.coord | 全樓層 | map | `.hud` | span | `#coord` | src/index.html:743；pointermove 3297 | 動態文字 | 桌面專用（≤820px `.hud .coord{display:none}`，src/index.html:662） | 顯示游標座標 | N/A | N/A | `fromPx()` | N/A | N/A | 低 | P2 | 保留 | VERIFIED（桌面可見、手機隱藏） |
| map.zoom.buttons | 全樓層 | map | `#stage` | button ×3 | `.zoombtns #zin`、`#zout`、`#zfit` | src/index.html:745；3307–3309 | 靜態 | 共用 | 縮放／顯示全圖 | N/A | N/A | N/A | N/A | N/A | 低 | P1 | 補識別：外層 `.zoombtns` 沒有 id（renderMap 用 `document.querySelector(".zoombtns")`），可補 `id` 方便測試 | CODE renderMap 第 2 行 |
| map.overlay.route-bar | 全樓層 | map | `#stage` | div＋button | `#routeBar`、`#routeName`、`#routeX` | src/index.html:744；`drawRoute`/`showRoute`/`clearRoute` 3512–3527 | 動態 | 共用 | 原本在大地圖上畫主線路線 | `ROUTE` 一直是 null | 任務 | N/A | N/A | 過渡查找清理 | 低 | P2 | 不處理或刪除：`showRoute` 全檔只有定義（3523）、沒有呼叫者，所以 `ROUTE` 永遠是 null；`drawRoute()` 每次 renderMap（3445）都會呼叫但立刻 return；路線改用 `#rwin`；說明 `#qNoteMain` 還寫「按『在地圖上看路線』」 | CODE `grep -n 'showRoute\b'` 只有 3523、`ROUTE=` 只有 3512／3513／3523 |
| map.marker.town | 全樓層 | map | `#world` | button.town（`.tp`/`.land`） | `#world .town[data-t="<town.id>"]` | renderMap（src/index.html:3388 起，towns 迴圈） | 重建（每次 renderMap 全刪全畫） | 共用 | 點了 `openP("t",id,"new")` | `.shide`（搜尋不符）、`.under-tp`（declutter） | 城鎮 | `data-t`＝town id → `F().towns.find` | 低：id 已是資料檔字串；R0.6 若城鎮換永久 ID 要改 `data-t` 值 | 後續：NPC／地點／怪物／任務遷移 | 低 | P2 | 保留：定位 `#world .town[data-t]` | VERIFIED 第 1 層 8 個 |
| map.marker.spot | 全樓層 | map | `#world` | button.town（`.tp/.land/.gather/.wboss/.dungeon`）或 div.zone（`.mobarea/.poi/.under/.est`）＋button.zlabel | `#world .town[data-s="<spot.id>"]`、`#world .zone[data-s="<spot.id>"]` | renderMap spots 迴圈 | 重建 | 共用 | 點了 `openP("s",id,"new")` | `.shide`、`.moved`、`.flash`（focusSpot 3529） | 地點、怪物 | `data-s`＝spot id → `spotsOf(FL).find`；`zoneEls[id]` | 低：同上 | 後續 | 低 | P2 | 保留：定位 `#world [data-s]` | VERIFIED 35 個 |
| map.marker.area-outline | 全樓層 | map | `#world > svg.areas` | svg path | `.areas path[data-s="<spot.id>"]` | `drawAreas` 3381 | 重建 | 共用 | 不可點；搜尋時 `.shide` | N/A | 地點 | `data-s` | 低 | 後續 | 低 | P2 | 保留 | CODE 3381–3387 |
| map.marker.monster-thumb | 全樓層 | map | `.zone .thumbs`、`#zlist .zrow .thumbs` | button.th.mapth | `[data-id="<m.id>"][data-key="m\|<m.id>"]` | `mapThumb` 3372 | 重建 | 共用 | 點了開怪物面板；`markSel` 會加 `.selm` | `.dim`、`.hit`（filterMap） | 怪物 | `data-id`＝怪物索引 id → `monById` | **中**：`m<索引>` 是 data.js 陣列位置（見 C-R9） | 後續 | 中 | P2 | 保留定位；身份要隨怪物永久 ID 改 | VERIFIED 26 個 |
| map.marker.boss-spawn | 全樓層（第 1 層 data.js `BOSS_SPAWNS`；第 2、3 層 data23.js:105、275） | map | `#world` | button.bsp（`.ug`＝地下） | `#world .bsp[data-id][data-key="m\|<m.id>"]` | renderMap SPAWNS 迴圈；`SPAWNS` 1057 | 重建 | 共用 | 開怪物面板 | `.shide` | 怪物 | `BOSS_SPAWNS` 以**怪物名稱** → `monByName[n]` 對到怪物 | 中：重生點資料以名稱連怪物，怪物改名要同步 | 後續 | 中 | P2 | 保留；R0.6 把 `BOSS_SPAWNS` 第 0 欄改成怪物 ID | CODE 1057、data23.js:105、275；VERIFIED 預設篩選（首領、小首領關閉）時 0 個 |
| map.marker.npc | 全樓層 | map | `#world` | div.zone.poi.shop.npc＋button.zlabel | `#world .npc[data-n="n<f>_<i>"]` | renderMap NPCM 迴圈 | 重建 | 共用 | 開 NPC 面板 | `.shide`、`.hit` | NPC | `data-n`＝NPC 索引 id → `npcById`（1075，每次重算 `NPCS(f)`） | **高**：索引 id（見 C-R9）；沒有 `data-key`，NPC 面板開著時地圖標記不會亮 | 後續 | 中 | P2 | 補識別：加 `data-key="n\|…"`；身份改永久 ID | CODE；VERIFIED 預設 0 個、搜尋時出現 |
| map.marker.rpin | 全樓層 | map | `#world` | div.rpin | `#world .rpin` | `repPin` 3528 | 動態（一次一個） | 共用 | 標出點到的座標 | N/A | N/A | 座標 | N/A | N/A | 低 | P2 | 保留 | CODE |
| map.marker.declutter | 全樓層 | map | `#world` | 行為（改 label 的 left/top/visibility） | `.tname`、`.zlabel` 加 `.moved` | `declutter` 3449；`declutterSoon` | 動態 | 共用 | 名稱避讓 | `.under-tp` | N/A | N/A | N/A | N/A | 低 | P2 | 保留 | CODE 3449–3472 |
| map.side.list | 全樓層 | map | `.mapside` | div | `#zlist` | src/index.html:748；`renderZoneList0` 3478 | 重建 | 共用但版面不同（≤820px 分組預設收合，`zfoldSync` 3476） | 分組列出傳送點、地標、採集點、世界王、地下城、怪物區、首領、NPC、位置未知 | `ZOPEN` | 城鎮、地點、怪物、NPC | 見下兩列 | 低 | 後續 | **中**（見 C-R1） | P1 | 修正：列的搜尋比對要和地圖一致 | VERIFIED 31 列 5 組 |
| map.side.section | 全樓層 | map | `#zlist` | div.zsec | `#zlist .zsec[data-k="<標題文字>"]` | renderZoneList0 `sec()` | 重建 | 共用（手機可點展開） | 展開／收合 | `.zopen`、`aria-expanded` | N/A | `data-k`＝**顯示標題文字**（例如「🌀 傳送點－城鎮」） | N/A | N/A | 低 | P2 | 補識別：`data-k` 用顯示文字當 key，改字就丟掉使用者展開狀態；改成固定代碼 | CODE 3479 |
| map.side.row | 全樓層 | map | `#zlist` | div.zrow（`.npcrow`）＋button.zn＋button[data-x][data-z] | `#zlist .zrow[data-s]`（地點）、`.zrow[data-tp]`（城鎮／首領／NPC，值是**搜尋用文字**）、`.zrow[data-z]`（位置未知的區域 key） | renderZoneList0 3482–3505 | 重建 | 共用 | 點名稱：移地圖＋開面板；首領列的座標按鈕 `repPin` | `hidden`（filterMap） | 城鎮、地點、怪物、NPC | 城鎮／首領／NPC 列沒有身份屬性，只有 `data-tp` 英文名字串 | 中：城鎮／首領／NPC 列沒有 id，測試只能用文字找 | 後續 | 中 | P2 | 補識別：城鎮列加 `data-t`、首領列 `data-key="m\|…"`、NPC 列 `data-n` | CODE；smoke.py:458 用 `has_text` 找 NPC 列 |
| map.edit.calibration | 全樓層（`?edit`） | map | `.mapside .mapfoot`、`#stage` | buttons＋textarea＋div | `#editToggle`、`#exportBtn`、`#resetBtn`、`#exportBox`、`#editbar`、`.zrow .place` | src/index.html:742, 749–756；1049–1054；3548–3562 | 靜態＋動態 | 共用（沒有 `?edit` 時 `.mapfoot` 整個 hidden） | 站長把位置未知的區域放到地圖、匯出 JSON | `editing`、`placing`、`userPos`（localStorage `sao-f1-zone-pos`、`sao-f<N>-zone-pos`） | 地點（區域） | zone key（`F().zones[z]`）；匯出用區域**英文名**當 key | 低：匯出 JSON 用 `zones[z].n` 名稱，R0.6 可改成 zone key | 1.5 S15-B1 | 低 | P2 | 保留 | CODE；smoke.py:602–605 |
| map.dungeon-mode@f1 | 第 1 層 | map | `#stage`（`.dgmode`） | 模式 | `#stage.dgmode`；入口 `[data-dgmap="<dg id>"]` | `DGV` 3217；`MP` 3219；`dgFit` 3317；document capture click 3322 | 動態 | 共用（手機點入口時先 `closeP()`） | 從地下城面板「在地圖上看」進入，換成 jmmeta 地下城框架，藏篩選和第 1 層標記 | `DGV`、`DJL` | 地下城地圖 | `data-dgmap`＝jmmeta dg id（`xalzirith`/`geldorack`/`labyrinthe`/`kobold`），經 `DG_DIM`（2688）對 spot id | 低：dg id 來自 JourneyMap 資料夾名，不是遊戲名稱 | N/A | 低 | P1 | 保留 | CODE 3314；CLAUDE.md 說 jm_pack_test.py 有測（NOT RUN） |
| map.panel.under-button@f1 | 第 1 層 | map（面板內） | 城鎮／tp／poi 地點面板 `.maplinks` | button＋figure.underfig | `[data-under="<顯示名稱>"][data-ux][data-uz]` | `underBtn` 3247；document capture click 3326；`underCrop` 3335 | 動態 | 共用 | 在面板裡展開附近 320×320 格地下圖（blob JPEG），點圖放大 | `aria-expanded` | 城鎮、地點 | `data-under`＝**pN() 顯示名稱**，只拿來寫圖說；座標用 `data-ux/uz` | 低：名稱只做顯示 | N/A | 低 | P2 | 保留；建議 `URL.revokeObjectURL`（見 C-R6） | VERIFIED 起始之鎮面板有 `["起始之鎮","1700","4300"]` |
| map.base.tile-loader | 全樓層 | map | N/A | 行為 | N/A | `updateTiles` 3251、`schedTiles`、resize | 動態 | 共用 | N/A | N/A | 探索地圖 | N/A | N/A | N/A | 低 | P2 | 保留 | CODE |

### 這一區的風險

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

---

## 2. 任務 `#view-quests`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| quests.view.section | 全樓層 | quests | `main` | section.browse | `#view-quests` | src/index.html:797 | 靜態 | 共用 | 路由 `#f{N}-quests` | hidden | N/A | hash | N/A | N/A | 低 | P0 | 保留 | tests/fixed_links.json `route:#f1-quests` 等 3 條 |
| quests.filter.kind | 全樓層 | quests | `.filters` | chips | `#fQKind .chip[data-v="main"\|"side"]` | src/index.html:799；chipsInto 1587 | 動態（一次） | 共用（手機是第一組篩選，不收合） | 切換主線／支線 | `qKind`（預設 main，不存） | 任務 | N/A | N/A | N/A | 低 | P1 | 保留 | VERIFIED 主線 35 張、支線 51 張（第 1 層） |
| quests.filter.town | 全樓層（支線） | quests | `.filters` | chips | `#gQTown`、`#fQTown .chip[data-v="<town.id>"\|"all"]` | src/index.html:800；`fillTownChips` 2010（換樓層時重建，`qTown` 重設成 all） | 動態 | 共用（手機收進「更多篩選」） | 依城鎮篩選 | `qTown` | 城鎮、任務 | `data-v`＝town id；顯示 `pN(t)` | 低 | 後續 | 低 | P1 | 保留 | VERIFIED 9 個 chip |
| quests.filter.sort | 全樓層（支線） | quests | `.filters`（桌面搬到 `.rhead .rsel`） | select | `#gQSort`、`#fQSort`（town/xp/col） | src/index.html:801–802；change 2009 | 靜態 | 共用但版面不同（`placeTopFilters`） | 排序 | N/A | 任務 | N/A | N/A | N/A | 低 | P1 | 保留 | CODE |
| quests.filter.notes | 全樓層 | quests | `.filters` | div.note | `#qNoteMain`、`#qNoteSide` | src/index.html:803–804；renderQuests 2016 | 靜態，hidden 動態 | 共用（手機收進「ⓘ 說明」） | N/A | N/A | N/A | N/A | N/A | N/A | 低（見 C-R2） | P2 | 改字：拿掉「在地圖上看路線」 | CODE |
| quests.list.container | 全樓層 | quests | `.results` | div（flex 直列） | `#lQ`、`#hQ`、`#cQ` | src/index.html:806；`renderQuests` 2015、`renderMainQ` 2005 | 重建 | 共用 | N/A | N/A | 任務、城鎮 | `MQ(FL)`、`F().quests`、`mqHit`/`questHit` | N/A | 後續 | 低 | P1 | 保留 | VERIFIED |
| quests.list.main-card | 全樓層 | quests | `#lQ` | button.card.qcard | `#lQ [data-key="q\|mq<f>_<i>"]`（同值 `data-go`） | `mqCard` 2002 | 重建 | 共用 | 開任務面板 | `.sel` | 任務 | `questById("mq<f>_<i>")` → `MQ(f)[i]`（1590） | **高**：id 是 mainq.js 陣列索引（見 C-R9） | 後續：任務遷移 | 中 | P2 | 定位 `#lQ [data-key^="q\|mq"]`；身份改成永久任務 ID | VERIFIED `q\|mq1_0…` |
| quests.list.side-card | 全樓層 | quests | `#lQ .qtown` | button.card.qcard.qside | `#lQ [data-key="q\|q<i>"]`（第 1 層）／`[data-key="q\|f<f>q<i>"]`（第 2、3 層） | `qRow` 2012 | 重建 | 共用 | 開任務面板 | `.sel` | 任務、城鎮 | `ALLQ.find(id)` | **高**：兩種格式都是陣列索引（見 C-R9） | 後續 | 中 | P2 | 同上 | VERIFIED `q\|q2`、`q\|q14` |
| quests.list.town-heading | 全樓層（支線、依村鎮排序） | quests | `#lQ .qtown h3` | button | `#lQ .qtown h3 [data-go="t\|<town.id>"]` | renderQuests 2022 | 重建 | 共用 | 開城鎮面板 | N/A | 城鎮 | town id | 低 | 後續 | 低 | P2 | 保留 | VERIFIED 8 個 |
| panel.quest.body | 全樓層 | 任務面板（`#panel` 或 `gvOpen`） | `#pBody` | 面板內容 | `#pBody`（`stack` 最上層 type `q`） | `questDetail` 1990；renderP 1205 | 重建 | 共用；`body.panel-wide` | N/A | N/A | 任務、城鎮、NPC | `questById`；NPC 名稱用 `qNpc`（名稱→zhnames 顯示） | 中：主線的 NPC 用名稱字串、不是 NPC id | 後續 | 低 | P1 | 保留 | CODE |
| panel.quest.step-coord | 全樓層 | 任務面板 | `#pBody ol.mqs li` | button.linkbtn | `#pBody .mqs [data-rep="<f>\|<x>\|<z>"]` | questDetail 1995；renderP data-rep 1216–1226 | 重建 | 共用但版面不同：桌面不在地圖分頁時開 `#rwin` 並 `rwFocus`；手機在小地圖上標紅 `g.hl` | 移到那一步 | `.on` | 任務步驟座標 | 座標字串 | N/A（座標不是身份） | N/A | 低 | P2 | 保留 | smoke.py:283；CODE |
| panel.quest.route-mini | 全樓層 | 任務面板 | `#pBody` | div.qmap > svg | `#pBody .qmap svg g[data-xz="x,z …"]` | `routeMini` 1627；`clusterPts` 1619；`refMarks` 1623；`miniTiles` 1611 | 重建 | 共用 | 不能點（只標記） | `g.hl` | 任務步驟、城鎮、地點 | `data-xz`＝座標清單 | N/A | N/A | 低 | P2 | 保留 | smoke.py:178–180 |
| panel.quest.route-button | 全樓層 | 任務面板 | `#pBody` | button | `#pBody [data-route="<quest id>"]` | questDetail 2001；renderP 1229；gv 1465 | 重建 | 桌面專用（≤820px `[data-route],[data-imap]{display:none!important}`，src/index.html:175） | 開 `#rwin` 路線視窗 | N/A | 任務 | `questById(data-route)`；值＝`mq<f>_<i>` 等索引 id | 高（同 C-R9） | 後續 | 中 | P1 | 保留；身份隨任務 ID 改 | VERIFIED `["mq1_20"]` |
| floatmap.route-window | 全樓層 | 跨分頁 | `body` | div.rwin[role=dialog] | `#rwin`、`#rwHead`、`#rwTitle`、`#rwIn`、`#rwOut`、`#rwFit`、`#rwX`、`#rwBody`、`#rwSvg` | src/index.html:882；`openRouteWin` 1652；`rwRender` 1641；事件 1654–1664 | 靜態框；`#rwSvg` 內容重建 | 桌面專用（手機改用 `goMapThen`，1183） | 滾輪縮放、拖曳、拉大小、Esc 關 | `RW`（含 `view`，換分頁時關，3614） | 任務、怪物、物品、NPC 座標 | `RW.steps` 座標 | N/A | N/A | 低 | P0 | 保留：任務、物品取得地點、座標連結共用 | smoke.py:128–134, 258, 270, 283, 299 |
| panel.quest.town-link | 全樓層（支線） | 任務面板 | `#pBody .facts` | button | `[data-go="t\|<qq.town>"]` | questDetail 1992 | 重建 | 共用 | 開城鎮面板 | N/A | 城鎮 | town id | 低 | 後續 | 低 | P2 | 保留 | tests/fixed_links.json 有 8 條 `t\|` |
| panel.quest.images@f1 | 第 1 層（主線 27、32） | 任務面板 | `#pBody .stimg` | a[data-imgzoom] | `#pBody .stimg a[data-imgzoom]` | questDetail 1995；document click 2957 | 重建 | 共用 | 在本頁開看圖視窗 | N/A | 任務 | 圖片路徑 | N/A | N/A | 低 | P2 | 保留 | CODE |

### 這一區的風險

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

---

## 3. 配方 `#view-recipes`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| recipes.view.section | 全樓層 | recipes | `main` | section.browse | `#view-recipes` | src/index.html:842 | 靜態 | 共用 | 路由 | hidden | N/A | hash | N/A | N/A | 低 | P0 | 保留：官方信件裡的連結 | tests/fixed_links.json `route:#f1-recipes`（why：官方信件裡的連結） |
| recipes.filter.category | 全樓層 | recipes | `.filters`（桌面搬到 `.topf`） | chips | `#fRcCat .chip[data-v="all\|weapon\|armor\|acc\|potion\|key\|other"]` | src/index.html:844；`rcFill` 1765 | 重建（換樓層時，`rcFL!==FL`） | 共用但版面不同 | 分類；沒有東西的分類不顯示 | `rcCat` | 配方 | `RC_CAT`（固定代碼） | N/A | N/A | 低 | P1 | 保留 | VERIFIED 5 個 chip |
| recipes.filter.subtype | 全樓層 | recipes | `.filters` | chips | `#gRcSub`、`#fRcSub .chip[data-v="<eqSub>\|?\|all"]` | src/index.html:845；`fillRcSub` 1761 | 重建 | 共用 | 武器／防具／飾品的細分 | `rcSubV` | 配方、裝備 | `rcEq(r)`＝`eqById[r.oid]` 或 `EQX_BY[r.en]`（**英文名**） | 中：遊戲才有的裝備靠英文名對 EQX | 2 物品引用遷移 | 低 | P1 | 保留 | CODE 1759–1767 |
| recipes.filter.npc | 全樓層 | recipes | `.filters`（桌面搬到 `.rhead .rsel`） | select | `#fRcNpc option[value="<NPC 名稱>"]` | src/index.html:846；rcFill 1767；change 1769 | 重建（換樓層） | 共用但版面不同 | 依 NPC 篩選 | value（不存） | 配方、NPC | option value＝`r.npc`＝**npcs.js／recipes.js 的 NPC 名稱 key** | 中：NPC 改用 ID 後 value 要改 | 後續：NPC 遷移 | 低 | P1 | 保留；R0.6 改成 NPC ID | VERIFIED 32 個選項；桌面在 `.rhead` |
| recipes.filter.sort | 全樓層 | recipes | `.rsel` | select | `#fRcSort`（npc/lv/name） | src/index.html:847–848 | 靜態 | 共用但版面不同 | 排序 | N/A | 配方 | N/A | N/A | N/A | 低 | P1 | 保留 | CODE |
| recipes.list.container | 全樓層 | recipes | `.results` | div.grid | `#lRc`、`#cRc` | src/index.html:851；`renderRecipes` 1784 | 重建 | 共用 | N/A | N/A | 配方 | `RCVF()`＝有材料的配方（`RCV` 1753） | N/A | 後續 | 低 | P1 | 保留 | VERIFIED 87 張 |
| recipes.list.card | 全樓層 | recipes | `#lRc` | button.card.rcard | `#lRc [data-key="r\|<ALLREC 索引>"]`（同值 `data-go`） | renderRecipes 1789 | 重建 | 共用 | 開配方面板 | `.sel` | 配方、裝備、道具、NPC | `ALLREC[+id]`（1742） | **高**：陣列索引（見 C-R9） | 2 物品引用遷移／後續 | 高 | P2 | 定位 `#lRc [data-key^="r\|"]`；身份要改成穩定的配方 ID | VERIFIED 第一張 `r\|0` |
| panel.recipe.body | 全樓層 | 配方面板（`#panel`／`gvOpen`） | `#pBody` | 面板內容 | `#pBody`（type `r`） | `recipeDetail` 1972；`recItemInfo` 1963 | 重建 | 共用 | N/A | N/A | 配方、裝備、道具、物品、NPC、地點 | `ALLREC[+id]`、`npcByName(r.f,r.npc)`（1681，**名稱**）、`matRef(m)`（1694）、`EQX_BY[r.en]`、`RQTY[rKey+"\|"+r.en]`、`RMISS[…]` | 高：NPC、材料、產量、缺料表都用名稱字串組 key | 2 物品引用遷移／後續 NPC | 中 | P1 | 保留；R0.6 把 recipes.js 的 NPC 名稱、材料名稱換成 ID | VERIFIED r\|0 面板：`n\|n1_0`、`i\|Sylve Sprout`、`i\|Allium Flower`、`props\|p\|2463` |
| panel.recipe.npc-link | 全樓層 | 配方面板 | `#pBody .facts` | button＋npcWhere 座標 | `[data-go="n\|n<f>_<i>"]`、`[data-rep="<f>\|<x>\|<z>"]` | recipeDetail 1976；`npcWhere` 1684 | 重建 | 共用 | 開 NPC 面板／浮動地圖 | N/A | NPC | `npcByName` → `n.id`（索引） | 高（C-R9） | 後續 | 中 | P2 | 同上 | VERIFIED |
| panel.recipe.material-row | 全樓層 | 配方面板 | `#pBody ul.rows` | button.lrow | `[data-go="i\|<ITEMS key>"\|"e\|<oid>"\|"p\|<oid>"]` | recipeDetail 1976 | 重建 | 共用（手機不顯示「點了看哪裡拿得到」） | 開物品面板 | N/A | 物品、裝備、道具 | `matRef` → `ikey()`、`en2go()`、`enGo()` | 高：材料用名稱 | 2 物品引用遷移 | 中 | P2 | 保留 | tests/fixed_links.json 194 條 `i\|` |
| panel.recipe.dungeon-use | 全樓層 | 配方面板（鑰匙） | `#pBody .facts` | button | `[data-go="s\|<spot.id>"]` | recipeDetail 1976（`r.cat==="key"`） | 重建 | 共用 | 開地下城 | N/A | 地點、配方 | `dgKeys(x).hit.includes(r)` | 中（見 C-R11） | 後續 | 低 | P2 | 保留 | CODE |
| panel.recipe.goview | 全樓層 | 配方面板 | `#pBody .gobtns` | button.btn | `[data-goview="equip\|e\|<oid>"\|"props\|p\|<oid>"]` | recItemInfo 1971 | 重建 | 共用 | `gvOpen` 彈出圖鑑 | N/A | 裝備、道具 | 官網 oid | 低：oid 是官網 id | 2 物品引用遷移 | 低 | P2 | 保留 | tests/fixed_links.json `goview equip/props` 245 條 |
| panel.item.recipe-goview | 全樓層 | 裝備／道具面板 | `.gobtns` | button.btn | `[data-goview="recipes\|r\|<ALLREC 索引>"]` | `recGoBtns` 1701 | 重建 | 共用 | 彈出配方 | N/A | 配方 | `ALLREC.findIndex(npc＋en)`（**名稱**） | 高（C-R9） | 2 物品引用遷移 | 高 | P1 | 身份改成配方 ID | tests/fixed_links.json 293 條 `goview recipes\|r\|N` |
| recipes.logic.is-shop | 全樓層 | recipes（邏輯） | N/A | 函式 | N/A | `isShop` 1738；`SHOP_CATS` 1735 | N/A | 共用 | 判斷「販售」或「製作」（面板標題、`howTitle`、NPC 面板分段） | N/A | 配方、NPC | `npcByName(r.f,r.npc)` 的類別＋`r.src`/`mats`/`sec`/`cost` | 中：名稱查 NPC | 後續 | 低 | P1 | 保留；R0.6 換成 NPC ID | CODE |
| recipes.logic.miss-of | 全樓層 | recipes（邏輯） | N/A | 函式 | `.mats` 裡的「??? ×?」 | `missV`/`missOf`/`missNm` 1677 | N/A | 共用 | 截圖沒看到的材料列 | N/A | 配方 | `RMISS[rKey(r.f,r.npc)+"\|"+r.en]`（NPC 名＋英文物品名） | 中：名稱組 key | 2 物品引用遷移 | 低 | P2 | 保留 | CODE |

### 這一區的風險

- **C-R11｜低｜src/index.html:1329–1333（`dgKeys`）**
  - 問題：地下城鑰匙用兩種方式推斷，都不是 ID：① 地點 `note` 裡用正則抓 `Clé …` 法文名，再比對官網道具名；② 找入口 150 格內 NPC 做的鑰匙配方。
  - 實際影響：改 note 文字或搬 NPC 都會讓鑰匙改變或消失，不會報錯。地下城卡片圖示、面板「需要的鑰匙」、配方面板「用途」都依賴它。
  - 建議修法：R0.6 在地點資料加明確的 `key` 欄位（配方或道具 ID）。
  - 需要改程式：R0.6。
  - 證據：CODE。
- **已檢查但沒發現問題的項目**：
  - 配方分頁只列有材料的配方：87 筆，和 CLAUDE.md 一致（VERIFIED）。
  - NPC 下拉選單：桌面搬到標題旁，手機留在原位（VERIFIED `rselMoved` true／false）。

---

## 4. 地下城 `#view-dungeons`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dungeons.view.section | 全樓層 | dungeons | `main` | section.browse | `#view-dungeons` | src/index.html:855 | 靜態 | 共用 | 路由 | hidden | N/A | hash | N/A | N/A | 低 | P0 | 保留 | tests/fixed_links.json `route:#f1-dungeons` 等 |
| dungeons.list.container | 全樓層 | dungeons | `.results` | div.grid（直列） | `#lDg`、`#cDg` | src/index.html:859；`renderDungeons` 1802 | 重建 | 共用但版面不同：>820px 自動開內嵌面板（`lastDg` 或第一個）；手機不自動開 | 列活動（只在第 1 層）→ 樓層首領塔 → 其他地下城 | `lastDg` | 地點、活動 | `spotsOf(FL).filter(kind==="dungeon")`；`isTowerSp`（1801，`zh` 含「樓層首領」，**文字判斷**） | 中：首領塔用 zh 文字判斷 | 後續 | 低 | P1 | 保留；R0.6 改成明確欄位 | VERIFIED 桌面 inline=true、手機 panel 關閉 |
| dungeons.list.card | 全樓層 | dungeons | `#lDg` | button.card（`.dgtower`） | `#lDg [data-key="d\|<event.id>"]`、`#lDg [data-key="s\|<spot.id>"]` | renderDungeons 1809–1810 | 重建 | 共用 | 開地下城面板（桌面內嵌） | `.sel` | 地點、活動、配方（鑰匙圖示） | `dgKeys(sp).hit[0]` → `recIcon` | 低：spot id／event id 是資料字串 | 後續 | 低 | P2 | 保留：定位 `#lDg [data-key]` | VERIFIED `d\|souls,s\|kobold,s\|geldorakd,s\|fallen,s\|xal,s\|skeld` |
| panel.inline.mode | 全樓層 | dungeons、classes | `#panel` | 面板模式 | `body.cls-inline`、`body.cls-one`、CSS 變數 `--clsw/--clsl/--clst` | `INL` 1196；`fitClsPanel` 1197；renderP 1212–1214；Esc 例外 1236 | 動態 | 桌面專用（>820px） | 面板成為頁面的一部分；裡面的連結改開 `gvOpen`，連到同類（`INL[view].ok`）時直接換頁面內容 | `stack`、`lastDg`/`lastCls` | 地點、活動、職業 | `isDgP`（`d` 或 kind dungeon 的 `s`） | N/A | N/A | 低 | P0 | 保留：重要共用面板模式 | VERIFIED `inline:true`（1280） |
| panel.dungeon.body | 全樓層 | 地下城面板 | `#pBody` | 面板內容（`.dgsplit` `.dga`/`.dgm`/`.dgb`） | `#pBody .dgsplit` | `spotDetail` 1372（dungeon 分支 1379–1384）；`dgTilesHTML` 1346、`dgEntryHTML` 1369、`dgKeyRows` 1365、`dgBossHTML` 1350、`dgLootHTML` 1357、`dgMapHTML` 1339 | 重建 | 共用但版面不同（≥1180px 左右兩欄，地圖 sticky） | N/A | N/A | 地點、怪物、配方、物品、裝備、道具 | 寶箱：`matRef(ITEMS[it]?it:DG_ITEM[it]\|\|it)`（名稱）；首領／寶箱標示怪物：`dgMonByName(f,name)`（名稱）；地圖：`dgOfSpot` 經 `DG_DIM` | 高：寶箱物品和怪物都是名稱字串 | 2 物品引用遷移／後續 | 中 | P1 | 保留；R0.6 把 `sp.dg.loot` 的物品和怪物換成 ID | VERIFIED geldorakd 面板：`r\|52`、`m\|m40`、`e\|1448`、`p\|1968`… |
| panel.dungeon.entry-map-link | 全樓層 | 地下城面板 | `.dga .facts` | button.linkbtn | `[data-spot="<spot.id>"]` | dgEntryHTML 1370；renderP 1230 | 重建 | 共用（手機走 `goMapThen`） | 浮動地圖或大地圖定位 | N/A | 地點 | `spotById` | 低 | 後續 | 低 | P2 | 保留 | CODE dgEntryHTML 1370（實測輸出被截斷，沒看到值） |
| panel.dungeon.map@f1 | 第 1 層（有 jmmeta dg 的 4 個） | 地下城面板 | `.dgm` | figure＋button | `.dgmap [data-dgmap="<dg id>"]`（圖和文字連結各一個） | `dgMapHTML` 1339 | 重建 | 共用 | 進地圖分頁的地下城模式 | N/A | 地下城地圖 | jmmeta dg id | 低 | N/A | 低 | P1 | 保留 | CODE |
| panel.dungeon.key-row | 全樓層 | 地下城面板 | `.dga` | button.lrow | `[data-go="r\|<ALLREC 索引>"]` 或 `[data-go="p\|<oid>"]` | `dgKeyRows` 1365 | 重建 | 共用 | 開鑰匙配方 | N/A | 配方、道具 | `dgKeys`（C-R11） | 高（r 索引） | 2 物品引用遷移 | 中 | P2 | 同 C-R9 | VERIFIED `r\|52` |
| panel.dungeon.loot-row | 全樓層 | 地下城面板 | `.dgb ul.dgloot` | button.lrow／div.lrow.nolink | `.dgloot [data-go]` | dgLootHTML 1357 | 重建 | 共用 | 開物品 | N/A | 物品、裝備、道具、怪物 | 名稱 → `matRef` | 高 | 2 物品引用遷移 | 中 | P2 | 保留 | VERIFIED |
| panel.event-dungeon.body@f1 | 第 1 層（活動） | 活動地下城面板 | `#pBody` | 面板內容 | `#pBody`（type `d`） | `evDgDetail` 1817 | 重建 | 共用 | N/A | N/A | 活動、物品 | 首領、鑰匙材料、兌換武器是 events.js 的**純文字**，沒有連結；寶箱用 `dgLootHTML` | 中：活動的首領、怪物、NPC、兌換表沒有身份（CLAUDE.md 的 R44／RN） | 後續 | 低 | P1 | 保留 | VERIFIED `d\|souls` 面板有 `i\|Skeletal Sword` 等連結 |
| panel.item.dungeon-source | 全樓層 | 物品／裝備面板 | `#pBody` | button.lrow | `[data-go="s\|<spot.id>"]` | `dgSrcHTML` 1354 | 重建（`DG_SRC` 快取） | 共用 | 從物品回到地下城 | N/A | 地點、物品 | `matRef(loot 名稱).go` 反查 | 中：名稱 | 2 物品引用遷移 | 低 | P2 | 保留 | CODE |

### 這一區的風險

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

---

## 5. 職業 `#view-classes`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| classes.view.section | 全樓層（內容不分樓層） | classes | `main` | section.browse | `#view-classes` | src/index.html:863 | 靜態 | 共用但版面不同（≥821px `#view-classes .filters` 隱藏，src/index.html:197） | 路由 | hidden | N/A | hash | N/A | N/A | 低 | P0 | 保留 | tests/fixed_links.json `route:#f1-classes` |
| classes.list.container | 全樓層 | classes | `.results` | div.grid（一欄，最寬 290px） | `#lCls`、`#cCls` | src/index.html:868；`renderClasses` 1833 | 重建 | 共用但版面不同：>820px 自動開內嵌（`lastCls`） | N/A | `lastCls` | 職業 | `CLS`（classes.js） | N/A | N/A | 低 | P1 | 保留 | VERIFIED 6 張 |
| classes.list.card | 全樓層 | classes | `#lCls` | button.card | `#lCls [data-key="c\|<class.id>"]` | renderClasses 1835 | 重建 | 共用 | 開職業面板 | `.sel` | 職業 | class id（guerrier/assassin/mage/shaman/archer/martial） | 低：固定字串 | N/A | 低 | P2 | 保留 | VERIFIED；smoke.py:311、319 |
| panel.class.body | 全樓層 | 職業面板 | `#pBody .cls2` | 面板內容 | `#pBody .cls2`、`details.clsfold`、`details.gskwiki`、`details.gskup` | `classDetail` 1843；`gameSkillsHTML` 1866 | 重建 | 共用；`body.panel-xwide`、`cls-one` | N/A | N/A | 職業、技能 | `c.game`＝`SAO_GAMESKILLS[c.id]`；`c.reps` 用 `norm(r.cls)===norm(c.name)`（**名稱**） | 低 | N/A | 低 | P1 | 保留 | smoke.py:303–341 |
| panel.class.equip-button | 全樓層 | 職業面板 | `.clsbtns` | button.btn | `[data-eqcls="<class.id>"]` | classDetail 1852；renderP 1227；gv 1464 | 重建 | 共用（只有有武器資料且 `CLASS_ZH` 有這個職業才顯示） | 開 `#cwin` | N/A | 裝備 | class id | 低 | N/A | 低 | P1 | 保留 | VERIFIED 桌面 1 個 |
| panel.class.builds-link | 全樓層 | 職業面板 | `.clsbtns` | a（外部） | `.clsbtns a[href*="saominecraft.com/builds"]` | classDetail 1853 | 重建 | 共用 | 開官網配裝（`martial`→`martial_artist`） | N/A | 職業 | class id | 低 | N/A | 低 | P2 | 補識別：沒有 class 或 data 屬性，只能用 href 找 | VERIFIED `https://saominecraft.com/builds?class=guerrier` |
| cwin.class-equipment.window | 全樓層 | 跨分頁 | `body` | div.rwin[role=dialog] | `#cwin`、`#cwHead`、`#cwTitle`、`#cwX`、`#cwBody`、`[data-cwp="<cat>"]`、`[data-cwe="<oid>"][data-key="e\|<oid>"]`、`#cwBack` | src/index.html:881；`openClassEquip` 1881；`showCWItem` 1894；`closeCW` 1896；拖曳 1898；Esc 1901 | 靜態框；`#cwBody` 重建 | 共用（手機版面 NOT RUN） | 部位 chip 篩選；點裝備在同一視窗顯示 `equipDetail` | `CW`（含 `view`，換分頁時關，3614） | 裝備 | 官網 oid；`eqClasses(e)` | 低 | 2 物品引用遷移 | 低 | P1 | 保留（見 C-R13） | VERIFIED 477 張卡片 |

### 這一區的風險

- **C-R13｜低｜src/index.html:1888（cwin 卡片 `data-key="e|oid"`）、1237（`markSel` 掃整份 document）**
  - 問題：`#cwin` 的卡片和裝備分頁的卡片用同一個 `data-key`。
  - 實際影響：右側面板開著某件裝備時，`#cwin` 裡同一件卡片也會被標成 `.sel`。目前看不出問題，但兩處用同一個識別。實測：開 `#cwin` 後 `.card.sel`＝1。
  - 建議修法：`#cwin` 卡片改用 `data-cwe` 就好，或者讓 `markSel` 限定範圍。
  - 需要改程式：可選。
  - 證據：VERIFIED `selMarked:1`；CODE。
- **已檢查但沒發現問題的項目**：
  - 官網配裝連結的參數和 class id 相同（VERIFIED）。
  - 手機不自動開面板（VERIFIED）。

---

## 6. 世界王 `#view-bosses`

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bosses.view.section | 全樓層（內容不分樓層） | bosses | `main` | section.bossview | `#view-bosses`、`#bWrap` | src/index.html:872；`renderBosses` 2430 | 重建（每 30 秒，`bossTimer`） | 共用（進入時關閉右側面板，3614） | 路由 | `bossTimer` | 世界首領、獨特怪物、樓層首領 | `BO`（bosses.js） | N/A | N/A | 低 | P0 | 保留 | tests/fixed_links.json `route:#f1-bosses` |
| bosses.view.card | 全樓層 | bosses | `#bWrap` | article.bcard ×3 | `#bWrap article.bcard` | renderBosses 2437–2469 | 重建 | 共用 | N/A | N/A | 首領 | N/A | N/A | N/A | 低 | P2 | 補識別：3 張卡片沒有 id 或 data 屬性，只能用順序或文字找 | CODE |
| bosses.card.figure-toggle | 全樓層 | bosses | `.bfig` | img＋button | `.bfig img[data-v34][data-vf]`、`.bview [data-bv="34"\|"f"]` | `bFig` 2429；2471 | 重建 | 共用 | 切換 3/4／正面 | `aria-pressed` | 首領 | 圖片路徑 | N/A | N/A | 低 | P2 | 保留 | VERIFIED 4 個按鈕 |
| bosses.card.schedule | 全樓層 | bosses | `.bcols section` | ul.sched | `#bWrap ul.sched` | renderBosses 2443 | 重建 | 共用 | 顯示時段（使用者時區） | `li.on` | 世界首領 | `nextSlot` | N/A | N/A | 低 | P2 | 保留 | CODE |
| bosses.card.floor-boss-link | 全樓層 | bosses | `ul.flboss` | button.linkbtn | `#bWrap .flboss [data-go="m\|<m.id>"]` | renderBosses 2434 | 重建 | 共用 | 開怪物面板 | N/A | 怪物 | `Fx.M.find(x=>x.name.startsWith(Fx.boss))`（**名稱前綴**） | 中：用名稱前綴找首領；id 是怪物索引 | 後續 | 中（見 C-R14） | P2 | 改成資料欄位（樓層首領的怪物 ID） | VERIFIED 只有 `m\|m64`、`m\|f3m36` 兩個連結，第 2 層沒有 |

### 這一區的風險

- **C-R14｜中｜src/index.html:2434**
  - 問題：樓層首領「看圖鑑」的連結用 `m.name.startsWith(Fx.boss)` 找怪物。第 2 層的 `boss` 是 "Asterius"，第 2 層怪物資料裡沒有名稱以 "Asterius" 開頭的怪物（Boss 類有 8 隻：Winnie, Man's Best Friend／Melisara, Sovereign of the Hive／Sanctuary Guardian／Magnus, Colossus of the Veins／Velindra the Weaver／Morverth the Soul Flayer／Rugibœuf, The Guardian／Taurus）。另外 `Fx.status==="soon"` 的判斷已經沒有樓層會用到（第 2、3 層是 `new`）。
  - 實際影響：第 2 層顯示「（圖鑑還沒有收錄）」。實測：頁面上只有第 1、3 層的連結。Asterius 對應哪一隻（或還沒有收錄）要由站長確認，本盤點不判斷。
  - 建議修法：floors 資料加樓層首領的怪物 id；或者先確認 Asterius 和 Taurus 的關係。
  - 需要改程式：是（資料或程式）。
  - 證據：VERIFIED（`desk_boss.go`）；`node` 讀 data23：第 2 層 boss "Asterius"，Boss 類怪物清單裡沒有 Asterius。
- **已檢查但沒發現問題的項目**：
  - 手機寬度沒有左右捲動（VERIFIED）。
  - 3/4／正面切換按鈕存在（VERIFIED）。

---


---

## 第 4 部分（分工 D）：協作區、關於本站、更新紀錄

## 1. 協作區外框與子分頁（`#view-report`）

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| report.view | 全樓層 | report | `main` | section 容器 | `#view-report`（內層 `#rWrap`） | src/index.html:875 | 靜態外框；內容由 `buildFormReport` 一次寫入（`rBuilt` 之後不再重建） | 共用 | `show()` 依 hash 切顯示 | `hidden` 屬性 | N/A | N/A | N/A | N/A | 低 | P0 | 保留：主要容器 | L875、L3612–3613；VERIFIED：換樓層後 `#rWrap` 第一個子節點是同一個（`rwrap_same_after_floor:true`） |
| report.route | 全樓層 | report | 全站路由 | hash 路由 | `#report`、`#feedback`、`#f{N}-report`、`#f{N}-feedback` | src/index.html:3567（hashFor）、3612（show 正則） | N/A | 共用 | `#feedback` 改成 view=report＋`rSub="feedback"`；`#report` 設 `rSub="data"` | `rSub` 變數 | N/A | N/A | 不帶資料 id，R0.6 不影響 | N/A | 低 | P0 | 保留 | L3612–3613；tests/fixed_links.json 有 `route:#f1-report` 類路由；smoke.py:546–551 |
| report.head.collab-btn | 全樓層 | 全站 | `.hbtns` | 連結按鈕 | `#collabBtn`（`data-v="report"`） | src/index.html:3569、3617（href 由 show 每次重寫） | 靜態，href 動態 | 共用 | `go("report")` | `aria-current="page"` | N/A | N/A | N/A | N/A | 低 | P0 | 保留：全站主要入口 | L3569、L3617–3618；smoke.py:547 |
| report.subtabs | 全樓層 | report | `#rWrap .rhead` 下 | nav（兩個連結） | `.csub a[data-sub="data"]`、`.csub a[data-sub="feedback"]` | src/index.html:2607–2608（collabHead）、3138（showCollab 改 href／aria-current） | 動態（buildFormReport 一次） | 共用 | 一般 hash 連結 → `show()` | `aria-current` | N/A | N/A | N/A | N/A | 低 | P0 | 保留；`data-sub` 已是穩定識別 | L2608、L3138；VERIFIED：href 為 `#report`／`#feedback`（第 1 層） |
| report.data.panel | 全樓層 | report | `#rWrap` | div 容器 | `#rData` | src/index.html:3149–3150 | 動態一次 | 共用（≤1100px 兩欄、≤900px 一欄，`.cgrid3`） | 由 showCollab 切 `hidden` | `hidden` | N/A | N/A | N/A | N/A | 低 | P0 | 保留 | L3139；smoke.py:551 |
| report.feedback.panel | 全樓層 | report | `#rWrap` | div 容器 | `#rFeedW`（內層 `#rFeed`） | src/index.html:3149、2609 | 動態一次 | 共用 | 由 showCollab 切 `hidden` | `hidden` | N/A | N/A | N/A | N/A | 低 | P0 | 保留 | L3139；smoke.py:546–549；VERIFIED `#feedback` 時可見 |

## 2. 攻略資料維護（回報表單、處理中、已收錄）

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| report.form.go-button | 全樓層 | report | `#rData .rc-form .rform` | 外部連結按鈕 | `#formGo` | src/index.html:3153（HTML）、3200（href＝`formUrl(FL)`）、2601–2602 | 動態一次；href 每次 render 依樓層重寫 | 共用 | 開 Google 表單（`{floor}` 換成目前樓層） | `.off`（COLLAB_PAUSE 時）、href 有無 | N/A（樓層數字） | `formcfg.js` 的 `SAO_FORM.prefill` | N/A | N/A | 低 | P1 | 保留 | L3200；VERIFIED：第 2 層 href 的 4 個 entry 都是 2；smoke.py:613–616 |
| report.form.howto | 全樓層 | report | `.rform` | 說明（ol、details） | `.rform .steps.big`、`details.rhow` | src/index.html:3155–3172 | 動態一次 | 共用；`.pconly` 一行在 ≤820px 隱藏、`.mbonly` 只手機顯示 | 展開／收合 | `details[open]` | N/A | N/A | N/A | N/A | 低 | P2 | 不處理（說明文字） | L3165、L3172；smoke.py:607–611（路徑反斜線） |
| report.form.review-steps | 全樓層 | report | `.rc-form` | 說明卡 | `.rc-form article.bcard:nth-of-type(2)`（沒有 id） | src/index.html:3174–3176 | 動態一次 | 共用 | 無 | 無 | N/A | N/A | N/A | N/A | 低 | P2 | 不處理 | L3174 |
| report.queue.list | 全樓層 | report | `#rData .rc-q` | 動態清單容器 | `#qCard`（`#qC` 件數、`#qL` 清單） | src/index.html:3193（HTML）、2638–2643（renderQueue）、2631（loadQueue） | 重建（每次 renderReport 整塊 innerHTML；pending.js 每分鐘最多重抓一次，`cache:"no-store"`） | 共用 | 無（純顯示） | 讀取中／讀不到／空 | 回報（只有編號、種類、樓層、送出時間、狀態） | `fetch("pending.js")` | 不含遊戲資料，N/A | N/A | 低 | P1 | 保留 | L2631–2643；VERIFIED `#qL` 1 個 |
| report.done.list | 全樓層（列全部樓層的回報，不依目前樓層篩） | report | `#rData .rc-q` | 動態清單容器 | `#doneL`、件數 `#doneC` | src/index.html:3195（現行 HTML）、3201–3207（renderReport 產生內容） | 重建（每次 renderReport） | 共用 | 列已收錄；內含 `data-go`、`data-rep` 按鈕（`bindGo`） | 無 | 回報；連到怪物／配方／職業／任務 | 怪物：`monById[r.monId]` 或 `FLOORS[f].M.find(name/aka)`；配方：`ALLREC.findIndex(x=>x.rep===r.id)`；任務：`r.qref` 或 `MQ(f).findIndex(...)` | 內含的 `data-go` 會隨 R0.6 變 | 後續：NPC／地點／怪物／任務遷移 | 中（見 D-R3） | P1 | 補識別：清單已有 `li[data-rid]`，其他照舊 | L3201–3207；VERIFIED：1 個 `#doneL`、23 則 `li.replist`、`data-go` 有 `m\|rep-R0022`、`m\|m12`、`m\|m4` |
| report.done.card | 全樓層 | report | `#doneL` | 重複卡片（P2 類別） | `#doneL li.replist[data-rid="<回報編號>"]`；連結 `.rgo [data-go]`、`.rgo [data-rep="f\|x\|z"]` | src/index.html:3204–3206 | 重建 | 共用 | `data-go`→`openP`（bindGo L1422）；`data-rep`→`showPoints` | `.rflash`（goRep 閃一下） | 回報、怪物、配方、職業、任務 | 同上 | `data-go` 值格式變動時要同步 | 後續：NPC／地點／怪物／任務遷移 | 中 | P2 | 保留；`data-rid` 已是回報編號，穩定 | L3206、L3684–3686；report_types_test.py:102–105 |
| global.report-ref.link | 全樓層 | 全站（怪物、地點、任務、技能、配方、NPC 面板的資料來源） | 各面板 | 連結（委派） | `a.replink[data-repgo="<回報編號>"]` | src/index.html:1271（repLink）、1272（repRef）、3684–3687（goRep＋document click 委派） | 動態（各面板 render） | 共用 | 切到 `#report`、輪詢 40×50ms 找 `#doneL li.replist[data-rid]`，捲到中間並閃一下 | `.rflash` | 回報編號 | `data-repgo`＝回報 id（`R000N`；舊 GitHub 回報用 `issue` 外連） | N/A（回報 id 本來就是穩定 id） | N/A | 低 | P0（跨分頁跳轉入口） | 保留 | L1271–1272、L3684–3687；report_types_test.py:102–105 |
| report.legacy.github-form | 全樓層 | report | `#rWrap` | 舊版回報表單整塊（`#rf_form`、`#rf_go`、`#pendL`、`#pendC`，以及**另一份** `#doneL`／`#doneC`） | `#rf_form` 等 | src/index.html:2505–2593（buildReport）、2585（舊版 `#doneL`）、2594–2597（loadPending） | 只有 `FORM_PREFILL` 為空時才會建立 | 共用 | 開 GitHub issue | — | 回報 | GitHub API | N/A | 過渡查找清理（只是建議歸類：死碼） | 低（見 D-R1） | P2 | 不處理或刪除：`FORM_PREFILL` 有字面值備援（L2601），永遠不會走到 | L2601、L3200–3201；VERIFIED：`#pendL` 數量 0、`#doneL` 只有 1 個 |

## 3. 問題回報及建議（`#feedback`）

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| report.feedback.idea-button | 全樓層 | report(feedback) | `#rFeed .fbbtns` | 外部連結按鈕 | `#ideaGo` | src/index.html:2615（HTML）、3140（href＝`FORM_PLAIN`、pauseBtn） | 動態一次，href 每次 showCollab 設 | 共用 | 開不帶預填的 Google 表單 | `.off`（暫停時） | N/A | N/A | N/A | N/A | 低 | P1 | 保留 | L2603、L3140；VERIFIED href＝表單 viewform |
| report.feedback.bug-button | 全樓層 | report(feedback) | `.fbbtns` | 外部連結 | `#rFeed a[href*="template=5-bug.yml"]`（沒有 id） | src/index.html:2615 | 動態一次 | 共用 | 開 GitHub issue 範本 | 無 | N/A | N/A | N/A | N/A | 低 | P1 | 補識別（測試目前用 href 子字串定位，smoke.py:548） | smoke.py:548 |
| report.feedback.idea-queue | 全樓層 | report(feedback) | `#rFeed .rcol` | 動態清單 | `#ideaQ` | src/index.html:2625、2642–2643 | 重建 | 共用 | 無 | `hidden`（沒有審核中的建議） | 回報（type idea） | pending.js | N/A | N/A | 低 | P2 | 保留 | VERIFIED：目前 hidden |
| report.feedback.ideas | 全樓層 | report(feedback) | `.rcol` | 動態清單 | `#ideaL`、`#ideaC` | src/index.html:2626、3141–3142 | 重建（每次 showCollab） | 共用 | 無 | 無 | 回報（type idea） | `REPS.filter(type==="idea")` | N/A | N/A | 低 | P2 | 保留 | L3141–3142 |
| report.feedback.github-list | 全樓層 | report(feedback) | `.rcol` | 動態清單 | `#fbL`、`#fbC` | src/index.html:2627、3130–3133（loadFeedback）、3143–3147 | 重建；只在 `rSub==="feedback"` 時抓，`fbCache` 整頁只抓一次 | 共用 | 外連 issue | 讀取中／讀不到／空 | N/A | GitHub API（標題 `[問題]`／`[建議]`） | N/A | N/A | 低 | P1 | 保留 | L3130–3147；VERIFIED 顯示「目前沒有處理中的問題或建議。」（是否真的連上 API 未分辨，見 UNKNOWN） |

## 4. 打包探索地圖（`#jmPack`，只在電腦版）

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| report.jmpack.card | 第 1～3 層（上傳內容依樓層判斷） | report | `.rc-jm` | 卡片容器 | `#jmPack` | src/index.html:3178 | 動態一次 | 桌面專用（`.pconly`，≤820px 整欄隱藏） | 無 | — | 地點（地下城）、城鎮（小地圖名稱） | 見下列 | 見 data-jmdg | N/A | 低 | P0 | 保留 | VERIFIED：1280 可見、390 隱藏 |
| report.jmpack.howto | 全樓層 | report | `#jmPack` | details | `#jmHow`（內含 `.jmscope`） | src/index.html:3180–3187 | 動態一次 | 桌面專用 | 選了資料夾後自動收起（jmChoose／jmRun） | `open` | N/A | N/A | N/A | N/A | 低（文字和 rc-form 說明不一致，見 D-R6） | P2 | 不處理 | L2836、L2880 |
| report.jmpack.folder-picker | 全樓層 | report | `.jmtools` | label＋隱藏 file input | `#jmPick`（label）、`#jmDir`（`webkitdirectory`） | src/index.html:3188、3197（onchange）、3196（暫停時 disabled） | 動態一次 | 桌面專用 | 選資料夾 → `jmChoose(files)` | disabled／`.off` | N/A | N/A | N/A | N/A | 低 | P1 | 保留 | L3196–3197；smoke.py:615 |
| report.jmpack.download | 第 1～3 層 | report | `.jmtools` | 按鈕列（`display:contents`） | `#jmDl`；按鈕 `[data-jmpart="<n>"]`（更新打包）、`[data-jmfull="<n>"]`（全地圖） | src/index.html:3188、3072–3074（jmShow）、2870（jmRunFull）、3120–3128（jmDlBind） | 重建（每次 jmShow／jmRunFull） | 桌面專用 | 打包 zip 並下載（含 `sao_pack.json`） | disabled、「打包中…」 | N/A（檔案） | N/A | N/A | N/A | 低（檔名固定寫「第1層」，見 D-R7） | P1 | 保留 | L3125；jm_pack_test.py:154–160、172–176 |
| report.jmpack.note | 全樓層 | report | `#jmPack` | 一行說明 | `#jmDlNote` | src/index.html:3189（HTML）、3076–3081 | 重建 | 桌面專用 | 無 | 文字 | N/A | N/A | N/A | N/A | 低 | P2 | 不處理 | L3076 |
| report.jmpack.output | 全樓層 | report | `#jmPack` | 動態容器 | `#jmOut`（內層 `#jmHead`、`#jmOpts`、`#jmRows`） | src/index.html:3190、2836–2840、2878、2898 | 重建（jmChoose／jmRun／jmRunFull） | 桌面專用 | — | `aria-live="polite"` | N/A | N/A | N/A | N/A | 低 | P1 | 保留 | jm_pack_test.py:141 |
| report.jmpack.mode | 全樓層 | report | `#jmOut .jmmode` | 兩顆模式按鈕 | `[data-jmmode="new"]`、`[data-jmmode="full"]` | src/index.html:2838–2840 | 動態（jmChoose） | 桌面專用 | new→`jmRun`、full→`jmRunFull` | 無 | N/A | N/A | N/A | N/A | 低 | P1 | 保留（data 屬性已是識別） | jm_pack_test.py:141–145（NOT RUN） |
| report.jmpack.mode-switch | 全樓層 | report | `#jmOut .jmmode` | 連結按鈕（document 委派） | `[data-jmsw="full"\|"new"]` | src/index.html:2842（jmSwitch）、2843（委派） | 動態 | 桌面專用 | 不重選資料夾直接換模式（需 `JMFILES`） | 無 | N/A | N/A | N/A | N/A | 低 | P2 | 保留 | jm_pack_test.py:169 |
| report.jmpack.floor-box | 第 1～3 層（可輸入 1～100） | report | `#jmHead .jmselbar` | 輸入框＋下拉 | `#jmFloorIn`、`#jmFloorBtn`、`#jmFloorList [data-jmfl="<N>"]` | src/index.html:3087–3089、3095–3100、2999（JM_FLOORS） | 重建（每次 jmShow） | 桌面專用 | 換樓層 → `jmShow(true)`；1～100 以外還原 | `aria-expanded`、`aria-current` | 樓層 | `JMFLS()`（有探索地圖的樓層） | N/A | N/A | 低 | P1 | 保留 | jm_pack_test.py:190、236–264 |
| report.jmpack.selected-button | 全樓層 | report | `.jmselbar` | 膠囊按鈕＋浮動小視窗 | `#jmNamesBtn`（內 `#jmRegSum`）、`#jmNames` | src/index.html:3090、3094 | 重建 | 桌面專用 | 開關「已選區塊」 | `aria-expanded` | 城鎮、地點、地下城名稱 | `jmRegNames`（L2789：城鎮、傳送點、地下城依座標）、`dgName`（L2691） | 顯示名稱，不當鍵；N/A | N/A | 低 | P1 | 保留 | jm_pack_test.py:200、224 |
| report.jmpack.help | 全樓層 | report | `.jmmapw .jmhelpa` | 膠囊按鈕＋浮動小視窗 | `#jmHelpBtn`、`#jmHelp` | src/index.html:3037–3044、3110、2979（jmHelpFit） | 重建 | 桌面專用 | 開關說明 | `aria-expanded`、`.jmtight` | N/A | N/A | N/A | N/A | 低 | P2 | 保留 | jm_pack_test.py:196–204 |
| report.jmpack.region-square | 第 1～3 層 | report | `#jmOpts svg.jmmap` | SVG rect（checkbox 角色）（P2 類別） | `#jmOpts [data-jmreg="<rx,rz>"]`（第 1 層）或 `"<f>:<rx,rz>"`（其他層） | src/index.html:3051–3052（產生）、3104–3106（點選、停留預覽）、3116（同步狀態）、2829（jmKey） | 重建 | 桌面專用 | 點一下加入／取消 `JMSEL.off`；停 350ms 預覽 | `.off`、`.chg`、`aria-checked` | 探索地圖區塊座標 | 座標鍵（不是遊戲資料） | N/A | N/A | 低 | P2 | 保留 | jm_pack_test.py:236–281（NOT RUN） |
| report.jmpack.region-all | 全樓層 | report | `.jmsech` | 兩顆連結按鈕 | `#jmRegAll`、`#jmRegNone`、`#jmDgAll`、`#jmDgNone` | src/index.html:3046、3056、3112–3114 | 重建 | 桌面專用 | 全選／清除 | 無 | N/A | N/A | N/A | N/A | 低 | P2 | 保留 | auto_checks 列為「沒有被引用」：實際是用字串 `on("jmRegAll",…)` 取（L3113），不是死 id |
| report.jmpack.dungeon-tile | 第 1 層 | report | `#jmOpts .jmdgs` | 圖塊按鈕（P2 類別） | `.jmdgt[data-jmdg="<資料夾名>"]`、縮圖 `[data-jmdgth="<同上>"]` | src/index.html:3057–3058、3107–3109、2688–2691（DG_DIM、dgOf、dgName） | 重建 | 桌面專用 | 點選切 `JMSEL.dgOff`；停留預覽（jmDgPreview） | `.on`、`aria-pressed`、`aria-disabled` | 地點（地下城） | `DG_DIM`：JourneyMap 資料夾名（xalzirith、geldorack、labyrinthe、kobold）→ SPOTS id（xal、geldorakd、fallen、kobold）＋備援英文名；`dgName` 用 `FLOORS[1].spots.find(x=>x.id===…)` | **SPOTS id 是 `tiles/dg/<id>/`、`jmmeta.js` 的 `SAO_JM.dg[id]`、tools/jm_merge.py `DUNGEONS` 共用的鍵**；地點 id 若改，三處要一起改（見 D-R8） | 後續：NPC／地點／怪物／任務遷移 | 中 | P2 | 保留；遷移時把 DG_DIM 列進對照 | L2688；jm_pack_test.py:182（NOT RUN） |
| report.jmpack.newfloor | 未開放樓層 | report | `#jmHead` | 勾選框 | `#jmNfOn` | src/index.html:3091–3092 | 重建 | 桌面專用 | 切 `JMSEL.nfOn` | checked | N/A | N/A | N/A | N/A | 低 | P2 | 保留 | L3091 |
| report.jmpack.folders | 全樓層 | report | `#jmRows` | details 清單 | `#jmRows details.jmfold` | src/index.html:3102、2878 | 重建 | 桌面專用 | 展開 | `open` | N/A | `jmSt`／`JM_ST` | N/A | N/A | 低 | P2 | 不處理 | L3102 |
| report.jmpack.preview | 全樓層 | report | `body` | 浮動視窗（可拖） | `#jmPop`（`#jmPopT`、`#jmPopB`、`#jmPopX`） | src/index.html:2912–2921 | 動態（第一次預覽時建立，✕／Esc 移除） | 桌面專用（來源卡片手機隱藏） | 拖標題移動、✕ 關 | 存在與否 | N/A | N/A | N/A | N/A | 低 | P1 | 保留 | L2991（Esc 順序）；jm_pack_test.py:280–281（NOT RUN） |
| report.jmpack.zoom | 全樓層 | report | `body` | 全螢幕放大（document 委派） | 觸發 `[data-jmzoom]`；視窗 `.jmzoom`（`.jmzx` ✕） | src/index.html:2965–2972 | 動態 | 桌面專用 | 點圖放大、Esc／✕／點暗處關 | 存在與否 | N/A | N/A | N/A | N/A | 低 | P2 | 保留 | L2965–2972（NOT RUN） |

## 5. 關於本站、更新紀錄

| component_key | floor | page | parent | element_type | current_selector | source_location | dynamic | desktop_mobile | action | state | data_dependency | lookup_dependency | registry_impact | migration_stage | risk | priority | recommendation | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| about.view | 全樓層 | about | `main` | section 容器 | `#view-about`（內層 `#aWrap`） | src/index.html:876、1933–1961（renderAbout） | 重建（每次 renderCurrent 整塊 innerHTML） | 共用（`.agrid` 兩欄；窄螢幕一欄） | 進頁捲回頂端；`aboutJump` 有值時捲到該 id | — | N/A | N/A | N/A | N/A | 低 | P0 | 保留 | L1961；VERIFIED 兩種寬度都無橫向捲動 |
| about.menu | 全樓層 | 全站 | `.hbtns` | 下拉選單 | `#aboutBtn`、`#aboutMenu`、`#aboutInfo`、`#logBtn`、`#tourBtn` | src/index.html:3572–3577（開關）、3619–3620（href／aria-current） | 靜態，href 動態 | 共用（手機兩顆按鈕 86px、跑馬燈） | 開選單、導到 `#about`／`#changelog` | `aria-current`、`hidden` | N/A | N/A | N/A | N/A | 低 | P0 | 保留（auto_checks 說 `aboutInfo`、`logBtn` 沒有被引用：實際 L3619 用陣列字串 `$(b)` 取，不是死 id） | L3619 |
| about.site | 全樓層 | about | `.agrid .rcol` | 說明卡 | `#aboutSite`；內含 `<a href="#report">協作區</a>` | src/index.html:1935–1941 | 重建 | 共用 | 一般 hash 連結 | — | N/A | N/A | N/A | N/A | 低（見 D-R5） | P2 | 保留 | VERIFIED：該連結 href 固定是 `#report` |
| about.legal | 全樓層 | about | `.agrid .rcol` | 說明卡（錨點） | `#legal` | src/index.html:1943–1953；入口 `#legalBtn`（樓層資訊列，L3596 產生，設 `aboutJump="legal"`） | 重建 | 共用 | 從 `#legalBtn` 跳過來捲到這裡 | — | N/A | N/A | N/A | N/A | 低 | P1（深層錨點） | 保留：`legal` 是跨頁跳轉目標，id 不要改 | smoke.py:234–235；VERIFIED 1 個 |
| about.sources | 全樓層 | about | `.agrid .rcol` | 說明卡 | `#aboutSrc`（`ul.srcl` 9 列，來自 `ABOUT_SRC`） | src/index.html:1904–1914、1955–1959 | 重建 | 共用 | 外連 | — | N/A | N/A | N/A | N/A | 低（內容過時，見 D-R6） | P2 | 不處理（文字） | VERIFIED 9 列 |
| changelog.view | 全樓層 | changelog | `main` | section 容器 | `#view-changelog`（內層 `#clWrap`） | src/index.html:877、1928–1932 | 重建（每次 render） | 共用（`scrollbar-gutter:stable`） | 切換時保留捲動位置（`renderChangelog.keep`） | — | 更新紀錄（changelog.js） | `SAO_CHANGELOG`、`SAO_CHANGELOG_SUM[日期]` | N/A | N/A | 低 | P0 | 保留 | L1928–1932 |
| changelog.mode | 全樓層 | changelog | `#clWrap .rhead .clmode` | chip 群組 | `.clmode [data-clm="sum"]`、`.clmode [data-clm="full"]`；另有卡片內 `.clwait [data-clm="full"]`（沒有 aria-pressed） | src/index.html:1929（chip）、1925（clwait 按鈕）、1931（onclick） | 重建 | 共用 | 切摘要／詳細，存 localStorage `sao-cl-mode` | `aria-pressed` | N/A | `CLM` | N/A | N/A | 低 | P1 | 保留；測試定位要加 `.clmode`（`[data-clm="full"]` 不唯一） | VERIFIED：3 個 `[data-clm]`，第 3 個是卡片內的「詳細內容」；smoke.py:156–157 |
| changelog.card | 全樓層 | changelog | `#clWrap` | 卡片群組 | `#clCard`；每天 `article.bcard.clday`；較早的 `details.clold` | src/index.html:1918–1927 | 重建（切換模式時 `#clCard` 是新節點） | 共用 | 展開較早的更新（重建時保留 open） | `details.clold[open]` | N/A | 同上 | N/A | N/A | 低 | P2 | 保留 | VERIFIED：切到詳細後 `#clCard` 不是同一個節點 |

### 這一區的風險

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

