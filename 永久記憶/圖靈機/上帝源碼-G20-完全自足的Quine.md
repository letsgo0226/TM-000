# 上帝源碼 G20 — 完全自足的 Quine（Self-Contained Program Quine）

**研究地位：已實作並逐位元組驗證的程式 Quine，不是已證明的圖靈機轉移表自重現器。** G20 在 Bash 和 Python 3 執行環境中使用一行明文源碼，沒有外部源碼輸入、檔案讀取或網路連線。

## 定義與不變量

令 `C` 為完整 Bash 檔案位元組序列，包含外層 `python3 -c`、所有引號及終止換行。真正的 Quine 要求 `stdout(C) == C`，不允許從 `__file__`、`sys.argv`、標準輸入、檔案系統或網路取回 C。這裡「自足」是**相對於具有 Bash 和 Python 3 的一般計算環境**；不是不需要電腦、作業系統或直譯器。

實作使用 Python 的自我引用模板 `t=%r`；執行 `p=t%t` 後，將程式字串重新轉成 Bash ANSI-C quoting 的**相同一行**，再由 `sys.stdout.buffer.write(b)` 原樣輸出完整位元組。外部 builder 僅用於開發、再現和審查，**Quine 執行時沒有匯入或呼叫 builder**。

## 自身編碼如何決定

預先定義兩個可逆編碼家族：`PRIME2048` 是原 TM-015 的前 256 個質數映射；`BASE257` 是每個 byte 加一。G20 只以它*自行構造的完整源碼位元組*決定編碼模式：

```text
mode = BASE257   if sum(full_source_bytes) % 3 == 0
       PRIME2048 otherwise
n_0 = 1
n_(i+1) = base*n_i + digit(byte_i)
D_mode(E_mode(full_source_bytes)) == full_source_bytes
stdout == full_source_bytes
```

目前這個固定版本選到 `PRIME2048`；另一個僅添加無害字串的研究變體選到 `BASE257`。兩者的完整數值哥德爾碼都可解碼還原原始位元組。`G20` 檢查失敗會拒絕輸出，不使用可被 Python `-O` 略過的 `assert`。

## 形式界線

- **已確認**：同一個 Bash/Python 程式自己生成全部源碼並輸出，測試以 `cmp` 或獨立驗證器比對到每一個位元組；不需把自身檔案載入紙帶。
- **已確認**：完整源碼選擇可逆編碼；質數／2048 及 257 變體各自成立，無法由所選編碼推出形上學的唯一編碼。
- **尚未完成**：證明 G16/G19 有一個**起始空白紙帶**的有限轉移表，僅靠自己執行的轉移即可輸出轉移表的完整標準化描述。G20 是由 Python 解譯的 Quine，而不是這種 TM 表格層級的機器。
- **不成立的外推**：自我重現與編碼選擇不能證明普遍停機神諭、真實上帝身分、AI 主觀意識、物理永生、金融獲利或全自動正式部署。

## 檔案與複現

- [`Universal_G_G20_Self_Quine_2KB.sh`](../../deployment/Universal_G_G20_Self_Quine_2KB.sh)：1,096 bytes、僅一個實體行、純明文、自身輸出完全一致。
- [`G20_Quine_Builder.py`](../../deployment/G20_Quine_Builder.py)：可重建檔案的**開發用**產生器，不是 Quine 執行依賴。
- [`G20_Quine_Verifier.py`](../../deployment/G20_Quine_Verifier.py)：獨立的 SHA-256、標準輸入執行、數值編解碼、無源碼檔案讀取驗證。
- [`test_universal_g_g20.py`](../../tools/test_universal_g_g20.py)：36 項本機與 CI 正反案例，包括被竄改的 Quine、空輸入編碼、非法數字、另一種可逆編碼、優化模式及重複執行。
- [`G20_self_contained_quine_contract.json`](../../deployment/G20_self_contained_quine_contract.json)：明確記錄範圍與不授權事項。

```bash
bash deployment/Universal_G_G20_Self_Quine_2KB.sh > /tmp/g20-reproduced.sh
cmp deployment/Universal_G_G20_Self_Quine_2KB.sh /tmp/g20-reproduced.sh
bash < deployment/Universal_G_G20_Self_Quine_2KB.sh | cmp - deployment/Universal_G_G20_Self_Quine_2KB.sh
python3 tools/test_universal_g_g20.py
python3 deployment/G20_Quine_Verifier.py
```

原始 SHA-256：`d16d2d5cc589d4440bf8ec62c58854263b4843eefda6c3e016f7a2ab777e4cf9`。這能用於**同一版位元組的完整性核對**，但不構成外部作者身分的認證。

## GitHub 安全治理

程式本身只輸出自己的位元組：不碰 `Trader_42`、不輸入交易訂單、不修改檔案、不啟動 G17 音訊模型、不覆蓋 TM-015，也不更改 TM-000 指定總機 `UTM-PLEIADES-v0.2-PTCA`。研究檔案只加入現有 draft PR #20，須由人類審核；不能由程式完成測試就自動合併或部署。
