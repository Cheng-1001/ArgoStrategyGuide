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
| `index.html` | build 產生的檔案，不要直接改 |
| `data.js` | 第 1 層：`window.SAO` = MAP、STATUS、ZONES、M（怪物）、ITEMS、EXTRA、TOWNS、SPOTS、QUESTS |
| `data23.js` | 第 2、3 層：`SAO23_ITEMS`、`SAO23.floors[2/3]`（第 3 層沒有地圖） |
| `bosses.js` | 世界首領 Galiath、獨特怪物 Seraphel、wiki 列的其他首領 |
| `reports.js` | 已收錄的玩家回報。格式必須維持 `window.SAO_REPORTS = <JSON 陣列>;`，Google 程式會自動讀寫它 |
| `mainq.js` | 第 1 層主線任務 `window.SAO_MAINQ[1]`：說明取自 wiki 主線表，步驟順序和座標取自參考互動地圖，步驟文字是本站中文改寫。步驟格式 `[文字, x, z, 約略]` |
| `equip.js`、`equip.png` | 裝備分頁：官網物品圖鑑的 656 件裝備（武器、盾、防具、飾品），由 scratchpad 的 `build_equip.py` 產生，不要手改。`equip.png` 48px 一格、一列 16 格 |
| `recipes.js` | 第 1 層配方，`tools/build_recipes.py` 產生（不要手改）。key 是 NPC 名稱；每筆 `[官網圖鑑 id 或 null, 遊戲英文名, 秒數, [[材料, 數量]], Col（"Free"；null＝未知）, 稀有度, 分類 weapon/armor/acc/potion/key, 等級, 來源 shot/ref]`。來源：使用者截圖（`SHOTS`，優先）＋參考地圖 eCompendium Current Data 的材料清單（只取事實；鯊魚飾品 4 筆和截圖完全相同）。英文名對官網 id 是人工對照表 `OID`（官網數值改版過，無法用屬性自動配對；藥水、水晶、強化藥、鑰匙 17 筆在 2026-11-01 補上，名稱和等級都吻合才收。官網沒有的：Mana Potion I、Quality Mana/Stamina Potion I～III、Teleportation Crystal、Kobold Key、Purification Elixir，維持 🧪/🔑 佔位），材料名對照表 `MAT`（Small Purse＝Small Pouch、Shark Carapace＝Shark Shell、Sylve Shoot＝Sylvan Sprout…）。武器、防具目前只有起始商人賣的新手裝備 |
| `recicons.js`、`icons/recipes/`、`tools/recipe_icons.py`、`tools/recipe_icons.json` | 官網圖鑑沒有的配方（Quality Mana/Stamina Potion 等 10 種）的圖示。**只能在使用者電腦上用本機 Claude Code 執行**：`find` 從 `sao.zip` 列出候選並輸出對照圖（不要 commit），把選定的貼圖路徑填進 `recipe_icons.json`，`build` 只把這幾張縮成 48px 寫進 `icons/recipes/` 和 `recicons.js`。`recIcon` 優先用官網圖示，沒有才用這裡的 |
| `classes.js`、`tools/build_classes.py` | 職業／技能分頁（`#classes`）。`build_classes.py` 讀 wiki 的 Classes 和 6 個職業頁（API parse 存成 JSON）、參考地圖 `Aincrad/Character Build` 的起始屬性／每級成長／天賦樹（文字解析）、`equip.js` 的職業限制。說明是本站中文改寫（`ZH` 對照表）。**不放任何職業或技能圖片**（使用者 2026-11-01：官方用的 SAO 原作圖片、圖示、標誌不要放，官方沒有原作授權）。wiki 除戰士外的技能圖示都是佔位圖（同一人 2026-04-18 一次建立），標「技能待確認」；武鬥家（Martial Artist）官方圖鑑沒有裝備、參考地圖也沒有屬性，標「可能尚未開放」 |
| `hints.js` | 遊戲圖鑑的 LOCATION HINT，對應到 41 隻第 1 層怪物（`sure=0` 表示依順序推斷） |
| `items.png` | 物品圖示表：64px 一格、一列 8 格，目前用到第 185 格。物品資料的最後一個欄位就是格子編號 |
| `floor1.jpg`、`floor2.jpg` | wiki 地圖。floor1.jpg 原本在 X 1652、Z 2770（腐臭沼澤北邊麥田旁）有一個 wiki 編輯者留下的測試路標「sdsd」，另外 X 1917–1967、Z 2412–2495 有一塊黑色 T 形破圖。2026-11-01 修掉：路標那一處用使用者 JourneyMap 的真實地形縮到 wiki 解析度、做色調轉換後貼上；黑色 T 處 JourneyMap 沒資料，改搬旁邊的森林紋理。之後換新的 wiki 地圖要再檢查一次 |
| `floor1_jm.jpg` | 第 1 層「探索地圖」3000px 預覽：使用者的 JourneyMap 疊在變暗的 wiki 地圖上（網站實際用 `tiles/f1jm`） |
| `tiles/f1jm/{L}/{c}_{r}.jpg` | 第 1 層探索地圖切片：256px，L0～L3 = 640／1280／2560／5120px，L3 是 1 格 1 像素。由 `tools/jm_tiles.py` 產生 |
| `tools/jm_tiles.py` | JourneyMap day 圖 → `floor1_jm.jpg` ＋ 切片（用法寫在檔案開頭） |
| `tools/build_equip.py` | 產生 `equip.js`／`equip.png`。要先在工作目錄準備官網圖鑑 `catalog.json`、`im_index.json`、官方圖示和 3D 截圖（做法見「抓資料的方法」） |
| `reports/` | 回報截圖 |
| `google/apps-script.gs` | Google Apps Script（獨立專案）：建立表單和試算表，核准後透過 GitHub API 寫入 `reports.js` 和截圖 |
| `google/review.html`、`google/review_server.js` | 審核網頁（另一個 Apps Script 專案）的前端和後端原始檔。改完執行 `python3 tools/build_review.py` 產生 `google/review.gs`（使用者貼這個檔） |
| `google/review.appsscript.json` | 審核網頁專案的資訊清單：最小權限（spreadsheets、drive.readonly、external_request、userinfo.email），以「存取的使用者」身分執行 |
| `tests/review_test.py`、`tests/apps_script_test.js` | 審核網頁前端（假的 google.script.run）和 Apps Script 後端（假的試算表）的本機測試 |
| `google/SETUP.md` | 給使用者看的表單、審核設定說明 |
| `tools/export_map.bat` | 使用者電腦上用的：把 JourneyMap 地圖複製到沒有「~」的資料夾 |
| `tests/smoke.py` | Playwright 冒煙測試 |
| `.github/ISSUE_TEMPLATE/` | 舊的 GitHub 回報表單，保留但已不是主要管道 |

