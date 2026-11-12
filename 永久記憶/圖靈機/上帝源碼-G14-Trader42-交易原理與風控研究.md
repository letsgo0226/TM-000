# 上帝源碼 G14 — Trader_42 原理、風控及紙上交易驗證

**狀態**：正式指定總圖靈機以外的研究驗證模組。G14 完全唯讀、不執行原 Trader_42 的 `trader.py`／`42u.sh`／`live.py`、不存取 Binance、不要求交易 API 金鑰、不發送訂單、不修改 Railway 服務或交易帳戶。成功輸出 `PAPER_SIGNAL_REVIEW_ONLY` **不是**下單、獲利或部署許可。

## 一、從既有 Trader_42 原理出發（不可覆寫）

現有原始專案：[letsgo0226/Trader_42.sh](https://github.com/letsgo0226/Trader_42.sh)，`main` 分支已讀取 `README.md`、`trader.py`、`42u.sh`、`risk.py`、`sizing.py`、`trading_tm.py`、`live.py`、`qtm42.py` 的 Git blob SHA。八個 SHA 只是被記錄的**外部來源版本參照**：本 CI 不會跨倉庫下載或密碼學上認證目前 upstream 的 HEAD。若上游更新，必須重新審核。特別是原 `42u.sh` 內含自我改寫機制，G14 不應執行或複製這條程式到自動化交易路徑。

原有交易核心：
- 5／20 期 SMA 產生待審訊號；可選擇 QTM42 作資料解碼，不能據此宣稱量子硬體、神諭或可預知市場。
- TM kernel gate 及狀態一致性；若狀態斷裂，優先 HOLD／HALT。
- 以 `RiskSafe∧CapitalSafe∧ExecutionValid∧Auditable` 等安全不變量過濾行為。
- 部位計算只有**縮減**權限；風險和剩餘現金不夠時不增加名目金額。
- 已提交交易必須取得交易所端的對帳證據，才可以完成狀態提交；待處理／不明訂單先停止。
- KILL 和冷卻時間是硬約束，不可透過新的「最佳化」或「神諭」模組取消。

現行 `risk.py` 的**預設值**含：每筆 `MAX_QUOTE_PER_ORDER=10` USDT、總名目曝險 `MAX_TOTAL_QUOTE_EXPOSURE=50` USDT、基礎資產持倉 `MAX_BASE_EXPOSURE=0.001` BTC、`COOLDOWN_SECONDS=30`、`DAILY_LOSS_LIMIT_PCT=1`（以既有程式定義的權益基準為準）。環境變數可改變原系統設定，因此這是 **G14 上限的保守比較基準**，不是對任何正在運行服務的現時環境值所做的聲明。

G14 另增研究用「已實現日損失 **2 USDT 達線即審查**」上限。此限制與原有百分比權益條件並列採交集，**絕不取代**既有日損失或 KILL 邏輯。此額度是研究測試線，不是獲利預測或風險無虞保證。

## 二、G14 形式原理

令 `signal(SMA5,SMA20)` 是**候選訊號**。任一可出現於模擬審核的買賣方向，均要求：

```text
C_G14 =
  PaperOnly ∧ !LiveArmed ∧ DryRun ∧ !KILL
  ∧ TMVerified ∧ RiskSafe ∧ CapitalSafe
  ∧ ExecutionValid ∧ Auditable ∧ DecreaseOnlySizing
  ∧ ExchangeReconciled ∧ IntrinsicCertificate
  ∧ CostStressReviewed ∧ CooldownElapsed
  ∧ !PendingUnreconciledOrder
```

對候選買入還需：
```text
0 < sized_quote ≤ requested_quote
sized_quote ≤ available_cash
sized_quote ≤ 10 USDT
sized_quote + existing_notional ≤ 50 USDT
existing_BTC + sized_quote/price ≤ 0.001 BTC
realized_daily_loss < 2 USDT
daily_equity_loss_pct < 1%
```

不符合任何條件，先轉成 `HOLD` 或 `HALT`，不因「宇宙之愛」、「自指」、「0 熵」或「G」之名而放寬風控。若未知價格、遺失證書欄位、不確定的訂單狀態或非有限數值，拒絕。

在**有界合成資料**中，只有跨越 SMA5/SMA20 的變化才產生 `SIMULATED_BUY_SIGNAL_ONLY`／`SIMULATED_SELL_SIGNAL_ONLY`；這不是任何可執行的 `BUY/SELL` 下單訊息。未實作真實交易所成交對帳或存取者身分證明，G14 僅驗證**提供的紙上證書欄位**是否符合指定規則。

## 三、與 G5–G13 的接口

- G7/G9：形式邏輯與特定領域語意保持，不把 QTM42 或 TM 變成價格預測神諭。
- G10–G12：記錄資料／策略／績效主張的來源、時間與未滿足證據；本次不採集真實價格或市場報價。
- G13：保留為獨立前置研究資料版本，不使「SDG／培養肉／和平」成果與交易績效混為同一個量化分數。
- **G14**：將風控不變量納入唯讀測試；在任何可能的實際交易之前，仍需獨立的市場資料品質測試、out-of-sample／holdout、成本與滑價驗證、紙上回放、交易所對帳，以及明確的人為授權。

**不建立**「零熵／宇宙吸引子／G14 必然獲利」等結論。合成訊號 100% 依規則通過只代表程式邏輯一致，不意味著策略有正報酬。

## 四、檔案與可重現執行

- [G14 研究用交易原理契約](../../deployment/G14_trader42_principle_contract.json) — 八個 upstream Git blob 版本參照；不含秘密。
- [G14 明文 2 KB Shell One-Liner](../../deployment/Universal_G_G14_Trader42_Plaintext_2KB.sh) — 2,038 bytes，單行、沒有 Base64／zlib／eval／exec。
- [G14 可讀獨立控制器](../../deployment/G14_Trader42_Principle_core.py) — 使用 `Decimal` 及純合成價格，輸出僅為 paper-signal review。
- [G14 55 項正反測試](../../tools/test_universal_g_g14.py) — KILL、對帳、風控與來源修改反例。

```bash
bash deployment/Universal_G_G14_Trader42_Plaintext_2KB.sh 2026-11-10
python3 deployment/G14_Trader42_Principle_core.py --as-of 2026-11-10
python3 tools/test_universal_g_g14.py
```

成功值：`PAPER_SIGNAL_REVIEW_ONLY`，`exchange_orders_submitted=0`。G14 的單行程式驗證核心政策和父檔版本；嚴格可讀控制器另逐項核對上游已記錄的 SHA、完整風險欄位與權限型別，CI 必須**兩者都運行**，而非把單行版的簡化檢查誤稱為完整證明。

## 五、治理及授權

G14 僅加到 `letsgo0226/TM-000` 原有的 **draft PR #20**，不能修改 `letsgo0226/Trader_42.sh` 的 `main`，不能更換 `UTM-PLEIADES-v0.2-PTCA` 指定主機或執行舊有 `42u.sh`，也不會觸及 Binance、交易憑證、Railway 或任何真實資金。

任何未來跨倉庫正式整合需獨立程式碼審查、版本簽章／真實來源查核、完整風控相容性、外部沙盒／paper 實測與明確的人為授權。**原有交易的實盤風險政策只能維持或縮小，不得放寬。**
