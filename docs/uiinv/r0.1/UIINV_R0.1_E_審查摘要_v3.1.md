# UI-INV R0.1｜E. GPT 複審摘要（v3.1）

> **v3.1 是 GPT 最終複審 PASS（審查對象：`UIINV_R0.1_E_審查摘要_v3.md`，SHA-256 `90bbf7ae122d76a241117ec6606aec0b182a7a064132cb71fcc67790223fe123`）之後的文字修訂**，只改兩處：① 標題由（v2）改為（v3.1）；② §0 M01 驗證欄「A §0 的 15 個正式 key」改為「A §0 的 15 列重複對照、17 個正式 key」。兩處都是 GPT 最終複審列出的非阻擋文字問題。**v3.1 本身沒有經過 GPT 複審，不繼承 v3 的審查宣告**；審查基準仍以 v3 原檔和 `UIINV_R0.1_baseline.md` 列的 9 份檔案為準。

- 基準：`Cheng-1001/ArgoStrategyGuide` main `14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d`（`src/index.html` blob `e9d4db271ea061d7c4f76aea22534db036847423`）
- 版本：**v3**（2026-11-19），依 GPT 第 2 輪複審（判定 NOT PASS，只剩 M01 一項）做最小修訂：只改 C 和 E；A、B、D 沿用 v2（`_v2` 檔案不變）。v2 是依第 1 輪（M01～M05）修訂。v1、v2 檔案都保留不動。
- 性質：唯讀盤點＋規劃建議，**不是已核准決策**；component_key 都是提案，網站沒有實作。

## 0a. v2 → v3 最小修訂（GPT 第 2 輪）

第 2 輪結論：M02～M05 PASS（M05 為文件證據），只剩 M01 要補「樓層範圍語意檢查」；另有 R6-5、A-R3a 註記、差異統計三處文字。

| 項目 | GPT 第 2 輪要求 | v3 怎麼改 | 改在哪 | 驗證 |
|---|---|---|---|---|
| M01 | 寫明正規表示式不檢查樓層範圍先後；`fN-M` 要另檢查 `M > N`；正式驗證＝正規表示式＋scope 白名單＋範圍語意；附 4 個驗證案例和 293 個 key 的語意檢查結果 | C v3 新增 §1.1（照 GPT 建議的文字），並補上 `@f1-1` 為不合法；新增驗證腳本 `keyvalidate_v3.py` | C v3 §1、§1.1；本檔 §7.3 | 4 個案例全部符合預期；293 個正式 key 三項全過、0 個不合法；A §0 的 17 個正式 key 全過；exit=0 |
| R6-5 | 補明「階段表示檢查責任，不代表全部搬進 Registry 或必須刪除」 | §4 R6-5 改寫：`DG_DIM` 改稱 JourneyMap 資料夾映射，並補上這句 | 本檔 §4 | 文字 |
| A-R3a | 保留「非玩家正常操作路徑」註記，不當成已確認的正常操作故障 | §3 第 1 項、§9 的 A-R3 加註：A-R3a 是人工建構狀態（改寫既有按鈕的 `data-goview` 開彈出視窗）的結果；A-R3b、A-R3c 是正常操作路徑 | 本檔 §3、§9 | 文字 |
| 差異統計 | E 的 v1→v2 實際差異是新增 200、刪除 149（上次寫 197／146） | 改用 `git diff --no-index --numstat` 統計並更正；上次的 197／146 是用 `diff` 逐行標記 `<`／`>` 數出來的，兩種演算法的對齊方式不同。只有 E 不一致，其他四份兩種方法結果相同 | 本檔 §7.3 | 原始輸出見 §7.3 |
| B-R13 | GPT 確認是指 A-R13 | 不新增編號；沿用 A-R13 | — | — |

## 0. v1 → v2 修正對照（M01～M05）

| 編號 | GPT 要求 | v2 怎麼改 | 改在哪 | 驗證 |
|---|---|---|---|---|
| M01 | C 的 key 格式和清冊不一致（47 個兩段 key；`global.link.data-dgmap／data-under` 含非 ASCII 和 `/`）；列出合法樓層後綴 | 語法改成 `<scope>.<name>{.<name>}[@floors]`（2～5 段，中間層選用），附正規表示式和合法／不合法後綴例子；合併的那一列拆成 `global.link.data-dgmap@f1`、`global.link.data-under@f1`；`map.legend.base-button` → `map.legend.base-button@f1-2`；`popup.jm-preview`／`popup.jm-zoom`（和 C §2「`popup` 只給 `#gvLayer`」衝突）直接改成 `report.jmpack.preview`／`report.jmpack.zoom`；A §0「正式 key」欄每個 key 各自一個 code span；D 依賴表檔頭寫明第一欄是「依賴項目名稱」不是 component_key，並列出和清冊 key 的對應 | C v2 §1、§3；A v2 §0、第 1／3／4 部分；D v2 對照表檔頭 | 腳本（§7.2）：293 個正式 key 全部符合正規表示式、scope 全在 C §2 白名單內；A §0 的 15 列重複對照、17 個正式 key 也全部符合；兩段 45、三段 245、四段 3（v1 的 47 個兩段 key 裡，2 個 `popup.jm-*` 改名後變三段）；有樓層後綴 11 個；`popup.*` 只剩 `popup.layer`、`popup.window`、`popup.menu-rule` |
| M02 | `data-key`／`data-go`／`data-goview` 不是「同格式」；要寫各格式、解析、合法字元、轉義、R0.6 相容 | 新增 C v2 §5.1：兩段 `<type>\|<id>`／三段 `<view>\|<type>\|<id>`、`split("\|")` 解構取前幾段、`<id>` 不能含 `\|` 和 `"`、只有 `i\|` 用 `esc()`、查找用 `CSS.escape`；R0.6 切換時要維持的 4 點相容。D-R12-4 和依賴表 `global.data-key` 那列的說法同步改成「實體身份部分一致」 | C v2 §5、§5.1；D v2 §A；B v2 D-R12-4 | 行號重新對過：`markSel` :1237–1239、`bindGo` :1422–1423、`renderP` :1212／:1215、`gvRender` :1462／:1463、`goView` :1480；`esc()` 在 `i\|` :1243、:1390、:1548 和 `s\|` :1356 |
| M03 | #32 已決定只適用桌面裝備面板；classes／dungeons 是排除範圍不是違規；修法只限裝備面板；bosses 等另列待確認例外 | 附錄 E1 的表：classes／dungeons 改成「不適用、排除範圍」；bosses／report／about／changelog 改成「既有特殊關閉行為，待確認例外」；結論和 A-R13 的修法限定為「桌面＋換樓層＋目前面板是裝備面板（`stack` 最上層 `type==="e"`）時 `closeP()`」，不影響其他面板和手機 | E v2 附錄 E1；A v2 §5；B v2 A-R13；本檔 §3、§5、§6 | v2 證據腳本 `A-R13_rule32_floor_change`（見 §7） |
| M04 | R6-3 不能把重產基準當成通過 G5；fixed_links 有 50 筆 route／search | R6-3、C v2 §8、D v2（D-R12-2、`tests.fixed-links`）改成：階段 1.5 網站不切換、G5 維持 `IDENTICAL`；階段 2 起依已審查的 `key_map`、舊連結對照和預期修正清單核對舊新結果，沒有非預期差異才更新基準；route 37＋search 13 不依實體 ID | 本檔 §4；C v2 §8；D v2 §B、§E；B v2 D-R12-2 | 文字修訂；fixed_links 統計沿用（entity 933、goview 538、route 37、search 13） |
| M05 | VERIFIED 證據要能獨立複核：A-R3、A-R13、B-R2、C-R1、執行時重複 ID 的腳本、命令、原始輸出、結束碼、寬度、SHA | 新寫一支獨立腳本 `UIINV_R0.1_evidence_v2.js`（唯讀），對指定 SHA 的 worktree 跑，輸出全文存 `UIINV_R0.1_evidence_v2_output.txt`；其他子代理實測的結論改標「VERIFIED（子代理實測，原始輸出未附）」，沒跑的維持 NOT RUN | 本檔 §7、§8、§9；兩個證據檔 | 8 項檢查全部重現、exit=0（§7） |
| 其他 | D-R5 提高為中並寫理由；E 寫明「高風險 3 列、不同根因 2 組」；292 是邏輯項目數不是 DOM 元素數 | D-R5 改「中」，理由寫在嚴重程度欄；§2 補上 | B v2 總表、D-R5；本檔 §2 | 風險分布重算：高 3、中 23、低 28 |

