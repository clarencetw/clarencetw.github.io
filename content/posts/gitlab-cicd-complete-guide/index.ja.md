---
title: GitLab CI/CD Configuration Guide
date: 2024-01-30T15:00:00+08:00
description: GitLab CI/CD の実務的な設定メモ。Runner、Harbor、multi-environment deployment を扱います。
menu:
  sidebar:
    name: GitLab CI/CD Guide
    identifier: gitlab-cicd-complete-guide
    weight: 40
tags: ["GitLab", "CI/CD", "DevOps", "Docker", "Automation"]
categories: ["DevOps", "Automation"]
---

Enterprise DevOps の実務では、code submission から production deployment までの GitLab CI/CD workflow を構築・運用します。ここではよく使う configuration pattern を整理します。

## GitLab Runner

Self-hosted runner は、private network、private registry、特定 runtime environment が必要な場合に便利です。

```bash
# Install GitLab Runner
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt-get install gitlab-runner

# Register runner
sudo gitlab-runner register \
  --url "https://gitlab.company.com/" \
  --registration-token "YOUR_TOKEN" \
  --executor "docker" \
  --docker-image "alpine:latest" \
  --description "Production Runner" \
  --tag-list "production,docker"
```

Docker build を行う場合、runner の security と build requirements を合わせて設計する必要があります。Docker-in-Docker は便利ですが、privileged mode のリスクも理解して使うべきです。

## Basic `.gitlab-ci.yml`

Node.js project の最小構成は test、build、deploy の 3 stage から始められます。

```yaml
image: node:18-alpine

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
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  before_script:
    - docker login -u $HARBOR_USERNAME -p $HARBOR_PASSWORD $HARBOR_REGISTRY
  script:
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
  only:
    - main
```

## Deployment Notes

Multi-environment deployment では、staging と production の違いを明示します。Staging は自動 deploy、production は review 後の manual trigger にすることが多いです。

実務で重要なのは、CI/CD を単なる script runner にしないことです。Testing、build、registry、deployment、rollback、observability をつないだ repeatable release system として設計します。
