---
title: Ollama 設定與使用
weight: 210
menu:
  notes:
    name: Ollama Setup
    identifier: notes-llm-ollama
    parent: notes-llm
    weight: 10
---

<!-- Ollama 安裝 -->
{{< note title="Ollama 安裝" >}}

```bash
# Linux/macOS 安裝
curl -fsSL https://ollama.ai/install.sh | sh

# 啟動服務
ollama serve

# 下載模型
ollama pull gemma2:9b
ollama pull gemma2:27b
ollama pull llama2
ollama pull mistral
```

{{< /note >}}

<!-- 常用模型指令 -->
{{< note title="常用模型指令" >}}

```bash
# 列出已安裝模型
ollama list

# 執行對話 (使用 Gemma2)
ollama run gemma2:9b

# 刪除模型
ollama rm gemma2:9b

# 查看模型資訊
ollama show gemma2:9b
```

{{< /note >}}

<!-- API 使用 -->
{{< note title="API 使用範例" >}}

```python
import requests
import json

def chat_with_ollama(prompt, model="gemma2:9b"):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(url, json=data)
    return response.json()["response"]

# 使用範例 - 文本摘要
def summarize_text(text):
    prompt = f"""請將以下文字進行摘要，保留重點資訊：

{text}

摘要："""
    return chat_with_ollama(prompt, "gemma2:9b")

# RTX 4090 最佳化設定
def chat_with_gemma2_optimized(prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "gemma2:9b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_ctx": 4096  # RTX 4090 24GB 可支援更大 context
        }
    }
    
    response = requests.post(url, json=data)
    return response.json()["response"]

# 使用範例
result = summarize_text("這是一段很長的文字需要摘要...")
print(result)
```

{{< /note >}}