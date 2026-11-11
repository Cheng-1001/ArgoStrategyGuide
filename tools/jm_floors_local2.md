# 給本機 Claude Code：把第 2、3 層候選世界的地面圖推上來（第二步）

`inbox/jm_folders.json`（d9e6f5f）看起來：第 2 層＝`Triggers_ba411067…/overworld`，第 3 層＝`Triggers_95a78a58…/overworld`（座標範圍和參考互動地圖的第 2、3 層吻合）。要用圖片內容確認，並當作第 2、3 層探索地圖的第一份。

---

請幫我複製幾個 JourneyMap 世界資料夾的地面圖到 repo，**只複製檔案，不改任何遊戲檔案**。

1. 來源都在
   `C:\Users\Administrator\AppData\Roaming\.Triggers Client\instances\Sword Art Online\journeymap\data\mp`
   底下（資料夾名稱有「~」，請用 PowerShell `Copy-Item -LiteralPath` 或 Bash `cp`，不要用讀檔工具開）。
2. 對下面每一個「伺服器資料夾開頭／世界資料夾」，把它的 **`day` 資料夾和所有整數名稱的資料夾**（例如 `-1`、`0`、`5`、`12`，＝洞穴的高度層）裡的 `x,z.png` 複製到 repo 的
   `inbox/jm_f23/<伺服器資料夾開頭 8 碼>_<世界資料夾名稱>/<子資料夾>/x,z.png`
   （不要複製 `night`、`topo`、`biome`）：
   - `Triggers_ba411067` / `overworld`
   - `Triggers_ba411067` / 名稱以 `_djt` 結尾的兩個世界資料夾
   - `Triggers_95a78a58` / `overworld`
   - `Triggers`（沒有 UUID 的那個）/ `overworld`
   - `Triggers_b7cfe0ee` / `gorge_rugiboeuf`
   - `Triggers_81292594` / `repaire_velindra`
   - `Triggers_b2318f76` / `chambre_ambre`
   - `Triggers_7ee58910` / `pre_breches`
3. 另外寫 `inbox/jm_f23/notes.txt`，用你知道的（或問我）寫下：這幾天在第 2 層、第 3 層各去過哪裡（城鎮、地下城、首領），以及 Rugibœuf、Velindra 這兩個資料夾是不是首領房間。不知道就寫不知道。
4. `git add inbox/jm_f23`，commit 訊息「第 2、3 層 JourneyMap 地面圖」，推到分支 `claude/affectionate-heisenberg-o71cvy`（先 `git pull --rebase origin claude/affectionate-heisenberg-o71cvy`）。**只推 `inbox/jm_f23`**。
5. 完成後告訴我 commit 編號和總共幾張、多大。

---

雲端收到後：拼圖、和 wiki 第 2 層地圖比對，確認樓層，校正第 2、3 層的座標，做成 `tiles/f2jm`、`tiles/f3jm`，再改打包工具和 `tools/jm_merge.py`。`inbox/` 用完從分支刪掉。
