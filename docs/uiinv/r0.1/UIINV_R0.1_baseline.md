# UI-INV R0.1｜已審查規劃基準（v3）

- 狀態：**GPT 最終複審 PASS**（2026-11-19）。範圍是 UI 元件識別清冊和架構規劃文件；不是網站修復、不是 R0.6 Gate、不是部署驗收，也不代表核准前端實作。
- 審查基準：`Cheng-1001/ArgoStrategyGuide` commit `14f677ba4c0d1a6d6743e17ddfaa7fcc150a250d`，`src/index.html` blob `e9d4db271ea061d7c4f76aea22534db036847423`
- 盤點範圍：14 個 view、293 項邏輯清冊（308 列，扣 15 列重複）、P0／P1／P2＝52／140／101、54 項風險（高 3、中 23、低 28）、45 筆資料依賴。

## 基準檔案（9 份）

| 檔案 | SHA-256 |
|---|---|
| UIINV_R0.1_A_元件清冊_v2.md | `476234b6a1a7f6b8f2ec805c47a5b8181bd9273b4688183bb4d3ee2c34162cd9` |
| UIINV_R0.1_B_風險清單_v2.md | `4a7410e9ef914831149c9b1fb42abd29bbb8461107ca5baa9fc62e1b57a6fab4` |
| UIINV_R0.1_C_命名規則_v3.md | `4c50ddff50d1742cab6aa56cdf5982bce879b568c2d5e93021ffb861141cd95a` |
| UIINV_R0.1_D_資料依賴對照表_v2.md | `5ecbbebaf573d73c7952ece37da6f036c897be7f2804ed4ab7a3d913bd561a11` |
| UIINV_R0.1_E_審查摘要_v3.md | `90bbf7ae122d76a241117ec6606aec0b182a7a064132cb71fcc67790223fe123` |
| UIINV_R0.1_evidence_v2.js.txt | `a58bc61e2c78e6bca73c091c3f0e43c20ed870b7b7e2819d7e678584cc35b719` |
| UIINV_R0.1_evidence_v2_output.txt | `3b4c9b86632aff0a9d0885150cbd86cfceb88fed0c04c81e17a63fcc279885f5` |
| UIINV_R0.1_keyvalidate_v3.py.txt | `1cf781f2fc447b5e8dc8ffdadaab3c407b4ce9c1ca093794aef161ba8daf1be9` |
| UIINV_R0.1_keyvalidate_v3_output.txt | `501e66f28ce855fbf1a008c3ab25ef18453f6c8992fa5e3af587637a8032f2db` |

## GPT 指出的非阻擋文字問題（不重新交付，日後整理時修）

1. E v3 第 1 行標題仍寫「（v2）」，第 4 行和檔名是 v3。
2. E §0（v1→v2 歷史對照）寫「A §0 的 15 個正式 key」，正確是「15 列重複對照、17 個正式 key」；E §7.3 的數字是對的。

## 後續

- 54 項風險都還沒修；要不要建立正式 UI 識別規格、要不要實作，由站長另行決定（待決 4 項見 E v3 §5）。
- 不修改 R0.6 的範圍、版本或 Gate。
