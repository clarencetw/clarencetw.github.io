---
title: "Docker コマンド"
url: "https://clarence.tw/ja/notes/docker/docker-commands/"
language: "ja"
---

# Docker コマンド

Docker image、container、Compose、cleanup のよく使うコマンド。

## Version と安全範囲

**最終確認：2026年7月11日**

これは一般的な command reference であり、特定 version に固定した完全な runbook ではありません。実行前に installed version、最新の公式ドキュメント、対象 account／host／path を確認してください。deploy、destroy、delete、prune、sync、upgrade、system setting の変更は、費用、停止、data loss につながる可能性があります。差分を事前確認し、必要に応じて backup を取得してください。

## Images と containers

```bash
docker pull nginx:latest
docker images
docker ps
docker ps -a
docker run -d --name web -p 8080:80 nginx
docker exec -it web sh
docker logs -f web
docker stop web
docker rm web
```

長く動かす container には名前を付ける。logs や operational commands が読みやすくなる。

## Compose workflow

```bash
docker compose up -d
docker compose up --build
docker compose ps
docker compose logs -f service_name
docker compose exec service_name sh
docker compose down
docker compose down -v
```

`down -v` は volume data を削除してよい場合だけ使う。

## Cleanup

```bash
docker system df
docker image prune
docker container prune
docker volume prune
docker system prune
```

shared build host では pruning 前に disk usage を確認する。
