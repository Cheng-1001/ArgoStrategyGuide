# 本機待辦：用資源包補「官網沒收錄的裝備」圖示

狀態：待辦（2026-11-06 使用者：「跟怪物圖鑑錄影一樣待辦」）。站長有空時，把下面整段貼給電腦上的本機 Claude Code（在 ArgoStrategyGuide 資料夾裡開）。
做完後回雲端說「本機圖示好了」，雲端檢查每件圖示、給預覽連結，站長說「上線」才發佈。

```text
請幫我用資源包補「官網沒收錄的裝備」圖示。規則：資源包只在這台電腦分析，GitHub 只能放選好的 64px 圖示；不要 commit 資源包、其他貼圖、模型檔，也不要 commit equip_icon_candidates.png。

1. 切到預覽分支並更新：
   git fetch origin claude/affectionate-heisenberg-o71cvy
   git checkout claude/affectionate-heisenberg-o71cvy
   git pull origin claude/affectionate-heisenberg-o71cvy

2. 先讀 tools/equip_icons.py 開頭的說明和 tools/equip_icons.json。json 裡 "_todo" 是網站上還是佔位圖示的 22 件，先做這些；"_rebuilt" 是雲端從截圖還原的 10 件，資源包有原圖的話也換掉。

3. 列出候選圖（會在目前資料夾產生 equip_icon_candidates.png）：
   python tools/equip_icons.py find "C:\Users\Administrator\AppData\Roaming\.Triggers Client\instances\Sword Art Online\resourcepacks\sao.zip"
   找不到的再加關鍵字重跑，例如：
   python tools/equip_icons.py find "<同上路徑>" shark requin collier bague bracelet gants
   武器、盾、箭袋（Dagger of Albal、Dague glacé、Galiath's Axe、Four-Armed Halberd、Colossus Pavise、Rhitta、Lostvayne、Nodachi Staff、Iron Quiver、Hunter's Quiver）是 3D 模型，要找物品模型（models/item/…json）用到的貼圖，或另外的背包圖示貼圖。

4. 打開候選對照圖，逐件挑出正確的貼圖，把路徑填進 tools/equip_icons.json 對應名稱的值。要對照遊戲畫面（拍賣場、製作視窗、背包）確認是同一件；名稱或外觀不確定就留空 ""，放錯比佔位圖示更糟。

5. 產生圖示：
   python tools/equip_icons.py build "C:\Users\Administrator\AppData\Roaming\.Triggers Client\instances\Sword Art Online\resourcepacks\sao.zip"

6. 檢查：
   python src/build.py
   python tests/smoke.py
   要看到 ALL PASSED。再開 index.html 的裝備分頁，搜尋 Elite、Shark、Glacial、Frozen、Spider、Nepenthes、Rhitta，確認圖示正確、清楚、沒有選錯。

7. 在 changelog.js 最上面那一天加一行：「官網沒收錄的裝備改用遊戲原圖示（N 件）」，N 填實際數量。

8. 只 commit 這些檔案：tools/equip_icons.json、icons/game/ 裡新產生或更新的 png、gameicons.js、index.html、changelog.js。commit 前用 git status 確認沒有 sao.zip、equip_icon_candidates.png 或其他貼圖。
   commit 訊息：「官網沒收錄的裝備改用資源包圖示（本機 equip_icons.py）」
   推到預覽分支，不要推到 main：
   git push origin claude/affectionate-heisenberg-o71cvy

9. 最後回報：每件選了哪個貼圖路徑、哪些留空和原因、commit 編號。
```