## 1. 基本資料

| 項目 | 內容 |
|---|---|
| 盤點基準 SHA | `14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d` |
| main 現況 | 2026-11-19T11:55:32Z（UTC）fetch：main 是 `2e36f43a644a0663bf2d62302a2991a98b736a5e`。和基準相比只多 2 個 Apps Script 自動提交（「處理中的回報：2 則」「…3 則」），只改 `pending.js`；`src/index.html` blob 仍是 `e9d4db271ea061d7c4f76aea22534db036847423`。**所以盤點基準維持 `14f677b`**，清冊、行號、證據都不受影響 |
| 盤點方式 | v1：4 個子代理分區（A 外殼／B 圖鑑／C 地圖等／D 協作區＋依賴表），各自在獨立 worktree 用 Playwright 實測。v2：另用一支證據腳本在新的獨立 worktree（detached HEAD＝基準 SHA）重跑 5 類問題 |
| 有沒有改東西 | 沒有：沒有改 GitHub 檔案、沒有 branch／commit／PR／push、沒有改網站或資料、沒有改 R0.6。v2 證據用的 worktree `git status --porcelain` 是 0 行 |
| 檢查的檔案 | `src/index.html`（3,755 行）；資料檔 data.js、data23.js、npcs.js、recipes.js、mainq.js、zhnames.js、events.js、classes.js、jmmeta.js、reports.js（身份相關部分）；測試 `tests/fixed_links.json`、`baseline_capture.js`、`baseline_compare.js`、`smoke.py`、`site_audit.js`、`jm_pack_test.py`、`report_types_test.py`；工具 `tools/check_refs.py`、`tools/jm_merge.py`；CLAUDE.md |
| 檢查的樓層 | 第 1、2、3 層（程式碼全部；實測以第 1 層為主，第 3 層 NPC 面板、第 2 層換樓層也有跑；第 2、3 層的篩選和清單畫面 NOT RUN） |
| 檢查的分頁 | 14 個 view：map、monsters、equip、props、items、npcs、recipes、dungeons、quests、classes、bosses、report（含 `#feedback` 子分頁）、about、changelog（GPT 已核對各 view 在 :721～:877） |
| 寬度 | 1280、390 實測；821～1179 NOT RUN |

## 2. 數量

| 項目 | v1 | **v2** | 說明 |
|---|---|---|---|
| 清冊列數 | 307 | **308** | A 分工 64→65（合併的 `data-dgmap／data-under` 拆成兩列）；B 109、C 89、D 45 不變 |
| 去重後清冊項目 | 292 | **293** | 扣掉 15 列重複 key（v1 的 2 列改名建議在 v2 已直接改名，照常計數）。**這是清冊的邏輯項目數**（含功能和行為識別，例如路由、連結種類、Esc 順序），**不是瀏覽器裡的 DOM 元素數** |
| P0／P1／P2（去重後） | 52／139／101 | **52／140／101** | 新增的一列是 P1 |
| 風險條目 | 54（高 3、中 22、低 29） | **54（高 3、中 23、低 28）** | D-R5 由低改中 |
| 不同根因 | 約 49 | **約 49** | 跨分工重複記錄的 4 組：{B-R1, C-R9, D-R12-2}、{A-R1, B-R4}、{A-R1b, D-R1}、{A-R9, D-R2}。**高風險 3 列只有 2 個不同根因**：A-R3（連結綁定缺口）和 B-R1＝C-R9（流水號身份），不能當成 3 個獨立的高風險缺陷 |
| 不穩定／重複識別 | 同 v1 | 同 v1 | 執行時重複 id 5 個（各 6 份，v2 證據腳本 1280／390 都重現）；靜態重複 1 組（`doneC`／`doneL`，互斥）；陣列流水號資料 id 7 種；用顯示文字當鍵的 UI 識別 6 處 |
| R0.6 依賴表 | 45 筆 | 45 筆 | 目前已確認 26、未來預計遷移 16、尚未確認 3 |

## 3. 高嚴重度和主要發現

1. **A-R3（高）三套連結綁定涵蓋不同**：`renderP`（:1212–1231，:1231 有 `data-town`）、彈出視窗 `gvRender`（:1458–1470，沒有 `data-town`）、`showCWItem`（:1894–1895）只對 `#cwBody` 呼叫 `bindGo`，而 `bindGo`（:1422–1423）只處理 `data-go`、`data-goview`。v2 證據腳本重現 3 種結果：彈出視窗裡城鎮「在地圖上查看」點了沒反應（**A-R3a 是人工建構狀態的結果**：測試把既有「查看」按鈕的 `data-goview` 改成 `map|t|tob` 來開彈出視窗，**不是玩家的正常操作路徑**，不能直接描述成已確認的正常操作故障；被測的是彈出視窗內 `data-town` 沒有綁定這件事，程式碼 :1458–1470 也可確認）；`#cwBody` 的座標 `1|1778|3530` 點了沒開浮動地圖；`#cwBody` 的 `data-go`（`n|n1_52`）把右側的職業頁（戰士）換成 NPC 面板。
2. **B-R1＝C-R9（高，同一根因）資料 id 是陣列流水號**：`e|x<k>`（:2093–2094，依 `ITEMS` 順序）、`p|g<k>`（:2297–2300，依未被排除的 potions 順序）、`r|<N>`（:1671–1675 先併入回報，再產生 `ALLREC` :1742），另有 `m`、`n`、`mq`、`q`。**不是**玩家現在每次點擊都會錯；是資料變動後，同一個舊識別可能指向別的資料。受影響的是 fixed_links、baseline、smoke 寫死的 id。
3. **#32（A-R13，中）**：站長已決定規則只適用**桌面版裝備面板**。前半條（同樓層切分頁保留）在一般分頁符合；後半條（換樓層關閉）**不符合**：v2 證據腳本在 `#equip` 打開 Ring of the Boar，切到 `#monsters` 面板仍開（符合），再到 `#f2-equip` 面板仍開、標題仍是 Ring of the Boar、樓層顯示第 2 層（不符合）。classes／dungeons 換成內嵌頁是排除範圍，不列為違規；bosses／report／about／changelog 的關閉行為是待確認的例外，和換樓層缺陷分開。
4. **B-R2（中）配方查找不比樓層**：`recGoBtns`（:1701）、`recipeTable`（:1704）用 `npc＋en` 找 `ALLREC` 索引。v2 證據：第 3 層煉金術士 `n|n3_0` 的 8 個配方連結裡，`r|4`、`r|5`、`r|7`、`r|8` 對到 recipes.js 的鍵 `Alchemist`（第 1 層），另外 4 個對到 `3|Alchemist`；當時 reports.js 沒有配方回報（0 則），所以索引和 recipes.js 順序一致。
5. **C-R1（中）中文搜尋時右側清單 0 列**：v2 證據：搜「煉金術士」地圖顯示 NPC 2 個、清單 0 列；搜「起始之鎮」地圖 NPC 1、城鎮 1、清單 0 列；搜英文「Alchemist」「Starting」清單各 2 列。
6. **A-R1／B-R4（中）執行時重複 id**：v2 證據在 1280 和 390 都是 `nMon`、`nEquip`、`nProp`、`nItem`、`nNpc` 各 6 份；`doneC`／`doneL` 在裝備頁 0 個、協作區頁各 1 個。
7. **D-R5（v2 改為中）**：關於本站的「協作區」連結寫死 `href="#report"`（:1939），在第 2、3 層點了會切回第 1 層，回報表單的預填樓層也變成 1（CODE：:3612–3613 沒有 `f` 前綴就是第 1 層）。
8. 其他中風險（A-R5 Esc 順序、A-R6 手機篩選計數、C-R14 第 2 層首領沒有「看圖鑑」）：子代理實測，原始輸出未附（見 §9）。
9. **深層連結不受影響（D-R12-6）**：網址只帶樓層＋分頁（:3612 正則），localStorage 不存資料 id。

