# UI-INV R0.1｜C. 命名規則 R0.1（提案）

- 基準：`Cheng-1001/ArgoStrategyGuide` main `14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d`
- 版本：**v3**（2026-11-19，依 GPT 第 2 輪複審只補 §1「樓層範圍語意檢查」和驗證案例；其他內容和 v2 相同。v2 修訂紀錄：依第 1 輪 M01、M02、M04 修訂 §1、§3、§5、§8。v1、v2 檔案保留不動）
- 性質：**提案，未核准、未實作**。網站目前沒有任何 component_key；這份規則只定義盤點和之後規劃時用的名稱，以及之後若要在 DOM 加識別屬性時的寫法。
- 和 R0.6 的關係：本規則只命名 UI 元件，不定義遊戲資料的身份。資料身份一律由 R0.6 定；元件只「引用」資料身份，不自己發明。

## 1. 格式

```
component_key = <scope> "." <name> { "." <name> } [ <floors> ]     （<name> 共 1～4 段，所以整個 key 是 2～5 段）
<scope>       = 第 2 節的 scope 之一
<name>        = [a-z0-9][a-z0-9-]*
<floors>      = "@" <fl> { "," <fl> }
<fl>          = "f" <N> [ "-" <M> ]        （N、M 是 1 起算的樓層數字，M > N）
```

驗證用的正規表示式（v2 清冊 293 個正式 key 全部通過，0 個不符合）：

```
^[a-z][a-z0-9-]*(\.[a-z0-9][a-z0-9-]*){1,4}(@f[1-9]\d*(-[1-9]\d*)?(,f[1-9]\d*(-[1-9]\d*)?)*)?$
```

- 全小寫，單字之間用 `-`，層級用 `.`。**只用 ASCII**；不能有 `/`、`／`、空白、中文。
- 段數：`<scope>.<name>` 兩段就夠的元件不用硬補中間層（例：`global.search`、`panel.root`、`popup.window`、`report.view`）。v1 寫成「`<scope>.<area>.<part>` 必填三段」和清冊 47 個兩段 key 不一致，v2 把中間層改為選用（M01）。目前清冊（v2，`popup.jm-*` 改名後）：兩段 45 個、三段 245 個、四段 3 個。
- 一個 key 只代表一個元件；兩種東西不能合寫在同一個 key（v1 清冊的 `global.link.data-dgmap／data-under` 已拆成 `global.link.data-dgmap@f1` 和 `global.link.data-under@f1`）。
- 不含顯示文字（中文名、英文名）、座標、序號（nth-child、陣列索引）。
- 合法的樓層後綴：`@f1`、`@f1-2`（第 1～2 層）、`@f2,f3`（第 2 層和第 3 層）、`@f1,f3-5`。不合法：`@1`（少 f）、`@f2-1`（範圍倒過來）、`@f1-1`（範圍只有一層，應寫 `@f1`）、`@f0`、`@F1`、`@f1;f2`。

### 1.1 正式驗證＝三項都要通過（v3 新增）

正規表示式僅驗證 component_key 的字元及基本格式，不驗證樓層範圍的數值先後。每個 `fN-M` 範圍必須另行檢查 `M > N`；不符合者判定為非法 key。正式驗證須同時通過：

1. **正規表示式**（上面那條）；
2. **scope 白名單**（第 2 節列的 scope：`global`、`panel`、`popup`、`floatmap`、`cwin`、`imgzoom` 和 14 個 view 名）；
3. **樓層範圍語意檢查**：`@` 後面每一段 `fN-M` 都要 `M > N`（`fN` 單層不檢查）。

驗證案例（腳本 `keyvalidate_v3.py` 實際執行結果，原始輸出 `UIINV_R0.1_keyvalidate_v3_output.txt`）：

| 測試值 | 預期 | 結果 |
|---|---|---|
| `map.legend.base-button@f1-2` | 合法 | 合法（PASS） |
| `map.legend.base-button@f2-1` | 不合法 | 不合法：範圍 f2-1 需要 M > N（PASS） |
| `map.legend.base-button@f1-1` | 不合法 | 不合法：範圍 f1-1 需要 M > N（PASS） |
| `map.legend.base-button@f2,f3` | 合法 | 合法（PASS） |

清冊結果：A v2 的 293 個正式 key 三項全部通過（0 個不合法）；其中有範圍的只有 `map.legend.base-button@f1-2`（合法）；A §0 的 17 個正式 key 也全部通過，且都在清冊裡。

