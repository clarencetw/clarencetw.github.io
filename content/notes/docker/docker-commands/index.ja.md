---
title: Docker コマンド早見表：image、container、Compose、cleanup
description: docker run、ps、exec、logs、Compose、prune などよく使う Docker コマンドを整理。--rm の使い捨て container や安全な cleanup の確認も扱います。
lastmod: 2026-07-11T00:00:00+08:00
weight: 410
menu:
  notes:
    name: Docker コマンド
    identifier: notes-docker-commands
    parent: notes-docker
    weight: 10
---

{{< note title="Version と安全範囲" >}}

**最終確認：2026年7月11日**

これは一般的な command reference であり、特定 version に固定した完全な runbook ではありません。実行前に installed version、最新の公式ドキュメント、対象 account／host／path を確認してください。deploy、destroy、delete、prune、sync、upgrade、system setting の変更は、費用、停止、data loss につながる可能性があります。差分を事前確認し、必要に応じて backup を取得してください。

{{< /note >}}


<!-- Docker 基本コマンド -->
{{< note title="Docker 基本コマンド" >}}

**Image 管理：**
```bash
# image を検索
docker search nginx
docker search ubuntu

# image を取得
docker pull nginx
docker pull nginx:alpine
docker pull ubuntu:24.04

# image 一覧
docker images
docker image ls

# image を削除
docker rmi nginx
docker rmi nginx:alpine
docker image rm ubuntu:24.04

# 未使用 image の整理
docker image prune     # dangling image を削除
docker image prune -a  # どの container にも使われていない image をすべて削除
```

{{< /note >}}

<!-- Container 操作 -->
{{< note title="Container 操作" >}}

**Container の起動：**
```bash
# 基本的な起動
docker run nginx
docker run -d nginx                    # background で実行
docker run -it ubuntu bash             # interactive mode
docker run --rm -it ubuntu bash        # 終了時に container を自動削除

# Port mapping
docker run -d -p 8080:80 nginx         # host の 8080 を container の 80 に対応付け
docker run -d -p 127.0.0.1:8080:80 nginx  # localhost のみに bind

# Directory の mount
docker run -d -v /host/path:/container/path nginx
docker run -d -v $(pwd):/app node      # current directory を mount

# 環境変数
docker run -d -e ENV_VAR=value nginx
docker run -d --env-file .env nginx

# Container に名前を付ける
docker run -d --name my-nginx nginx
```

**Container の管理：**
```bash
# Container 一覧
docker ps                              # 実行中の container
docker ps -a                           # すべての container
docker container ls

# Container を停止
docker stop container_id
docker stop my-nginx
docker kill container_id               # 強制停止

# 停止中の container を起動
docker start container_id
docker restart container_id

# Container を削除
docker rm container_id
docker rm my-nginx
docker rm -f container_id              # 実行中の container を強制削除

# 停止済み container の整理
docker container prune
```

長く動かす container には名前を付ける。logs や operational commands が読みやすくなる。

{{< /note >}}

<!-- Container との対話 -->
{{< note title="Container の操作とデバッグ" >}}

```bash
# 実行中の container に入る
docker exec -it container_id bash
docker exec -it my-nginx sh

# Container の log を確認
docker logs container_id
docker logs -f container_id             # log をリアルタイムで追跡
docker logs --tail 100 container_id     # 最後の 100 行を表示

# Container の情報を確認
docker inspect container_id
docker stats container_id               # リアルタイムの resource 使用状況
docker top container_id                 # container 内の process

# File をコピー
docker cp file.txt container_id:/path/  # container へコピー
docker cp container_id:/path/file.txt . # container からコピー

# Container 内の変更を確認
docker diff container_id
```

{{< /note >}}

<!-- Docker Compose -->
{{< note title="Docker Compose" >}}