## 4. R0.6 影響與待決事項（v2）

**依據**：本輪任務說明的「R0.6 方案 S」和「R0.6 階段關聯」兩段，以及 GPT 第 1 輪複審第五節的相容性意見。R0.6 已核准 Gate 的條文本身，Claude 仍沒有讀到（repo 這個 SHA、本工作階段 scratchpad 和逐字稿都沒有），所以 Claude 這端**沒有逐條比對 Gate（NOT RUN）**；下表的「GPT 複審」欄是 GPT 依 R0.5 G1～G8 和 R0.6 方案 S 補強方向所做的相容性審查。**都是規劃建議，不是決定，也沒有修改 R0.6**；本清冊沒有任何一項要求 S15-B1 等待或改變。

| # | 事項 | UI-INV 的觀察 | GPT 第 1 輪複審 | v2 的處理 |
|---|---|---|---|---|
| R6-1 | 配方身份 | `r\|<ALLREC 索引>` 會被配方回報推移（D-R12-1） | 待補設計：`r\|<索引>` 不能當長期身份；階段 2 使用前要定穩定配方鍵，是否另立永久 ID 還要設計決定 | 改寫為「階段 2 前要定穩定的配方鍵」，不主張配方必須另立一種永久實體 ID |
| R6-2 | EQX `e\|x<k>`、`p\|g<k>` | 補 `fr` 就推移（B-R1） | 相容：階段 2 物品身份遷移，依 G2 釘選，不沿用流水號 | 照 GPT 意見 |
| R6-3 | fixed_links／baseline | 1,521 筆：entity 933、goview 538、route 37、search 13 | 需修正：不能先重產再用新版對新版；依 G3／G5／G6 | **v2 修正（M04）**：route＋search 50 筆不依實體 ID；階段 1.5 網站不切換、G5 維持 `IDENTICAL`；階段 2 起依已審查的 `key_map`、舊連結對照和預期修正清單核對舊新結果，沒有非預期差異才更新相關基準 |
| R6-4 | 玩家回報用名稱對資料 | reports.js 是 Apps Script 自動寫入，格式不能改（D-R12-3） | 相容：保留既有回報格式和名稱解析的過渡相容，符合 G8 | 照 GPT 意見 |
| R6-5 | 程式內寫死的名稱表 | `ITEM_OLD`、`REP_MAT`、`DG_DIM`、`NPC_ZH` 不在 check_refs 範圍（D-R12-5） | 相容但有覆蓋缺口：依資料種類分配到階段 2～4；先分清「遊戲資料身份對照」和「一般介面顯示文字」 | 分類建議（v3）：`ITEM_OLD`、`REP_MAT`＝物品名稱對照（階段 2）；`NPC_ZH`＝回報類別轉換（NPC 階段）；`DG_DIM`＝JourneyMap 資料夾映射（地點階段）。**階段表示檢查責任，不代表全部搬進 Registry 或必須刪除。** 這是 UI 端的建議分類，最後由 R0.6 決定 |
| R6-6 | 地下城地圖鍵 | SPOTS id 同時是 `tiles/dg/<id>/`、jmmeta、jm_merge.py 的鍵（D-R8） | 相容有條件：階段 3 地點遷移要維持舊 slug／資源路徑對應；G4、G8 不能自動改名或回退動態資料 | 照 GPT 意見 |
| R6-7 | 同名查找 | `npcByName`、`offOf`、`enGo` 遇到重名取第一或最後一筆（B-R3） | 相容：用 R0.6 的 ambiguous／人工確認機制，不能自動取第一或最後一筆 | 照 GPT 意見 |
| R6-8 | 資料屬性格式 | 三種屬性段數不同（D-R12-4） | 需修正：明定兩段／三段格式和合法字元 | **v2 修正（M02）**：C v2 §5.1 |

## 5. 已確認的決策和待站長決定的事項

**已確認（站長決定，v2 不再列為待決）**：
- #32：「同樓層切換分頁保留面板，切換樓層關閉面板」，**只適用桌面版裝備面板**，不擴張到手機和職業／地下城等特殊元件。

**待站長決定**：
1. **bosses／report／about／changelog 進入時關閉面板**這個既有行為，要不要正式列為 #32 的例外。不處理的後果：維持現狀（進這 4 頁面板就關）。
2. **要不要實作 #32 後半條的修正**（只限桌面裝備面板，見 §6 第 1 項）。不修的後果：桌面換樓層後，裝備面板仍開著、停在舊樓層的內容。
3. **第 2 層樓層首領 Asterius 對應哪一隻怪物**（C-R14）。不處理的後果：世界王頁第 2 層一直沒有「看圖鑑」。
4. 本次發現的線上小問題（A-R3、A-R5、A-R6、B-R2、C-R1、D-R5）**要在 UI 架構調整前先單獨修，還是併入架構調整**。本次沒有修任何東西。

## 6. 最小改動建議（都還沒做，不是決定）

依「改動小、能立即消除錯連」排序：

1. #32 後半條：在 `setFloor`／`show()` 比較新舊 `FL`，**只在桌面、換樓層、目前面板是裝備面板**（`stack` 最上層 `type==="e"`）時 `closeP()`；其他面板和手機不變（M03）。
2. `recGoBtns`／`recipeTable` 的 `findIndex` 加樓層條件（B-R2）。
3. 地圖右側清單的 `data-tp` 加入官方中文名，或改用 `townHit`／`npcHit`／`monHit`（C-R1）。
4. `gvRender` 補綁 `data-town`；`#cwBody` 的 `data-rep` 補綁定、`data-go` 不要取代右側職業頁（A-R3）。
5. `syncVTabs` 複製時移除 id（A-R1／B-R4）。
6. 看圖視窗的 Esc 監聽改成比彈出視窗優先（A-R5）。
7. `fbarSync` 改讀各篩選的 `data-def`（A-R6）。
8. 關於本站的「協作區」連結改用目前樓層的 hash（D-R5）。
9. 測試補強（不改網站）：fixed_links 加 `q|`、`c|`、`d|` 代表連結；smoke 全分頁迴圈補 npcs、dungeons、about、changelog、feedback；加「執行時重複 id」和 #32（桌面裝備面板）的檢查；baseline_capture 的起點 `m|m0` 改用穩定字串。

