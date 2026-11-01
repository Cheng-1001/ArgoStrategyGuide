# ArgoStrategyGuide：SAO Minecraft「Aincrad 樓層查詢工具」

給接手的 Claude 工作階段看的專案說明。使用者（Cheng-1001）用中文溝通。

## 和使用者合作的方式

- **一律用中文回覆。**
- **用詞**：網站上的中文說明一律把 Aincrad 寫成「艾恩葛朗特」、Fractured Underworld 寫成「破碎的地下世界」（第一次出現可以括號附原文）。遊戲內的英文任務標題、法文物品名、以及使用者 Google 帳號裡已經建立的名稱（「Aincrad 回報自動化」專案、「Aincrad 查詢工具・回報審核」試算表、表單標題）不翻，否則會對不上。
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

- **網址格式**：`#f{樓層}-{分頁}`，分頁有 map / monsters / items / quests / equip / bosses / report。
- **怪物名稱以官方為準**：以遊戲內圖鑑為準（wiki 圖鑑表顯示的名稱跟著遊戲內圖鑑；wiki 寫成 `[[舊名|新名]]` 時用新名）。改名的怪物把舊名放在 M 的第 10 欄 `aka`，搜尋、回報、圖鑑提示都認舊名。參考互動地圖的怪物名稱是舊名，不要拿來用。
- **任務分頁**：主線（依劇情順序，可以在地圖上畫路線：編號步驟加虛線）和支線（wiki）兩種。
- **裝備分頁**：依部位、職業、稀有度、等級篩選。名稱和描述是官方法文原文；本站 ITEMS 有同名（`fr` 欄位）的會連過去。只有 16×16 的官方圖片直接當圖示，其他用官網搜尋結果卡片 `.w-it .ph` 的 3D 渲染截圖（去背）。樓層選擇器支援 1～100 層；不存在的樓層會回到第 1 層。
- **地圖**：
  - 依點位顯示怪物縮圖；縮小時只顯示最主要的一隻加「+N」。
  - **傳送點**：TOWNS 和 SPOTS 的 `tp` 欄位是遊戲傳送選單上的名稱（法文）。第 1 層 13 個（使用者 2026-11-01 提供的遊戲內傳送地圖）：7 個城鎮（Vallhat 不是，要走山腳的傳送裝置）、6 個地點（狼之谷、Geldorak 礦坑、詛咒廢墟、OG Quarter、巨人花園、商人公會）。地圖上可傳送的城鎮畫藍綠圓點加 🌀，地點標籤加 🌀，右側清單最上面有「🌀 傳送點」。傳送地圖本身沒有座標，座標沿用各城鎮／地點原本的資料。
  - 圖例可以隱藏首領、小首領、一般怪物、村鎮、收購商（存在 localStorage `sao-map-hide`）。收購商（spot `kind:"shop"`）在地圖上只畫 💰 小圖示，名稱放在 title。
  - 第 1 層可以切換「wiki 地圖 / 探索地圖」（`sao-map-base`），預設 wiki 地圖。探索地圖用切片載入（`updateTiles`）：L0 一直載入當底，再依縮放倍率 × devicePixelRatio 選層級，只載入畫面內的切片。手機版圖例只留底圖切換按鈕。
- **座標**：
  - 第 1 層地圖 size 4980，**x0 = z0 = 70**。這是用 SIFT 比對 JourneyMap 和 wiki 地圖得出的，806 組特徵點吻合。原本以為是 0，所有點都偏了約 70 格，已經修正。
  - 第 2 層：size 2124，x0 = z0 = −1062。
- **怪物詳細資料**：顯示等級（玩家回報）、圖鑑出沒提示、掉落物、相關任務、回報截圖。
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
- [x] 高解析度地圖（C1）：2026-10-31 用使用者 JourneyMap 原尺寸重做第 1 層探索地圖並改成切片，探索範圍約 25%。
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

## 抓資料的方法

- wiki：MediaWiki API `https://saominecraft.wiki.gg/api.php?action=parse|query`。雲端環境的 curl 可能被網路擋，要改用瀏覽器工具。
- 官網物品圖鑑：對 `/wiki?page=N` 發 fetch，帶標頭 `RSC: 1`，從回應中解析 `{"items":[...]}`（共約 1,382 項）。
- 物品圖示的來源，依序嘗試：
  1. 官網的 `image_url`。
  2. `/item-models/index.json` → `/item-models/m/{path}.json` → 貼圖 `/item-models/t/{hash}.png`。
  3. 截官網物品卡片的 3D 渲染圖。
