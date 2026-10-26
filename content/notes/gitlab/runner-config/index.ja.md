---
title: GitLab Runner config.toml 設定とよく使う CI/CD 変数
description: GitLab Runner の登録（glrt- authentication token）、config.toml の場所、concurrent・executor・[runners.docker]・cache 設定、Docker-in-Docker、Harbor など private registry、CI_COMMIT_SHA などの定義済み変数を整理。
lastmod: 2026-10-26T00:00:00+08:00
weight: 510
menu:
  notes:
    name: Runner config.toml
    identifier: notes-gitlab-runner-config
    parent: notes-gitlab
    weight: 10
---

{{< note title="Version と安全範囲" >}}

**最終確認：2026年10月26日**

2026年10月26日時点の GitLab 公式ドキュメントをもとに整理しています。当時の最新 GitLab Runner は v19.5.1 です。設定項目や default 値は version によって変わるため、本番環境では [Runner advanced configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/)、[Runner の登録](https://docs.gitlab.com/runner/register/)、[Predefined CI/CD variables](https://docs.gitlab.com/ci/variables/predefined_variables/) を確認してください。

`privileged = true`、`/var/run/docker.sock` の mount、`gitlab-runner unregister`、`gitlab-runner verify --delete` には security 上または取り消せないリスクがあり、以下で個別に示します。変更前に `config.toml` を backup してください。Runner token や registry password は secret です。repository や CI log に残さないでください。

{{< /note >}}

{{< note title="Runner の登録（authentication token 方式）" >}}

現在の手順では、先に GitLab で runner を作成し、runner authentication token で登録します。

1. Project runner の場合、project の **Settings** > **CI/CD** > **Runners** で **Create project runner** を選択します（Maintainer role が必要）。Group runner や instance runner は group 設定または Admin Area で作成します。
2. Tags や説明を設定して作成すると、`glrt-` で始まる authentication token が短時間だけ表示されます。
3. Runner host で登録します。

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.example.com/" \
  --token "$RUNNER_TOKEN" \
  --executor "docker" \
  --docker-image alpine:latest \
  --docker-pull-policy "if-not-present" \
  --description "docker-runner"
```

- 旧来の registration token（`--registration-token`）は deprecated で、公式ドキュメントでは GitLab 20.0 で削除予定とされています。新しい runner には authentication token を使ってください。
- Tags、protected、run untagged などは GitLab UI または API で runner を作成するときに設定し、`register` の引数では指定しません。
- Runner 作成を自動化する場合は、`create_runner` scope を持つ access token で `POST /api/v4/user/runners` を呼び出し、返された token を `register` に渡します。

```bash
curl --silent --request POST --url "https://gitlab.example.com/api/v4/user/runners" \
  --data "runner_type=project_type" \
  --data "project_id=<project_id>" \
  --data "description=docker-runner" \
  --data "tag_list=docker,linux" \
  --header "PRIVATE-TOKEN: <project_access_token>"
```

**`gitlab_pat` について：**`config.toml` に `gitlab_pat` という設定はありません。Runner が GitLab への接続に使うのは `[[runners]]` の `token`（`glrt-` で始まる runner authentication token）です。Personal access token（`glpat-` で始まる）は runner 作成などの API 自動化にだけ使い、`config.toml` に書く必要はありません。

{{< /note >}}

{{< note title="config.toml の場所" >}}

| インストール方法 | `config.toml` のパス |
| :-- | :-- |
| Linux／macOS を root（`sudo`）で実行 | `/etc/gitlab-runner/config.toml` |
| Linux／macOS を一般ユーザーで実行 | `~/.gitlab-runner/config.toml` |
| Windows | インストール folder、例：`C:\GitLab-Runner\config.toml` |
| その他の system | カレントディレクトリの `./config.toml` |
| Docker container | container 内の `/etc/gitlab-runner/`。通常は host の `/srv/gitlab-runner/config` または Docker volume を mount |

Docker container でのインストール例（公式ドキュメントの形式）：

```bash
docker run -d --name gitlab-runner --restart always \
  -v /srv/gitlab-runner/config:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitlab/gitlab-runner:latest
```

この例は host の Docker socket を runner container に渡します。リスクは「Docker-in-Docker と socket binding」を参照してください。

**再読み込み：**Runner は 3 秒ごとに `config.toml` を確認し、変更があれば自動で再読み込みします。`SIGHUP` でも再読み込みできます。ほとんどの設定は再起動不要ですが、`listen_address` は例外です。

{{< /note >}}

{{< note title="よく使う config.toml 設定" >}}

```toml
concurrent = 4          # 全 runner 合計の同時 job 上限。0 は不可
check_interval = 3      # GitLab に新しい job を問い合わせる間隔（秒）。default 3
log_level = "info"      # debug / info / warn / error / fatal / panic
shutdown_timeout = 30   # 強制終了までの秒数。default 30

[[runners]]
  name = "docker-runner"                 # 識別用
  url = "https://gitlab.example.com/"
  token = "glrt-REDACTED"                # authentication token（registration token ではない）
  executor = "docker"                    # shell、docker、kubernetes など
  limit = 0                              # この runner の同時 job 上限。0 は無制限
  request_concurrency = 1                # GitLab への同時 job request 数。default 1
  environment = ["TZ=Asia/Taipei"]       # job の環境変数を追加・上書き

  [runners.docker]
    image = "alpine:latest"              # job が image を指定しない場合に使用
    privileged = false                   # true にすると container 隔離が無効になる（後述）
    volumes = ["/cache"]                 # 追加 mount。docker -v と同じ書式
    pull_policy = "if-not-present"       # never / if-not-present / always。default always
    allowed_images = ["registry.example.com/*"]  # job が使える image を制限。未設定ならすべて許可
    shm_size = 0

  [runners.cache]
    Type = "s3"                          # s3 / gcs / azure
    Path = "runner-cache"                # cache URL の先頭に付く path
    Shared = true                        # runner 間で cache を共有。default false
    [runners.cache.s3]
      ServerAddress = "s3.example.com"
      BucketName = "gitlab-runner-cache"
      BucketLocation = "ap-northeast-1"
      AuthenticationType = "iam"         # iam または access-key
```

- `concurrent` は runner process 全体の上限、`limit` は個々の `[[runners]]` の上限で、両方が適用されます。
- `pull_policy = "if-not-present"` は job の起動を速くしますが、host にある古い image は更新されません。tag や digest を固定してください。
- `[runners.cache.s3]` で `ServerAddress`、`AccessKey`、`SecretKey` がすべて設定されていれば `AuthenticationType` の default は `access-key`、それ以外は `iam` です。`AccessKey`／`SecretKey` は secret なので、可能なら IAM role を使ってください。
- `listen_address = ":9252"` で Prometheus metrics を有効にできます。未設定なら metrics は無効で、変更時は再起動が必要です。

{{< /note >}}

{{< note title="Docker-in-Docker と socket binding" >}}

Job 内で `docker build` を実行する代表的な方法は 2 つあります。

| 方法 | 設定 | 利点 | リスク |
| :-- | :-- | :-- | :-- |
| Docker-in-Docker（DinD） | `privileged = true`、`volumes = ["/certs/client", "/cache"]` | Job ごとに独立した Docker daemon を持ち、job 同士が衝突しない | Privileged は container の security 機構を実質的に無効にし、host への escape につながり得る |
| Docker socket binding | `volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]`、`privileged = false` | Privileged 不要で、host の image cache を共有できる | Host の Docker daemon を job に渡すことになり、container breakout、権限昇格、runner 自身の container 削除が起こり得る |

**Security 警告：**`privileged = true` と `docker.sock` の mount は、どちらも job に host の root に近い権限を与えます。信頼できる project 専用の runner に限定し、fork や信頼できない code を実行する shared runner では使わないでください。

TLS を有効にした DinD の `.gitlab-ci.yml`：

```yaml
build-image:
  image: docker:<version>-cli          # チームで検証済みの version に置き換える
  services:
    - docker:<version>-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