## 2. scope（第一段）

| scope | 用在 | 例子 |
|---|---|---|
| `global` | 全站只有一份、和分頁無關的元件：頁首、樓層選擇、上方選單、全站搜尋、路由、連結種類、列表共用機制 | `global.floor.trigger`、`global.search`、`global.route.hash`、`global.link.data-go`、`global.list.actf` |
| `<view>` | 只屬於一個分頁：view 名照 `VIEWS`（map、monsters、equip、props、items、npcs、recipes、dungeons、quests、classes、bosses、report、about、changelog） | `equip.filter.effect`、`map.legend.base-button@f1-2` |
| `panel` | 右側資料面板 `#panel` 和它裡面的區塊（區塊依資料種類分第二段） | `panel.root`、`panel.equip.obtain`、`panel.quest.route-mini` |
| `popup` | 中間彈出視窗 `#gvLayer`（只有這個） | `popup.layer`、`popup.window` |
| `floatmap` | 浮動地圖／路線視窗 `#rwin` | `floatmap.window` |
| `cwin` | 職業可用裝備視窗 `#cwin` | `cwin.window` |
| `imgzoom` | 看圖視窗 `.imgzoom` | `imgzoom.viewer` |

規則：
- 一個元件只屬於一個 scope。**同一個實體元素只能有一個 key**（本次盤點有 15 列是不同分工替同一元素取了不同 key，正式 key 見清冊第 0 節）。
- 只在某一個分頁用的浮動視窗不算共用元件，放在那個分頁的 scope 下（例：打包工具的預覽 `#jmPop` → `report.jmpack.preview`，不是 `popup.*`）。
- 面板區塊用 `panel.<資料種類>.<區塊>`，不論區塊是在 `#panel`、`gvOpen` 彈出視窗或內嵌模式（`cls-inline`）裡顯示：容器不同，邏輯元件相同。

## 3. 全站元件 vs 樓層元件

- 預設**不分樓層**：大部分元件每層都一樣，內容依目前樓層變（例：`monsters.list.container`）。
- 只有**某幾層才存在**、或各層行為不同的元件，加樓層後綴 `@f<N>`（可多個 `@f2,f3` 或範圍 `@f2-3`）：
  - 例：`map.legend.dungeon-back@f1`（地下城地圖只有第 1 層）、`panel.event-dungeon.body@f1`（活動地下城只在第 1 層列）。
  - v2 已把清冊的 `map.legend.base-button` 改成 `map.legend.base-button@f1-2`（第 3 層 `jmAlways` 隱藏）。目前有樓層後綴的 key 共 11 個（都在清冊裡）。
- 後綴只描述「元件在哪些樓層出現」，**不能用來區分資料**（不要寫 `npcs.card@f3` 來代表第 3 層的 NPC 卡片，卡片的資料身份見第 5 節）。

## 4. 桌面／手機共用同一邏輯 key

- 同一個功能在桌面和手機外觀或位置不同，**仍是同一個 key**；差異寫在清冊的 `desktop_mobile` 欄，不另取名。
  - 例：圖鑑子分頁的上方 `#codexTabs`（手機）和左欄 `.vtabs`（桌面）功能相同，但目前是**兩個實體元素**：key 分成 `global.codextabs` 和 `global.codextabs.vtabs`，並在兩列互相註明「同一功能」。之後若合成一個元件，就收成一個 key。
  - 例：`placeTopFilters` 把同一個 `.fgroup` 在桌面搬到標題旁、手機搬回左欄：只是位置不同，同一個 key（`global.list.topf`／`global.list.rsel` 是容器，篩選本身用 `<view>.filter.<名稱>`）。
- 只在一種裝置存在的元件（例：`.pconly` 打包工具、手機 `.fbar`）照常命名，`desktop_mobile` 寫「桌面專用」或「手機專用」。
- **禁止**為了桌面／手機各複製一份帶 `id` 的節點（本次盤點：`syncVTabs` 複製 `#codexTabs` 讓 `#nMon` 等 5 個 id 執行時各 6 份，見 A-R1／B-R4）。

## 5. 動態卡片：靠資料身份定位，不靠位置

