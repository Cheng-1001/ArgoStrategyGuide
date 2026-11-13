# 給站長本機 Claude 的指令：官方 BlueMap → 網站「官方地圖」切片

把下面整段貼給本機的 Claude Code（在 ArgoStrategyGuide 的資料夾裡開）。

---

請照下面做，任何一步失敗就停下來，用一句話回報結果，不要自己換方法：

1. `git pull`，切到分支 `claude/affectionate-heisenberg-o71cvy`。
2. 先只送 2 個請求，間隔幾秒，記下時間、狀態碼和大小：
   - `https://saominecraft.com/bluemap/maps/palier_01/settings.json`
   - `https://saominecraft.com/bluemap/maps/palier_01/tiles/1/x3/z8.png`
   兩個都沒有真的內容（settings 不是 JSON、切片開頭不是 PNG 的 `\x89PNG`），就停下來回報「本機在 HH:MM 得到：…」。
   不要改 User-Agent、不要加瀏覽器標頭、不要用其他方法繞過。
3. 有內容的話，執行：
   `python3 -I tools/bluemap_tiles.py fetch <暫存資料夾>`
   （一張一張抓，間隔 1 秒，約 2 分鐘；結果會印出抓到幾張 PNG、幾張是空的）
4. `python3 -I tools/bluemap_tiles.py build <同一個暫存資料夾> --floor 1 --out tiles/f1bm`
5. 只 commit `tiles/f1bm/`（不要 commit 暫存資料夾的原始 PNG），push 到同一個分支，回報 commit 和第 3 步印出的數字。

雲端收到後會：和探索地圖並排比對、加網站的「官方地圖」底圖選項、給預覽連結，站長說「上線」才合併。