```

Socket binding の制限：`docker:dind` service と併用できず、job 内の volume path は host 基準で解決され、固定名の container は同時実行 job の間で衝突します。

{{< /note >}}

{{< note title="Harbor など private registry の利用" >}}

Runner が Harbor などの private registry から job image や service image を pull する場合は、`DOCKER_AUTH_CONFIG` で認証情報を渡します。

```bash
# auth 値を作成。printf を使い、改行を encode しない
printf "my_username:my_password" | openssl base64 -A
```

```json
{
  "auths": {
    "harbor.example.com": {
      "auth": "<base64 of username:password>"
    }
  }
}
```

- Project／group の CI/CD variable `DOCKER_AUTH_CONFIG`（masked 推奨）、`[[runners]]` の `environment`（二重引用符は escape）、または runner host の `.docker/config.json` に設定できます。
- 読み込み順：`/root/.docker/config.json` → CI/CD variable → `config.toml` の `environment` → runner を実行するユーザーの `$HOME/.docker/config.json`。
- `auths` の key は image の参照と完全に一致させます。image が `harbor.example.com:5000/...` なら key も `harbor.example.com:5000` です。
- Harbor の robot account を使い、必要な project だけに権限を絞ってください。

GitLab 内蔵の Container Registry に push する場合は、定義済み変数をそのまま使えます。

```yaml
script:
  - echo "$CI_REGISTRY_PASSWORD" | docker login "$CI_REGISTRY" -u "$CI_REGISTRY_USER" --password-stdin
  - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
