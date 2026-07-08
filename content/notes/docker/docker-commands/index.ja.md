---
title: Docker コマンド
description: Docker image、container、Compose、cleanup のよく使うコマンド。
weight: 410
menu:
  notes:
    name: Docker コマンド
    identifier: notes-docker-commands
    parent: notes-docker
    weight: 10
---

{{< note title="Images と containers" >}}

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

{{< /note >}}

{{< note title="Compose workflow" >}}

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

{{< /note >}}

{{< note title="Cleanup" >}}

```bash
docker system df
docker image prune
docker container prune
docker volume prune
docker system prune
```

shared build host では pruning 前に disk usage を確認する。

{{< /note >}}
