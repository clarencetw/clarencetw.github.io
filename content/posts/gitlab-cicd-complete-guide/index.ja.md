---
title: GitLab CI/CD 設定ガイド
date: 2024-01-30T15:00:00+08:00
lastmod: 2026-07-11T00:00:00+08:00
description: GitLab CI/CD の実務的な設定メモ。Runner、Harbor、multi-environment deployment を扱います。
menu:
  sidebar:
    name: GitLab CI/CD 設定
    identifier: gitlab-cicd-complete-guide
    weight: 40
tags: ["GitLab", "CI/CD", "DevOps", "Docker", "Automation"]
categories: ["DevOps", "Automation"]
---

Enterprise DevOps の実務では、code submission から production deployment までの GitLab CI/CD workflow を構築・運用します。ここではよく使う configuration pattern を整理します。

> **2026年7月11日確認：**サンプルを GitLab Runner authentication token、Node.js 24 LTS、Docker 29.6.1 に更新しました。version と security default は変わるため、production で使う前に [GitLab Runner 登録ドキュメント](https://docs.gitlab.com/runner/register/)、[Node.js release status](https://nodejs.org/en/about/previous-releases)、[Docker Engine release notes](https://docs.docker.com/engine/release-notes/29/) を確認し、team で検証した version または digest に固定してください。

## GitLab Runner

Self-hosted runner は、private network、private registry、特定 runtime environment が必要な場合に便利です。

まず GitLab の project、group、または Admin Area で runner を作成し、tags や protected scope を設定してから、`glrt-` で始まる runner authentication token を取得します。旧 registration token workflow は deprecated で、GitLab instance ですでに無効化されている場合があります。

```bash
# Install GitLab Runner
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt-get install gitlab-runner

# Register runner
export RUNNER_AUTHENTICATION_TOKEN="glrt-REDACTED"
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.company.com/" \
  --token "$RUNNER_AUTHENTICATION_TOKEN" \
  --executor "docker" \
  --docker-image "alpine:3.23"
```

Authentication token は secret として扱い、repository、CI log、共有 note に保存しないでください。登録後は runner host の `config.toml` に保存されるため、file と host の access を制限します。

以下の Docker-in-Docker job には、`privileged = true` と `/certs/client` volume を設定した Docker executor が必要です。Privileged runner は attack surface が大きいため、trusted project と user に限定するか、non-privileged な image build 方法を選択してください。

Docker build を行う場合、runner の security と build requirements を合わせて設計する必要があります。Docker-in-Docker は便利ですが、privileged mode のリスクも理解して使うべきです。

## Basic `.gitlab-ci.yml`

Node.js project の最小構成は test、build、deploy の 3 stage から始められます。

```yaml
image: node:24-alpine

stages:
  - test
  - build
  - deploy

before_script:
  - npm ci

test:
  stage: test
  script:
    - npm run test
  only:
    - merge_requests
    - main
```

## Harbor Registry Integration

Harbor は private container registry、access control、image scanning が必要な team に向いています。

```yaml
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
    - echo "$HARBOR_PASSWORD" | docker login --username "$HARBOR_USERNAME" --password-stdin "$HARBOR_REGISTRY"
  script:
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
  only:
    - main
```

## Deployment Notes

Multi-environment deployment では、staging と production の違いを明示します。Staging は自動 deploy、production は review 後の manual trigger にすることが多いです。

実務で重要なのは、CI/CD を単なる script runner にしないことです。Testing、build、registry、deployment、rollback、observability をつないだ repeatable release system として設計します。