## 7. 執行的指令和原始輸出

### 7.1 v2 證據腳本（M05）

- 腳本：`UIINV_R0.1_evidence_v2.js`（唯讀；Node＋Playwright＋Chromium）
- 對象：新建的 detached worktree，HEAD＝`14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d`，用 `python3 -m http.server 8781 --bind 127.0.0.1` 提供
- 寬度：1280×900（A-R3、A-R13、B-R2、C-R1、重複 id）、390×844（重複 id）
- 頁面 build：`<meta name="sao-build">` = `3e4e04dbf1`
- 執行時間：2026-11-19T11:52:08Z；結束碼 **0**（每項都有觀察結果）
- 完整原始輸出：`UIINV_R0.1_evidence_v2_output.txt`（JSON 全文）

```text
$ git worktree add --detach <scratchpad>/uiinv2_src 14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d
$ git -C <scratchpad>/uiinv2_src rev-parse HEAD ; git -C <scratchpad>/uiinv2_src rev-parse HEAD:src/index.html
14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d
e9d4db271ea061d7c4f76aea22534db036847423
$ (cd <scratchpad>/uiinv2_src && python3 -m http.server 8781 --bind 127.0.0.1) &
$ node UIINV_R0.1_evidence_v2.js http://127.0.0.1:8781/index.html ; echo "exit=$?"
（摘要；全文見 output.txt）
A-R3a_popup_data-town       reproduced=true   t|tob 在地圖上查看：gv 1→1、rwin false→false、view equip→equip
                            （觸發方式：先在 #equip 開一張裝備卡，再把面板裡現有「查看」按鈕的 data-goview 改成 "map|t|tob" 後點它，讓彈出視窗打開 Starting Town；
                             這是為了在彈出視窗裡取得一個 data-town 按鈕，不是玩家的正常操作路徑；被測的是彈出視窗內 data-town 的點擊結果）
A-R3b_cwBody_data-rep       reproduced=true   item 2475，rep 1|1778|3530：rwin false→false
A-R3c_cwBody_data-go        reproduced=true   n|n1_52：crumb 戰士→Corrupted Boar Accessories、cls-inline true→false
A-R13_rule32_floor_change   reproduced=true   #equip 開 Ring of the Boar → #monsters 仍開 → #f2-equip 仍開（標題不變、樓層第 2 層）
B-R2_recipe_floor           reproduced=true   n3_0：r|4、r|5、r|7、r|8 → recipes.js 鍵 "Alchemist"；r|171～174 → "3|Alchemist"；配方回報 0 則
C-R1_zh_search_list         reproduced=true   煉金術士 NPC2／清單0；起始之鎮 NPC1 城鎮1／清單0；Alchemist 清單2；Starting 清單2
A-R1_runtime_duplicate_ids_1280 reproduced=true nMon/nEquip/nProp/nItem/nNpc 各 6；doneC/doneL 裝備頁 0、協作區 1
A-R1_runtime_duplicate_ids_390  reproduced=true 同上
pageErrors: []
exit=0
$ pkill -f 'http.server 8781'
```

### 7.2 其他指令（v1 和 v2 彙整）

```text
$ git fetch -q origin main && git rev-parse origin/main        （v1 盤點開始）
14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d

$ git fetch -q origin main && date -u +%FT%TZ && git rev-parse origin/main   （v1 彙整完成後）
2026-11-19T07:23:00Z
14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d

$ git fetch -q origin main && date -u +%FT%TZ && git rev-parse origin/main   （v2 彙整時）
2026-11-19T11:55:32Z
2e36f43a644a0663bf2d62302a2991a98b736a5e

$ TZ=Asia/Taipei git log --format='%h %ad %an %s' --date=format-local:'%m-%d %H:%M' 14f677ba..origin/main
2e36f43 11-19 16:18 Cheng-1001 處理中的回報：3 則
1fa66e2 11-19 16:15 Cheng-1001 處理中的回報：2 則
$ git diff --stat 14f677ba origin/main
 pending.js | 16 +++++++++++++++-
 1 file changed, 15 insertions(+), 1 deletion(-)
$ git rev-parse origin/main:src/index.html
e9d4db271ea061d7c4f76aea22534db036847423

$ python3 -I uiinv_tools/keycheck_v2.py uiinv/out   （v2 清冊計數、key 語法、scope 白名單、A §0 正式 key）
rows 308 alias rows 15 dedup 293 {'P0': 52, 'P2': 101, 'P1': 140} unique 293
regex fail (dedup keys) []
scope not in C§2 whitelist []
A§0 正式 key count 17 regex fail [] not in inventory []
segments {2: 45, 3: 245, 4: 3}
suffixed ['global.link.data-dgmap@f1', 'global.link.data-under@f1', 'map.dungeon-mode@f1', 'map.legend.base-button@f1-2', 'map.legend.dungeon-back@f1', 'map.legend.dungeon-select@f1', 'map.legend.layer-select@f1', 'map.panel.under-button@f1', 'panel.dungeon.map@f1', 'panel.event-dungeon.body@f1', 'panel.quest.images@f1']
popup.* ['popup.layer', 'popup.menu-rule', 'popup.window']

$ v2 表格格式檢查（compile_v2.py）
UIINV_R0.1_A_元件清冊_v2.md bad rows 0
UIINV_R0.1_B_風險清單_v2.md bad rows 0
UIINV_R0.1_D_資料依賴對照表_v2.md bad rows 0

$ sed -n '1701p;1704p' src/index.html
const recGoBtns=rows=>{const b=rows.map(x=>[x,ALLREC.findIndex(y=>y.npc===x.npc&&y.en===x.en)]).filter(([,ri])=>ri>=0);
  const ri=r.i!=null?r.i:ALLREC.findIndex(x=>x.npc===r.npc&&x.en===r.en);

$ sed -n '1422,1423p' src/index.html
function bindGo(root){root.querySelectorAll("[data-go]").forEach(b=>b.onclick=e=>{e.stopPropagation();const [t,i]=b.dataset.go.split("|");openP(t,i,"new")});
  root.querySelectorAll("[data-goview]").forEach(b=>b.onclick=e=>{e.stopPropagation();const [v,t,i]=b.dataset.goview.split("|");gvOpen(t,i)})}

$ sed -n '1475p' src/index.html
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&GVW.length){e.stopImmediatePropagation();gvClose()}},true);
```

### 7.3 v3 指令和原始輸出

```text
$ python3 -I uiinv_tools/keyvalidate_v3.py uiinv/out ; echo exit=$?
2026-11-19T15:07:06Z
== test cases
map.legend.base-button@f1-2        expected=valid   got=valid                                    PASS
map.legend.base-button@f2-1        expected=invalid got=invalid: range f2-1 (need M > N)         PASS
map.legend.base-button@f1-1        expected=invalid got=invalid: range f1-1 (need M > N)         PASS
map.legend.base-button@f2,f3       expected=valid   got=valid                                    PASS
== inventory (A v2)
rows 308 alias rows 15 formal keys 293 unique 293
formal keys valid 293 invalid 0 []
keys with a floor range ['map.legend.base-button@f1-2'] ['valid']
A§0 formal keys 17 invalid [] not in inventory []
RESULT PASS
exit=0

$ for f in A B C D E; do git diff --no-index --numstat <v1> <v2>; done     （v1→v2 差異，新增／刪除）
A_元件清冊          10   10
B_風險清單          35   34
C_命名規則          35   6
D_資料依賴對照表    26   4
E_審查摘要          200  149     ← 上次交付寫 197／146（用 diff 的 < > 計數），更正為 200／149
```

