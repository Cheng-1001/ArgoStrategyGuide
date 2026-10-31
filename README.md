# ArgoStrategyGuide

SAO Minecraft（saominecraft.com）的 Aincrad 樓層查詢工具：地圖、怪物、物品、支線任務互相連結。

網站：https://cheng-1001.github.io/ArgoStrategyGuide/

資料來源：
- [SAO Minecraft Wiki](https://saominecraft.wiki.gg/)（怪物圖鑑、樓層地圖、支線任務）
- [官方物品圖鑑](https://saominecraft.com/wiki)（物品名稱、稀有度、數值、圖示）
- 玩家提供的遊戲內座標

第 2、3 層為開放前的 wiki 資料，開放後可能變動。

## 回報資料

到網站的「回報」分頁填 Google 表單（需附遊戲截圖），審核員核准後自動更新到網站。設定方式見 [google/SETUP.md](google/SETUP.md)。

## 開發

- 編輯 `src/index.html`（頁面）或根目錄的資料檔，再執行 `python3 src/build.py` 產生 `index.html`。
- 測試：`python3 tests/smoke.py`（需要 Python Playwright）。
- 專案說明與待辦：[CLAUDE.md](CLAUDE.md)。