- 重複的卡片（清單卡片、面板裡的連結列、地圖標記）**component_key 只寫到類別**，不替每張卡片編號：`equip.list.card`、`map.marker.npc`。
- 要找某一張卡片時，用「**容器＋資料身份屬性**」：
  - `#lEq [data-key="e|1760"]`、`#lRc [data-key="r|<配方身份>"]`。
  - 資料身份的值（`<type>|<id>`）由 R0.6 定。**目前**的值有 7 種是陣列順序流水號（`m<i>`、`n<f>_<i>`、`mq<f>_<i>`、`q<i>`／`f<f>q<i>`、`r|<索引>`、`e|x<k>`、`p|g<k>`），資料順序一變就指到別的東西（B-R1／C-R9／D-R12-2）。規則只規定**用 data 屬性定位**；屬性裡放什麼值，等 R0.6。
- 三種連結屬性的格式見 5.1；三者的**實體身份部分**必須一致，不是整條字串相同。

### 5.1 `data-key`／`data-go`／`data-goview` 的格式（v2 新增，M02）

| 屬性 | 段數 | 格式 | 現有例子 | 讀取方式（src/index.html） |
|---|---|---|---|---|
| `data-key` | 2 | `<type>\|<id>` | `e\|1760`、`m\|m0`、`i\|Wolf Fur` | `markSel` :1237–1239 用 `[data-key="${type}\|${CSS.escape(id)}"]` 找；`goView` :1480 同樣 |
| `data-go` | 2 | `<type>\|<id>` | `n\|n3_0`、`r\|4`、`s\|xal` | `bindGo` :1422 `const [t,i]=b.dataset.go.split("\|")`；右側面板 `renderP` :1212、彈出視窗 `gvRender` :1463 同樣用 `split("\|")` 取前兩段 |
| `data-goview` | 3 | `<view>\|<type>\|<id>` | `recipes\|r\|171`、`equip\|e\|1760` | `bindGo` :1423 `const [v,t,i]=b.dataset.goview.split("\|")`，接著 `gvOpen(t,i)`；`renderP` :1215 同樣；`gvRender` :1462 用 `[,t2,i2]` 跳過第一段。第一段 `<view>` 目前沒有被使用（B-R7），但仍佔一個位置 |

- **實體身份**＝`<type>\|<id>`。同一筆資料的 `data-key`、`data-go`、`data-goview` 後兩段必須相同，`markSel`、`goView` 才找得到對應卡片。
- `<type>`：目前用到 `m e p i r n q s t c d`（各代表怪物、裝備、道具、素材、配方、NPC、任務、地點、城鎮、職業、活動地下城）。
- **解析規則**：用 `split("\|")` 再用陣列解構取前 2／3 段，所以 **`<id>` 裡如果有 `\|`，後面的部分會被丟掉**（不會報錯）。`data-goview` 不能改成兩段，否則 `[v,t,i]` 會把 type 當成 view、id 當成 type。
- **`<id>` 的合法字元**（建議給 R0.6 參考，不是 R0.6 的決定）：不能含 `\|`；不能含 `"`（屬性值用雙引號包）；避免換行和控制字元。目前 `i\|` 的 id 是物品名（可能有空白、撇號、括號、中文），產生時用 `esc()` 做 HTML 轉義（例如 :1243、:1390、:1548）；`s\|` 有一處也用 `esc(sp.id)`（:1356 地下城寶箱），其他產生處直接插入、沒有轉義（因為目前都是數字或 slug）。轉義做法不一致，R0.6 若讓 id 含特殊字元，要統一用 `esc()`。找元素時一律用 `CSS.escape(id)`（`markSel`、`goView` 已經這樣做）。
- **R0.6 切換身份時要維持的相容**：① 段數不變（兩段／三段）；② `<type>` 字母不變，或同時改所有產生和讀取的地方；③ 新 id 不含 `\|` 和 `"`；④ `data-key` 和 `data-go` 同一批改，避免選取標示和「查看圖鑑」找不到卡片（D-R12-4）。
- 現在沒有身份屬性的動態元素（地圖 NPC 標記、右側清單的城鎮／首領／NPC 列、面板區塊 `h3.sec`、已篩選列 `.af[data-i]`），之後補屬性時用 `data-key`（資料）或 `data-part`（區塊種類，值＝component_key 最後一段）。這是提案，不在本次範圍。

## 6. 禁止當作主要定位方式

