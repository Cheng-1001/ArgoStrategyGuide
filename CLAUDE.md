# ArgoStrategyGuide：SAO Minecraft「Aincrad 樓層查詢工具」

給接手的 Claude 工作階段看的專案說明。使用者（Cheng-1001）用中文溝通。

## 和使用者合作的方式

- **一律用中文回覆。**
- **用詞**：網站和審核網頁上的**說明文字**（以及網站標題），把 Aincrad 寫成「艾恩葛朗特」、Fractured Underworld 寫成「破碎的地下世界」（可以括號附原文）。**地圖標籤、地點／怪物／物品名稱不翻**（例如 Aincrad Mine、Aincrad 礦坑維持原樣）。其他不翻的：遊戲內的英文任務標題、法文物品名，以及使用者 Google 帳號裡已經存在的名稱（「Aincrad 回報自動化」專案、「Aincrad 查詢工具・回報審核」試算表、表單標題、SETUP.md 裡指的專案名稱），改了會對不上。
- 給選項時要寫出每個選項的後果和取捨，包括「不處理會怎樣」。不要只列選項。
- 步驟要寫完整：每一步做什麼、在哪裡點、條件和原因、誰負責。不要留模糊的指示。
- 要給預期真的能改善的方案。不要反覆試錯，最後才說「做不到」。
- **只更新 GitHub 網站。** 對話裡早期用 Claude Artifact 做過一版，已經凍結在第 16 版，不要再發佈或更新它。
- 修改前先確認現況，完成後用證據回報（測試結果、截圖、commit）。

## 網址

- 網站（GitHub Pages）：https://cheng-1001.github.io/ArgoStrategyGuide/
- Repo：https://github.com/Cheng-1001/ArgoStrategyGuide（舊名 SAOMC-tool，GitHub 會自動轉址）
- 回報表單（玩家填）：https://docs.google.com/forms/d/e/1FAIpQLSfaQnB3WleBLxKQI5adUUUaik11q00qIopj5lPnDqaApNCgig/viewform
- 資料來源：
  - wiki：https://saominecraft.wiki.gg/wiki/Floor_1 、/wiki/Bestiary
  - 官網物品圖鑑：https://saominecraft.com/wiki
  - 官網世界首領：https://saominecraft.com/world-boss
  - 參考互動地圖（玩家製作，第 1 層 Current Data，和我們一樣用 Minecraft X / Z）：https://delayedcode.github.io/SAO-MC-Interactive-Map/ ，repo https://github.com/DelayedCode/SAO-MC-Interactive-Map 。repo **沒有授權條款**，所以只取座標和地名（事實資料），不複製描述文字、程式碼、區域多邊形。取來的點位在 `data.js` 標 `src:"ref"`，網站顯示「參考互動地圖」。解析它的檔案時只用文字解析，不要執行它的 JS。

## 檔案結構

