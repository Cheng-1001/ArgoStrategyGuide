# 基本網站更新紀錄（架構修正期間）

交接：HANDOFF_BASIC_UPDATES_V2（2026-11-23）。這條工作線只改資料檔和文字，不碰 `src/index.html` 的程式、`registry/`、`tools/check_refs*`、`tests/fixed_links.json`、`tests/baseline_capture.js`／`baseline_compare.js`、JourneyMap 相關檔案和身份類資料。

## 上線紀錄

每次 cheng 說「上線」、合併到 main 後加一行。

| 日期 | 上線後的 main commit | 改了哪些檔案 | baseline_compare 改變的面板數 | 有沒有碰到第 3 節的範圍 | 7 個檔案和 bd073255 | recipes.js 列數 | NPC 數（第 1／2／3 層） |
|---|---|---|---|---|---|---|---|
| 2026-11-24（台灣） | `4d3e09745e3db7287e9fe453eea35ea207ca5248`（bd07325 快轉；34b86f4＋4d3e097）；交接紀錄 `f2fd057ae39ed2a680f4a163c5d57e4582a6d46c` | tools/build_recipes.py→recipes.js、tools/build_npcs.py→npcs.js、zhnames.js、gameinfo.js、sets.js、data23.js、changelog.js、CLAUDE.md、docs/BASIC_UPDATES_LOG.md、index.html、build/registry_report.md、tests/baseline/panels.json、transfer.json | 164（新 53）；剩 3 筆 E5（見下） | 沒有 | 相同（2026-11-24 對 f2fd057 補查） | 315→354 | 82／44／66 → 82／53／66 |

## in30 A 批（2026-11-23 做、2026-11-24 上線）

- 起點：main `bd07325`
- 改的檔案：`tools/build_recipes.py`→`recipes.js`、`tools/build_npcs.py`→`npcs.js`、`zhnames.js`、`gameinfo.js`、`sets.js`、`data23.js`、`changelog.js`、`CLAUDE.md`、`index.html`（build）、`build/registry_report.md`、`tests/baseline/panels.json`、`tests/baseline/transfer.json`
- `recipes.js`：只加在最後（舊 315 列是新 354 列的前綴，`r|0`～`r|314` 不變）；新的 `r|315`～`r|353`
- `npcs.js`：第 2 層 NPC 從 44 位變 53 位（加在第 2 層陣列最後），新的 `n|n2_44`～`n|n2_52`
- 新支線 `q|f2q7`～`q|f2q9`；新的官網沒有的藥水 `p|g32`、`p|g33`（加在 sets.js potions 最後，`p|g1`～`p|g31` 不變）
- 引用檢查：E1 83、E2 28、E3 1、E9 0（和起點相同），沒有新例外、沒有 stale
- baseline_compare：164 個面板改變（新面板 53），逐一看過；重拍 `panels.json`、`transfer.json`；剩 3 筆 E5：`p|2408`、`p|2410`、`p|2416` 的說明換成遊戲中文（同一筆資料，`fixed_links.json` 存的是舊法文說明，沒有改）
- 碰到第 3 節的範圍：沒有（`baseline_capture.js` 執行時也改寫了 `tests/fixed_links.json` 和 `tests/baseline/fixtures/`，都已還原、沒有提交）

## in30 A 批待決五項（2026-11-24 站長「①A ②A' ③A ④A ⑤B」，工作分支，還沒上線）

- 起點：main `f2fd057`
- 改的檔案：`tools/build_recipes.py`→`recipes.js`、`data23.js`（SAO23_ITEMS 最後兩件劣質法杖、EXTRA note）、`zhnames.js`、`gameinfo.js`、`changelog.js`、`CLAUDE.md`、`registry/exceptions.json`（只刪 1 筆 stale：`recipe:3|Refaiter/out:金合歡細繩`，站長同意）、`index.html`、`build/registry_report.md`、`tests/baseline/panels.json`、`transfer.json`
- `recipes.js`：`r|309`（廢鐵護符）同一列加材料「廢鐵細繩 ×1」、拿掉 MISS；新增 `r|354`、`r|355`（裝備商人最後）；其他列不變
- 新的遊戲才有裝備 `e|x62`、`e|x63`（SAO23_ITEMS 最後，舊的 x 編號不變）
- 引用檢查：E1 82（少的就是刪掉的那筆例外）、E2 28、E3 1、E9 0；例外 112→111
- baseline_compare：38 個面板改變＋6 個新面板，逐一看過後重拍；E5 5 筆＝原本的 3 種錠＋Bull Horn、Reinforced Skeleton Bone（同一筆資料，標題換成中文）
- 碰到第 3 節的範圍：`registry/exceptions.json`（站長 2026-11-24 同意刪那一筆；沒有新增、沒有核准任何例外）
- 7 個檔案和 bd073255：相同（afce191 實際檢查）
- recipes.js 列數 354→356；NPC 數 82／53／66（不變）
- **和交接 V3 第 5a 節第 6 點衝突，待 cheng 決定再上線**：V3 寫「金合歡細繩的例外照舊留在待架構處理」，但這批照 cheng 11/24 的 ④A 已刪掉那筆例外（afce191，還沒上線）。

## 待架構處理

- **同一層有同名的 NPC（D6 B14／C8 類）**：第 2 層「第 2 層 - 烏爾巴斯鐵匠」和「第 2 層 - 烏爾巴斯鐵匠 (2)」（in30 A 批，已在 main 4d3e097）。遊戲裡兩位的視窗標題相同（一位做鋁土礦錠、不純黑瑪瑙錠，約 X 76 Z -427；另一位只做純淨黑瑪瑙錠，約 X 109 Z -412），網站內部名稱用「 (2)」區分，畫面顯示同名；物品取得途徑「製作地點：第2層-烏爾巴斯鐵匠」只能連到第一位，純淨黑瑪瑙錠的製作地點寫在 note。沒有合併也沒有指定。原本第 3 層的 Equipment Merchant ×2、Consumables Merchant ×2、符文工匠 ×2 不變。

- 第 2、3 層支線沒有 NPC／座標欄位（`SAO23.floors{}.quests[]` 只登記 title、d、en、steps、xp、money、src、date）：in30 三個支線的接任務 NPC 先寫在 `data23.js` 註解（歐利克斯 約 X 90 Z -389、德雷爾 約 X 69 Z -343、暮風 沒有座標）。
- 收購清單只支援第 1 層：當地樵夫（相思木板 13、金合歡粉末 28）、當地礦工（鋁土礦錠 21、不純黑瑪瑙錠 70、純淨黑瑪瑙錠 250）、瑪羅姆收購商（骨髓粉末 7）、凱洛爾收購商（泥土羽毛 7）寫在 gameinfo note。
- `tests/fixed_links.json` 的 3 筆 E5（見上）要不要更新。
- ~~「金合歡細繩」的 stale 例外~~：站長 2026-11-24 同意刪除，已處理。
- 配方列要插在已上線的 NPC 區塊中間的：材料重塑師的廢鐵細繩（COMMON 1 分鐘 15 珂爾：鐵礦 2、廢鐵碎片 4、蛛絲 4）、鍊金術師助手的品質凶猛強化劑 II（RARE 1 分鐘 15 珂爾：強化骷髏骨 12、阿爾巴爾之牙 2、公牛角 4、琥珀萼片 8）。`r|N` 依陣列順序，插入會移動後面的編號，等架構的配方編號方案。