## 8. 證據檔

| 檔案 | 內容 | 是否附給 GPT |
|---|---|---|
| `UIINV_R0.1_evidence_v2.js` | v2 證據腳本（唯讀，可在任何有 Playwright 的機器對指定 SHA 重跑） | 是 |
| `UIINV_R0.1_evidence_v2_output.txt` | 上面腳本的完整原始輸出（含執行時間、HEAD、exit 碼） | 是 |
| `UIINV_R0.1_evidence_v2.js.txt` | 和 `evidence_v2.js` 逐位元組相同（副檔名改 .txt 方便下載） | 是（第 2 輪已附） |
| `UIINV_R0.1_keyvalidate_v3.py.txt` | v3 key 驗證腳本（正規表示式＋scope 白名單＋樓層範圍語意） | 是 |
| `UIINV_R0.1_keyvalidate_v3_output.txt` | 上面腳本的完整原始輸出 | 是 |
| scratchpad `uiinv/a_tools/check1.js`～`check4.js`、`uiinv/pwB/*.py`、`uiinv/c_probe.py`、`uiinv_D_tmp/d_check.py` | v1 子代理的實測腳本 | 否（原始輸出沒有保存成檔案；它們支撐的結論在 §9 標「子代理實測，原始輸出未附」） |
| scratchpad `uiinv/part_A.md`～`part_D.md`、`uiinv/parts_v2/` | 各分工原稿和 v2 修訂稿 | 否（內容已全部收進 A～E） |
| scratchpad `uiinv_tools/risks.py`、`compile_v2.py`、`v2_edit.py`、`alias.json` | 彙整和 v2 修訂腳本 | 否 |

## 9. 結論標記總覽（v2 重新分級）

- **VERIFIED（v2 證據腳本，可重現，原始輸出已附）**：A-R3（三種情況；其中 A-R3a 是人工建構狀態、非玩家正常操作路徑）、A-R13（#32 後半條）、B-R2、C-R1、A-R1／B-R4（執行時重複 id，1280 和 390）、`doneC`／`doneL` 互斥（A-R1b／D-R1）。
- **VERIFIED（v1 子代理實測，原始輸出未附）**：A-R5、A-R6、B-R3（Occult Amulet (2) 圖示）、C-R13、C-R14、D-R12-6、1280／390 無 console 錯誤、地圖和世界王頁手機無橫向捲動。GPT 尚未取得這些項目的原始證據，**不能當成已獨立複核**；需要時可以比照 v2 腳本補。
- **CODE（只讀程式碼）**：B-R1／C-R9／D-R12-1／D-R12-2 的推移機制（沒有實際製造一則配方回報）、A-R5 三個視窗同時開、`#fPrFl` 的 fbar 計數、D-R5。
- **NOT RUN**：821～1179px 寬度；第 2、3 層篩選和清單畫面；打包工具互動（需要真的 JourneyMap 資料）；手機 `#cwin`／`#rwin`；地下城地圖模式；`?edit` 校正模式；R0.6 Gate 逐條比對（Claude 端）。
- **UNKNOWN**：見附錄 E3（各分工未驗證清單）。

## 10. 任務指定的 12 項風險檢查（逐項對照）

| # | 檢查項 | 對應風險 | 結論 | 主要行號（src/index.html） | 證據等級 |
|---|---|---|---|---|---|
| 1 | 重複 HTML ID | A-R1、B-R4、A-R1b、D-R1 | 靜態：`doneC`／`doneL` 兩處定義，互斥、不會同時存在。執行時：`nMon`、`nEquip`、`nProp`、`nItem`、`nNpc` 各 6 份 | :2585、:3195、:3200–3201；:3639–3641、:713–717 | VERIFIED（v2 證據） |
| 2 | 不同元件共用 selector | A-R2a、A-R2b、A-R2c、C-R13 | `data-v` 有兩種意義（view 名／膠囊值）；`#cwin` 和 `#rwin` 共用 `.rwin`；`#cwin` 卡片和裝備分頁卡片共用 `data-key`，會一起被標成選取 | :695–703、:1420、:881–882、:3666–3668、:1888、:1237 | VERIFIED（C-R13，子代理，原始輸出未附）／CODE |
| 3 | 同功能不同名 | B-R7、清冊第 0 節（15 列重複 key） | `CODEX`／`CODEX_V` 同一份清單；`#codexTabs`／`.vtabs` 同一功能兩份 DOM；「相關任務」「用途」連結是 `t\|城鎮`；`#fItemAll` 勾了反而只看這一層；`goView` 沒有呼叫者 | :3566、:3638、:1479、:1702 等 | CODE。**涵蓋範圍**：圖鑑五分頁逐項查（B）；地圖、任務、配方、地下城、職業、世界王、協作區只在元件表順帶記錄＝NOT RUN |
| 4 | 動態按鈕能不能唯一定位 | B-R5、B-R6、C-R4、C-R5、C-R1 | 卡片：容器 id＋`data-key` 可唯一定位；膠囊：容器 id＋`data-v` 可以。不能唯一定位：面板區塊（只有 `h3.sec` 文字）、已篩選列（序號）、地圖 NPC 標記和右側清單的城鎮／首領／NPC 列（沒有身份屬性）、`.zsec`（顯示文字） | :1242–1265、:1420、:3644–3665、:3479、:3482–3500 | VERIFIED（子代理，原始輸出未附）／CODE；協作區打包工具的 `data-jmreg`、`data-jmdg` 用座標／名稱字串（CODE） |
| 5 | 事件委派依賴不穩定 DOM | A-R2c、A-R3、D-R2／A-R9 | 委派依賴 `.filters,.topf,.rsel` 三個 class；三套連結綁定涵蓋不同；`goRep` 輪詢找 `li[data-rid]` | :3666–3668、:1212–1231、:1420–1424、:1458–1470、:1894–1895、:3684–3686 | VERIFIED（A-R3，v2 證據）／CODE |
| 6 | 桌面／手機識別衝突 | A-R6、B-R4 | 沒有發現同一邏輯元件在兩種裝置用不同 id；但圖鑑子分頁是兩份 DOM，判斷寬度有 4 種寫法，手機 fbar 計數錯 | :3601–3605、:3624–3657、:1183 | VERIFIED（B-R4 v2 證據；A-R6 子代理，原始輸出未附） |
| 7 | 面板狀態依賴 DOM 存在 | A-R7、A-R14 | 面板真正狀態是 JS 變數 `stack`；但 `fitClsPanel`、`show()` 用 `panel.hidden` 判斷；面板不帶樓層，瀏覽器上一頁和面板脫鉤 | :1188、:1197、:1226、:3614、:1176–1179 | CODE／VERIFIED（A-R14 部分，子代理） |
| 8 | 切樓層／分頁時 DOM 重建 | A-R8、A-R13 | 清單、地圖標記、面板內容每次重建；樓層格子只產生一次；`setFloor` 不重建、不關閉面板（#32 後半不成立，只限桌面裝備面板這條規則） | :3593–3599、:3670、:1813–1815、:1841 | VERIFIED（A-R13 v2 證據） |
| 9 | 固定連結依賴名稱 | C-R9、B-R1、D-R12-2、C-R7、C-R11 | 網址不帶資料 id；固定的是 fixed_links／baseline／smoke。7 種陣列流水號 id；`recGoBtns`、首領重生點、地下城鑰匙用名稱 | data.js:121、489；:937、1074、1590、1742、2002、1057、1329 | CODE（推移機制）／VERIFIED（fixed_links 統計，GPT 也核對過） |
| 10 | 測試能不能定位元素 | A-R11a、附錄 E2 | smoke／site_audit／baseline 主要靠靜態 id 和 `window.__detail`／`__auditIds`，可以定位；但 baseline 和 site_audit 只比 `__detail` 回傳的 HTML，不經過面板綁定（所以 A-R3 測不到）；測試裡寫死的流水號 3 條（smoke.py:110 `q\|mq1_33`、:123 `q\|mq1_15`、baseline_capture.js:83 `m\|m0`）；導覽依賴 9 個 selector 沒有測試；#32、`.fbar`、`.rsel`、樓層選擇器、`#pBack` 沒有測試 | tests/smoke.py:110、123；tests/baseline_capture.js:55、83；:3721–3729 | CODE |
| 11 | 拆分 index.html 時必須保留的識別 | A-R11 | 相容清單：路由、面板 id、連結 data 屬性、被 JS／測試當 selector 的 class、body 狀態 class、localStorage 鍵、`window.__*` 介面；重名 `function show`（:3612／:3746）、導覽 `const esc` 遮蔽（:3720）、宣告順序（`COLLAB_PAUSE` :3135 在 `setFloor` 使用） | 見清冊 A §6／風險 B 檔 2.2 | CODE |
| 12 | R0.6 對 data-*、事件、深層連結的影響 | D-R12-1～D-R12-7 | 深層連結不受影響（網址不帶資料 id）；三種連結屬性的**實體身份部分**必須一致，格式見 C v2 §5.1，ID 不能含 `\|` 和 `"`；基準更新依 §4 R6-3（不先重產再自我比對）；玩家回報用名稱，要保留過渡查找 | :3612、:1237–1239、:1422–1423、:1464–1470、:986–1030 | VERIFIED（深層連結，子代理）／CODE |

