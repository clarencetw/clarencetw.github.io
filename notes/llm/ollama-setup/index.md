---
title: "Ollama 指令與設定速查：模型管理、刪除模型與環境變數"
url: "https://clarence.tw/notes/llm/ollama-setup/"
language: "zh-tw"
---

# Ollama 指令與設定速查：模型管理、刪除模型與環境變數

整理 Ollama 常用指令（pull、run、list、ps、show、stop、rm、cp、create、serve）、刪除模型與釋放磁碟空間、模型存放路徑，以及 OLLAMA_HOST、OLLAMA_MODELS 等環境變數在 macOS、Linux、Windows 的設定方式與 REST API 範例。

## 版本與安全範圍

**最後檢視：2026-10-26**

這是通用指令速查，不是綁定特定版本的完整 runbook。執行前請確認工具版本、目前官方文件、帳號／主機／路徑等目標；涉及 deploy、destroy、delete、prune、sync、upgrade 或系統設定變更的指令，可能造成費用、停機或資料遺失，請先預覽差異並視需要備份。

本頁指令、旗標、環境變數與預設路徑，已對照 Ollama v0.40.11（2026-10-24 發布）時的官方文件與原始碼：[CLI Reference](https://docs.ollama.com/cli)、[FAQ](https://docs.ollama.com/faq)、[Context length](https://docs.ollama.com/context-length) 與 [API](https://docs.ollama.com/api/introduction)。不同版本的預設值可能不同，請以 `ollama -v` 與 `ollama serve --help` 的實際輸出為準。

<!-- Ollama 安裝 -->
## Ollama 安裝

```bash
# Linux 安裝；再次執行同一個 script 即可升級
curl -fsSL https://ollama.com/install.sh | sh

# 查看版本
ollama -v

# 手動啟動 server（預設監聽 127.0.0.1:11434）
ollama serve
```

- macOS 與 Windows 從 [ollama.com/download](https://ollama.com/download) 安裝 app，會自動下載更新，從選單列／工作列點「Restart to update」套用。
- Linux 用安裝 script 安裝時會建立 `ollama` systemd service，通常不需要再手動執行 `ollama serve`。

<!-- 常用指令速查 -->
## Ollama 常用指令速查

| 指令 | 用途 |
| :-- | :-- |
| `ollama pull MODEL` | 下載或更新模型 |
| `ollama run MODEL [PROMPT]` | 執行模型；沒有本機模型時會先下載 |
| `ollama list`／`ollama ls` | 列出已下載的模型 |
| `ollama ps` | 列出目前載入記憶體的模型 |
| `ollama show MODEL` | 查看模型資訊 |
| `ollama stop MODEL` | 立即從記憶體卸載模型 |
| `ollama cp SOURCE DESTINATION` | 以新名稱複製模型 |
| `ollama rm MODEL [MODEL...]` | **刪除模型（無法復原）** |
| `ollama create NAME -f Modelfile` | 從 Modelfile 建立自訂模型 |
| `ollama serve` | 啟動 Ollama server |

```bash
# 下載模型
ollama pull llama3.2

# 互動式對話；輸入 /bye 離開
ollama run llama3.2

# 單次提問，適合寫進 script
ollama run llama3.2 "用三句話說明什麼是 RAG"

# 顯示回應耗時、速度等統計
ollama run llama3.2 --verbose

# 指定模型在記憶體停留多久
ollama run llama3.2 --keepalive 30m

# 列出已下載模型（ls 是 list 的別名）
ollama list
ollama ls

# 查看已載入的模型、佔用大小與 GPU/CPU 分配
ollama ps

# 立即卸載模型，釋放 RAM / VRAM（不會刪除檔案）
ollama stop llama3.2
```

`ollama ps` 的 `PROCESSOR` 欄位：`100% GPU` 代表完全載入 GPU；`100% CPU` 代表完全在系統記憶體；`48%/52% CPU/GPU` 代表部分在 GPU、部分在系統記憶體。

**查看模型資訊：**
```bash
ollama show llama3.2
ollama show llama3.2 --modelfile   # 顯示 Modelfile
ollama show llama3.2 --parameters  # 顯示參數
ollama show llama3.2 --template    # 顯示 template
ollama show llama3.2 --system      # 顯示 system message
ollama show llama3.2 --license     # 顯示授權
```

script 裡請寫明完整模型名稱與 tag，避免預設模型或 `latest` 變動後結果悄悄改變。

<!-- 刪除模型 -->
## 刪除模型與釋放磁碟空間

> ⚠️ **破壞性操作：** `ollama rm` 會直接刪除本機模型，沒有確認提示也無法復原；之後要用必須重新 `ollama pull` 下載。

```bash
# 先確認模型名稱與大小
ollama list

# 刪除單一模型
ollama rm llama3.2

# 一次刪除多個模型
ollama rm llama3.2 mymodel
```

**模型存放位置（預設）：**

| 平台 | 路徑 |
| :-- | :-- |
| macOS | `~/.ollama/models` |
| Linux（官方安裝 script） | `/usr/share/ollama/.ollama/models` |
| Windows | `C:\Users\%username%\.ollama\models` |

若設定了 `OLLAMA_MODELS`，模型會放在該目錄。

```bash
# 查看模型目錄佔用的空間（macOS）
du -sh ~/.ollama/models

# Linux（官方安裝 script）
sudo du -sh /usr/share/ollama/.ollama/models
```

- 請優先用 `ollama rm` 刪除模型，不要手動刪除 `blobs`／`manifests` 底下的個別檔案，以免模型資料不一致。
- Ollama server 啟動時預設會清除未被使用的 model blob；設定 `OLLAMA_NOPRUNE=1` 會停用這個行為。
- ⚠️ 直接 `rm -rf` 整個模型目錄（例如 macOS 的 `~/.ollama`，或 Linux 的 `/usr/share/ollama`）會一次清掉所有模型；官方文件只把它列在解除安裝步驟中，執行前請確認路徑。
- 只是想釋放記憶體而不是磁碟空間時，用 `ollama stop MODEL` 即可。

<!-- Modelfile -->
## 用 Modelfile 建立自訂模型

```text
# Modelfile
FROM llama3.2
PARAMETER temperature 0.7
PARAMETER num_ctx 8192
SYSTEM 你是一位使用繁體中文回答的技術助理。
```

```bash
# 建立模型（-f 預設讀取目前目錄的 Modelfile）
ollama create my-assistant -f ./Modelfile

# 執行自訂模型
ollama run my-assistant

# 複製一份模型再修改，保留原版
ollama cp my-assistant my-assistant-v2
```

<!-- 環境變數 -->
## Ollama 設定：常用環境變數

Ollama server 透過環境變數設定，完整清單可用 `ollama serve --help` 查看。

| 環境變數 | 用途 | 預設值 |
| :-- | :-- | :-- |
| `OLLAMA_HOST` | server 監聽位址與 port | `127.0.0.1:11434` |
| `OLLAMA_MODELS` | 模型存放目錄 | 見上方「模型存放位置」 |
| `OLLAMA_KEEP_ALIVE` | 模型閒置後留在記憶體的時間；負數為永久，`0` 為立即卸載 | `5m` |
| `OLLAMA_CONTEXT_LENGTH` | 預設 context length | 依 VRAM：<24 GiB 為 4k、24–48 GiB 為 32k、≥48 GiB 為 256k |
| `OLLAMA_NUM_PARALLEL` | 每個模型同時處理的請求數 | `1` |
| `OLLAMA_MAX_LOADED_MODELS` | 可同時載入的模型數 | GPU 數 × 3；CPU 推論為 3 |
| `OLLAMA_MAX_QUEUE` | 忙碌時可排隊的請求數，超過回傳 503 | `512` |
| `OLLAMA_ORIGINS` | 額外允許的 CORS origin，以逗號分隔 | 允許 `127.0.0.1`、`0.0.0.0` |
| `OLLAMA_FLASH_ATTENTION` | `1` 強制啟用、`0` 停用 Flash Attention | 支援時自動啟用 |
| `OLLAMA_KV_CACHE_TYPE` | K/V cache 量化：`f16`、`q8_0`、`q4_0` | `f16` |
| `OLLAMA_DEBUG` | 顯示除錯資訊，例如 `OLLAMA_DEBUG=1` | 關閉 |
| `OLLAMA_NOPRUNE` | 啟動時不清除未使用的 model blob | 關閉 |
| `OLLAMA_NO_CLOUD` | 停用雲端模型與 web search 等雲端功能 | 關閉 |

- 舊版 FAQ 仍寫 context length 預設 4096；實際預設值請以你安裝版本的 `ollama serve --help` 為準。
- `OLLAMA_NUM_PARALLEL` 加大時，需要的記憶體會隨「平行數 × context length」增加。
- API 請求中的 `keep_alive` 參數會覆蓋 `OLLAMA_KEEP_ALIVE`。

**臨時設定（前景執行 `ollama serve`）：**
```bash
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_CONTEXT_LENGTH=8192 ollama serve
```

<!-- macOS 設定 -->
## macOS 設定環境變數

以 macOS app 執行 Ollama 時，用 `launchctl` 設定，再重新啟動 Ollama app：

```bash
launchctl setenv OLLAMA_MODELS "/Volumes/Data/ollama/models"
launchctl setenv OLLAMA_KEEP_ALIVE "30m"
# 設定完成後，結束並重新開啟 Ollama app
```

<!-- Linux 設定 -->
## Linux 設定環境變數（systemd override）

以 systemd service 執行時，用 override 設定，不要直接改安裝產生的 unit 檔：

```bash
sudo systemctl edit ollama.service
```

在開啟的編輯器中，於 `[Service]` 底下加入：

```ini
[Service]
Environment="OLLAMA_MODELS=/data/ollama/models"
Environment="OLLAMA_KEEP_ALIVE=30m"
Environment="OLLAMA_NUM_PARALLEL=2"
```

```bash
# 自訂模型目錄時，ollama 使用者需要讀寫權限
sudo chown -R ollama:ollama /data/ollama/models

# 重新載入並重啟服務
sudo systemctl daemon-reload
sudo systemctl restart ollama

# 查看 log
journalctl -e -u ollama
```

<!-- Windows 設定 -->
## Windows 設定環境變數

Windows 上的 Ollama 會繼承使用者與系統環境變數：

1. 從工作列結束 Ollama。
2. 開啟「設定」（Windows 11）或「控制台」（Windows 10），搜尋「環境變數」。
3. 點選「編輯您帳戶的環境變數」。
4. 新增或編輯 `OLLAMA_HOST`、`OLLAMA_MODELS` 等使用者變數。
5. 按「確定／套用」儲存。
6. 從開始選單重新啟動 Ollama。

把 `OLLAMA_MODELS` 指到其他磁碟，可避免模型塞滿系統碟。若改過模型位置，解除安裝程式不會刪除該目錄中的模型。

<!-- 對外開放 -->
## 開放區網連線的注意事項

```bash
# 讓 server 監聽所有網路介面（設定方式依平台，見上方）
OLLAMA_HOST=0.0.0.0:11434
```

> ⚠️ 本機 API 預設不需要驗證。改成 `0.0.0.0` 後，同網段的任何人都能呼叫模型、下載或刪除模型；請搭配防火牆、reverse proxy 或 VPN 限制來源，不要直接暴露到公網。

允許瀏覽器擴充功能呼叫 API 時，需要明確設定 origin：

```bash
OLLAMA_ORIGINS=chrome-extension://*,moz-extension://*,safari-web-extension://* ollama serve
```

<!-- API 使用 -->
## REST API 範例

本機 API base URL 為 `http://localhost:11434/api`，另有 OpenAI 相容的 `http://localhost:11434/v1`。

```bash
# 確認 server 版本
curl http://localhost:11434/api/version

# 列出已下載模型（等同 ollama list）
curl http://localhost:11434/api/tags

# 列出已載入模型（等同 ollama ps）
curl http://localhost:11434/api/ps

# 單次生成
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "請用一句話說明 Ollama。",
  "stream": false
}'

# 對話，並指定 context length
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "為什麼天空是藍色的？"}],
  "stream": false,
  "options": {"num_ctx": 8192}
}'

# 預先載入並常駐記憶體
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "keep_alive": -1}'

# 立即卸載模型
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "keep_alive": 0}'

# ⚠️ 刪除模型（等同 ollama rm，無法復原）
curl -X DELETE http://localhost:11434/api/delete -d '{"model": "llama3.2"}'
```

**Python 範例：**
```python
import requests

def chat_with_ollama(prompt, model="llama3.2"):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]

print(chat_with_ollama("請將以下文字摘要成三個重點：..."))
```

本機 API 適合私人實驗；正式環境仍需要設定 timeout、retry 與 logging。
