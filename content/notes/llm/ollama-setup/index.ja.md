---
title: Ollama 設定と使い方
description: Ollama installation、model management、local API の例。
lastmod: 2026-07-11T00:00:00+08:00
weight: 210
menu:
  notes:
    name: Ollama
    identifier: notes-llm-ollama
    parent: notes-llm
    weight: 10
---

{{< note title="Version と安全範囲" >}}

**最終確認：2026年7月11日**

これは一般的な command reference であり、特定 version に固定した完全な runbook ではありません。実行前に installed version、最新の公式ドキュメント、対象 account／host／path を確認してください。deploy、destroy、delete、prune、sync、upgrade、system setting の変更は、費用、停止、data loss につながる可能性があります。差分を事前確認し、必要に応じて backup を取得してください。

{{< /note >}}

{{< note title="Install と実行" >}}

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull gemma2:9b
ollama pull llama3.1:8b
ollama list
```

prompt testing では小さめの model から始め、workflow が安定してから大きな model に移る。

{{< /note >}}

{{< note title="Model commands" >}}

```bash
ollama run gemma2:9b
ollama show gemma2:9b
ollama rm gemma2:9b
```

script では model name を明示する。default model の変更で結果が変わるのを避けるため。

{{< /note >}}

{{< note title="Local API" >}}

```bash
curl http://localhost:11434/api/generate \
  -d '{"model":"gemma2:9b","prompt":"Summarize this text.","stream":false}'
```

local API は private experiment に便利だが、production では timeout、retry、logging boundary が必要。

{{< /note >}}
