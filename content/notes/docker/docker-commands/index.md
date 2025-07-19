---
title: Docker 常用指令
weight: 410
menu:
  notes:
    name: Docker Commands
    identifier: notes-docker-commands
    parent: notes-docker
    weight: 10
---

<!-- Docker 基本指令 -->
{{< note title="Docker 基本指令" >}}

**映像檔管理：**
```bash
# 搜尋映像檔
docker search nginx
docker search ubuntu

# 下載映像檔
docker pull nginx
docker pull nginx:1.21
docker pull ubuntu:20.04

# 列出映像檔
docker images
docker image ls

# 移除映像檔
docker rmi nginx
docker rmi nginx:1.21
docker image rm ubuntu:20.04

# 清理未使用的映像檔
docker image prune
docker image prune -a  # 移除所有未使用的映像檔
```

{{< /note >}}

<!-- 容器操作 -->
{{< note title="容器操作" >}}

**啟動容器：**
```bash
# 基本啟動
docker run nginx
docker run -d nginx                    # 背景執行
docker run -it ubuntu bash             # 互動模式

# 埠對應
docker run -d -p 8080:80 nginx         # 對應埠 8080 到容器的 80
docker run -d -p 127.0.0.1:8080:80 nginx  # 只綁定本機

# 掛載目錄
docker run -d -v /host/path:/container/path nginx
docker run -d -v $(pwd):/app node      # 掛載當前目錄

# 環境變數
docker run -d -e ENV_VAR=value nginx
docker run -d --env-file .env nginx

# 容器命名
docker run -d --name my-nginx nginx
```

**容器管理：**
```bash
# 列出容器
docker ps                              # 運行中的容器
docker ps -a                           # 所有容器
docker container ls

# 停止容器
docker stop container_id
docker stop my-nginx
docker kill container_id               # 強制停止

# 啟動已停止的容器
docker start container_id
docker restart container_id

# 移除容器
docker rm container_id
docker rm my-nginx
docker rm -f container_id              # 強制移除運行中的容器

# 清理停止的容器
docker container prune
```

{{< /note >}}

<!-- 容器互動 -->
{{< note title="容器互動與除錯" >}}

```bash
# 進入運行中的容器
docker exec -it container_id bash
docker exec -it my-nginx sh

# 查看容器日誌
docker logs container_id
docker logs -f container_id             # 即時查看日誌
docker logs --tail 100 container_id     # 查看最後 100 行

# 查看容器資訊
docker inspect container_id
docker stats container_id               # 即時資源使用情況
docker top container_id                 # 容器內程序

# 複製檔案
docker cp file.txt container_id:/path/  # 複製到容器
docker cp container_id:/path/file.txt . # 從容器複製出來

# 查看容器變更
docker diff container_id
```

{{< /note >}}

<!-- Docker Compose -->
{{< note title="Docker Compose" >}}

**基本指令：**
```bash
# 啟動服務
docker-compose up
docker-compose up -d                    # 背景執行
docker-compose up --build               # 重新建置映像檔

# 停止服務
docker-compose down
docker-compose down -v                  # 同時移除 volumes
docker-compose stop

# 查看服務狀態
docker-compose ps
docker-compose logs
docker-compose logs -f service_name     # 查看特定服務日誌

# 執行指令
docker-compose exec service_name bash
docker-compose run service_name command

# 重啟服務
docker-compose restart
docker-compose restart service_name
```

**範例 docker-compose.yml：**
```yaml
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
    
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: myapp
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:
```

{{< /note >}}

<!-- 映像檔建置 -->
{{< note title="映像檔建置 (Dockerfile)" >}}

**基本 Dockerfile：**
```dockerfile
# Node.js 應用程式範例
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

USER node

CMD ["npm", "start"]
```

**建置指令：**
```bash
# 建置映像檔
docker build -t my-app .
docker build -t my-app:v1.0 .
docker build -f Dockerfile.prod -t my-app:prod .

# 多階段建置
docker build --target production -t my-app:prod .

# 建置時傳入參數
docker build --build-arg NODE_ENV=production -t my-app .

# 查看建置歷史
docker history my-app
```

{{< /note >}}

<!-- 網路管理 -->
{{< note title="Docker 網路" >}}

```bash
# 列出網路
docker network ls

# 建立網路
docker network create my-network
docker network create --driver bridge my-bridge

# 連接容器到網路
docker network connect my-network container_id

# 中斷網路連接
docker network disconnect my-network container_id

# 查看網路詳細資訊
docker network inspect my-network

# 移除網路
docker network rm my-network

# 清理未使用的網路
docker network prune
```

{{< /note >}}

<!-- 資料卷管理 -->
{{< note title="Docker Volumes" >}}

```bash
# 列出資料卷
docker volume ls

# 建立資料卷
docker volume create my-volume

# 查看資料卷詳細資訊
docker volume inspect my-volume

# 使用資料卷
docker run -d -v my-volume:/data nginx

# 移除資料卷
docker volume rm my-volume

# 清理未使用的資料卷
docker volume prune

# 備份資料卷
docker run --rm -v my-volume:/data -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz -C /data .

# 還原資料卷
docker run --rm -v my-volume:/data -v $(pwd):/backup ubuntu tar xzf /backup/backup.tar.gz -C /data
```

{{< /note >}}

<!-- 系統清理 -->
{{< note title="Docker 系統清理" >}}

```bash
# 查看 Docker 使用空間
docker system df

# 清理未使用的資源
docker system prune                     # 清理停止的容器、未使用的網路、映像檔
docker system prune -a                  # 包含未使用的映像檔
docker system prune -a --volumes        # 包含未使用的資料卷

# 分別清理
docker container prune                  # 清理停止的容器
docker image prune                      # 清理未使用的映像檔
docker image prune -a                   # 清理所有未使用的映像檔
docker network prune                    # 清理未使用的網路
docker volume prune                     # 清理未使用的資料卷

# 強制移除所有容器
docker rm -f $(docker ps -aq)

# 移除所有映像檔
docker rmi -f $(docker images -q)
```

{{< /note >}}

<!-- Registry 操作 -->
{{< note title="Docker Registry" >}}

```bash
# 登入 Registry
docker login
docker login registry.example.com
docker login -u username -p password registry.example.com

# 標記映像檔
docker tag my-app:latest registry.example.com/my-app:latest
docker tag my-app:latest harbor.company.com/project/my-app:v1.0

# 推送映像檔
docker push registry.example.com/my-app:latest
docker push harbor.company.com/project/my-app:v1.0

# 從私有 Registry 拉取
docker pull harbor.company.com/project/my-app:v1.0

# 登出
docker logout
docker logout registry.example.com
```

{{< /note >}}