## 修改和發佈流程

1. 改 `src/index.html`，或根目錄的資料檔。
2. `python3 src/build.py`
3. `python3 tests/smoke.py`，要看到 ALL PASSED。改了畫面的話，另外用 Playwright 截圖親眼確認，電腦寬度（1280）和手機寬度（390）都要看，手機不能左右捲動。
4. commit，訊息結尾附上工作階段規定的署名行，然後 push 到 `main`。GitHub Pages 大約 1～3 分鐘後更新。使用者看到舊畫面時，請他按 Ctrl+F5。
5. Google Apps Script 也會直接 commit 到 `main`。**push 之前先 `git pull --rebase`**，避免和自動收錄的回報衝突。

## 網站功能（`src/index.html`）

- **網址格式**：`#f{樓層}-{分頁}`，分頁有 map / monsters / equip / items / props（圖鑑的子分頁）、quests、recipes、classes、bosses、report。上方選單：地圖／圖鑑／任務／配方／職業／技能（手機顯示「職業」）／世界王／回報區。
- **版權聲明**：樓層列的「非官方攻略・版權聲明」→ `legalDetail()`；第一句是「本攻略由中文玩家社群協力製作，提供中文玩家使用」（使用者 2026-11-01 指定）。README 同步。**不要放 SAO 原作的圖片、圖示、標誌**，即使官方網站或遊戲有用（官方沒有原作授權）。
- **怪物名稱以官方為準**：以遊戲內圖鑑為準（wiki 圖鑑表顯示的名稱跟著遊戲內圖鑑；wiki 寫成 `[[舊名|新名]]` 時用新名）。改名的怪物把舊名放在 M 的第 10 欄 `aka`，搜尋、回報、圖鑑提示都認舊名。參考互動地圖的怪物名稱是舊名，不要拿來用。
- **任務分頁**：主線（依劇情順序，可以在地圖上畫路線：編號步驟加虛線）和支線（wiki）兩種。主線的 `n` 是遊戲任務追蹤上的編號：wiki 主線表寫明 8～18，R0001 截圖證實「24. The Truth About the Seal」，19～23 依順序；25 以後是推算（`nEst`）；The Trader 之前的編號還不確定，不顯示數字。參考地圖把「The Southern Marshes」(14) 併進「The Suspended City」，已拆開；它把 The Truth About the Seal 標在起始之城也不對，Catherine 在墮落者迷宮門口（X 2382、Z 2415；使用者 2026-11-01 確認，R0001 的任務距離 1565 格也吻合）。拿到玩家截圖裡的任務追蹤畫面時，用來校正編號和步驟。
- **配方分頁**（上方選單的獨立分頁 `#recipes`，在任務和世界王中間）：分類 武器／防具／飾品／藥水／鑰匙、依 NPC 篩選、排序；每張卡片點了開自己的配方面板（type `r`，id 是 `ALLREC` 的索引，所以只會選到一張），面板列 NPC、等級、費用、時間、材料，有對應官網物品時另有「查看裝備／道具資料」按鈕。NPC 資料列「可以製作」，裝備列「製作方式」，材料列「可以拿去製作」。
- **卡片欄數**：寬螢幕（≥1180px）的卡片格線用 `fixCols()` 固定成「右側面板開著時」的欄數，面板開關都不會重排。
- **物品面板的取得方式**：`itemMap` 把掉落怪物的怪物區（或首領重生點）和採集點編號，畫成和任務一樣的小地圖（`routeMini(steps,f,true)`，不畫虛線），列表項目前面有同樣的編號，「放大查看取得地點」開浮動地圖視窗（`openRouteWin(…,true)`）。
- **任務面板**：步驟 → 需要的物品和目標 → 原文 → 來源 → 最下面才是路線小地圖和放大按鈕。
- **裝備分頁**：依部位、職業、稀有度、等級篩選。名稱和描述是官方法文原文；本站 ITEMS 有同名（`fr` 欄位）的會連過去。只有 16×16 的官方圖片直接當圖示，其他用官網搜尋結果卡片 `.w-it .ph` 的 3D 渲染截圖（去背）。樓層選擇器支援 1～100 層；不存在的樓層會回到第 1 層。
- **地圖**：
  - 依點位顯示怪物縮圖；縮小時只顯示最主要的一隻加「+N」。
  - **傳送點**：TOWNS 和 SPOTS 的 `tp` 欄位是遊戲傳送選單上的名稱（法文）。第 1 層 13 個（使用者 2026-11-01 提供的遊戲內傳送地圖）：7 個城鎮（Vallhat 不是，要走山腳的傳送裝置）、6 個地點（狼之谷、Geldorak 礦坑、詛咒廢墟、OG Quarter、巨人花園、商人公會）。地圖上可傳送的城鎮畫藍綠圓點加 🌀，地點標籤加 🌀，右側清單最上面有「🌀 傳送點」。傳送地圖本身沒有座標，座標沿用各城鎮／地點原本的資料。
  - **篩選**（存在 localStorage `sao-map-filter`）：電腦版（≥821px）固定在地圖左側、寬 196px，一直展開；手機版用「篩選 ▾」按鈕開關。分兩組（`MAPGRP`）：上「地點」＝傳送點 `tp`、地標 `land`（無法傳送的城鎮和 poi）、採集點 `gather`、NPC `npc`（18 個子類別：NPC 按鈕下方的「NPC 類別 ▸」，電腦版點了在篩選面板右側彈出 `#fpFly`（`syncNpcFly` 把 `#fpNpcBody` 搬過去），手機版在下方展開）；下「戰鬥」＝世界王 `wboss`、地下城 `dungeon`、怪物區 `area`（kind mob 的地點和框線）、區域首領 `boss`（重生點標記）、一般怪物 `mobs`（地點上的一般怪物縮圖）。同時是傳送點的地點，只要「傳送點」或它本身的分類有開就會顯示。右側清單照同樣的篩選，分成 傳送點－城鎮／傳送點－地標／地標／採集點／世界王／地下城／怪物區／區域首領（每隻一列，列出可點的重生點座標）／NPC。
  - SPOTS 的 kind：mob（怪物區）、dungeon、poi（地標）、gather（採集點，`gt` = crop／ore／wood，標籤前畫 🌾／⛏️／🪵）、wboss（世界王：參考地圖的 Floor 1 World Event）。Ice Fortress 是 mob（Ice Golem、Ice Spirit），不是首領。
  - **區域首領重生點**：`data.js` 的 `BOSS_SPAWNS`（[名稱, x, z, 地下=1]，取自參考地圖 bossSpawns，23 點；Illfang 的 (2,2) 是佔位值，略過）。一隻首領可以有多個重生點（Pumba 5、Guardian Colossal 4、Albal 3）。地圖上畫成怪物頭像圓框 `.bsp`（框線一律實線），地下的在左下角加「⤓」小徽章；怪物資料列「重生點」座標。原本 kind boss 的 SPOTS（albal、colossal、gorbel、nymbrea）已移除，改用這份資料。
  - **地下城**（kind dungeon，非傳送點）：深紫色名稱框加小箭頭在上、⚔ 方點在入口座標上（`.town.dungeon`），怪物縮圖畫在點的下方。
  - **怪物區名稱**（kind mob，非傳送點）：不畫底框，只有白字加陰影（`.zone.mobarea`），有沒有開「一般怪物」都同一個樣式。名稱（2026-11-01 使用者選 B）：有 wiki 圖鑑表區域名的改用它（Boar Zone、Mizunari Fields、Putrid Swamp、Virelune Lake、Tolbana Mountains、Snow Citadel；`nsrc:"wiki"`，舊名放 `old`，搜尋認舊名）；wiki 區域和附近地點同名的（Spiders→Hanaka、Slimes→Vallhat、Bandits／Ika→Geldorak Mine）保留本站命名（`nsrc:"site"`）。**之後要改成遊戲圖鑑的區域原文（使用者選的 A）**：拿到遊戲圖鑑各區域名稱的截圖後照改。
  - **怪物區框線**：SPOTS 的 `area`（[[x,z],…]）是依探索地圖的地形自己描的大略範圍（沒有用參考地圖的多邊形），用 Catmull-Rom 平滑曲線畫在 `.areas` SVG，`vector-effect:non-scaling-stroke` 讓線寬不隨縮放改變。「怪物區」篩選關掉時一起隱藏。
  - **標記樣式**（`.town` 元素，點的中心正好在座標上）：傳送點（城鎮和地標一律）仿遊戲傳送地圖：白色名稱框加向下小箭頭在上、橘色圓點（白框）在座標上，z-index 高於 NPC 圖示；地標（無法傳送）橘色菱形、採集點棕色方點、世界王紅點，這三種的名字寫在點下面。有怪物的傳送地標，怪物縮圖畫在點的下方（`.zone.under`）。`apply()` 的 `--inv` = 螢幕倍率 ÷ 縮放（文字標籤：1.08（整張地圖）→ 0.92（放到最大），手機再乘 0.8）；怪物縮圖和重生點再乘 `--tk`（整張地圖 0.62 → 放大後最多 1，用 CSS `zoom`），所以縮小時圖示小、放大時圖示變大但比地圖慢；框線寬度 `--areaw`。地圖上的怪物大小依類型：首領 50px ＞ 小首領 44px ＞ 一般 38px ＞ 嘍囉 32px（重生點 `.bsp` 也一樣）。NPC 圖示 27px。
  - 只開「傳送點」時，傳送地標（狼之谷、Geldorak、詛咒廢墟）只畫名稱不畫怪物；右側「傳送點－地標」清單也不列怪物。怪物只在它本身的分類（怪物區、地下城）開著時顯示。
  - **NPC**：`npcs.js`（`tools/build_npcs.py` 從參考地圖文字解析產生）。參考地圖 Current Data 有的類別只用 Current；Current 沒有的類別（旅行商人、武器收購商、裝備商人、飾品商人、武器鐵匠、防具鐵匠、金屬錠鐵匠、伐木工）才用它的測試版資料，標「測試版資料」。地圖上畫小圓圖示，點了開右側資料（type "n"）。收購商已從 SPOTS 移到這裡。
  - 第 1 層可以切換「wiki 地圖 / 探索地圖」（`sao-map-base`），預設 wiki 地圖。探索地圖用切片載入（`updateTiles`）：L0 一直載入當底，再依縮放倍率 × devicePixelRatio 選層級，只載入畫面內的切片。手機版圖例只留底圖切換按鈕。
