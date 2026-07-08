---
title: System Administration Commands
description: Linux / Unix system information, file operations, systemd, and network diagnostics.
weight: 320
menu:
  notes:
    name: System Commands
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
