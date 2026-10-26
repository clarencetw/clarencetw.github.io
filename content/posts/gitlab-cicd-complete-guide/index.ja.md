---
title: GitLab CI/CD 設定ガイド：Runner、.gitlab-ci.yml、Harbor、デプロイ
date: 2024-01-30T15:00:00+08:00
lastmod: 2026-07-11T00:00:00+08:00
description: GitLab Runner と config.toml、.gitlab-ci.yml の基本例、Harbor registry 連携、multi-environment deployment までの GitLab CI/CD 実務設定メモ。
menu:
  sidebar:
    name: GitLab CI/CD 設定
    identifier: gitlab-cicd-complete-guide
    weight: 40
tags: ["GitLab", "CI/CD", "DevOps", "Docker", "Automation"]
categories: ["DevOps", "Automation"]
---

Enterprise DevOps の実務では、code submission から production deployment までを自動化する GitLab CI/CD workflow を構築・運用しています。この記事では、GitLab CI/CD の基本的な configuration で得た経験を共有します。

> **2026年7月11日確認：**サンプルを GitLab Runner authentication token、Node.js 24 LTS、Docker 29.6.1 に更新しました。version と security default は変わるため、production で使う前に [GitLab Runner 登録ドキュメント](https://docs.gitlab.com/runner/register/)、[Node.js release status](https://nodejs.org/en/about/previous-releases)、[Docker Engine release notes](https://docs.docker.com/engine/release-notes/29/) を確認し、team で検証した version または digest に固定してください。

## GitLab CI/CD の基本構成

### 1. GitLab Runner のデプロイ

まず GitLab の project、group、または Admin Area で runner を作成し、tags や protected scope を設定してから、`glrt-` で始まる runner authentication token を取得します。旧 registration token workflow は deprecated で、GitLab instance ですでに無効化されている場合もあります。新しい runner で `--registration-token` を前提にするのはやめましょう。

**Self-hosted runner の設定：**
```bash
# GitLab Runner をインストール
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt-get install gitlab-runner

# Runner を登録
export RUNNER_AUTHENTICATION_TOKEN="glrt-REDACTED"
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.company.com/" \
  --token "$RUNNER_AUTHENTICATION_TOKEN" \
  --executor "docker" \
  --docker-image "alpine:3.23"
```

Authentication token は secret として扱い、repository、CI log、共有 note に保存しないでください。登録後は runner host の `config.toml` に保存されるため、file と host の access を制限します。

`config.toml` の設定項目、Docker-in-Docker の注意点、よく使う CI/CD 変数は [GitLab Runner config.toml 設定とよく使う CI/CD 変数]({{< ref "/notes/gitlab/runner-config" >}}) にまとめています。

**Docker-in-Docker の設定：**
```toml
# /etc/gitlab-runner/config.toml
concurrent = 4
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "docker-runner"
  url = "https://gitlab.company.com/"
  token = "glrt-REDACTED"
  executor = "docker"
  [runners.custom_build_dir]
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]
    [runners.cache.azure]
  [runners.docker]
    tls_verify = false
    image = "docker:29.6.1-cli"
    privileged = true
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/certs/client", "/cache"]
    shm_size = 0
```

以下の Docker-in-Docker job には、`privileged = true` と `/certs/client` volume を設定した Docker executor が必要です。Privileged runner は attack surface が大きいため、trusted project と user に限定するか、non-privileged な image build 方法を選択してください。

## `.gitlab-ci.yml` の基本例

### シンプルな Node.js project

```yaml
# .gitlab-ci.yml
image: node:24-alpine

# Stage の定義
stages:
  - test
  - build
  - deploy

# Cache の設定
cache:
  paths:
    - node_modules/

# 依存関係をインストール
before_script:
  - npm ci

# テスト stage
test:
  stage: test
  script:
    - npm run test
  only:
    - merge_requests
    - main

# ビルド stage
build:
  stage: build
  image: docker:29.6.1-cli
  services:
    - name: docker:29.6.1-dind
      alias: docker
  variables:
    DOCKER_HOST: "tcp://docker:2376"
    DOCKER_TLS_CERTDIR: "/certs"
    DOCKER_TLS_VERIFY: "1"
    DOCKER_CERT_PATH: "$DOCKER_TLS_CERTDIR/client"
  before_script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login --username "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main

# Staging 環境へ deploy
deploy:staging:
  stage: deploy
  image: alpine:3.23
  before_script:
    - apk add --no-cache kubectl
  script:
    - echo "Deploying to staging environment"
    - kubectl set image deployment/myapp myapp=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  environment:
    name: staging
  only:
    - main
```

## Harbor private registry との連携

### Harbor の設定と利用

Harbor を private Docker image registry として使い、安全かつ効率的に image を管理しています。

**Harbor の基本設定：**
```yaml
# Harbor を image registry として使う
variables:
  HARBOR_REGISTRY: "harbor.company.com"
  HARBOR_PROJECT: "myproject"
  IMAGE_NAME: "$HARBOR_REGISTRY/$HARBOR_PROJECT/myapp"

build:harbor:
  stage: build
  image: docker:29.6.1-cli
  services:
    - name: docker:29.6.1-dind
      alias: docker
  variables:
    DOCKER_HOST: "tcp://docker:2376"
    DOCKER_TLS_CERTDIR: "/certs"
    DOCKER_TLS_VERIFY: "1"
    DOCKER_CERT_PATH: "$DOCKER_TLS_CERTDIR/client"
  before_script:
    # Harbor に login
    - echo "$HARBOR_PASSWORD" | docker login --username "$HARBOR_USERNAME" --password-stdin "$HARBOR_REGISTRY"
  script:
    # Build して Harbor に push
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker build -t $IMAGE_NAME:latest .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
    - docker push $IMAGE_NAME:latest
  only:
    - main
```

**Harbor の image scan：**
```yaml
# Harbor 内蔵の image security scan
scan:harbor:
  stage: build
  needs: ["build:harbor"]
  image: alpine:3.23
  before_script:
    - apk add --no-cache curl jq
  script:
    # Harbor scan を実行
    - |
      curl -X POST -u "$HARBOR_USERNAME:$HARBOR_PASSWORD" \
      "https://$HARBOR_REGISTRY/api/v2.0/projects/$HARBOR_PROJECT/repositories/myapp/artifacts/$CI_COMMIT_SHA/scan"
    # Scan の完了を待って結果を取得
    - sleep 30
    - |
      curl -u "$HARBOR_USERNAME:$HARBOR_PASSWORD" \
      "https://$HARBOR_REGISTRY/api/v2.0/projects/$HARBOR_PROJECT/repositories/myapp/artifacts/$CI_COMMIT_SHA?with_scan_overview=true" | jq '.scan_overview'
  only:
    - main
```

## シンプルな multi-environment deployment

### 基本的な deploy の例

```yaml
# シンプルな multi-environment deployment
.deploy_template:
  image: alpine:3.23
  before_script:
    - apk add --no-cache kubectl
  script:
    - kubectl set image deployment/$APP_NAME $APP_NAME=$IMAGE_NAME:$CI_COMMIT_SHA

deploy:staging:
  extends: .deploy_template
  stage: deploy
  variables:
    APP_NAME: "myapp-staging"
  environment:
    name: staging
  only:
    - develop

deploy:production:
  extends: .deploy_template
  stage: deploy
  variables:
    APP_NAME: "myapp-prod"
  environment:
    name: production
  when: manual
  only:
    - main
```

## Docker との統合

### Dockerfile の best practices

```dockerfile
# Multi-stage build
FROM node:24-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

FROM node:24-alpine AS runtime
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .

USER nextjs
EXPOSE 3000
CMD ["npm", "start"]
```

### Docker Compose による test 環境

```yaml
# compose.test.yml
services:
  app:
    build: .
    environment:
      - NODE_ENV=test
      - DATABASE_URL=postgresql://test:test@db:5432/testdb
    depends_on:
      - db
      - redis
    
  db:
    image: postgres:18
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    
  redis:
    image: redis:8-alpine
```


## 基本的な最適化

### Cache の設定

```yaml
# シンプルな cache 設定
cache:
  paths:
    - node_modules/
    - dist/
```

```yaml
# Branch ごとの cache（どちらか一方を使う。同じ階層で cache を二重に定義できない）
cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - node_modules/
```

## トラブルシューティング

### よくある問題と対処

**問題 1：Runner の memory 不足**
```toml
# config.toml
[[runners]]
  [runners.docker]
    memory = "4g"
    memory_swap = "4g"
```

**問題 2：Network 接続の問題**
```yaml
# Retry を追加
retry:
  max: 2
  when:
    - runner_system_failure
    - stuck_or_timeout_failure
```

**問題 3：権限の問題**
```bash
# Runner の権限を確認
sudo usermod -aG docker gitlab-runner
sudo systemctl restart gitlab-runner
```

## まとめ

GitLab CI/CD は実用的な DevOps tool で、シンプルな設定だけで基本的な自動 deploy の流れを構築できます。ポイントは次のとおりです。

1. **シンプルに始める**：基本的な test、build、deploy から始める
2. **Harbor との連携**：private image registry で security を確保する
3. **段階的に最適化する**：必要に応じて機能を少しずつ追加する
4. **モジュール化する**：`extends` で重複した設定を減らす

シンプルな設定から始め、team に合った CI/CD workflow を段階的に作っていくことで、開発効率を着実に高められます。
