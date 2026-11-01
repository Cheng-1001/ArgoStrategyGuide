# ArgoStrategyGuide

SAO Minecraft（saominecraft.com）的艾恩葛朗特（Aincrad）樓層查詢工具：地圖、怪物、裝備、配方、任務、職業技能、世界王互相連結。

網站：https://cheng-1001.github.io/ArgoStrategyGuide/

此攻略由中文玩家社群協力製作，提供中文玩家使用。

## 遊戲官方連結

- 遊戲官網：https://saominecraft.com/
- 官方 Discord：https://discord.gg/HdHba5awgn （官網上的邀請連結；開放時段異動、維護等公告會發在這裡）

## 資料來源

| 來源 | 用在哪裡 |
|---|---|
| [SAO Minecraft Wiki](https://saominecraft.wiki.gg/)（[Floor 1](https://saominecraft.wiki.gg/wiki/Floor_1)、[Bestiary](https://saominecraft.wiki.gg/wiki/Bestiary)） | 怪物圖鑑、掉落物、樓層地圖（`floor1.jpg`、`floor2.jpg`）、支線任務、主線任務表與編號 8～18 |
| [官方物品圖鑑](https://saominecraft.com/wiki) | 物品與裝備的名稱（法文原文）、稀有度、數值、描述、圖示與 3D 預覽截圖 |
| [官方世界首領頁](https://saominecraft.com/world-boss) | 世界王 Galiath、獨特怪物 Seraphel |
| [SAO MC Interactive Map](https://delayedcode.github.io/SAO-MC-Interactive-Map/)（DelayedCode 製作的參考互動地圖，[repo](https://github.com/DelayedCode/SAO-MC-Interactive-Map)） | 第 1 層的座標與地名、NPC 位置與類別、區域首領重生點、配方材料、主線任務步驟順序。該 repo 沒有授權條款，所以只取座標、名稱、數量這類事實資料，不使用它的描述文字、程式碼或區域範圍；網站上這些資料標示「參考互動地圖」 |
| 遊戲內畫面（玩家截圖） | 傳送點清單、配方（製作時間、材料、價格）、任務追蹤上的主線編號、怪物改名 |
| 遊戲模組的圖鑑提示（SAOUI `codex/hints.json`） | 怪物的出沒提示文字（只取文字，不放遊戲素材） |
| 站長的 JourneyMap 探索紀錄 | 第 1 層「探索地圖」底圖、修補 wiki 地圖的破損處 |
| 玩家回報（Google 表單，審核員核准後收錄） | 怪物等級、座標、圖鑑編號與區域、掉落物、回報截圖（`reports.js`、`reports/`） |
| [Minecraft Wiki](https://zh.minecraft.wiki/) | 少數原版 Minecraft 物品圖示（Allium、Wheat） |

怪物名稱以遊戲內圖鑑為準；wiki 或參考地圖的舊名會保留成別名，搜尋時仍找得到。

第 2、3 層為開放前的 wiki 資料，開放後可能變動。

## 版權聲明

本攻略由中文玩家社群協力製作，提供中文玩家使用。本站是玩家自製的非官方攻略，免費、沒有廣告、不販售任何東西，與 SAO Minecraft 的營運方 Triggers Studio（TRIGGERS SAO）沒有關係，也沒有經過他們認可；同樣與 Mojang、Microsoft 及《刀劍神域》的權利人無關。遊戲裡的物品圖示、名稱、描述、截圖等內容，權利屬於 Triggers SAO 或各自的權利人。權利人要求移除任何內容時，我們會立即下架，請在 [Issues](https://github.com/Cheng-1001/ArgoStrategyGuide/issues) 留言。

*Guide communautaire non officiel, réalisé de façon collaborative par la communauté sinophone pour les joueurs chinois, gratuit et sans publicité, ni affilié à Triggers SAO ni approuvé par Triggers SAO. Les contenus du jeu appartiennent à Triggers SAO ou à leurs titulaires respectifs ; tout élément sera retiré sur simple demande des ayants droit.*

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

## 回報資料

到網站的「協作區 → 攻略資料維護」填 Google 表單（需附遊戲截圖），審核員核准後自動更新到網站。設定方式見 [google/SETUP.md](google/SETUP.md)。

## 開發

- 編輯 `src/index.html`（頁面）或根目錄的資料檔，再執行 `python3 src/build.py` 產生 `index.html`。
- 測試：`python3 tests/smoke.py`（需要 Python Playwright）。
- 專案說明與待辦：[CLAUDE.md](CLAUDE.md)。