**基本コマンド：**
```bash
# Service を起動
docker compose up
docker compose up -d                    # background で実行
docker compose up --build               # image を再 build

# Service を停止
docker compose down
docker compose down -v                  # volumes も削除
docker compose stop

# Service の状態を確認
docker compose ps
docker compose logs
docker compose logs -f service_name     # 特定 service の log を追跡

# コマンドを実行
docker compose exec service_name bash
docker compose run service_name command

# Service を再起動
docker compose restart
docker compose restart service_name
```

`down -v` は volume data を削除してよい場合だけ使う。

**docker-compose.yml の例：**
```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
    
  db:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: myapp
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

{{< /note >}}

<!-- Image の build -->
{{< note title="Image の build（Dockerfile）" >}}

**基本的な Dockerfile：**
```dockerfile
# Node.js application の例
FROM node:24-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

EXPOSE 3000

USER node

CMD ["npm", "start"]
```

**Build コマンド：**
```bash
# Image を build
docker build -t my-app .
docker build -t my-app:v1.0 .
docker build -f Dockerfile.prod -t my-app:prod .

# Multi-stage build
docker build --target production -t my-app:prod .

# Build 時に引数を渡す
docker build --build-arg NODE_ENV=production -t my-app .

# Build 履歴を確認
docker history my-app
```

{{< /note >}}

<!-- Network 管理 -->
{{< note title="Docker network" >}}

```bash
# Network 一覧
docker network ls

# Network を作成
docker network create my-network
docker network create --driver bridge my-bridge

# Container を network に接続
docker network connect my-network container_id

# Network から切断
docker network disconnect my-network container_id

# Network の詳細を確認
docker network inspect my-network

# Network を削除
docker network rm my-network

# 未使用 network の整理
docker network prune
```

{{< /note >}}

<!-- Volume 管理 -->
{{< note title="Docker volumes" >}}

```bash
# Volume 一覧
docker volume ls

# Volume を作成
docker volume create my-volume

# Volume の詳細を確認
docker volume inspect my-volume

# Volume を使う
docker run -d -v my-volume:/data nginx

# Volume を削除
docker volume rm my-volume

# 未使用の匿名 volume を整理（Docker 23 以降、named volume も含めるには -a が必要）
docker volume prune

# Volume を backup
docker run --rm -v my-volume:/data -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz -C /data .

# Volume を restore
docker run --rm -v my-volume:/data -v $(pwd):/backup ubuntu tar xzf /backup/backup.tar.gz -C /data
```

{{< /note >}}

<!-- System cleanup -->
{{< note title="Docker system cleanup" >}}

```bash
# Docker の disk 使用量を確認
docker system df

# 未使用 resource の整理
docker system prune                     # 停止済み container、未使用 network、dangling image、build cache
docker system prune -a                  # 未使用 image も含める
docker system prune -a --volumes        # さらに未使用の匿名 volume も含める

# Resource ごとに整理
docker container prune                  # 停止済み container
docker image prune                      # dangling image
docker image prune -a                   # 未使用 image すべて
docker network prune                    # 未使用 network
docker volume prune                     # 未使用の匿名 volume

# すべての container を強制削除
docker rm -f $(docker ps -aq)

# すべての image を削除
docker rmi -f $(docker images -q)
```

shared build host では pruning 前に disk usage を確認する。

{{< /note >}}

<!-- Registry 操作 -->
{{< note title="Docker registry" >}}

```bash
# Registry に login
docker login
docker login registry.example.com
echo "$REGISTRY_PASSWORD" | docker login -u username --password-stdin registry.example.com  # password を shell history や process 一覧に残さない

# Image に tag を付ける
docker tag my-app:latest registry.example.com/my-app:latest
docker tag my-app:latest harbor.company.com/project/my-app:v1.0

# Image を push
docker push registry.example.com/my-app:latest
docker push harbor.company.com/project/my-app:v1.0

# Private registry から pull
docker pull harbor.company.com/project/my-app:v1.0

# Logout
docker logout
docker logout registry.example.com
```

{{< /note >}}
