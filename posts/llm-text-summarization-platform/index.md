---
title: "LLM 文字摘要流程的設計與取捨：OpenAI API、Ollama 與 Local Model"
url: "https://clarence.tw/posts/llm-text-summarization-platform/"
language: "zh-tw"
---

# LLM 文字摘要流程的設計與取捨：OpenAI API、Ollama 與 Local Model

整理我設計與維運 LLM 文字摘要流程時的原則與取捨，包含前處理與切段、cloud API 與 local model 的選擇、batch processing、retry、成本控制與輸出驗證。

自 2022 年起，我開始把 LLM 放進實際產品流程，其中一塊是內部的文字摘要與 AI application 平台：整合 OpenAI API、Ollama、local model 與 batch processing，重點放在可控、可維運的 model usage。

這類內部系統的細節不適合公開，所以這篇不是完整的 case study，而是整理我設計與維運摘要流程時採用的原則與取捨。文中提到的 API 行為都以官方文件為準，寫作時（2026-10）已對照過；實際使用前仍請以最新文件為準。

## 為什麼摘要不只是呼叫 API

做出一個摘要 demo 很快：把文字丟進 prompt，請模型「幫我摘要」，幾分鐘就能看到結果。真正的工作在 demo 之後：

- 輸入長度不固定，有些文字會超過模型的 context length。
- 同一批資料要處理很多筆，會碰到 rate limit、timeout 與部分失敗。
- 下游系統需要固定格式，但模型輸出不一定每次都長得一樣。
- 成本、延遲與資料敏感度，會影響每一筆該送到哪個模型。
- 換模型或改 prompt 之後，需要知道品質是變好還是變差。

所以我會把摘要當成一條資料處理 pipeline 來設計，而不是一個 API call。

## 流程拆解

我習慣把流程拆成幾個可以各自觀察、各自重跑的階段：

1. **前處理**：清掉格式雜訊、重複內容與不需要送進模型的欄位，並在這一步處理不該離開環境的資料。送進模型的內容越乾淨，token 用量與輸出品質都越好控制。
2. **切段**：先估算 token 數，超過模型可處理的長度就依段落或語意邊界切段，必要時保留少量重疊，避免重點剛好被切斷。
3. **模型呼叫**：短文字直接摘要；長文字用 map-reduce 的方式，先對每一段產生摘要，再把段落摘要合併成最終摘要。這樣每次呼叫的輸入都在可控範圍內，失敗時也只需要重跑單一段落。
4. **驗證**：檢查輸出格式、必要欄位、長度與明顯的錯誤，不通過就標記為失敗或進入重試。
5. **輸出**：把結果連同使用的模型、prompt 版本與處理狀態一起保存，之後才能追查與比較。

