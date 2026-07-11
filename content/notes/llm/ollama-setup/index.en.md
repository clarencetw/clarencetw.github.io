---
title: Ollama Setup and Usage
description: Ollama installation, model management, and local API examples.
lastmod: 2026-07-11T00:00:00+08:00
weight: 210
menu:
  notes:
    name: Ollama
    identifier: notes-llm-ollama
    parent: notes-llm
    weight: 10
---

{{< note title="Version and safety scope" >}}

**Last reviewed: July 11, 2026**

This is a general command reference, not a version-pinned runbook. Check the installed version, current official documentation, and the target account, host, and path before use. Commands that deploy, destroy, delete, prune, sync, upgrade, or change system settings can cause cost, downtime, or data loss; preview changes and back up where appropriate.

{{< /note >}}

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
