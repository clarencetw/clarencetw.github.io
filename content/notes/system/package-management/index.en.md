---
title: Package Management Commands
description: Common Homebrew, APT, DNF, YUM, and package-manager operations.
weight: 310
menu:
  notes:
    name: Package Management
    identifier: notes-system-package
    parent: notes-system
    weight: 10
---

{{< note title="Homebrew" >}}

```bash
brew update
brew install git node hugo
brew install --cask visual-studio-code
brew list
brew outdated
brew upgrade
brew cleanup
```

Use `brew outdated` before broad upgrades on machines used for active development.

{{< /note >}}

{{< note title="APT" >}}

```bash
sudo apt update
sudo apt upgrade
sudo apt install git curl wget vim
apt list --installed
apt list --upgradable
sudo apt autoremove
```

For production hosts, review upgrade scope before applying kernel or runtime updates.

{{< /note >}}

{{< note title="DNF and YUM" >}}

```bash
sudo dnf check-update
sudo dnf install git nginx
sudo dnf upgrade

sudo yum check-update
sudo yum install git nginx
sudo yum update
```

Use the package manager native to the distribution so service scripts and dependencies remain consistent.

{{< /note >}}