```

`CI_REGISTRY_PASSWORD` は `CI_JOB_TOKEN` と同じで、job 終了時に失効します。長期的なアクセスには deploy token を使ってください。Harbor に push する場合は、robot account の認証情報を masked CI/CD variables として自分で用意します。

{{< /note >}}

{{< note title="よく使う gitlab-runner コマンド" >}}

```bash
sudo gitlab-runner list        # config.toml の runner を一覧表示
sudo gitlab-runner verify      # 登録済み runner が GitLab に接続できるか確認
sudo gitlab-runner status      # service の状態。実行中なら exit code 0
sudo gitlab-runner restart     # service を停止して再起動
sudo gitlab-runner start
sudo gitlab-runner stop

# 再起動せずに config.toml を再読み込み
sudo kill -SIGHUP <main_runner_pid>
```

**取り消せないコマンド（先に `config.toml` を backup）：**

```bash
# GitLab に存在しなくなった runner を削除。config.toml を書き換える
sudo gitlab-runner verify --delete

# 名前で登録解除。同名が複数ある場合は最初の 1 つだけ削除
sudo gitlab-runner unregister --name docker-runner

# URL と token で登録解除
sudo gitlab-runner unregister --url "https://gitlab.example.com/" --token "$RUNNER_TOKEN"

# すべての runner を登録解除
sudo gitlab-runner unregister --all-runners
```

- GitLab UI または API で作成した runner に `unregister` を実行しても、削除されるのは runner manager だけです。Runner を完全に削除するには UI または API で削除してください。
- `sudo` なしで実行すると user-mode になり、`~/.gitlab-runner/config.toml` を使います。「runner が見つからない」原因としてよくあります。
- Shell／docker executor の runner を `killall` や `pkill` で止めないでください。signal 処理が壊れることがあります。正常に停止するには `SIGQUIT` を送ります。

{{< /note >}}

{{< note title="よく使う定義済み CI/CD 変数" >}}

| 変数 | 内容 | 注意点 |
| :-- | :-- | :-- |
| `CI_COMMIT_SHA` | Pipeline が build する commit の完全な hash | |
| `CI_COMMIT_SHORT_SHA` | `CI_COMMIT_SHA` の先頭 8 文字 | Image tag によく使う |
| `CI_COMMIT_REF_NAME` | Build 対象の branch または tag 名 | |
| `CI_COMMIT_REF_SLUG` | `CI_COMMIT_REF_NAME` を小文字化し、英数字以外を `-` に置換、最大 63 bytes | URL、hostname、image tag 向け |
| `CI_COMMIT_BRANCH` | Branch 名 | Merge request pipeline と tag pipeline では使えない |
| `CI_COMMIT_TAG` | Tag 名 | Tag pipeline のみ |
| `CI_DEFAULT_BRANCH` | Project の default branch 名 | |
| `CI_PIPELINE_SOURCE` | Pipeline の起動元 | 例：`push`、`merge_request_event`、`schedule`、`web`、`api`、`trigger`、`parent_pipeline` |
| `CI_PIPELINE_ID` | Pipeline ID（instance 全体で一意） | Job 内のみ |
| `CI_JOB_ID` | Job ID（instance 全体で一意） | Job 内のみ |
| `CI_REGISTRY` | Container Registry のアドレス（`<host>[:<port>]`） | Instance で registry が有効な場合のみ |
| `CI_REGISTRY_IMAGE` | Project の image のベースパス（`<host>[:<port>]/<project_full_path>`） | Project で registry が有効な場合のみ |
| `CI_REGISTRY_USER`／`CI_REGISTRY_PASSWORD` | Project registry へ push するための認証情報 | Password は `CI_JOB_TOKEN` と同じで、job 終了時に失効 |
| `CI_PROJECT_DIR` | Repository が clone され、job が実行される完全なパス | `builds_dir` を設定した場合はそれに従う |
| `CI_PROJECT_NAME`／`CI_PROJECT_PATH` | Project の directory 名／namespace と project 名 | |
| `CI_JOB_TOKEN` | 一部の API endpoint 用の token | Job 実行中のみ有効。log に出力しない |
| `CI_ENVIRONMENT_NAME` | Job の environment 名 | `environment:name` を設定した場合のみ |
| `CI_MERGE_REQUEST_IID` | Project 内の merge request ID | Merge request pipeline のみ |
| `CI_SERVER_URL` | GitLab instance のベース URL（protocol と port を含む） | |
| `GITLAB_USER_LOGIN` | Pipeline を開始したユーザー名 | Manual job ではその job を開始したユーザー |

Pipeline の種類で挙動を切り替えるよくある書き方：

```yaml
deploy:
  script:
    - echo "Deploy $CI_COMMIT_SHORT_SHA to $CI_ENVIRONMENT_NAME"
  environment:
    name: production
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"   # schedule 起動の pipeline ではデプロイしない
      when: never
    - if: $CI_COMMIT_TAG                       # tag pipeline でのみデプロイ
```

{{< /note >}}

関連記事：`.gitlab-ci.yml`、Harbor、複数環境へのデプロイの詳しい例は [GitLab CI/CD 設定ガイド]({{< ref "/posts/gitlab-cicd-complete-guide" >}}) を参照してください。
