---
title: パッケージ管理コマンド
description: Homebrew、APT、DNF、YUM など package manager の基本操作。
weight: 310
menu:
  notes:
    name: パッケージ管理
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

active development 用の machine では、広範囲 upgrade 前に `brew outdated` を確認する。

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

production host では kernel や runtime updates の範囲を確認してから適用する。

{{< /note >}}

{{< note title="DNF と YUM" >}}

```bash
sudo dnf check-update
sudo dnf install git nginx
sudo dnf upgrade

sudo yum check-update
sudo yum install git nginx
sudo yum update
```

distribution native の package manager を使い、service scripts と dependencies の一貫性を保つ。

{{< /note >}}
