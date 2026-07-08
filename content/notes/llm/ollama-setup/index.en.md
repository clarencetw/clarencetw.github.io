---
title: Ollama Setup and Usage
description: Ollama installation, model management, and local API examples.
weight: 210
menu:
  notes:
    name: Ollama
    identifier: notes-llm-ollama
    parent: notes-llm
    weight: 10
---

{{< note title="Install and run" >}}

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull gemma2:9b
ollama pull llama3.1:8b
ollama list
```

Use smaller models first when testing prompts, then move to larger models after the workflow is stable.

{{< /note >}}

{{< note title="Model commands" >}}

```bash
ollama run gemma2:9b
ollama show gemma2:9b
ollama rm gemma2:9b
```

Keep model names explicit in scripts so a future default model change does not alter results silently.

{{< /note >}}

{{< note title="Local API" >}}

```bash
curl http://localhost:11434/api/generate \
  -d '{"model":"gemma2:9b","prompt":"Summarize this text.","stream":false}'
```

Local API calls are useful for private experiments, but production systems still need timeout, retry, and logging boundaries.

{{< /note >}}