- **座標**：
  - 第 1 層地圖 size 4980，**x0 = z0 = 70**。這是用 SIFT 比對 JourneyMap 和 wiki 地圖得出的，806 組特徵點吻合。原本以為是 0，所有點都偏了約 70 格，已經修正。
  - 第 2 層：size 2124，x0 = z0 = −1062。
- 城鎮名稱用英文（`n`），中文放 `zh` 當副標，例如 Town of Beginnings（起始之城），比照 SPOTS 的 Wolf Valley（狼之谷）。
- **怪物詳細資料**：顯示等級（玩家回報優先；沒有回報時用 M 第 11 欄 `lvShot`，來自使用者的遊戲截圖，標「遊戲截圖」。目前只有 Cursed Nazgul Protector LV 8，牠的兩階段打法寫在說明欄）、圖鑑出沒提示、掉落物、相關任務、回報截圖。
- **回報對應到哪隻怪物**（`findMon`／`renameMon`，遊戲圖鑑截圖優先於 wiki）：① 審核備註有「舊名：X」→ 對應 X 並改成回報的名字；② 正式三位數圖鑑編號（#018）→ 對應同編號的怪物，名字不同就改名（`014-2` 這種非正式編號不拿來比對）；③ 名稱或舊名（aka）相同；④ 都對不上才新增「玩家回報新增」。改名時舊名進 aka，搜尋、地圖位置、圖鑑提示都照常；回報的圖鑑區域顯示在怪物資料上，正式編號會補上沒有編號的怪物。測試：`tests/report_rules_test.py`。
- **玩家回報的處理**（`normRep`）：表單送來的 `raw`（題目名稱 → 答案）在網頁端解讀成等級、座標、圖鑑編號、掉落物等欄位。
  - 掉落物名稱全部對得上物品資料時，才取代 wiki 的掉落表；對不上就以文字列出。
  - 工具裡沒有的怪物，會自動新增成「玩家回報新增」的怪物，放在 zone `rep`。
