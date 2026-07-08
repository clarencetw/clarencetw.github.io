---
title: システム管理コマンド
description: Linux / Unix system information、file operations、systemd、network diagnostics。
weight: 320
menu:
  notes:
    name: システムコマンド
    identifier: notes-system-commands
    parent: notes-system
    weight: 20
---

{{< note title="System inspection" >}}

```bash
uname -a
cat /etc/os-release
lscpu
free -h
df -h
lsblk
ip addr show
ip route show
```

server incident を記録するときは、この基本情報から取得する。

{{< /note >}}

{{< note title="Files と logs" >}}

```bash
ls -la
find /path -name "*.log"
du -sh /path/*
tail -f /var/log/syslog
grep "error" /var/log/syslog
tar -czf archive.tar.gz folder/
```

live logs には `tail -f`、過去ログの絞り込みには `grep` を使う。

{{< /note >}}

{{< note title="systemd と networking" >}}

```bash
sudo systemctl status nginx
sudo systemctl restart nginx
sudo journalctl -u nginx -f

ping -c 4 8.8.8.8
ss -tuln
lsof -i :80
curl -I https://example.com
```

service state、listening ports、external HTTP path の順で確認する。

{{< /note >}}