| 檔案 | 內容 |
|---|---|
| `src/index.html` | **要編輯的頁面原始檔**，HTML、CSS、JS 都在這一個檔案裡。沒有 `<!doctype>` 和 `<head>`，因為最初是 Artifact 格式 |
| `src/build.py` | 加上 doctype 和 head，產生根目錄的 `index.html`。**改完 `src/index.html` 一定要執行** |
| `index.html` | build 產生的檔案，不要直接改。build 會在每個本地 `<script src="x.js">` 後面加 `?v=內容雜湊`（2026-11-02：GitHub Pages 讓瀏覽器快取 10 分鐘，手機曾拿到新頁面配舊 `npcs.js`，篩選顯示錯的類別名稱）。Apps Script／Actions 直接改的資料檔（reports.js、jmmeta.js、formcfg.js）不會更新雜湊，和以前一樣最多 10 分鐘後更新 |
| `data.js` | 第 1 層：`window.SAO` = MAP、STATUS、ZONES、M（怪物）、ITEMS、EXTRA、TOWNS、SPOTS、QUESTS |
| `data23.js` | 第 2、3 層：`SAO23_ITEMS`、`SAO23.floors[2/3]`（第 3 層沒有地圖） |
| `bosses.js` | 世界首領 Galiath、獨特怪物 Seraphel、wiki 列的其他首領 |
| `reports.js` | 已收錄的玩家回報。格式必須維持 `window.SAO_REPORTS = <JSON 陣列>;`，Google 程式會自動讀寫它 |
| `mainq.js` | 第 1 層主線任務 `window.SAO_MAINQ[1]`：說明取自 wiki 主線表，步驟順序和座標取自參考互動地圖，步驟文字是本站中文改寫。步驟格式 `[文字, x, z, 約略]` |
| `equip.js`、`equip.png` | 裝備分頁：官網物品圖鑑的 656 件裝備（武器、盾、防具、飾品），由 scratchpad 的 `build_equip.py` 產生，不要手改。`equip.png` 48px 一格、一列 16 格 |
| `recipes.js` | 第 1 層配方，`tools/build_recipes.py` 產生（不要手改）。key 是 NPC 名稱；每筆 `[官網圖鑑 id 或 null, 遊戲英文名, 秒數, [[材料, 數量]], Col（"Free"；null＝未知）, 稀有度, 分類 weapon/armor/acc/potion/key, 等級, 來源 shot/ref]`。來源：使用者截圖（`SHOTS`，優先）＋參考地圖 eCompendium Current Data 的材料清單（只取事實；鯊魚飾品 4 筆和截圖完全相同）。英文名對官網 id 是人工對照表 `OID`（官網數值改版過，無法用屬性自動配對；藥水、水晶、強化藥、鑰匙 17 筆在 2026-11-01 補上，名稱和等級都吻合才收。2026-11-02 再人工對上 11 件飾品（Occult Hood/Robe/Amulet/Ring/Bracelet/Gloves、Ring of the Leviathan、Necklace of Aragorn、Bracelet of Ice、Gloves of the Wolves、Amulet of the Sylvan；名稱唯一對得上，等級可能不同，網站顯示官方等級；recipes.js 直接改＋OID 同步）。還對不上的：Spider Ring/Gloves/Cloak、Elite Treant 4 件、Frozen／Glacial 8 件、Nepenthes 3 件、Shark 4 件、Training Quiver（官方圖鑑查不到同名或同系列）。官網沒有的：Mana Potion I、Quality Mana/Stamina Potion I～III、Teleportation Crystal、Kobold Key、Purification Elixir，維持 🧪/🔑 佔位），參考地圖的製作地點寫「A / B」（例如 Health/Mana/Stamina Potion I 的「Starting Merchant / Alchemist」）＝兩個 NPC 都能做，拆開列在兩個 NPC 底下（使用者 2026-11-03 選 A），材料名對照表 `MAT`（Small Purse＝Small Pouch、Shark Carapace＝Shark Shell、Sylve Shoot＝Sylvan Sprout…）。武器、防具目前只有起始商人賣的新手裝備。**等級以官方圖鑑為準**：來源 ref 的配方等級和對應官網物品不同時（2026-11-02 查到 18 筆，例如 Belt of the Stags 7→5；來源 shot 的全部吻合），網站在建 `ALLREC` 後改用官方等級，原值放 `lvRef`，配方面板註明 |
| `recicons.js`、`icons/recipes/`、`tools/recipe_icons.py`、`tools/recipe_icons.json` | 官網圖鑑沒有的配方（Quality Mana/Stamina Potion 等 10 種）的圖示。**只能在使用者電腦上用本機 Claude Code 執行**：`find` 從 `sao.zip` 列出候選並輸出對照圖（不要 commit），把選定的貼圖路徑填進 `recipe_icons.json`，`build` 只把這幾張縮成 48px 寫進 `icons/recipes/` 和 `recicons.js`。**2026-11-03 使用者選 A：遊戲圖示優先於官網**（官網的藥水圖只有 3 張共用的佔位圖、分類全寫體力藥水，顏色和遊戲對不上）：`recIcon` 先用 `RECIC`，配方對得到官網 id 的，道具分頁的 `pslot` 也改用同一張（`OID_RECIC`）。`recipe_icons.json` 列 24 項（全部藥水 I～III、Quality I～III、4 種水晶、Purification Elixir、Kobold Key），`_look` 寫遊戲裡的外觀（試管／圓瓶，紅＝Health、藍＝Mana、橘＝Stamina）；對照圖是 scratchpad `potion_ref.png`（從站長截圖切的，不上網站）。2026-11-04 站長本機完成：19 張（藥水 I～III、Quality I～III、Purification Elixir），4 種水晶和 Kobold Key 留空（維持官網圖或佔位）；smoke 檢查 Quality Health Potion I 用遊戲圖示 |
| `classes.js`、`tools/build_classes.py` | 職業／技能分頁（`#classes`）。`build_classes.py` 讀 wiki 的 Classes 和 6 個職業頁（API parse 存成 JSON）、參考地圖 `Aincrad/Character Build` 的起始屬性／每級成長／天賦樹（文字解析）、`equip.js` 的職業限制。說明是本站中文改寫（`ZH` 對照表）。**不放任何職業或技能圖片**（使用者 2026-11-01：官方用的 SAO 原作圖片、圖示、標誌不要放，官方沒有原作授權）。wiki 除戰士外的技能圖示都是佔位圖（同一人 2026-04-18 一次建立），標「技能待確認」；武鬥家（Martial Artist）官方圖鑑沒有裝備、參考地圖也沒有屬性，標「可能尚未開放」 |
| `changelog.js` | 「更新紀錄」頁（右上角按鈕，`#changelog`）`window.SAO_CHANGELOG=[["YYYY-MM-DD",[項目…]],…]`，新的在最上面，依日期分組（使用者 2026-11-02 指定格式：日期下面列點）。**日期用台灣時間（UTC+8，使用者 2026-11-03 指定）**：查改動日期用 `TZ=Asia/Taipei git log --date=format-local:'%m-%d %H:%M'`，不要看 UTC。**每次推送玩家看得到的改動，都要在當天那一筆加一行**（中文、一行一件事、寫玩家感受得到的結果，不寫技術細節）；玩家回報自動收錄、探索地圖自動合併不列。網站顯示最近 3 天，較早的收在「較早的更新」 |
| `codex.js` | 遊戲圖鑑（Monstres）說明：`window.SAO_CODEX[1][圖鑑編號]={n 圖鑑名稱, reg 圖鑑區域標籤, desc 英文說明}`，取自站長 2026-11-03 的圖鑑截圖（`inbox/`，本機 Claude 推到分支，處理完刪掉、不上網站）。怪物面板在出沒提示下面顯示「遊戲圖鑑說明」。同一批截圖也校正了 hints.js（對上的改 sure=1，Elite Treant／Mini Treant、Healer／Mage Slime、Gorbel 的提示原本對錯怪物）、怪物名稱（Gorbel, King of Slimes／Narax Cursed Skeleton／Vyrmoss, the Royal Thorn／Thornak, the Sylvan Guardian，舊名進 aka）、編號（Narax 038、Vyrmoss 045、Forest Brute 046）、掉落率（Skeleton Tank、Skeleton Wizard、Sturdy Bandit、Narax 的 Putrefied Heart）、主線編號 1～7（任務日誌截圖）。#043 圖鑑也叫 Forest Treant（和 #042 同名），網站保留 Evil Forest Treant 以免同名 |
| （2026-11-03 晚間截圖） | 站長本機 Claude 推到 `inbox/` 的 153 張（20:27～22:16）：13 個製作／商店視窗寫進 `tools/build_recipes.py` 的 `SHOTS`（`(名稱, 稀有度, 秒數, 材料, 費用, 分類)`，飾品鐵匠 9 個、Bandit、Geldorak 守衛的 Forest Key、Sewer Reshaper 的 Slime Essence／Slime Tear（分類 other）、8 個 Loot Buyer 的 Buy 分頁＝賣藥水（網站用 `isShop`＝NPC 類別 lootBuyers 標成「販售」：NPC 資料標題「販售」、配方面板「NPC 販售・藥水」「在哪裡買」、清單右側「販售」、裝備／道具面板 `howTitle`「製作方式／NPC 販售／製作或購買」；使用者 2026-11-03 選改。Cursed Ruins - Loot Buyer 和 (2) 是兩個不同 NPC：遊戲裡商店標題都叫「Cursed Ruins - Loot Buyer」、賣的一樣，一個在廢墟 X 2857 Z 4494、一個在南邊 Château Abandonné 高處 X 2834 Z 4704 Y 113）：Vallhat／Hanaka Potion I 5.02、Virelune／Mizunari／Cursed Ruins×2 Potion II 10.05、Candelia／Magical & Icy（Tolbana）Potion III 15.07）；遊戲裡叫 Bracelet／Amulet of the Sylve（參考地圖寫 Sylvan，`SAME`）。Nodachi Altar 25 個升階配方（同武器兩把合成，5 階 10s～1m，全部 MYTHIC、免費）不進配方分頁，只在 Nodachi Blacksmith 的 NPC 資料寫一段說明（使用者 2026-11-03 選 B；材料要哪一階確定後再評估要不要收進配方分頁）。截圖的 NPC 座標和參考地圖相差都在 10 格內，沒改；新增 Mine Archaeologist（`SITE`，src `site2`，X 4280 Z 3891）。Trader 在 Hanaka 樓上 X 1562 Z 3431（主線 20 第 6 步推測位置吻合；站長沒有交過、不確定這一步有沒有實裝，步驟文字註明「可能尚未實裝」）。轉錄 JSON 在 scratchpad `eve1～4.json`，截圖處理完從 repo 刪掉 |
| （2026-11-03 深夜截圖） | 站長本機 Claude 推到 `inbox/` 的 150 張（22:38～23:18），轉錄在 scratchpad `eve5～8.json`，截圖從 repo 刪掉。**配方**（`build_recipes.py` 的 `SHOTS`，`FULL` 集合＝截圖看到 NPC 的完整清單，丟掉參考地圖多出來的列）：Starting Merchant 的 Buy 分頁（Potion I 5.02 是用買的、不是做的；Teleportation Crystal 301.49、Boar Meat、新手防具 50.25、訓練武器 1.00 共 22 項）、Starting Town - Tools（4 種工具 50.25）、Alchemist 的 Recipes 只有 9 種 Quality 藥水（各做 3 瓶，參考地圖的 Potion I 拿掉）；2026-11-04 Buy 分頁截圖：另外賣 Health／Mana／Stamina Potion I～III（5.02／10.05／15.07）。**`isShop(r)` 改成一筆一筆判斷**：NPC 類別在 `SHOP_CATS`，或截圖來源、沒有材料、沒有秒數、有 Col 價格＝販售；NPC 面板分「可以製作」「販售」兩段、The Assistant 6 種強化藥（材料和參考地圖不同：Wheat Flower、Lavender、Refined Allium、Wheat Leaves、Refined Wheat、Wisteria 本站還沒有物品資料）、Crystallographer 3 種水晶（EPIC 5 分鐘）、Purification Elixir、Copper／Iron Accessories、Key of the Fallen。`isShop` 用 NPC 類別 `SHOP_CATS`＝lootBuyers＋toolMerchants。**NPC**：截圖位置和現有座標都在 7 格內，不改；新增 Weapon Recycling、Accessory Recycling、Auction House、Vault、Labyrinth Archaeologist（`SITE`，site2）；`NPC_NOTE` 在 NPC 面板顯示 Alchemist 的位置（使用者 2026-11-04：「[NPC] Alchemist」在建築二樓，一樓金色名牌的「Alchemist」是任務 NPC；Crystallographer 也在二樓）、回收清單（交 1 件換 Recycling Coins ×3～5）、倉庫（加 1 頁 25000 Col）、拍賣場。**地下城**：SPOTS `fallen` 改名 Labyrinth of the Fallen（old Fallen Dungeon），`dg` 欄位＝Dungeons 視窗（首領 Le duo des Déchus、鑰匙、4 種難度、Easy 的限制、12 項通關寶箱內容（使用者 2026-11-03：Loot＝完成時的寶箱，不是怪物掉落；有些項目視窗下方寫怪物名，面板顯示「視窗標示：…」），`dgInfoHTML` 顯示；23:44 再補 Geldorak Mine Dungeon 的 `dg`（視窗名稱 Geldorack，`title`；首領 Les gardiens de la Forêt、Forest Key、Easy 無時間限制、建議 6 級、寶箱 4 項）；Ornstein 改名 Ornstein, Fallen Defender（舊名 aka）。**地點**：Lac des Nénuphars（圖鑑 #011，X 2438 Z 2783，poi，不是 Virelune Lake）。這批沒有怪物近照，不能做縮圖 |
| `hints.js` | 遊戲圖鑑的 LOCATION HINT，對應到 41 隻第 1 層怪物（`sure=0` 表示依順序推斷） |
| `items.png` | 物品圖示表：64px 一格、一列 8 格，目前用到第 185 格。物品資料的最後一個欄位就是格子編號 |
| `floor1.jpg`、`floor2.jpg` | wiki 地圖。**floor1.jpg 2026-11-02 換成 wiki 新圖「File:Updated floor 1 map.png」**（2026-10-29 23:17 UTC 上傳，Floor 1 頁修訂 2802；舊圖是同日 14:44 UTC 之前抓的）：新圖是看圖軟體截圖、島約 1408px，用 SIFT 對到舊圖（2123 組特徵點，殘差中位數 0.26px，比例 1.483、無旋轉）轉成同樣的 2100px 座標框（x0＝z0＝70 不變），輕微銳化、圓外塗黑。和舊圖的差異：Boar Zone 的「Zone Sanglier」字樣拿掉、Mizunari 東邊和 X 1836 Z 2481 一帶地形重做（舊圖的黑色破圖和 sdsd 路標都不在了）。之後 wiki 換圖時同樣做法：對位 → 覆蓋 floor1.jpg → `python3 -I tools/jm_rebase.py`（只重畫探索地圖切片裡未探索區塊的變暗 wiki 底，已探索區塊不動，再重產 L0～L2 和 floor1_jm.jpg） |
| `floor1_jm.jpg` | 第 1 層「探索地圖」3000px 預覽：使用者的 JourneyMap 疊在變暗的 wiki 地圖上（網站實際用 `tiles/f1jm`） |
| `tiles/f1jm/{L}/{c}_{r}.jpg` | 第 1 層探索地圖切片：256px，L0～L3 = 640／1280／2560／5120px，L3 是 1 格 1 像素。由 `tools/jm_tiles.py` 產生 |
| `tools/jm_rebase.py` | 換 wiki 底圖後重畫探索地圖切片的未探索部分（見 floor1.jpg 那一列） |
| `tools/jm_tiles.py` | JourneyMap day 圖 → `floor1_jm.jpg` ＋ 切片，**整張重做**（2026-11-02 起不要再用，會蓋掉玩家合併的部分） |
| `tools/jm_merge.py`、`tiles/f1jm/explored.png`、`jmmeta.js` | **探索地圖的合併**：玩家上傳的 zip（網站「打包探索地圖」產生，或本機資料夾）疊到現有切片上。**依資料夾分組，只收名叫 `day` 的資料夾（或 zip 根目錄）的圖**（夜間、地形、洞穴層不收）；**每個資料夾各自檢查**：和已探索區塊重疊至少 `--min-overlap`（20）塊且顏色對得上才合併，重疊太少（無法確認是第 1 層）或對不上就略過；多個資料夾依檔案日期舊→新貼上（新的蓋舊的）；結果有 `folders`／`skipped`。`explored.png` 是已探索的 16×16 區塊（1 px＝1 區塊，世界座標；2026-11-02 用 `--init-mask` 從切片推算，直方圖雙峰、門檻 9）。和已探索區塊重疊處顏色差異中位數 > 32 就拒絕（別的樓層／世界）；只接受 `x,z.png`、512×512、≤ 600 張、每張 ≤ 4 MB。只重寫碰到的 L3 切片，L0～L2 和 `floor1_jm.jpg` 由 L3 重產。結果寫在 `jmmeta.js`（`SAO_JM["1"]` 日期、探索比例、合併紀錄；`results[回報編號]`），**不碰 `reports.js`**（避免和 Apps Script 衝突）。測試 `tests/jm_merge_test.py` |
| `formcfg.js` | 回報表單預填網址 `window.SAO_FORM = {prefill, updated}`，**Apps Script 的 `upgradeForm` 自動寫入，不要手改**（`{floor}` 每個必填樓層題各一個，網站全部替換） |
| `tests/jm_pack_test.py` | 網站打包工具端到端測試：假的 mp 資料夾（第 1 層＋新區域、別處真實地形、雜訊、只有新區域、範圍外、夜間層）→ 瀏覽器判斷 → 下載 zip → `jm_merge.py` 合併；也測分份 |
| `.github/workflows/jm_merge.yml` | release `jmap-回報編號` 發佈時執行：下載 zip → `jm_merge.py` → commit 切片和 `jmmeta.js` → 要求 Pages 重建 → 刪掉 release |
| `tools/build_equip.py` | 產生 `equip.js`／`equip.png`。要先在工作目錄準備官網圖鑑 `catalog.json`、`im_index.json`、官方圖示和 3D 截圖（做法見「抓資料的方法」） |
| `pending.js` | 處理中的回報 `window.SAO_PENDING = {updated, list}`，**Google Apps Script 自動寫入，不要手改**。每筆只有 `id`、`type`、`floor`、`date`（送出時間 yyyy-MM-dd HH:mm）、`status`（pending／approved／error／rejected）、退回的 `rdate`；不放名稱、內容、暱稱、截圖、審核備註（使用者 2026-11-02 選 A，只公開這幾欄） |
| `reports/` | 回報截圖 |
| `google/apps-script.gs` | Google Apps Script（獨立專案）：建立表單和試算表，核准後透過 GitHub API 寫入 `reports.js` 和截圖 |
| `google/review.html`、`google/review_server.js` | 審核網頁（另一個 Apps Script 專案）的前端和後端原始檔。改完執行 `python3 tools/build_review.py` 產生 `google/review.gs`（使用者貼這個檔） |
| `google/review.appsscript.json` | 審核網頁專案的資訊清單：最小權限（spreadsheets、drive.readonly、external_request、userinfo.email），以「存取的使用者」身分執行 |
| `tests/review_test.py`、`tests/apps_script_test.js` | 審核網頁前端（假的 google.script.run）和 Apps Script 後端（假的試算表）的本機測試 |
| `google/SETUP.md` | 給使用者看的表單、審核設定說明 |
| `tools/export_map.bat` | 使用者電腦上用的：把 JourneyMap 地圖複製到沒有「~」的資料夾 |
| `tests/smoke.py` | Playwright 冒煙測試 |
| `tests/jm_merge_test.py` | `tools/jm_merge.py` 在暫存複本上的測試（正常合併、別的世界被擋、壞檔被擋） |
| `tests/report_types_test.py` | 新回報種類（配方、任務追蹤、技能、地點擴充）的整合測試，用假的已核准回報 |
| `.github/ISSUE_TEMPLATE/` | 1～4 是舊的 GitHub 遊戲資料回報（保留但已不是主要管道）；5-bug、6-idea 是協作區「問題回報及建議」用的網站問題／建議範本 |