## 11. 本輪驗收標準對照（任務第十三節）

| # | 驗收標準 | v2 狀態 |
|---|---|---|
| 1 | 全站主要分頁與功能區完整盤點 | 14 個 view 全部有元件列（含 `feedback` 子分頁）；第 2、3 層畫面、821～1179px 沒有實測（NOT RUN） |
| 2 | 每個重要元件可回溯到程式碼 | 每列有 `source_location`；P0／P1 都有行號 |
| 3 | 相似元件不會因命名而混淆 | 清冊第 0 節列出 15 列重複 key 的正式名稱；C v2 §1 規定一個 key 只代表一個元件、合併列已拆開 |
| 4 | 桌面及手機共用關係清楚 | 每列有 `desktop_mobile`；C v2 §4 |
| 5 | 動態元件有穩定定位方法 | C v2 §5、§5.1；不能唯一定位的列在 §10 第 4 項 |
| 6 | UI 識別與遊戲資料永久 ID 明確分離 | C v2 開頭和 §5：component_key 不含資料身份，資料身份由 R0.6 定 |
| 7 | R0.6 資料依賴能追溯到實際程式 | 依賴表 45 筆，每筆有程式碼位置 |
| 8 | 不變更任何已核准 R0.6 決策與 Gate | 沒有變更；Claude 端沒讀到 Gate 條文，相容性審查由 GPT 第 1 輪完成（§4） |
| 9 | 不修改網站及 GitHub | 沒有修改；兩個 worktree 的 `git status` 都乾淨 |
| 10 | 結論區分 VERIFIED／UNKNOWN／NOT RUN | 每項結論都有標記；v2 把 VERIFIED 再分成「v2 證據，可重現」和「子代理實測，原始輸出未附」（§9） |

## 12. 交付分段說明

- 七份檔案（A～E 的 `_v2`、證據腳本、證據輸出）都依同一個基準 SHA `14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d`。
- A 元件清冊是完整清冊，不是摘要；篇幅大，以檔案交付；需要時可以依分工 A／B／C／D 四段貼在對話。
- v1 五份檔案保留不動（SHA-256 和 v1 交付時相同）。

---
## 附錄 E1（分工 A）：#32 面板切換規則盤點


站長決策：「同樓層切換分頁保留面板，切換樓層關閉面板」，只適用桌面版裝備面板。

**程式裡處理面板的位置**（CODE）：

- 切分頁：`show()` :3614 一行裡有 4 個條件：
  1. 離開 classes／dungeons，而且面板是內嵌的職業／地下城（看 `stack[0]`），桌面（`innerWidth>820`）→ `closeP()`。
  2. 進入 `report`、`bosses`、`about`、`changelog` → `closeP()`（桌面和手機都一樣）。
  3. 手機（`matchMedia max-width:820px`）、view 改變、不是 `goView` 造成的（`!viewPending`）→ `closeP()`。
  4. 其他情況：**保留**。
- 進入 classes／dungeons：`renderClasses` :1841、`renderDungeons` :1813–1815 在桌面會用 `openP(...)` **取代**目前的面板（不是 push），原本的裝備面板就不見了；回到裝備分頁時，條件 1 會把內嵌面板關掉，所以裝備面板不會回來。
- 切樓層：`pickFloor` :3588–3590 → `go(view,f)` → `show()` → `setFloor` :3593–3599。`setFloor` **沒有 `closeP()`、沒有碰 `stack`、沒有重畫 `#pBody`**；`show()` 的條件 1～3 都只看 view 有沒有變，同分頁換樓層一個都不成立。

**實測**（VERIFIED，check1：在 `#f1-equip` 打開第一張裝備卡片，再做下面的操作）：

| 操作 | 桌面 1280 面板 | 手機 390 面板 | 規則要求（桌面） | 符合？ |
|---|---|---|---|---|
| 切到 `#f1-monsters` | 開著，仍是裝備 | 關閉 | 保留 | 桌面符合 |
| 切到 `#f1-map` | 開著，仍是裝備 | 關閉 | 保留 | 桌面符合 |
| 切到 `#f1-quests` | 開著，仍是裝備 | 關閉 | 保留 | 桌面符合 |
| 切到 `#f1-classes` | 開著，換成職業頁（戰士，內嵌） | 關閉 | **不適用**（站長決定：規則不擴張到職業／地下城等特殊元件） | 排除範圍，不列為違規 |
| 切到 `#f1-dungeons` | 開著，換成地下城頁（Sanctuary of Souls，內嵌） | 關閉 | **不適用**（同上） | 排除範圍，不列為違規 |
| 切到 `#f1-bosses`（report、about、changelog 同一條件） | 關閉 | 關閉 | 保留 | 既有的特殊關閉行為，**待確認的例外**，不混入換樓層缺陷 |
| 同分頁換樓層 `#f2-equip` | 開著，仍是第 1 層那件 | 開著 | 關閉 | **不符合** |
| 用樓層選擇格子 `.flcell[data-f=2]` | 開著 | 開著 | 關閉 | **不符合** |
| 換樓層＋換分頁 `#f2-monsters` | 開著 | 關閉（因為換分頁） | 關閉 | **不符合**（桌面） |
| 第 2 層裝備面板 → `#equip`（回第 1 層） | 開著 | 開著 | 關閉 | **不符合** |

