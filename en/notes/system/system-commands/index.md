---
title: "System Administration Commands"
url: "https://clarence.tw/en/notes/system/system-commands/"
language: "en"
---

# System Administration Commands

Linux / Unix system information, file operations, systemd, and network diagnostics.

## Version and safety scope

**Last reviewed: July 11, 2026**

This is a general command reference, not a version-pinned runbook. Check the installed version, current official documentation, and the target account, host, and path before use. Commands that deploy, destroy, delete, prune, sync, upgrade, or change system settings can cause cost, downtime, or data loss; preview changes and back up where appropriate.

## System inspection

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

## Files and logs

```bash
ls -la
find /path -name "*.log"
du -sh /path/*
tail -f /var/log/syslog
grep "error" /var/log/syslog
tar -czf archive.tar.gz folder/
```

Use `tail -f` for live logs and `grep` for narrowing down historical evidence.

## systemd and networking

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