使用 local model 時，context length 要特別留意。Ollama 的預設 context length 會依 VRAM 大小決定，可以用 `OLLAMA_CONTEXT_LENGTH` 調整，並透過 `ollama ps` 的 CONTEXT 欄位確認實際配置（[Context length 官方文件](https://docs.ollama.com/context-length)）。如果沒有確認這個設定，長文字可能沒有被模型完整看到。Ollama 的安裝、指令與環境變數，我整理在 [Ollama 指令與設定速查](https://clarence.tw/notes/llm/ollama-setup/)。

### 用 structured output 讓下游可以接

摘要如果要被其他系統使用，我會要求模型輸出 JSON，並用 schema 約束欄位：

- OpenAI 的 [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) 在 `strict` 模式下可以讓輸出符合指定的 JSON Schema；JSON mode 只保證是合法 JSON，不保證符合 schema。仍要處理模型拒答（refusal）與輸出達到 token 上限而不完整的情況。
- Ollama 透過 `format` 參數支援 JSON schema，OpenAI 相容 API 則使用 `response_format`。官方建議同時把 schema 寫進 prompt，並把 temperature 設為 0 以取得較穩定的結果（[Structured outputs 官方文件](https://docs.ollama.com/capabilities/structured-outputs)）。

要注意的是，schema 只能保證「形狀」正確，不能保證內容正確。格式通過驗證，不代表摘要沒有漏掉重點或加入原文沒有的內容。

## Cloud API 與 Local Model 怎麼選

我在 [Gemma 4 12B 的文章](https://blog.clarence.tw/2026/06/04/google-%e7%99%bc%e5%b8%83-gemma-4-12b%ef%bc%9alocal-ai-%e7%9a%84%e9%87%8d%e9%bb%9e%e4%b8%8d%e6%98%af%e5%8f%96%e4%bb%a3%e9%9b%b2%e7%ab%af%e6%a8%a1%e5%9e%8b%ef%bc%8c%e8%80%8c%e6%98%af%e8%a3%9c%e4%b8%8a/)寫過，local model 的重點不是取代雲端模型，而是補上可部署的中間選項。這也是我在摘要流程裡選模型的基本想法：

- **Cloud API** 適合需要較強理解能力、較長上下文或較複雜指令的任務，也不必自己維護 GPU 與 runtime。
- **Local model** 解決的是另一組問題：能不能在私有環境跑、資料能不能留在自己的環境、推論成本與延遲能不能控制。

實際上我不會只用一種。比較好的做法是讓兩者都能接上同一套流程：Ollama 提供 OpenAI 相容的 API（本機預設為 `http://localhost:11434/v1/`），同一套 client 程式碼換 base URL 與模型名稱就能切換（[OpenAI compatibility 官方文件](https://docs.ollama.com/api/openai-compatibility)）。不過相容不代表完全相同，例如 context length 無法透過 OpenAI 相容 API 設定，切換前仍要個別測試。

選擇時我會看幾件事：資料敏感度、需要的品質、可接受的延遲、整體成本，以及這個模型量化後在實際硬體上的表現。benchmark 只能參考，最後還是要用自己的資料測。

## Batch、Retry 與成本控制

### Batch processing

不需要即時結果的工作，我會用批次處理。OpenAI 的 [Batch API](https://developers.openai.com/api/docs/guides/batch) 以 JSONL 檔案送出請求，在 24 小時內完成，費用比同步呼叫少 50%，而且有獨立的 rate limit。要注意輸出順序不一定和輸入相同，必須用每筆請求的 `custom_id` 對回結果；失敗與過期的請求會放在另外的 error file，需要另外處理。

Local model 沒有這種託管的批次服務，批次的節奏要自己控制：限制同時處理的數量，避免把 GPU 記憶體或服務塞滿。

### Retry

重試要有規則，不能無限重送。OpenAI 的 [rate limit 文件](https://developers.openai.com/api/docs/guides/rate-limits) 建議：

- 有 `Retry-After` 就依照它等待；沒有就用 exponential backoff 加上 jitter。
- 限制重試次數與總等待時間。
- 失敗的請求也會計入每分鐘限制，連續重送反而更難恢復。
- 官方 SDK 本身會自動重試部分錯誤，自己實作重試時要避免重複計算。
- 額度或帳單相關的錯誤不應該重試。

我會再加上一個原則：重試要以「段落」或「單筆」為單位，而且要能辨識已經成功的部分，避免整批重跑。

### 成本控制

成本大多在流程設計時就決定了：

- 前處理先刪掉不需要的內容，減少輸入 token。
- `max_tokens` 設在接近預期輸出的長度。OpenAI 計算 rate limit 時，會取 `max_tokens` 與估算的請求 token 數中較大的一個，設太大會白白占用額度。
- 不急的工作走 Batch API 或 local model。
- 記錄每次呼叫的模型與 token 用量，才看得出成本落在哪裡。

## 輸出品質怎麼驗證

摘要品質很難只靠自動化判斷，我會分成兩層：

- **自動檢查**：schema 是否通過、必要欄位是否存在、長度是否合理、是否有拒答或被截斷的輸出。這些是硬性條件，不通過就不往下送。
- **人工抽查**：定期抽樣比對原文與摘要，看有沒有漏掉重點、扭曲原意，或加入原文沒有的內容。換模型或改 prompt 前後，用同一批樣本比較，才知道改動是否真的有幫助。

OpenAI 的文件也提醒，structured output 只保證格式，應該另外建立 evaluation 來確認內容是否符合需求。抽查的樣本與結果最好保留下來，之後換模型時可以直接重用。

## 學到的事

- **先把流程設計好，再挑模型。** 前處理、切段、驗證與重試做好之後，換模型的成本會低很多。
- **Cloud 與 local 不是二選一。** 讓兩者都能接上同一套流程，再依資料、品質與成本決定每一類工作走哪一邊。
- **格式正確不等於內容正確。** schema 驗證擋得住格式錯誤，擋不住摘要漏掉重點，人工抽查不能省。
- **能追查比一次做對更重要。** 保存模型、prompt 版本、token 用量與處理狀態，出問題時才知道要從哪裡查起。