**結論（v2，依 GPT 複審 M03 修正）**：
- 規則範圍：站長已決定，只適用**桌面版裝備面板**；手機、職業／地下城等特殊元件不在範圍內，所以上表 classes／dungeons 兩列是排除範圍，不是違規。
- 前半條「同樓層切換分頁保留面板」：一般分頁（monsters、map、quests 等）**符合**。bosses／report／about／changelog 會關面板，這是既有的特殊關閉行為，列為**待確認的例外**，和換樓層缺陷分開處理。
- 後半條「切換樓層關閉面板」：**不符合**（VERIFIED，另見 v2 證據腳本 `A-R13_rule32_floor_change`）。任何換樓層方式都不關面板，面板停在舊樓層的內容。
- 修法範圍（建議，未實作）：只在**桌面**、**換樓層（新舊 `FL` 不同）**、而且**目前面板是裝備面板**（`stack` 最上層 `type==="e"`）時呼叫 `closeP()`。其他種類的面板（怪物、道具、NPC、內嵌的職業／地下城等）和手機都不受影響。要不要擴大到其他面板，不在 #32 範圍內，另外由站長決定。
- 附帶：關閉後 `#pCrumb` 不清空（A-R7）。

**A-R13｜中｜:3593–3599、:3614｜#32 規則「切換樓層關閉面板」不成立（桌面裝備面板）**：問題、影響、修法見上面結論。**需要程式修改**：是（一處：`setFloor`／`show()` 在桌面、換樓層、目前面板是裝備面板時 `closeP()`，不影響其他面板）；bosses／report／about／changelog 的關閉行為另列待確認例外，不在這項修法裡。**證據**：check1 實測表；v2 證據腳本 `A-R13_rule32_floor_change`。

---


## 附錄 E2（分工 A）：既有回歸測試涵蓋


### 7.1 `tests/fixed_links.json` 統計（1,521 筆，CODE）

| type | 筆數 | 細分 |
|---|---|---|
| entity（`data-go` 的值） | 933 | e 233、i 194、m 180、p 109、n 95、r 69、s 45、t 8；**沒有 q（任務）、c（職業）、d（活動地下城）** |
| goview（`data-goview`） | 538 | recipes 293、equip 188、props 57 |
| route（hash） | 37 | 11 個分頁 × 第 1～3 層＝33，加 `#f1-report`、`#f1-feedback`、`#f1-about`、`#f1-changelog` |
| search | 13 | items 4、equip 4、monsters 2、props 1、npcs 1、recipes 1（含舊名 Shark Shell、Leaf Fragment、Pumba's Ring） |

沒有收的連結種類：`data-repgo`、`data-rep`、`data-route`、`data-imap`、`data-spot`、`data-town`、`data-eqcls`、`data-imgzoom`、`data-dgmap`、`data-under`、`data-cwe`。

### 7.2 各測試怎麼測

| 測試 | 涵蓋 | 方法（selector／掛鉤） | 缺口 |
|---|---|---|---|
| `baseline_capture.js`／`baseline_compare.js` panels | 所有 type 的面板內容（m、e、p、i、r、n、q、s、t、c） | `window.__auditIds()` 列 id，`window.__detail(t,i)` 取 HTML 字串，比文字、連結目標、圖片的雜湊（:62–77） | **只比 HTML 字串**，不經過 `renderP`／`gvRender`／`bindGo`，所以綁定（A-R3）和 `zhHTML` 以外的後處理（`srcMerge`、手機 `srcfold`）不在裡面；`__auditIds` 沒有 `d`（活動地下城，:2192） |
| baseline routes | 33＋4 個 hash | 設 `location.hash`，讀 `[id^="view-"]` 哪個 `display!=="none"` 和 `location.hash`（:126–141） | 只看顯示哪個 view，不看面板、彈出視窗、選單 `aria-current`；不測不合法 hash（A-R12） |
| baseline searches | 13 個詞 | `#q` 填字，讀 `#view-<v> .card[data-key]` 可見的 key（:143–154） | 只有 6 個分頁；地圖搜尋（`.shide`、`#srchHint`）不在內 |
| fixed_links entity | 933 筆 | 打開 `.card[data-key="m\|m0"]` 的面板，把面板裡第一個 `[data-go]` 改成目標再點，讀 `#pBody` 前 60 字（:80–94） | 全部只走「面板內 push」這一條路；清單卡片、彈出視窗、內嵌頁、`#cwBody` 的 `data-go` 行為沒測；只比前 60 字 |
| fixed_links goview | 538 筆 | 打開 `#view-equip` 的 `e\|1760` 面板，把 `[data-goview]` 改目標再點，讀最上面 `.gvbox` 文字（:96–124） | 只測一層彈出視窗；彈出視窗內再點（`gvLink`）不在內 |
| baseline transfer | 手機冷快取傳輸量、橫向捲動 | CDP `Network.loadingFinished`（:156–171） | 只有首頁 |
| `site_audit.js` | 所有面板的 HTML 內容 | 同樣用 `__auditIds`／`__detail`；找錯誤字樣、壞 `data-go`（跳過 t、d、wb）、壞圖、佔位 emoji | 同 baseline，只看 HTML 字串，不點擊 |
| `smoke.py` 全分頁載入 | 第 1～3 層 × map、monsters、items、props、recipes、quests、equip、classes、bosses、report；1280 和 390 | `goto #f{f}-{v}`，收 pageerror，手機檢查 `scrollWidth>innerWidth`（:44–56） | **沒有 npcs、dungeons、about、changelog、feedback** |
| smoke 新版提示 | `#updBar` | `__updCheck()`＋攔截 `index.html?_=*` 改版號，點 `.ub-go`（:58–73） | — |
| smoke 面板 | 怪物、任務、裝備、配方、NPC、職業、地下城面板內容；Esc 關看圖保留面板；內嵌頁沒有 ✕、Esc 不關；彈出視窗 Esc 只關最上面、不關面板 | `#lMon .card`、`[data-go='q\|mq1_33']`、`#pBody`、`#pClose`（18 次）、`.imgzoom`、`.gvback`、`__gv`、`cls-inline` | `#pBack` 0 次；**沒有測「切分頁／切樓層時面板留不留」（#32）**；沒有測看圖在彈出視窗上的 Esc（A-R5） |
| smoke 浮動視窗 | 路線視窗開、縮放、關；物品取得地點；職業裝備視窗開、裝備詳細、返回 | `#rwin`、`#rwSvg`、`#rwTitle`、`#cwin` | 沒有測 `#cwBody` 裡的座標、連結（A-R3） |
| smoke 關於本站 | 選單 3 項、點外面關、更新紀錄、導覽不自動開、略過 | `#aboutBtn`、`#aboutMenu`、`#tourBtn` | — |
| smoke 列表共用 | 已篩選列、`.topf`、`.vtabs`、效果篩選、卡片欄數固定 | `.actf`（7 次）、`.topf`（1）、`.vtabs`（3）、`#fEqEff`、`__effPick` | **`.rsel` 0 次、`.fbar` 0 次**（所以 A-R6 的「已調整 1 項」沒被抓到）；手機篩選收合沒測 |
| smoke 樓層 | 只透過 hash 進第 2、3 層 | `goto #f2-...` | **`#flTrig`、`.flcell`、`#flJump` 0 次**；`#floorInfo` 內容只檢查了 `pauseBar`（1 次）、`legalBtn`（1 次） |
| smoke 搜尋 | 舊名、中文 NPC、任務獎勵、套裝名、地圖搜尋 | `#q` | — |

### 7.3 涵蓋缺口摘要