## 修改和發佈流程

1. 改 `src/index.html`，或根目錄的資料檔。
2. `python3 src/build.py`
3. `python3 tests/smoke.py`，要看到 ALL PASSED。改了畫面的話，另外用 Playwright 截圖親眼確認，電腦寬度（1280）和手機寬度（390）都要看，手機不能左右捲動。
4. 玩家看得到的改動要在 `changelog.js` 當天那一筆加一行。
5. commit，訊息結尾附上工作階段規定的署名行，然後 push 到 `main`。GitHub Pages 大約 1～3 分鐘後更新。使用者看到舊畫面時，請他按 Ctrl+F5。
6. Google Apps Script 也會直接 commit 到 `main`。**push 之前先 `git pull --rebase`**，避免和自動收錄的回報衝突。

## 網站功能（`src/index.html`）

- **網站名稱**：「阿爾戈的攻略本」（使用者 2026-11-02 指定，原「艾恩葛朗特查詢工具」）：頁面 `<title>`、站名 `h1`、介紹頁、`build.py` 的 description、README。Google 表單／試算表／Apps Script 裡的「Aincrad 查詢工具…」是使用者帳號裡已存在的名稱，不改。
- **網址格式**：`#f{樓層}-{分頁}`，分頁有 map / monsters / equip / items / props（圖鑑的子分頁）、quests、recipes、classes、bosses、report（協作區・攻略資料維護）、feedback（協作區・問題回報及建議）、about（說明）。上方選單：地圖／圖鑑／任務／配方／地下城／職業／技能（1600px 以下和手機顯示「職業」）／世界王。右上角按鈕列 `.hbtns`：協作區（`#collabBtn`，`data-v="report"`，2026-11-02 使用者「拉出來放到更新紀錄左邊」）／ⓘ 關於本站 ▾（下拉選單 `#aboutMenu`：介紹及資訊 `#aboutInfo`→`#about`、更新紀錄 `#logBtn`→`#changelog`；使用者 2026-11-02 指定；點外面或 Esc 關閉；兩頁時按鈕 aria-current；選單靠按鈕左邊、至少和按鈕同寬；手機兩顆按鈕都 86px、選單和按鈕同寬，項目文字放不下時自動跑馬燈（`.amq`／`.marq`，開選單時量寬度；**`.mq` 已被主線任務卡片用掉，不要再用這個 class 名**））；821～1600px 站名兩行、職業用短標籤，讓搜尋留在第一列；樓層選擇只顯示「1F 第 1 層」（2026-11-02 使用者選 A：原本的 Town of Beginnings／Urbus／Forest of Wavering Mists 是主城或區域名，不是官方樓層名；`FLOORS[f].name` 資料保留但不顯示，拿到遊戲畫面上的樓層名稱再改）。
- **網頁導覽**（2026-11-03，使用者選 A）：`window.saoTour`（在主程式 IIFE 裡，`src/index.html` 最後），9 步：歡迎／樓層選擇／功能選單／全站搜尋／篩選器（會切到地圖）／地圖（點圖示開資料）／協作區／關於本站／導覽結束（只有置中的「林哭斯大斗！」按鈕（字和標題一樣大；內容上下置中、上下留白一樣），沒有上一步和頁數；使用者刪掉「兩種底圖」，2026-11-03 說明文字全部由使用者指定）。聚光燈 `.tour-hole`（box-shadow 挖洞）＋說明卡 `.tour-card`；**class 一律 `tour-` 開頭**（網站已有 `.th`，同名會讓框內變白）。電腦版說明卡固定在畫面正中間，只有地圖那一步（`pos:"tr"`）放在地圖右上角、框不含左邊篩選器（`cut:"#fpanel"`）（使用者 2026-11-03）；說明卡電腦版放大 1.2 倍（寬 408px）、每一步一樣高（`cardH`：量所有步驟取最高；手機不套用，高度跟著內容，使用者 2026-11-03）、標題置中，「略過」在說明卡外面的右上方、頁數點在中間（使用者 2026-11-03）；手機說明卡左右留 16px、固定在下方（框不蓋到卡片），只有「導覽結束」上下置中（使用者 2026-11-03）。手機的地圖那一步（`fit:"#stage img.map"`）會把頁面往下捲，讓地圖露在說明卡上方（畫面矮的手機原本會被說明卡蓋住下半部）。第一次來、停在地圖、不是 `?edit`、不是自動化瀏覽器（`navigator.webdriver`，測試不會被擋）時自動開始；「略過」跳到最後一步「導覽結束」（使用者 2026-11-03），看完寫 localStorage `sao-tour-v1`。「關於本站」選單第三項「網頁導覽」（`#tourBtn`）可重看。Esc 直接關閉（同樣記住）。
- **新版提示**（2026-11-03，使用者選 A：GitHub Pages 讓瀏覽器暫存頁面 10 分鐘，無法調整）：`build.py` 在 `<head>` 寫 `<meta name="sao-build">`（頁面內容雜湊）；頁面在打開 3 秒後、回到分頁時、每 5 分鐘（最多每分鐘一次）用 `fetch(pathname+"?_=時間",{cache:"no-store"})` 抓線上版本比對，不同就在上方顯示 `#updBar`「網站有更新，點這裡載入新版」（不自動重新載入，免得打斷玩家），點了用 `?u=新版號` 載入（新網址避開暫存），載入後用 replaceState 拿掉 `u`。只改資料檔（reports.js 等）不會換 build，不會提示。預覽網址 raw.githack.com 不檢查（githack 會把分支網址快取成舊版，點了也載不到新的，2026-11-03 使用者遇到）。測試在 smoke.py（`window.__updCheck`）。
- **地下城分頁**（`#dungeons`，2026-11-02 使用者「預新增」，先只放名稱）：`renderDungeons` 列這一層 SPOTS 裡 kind dungeon、名稱副標不含「樓層首領」的地點（第 1 層 4 個：Geldorak Mine Dungeon、Fallen、Xal'Zirith、Skeleton；**Geldorak 2026-11-02 使用者選 B 拆成兩點**：傳送點 `geldorak`（poi、tp Mine de Geldorak、n Geldorak Mine，X 4267 Z 3894）和地下城 `geldorakd`（n Geldorak Mine Dungeon＝圖鑑區域名，入口取主線步驟 X 4288 Z 3887）；Kobold Tower 是樓層首領塔不列），卡片只有名稱，點了開地點面板。地下城面板有「進入鑰匙」（`dgKeys`：地點說明裡寫的 Clé…＝官方道具法文名對到 key 配方，對不到就找入口 150 格內 NPC 做的 key 配方；第 1 層：Geldorak Mine Dungeon→Forest Key、Fallen→Key of the Fallen、Xal'Zirith→Key of Xal'Zirith、Kobold Tower→Kobold Key，Skeleton 沒有），鑰匙配方面板反過來列「用途：進入…」。之後要補進入條件、鑰匙、攻略、掉落。
- **協作區**（2026-11-02 由「回報區」改名，view 仍是 `report`）：子分頁「📝 攻略資料維護」（`#report`，回報表單＋審核流程＋已收錄）和「💬 問題回報及建議」（`#feedback`，`rSub`）。後者：**建議用 Google 表單**（使用者 2026-11-02 指定，只有建議；「💡 提出建議」開回報表單，回報種類「建議」，題目「建議・內容／相關頁面」，不用截圖、填完直接送出），核准後（`type:idea`）列在右欄「玩家建議」，審核備註去掉「審核：帳號｜」後顯示成「回覆：…」，不列在攻略資料維護的已收錄；**網站問題用 GitHub Issues** 範本 `5-bug.yml`（`[問題]`），`6-idea.yml`（`[建議]`）保留給有 GitHub 帳號的人；右欄下方用 GitHub API 列出標題以 [問題]／[建議] 開頭的未關閉 issue（`loadFeedback`）。有截圖的遊戲資料一律走表單「攻略資料維護」。
- **關於本站**（`#about`，2026-11-01；2026-11-02 由「說明」改名，使用者指定）：右上角搜尋欄左側的「ⓘ 關於本站」按鈕（`#aboutBtn`，不在上方分頁選單裡；手機版在樓層選擇那一列右邊）。左邊是「更新紀錄」按鈕（`#logBtn`，`.hbtns` 包住兩個按鈕，獨立頁面 `#changelog`／`renderChangelog`，使用者 2026-11-02「拉出來放在說明左邊」）。821～1360px 時站名改成兩行（SAO MINECRAFT 在上）讓搜尋留在第一列；手機兩個按鈕縮小、樓層選擇可縮。`renderAbout()`：關於本站、遊戲官方連結（官網 https://saominecraft.com/ 、官方 Discord https://discord.gg/HdHba5awgn ，取自官網首頁）、資料來源（`ABOUT_SRC`，和 README「資料來源」表同步）、版權聲明（`#legal`）。
- **版權聲明**：放在說明頁的 `#legal`；樓層列的「非官方攻略・版權聲明」會跳到說明頁的這一段（`aboutJump`）。第一句是「本攻略由中文玩家社群協力製作，提供中文玩家使用」（使用者 2026-11-01 指定）。README 同步。**不要放 SAO 原作的圖片、圖示、標誌**，即使官方網站或遊戲有用（官方沒有原作授權）。
- **怪物名稱以官方為準**：以遊戲內圖鑑為準（wiki 圖鑑表顯示的名稱跟著遊戲內圖鑑；wiki 寫成 `[[舊名|新名]]` 時用新名）。改名的怪物把舊名放在 M 的第 10 欄 `aka`，搜尋、回報、圖鑑提示都認舊名。參考互動地圖的怪物名稱是舊名，不要拿來用。
- **任務分頁**：主線（依劇情順序，可以在地圖上畫路線：編號步驟加虛線）和支線（wiki）兩種。主線的 `n` 是遊戲任務追蹤上的編號：wiki 主線表寫明 8～18，R0001 截圖證實「24. The Truth About the Seal」，19～23 依順序；25 以後是推算（`nEst`）；The Trader 之前的編號還不確定，不顯示數字。參考地圖把「The Southern Marshes」(14) 併進「The Suspended City」，已拆開；它把 The Truth About the Seal 標在起始之城也不對，Catherine 在墮落者迷宮門口（X 2382、Z 2415；使用者 2026-11-01 確認，R0001 的任務距離 1565 格也吻合）。拿到玩家截圖裡的任務追蹤畫面時，用來校正編號和步驟。
- **職業分頁版面**：卡片固定 3 欄（`#lCls`，`fixCols` 略過它）；點職業開加寬面板（`panel-xwide`，880px），內容分兩欄 `.cls2`：左＝能力傾向、起始屬性和成長，右＝技能、天賦樹。「官網的玩家配裝」連到 `https://saominecraft.com/builds?class=<職業 id>`（官網參數和本站 id 相同，武鬥家是 `martial_artist`；使用者 2026-11-03）。「查看這個職業可用的裝備（另開視窗）」開浮動視窗 `#cwin`（和任務路線視窗同樣的拖曳、調整大小），可依部位篩選；點裝備在**同一個視窗**顯示詳細資料（`showCWItem`，有「← 回到裝備清單」），右側職業面板不變。原則：右側面板的關聯內容一律用浮動視窗，不取代面板。面板裡的座標、「在地圖上查看」：在地圖分頁時移動大地圖；**手機（≤820px）一律不開浮動地圖**（使用者 2026-11-02）：`showPoints` 改走 `goMapThen`，關掉面板、切到地圖分頁、移到那一點並把地圖捲到畫面上（任務步驟座標例外：只在面板小地圖上標紅）；電腦版在其他分頁時用 `showPoints` 開浮動地圖視窗（同一欄的多個座標一起標號，例如首領的所有重生點），不切換分頁。
- **配方分頁**（上方選單的獨立分頁 `#recipes`，在任務和世界王中間）：分類 武器／防具／飾品／藥水／鑰匙、依 NPC 篩選、排序；每張卡片點了開自己的配方面板（type `r`，id 是 `ALLREC` 的索引，所以只會選到一張），面板列 NPC、等級、費用、時間、材料；有對應官網物品時，**裝備／道具資料直接顯示在配方面板裡**（`recItemInfo`：分類、等級、職業、描述、數值、本站物品連結、其他製作地點；使用者 2026-11-02：不要再多點一次）。配方面板最下面有「查看圖鑑」（切到裝備／道具分頁打開那一件），圖鑑的裝備／道具面板「製作方式」下面有「查看配方」（每個 NPC 一個，切到配方分頁打開）：`data-goview="分頁|type|id"` → `goView()`，切分頁後開面板並把卡片捲到中間；卡片被搜尋或那一頁的篩選藏住時，先把搜尋清空、篩選恢復「全部」。NPC 資料列「可以製作」，裝備列「製作方式」，材料列「可以拿去製作」。
- **手機的篩選區**（≤820px，2026-11-02 使用者：上半部說明太多）：每個列表分頁（怪物、裝備、掉落物、道具、任務、配方、職業）的 `.filters` 只顯示第一組篩選（類型／分類／部位），其他篩選收在「更多篩選 ▾」（有調整過時顯示「已調整 N 項」，`fbarSync`），`.note` 說明收在「ⓘ 說明 ▾」；按鈕列 `.fbar` 由 JS 在載入時插入，電腦版隱藏、畫面不變。手機的篩選標籤和選項排在同一列。
- **樓層資訊列**（`#floorInfo`，搜尋列下方）：不再重複樓層名稱（上方樓層選擇已經有，使用者 2026-11-02），只列建議等級、樓層首領、即將開放提示、「非官方攻略・版權聲明」。手機（≤820px）整列隱藏，只有即將開放的樓層會留下那句提示（版權聲明從「ⓘ 說明」頁進）。
- **手機不顯示電腦才能用的功能**（使用者 2026-11-02）：`.pconly` 在 ≤820px 隱藏——「打包探索地圖」卡片（`#jmPack`，手機選不了 mp 資料夾）和說明裡「上傳探索地圖」那一步；改顯示一行 `.mbonly`「上傳探索地圖要在電腦上開本站…」。浮動視窗標題列的操作提示（滾輪縮放、拉右下角）手機也隱藏。
- **手機精簡**（≤820px，使用者 2026-11-02「全做」，電腦版不變）：
  - 不顯示站名那一行（`.brand`）、地圖左下角的游標座標（`#coord`）。
  - 資料面板全螢幕（`#panel` top:0）；頂端路徑只在有上一層時顯示（`body.pdeep`），否則只有 ✕。切換分頁時關閉面板（`show()` 的 `pv!==view`，`goView` 除外）。
  - 地圖下方的地點清單預設只顯示分組標題（`.zsec`，點了展開，`ZOPEN`／`zfoldSync`；有搜尋時全部展開）。
  - 卡片和地點清單不顯示「玩家座標」「參考互動地圖」「地圖標示」標籤（推估位置、位置未知照常顯示）；面板裡照常。
  - 面板裡的資料來源說明（`.note.srcn`：怪物位置來源、任務、配方、NPC、職業、官方圖鑑編號）收進面板最下面「ⓘ 資料來源」（`.srcfold`，在 renderP 搬移）。新增來源說明時加 `srcn`。
  - 圖鑑出沒提示只顯示英文（`.hfr` 法文隱藏）；配方材料不顯示「點了看哪裡拿得到」，改成數量後的「›」；任務卡片不顯示「獎勵未記錄」。
