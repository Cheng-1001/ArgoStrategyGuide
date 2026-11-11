# 給本機 Claude Code：列出 JourneyMap 的世界資料夾（找第 2、3 層存在哪裡）

把下面整段貼給站長電腦上的 Claude Code（在 ArgoStrategyGuide 的 clone 裡開）。

---

請幫我整理 JourneyMap 的地圖資料夾結構，**只讀檔名和資料夾名稱，不讀圖片內容、不改任何遊戲檔案**。

1. JourneyMap 資料夾：
   `C:\Users\Administrator\AppData\Roaming\.Triggers Client\instances\Sword Art Online\journeymap\data\mp`
   資料夾名稱裡有「~」，讀檔工具會擋，請用 PowerShell 的 `Get-ChildItem -LiteralPath`（或 Bash 的 `ls`）列，不要用讀檔工具開。
2. 對 `mp` 底下每一個伺服器資料夾（`Triggers_…`），再對它底下每一個世界資料夾（例如 `overworld`、`…_geldorack`），記錄：
   - `server`：伺服器資料夾名稱，`world`：世界資料夾名稱
   - `layers`：世界資料夾底下的子資料夾名稱（例如 `day`、`night`、`0`、`1`、`-1`），每個子資料夾記：
     - `n`：裡面 `x,z.png` 檔案的數量
     - `xmin`／`xmax`／`zmin`／`zmax`：檔名裡 x、z 的最小和最大值
     - `newest`：最新一張的修改時間（台灣時間，`yyyy-MM-dd HH:mm`）
   - 世界資料夾裡如果有 `waypoints` 或其他設定檔，只記檔名，不要讀內容
3. 另外記：`mp` 底下每個伺服器資料夾的修改時間，以及你看得出來的提示（例如哪個資料夾的檔案是 11/9 之後才出現的）。
4. 寫成 `inbox/jm_folders.json`（UTF-8），格式：
   `{"made":"yyyy-MM-dd HH:mm","root":"…\\journeymap\\data\\mp","servers":[{"server":"…","mtime":"…","worlds":[{"world":"…","layers":{"day":{"n":81,"xmin":…,"xmax":…,"zmin":…,"zmax":…,"newest":"…"}},"files":["…"]}]}]}`
5. `git add inbox/jm_folders.json`，commit 訊息「JourneyMap 資料夾清單」，推到分支 `claude/affectionate-heisenberg-o71cvy`（先 `git pull --rebase origin claude/affectionate-heisenberg-o71cvy`）。**只推這一個檔案**，不要推圖片或其他遊戲檔案。
6. 完成後告訴我 commit 編號。

---

雲端收到後：從資料夾名稱、座標範圍和修改時間判斷第 2、3 層是哪個世界資料夾，再改打包工具（`DG_DIM`／樓層辨認）和 `tools/jm_merge.py`。`inbox/jm_folders.json` 用完從分支刪掉。
