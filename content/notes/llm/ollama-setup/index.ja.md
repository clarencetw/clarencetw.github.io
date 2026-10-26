---
title: "Ollama コマンドと設定：モデル管理、モデル削除、環境変数"
description: Ollama のよく使うコマンド（pull、run、list、ps、show、stop、rm、cp、create、serve）、モデルの削除とディスク容量の解放、モデルの保存場所、OLLAMA_HOST や OLLAMA_MODELS などの環境変数を macOS・Linux・Windows で設定する方法と REST API の例をまとめています。
lastmod: 2026-10-26T00:00:00+08:00
weight: 210
menu:
  notes:
    name: Ollama
    identifier: notes-llm-ollama
    parent: notes-llm
    weight: 10
---

{{< note title="Version と安全範囲" >}}

**最終確認：2026年10月26日**

これは一般的な command reference であり、特定 version に固定した完全な runbook ではありません。実行前に installed version、最新の公式ドキュメント、対象 account／host／path を確認してください。deploy、destroy、delete、prune、sync、upgrade、system setting の変更は、費用、停止、data loss につながる可能性があります。差分を事前確認し、必要に応じて backup を取得してください。

このページのコマンド、フラグ、環境変数、デフォルトパスは、Ollama v0.40.11（2026年10月24日リリース）時点の公式ドキュメントとソースコードで確認しています：[CLI Reference](https://docs.ollama.com/cli)、[FAQ](https://docs.ollama.com/faq)、[Context length](https://docs.ollama.com/context-length)、[API](https://docs.ollama.com/api/introduction)。デフォルト値はバージョンによって変わるため、手元の `ollama -v` と `ollama serve --help` の出力を優先してください。

{{< /note >}}

<!-- インストール -->
{{< note title="Ollama のインストール" >}}

```bash
# Linux へのインストール。同じ script を再実行するとアップグレード
curl -fsSL https://ollama.com/install.sh | sh

# バージョン確認
ollama -v

# server を手動で起動（デフォルトは 127.0.0.1:11434）
ollama serve
```

- macOS と Windows は [ollama.com/download](https://ollama.com/download) からアプリをインストールします。更新は自動でダウンロードされ、メニューバー／タスクバーの「Restart to update」で適用されます。
- Linux のインストール script は `ollama` systemd service を作成するため、通常は `ollama serve` を手動で実行する必要はありません。

{{< /note >}}

<!-- コマンド一覧 -->
{{< note title="Ollama コマンド一覧" >}}

| コマンド | 用途 |
| :-- | :-- |
| `ollama pull MODEL` | モデルのダウンロード・更新 |
| `ollama run MODEL [PROMPT]` | モデルを実行。ローカルにない場合は先にダウンロード |
| `ollama list`／`ollama ls` | ダウンロード済みモデルの一覧 |
| `ollama ps` | メモリにロード中のモデルの一覧 |
| `ollama show MODEL` | モデル情報の表示 |
| `ollama stop MODEL` | モデルをメモリから即時アンロード |
| `ollama cp SOURCE DESTINATION` | 別名でモデルをコピー |
| `ollama rm MODEL [MODEL...]` | **モデルを削除（元に戻せない）** |
| `ollama create NAME -f Modelfile` | Modelfile からカスタムモデルを作成 |
| `ollama serve` | Ollama server を起動 |

```bash
# モデルをダウンロード
ollama pull llama3.2

# 対話モード。/bye で終了
ollama run llama3.2

# 1 回だけ質問（script 向け）
ollama run llama3.2 "RAG とは何かを 3 文で説明して"

# 応答時間や速度などの統計を表示
ollama run llama3.2 --verbose

# モデルをメモリに保持する時間を指定
ollama run llama3.2 --keepalive 30m

# ダウンロード済みモデルの一覧（ls は list の別名）
ollama list
ollama ls

# ロード中のモデル、サイズ、GPU/CPU の割り当てを確認
ollama ps

# モデルをアンロードして RAM / VRAM を解放（ファイルは削除しない）
ollama stop llama3.2
```

`ollama ps` の `PROCESSOR` 列は、`100% GPU` なら GPU に完全ロード、`100% CPU` ならシステムメモリに完全ロード、`48%/52% CPU/GPU` なら両方に分散していることを示します。

**モデル情報の確認：**
```bash
ollama show llama3.2
ollama show llama3.2 --modelfile   # Modelfile
ollama show llama3.2 --parameters  # パラメータ
ollama show llama3.2 --template    # template
ollama show llama3.2 --system      # system message
ollama show llama3.2 --license     # ライセンス
```

script ではモデル名と tag を明示し、デフォルトモデルや `latest` の変更で結果が気づかないうちに変わらないようにします。

{{< /note >}}

<!-- モデル削除 -->
{{< note title="モデルの削除とディスク容量の解放" >}}

> ⚠️ **破壊的な操作：** `ollama rm` は確認なしでローカルのモデルを即座に削除し、元に戻せません。再び使うには `ollama pull` で再ダウンロードが必要です。

```bash
# まずモデル名とサイズを確認
ollama list

# モデルを 1 つ削除
ollama rm llama3.2

# 複数のモデルをまとめて削除
ollama rm llama3.2 mymodel
```

**モデルのデフォルト保存場所：**

| プラットフォーム | パス |
| :-- | :-- |
| macOS | `~/.ollama/models` |
| Linux（公式インストール script） | `/usr/share/ollama/.ollama/models` |
| Windows | `C:\Users\%username%\.ollama\models` |

`OLLAMA_MODELS` を設定している場合は、そのディレクトリに保存されます。

```bash
# モデルディレクトリの使用量（macOS）
du -sh ~/.ollama/models

# Linux（公式インストール script）
sudo du -sh /usr/share/ollama/.ollama/models
```

- モデルの削除には `ollama rm` を使い、`blobs`／`manifests` 配下のファイルを個別に手動削除しないでください。モデルデータが不整合になるおそれがあります。
- server は起動時に未使用の model blob をデフォルトで削除します。`OLLAMA_NOPRUNE=1` でこの動作を無効にできます。
- ⚠️ データディレクトリ全体（macOS の `~/.ollama`、Linux の `/usr/share/ollama` など）を `rm -rf` すると、すべてのモデルが一度に消えます。公式ドキュメントではアンインストール手順としてのみ記載されています。実行前にパスを確認してください。
- ディスクではなくメモリだけを解放したい場合は `ollama stop MODEL` で十分です。

{{< /note >}}

<!-- Modelfile -->
{{< note title="Modelfile でカスタムモデルを作成" >}}

```text
# Modelfile
FROM llama3.2
PARAMETER temperature 0.7
PARAMETER num_ctx 8192
SYSTEM あなたは日本語で簡潔に答える技術アシスタントです。
```

```bash
# モデルを作成（-f のデフォルトはカレントディレクトリの Modelfile）
ollama create my-assistant -f ./Modelfile

# カスタムモデルを実行
ollama run my-assistant

# 元のモデルを残したまま変更したいときはコピーしてから編集
ollama cp my-assistant my-assistant-v2
```

{{< /note >}}

<!-- 環境変数 -->
{{< note title="Ollama の設定：主な環境変数" >}}

Ollama server は環境変数で設定します。全一覧は `ollama serve --help` で確認できます。

| 環境変数 | 用途 | デフォルト |
| :-- | :-- | :-- |
| `OLLAMA_HOST` | server の待ち受けアドレスとポート | `127.0.0.1:11434` |
| `OLLAMA_MODELS` | モデルの保存ディレクトリ | 上の「デフォルト保存場所」を参照 |
| `OLLAMA_KEEP_ALIVE` | アイドル状態のモデルをメモリに残す時間。負の値で常駐、`0` で即時アンロード | `5m` |
| `OLLAMA_CONTEXT_LENGTH` | デフォルトの context length | VRAM に応じて 24 GiB 未満は 4k、24–48 GiB は 32k、48 GiB 以上は 256k |
| `OLLAMA_NUM_PARALLEL` | モデルごとの同時処理リクエスト数 | `1` |
| `OLLAMA_MAX_LOADED_MODELS` | 同時にロードできるモデル数 | GPU 数 × 3、CPU 推論では 3 |
| `OLLAMA_MAX_QUEUE` | ビジー時に待機できるリクエスト数。超えると 503 | `512` |
| `OLLAMA_ORIGINS` | 追加で許可する CORS origin（カンマ区切り） | `127.0.0.1`、`0.0.0.0` を許可 |
| `OLLAMA_FLASH_ATTENTION` | `1` で Flash Attention を強制有効、`0` で無効 | 対応環境では自動 |
| `OLLAMA_KV_CACHE_TYPE` | K/V cache の量子化：`f16`、`q8_0`、`q4_0` | `f16` |
| `OLLAMA_DEBUG` | デバッグ情報を表示（例：`OLLAMA_DEBUG=1`） | オフ |
| `OLLAMA_NOPRUNE` | 起動時に未使用の model blob を削除しない | オフ |
| `OLLAMA_NO_CLOUD` | クラウドモデルや web search などのクラウド機能を無効化 | オフ |

- FAQ には context length のデフォルトが 4096 と書かれたままです。実際の値はインストール済みバージョンの `ollama serve --help` で確認してください。
- `OLLAMA_NUM_PARALLEL` を増やすと、必要なメモリは「並列数 × context length」に応じて増えます。
- API リクエストの `keep_alive` パラメータは `OLLAMA_KEEP_ALIVE` より優先されます。

**一時的な設定（`ollama serve` をフォアグラウンドで実行する場合）：**
```bash
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_CONTEXT_LENGTH=8192 ollama serve
```

{{< /note >}}

<!-- macOS -->
{{< note title="macOS で環境変数を設定" >}}

macOS アプリとして Ollama を実行している場合は `launchctl` で設定し、アプリを再起動します。

```bash
launchctl setenv OLLAMA_MODELS "/Volumes/Data/ollama/models"
launchctl setenv OLLAMA_KEEP_ALIVE "30m"
# 設定後、Ollama アプリを終了して再度起動する
```

{{< /note >}}

<!-- Linux -->
{{< note title="Linux で環境変数を設定（systemd override）" >}}

systemd service として実行している場合は、インストール時の unit ファイルを直接編集せず override で設定します。

```bash
sudo systemctl edit ollama.service
```

開いたエディタで `[Service]` の下に追加します。

```ini
[Service]
Environment="OLLAMA_MODELS=/data/ollama/models"
Environment="OLLAMA_KEEP_ALIVE=30m"
Environment="OLLAMA_NUM_PARALLEL=2"
```

```bash
# モデルディレクトリを変更した場合、ollama ユーザーに読み書き権限が必要
sudo chown -R ollama:ollama /data/ollama/models

# 設定を再読み込みしてサービスを再起動
sudo systemctl daemon-reload
sudo systemctl restart ollama

# ログを確認
journalctl -e -u ollama
```

{{< /note >}}

<!-- Windows -->
{{< note title="Windows で環境変数を設定" >}}

Windows の Ollama はユーザーとシステムの環境変数を引き継ぎます。

1. タスクバーから Ollama を終了します。
2. 「設定」（Windows 11）または「コントロール パネル」（Windows 10）を開き、「環境変数」を検索します。
3. 「アカウントの環境変数を編集」をクリックします。
4. `OLLAMA_HOST`、`OLLAMA_MODELS` などのユーザー環境変数を作成・編集します。
5. 「OK／適用」で保存します。
6. スタートメニューから Ollama を再度起動します。

`OLLAMA_MODELS` を別ドライブに向けると、モデルでシステムドライブが埋まるのを防げます。保存場所を変更した場合、アンインストーラーはそのディレクトリ内のモデルを削除しません。

{{< /note >}}

<!-- ネットワーク公開 -->
{{< note title="LAN に公開するときの注意" >}}

```bash
# すべてのネットワークインターフェースで待ち受け（設定方法はプラットフォームごとに上記参照）
OLLAMA_HOST=0.0.0.0:11434
```

> ⚠️ ローカル API はデフォルトで認証がありません。`0.0.0.0` にすると、同じネットワーク上の誰でもモデルの実行、ダウンロード、削除ができます。ファイアウォール、reverse proxy、VPN などでアクセス元を制限し、インターネットに直接公開しないでください。

ブラウザ拡張機能から API を呼び出す場合は、origin を明示的に許可します。

```bash
OLLAMA_ORIGINS=chrome-extension://*,moz-extension://*,safari-web-extension://* ollama serve
```

{{< /note >}}

<!-- API -->
{{< note title="REST API の例" >}}

ローカル API の base URL は `http://localhost:11434/api` です。OpenAI 互換 API は `http://localhost:11434/v1` で利用できます。

```bash
# server のバージョン
curl http://localhost:11434/api/version

# ダウンロード済みモデルの一覧（ollama list と同じ）
curl http://localhost:11434/api/tags

# ロード中のモデルの一覧（ollama ps と同じ）
curl http://localhost:11434/api/ps

# 単発の生成
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Ollama を一文で説明してください。",
  "stream": false
}'

# context length を指定してチャット
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "空はなぜ青いのですか？"}],
  "stream": false,
  "options": {"num_ctx": 8192}
}'

# モデルを事前ロードして常駐させる
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "keep_alive": -1}'

# モデルを即時アンロード
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "keep_alive": 0}'

# ⚠️ モデルを削除（ollama rm と同じ、元に戻せない）
curl -X DELETE http://localhost:11434/api/delete -d '{"model": "llama3.2"}'
```

**Python の例：**
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

print(chat_with_ollama("次の文章を 3 つの要点に要約してください：..."))
```

ローカル API は個人的な実験に便利ですが、本番環境では timeout、retry、logging が必要です。

{{< /note >}}