- **卡片欄數**：寬螢幕（≥1180px）的卡片格線用 `fixCols()` 固定成「右側面板開著時」的欄數，面板開關都不會重排。
- **圖鑑子標籤**（怪物／裝備／道具／素材，`#codexTabs`）：**電腦版（≥821px）放在左側篩選欄最上面**（使用者 2026-11-04：分頁選完要跳到左邊篩選、再跳回中間，視線來回跳；要保留左欄）：`#codexTabs` 在電腦版隱藏（`.app` 少一列），`syncVTabs` 在 4 個圖鑑分頁的 `.filters` 最前面放直式的 `.vtabs`（「圖鑑分類」，目前這頁左邊橘色線），點了 `go()`；手機版照舊用上方的 `#codexTabs`。
- **圖鑑四分類**（2026-11-04 使用者指定：怪物／裝備／道具／素材，素材＝怪物掉落＋採集類；取代同日的「怪物掉落」B 方案）：一件東西只在一個分頁。
  - 歸屬：本站物品（`ITEMS`，wiki 來的英文名＋掉落率、任務、取得地圖）用 `offOf` 依法文名對到官網裝備或道具；對到裝備、或對到不是材料／採集的道具（`MATG`＝PR_GROUP 材料或採集）就屬於裝備／道具，其餘（材料、採集物、官網未收錄的 10 件）屬於素材。
  - 轉向：`redirI(id)` 讓 `openP("i",…)` 和 `goView` 自動改開裝備（e）或道具（p）面板；`redirP(oid)` 反過來把官網材料改開本站素材面板。所以怪物掉落清單、地下城寶箱、任務需求、配方材料、採集點等舊的 `data-go="i|…"` 連結都不用改。
  - 面板：`itemObtainHTML(id)`（取得方式＋編號小地圖、用途、可以拿去製作）由 `itemDetail` 拆出，裝備面板 `equipDetail` 和道具面板 `propDetail` 在有對應本站物品時直接顯示（原本只有「本站物品資料」連結）。
  - 素材分頁（view 仍是 `items`、網址 `#items`）：`matPool`＝本站素材（預設只列這一層有取得資料的；第 1 層 62 件）＋勾「顯示全部素材」時加官網沒有本站資料的材料／採集物（卡片 `p|oid`，共 431 件）；分類 `GROUPS`＝材料／作物／礦物／木材／漁獲／官網未收錄（`matGroup`，沒有東西的隱藏）。
  - 道具分頁：`PRV()`＝PR 去掉材料和採集（273 件），分類膠囊也拿掉這兩個。
  - 測試：smoke.py「four-tab codex」3 項；scratchpad `four.js` 逐一點過 14 個入口（怪物掉落的裝備／材料／食物、配方材料、地下城寶箱、任務需求、舊網址、搜尋）。

