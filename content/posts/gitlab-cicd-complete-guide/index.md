---
title: GitLab CI/CD 完整配置指南
date: 2024-01-30T15:00:00+08:00
description: 分享 GitLab CI/CD 的完整配置經驗，從基礎設定到進階部署策略
menu:
  sidebar:
    name: GitLab CI/CD 完整配置指南
    identifier: gitlab-cicd-complete-guide
    weight: 40
tags: ["GitLab", "CI/CD", "DevOps", "Docker", "Automation"]
categories: ["DevOps", "Automation"]
---

在企業 DevOps 實踐中，我負責建置和維護 GitLab CI/CD 流程，涵蓋從程式碼提交到生產部署的完整自動化。這篇文章將分享 GitLab CI/CD 的基礎配置經驗。

## GitLab CI/CD 基礎架構

### 1. GitLab Runner 部署

**自建 Runner 配置：**
```bash
# 安裝 GitLab Runner
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt-get install gitlab-runner

# 註冊 Runner
sudo gitlab-runner register \
  --url "https://gitlab.company.com/" \
  --registration-token "YOUR_TOKEN" \
  --executor "docker" \
  --docker-image "alpine:latest" \
  --description "Production Runner" \
  --tag-list "production,docker"
```

**Docker-in-Docker 配置：**
```toml
# /etc/gitlab-runner/config.toml
concurrent = 4
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "docker-runner"
  url = "https://gitlab.company.com/"
  token = "YOUR_TOKEN"
  executor = "docker"
  [runners.custom_build_dir]
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]
    [runners.cache.azure]
  [runners.docker]
    tls_verify = false
    image = "docker:20.10.16"
    privileged = true
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]
    shm_size = 0
```

## .gitlab-ci.yml 基礎範例

### 簡單的 Node.js 專案配置

```yaml
# .gitlab-ci.yml
image: node:18-alpine

# 定義階段
stages:
  - test
  - build
  - deploy

# 快取設定
cache:
  paths:
    - node_modules/

# 安裝依賴
before_script:
  - npm ci

# 測試階段
test:
  stage: test
  script:
    - npm run test
  only:
    - merge_requests
    - main

# 建置階段
build:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main

# 部署到測試環境
deploy:staging:
  stage: deploy
  script:
    - echo "Deploying to staging environment"
    - kubectl set image deployment/myapp myapp=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  environment:
    name: staging
  only:
    - main
```

## Harbor 私有映像倉庫整合

### Harbor 設定與使用

我們使用 Harbor 作為私有 Docker 映像倉庫，提供安全且高效的映像管理。

**Harbor 基本配置：**
```yaml
# 使用 Harbor 作為映像倉庫
variables:
  HARBOR_REGISTRY: "harbor.company.com"
  HARBOR_PROJECT: "myproject"
  IMAGE_NAME: "$HARBOR_REGISTRY/$HARBOR_PROJECT/myapp"

build:harbor:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  before_script:
    # 登入 Harbor
    - docker login -u $HARBOR_USERNAME -p $HARBOR_PASSWORD $HARBOR_REGISTRY
  script:
    # 建置並推送到 Harbor
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker build -t $IMAGE_NAME:latest .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
    - docker push $IMAGE_NAME:latest
  only:
    - main
```

**Harbor 映像掃描：**
```yaml
# Harbor 內建的映像安全掃描
scan:harbor:
  stage: test
  image: alpine:latest
  before_script:
    - apk add --no-cache curl jq
  script:
    # 觸發 Harbor 掃描
    - |
      curl -X POST -u "$HARBOR_USERNAME:$HARBOR_PASSWORD" \
      "$HARBOR_REGISTRY/api/v2.0/projects/$HARBOR_PROJECT/repositories/myapp/artifacts/$CI_COMMIT_SHA/scan"
    # 等待掃描完成並取得結果
    - sleep 30
    - |
      curl -u "$HARBOR_USERNAME:$HARBOR_PASSWORD" \
      "$HARBOR_REGISTRY/api/v2.0/projects/$HARBOR_PROJECT/repositories/myapp/artifacts/$CI_COMMIT_SHA" | jq '.scan_overview'
  only:
    - main
```

## 簡化的多環境部署

### 基礎部署範例

```yaml
# 簡單的多環境部署
.deploy_template:
  image: alpine:latest
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

## Docker 整合

### Dockerfile 最佳實踐

```dockerfile
# 多階段建置
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:18-alpine AS runtime
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .

USER nextjs
EXPOSE 3000
CMD ["npm", "start"]
```

### Docker Compose 測試環境

```yaml
# docker-compose.test.yml
version: '3.8'
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
    image: postgres:13
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    
  redis:
    image: redis:6-alpine
```


## 基礎優化技巧

### 快取設定

```yaml
# 簡單的快取配置
cache:
  paths:
    - node_modules/
    - dist/

# 分支別快取
cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - node_modules/
```

## 故障排除

### 常見問題解決

**問題 1：Runner 記憶體不足**
```toml
# config.toml
[[runners]]
  [runners.docker]
    memory = "4g"
    memory_swap = "4g"
```

**問題 2：網路連線問題**
```yaml
# 增加重試機制
retry:
  max: 2
  when:
    - runner_system_failure
    - stuck_or_timeout_failure
```

**問題 3：權限問題**
```bash
# 檢查 Runner 權限
sudo usermod -aG docker gitlab-runner
sudo systemctl restart gitlab-runner
```

## 結語

GitLab CI/CD 是一個實用的 DevOps 工具，透過簡單的配置就能建立基礎的自動化部署流程。關鍵在於：

1. **簡單開始**：從基礎的測試、建置、部署開始
2. **Harbor 整合**：使用私有映像倉庫確保安全性
3. **逐步優化**：根據需求逐步加入更多功能
4. **模組化設計**：使用 extends 減少重複配置

從簡單的配置開始，逐步建立適合團隊的 CI/CD 流程，可以有效提升開發效率。