- **回報分頁**：`FORM_PREFILL` 有值時顯示 Google 表單大按鈕，並把目前樓層帶入表單；沒有值時退回舊的 GitHub issue 流程。

## 玩家回報流程（Google 表單）

1. 玩家填 Google 表單，必須登入 Google 才能上傳截圖。回報種類有怪物、物品、地點，最後一頁是上傳題目「截圖」。
2. 回報進到使用者 Google 帳號裡的試算表「Aincrad 查詢工具・回報審核」的「回報」分頁。程式自動填上回報編號 R0001…，狀態設為「待審核」。
3. 審核員（試算表編輯者，只能改「狀態」和「審核備註」）把狀態改成「核准」。**一個人核准就上線。**
4. Apps Script 的觸發器會縮小截圖，存到 `reports/R000N.jpg`，把資料加進 `reports.js`，再寫回「處理結果」欄。
5. GitHub 金鑰是 fine-grained token，只限這個 repo 的 Contents 讀寫。存在 Apps Script 的指令碼屬性 `GITHUB_TOKEN`。**不要叫使用者把金鑰貼到對話裡。** 金鑰到期後換新，再執行 `retryApproved`。
6. 之後改表單：網站靠題目名稱判斷內容（例如「怪物・等級」），所以題目改名要同步修改 `RAWF`（在 `src/index.html`）。「回報種類」「樓層」「名稱」「截圖」以及試算表的四個審核欄位，名稱都不要改。