1. **#32 面板規則完全沒有測試**（切分頁、切樓層時面板狀態）。
2. **連結綁定只測「面板內 `data-go`」和「一層 `data-goview`」**；彈出視窗內的 `data-town`、`#cwBody` 內的 `data-rep`／`data-go` 沒測，實測已發現 3 個問題（A-R3）。
3. **Esc 組合**只測了 2 種（看圖在面板上、彈出視窗在面板上）；看圖在彈出視窗上、面板＋路線視窗同時開都沒測（A-R5）。
4. smoke 的全分頁載入迴圈少 npcs、dungeons、about、changelog、feedback 5 個分頁（baseline routes 有，但只看顯示哪個 view，不檢查手機橫向捲動）。
5. 手機專用元件（`.fbar`、`#codexTabs` 在手機的點擊、`srcfold`）、樓層選擇器 UI、`#pBack` 沒有直接測試。
6. fixed_links 沒有 q／c／d 的 entity，也沒有 `data-repgo` 等 10 種連結屬性。
7. 執行時重複 id（A-R1）沒有測試會檢查。

---


## 附錄 E3-A：分工 A 未驗證／UNKNOWN


- 四種斷點寫法（A-R6）在 820／821px 邊界的行為沒有逐一實測（NOT RUN）；只實測了 1280 和 390。
- 面板＋路線視窗＋職業裝備視窗三個同時開、一次 Esc 全關：CODE（只實測了面板＋路線視窗兩個）。
- `data-route`／`data-imap` 按鈕在手機隱藏：只讀 CSS :175（CODE），沒有量 computed style。
- `data-dgmap`／`data-under` 的細節（地下城地圖切換、地下截圖）屬於地圖分工，這裡只記綁定方式。
- 導覽 `saoTour` 在拆分後每一步的 selector 是否都還找得到：CODE 列出，沒有逐步實測。
- `goView`（:1479）是否有 repo 以外（例如書籤小工具、使用者腳本）在呼叫：UNKNOWN；repo 內沒有呼叫者。
- 協作區 `buildReport`（:2555）是否還有人打算恢復舊 GitHub issue 流程：UNKNOWN（目前 `FORM_PREFILL` 永遠有值，它不會執行）。
- `#32`（v2）：classes／dungeons 取代面板是**排除範圍**（站長已決定規則只適用桌面裝備面板，不擴張到職業／地下城等特殊元件），不是待決事項；bosses／report／about／changelog 進入時關閉面板是既有特殊行為，列為**待確認的例外**，由站長決定是否正式列入。
- 手機換樓層時面板是否也要關：規則只講桌面，UNKNOWN。


## 附錄 E3-B：分工 B 未驗證／UNKNOWN


- 第 2、3 層的五個分頁只跑了 NPC（`#f3-npcs`）和面板 HTML（`__detail`，不分樓層）；第 2、3 層的篩選和清單畫面 NOT RUN。
- 821～1179px 寬度（`fixCols` 不固定欄數、`.topf` 和 `.rsel` 是否換行）NOT RUN；只測 1280 和 390。
- 彈出視窗（gv）裡點連結的換頁／疊視窗規則：只讀程式碼（CODE，1440-1470），沒有在本區實測（smoke 557-565 有測）。
- `Occult Amulet (2)` 該用哪個圖示：只確認它和第 1 層那件用同一張圖（VERIFIED），遊戲裡實際長怎樣以 CLAUDE.md 的描述為準，沒有看截圖。
- `monPos` 用怪物名稱比對 `spot.mons`：回報改名後地點會不會對不到，沒有實測（renameMon 會把舊名放進 aka，monPos 也查 aka，所以應該對得到，CODE）。
- 重名 NPC（Traveling Merchant ×8 等）目前沒有配方或回收資料，`npcByName` 取第一個的影響沒有實例，屬於潛在風險。
- `r\|N` 因自動收錄的配方回報而移位：依程式順序推得（1668-1674 在 1742 之前），沒有實際製造一則回報測試。
- CLAUDE.md 和程式的差異：CLAUDE.md 寫 `goView()`「保留給其他地方用」，程式裡沒有任何呼叫（CODE）；怪物頭像 CLAUDE.md 檔案表寫官網新聞圖，程式先用 `mobcodex.js` 的圖鑑截圖（1138-1141 註解寫 2026-11-18 站長決定），CLAUDE.md 有提到 mobcodex（2 處），沒有逐字核對。其餘（效果篩選 datalist 已拿掉、怪物面板「位置」合併）CLAUDE.md 後段已寫成取代，不算差異。


## 附錄 E3-C：分工 C 未驗證／UNKNOWN


- **手機上 `#cwin`、`#rwin` 的行為**：手機的職業面板不會自動打開，所以沒實測手機點「可用的裝備」的版面和拖曳（NOT RUN）。`#rwin` 在手機上由 `showPoints` 改走 `goMapThen`，只讀了程式碼（CODE）。
- **地下城地圖模式**：`#layerSel`、`#dgBack`、`dgFit` 的實際畫面沒有實測（NOT RUN；CLAUDE.md 說 jm_pack_test.py 有測）。
- **`#jmCredit`／`#mapNote` 的手機收合**：切到探索地圖後的展開行為沒有實測（NOT RUN）。
- **`?edit` 校正模式**：只讀了程式碼和 smoke.py:602–605，沒有實測放置和匯出（NOT RUN）。
- **第 3 層地點 id 是不是由工具產生**：data23.js 的第 3 層地點 id 看起來是由英文名截短（例如 `f3dungeonthemyst`），但沒找到產生它的工具，無法確定重產時 id 會不會變（UNKNOWN）。
- **第 2 層樓層首領 "Asterius" 和怪物資料 "Taurus" 是不是同一隻**：UNKNOWN，要由站長確認，本盤點不判斷。
- **NPC、城鎮、首領列的搜尋**：C-R1 只實測了「煉金術士」「起始之鎮」兩個詞，其他官方中文名沒有逐一測試；依程式碼判斷，其他詞的結果會一樣（CODE）。


## 附錄 E3-D：分工 D 未驗證／UNKNOWN


1. 打包工具的互動（`data-jmreg`、`data-jmdg`、`#jmPop`、`data-jmzoom`、`data-jmmode`／`data-jmsw`／`data-jmfull`）：沒有真的 mp 資料夾，NOT RUN；以 tests/jm_pack_test.py:141–281 的步驟為證據。
2. `#fbL` 顯示「目前沒有處理中的問題或建議」時，雲端是否真的連上 GitHub API：沒分辨（D-R4）。
3. （已查：`p|g<k>` 在 L2297–2301 依 sets.js potions 順序產生。）
4. 支線任務有多少筆沒有自己的 `id`、因而用 `f<f>q<i>` 流水號：未統計。
5. fixed_links.json 的 entity／goview 是從基準時所有面板裡的 `[data-go],[data-goview]` 收集（tests/baseline_capture.js:70、269–274），沒有 `q|`、`c|`、`d|` 前綴；為什麼面板裡收不到這三種（例如怪物面板的「相關任務」應該有 `q|`）沒有再追，UNKNOWN。
6. `gachaHTML`、`renderBosses` 名稱比對的細節：只看到呼叫處，沒逐行讀。
7. 裝備數值覆蓋（gamestats／eqPatch）的確切行號：只粗定位在 L2100–2130 附近。
8. D-R12-1 的推移只依程式推論（L1668–1675 全文已讀；目前 reports.js 沒有配方回報，無法實測）。

