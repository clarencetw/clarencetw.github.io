---
title: Docker Commands
description: Common commands for Docker images, containers, Compose, and cleanup.
lastmod: 2026-07-11T00:00:00+08:00
weight: 410
menu:
  notes:
    name: Docker Commands
    identifier: notes-docker-commands
    parent: notes-docker
    weight: 10
---

{{< note title="Version and safety scope" >}}

**Last reviewed: July 11, 2026**

This is a general command reference, not a version-pinned runbook. Check the installed version, current official documentation, and the target account, host, and path before use. Commands that deploy, destroy, delete, prune, sync, upgrade, or change system settings can cause cost, downtime, or data loss; preview changes and back up where appropriate.

{{< /note >}}

{{< note title="Images and containers" >}}

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

Name long-running containers so logs and operational commands are easier to read.

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

Use `down -v` only when the volume data is disposable.

{{< /note >}}

{{< note title="Cleanup" >}}

```bash
docker system df
docker image prune
docker container prune
docker volume prune
docker system prune
```

Check disk usage before pruning shared build hosts.

{{< /note >}}