## 目前狀態和待辦（2026-10-31）

- 裝備圖示：只剩官方還沒做模型的幾件（例如 Bottes de l’écume、情人節系列）用 ⚔️/🛡️/💍 佔位。截圖來源依序：官方 16×16 圖示 → 官網搜尋卡片縮圖 `.w-it .ph`（去背）→ 卡片破圖時改截右側檢視器 `.w-stage` 的 three.js 畫面。
- [x] 高解析度地圖（C1）：2026-10-31 用使用者 JourneyMap 原尺寸重做第 1 層探索地圖並改成切片。2026-11-01 用 jm-upload-2 更新（62 張，島上探索範圍 32.4% → 38.2%，新增 Virelune 往北經 Candelia 到 Kobold Tower 的路線）。之後使用者會改用本機 Claude Code 直接執行 `tools/jm_tiles.py` 並 push，不再走 release。
- JourneyMap 更新流程：**雲端工作階段連不到使用者的 Windows 電腦**（Remote Control 不支援 Windows）。使用者讓 GPT 在電腦上打包 `jm_export.zip`，用 `gh release create jm-upload-N ... --prerelease` 上傳到 GitHub Release。下載 `https://github.com/Cheng-1001/ArgoStrategyGuide/releases/download/jm-upload-N/jm_export.zip`，第 1 層是 `Triggers_815bd3d6-…/overworld/day`，執行 `tools/jm_tiles.py`，更新 `jmDate`。用完請使用者刪掉 release。
- [ ] 評估讓玩家回報 JourneyMap（像怪物回報一樣）。

