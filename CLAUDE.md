# ArgoStrategyGuide：SAO Minecraft「Aincrad 樓層查詢工具」

給接手的 Claude 工作階段看的專案說明。使用者（Cheng-1001）用中文溝通。

## 和使用者合作的方式

- **一律用中文回覆。**
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
| `hints.js` | 遊戲圖鑑的 LOCATION HINT，對應到 41 隻第 1 層怪物（`sure=0` 表示依順序推斷） |
| `items.png` | 物品圖示表：64px 一格、一列 8 格，目前用到第 185 格。物品資料的最後一個欄位就是格子編號 |
| `floor1.jpg`、`floor2.jpg` | wiki 地圖 |
| `floor1_jm.jpg` | 第 1 層「探索地圖」：使用者的 JourneyMap 疊在變暗的 wiki 地圖上 |
| `reports/` | 回報截圖 |
| `google/apps-script.gs` | Google Apps Script（獨立專案）：建立表單和試算表，核准後透過 GitHub API 寫入 `reports.js` 和截圖 |
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

- **網址格式**：`#f{樓層}-{分頁}`，分頁有 map / monsters / items / quests / bosses / report。樓層選擇器支援 1～100 層；不存在的樓層會回到第 1 層。
- **地圖**：
  - 依點位顯示怪物縮圖；縮小時只顯示最主要的一隻加「+N」。
  - 圖例可以隱藏首領、小首領、一般怪物、村鎮（存在 localStorage `sao-map-hide`）。
  - 第 1 層可以切換「wiki 地圖 / 探索地圖」（`sao-map-base`）。手機版會把整個圖例藏起來，所以手機上切換不了，還沒處理。
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

- [ ] **Google 表單第一筆端到端測試還沒做。** 使用者已經執行 setup 和 repair，也給了預先填好樓層的網址；「截圖」上傳題目加了沒、checkSetup 有沒有通過，都還沒確認。測試建議：送 Young Spider LV3（座標 1340, 3569）→ 核准 → 看「處理結果」→ 網站顯示等級 3。截圖縮圖用的是 Drive thumbnailLink（`=s1600`），這部分還沒驗證過；失敗時會改傳原始檔（8 MB 以內）。
- [ ] 確認表單「回報種類」的分頁跳轉：怪物 → 第 2 區段、物品 → 第 3 區段、地點 → 第 4 區段；第 2、3 區段結束後都跳到第 5 區段（截圖）。
- [ ] 手機上看不到底圖切換按鈕，要找手機也看得到的位置。
- [ ] 第 2、3 層預計 **11/4 開放**（遊戲改版）。使用者通知後，重新抓 wiki 和官網資料，比對差異後更新 `data23.js`。第 3 層還沒有地圖。
- [ ] 物品和地點類型的回報，目前只出現在「已收錄」清單和地圖的回報標記上，還沒整合進物品詳細資料和地圖點位。
- 已知限制：
  - 第 1 層有 20 隻、第 2 和第 3 層全部怪物的區域沒有座標。
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