- **主要篩選在清單上方**（`.topf`，電腦版，使用者 2026-11-04 指定）：`TOPF`＝怪物 類型、裝備 部位＋細分、素材 分類、道具 分類＋細分（稀有度 2026-11-04 使用者要求放回左欄）；細分的數字跟著其他條件（職業、稀有度、等級、搜尋）即時算（`renderEquip`／`renderProps` 的 `base`），不然「弓 22」和清單 3 件對不上；`placeTopFilters` 把這些 `.fgroup` 搬到 `.results` 的 `.rhead` 下面（不是複製，原本的事件照常），左欄留下圖鑑分類、其他篩選和排序；手機（`topMQ` ≤820px）搬回左欄原位（`__home` 註解節點），維持「更多篩選」收合。
- **裝備部位照官方配裝欄位**（2026-11-04）：`EQ_PART`＝武器（主手）／副手（盾牌 shield＋催化器 catalyst，原本盾牌在防具、催化器在武器）／防具／飾品；選了部位出現「細分」（`EQ_SUBS`、`eqSub`、`#gEqSub`）：武器 6 種、副手 2 種、防具 頭盔／胸甲／護腿／靴子（`slot`；官網 12 件 Casque／Masque 沒有 slot，`SLOT_BY_NAME` 依法文名字首補成頭盔）、飾品 項鍊／戒指／手環／手套／遺物。官方把一些活動武器（例如 Arc des Murmures）放在活動道具類，不在裝備裡。
- **道具細分**（2026-11-04，使用者：要能區分活動道具）：分類「活動」顯示成「活動道具」；選了分類且裡面有 2 種以上的官網類別時出現「細分」（`fillPrSub`、`PR_SUBLAB`）：活動道具＝萬聖節／農曆新年／聖誕節／情人節，採集＝漁獲／礦物／木材／作物，鑰匙＝寶箱鑰匙／地下城鑰匙…。
- **怪物區域分野外／地下城**（2026-11-04）：`fMonZone` 用 optgroup 分「野外」「地下城」（`isDgZone`：名稱有 Dungeon／Labyrinth／Sanctuary／Tower／Lair／地下城／迷宮／聖所），另有「全部地下城」`@dg`、「全部野外」`@wild`。
- **已篩選列**（`.actf`，2026-11-04）：每個列表分頁（`.browse`）清單標題旁列出左欄目前不是預設值的條件（膠囊 chips 不是「全部」、下拉不是第一項（排序除外）、勾選框、等級範圍），點 ✕ 取消那一項，兩項以上有「全部清除」；`actControls`／`actSync`，左欄任何點擊／變更後和 `renderCurrent` 時更新。
- **任務獎勵連結**：`rewardGo` 把獎勵物品名稱（可帶數量，例如「24 Minerai de Fer」）對到本站物品、官方裝備或道具；任務面板裡的獎勵（`rewardText(qq,true)`）可以點，卡片上不加連結。
- **浮動地圖的「目前這一點」**：`showPoints(…,sel)` 會把點的那一個座標畫成紅色加外圈（`RW.sel`），視窗標題寫「第 N 點（共 M 點）」；面板裡的重生點座標前面有同樣的編號（`.rnum`）。
- **路線／地點小地圖的編號**：步驟的第 5 欄（`step[4]`）可以指定標籤；同一個來源的多個點（例如首領的 4 個重生點）都用同一個編號，同一位置的相同標籤只畫一次。
- **主線步驟的遊戲原文**（2026-11-03 使用者選 B）：`mainq.js` 任務可加 `en:{步驟索引:"英文原文"}`（取自玩家截圖的任務追蹤），任務面板在該步座標後面顯示「遊戲原文：…」，搜尋也比對（`mqHit`）。目前只有主線 20 The Geldorak Mine 的第 5、6 步。第 6 步（額外：稀有素材交給 Hanaka 的商人）的座標 X 1564 Z 3428 是推測（第 8 段村長的商人 The Trader，wiki 主線表「introduces his trader」；不是 Hanaka - Loot Buyer），使用者 2026-11-03 選先標，遊戲確認後拿掉「推測」字樣。
- **搜尋時顯示符合的 NPC**（2026-11-03 使用者選 C）：`npcVisible` 在名字或類別（中文、英文 key）符合搜尋時，就算 NPC 篩選關著也畫出來並亮起（`npcHit`）；符合的集合改變時 `filterMap` 重畫地圖和清單（`npcSearchKey`）。
- **路線圖的點合併**（2026-11-03 使用者：點擠在一起）：`routeMini` 和浮動路線視窗 `rwRender` 用 `clusterPts` 把畫面上距離小於標記 2.2 倍半徑的點合成一個標記，連號寫成「1–4」（`numLab`）；`g[data-xz]` 是空白分隔的座標清單，點步驟座標用 `~=` 找標記。浮動視窗放大後會分開。路線圖也畫畫面範圍內的傳送點（橘圓點）和地標（橘菱形）加名稱當參考（`refMarks`，`g.refm`，不能點；使用者 2026-11-03）。小地圖範圍 > 500 地圖單位時底圖一律用 wiki 地圖（探索地圖縮小後未探索區太暗、像素塊明顯，使用者 2026-11-03）。
- **地圖搜尋**（2026-11-03 使用者：有輸入搜尋時先關閉其他篩選）：搜尋有字時**篩選暫時不套用**（`SRCH_ALL`，`catOn` 一律 true；renderMap／renderZoneList 全部畫出來），`filterMap` 把不符合的城鎮、地點、怪物區框線、首領重生點、NPC 加 `.shide` 藏起來，只留符合的；清掉搜尋就回到原本的篩選（`npcSearchKey` 只記有沒有在搜尋）。提示條「正在搜尋「…」：地圖上只顯示符合的 N 個位置（篩選暫時不套用）」和「清除搜尋」（地圖上方，手機在下方）。
- **物品面板的取得方式**：`itemMap` 把掉落怪物的怪物區（或首領重生點）和採集點編號，畫成和任務一樣的小地圖（`routeMini(steps,f,true)`，不畫虛線），列表項目前面有同樣的編號，「放大查看取得地點」開浮動地圖視窗（`openRouteWin(…,true)`）。手機（≤820px）不顯示這個按鈕，小地圖全寬（使用者 2026-11-02，同任務面板）。
- **任務面板**：步驟 → 需要的物品和目標 → 原文 → 來源 → 最下面才是路線小地圖和放大按鈕。小地圖（`routeMini`）在範圍 ≤ 500 地圖單位時疊上探索地圖切片（`miniTiles`：≤ 260 用 L3、否則 L2；wiki 底圖時只畫 `explored.png` 已探索的區塊，當遮罩），比 2100px 的 floor1.jpg 清楚。**手機（≤820px）不開浮動視窗**（使用者 2026-11-02）：放大按鈕隱藏、小地圖全寬，點步驟座標只把小地圖上那一點標紅（`g.hl`）並捲到小地圖。
- **物品分類對齊 wiki**（使用者 2026-11-03）：官網圖鑑 catalyst（Grimoire、Lanterne、Catalyseur 等 34 件，法師／薩滿副手）在 `props.js` 裡，但網站把它們併進裝備 `EQ`（`cat:"catalyst"`、`ps:1`＝圖示用 props.png，`eslot` 轉給 `pslot`；`EQ_PART` 武器、`EQ_CAT`「催化器（副手）」），`PR` 不含 catalyst。道具分組 `PR_GROUP`：水晶 crystal 歸「消耗品」，符文 gem_stone 和強化藥 fortifier 是「符文・強化」。wiki 還有 Gauntlets（拳套）、Offhand（Training Quiver／Pavise／Buckler）兩類，官方圖鑑沒有，先不做。
- **裝備分頁**：依部位、職業、稀有度、等級篩選。官方 artifact（ACCESSOIRES_ARTEFACTS：腰帶、披風、靴子、錢幣、護符等被動加成裝備）網站顯示「遺物」（使用者 2026-11-03 選，原「飾品」和大類同名）。官網玩家配裝的裝備欄位（2026-11-03 查 saominecraft.com/builds 的資料）：頭盔、胸甲、護腿、靴子、主手、副手，項鍊 1、戒指 2、手環 1、手套 1、遺物 3（官方把手套歸在 ACCESSOIRES_GANTS 飾品類；網站 2026-11-03 起手套也放在「飾品」部位，`EQ_PART.gloves="acc"`，使用者指定）。名稱和描述是官方法文原文；本站 ITEMS 有同名（`fr` 欄位）的會連過去。只有 16×16 的官方圖片直接當圖示，其他用官網搜尋結果卡片 `.w-it .ph` 的 3D 渲染截圖（去背）。樓層選擇器支援 1～100 層；不存在的樓層會回到第 1 層。
- **地圖**：
  - 依點位顯示怪物縮圖；縮小時只顯示最主要的一隻加「+N」。
  - **傳送點**：TOWNS 和 SPOTS 的 `tp` 欄位是遊戲傳送選單上的名稱（法文）。第 1 層 13 個（使用者 2026-11-01 提供的遊戲內傳送地圖）：7 個城鎮（Vallhat 不是，要走山腳的傳送裝置）、6 個地點（狼之谷、Geldorak 礦坑、詛咒廢墟、OG Quarter、巨人花園、商人公會）。地圖上可傳送的城鎮畫藍綠圓點加 🌀，地點標籤加 🌀，右側清單最上面有「🌀 傳送點」。傳送地圖本身沒有座標，座標沿用各城鎮／地點原本的資料。2026-11-03 站長去過商人公會後的傳送地圖有 13 個點（含 Guilde Marchand），確認 13 個都對；傳送點要先走到過才會出現在傳送地圖上。
  - **篩選**（存在 localStorage `sao-map-filter-v4`；預設只開 傳送點、地標、怪物區、一般怪物，其餘關閉（使用者 2026-11-01 指定，`FILT_DEF`）；「全部顯示」全開）：電腦版（≥821px）固定在地圖左側、寬 196px，一直展開，上緣和底圖切換按鈕對齊（top 12px）；探索地圖的說明文字 `#mapNote` 寬 280px、靠左（使用者 2026-11-01 指定），篩選面板的最大高度扣掉說明的高度（`--noteh`，在 renderMap 設定），面板太長時在面板內捲動，不會蓋住說明；手機版用「篩選 ▾」按鈕開關。分兩組（`MAPGRP`）：上「地點」＝傳送點 `tp`、地標 `land`（無法傳送的城鎮和 poi）、採集點 `gather`、NPC `npc`（**依功能分組篩選**（使用者 2026-11-03）：`NGRP`＝藥水・水晶（alchemist＋consumablesMerchants）／收購商（lootBuyers＋weaponSellers）／地下城鑰匙（keyBlacksmith）／飾品（accessoriesBlacksmith＋secretAccessoryBlacksmith＋occultMerchants＋accessoriesMerchants）／武器・防具（weaponsmith＋armorBlacksmith＋equipmentBlacksmith＋equipmentMerchants）／材料加工（materialsBlacksmith＋ingotBlacksmith＋lumberjack）／工具商人／旅行商人／臭乞丐／其他；`npcGrp(c)`。`npcs.js` 保留參考互動地圖的細分類型（`NPCCAT`，不是官方分類），只在 NPC 右側資料寫「類型：…（參考互動地圖的分類）」。地圖圖示和清單用分組的圖示和名稱。篩選存在 `sao-map-filter-v5`（改分組時換版號，舊設定作廢一次）。電腦版只要 NPC 開著就直接顯示在篩選面板右側 `#fpFly`（`syncNpcFly` 把 `#fpNpcBody` 搬過去），不用再點；手機版在 NPC 按鈕下方展開。預設只開 藥水・水晶、收購商、地下城鑰匙、飾品，這 4 組排最上面（`NPC_TOP`））；下「戰鬥」＝世界王 `wboss`、地下城 `dungeon`、怪物區 `area`（kind mob 的地點和框線）、首領 `boss`、小首領 `mini`（重生點標記；2026-11-02 由「區域首領」拆成兩項，和圖鑑標籤一致，`bossCat`）、一般怪物 `mobs`（地點上的一般怪物縮圖）。同時是傳送點的地點，只要「傳送點」或它本身的分類有開就會顯示。右側清單照同樣的篩選，分成 傳送點－城鎮／傳送點－地標／地標／採集點／世界王／地下城／怪物區／首領／小首領（每隻一列，列出可點的重生點座標）／NPC。
  - SPOTS 的 kind：mob（怪物區）、dungeon、poi（地標）、gather（採集點，`gt` = crop／ore／wood，標籤前畫 🌾／⛏️／🪵）、wboss（世界王：參考地圖的 Floor 1 World Event）。Ice Fortress 是 mob（Ice Golem、Ice Spirit），不是首領。
  - **首領／小首領重生點**：`data.js` 的 `BOSS_SPAWNS`（[名稱, x, z, 地下=1]，取自參考地圖 bossSpawns，23 點；Illfang 的 (2,2) 是佔位值，略過）。一隻首領可以有多個重生點（Pumba 5、Guardian Colossal 4、Albal 3）。地圖上畫成怪物頭像圓框 `.bsp`（框線一律實線），地下的在左下角加洞窟小徽章（CSS 內嵌 SVG，本站自畫）；怪物資料列「重生點」座標。原本 kind boss 的 SPOTS（albal、colossal、gorbel、nymbrea）已移除，改用這份資料。
  - **地下城**（kind dungeon，非傳送點）：深紫色名稱框加小箭頭在上、⚔ 方點在入口座標上（`.town.dungeon`），怪物縮圖畫在點的下方。
  - **怪物區名稱**（kind mob，非傳送點）：不畫底框，只有白字加陰影（`.zone.mobarea`），有沒有開「一般怪物」都同一個樣式。名稱（2026-11-01 使用者選 B）：有 wiki 圖鑑表區域名的改用它（Boar Zone、Mizunari Fields、Putrid Swamp、Virelune Lake、Tolbana Mountains、Snow Citadel；`nsrc:"wiki"`，舊名放 `old`，搜尋認舊名）；wiki 區域和附近地點同名的（Spiders→Hanaka、Slimes→Vallhat、Bandits／Ika→Geldorak Mine）保留本站命名（`nsrc:"site"`）。**2026-11-03 對照遊戲圖鑑（Régions）（使用者：有英文的用英文）**：圖鑑名稱本身是英文或專有名詞的改用圖鑑名（Starting Town（原 Town of Beginnings）、Castelbrume；`csrc:1`，面板「名稱：遊戲圖鑑的區域名」）；圖鑑是法文的維持英文名（Wolf Valley、Boar Zone、Putrid Swamp、Giant's Garden、Kobold Tower、Cursed Ruins、OG Quarter），法文圖鑑名放 `csrc`（字串，面板「本站用英文名稱；遊戲圖鑑的區域名是「…」」）和 `old`（搜尋、地點回報比對都認）。ZONES 用英文名。還沒處理：#012 Vallée des Pétales（主線「花瓣谷」，地圖上沒有點）、圖鑑區域 #005／014／015／020／022／024／025／027～031 還沒解鎖。
  - **名稱避讓**（`declutter`，畫完和縮放停下後執行）：傳送點名稱固定；其他名稱（地下城 → 世界王／地標／採集點 → 怪物區）碰到別的點或名稱時：有自己的點（`.pin`）的名稱只能貼著自己的點換位置（下、右、左、上，2026-11-02 改：Harold's Quest 的名稱曾被挪到 Geldorak 旁邊，看起來像在標別的點），沒有點的怪物區名稱才試上、下、右、左、斜角；都沒有空位就在這個縮放倍率先隱藏（放大後會出現）。被傳送點名稱蓋到的點留在名稱框後面（`.town.under-tp`，z-index 4），滑鼠移到它自己的名稱上（或鍵盤聚焦）時才浮到最上層（使用者 2026-11-02 指定；之前是一律提到名稱上面，會壓到傳送點的字）。所有 `.town` 的 z-index 是 5，名稱在怪物縮圖之上。首領頭像左下角的洞窟圖案＝重生點在地下，篩選面板有圖例。
  - **怪物區框線**：SPOTS 的 `area`（[[x,z],…]）是依探索地圖的地形自己描的大略範圍（沒有用參考地圖的多邊形），用 Catmull-Rom 平滑曲線畫在 `.areas` SVG，`vector-effect:non-scaling-stroke` 讓線寬不隨縮放改變。「怪物區」篩選關掉時一起隱藏。
  - **標記樣式**（`.town` 元素，點的中心正好在座標上）：傳送點（城鎮和地標一律）仿遊戲傳送地圖：白色名稱框加向下小箭頭在上、橘色圓點（白框）在座標上，z-index 高於 NPC 圖示；地標（無法傳送）橘色菱形、採集點棕色方點、世界王紅點，這三種的名字寫在點下面。有怪物的傳送地標，怪物縮圖畫在點的下方（`.zone.under`）。`apply()` 的 `--inv` = 螢幕倍率 ÷ 縮放（文字標籤：1.08（整張地圖）→ 0.92（放到最大），手機再乘 0.8）；怪物縮圖和重生點再乘 `--tk`（整張地圖 0.62 → 放大後最多 1，用 CSS `zoom`），所以縮小時圖示小、放大時圖示變大但比地圖慢；框線寬度 `--areaw`。地圖上的怪物大小依類型：首領 50px ＞ 小首領 44px ＞ 一般 38px ＞ 嘍囉 32px（重生點 `.bsp` 也一樣）。NPC 圖示 27px。
  - 只開「傳送點」時，傳送地標（狼之谷、Geldorak、詛咒廢墟）只畫名稱不畫怪物；右側「傳送點－地標」清單也不列怪物。怪物只在它本身的分類（怪物區、地下城）開著時顯示。
  - **NPC**：`npcs.js`（`tools/build_npcs.py` 從參考地圖文字解析產生）。參考地圖 Current Data 有的類別只用 Current；Current 沒有的類別（旅行商人、武器收購商、裝備商人、飾品商人、武器鐵匠、防具鐵匠、金屬錠鐵匠、伐木工）才用它的測試版資料，標「測試版資料」。地圖上畫小圓圖示，點了開右側資料（type "n"）。收購商已從 SPOTS 移到這裡。站長在遊戲裡自己找到的 NPC 放在 `build_npcs.py` 的 `SITE` 清單（src `site`，面板寫「位置取自站長的遊戲影片」），重產 `npcs.js` 時會保留；目前有 臭乞丐（自己一個類別 `beggar`，篩選面板顯示「臭乞丐」（使用者 2026-11-02），預設關閉，Tolbana X 3336、Z 1760，2026-10-30 影片小地圖座標，使用者 2026-11-02 提供名稱）。
  - **第 1 層地圖裁成圓形**（`map.clip:{c:500,r:499.5}`，world 座標；renderMap 對 `img.map` 和 `.tiles` 套 CSS `mask-image` 圓形遮罩）：wiki 地圖島嶼是半徑約 1044/2100 的圓，圓外角落有帶藍的雜訊和 JPEG 痕跡，不管背景什麼顏色都看得出方框（使用者 2026-11-02 要求移除）。標記不受遮罩影響。背景 `--stage` 維持深藍黑（淺色 #0b1219、深色 #070c11）。第 2 層地圖不是圓的，沒有裁。
  - **校正模式**（把「位置未知」的區域放到地圖上、匯出座標）**只給站長用**：網址加 `?edit`（例如 `…/ArgoStrategyGuide/?edit#f2-map`）才顯示右側底部的按鈕列（`EDIT_MODE`），一般模式也不套用瀏覽器裡存的位置（`userPos`）。使用者 2026-11-02 選 A。第 2 層 11 個、第 3 層 13 個區域位置未知，第 2 層開放後可用它放位置再匯出給 Claude。
  - 第 1 層可以切換「wiki 地圖 / 探索地圖」（`sao-map-base`），預設 wiki 地圖。探索地圖用切片載入（`updateTiles`）：L0 一直載入當底，再依縮放倍率 × devicePixelRatio 選層級，只載入畫面內的切片。手機版圖例只留底圖切換按鈕。