- [x] Google 表單端到端測試（2026-11-01）：R0001 Young Spider LV3 核准後自動寫入 `reports.js` 和 3 張截圖，網站顯示等級 3。checkSetup、分頁跳轉都已確認。Drive 縮圖（`=s1600`）可用，但當時存成 PNG（每張 1.7 MB），已手動轉成 JPEG。
- [x] 審核畫面（2026-11-01 使用者執行 `upgradeSheet` 確認）：「截圖預覽」用 `newCellImage` 嵌 base64 縮圖可正常顯示（Drive 檔案不公開）、「內容摘要」、原始欄位收起、整列依狀態上色；表單「截圖」頁換成 F2 說明。截圖一律轉 JPEG。注意：Google 會把回應表自動轉成「表格」（Form_Responses），表格標題預設白字，所以標題要明確設深色字。
- 使用者的 Chrome 會把表單誤判成簡體並自動翻譯（出現「內置」「文件夾」等用詞），原文是繁體，不用改。
- [ ] **審核網頁**（2026-11-01 做好，等使用者部署，步驟在 SETUP.md「審核網頁」）。設計：獨立專案、以「存取的使用者」執行，所以審核員用自己的 Google 帳號、權限就是試算表編輯權；網頁只改「狀態」「審核備註」（`apiDecide`，已被處理過的不覆蓋，備註前面加「審核：帳號」）。程式改儲存格不會觸發 onEdit，所以主程式的 `processQueue` 每分鐘把「核准且處理結果空白」的列送上線、「退回」的寫結果；`enableReviewQueue` 建這個觸發器，並把表單截圖資料夾以檢視者分享給所有試算表編輯者（審核網頁用審核員自己的權限讀 Drive 縮圖）。佇列預設怪物、物品優先，再依時間。
- 改了 `apps-script.gs` 或審核網頁後：`node tests/apps_script_test.js`、`python3 tests/review_test.py` 都要 ALL PASSED。
- [ ] 第 2、3 層預計 **11/4 開放**（遊戲改版）。使用者通知後，重新抓 wiki 和官網資料，比對差異後更新 `data23.js`。第 3 層還沒有地圖。
- [ ] 物品和地點類型的回報，目前只出現在「已收錄」清單和地圖的回報標記上，還沒整合進物品詳細資料和地圖點位。
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
