---
title: "Speech AI 與 GPU Runtime：Kaldi、Whisper 的部署與維運筆記"
url: "https://clarence.tw/posts/speech-ai-gpu-runtime/"
language: "zh-tw"
---

# Speech AI 與 GPU Runtime：Kaldi、Whisper 的部署與維運筆記

整理我看待 Speech AI 與 GPU runtime 的方式，包含 Kaldi 與 Whisper 的特性與取捨、NVIDIA driver / CUDA / container 的分層，以及部署與效能維運時會檢查的項目。

自 2022 年起，我在工作中負責把 Kaldi、Whisper 這類 speech recognition 技術與 GPU runtime 接進實際的系統，範圍包含 model inference、system deployment 與後續的 performance maintenance。

這篇不是某個專案的完整案例，不會寫內部架構、資料內容或效能數據。我想整理的是自己面對這類工作的方式：怎麼看待 Kaldi 與 Whisper 的差異、為什麼我會先把 GPU runtime 弄穩，以及部署之後會固定檢查哪些東西。文中的技術說明以官方文件為準，踩坑經驗則來自我過去公開在 [blog.clarence.tw](https://blog.clarence.tw/) 的文章。

## Speech AI 在產品中的位置

我在 [我的技術工作方式](/posts/technical-delivery-chain/) 提過，LLM 與 Speech AI 不只是呼叫一個 model API，而是要和 batch processing、local model、GPU runtime 與既有 backend workflow 串在一起。

語音辨識在產品裡通常只是其中一段。一般來說，前面會有音訊取得、格式轉換與切段，後面會有文字後處理、儲存、搜尋，或交給其他服務繼續使用。所以我評估一個 Speech AI 元件時，除了辨識結果本身，也會一起看：

- 輸入音訊的格式與品質是否一致，前處理放在哪一層。
- 辨識是即時串流還是批次處理，失敗時怎麼 retry。
- 模型輸出要怎麼驗證，哪些情況需要人工確認。
- 這個 runtime 能不能在另一台機器上被重複建出來。

這種「同一個工具在不同內容上表現差很多」的感覺，我很早就有。2019 年 Amazon Transcribe 剛支援簡體中文時，我[試用並寫了心得](https://blog.clarence.tw/2019/08/25/amazon-transcribe-supports-simplified-chinese-using-teaching-and-experience/)，當時拿歌曲測試的效果不太好，換成以對話為主的影片就好很多。不論是 managed service 還是自己部署的模型，都要用接近實際情境的音訊來判斷。

## Kaldi 與 Whisper 的特性與取捨

Kaldi 與 Whisper 在我的工作中都會用到。我不把它們看成誰取代誰，而是兩種設計思路很不一樣的工具。

### Kaldi

依照 [Kaldi 官方說明](https://kaldi-asr.org/doc/about.html)，Kaldi 是以 C++ 撰寫、採 Apache License v2.0 的 speech recognition toolkit，定位是給 speech recognition 研究者使用。它的特色包括：

- 以 finite state transducer（FST）為核心，使用 OpenFst。傳統的 decoding graph 是 [HCLG](https://kaldi-asr.org/doc/graph.html)，由 HMM、context dependency、lexicon 與 grammar / language model 組合而成。
- 提供各種資料集的 recipes，從資料準備、訓練到解碼都有完整流程可以參考。
- 提供 [online decoding](https://kaldi-asr.org/doc/online_decoding.html) 的函式庫，也在 `src/cudadecoder` 提供 batched CUDA decoding 的實作。

對維運來說，Kaldi 的好處是元件拆得很細，lexicon、language model 與 acoustic model 各自可以調整；代價是建置流程長、需要的語音專業知識多，環境也比較容易因為編譯參數或相依套件不同而出問題。

### Whisper

依照 [openai/whisper](https://github.com/openai/whisper) 的說明，Whisper 是一個 Transformer sequence-to-sequence 的通用語音辨識模型，以大量且多樣的音訊訓練，可以做多語言轉寫、翻譯成英文與語言辨識，程式碼與模型權重採 MIT License。

部署時比較需要注意的幾點：

- 模型有 tiny、base、small、medium、large 與 turbo 等尺寸。官方列出的 VRAM 需求大約從 1 GB 到 10 GB，速度也差很多，選模型時要和 GPU 資源一起考慮。
- 需要 `ffmpeg`；`transcribe()` 會以 30 秒的 sliding window 處理整段音訊。
- turbo 是 large-v3 的最佳化版本，速度快但沒有針對翻譯任務訓練，需要翻譯時要改用多語言模型。
- 官方 [model card](https://github.com/openai/whisper/blob/main/model-card.md) 提醒，模型可能產生音訊裡沒有說的內容（hallucination）、可能重複輸出，在不同語言、口音與方言上的表現也不一致，並且不建議用在高風險的決策情境。

### 怎麼選

| 面向 | Kaldi | Whisper |
| :-- | :-- | :-- |
| 設計方式 | 多個元件組成的 pipeline（acoustic model、lexicon、language model、FST decoding） | 端到端的 Transformer 模型 |
| 上手成本 | 高，需要理解 recipe 與建置流程 | 低，安裝套件後就能轉寫 |
| 可調整性 | 可以分別調整詞彙、language model 等元件 | 主要透過模型尺寸、解碼參數與前後處理調整 |
| 多語言 | 依訓練資料與 recipe 而定 | 內建多語言轉寫、翻譯成英文與語言辨識 |
| 需要特別注意 | 編譯環境、相依套件、模型與 graph 的版本管理 | VRAM、長音訊處理、hallucination 與重複輸出 |

我的原則很簡單：先用接近實際情境的音訊比較，再看部署與維護成本，而不是只看公開 benchmark。

### 我對 Kaldi 的公開貢獻

我在 Kaldi 的公開貢獻是一個小修正：[kaldi-asr/kaldi#4657](https://github.com/kaldi-asr/kaldi/pull/4657)，於 2021 年 12 月合併。當時從 Gitpod 開啟 Kaldi 會出現找不到 `.gitpod.dockerfile` 的錯誤，原因是設定檔裡的檔名大小寫和實際的 `.gitpod.Dockerfile` 不一致。這個 PR 修正了檔名，移除 Dockerfile 裡不存在的使用者與用不到的路徑，並固定 Intel MKL 的安裝版本。

修改的範圍不大，但它也是我對這類工具一直很在意的事：開發與執行環境要能被別人重複建起來。

## GPU runtime 要先穩：driver、CUDA、container

不論用 Kaldi 還是 Whisper，只要用到 GPU，模型之下就有一整層 runtime。我會把它拆成幾層來看，出問題時也按照這個順序往下查：

1. **硬體與韌體設定**：GPU 是否被系統認到、Secure Boot 是否啟用。
2. **Kernel 與 NVIDIA kernel module**：module 是否針對目前的 kernel 建好、是否被允許載入。
3. **NVIDIA driver**：`nvidia-smi` 能不能正常回應。
4. **CUDA 與相關函式庫**：CUDA runtime、cuDNN 等版本是否和 driver、framework 相容。
5. **Container runtime**：container 裡能不能看到 GPU。
6. **應用與模型**：PyTorch、Kaldi build 與模型檔本身。

### Driver 與 CUDA 的版本關係

依照 NVIDIA 的 [CUDA Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/index.html) 文件，driver 與 CUDA toolkit 可以分開更新。從 CUDA 11 開始有 [minor version compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html)：同一個 major 版本內編譯的應用，只要 driver 達到最低版本（例如 CUDA 12.x 需要 525 以上、CUDA 11.x 需要 450 以上）就可以執行，但部分需要較新 driver 的功能會受限，把 device code 編成 PTX 再 JIT 的應用也不適用。

實務上的意思是：先決定 driver 版本，再決定上面能跑哪些 CUDA 版本，而不是每次升級 framework 都跟著動 driver。

### 用 container 隔開 CUDA 與 framework

[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) 的安裝前提是 host 上已經裝好 NVIDIA driver。以 Docker 為例，安裝套件後執行：

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

`nvidia-ctk` 會修改 host 上的 `/etc/docker/daemon.json`，所以這一步應該納入設定管理。接著用官方的 [sample workload](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/sample-workload.html) 確認 container 看得到 GPU：

```bash
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

這樣分層之後，host 主要負責 driver 與 container toolkit，CUDA、cuDNN 與 framework 則跟著 image 走。不同服務可以使用不同的 CUDA 版本，升級與 rollback 也變成切換 image，而不是在 host 上反覆安裝與移除套件。

### 我在部落格記錄過的問題

以下是我過去公開記錄的 GPU 環境問題。它們不一定發生在同一個環境，但很能說明為什麼 runtime 要分層管理：

| 現象 | 原因與處理方向 | 學到的事 |
| :-- | :-- | :-- |
| [nvidia-smi 無法和 driver 溝通](https://blog.clarence.tw/2023/07/14/%e8%a7%a3%e6%b1%ba-ubuntu-%e4%b8%ad-nvidia-gpu-%e9%a9%85%e5%8b%95%e5%95%8f%e9%a1%8c/) | Kernel 更新後 driver module 沒有重建，用 DKMS 為新 kernel 重新建立 | Kernel 更新也是 GPU 環境的變更 |
| [Secure Boot 下 driver 無法載入](https://blog.clarence.tw/2026/01/31/%e8%a7%a3%e6%b1%ba-ubuntu-24-04-secure-boot-%e7%92%b0%e5%a2%83%e4%b8%8b-nvidia-%e9%a9%85%e5%8b%95%e7%84%a1%e6%b3%95%e8%bc%89%e5%85%a5%e5%95%8f%e9%a1%8c/) | DKMS 在本機編譯的 module 沒有簽章而被拒絕，改用 Ubuntu 預先簽署的 `linux-modules-nvidia-*` 套件 | 不必為了 driver 關掉 Secure Boot |
| [nvidia-smi 顯示 No devices were found](https://blog.clarence.tw/2024/02/19/%e8%a7%a3%e6%b1%ba-nvidia-linux-%e4%bd%bf%e7%94%a8-nvidia-smi-%e5%87%ba%e7%8f%be-no-devices-were-found-%e5%95%8f%e9%a1%8c/) | 套件安裝的 driver 無法初始化 GPU，改用 NVIDIA 官方 installer 重裝，並處理 kernel 與 GCC 版本不一致 | 安裝失敗時先看 kernel log 與 installer log |
| [CUDA 套件相依無法安裝](https://blog.clarence.tw/2022/05/31/%e5%ae%89%e8%a3%9d-cuda-%e5%87%ba%e7%8f%be-depends-cuda-11-7-11-7-0-but-it-is-not-going-to-be-installed-%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/) | 圖形介面占用 driver，需要切到 `multi-user.target` 再移除與重裝 | 更新 driver 要排停機時間 |
| [dpkg 覆寫檔案錯誤](https://blog.clarence.tw/2023/07/14/%e5%9c%a8-ubuntu-%e7%99%bc%e7%94%9f-dpkg-error-processing-archive-%e7%9a%84%e5%95%8f%e9%a1%8c%e8%a9%b2%e5%a6%82%e4%bd%95%e8%99%95%e7%90%86%ef%bc%9f/) | 不同版本的 NVIDIA 套件互相覆寫同一個檔案 | 同一台機器的 driver 套件來源要一致 |
| [DGX 出現 NO_PUBKEY](https://blog.clarence.tw/2023/03/04/dgx-%e7%b3%bb%e7%b5%b1-ubuntu-18-04-%e5%87%ba%e7%8f%be-no_pubkey-a4b469963bf863cc-%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/) | NVIDIA CUDA repository 更換簽章金鑰，更新 key 後恢復 | 外部 repository 也會改變，更新失敗要先看訊息 |
| [cuDNN 驗證範例編譯失敗](https://blog.clarence.tw/2022/06/01/%e5%ae%89%e8%a3%9d-cuda-deep-neural-network-cudnn-%e9%81%87%e5%88%b0-test-c110-fatal-error-freeimage-h-no-such-file-or-directory-%e8%a7%a3%e6%b1%ba%e6%96%b9%e6%b3%95/) | 範例程式需要額外的 FreeImage 函式庫 | 驗證步驟本身也有相依套件 |

另外，[CUDA Toolkit 11.7 的安裝方式](https://blog.clarence.tw/2022/05/31/%e5%ae%89%e8%a3%9d-cuda-toolkit-11-7/)（deb local、deb network、runfile）與 [darknet 指定 GPU 編號](https://blog.clarence.tw/2021/10/24/yolo-alexeyab-darknet-set-gpu-number/)（`CUDA_VISIBLE_DEVICES` 與 framework 自己的設定）這兩篇，也是我在規劃 GPU 環境時常回頭看的基本功。

## 部署與效能維運的檢查清單

以下是一般性的檢查項目，實際內容會依環境調整。

### 部署前

- 記錄完整的版本組合：OS、kernel、NVIDIA driver、CUDA、cuDNN、framework、模型版本與 image tag。
- 確認 Secure Boot 狀態（`mokutil --sb-state`），決定 kernel module 要用預先簽署的套件還是自行簽署。
- 決定 kernel 與 driver 的更新策略，避免自動更新在沒人注意時改變 GPU 環境。
- 依模型尺寸與預期的併發量估算 VRAM，決定每張 GPU 跑幾個 process，以及用 `CUDA_VISIBLE_DEVICES` 怎麼分配。

### 部署後驗證

- Host：`lsmod | grep nvidia` 確認 module 已載入，`nvidia-smi` 正常回應。
- Container：用 sample workload 確認 container 內看得到 GPU。
- 應用：用一小段固定的測試音訊跑完整流程，確認輸出格式與內容合理。
- 重開機後再驗證一次，確認 driver 與服務都會自動恢復。

### 日常觀察

- 用 `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv` 這類指令，或接進 monitoring，持續觀察 GPU 使用率與記憶體。
- 觀察處理時間與佇列長度，區分是 GPU 不夠、前處理太慢，還是 I/O 卡住。
- 留意辨識結果的異常，例如大量重複文字或明顯不屬於音訊的內容。

### 有風險的操作

- `apt purge nvidia*`、切換 `multi-user.target`、移除或替換 kernel module 都會讓 GPU 服務中斷，應該排在維護時段，並先確認有回復方式。
- `nvidia-ctk runtime configure` 會改寫 Docker daemon 設定，要和既有設定一起 review。
- 不要為了省事直接關閉 Secure Boot；如果真的需要，要先評估安全影響。

## 學到的事

- **模型只是其中一層。** Speech AI 能不能長期穩定運作，很大一部分取決於 driver、kernel、CUDA 與 container 這些底層有沒有被管好。
- **Driver 留在 host，其他交給 image。** 把 CUDA 與 framework 放進 container，升級與 rollback 都會單純很多。
- **用自己的情境驗證。** Kaldi 與 Whisper 各有取捨，公開 benchmark 只能參考，最後還是要用接近實際情境的音訊來比較。
- **把踩過的坑寫下來。** 我在部落格記錄的每個 GPU 問題，後來都變成部署前後的檢查項目。