- **座標**：
  - 第 1 層地圖 size 4980，**x0 = z0 = 70**。這是用 SIFT 比對 JourneyMap 和 wiki 地圖得出的，806 組特徵點吻合。原本以為是 0，所有點都偏了約 70 格，已經修正。
  - 第 2 層：size 2124，x0 = z0 = −1062。
- 城鎮名稱用英文（`n`），中文放 `zh` 當副標，例如 Town of Beginnings（起始之城），比照 SPOTS 的 Wolf Valley（狼之谷）。
- **怪物詳細資料**：顯示等級（玩家回報優先；沒有回報時用 M 第 11 欄 `lvShot`，來自使用者的遊戲截圖，標「遊戲截圖」。目前有 Cursed Nazgul Protector LV 8（兩階段打法寫在說明欄）、Small／Healer／Mage Slime LV 4（2026-11-03 晚間截圖））。掉落物第 3 欄 `"wiki"`＝遊戲圖鑑截圖沒有、只有 wiki 有記錄，怪物和物品面板顯示「只有 wiki 有記錄」標籤（`.wonly`；Skeleton Wizard 的 Skeleton Mage／Shaman Staff 2%，使用者 2026-11-03 選加回）、圖鑑出沒提示、掉落物、相關任務、回報截圖。
- **回報對應到哪隻怪物**（`findMon`／`renameMon`，遊戲圖鑑截圖優先於 wiki）：① 審核備註有「舊名：X」→ 對應 X 並改成回報的名字；② 正式三位數圖鑑編號（#018）→ 對應同編號的怪物，名字不同就改名（`014-2` 這種非正式編號不拿來比對）；③ 名稱或舊名（aka）相同；④ 都對不上才新增「玩家回報新增」。改名時舊名進 aka，搜尋、地圖位置、圖鑑提示都照常；回報的圖鑑區域顯示在怪物資料上，正式編號會補上沒有編號的怪物。測試：`tests/report_rules_test.py`。
- **玩家回報的處理**（`normRep`）：表單送來的 `raw`（題目名稱 → 答案）在網頁端解讀成等級、座標、圖鑑編號、掉落物等欄位。新種類（測試 `tests/report_types_test.py`）：
  - 配方（`recipe`，題目「配方・NPC／分類／材料／費用 Col／製作時間（秒）／需求等級／稀有度」）：建 `RECIPES` 前合併，同 NPC＋同名物品取代（保留官網 id），否則新增；來源 `rep`，第 10 欄是回報編號。材料名用 `REP_MAT` 對照（同 build_recipes 的 MAT）。
  - 任務追蹤（`quest`，「任務・種類／編號／目前步驟／NPC／座標／獎勵」）：主線用名稱對 `SAO_MAINQ`，有編號就設 `n`、清掉 `nEst`、記 `nRep`；回報列在任務面板「玩家回報」。支線用標題或 NPC 對。
  - 技能（`skill`，「技能・職業／主動或被動／解鎖等級／說明原文／冷卻或消耗」）：`CLS[].reps`，職業面板「技能（玩家回報）」。
  - 地點（「地點・種類」加了 傳送點、怪物區；「地點・在地下嗎／傳送選單名稱／NPC 類別」）：NPC → `SAO_NPCS` 新列（類別中文對 key，對不上用 `other`）；首領位置＋對得上怪物（第 1 層）→ `BOSS_SPAWNS`；其他新增成 SPOTS（`src:"rep"`、`rep` 回報編號、`u` 地下）；地圖上已有同名地點／城鎮的只掛 `reps`（面板顯示回報座標），不移動。
  - 掉落物名稱全部對得上物品資料時，才取代 wiki 的掉落表；對不上就以文字列出。
  - 工具裡沒有的怪物，會自動新增成「玩家回報新增」的怪物，放在 zone `rep`。
