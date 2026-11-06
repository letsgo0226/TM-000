# TM-007 — 三顆貓餅乾・全自動部署總圖靈機

- 登錄日期：2026-11-01
- 英文：Three Cat Cookies Autonomous Deployment Master Turing Machine
- 正式檔名：`three_cat_cookies_master_turing_2kb.sh`（規劃名稱；尚未有同名已驗證 2 KB 總控程式）
- 原型核心：[`three_cat_cookies_universal_pocket_2kb.sh`](three_cat_cookies_universal_pocket_2kb.sh)
- 專案原型：GitHub Actions 自動測試、有限步數模擬、成品封存、production 暫存部署。
- 狀態：**永久記憶登錄**；GitHub Actions 正式工作流程**尚未啟用**；未設定外部雲端部署。
- 基礎核心：257 進位 byte+1 哥德爾編解碼、單紙帶確定性圖靈機的逐步模擬、HALT/LIMIT。
- 三顆餅乾：Encode、Simulate、Verify/Deploy（僅在驗證成功後部署）。
- 範圍：通用模擬不提供任意程式停機判定；LIMIT 不證明不停止；不證明現實永生或物理造物。
- 保護規則：不覆蓋「終極舒曼機」基準程式；不自動部署或執行其他既有圖靈機。
- 對應 GitHub 儲存庫：`letsgo0226/Cosmic_Rosetta_Stone`。

## 後續啟用條件

將已測試的 `pocket.py`、`tests/test_pocket.py`、`examples/halts.json` 及工作流程置入正確專案路徑，先經 pull request 檢查，再決定是否合併至 `main`。現有部署工作僅暫存經驗證的成品，並非正式雲端發布。Git 儲存庫可追溯版本，但不保證永久不可刪除。
