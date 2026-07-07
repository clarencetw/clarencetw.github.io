---
title: GitLab CI/CD Configuration Guide
date: 2024-01-30T15:00:00+08:00
description: Practical GitLab CI/CD configuration notes, from runner setup to Harbor integration and multi-environment deployment.
menu:
  sidebar:
    name: GitLab CI/CD Configuration Guide
    identifier: gitlab-cicd-complete-guide
    weight: 40
tags: ["GitLab", "CI/CD", "DevOps", "Docker", "Automation"]
categories: ["DevOps", "Automation"]
---

In enterprise DevOps work, I build and maintain GitLab CI/CD workflows from code submission to production deployment. This article summarizes the practical configuration patterns I use most often.

## GitLab CI/CD Foundation

### GitLab Runner Deployment

Self-hosted runners are useful when a team needs controlled network access, private registry connectivity, or predictable runtime behavior.

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

For Docker-based builds, the runner configuration needs to match the team's security and build requirements. Docker-in-Docker is convenient, but it should be used intentionally because privileged mode increases risk.

## Basic `.gitlab-ci.yml`

A small Node.js project can start with a simple test, build, and deploy pipeline.

```yaml
image: node:18-alpine

stages:
  - test
  - build
  - deploy

cache:
  paths:
    - node_modules/

before_script:
  - npm ci

test:
  stage: test
  script:
    - npm run test
  only:
    - merge_requests
    - main

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
```

## Harbor Registry Integration

Harbor is useful when teams need a private container registry with access control and image scanning.

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
    - docker build -t $IMAGE_NAME:latest .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
    - docker push $IMAGE_NAME:latest
  only:
    - main
```

## Deployment Notes

Multi-environment deployment should make environment differences explicit. Staging can deploy automatically from a development branch, while production should usually be reviewed and triggered manually.

```yaml
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

## Practical Takeaways

- Keep CI/CD jobs small enough to debug.
- Make registry, image tag, and deployment target explicit.
- Separate staging and production behavior.
- Treat credentials and registry permissions as part of the deployment design.
- Keep rollback and observability in mind before production release.

GitLab CI/CD is most useful when it becomes a repeatable release system, not just a script runner.
