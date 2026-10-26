---
title: "Docker Commands Cheat Sheet: Images, Containers, Compose, and Cleanup"
description: Everyday Docker commands for run, ps, exec, logs, Compose, and prune, including --rm throwaway containers and safe cleanup checks.
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


<!-- Docker basics -->
{{< note title="Docker basics" >}}

**Image management:**
```bash
# Search for images
docker search nginx
docker search ubuntu

# Pull images
docker pull nginx
docker pull nginx:alpine
docker pull ubuntu:24.04

# List images
docker images
docker image ls

# Remove images
docker rmi nginx
docker rmi nginx:alpine
docker image rm ubuntu:24.04

# Clean up unused images
docker image prune     # Remove dangling images
docker image prune -a  # Remove all images not used by any container
```

{{< /note >}}

<!-- Container operations -->
{{< note title="Container operations" >}}

**Running containers:**
```bash
# Basic run
docker run nginx
docker run -d nginx                    # Run in the background (detached)
docker run -it ubuntu bash             # Interactive mode
docker run --rm -it ubuntu bash        # Remove the container automatically on exit

# Port mapping
docker run -d -p 8080:80 nginx         # Map host port 8080 to container port 80
docker run -d -p 127.0.0.1:8080:80 nginx  # Bind to localhost only

# Bind-mount directories
docker run -d -v /host/path:/container/path nginx
docker run -d -v $(pwd):/app node      # Mount the current directory

# Environment variables
docker run -d -e ENV_VAR=value nginx
docker run -d --env-file .env nginx

# Name the container
docker run -d --name my-nginx nginx
```

**Managing containers:**
```bash
# List containers
docker ps                              # Running containers
docker ps -a                           # All containers
docker container ls

# Stop containers
docker stop container_id
docker stop my-nginx
docker kill container_id               # Force stop

# Start a stopped container
docker start container_id
docker restart container_id

# Remove containers
docker rm container_id
docker rm my-nginx
docker rm -f container_id              # Force-remove a running container

# Clean up stopped containers
docker container prune
```

Name long-running containers so logs and operational commands are easier to read.

{{< /note >}}

<!-- Container interaction -->
{{< note title="Interacting with and debugging containers" >}}

```bash
# Open a shell in a running container
docker exec -it container_id bash
docker exec -it my-nginx sh

# View container logs
docker logs container_id
docker logs -f container_id             # Follow logs in real time
docker logs --tail 100 container_id     # Show the last 100 lines

# Inspect containers
docker inspect container_id
docker stats container_id               # Live resource usage
docker top container_id                 # Processes inside the container

# Copy files
docker cp file.txt container_id:/path/  # Copy into the container
docker cp container_id:/path/file.txt . # Copy out of the container

# Show filesystem changes in the container
docker diff container_id
```

{{< /note >}}

<!-- Docker Compose -->
{{< note title="Docker Compose" >}}

**Basic commands:**
```bash
# Start services
docker compose up
docker compose up -d                    # Run in the background
docker compose up --build               # Rebuild images

# Stop services
docker compose down
docker compose down -v                  # Also remove volumes
docker compose stop

# Check service status
docker compose ps
docker compose logs
docker compose logs -f service_name     # Follow logs for one service

# Run commands
docker compose exec service_name bash
docker compose run service_name command

# Restart services
docker compose restart
docker compose restart service_name
```

Use `down -v` only when the volume data is disposable.

**Example docker-compose.yml:**
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

<!-- Building images -->
{{< note title="Building images (Dockerfile)" >}}

**Basic Dockerfile:**
```dockerfile
# Node.js application example
FROM node:24-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

EXPOSE 3000

USER node

CMD ["npm", "start"]
```

**Build commands:**
```bash
# Build an image
docker build -t my-app .
docker build -t my-app:v1.0 .
docker build -f Dockerfile.prod -t my-app:prod .

# Multi-stage build
docker build --target production -t my-app:prod .

# Pass build arguments
docker build --build-arg NODE_ENV=production -t my-app .

# Show image build history
docker history my-app
```

{{< /note >}}

<!-- Networking -->
{{< note title="Docker networking" >}}

```bash
# List networks
docker network ls

# Create networks
docker network create my-network
docker network create --driver bridge my-bridge

# Connect a container to a network
docker network connect my-network container_id

# Disconnect a container from a network
docker network disconnect my-network container_id

# Inspect a network
docker network inspect my-network

# Remove a network
docker network rm my-network

# Clean up unused networks
docker network prune
```

{{< /note >}}

<!-- Volumes -->
{{< note title="Docker volumes" >}}

```bash
# List volumes
docker volume ls

# Create a volume
docker volume create my-volume

# Inspect a volume
docker volume inspect my-volume

# Use a volume
docker run -d -v my-volume:/data nginx

# Remove a volume
docker volume rm my-volume

# Clean up unused anonymous volumes (Docker 23+ needs -a to include named volumes)
docker volume prune

# Back up a volume
docker run --rm -v my-volume:/data -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz -C /data .

# Restore a volume
docker run --rm -v my-volume:/data -v $(pwd):/backup ubuntu tar xzf /backup/backup.tar.gz -C /data
```

{{< /note >}}

<!-- System cleanup -->
{{< note title="Docker system cleanup" >}}

```bash
# Show Docker disk usage
docker system df

# Clean up unused resources
docker system prune                     # Stopped containers, unused networks, dangling images, and build cache
docker system prune -a                  # Also unused images
docker system prune -a --volumes        # Also unused anonymous volumes

# Clean up by resource type
docker container prune                  # Stopped containers
docker image prune                      # Dangling images
docker image prune -a                   # All unused images
docker network prune                    # Unused networks
docker volume prune                     # Unused anonymous volumes

# Force-remove all containers
docker rm -f $(docker ps -aq)

# Remove all images
docker rmi -f $(docker images -q)
```

Check disk usage before pruning shared build hosts.

{{< /note >}}

<!-- Registry -->
{{< note title="Docker registry" >}}

```bash
# Log in to a registry
docker login
docker login registry.example.com
echo "$REGISTRY_PASSWORD" | docker login -u username --password-stdin registry.example.com  # Keeps the password out of shell history and the process list

# Tag images
docker tag my-app:latest registry.example.com/my-app:latest
docker tag my-app:latest harbor.company.com/project/my-app:v1.0

# Push images
docker push registry.example.com/my-app:latest
docker push harbor.company.com/project/my-app:v1.0

# Pull from a private registry
docker pull harbor.company.com/project/my-app:v1.0

# Log out
docker logout
docker logout registry.example.com
```

{{< /note >}}