- **打包探索地圖**（2026-11-02，`#jmPack`，`jmRun`）：玩家選 JourneyMap 的 `mp` 資料夾（`webkitdirectory`，檔案只在瀏覽器處理）。`jmGroups` 只收 `…/day/x,z.png`、依資料夾分組；`jmAnalyze` 把每張圖以 1/4 畫到 1280px canvas，和 L1 切片（1 px＝4 格）在已探索區塊（`explored.png`）上逐塊比色：重疊 ≥ 20 塊且中位數 ≤ 20 ＝第 1 層（實測：真的 6～7、別處真實地形 29～37、雜訊 65）；`few`＝重疊太少、`other`、`out`。只打包有 ≥ 4 個新區塊的區域，每一份再補重疊的區域到 60 塊（`jmPlan`，伺服器才能再驗證），超過 40 MB 自動分份；`jmZip` 自己寫的 STORE zip（保留資料夾路徑和檔案時間）。參數 `JMP`（測試用 `window.__JMP`），結果 `window.__jm`。
- **回報分頁**：`FORM_PREFILL`（優先用 `formcfg.js` 的 `SAO_FORM.prefill`）有值時顯示 Google 表單大按鈕，`formUrl(FL)` 把所有 `{floor}` 換成目前樓層；「提出建議」用不帶預填的網址（建議不問樓層）；沒有值時退回舊的 GitHub issue 流程。有未送出的 Google 表單草稿時，用預填連結打開會跳「繼續使用目前的草稿？」（Google 表單的行為）；使用者 2026-11-02 選 A：維持預填，不改。
- **探索地圖貢獻**（2026-11-02，使用者指定）：底圖切到探索地圖時，底圖按鈕下方 `#jmCredit`（z-index 8，背景 0.9 不透明）先列「第 N 層已探索 X%」（`SAO_JM["1"].pct`），再列貢獻比例。**手機（≤820px）預設收成一行**「第 N 層已探索 X% ▾」，點了展開（`.open`）；探索地圖說明 `#mapNote` 手機也只顯示一行（…），點了展開（使用者 2026-11-02：手機被遮太多）。站長的遊戲內名稱 **IICHENGII**（`JM_OWNER`，使用者 2026-11-02）。`jmCredits()`：`jmmeta.js` 的 `SAO_JM["1"].chunks`（已探索區塊總數）和 `log[].newChunks`（第一筆 report:null＝站長原本的地圖），名稱依序取 log 的 `by` → reports.js 該回報的暱稱 `by` → 回報名稱（＝表單「探索地圖・貢獻者名稱」，必填）→「未具名玩家」（第一筆沒名字＝`JM_OWNER`）；同名合併，前 5 名＋「其他 N 位」。站長原本的地圖和 R0002（站長測試）在 log 標 `by:"IICHENGII"`。表單的「探索地圖・貢獻者名稱」2026-11-02 02:24 由使用者執行 `upgradeForm`／`upgradeSheet` 加上。**2026-11-03 使用者指出和第 1 頁暱稱重複，`apps-script.gs` 改成不問這題（`CFG.HEAD['探索地圖'].name=null`，`upgradeForm` 刪掉 `JMAP_OLD_NAME`），新的探索地圖回報名稱固定「探索地圖」、貢獻名單用暱稱 `by`；要使用者貼新版 apps-script.gs 並執行 upgradeForm 才生效。**`jm_merge.py` 的 `write_meta` 會寫 `chunks`，第一筆缺 `newChunks` 時用總數補。
- **回報編號連結**（2026-11-03 使用者指定）：網站各處的「回報 R000N」（`repRef`／`repLink`：怪物截圖和掉落、地點座標、任務、技能、配方、NPC 的資料來源）都是 `data-repgo` 連結，`goRep` 切到協作區「攻略資料維護」，把已收錄裡 `li[data-rid]` 那一則捲到中間並閃一下（`.rflash`）；已收錄自己的標題不連。測試在 `report_types_test.py`。
- **已收錄清單**（`#doneL`）：每一則最上面是標題列 `.rhd`「回報 R000N・日期」（含暱稱「X 提供」，使用者 2026-11-02 指定），下面是截圖＋名稱、摘要，最後一行是「看怪物資料／看配方／在地圖上看」等連結（`.rgo`）。
- **處理中的回報**（2026-11-02）：`renderQueue` 用 `fetch("pending.js",{cache:"no-store"})` 讀（不用 script 標籤，避免瀏覽器快取；每分鐘最多重讀一次），攻略資料維護右欄「處理中的回報」列非建議的、問題回報及建議右欄「審核中的建議」（`#ideaQ`，沒有就隱藏）列建議。Apps Script 的 `pendingList_`／`syncPending_` 在送出、改狀態、`processQueue`、`retryApproved` 時更新，內容有變（MD5 存在指令碼屬性 `PENDING_SIG`）才 commit；退回保留 `PENDING_REJECT_DAYS`＝14 天；`syncPending` 手動整份重寫。測試：`tests/apps_script_test.js`、`tests/report_types_test.py`。

## 玩家回報流程（Google 表單）

1. 玩家填 Google 表單，必須登入 Google 才能上傳截圖。**第 1 頁只有「回報者・遊戲內暱稱」「回報種類」**（2026-11-02 使用者指定）；樓層、名稱在各種類頁開頭（`CFG.HEAD`：怪物／物品／地點／配方／任務 X・樓層＋X・名稱（配方・物品名稱、任務・標題），物品樓層選填＝各層通用（`floor: null`，網站顯示「通用」），技能、建議只有名稱（技能・名稱、建議・標題），探索地圖都沒有＝第 1 層、名稱「探索地圖」）。`headOf_` 先讀種類頁的題目，沒有再讀舊第 1 頁的「樓層」「名稱」（舊回報；試算表這兩欄不要刪）；審核網頁 `HEAD_FLOOR`／`HEAD_NAME` 同樣。回報種類有怪物、物品、地點、配方、任務追蹤、技能、探索地圖、建議（「建議」一定在最後；截圖頁和建議頁的 goto 是 SUBMIT，所以**建議和探索地圖填完直接送出**）。`upgradeForm` 負責搬題目、刪舊題、寫 `formcfg.js`；探索地圖的上傳題目「探索地圖・壓縮檔」要手動加。題目／欄位名稱比對用 `hn_`（忽略空白和中點寫法；R0002 因手動加的上傳題目多了空白而找不到壓縮檔，2026-11-02 修），審核網頁同樣。最後一頁是上傳題目「截圖」。
   - **探索地圖**（`jmap`）：**送出時 `onReportSubmit` 自動核准**（審核備註「自動核准：探索地圖由程式比對網站地圖檢查」，不用截圖；使用者 2026-11-02 指出人工審核看不出 zip 是哪個世界，選 A：網站打包工具＋程式檢查）。`publishJmap_` 把 zip（≤ 45 MB、只收第 1 層）放到 GitHub Release `jmap-回報編號`：**先建草稿、上傳 zip、再 PATCH `draft:false` 發佈**（發佈才觸發 Actions；2026-11-02 R0002 因為先發佈再上傳，Actions 找不到檔案而失敗；Actions 下載也會重試 6 次，下載失敗時不刪 Release），「處理結果」寫「已送去合併」（`done_` 視為完成，不會重做）；之後由 GitHub Actions 合併。網站回報清單從 `jmmeta.js` 的 `results` 顯示「合併中／已合併／沒有合併：原因」。
   - **回報者暱稱**（2026-11-02）：第 1 頁「回報種類」前面的選填題「回報者・遊戲內暱稱」（`CFG.Q_NICK`，`upgradeForm` 會補）。網站 `normRep` 讀成 `r.by`（最多 32 字），`repRef` 顯示「暱稱 提供」，玩家建議顯示「暱稱 提出」，任務／技能回報列也會帶上。
2. 回報進到使用者 Google 帳號裡的試算表「Aincrad 查詢工具・回報審核」的「回報」分頁。程式自動填上回報編號 R0001…，狀態設為「待審核」。
3. 審核員（試算表編輯者，只能改「狀態」和「審核備註」）把狀態改成「核准」。**一個人核准就上線。**
4. Apps Script 的觸發器會縮小截圖，存到 `reports/R000N.jpg`，把資料加進 `reports.js`，再寫回「處理結果」欄。
5. GitHub 金鑰是 fine-grained token，只限這個 repo 的 Contents 讀寫。存在 Apps Script 的指令碼屬性 `GITHUB_TOKEN`。**不要叫使用者把金鑰貼到對話裡。** 金鑰到期後換新，再執行 `retryApproved`。
6. 之後改表單：網站靠題目名稱判斷內容（例如「怪物・等級」），所以題目改名要同步修改 `RAWF`（在 `src/index.html`）。「回報種類」「截圖」「探索地圖・壓縮檔」、`CFG.HEAD` 的樓層／名稱題目，以及試算表的四個審核欄位，名稱都不要改。

## 目前狀態和待辦（2026-10-31）

