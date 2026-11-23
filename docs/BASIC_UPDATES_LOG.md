# 基本網站更新紀錄（架構修正期間）

交接：HANDOFF_BASIC_UPDATES_V2（2026-11-23）。這條工作線只改資料檔和文字，不碰 `src/index.html` 的程式、`registry/`、`tools/check_refs*`、`tests/fixed_links.json`、`tests/baseline_capture.js`／`baseline_compare.js`、JourneyMap 相關檔案和身份類資料。

## 上線紀錄

每次 cheng 說「上線」、合併到 main 後加一行。

| 日期 | commit | 改了哪些檔案 | baseline_compare 改變的面板數 | 有沒有碰到第 3 節的範圍 |
|---|---|---|---|---|
| （in30 A 批：還沒上線） | | | | |

## in30 A 批（2026-11-23，工作分支，還沒上線）

- 起點：main `bd07325`
- 改的檔案：`tools/build_recipes.py`→`recipes.js`、`tools/build_npcs.py`→`npcs.js`、`zhnames.js`、`gameinfo.js`、`sets.js`、`data23.js`、`changelog.js`、`CLAUDE.md`、`index.html`（build）、`build/registry_report.md`、`tests/baseline/panels.json`、`tests/baseline/transfer.json`
- `recipes.js`：只加在最後（舊 315 列是新 354 列的前綴，`r|0`～`r|314` 不變）；新的 `r|315`～`r|353`
- `npcs.js`：第 2 層 NPC 從 44 位變 53 位（加在第 2 層陣列最後），新的 `n|n2_44`～`n|n2_52`
- 新支線 `q|f2q7`～`q|f2q9`；新的官網沒有的藥水 `p|g32`、`p|g33`（加在 sets.js potions 最後，`p|g1`～`p|g31` 不變）
- 引用檢查：E1 83、E2 28、E3 1、E9 0（和起點相同），沒有新例外、沒有 stale
- baseline_compare：164 個面板改變（新面板 53），逐一看過；重拍 `panels.json`、`transfer.json`；剩 3 筆 E5：`p|2408`、`p|2410`、`p|2416` 的說明換成遊戲中文（同一筆資料，`fixed_links.json` 存的是舊法文說明，沒有改）
- 碰到第 3 節的範圍：沒有（`baseline_capture.js` 執行時也改寫了 `tests/fixed_links.json` 和 `tests/baseline/fixtures/`，都已還原、沒有提交）

## 待架構處理

- 第 2、3 層支線沒有 NPC／座標欄位（`SAO23.floors{}.quests[]` 只登記 title、d、en、steps、xp、money、src、date）：in30 三個支線的接任務 NPC 先寫在 `data23.js` 註解（歐利克斯 約 X 90 Z -389、德雷爾 約 X 69 Z -343、暮風 沒有座標）。
- 收購清單只支援第 1 層：當地樵夫（相思木板 13、金合歡粉末 28）、當地礦工（鋁土礦錠 21、不純黑瑪瑙錠 70、純淨黑瑪瑙錠 250）、瑪羅姆收購商（骨髓粉末 7）、凱洛爾收購商（泥土羽毛 7）寫在 gameinfo note。
- `tests/fixed_links.json` 的 3 筆 E5（見上）要不要更新。
- 「金合歡細繩」＝官網 2374（說明逐句對上）：加中文名會讓 `registry/exceptions.json` 的 `recipe:3|Refaiter/out:金合歡細繩` 變 stale，要站長同意刪那筆例外。
