---
title: システム管理コマンド
description: Linux / Unix system information、file operations、systemd、network diagnostics。
lastmod: 2026-07-11T00:00:00+08:00
weight: 320
menu:
  notes:
    name: システムコマンド
    identifier: notes-system-commands
    parent: notes-system
    weight: 20
---

{{< note title="Version と安全範囲" >}}

**最終確認：2026年7月11日**

これは一般的な command reference であり、特定 version に固定した完全な runbook ではありません。実行前に installed version、最新の公式ドキュメント、対象 account／host／path を確認してください。deploy、destroy、delete、prune、sync、upgrade、system setting の変更は、費用、停止、data loss につながる可能性があります。差分を事前確認し、必要に応じて backup を取得してください。

{{< /note >}}

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