| 禁止 | 原因 | 目前的例子 |
|---|---|---|
| `nth-child`／`:nth-of-type`／清單序號 | 篩選、排序、資料新增都會改順序 | `.actf .af[data-i]`（序號）、測試 `baseline_capture.js:83` 用第一張卡 `m\|m0` |
| 顯示文字（中英文名稱、標題字） | 官方中文化、改名、翻譯都會變 | `.zrow[data-tp]`（英文名，C-R1 已造成中文搜尋清單 0 列）、`.zsec[data-k]`、`h3.sec` 文字、`#fRcNpc` option 值＝NPC 名 |
| 座標 | 校正、截圖推算會改 | `data-rep="<f>\|<x>\|<z>"` 只能當參數，不能當身份 |
| 陣列索引產生的資料 id | 見第 5 節 | `r\|N`、`n<f>_N`… |

輔助定位（可以用、但不能是唯一依據）：class（`.card`、`.chip`）、ARIA（`aria-pressed`、`aria-current`）、元素種類。

## 7. 既有 ID 要不要保留

- **全部保留**現有靜態 `id`（約 238 個不重複的 id；auto_checks 列為「沒有被引用」的 27 個裡，至少 `aboutInfo`、`logBtn`、`jmRegAll`、`view-*` 其實是用字串陣列或拼接取得，不能刪）。
- component_key **不取代** id；之後若要在 DOM 標 key，用新屬性（提案：`data-ui="<component_key>"`），不改 id、不改 class。
- 必須維持不變的識別（拆分 `src/index.html` 或重構時的相容清單，詳見清冊 A §6／風險 A-R11）：
  - 路由：`#view-<view>`（14 個）、hash `#f{N}-{view}`（第 1 層正規形式沒有前綴）、`VIEWS` 名稱、`feedback`→`report` 的轉換。
  - 面板：`#panel`、`#pBody`、`#pBack`、`#pClose`、`#pCrumb`；彈出視窗 `#gvLayer`；`#rwin`、`#cwin`。
  - 連結屬性：`data-go`、`data-goview`、`data-key`、`data-repgo`、`data-rep`、`data-route`、`data-spot`、`data-town`、`data-imap`、`data-eqcls`、`data-imgzoom`、`data-dgmap`、`data-under`（格式見清冊 A 的連結綁定矩陣）。
  - 測試和導覽依賴：smoke.py／site_audit.js／baseline_capture.js 用到的 id 與 `window.__*` 掛鉤（`__detail`、`__auditIds`、`__effPick`、`__jm` 等）、導覽 `saoTour` 的 9 個 selector（A-R11a）。
- 重複的 id：`doneC`／`doneL` 兩處定義不會同時存在（舊流程是死碼，D-R1／A-R1b），保留或清理都不影響；`nMon` 等 5 個執行時重複要在重構時處理（不保留重複）。

## 8. 和舊測試、舊路由的相容

- 舊網址：只有 `#f{N}-{view}` 和 `#{view}`，**不含資料 id**（D-R12-6，VERIFIED），所以命名規則和 R0.6 都不會讓玩家的網址失效。規則：不改 hash 格式；若之後要讓網址帶資料，另立規格，舊格式仍要能用。
- `tests/fixed_links.json` 共 1,521 筆：entity 933、goview 538、route 37、search 13。route 和 search 共 50 筆不以實體 id 當鍵，不會只因 id 更新而失敗；其他用穩定身份（`s\|`、`t\|`、官網 oid）的連結也未必改變。
- R0.6 改資料身份時的基準處理（v2，M04；屬於 R0.6 範圍，這裡只寫 UI 這端的期待）：**不能先把 baseline 和 fixed_links 全部重產，再用新版對新版證明一致**。階段 1.5 網站不切換，G5 維持 `IDENTICAL`；階段 2 起的預期身份遷移，依已審查的 `key_map`、舊連結對照和預期修正清單核對舊新結果，確認沒有非預期差異後，才更新相關基準。
- smoke.py 寫死的 `q|mq1_33`、`q|mq1_15`、baseline_capture.js 的 `m|m0` 是流水號：測試改寫時改成用資料身份或穩定字串（`c|archer`、`s|xal`、`d|souls` 這類已經穩定）。
- 新測試定位元素的優先順序：① `id`（靜態、唯一的）→ ② 容器 `id`＋`data-key`／`data-v` → ③ 之後加的 `data-ui`。不用文字和序號。
