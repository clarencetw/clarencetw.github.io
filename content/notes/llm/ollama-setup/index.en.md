---
title: "Ollama Commands and Settings: Model Management, Deleting Models, and Environment Variables"
description: Ollama CLI command reference (pull, run, list, ps, show, stop, rm, cp, create, serve), how to delete models and free disk space, where models are stored, and how to set OLLAMA_HOST, OLLAMA_MODELS, and other environment variables on macOS, Linux, and Windows, with REST API examples.
lastmod: 2026-10-26T00:00:00+08:00
weight: 210
menu:
  notes:
    name: Ollama
    identifier: notes-llm-ollama
    parent: notes-llm
    weight: 10
---

{{< note title="Version and safety scope" >}}

**Last reviewed: October 26, 2026**

This is a general command reference, not a version-pinned runbook. Check the installed version, current official documentation, and the target account, host, and path before use. Commands that deploy, destroy, delete, prune, sync, upgrade, or change system settings can cause cost, downtime, or data loss; preview changes and back up where appropriate.

Commands, flags, environment variables, and default paths on this page were checked against the official documentation and source code as of Ollama v0.40.11 (released October 24, 2026): [CLI Reference](https://docs.ollama.com/cli), [FAQ](https://docs.ollama.com/faq), [Context length](https://docs.ollama.com/context-length), and [API](https://docs.ollama.com/api/introduction). Defaults can change between versions, so trust the output of `ollama -v` and `ollama serve --help` on your machine.

{{< /note >}}

<!-- Install -->
{{< note title="Install Ollama" >}}

```bash
# Install on Linux; re-run the same script to upgrade
curl -fsSL https://ollama.com/install.sh | sh

# Show the version
ollama -v

# Start the server manually (listens on 127.0.0.1:11434 by default)
ollama serve
```

- On macOS and Windows, install the app from [ollama.com/download](https://ollama.com/download). It downloads updates automatically; click "Restart to update" in the menu bar or taskbar to apply them.
- The Linux install script creates an `ollama` systemd service, so you usually do not need to run `ollama serve` yourself.

{{< /note >}}

<!-- Command reference -->
{{< note title="Ollama command reference" >}}

| Command | Purpose |
| :-- | :-- |
| `ollama pull MODEL` | Download or update a model |
| `ollama run MODEL [PROMPT]` | Run a model; pulls it first if it is not available locally |
| `ollama list` / `ollama ls` | List downloaded models |
| `ollama ps` | List models currently loaded in memory |
| `ollama show MODEL` | Show model information |
| `ollama stop MODEL` | Unload a model from memory immediately |
| `ollama cp SOURCE DESTINATION` | Copy a model under a new name |
| `ollama rm MODEL [MODEL...]` | **Delete models (irreversible)** |
| `ollama create NAME -f Modelfile` | Create a custom model from a Modelfile |
| `ollama serve` | Start the Ollama server |

```bash
# Download a model
ollama pull llama3.2

# Interactive chat; type /bye to exit
ollama run llama3.2

# One-shot prompt, handy in scripts
ollama run llama3.2 "Explain RAG in three sentences."

# Show timings and token speed
ollama run llama3.2 --verbose

# Control how long the model stays in memory
ollama run llama3.2 --keepalive 30m

# List downloaded models (ls is an alias of list)
ollama list
ollama ls

# Show loaded models, their size, and GPU/CPU split
ollama ps

# Unload a model to free RAM / VRAM (files stay on disk)
ollama stop llama3.2
```

In the `PROCESSOR` column of `ollama ps`, `100% GPU` means the model is fully on the GPU, `100% CPU` means it is fully in system memory, and `48%/52% CPU/GPU` means it is split across both.

**Inspect a model:**
```bash
ollama show llama3.2
ollama show llama3.2 --modelfile   # Modelfile
ollama show llama3.2 --parameters  # parameters
ollama show llama3.2 --template    # template
ollama show llama3.2 --system      # system message
ollama show llama3.2 --license     # license
```

Use explicit model names and tags in scripts so that a change to a default model or `latest` does not silently alter results.

{{< /note >}}

<!-- Delete models -->
{{< note title="Delete models and free disk space" >}}

> ⚠️ **Destructive:** `ollama rm` deletes local models immediately, without a confirmation prompt, and cannot be undone. You must `ollama pull` the model again to use it.

```bash
# Check model names and sizes first
ollama list

# Delete one model
ollama rm llama3.2

# Delete several models at once
ollama rm llama3.2 mymodel
```

**Default model locations:**

| Platform | Path |
| :-- | :-- |
| macOS | `~/.ollama/models` |
| Linux (official install script) | `/usr/share/ollama/.ollama/models` |
| Windows | `C:\Users\%username%\.ollama\models` |

If `OLLAMA_MODELS` is set, models are stored in that directory instead.

```bash
# Disk usage of the model directory (macOS)
du -sh ~/.ollama/models

# Linux (official install script)
sudo du -sh /usr/share/ollama/.ollama/models
```

- Prefer `ollama rm` over deleting individual files under `blobs` or `manifests`, which can leave model data inconsistent.
- By default the server prunes unused model blobs on startup; set `OLLAMA_NOPRUNE=1` to disable this.
- ⚠️ Running `rm -rf` on the whole data directory (for example `~/.ollama` on macOS or `/usr/share/ollama` on Linux) removes every model at once. The official docs only list this as an uninstall step; double-check the path first.
- If you only need to free memory rather than disk space, `ollama stop MODEL` is enough.

{{< /note >}}

<!-- Modelfile -->
{{< note title="Create a custom model with a Modelfile" >}}

```text
# Modelfile
FROM llama3.2
PARAMETER temperature 0.7
PARAMETER num_ctx 8192
SYSTEM You are a concise technical assistant.
```

```bash
# Create the model (-f defaults to Modelfile in the current directory)
ollama create my-assistant -f ./Modelfile

# Run the custom model
ollama run my-assistant

# Copy a model before changing it so the original stays intact
ollama cp my-assistant my-assistant-v2
```

{{< /note >}}

<!-- Environment variables -->
{{< note title="Ollama settings: common environment variables" >}}

The Ollama server is configured through environment variables. Run `ollama serve --help` for the full list.

| Variable | Purpose | Default |
| :-- | :-- | :-- |
| `OLLAMA_HOST` | Server bind address and port | `127.0.0.1:11434` |
| `OLLAMA_MODELS` | Model storage directory | See "Default model locations" above |
| `OLLAMA_KEEP_ALIVE` | How long an idle model stays in memory; negative keeps it loaded, `0` unloads immediately | `5m` |
| `OLLAMA_CONTEXT_LENGTH` | Default context length | Based on VRAM: 4k below 24 GiB, 32k for 24–48 GiB, 256k at 48 GiB or more |
| `OLLAMA_NUM_PARALLEL` | Parallel requests per model | `1` |
| `OLLAMA_MAX_LOADED_MODELS` | Models that can be loaded concurrently | 3 × number of GPUs, or 3 for CPU inference |
| `OLLAMA_MAX_QUEUE` | Requests queued while busy before returning 503 | `512` |
| `OLLAMA_ORIGINS` | Additional allowed CORS origins, comma-separated | `127.0.0.1` and `0.0.0.0` allowed |
| `OLLAMA_FLASH_ATTENTION` | `1` forces Flash Attention on, `0` disables it | Automatic when supported |
| `OLLAMA_KV_CACHE_TYPE` | K/V cache quantization: `f16`, `q8_0`, `q4_0` | `f16` |
| `OLLAMA_DEBUG` | Extra debug output, e.g. `OLLAMA_DEBUG=1` | Off |
| `OLLAMA_NOPRUNE` | Do not prune unused model blobs on startup | Off |
| `OLLAMA_NO_CLOUD` | Disable cloud features such as cloud models and web search | Off |

- The FAQ still states a 4096-token default context length; check `ollama serve --help` for the default in your installed version.
- Raising `OLLAMA_NUM_PARALLEL` increases memory use in proportion to parallel requests × context length.
- The `keep_alive` parameter in an API request overrides `OLLAMA_KEEP_ALIVE`.

**Temporary setting (running `ollama serve` in the foreground):**
```bash
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_CONTEXT_LENGTH=8192 ollama serve
```

{{< /note >}}

<!-- macOS -->
{{< note title="Set environment variables on macOS" >}}

When Ollama runs as the macOS app, set variables with `launchctl`, then restart the app:

```bash
launchctl setenv OLLAMA_MODELS "/Volumes/Data/ollama/models"
launchctl setenv OLLAMA_KEEP_ALIVE "30m"
# Quit and reopen the Ollama app afterwards
```

{{< /note >}}

<!-- Linux -->
{{< note title="Set environment variables on Linux (systemd override)" >}}

When Ollama runs as a systemd service, use an override instead of editing the installed unit file:

```bash
sudo systemctl edit ollama.service
```

In the editor, add lines under `[Service]`:

```ini
[Service]
Environment="OLLAMA_MODELS=/data/ollama/models"
Environment="OLLAMA_KEEP_ALIVE=30m"
Environment="OLLAMA_NUM_PARALLEL=2"
```

```bash
# A custom model directory must be readable and writable by the ollama user
sudo chown -R ollama:ollama /data/ollama/models

# Reload and restart the service
sudo systemctl daemon-reload
sudo systemctl restart ollama

# View logs
journalctl -e -u ollama
```

{{< /note >}}

<!-- Windows -->
{{< note title="Set environment variables on Windows" >}}

Ollama on Windows inherits your user and system environment variables:

1. Quit Ollama from the taskbar.
2. Open Settings (Windows 11) or Control Panel (Windows 10) and search for "environment variables".
3. Click "Edit environment variables for your account".
4. Create or edit user variables such as `OLLAMA_HOST` and `OLLAMA_MODELS`.
5. Click OK/Apply to save.
6. Start Ollama again from the Start menu.

Pointing `OLLAMA_MODELS` at another drive keeps models from filling the system drive. If you change the model location, the uninstaller does not remove models stored there.

{{< /note >}}

<!-- Network exposure -->
{{< note title="Exposing Ollama on your network" >}}

```bash
# Listen on all interfaces (set it per platform as shown above)
OLLAMA_HOST=0.0.0.0:11434
```

> ⚠️ The local API requires no authentication by default. With `0.0.0.0`, anyone on the same network can run, pull, or delete models. Restrict access with a firewall, reverse proxy, or VPN, and do not expose it directly to the internet.

To let browser extensions call the API, allow their origins explicitly:

```bash
OLLAMA_ORIGINS=chrome-extension://*,moz-extension://*,safari-web-extension://* ollama serve
```

{{< /note >}}

<!-- API -->
{{< note title="REST API examples" >}}

The local API base URL is `http://localhost:11434/api`; an OpenAI-compatible API is available at `http://localhost:11434/v1`.

```bash
# Server version
curl http://localhost:11434/api/version

# List downloaded models (same as ollama list)
curl http://localhost:11434/api/tags

# List loaded models (same as ollama ps)
curl http://localhost:11434/api/ps

# One-shot generation
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Describe Ollama in one sentence.",
  "stream": false
}'

# Chat with an explicit context length
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "Why is the sky blue?"}],
  "stream": false,
  "options": {"num_ctx": 8192}
}'

# Preload a model and keep it in memory
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "keep_alive": -1}'

# Unload a model immediately
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "keep_alive": 0}'

# ⚠️ Delete a model (same as ollama rm, irreversible)
curl -X DELETE http://localhost:11434/api/delete -d '{"model": "llama3.2"}'
```

**Python example:**
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

print(chat_with_ollama("Summarize the following text in three bullet points: ..."))
```

The local API is useful for private experiments; production systems still need timeouts, retries, and logging.

{{< /note >}}
