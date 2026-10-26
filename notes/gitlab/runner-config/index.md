---
title: "GitLab Runner config.toml 設定與常用 CI/CD 變數"
url: "https://clarence.tw/notes/gitlab/runner-config/"
language: "zh-tw"
---

# GitLab Runner config.toml 設定與常用 CI/CD 變數

GitLab Runner 註冊（glrt- authentication token）、config.toml 位置與 concurrent、executor、[runners.docker]、cache 設定，Docker-in-Docker、Harbor 私有 registry 與 CI_COMMIT_SHA 等常用預先定義變數速查。

## 版本與安全範圍

**最後檢視：2026-10-26**

內容依 2026-10-26 的 GitLab 官方文件整理，當時最新的 GitLab Runner 為 v19.5.1。設定項目與預設值會隨版本變動，正式環境請先核對 [Runner advanced configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/)、[Runner 註冊](https://docs.gitlab.com/runner/register/) 與 [Predefined CI/CD variables](https://docs.gitlab.com/ci/variables/predefined_variables/)。

`privileged = true`、掛載 `/var/run/docker.sock`、`gitlab-runner unregister` 與 `gitlab-runner verify --delete` 都有安全或不可復原的風險，下方會個別標示。修改前先備份 `config.toml`；runner token 與 registry 密碼都是 secret，不要寫進 repository 或 CI log。

## 註冊 Runner（authentication token 流程）

新的流程是先在 GitLab 建立 runner，再用 runner authentication token 註冊：

1. Project runner：到 project 的 **Settings** > **CI/CD** > **Runners**，選 **Create project runner**（需要 Maintainer 角色）。Group 或 instance runner 則在 group 設定或 Admin Area 建立。
2. 設定 tags、描述等屬性後建立，畫面會顯示以 `glrt-` 開頭的 authentication token，只會短暫顯示一次。
3. 在 runner 主機上註冊：

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

- 舊的 registration token（`--registration-token`）已 deprecated，官方文件標示預計在 GitLab 20.0 移除；新 runner 請一律使用 authentication token。
- Tags、protected、run untagged 等屬性改在 GitLab UI 或 API 建立 runner 時設定，不再由 `register` 參數決定。
- 自動化建立 runner 可呼叫 `POST /api/v4/user/runners`，用具備 `create_runner` scope 的 access token 取得 runner token，再交給 `register`：

```bash
curl --silent --request POST --url "https://gitlab.example.com/api/v4/user/runners" \
  --data "runner_type=project_type" \
  --data "project_id=<project_id>" \
  --data "description=docker-runner" \
  --data "tag_list=docker,linux" \
  --header "PRIVATE-TOKEN: <project_access_token>"
```

**關於 `gitlab_pat`：**`config.toml` 沒有 `gitlab_pat` 這個設定。Runner 連線 GitLab 用的是 `[[runners]]` 裡的 `token`（`glrt-` 開頭的 runner authentication token）；Personal access token（`glpat-` 開頭）只用在呼叫 API 建立 runner 這類自動化步驟，不需要也不應該寫進 `config.toml`。

## config.toml 位置

| 安裝方式 | `config.toml` 路徑 |
| :-- | :-- |
| Linux／macOS 以 root（`sudo`）執行 | `/etc/gitlab-runner/config.toml` |
| Linux／macOS 以一般使用者執行 | `~/.gitlab-runner/config.toml` |
| Windows | 安裝目錄下，例如 `C:\GitLab-Runner\config.toml` |
| 其他系統 | 目前目錄的 `./config.toml` |
| Docker container | container 內的 `/etc/gitlab-runner/`，通常掛載自 host 的 `/srv/gitlab-runner/config` 或 Docker volume |

Docker container 安裝範例（官方文件寫法）：

```bash
docker run -d --name gitlab-runner --restart always \
  -v /srv/gitlab-runner/config:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitlab/gitlab-runner:latest
```

這個範例會把 host 的 Docker socket 交給 runner container，風險見下方「Docker-in-Docker 與 socket binding」。

**重新載入：**Runner 每 3 秒檢查一次 `config.toml`，有變更會自動重新載入，也可送 `SIGHUP`。大部分設定不需要重新啟動，例外是 `listen_address`。

## 常用 config.toml 設定

```toml
concurrent = 4          # 所有 runner 合計的同時 job 上限，不能設 0
check_interval = 3      # 向 GitLab 詢問新 job 的間隔（秒），預設 3
log_level = "info"      # debug / info / warn / error / fatal / panic
shutdown_timeout = 30   # 強制關閉前等待的秒數，預設 30

[[runners]]
  name = "docker-runner"                 # 僅供識別
  url = "https://gitlab.example.com/"
  token = "glrt-REDACTED"                # authentication token，不是 registration token
  executor = "docker"                    # shell、docker、kubernetes 等
  limit = 0                              # 此 runner 的同時 job 上限，0 代表不限制
  request_concurrency = 1                # 同時向 GitLab 要 job 的請求數，預設 1
  environment = ["TZ=Asia/Taipei"]       # 附加或覆寫 job 的環境變數

  [runners.docker]
    image = "alpine:latest"              # job 未指定 image 時使用
    privileged = false                   # 開啟會停用 container 隔離，見下方
    volumes = ["/cache"]                 # 額外掛載，語法同 docker -v
    pull_policy = "if-not-present"       # never / if-not-present / always，預設 always
    allowed_images = ["registry.example.com/*"]  # 限制 job 可用的 image，未設定代表全部允許
    shm_size = 0

  [runners.cache]
    Type = "s3"                          # s3 / gcs / azure
    Path = "runner-cache"                # 加在 cache URL 前的路徑
    Shared = true                        # 多個 runner 共用 cache，預設 false
    [runners.cache.s3]
      ServerAddress = "s3.example.com"
      BucketName = "gitlab-runner-cache"
      BucketLocation = "ap-northeast-1"
      AuthenticationType = "iam"         # iam 或 access-key
```

- `concurrent` 是整台 runner process 的上限；`limit` 是單一 `[[runners]]` 的上限，兩者同時生效。
- `pull_policy = "if-not-present"` 可加快 job 啟動，但 host 上已存在的舊 image 不會自動更新；固定 tag 或 digest 比較好掌握。
- `[runners.cache.s3]` 若同時提供 `ServerAddress`、`AccessKey`、`SecretKey`，`AuthenticationType` 預設為 `access-key`，否則為 `iam`。`AccessKey`／`SecretKey` 屬於 secret，優先使用 IAM role。
- `listen_address = ":9252"` 可開啟 Prometheus metrics；未設定時不提供 metrics，修改後需要重新啟動。

## Docker-in-Docker 與 socket binding

在 job 裡執行 `docker build` 有兩種常見做法：

| 做法 | 設定 | 優點 | 風險 |
| :-- | :-- | :-- | :-- |
| Docker-in-Docker（DinD） | `privileged = true`、`volumes = ["/certs/client", "/cache"]` | 每個 job 有獨立的 Docker daemon，job 之間不衝突 | Privileged 會實質停用 container 安全機制，可能被利用來逃逸到 host |
| Docker socket binding | `volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]`、`privileged = false` | 不需要 privileged，可共用 host 的 image cache | 等同把 host Docker daemon 交給 job：可能 container breakout、提權，或刪掉 runner 自己的 container |

**安全警告：**`privileged = true` 與掛載 `docker.sock` 都等同給 job 接近 host root 的權限。只在專用、可信任 project 使用的 runner 上開啟，不要用在會執行外部 fork 或不受信任程式碼的 shared runner。

DinD（TLS 啟用）的 `.gitlab-ci.yml`：

```yaml
build-image:
  image: docker:<version>-cli          # 換成團隊驗證過的版本
  services:
    - docker:<version>-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
```

Socket binding 的限制：不能搭配 `docker:dind` service；job 裡的 volume 路徑是以 host 為準，固定名稱的 container 在同時執行的 job 之間會衝突。

## 使用 Harbor 等私有 registry

Runner 拉取 job image 或 service image 時，若來源是 Harbor 等私有 registry，用 `DOCKER_AUTH_CONFIG` 提供認證：

```bash
# 產生 auth 值；用 printf 避免把換行一起編碼
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

- 可以設成 project／group 的 CI/CD variable `DOCKER_AUTH_CONFIG`（建議設為 masked），或寫在 `[[runners]]` 的 `environment`（雙引號需跳脫），也可放在 runner 主機的 `.docker/config.json`。
- Runner 讀取順序：`/root/.docker/config.json` → CI/CD variable → `config.toml` 的 `environment` → 執行 runner 的使用者 `$HOME/.docker/config.json`。
- `auths` 的 key 必須與 image 參照完全相同；image 是 `harbor.example.com:5000/...` 時，key 也要寫 `harbor.example.com:5000`。
- 建議使用 Harbor 的 robot account，只給需要的 project 權限。

推送 image 到 GitLab 內建 Container Registry 時，可直接使用預先定義變數：

```yaml
script:
  - echo "$CI_REGISTRY_PASSWORD" | docker login "$CI_REGISTRY" -u "$CI_REGISTRY_USER" --password-stdin
  - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
```

`CI_REGISTRY_PASSWORD` 與 `CI_JOB_TOKEN` 相同，job 結束就失效；需要長期存取請改用 deploy token。推送到 Harbor 則需要自行建立 masked CI/CD variables 保存 robot account 帳密。

## 常用 gitlab-runner 指令

```bash
sudo gitlab-runner list        # 列出 config.toml 中的 runner
sudo gitlab-runner verify      # 檢查已註冊的 runner 能否連上 GitLab
sudo gitlab-runner status      # 服務狀態；執行中時 exit code 為 0
sudo gitlab-runner restart     # 停止後再啟動服務
sudo gitlab-runner start
sudo gitlab-runner stop

# 不需重啟，讓 runner 重新讀取 config.toml
sudo kill -SIGHUP <main_runner_pid>
```

**不可復原的指令（先備份 `config.toml`）：**

```bash
# 移除 GitLab 上已不存在的 runner，會改寫 config.toml
sudo gitlab-runner verify --delete

# 依名稱取消註冊；同名時只移除第一個
sudo gitlab-runner unregister --name docker-runner

# 依 URL 與 token 取消註冊
sudo gitlab-runner unregister --url "https://gitlab.example.com/" --token "$RUNNER_TOKEN"

# 取消註冊所有 runner
sudo gitlab-runner unregister --all-runners
```

- 對在 GitLab UI 或 API 建立的 runner 執行 `unregister`，只會移除 runner manager；要完整刪除 runner，還要到 GitLab UI 或用 API 刪除。
- 不加 `sudo` 執行時是 user-mode，會讀寫 `~/.gitlab-runner/config.toml`，常見「找不到 runner」就是這個原因。
- 不要用 `killall` 或 `pkill` 關閉 shell／docker executor 的 runner，可能破壞 signal 處理；要優雅停止請送 `SIGQUIT`。

## 常用預先定義 CI/CD 變數

| 變數 | 內容 | 注意事項 |
| :-- | :-- | :-- |
| `CI_COMMIT_SHA` | 此 pipeline 建置的完整 commit hash | |
| `CI_COMMIT_SHORT_SHA` | `CI_COMMIT_SHA` 的前 8 個字元 | 常用於 image tag |
| `CI_COMMIT_REF_NAME` | 正在建置的 branch 或 tag 名稱 | |
| `CI_COMMIT_REF_SLUG` | `CI_COMMIT_REF_NAME` 轉小寫、非英數字元換成 `-`、最長 63 bytes | 適合用在 URL、hostname、image tag |
| `CI_COMMIT_BRANCH` | Branch 名稱 | Merge request pipeline 與 tag pipeline 中不存在 |
| `CI_COMMIT_TAG` | Tag 名稱 | 只在 tag pipeline 中存在 |
| `CI_DEFAULT_BRANCH` | Project 的預設 branch 名稱 | |
| `CI_PIPELINE_SOURCE` | Pipeline 的觸發來源 | 例如 `push`、`merge_request_event`、`schedule`、`web`、`api`、`trigger`、`parent_pipeline` |
| `CI_PIPELINE_ID` | Pipeline ID（整個 instance 唯一） | 只在 job 中可用 |
| `CI_JOB_ID` | Job ID（整個 instance 唯一） | 只在 job 中可用 |
| `CI_REGISTRY` | Container Registry 位址（`<host>[:<port>]`） | Instance 啟用 registry 時才有 |
| `CI_REGISTRY_IMAGE` | Project 的 image 基礎路徑（`<host>[:<port>]/<project_full_path>`） | Project 啟用 registry 時才有 |
| `CI_REGISTRY_USER`／`CI_REGISTRY_PASSWORD` | 推送到 project registry 用的帳密 | 密碼等同 `CI_JOB_TOKEN`，job 結束即失效 |
| `CI_PROJECT_DIR` | Repository clone 的完整路徑，也是 job 的工作目錄 | 設定 `builds_dir` 時以它為準 |
| `CI_PROJECT_NAME`／`CI_PROJECT_PATH` | Project 目錄名稱／namespace 加 project 名稱 | |
| `CI_JOB_TOKEN` | 呼叫部分 API 用的 token | 只在 job 執行期間有效，不要印到 log |
| `CI_ENVIRONMENT_NAME` | Job 的 environment 名稱 | 有設定 `environment:name` 時才有 |
| `CI_MERGE_REQUEST_IID` | Merge request 在 project 內的 ID | 只在 merge request pipeline 中存在 |
| `CI_SERVER_URL` | GitLab instance 的基礎 URL（含 protocol 與 port） | |
| `GITLAB_USER_LOGIN` | 啟動 pipeline 的使用者帳號 | Manual job 為啟動該 job 的使用者 |

依 pipeline 類型切換行為的常見寫法：

```yaml
deploy:
  script:
    - echo "Deploy $CI_COMMIT_SHORT_SHA to $CI_ENVIRONMENT_NAME"
  environment:
    name: production
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"   # 排程觸發的 pipeline 不部署
      when: never
    - if: $CI_COMMIT_TAG                       # 只在 tag pipeline 部署
```

延伸閱讀：完整的 `.gitlab-ci.yml`、Harbor 與多環境部署範例，請參考 [GitLab CI/CD 完整配置指南](https://clarence.tw/posts/gitlab-cicd-complete-guide/)。
