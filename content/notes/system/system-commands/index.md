---
title: 系統管理指令
weight: 320
menu:
  notes:
    name: System Commands
    identifier: notes-system-commands
    parent: notes-system
    weight: 20
---

<!-- 系統資訊查詢 -->
{{< note title="系統資訊查詢" >}}

```bash
# 查看系統資訊
uname -a                # 完整系統資訊
uname -r                # 核心版本
lsb_release -a          # 發行版資訊 (Ubuntu/Debian)
cat /etc/os-release     # 系統版本資訊

# 查看硬體資訊
lscpu                   # CPU 資訊
free -h                 # 記憶體使用情況
df -h                   # 磁碟使用情況
lsblk                   # 區塊設備資訊
lsusb                   # USB 設備
lspci                   # PCI 設備

# 查看網路資訊
ip addr show            # 網路介面資訊
ip route show           # 路由表
netstat -tuln           # 網路連線狀態
ss -tuln                # 現代版 netstat

# 查看程序資訊
ps aux                  # 所有程序
top                     # 即時程序監控
htop                    # 更好的 top (需安裝)
pgrep nginx             # 尋找特定程序
```

{{< /note >}}

<!-- 檔案與目錄操作 -->
{{< note title="檔案與目錄操作" >}}

```bash
# 檔案操作
ls -la                  # 詳細列出檔案
find /path -name "*.log" # 尋找檔案
locate filename         # 快速尋找檔案 (需 updatedb)
which command           # 尋找指令位置
whereis command         # 尋找指令、手冊等

# 檔案權限
chmod 755 file          # 設定檔案權限
chmod +x script.sh      # 加入執行權限
chown user:group file   # 變更擁有者
chgrp group file        # 變更群組

# 檔案內容
cat file.txt            # 顯示檔案內容
less file.txt           # 分頁顯示
head -n 10 file.txt     # 顯示前 10 行
tail -f /var/log/syslog # 即時顯示檔案末尾
grep "error" file.txt   # 搜尋文字

# 壓縮與解壓縮
tar -czf archive.tar.gz folder/     # 壓縮
tar -xzf archive.tar.gz             # 解壓縮
zip -r archive.zip folder/          # ZIP 壓縮
unzip archive.zip                   # ZIP 解壓縮
```

{{< /note >}}

<!-- 服務管理 (systemd) -->
{{< note title="服務管理 (systemd)" >}}

```bash
# 服務狀態
sudo systemctl status nginx        # 查看服務狀態
sudo systemctl is-active nginx     # 檢查是否運行
sudo systemctl is-enabled nginx    # 檢查是否開機啟動

# 服務控制
sudo systemctl start nginx         # 啟動服務
sudo systemctl stop nginx          # 停止服務
sudo systemctl restart nginx       # 重啟服務
sudo systemctl reload nginx        # 重新載入設定

# 開機啟動
sudo systemctl enable nginx        # 設定開機啟動
sudo systemctl disable nginx       # 取消開機啟動

# 查看日誌
sudo journalctl -u nginx           # 查看服務日誌
sudo journalctl -u nginx -f        # 即時查看日誌
sudo journalctl -u nginx --since "1 hour ago"  # 查看最近一小時日誌

# 列出服務
systemctl list-units --type=service            # 所有服務
systemctl list-units --type=service --state=running  # 運行中服務
systemctl list-unit-files --type=service       # 所有服務檔案
```

{{< /note >}}

<!-- 網路工具 -->
{{< note title="網路診斷工具" >}}

```bash
# 連線測試
ping google.com         # 測試連線
ping -c 4 8.8.8.8      # 發送 4 個封包

# 路由追蹤
traceroute google.com   # 追蹤路由
mtr google.com          # 持續追蹤 (需安裝)

# 埠掃描
nmap localhost          # 掃描本機埠
nmap -p 80,443 example.com  # 掃描特定埠

# 網路連線
netstat -tuln           # 查看監聽埠
ss -tuln                # 現代版 netstat
lsof -i :80             # 查看使用特定埠的程序

# 下載工具
wget https://example.com/file.zip       # 下載檔案
curl -O https://example.com/file.zip    # 使用 curl 下載
curl -I https://example.com             # 只取得 HTTP 標頭
```

{{< /note >}}

<!-- 效能監控 -->
{{< note title="效能監控" >}}

```bash
# CPU 監控
top                     # 基本監控
htop                    # 進階監控 (需安裝)
iotop                   # I/O 監控 (需安裝)
vmstat 1                # 虛擬記憶體統計

# 記憶體監控
free -h                 # 記憶體使用情況
cat /proc/meminfo       # 詳細記憶體資訊

# 磁碟監控
df -h                   # 磁碟使用情況
du -sh /path/*          # 目錄大小
iostat 1                # I/O 統計 (需安裝 sysstat)

# 網路監控
iftop                   # 網路流量監控 (需安裝)
nethogs                 # 按程序顯示網路使用 (需安裝)
```

{{< /note >}}

<!-- 定時任務 -->
{{< note title="定時任務 (Cron)" >}}

```bash
# 編輯 crontab
crontab -e              # 編輯當前使用者的 crontab
sudo crontab -e         # 編輯 root 的 crontab

# 查看 crontab
crontab -l              # 列出當前使用者的 crontab
sudo crontab -l         # 列出 root 的 crontab

# Cron 時間格式
# 分 時 日 月 週 指令
# 0  2  *  *  *  /path/to/script.sh

# 常用範例
0 2 * * *               # 每天凌晨 2 點
0 */6 * * *             # 每 6 小時
0 0 1 * *               # 每月 1 號
0 0 * * 0               # 每週日
*/5 * * * *             # 每 5 分鐘

# 查看 cron 日誌
sudo tail -f /var/log/cron      # CentOS/RHEL
sudo tail -f /var/log/syslog    # Ubuntu/Debian
```

{{< /note >}}