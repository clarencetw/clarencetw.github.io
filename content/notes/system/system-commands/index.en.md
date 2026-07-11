---
title: System Administration Commands
description: Linux / Unix system information, file operations, systemd, and network diagnostics.
lastmod: 2026-07-11T00:00:00+08:00
weight: 320
menu:
  notes:
    name: System Commands
    identifier: notes-system-commands
    parent: notes-system
    weight: 20
---

{{< note title="Version and safety scope" >}}

**Last reviewed: July 11, 2026**

This is a general command reference, not a version-pinned runbook. Check the installed version, current official documentation, and the target account, host, and path before use. Commands that deploy, destroy, delete, prune, sync, upgrade, or change system settings can cause cost, downtime, or data loss; preview changes and back up where appropriate.

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

Capture these basics first when documenting a server incident.

{{< /note >}}

{{< note title="Files and logs" >}}

```bash
ls -la
find /path -name "*.log"
du -sh /path/*
tail -f /var/log/syslog
grep "error" /var/log/syslog
tar -czf archive.tar.gz folder/
```

Use `tail -f` for live logs and `grep` for narrowing down historical evidence.

{{< /note >}}

{{< note title="systemd and networking" >}}

```bash
sudo systemctl status nginx
sudo systemctl restart nginx
sudo journalctl -u nginx -f

ping -c 4 8.8.8.8
ss -tuln
lsof -i :80
curl -I https://example.com
```

Start with service state, then check listening ports and the external HTTP path.

{{< /note >}}