- 裝備圖示：只剩官方還沒做模型的幾件（例如 Bottes de l’écume、情人節系列）用 ⚔️/🛡️/💍 佔位。截圖來源依序：官方 16×16 圖示 → 官網搜尋卡片縮圖 `.w-it .ph`（去背）→ 卡片破圖時改截右側檢視器 `.w-stage` 的 three.js 畫面。
- [x] 高解析度地圖（C1）：2026-10-31 用使用者 JourneyMap 原尺寸重做第 1 層探索地圖並改成切片。2026-11-01 用 jm-upload-2 更新（62 張，島上探索範圍 32.4% → 38.2%，新增 Virelune 往北經 Candelia 到 Kobold Tower 的路線）。之後使用者會改用本機 Claude Code 直接執行 `tools/jm_tiles.py` 並 push，不再走 release。
- **2026-11-02 起 JourneyMap 一律走合併**：玩家和站長都用表單「探索地圖」上傳（或本機 `python3 -I tools/jm_merge.py <day 資料夾>` 後 commit 切片、`explored.png`、`jmmeta.js`），不要再用 `jm_tiles.py` 整張重做。以下是舊流程，僅供參考。
- JourneyMap 更新流程（舊）：**雲端工作階段連不到使用者的 Windows 電腦**（Remote Control 不支援 Windows）。使用者讓 GPT 在電腦上打包 `jm_export.zip`，用 `gh release create jm-upload-N ... --prerelease` 上傳到 GitHub Release。下載 `https://github.com/Cheng-1001/ArgoStrategyGuide/releases/download/jm-upload-N/jm_export.zip`，第 1 層是 `Triggers_815bd3d6-…/overworld/day`，執行 `tools/jm_tiles.py`，更新 `jmDate`。用完請使用者刪掉 release。
- [x] 玩家回報 JourneyMap（2026-11-02 做好，使用者選 A：表單上傳 zip，全自動合併；同日改成網站打包工具＋送出自動核准）。
- [x] 探索地圖端到端測試（2026-11-02 01:18，R0002，站長自己的地圖）：送出自動核准 → Release（草稿→上傳→發佈）→ Actions 合併成功：52 張、2 個第 1 層資料夾、重疊 25894 區塊、新增 27 區塊（探索比例仍 28.5%，站長的地圖本來就是網站底圖）。

- [x] Google 表單端到端測試（2026-11-01）：R0001 Young Spider LV3 核准後自動寫入 `reports.js` 和 3 張截圖，網站顯示等級 3。checkSetup、分頁跳轉都已確認。Drive 縮圖（`=s1600`）可用，但當時存成 PNG（每張 1.7 MB），已手動轉成 JPEG。
- [x] 審核畫面（2026-11-01 使用者執行 `upgradeSheet` 確認）：「截圖預覽」用 `newCellImage` 嵌 base64 縮圖可正常顯示（Drive 檔案不公開）、「內容摘要」、原始欄位收起、整列依狀態上色；表單「截圖」頁換成 F2 說明。截圖一律轉 JPEG。注意：Google 會把回應表自動轉成「表格」（Form_Responses），表格標題預設白字，所以標題要明確設深色字。
- 使用者的 Chrome 會把表單誤判成簡體並自動翻譯（出現「內置」「文件夾」等用詞），原文是繁體，不用改。
- [x] **審核網頁**（2026-11-02 使用者部署：enableReviewQueue、新專案、網頁應用程式，看得到 R0001／R0002。截圖出現「沒有檢視權限」（擁有者本人也是，Drive API 回 403/404，原因待確認），`apiShot` 回傳 `{src, via, why, ms}`，依序試：進階服務 Drive 或直接呼叫 Drive API 拿 thumbnailLink 下載 → `drive.google.com/thumbnail?id=&sz=w1600`（第二入口）→ `DriveApp.getFileById` 讀原檔；不是走縮圖時，審核網頁截圖下方 `#shotVia` 顯示讀取方式、秒數和縮圖失敗原因（2026-11-02 使用者回報：多數 7～14 秒、執行項目沒有記錄；831faba 部署後截圖下方沒有灰字＝縮圖路線成功）（使用者確認讀原檔可以顯示，但很慢；改讀原檔時 `console.log` 原因，在專案「執行項目」看得到）；錯誤訊息附上 Google 原始錯誤。前端 `getShot` 每張只請求一次，`prefetch` 背景載入同一筆其他截圖和下一筆的第一張）。原文：（2026-11-01 做好，等使用者部署，步驟在 SETUP.md「審核網頁」）。設計：獨立專案、以「存取的使用者」執行，所以審核員用自己的 Google 帳號、權限就是試算表編輯權；網頁只改「狀態」「審核備註」（`apiDecide`，已被處理過的不覆蓋，備註前面加「審核：帳號」）。程式改儲存格不會觸發 onEdit，所以主程式的 `processQueue` 每分鐘把「核准且處理結果空白」的列送上線、「退回」的寫結果；`enableReviewQueue` 建這個觸發器，並把表單截圖資料夾以檢視者分享給所有試算表編輯者（審核網頁用審核員自己的權限讀 Drive 縮圖）。佇列預設怪物、物品優先，再依時間。
- 改了 `apps-script.gs` 或審核網頁後：`node tests/apps_script_test.js`（含假表單上的 `upgradeForm` 測試）、`python3 tests/review_test.py` 都要 ALL PASSED。改了回報解讀要跑 `python3 tests/report_types_test.py`、`tests/report_rules_test.py`。
- [ ] 第 2、3 層和 Kobold、Taurus 地下城 **11/4 20:00 巴黎時間＝台灣 11/5（四）03:00 開放**（官方 2026-10-28 公告；網站提示、樓層選單、Kobold Tower 說明都寫台灣時間）。使用者通知後，重新抓 wiki 和官網資料，比對差異後更新 `data23.js`。第 3 層還沒有地圖。
- [ ] 物品類型的回報，目前只出現在「已收錄」清單，還沒整合進物品詳細資料（地點回報 2026-11-02 已整合成地圖點位）。
- [x] 使用者執行 `upgradeForm`（2026-11-01 22:05，執行記錄：回報種類 8 個、共 58 題）。
- [x] 2026-11-02 表單改版＋探索地圖改成打包工具／自動核准：使用者已貼新版 `apps-script.gs`、執行 `upgradeForm`（`formcfg.js` 已寫入 4 個樓層題）、加上傳題目、`upgradeSheet`、`retryApproved`，R0002 合併成功。[ ] 審核網頁部署時要用新版 `review.gs`。
- [x] 使用者貼上新版 `apps-script.gs` 並執行 `syncPending`（2026-11-01 21:57，Apps Script commit「處理中的回報：0 則」）。
- 已知限制：
  - 第 1 層只剩 Skeleton、Kazor 沒有座標（參考互動地圖的 Current Data 也沒有 Kazor）；第 2 和第 3 層全部怪物的區域沒有座標。
  - 和參考互動地圖還沒對齊的差異：城鎮座標（起始之城、Castlebrume、Candelia、Virelune 差約 100 格）、多個怪物名稱不同（例如 Black/White Sinister Wolf、Little Slime、Slime Magician、Robust Bandit、Tank Skeleton、Mage Sylvester）、它的 8 個英文支線任務和其他 NPC（飾品鐵匠、鑰匙鐵匠、神秘商人等）。
  - wiki 的 Bestiary 表會留著 2026-06（Seas）加的**舊條目**（沒有圖鑑編號），10 月（SpaceKat）照遊戲圖鑑補新條目時沒刪。已合併：Mountain Stag → #018 Mountain Deer、Sylvan Mage → #012 Woodland Mage（舊名放 aka）。重抓 wiki 時用 Bestiary 頁的編輯歷史判斷新舊，不要再把沒編號的舊條目當成另一隻。沒編號的「Skeleton」也是 6 月舊條目，還不知道對應哪一隻，先保留。
  - Sissou 任務的「harpies des vents」找不到對應的怪物。
  - 還有幾個未知物品：Arc courbe、bûches de ???、Sac à dos、Sylvan/Skeleton Shaman Staff、兩種 Scroll、Curved Bow。

## 使用者電腦上的資料（要連上使用者電腦才讀得到）

- 遊戲資料夾：`C:\Users\Administrator\AppData\Roaming\.Triggers Client\instances\Sword Art Online`
- **讀檔工具會擋任何含「~」的路徑。** JourneyMap 的世界資料夾名稱有「~」，例如第 1 層是 `journeymap\data\mp\Triggers_815bd3d6~f22f~4114~a601~dfcf0a106221\overworld`。所以要請使用者先執行遊戲資料夾裡的 `export_map.bat`，再從 `jm_export\Triggers_815bd3d6-…\overworld\day\*.png` 讀取。
- JourneyMap 地圖格式：每張 512×512，對應 1 格方塊 1 像素，檔名 `x,z.png` 代表方塊座標 x×512、z×512。重新拼接地圖時：
  1. 用世界座標貼上每一張。
  2. 裁切範圍 [70, 5050]，縮成 3000px。
  3. 疊在變暗的 `floor1.jpg` 上（色彩 0.35、亮度 0.45）。
  4. 輸出成 `floor1_jm.jpg`，並更新 `jmDate`。
- 圖鑑資料（掉落率、描述）是伺服器即時傳送的，電腦上沒有存檔，只能靠截圖或回報取得。
- `mods/SAOUI-*.jar` 裡的 `assets/saoui/codex/hints.json` 是圖鑑提示文字。資源包 `resourcepacks/sao.zip` 只拿來比對圖示，**不要把原始素材放上網站**，裡面很多是伺服器買來的付費素材。只放工具需要的小圖示。
- 讀資源包時只讀資料檔，不反編譯程式碼。
- **官網使用條款（2026-11-01 查，saominecraft.com/fr/legal/conditions-utilisation，2026-10-24 版，法文版為準）**：第 5 條「禁止複製、擷取、重製（copier, extraire, reproduire）全部或部分服務，除非有書面授權或法律明文的例外」；第 8 條「軟體、介面、文字、資料庫、圖像元素等屬於 Triggers SAO 或各權利人」。沒有給攻略站、粉絲站或 wiki 的素材使用規定，也沒有「小圖示可以用」的例外。聯絡信箱 contact@triggersstudio.com。所以上面「只放小圖示」只是降低風險的自訂做法，**不是條款允許的**。使用者 2026-11-01 了解條款後決定：網站加版權聲明（選項 C：樓層列「非官方攻略・版權聲明」→ `legalDetail()`、README「版權聲明」），**不寄信**；`tools/recipe_icons.py` 可以執行，但**資源包只在使用者電腦本機分析，GitHub 只放選定的 48px 圖示**（不放資源包、其他貼圖、候選對照圖）。

## 抓資料的方法

- wiki：MediaWiki API `https://saominecraft.wiki.gg/api.php?action=parse|query`。雲端環境的 curl 可能被網路擋，要改用瀏覽器工具。
- 官網物品圖鑑：對 `/wiki?page=N` 發 fetch，帶標頭 `RSC: 1`，從回應中解析 `{"items":[...]}`（共約 1,382 項）。
- 物品圖示的來源，依序嘗試：
  1. 官網的 `image_url`。
  2. `/item-models/index.json` → `/item-models/m/{path}.json` → 貼圖 `/item-models/t/{hash}.png`。
  3. 截官網物品卡片的 3D 渲染圖。
